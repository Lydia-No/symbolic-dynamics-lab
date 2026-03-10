class SymbolicGrammar:

    def __init__(self):

        self.rules = {}

    def add(self, symbol, operator):

        self.rules[symbol] = operator

    def operator(self, symbol):

        return self.rules[symbol]
