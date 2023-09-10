import logging

from asgiref.sync import sync_to_async

from telegram.ext import (
    ContextTypes,
)
from django.contrib.auth import get_user_model

from tg_bot.services.shop_services import ShopService

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
        return self.context.user_data.get(self.AUTH_KEY, False)

    def get_role(self):
        # find role in db
        return self.context.user_data.get(self.ROLE_KEY)

    def set_admin_role(self):
        self.context.user_data[self.ROLE_KEY] = self.ADMIN_ROLE

    def set_seller_role(self):
        self.context.user_data[self.ROLE_KEY] = self.SELLER_ROLE

    def get_related_shop_id(self):
        return self.context.user_data.get(self.SHOP_KEY)

    def set_related_shop_id(self):
        # todo checks (role, ...)
        self.context.user_data[self.SHOP_KEY] = self.SHOP_KEY

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

    async def authenticate_seller(
            self,
            shop_api_key,
            tg_user_id,
    ):
        key_is_correct = await ShopService().check_shop_api_key(shop_api_key)
        if key_is_correct:
            self.context.user_data[self.AUTH_KEY] = True
            self.context.user_data[self.ROLE_KEY] = self.SELLER_ROLE
            self.context.user_data[self.SHOP_KEY] = shop_api_key
            return True
        else:
            return False

        # todo confirmation by admin
