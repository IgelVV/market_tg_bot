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


# if user has chosen Admin role
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
    chat_id = update.message.chat_id
    username = update.message.text
    chat_service = ChatService(chat_id, context)
    chat_service.set_admin_username(username)
    logger.info(f"Username `{username}` is saved.")
    await update.message.reply_text(texts.ask_password)
    return States.CHECK_PASSWORD


async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # """
    # Authenticate admin.
    #
    # Deletes user message that contains password.
    # If authentication is failed, request if user want to enter username again.
    # It is possible to send password again, ignoring inline keyboard.
    #
    # Display `admin menu` if authenticated.
    # """
    chat_id = update.message.chat_id
    chat_service = ChatService(chat_id, context=context)
    password = update.message.text
    await update.message.delete()
    await update.message.reply_text(
        texts.password_received.format(password=password),
    )
    username = chat_service.get_admin_username()
    authenticated = await chat_service.authenticate_admin(
        username=username,
        password=password,
    )
    if authenticated:
        logger.info(f"User is authenticated")
        await chat_service.login_admin(
            first_name=update.message.from_user.first_name,
            last_name=update.message.from_user.last_name,
            tg_username=update.message.from_user.username,
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


# if user has chosen Seller role
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
        texts.api_key_received.format(shop_api_key=shop_api_key)
    )
    logged_in = await user_service.authenticate_and_login_seller(
        shop_api_key=shop_api_key,
        first_name=update.message.from_user.first_name,
        last_name=update.message.from_user.last_name,
        tg_username=update.message.from_user.username,
    )
    if logged_in:
        await update.message.reply_text(
            text=texts.logged_in_as_seller,
            reply_markup=inline_keyboards.build_seller_menu()
        )
        return States.SELLER_MENU
    else:
        await update.message.reply_text(
            texts.wrong_api_key,
            reply_markup=inline_keyboards.build_cancel(),
        )
        return None
