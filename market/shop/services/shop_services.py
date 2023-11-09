import logging

from typing import Optional

from django.conf import settings
from django.db.models import QuerySet

from shop.models import Shop
from tg_bot.data_classes import ShopInfo

logger = logging.getLogger(__name__)

LIST_LIMIT = settings.TG_BOT_LIST_LIMIT


class ShopService:
    """Services related to Shop model that are used in the bot."""

    async def paginate_shops_for_buttons(
            self,
            qs: QuerySet[Shop],
            limit: int = LIST_LIMIT,
            offset: int = 0,
    ) -> list[ShopInfo]:
        """
        Prepare `page` of ShopInfo for displaying (e.g. as a keyboard).

        :param qs: QuerySet of Shops
        :param limit: limit
        :param offset: offset
        :return: list of ShopInfo obj. that represents a part of passed
            QuerySet. ShopInfo obj. contains only important fields for
            pagination (id, name, is_active).
        """
        if (limit < 0) or (offset < 0):
            raise AttributeError(
                f"Limit or offset less than 0: {limit=}; {offset=}")

        shops = qs.order_by("id").only("name", "is_active")
        shops = shops[offset:(offset + limit)]

        result = []
        async for shop in shops:
            shop_info = ShopInfo(
                id=shop.pk,
                name=shop.name,
                is_active=shop.is_active,
            )
            result.append(shop_info)
        return result

    async def get_shop_info_by_id(self, shop_id: int) -> ShopInfo:
        """
        Get full information about Shop object.

        :param shop_id: Shop.pk.
        :return: data object ShopInfo.
        """
        shop = await Shop.objects.aget(id=shop_id)
        logger.debug(f"get_shop_info {shop.pk}")
        return self._to_shop_info(shop)

    async def get_shop_info_by_api_key(self, api_key: str) -> ShopInfo:
        """
        Get full information about Shop object.

        :param api_key: api_key, used as identifier
        :return: data object ShopInfo
        """
        shop = await Shop.objects.aget(ozon_api_key=api_key)
        logger.debug(f"get_shop_info {shop.pk=}")
        return self._to_shop_info(shop)

    def _to_shop_info(self, shop: Shop) -> ShopInfo:
        """Convert Shop obj. to ShopInfo."""
        shop_info = ShopInfo(
            id=shop.pk,
            name=shop.name,
            slug=shop.slug,
            api_key=shop.ozon_api_key,
            vendor_name=shop.vendor_name,
            is_active=shop.is_active,
            update_prices=shop.price_updating,
        )
        return shop_info

    async def get_shop_by_api_key(self, shop_api_key: str) -> Optional[Shop]:
        """
        Async get Shop by api_key.

        If shop does not exist returns None
        :param shop_api_key: api_key.
        :return: Shop object or None.
        """
        try:
            shop = await Shop.objects.aget(ozon_api_key=shop_api_key)
            return shop
        except Shop.DoesNotExist:
            logger.debug(f"Shop with {shop_api_key=} DoesNotExist")

    async def get_shop_by_id(self, shop_id) -> Optional[Shop]:
        """
        Async get Shop by id.

        If shop does not exist returns None.
        :param shop_id: Shop.pk.
        :return: Shop object or None.
        """
        try:
            shop = await Shop.objects.aget(id=shop_id)
            return shop
        except Shop.DoesNotExist:
            logger.debug(f"Shop with {shop_id=} DoesNotExist")

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
        shop.update_prices = not shop.update_prices
        await shop.asave()
