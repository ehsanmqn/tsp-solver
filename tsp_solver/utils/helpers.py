import math

# Scale factor used for scale distances
distance_scale_factor = 100
vehicle_speed_constant = 80


def euclidean_distance(p, q):
    """
    Giving points p, and q, this function calculate the Euclidean distance between p, and q
    :param p: Location 1
    :param q: Location 2
    :return: Distance between p, and q
    """
    return int(math.sqrt(
        (p['latitude'] - q['latitude']) ** 2 + (p['longitude'] - q['longitude']) ** 2) * distance_scale_factor)


def euclidean_time(p, q):
    """
    This function calculates the amount of time required to travel between points p and q using the Euclidean distance formula, where velocity (V) is assumed to be constant at 80 and given by the equation V = X * t.
    :param p: Location 1
    :param q: Location 2
    :return: Time needed to travel between p, and q in a Euclidean path
    """
    try:
        return int(vehicle_speed_constant / (math.sqrt(
            (p['latitude'] - q['latitude']) ** 2 + (p['longitude'] - q['longitude']) ** 2) * distance_scale_factor))
    except ZeroDivisionError:
        return 0


def generate_distance_matrix(request):
    """
    This function generate the diagonal distance matrix
    :param request:
    :return: Distance matrix
    """
    distances = [[euclidean_distance(request.locations[i], request.locations[j]) for j in range(len(request.locations))]
                 for i in range(len(request.locations))]

    return distances


def generate_time_matrix(request):
    """
    This function generates diagonal time matrix
    :param request:
    :return: Time matrix
    """
    times = [[euclidean_time(request.locations[i], request.locations[j]) for j in range(len(request.locations))]
             for i in range(len(request.locations))]

    return times
