class SymbolicGrammar:

    def __init__(self):
        self.rules = {}

    def add(self, symbol, operator):
        self.rules[symbol] = operator

    def operator(self, symbol):
        if symbol not in self.rules:
            raise KeyError(f"Unknown symbol: {symbol}")
        return self.rules[symbol]
