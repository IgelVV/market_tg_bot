from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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


def build_shop_list(limit=None, offset=None):
    # keyboard = []
    # shops = shop_services.get_shops_to_display()
    # for shop in shops:
    #     keyboard.append(
    #         [InlineKeyboardButton(shop.name, callback_data=f"shop_{shop.slug}")]
    #     )
    # keyboard.append(
    #     [
    #         InlineKeyboardButton("<<", callback_data=f"previous_page_limit_{limit}_offset_{offset}")
    #         InlineKeyboardButton(">>", callback_data=f"next_page_limit_{limit}_offset_{offset}")
    #     ]
    # )
    # todo create SHOP_PREFIX = 'shop_' PREVIOUS_PAGE_PREFIX = 'previous_page_'
    #  NEXT_PAGE_PREFIX = 'NEXT_page_'

    keyboard = [
        [InlineKeyboardButton("shop1", callback_data='shop_shop1')],
        [InlineKeyboardButton("shop2", callback_data='shop_shop2')],
        [InlineKeyboardButton("shop3", callback_data='shop_shop3')],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_shop_menu():
    keyboard = [
        [InlineKeyboardButton("Activate", callback_data=ACTIVATE)],
        [InlineKeyboardButton("Shop info", callback_data=SHOP_INFO)],
        [InlineKeyboardButton("Price updating", callback_data=PRICE_UPDATING)],
    ]
    return InlineKeyboardMarkup(keyboard)
