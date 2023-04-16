import asyncio
from abc import ABCMeta, abstractmethod

from aio_pika.message import IncomingMessage
from aio_pika.queue import Queue


async def mark_message_processed(message: IncomingMessage):
    """
    Notify message broker about message being processed.
    """
    try:
        await message.ack()
    except Exception:
        await message.nack()
        raise


class RabbitMQConsumer(metaclass=ABCMeta):
    """
    RabbitMQ consumer abstract class responsible for consuming data from the queue.
    """

    def __init__(self, queue: Queue, iterator_timeout: int = 5, iterator_timeout_sleep: float = 5.0, *args, **kwargs, ):
        """
        :param queue: aio_pika queue object
        :param iterator_timeout: The queue iterator raises TimeoutError if no message comes for this time and iterating starts again (In seconds)
        :param iterator_timeout_sleep:  In seconds. Time for sleeping between attempts of iterating.
        :param args:
        :param kwargs:
        """

        self.queue = queue
        self.iterator_timeout = iterator_timeout
        self.iterator_timeout_sleep = iterator_timeout_sleep
        self.consuming_flag = True

    async def consume(self):
        """Consumes data from RabbitMQ queue forever until `stop_consuming()` is called."""
        async with self.queue.iterator(timeout=self.iterator_timeout) as queue_iterator:
            while self.consuming_flag:
                try:
                    async for message in queue_iterator:
                        if self.queue.name in message.body.decode():
                            continue

                        # Process incoming message
                        await self.process_message(message)

                        # Send ack to RabbitMQ
                        await mark_message_processed(message)

                        if not self.consuming_flag:
                            break
                except asyncio.exceptions.TimeoutError:
                    await self.on_finish()
                    if self.consuming_flag:
                        await asyncio.sleep(self.iterator_timeout_sleep)
                finally:
                    await self.on_finish()

    @abstractmethod
    async def process_message(self, message: IncomingMessage):
        """
        Abstract method to process incoming message
        :param message: Received message
        """
        raise NotImplementedError()

    def stop_consuming(self):
        """
        Stops the consuming gracefully.
        """
        self.consuming_flag = False

    async def on_finish(self):
        """
        Called after the message consuming finished.
        """
        pass
