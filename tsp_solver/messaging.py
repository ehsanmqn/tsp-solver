
class TspRequest:
    """
    The request message format
    """
    def __init__(self, message_id, locations):
        self.message_id = message_id
        self.locations = locations

