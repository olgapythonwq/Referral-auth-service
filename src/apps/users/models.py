from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Phone number must be provided")

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)  # хэширует пароль
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(phone, password, **extra_fields)


phone_validator = RegexValidator(
    regex=r'^\+[1-9]\d{7,14}$',
    message="Enter a valid phone number in international format (e.g. +14155552671)."
)

alphanumeric_validator = RegexValidator(
    regex=r'^[A-Za-z0-9]+$',
    message="Only letters and numbers are allowed."
)

numeric_validator = RegexValidator(
    regex=r'^[0-9]+$',
    message="Only numbers are allowed."
)

class User(AbstractBaseUser, PermissionsMixin):

    phone = models.CharField(
        max_length=16,  # "+" and up to 15 digits (E.164 standard)
        unique=True,
        validators=[phone_validator],
        verbose_name="Phone number"
    )
    invite_code = models.CharField(max_length=6, unique=True, blank=True, validators=[alphanumeric_validator])
    invited_by = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="referrals")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # для админки
    otp_code = models.CharField(max_length=6, blank=True, null=True, validators=[numeric_validator])
    otp_created_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "phone"  # авторизация
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.phone
