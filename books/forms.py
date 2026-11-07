from django import forms

from .models import Author, Category


class CatalogFilterForm(forms.Form):
    q = forms.CharField(label="Kitap, yazar, ISBN veya demirbaş", max_length=200, required=False,
                        widget=forms.TextInput(attrs={"type": "search", "placeholder": "Katalogda ara…"}))
    category = forms.ModelChoiceField(label="Kategori", queryset=Category.objects.all(), required=False, empty_label="Tüm kategoriler")
    author = forms.ModelChoiceField(label="Yazar", queryset=Author.objects.all(), required=False, empty_label="Tüm yazarlar")
    year_from = forms.IntegerField(label="İlk yayın yılı", min_value=1, max_value=9999, required=False)
    year_to = forms.IntegerField(label="Son yayın yılı", min_value=1, max_value=9999, required=False)
    available = forms.BooleanField(label="Yalnızca müsait kitaplar", required=False)
    sort = forms.ChoiceField(label="Sıralama", required=False, choices=[
        ("title", "Kitap adı A–Z"), ("title_desc", "Kitap adı Z–A"),
        ("year", "En yeni yayın"), ("oldest", "En eski yayın"),
    ])

    def clean(self):
        data = super().clean()
        start, end = data.get("year_from"), data.get("year_to")
        if start and end and start > end:
            self.add_error("year_to", "Son yıl ilk yıldan önce olamaz.")
        return data
