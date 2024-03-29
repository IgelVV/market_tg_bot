"""
Service for using in handlers.

It allows interacting with telegram context, and other services.
"""

import logging
from typing import Optional
from enum import Enum, auto

from telegram.ext import (
    ContextTypes,
)
from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from shop.services import ShopService
from shop.models import Shop
from tg_bot.services.telegram_user_service import TelegramUserService
from tg_bot.services.user_services import UserService
from tg_bot.models import TelegramUser
from tg_bot.data_classes import ShopInfo

UserModel = get_user_model()

logger = logging.getLogger(__name__)


class ExpectedInput(Enum):
    """States for text message dispatcher."""
    USERNAME = auto()
    PASSWORD = auto()
    API_KEY_TO_LOGIN = auto()
    API_KEY_TO_ADD = auto()


class ChatService:
    """
    Actions and data related to telegram users.

    Uses context.chat_data as a storage.
    Constants with `_ROLE` postfix are used fer marking user's roles.
    It can be any immutable object, e.g. strings with verbose names of roles.

    Constants with `_KEY` postfix are used for data storage
    in context.chat_data.
    """
    ADMIN_ROLE = TelegramUser.Roles.ADMIN
    SELLER_ROLE = TelegramUser.Roles.SELLER

    AUTH_KEY = "authenticated"
    ROLE_KEY = "role"
    SHOP_INFO_KEY = "shop_info"
    SHOP_INFO_TO_UNLINK_KEY = "shop_to_unlink"
    ADMIN_USERNAME_KEY = "admin_username"
    EXPECTED_INPUT_KEY = "expected_input"

    def __init__(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
        self.context = context
        self.chat_id = chat_id

    async def get_role(self):
        """Get role from chat_data or from db."""
        cached_role = self.context.chat_data.get(self.ROLE_KEY)
        if cached_role:
            return cached_role
        else:
            tg_user_service = TelegramUserService()
            tg_user = await tg_user_service.get_by_chat_id(self.chat_id)
            if tg_user is None:
                return None
            role = tg_user.role
            if role == TelegramUser.Roles.ADMIN:
                self.set_admin_role()
            elif role == TelegramUser.Roles.SELLER:
                self.set_seller_role()
            else:
                raise ValueError("Unknown TelegramUser role.")
            return self.context.chat_data.get(self.ROLE_KEY)

    def set_admin_role(self):
        """Set tg_user role as `admin`."""
        self.context.chat_data[self.ROLE_KEY] = self.ADMIN_ROLE

    def set_seller_role(self):
        """Set tg_user role as `seller`."""
        self.context.chat_data[self.ROLE_KEY] = self.SELLER_ROLE

    def get_shop_info(self) -> ShopInfo:
        return self.context.chat_data.get(self.SHOP_INFO_KEY)

    def set_shop_info(self, shop: ShopInfo):
        self.context.chat_data[self.SHOP_INFO_KEY] = shop

    def get_shop_info_to_unlink(self) -> ShopInfo:
        return self.context.chat_data.get(self.SHOP_INFO_TO_UNLINK_KEY)

    def set_shop_info_to_unlink(self, shop: ShopInfo):
        self.context.chat_data[self.SHOP_INFO_TO_UNLINK_KEY] = shop

    def get_admin_username(self):
        return self.context.chat_data.get(self.ADMIN_USERNAME_KEY)

    def set_admin_username(self, username):
        self.context.chat_data[self.ADMIN_USERNAME_KEY] = username

    def get_expected_input(self):
        return self.context.chat_data.get(self.EXPECTED_INPUT_KEY)

    def set_expected_input(self, input_type: Optional[ExpectedInput]):
        self.context.chat_data[self.EXPECTED_INPUT_KEY] = input_type

    async def get_shops(self) -> QuerySet[Shop]:
        """Get available Shops depending on TgUser.role."""
        role = await self.get_role()
        if role == self.SELLER_ROLE:
            shops = await TelegramUserService().get_related_shops_by_chat_id(
                self.chat_id)
        elif role == self.ADMIN_ROLE:
            shops = Shop.objects.all()
        else:
            raise ValueError(f"Wrong {role=}")
        return shops

    async def get_statuses(self) -> tuple:
        """
        Get all TgUser statuses at once.

        If user does not exist return None in every status.
        :return: is_banned: Optional[bool], is_activate: Optional[bool],
        is_logged_out: Optional[bool].
        """
        tg_user_service = TelegramUserService()
        tg_user = await tg_user_service.get_by_chat_id(self.chat_id)

        is_banned = None
        is_active = None
        is_logged_out = None

        if tg_user is not None:
            is_banned = tg_user.is_banned
            is_active = tg_user.is_active
            is_logged_out = tg_user.is_logged_out

        return is_banned, is_active, is_logged_out

    async def authenticate_admin(
            self,
            username: str,
            password: str,
    ) -> bool:
        """
        Check if User with the credentials exists
        and in telegram admin group.

        :param username: Username of User
        :param password: Password of User
        :return: True if authenticated.
        """
        user = await UserService() \
            .authenticate_telegram_admin(username, password)
        return user is not None

    async def login_admin(
            self,
            first_name: Optional[str],
            last_name: Optional[str],
            tg_username: Optional[str],
    ):
        """Create or update TelegramUser record."""
        logger.debug(f"Admin has logged in: {self.chat_id=}, {first_name=},"
                     f" {last_name=}, {tg_username=},")
        first_name = first_name if first_name is not None else ""
        last_name = last_name if last_name is not None else ""
        tg_username = tg_username if tg_username is not None else ""

        tg_user, created = await TelegramUser.objects.aupdate_or_create(
            chat_id=self.chat_id,
            defaults=dict(
                first_name=first_name,
                last_name=last_name,
                username=tg_username,
                role=TelegramUser.Roles.ADMIN,
                is_logged_out=False,
            )
        )
        self.set_admin_role()

    async def authenticate_and_login_seller(
            self,
            shop_api_key: str,
            first_name: Optional[str],
            last_name: Optional[str],
            tg_username: Optional[str],
    ):
        """Create or update TelegramUser record."""
        # authentication
        shop_service = ShopService()
        shop = await shop_service.get_shop_by_api_key(shop_api_key)
        # if (shop is None) or (not shop.is_active):
        if shop is None:
            return False
        else:
            # login
            first_name = first_name if first_name is not None else ""
            last_name = last_name if last_name is not None else ""
            tg_username = tg_username if tg_username is not None else ""

            tg_user, created = await TelegramUser.objects.aupdate_or_create(
                chat_id=self.chat_id,
                defaults=dict(
                    first_name=first_name,
                    last_name=last_name,
                    username=tg_username,
                    role=TelegramUser.Roles.SELLER,
                    is_logged_out=False,
                )
            )
            await tg_user.shops.aadd(shop)
            self.set_seller_role()

            logger.debug(
                f"Seller has logged in: {self.chat_id=}, {first_name=},"
                f" {last_name=}, {tg_username=}, {shop.pk=}")
            return True

    async def logout(self):
        """
        Mark user as logged out.

        Allows restart authentication and logging in to refresh user data
        (e.g. change role, or names).
        """
        tg_user_service = TelegramUserService()
        await tg_user_service.mark_as_logged_out_by_chat_id(self.chat_id)

    async def add_shop(self, shop_api_key: str):
        try:
            shop_info = await ShopService().get_shop_info_by_api_key(
                shop_api_key)
        except Shop.DoesNotExist:
            return None
        await TelegramUserService().add_shop_by_chat_id(
            chat_id=self.chat_id,
            shop_id=shop_info.id
        )
        return shop_info
