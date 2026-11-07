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

    def test_demo_can_be_run_twice(self):
        from django.core.management import call_command
        from io import StringIO

        for _ in range(2):
            call_command("seed_catalog", stdout=StringIO())
        self.assertEqual(Book.objects.count(), 3)
        self.assertEqual(BookCopy.objects.count(), 3)

    def test_return_from_detail_keeps_filtered_page(self):
        from html.parser import HTMLParser

        class Links(HTMLParser):
            def __init__(self):
                super().__init__()
                self.urls = []

            def handle_starttag(self, tag, attrs):
                if tag == "a":
                    self.urls.append(dict(attrs)["href"])

        Book.objects.bulk_create([Book(title=f"Ada & Deniz {i:02}") for i in range(13)])
        listing = self.client.get(reverse("books:list"), {"q": "Ada & Deniz", "page": 2})
        links = Links()
        links.feed(listing.content.decode())
        detail = self.client.get(next(url for url in links.urls if url.startswith("/kitap/")))
        self.assertContains(detail, "Ada &amp; Deniz 12")
        links = Links()
        links.feed(detail.content.decode())
        restored = self.client.get(next(url for url in links.urls if url.startswith("/?")))
        self.assertEqual(restored.wsgi_request.GET, listing.wsgi_request.GET)
        self.assertEqual(restored.context["page_obj"].number, 2)
        self.assertEqual([b.title for b in restored.context["books"]], ["Ada & Deniz 12"])

    def test_turkish_case_in_title_and_author_search(self):
        from .models import Author

        book = Book.objects.create(title="Gökyüzü ve Işık")
        book.authors.add(Author.objects.create(name="İpek Çağrı"))
        Book.objects.create(title="Başka kitap")
        for query in ["GÖKYÜZÜ", "ışık", "ipek", "ÇAĞRI"]:
            with self.subTest(query=query):
                response = self.client.get(reverse("books:list"), {"q": query})
                self.assertEqual([item.pk for item in response.context["books"]], [book.pk])


class CatalogSearchRegressionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from .models import Author, Category

        cls.author = Author.objects.create(name="İpek Çağrı")
        cls.other_author = Author.objects.create(name="Deniz Örnek")
        cls.category = Category.objects.create(name="Mühendislik")
        cls.other_category = Category.objects.create(name="Bilim")
        cls.book = Book.objects.create(
            title="Gökyüzü ve Işık", isbn="9780306406157",
            publication_year=2001, description="Yıldızlar üzerine bir deneme.",
        )
        cls.book.authors.set([cls.author, cls.other_author])
        cls.book.categories.set([cls.category, cls.other_category])
        for index in range(3):
            BookCopy.objects.create(
                book=cls.book, inventory_code=f"S1-00{index + 1}",
                status=BookCopy.Status.ON_LOAN if index == 2 else BookCopy.Status.AVAILABLE,
            )
        cls.unrelated = Book.objects.create(title="Başka Deneme", publication_year=2001)

    def test_category_name_search_finds_only_the_category_match(self):
        response = self.client.get(reverse("books:list"), {"q": "Mühendislik"})
        self.assertEqual([book.pk for book in response.context["books"]], [self.book.pk])
        self.assertEqual(response.context["paginator"].count, 1)
        self.assertNotContains(response, self.unrelated.title)

    def test_title_search(self):
        response = self.client.get(reverse("books:list"), {"q": "GÖKYÜZÜ"})
        self.assertEqual([book.pk for book in response.context["books"]], [self.book.pk])
        self.assertEqual(response.context["paginator"].count, 1)

    def test_author_search(self):
        response = self.client.get(reverse("books:list"), {"q": "ÇAĞRI"})
        self.assertEqual([book.pk for book in response.context["books"]], [self.book.pk])
        self.assertEqual(response.context["paginator"].count, 1)

    def test_turkish_category_case_search(self):
        for category_name, query in [
            ("Mühendislik", "MÜHENDİSLİK"),
            ("IŞIK VE ÖLÇÜM", "ışık ve ölçüm"),
            ("Çığ Araştırmaları", "ÇIĞ ARAŞTIRMALARI"),
        ]:
            with self.subTest(category=category_name, query=query):
                self.category.name = category_name
                self.category.save(update_fields=["name"])
                response = self.client.get(reverse("books:list"), {"q": query})
                self.assertEqual([book.pk for book in response.context["books"]], [self.book.pk])
                self.assertEqual(response.context["paginator"].count, 1)

    def test_isbn_search(self):
        response = self.client.get(reverse("books:list"), {"q": "9780306406157"})
        self.assertEqual([book.pk for book in response.context["books"]], [self.book.pk])
        self.assertEqual(response.context["paginator"].count, 1)

    def test_inventory_search_does_not_limit_stock_to_matching_copy(self):
        response = self.client.get(reverse("books:list"), {"q": "S1-002"})
        self.assertEqual([book.pk for book in response.context["books"]], [self.book.pk])
        self.assertEqual(response.context["paginator"].count, 1)
        result = response.context["books"][0]
        self.assertEqual((result.total, result.available), (3, 2))

    def test_multiple_matching_authors_and_categories_return_one_book(self):
        # Both authors and both categories match, creating a many-to-many
        # fan-out if text-search joins are added without preserving grouping.
        for author in (self.author, self.other_author):
            author.name = "Ortak " + author.name
            author.save(update_fields=["name"])
        for category in (self.category, self.other_category):
            category.name = "Ortak " + category.name
            category.save(update_fields=["name"])
        response = self.client.get(reverse("books:list"), {"q": "Ortak"})
        self.assertEqual([book.pk for book in response.context["books"]], [self.book.pk])
        self.assertEqual(response.context["paginator"].count, 1)
        result = response.context["books"][0]
        self.assertEqual((result.total, result.available), (3, 2))

    def test_search_combines_category_author_year_and_availability_filters(self):
        from .models import Author

        different_author = Author.objects.create(name="Farklı Yazar")
        for index, mismatch in enumerate(("category", "author", "year", "stock")):
            book = Book.objects.create(
                title=f"Elenecek {mismatch}",
                publication_year=1990 if mismatch == "year" else 2001,
            )
            book.authors.add(different_author if mismatch == "author" else self.author)
            # Search matches engineering, while the independent category
            # filter requires science on the same book, not the same M2M row.
            book.categories.add(self.category)
            if mismatch != "category":
                book.categories.add(self.other_category)
            BookCopy.objects.create(
                book=book, inventory_code=f"FILTER-{index}",
                status=BookCopy.Status.ON_LOAN if mismatch == "stock" else BookCopy.Status.AVAILABLE,
            )
        response = self.client.get(reverse("books:list"), {
            "q": "Mühendislik", "category": self.other_category.pk,
            "author": self.author.pk, "year_from": 2000, "year_to": 2005,
            "available": "1", "sort": "year",
        })
        self.assertEqual([book.pk for book in response.context["books"]], [self.book.pk])
        self.assertEqual(response.context["paginator"].count, 1)
        result = response.context["books"][0]
        self.assertEqual((result.total, result.available), (3, 2))

    def test_category_search_counts_all_copies_and_only_available_stock(self):
        response = self.client.get(reverse("books:list"), {"q": "Mühendislik"})
        self.assertEqual([book.pk for book in response.context["books"]], [self.book.pk])
        result = response.context["books"][0]
        self.assertEqual((result.total, result.available), (3, 2))
        self.assertContains(response, "2 / 3 kopya müsait")

    def test_category_search_pagination_and_detail_return_preserve_filters(self):
        from html.parser import HTMLParser

        class Links(HTMLParser):
            def __init__(self):
                super().__init__()
                self.urls = []

            def handle_starttag(self, tag, attrs):
                if tag == "a" and "href" in dict(attrs):
                    self.urls.append(dict(attrs)["href"])

        expected = []
        for index in range(13):
            book = Book.objects.create(title=f"Sayfa {index:02}", publication_year=2010)
            book.authors.set([self.author, self.other_author])
            book.categories.set([self.category, self.other_category])
            for copy in range(3):
                BookCopy.objects.create(book=book, inventory_code=f"PAGE-{index}-{copy}")
            expected.append(book.pk)
        params = {
            "q": "Mühendislik", "category": self.other_category.pk,
            "author": self.author.pk, "year_from": "2010", "year_to": "2010",
            "available": "1", "sort": "title",
        }
        first = self.client.get(reverse("books:list"), params)
        self.assertEqual(first.context["paginator"].count, 13)
        self.assertEqual([book.pk for book in first.context["books"]], expected[:12])
        self.assertTrue(all((book.total, book.available) == (3, 3) for book in first.context["books"]))
        second = self.client.get(reverse("books:list"), {**params, "page": "2"})
        self.assertEqual(second.context["paginator"].count, 13)
        self.assertEqual([book.pk for book in second.context["books"]], expected[12:])
        self.assertEqual((second.context["books"][0].total, second.context["books"][0].available), (3, 3))
        links = Links()
        links.feed(second.content.decode())
        detail = self.client.get(next(url for url in links.urls if url.startswith("/kitap/")))
        self.assertEqual(detail.context["book"].pk, expected[-1])
        self.assertEqual((detail.context["book"].total, detail.context["book"].available), (3, 3))
        links = Links()
        links.feed(detail.content.decode())
        restored = self.client.get(next(url for url in links.urls if url.startswith("/?")))
        self.assertEqual(restored.wsgi_request.GET, second.wsgi_request.GET)
        self.assertEqual(restored.context["page_obj"].number, 2)
        self.assertEqual(restored.context["paginator"].count, 13)
        self.assertEqual([book.pk for book in restored.context["books"]], expected[12:])
