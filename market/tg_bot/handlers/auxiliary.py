"""Service functions for handlers, or handlers."""
import logging
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from tg_bot import texts

logger = logging.getLogger(__name__)


async def callback_and_message_unifier(
        update: Update, callback_answer: Optional[str] = None):
    """
    Unify update for two types of handlers (adapter).

    It is important to use only common args when call reply_func.
    """
    if update.message:
        reply_func = update.message.reply_text
    elif query := update.callback_query:
        reply_func = query.edit_message_text
        await query.answer(text=callback_answer)
    else:
        raise ValueError(
            "Unexpected update. It is expected Callback or Message.")

    return reply_func


async def do_nothing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Answer to a callback."""
    query = update.callback_query
    await query.answer(text=texts.DO_NOTHING_ANS)
