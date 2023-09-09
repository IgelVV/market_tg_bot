import logging

from asgiref.sync import sync_to_async

from telegram.ext import (
    ContextTypes,
)
from django.contrib.auth import get_user_model

from shop.models import Shop

UserModel = get_user_model()

logger = logging.getLogger(__name__)


class UserService:
    ADMIN_ROLE = "admin"
    SELLER_ROLE = "seller"

    AUTH_KEY = "authenticated"
    ROLE_KEY = "role"
    SHOP_KEY = "shop"
    ADMIN_USERNAME_KEY = "admin_username"

    def __init__(self, context: ContextTypes.DEFAULT_TYPE):
        self.context = context

    def is_authenticated(self) -> bool:
        return self.context.user_data.get("authenticated", False)

    def get_role(self):
        # find role in db
        return self.context.user_data.get('role')

    def set_role(self):
        ...

    async def authenticate_admin(
            self,
            username: str,
            password: str,
            tg_user_id: int,
    ):
        # tg_user_id for saving to db
        try:
            user = await UserModel.objects.aget(username=username)
            if user.check_password(password):
                self.context.user_data[self.AUTH_KEY] = True
                self.context.user_data[self.ROLE_KEY] = self.ADMIN_ROLE
                self.context.user_data[self.ADMIN_USERNAME_KEY] = username
                return True

        except UserModel.DoesNotExist:
            logger.info(f"User with {username=} DoesNotExists")
            return False

    # todo move to shop_services
    async def check_shop_api_key(self, shop_api_key: str):
        # todo use django service layer to access models
        exists = await Shop.objects.filter(api_key=shop_api_key).aexists()
        if exists:
            return True
        else:
            return False

    async def _get_shop_by_api_key(self, shop_api_key: str):
        try:
            shop = await Shop.objects.aget(api_key=shop_api_key)
            return shop
        except Shop.DoesNotExist:
            logger.info(f"Shop with {shop_api_key} DoesNotExists")

    async def authenticate_seller(
            self,
            shop_api_key,
            tg_user_id,
    ):
        key_is_correct = await self.check_shop_api_key(shop_api_key)
        if key_is_correct:
            self.context.user_data[self.AUTH_KEY] = True
            self.context.user_data[self.ROLE_KEY] = self.SELLER_ROLE
            self.context.user_data[self.SHOP_KEY] = shop_api_key
            return True
        else:
            return False

        # todo confirmation by admin
