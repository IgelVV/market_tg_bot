import logging
from typing import Optional

from asgiref.sync import sync_to_async

from telegram.ext import (
    ContextTypes,
)

from shop.models import Shop

from tg_bot.dataclasses import ShopInfo

logger = logging.getLogger(__name__)


class ShopService:
    # todo use django service layer to access models
    async def count_shops(self):
        return await Shop.objects.acount()

    async def get_shops_to_display(
            self, limit: Optional[int] = None, offset: Optional[int] = None):
        shops = Shop.objects.all() \
            .order_by("id") \
            .values("id", "name")
        if (limit is not None) and (offset is not None):
            shops = shops[offset:(offset + limit)]
        result = []
        async for shop in shops:
            shop_info = ShopInfo(id=shop["id"], name=shop["name"])
            result.append(shop_info)
        return result

    async def get_shop_info(self, shop_id: int):
        shop = await Shop.objects.aget(id=shop_id)
        shop_info = ShopInfo(
            id=shop.pk,
            name=shop.name,
        )
        return shop_info

    async def check_shop_api_key(self, shop_api_key: str):
        exists = await Shop.objects.filter(api_key=shop_api_key).aexists()
        if exists:
            return True
        else:
            return False

    # async def _get_shop_by_api_key(self, shop_api_key: str):
    #     try:
    #         shop = await Shop.objects.aget(api_key=shop_api_key)
    #         return shop
    #     except Shop.DoesNotExist:
    #         logger.info(f"Shop with {shop_api_key} DoesNotExists")
