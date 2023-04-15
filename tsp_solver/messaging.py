import json
import logging
import os
import pika

from tsp_solver.vrp_solver import ortools_vrp_solver
from tsp_solver.vrptw_solver import ortools_vrptw_solver
from tsp_solver.utils import generate_distance_matrix, generate_time_matrix
from tsp_solver.models import VrpRequest, VrptwRequest, VrpResponse


def dispatch_message(channel, method, properties, body):
    """
    Process incoming message regarding the message type
    :param channel: Message channel
    :param body: Message body
    """

    # Load message data as json
    json_data = json.loads(body.decode('utf-8'))

    # Get required variables
    message_type = json_data.get('message_type')
    message_id = json_data.get('id')

    # Dispatch request based on message type
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

    # Construct response message
    outbound_message = json.dumps(response.__dict__)

    # Publish response message
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
    Process incoming message against the VRP/TSP optimization engine
    :param request: Request message
    :param channel: Messaging channel object
    """

    # Generate distance matrix
    distance_matrix = generate_distance_matrix(request)

    try:
        # Solve the problem using generated distance matrix
        routes = ortools_vrp_solver(distance_matrix=distance_matrix,
                                    depot=request.depot,
                                    num_vehicles=request.num_vehicles,
                                    max_distance=request.max_distance,
                                    cost_coefficient=request.cost_coefficient)

        # Construct response
        response = VrpResponse(request.id, routes, 200, "Operation successful.")
    except Exception as e:
        # Create appropriate response in error cases
        response = VrpResponse(request.id, None, 404, str(e))

    logging.info("Incoming {} request with id {} processed".format(request.message_type, request.id))

    return response


def process_vrptw_message(request, channel):
    """
    Process incoming message against the TSP optimization engine
    :param channel: Message channel
    :param request: Request data
    """

    # Generate the time matrix
    time_matrix = generate_time_matrix(request)

    try:
        # Solve the problem using time matrix
        routes = ortools_vrptw_solver(time_matrix=time_matrix,
                                      time_windows=request.time_windows,
                                      depot=request.depot,
                                      num_vehicles=request.num_vehicles,
                                      wait_time=request.wait_time,
                                      max_time_vehicle=request.max_time_vehicle)

        # Construct response
        response = VrpResponse(request.id, routes, 200, "Operation successful.")
    except Exception as e:
        # Create appropriate response in error cases
        response = VrpResponse(request.id, None, 404, str(e))

    logging.info("Incoming {} request with id {} processed".format(request.message_type, request.id))

    return response


def start_service():
    # Create connection to the RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=os.environ.get('MESSAGE_BROKER'),
        port=5672,
        virtual_host='/',
        heartbeat=30,
        credentials=pika.PlainCredentials('admin', 'admin')))

    # Declare queues
    channel = connection.channel()
    channel.queue_declare(queue='TSP_INPUT_QUEUE')
    channel.queue_declare(queue='TSP_OUTPUT_QUEUE')

    # Declare consuming queue
    channel.basic_consume(queue='TSP_INPUT_QUEUE', on_message_callback=dispatch_message, auto_ack=True)

    logging.info("Waiting for inbound messages...")

    # Start consuming
    channel.start_consuming()
