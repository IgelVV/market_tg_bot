import logging

from telegram import Update
from telegram.ext import ContextTypes

from shop.services import ShopService
from tg_bot.conversation_states import States
from tg_bot.keyboards import inline_keyboards
from tg_bot.services import ChatService
from tg_bot.data_classes import ShopInfo
from tg_bot import texts, utils
from tg_bot.handlers import prohibitions

logger = logging.getLogger(__name__)


async def display_shop_menu(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
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


async def display_shop_info(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
    """Display information from Shop model and `back` button."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.from_user.id
    await query.answer(text=texts.DISPLAY_SHOP_INFO_ANS)
    shop_service = ShopService()
    chat_service = ChatService(chat_id, context)
    is_banned, is_activate, _ = await chat_service.get_statuses()
    if is_banned:
        return await prohibitions.display_ban(update, context)
    if not is_activate:
        return await prohibitions.display_not_active(update, context)

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


async def switch_activation(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
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
        return await prohibitions.display_ban(update, context)
    if not is_activate:
        return await prohibitions.display_not_active(update, context)
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


async def switch_price_updating(update: Update,
                                context: ContextTypes.DEFAULT_TYPE):
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
        return await prohibitions.display_ban(update, context)
    if not is_activate:
        return await prohibitions.display_not_active(update, context)

    shop_service = ShopService()
    shop_info = chat_service.get_shop_info()
    logger.info(f"User {user.username} {chat_id=} "
                f"is switching price_updating of {shop_info}")
    await shop_service.switch_price_updating(shop_info.id)
    return await price_updating(update, context)
