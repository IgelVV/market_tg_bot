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
    (START, texts.start_command_description),
    (HELP, texts.help_command_description),
    (MENU, texts.menu_command_description),
    (CANCEL, texts.cancel_command_description),
    (SIGN_OUT, texts.sign_out_command_description),  # todo make it hidden
]


def set_bot_commands(bot: Bot) -> None:
    """Set available commands for user."""
    loop = asyncio.get_event_loop()
    coroutine = bot.set_my_commands(commands=COMMANDS)
    loop.run_until_complete(coroutine)
