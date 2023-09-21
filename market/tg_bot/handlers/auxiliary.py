from typing import Optional

from telegram import Update


async def callback_and_message_unifier(
        update: Update, callback_answer: Optional[str] = None):
    if update.message:
        from_user = update.message.from_user
        reply_func = update.message.reply_text
    elif query := update.callback_query:
        from_user = query.from_user
        reply_func = query.edit_message_text
        await query.answer(text=callback_answer)
    else:
        raise ValueError(
            "Unexpected update. It is expected Callback or Message.")

    return from_user, reply_func
