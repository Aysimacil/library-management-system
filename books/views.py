from django.db.models import Count, Q
from django.views.generic import DetailView, ListView

from .models import Book, BookCopy


def catalog_books():
    return Book.objects.prefetch_related("authors", "categories").annotate(
        total=Count("copies", distinct=True),
        available=Count("copies", filter=Q(copies__status=BookCopy.Status.AVAILABLE), distinct=True),
    )


class BookList(ListView):
    template_name = "books/book_list.html"
    paginate_by = 12
    context_object_name = "books"

    def get_queryset(self):
        return catalog_books().order_by("title", "pk")


class BookDetail(DetailView):
    template_name = "books/book_detail.html"
    context_object_name = "book"

    def get_queryset(self):
        return catalog_books()
