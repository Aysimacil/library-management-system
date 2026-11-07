from contextlib import contextmanager
import logging
import os
from pathlib import Path
import re
import tempfile

from django.conf import settings
from django.db import DatabaseError, models, transaction

logger = logging.getLogger("library.media")
MANAGED_NAME = re.compile(r"covers/[0-9a-f]{32}\.jpg\Z")


@contextmanager
def media_lock(using="default"):
    from .models import MediaLock
    with transaction.atomic(using=using):
        lock, _ = MediaLock.objects.using(using).get_or_create(pk=1)
        MediaLock.objects.using(using).select_for_update().get(pk=lock.pk)
        # Also acquire SQLite's write lock, where select_for_update is a no-op.
        MediaLock.objects.using(using).filter(pk=lock.pk).update(version=models.F("version") + 1)
        yield


def enqueue_delete(name, using):
    from .models import CoverOperation
    if name and MANAGED_NAME.fullmatch(name):
        CoverOperation.objects.using(using).get_or_create(name=name, kind="DELETE")
        transaction.on_commit(lambda: flush_safely(using), using=using)


def publish(name, data):
    root = Path(settings.MEDIA_ROOT).resolve()
    target = root / name
    target.parent.mkdir(parents=True, exist_ok=True)
    # Unique filenames are application-generated. Never traverse a symlink.
    if target.parent.resolve() != root / "covers" or target.is_symlink():
        raise OSError("Unsafe media destination")
    fd, temporary = tempfile.mkstemp(prefix=".upload-", dir=target.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
        directory = os.open(target.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def flush_media(using="default", limit=100):
    from .models import Book, CoverOperation
    done = 0
    with media_lock(using):
        operations = CoverOperation.objects.using(using).order_by("pk")[:limit]
        for operation in list(operations):
            if not MANAGED_NAME.fullmatch(operation.name):
                raise ValueError("Unmanaged cover name")
            referenced = Book.objects.using(using).filter(cover=operation.name).exists()
            if operation.kind == "WRITE" and referenced:
                publish(operation.name, bytes(operation.content))
            elif operation.kind == "DELETE" and not referenced:
                target = Path(settings.MEDIA_ROOT).resolve() / operation.name
                if target.parent.resolve() != Path(settings.MEDIA_ROOT).resolve() / "covers":
                    raise OSError("Unsafe media destination")
                target.unlink(missing_ok=True)
            operation.delete(using=using)
            done += 1
    return done


def flush_safely(using):
    try:
        flush_media(using)
    except (OSError, DatabaseError, ValueError):
        # The durable operation remains for retry. Don't log file contents,
        # paths or arbitrary exception strings.
        logger.error("cover_publish_retry_required")
