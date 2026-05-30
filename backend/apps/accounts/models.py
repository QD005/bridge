from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('AGENCY_ADMIN', 'Agency Admin'),
        ('OPERATIONS_OFFICER', 'Operations Officer'),
        ('AUDITOR', 'Auditor'),
        ('DEVELOPER', 'Developer'),
    ]

    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, blank=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=50, blank=True)

    # Agency relation — nullable so Super Admin can exist without an agency
    agency = models.ForeignKey(
        'agencies.Agency',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='OPERATIONS_OFFICER')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()