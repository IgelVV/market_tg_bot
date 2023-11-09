from django.db import models
from django.utils.translation import gettext_lazy as _


class Shop(models.Model):
    """ Магазин """
    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
        db_table = 'shops'

    name = models.CharField(max_length=50, verbose_name='Название магазина', blank=True)
    slug = models.SlugField(unique=True, auto_created=True, blank=True, null=True)
    client_id = models.CharField(max_length=8, verbose_name="Client-Id Ozon")
    ozon_api_key = models.CharField(max_length=50, verbose_name="Api-Key Ozon")
    shipper_api_key = models.CharField(max_length=200, verbose_name="Api-Key поставщика", blank=True)
    is_active = models.BooleanField(verbose_name="Магазин активен", default=False)
    price_updating = models.BooleanField(verbose_name="Обновление цен", default=True)
    vendor_name = models.CharField(max_length=50, verbose_name="Поставщик", default='Сималенд')


class Warehouse(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название склада', blank=True)
    warehouse_id = models.PositiveBigIntegerField(verbose_name="id Склада")
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='warehouses', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'
        db_table = 'warehouses'

    def __str__(self):
        return f'{self.shop.name} - {self.name}'
