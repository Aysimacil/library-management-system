import logging
from pathlib import Path
import tempfile

from django.conf import settings
from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.views.decorators.http import require_safe

logger = logging.getLogger("library.health")


@require_safe
def live(request):
    response = JsonResponse({"status": "ok"})
    response["Cache-Control"] = "no-store"
    return response


@require_safe
def ready(request):
    checks = {"database": False, "media": False, "static": False}
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            connected = cursor.fetchone()[0] == 1
        from books.models import Book, CoverOperation
        Book.objects.exists()
        CoverOperation.objects.exists()
        checks["database"] = connected
    except DatabaseError:
        pass
    try:
        root = Path(settings.MEDIA_ROOT)
        if settings.MEDIA_PROBE_ON_READINESS:
            with tempfile.TemporaryFile(dir=root) as stream:
                stream.write(b"health")
                stream.flush()
                stream.seek(0)
                checks["media"] = stream.read() == b"health"
        else:
            checks["media"] = root.is_dir()
    except OSError:
        pass
    if settings.PRODUCTION:
        checks["static"] = (Path(settings.STATIC_ROOT) / "css/catalog.css").is_file()
    else:
        from django.contrib.staticfiles import finders
        checks["static"] = bool(finders.find("css/catalog.css"))
    healthy = all(checks.values())
    if not healthy:
        logger.warning("readiness_failed")
    response = JsonResponse({"status": "ok" if healthy else "unavailable", "checks": checks}, status=200 if healthy else 503)
    response["Cache-Control"] = "no-store"
    return response
