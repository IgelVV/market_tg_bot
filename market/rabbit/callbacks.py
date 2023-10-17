import asyncio
from aio_pika.abc import AbstractIncomingMessage


async def on_message(message: AbstractIncomingMessage) -> None:
    """
    on_message doesn't necessarily have to be defined as async.
    Here it is to show that it's possible.
    """
    print(" [x] Received message %r" % message)
    print("Message body is: %r" % message.body)

    print("Before sleep!")
    await asyncio.sleep(5)  # Represents async I/O operations
    print("After sleep!")
