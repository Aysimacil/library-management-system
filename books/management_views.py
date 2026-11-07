"""Permission-scoped catalog screens; circulation remains the status owner."""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods

from .forms import (
    AuthorManagementForm, BookManagementForm, CategoryManagementForm,
    CopyManagementForm, ShelfManagementForm,
)
from .models import Author, Book, BookCopy, Category
from .views import BookList


def staff_permission(codename):
    def decorate(view):
        @login_required
        @permission_required(f"books.{codename}", raise_exception=True)
        @wraps(view)
        def protected(request, *args, **kwargs):
            if not request.user.is_staff:
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return protected
    return decorate


@method_decorator(staff_permission("view_book"), name="dispatch")
class CatalogManagement(BookList):
    template_name = "books/manage/list.html"


def book_form(request, pk=None):
    book = get_object_or_404(Book, pk=pk) if pk is not None else None
    form = BookManagementForm((request.POST if request.method == "POST" else None), request.FILES or None, instance=book)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            book = form.save()
        messages.success(request, "Kitap kaydedildi. Fiziksel kopyaları aşağıdan yönetebilirsiniz.")
        return redirect("books:manage-detail", pk=book.pk)
    return render(request, "books/manage/book_form.html", {"form": form, "book": book})


@staff_permission("add_book")
@require_http_methods(["GET", "POST"])
def book_create(request):
    return book_form(request)


@staff_permission("change_book")
@require_http_methods(["GET", "POST"])
def book_edit(request, pk):
    return book_form(request, pk)


@staff_permission("view_book")
def book_detail(request, pk):
    from .views import catalog_books
    book = get_object_or_404(catalog_books(), pk=pk)
    return render(request, "books/manage/detail.html", {
        "book": book, "copies": book.copies.all() if request.user.has_perm("books.view_bookcopy") else [],
    })


@staff_permission("add_bookcopy")
@require_http_methods(["GET", "POST"])
def copy_create(request, pk):
    book = get_object_or_404(Book, pk=pk)
    copy = BookCopy(book=book)
    form = CopyManagementForm((request.POST if request.method == "POST" else None), instance=copy)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Fiziksel kopya eklendi.")
        return redirect("books:manage-detail", pk=book.pk)
    return render(request, "books/manage/copy_form.html", {"form": form, "book": book, "copy": None})


@staff_permission("change_bookcopy")
@require_http_methods(["GET", "POST"])
def shelf_edit(request, pk):
    # Lock the same physical row as circulation. Never save a stale status,
    # inventory code or book relation received from a metadata form.
    with transaction.atomic():
        copies = BookCopy.objects.select_for_update() if request.method == "POST" else BookCopy.objects
        copy = get_object_or_404(copies, pk=pk)
        form = ShelfManagementForm((request.POST if request.method == "POST" else None), instance=copy)
        if request.method == "POST" and form.is_valid():
            copy = form.save(commit=False)
            copy.save(update_fields=["shelf_location", "updated_at"])
            messages.success(request, "Raf konumu güncellendi.")
            return redirect("books:manage-detail", pk=copy.book_id)
    return render(request, "books/manage/copy_form.html", {"form": form, "book": copy.book, "copy": copy})


TAXONOMY = {
    "authors": (Author, AuthorManagementForm, "author", "Yazarlar", "Yazar"),
    "categories": (Category, CategoryManagementForm, "category", "Kategoriler", "Kategori"),
}


def taxonomy(request, kind, pk=None, create=False):
    if kind not in TAXONOMY:
        raise Http404
    model, form_class, codename, heading, singular = TAXONOMY[kind]
    action = "add" if create else "change" if pk is not None else "view"

    @staff_permission(f"{action}_{codename}")
    @require_http_methods(["GET", "POST"] if action != "view" else ["GET"])
    def screen(request):
        if action == "view":
            from django.core.paginator import Paginator
            entries = model.objects.all()
            q = request.GET.get("q", "").strip()[:200]
            if q:
                from .search import fold_text, searchable_text
                entries = entries.alias(search_name=searchable_text("name")).filter(search_name__contains=fold_text(q))
            page = Paginator(entries, 24).get_page(request.GET.get("page"))
            return render(request, "books/manage/taxonomy.html", {
                "heading": heading, "kind": kind, "page_obj": page, "q": q,
                "can_add": request.user.has_perm(f"books.add_{codename}"),
                "can_change": request.user.has_perm(f"books.change_{codename}"),
            })
        entry = get_object_or_404(model, pk=pk) if pk is not None else None
        form = form_class((request.POST if request.method == "POST" else None), instance=entry)
        if request.method == "POST" and form.is_valid():
            form.save()
            messages.success(request, f"{singular} kaydedildi.")
            return redirect("books:manage-taxonomy", kind=kind)
        return render(request, "books/manage/taxonomy_form.html", {
            "form": form, "heading": singular, "kind": kind, "entry": entry,
        })
    return screen(request)
