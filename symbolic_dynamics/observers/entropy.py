import math
from collections import Counter


def symbol_entropy(sequence):

    counts = Counter(sequence)

    total = len(sequence)

    entropy = 0

    for c in counts.values():

        p = c / total

        entropy -= p * math.log2(p)

    return entropy
