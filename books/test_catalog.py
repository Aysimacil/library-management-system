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
