"""Handlers that are used in main ConversationHandler."""
import logging

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from django.conf import settings

from shop.services import ShopService
from tg_bot.conversation_states import States
from tg_bot.keyboards import inline_keyboards
from tg_bot.services import ChatService
from tg_bot.dataclasses import Navigation, ShopInfo
from tg_bot import texts

logger = logging.getLogger(__name__)

LIST_LIMIT: int = settings.TG_BOT_LIST_LIMIT


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Starts the conversation and asks the user about their role.

    If user is authenticated it displays corresponding menu,
    otherwise directs to `login conversation`.
    """
    chat_id = update.message.chat_id
    chat_service = ChatService(chat_id, context)
    logger.info(f"{chat_id} starts. {chat_service.ADMIN_ROLE.label} {type(chat_service.ADMIN_ROLE.label)}")

    is_logged_out, is_banned, is_activate = await chat_service.check_to_login()

    exists = is_logged_out is not None
    is_logged_in = exists and (not is_logged_out)

    if exists and is_banned:
        return await display_ban(update, context)

    if exists and (not is_activate):
        return await display_not_active(update, context)

    if not is_logged_in:
        keyboard = inline_keyboards.build_role_keyboard()
        await update.message.reply_text(
            texts.start_choose_role,
            reply_markup=keyboard,
        )
        return States.LOGIN
    else:
        role = await chat_service.get_role()
        message = texts.after_login.format(
            full_name=update.message.from_user.full_name,
            role=role,
        )
        if role == chat_service.ADMIN_ROLE:
            await update.message.reply_text(
                message,
                reply_markup=inline_keyboards.build_admin_menu()
            )
            return States.ADMIN_MENU
        elif role == chat_service.SELLER_ROLE:
            await update.message.reply_text(
                message,
                reply_markup=inline_keyboards.build_shop_menu()
            )
            return States.SHOP_MENU
        else:
            raise ValueError(f"Wrong {role=}")


async def display_shop_list(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    # for Seller add buttons `add shop` `unlink shop`
    """
    Display available shops.

    It uses pagination.
    It is allowed only for admins.
    """
    query = update.callback_query
    chat_id = query.from_user.id
    user_service = ChatService(chat_id, context)
    # if user_service.get_role() == user_service.SELLER_ROLE:
    #     return await display_shop_menu(update, context)

    limit = LIST_LIMIT
    offset = 0
    if isinstance(query.data, Navigation):
        limit = query.data.limit
        offset = query.data.offset
    await query.answer(text=str(query.data))
    await query.edit_message_text(
        text=texts.display_shop_list,
        reply_markup=await inline_keyboards.build_shop_list(limit, offset),
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

    user_service = ChatService(chat_id, context)
    if user_service.get_role() == user_service.ADMIN_ROLE:
        if isinstance(query.data, ShopInfo):
            user_service.set_shop_id(query.data.id)
        keyboard = inline_keyboards.build_shop_menu(with_back=True)
    else:
        keyboard = inline_keyboards.build_shop_menu()
    await query.answer(text=str(query.data))
    await query.edit_message_text(
        # todo format()
        text=texts.display_shop_menu,
        reply_markup=keyboard,
    )
    return States.SHOP_MENU


async def display_shop_info(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display information from Shop model and `back` button."""
    query = update.callback_query
    chat_id = query.from_user.id
    await query.answer(text=str(query.data))
    shop_service = ShopService()
    user_service = ChatService(chat_id, context)
    shop_id = user_service.get_shop_id()
    logger.info(f"display shop {shop_id=}")
    shop_info = await shop_service.get_shop_info(shop_id=shop_id)
    text = texts.display_shop_info.format(
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
    await query.answer(text=str(query.data))
    shop_service = ShopService()
    user_service = ChatService(chat_id, context)
    shop_id = user_service.get_shop_id()
    shop_info = await shop_service.get_shop_info(shop_id)
    await query.edit_message_text(
        text=texts.activate_shop.format(
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
    await query.answer(text=str(query.data))
    shop_service = ShopService()
    user_service = ChatService(chat_id, context)
    shop_id = user_service.get_shop_id()
    await shop_service.switch_activation(shop_id)
    return await activate_shop(update, context)


async def price_updating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display `stop_updated_price` status of shop, and button to change it."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer(text=str(query.data))
    shop_service = ShopService()
    user_service = ChatService(chat_id, context)
    shop_id = user_service.get_shop_id()
    shop_info = await shop_service.get_shop_info(shop_id)
    is_updating_on = not shop_info.stop_updated_price
    await query.edit_message_text(
        text=texts.price_updating.format(
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
    await query.answer(text=str(query.data))
    shop_service = ShopService()
    user_service = ChatService(chat_id, context)
    shop_id = user_service.get_shop_id()
    await shop_service.switch_price_updating(shop_id)
    return await price_updating(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancels and ends the conversation.

    It handles both messages or callback queries.
    """
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


async def sign_out(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Logout user."""
    user = update.message.from_user

    chat_id = update.message.chat_id
    logger.info("User %s signed out.", user.full_name)
    await ChatService(chat_id, context).logout()
    return await start(update, context)


async def display_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display message for banned user."""
    bot = context.bot
    if update.message:
        chat_id = update.message.chat_id
    else:
        chat_id = update.callback_query.message.chat_id
    await bot.send_message(chat_id, texts.display_ban)
    return ConversationHandler.END


async def display_not_active(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display message for not active user."""
    bot = context.bot
    if update.message:
        chat_id = update.message.chat_id
    else:
        chat_id = update.callback_query.message.chat_id
    await bot.send_message(chat_id, texts.display_not_active)
    return ConversationHandler.END
