from django.contrib import admin
from shop import models


@admin.register(models.Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'ozon_api_key', 'client_id', 'vendor_name',
                    'is_active', 'price_updating',)
    list_display_links = ('pk', 'name')
    prepopulated_fields = {"slug": ["name"]}


@admin.register(models.Warehouse)
class StorageAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'warehouse_id',)
    list_display_links = ('pk', 'name')
