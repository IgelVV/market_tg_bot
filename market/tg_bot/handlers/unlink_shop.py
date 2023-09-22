import logging

from telegram import Update
from telegram.ext import ContextTypes

from django.conf import settings

from tg_bot.conversation_states import States
from tg_bot.keyboards import inline_keyboards
from tg_bot.services import ChatService, TelegramUserService
from tg_bot.data_classes import Navigation, ShopInfo
from tg_bot import texts
from tg_bot.handlers import prohibitions

logger = logging.getLogger(__name__)

LIST_LIMIT: int = settings.TG_BOT_LIST_LIMIT


async def display_unlink_shop(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    # possible callbacks: back, Navigation
    user = update.callback_query.from_user
    query = update.callback_query
    chat_id = query.from_user.id
    logger.debug(
        f"User {user.username} {chat_id} goes to `unlink_shop` menu."
        f" {query.data=}.")
    chat_service = ChatService(chat_id, context)

    limit = LIST_LIMIT
    offset = 0
    if isinstance(query.data, Navigation):
        limit = query.data.limit
        offset = query.data.offset
    await query.answer(text=texts.DISPLAY_UNLINK_SHOP_ANS)
    shop_qs = await chat_service.get_shops()
    keyboard = await inline_keyboards.build_shop_list(
        qs=shop_qs,
        limit=limit,
        offset=offset,
    )
    await query.edit_message_text(
        text=texts.DISPLAY_UNLINK_SHOP,
        reply_markup=keyboard,
    )
    return States.UNLINK_SHOP


async def confirm_unlink_shop(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    # possible callbacks: back, Shop_info
    query = update.callback_query
    chat_id = query.from_user.id
    chat_service = ChatService(chat_id, context)
    if not isinstance(query.data, ShopInfo):
        logger.error(f"{chat_id=} Wrong callback data: {query.data}")
        raise ValueError(f"Wrong callback data: {query.data=}")
    shop_info = query.data
    chat_service.set_shop_info(shop_info)
    await query.answer(
        text=texts.CONFIRM_UNLINK_SHOP_ANS.format(name=shop_info.name))
    keyboard = inline_keyboards.build_yes_no(no_data=inline_keyboards.BACK)
    text = texts.UNLINK_SHOP.format(name=shop_info.name)
    await query.edit_message_text(
        text=text,
        reply_markup=keyboard,
    )
    return States.UNLINK_SHOP


async def unlink_shop(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.from_user.id
    chat_service = ChatService(chat_id, context)
    is_banned, is_activate, _ = await chat_service.get_statuses()
    if is_banned:
        return await prohibitions.display_ban(update, context)
    if not is_activate:
        return await prohibitions.display_not_active(update, context)

    shop_to_unlink = chat_service.get_shop_info()
    tg_user_service = TelegramUserService()
    await tg_user_service.unlink_shop_by_chat_id(
        chat_id=chat_id, shop_id=shop_to_unlink.id)
    await query.answer(
        text=texts.UNLINK_SHOP_ANS.format(name=shop_to_unlink.name),
        show_alert=True,
    )
    logger.info(f"User {user.username} {chat_id=} "
                f"has unlinked shop {shop_to_unlink.name}")
    return await display_unlink_shop(update, context)
