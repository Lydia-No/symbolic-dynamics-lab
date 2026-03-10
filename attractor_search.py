import random

from symbolic_dynamics.hypercube import Hypercube
from symbolic_dynamics.walkers.walker import Walker
from grammar_generators import random_grammar


def detect_cycle(traj):

    seen = {}

    for i, s in enumerate(traj):

        t = tuple(s)

        if t in seen:
            return seen[t], i

        seen[t] = i

    return None


def main():

    dimension = 8

    space = Hypercube(dimension)

    for trial in range(200):

        grammar = random_grammar(5, dimension)

        walker = Walker(space, grammar)

        seq = [random.choice(list(grammar.rules.keys())) for _ in range(30)]

        traj = walker.run(seq)

        cycle = detect_cycle(traj)

        if cycle:

            print("Attractor found")
            print(seq)
            print(cycle)
            print()


if __name__ == "__main__":
    main()
