import random
from .base import Operator


class RandomFlip(Operator):

    def apply(self, state):

        new = state.copy()

        i = random.randrange(len(state))

        new[i] ^= 1

        return new
