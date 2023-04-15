from pydantic import BaseModel
from typing import List


class VrpRequest(BaseModel):
    """
    The VRP/TSP request message format
    """
    id: str
    locations: List
    depot: int
    num_vehicles: int
    message_type: str
    max_distance: int
    cost_coefficient: int


class VrptwRequest(BaseModel):
    """
    The VRPTW request message format
    """
    id: str
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