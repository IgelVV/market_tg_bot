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
    # arbitrary_callback_data(True) makes it possible to pass
    # any type as callback data
    application = ApplicationBuilder() \
        .concurrent_updates(False) \
        .token(TOKEN) \
        .arbitrary_callback_data(True) \
        .build()

    set_bot_commands(bot=application.bot)

    # Nested conversation
    login_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                login_conversation.ask_username,
                pattern=f"^{il_keyboards.ADMIN}$",
            ),
            CallbackQueryHandler(
                login_conversation.ask_shop_api_key,
                pattern=f"^{il_keyboards.SELLER}$",
            ),
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
                    login_conversation.check_password,
                ),
                CallbackQueryHandler(
                    login_conversation.ask_username,
                    pattern=f"^{il_keyboards.YES}$"
                ),
                CallbackQueryHandler(
                    main_conversation.cancel,
                    pattern=f"^{il_keyboards.NO}$"
                ),
            ],
            States.API_KEY: [
                MessageHandler(
                    filters.TEXT,
                    login_conversation.check_shop_api_key,
                ),
            ]
        },
        fallbacks=[
            CommandHandler("cancel", main_conversation.cancel),
            CallbackQueryHandler(
                main_conversation.cancel,
                pattern=f"^{il_keyboards.CANCEL}$",
            )
        ],
        map_to_parent={
            ConversationHandler.END: ConversationHandler.END,
            States.ADMIN_MENU: States.ADMIN_MENU,
            States.SHOP_MENU: States.SHOP_MENU,
        },
    )

    main_conv = ConversationHandler(
        entry_points=[CommandHandler("start", main_conversation.start)],
        states={
            States.LOGIN: [
                login_conv,
            ],
            States.ADMIN_MENU: [
                CallbackQueryHandler(
                    main_conversation.display_shop_list,
                    pattern=f"^{il_keyboards.SHOP_LIST}$"
                ),
            ],
            States.SHOP_MENU: [

            ],
        },
        # todo add logout
        fallbacks=[CommandHandler("cancel", main_conversation.cancel)],
    )

    application.add_handler(main_conv)

    application.run_polling()


if __name__ == '__main__':
    run()
