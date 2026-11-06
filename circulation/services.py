from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from accounts.roles import MEMBER
from books.models import BookCopy
from .models import Fine, Loan


def open_day(day):
    while day.weekday() >= 5 or day.isoformat() in settings.LIBRARY_CLOSED_DATES:
        day += timedelta(days=1)
    return day


def calculate_fine(loan, as_of=None):
    day = timezone.localdate(loan.returned_at) if loan.returned_at else (as_of or timezone.localdate())
    days = max((day - loan.due_date).days, 0)
    return min(loan.fine_cap, Decimal(days) * loan.daily_rate)


def check_account(member_id, today):
    if Fine.objects.filter(loan__member_id=member_id, paid_at__isnull=True).exists():
        raise ValidationError("Üyenin ödenmemiş cezası var.")
    if Loan.objects.filter(member_id=member_id, returned_at__isnull=True, due_date__lt=today).exists():
        raise ValidationError("Üyenin gecikmiş bir ödüncü var.")


@transaction.atomic
def borrow_book(*, member_id, copy_id):
    member = get_user_model().objects.select_for_update().get(pk=member_id)
    if not member.is_active or not member.groups.filter(name=MEMBER).exists():
        raise ValidationError("Teslim için etkin bir üye seçin.")
    copy = BookCopy.objects.select_for_update().get(pk=copy_id)
    now = timezone.now()
    today = timezone.localdate(now)
    check_account(member_id, today)
    if member.loans.filter(returned_at__isnull=True).count() >= 3:
        raise ValidationError("Üye üç aktif ödünç sınırına ulaştı.")
    if copy.status != BookCopy.Status.AVAILABLE or copy.loans.filter(returned_at__isnull=True).exists():
        raise ValidationError("Bu kopya zaten ödünçte.")
    loan = Loan.objects.create(member=member, copy=copy, issued_at=now, due_date=open_day(today + timedelta(days=14)))
    copy.status = BookCopy.Status.ON_LOAN
    copy.save(update_fields=["status", "updated_at"])
    return loan


def locked_loan(loan_id):
    # Same lock order as issuance: member, physical copy, loan.
    member_id, copy_id = Loan.objects.values_list("member_id", "copy_id").get(pk=loan_id)
    get_user_model().objects.select_for_update().get(pk=member_id)
    copy = BookCopy.objects.select_for_update().get(pk=copy_id)
    loan = Loan.objects.select_for_update().get(pk=loan_id)
    return loan, copy


@transaction.atomic
def return_book(*, loan_id):
    loan, copy = locked_loan(loan_id)
    if loan.returned_at is not None:
        return loan
    loan.returned_at = timezone.now()
    loan.save(update_fields=["returned_at"])
    amount = calculate_fine(loan)
    if amount:
        Fine.objects.create(loan=loan, amount=amount)
    copy.status = BookCopy.Status.AVAILABLE
    copy.save(update_fields=["status", "updated_at"])
    return loan


@transaction.atomic
def renew_loan(*, loan_id):
    loan, _ = locked_loan(loan_id)
    if loan.returned_at or loan.renewal_count:
        raise ValidationError("Bu ödünç için uzatma yapılamaz.")
    check_account(loan.member_id, timezone.localdate())
    loan.previous_due_date = loan.due_date
    loan.due_date = open_day(loan.due_date + timedelta(days=7))
    loan.renewal_count = 1
    loan.renewed_at = timezone.now()
    loan.save(update_fields=["due_date", "previous_due_date", "renewal_count", "renewed_at"])
    return loan


@transaction.atomic
def pay_fine(*, fine_id, actor):
    if not actor.has_perm("circulation.pay_fine"):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    fine = Fine.objects.select_for_update().get(pk=fine_id)
    if fine.paid_at is None:
        fine.paid_at = timezone.now()
        fine.paid_by = actor
        fine.save(update_fields=["paid_at", "paid_by"])
    return fine
