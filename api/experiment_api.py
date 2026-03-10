from symbolic_dynamics.hypercube import Hypercube
from symbolic_dynamics.operators.bit_flip import BitFlip
from symbolic_dynamics.grammars.symbolic_grammar import SymbolicGrammar
from symbolic_dynamics.walkers.walker import Walker


class SymbolicExperiment:

    def __init__(self, dimension=8):

        self.space = Hypercube(dimension)
        self.grammar = SymbolicGrammar()
        self.walker = Walker(self.space, self.grammar)

    def add_symbol(self, word, bit):

        self.grammar.add(word, BitFlip(bit))

    def symbols(self):

        return list(self.grammar.rules.keys())

    def run(self, sequence):

        return self.walker.run(sequence)

    def run_text(self, text):

        sequence = text.split()

        return self.run(sequence)
