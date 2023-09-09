import asyncio
from telegram import Bot


COMMANDS = [
    ("menu", "Available actions"),
    ("cancel", "Cancel the current operation"),
]


def set_bot_commands(bot: Bot) -> None:
    loop = asyncio.get_event_loop()
    coroutine = bot.set_my_commands(commands=COMMANDS)
    loop.run_until_complete(coroutine)