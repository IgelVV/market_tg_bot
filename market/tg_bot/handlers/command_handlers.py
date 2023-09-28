import logging

from telegram import Update
from telegram.ext import (
    ContextTypes,
)

from tg_bot.services import ChatService
from tg_bot import texts
from tg_bot.handlers import prohibitions, auxiliary, login, user_menu

logger = logging.getLogger(__name__)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Send help message.

    It is possible to use in Callback and Message handlers.
    """
    reply_func = await auxiliary.callback_and_message_unifier(update,
                                                              texts.HELP_ANS)
    await reply_func(texts.HELP_TEXT)
    user = update.effective_user
    logger.debug("User %s asks help.", user.username)
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Starts the conversation and asks the users about their role.

    Check prohibitions.
    If user is authenticated it displays user menu,
    otherwise starts logging in.
    """
    chat_id = update.effective_chat.id
    user = update.effective_user
    logger.info(f"User {user.username} with {chat_id=} starts.")

    chat_service = ChatService(chat_id, context)
    chat_service.set_expected_input(None)
    is_banned, is_activate, is_logged_out = await chat_service.get_statuses()

    exists = is_banned is not None
    is_logged_in = exists and (not is_logged_out)

    if exists and is_banned:
        return await prohibitions.display_ban(update, context)

    if exists and (not is_activate):
        return await prohibitions.display_not_active(update, context)

    if not is_logged_in:
        return await login.choose_role(update, context)
    else:
        logger.info(f"User {user.username} {chat_id} is recognised.")
        return await user_menu.display_user_menu(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel input and call start().

    It is possible to use in Callback and Message handlers.
    """
    from_user = update.effective_user
    reply_func = await auxiliary.callback_and_message_unifier(update,
                                                              texts.CANCEL_ANS)
    chat_service = ChatService(from_user.id, context)
    expected_input = chat_service.get_expected_input()
    chat_service.set_expected_input(None)
    logger.info(
        "User %s canceled input of %s.", from_user.username, expected_input)
    if expected_input is not None:
        text = texts.CANCEL
    else:
        text = texts.USELESS_CANCEL
    await reply_func(text)
    return await start(update, context)


async def sign_out(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Logout user."""
    user = update.message.from_user
    chat_id = update.message.chat_id
    logger.info("User %s signed out.", user.username)
    await ChatService(chat_id, context).logout()
    return await start(update, context)


async def unexpected_command(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
    """Send message that the Command is unexpected."""
    user = update.message.from_user
    command = update.message.text
    logger.info("User %s sent unexpected command %s.", user.username, command)
    await update.message.reply_text(text=texts.UNEXPECTED_COMMAND)
