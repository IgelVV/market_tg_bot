"""Inline keyboard builders and related data."""
import logging

from math import ceil

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from django.conf import settings
from django.db.models import QuerySet

from tg_bot.data_classes import ShopInfo, Navigation
from tg_bot import utils
from shop.services import ShopService
from shop.models import Shop

logger = logging.getLogger(__name__)

# Maximum items per list, used in pagination
LIST_LIMIT = settings.TG_BOT_LIST_LIMIT

# Callback data:
ADMIN_LOGIN = "admin"
SELLER_LOGIN = "seller"

BACK_TO_CHOOSE_ROLE = "back_to_choose_role"

YES = "yes"
NO = "no"

USER_MENU = "user_menu"

BACK = "back"

CANCEL = "cancel"

SHOP_LIST = "shop_list"

ADD_SHOP = "add_shop"
UNLINK_SHOP = "unlink_shop"

ACTIVATE = "activate"
SHOP_INFO = "shop_info"
PRICE_UPDATING = "price_updating"

DO_NOTHING = "do_nothing"

SWITCH_ACTIVATION = "switch_activation"
SWITCH_PRICE_UPDATING = "switch_price_updating"


def build_role_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Админ", callback_data=ADMIN_LOGIN),
            InlineKeyboardButton("Продавец", callback_data=SELLER_LOGIN),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_wrong_credentials():
    keyboard = [
        [
            InlineKeyboardButton("Ввести username", callback_data=ADMIN_LOGIN),
            InlineKeyboardButton("Отмена", callback_data=CANCEL),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_yes_no(yes_data=YES, no_data=NO):
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data=yes_data),
            InlineKeyboardButton("Нет", callback_data=no_data),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_cancel():
    keyboard = [
        [
            InlineKeyboardButton("Отмена", callback_data=CANCEL),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def build_admin_menu():
    keyboard = [
        [
            InlineKeyboardButton("📋 Список магазинов 📋", callback_data=SHOP_LIST),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def build_seller_menu():
    keyboard = [
        [InlineKeyboardButton("➕ Добавить магазин ➕", callback_data=ADD_SHOP)],
        [InlineKeyboardButton("➖ Отвязать магазин ➖", callback_data=UNLINK_SHOP)],
        [InlineKeyboardButton("📋 Список магазинов 📋", callback_data=SHOP_LIST)],
    ]
    return InlineKeyboardMarkup(keyboard)


async def build_shop_list(
        qs: QuerySet[Shop],
        limit: int = LIST_LIMIT,
        offset: int = 0,
        with_back: bool = True,
):
    # """
    # Build keyboard, that contains shop list.
    #
    # It uses pagination.
    # :param limit: maximum items per page.
    # :param offset: index of start item.
    # :return: keyboard with navigation buttons.
    # """
    shop_service = ShopService()
    shops: list[ShopInfo] = await shop_service.paginate_shops_for_buttons(
        qs=qs,
        limit=limit,
        offset=offset,
    )
    keyboard = []
    for shop in shops:
        keyboard.append(
            [InlineKeyboardButton(
                f"{shop.name} {utils.readable_shop_activiti(shop.is_active)}",
                callback_data=shop,
            )]
        )
    keyboard.append(
        _build_navigation_buttons(
            limit=limit,
            offset=offset,
            displayed_count=len(shops),
            total_count=await qs.acount(),
        )
    )
    if with_back:
        keyboard.append(_build_back_button())
    return InlineKeyboardMarkup(keyboard)


def build_shop_menu(with_back: bool = False):
    keyboard = [
        [InlineKeyboardButton(
            "ℹ️ Информация о магазине ℹ️", callback_data=SHOP_INFO)],
        [InlineKeyboardButton(
            f"🔘 {'Активация': ^34} 🔘", callback_data=ACTIVATE)],
        [InlineKeyboardButton(
            f"💰 {'Обновление цен': ^29} 💰", callback_data=PRICE_UPDATING)],
    ]
    if with_back:
        keyboard.append(_build_back_button())
    return InlineKeyboardMarkup(keyboard)


def build_back(back_data=BACK):
    back_button = _build_back_button(back_data)
    keyboard = [back_button]
    return InlineKeyboardMarkup(keyboard)


def build_activate_shop(is_active: bool):
    if is_active:
        text = "⏹ Деактивировать ⏹"
    else:
        text = "▶️ Активировать ▶️"

    keyboard = [
        [InlineKeyboardButton(text, callback_data=SWITCH_ACTIVATION), ],
        _build_back_button()
    ]
    return InlineKeyboardMarkup(keyboard)


def build_price_updating(is_updating_on: bool):
    if is_updating_on:
        text = "⏹ OFF ⏹"
    else:
        text = "▶️ ON ▶️"

    keyboard = [
        [InlineKeyboardButton(text, callback_data=SWITCH_PRICE_UPDATING), ],
        _build_back_button()
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_navigation_buttons(
        limit: int, offset: int, displayed_count: int, total_count: int):
    """
    Creates navigation buttons to adding to keyboards as a line.

    Displays: `back`, `page counter`, `next`.
    :param limit: maximum items per page.
    :param offset: index of start item.
    :param displayed_count: how many items in the current page.
    :param total_count: total amount of items.
    :return: buttons for keyboard.
    """
    if offset > 0:
        nav_back = Navigation(limit=limit, offset=max(0, (offset - limit)))
    else:
        nav_back = Navigation(limit=limit, offset=0)
    if displayed_count < limit:
        nav_forward = Navigation(limit=limit, offset=offset)
    else:
        nav_forward = Navigation(limit=limit, offset=(offset + limit))

    buttons = [
        InlineKeyboardButton("<<", callback_data=nav_back),
        InlineKeyboardButton(
            f"{offset // limit + 1} / {ceil(total_count / limit)}",
            callback_data=DO_NOTHING
        ),
        InlineKeyboardButton(">>", callback_data=nav_forward),
    ]
    return buttons


def _build_back_button(back_data=BACK):
    """Creates `back` button to adding to keyboards as a line."""
    # button = [InlineKeyboardButton("\U0001F868", callback_data=BACK)]
    # ↤ ⟵ ← ⇐ ↵ ⤶
    button = [InlineKeyboardButton("⟵", callback_data=back_data)]
    return button
