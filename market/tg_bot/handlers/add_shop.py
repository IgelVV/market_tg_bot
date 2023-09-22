import logging

from telegram import Update
from telegram.ext import ContextTypes

from tg_bot.conversation_states import States
from tg_bot.keyboards import inline_keyboards
from tg_bot.services import ChatService, ExpectedInput
from tg_bot import texts
from tg_bot.handlers import auxiliary, prohibitions

logger = logging.getLogger(__name__)


async def display_add_shop(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    from_user = update.effective_user
    reply_func = await auxiliary.callback_and_message_unifier(
        update, texts.DISPLAY_ADD_SHOP_ANS)
    chat_service = ChatService(chat_id=from_user.id, context=context)
    logger.debug(
        f"User {from_user.username} {from_user.id} goes to `add shop` menu.")
    chat_service.set_expected_input(ExpectedInput.API_KEY_TO_ADD)
    await reply_func(
        text=texts.DISPLAY_ADD_SHOP,
        reply_markup=inline_keyboards.build_back(
            back_data=inline_keyboards.USER_MENU),
    )
    return States.ADD_SHOP


async def add_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat_id
    chat_service = ChatService(chat_id, context=context)

    is_banned, is_activate, _ = await chat_service.get_statuses()
    if is_banned:
        return await prohibitions.display_ban(update, context)
    if not is_activate:
        return await prohibitions.display_not_active(update, context)

    shop_api_key = update.message.text
    await update.message.delete()
    await update.message.reply_text(
        text=texts.API_KEY_RECEIVED.format(shop_api_key=shop_api_key),
    )
    logger.debug(f"User {user.username} {chat_id} "
                 f"is trying to add shop by {shop_api_key=}.")
    shop_info = await chat_service.add_shop(shop_api_key)
    if shop_info is not None:
        chat_service.set_expected_input(None)
        text = texts.SHOP_IS_ADDED.format(name=shop_info.name)
        await update.message.reply_text(text=text)
        logger.info(f"User {user.username} {chat_id} "
                    f"has added shop {shop_api_key=}")
        return await display_add_shop(update, context)
    else:
        await update.message.reply_text(
            texts.WRONG_API_KEY,
            reply_markup=inline_keyboards.build_back(
                back_data=inline_keyboards.USER_MENU),
        )
        logger.info(f"User {user.username} {chat_id} "
                    f"has passed wrong {shop_api_key=}")
        return None
