"""Main bot module."""
import json
import logging.config
from warnings import filterwarnings

from telegram.warnings import PTBUserWarning
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    InvalidCallbackData,
    filters,
)
from django.conf import settings

from tg_bot import commands, customisation
from tg_bot.handlers import (
    main_conversation,
    login,
    text_message,
    command_handlers,
    invalid_button,
    error_handlers,
)
from tg_bot.conversation_states import States
from tg_bot.keyboards import inline_keyboards as il_keyboards
from tg_bot.dataclasses import ShopInfo, Navigation

# to ignore CallbackQueryHandler warnings
filterwarnings(
    action="ignore",
    message=r".*CallbackQueryHandler",
    category=PTBUserWarning,
)
with open("tg_bot/logging_config.json", "r") as f:
    json_config = json.load(f)
    logging.config.dictConfig(json_config)

logger = logging.getLogger(__name__)

TOKEN = settings.TG_BOT_TOKEN
AUTO_CUSTOMISATION = settings.TG_AUTO_CUSTOMISATION


def run():
    """Starts telegram bot."""
    logger.info("Bot is running.")
    # arbitrary_callback_data(True) makes it possible to pass
    # any type as callback data
    application = ApplicationBuilder() \
        .concurrent_updates(False) \
        .token(TOKEN) \
        .arbitrary_callback_data(True) \
        .build()

    # Nested conversation
    login_conv = ConversationHandler(
        per_message=True,
        entry_points=[
            CallbackQueryHandler(
                login.ask_username,
                pattern=f"^{il_keyboards.ADMIN_LOGIN}$",
            ),
            CallbackQueryHandler(
                login.ask_shop_api_key,
                pattern=f"^{il_keyboards.SELLER_LOGIN}$",
            ),
        ],
        states={
            States.PASSWORD: [
                # MessageHandler(
                #     filters.TEXT & (~filters.COMMAND),
                #     login_conversation.ask_password,
                # ),
            ],
            States.CHECK_PASSWORD: [
                # MessageHandler(
                #     filters.TEXT & (~filters.COMMAND),
                #     login_conversation.check_password,
                # ),
                CallbackQueryHandler(
                    login.ask_username,
                    pattern=f"^{il_keyboards.YES}$"
                ),
                CallbackQueryHandler(
                    command_handlers.cancel,
                    pattern=f"^{il_keyboards.NO}$"
                ),
            ],
            States.API_KEY: [
                # MessageHandler(
                #     filters.TEXT & (~filters.COMMAND),
                #     login_conversation.check_shop_api_key,
                # ),
            ]
        },
        fallbacks=[
            CallbackQueryHandler(
                command_handlers.cancel,
                pattern=f"^{il_keyboards.CANCEL}$",
            ),
            CallbackQueryHandler(invalid_button.handle_invalid_button,
                                 pattern=InvalidCallbackData),
        ],
    )
    main_conv = ConversationHandler(
        per_message=True,
        entry_points=[
            CallbackQueryHandler(
                main_conversation.display_shop_list,
                pattern=f"^{il_keyboards.SHOP_LIST}$"
            ),
            CallbackQueryHandler(
                main_conversation.display_add_shop,
                pattern=f"^{il_keyboards.ADD_SHOP}$"
            ),
            CallbackQueryHandler(
                main_conversation.display_unlink_shop,
                pattern=f"^{il_keyboards.UNLINK_SHOP}$"
            ),
        ],
        states={
            # States.LOGIN: [
            #     login_conv,
            # ],
            States.ADMIN_MENU: [
                CallbackQueryHandler(
                    main_conversation.display_shop_list,
                    pattern=f"^{il_keyboards.SHOP_LIST}$"
                ),
            ],
            States.SELLER_MENU: [
                CallbackQueryHandler(
                    main_conversation.display_add_shop,
                    pattern=f"^{il_keyboards.ADD_SHOP}$"
                ),
                CallbackQueryHandler(
                    main_conversation.display_unlink_shop,
                    pattern=f"^{il_keyboards.UNLINK_SHOP}$"
                ),
                CallbackQueryHandler(
                    main_conversation.display_shop_list,
                    pattern=f"^{il_keyboards.SHOP_LIST}$"
                ),
            ],
            States.ADD_SHOP: [
                # MessageHandler(
                #     filters.TEXT & (~filters.COMMAND),
                #     main_conversation.add_shop,
                # ),
                CallbackQueryHandler(
                    main_conversation.display_user_menu,
                    pattern=f"^{il_keyboards.BACK}$",
                ),
            ],
            States.UNLINK_SHOP: [
                CallbackQueryHandler(
                    main_conversation.confirm_unlink_shop,
                    pattern=ShopInfo,
                ),
                CallbackQueryHandler(
                    main_conversation.display_unlink_shop,
                    pattern=Navigation,
                ),
                CallbackQueryHandler(
                    main_conversation.unlink_shop,
                    pattern=f"^{il_keyboards.YES}$",
                ),
                CallbackQueryHandler(
                    main_conversation.display_user_menu,
                    pattern=f"^{il_keyboards.BACK}$",
                ),
            ],
            States.SHOP_LIST: [
                CallbackQueryHandler(
                    main_conversation.display_shop_menu,
                    pattern=ShopInfo,
                ),
                CallbackQueryHandler(
                    main_conversation.display_shop_list,
                    pattern=Navigation,
                ),
                CallbackQueryHandler(
                    main_conversation.display_user_menu,
                    pattern=f"^{il_keyboards.BACK}$",
                ),
            ],
            States.SHOP_MENU: [
                CallbackQueryHandler(
                    main_conversation.display_shop_info,
                    pattern=f"^{il_keyboards.SHOP_INFO}$",
                ),
                CallbackQueryHandler(
                    main_conversation.activate_shop,
                    pattern=f"^{il_keyboards.ACTIVATE}$",
                ),
                CallbackQueryHandler(
                    main_conversation.price_updating,
                    pattern=f"^{il_keyboards.PRICE_UPDATING}$",
                ),
                CallbackQueryHandler(
                    main_conversation.display_shop_list,
                    pattern=f"^{il_keyboards.BACK}$",
                ),
            ],
            States.SHOP_INFO: [
                CallbackQueryHandler(
                    main_conversation.display_shop_menu,
                    pattern=f"^{il_keyboards.BACK}$",
                ),
            ],
            States.ACTIVATE: [
                CallbackQueryHandler(
                    main_conversation.switch_activation,
                    pattern=f"^{il_keyboards.SWITCH_ACTIVATION}$",
                ),
                CallbackQueryHandler(
                    main_conversation.display_shop_menu,
                    pattern=f"^{il_keyboards.BACK}$",
                ),
            ],
            States.PRICE_UPDATING: [
                CallbackQueryHandler(
                    main_conversation.switch_price_updating,
                    pattern=f"^{il_keyboards.SWITCH_PRICE_UPDATING}$",
                ),
                CallbackQueryHandler(
                    main_conversation.display_shop_menu,
                    pattern=f"^{il_keyboards.BACK}$",
                ),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(invalid_button.handle_invalid_button,
                                 pattern=InvalidCallbackData)
        ],
    )

    if AUTO_CUSTOMISATION:
        customisation.set_bot_commands(bot=application.bot)
        customisation.set_bot_description(bot=application.bot)
        customisation.set_bot_short_description(bot=application.bot)

    application.add_handlers(
        [
            CommandHandler(commands.HELP, command_handlers.help_handler),
            CommandHandler(commands.START, command_handlers.start),
            CommandHandler(commands.MENU, command_handlers.start),
            CommandHandler(commands.CANCEL, command_handlers.cancel),
            CommandHandler(commands.SIGN_OUT, command_handlers.sign_out),
            login_conv,
            main_conv,
            CallbackQueryHandler(invalid_button.handle_invalid_button,
                                 pattern=InvalidCallbackData),
            MessageHandler(filters.TEXT & (~filters.COMMAND),
                           text_message.text),
            MessageHandler(filters.COMMAND, command_handlers.unexpected_command)
        ]
    )

    application.add_error_handler(error_handlers.error_handler)

    application.run_polling()


if __name__ == '__main__':
    run()
