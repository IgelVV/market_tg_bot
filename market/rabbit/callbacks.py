import logging

from aio_pika.abc import AbstractIncomingMessage
from rabbit import broker

from django.core import serializers
from django.db.models import Model

from shop.models import Shop
from shop.services.shop_services import ShopService

logger = logging.getLogger(__name__)


async def on_message_shop(message: AbstractIncomingMessage) -> None:
    """
    Callback for consumer
    """
    logger.info(" [x] Received message %r" % message)
    logger.info("Message body is: %r" % message.body)

    operation = message.headers.get(broker.OPERATION_KEY, None)
    match operation:
        case broker.UPDATE_OPERATION:
            for deserialized_shop in serializers.deserialize(
                    'json', message.body):
                received_shop_obj: Shop = deserialized_shop.object
                local_shop_obj = await ShopService()\
                    .get_shop_by_id(received_shop_obj.pk)
                is_equal = compare_model_objs_by_fields(
                    received_shop_obj, local_shop_obj)
                if not is_equal:
                    await received_shop_obj.asave()
                break

        case broker.CREATE_OPERATION:
            for deserialized_shop in serializers.deserialize(
                    'json', message.body):
                received_shop_obj: Shop = deserialized_shop.object
                local_shop_obj = await ShopService() \
                    .get_shop_by_id(received_shop_obj.pk)
                if local_shop_obj is None:
                    await received_shop_obj.asave()
                break

        case broker.DELETE_OPERATION:
            id_to_delete = int(message.body.decode())
            local_shop_obj = await ShopService() \
                .get_shop_by_id(id_to_delete)
            if local_shop_obj is not None:
                await local_shop_obj.adelete()

        case _:
            assert False, f"{operation=} does not match any known operation."

    await message.ack()


def compare_model_objs_by_fields(instance: Model, other: Model):
    instance_fields_values = {
        getattr(instance, field.name) for field in instance._meta.fields}
    other_fields_values = {
        getattr(other, field.name) for field in other._meta.fields}
    return instance_fields_values == other_fields_values
