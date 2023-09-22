import logging

from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from tg_bot.conversation_states import States
from tg_bot.keyboards import inline_keyboards
from tg_bot.services import ChatService
from tg_bot import texts
from tg_bot.handlers import main_conversation, auxiliary

logger = logging.getLogger(__name__)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(texts.HELP_TEXT)
    user = update.message.from_user
    logger.debug("User %s asks help.", user.username)
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Starts the conversation and asks the user about their role.

    If user is authenticated it displays corresponding menu,
    otherwise directs to `login conversation`.
    """
    chat_id = update.message.chat_id
    chat_service = ChatService(chat_id, context)
    user = update.message.from_user
    logger.info(
        f"User {user.username} with {chat_id=} starts.")

    is_banned, is_activate, is_logged_out = await chat_service.get_statuses()

    exists = is_banned is not None
    is_logged_in = exists and (not is_logged_out)

    if exists and is_banned:
        return await main_conversation.display_ban(update, context)

    if exists and (not is_activate):
        return await main_conversation.display_not_active(update, context)

    if not is_logged_in:
        keyboard = inline_keyboards.build_role_keyboard()
        await update.message.reply_text(
            texts.START_CHOOSE_ROLE,
            reply_markup=keyboard,
        )
        return States.LOGIN
    else:
        logger.info(f"User {user.username} {chat_id} is recognised.")
        return await main_conversation.display_user_menu(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancels and ends the conversation.

    It handles both messages or callback queries.
    """
    from_user, reply_func = await auxiliary.callback_and_message_unifier(
        update, texts.CANCEL_ANS)

    logger.info("User %s canceled the conversation.", from_user.username)
    await reply_func(texts.CANCEL)
    return ConversationHandler.END


async def sign_out(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Logout user."""
    user = update.message.from_user

    chat_id = update.message.chat_id
    logger.info("User %s signed out.", user.username)
    await ChatService(chat_id, context).logout()
    return await start(update, context)


async def unexpected_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Logout user."""
    user = update.message.from_user
    command = update.message.text

    chat_id = update.message.chat_id
    logger.info("User %s sent unexpected command %s.", user.username, command)
    await update.message.reply_text(text=texts.UNEXPECTED_COMMAND)
