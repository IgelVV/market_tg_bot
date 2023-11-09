from django.contrib import admin
from tg_bot import models


@admin.register(models.TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "chat_id",
        "username",
        "role",
        "created_at",
        "is_banned",
        "is_active",
        "is_logged_out",
    )
    list_display_links = ("pk", "chat_id", "username")
