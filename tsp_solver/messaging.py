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
