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

    def __init__(self, context: ContextTypes.DEFAULT_TYPE):
        self.context = context

    def is_authenticated(self) -> bool:
        return self.context.user_data.get("authenticated", False)

    def get_role(self):
        # find role in db
        return self.context.user_data.get('role')

    def set_role(self):
        ...

    @sync_to_async
    def authenticate_admin(
            self,
            username: str,
            password: str,
            tg_user_id: int,
    ):
        # tg_user_id for saving to db
        try:
            user = UserModel.objects.get(username=username)
            if user.check_password(password):
                self.context.user_data[self.AUTH_KEY] = True
                self.context.user_data[self.ROLE_KEY] = self.ADMIN_ROLE
                return True

        except UserModel.DoesNotExist:
            logger.info(f"User with {username=} DoesNotExist")
            return False

    @sync_to_async
    def check_shop_api_key(self, shop_api_key: str, tg_user_id: int):
        # todo use django service layer to access models
        shop = Shop.objects.filter(api_key=shop_api_key).first()
        if shop:
            return True
        else:
            return False
        # todo confirmation by admin
