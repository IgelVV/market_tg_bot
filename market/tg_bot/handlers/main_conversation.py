"""Handlers that are used in main ConversationHandler."""
import logging

from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from django.conf import settings

from shop.services import ShopService
from tg_bot.conversation_states import States
from tg_bot.keyboards import inline_keyboards
from tg_bot.services import ChatService, TelegramUserService
from tg_bot.dataclasses import Navigation, ShopInfo
from tg_bot import texts
from tg_bot.handlers import utils

logger = logging.getLogger(__name__)

LIST_LIMIT: int = settings.TG_BOT_LIST_LIMIT


async def display_user_menu(
        update: Update, context: ContextTypes.DEFAULT_TYPE):

    from_user, reply_func = await utils.callback_and_message_unifier(
        update, texts.DISPLAY_USER_MENU_ANS)
    chat_id = from_user.id
    full_name = from_user.full_name

    chat_service = ChatService(chat_id, context)
    role = await chat_service.get_role()
    text = texts.DISPLAY_USER_MENU.format(
        full_name=full_name,
        role=role,
    )
    if role == chat_service.ADMIN_ROLE:
        await reply_func(
            text=text,
            reply_markup=inline_keyboards.build_admin_menu(),
        )
        return States.ADMIN_MENU
    elif role == chat_service.SELLER_ROLE:
        await reply_func(
            text=text,
            reply_markup=inline_keyboards.build_seller_menu(),
        )
        return States.SELLER_MENU
    else:
        raise ValueError(f"Wrong {role=}")


async def display_add_shop(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    from_user, reply_func = await utils.callback_and_message_unifier(
        update, texts.DISPLAY_ADD_SHOP_ANS)
    await reply_func(
        text=texts.DISPLAY_ADD_SHOP,
        reply_markup=inline_keyboards.build_back(),
    )
    return States.ADD_SHOP


async def add_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    chat_service = ChatService(chat_id, context=context)
    if await chat_service.is_banned():
        return await display_ban(update, context)

    shop_api_key = update.message.text
    await update.message.delete()
    await update.message.reply_text(
        text=texts.API_KEY_RECEIVED.format(shop_api_key=shop_api_key),
    )
    shop_info = await chat_service.add_shop(shop_api_key)
    if shop_info is not None:
        text = texts.SHOP_IS_ADDED.format(name=shop_info.name)
        await update.message.reply_text(text=text)
        return await display_add_shop(update, context)
    else:
        await update.message.reply_text(
            texts.WRONG_API_KEY,
            reply_markup=inline_keyboards.build_back(),
        )
        return None


async def display_unlink_shop(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    # possible callbacks: back, Navigation
    query = update.callback_query
    chat_id = query.from_user.id
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
        raise ValueError("Wrong callback data")
    shop_info = query.data
    chat_service.set_shop_to_unlink(shop_info)
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
    chat_id = query.from_user.id
    chat_service = ChatService(chat_id, context)
    if await chat_service.is_banned():
        return await display_ban(update, context)

    shop_to_unlink = chat_service.get_shop_to_unlink()
    tg_user_service = TelegramUserService()
    await tg_user_service.unlink_shop_by_chat_id(
        chat_id=chat_id, shop_id=shop_to_unlink.id)
    await query.answer(
        text=texts.UNLINK_SHOP_ANS.format(name=shop_to_unlink.name),
        show_alert=True,
    )
    return await display_unlink_shop(update, context)


async def display_shop_list(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Display available shops.

    It uses pagination.
    It is allowed only for admins.
    """
    query = update.callback_query
    chat_id = query.from_user.id
    chat_service = ChatService(chat_id, context)

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


async def display_shop_menu(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Display actions related to specific shop.

    Allowed for both admin and seller.
    """
    query = update.callback_query
    chat_id = query.from_user.id

    chat_service = ChatService(chat_id, context)
    shop_service = ShopService()
    if isinstance(query.data, ShopInfo):
        shop_info = query.data
        chat_service.set_shop_id(shop_info.id)
    else:
        # todo optimize
        shop_id = chat_service.get_shop_id()
        shop_info = await shop_service.get_shop_info_by_id(shop_id)
    keyboard = inline_keyboards.build_shop_menu(with_back=True)
    await query.answer(
        text=texts.DISPLAY_SHOP_MENU_ANS.format(name=shop_info.name))
    text = texts.DISPLAY_SHOP_MENU.format(name=shop_info.name)
    await query.edit_message_text(
        text=text,
        reply_markup=keyboard,
    )
    return States.SHOP_MENU


async def display_shop_info(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display information from Shop model and `back` button."""
    query = update.callback_query
    chat_id = query.from_user.id
    await query.answer(text=texts.DISPLAY_SHOP_INFO_ANS)
    shop_service = ShopService()
    chat_service = ChatService(chat_id, context)
    if await chat_service.is_banned():
        return await display_ban(update, context)

    shop_id = chat_service.get_shop_id()
    shop_info = await shop_service.get_shop_info_by_id(shop_id=shop_id)
    text = texts.DISPLAY_SHOP_INFO.format(
        id=shop_info.id,
        name=shop_info.name,
        slug=shop_info.slug,
        api_key=shop_info.api_key,
        vendor_name=shop_info.vendor_name,
        is_active=shop_info.is_active,
        stop_updated_price=shop_info.stop_updated_price,
        individual_updating_time=shop_info.individual_updating_time,
    )

    await query.edit_message_text(
        text=text,
        reply_markup=inline_keyboards.build_back(),
        parse_mode="html"
    )
    return States.SHOP_INFO


async def activate_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display `is_active` status of shop, and button to change it."""
    query = update.callback_query
    chat_id = query.from_user.id
    await query.answer(text=texts.ACTIVATE_SHOP_ANS)
    shop_service = ShopService()
    chat_service = ChatService(chat_id, context)
    shop_id = chat_service.get_shop_id()
    shop_info = await shop_service.get_shop_info_by_id(shop_id)
    await query.edit_message_text(
        text=texts.ACTIVATE_SHOP.format(
            name=shop_info.name,
            is_active=shop_info.is_active
        ),
        reply_markup=inline_keyboards.build_activate_shop(shop_info.is_active)
    )
    return States.ACTIVATE


async def switch_activation(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Change `is_active` status to opposite.

    Then displays new status.
    """
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer(text=texts.SWITCH_ACTIVATION_ANS)
    chat_service = ChatService(chat_id, context)
    if await chat_service.is_banned():
        return await display_ban(update, context)

    shop_service = ShopService()
    shop_id = chat_service.get_shop_id()
    await shop_service.switch_activation(shop_id)
    return await activate_shop(update, context)


async def price_updating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display `stop_updated_price` status of shop, and button to change it."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer(text=texts.PRICE_UPDATING_ANS)
    shop_service = ShopService()
    chat_service = ChatService(chat_id, context)
    shop_id = chat_service.get_shop_id()
    shop_info = await shop_service.get_shop_info_by_id(shop_id)
    is_updating_on = not shop_info.stop_updated_price
    await query.edit_message_text(
        text=texts.PRICE_UPDATING.format(
            name=shop_info.name,
            switch='ON' if is_updating_on else 'OFF',
        ),
        reply_markup=inline_keyboards.build_price_updating(is_updating_on)
    )
    return States.PRICE_UPDATING


async def switch_price_updating(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Change `stop_updated_price` status to opposite.

    Then displays new status.
    """
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer(text=texts.SWITCH_PRICE_UPDATING_ANS)
    chat_service = ChatService(chat_id, context)

    if await chat_service.is_banned():
        return await display_ban(update, context)

    shop_service = ShopService()
    shop_id = chat_service.get_shop_id()
    await shop_service.switch_price_updating(shop_id)
    return await price_updating(update, context)


async def display_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display message for banned user."""
    bot = context.bot
    if update.message:
        chat_id = update.message.chat_id
    else:
        chat_id = update.callback_query.message.chat_id
    await bot.send_message(chat_id, texts.DISPLAY_BAN)
    return ConversationHandler.END


async def display_not_active(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display message for not active user."""
    bot = context.bot
    if update.message:
        chat_id = update.message.chat_id
    else:
        chat_id = update.callback_query.message.chat_id
    await bot.send_message(chat_id, texts.DISPLAY_NOT_ACTIVE)
    return ConversationHandler.END


async def handle_invalid_button(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Informs the user that the button is no longer available."""
    await update.callback_query.answer(texts.HANDLE_INVALID_BUTTON_ANS)
    await update.effective_message.edit_text(texts.INVALID_BUTTON)
