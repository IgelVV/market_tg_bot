import logging

from math import ceil

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

DO_NOTHING = "do_nothing"


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
    shop_service = ShopService()
    shops: list[ShopInfo] = await shop_service.get_shops_to_display(
        limit=limit,
        offset=offset,
    )
    for shop in shops:
        keyboard.append(
            [InlineKeyboardButton(f"{shop.name}", callback_data=shop,)]
        )
    keyboard.append(
        build_navigation_buttons(
            limit=limit,
            offset=offset,
            displayed_count=len(shops),
            total_count=await shop_service.count_shops(),
        )
    )

    return InlineKeyboardMarkup(keyboard)


def build_navigation_buttons(
        limit: int, offset: int, displayed_count: int, total_count: int):
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
            f"{offset//limit + 1} / {ceil(total_count/limit)}",
            callback_data=DO_NOTHING
        ),
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
