import math

# Scale factor used for scale distances
scale_factor = 100


def euclidean_distance(p, q):
    """
    Giving points p, and q, this function calculate the Euclidean distance between p, and q
    :param p: Location 1
    :param q: Location 2
    :return: Distance between p, and q
    """
    return int(math.sqrt((p['latitude'] - q['latitude']) ** 2 + (p['longitude'] - q['longitude']) ** 2) * scale_factor)


def generate_distances(request):
    distances = [[euclidean_distance(request.locations[i], request.locations[j]) for j in range(len(request.locations))]
                 for i in range(len(request.locations))]

    return distances
