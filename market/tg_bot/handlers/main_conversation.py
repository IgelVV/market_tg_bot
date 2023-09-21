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

    chat_service = ChatService(chat_id, context)
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
        return States.ADMIN_MENU
    elif role == chat_service.SELLER_ROLE:
        await reply_func(
            text=text,
            reply_markup=inline_keyboards.build_seller_menu(),
        )
        return States.SELLER_MENU
    else:
        logger.error(f"{chat_id=} Wrong {role=}")
        raise ValueError(f"Wrong {role=}")


async def display_add_shop(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    from_user, reply_func = await utils.callback_and_message_unifier(
        update, texts.DISPLAY_ADD_SHOP_ANS)
    logger.debug(
        f"User {from_user.username} {from_user.id} goes to `add shop` menu.")
    await reply_func(
        text=texts.DISPLAY_ADD_SHOP,
        reply_markup=inline_keyboards.build_back(),
    )
    return States.ADD_SHOP


async def add_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat_id
    chat_service = ChatService(chat_id, context=context)

    is_banned, is_activate, _ = await chat_service.get_statuses()
    if is_banned:
        return await display_ban(update, context)
    if not is_activate:
        return await display_not_active(update, context)

    shop_api_key = update.message.text
    await update.message.delete()
    await update.message.reply_text(
        text=texts.API_KEY_RECEIVED.format(shop_api_key=shop_api_key),
    )
    logger.debug(f"User {user.username} {chat_id} "
                 f"is trying to add shop by {shop_api_key=}.")
    shop_info = await chat_service.add_shop(shop_api_key)
    if shop_info is not None:
        text = texts.SHOP_IS_ADDED.format(name=shop_info.name)
        await update.message.reply_text(text=text)
        logger.info(f"User {user.username} {chat_id} "
                    f"has added shop {shop_api_key=}")
        return await display_add_shop(update, context)
    else:
        await update.message.reply_text(
            texts.WRONG_API_KEY,
            reply_markup=inline_keyboards.build_back(),
        )
        logger.info(f"User {user.username} {chat_id} "
                    f"has passed wrong {shop_api_key=}")
        return None


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
        return await display_ban(update, context)
    if not is_activate:
        return await display_not_active(update, context)

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


async def display_shop_list(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
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


async def display_shop_menu(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Display actions related to specific shop.

    Allowed for both admin and seller.
    """
    query = update.callback_query
    user = query.from_user
    chat_id = query.from_user.id
    logger.debug(f"User {user.username} {chat_id=} is opening "
                 f"`shop_menu with {query.data=}")

    chat_service = ChatService(chat_id, context)
    if isinstance(query.data, ShopInfo):
        # callback from shop list, using `shop` button
        shop_info = query.data
        chat_service.set_shop_info(shop_info)
    else:
        # callback from shop submenu using `back` button
        shop_info = chat_service.get_shop_info()
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
    user = query.from_user
    chat_id = query.from_user.id
    await query.answer(text=texts.DISPLAY_SHOP_INFO_ANS)
    shop_service = ShopService()
    chat_service = ChatService(chat_id, context)
    is_banned, is_activate, _ = await chat_service.get_statuses()
    if is_banned:
        return await display_ban(update, context)
    if not is_activate:
        return await display_not_active(update, context)

    shop_info = chat_service.get_shop_info()
    # to refresh data
    new_shop_info = await shop_service.get_shop_info_by_id(
        shop_id=shop_info.id)
    text = texts.DISPLAY_SHOP_INFO.format(
        name=new_shop_info.name,
        vendor_name=new_shop_info.vendor_name,
        is_active=utils.readable_flag(new_shop_info.is_active),
        update_prices=utils.readable_flag(new_shop_info.update_prices),
        individual_updating_time=utils.readable_flag(
            new_shop_info.individual_updating_time),
    )
    logger.info(f"User {user.username} {chat_id=} is opening "
                f"`shop_info of shop {new_shop_info}")

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
    shop_info = chat_service.get_shop_info()
    # to refresh data about shop
    new_shop_info = await shop_service.get_shop_info_by_id(shop_info.id)
    await query.edit_message_text(
        text=texts.ACTIVATE_SHOP.format(
            name=new_shop_info.name,
            is_active=utils.readable_shop_activiti(new_shop_info.is_active)
        ),
        reply_markup=inline_keyboards.build_activate_shop(
            new_shop_info.is_active)
    )
    return States.ACTIVATE


async def switch_activation(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Change `is_active` status to opposite.

    Then displays new status.
    """
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat_id
    await query.answer(text=texts.SWITCH_ACTIVATION_ANS)
    chat_service = ChatService(chat_id, context)
    is_banned, is_activate, _ = await chat_service.get_statuses()
    if is_banned:
        return await display_ban(update, context)
    if not is_activate:
        return await display_not_active(update, context)
    shop_service = ShopService()
    shop_info = chat_service.get_shop_info()
    logger.info(f"User {user.username} {chat_id=} "
                f"is switching activations of {shop_info}")
    await shop_service.switch_activation(shop_info.id)
    return await activate_shop(update, context)


async def price_updating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display `stop_updated_price` status of shop, and button to change it."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer(text=texts.PRICE_UPDATING_ANS)
    shop_service = ShopService()
    chat_service = ChatService(chat_id, context)
    shop_info = chat_service.get_shop_info()
    shop_info = await shop_service.get_shop_info_by_id(shop_info.id)
    is_updating_on = not shop_info.update_prices
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
    user = query.from_user
    chat_id = query.message.chat_id
    await query.answer(text=texts.SWITCH_PRICE_UPDATING_ANS)
    chat_service = ChatService(chat_id, context)
    is_banned, is_activate, _ = await chat_service.get_statuses()
    if is_banned:
        return await display_ban(update, context)
    if not is_activate:
        return await display_not_active(update, context)

    shop_service = ShopService()
    shop_info = chat_service.get_shop_info()
    logger.info(f"User {user.username} {chat_id=} "
                f"is switching price_updating of {shop_info}")
    await shop_service.switch_price_updating(shop_info.id)
    return await price_updating(update, context)


async def display_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display message for banned user."""
    bot = context.bot
    if update.message:
        user = update.message.from_user
    else:
        user = update.callback_query.from_user
    chat_id = user.id
    logger.info(f"User {user.username} {chat_id} has got a ban.")
    await bot.send_message(chat_id, texts.DISPLAY_BAN)
    return ConversationHandler.END


async def display_not_active(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display message for not active user."""
    bot = context.bot
    if update.message:
        user = update.message.from_user
    else:
        user = update.callback_query.from_user
    chat_id = user.id
    logger.info(f"User {user.username} {chat_id} "
                f"has got a `not active` message.")
    await bot.send_message(chat_id, texts.DISPLAY_NOT_ACTIVE)
    return ConversationHandler.END


async def handle_invalid_button(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Informs the user that the button is no longer available."""
    user = update.callback_query.from_user
    await update.callback_query.answer(texts.HANDLE_INVALID_BUTTON_ANS)
    await update.effective_message.edit_text(texts.INVALID_BUTTON)
    logger.debug(f"User {user.username} {user.id} "
                 f"has clicked on invalid button.")
