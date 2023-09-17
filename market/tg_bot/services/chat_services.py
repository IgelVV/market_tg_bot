import logging
from typing import Optional

from asgiref.sync import sync_to_async

from telegram.ext import (
    ContextTypes,
)
from django.contrib.auth import get_user_model

from shop.services import ShopService
from tg_bot.services.telegram_user_service import TelegramUserService
from tg_bot.services.user_services import UserService
from tg_bot.models import TelegramUser

UserModel = get_user_model()

logger = logging.getLogger(__name__)


class ChatService:
    """
    Actions and data related to telegram users.

    Uses context.chat_data as a storage.
    """
    ADMIN_ROLE = TelegramUser.Roles.ADMIN
    SELLER_ROLE = TelegramUser.Roles.SELLER

    AUTH_KEY = "authenticated"
    ROLE_KEY = "role"
    SHOP_API_KEY = "shop_api_key"
    ADMIN_USERNAME_KEY = "admin_username"
    SHOP_ID_KEY = "shop id"

    def __init__(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
        self.context = context
        self.chat_id = chat_id

    async def get_role(self):
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

    def get_related_shop_api_key(self):
        """"""
        return self.context.chat_data.get(self.SHOP_API_KEY)

    def set_related_shop_api_key(self, api_key):
        self.context.chat_data[self.SHOP_API_KEY] = api_key

    def get_shop_id(self):
        self.context.chat_data.get(self.SHOP_ID_KEY)

    def set_shop_id(self, shop_id):
        self.context.chat_data[self.SHOP_ID_KEY] = shop_id

    def get_admin_username(self):
        self.context.chat_data.get(self.ADMIN_USERNAME_KEY)

    def set_admin_username(self, username):
        self.context.chat_data[self.ADMIN_USERNAME_KEY] = username

    async def check_to_login(self) -> tuple:
        """

        :return: is_logged_out: Optional[bool],
         is_banned: Optional[bool], is_activate: Optional[bool].
        """
        tg_user_service = TelegramUserService()
        tg_user = await tg_user_service.get_by_chat_id(self.chat_id)

        is_logged_out = None
        is_banned = None
        is_active = None

        if tg_user is not None:
            is_logged_out = tg_user.is_logged_out
            is_banned = tg_user.is_banned
            is_active = tg_user.is_active

        return is_logged_out, is_banned, is_active

    async def authenticate_admin(
            self,
            username: str,
            password: str,
    ):
        user = await UserService()\
            .authenticate_telegram_admin(username, password)
        return user is not None

    async def login_admin(
            self,
            first_name: Optional[str],
            last_name: Optional[str],
            username: Optional[str],
    ):
        """Create or update TelegramUser record."""
        logger.info(f"Admin has logged in: {self.chat_id=}, {first_name=},"
                    f" {last_name=}, {username=},")
        first_name = first_name if first_name is not None else ""
        last_name = last_name if last_name is not None else ""
        username = username if username is not None else ""

        tg_user, created = await TelegramUser.objects.aupdate_or_create(
            chat_id=self.chat_id,
            defaults=dict(
                first_name=first_name,
                last_name=last_name,
                username=username,
                role=TelegramUser.Roles.ADMIN,
                is_logged_out=False,
            )
        )
        self.set_admin_role()
        self.set_shop_id(None)

    async def authenticate_seller(
            self,
            shop_api_key,
            tg_user_id,
    ):
        """
        Mark tg_user (seller) as authenticated, if api_key is correct.

        :param shop_api_key:
        :param tg_user_id:
        :return:
        """
        key_is_correct = await ShopService().check_shop_api_key(shop_api_key)
        if key_is_correct:
            self.context.chat_data[self.AUTH_KEY] = True
            self.set_seller_role()
            self.set_related_shop_api_key(shop_api_key)
            return True
        else:
            return False

        # todo confirmation by admin

    def logout(self):
        """Mark user as not authenticated."""
        self.context.chat_data[self.AUTH_KEY] = False
