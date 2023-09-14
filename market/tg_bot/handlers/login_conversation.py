"""
Handlers that are used in nested ConversationHandler.

It responsible for authentication and registration.
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from tg_bot.conversation_states import States
from tg_bot.keyboards import inline_keyboards
from tg_bot.services import ChatService
from tg_bot import texts

logger = logging.getLogger(__name__)


async def ask_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Request admin username.

    Command handlers can be unavailable, because it requests text answer,
    and next handler will handle commands too.
    """
    query = update.callback_query
    await query.answer(text=query.data)
    await query.edit_message_text(text=texts.ask_username)
    return States.PASSWORD


async def ask_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Request admin password and save the username.

    Command handlers can be unavailable, because it requests text answer,
    and next handler will handle commands too.
    """
    username = update.message.text
    context.chat_data[ChatService.ADMIN_USERNAME_KEY] = username
    logger.info(f"Username {username} is saved.")
    await update.message.reply_text(texts.ask_password)
    return States.CHECK_PASSWORD


async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Authenticate admin.

    Deletes user message that contains password.
    If authentication is failed, request if user want to enter username again.
    It is possible to send password again, ignoring inline keyboard.

    Display `admin menu` if authenticated.
    """
    # todo check admin rights
    chat_id = update.message.chat_id
    chat_service = ChatService(chat_id, context=context)
    password = update.message.text
    await update.message.delete()
    await update.message.reply_text(
        texts.password_received.format(password=password),
    )
    username = context.chat_data.get(chat_service.ADMIN_USERNAME_KEY)
    authenticated = await chat_service.authenticate_admin(
        username=username,
        password=password,
    )
    if authenticated:
        logger.info(f"User is authenticated")
        await chat_service.login_admin(
            first_name=update.message.from_user.first_name,
            last_name=update.message.from_user.last_name,
            username=update.message.from_user.username,
        )
        message = texts.logged_in_as_admin
        await update.message.reply_text(
            message,
            reply_markup=inline_keyboards.build_admin_menu()
        )
        return States.ADMIN_MENU
    else:
        logger.info(f"User is not authenticated {username}: {password}")
        await update.message.reply_text(
            text=texts.wrong_credentials,
            reply_markup=inline_keyboards.build_yes_no()
        )
        return None


async def ask_shop_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Request shop api_key from the seller.

    Command handlers can be unavailable, because it requests text answer,
    and next handler will handle commands too.
    """
    query = update.callback_query
    await query.answer(text=query.data)
    await query.edit_message_text(text=texts.ask_shop_api_key)
    return States.API_KEY


async def check_shop_api_key(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Authenticate seller by api_key.

    Deletes user message that contains api_key.
    If authentication is failed, requests api_key again.

    Displays `shop menu` if authenticated.
    """
    chat_id = update.message.chat_id
    user_service = ChatService(chat_id, context=context)
    shop_api_key = update.message.text
    await update.message.delete()
    await update.message.reply_text(
        texts.ask_shop_api_key.format(shop_api_key=shop_api_key)
    )
    authenticated = await user_service.authenticate_seller(
        shop_api_key=shop_api_key,
        tg_user_id=update.message.from_user.id
    )
    if authenticated:
        message = texts.logged_in_as_seller
        await update.message.reply_text(
            message,
            reply_markup=inline_keyboards.build_shop_menu()
        )
        return States.SHOP_MENU
    else:
        await update.message.reply_text(
            texts.wrong_api_key,
            reply_markup=inline_keyboards.build_cancel(),
        )
        return None
