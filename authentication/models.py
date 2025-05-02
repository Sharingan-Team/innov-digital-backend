# models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not username:
            raise ValueError('Username is required')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)

    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    # Verification status
    email_verified = models.BooleanField(default=False)
    face_verified = models.BooleanField(default=False)

    # Email confirmation
    email_code = models.CharField(max_length=6, blank=True, null=True)
    email_code_expires = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def generate_email_code(self, code, validity_minutes=10):
        """
        Stocke le code et fixe la date d'expiration à maintenant + validity_minutes
        """
        self.email_code = code
        self.email_code_expires = timezone.now() + timezone.timedelta(minutes=validity_minutes)
        self.save(update_fields=['email_code', 'email_code_expires'])

    def is_email_code_valid(self, code):
        return (
            self.email_code == code and
            self.email_code_expires and
            timezone.now() < self.email_code_expires
        )


class UserFace(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='face')
    image = models.ImageField(upload_to='user_faces/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Face image for {self.user.username}"
