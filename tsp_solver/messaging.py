import json
import logging
import math
import os
import pika

from tsp_solver.vrp_solver import ortools_vrp_solver
from tsp_solver.utils import euclidean_distance, generate_distances


class TspRequest:
    """
    The request message format
    """

    def __init__(self, id, locations, depot, num_vehicles):
        self.id = id
        self.locations = locations
        self.depot = depot
        self.num_vehicles = num_vehicles


class TspResponse:
    """
    The response message format
    """

    def __init__(self, id, solution, code, message):
        self.id = id
        self.solution = solution
        self.code = code
        self.message = message


def process_message(channel, method, properties, body):
    """
    Process incoming message regarding the TSP optimization engine, then publish result on output queue
    :param channel: Message channel
    :param body: Message body
    """

    json_data = json.loads(body.decode('utf-8'))
    request = TspRequest(**json_data)
    distance_matrix = generate_distances(request)

    try:
        routes = ortools_vrp_solver(distance_matrix=distance_matrix,
                                    depot=json_data['depot'],
                                    num_vehicles=json_data['num_vehicles'],
                                    max_distance=100000,
                                    cost_coefficient=100)
        response = TspResponse(request.id, routes, 200, "Operation successful.")
    except Exception as e:
        response = TspResponse(request.id, None, 404, str(e))

    outbound_message = json.dumps(response.__dict__)

    channel.basic_publish(
        exchange='',
        routing_key='TSP_OUTPUT_QUEUE',
        properties=pika.BasicProperties(
            reply_to=str(json_data.get('id')),
            correlation_id=str(json_data.get('id')),
        ),
        body=outbound_message
    )

    logging.info("Incoming request with id {} processed".format(request.id))


def start_service():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=os.environ.get('MESSAGE_BROKER'),
        port=5672,
        virtual_host='/',
        heartbeat=30,
        credentials=pika.PlainCredentials('admin', 'admin')))

    channel = connection.channel()
    channel.queue_declare(queue='TSP_INPUT_QUEUE')
    channel.queue_declare(queue='TSP_OUTPUT_QUEUE')
    channel.basic_consume(queue='TSP_INPUT_QUEUE', on_message_callback=process_message, auto_ack=True)

    logging.info("Waiting for inbound messages...")

    channel.start_consuming()
