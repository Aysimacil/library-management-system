from django.contrib import admin
from django.db.models import Count, Q

from .models import Author, Book, BookCopy, Category


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "isbn", "author_names", "publication_year", "copy_total", "available_total"]
    search_fields = ["title", "isbn", "authors__name"]
    list_filter = ["categories"]
    autocomplete_fields = ["authors", "categories"]
    readonly_fields = ["created_at", "updated_at"]
    list_per_page = 50

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("authors").annotate(
            _copy_total=Count("copies", distinct=True),
            _available_total=Count(
                "copies", filter=Q(copies__status=BookCopy.Status.AVAILABLE), distinct=True,
            ),
        )

    @admin.display(description="Yazarlar")
    def author_names(self, obj):
        return ", ".join(author.name for author in obj.authors.all())

    @admin.display(description="Toplam kopya", ordering="_copy_total")
    def copy_total(self, obj):
        return obj._copy_total

    @admin.display(description="Müsait kopya", ordering="_available_total")
    def available_total(self, obj):
        return obj._available_total


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ["inventory_code", "book", "shelf_location", "status"]
    search_fields = ["inventory_code", "book__title", "book__isbn"]
    list_filter = ["status"]
    autocomplete_fields = ["book"]
    readonly_fields = ["status", "created_at", "updated_at"]
    list_select_related = ["book"]
    list_per_page = 50
    # Per-copy deletion checks must not be bypassed through bulk deletion.
    actions = None

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if obj and obj.status == BookCopy.Status.ON_LOAN:
            return [*fields, "book", "inventory_code"]
        return fields

    def has_delete_permission(self, request, obj=None):
        allowed = super().has_delete_permission(request, obj)
        return allowed and (obj is None or obj.status == BookCopy.Status.AVAILABLE)
