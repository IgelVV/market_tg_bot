import logging
from typing import Optional

from asgiref.sync import sync_to_async

from telegram.ext import (
    ContextTypes,
)
from django.contrib.auth import get_user_model, models as auth_models

from shop.services.shop_services import ShopService
from tg_bot.models import TelegramUser

UserModel = get_user_model()

logger = logging.getLogger(__name__)


class TelegramUserService:


    # async def does_exist_by_chat_id(self, chat_id: int):
    #     return await TelegramUser.objects\
    #         .filter(chat_id=chat_id)\
    #         .aexists()

    async def get_by_chat_id(self, chat_id: int) -> Optional[TelegramUser]:
        try:
            tg_user = await TelegramUser.objects.aget(chat_id=chat_id)
            return tg_user
        except TelegramUser.DoesNotExist:
            return None

    async def create_or_update(self, ignore_is_banned=False, ignore_is_active=False):
        # check is_banned and is_active
        ...