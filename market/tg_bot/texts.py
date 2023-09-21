"""All static text, except of buttons."""

# It is shown in the chat with the bot if the chat is empty.
BOT_DESCRIPTION = "Бот для управления магазинами."

# It is shown on the bot’s profile page and is sent together with the link
# when users share the bot. (it is called `about` in BotFather)
BOT_SHORT_DESCRIPTION = "Бот для управления магазинами."

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

❗️ Служебные команды: 
/sign_out - позволяет повторно пройти процесс регистрации. \
Используется для смены роли или обновления данных пользователя, \
таких как `username`.
"""

START_CHOOSE_ROLE = "Выберите роль:"

DISPLAY_USER_MENU = "Главное меню ({full_name}: {role}):"

DISPLAY_ADD_SHOP = "Добавить магазин по API key. \nВведите API key 🔑:"

SHOP_IS_ADDED = "✅ Магазин `{name}` добавлен."

DISPLAY_UNLINK_SHOP = "Открепление магазина."

UNLINK_SHOP = "Открепить магазин `{name}`?"

DISPLAY_SHOP_LIST = "Доступные магазины:"

DISPLAY_SHOP_MENU = "Магазин: `{name}`"

DISPLAY_SHOP_INFO = """
<b>Детальная информация о магазине:</b>

Название: 
  <code>{name}</code>
Поставщик: 
  <code>{vendor_name}</code>
Активен: 
  <code>{is_active}</code>
Обновлять цены: 
  <code>{update_prices}</code>
Индивидуальное время обновления: 
  <code>{individual_updating_time}</code>
"""

ACTIVATE_SHOP = "Магазин: {name}\nАктивен: {is_active}"

PRICE_UPDATING = "Магазин: {name}\n" \
                 "Обновление цен: {switch}"

DISPLAY_BAN = "🚫 Вы забанены. Обратитесь в службу поддержки."

DISPLAY_NOT_ACTIVE = "🔒 Ваш аккаунт не активен. " \
                     "Оформите подписку для использования сервиса."

INVALID_BUTTON = "Извините, клавиатура больше не активна 😕 " \
                 "Пожалуйста нажмите /start чтобы возобновить диалог."

CANCEL = "👋 Диалог завершен. Для возобновления нажмите /start"


ASK_USERNAME = "Введите ваш Username:"

ASK_PASSWORD = "Введите пароль:"

PASSWORD_RECEIVED = "Пароль получен. Ожидайте."

LOGGED_IN_AS_ADMIN = "✅ Вы вошли в систему как Администратор."

WRONG_CREDENTIALS = "❌ Неверный username или password.\n" \
                    "Вы можете ввести пароль повторно.\n" \
                    "Хотите пройти процедуру авторизации заново?"

ASK_SHOP_API_KEY = "Введите API key 🔑 вашего магазина:"

API_KEY_RECEIVED = "API key получен. \nОжидайте."

LOGGED_IN_AS_SELLER = "✅ Вы вошли в систему как Продавец."

WRONG_API_KEY = "❌ Неверный API key 🔑, пожалуйста повторите ввод:"


# Commands:
START_COMMAND_DESCR = "Начало работы."
HELP_COMMAND_DESCR = "Справка о работе Бота."
MENU_COMMAND_DESCR = "Переход в основное меню."
CANCEL_COMMAND_DESCR = "Отменить текущую операцию, и завершить диалог."
SIGN_OUT_COMMAND_DESCR = "Пройти регистрацию повторно."


# Callback answers:
ASK_USERNAME_ANS = None
ASK_SHOP_API_KEY_ANS = None
DISPLAY_USER_MENU_ANS = "User menu"
DISPLAY_ADD_SHOP_ANS = "Add shop"
DISPLAY_UNLINK_SHOP_ANS = "Unlink shops"
CONFIRM_UNLINK_SHOP_ANS = "Unlink `{name}`"
UNLINK_SHOP_ANS = "Магазин `{name}` отвязан."
DISPLAY_SHOP_LIST_ANS = "Shop list"
DISPLAY_SHOP_MENU_ANS = "Shop `{name}` menu"
DISPLAY_SHOP_INFO_ANS = "Shop info"
ACTIVATE_SHOP_ANS = "Activation"
SWITCH_ACTIVATION_ANS = "Switch activation"
PRICE_UPDATING_ANS = "Price updating"
SWITCH_PRICE_UPDATING_ANS = "Switch price updating"
CANCEL_ANS = "Cancel"
HANDLE_INVALID_BUTTON_ANS = "Invalid button"

# emoji and decoration

# readable names
READABLE_ADMIN_ROLE = "Админ"
READABLE_SELLER_ROLE = "Продавец"
