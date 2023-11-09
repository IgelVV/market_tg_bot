from tg_bot.models import TelegramUser


def send_ban_unban_notification(tg_user: TelegramUser):
    """Send message about ban status in telegram, using chat_id"""
    import asyncio
    from telegram.ext import ApplicationBuilder
    from django.conf import settings
    from tg_bot import texts

    application = ApplicationBuilder() \
        .concurrent_updates(False) \
        .token(settings.TG_BOT_TOKEN) \
        .build()

    if tg_user.is_banned:
        text = texts.DISPLAY_BAN
    else:
        text = texts.DISPLAY_UNBAN
    coroutine = application.bot.send_message(tg_user.chat_id, text)
    asyncio.run(coroutine)
