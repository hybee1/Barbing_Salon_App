from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import models, transaction


class Command(BaseCommand):
    help = "Migrate existing local image files to Cloudinary."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Actually upload images and update database records.",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        media_root = Path(settings.MEDIA_ROOT).resolve()

        if not media_root.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"MEDIA_ROOT does not exist: {media_root}"
                )
            )
            return

        self.stdout.write(
            "Mode: " + ("APPLY" if apply_changes else "DRY RUN")
        )
        self.stdout.write(f"Local media root: {media_root}")

        migrated = 0
        missing = 0
        failed = 0

        for model in apps.get_models():
            for field in model._meta.concrete_fields:
                if not isinstance(field, models.ImageField):
                    continue

                queryset = model._base_manager.exclude(
                    **{field.name: ""}
                ).exclude(
                    **{f"{field.name}__isnull": True}
                )

                for obj in queryset.iterator():
                    image_field = getattr(obj, field.name)
                    old_name = image_field.name

                    if not old_name:
                        continue

                    # Resolve the local path safely.
                    relative_path = Path(old_name)

                    if relative_path.is_absolute():
                        self.stderr.write(
                            f"SKIP absolute path: {old_name}"
                        )
                        continue

                    local_path = (
                        media_root / relative_path
                    ).resolve()

                    # Some older records may contain a leading
                    # "media/" prefix. Try removing it if needed.
                    if (
                        not local_path.is_file()
                        and relative_path.parts
                        and relative_path.parts[0] == "media"
                    ):
                        local_path = (
                            media_root.joinpath(
                                *relative_path.parts[1:]
                            )
                        ).resolve()

                    # Never allow a path to escape MEDIA_ROOT.
                    if (
                        local_path != media_root
                        and media_root not in local_path.parents
                    ):
                        self.stderr.write(
                            f"SKIP unsafe path: {old_name}"
                        )
                        continue

                    if not local_path.is_file():
                        missing += 1
                        self.stdout.write(
                            f"MISSING {model._meta.label} "
                            f"id={obj.pk} field={field.name}: "
                            f"{local_path}"
                        )
                        continue

                    self.stdout.write(
                        f"{'UPLOAD' if apply_changes else 'WOULD UPLOAD'} "
                        f"{model._meta.label} id={obj.pk} "
                        f"field={field.name}: {old_name}"
                    )

                    if not apply_changes:
                        continue

                    try:
                        # Upload via the existing Django ImageField.
                        # The model's upload_to setting is retained.
                        with local_path.open("rb") as source:
                            upload = File(
                                source,
                                name=local_path.name,
                            )

                            with transaction.atomic():
                                setattr(obj, field.name, upload)
                                obj.save(
                                    update_fields=[field.name]
                                )

                        migrated += 1

                    except Exception as exc:
                        failed += 1
                        self.stderr.write(
                            self.style.ERROR(
                                f"FAILED {model._meta.label} "
                                f"id={obj.pk} field={field.name}: "
                                f"{exc}"
                            )
                        )

        self.stdout.write("")
        self.stdout.write(f"Migrated: {migrated}")
        self.stdout.write(f"Missing local files: {missing}")
        self.stdout.write(f"Failed uploads: {failed}")

        if not apply_changes:
            self.stdout.write(
                self.style.WARNING(
                    "Preview only. No files or database records "
                    "were changed. Re-run with --apply to migrate."
                )
            )