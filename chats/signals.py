import os
from django.db.models.signals import pre_delete
from django.dispatch import receiver  # импортируем нужный декоратор
from .models import ProfileData

@receiver(pre_delete, sender=ProfileData, weak=False)
def delete_image(sender, instance, **kwargs):
    path_to_photo = instance.avatar_photo.path
    if os.path.exists(path_to_photo):
        os.remove(path_to_photo)
