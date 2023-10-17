import logging
import asyncio

from django.conf import settings

import aio_pika
from aio_pika import Channel
from aio_pika.message import IncomingMessage, Message

logger = logging.getLogger(__name__)


RMQ_HOST = settings.RMQ_HOST
RMQ_PORT = settings.RMQ_PORT
RMQ_LOGIN = settings.RMQ_LOGIN
RMQ_PASSWORD = settings.RMQ_PASSWORD


class Broker:
    connection = None

    @classmethod
    async def connect_to_broker(cls):
        """"""
        retries = 0
        while not cls.connection:
            logger.info(f"Trying to create connection to broker: {RMQ_HOST}")
            try:
                cls.connection = await aio_pika.connect_robust(
                    host=RMQ_HOST,
                    port=RMQ_PORT,
                    login=RMQ_LOGIN,
                    password=RMQ_PASSWORD,
                )
                logger.info(f"Connected to broker ({type(cls.connection)} "
                            f"ID {id(cls.connection)})")
            except Exception as e:
                retries += 1
                logger.warning(
                    f"Can't connect to broker {retries} time"
                    f"({e.__class__.__name__}:{e}). Will retry in 5 seconds...")
                await asyncio.sleep(5)

        return cls.connection

    async def send(self):
        ...

    async def consume_queue(self, callback, queue_name: str,
                            auto_delete_queue: bool = False):
        """Listen queue"""
        if self.connection is None:
            await self.connect_to_broker()

        channel = await self.connection.channel()
        queue = await channel.declare_queue(
            queue_name,
            auto_delete=auto_delete_queue,
            durable=True
        )
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                logging.debug(f'Received message body: {message.body}')
                await callback(message)

        # async with self.connection as connection:
        #     channel = await connection.channel()
        #
        #     queue = await channel.declare_queue(
        #         queue_name,
        #         auto_delete=auto_delete_queue,
        #         durable=True
        #     )
        #     await queue.consume(callback, no_ack=True)
        #
        #     print(" [*] Waiting for messages. To exit press CTRL+C")
        #     await asyncio.Future()

