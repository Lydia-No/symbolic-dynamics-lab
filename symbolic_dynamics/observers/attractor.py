def detect_cycle(trajectory):
    """
    Detect a repeated state (cycle) in a trajectory.
    """

    seen = {}

    for i, state in enumerate(trajectory):

        key = tuple(state)

        if key in seen:
            return {
                "first_seen": seen[key],
                "repeated_at": i,
                "cycle_length": i - seen[key],
                "state": list(key),
            }

        seen[key] = i

    return None
