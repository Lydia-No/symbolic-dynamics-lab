import math
from collections import Counter


def symbol_entropy(sequence):

    counts = Counter(sequence)

    total = len(sequence)

    H = 0

    for c in counts.values():

        p = c / total

        H -= p * math.log2(p)

    return H
