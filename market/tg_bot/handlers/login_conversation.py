"""
Handlers that are used in nested ConversationHandler.

It responsible for authentication and registration.
"""
from telegram import Update
from telegram.ext import ContextTypes

from tg_bot.conversation_states import States
from tg_bot.keyboards import inline_keyboards
from tg_bot.services.user_services import UserService


async def ask_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Request admin username.

    Command handlers can be unavailable, because it requests text answer,
    and next handler will handle commands too.
    """
    query = update.callback_query
    await query.answer(text=query.data)
    await query.edit_message_text(
        text="Type your Username:"
    )
    return States.PASSWORD


async def ask_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Request admin password and save the username.

    Command handlers can be unavailable, because it requests text answer,
    and next handler will handle commands too.
    """
    username = update.message.text
    context.user_data["username"] = username
    user = update.message.from_user
    await update.message.reply_text(
        "Type password:",
    )
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
    user_service = UserService(context=context)
    password = update.message.text
    await update.message.delete()
    await update.message.reply_text(
        f"password received: {password} \nPlease wait.",
    )
    authenticated = await user_service.authenticate_admin(
        username=context.user_data.get("username"),
        password=password,
        tg_user_id=update.message.from_user.id,
    )
    if authenticated:
        message = f"You are logged in as admin."
        await update.message.reply_text(
            message,
            reply_markup=inline_keyboards.build_admin_menu()
        )
        return States.ADMIN_MENU
    else:
        await update.message.reply_text(
            "Wrong username or password. "
            "\nDo you want to try again?",
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
    await query.edit_message_text(
        text="Type API key of your shop:"
    )
    return States.API_KEY


async def check_shop_api_key(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Authenticate seller by api_key.

    Deletes user message that contains api_key.
    If authentication is failed, requests api_key again.

    Displays `shop menu` if authenticated.
    """
    user_service = UserService(context=context)
    shop_api_key = update.message.text
    await update.message.delete()
    await update.message.reply_text(
        f"API key received: {shop_api_key} \nPlease wait.",
    )
    authenticated = await user_service.authenticate_seller(
        shop_api_key=shop_api_key,
        tg_user_id=update.message.from_user.id
    )
    if authenticated:
        message = f"You are logged in as Seller."
        await update.message.reply_text(
            message,
            reply_markup=inline_keyboards.build_shop_menu()
        )
        return States.SHOP_MENU
    else:
        await update.message.reply_text(
            "Wrong API key, please enter it again:",
            reply_markup=inline_keyboards.build_cancel(),
        )
        return None
