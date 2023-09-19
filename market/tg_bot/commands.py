"""Telegram commands."""
import asyncio
from telegram import Bot

from tg_bot import texts


START = "start"
HELP = "help"
MENU = "menu"
CANCEL = "cancel"
SIGN_OUT = "sign_out"


COMMANDS = [
    (START, texts.START_COMMAND_DESCR),
    (HELP, texts.HELP_COMMAND_DESCR),
    (MENU, texts.MENU_COMMAND_DESCR),
    (CANCEL, texts.CANCEL_COMMAND_DESCR),
    # (SIGN_OUT, texts.SIGN_OUT_COMMAND_DESCR),
]


def set_bot_commands(bot: Bot) -> None:
    """Set available commands for user."""
    loop = asyncio.get_event_loop()
    coroutine = bot.set_my_commands(commands=COMMANDS)
    loop.run_until_complete(coroutine)
