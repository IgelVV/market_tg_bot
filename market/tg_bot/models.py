from django.db import models
from django.utils.translation import gettext_lazy as _

from shop.models import Shop


class TelegramUser(models.Model):
    class Meta:
        verbose_name = _("telegram user")
        verbose_name_plural = _("telegram users")

    class Roles(models.TextChoices):
        ADMIN = "AD", _("admin")
        SELLER = "SE", _("seller")

    chat_id = models.PositiveIntegerField(unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    username = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=2, choices=Roles.choices)
    shops = models.ManyToManyField(Shop, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_banned = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  # for subscription
    is_logged_out = models.BooleanField(default=False)  # for refreshing data
