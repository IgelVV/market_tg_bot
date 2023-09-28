from django.db.models.signals import pre_save
from django.dispatch import receiver

from tg_bot.models import TelegramUser
from tg_bot.tasks import ban_notification


@receiver(pre_save, sender=TelegramUser)
def notify_banned_user(sender, instance: TelegramUser, **kwargs):
    """Check if ban status has changed, and send notification."""
    if instance.pk is None:
        pass
    else:
        current = instance
        previous: TelegramUser = TelegramUser.objects.get(pk=instance.pk)
        if previous.is_banned != current.is_banned:
            try:
                ban_notification.send_ban_unban_notification(current)
            except Exception as e:
                print(e.__repr__())
