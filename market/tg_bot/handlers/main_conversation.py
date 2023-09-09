import logging

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from tg_bot.conversation_states import States
from tg_bot.keyboards import inline_keyboards
from tg_bot.services import user_services

logger = logging.getLogger(__name__)

# todo split handlers by type (callback, message) or by conversations


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the conversation and asks the user about their role."""

    logger.info(f"{update.message.from_user.id} starts")

    if user_services.is_authenticated(context):
        await update.message.reply_text(
            f"Hello {update.message.from_user.full_name} your role is "
            f"{user_services.get_role(context)}"
        )
        return ConversationHandler.END
    else:
        keyboard = inline_keyboards.get_role_keyboard()
        await update.message.reply_text(
            "Choose your role",
            reply_markup=keyboard,
        )
        return States.LOGIN


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    cancel_message = "Bye! I hope we can talk again some day."

    if update.message:
        user = update.message.from_user
        logger.info("User %s canceled the conversation.", user.first_name)
        # todo clean username or other data from storage
        await update.message.reply_text(
            cancel_message,
            reply_markup=ReplyKeyboardRemove(),
        )
    elif update.callback_query:
        query = update.callback_query
        await query.answer(text=query.data)
        await query.edit_message_text(
            text=cancel_message
        )
    else:
        ...
    return ConversationHandler.END
