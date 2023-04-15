import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def create_data_model(distance_matrix, depot, num_vehicles):
    """
    Store the data for the problem
    :param num_vehicles: The number of vehicles in the fleet.
    :param depot: The start and end location for the route.
    :param distance_matrix: The distance matrix is an array whose i, j entry is the distance from location i to location j in miles.
    :return: Json data
    """
    data = {
        'distance_matrix': distance_matrix,
        'num_vehicles': num_vehicles,
        'depot': depot
    }
    return data


def print_solution(data, manager, routing, solution):
    """
    The function displays the optimal route and its distance, which is given by ObjectiveValue().
    :param data: Problem json data created by the create_data_model function
    :param manager: Index manager
    :param routing: Routing model
    :param solution: The solution calculated by the ortools optimizer
    """

    print(f'Objective: {solution.ObjectiveValue()}')
    max_route_distance = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
    print('Maximum of the route distances: {}m'.format(max_route_distance))


def get_routes(solution, routing, manager):
    """
    Get vehicle routes from a solution and store them in an array. i,j entry is the jth location visited by vehicle i along its route.
    :param solution: The ortools routing solution object
    :param routing: The routing object
    :param manager: The manager object
    :return: List containing available routes
    """

    routes = []
    max_route_distance = 0

    # Iterate over routes
    for route_nbr in range(routing.vehicles()):
        index = routing.Start(route_nbr)
        route = [manager.IndexToNode(index)]
        route_distance = 0

        # Obtain route locations and distance
        while not routing.IsEnd(index):
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route.append(manager.IndexToNode(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, route_nbr)

        # Compute the max distance
        max_route_distance = max(route_distance, max_route_distance)

        routes.append({
            "route": route,
            "vehicle": route_nbr,
            "distance": route_distance
        })

    return {
        "routes": routes,
        "max_route_distance": max_route_distance
    }


def ortools_vrp_solver(distance_matrix: list[list[int]],
                       depot: int,
                       num_vehicles: int,
                       max_distance: int,
                       cost_coefficient: int):
    """
    Entry point for finding the optimal path between points using the ortools library
    :param cost_coefficient: Difference between the largest value of route end cumul variables and the smallest value of route start cumul variables.
    :param max_distance: Vehicle maximum travel distance
    :param num_vehicles: The number of vehicles in the fleet. If set 1, it would be TSP.
    :param depot: The start and end location for the route.
    :param distance_matrix: The distance matrix is an array whose i, j entry is the distance from location i to location j.
    :return: Json object containing optimal routes
    """

    # Validate inputs
    assert len(distance_matrix) == len(distance_matrix[0]), "The distance matrix does not have equal rows and columns."
    assert depot >= 0, "depot should be greater than or equal to zero."
    assert num_vehicles >= 0, "Number of vehicles should be greater than or equal to zero."
    assert max_distance >= 0, "Max distance should be greater than or equal to zero."
    assert cost_coefficient >= 0, "Cost coefficient should be greater than or equal to zero."

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, depot)

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and assign the transit callback
    def distance_callback(from_index, to_index):
        """
        Returns the distance between the two nodes.
        """
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Define the distance dimension to support VRP cases
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,              # no slack
        max_distance,   # vehicle maximum travel distance
        True,           # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(cost_coefficient)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()

    # Set first solution strategy as optimizer
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Set local search as optimizer (Link: https://developers.google.com/optimization/routing/routing_options#local_search_options)
    # search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    # search_parameters.time_limit.seconds = 30
    # search_parameters.log_search = True

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        # Get routes from the solution
        routes = get_routes(solution, routing, manager)
        return routes

    raise Exception("Could not find an optimal route.")
