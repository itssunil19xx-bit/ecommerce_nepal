from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from .managers import CustomUserManager


class User (AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = 'customer', _('Customer')
        SELLER = 'seller', _('Seller')
        ADMIN = 'admin', _('admin')

    username = None

    email = models.EmailField(_('email address'), unique=True,
                              error_messages={
                              'unique': _("a uses with this email already exist"),
                              })

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+977XXXXXXXXX'. Up to 15 digits allowed."
    )

    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=15,
        unique=True,
        null=True,
        blank=True
    )

    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.CUSTOMER)

    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)

    province = models.CharField(max_length=50, blank=True)
    district = models.CharField(max_length=50, blank=True)
    municipality = models.CharField(max_length=50, blank=True)
    ward_no = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.email

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    @property
    def is_seller(self):
        return self.role == self.Role.SELLER

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @is_admin.setter
    def is_admin(self, value):
        """Setter for is_admin property"""
        if value:
            self.role = self.Role.ADMIN

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile")

    avatar = models.ImageField(
        'avatars/', null=True, blank=True, help_text=_("profile picture"))

    # for seller only
    company_name = models.CharField(max_length=100, blank=True)
    pan_vat_number = models.CharField(max_length=50, blank=True)
    seller_license = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)

    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)

    receive_marketing_emails = models.BooleanField(default=True)
    receve_sms_notiifications = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
        db_table = "user_profile"

    def __str__(self):
        return f"profile of {self.user.email}"
