import asyncio
import os
import sys
import logging
import aio_pika

from tsp_solver.dispatcher import Dispatcher

# Configure logging settings
logging.basicConfig(filename='../tsp_solver.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')


async def start_service(consumer_class) -> None:
    # Creat connection
    connection = await aio_pika.connect_robust(
        url="amqp://admin:admin@{}/".format(os.environ.get('MESSAGE_BROKER'))
    )

    input_queue_name = "TSP_INPUT_QUEUE"
    output_queue_name = "TSP_OUTPUT_QUEUE"

    try:
        async with connection:
            # Creating channel
            channel = await connection.channel()

            # Will take no more than 10 messages in advance
            await channel.set_qos(prefetch_count=10)

            # Declaring queue
            input_queue = await channel.declare_queue(input_queue_name, auto_delete=False)
            output_queue = await channel.declare_queue(output_queue_name)

            # Setup consumer
            consumer = consumer_class(channel=channel, queue=input_queue, )

            await consumer.consume()
    finally:
        await connection.close()


def main():
    logging.info('TSP solver service is going to be started.')

    try:
        asyncio.run(start_service(Dispatcher))
    except asyncio.CancelledError:
        logging.info('Main task cancelled')
    except Exception as e:
        logging.exception('Something unexpected happened: ', e)
    finally:
        logging.info("Shutdown complete")


if __name__ == '__main__':
    sys.exit(main())

# Shutdown the logger when done
logging.shutdown()
