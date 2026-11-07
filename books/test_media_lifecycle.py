from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.db import transaction
from django.test import TestCase, override_settings
from django.urls import reverse

from .media_lifecycle import flush_media
from .models import Book, CoverOperation
from .test_enhancements import upload


class MediaLifecycleTests(TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        context = override_settings(MEDIA_ROOT=directory.name)
        context.enable()
        self.addCleanup(context.disable)
        self.root = Path(directory.name)

    def book(self):
        with self.captureOnCommitCallbacks(execute=True):
            return Book.objects.create(title="Kalıcı kapak", cover=upload())

    def test_replace_and_clear_delete_only_after_commit(self):
        book = self.book()
        old = book.cover.name
        with self.captureOnCommitCallbacks(execute=True):
            book.cover = upload()
            book.save()
            self.assertTrue((self.root / old).exists())
            self.assertFalse((self.root / book.cover.name).exists())
        self.assertFalse((self.root / old).exists())
        self.assertTrue((self.root / book.cover.name).exists())
        latest = book.cover.name
        with self.captureOnCommitCallbacks(execute=True):
            book.cover = ""
            book.save()
        self.assertFalse((self.root / latest).exists())

    def test_outer_rollback_leaves_original_and_no_new_files(self):
        book = self.book()
        old = book.cover.name
        with self.captureOnCommitCallbacks(execute=True):
            with self.assertRaises(RuntimeError), transaction.atomic():
                book.cover = upload()
                book.save()
                proposed = book.cover.name
                raise RuntimeError("rollback")
        book.refresh_from_db()
        self.assertEqual(book.cover.name, old)
        self.assertTrue((self.root / old).exists())
        self.assertFalse((self.root / proposed).exists())
        self.assertFalse(CoverOperation.objects.exists())

    def test_failed_create_has_no_orphan(self):
        with self.captureOnCommitCallbacks(execute=True):
            with self.assertRaises(RuntimeError), transaction.atomic():
                book = Book.objects.create(title="Rollback", cover=upload())
                proposed = book.cover.name
                raise RuntimeError("rollback")
        self.assertFalse((self.root / proposed).exists())
        self.assertFalse(Book.objects.exists())
        self.assertFalse(CoverOperation.objects.exists())

    def test_shared_file_survives_until_last_reference_deleted(self):
        first = self.book()
        name = first.cover.name
        second = Book.objects.create(title="Paylaşılan", cover=name)
        with self.captureOnCommitCallbacks(execute=True):
            first.delete()
        self.assertTrue((self.root / name).exists())
        with self.captureOnCommitCallbacks(execute=True):
            Book.objects.filter(pk=second.pk).delete()
        self.assertFalse((self.root / name).exists())

    def test_storage_failure_retains_durable_content_and_serves_pending_image(self):
        with patch("books.media_lifecycle.publish", side_effect=OSError), self.assertLogs("library.media"):
            book = self.book()
        self.assertEqual(CoverOperation.objects.filter(kind="WRITE").count(), 1)
        response = self.client.get(reverse("books:cover", args=[book.pk]))
        self.assertTrue(b"".join(response.streaming_content).startswith(b"\xff\xd8"))
        self.assertEqual(flush_media(), 1)
        self.assertTrue((self.root / book.cover.name).exists())
        self.assertEqual(flush_media(), 0)

    def test_stale_metadata_save_keeps_new_cover(self):
        book = self.book()
        stale = Book.objects.get(pk=book.pk)
        with self.captureOnCommitCallbacks(execute=True):
            book.cover = upload()
            book.save()
        current = book.cover.name
        stale.description = "Metadata düzenlemesi"
        stale.save()
        stale.refresh_from_db()
        self.assertEqual(stale.cover.name, current)
        self.assertTrue((self.root / current).exists())

    def test_update_fields_excluding_cover_does_not_publish_upload(self):
        book = self.book()
        name = book.cover.name
        book.cover = upload()
        book.title = "Yeni başlık"
        book.save(update_fields=["title"])
        book.refresh_from_db()
        self.assertEqual(book.cover.name, name)
        self.assertFalse(CoverOperation.objects.exists())

    def test_delete_rollback_keeps_referenced_file(self):
        book = self.book()
        pk, name = book.pk, book.cover.name
        with self.captureOnCommitCallbacks(execute=True):
            with self.assertRaises(RuntimeError), transaction.atomic():
                Book.objects.filter(pk=pk).delete()
                raise RuntimeError("rollback")
        self.assertTrue(Book.objects.filter(pk=pk).exists())
        self.assertTrue((self.root / name).exists())
        self.assertFalse(CoverOperation.objects.exists())
