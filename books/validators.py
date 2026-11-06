import re

from django.core.exceptions import ValidationError


def validate_isbn(value):
    """Validate canonical ISBN-10/ISBN-13 values, including their check digit."""
    if re.fullmatch(r"[0-9]{9}[0-9X]", value):
        digits = [10 if digit == "X" else int(digit) for digit in value]
        if sum((10 - index) * digit for index, digit in enumerate(digits)) % 11 == 0:
            return
    elif re.fullmatch(r"97[89][0-9]{10}", value):
        checksum = sum(
            int(digit) * (1 if index % 2 == 0 else 3)
            for index, digit in enumerate(value)
        )
        if checksum % 10 == 0:
            return

    raise ValidationError(
        "Tire veya boşluk olmadan, kontrol basamağı doğru bir ISBN-10 ya da ISBN-13 girin.",
        code="invalid_isbn",
    )
