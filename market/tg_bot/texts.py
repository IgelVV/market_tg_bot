"""Text for bot messages, commands."""

# Messages:
HELP_TEXT = """
Основной способ управления ботом - интерактивные кнопки, под сообщениями. \
Однако при длительном бездействии кнопки становятся неактивными. \
В таком случае на помощь приходят команды, доступные в любое время.

Список команд для управления ботом:
/start - запуск диалога с ботом.
/menu - переход в меню пользователя из любого места диалога.
/cancel - отмена действия и завершение диалога. \
После использования этой команды необходимо заново запустить диалог.

При вводе текста с клавиатуры, например пароля или API key, текст, \
который начинается как команда с '/' будет распознан как команда. \
По этому не используйте данные, начинающиеся с этого символа.

Служебные команды: 
/sign_out - позволяет повторно пройти процесс регистрации. \
Используется для смены роли или обновления данных пользователя, \
таких как `username`.
"""

START_CHOOSE_ROLE = "Choose your role"

DISPLAY_USER_MENU = "Main menu ({full_name}: {role}):"

DISPLAY_ADD_SHOP = "Add shop by API key. \nType new API key:"

SHOP_IS_ADDED = "Shop `{name}` is added."

DISPLAY_UNLINK_SHOP = "Unlink shop from the seller."

UNLINK_SHOP = "Forget shop `{name}`?"

DISPLAY_SHOP_LIST = "Available shops:"

DISPLAY_SHOP_MENU = "Shop: `{name}`"

DISPLAY_SHOP_INFO = \
    "<b>Full shop information</b>\n" \
    "Id: {id}\n" \
    "Name: {name}\n" \
    "Slug: {slug}\n" \
    "API key: {api_key}\n" \
    "Vendor Name: {vendor_name}\n" \
    "Is Active: {is_active}\n" \
    "Stop updated price: {stop_updated_price}\n" \
    "Individual updating time: {individual_updating_time}\n"

ACTIVATE_SHOP = "Shop name: {name}\nIs active: {is_active}"

PRICE_UPDATING = "Shop name: {name}\n" \
                 "Price updating: {switch}"

DISPLAY_BAN = "You are banned. Contact the support service to unban."

DISPLAY_NOT_ACTIVE = "Your account is not active. " \
                     "Buy a subscription to the service"

INVALID_BUTTON = "Sorry, I could not process this button click 😕 " \
                 "Please send /start to get a new keyboard."

CANCEL = "Bye! I hope we can talk again some day."


ASK_USERNAME = "Type your Username:"

ASK_PASSWORD = "Type password:"

PASSWORD_RECEIVED = "Password received: {password} \nPlease wait."

LOGGED_IN_AS_ADMIN = "You are logged in as admin."

WRONG_CREDENTIALS = "Wrong username or password.\nDo you want to try again?"

ASK_SHOP_API_KEY = "Type API key of your shop:"

API_KEY_RECEIVED = "API key received: {shop_api_key} \nPlease wait."

LOGGED_IN_AS_SELLER = "You are logged in as Seller."

WRONG_API_KEY = "Wrong API key, please enter it again:"


# Commands:
START_COMMAND_DESCR = "Start"
HELP_COMMAND_DESCR = "Information about the work of the bot"
MENU_COMMAND_DESCR = "Available actions"
CANCEL_COMMAND_DESCR = "Cancel the current operation"
SIGN_OUT_COMMAND_DESCR = "logout TEST command"


# Callback answers:
ASK_USERNAME_ANS = None
ASK_SHOP_API_KEY_ANS = None
DISPLAY_USER_MENU_ANS = "User menu"
DISPLAY_ADD_SHOP_ANS = "Add shop"
DISPLAY_UNLINK_SHOP_ANS = "Unlink shops"
CONFIRM_UNLINK_SHOP_ANS = "Unlink `{name}`"
UNLINK_SHOP_ANS = "Shop `{name}` is unlinked."
DISPLAY_SHOP_LIST_ANS = "Shop list"
DISPLAY_SHOP_MENU_ANS = "Shop `{name}` menu"
DISPLAY_SHOP_INFO_ANS = "Shop info"
ACTIVATE_SHOP_ANS = "Activation"
SWITCH_ACTIVATION_ANS = "Switch activation"
PRICE_UPDATING_ANS = "Price updating"
SWITCH_PRICE_UPDATING_ANS = "Switch price updating"
CANCEL_ANS = "Cancel"
HANDLE_INVALID_BUTTON_ANS = "Invalid button"
