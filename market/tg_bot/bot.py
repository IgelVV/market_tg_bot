"""Main bot module."""
import json
import logging.config
from warnings import filterwarnings

from telegram import Update
from telegram.warnings import PTBUserWarning
from telegram.ext import ApplicationBuilder
from django.conf import settings

from tg_bot import set_up, customisation
from tg_bot.run import run_polling
from rabbit import broker, callbacks


# to ignore CallbackQueryHandler warnings
# filterwarnings(
#     action="ignore",
#     message=r".*CallbackQueryHandler",
#     category=PTBUserWarning,
# )
with open("tg_bot/logging_config.json", "r") as f:
    json_config = json.load(f)
    logging.config.dictConfig(json_config)

logger = logging.getLogger(__name__)

TOKEN = settings.TG_BOT_TOKEN
AUTO_CUSTOMISATION = settings.TG_AUTO_CUSTOMISATION


def run():
    """
    Start telegram bot and register all handlers.
    """
    logger.info("Bot is running.")
    # arbitrary_callback_data(True) makes it possible to pass
    # any type as callback data
    application = ApplicationBuilder() \
        .concurrent_updates(False) \
        .token(TOKEN) \
        .arbitrary_callback_data(True) \
        .build()

    set_up.register_handlers(application)

    # Set or refresh some bot attributes
    # (if False it can be set manually using BotFather).
    if AUTO_CUSTOMISATION:
        customisation.set_bot_commands(bot=application.bot)
        customisation.set_bot_description(bot=application.bot)
        customisation.set_bot_short_description(bot=application.bot)

    rmq_consumer_coro = broker.Broker().consume_queue(
        callbacks.on_message_shop,
        broker.OZON_SHOP_EXCHANGE,
        broker.OZON_SHOP_ROUTING_KEY,
    )
    run_polling(application,
                side_coroutines=[rmq_consumer_coro],
                allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    run()
