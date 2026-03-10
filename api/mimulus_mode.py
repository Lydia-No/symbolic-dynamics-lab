from symbolic_dynamics.hypercube import Hypercube
from symbolic_dynamics.operators.bit_flip import BitFlip
from symbolic_dynamics.grammars.symbolic_grammar import SymbolicGrammar
from symbolic_dynamics.walkers.walker import Walker


class MimulusExperiment:

    def __init__(self, dimension=16):

        self.dimension = dimension

        self.space = Hypercube(dimension)

        self.grammar = SymbolicGrammar()

        self.walker = Walker(self.space, self.grammar)

        self.symbol_meanings = {}

        self.symbol_to_bit = {}

        self.next_bit = 0


    def add_symbol(self, word, meaning):

        if word in self.symbol_to_bit:
            return self.symbol_to_bit[word]

        if self.next_bit >= self.dimension:
            raise ValueError("cube dimension exceeded")

        bit = self.next_bit

        self.symbol_to_bit[word] = bit

        self.symbol_meanings[word] = meaning

        self.grammar.add(word, BitFlip(bit))

        self.next_bit += 1

        return bit


    def meanings(self):

        return self.symbol_meanings


    def mapping_table(self):

        rows = []

        for word, meaning in self.symbol_meanings.items():

            rows.append({
                "symbol": word,
                "meaning": meaning,
                "bit": self.symbol_to_bit[word]
            })

        return rows


    def run_sequence(self, text):

        sequence = text.split()

        return self.walker.run(sequence)
