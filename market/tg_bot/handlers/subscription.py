import logging

from telegram import Update
from telegram.ext import ContextTypes

from tg_bot.keyboards import inline_keyboards
from tg_bot.services import ChatService
from tg_bot import texts
from tg_bot.conversation_states import States
from tg_bot.handlers import auxiliary

logger = logging.getLogger(__name__)


async def display_subscription_menu(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Send message with subscription menu.

    It is possible to use in Callback and Message handlers.
    """
    from_user = update.effective_user
    reply_func = await auxiliary.callback_and_message_unifier(
        update, texts.DISPLAY_SUBSCRIPTION_MENU_ANS)
    chat_id = from_user.id

    chat_service = ChatService(chat_id, context)

    logger.debug(f"User {from_user.username} {chat_id} "
                 f"displays subscription menu.")
    _, is_active, _ = await chat_service.get_statuses()
    text = texts.DISPLAY_SUBSCRIPTION_MENU.format(
        username=from_user.username,
        is_active=is_active,
    )
    await reply_func(
        text=text,
        reply_markup=inline_keyboards.build_subscription_menu(),
        parse_mode="html",
    )
    return States.SUBSCRIPTION


async def display_pay_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    """
    query = update.callback_query
    await query.answer(texts.DISPLAY_PAY_MENU_ANS)
    await query.edit_message_text(
        texts.DISPLAY_PAY_MENU,
        reply_markup=inline_keyboards.build_back(),
        parse_mode="html",
    )
