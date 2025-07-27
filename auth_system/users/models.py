import uuid
from datetime import timedelta

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.utils import timezone

from users.hashing import check_password, hash_password


class CustomUserManager(BaseUserManager):
    def create_user(
            self,
            email,
            password=None,
            **extra_fields
    ):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_active=True,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('role') != 'admin':
            raise ValueError('Superuser must have role="admin".')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'patronymic']

    objects = CustomUserManager()

    def set_password(self, raw_password):
        self.password = hash_password(raw_password)  # ⬅️ твоя функция

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)  # ⬅️ твоя функция

    def __str__(self):
        return self.email


class AuthToken(models.Model):
    key = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='auth_tokens'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def has_expired(self):
        return timezone.now() >= self.expires_at

    @classmethod
    def create_token(cls, user, lifetime=timedelta(days=7)):
        cls.objects.filter(
            user=user,
            expires_at__lt=timezone.now()
        ).delete()
        token = cls.objects.create(
            user=user,
            expires_at=timezone.now() + lifetime
        )
        return token

    def __str__(self):
        return f"Token for {self.user.email} (expires {self.expires_at})"
