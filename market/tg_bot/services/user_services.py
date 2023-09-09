from telegram.ext import (
    ContextTypes,
)

# roles
ADMIN = "admin"
SELLER = "seller"


def is_authenticated(context: ContextTypes.DEFAULT_TYPE) -> bool:
    return context.user_data.get("authenticated", False)


def get_role(context: ContextTypes.DEFAULT_TYPE):
    # find role in db
    return context.user_data.get('role')


def set_role(context: ContextTypes.DEFAULT_TYPE):
    ...