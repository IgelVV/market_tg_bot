from django.contrib import admin
from shop import models


@admin.register(models.Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'api_key', 'client_id', 'vendor_name',
                    'is_active', 'stop_updated_price',
                    'individual_updating_time',)
    list_display_links = ('pk', 'name')
    prepopulated_fields = {"slug": ["name"]}


@admin.register(models.Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'ozon_id',)
    list_display_links = ('pk', 'name')
