from django.db.models import Count, F, Q
from django.views.generic import DetailView, ListView

from .models import Book, BookCopy, Category


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
        params = self.request.GET
        books = catalog_books()
        term = params.get("q", "").strip()
        if term:
            books = books.filter(Q(title__icontains=term) | Q(authors__name__icontains=term) | Q(isbn__icontains=term))
        category = params.get("category", "")
        if category:
            if not category.isascii() or not category.isdecimal() or len(category) > 18:
                return books.none()
            books = books.filter(categories__pk=int(category))
        if params.get("available") == "1":
            books = books.filter(available__gt=0)
        sort = params.get("sort")
        if sort == "year":
            return books.order_by(F("publication_year").desc(nulls_last=True), "title", "pk")
        return books.order_by("title", "pk")

    def get_context_data(self, **kwargs):
        return super().get_context_data(categories=Category.objects.all(), **kwargs)


class BookDetail(DetailView):
    template_name = "books/book_detail.html"
    context_object_name = "book"

    def get_queryset(self):
        return catalog_books()
