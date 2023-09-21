from typing import Optional

from telegram import Update
from tg_bot import texts
from tg_bot.models import TelegramUser


async def callback_and_message_unifier(
        update: Update, callback_answer: Optional[str] = None):
    if update.message:
        from_user = update.message.from_user
        reply_func = update.message.reply_text
    elif query := update.callback_query:
        from_user = query.from_user
        reply_func = query.edit_message_text
        await query.answer(text=callback_answer)
    else:
        raise ValueError(
            "Unexpected update. It is expected Callback or Message.")

    return from_user, reply_func


def readable_role(role):
    if role == TelegramUser.Roles.ADMIN:
        return texts.READABLE_ADMIN_ROLE
    elif role == TelegramUser.Roles.SELLER:
        return texts.READABLE_SELLER_ROLE
    else:
        raise ValueError("Unknown TelegramUser role.")


def readable_flag(flag: bool):
    if flag:
        return texts.READABLE_TRUE
    else:
        return texts.READABLE_FALSE


def readable_shop_activiti(is_active: bool):
    if is_active:
        return texts.READABLE_ACTIVE
    else:
        return texts.READABLE_INACTIVE
