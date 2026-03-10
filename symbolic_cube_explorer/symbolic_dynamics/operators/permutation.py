from .base import Operator


class BitPermutation(Operator):

    def __init__(self, mapping):
        self.mapping = mapping

    def apply(self, state):

        return [state[i] for i in self.mapping]
