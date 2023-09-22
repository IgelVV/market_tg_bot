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
    add_shop,
    command_handlers,
    error_handlers,
    invalid_button,
    login,
    shop_list,
    shop_menu,
    text_message,
    unlink_shop,
    user_menu,
)
from tg_bot.conversation_states import States
from tg_bot.keyboards import inline_keyboards as il_keyboards
from tg_bot.data_classes import ShopInfo, Navigation

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

    main_conv = ConversationHandler(
        per_message=True,
        entry_points=[
            CallbackQueryHandler(command_handlers.start,
                                 pattern=f"^{il_keyboards.USER_MENU}$"),
            CallbackQueryHandler(shop_list.display_shop_list,
                                 pattern=f"^{il_keyboards.SHOP_LIST}$"),
            CallbackQueryHandler(add_shop.display_add_shop,
                                 pattern=f"^{il_keyboards.ADD_SHOP}$"),
            CallbackQueryHandler(unlink_shop.display_unlink_shop,
                                 pattern=f"^{il_keyboards.UNLINK_SHOP}$"),
        ],
        states={
            States.ADMIN_MENU: [
                CallbackQueryHandler(shop_list.display_shop_list,
                                     pattern=f"^{il_keyboards.SHOP_LIST}$"),
            ],
            States.SELLER_MENU: [
                CallbackQueryHandler(add_shop.display_add_shop,
                                     pattern=f"^{il_keyboards.ADD_SHOP}$"),
                CallbackQueryHandler(unlink_shop.display_unlink_shop,
                                     pattern=f"^{il_keyboards.UNLINK_SHOP}$"),
                CallbackQueryHandler(shop_list.display_shop_list,
                                     pattern=f"^{il_keyboards.SHOP_LIST}$"),
            ],
            States.ADD_SHOP: [
                CallbackQueryHandler(user_menu.display_user_menu,
                                     pattern=f"^{il_keyboards.BACK}$"),
            ],
            States.UNLINK_SHOP: [
                CallbackQueryHandler(unlink_shop.confirm_unlink_shop,
                                     pattern=ShopInfo),
                CallbackQueryHandler(unlink_shop.display_unlink_shop,
                                     pattern=Navigation),
                CallbackQueryHandler(unlink_shop.unlink_shop,
                                     pattern=f"^{il_keyboards.YES}$"),
                CallbackQueryHandler(user_menu.display_user_menu,
                                     pattern=f"^{il_keyboards.BACK}$"),
            ],
            States.SHOP_LIST: [
                CallbackQueryHandler(shop_menu.display_shop_menu,
                                     pattern=ShopInfo),
                CallbackQueryHandler(shop_list.display_shop_list,
                                     pattern=Navigation),
                CallbackQueryHandler(user_menu.display_user_menu,
                                     pattern=f"^{il_keyboards.BACK}$", ),
            ],
            States.SHOP_MENU: [
                CallbackQueryHandler(shop_menu.display_shop_info,
                                     pattern=f"^{il_keyboards.SHOP_INFO}$"),
                CallbackQueryHandler(shop_menu.activate_shop,
                                     pattern=f"^{il_keyboards.ACTIVATE}$"),
                CallbackQueryHandler(
                    shop_menu.price_updating,
                    pattern=f"^{il_keyboards.PRICE_UPDATING}$"),
                CallbackQueryHandler(shop_list.display_shop_list,
                                     pattern=f"^{il_keyboards.BACK}$"),
            ],
            States.SHOP_INFO: [
                CallbackQueryHandler(shop_menu.display_shop_menu,
                                     pattern=f"^{il_keyboards.BACK}$"),
            ],
            States.ACTIVATE: [
                CallbackQueryHandler(
                    shop_menu.switch_activation,
                    pattern=f"^{il_keyboards.SWITCH_ACTIVATION}$"),
                CallbackQueryHandler(shop_menu.display_shop_menu,
                                     pattern=f"^{il_keyboards.BACK}$"),
            ],
            States.PRICE_UPDATING: [
                CallbackQueryHandler(
                    shop_menu.switch_price_updating,
                    pattern=f"^{il_keyboards.SWITCH_PRICE_UPDATING}$"),
                CallbackQueryHandler(shop_menu.display_shop_menu,
                                     pattern=f"^{il_keyboards.BACK}$"),
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
            # commands
            CommandHandler(commands.HELP, command_handlers.help_handler),
            CommandHandler(commands.START, command_handlers.start),
            CommandHandler(commands.MENU, user_menu.display_user_menu),
            CommandHandler(commands.CANCEL, command_handlers.cancel),
            CommandHandler(commands.SIGN_OUT, command_handlers.sign_out),

            # login,
            CallbackQueryHandler(login.ask_username,
                                 pattern=f"^{il_keyboards.ADMIN_LOGIN}$"),
            CallbackQueryHandler(login.ask_shop_api_key,
                                 pattern=f"^{il_keyboards.SELLER_LOGIN}$"),
            CallbackQueryHandler(login.back_to_choose_role,
                                 pattern=f"^{il_keyboards.BACK_TO_CHOOSE_ROLE}$"),
            CallbackQueryHandler(command_handlers.cancel,
                                 pattern=f"^{il_keyboards.CANCEL}$"),

            main_conv,

            # all text messages
            MessageHandler(filters.TEXT & (~filters.COMMAND),
                           text_message.dispatcher),

            CallbackQueryHandler(invalid_button.handle_invalid_button,
                                 pattern=InvalidCallbackData),
            CallbackQueryHandler(invalid_button.unexpected_callback),
            MessageHandler(filters.COMMAND,
                           command_handlers.unexpected_command),
        ]
    )

    application.add_error_handler(error_handlers.error_handler)

    application.run_polling()


if __name__ == '__main__':
    run()
