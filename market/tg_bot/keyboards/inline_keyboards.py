"""Inline keyboard builders and related data."""
import logging

from math import ceil

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from django.conf import settings

from tg_bot.dataclasses import ShopInfo, Navigation
from tg_bot.services.shop_services import ShopService

logger = logging.getLogger(__name__)

# Maximum items per list, used in pagination
LIST_LIMIT = settings.TG_BOT_LIST_LIMIT

# Callback data:
ADMIN = "admin"
SELLER = "seller"

YES = "yes"
NO = "no"

BACK = "back"

CANCEL = "cancel"

SHOP_LIST = "shop_list"

ACTIVATE = "activate"
SHOP_INFO = "shop_info"
PRICE_UPDATING = "price_updating"

DO_NOTHING = "do_nothing"

SWITCH_ACTIVATION = "switch_activation"
SWITCH_PRICE_UPDATING = "switch_price_updating"


def build_role_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Admin", callback_data=ADMIN),
            InlineKeyboardButton("Seller", callback_data=SELLER),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_yes_no():
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data=YES),
            InlineKeyboardButton("No", callback_data=NO),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_cancel():
    keyboard = [
        [
            InlineKeyboardButton("Cancel", callback_data=CANCEL),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def build_admin_menu():
    keyboard = [
        [
            InlineKeyboardButton("Shop list", callback_data=SHOP_LIST),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


async def build_shop_list(limit: int = LIST_LIMIT, offset: int = 0):
    """
    Build keyboard, that contains shop list.

    It uses pagination.
    :param limit: maximum items per page.
    :param offset: index of start item.
    :return: keyboard with navigation buttons.
    """
    keyboard = []
    shop_service = ShopService()
    shops: list[ShopInfo] = await shop_service.get_shops_to_display(
        limit=limit,
        offset=offset,
    )
    for shop in shops:
        keyboard.append(
            [InlineKeyboardButton(f"{shop.name}", callback_data=shop, )]
        )
    keyboard.append(
        _build_navigation_buttons(
            limit=limit,
            offset=offset,
            displayed_count=len(shops),
            total_count=await shop_service.count_shops(),
        )
    )
    return InlineKeyboardMarkup(keyboard)


def build_shop_menu():
    keyboard = [
        [InlineKeyboardButton("Shop info", callback_data=SHOP_INFO)],
        [InlineKeyboardButton("Activate", callback_data=ACTIVATE)],
        [InlineKeyboardButton("Price updating", callback_data=PRICE_UPDATING)],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_back():
    back_button = _build_back_button()
    keyboard = [back_button]
    return InlineKeyboardMarkup(keyboard)


def build_activate_shop(is_active: bool):
    if is_active:
        text = "Deactivate"
    else:
        text = "Activate"

    keyboard = [
        [InlineKeyboardButton(text, callback_data=SWITCH_ACTIVATION), ],
        _build_back_button()
    ]
    return InlineKeyboardMarkup(keyboard)


def build_price_updating(is_updating_on: bool):
    if is_updating_on:
        text = "OFF"
    else:
        text = "ON"

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


def _build_back_button():
    """Creates `back` button to adding to keyboards as a line."""
    button = [InlineKeyboardButton("\U0001F868", callback_data=BACK)]
    return button
