import logging

from django.contrib.auth import get_user_model, models as auth_models

UserModel = get_user_model()

logger = logging.getLogger(__name__)


class UserService:
    """
    Contains methods for working with main user model.

    TG_ADMIN_GROUP_NAME - group name that must be created for tg_bot app.
    Only users from this group can be admins of telegram bot.
    """

    TG_ADMIN_GROUP_NAME = "telegram_admins"

    async def authenticate_telegram_admin(
            self,
            username: str,
            password: str,
    ):
        try:
            user = await UserModel.objects.aget(
                username=username)
        except UserModel.DoesNotExist:
            logger.debug(f"User with {username=} DoesNotExists")
        else:
            is_admin = await user.groups.filter(name=self.TG_ADMIN_GROUP_NAME) \
                .aexists()
            if user.check_password(password) and user.is_active and is_admin:

                logger.debug(f"User: {username} is authenticated.")
                return user
            else:
                logger.debug(
                    f"User: {username} is NOT authenticated. "
                    f"is_active={user.is_active}, is in admin group={is_admin}"
                    f" (if both is Thue, then wrong password)"
                )

    async def get_or_create_tg_admin_group(self):
        group, created = await auth_models.Group.objects.aget_or_create(
            name=self.TG_ADMIN_GROUP_NAME,
        )
        return group, created
