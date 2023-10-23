import logging
import asyncio

from django.conf import settings

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust

logger = logging.getLogger(__name__)

RMQ_HOST = settings.RMQ_HOST
RMQ_PORT = settings.RMQ_PORT
RMQ_LOGIN = settings.RMQ_LOGIN
RMQ_PASSWORD = settings.RMQ_PASSWORD

SHOP_EXCHANGE = "shop"
SHOP_ROUTING_KEY = "shop"

CREATE_OPERATION = "create"
UPDATE_OPERATION = "update"
DELETE_OPERATION = "delete"


class Broker:
    connection = None

    @classmethod
    async def connect_to_broker(cls):
        """"""
        retries = 0
        while not cls.connection:
            logger.info(f"Trying to create connection to broker: {RMQ_HOST}")
            try:
                cls.connection = await connect_robust(host=RMQ_HOST,
                                                      port=RMQ_PORT,
                                                      login=RMQ_LOGIN,
                                                      password=RMQ_PASSWORD,)
                logger.info(f"Connected to broker ({type(cls.connection)} "
                            f"ID {id(cls.connection)})")
            except Exception as e:
                retries += 1
                logger.warning(
                    f"Can't connect to broker {retries} time"
                    f"({e.__class__.__name__}:{e}). Will retry in 5 seconds...")
                await asyncio.sleep(5)

        return cls.connection

    async def send(self,
                   exchange_name: str,
                   message: Message,
                   routing_key: str,
                   ):
        """Send message to queue."""
        if self.connection is None:
            await self.connect_to_broker()

        async with self.connection:
            channel = await self.connection.channel()

            exchange = await channel.declare_exchange(
                exchange_name, ExchangeType.DIRECT,
            )
            await exchange.publish(message, routing_key=routing_key)

    async def consume_queue(self,
                            callback,
                            exchange_name: str,
                            routing_key: str,
                            auto_delete_queue: bool = False,
                            ):
        """Listen queue"""
        if self.connection is None:
            await self.connect_to_broker()

        channel = await self.connection.channel()

        exchange = await channel.declare_exchange(
            exchange_name, ExchangeType.DIRECT,
        )
        queue = await channel.declare_queue(
            auto_delete=auto_delete_queue,
            durable=True
        )
        await queue.bind(exchange, routing_key=routing_key)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                logging.debug(f'Received message body: {message.body}')
                await callback(message)
