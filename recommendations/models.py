from django.db import models


class UsageWindow(models.Model):
    scope = models.CharField(max_length=80, primary_key=True)
    window = models.CharField(max_length=32)
    used = models.PositiveIntegerField(default=0)
