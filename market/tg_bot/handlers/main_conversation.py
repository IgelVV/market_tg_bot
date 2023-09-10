import logging

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from tg_bot.conversation_states import States
from tg_bot.keyboards import inline_keyboards
from tg_bot.services.user_services import UserService

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the conversation and asks the user about their role."""
    # todo refactor
    logger.info(f"{update.message.from_user.id} starts")
    user_service = UserService(context)

    if not user_service.is_authenticated():
        keyboard = inline_keyboards.build_role_keyboard()
        await update.message.reply_text(
            "Choose your role",
            reply_markup=keyboard,
        )
        return States.LOGIN
    else:
        role = user_service.get_role()
        message = f"Hello {update.message.from_user.full_name} your role is " \
            f"{role}"
        if role == user_service.ADMIN_ROLE:
            await update.message.reply_text(
                message,
                reply_markup=inline_keyboards.build_admin_menu()
            )
            return States.ADMIN_MENU
        elif role == user_service.SELLER_ROLE:
            await update.message.reply_text(
                message,
                reply_markup=inline_keyboards.build_shop_menu()
            )
            return States.SHOP_MENU
        else:
            raise ValueError(f"Wrong {role=}")


async def display_shop_list(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(text=query.data)
    await query.edit_message_text(
        text="Available shops:",
        reply_markup=inline_keyboards.build_shop_list(),
    )
    return States.SHOP_MENU


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    cancel_message = "Bye! I hope we can talk again some day."

    if update.message:
        user = update.message.from_user
        logger.info("User %s canceled the conversation.", user.first_name)
        await update.message.reply_text(
            cancel_message,
            reply_markup=ReplyKeyboardRemove(),
        )
    elif update.callback_query:
        query = update.callback_query
        await query.answer(text=query.data)
        await query.edit_message_text(
            text=cancel_message
        )
    else:
        ...
    return ConversationHandler.END
