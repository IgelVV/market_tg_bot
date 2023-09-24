""""""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from tg_bot.keyboards import inline_keyboards
from tg_bot.services import ChatService
from tg_bot import texts, utils
from tg_bot.handlers import auxiliary

logger = logging.getLogger(__name__)


async def display_user_menu(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    from_user = update.effective_user
    reply_func = await auxiliary.callback_and_message_unifier(
        update, texts.DISPLAY_USER_MENU_ANS)
    chat_id = from_user.id

    chat_service = ChatService(chat_id, context)
    chat_service.set_expected_input(None)
    role = await chat_service.get_role()
    logger.info(f"User {from_user.username} {chat_id} "
                f"displays menu as {role}.")
    readable_role = utils.readable_role(role)
    text = texts.DISPLAY_USER_MENU.format(
        full_name=from_user.full_name,
        role=readable_role,
    )
    if role == chat_service.ADMIN_ROLE:
        await reply_func(
            text=text,
            reply_markup=inline_keyboards.build_admin_menu(),
        )
    elif role == chat_service.SELLER_ROLE:
        await reply_func(
            text=text,
            reply_markup=inline_keyboards.build_seller_menu(),
        )
    else:
        logger.error(f"{chat_id=} Wrong {role=}")
        raise ValueError(f"Wrong {role=}")










