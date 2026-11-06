from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from .validators import validate_isbn


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
