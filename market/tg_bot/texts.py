"""Text for bot messages, commands."""

# Messages:
help_text = """
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

start_choose_role = "Choose your role"

after_login = "Hello {full_name} your role is {role}"

display_user_menu = "Main menu ({full_name}: {role}):"

display_add_shop = "Add shop by API key. \nType new API key:"

shop_is_added = "Shop `{name}` is added."

display_unlink_shop = "Unlink shop from the seller."

unlink_shop = "Forget shop `{name}`?"

display_shop_list = "Available shops:"

display_shop_menu = "Shop: `{name}`"

display_shop_info = \
    "<b>Full shop information</b>\n" \
    "Id: {id}\n" \
    "Name: {name}\n" \
    "Slug: {slug}\n" \
    "API key: {api_key}\n" \
    "Vendor Name: {vendor_name}\n" \
    "Is Active: {is_active}\n" \
    "Stop updated price: {stop_updated_price}\n" \
    "Individual updating time: {individual_updating_time}\n"

activate_shop = "Shop name: {name}\nIs active: {is_active}"

price_updating = "Shop name: {name}\n" \
                 "Price updating: {switch}"

display_ban = "You are banned."

display_not_active = "Your account is not active."

invalid_button = "Sorry, I could not process this button click 😕 " \
                 "Please send /start to get a new keyboard."


ask_username = "Type your Username:"

ask_password = "Type password:"

password_received = "Password received: {password} \nPlease wait."

logged_in_as_admin = "You are logged in as admin."

wrong_credentials = "Wrong username or password.\nDo you want to try again?"

ask_shop_api_key = "Type API key of your shop:"

api_key_received = "API key received: {shop_api_key} \nPlease wait."

logged_in_as_seller = "You are logged in as Seller."

wrong_api_key = "Wrong API key, please enter it again:"


# Commands:
start_command_description = "Start"
help_command_description = "Information about the work of the bot"
menu_command_description = "Available actions"
cancel_command_description = "Cancel the current operation"
sign_out_command_description = "logout TEST command"


# Callback answers:
ask_username_answer = None
ask_shop_api_key_answer = None
display_user_menu_answer = "User menu"
display_add_shop_answer = "Add shop"
display_unlink_shop_answer = "Unlink shops"
confirm_unlink_shop_answer = "Unlink `{name}`"
unlink_shop_answer = "Shop `{name}` is unlinked."
display_shop_list_answer = "Shop list"
display_shop_menu_answer = "Shop `{name}` menu"
display_shop_info_answer = "Shop info"
activate_shop_answer = "Activation"
switch_activation_answer = "Switch activation"
price_updating_answer = "Price updating"
switch_price_updating_answer = "Switch price updating"
cancel_answer = "Cancel"
handle_invalid_button_answer = "Invalid button"
