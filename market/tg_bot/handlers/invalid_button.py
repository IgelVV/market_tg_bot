import logging

from telegram import Update
from telegram.ext import (
    ContextTypes,
)
from tg_bot import texts

logger = logging.getLogger(__name__)


async def handle_invalid_button(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Informs the user that the button is no longer available."""
    user = update.callback_query.from_user
    await update.callback_query.answer(texts.HANDLE_INVALID_BUTTON_ANS)
    await update.effective_message.edit_text(texts.INVALID_BUTTON)
    logger.debug(f"User {user.username} {user.id} "
                 f"has clicked on invalid button.")


async def unexpected_callback(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Write log message about unexpected callback for debugging."""
    logger.info(f"Unexpected callback: {update.callback_query.data}")
