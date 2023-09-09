from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from tg_bot.conversation_states import States
from tg_bot.keyboards import inline_keyboards


async def ask_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(text=query.data)
    await query.edit_message_text(
        text="Type your Username:"
    )
    return States.PASSWORD


async def ask_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels and ends the conversation."""
    # todo save username

    user = update.message.from_user
    await update.message.reply_text(
        "Type password:",
    )
    return States.CHECK_PASSWORD


async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels and ends the conversation."""
    text = update.message.text
    await update.message.delete()
    # todo clean username, and login
    await update.message.reply_text(
        f"password received: {text} \nPlease wait.",
    )
    # todo authentication
    authenticated = True
    if authenticated:
        context.user_data['authenticated'] = True
        context.user_data['role'] = "admin"
        await update.message.reply_text(
            f"You are logged in.",
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Wrong username or password. \nDo you want to try again?",
            reply_markup=inline_keyboards.get_yes_no()
        )
        return None
