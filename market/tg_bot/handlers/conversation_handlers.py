import logging

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from tg_bot.conversation_states import States
from tg_bot.keyboards import inline_keyboards

logger = logging.getLogger(__name__)

# todo split handlers by type (callback, message)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> States:
    """Starts the conversation and asks the user about their role."""
    # todo check if user authenticated, then skip login
    keyboard = inline_keyboards.get_role_keyboard()
    logger.info(f"{update.message.from_user.id} starts")

    await update.message.reply_text(
        "Choose your role",
        reply_markup=keyboard,
    )

    return States.LOGIN


async def ask_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(text=query.data)
    await query.edit_message_text(
        text="Type your Username:"
    )
    return States.PASSWORD


async def ask_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels and ends the conversation."""
    # todo save username

    user = update.message.from_user
    await update.message.reply_text(
        "Type password:",
    )
    return States.CHECK_PASSWORD


async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels and ends the conversation."""
    text = update.message.text
    await update.message.delete()
    # todo clean username, and login
    await update.message.reply_text(
        f"password received: {text} \nPlease wait.",
    )
    # todo authentication
    authenticated = False
    if authenticated:
        return ConversationHandler.END
    else:

        await update.message.reply_text(
            "Wrong username or password. \nDo you want to try again?",
            reply_markup=inline_keyboards.get_yes_no()
        )
        return None


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    # todo clean username or other data from storage
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END
