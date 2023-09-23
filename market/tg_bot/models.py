from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
from django.dispatch import receiver

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


@receiver(pre_save, sender=TelegramUser)
def save_user_cart(sender, instance: TelegramUser, **kwargs):
    if instance.pk is None:
        pass
    else:
        current = instance
        previous: TelegramUser = TelegramUser.objects.get(pk=instance.pk)
        if previous.is_banned != current.is_banned:
            import asyncio
            from telegram.ext import ApplicationBuilder
            from django.conf import settings
            from tg_bot import texts

            application = ApplicationBuilder() \
                .concurrent_updates(False) \
                .token(settings.TG_BOT_TOKEN) \
                .build()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            if current.is_banned:
                coroutine = application.bot.send_message(instance.chat_id,
                                                         texts.DISPLAY_BAN)
            else:
                coroutine = application.bot.send_message(instance.chat_id,
                                                         texts.DISPLAY_UNBAN)
            loop.run_until_complete(coroutine)
