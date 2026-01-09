from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(blank=True)
    is_contributor = models.BooleanField(
        default=False,
        help_text="Designates whether this user can upload or submit content site-wide."
    )

    def __str__(self):
        return self.username