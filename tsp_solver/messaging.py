import json
import logging
import os
import pika
from pydantic import BaseModel
from typing import List

from tsp_solver.vrp_solver import ortools_vrp_solver
from tsp_solver.vrptw_solver import ortools_vrptw_solver
from tsp_solver.utils import generate_distance_matrix, generate_time_matrix


class VrpRequest(BaseModel):
    """
    The VRP/TSP request message format
    """
    id: int
    locations: List
    depot: int
    num_vehicles: int
    message_type: str


class VrptwRequest(BaseModel):
    """
    The VRPTW request message format
    """
    id: int
    locations: List
    depot: int
    num_vehicles: int
    message_type: str
    time_windows: List
    wait_time: int
    max_time_vehicle: int


class VrpResponse:
    """
    The response message format
    """
    def __init__(self, id, solution, code, message):
        self.id = id
        self.solution = solution
        self.code = code
        self.message = message


def dispatch_message(channel, method, properties, body):
    """
    Process incoming message regarding the message type
    :param channel: Message channel
    :param body: Message body
    """
    json_data = json.loads(body.decode('utf-8'))

    message_type = json_data.get('message_type')
    message_id = json_data.get('id')

    try:
        if message_type in ['VRP', 'TSP']:
            request = VrpRequest(**json_data)
            response = process_vrp_message(request, channel)
        elif message_type == 'VRPTW':
            request = VrptwRequest(**json_data)
            response = process_vrptw_message(request, channel)
        else:
            response = VrpResponse(message_id, None, 400, "Not supported message type.")
    except ValueError as e:
        response = VrpResponse(message_id, None, 400, str(e))

    outbound_message = json.dumps(response.__dict__)
    channel.basic_publish(
        exchange='',
        routing_key='TSP_OUTPUT_QUEUE',
        properties=pika.BasicProperties(
            reply_to=str(message_id),
            correlation_id=str(message_id)
        ),
        body=outbound_message
    )


def process_vrp_message(request, channel):
    """
    Process incoming message regarding the VRP/TSP optimization engine, then publish result on output queue
    :param request: Request message
    :param channel: Messaging channel object
    """

    distance_matrix = generate_distance_matrix(request)

    try:
        routes = ortools_vrp_solver(distance_matrix=distance_matrix,
                                    depot=request.depot,
                                    num_vehicles=request.num_vehicles,
                                    max_distance=100000,
                                    cost_coefficient=100)
        response = VrpResponse(request.id, routes, 200, "Operation successful.")
    except Exception as e:
        response = VrpResponse(request.id, None, 404, str(e))

    logging.info("Incoming {} request with id {} processed".format(request.message_type, request.id))
    return response


def process_vrptw_message(request, channel):
    """
    Process incoming message regarding the TSP optimization engine, then publish result on output queue
    :param channel: Message channel
    :param request: Request data
    """

    time_matrix = generate_time_matrix(request)

    try:
        routes = ortools_vrptw_solver(time_matrix=time_matrix,
                                      time_windows=request.time_windows,
                                      depot=request.depot,
                                      num_vehicles=request.num_vehicles,
                                      wait_time=request.wait_time,
                                      max_time_vehicle=request.max_time_vehicle)

        response = VrpResponse(request.id, routes, 200, "Operation successful.")
    except Exception as e:
        response = VrpResponse(request.id, None, 404, str(e))

    logging.info("Incoming {} request with id {} processed".format(request.message_type, request.id))
    return response


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

    channel.basic_consume(queue='TSP_INPUT_QUEUE', on_message_callback=dispatch_message, auto_ack=True)

    logging.info("Waiting for inbound messages...")

    channel.start_consuming()
