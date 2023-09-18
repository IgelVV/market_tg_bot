import logging
from typing import Optional

from asgiref.sync import sync_to_async

from telegram.ext import (
    ContextTypes,
)
from django.contrib.auth import get_user_model, models as auth_models
from django.db.models import QuerySet

from shop.services.shop_services import ShopService
from shop.models import Shop
from tg_bot.models import TelegramUser

UserModel = get_user_model()

logger = logging.getLogger(__name__)


class TelegramUserService:

    async def get_by_chat_id(self, chat_id: int) -> Optional[TelegramUser]:
        try:
            tg_user = await TelegramUser.objects.aget(chat_id=chat_id)
            return tg_user
        except TelegramUser.DoesNotExist:
            return None

    async def mark_as_logged_out_by_chat_id(self, chat_id: int):
        tg_user = await self.get_by_chat_id(chat_id)
        tg_user.is_logged_out = True
        await tg_user.asave()

    async def get_related_shops_by_chat_id(self, chat_id: int) -> QuerySet[Shop]:
        tg_user = await self.get_by_chat_id(chat_id)
        return tg_user.shops.all()

    async def add_shop_by_chat_id(self, chat_id: int, shop_id: int):
        tg_user = await self.get_by_chat_id(chat_id)
        if tg_user is None:
            raise TelegramUser.DoesNotExist
        await tg_user.shops.aadd(shop_id)

    async def unlink_shop_by_chat_id(self, chat_id: int, shop_id: int):
        tg_user = await self.get_by_chat_id(chat_id)
        if tg_user is None:
            raise TelegramUser.DoesNotExist
        await tg_user.shops.aremove(shop_id)
