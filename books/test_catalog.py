from django.test import TestCase
from django.urls import reverse

from .models import Book, BookCopy


class CatalogScreenTests(TestCase):
    def test_empty_and_paginated_catalog(self):
        url = reverse("books:list")
        self.assertContains(self.client.get(url), "kitap bulunamadı")
        Book.objects.bulk_create([Book(title=f"Kitap {n:02}") for n in range(13)])
        last = Book.objects.get(title="Kitap 12")
        BookCopy.objects.create(book=last, inventory_code="K-12")
        response = self.client.get(url, {"page": 2})
        self.assertContains(response, last.title)
        self.assertContains(response, "1 / 1 kopya müsait")

    def test_detail_link_and_missing_book(self):
        book = Book.objects.create(title="Ada", description="Bir yolculuk")
        link = reverse("books:detail", args=[book.pk])
        self.assertContains(self.client.get(reverse("books:list")), link)
        self.assertContains(self.client.get(link), book.description)
        self.assertEqual(self.client.get(reverse("books:detail", args=[book.pk + 1])).status_code, 404)

    def test_combined_search_preserves_filters_and_distinct_counts(self):
        from .models import Author, Category

        authors = [Author.objects.create(name=f"Deniz {n}") for n in (1, 2)]
        cat = Category.objects.create(name="Roman")
        for n in range(14):
            book = Book.objects.create(title=f"Ada {n:02}", publication_year=2000 + n)
            book.authors.set(authors)
            book.categories.add(cat)
            if n:
                BookCopy.objects.create(book=book, inventory_code=str(n))
        params = {"q": "Deniz", "category": cat.pk, "available": "1", "sort": "year"}
        response = self.client.get(reverse("books:list"), params)
        self.assertEqual(response.context["paginator"].count, 13)
        self.assertEqual(response.context["books"][0].title, "Ada 13")
        self.assertEqual(response.context["books"][0].available, 1)
        self.assertContains(response, "q=Deniz&amp;category=")
        second = self.client.get(reverse("books:list"), {**params, "page": 2})
        self.assertEqual([b.title for b in second.context["books"]], ["Ada 01"])
