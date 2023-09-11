"""Telegram commands."""
import asyncio
from telegram import Bot


COMMANDS = [
    ("start", "Start"),
    ("menu", "Available actions"),
    ("cancel", "Cancel the current operation"),
    ("signOut", "logout TEST command"),
]


def set_bot_commands(bot: Bot) -> None:
    """Set available commands for user."""
    loop = asyncio.get_event_loop()
    coroutine = bot.set_my_commands(commands=COMMANDS)
    loop.run_until_complete(coroutine)
