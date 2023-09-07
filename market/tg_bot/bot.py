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
from django.conf import settings

from tg_bot.handlers.conversation_handlers import (
    start,
    cancel,
    login,

)
from tg_bot.conversation_states import States

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

TOKEN = settings.TG_BOT_TOKEN


def run():
    application = ApplicationBuilder() \
        .concurrent_updates(False) \
        .token(TOKEN) \
        .build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            States.LOGIN: [
                MessageHandler(filters.Regex("^(Admin|User)$"), login),
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    run()
