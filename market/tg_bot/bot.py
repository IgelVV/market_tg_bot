"""Main bot module."""
import asyncio
import json
import logging.config
from warnings import filterwarnings

from telegram import Update
from telegram.warnings import PTBUserWarning
from telegram.ext import ApplicationBuilder
from django.conf import settings

from tg_bot import set_up, customisation
from tg_bot.run import run_polling

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

    # application.run_polling(allowed_updates=Update.ALL_TYPES)

    async def consume():
        count = 0
        while True:
            count += 1
            print(f"{count=}")
            await asyncio.sleep(1)

    run_polling(application,
                side_coroutines=[consume()],
                allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    run()
