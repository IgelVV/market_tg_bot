import logging

from telegram import LabeledPrice, Update
from telegram.ext import ContextTypes, ConversationHandler

from django.conf import settings

from tg_bot import texts
from tg_bot.services import TelegramUserService
from tg_bot.handlers.command_handlers import start

logger = logging.getLogger(__name__)

TG_PAYMENT_PROVIDER_TOKEN = settings.TG_PAYMENT_PROVIDER_TOKEN


PAYLOAD = "Market telegram bot subscription"


async def display_payment(update: Update,
                          context: ContextTypes.DEFAULT_TYPE):
    """Sends an invoice without shipping-payment."""
    chat_id = update.effective_chat.id
    logger.info(f"{chat_id} starts payment.")
    await update.callback_query.message.delete()
    title = texts.PAYMENT_TITLE
    description = texts.PAYMENT_DESCRIPTION
    # select a payload just for you to recognize its the donation from your bot
    payload = PAYLOAD
    currency = "RUB"
    price = 100
    # price * 100 so as to include 2 decimal points
    prices = [LabeledPrice(texts.PAYMENT_LABEL_PRICE, price * 100)]

    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    await context.bot.send_invoice(
        chat_id,
        title,
        description,
        payload,
        TG_PAYMENT_PROVIDER_TOKEN,
        currency,
        prices
    )
    return ConversationHandler.END


async def precheckout_callback(update: Update,
                               context: ContextTypes.DEFAULT_TYPE) -> None:
    """Answers the PreQecheckoutQuery"""
    query = update.pre_checkout_query
    logger.info(f"{update.effective_user.username} precheckout_callback.")
    # check the payload, is this from your bot?
    if query.invoice_payload != PAYLOAD:
        await query.answer(
            ok=False, error_message=texts.PAYMENT_WRONG_PAYLOAD_ERROR)
    else:
        await query.answer(ok=True)


async def successful_payment_callback(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Confirms the successful payment."""
    logger.info(f"{update.effective_chat.id} precheckout_callback payment.")
    await TelegramUserService().activate(update.effective_user.id)
    await update.message.reply_text(texts.PAYMENT_SUCCESS)
    return await start(update, context)
