from django.db.models import F, TextField, Value
from django.db.models.functions import Lower, Replace

TURKISH_CAPITALS = dict(zip("IİÇĞÖŞÜ", "ıiçğöşü"))


def fold_text(value):
    return value.translate(str.maketrans(TURKISH_CAPITALS)).lower()


def searchable_text(field):
    # SQLite's LOWER handles ASCII only; fold Turkish capitals explicitly.
    expression = F(field)
    for upper, lower in TURKISH_CAPITALS.items():
        expression = Replace(expression, Value(upper), Value(lower), output_field=TextField())
    return Lower(expression)
