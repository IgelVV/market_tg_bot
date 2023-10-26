import asyncio
import logging

from aio_pika import DeliveryMode, Message
from django.core import serializers
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rabbit import broker

from .models import Shop

logger = logging.getLogger(__name__)

ENABLE_SIGNALS_TO_SYNCHRONISE_DB = settings.ENABLE_SIGNALS_TO_SYNCHRONISE_DB


def only_if_enabled(signal, enabled, **kwargs):
    """
    Decorator for signals, to use right before `@receiver`
    decorator to cancel connection.

    Use to disable some signals during specific working mode.
    E.g. disable signals depending on message broker while migrations
    or loading fixtures.
    ```
    @only_if_enabled(post_save, ENABLE_SIGNALS_TO_SYNCHRONISE_DB, sender=Shop)
    @receiver(post_save, sender=Shop)
    def create_or_update_shop(sender, instance, created, **kwargs):
        ...
    ```
    :param signal:
    :param enabled:
    :param kwargs:
    :return:
    """
    def _decorator(func):
        if enabled:
            return func
        else:
            if isinstance(signal, (list, tuple)):
                for s in signal:
                    s.disconnect(func, **kwargs)
            else:
                signal.disconnect(func, **kwargs)
            return func

    return _decorator


@only_if_enabled(post_save, ENABLE_SIGNALS_TO_SYNCHRONISE_DB, sender=Shop)
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


@only_if_enabled(post_delete, ENABLE_SIGNALS_TO_SYNCHRONISE_DB, sender=Shop)
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
