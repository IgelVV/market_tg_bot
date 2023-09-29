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
/menu - открыть меню пользователя.
/cancel - Отменить команду и вернуться в главное меню \
После использования этой команды необходимо заново запустить диалог.

При вводе текста с клавиатуры, например пароля или API key, текст, \
который начинается как команда с '/' будет распознан как команда. \
По этому не используйте данные, начинающиеся с этого символа.

❗️ Служебные команды: 
/sign_out - позволяет повторно пройти процесс регистрации. \
Используется для смены роли или обновления данных пользователя, \
таких как `username`.
"""

# registration
START_CHOOSE_ROLE = "Выберите роль:"

ASK_USERNAME = "Введите ваш Username:"

ASK_PASSWORD = "Введите пароль:"

PASSWORD_RECEIVED = "Пароль получен. Ожидайте."

LOGGED_IN_AS_ADMIN = "✅ Вы вошли в систему как Администратор."

WRONG_CREDENTIALS = "❌ Неверный username или password.\n" \
                    "Вы можете ввести пароль повторно:"

ASK_SHOP_API_KEY = "Введите API key 🔑 вашего магазина:"

API_KEY_RECEIVED = "API key получен. \nОжидайте."

LOGGED_IN_AS_SELLER = "✅ Вы вошли в систему как Продавец."

WRONG_API_KEY = "❌ Неверный API key 🔑, пожалуйста повторите ввод:"


# menu
DISPLAY_USER_MENU = "Главное меню ({full_name}: {role}):"

# payment
DISPLAY_SUBSCRIPTION_MENU = "Состояние подписки пользователя " \
                            "<code>{username}</code>: {is_active}"

DISPLAY_PAY_MENU = "В данный момент возможности бота предоставляются бесплатно."
#"Нажмите на кнопку ниже, чтобы оплатить подписку"

# add shop
DISPLAY_ADD_SHOP = "Добавить магазин по API key. \nВведите API key 🔑:"

SHOP_IS_ADDED = "✅ Магазин <code>{name}</code> добавлен."

# unlink shop
DISPLAY_UNLINK_SHOP = "Открепление магазина."

UNLINK_SHOP = "Открепить магазин <code>{name}</code>?"

# shop list
DISPLAY_SHOP_LIST = "Доступные магазины и их активность:"

# shop menu
DISPLAY_SHOP_MENU = "Магазин: <code>{name}</code>"

DISPLAY_SHOP_INFO = """
<b>Детальная информация о магазине:</b>

Название: 
  <code>{name}</code>
Поставщик: 
  <code>{vendor_name}</code>
Активен: {is_active}
Обновлять цены: {update_prices}
Индивидуальное время обновления: {individual_updating_time}
"""

ACTIVATE_SHOP = "Магазин: <code>{name}</code>\nАктивен: {is_active}"

PRICE_UPDATING = "Магазин: <code>{name}</code>\n" \
                 "Обновление цен: {switch}"

# service messages
DISPLAY_BAN = "🚫 Вы забанены. Обратитесь в службу поддержки."

DISPLAY_UNBAN = "🎉 Вы разбанены!"

DISPLAY_NOT_ACTIVE = "🔒 Ваш аккаунт не активен. " \
                     "Оформите подписку для использования сервиса."

INVALID_BUTTON = "Извините, клавиатура больше не активна 😕 " \
                 "Пожалуйста нажмите /start чтобы возобновить диалог."

CANCEL = "Команда отменена. Ввод данных с клавиатуры больше не ожидается."

USELESS_CANCEL = "Нет активной команды для отмены. Бот не ожидал ввода данных."

UNEXPECTED_TEXT = "Сейчас бот не ожидает ввода текста. " \
                  "Используйте кнопки чтобы управлять ботом. " \
                  "Для справки нажмите /help."

UNEXPECTED_COMMAND = "Такой команды не существует. Используйте /help," \
                     " чтобы получить список команд."


# Command descriptions:
START_COMMAND_DESCR = "Начало работы."
HELP_COMMAND_DESCR = "Справка о работе Бота."
MENU_COMMAND_DESCR = "Переход в основное меню."
CANCEL_COMMAND_DESCR = "Отменить команду и вернуться в главное меню."
SIGN_OUT_COMMAND_DESCR = "Пройти регистрацию повторно."


# Callback answers:
ASK_USERNAME_ANS = None
ASK_SHOP_API_KEY_ANS = None
DISPLAY_USER_MENU_ANS = "User menu"
DISPLAY_SUBSCRIPTION_MENU_ANS = "Subscription menu"
DISPLAY_PAY_MENU_ANS = "Pay menu"
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
HELP_ANS = "Help"
HANDLE_INVALID_BUTTON_ANS = "Invalid button"
DO_NOTHING_ANS = "Do nothing"


# readable elements
READABLE_ADMIN_ROLE = "Админ"
READABLE_SELLER_ROLE = "Продавец"
READABLE_TRUE = "✅"
READABLE_FALSE = "❌"
READABLE_ACTIVE = "🟢"
READABLE_INACTIVE = "🔴"  # "🛑"
