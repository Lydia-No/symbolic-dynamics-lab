from .base import Operator


class BitFlip(Operator):

    def __init__(self, index):
        self.index = index

    def apply(self, state):

        new_state = state.copy()

        new_state[self.index] ^= 1

        return new_state
