from django.db import models

from backend.utils.image_optimizer import optimize_uploaded_image


class OptimizedImageField(models.ImageField):
    """
    Optimize new image uploads before Django saves them
    through the configured storage backend.
    """

    def pre_save(self, model_instance, add):
        image_field = getattr(model_instance, self.attname)

        if image_field and not image_field._committed:
            optimized_file = optimize_uploaded_image( image_field.file )

            setattr( model_instance, self.attname, optimized_file, )

        # Save the optimized file using Django's configured
        # storage backend, which is now Cloudinary.
        return super().pre_save(model_instance, add)