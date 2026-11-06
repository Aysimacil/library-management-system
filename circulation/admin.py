from django.contrib import admin

from .models import Fine, Loan


class LedgerAdmin(admin.ModelAdmin):
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Loan)
class LoanAdmin(LedgerAdmin):
    list_display = ["member", "copy", "issued_at", "due_date", "returned_at"]
    search_fields = ["member__username", "copy__inventory_code"]
    list_select_related = ["member", "copy__book"]


@admin.register(Fine)
class FineAdmin(LedgerAdmin):
    list_display = ["loan_id", "amount", "created_at", "paid_at", "paid_by"]
