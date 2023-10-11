import logging

from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from tg_bot import texts
from tg_bot.keyboards import inline_keyboards

logger = logging.getLogger(__name__)


async def display_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display message for banned user."""
    bot = context.bot
    user = update.effective_user
    logger.info(f"User {user.username} {user.id} has got a ban.")
    await bot.send_message(user.id, texts.DISPLAY_BAN)
    return ConversationHandler.END


async def display_not_active(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display message for not active user."""
    bot = context.bot
    user = update.effective_user
    logger.info(f"User {user.username} {user.id} "
                f"has got a `not active` message.")
    await bot.send_message(
        user.id,
        texts.DISPLAY_NOT_ACTIVE,
        reply_markup=inline_keyboards.build_base_menu(),
    )
    return ConversationHandler.END

