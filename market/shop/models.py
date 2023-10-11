from django.db import models
from django.utils.translation import gettext_lazy as _


class Shop(models.Model):
    class Meta:
        verbose_name = _("shop")
        verbose_name_plural = _("shops")

    name = models.CharField(max_length=1024)
    slug = models.SlugField()
    api_key = models.CharField(max_length=1024)
    client_id = models.CharField(max_length=1024)
    vendor_name = models.CharField(max_length=1024)
    is_active = models.BooleanField(default=True)
    update_prices = models.BooleanField(default=False)


class Storage(models.Model):
    class Meta:
        verbose_name = _("storage")
        verbose_name_plural = _("storages")

    name = models.CharField(max_length=1024)
    ozon_id = models.CharField(max_length=1024)
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
