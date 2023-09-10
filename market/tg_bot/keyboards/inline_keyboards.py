import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from django.conf import settings

from tg_bot.dataclasses import ShopInfo, Navigation
from tg_bot.services.shop_services import ShopService

logger = logging.getLogger(__name__)

LIST_LIMIT = settings.TG_BOT_LIST_LIMIT

# Callback data
ADMIN = "admin"
SELLER = "seller"

YES = "yes"
NO = "no"

CANCEL = "cancel"

SHOP_LIST = "shop_list"

ACTIVATE = "activate"
SHOP_INFO = "shop_info"
PRICE_UPDATING = "price_updating"


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
    keyboard = []
    shops: list[ShopInfo] = await ShopService().get_shops_to_display(
        limit=limit,
        offset=offset,
    )
    for shop in shops:
        keyboard.append(
            [InlineKeyboardButton(shop.name, callback_data=shop)]
        )
    keyboard.append(
        build_navigation_buttons(
            limit=limit, offset=offset, list_len=len(shops))
    )

    return InlineKeyboardMarkup(keyboard)


def build_navigation_buttons(limit: int, offset: int, list_len: int):
    if offset > 0:
        nav_back = Navigation(limit=limit, offset=max(0, (offset - limit)))
    else:
        nav_back = Navigation(limit=limit, offset=0)
    if list_len < limit:
        nav_forward = Navigation(limit=limit, offset=offset)
    else:
        nav_forward = Navigation(limit=limit, offset=(offset + limit))

    buttons = [
            InlineKeyboardButton("<<", callback_data=nav_back),
            InlineKeyboardButton(">>", callback_data=nav_forward),
        ]
    return buttons


def build_shop_menu():
    keyboard = [
        [InlineKeyboardButton("Activate", callback_data=ACTIVATE)],
        [InlineKeyboardButton("Shop info", callback_data=SHOP_INFO)],
        [InlineKeyboardButton("Price updating", callback_data=PRICE_UPDATING)],
    ]
    return InlineKeyboardMarkup(keyboard)
