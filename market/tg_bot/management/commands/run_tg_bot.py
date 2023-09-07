from django.core.management.base import BaseCommand, CommandError
from tg_bot import bot


class Command(BaseCommand):
    help = "Run telegram bot."

    def handle(self, *args, **options):
        bot.run()