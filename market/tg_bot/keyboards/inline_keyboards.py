from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Callback data
ADMIN = "admin"
USER = "user"
YES = "yes"
NO = "no"


def get_role_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Admin", callback_data=ADMIN),
            InlineKeyboardButton("User", callback_data=USER),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_yes_no():
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data=YES),
            InlineKeyboardButton("No", callback_data=NO),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
