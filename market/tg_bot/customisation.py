import asyncio
from telegram import Bot

from tg_bot import texts, commands


COMMANDS = [
    (commands.START, texts.START_COMMAND_DESCR),
    (commands.HELP, texts.HELP_COMMAND_DESCR),
    (commands.MENU, texts.MENU_COMMAND_DESCR),
    (commands.CANCEL, texts.CANCEL_COMMAND_DESCR),
    # (commands.SIGN_OUT, texts.SIGN_OUT_COMMAND_DESCR),
]


def set_bot_commands(bot: Bot) -> None:
    """Set available commands for user."""
    loop = asyncio.get_event_loop()
    coroutine = bot.set_my_commands(commands=COMMANDS)
    loop.run_until_complete(coroutine)


def set_bot_description(bot: Bot) -> None:
    """Set available commands for user."""
    loop = asyncio.get_event_loop()
    coroutine = bot.set_my_description(description=texts.BOT_DESCRIPTION[:512])
    loop.run_until_complete(coroutine)


def set_bot_short_description(bot: Bot) -> None:
    """Set available commands for user."""
    loop = asyncio.get_event_loop()
    coroutine = bot.set_my_short_description(
        short_description=texts.BOT_SHORT_DESCRIPTION[:120])
    loop.run_until_complete(coroutine)
