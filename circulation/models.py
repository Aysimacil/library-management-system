from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Loan(models.Model):
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="loans")
    copy = models.ForeignKey("books.BookCopy", on_delete=models.PROTECT, related_name="loans")
    issued_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateField(db_index=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    renewal_count = models.PositiveSmallIntegerField(default=0)
    previous_due_date = models.DateField(null=True, blank=True)
    renewed_at = models.DateTimeField(null=True, blank=True)
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("5.00"))
    fine_cap = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("100.00"))

    class Meta:
        ordering = ["-issued_at", "-pk"]
        permissions = [
            ("issue_loan", "Kitap teslim edebilir"), ("return_loan", "İade alabilir"),
            ("renew_loan", "Süre uzatabilir"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["copy"], condition=Q(returned_at__isnull=True), name="one_open_loan_per_copy"),
            models.CheckConstraint(condition=Q(renewal_count__lte=1), name="loan_one_renewal"),
            models.CheckConstraint(condition=Q(returned_at__isnull=True) | Q(returned_at__gte=F("issued_at")), name="loan_return_after_issue"),
            models.CheckConstraint(condition=Q(daily_rate__gte=0, fine_cap__gte=0), name="loan_nonnegative_tariff"),
        ]


class Fine(models.Model):
    loan = models.OneToOneField(Loan, on_delete=models.PROTECT, related_name="fine")
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    paid_at = models.DateTimeField(null=True, blank=True)
    paid_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="recorded_payments", null=True, blank=True)

    class Meta:
        permissions = [("pay_fine", "Demo ödeme kaydedebilir")]
        constraints = [
            models.CheckConstraint(condition=Q(amount__gt=0), name="fine_positive_amount"),
            models.CheckConstraint(condition=Q(paid_at__isnull=True, paid_by__isnull=True) | Q(paid_at__isnull=False, paid_by__isnull=False), name="fine_payment_complete"),
        ]


class CheckoutRequest(models.Model):
    """An interest in a title, without holding or reserving a copy."""
    class Status(models.TextChoices):
        PENDING = "PENDING", "Bekliyor"
        FULFILLED = "FULFILLED", "Teslim edildi"
        CANCELLED = "CANCELLED", "İptal edildi"

    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    book = models.ForeignKey("books.Book", on_delete=models.PROTECT)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(default=timezone.now)
    loan = models.OneToOneField(Loan, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["member", "book"], condition=Q(status="PENDING"), name="one_pending_request_per_title"),
        ]
