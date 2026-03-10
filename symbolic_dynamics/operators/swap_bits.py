from .base import Operator


class SwapBits(Operator):

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def apply(self, state):

        new = state.copy()

        new[self.a], new[self.b] = new[self.b], new[self.a]

        return new
