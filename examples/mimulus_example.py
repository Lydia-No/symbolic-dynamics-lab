from symbolic_dynamics.hypercube import Hypercube
from symbolic_dynamics.operators.bit_flip import BitFlip
from symbolic_dynamics.grammars.symbolic_grammar import SymbolicGrammar
from symbolic_dynamics.walkers.walker import Walker

space = Hypercube(8)

grammar = SymbolicGrammar()

grammar.add("cave", BitFlip(0))
grammar.add("horse", BitFlip(1))
grammar.add("ladder", BitFlip(2))
grammar.add("flowers", BitFlip(3))
grammar.add("storm", BitFlip(4))


sequence = [
    "cave",
    "horse",
    "cave",
    "storm",
    "ladder"
]


walker = Walker(space, grammar)

trajectory = walker.run(sequence)

for state in trajectory:
    print(state)
