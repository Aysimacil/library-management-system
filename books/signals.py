from django.db.models.signals import post_delete
from django.dispatch import receiver

from .media_lifecycle import enqueue_delete
from .models import Book


@receiver(post_delete, sender=Book)
def book_deleted(sender, instance, using, **kwargs):
    enqueue_delete(instance.cover.name, using)
