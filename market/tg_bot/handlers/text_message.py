"""Handles all text inputs."""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from tg_bot.services import ChatService, ExpectedInput
from tg_bot import texts

logger = logging.getLogger(__name__)


async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat_id
    chat_service = ChatService(chat_id, context=context)

    expected_input = chat_service.get_expected_input()
    match expected_input:
        case ExpectedInput.USERNAME:
            await update.message.reply_text(text="обработка username")
        case ExpectedInput.PASSWORD:
            await update.message.reply_text(text="обработка пароля")
        case ExpectedInput.API_KEY_TO_LOGIN:
            await update.message.reply_text(text="обработка api_key_to_login")
        case ExpectedInput.API_KEY_TO_ADD:
            await update.message.reply_text(text="обработка api_key_to_add")
        case _:
            return await _answer_unexpected_text(update, context)


async def _answer_unexpected_text(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat_id
    chat_service = ChatService(chat_id, context=context)

    await update.message.reply_text(text=texts.HELP_TEXT,)
