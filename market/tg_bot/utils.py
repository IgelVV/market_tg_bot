from tg_bot import texts
from tg_bot.models import TelegramUser


def readable_role(role):
    """Convert internal role marker into a user-friendly text or picture."""
    if role == TelegramUser.Roles.ADMIN:
        return texts.READABLE_ADMIN_ROLE
    elif role == TelegramUser.Roles.SELLER:
        return texts.READABLE_SELLER_ROLE
    else:
        raise ValueError("Unknown TelegramUser role.")


def readable_flag(flag: bool):
    """Convert bool into a user-friendly text or picture."""
    if flag:
        return texts.READABLE_TRUE
    else:
        return texts.READABLE_FALSE


def readable_shop_activiti(is_active: bool):
    """
    Convert internal is_active marker into a user-friendly text or picture.
    """
    if is_active:
        return texts.READABLE_ACTIVE
    else:
        return texts.READABLE_INACTIVE
