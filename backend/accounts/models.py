from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
        ADMIN = "ADMIN", "Admin"
        BRANCH_MANAGER = "BRANCH_MANAGER", "Branch Manager"
        STAFF = "STAFF", "Staff"

    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.STAFF
    )