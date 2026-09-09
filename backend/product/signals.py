from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver

from .models import ProductImageModel

from shop.configs.bucket_conf import Bucket


@receiver(pre_save, sender=ProductImageModel)
def optimize_product_image(sender, instance, **kwargs):
    if not instance.image:
        return
    if not instance.image.name:
        return
    old_image = instance.image.name
    if ProductImageModel.objects.filter(image=old_image).exclude(pk=instance.pk).exists():
        Bucket().delete_object(old_image)
    image = Image.open(instance.image)
    if image.mode != "RGB":
        image = image.convert("RGB")
    max_size = 1600
    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    output = BytesIO()
    image.save(output, format="JPEG", quality=85, optimize=True)
    last_id = ProductImageModel.objects.filter(product=instance.product).count() + 1
    filename = f"{last_id}.jpg"
    instance.image.save(filename,ContentFile(output.getvalue()),save=False)

@receiver(post_delete, sender=ProductImageModel)
def optimize_product_image_delete(sender, instance, **kwargs):
    if instance.image:
        Bucket().delete_object(instance.image.name)
