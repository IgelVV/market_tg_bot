"""Handles all text inputs."""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from tg_bot.services import ChatService, ExpectedInput
from tg_bot import texts
from tg_bot.handlers.login import ask_password,\
    check_password,\
    check_shop_api_key
from tg_bot.handlers import add_shop

logger = logging.getLogger(__name__)


async def dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat_id
    chat_service = ChatService(chat_id, context=context)

    expected_input = chat_service.get_expected_input()
    match expected_input:
        case ExpectedInput.USERNAME:
            return await ask_password(update, context)
        case ExpectedInput.PASSWORD:
            return await check_password(update, context)
        case ExpectedInput.API_KEY_TO_LOGIN:
            return await check_shop_api_key(update, context)
        case ExpectedInput.API_KEY_TO_ADD:
            return await add_shop.add_shop(update, context)
        case _:
            return await _answer_unexpected_text(update, context)


async def _answer_unexpected_text(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat_id
    chat_service = ChatService(chat_id, context=context)

    await update.message.reply_text(text=texts.UNEXPECTED_TEXT,)
