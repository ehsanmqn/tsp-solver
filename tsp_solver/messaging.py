import json
import math
import numpy
import pika

from tsp_solver.solver import ortools_tsp_solver


class TspRequest:
    """
    The request message format
    """

    def __init__(self, id, locations):
        self.id = id
        self.locations = locations


class TspResponse:
    """
    The response message format
    """

    def __init__(self, id, solution, distance, code, message):
        self.id = id
        self.solution = solution
        self.distance = distance
        self.code = code
        self.message = message


def euclidean_distance(p, q):
    """
    Giving points p, and q, this function calculate the Euclidean distance between p, and q
    :param p: Location 1
    :param q: Location 2
    :return: Distance between p, and q
    """
    return math.sqrt((p['latitude'] - q['latitude']) ** 2 + (p['longitude'] - q['longitude']) ** 2)


def generate_distances(request):
    distances = [[euclidean_distance(request.locations[i], request.locations[j]) for j in range(len(request.locations))]
                 for i in range(len(request.locations))]

    distances = numpy.rint(numpy.array(distances) * 100).astype(int)

    return distances


def process_message(channel, method, properties, body):
    """
    Process incoming message regarding the TSP optimization engine, then publish result on output queue
    :param channel: Message channel
    :param body: Message body
    """
    request = TspRequest(**json.loads(body.decode('utf-8')))
    distances = generate_distances(request)

    try:
        distance, routes = ortools_tsp_solver(distances)
        response = TspResponse(request.id, routes[0], distance, 200, "Operation successful.")
    except Exception as e:
        response = TspResponse(request.id, None, None, 404, str(e))

    outbound_message = json.dumps(response.__dict__)
    channel.basic_publish(exchange='', routing_key='TSP_OUTPUT_QUEUE', body=outbound_message)
    print("Incoming request with id {} processed".format(request.id))


def start_service():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        # host=os.environ.get('MESSAGE_BROKER'),
        host='localhost',
        port=5672,
        virtual_host='/',
        credentials=pika.PlainCredentials('admin', 'admin')))

    channel = connection.channel()
    channel.queue_declare(queue='TSP_INPUT_QUEUE')
    channel.queue_declare(queue='TSP_OUTPUT_QUEUE')
    channel.basic_consume(queue='TSP_INPUT_QUEUE', on_message_callback=process_message, auto_ack=True)
    print('Waiting for inbound messages...')
    channel.start_consuming()
