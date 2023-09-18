import logging

from telegram import Update
from telegram.ext import ContextTypes
from tg_bot import texts

logger = logging.getLogger(__name__)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(texts.help_text)
    user = update.message.from_user
    logger.debug("User %s asks help.", user.full_name)
    return None
