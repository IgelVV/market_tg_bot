import logging

from typing import Optional
from asgiref.sync import sync_to_async

from django.conf import settings
from django.db.models import QuerySet

from shop.models import Shop
from tg_bot.dataclasses import ShopInfo

logger = logging.getLogger(__name__)

LIST_LIMIT = settings.TG_BOT_LIST_LIMIT


class ShopService:
    """Services related to Shop model that are used in the bot."""

    # todo use django service layer to access models
    async def count_shops(self):
        """Count all shops."""
        # todo cache
        return await Shop.objects.acount()

    async def paginate_shops_for_buttons(
            self,
            qs: QuerySet[Shop],
            limit: int = LIST_LIMIT,
            offset: int = 0,
    ):
        if (limit < 0) or (offset < 0):
            raise AttributeError(
                f"Limit or offset less than 0: {limit=}; {offset=}")

        shops = qs.order_by("id").only("name")
        shops = shops[offset:(offset + limit)]

        result = []
        async for shop in shops:
            shop_info = ShopInfo(
                id=shop.pk,
                name=shop.name,
            )
            result.append(shop_info)
        return result

    async def get_shop_info(self, shop_id: int):
        """
        Get full information about Shop object.

        :param shop_api_key: api_key, used as identifier
        :return: data object ShopInfo
        """
        logger.info(f"get_shop_info {shop_id}")
        shop = await Shop.objects.aget(id=shop_id)
        shop_info = ShopInfo(
            id=shop.pk,
            name=shop.name,
            slug=shop.slug,
            api_key=shop.api_key,
            vendor_name=shop.vendor_name,
            is_active=shop.is_active,
            stop_updated_price=shop.stop_updated_price,
            individual_updating_time=shop.individual_updating_time,
        )
        return shop_info

    async def check_shop_api_key(self, shop_api_key: str):
        """
        Check if shop with passed api_key exists.

        :param shop_api_key: api_key.
        :return: bool
        """
        return await Shop.objects.filter(api_key=shop_api_key).aexists()

    async def get_shop_by_api_key(self, shop_api_key: str) -> Optional[Shop]:
        """
        Get shop by api_key.

        If shop does not exist returns None
        :param shop_api_key: api_key.
        :return: Shop object or None.
        """
        try:
            shop = await Shop.objects.aget(api_key=shop_api_key)
            return shop
        except Shop.DoesNotExist:
            logger.info(f"Shop with {shop_api_key=} DoesNotExist")

    async def get_shop_by_id(self, shop_id) -> Optional[Shop]:
        try:
            shop = await Shop.objects.aget(id=shop_id)
            return shop
        except Shop.DoesNotExist:
            logger.info(f"Shop with {shop_id=} DoesNotExist")

    async def switch_activation(self, shop_id):
        """Changes `is_active` field in Shop object to opposite value."""
        shop = await self.get_shop_by_id(shop_id)
        shop.is_active = not shop.is_active
        await shop.asave()

    async def switch_price_updating(self, shop_id):
        """
        Changes `stop_updated_price` field in Shop object to opposite value.
        """
        shop = await self.get_shop_by_id(shop_id)
        shop.stop_updated_price = not shop.stop_updated_price
        await shop.asave()