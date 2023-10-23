import asyncio
import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Shop
from django.core import serializers

from aio_pika import DeliveryMode, Message

from rabbit import broker

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Shop)
def create_or_update_shop(sender, instance, created, **kwargs):
    """
    Signal triggered when the Shop object is created or updated
    """
    logger.info("Shop post save signal")

    data = serializers.serialize("json", [instance])

    if not created:
        logger.info(f"Updated {instance=}, {instance.pk=}")
        message = Message(
            data.encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            headers={broker.OPERATION_KEY: broker.UPDATE_OPERATION},
        )
    else:
        logger.info(f"Created {instance=}, {instance.pk=}")
        message = Message(
            data.encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            headers={broker.OPERATION_KEY: broker.CREATE_OPERATION},
        )
    coro = broker.Broker().send(
        broker.BOT_SHOP_EXCHANGE, message, broker.BOT_SHOP_ROUTING_KEY)
    asyncio.run(coro)


@receiver(post_delete, sender=Shop)
def delete_shop(sender, instance, **kwargs):
    """
    Signal triggered when the Shop object is deleted
    """
    logger.info(f"Deleted {instance=}, {instance.pk=}")
    message = Message(
        str(instance.id).encode(),
        delivery_mode=DeliveryMode.PERSISTENT,
        headers={broker.OPERATION_KEY: broker.DELETE_OPERATION},
    )
    coro = broker.Broker().send(
        broker.BOT_SHOP_EXCHANGE, message, broker.BOT_SHOP_ROUTING_KEY)
    asyncio.run(coro)
