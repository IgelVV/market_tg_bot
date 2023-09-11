import logging

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from django.conf import settings

from tg_bot.conversation_states import States
from tg_bot.keyboards import inline_keyboards
from tg_bot.services.user_services import UserService, ShopService
from tg_bot.dataclasses import Navigation

logger = logging.getLogger(__name__)

LIST_LIMIT: int = settings.TG_BOT_LIST_LIMIT


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the conversation and asks the user about their role."""
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
    limit = LIST_LIMIT
    offset = 0
    if isinstance(query.data, Navigation):
        limit = query.data.limit
        offset = query.data.offset
    await query.answer(text=str(query.data))
    await query.edit_message_text(
        text="Available shops:",
        reply_markup=await inline_keyboards.build_shop_list(limit, offset),
        parse_mode="html",
    )
    return States.SHOP_LIST


async def display_shop_menu(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(text=str(query.data))
    await query.edit_message_text(
        text=f"Shop `{query.data}`",
        reply_markup=inline_keyboards.build_shop_menu(),
    )
    return States.SHOP_MENU


async def display_shop_info(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(text=str(query.data))
    shop_service = ShopService()
    user_service = UserService(context)
    shop_api_key = user_service.get_related_shop_api_key()
    shop_info = await shop_service.get_shop_info(shop_api_key=shop_api_key)
    text = "<b>Full shop information</b>\n" \
        "Id: {id}\n" \
        "Name: {name}\n" \
        "Slug: {slug}\n" \
        "API key: {api_key}\n" \
        "Vendor Name: {vendor_name}\n" \
        "Is Active: {is_active}\n" \
        "Stop updated price: {stop_updated_price}\n" \
        "Individual updating time: {individual_updating_time}\n" \
        .format(
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
    return States.SHOP_MENU


async def activate_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(text=str(query.data))
    shop_service = ShopService()
    user_service = UserService(context)
    shop_api_key = user_service.get_related_shop_api_key()
    shop_info = await shop_service.get_shop_info(shop_api_key)
    await query.edit_message_text(
        text=f"Shop name: {shop_info.name}\n"
             f"Is active: {shop_info.is_active}",
        reply_markup=inline_keyboards.build_activate_shop(shop_info.is_active)
    )
    return States.ACTIVATE


async def switch_activation(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(text=str(query.data))
    shop_service = ShopService()
    user_service = UserService(context)
    shop_api_key = user_service.get_related_shop_api_key()
    await shop_service.switch_activation(shop_api_key)
    return await activate_shop(update, context)


async def price_updating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(text=str(query.data))
    shop_service = ShopService()
    user_service = UserService(context)
    shop_api_key = user_service.get_related_shop_api_key()
    shop_info = await shop_service.get_shop_info(shop_api_key)
    is_updating_on = not shop_info.stop_updated_price
    await query.edit_message_text(
        text=f"Shop name: {shop_info.name}\n"
             f"Price updating: "
             f"{'ON' if  is_updating_on else 'OF'}",
        reply_markup=inline_keyboards.build_price_updating(is_updating_on)
    )
    return States.PRICE_UPDATING


async def switch_price_updating(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(text=str(query.data))
    shop_service = ShopService()
    user_service = UserService(context)
    shop_api_key = user_service.get_related_shop_api_key()
    await shop_service.switch_price_updating(shop_api_key)
    return await price_updating(update, context)


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
