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

import tg_bot.handlers.login_conversation
from tg_bot.commands import set_bot_commands
from tg_bot.handlers import (
    main_conversation,
    login_conversation,
)
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

    # Nested conversation
    login_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                login_conversation.ask_username,
                pattern=f"^{il_keyboards.ADMIN}$"
            ),
            # todo handle all possible variants
        ],
        states={
            States.PASSWORD: [
                MessageHandler(
                    filters.TEXT,
                    login_conversation.ask_password,
                ),
            ],
            States.CHECK_PASSWORD: [
                MessageHandler(
                    filters.TEXT,
                    tg_bot.handlers.login_conversation.check_password,
                ),
                CallbackQueryHandler(
                    tg_bot.handlers.login_conversation.ask_username,
                    pattern=f"^{il_keyboards.YES}$"
                ),
                CallbackQueryHandler(
                    main_conversation.cancel,
                    pattern=f"^{il_keyboards.NO}$"
                )
            ]
        },
        fallbacks=[CommandHandler("cancel", main_conversation.cancel)],
        map_to_parent={
            ConversationHandler.END: ConversationHandler.END,

        },
    )

    main_conv = ConversationHandler(
        entry_points=[CommandHandler("start", main_conversation.start)],
        states={
            States.LOGIN: [
                login_conv,
            ],
        },
        # todo add logout
        fallbacks=[CommandHandler("cancel", main_conversation.cancel)],
    )

    application.add_handler(main_conv)

    application.run_polling()


if __name__ == '__main__':
    run()
