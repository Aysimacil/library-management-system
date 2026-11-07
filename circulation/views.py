from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.roles import MEMBER
from books.models import Book, BookCopy
from .forms import IssueForm
from .models import CheckoutRequest, Fine, Loan
from .services import borrow_book, check_account, pay_fine, renew_loan, return_book


@login_required
@permission_required("circulation.view_loan", raise_exception=True)
def desk(request):
    q = request.GET.get("q", "").strip()
    all_active = Loan.objects.filter(returned_at=None)
    overview = {
        "active": all_active.count(),
        "overdue": all_active.filter(due_date__lt=timezone.localdate()).count(),
        "pending": CheckoutRequest.objects.filter(status="PENDING").count(),
    }
    active = Loan.objects.filter(returned_at=None).select_related("member", "copy__book")
    copies = BookCopy.objects.select_related("book")
    members = get_user_model().objects.filter(groups__name=MEMBER, is_active=True)
    if q:
        active = active.filter(Q(member__username__icontains=q) | Q(copy__inventory_code__icontains=q) | Q(copy__book__title__icontains=q))
        copies = copies.filter(Q(inventory_code__icontains=q) | Q(book__title__icontains=q))
        members = members.filter(username__icontains=q)
    if request.GET.get("overdue"):
        active = active.filter(due_date__lt=timezone.localdate())
    fines = Fine.objects.select_related("loan__member", "loan__copy__book").filter(paid_at=None)
    if q:
        fines = fines.filter(Q(loan__member__username__icontains=q) | Q(loan__copy__inventory_code__icontains=q))
    return render(request, "circulation/desk.html", {
        "form": IssueForm(initial={"inventory_code": request.GET.get("copy", ""), "username": request.GET.get("member", "")}),
        "loans": active[:100], "copies": copies[:25] if q else [], "members": members[:25] if q else [],
        "fines": fines[:100] if request.user.has_perm("circulation.view_fine") else [],
        "pending": CheckoutRequest.objects.filter(status="PENDING").select_related("member", "book").order_by("created_at")[:100],
        "today": timezone.localdate(), "overview": overview,
    })


@login_required
@permission_required("circulation.issue_loan", raise_exception=True)
@require_POST
def issue(request):
    form = IssueForm(request.POST)
    if form.is_valid():
        try:
            borrow_book(member_id=form.cleaned_data["username"].pk, copy_id=form.cleaned_data["inventory_code"].pk)
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(request, "Teslim kaydedildi.")
            return redirect("circulation:desk")
    return render(request, "circulation/issue.html", {"form": form}, status=400)


def report_operation(request, operation, success, **kwargs):
    try:
        operation(**kwargs)
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
    else:
        messages.success(request, success)


@login_required
@permission_required("circulation.return_loan", raise_exception=True)
@require_POST
def accept_return(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    report_operation(request, return_book, "İade kaydedildi.", loan_id=loan.pk)
    return redirect("circulation:desk")


@login_required
@permission_required("circulation.renew_loan", raise_exception=True)
@require_POST
def extend(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    report_operation(request, renew_loan, "Vade uzatıldı.", loan_id=loan.pk)
    return redirect("circulation:desk")


@login_required
@require_POST
def member_renew(request, pk):
    loan = get_object_or_404(Loan, pk=pk, member=request.user)
    report_operation(request, renew_loan, "Vade uzatıldı.", loan_id=loan.pk)
    return redirect("accounts:profile")


@login_required
@permission_required("circulation.pay_fine", raise_exception=True)
@require_POST
def payment(request, pk):
    fine = get_object_or_404(Fine, pk=pk)
    report_operation(request, pay_fine, "Demo ödeme kaydedildi.", fine_id=fine.pk, actor=request.user)
    return redirect("circulation:desk")


@login_required
@require_POST
@transaction.atomic
def request_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    member = get_user_model().objects.select_for_update().get(pk=request.user.pk)
    if not member.groups.filter(name=MEMBER).exists():
        raise PermissionDenied
    try:
        check_account(member.pk, timezone.localdate())
        if not book.available_copy_count or member.loans.filter(returned_at=None).count() >= 3:
            raise ValidationError("Müsait kopya veya aktif ödünç hakkı bulunmuyor.")
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
    else:
        CheckoutRequest.objects.get_or_create(member=member, book=book, status="PENDING")
        messages.success(request, "Talebiniz teslim masasına iletildi.")
    return redirect("accounts:profile")


@login_required
@require_POST
def cancel_request(request, pk):
    entry = get_object_or_404(CheckoutRequest, pk=pk, member=request.user)
    CheckoutRequest.objects.filter(pk=entry.pk, status="PENDING").update(status="CANCELLED")
    return redirect("accounts:profile")
