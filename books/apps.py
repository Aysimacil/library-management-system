from django.apps import AppConfig


class BooksConfig(AppConfig):
    name = 'books'

    def ready(self):
        from . import signals  # Register deletion cleanup for ORM/admin deletes.
