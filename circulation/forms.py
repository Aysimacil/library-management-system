from django import forms
from django.contrib.auth import get_user_model

from accounts.roles import MEMBER
from books.models import BookCopy


class IssueForm(forms.Form):
    username = forms.CharField(label="Üye kullanıcı adı", max_length=150)
    inventory_code = forms.CharField(label="Demirbaş kodu", max_length=50)

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            return get_user_model().objects.get(username=username, is_active=True, groups__name=MEMBER)
        except get_user_model().DoesNotExist:
            raise forms.ValidationError("Etkin üye bulunamadı.")

    def clean_inventory_code(self):
        try:
            return BookCopy.objects.get(inventory_code=self.cleaned_data["inventory_code"])
        except BookCopy.DoesNotExist:
            raise forms.ValidationError("Bu demirbaş koduna ait kopya bulunamadı.")
