"""
Handlers that are used in nested ConversationHandler.

It responsible for authentication and registration.
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from tg_bot.keyboards import inline_keyboards
from tg_bot.services import ChatService, ExpectedInput
from tg_bot.handlers.auxiliary import callback_and_message_unifier
from tg_bot import texts

logger = logging.getLogger(__name__)


async def choose_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_func = await callback_and_message_unifier(update, None)
    keyboard = inline_keyboards.build_role_keyboard()
    await reply_func(texts.START_CHOOSE_ROLE, reply_markup=keyboard)


# if user has chosen Admin role
async def ask_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Request admin username.

    Command handlers can be unavailable, because it requests text answer,
    and next handler will handle commands too.
    """
    query = update.callback_query
    user = query.from_user
    chat_service = ChatService(chat_id=user.id, context=context)
    chat_service.set_expected_input(ExpectedInput.USERNAME)
    await query.answer(text=texts.ASK_USERNAME_ANS)
    await query.edit_message_text(
        text=texts.ASK_USERNAME,
        reply_markup=inline_keyboards.build_back(
            back_data=inline_keyboards.BACK_TO_CHOOSE_ROLE),
    )


async def ask_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Request admin password and save the username.

    Command handlers can be unavailable, because it requests text answer,
    and next handler will handle commands too.
    """
    chat_id = update.message.chat_id
    user = update.message.from_user
    username = update.message.text
    logger.debug(f"User {user.username} {chat_id} is entering "
                 f"{username=} for authorisation as admin.")
    chat_service = ChatService(chat_id, context)
    chat_service.set_admin_username(username)
    chat_service.set_expected_input(ExpectedInput.PASSWORD)
    await update.message.reply_text(texts.ASK_PASSWORD)


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
    user = update.message.from_user
    chat_service = ChatService(chat_id, context=context)
    password = update.message.text
    logger.debug(f"User {user.username} {chat_id} is entering "
                 f"password for authorisation as admin.")
    await update.message.delete()
    await update.message.reply_text(
        texts.PASSWORD_RECEIVED.format(password=password),
    )
    username = chat_service.get_admin_username()
    authenticated = await chat_service.authenticate_admin(
        username=username,
        password=password,
    )
    if authenticated:
        logger.info(f"User {user.username} {chat_id} "
                    f"is authenticated as admin")
        chat_service.set_expected_input(None)
        await chat_service.login_admin(
            first_name=user.first_name,
            last_name=user.last_name,
            tg_username=user.username,
        )
        message = texts.LOGGED_IN_AS_ADMIN
        await update.message.reply_text(
            message,
            reply_markup=inline_keyboards.build_admin_menu()
        )
    else:
        logger.info(f"User {user.username} {chat_id} "
                    f"is not authenticated with {username=}")
        await update.message.reply_text(
            text=texts.WRONG_CREDENTIALS,
            reply_markup=inline_keyboards.build_wrong_credentials()
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
    chat_id = update.effective_chat.id
    chat_service = ChatService(chat_id, context)
    chat_service.set_expected_input(ExpectedInput.API_KEY_TO_LOGIN)
    await query.answer(text=texts.ASK_SHOP_API_KEY_ANS)
    await query.edit_message_text(text=texts.ASK_SHOP_API_KEY)


async def check_shop_api_key(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Authenticate seller by api_key.

    Deletes user message that contains api_key.
    If authentication is failed, requests api_key again.

    Displays `shop menu` if authenticated.
    """
    chat_id = update.message.chat_id
    user = update.message.from_user
    chat_service = ChatService(chat_id, context=context)
    shop_api_key = update.message.text
    logger.debug(f"User {user.username} {chat_id} is entering "
                 f"{shop_api_key=} for authorisation as seller.")
    await update.message.delete()
    await update.message.reply_text(
        texts.API_KEY_RECEIVED.format(shop_api_key=shop_api_key)
    )
    logged_in = await chat_service.authenticate_and_login_seller(
        shop_api_key=shop_api_key,
        first_name=update.message.from_user.first_name,
        last_name=update.message.from_user.last_name,
        tg_username=update.message.from_user.username,
    )
    if logged_in:
        logger.info(f"User {user.username} {chat_id} "
                    f"is authenticated as seller")
        chat_service.set_expected_input(None)
        await update.message.reply_text(
            text=texts.LOGGED_IN_AS_SELLER,
            reply_markup=inline_keyboards.build_seller_menu()
        )
    else:
        logger.info(f"User {user.username} {chat_id} "
                    f"is not authenticated with {shop_api_key=}")
        await update.message.reply_text(
            texts.WRONG_API_KEY,
            reply_markup=inline_keyboards.build_cancel(),
        )
        return None


async def back_to_choose_role(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_service = ChatService(user.id, context)
    chat_service.set_expected_input(None)
    return await choose_role(update, context)
