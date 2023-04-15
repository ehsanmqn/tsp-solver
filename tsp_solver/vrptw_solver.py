import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def create_data_model(time_matrix, time_windows, depot, num_vehicles):
    """
    Prepare data structure for the VRPTW problem
    :param time_matrix: An array of travel times between locations.
    :param time_windows: An array of time windows for the locations.
    :param depot: The number of vehicles in the fleet.
    :param num_vehicles: The index of the depot.
    :return: Json packed data
    """
    data = {
        'time_matrix': time_matrix,
        'time_windows': time_windows,
        'num_vehicles': num_vehicles,
        'depot': depot
    }

    return data


def print_solution(data, manager, routing, solution):
    """
    Prints solution on console
    :param data: Problem json data created by the create_data_model function
    :param manager: Index manager instance
    :param routing: Routing model instance
    :param solution: The solution calculated by the optimizer
    """

    print(f'Objective: {solution.ObjectiveValue()}')
    time_dimension = routing.GetDimensionOrDie('Time')
    total_time = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            plan_output += '{0} Time({1},{2}) -> '.format(
                manager.IndexToNode(index), solution.Min(time_var),
                solution.Max(time_var))
            index = solution.Value(routing.NextVar(index))
        time_var = time_dimension.CumulVar(index)
        plan_output += '{0} Time({1},{2})\n'.format(manager.IndexToNode(index),
                                                    solution.Min(time_var),
                                                    solution.Max(time_var))
        plan_output += 'Time of the route: {}min\n'.format(
            solution.Min(time_var))
        print(plan_output)
        total_time += solution.Min(time_var)
    print('Total time of all routes: {}min'.format(total_time))


def get_routes(solution, manager, routing, dimension):
    """
    Get cumulative data from a dimension and store it in a json object.
    :param solution: The ortools routing solution instance
    :param manager: The manager instance
    :param routing: The routing instance
    :param dimension: The dimension
    :return: List containing potential optimal routes
    """

    total_time = 0
    routes = []

    # Iterate over routes
    for route_nbr in range(routing.vehicles()):
        index = routing.Start(route_nbr)
        route = [manager.IndexToNode(index)]

        time_var = dimension.CumulVar(index)
        time_data = [[solution.Min(time_var), solution.Max(time_var)]]

        # Iterate over route indices to provide locations where route have to pass
        while not routing.IsEnd(index):
            index = solution.Value(routing.NextVar(index))

            route.append(manager.IndexToNode(index))

            time_var = dimension.CumulVar(index)
            time_data.append([solution.Min(time_var), solution.Max(time_var)])

        # Get route time
        route_time = solution.Min(time_var)
        total_time += route_time

        routes.append({
            "route": route,
            "time_windows": time_data,
            "vehicle": route_nbr,
            "route_time": route_time
        })

    return {
        "routes": routes,
        "total_time": total_time
    }


def ortools_vrptw_solver(time_matrix, time_windows, depot, num_vehicles, wait_time, max_time_vehicle):
    """
    Solve the VRP with time windows.
    :param time_matrix: An array of travel times between locations.
    :param time_windows: An array of time windows for the locations.
    :param depot: The index of the depot.
    :param num_vehicles: The number of vehicles in the fleet.
    :param wait_time: An upper bound for slack (the wait times at the locations).
    :param max_time_vehicle: An upper bound for the total time over each vehicle's route.
    :return:
    """

    # Validate inputs
    assert len(time_matrix) == len(time_matrix[0]), "The time matrix does not have equal rows and columns."
    assert depot >= 0, "depot should be greater than or equal to zero."
    assert num_vehicles >= 0, "Number of vehicles should be greater than or equal to zero."
    assert wait_time >= 0, "Wait time should be greater than or equal to zero."
    assert max_time_vehicle >= 0, "Maximum time per vehicle should be greater than or equal to zero."

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(time_matrix), num_vehicles, depot)

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def time_callback(from_index, to_index):
        """
        Returns the travel time between the two nodes.
        """
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return time_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Time Windows constraint.
    dimension_name = 'Time'
    routing.AddDimension(
        transit_callback_index,
        wait_time,  # allow waiting time
        max_time_vehicle,  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        dimension_name)
    time_dimension = routing.GetDimensionOrDie(dimension_name)

    # Add time window constraints for each location except depot.
    for location_idx, time_window in enumerate(time_windows):
        if location_idx == depot:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    # Add time window constraints for each vehicle start node.
    depot_idx = depot
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(time_window[depot_idx][0], time_window[depot_idx][1])

    # Instantiate route start and end times to produce feasible times.
    for i in range(num_vehicles):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        # Get routes from the solution
        routes = get_routes(solution, manager, routing, time_dimension)
        return routes
    else:
        raise Exception("Could not find an optimal route.")
