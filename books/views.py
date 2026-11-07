from django.db.models import Count, Exists, F, OuterRef, Q
from django.http import FileResponse, Http404
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views.decorators.http import require_safe
from .forms import CatalogFilterForm
from django.views.generic import DetailView, ListView

from .models import Book, BookCopy, Category


from .search import TURKISH_CAPITALS, searchable_text


def catalog_books():
    return Book.objects.prefetch_related("authors", "categories").annotate(
        total=Count("copies", distinct=True),
        available=Count("copies", filter=Q(copies__status=BookCopy.Status.AVAILABLE), distinct=True),
    )


class BookList(ListView):
    template_name = "books/book_list.html"
    paginate_by = 12
    context_object_name = "books"

    @cached_property
    def filters(self):
        return CatalogFilterForm(self.request.GET)

    def get_queryset(self):
        if not self.filters.is_valid():
            return catalog_books().none()
        params = self.filters.cleaned_data
        books = catalog_books()
        term = params.get("q", "")
        if term:
            folded = term.translate(str.maketrans(TURKISH_CAPITALS)).lower()
            matching_codes = BookCopy.objects.filter(book_id=OuterRef('pk'), inventory_code__icontains=term)
            books = books.alias(
                search_title=searchable_text("title"),
                search_author=searchable_text("authors__name"),
            ).filter(
                Q(search_title__contains=folded)
                | Q(search_author__contains=folded)
                | Q(isbn__icontains=term)
                | Exists(matching_codes)
            )
        if params.get("category"):
            books = books.filter(categories=params["category"])
        if params.get("author"):
            books = books.filter(authors=params["author"])
        if params.get("year_from"):
            books = books.filter(publication_year__gte=params["year_from"])
        if params.get("year_to"):
            books = books.filter(publication_year__lte=params["year_to"])
        if params.get("available"):
            books = books.filter(available__gt=0)
        sort = params.get("sort")
        if sort in {"year", "oldest"}:
            order = F("publication_year").desc(nulls_last=True) if sort == "year" else F("publication_year").asc(nulls_last=True)
            return books.order_by(order, "title", "pk")
        return books.order_by("-title" if sort == "title_desc" else "title", "pk")

    def get_context_data(self, **kwargs):
        return super().get_context_data(filters=self.filters, **kwargs)


class BookDetail(DetailView):
    template_name = "books/book_detail.html"
    context_object_name = "book"

    def get_queryset(self):
        return catalog_books()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["can_request"] = user.is_authenticated and user.groups.filter(name="Üye").exists()
        if user.has_perm("circulation.issue_loan"):
            context["available_copies"] = self.object.copies.filter(status=BookCopy.Status.AVAILABLE)
        context["related_books"] = catalog_books().filter(categories__in=self.object.categories.all()).exclude(pk=self.object.pk).order_by("title", "pk")[:4]
        return context


@require_safe
def cover(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if not book.cover:
        raise Http404
    from .models import CoverOperation
    pending = CoverOperation.objects.filter(name=book.cover.name, kind="WRITE").first()
    if pending is not None:
        stream = ContentFile(bytes(pending.content))
    else:
        try:
            stream = book.cover.open("rb")
        except OSError:
            # The commit callback may have published between the two reads.
            pending = CoverOperation.objects.filter(name=book.cover.name, kind="WRITE").first()
            if pending is None:
                raise Http404 from None
            stream = ContentFile(bytes(pending.content))
    response = FileResponse(stream, content_type="image/jpeg")
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "public, max-age=3600"
    return response
