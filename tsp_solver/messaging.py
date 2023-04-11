import json
import math
import pika


class TspRequest:
    """
    The request message format
    """

    def __init__(self, message_id, locations):
        self.message_id = message_id
        self.locations = locations


class TspResponse:
    """
    The response message format
    """

    def __init__(self, message_id, solution, distance):
        self.message_id = message_id
        self.solution = solution
        self.distance = distance


def euclidean_distance(p, q):
    """
    Giving points p, and q, this function calculate the Euclidean distance between p, and q
    :param p: Location 1
    :param q: Location 2
    :return: Distance between p, and q
    """
    return math.sqrt((p['latitude'] - q['latitude']) ** 2 + (p['longitude'] - q['longitude']) ** 2)


def process_message(channel, method, properties, body):
    """
    Process incoming message regarding the TSP optimization engine, then publish result on output queue
    :param channel: Message channel
    :param body: Message body
    :return: Nothing
    """
    request = TspRequest(**json.loads(body.decode('utf-8')))
    distances = [[euclidean_distance(request.locations[i], request.locations[j]) for j in range(len(request.locations))]
                 for i in range(len(request.locations))]

    response = TspResponse(request.message_id, "", "")
    outbound_message = json.dumps(response.__dict__)
    channel.basic_publish(exchange='', routing_key='TSP_OUTPUT_QUEUE', body=outbound_message)


def start_service():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='TSP_INPUT_QUEUE')
    channel.queue_declare(queue='TSP_OUTPUT_QUEUE')
    channel.basic_consume(queue='TSP_INPUT_QUEUE', on_message_callback=process_message, auto_ack=True)
    print('Waiting for inbound messages...')
    channel.start_consuming()
