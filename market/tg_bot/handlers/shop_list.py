import logging

from telegram import Update
from telegram.ext import ContextTypes

from django.conf import settings

from tg_bot.conversation_states import States
from tg_bot.keyboards import inline_keyboards
from tg_bot.services import ChatService
from tg_bot.data_classes import Navigation
from tg_bot import texts

logger = logging.getLogger(__name__)

LIST_LIMIT: int = settings.TG_BOT_LIST_LIMIT


async def display_shop_list(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
    """
    Display available shops.

    It uses pagination.
    It is allowed only for admins.
    """
    query = update.callback_query
    user = query.from_user
    chat_id = query.from_user.id
    chat_service = ChatService(chat_id, context)
    logger.debug(f"User {user.username} {chat_id=} is opening "
                 f"`shop_list with {query.data=}")

    limit = LIST_LIMIT
    offset = 0
    if isinstance(query.data, Navigation):
        limit = query.data.limit
        offset = query.data.offset
    await query.answer(text=texts.DISPLAY_SHOP_LIST_ANS)
    shop_qs = await chat_service.get_shops()
    keyboard = await inline_keyboards.build_shop_list(
        qs=shop_qs,
        limit=limit,
        offset=offset,
    )
    await query.edit_message_text(
        text=texts.DISPLAY_SHOP_LIST,
        reply_markup=keyboard,
        parse_mode="html",
    )
    return States.SHOP_LIST
