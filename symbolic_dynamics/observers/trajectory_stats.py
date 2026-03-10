def hamming_distance(a, b):
    return sum(x != y for x, y in zip(a, b))


def drift_from_origin(trajectory):

    origin = trajectory[0]

    distances = []

    for state in trajectory:

        distances.append(hamming_distance(origin, state))

    return distances
