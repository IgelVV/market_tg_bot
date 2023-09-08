import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from django.conf import settings

from tg_bot.commands import set_bot_commands
from tg_bot.handlers import conversation_handlers as c_handlers
from tg_bot.conversation_states import States
from tg_bot.keyboards import inline_keyboards as il_keyboards

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

    set_bot_commands(bot=application.bot)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", c_handlers.start)],
        states={
            States.LOGIN: [
                CallbackQueryHandler(
                    c_handlers.ask_username,
                    pattern=f"^{il_keyboards.ADMIN}$"
                ),
            ],
            States.PASSWORD: [
                MessageHandler(
                    filters.TEXT,
                    c_handlers.ask_password,
                ),
            ],
            States.CHECK_PASSWORD: [
                MessageHandler(
                    filters.TEXT,
                    c_handlers.check_password,
                ),
                CallbackQueryHandler(
                    c_handlers.ask_username,
                    pattern=f"^{il_keyboards.YES}$"
                ),
                CallbackQueryHandler(
                    c_handlers.cancel,
                    pattern=f"^{il_keyboards.NO}$"
                )
            ]
        },
        fallbacks=[CommandHandler("cancel", c_handlers.cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    run()
