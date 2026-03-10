import random

from symbolic_dynamics.hypercube import Hypercube
from symbolic_dynamics.operators.bit_flip import BitFlip
from symbolic_dynamics.grammars.symbolic_grammar import SymbolicGrammar
from symbolic_dynamics.walkers.walker import Walker


def detect_cycle(trajectory):

    seen = {}

    for i, state in enumerate(trajectory):

        key = tuple(state)

        if key in seen:
            return seen[key], i

        seen[key] = i

    return None


def random_sequence(symbols, length):

    return [random.choice(symbols) for _ in range(length)]


def main():

    dimension = 8
    trials = 100
    sequence_length = 20

    space = Hypercube(dimension)

    grammar = SymbolicGrammar()

    grammar.add("cave", BitFlip(0))
    grammar.add("horse", BitFlip(1))
    grammar.add("ladder", BitFlip(2))
    grammar.add("flowers", BitFlip(3))
    grammar.add("storm", BitFlip(4))

    symbols = list(grammar.rules.keys())

    walker = Walker(space, grammar)

    print("Searching for attractors...\n")

    for trial in range(trials):

        seq = random_sequence(symbols, sequence_length)

        trajectory = walker.run(seq)

        cycle = detect_cycle(trajectory)

        if cycle:

            start, end = cycle

            print("Cycle found!")
            print("sequence:", seq)
            print("cycle start:", start)
            print("cycle end:", end)
            print("cycle length:", end - start)

            print("states:")

            for state in trajectory[start:end]:
                print(state)

            print()
            print("----------")
            print()


if __name__ == "__main__":
    main()
