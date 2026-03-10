import random
from symbolic_dynamics.operators.bit_flip import BitFlip
from symbolic_dynamics.grammars.symbolic_grammar import SymbolicGrammar


def random_grammar(symbol_count, dimension):

    grammar = SymbolicGrammar()

    for i in range(symbol_count):

        word = f"s{i}"

        bit = random.randrange(dimension)

        grammar.add(word, BitFlip(bit))

    return grammar
