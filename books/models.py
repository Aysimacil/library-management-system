from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, router, transaction
from django.db.models import Q

from .validators import validate_isbn
from .covers import cover_path, prepare_cover, validate_cover


class Author(models.Model):
    name = models.CharField("Yazar adı", max_length=200, db_index=True)
    biography = models.TextField("Biyografi", blank=True)

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "Yazar"
        verbose_name_plural = "Yazarlar"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField("Kategori adı", max_length=100, unique=True)
    description = models.TextField("Açıklama", blank=True)

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField("Kitap adı", max_length=255, db_index=True)
    isbn = models.CharField(
        "ISBN", max_length=13, blank=True, default="", validators=[validate_isbn],
        help_text="Tire veya boşluk olmadan ISBN-10 ya da ISBN-13 girin.",
    )
    cover = models.ImageField("Kapak görseli", upload_to=cover_path, blank=True, validators=[validate_cover])
    authors = models.ManyToManyField(Author, related_name="books", verbose_name="Yazarlar")
    categories = models.ManyToManyField(
        Category, related_name="books", blank=True, verbose_name="Kategoriler",
    )
    publication_year = models.PositiveSmallIntegerField(
        "Yayın yılı", null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(9999)],
    )
    description = models.TextField("Açıklama", blank=True)
    created_at = models.DateTimeField("Oluşturulma zamanı", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme zamanı", auto_now=True)

    class Meta:
        ordering = ["title", "pk"]
        verbose_name = "Kitap"
        verbose_name_plural = "Kitaplar"
        constraints = [
            models.UniqueConstraint(
                fields=["isbn"], condition=~Q(isbn=""), name="book_unique_nonempty_isbn",
            ),
            models.CheckConstraint(
                condition=Q(publication_year__isnull=True)
                | Q(publication_year__gte=1, publication_year__lte=9999),
                name="book_valid_publication_year",
            ),
        ]

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        if "cover" in field_names:
            instance._original_cover = instance.cover.name
        return instance

    def refresh_from_db(self, using=None, fields=None, from_queryset=None):
        super().refresh_from_db(using=using, fields=fields, from_queryset=from_queryset)
        if fields is None or "cover" in fields:
            self._original_cover = self.cover.name

    def save(self, *args, **kwargs):
        from .media_lifecycle import enqueue_delete, flush_safely, media_lock
        using = kwargs.get("using") or router.db_for_write(type(self), instance=self)
        fields = kwargs.get("update_fields")
        if fields is not None and "cover" not in fields:
            return super().save(*args, **kwargs)
        with media_lock(using):
            previous = type(self).objects.using(using).filter(pk=self.pk).values_list("cover", flat=True).first() if self.pk else ""
            content = None
            original = getattr(self, "_original_cover", None)
            if self.cover._committed and original is not None and self.cover.name == original and previous != original:
                self.cover = previous or ""
            if self.cover and not self.cover._committed:
                content = prepare_cover(self.cover).read()
                self.cover = cover_path(self, "")
            super().save(*args, **kwargs)
            self._original_cover = self.cover.name
            if content is not None:
                CoverOperation.objects.using(using).create(name=self.cover.name, kind="WRITE", content=content)
                transaction.on_commit(lambda: flush_safely(using), using=using)
            if previous and previous != self.cover.name:
                enqueue_delete(previous, using)
        return None

    @property
    def available_copy_count(self):
        """Derive availability from physical copies instead of a mutable counter."""
        return self.copies.filter(status=BookCopy.Status.AVAILABLE).count()

    def __str__(self):
        return self.title


class BookCopy(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Ödünç verilebilir"
        ON_LOAN = "ON_LOAN", "Ödünçte"

    book = models.ForeignKey(
        Book, on_delete=models.PROTECT, related_name="copies", verbose_name="Kitap",
    )
    inventory_code = models.CharField("Demirbaş kodu", max_length=50, unique=True)
    shelf_location = models.CharField("Raf konumu", max_length=100, blank=True)
    status = models.CharField(
        "Durum", max_length=10, choices=Status.choices,
        default=Status.AVAILABLE, editable=False,
    )
    created_at = models.DateTimeField("Oluşturulma zamanı", auto_now_add=True)
    updated_at = models.DateTimeField("Güncellenme zamanı", auto_now=True)

    class Meta:
        ordering = ["inventory_code", "pk"]
        verbose_name = "Fiziksel kopya"
        verbose_name_plural = "Fiziksel kopyalar"
        indexes = [models.Index(fields=["book", "status"], name="copy_book_status_idx")]
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=["AVAILABLE", "ON_LOAN"]),
                name="copy_valid_status",
            ),
        ]

    def __str__(self):
        return f"{self.inventory_code} — {self.book.title}"


class MediaLock(models.Model):
    """Serializes supported cover-reference writes, publishing and backup."""
    version = models.PositiveBigIntegerField(default=0)


class CoverOperation(models.Model):
    class Kind(models.TextChoices):
        WRITE = "WRITE"
        DELETE = "DELETE"

    name = models.CharField(max_length=255)
    kind = models.CharField(max_length=6, choices=Kind.choices)
    content = models.BinaryField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "kind"], name="unique_cover_operation"),
        ]
