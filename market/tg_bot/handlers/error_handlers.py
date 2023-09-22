import html
import json
import logging
import traceback

from django.conf import settings

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# This can be your own ID, or one for a developer group/channel.
TG_REPORT_CHAT_ID = settings.TG_REPORT_CHAT_ID


async def error_handler(
        update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else,
    # so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about
    # an exception, but as a list of strings rather than a single string,
    # so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about
    # what happened. You might need to add some logic to deal with messages
    # longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        # f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    if TG_REPORT_CHAT_ID:
        await context.bot.send_message(
            chat_id=TG_REPORT_CHAT_ID, text=message, parse_mode=ParseMode.HTML
        )
