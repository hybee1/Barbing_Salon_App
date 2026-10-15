

import io
import warnings
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile


MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_IMAGE_DIMENSION = 1200
MAX_IMAGE_PIXELS = 25_000_000
WEBP_QUALITY = 82

ALLOWED_FORMATS = {"JPEG", "PNG"}

# Protect against decompression-bomb images.
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


def optimize_uploaded_image(uploaded_file):
    """
    Validate an uploaded image and return an optimized WebP ContentFile.

    Accepted input: JPEG and PNG.
    Output: WebP, maximum 1200 x 1200 pixels.
    """

    if not uploaded_file:
        return uploaded_file

    if uploaded_file.size > MAX_UPLOAD_BYTES:
        raise ValidationError( {"detail": "Image must not exceed 10 MB."} )

    try:
        uploaded_file.seek(0)
        image_bytes = uploaded_file.read()

        with warnings.catch_warnings():
            warnings.simplefilter( "error", Image.DecompressionBombWarning,  )

            # Verify the image contents rather than trusting
            # its filename or supplied content type.
            with Image.open(io.BytesIO(image_bytes)) as source:
                if source.format not in ALLOWED_FORMATS:
                    raise ValidationError( {"detail": "Only JPEG and PNG images are allowed."} )

                if source.width * source.height > MAX_IMAGE_PIXELS:
                    raise ValidationError( {"detail": "Image dimensions are too large."} )

                source.verify()

            # Reopen because verify() invalidates normal image use.
            with Image.open(io.BytesIO(image_bytes)) as source:
                image = ImageOps.exif_transpose(source)
                image.load()

                image.thumbnail(
                    (MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION),
                    Image.Resampling.LANCZOS,
                )

                # Preserve PNG transparency in the WebP output.
                if "A" in image.getbands():
                    image = image.convert("RGBA")
                else:
                    image = image.convert("RGB")

                output = io.BytesIO()

                image.save( output, format="WEBP", quality=WEBP_QUALITY, method=6, )

                output.seek(0)

        original_name = Path( getattr(uploaded_file, "name", "image") ).stem

        # Django will save this content using the .webp filename.
        return ContentFile( output.read(), name=f"{original_name}.webp", )

    except ValidationError:
        raise

    except (
        UnidentifiedImageError, OSError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as exc:
        raise ValidationError(
            {"detail": "The uploaded image is invalid or too large to process."}
        ) from exc

    finally:
        try:
            uploaded_file.seek(0)
        except (AttributeError, OSError):
            pass