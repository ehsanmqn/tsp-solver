import json
import logging
import aio_pika

from aio_pika.message import IncomingMessage
from aio_pika.queue import Queue
from aio_pika.channel import Channel

from tsp_solver.utils.abstract_consumer import RabbitMQConsumer
from tsp_solver.vrp_solver import ortools_vrp_solver
from tsp_solver.vrptw_solver import ortools_vrptw_solver
from tsp_solver.utils.helpers import generate_distance_matrix, generate_time_matrix
from tsp_solver.utils.models import VrpRequest, VrptwRequest, VrpResponse


class Dispatcher(RabbitMQConsumer):
    """
    Message dispatcher class for handling incoming messages
    """
    def __init__(self, channel: Channel, queue: Queue):
        super().__init__(channel=channel, queue=queue)

    async def process_message(self, message: IncomingMessage):
        # Load message data as json
        json_data = json.loads(message.body.decode('utf-8'))

        # Get required variables
        message_type = json_data.get('message_type')
        message_id = json_data.get('id')

        # Dispatch request based on message type
        try:
            if message_type in ['VRP', 'TSP']:
                request = VrpRequest(**json_data)
                response = self.process_vrp_message(request)
            elif message_type == 'VRPTW':
                request = VrptwRequest(**json_data)
                response = self.process_vrptw_message(request)
            else:
                response = VrpResponse(message_id, None, 400, "Not supported message type.")
        except ValueError as e:
            response = VrpResponse(message_id, None, 400, str(e))

        # Construct response message
        outbound_message = json.dumps(response.__dict__)

        # Publish response message
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=outbound_message.encode()),
            routing_key='TSP_OUTPUT_QUEUE',
        )

        # Publish response message
        # channel.basic_publish(
        #     exchange='',
        #     routing_key='TSP_OUTPUT_QUEUE',
        #     properties=pika.BasicProperties(
        #         reply_to=str(message_id),
        #         correlation_id=str(message_id)
        #     ),
        #     body=outbound_message
        # )

    def process_vrptw_message(self, request):
        """
        Process incoming message against the TSP optimization engine
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

    def process_vrp_message(self, request):
        """
        Process incoming message against the VRP/TSP optimization engine
        :param request: Request message
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
