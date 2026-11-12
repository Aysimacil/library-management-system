from io import BytesIO
import warnings
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile
from django.urls import reverse
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_COVER_BYTES = 4 * 1024 * 1024
MAX_COVER_PIXELS = 12_000_000


def cover_path(instance, filename):
    return f"covers/{uuid4().hex}.jpg"


def prepare_cover(upload):
    """Decode bounded raster input and produce a metadata-free JPEG."""
    try:
        upload.seek(0)
        data = upload.read(MAX_COVER_BYTES + 1)
        if len(data) > MAX_COVER_BYTES:
            raise ValidationError("Kapak en fazla 4 MB olabilir.")
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(data)) as image:
                if image.format not in {"JPEG", "PNG", "WEBP"}:
                    raise ValidationError("JPEG, PNG veya WebP kapak yükleyin.")
                if image.width * image.height > MAX_COVER_PIXELS:
                    raise ValidationError("Kapak en fazla 12 milyon piksel olabilir.")
                image.load()
                cleaned = ImageOps.exif_transpose(image).convert("RGB")
                cleaned.thumbnail((1200, 1600))
                output = BytesIO()
                cleaned.save(output, format="JPEG", quality=85)
        return ContentFile(output.getvalue(), name="cover.jpg")
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise ValidationError("Görsel okunamadı. Geçerli bir kapak yükleyin.") from None
    finally:
        upload.seek(0)


def validate_cover(upload):
    prepare_cover(upload)


# Keep admin's "current file" link on the same safe route as catalog covers.
class BookCoverFile(ImageFieldFile):
    @property
    def url(self):
        self._require_file()
        return reverse("books:cover", args=[self.instance.pk]) if self.instance.pk else ""


class BookCoverField(ImageField):
    attr_class = BookCoverFile

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Only runtime URL handling differs; the database schema stays ImageField.
        return name, "django.db.models.ImageField", args, kwargs
