def detect_cycle(trajectory):

    seen = {}

    for i, state in enumerate(trajectory):

        key = tuple(state)

        if key in seen:

            return seen[key], i

        seen[key] = i

    return None
