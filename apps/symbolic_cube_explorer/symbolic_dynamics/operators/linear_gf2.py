from .base import Operator


class LinearGF2(Operator):

    def __init__(self, matrix):
        self.matrix = matrix

    def apply(self, state):

        result = []

        for row in self.matrix:

            value = 0

            for a, b in zip(row, state):

                value ^= (a & b)

            result.append(value)

        return result
