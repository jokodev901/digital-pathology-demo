from django.db import models
from django.utils import timezone


class TimestampBaseModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True