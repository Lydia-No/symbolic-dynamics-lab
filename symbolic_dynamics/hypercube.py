class Hypercube:
    def __init__(self, dimension: int):
        if dimension <= 0:
            raise ValueError("dimension must be positive")

        self.dimension = dimension

    def initial_state(self):
        return [0] * self.dimension

    def validate(self, state):

        if len(state) != self.dimension:
            raise ValueError("invalid state length")

        for bit in state:
            if bit not in (0, 1):
                raise ValueError("state must contain only 0 or 1")

    def neighbors(self, state):

        self.validate(state)

        out = []

        for i in range(self.dimension):

            new_state = state.copy()

            new_state[i] ^= 1

            out.append(new_state)

        return out
