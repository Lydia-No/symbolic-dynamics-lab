class Walker:

    def __init__(self, space, grammar):
        self.space = space
        self.grammar = grammar

    def run(self, sequence):

        state = self.space.initial_state()
        trajectory = [state]

        for symbol in sequence:

            op = self.grammar.operator(symbol)
            state = op.apply(state)

            trajectory.append(state)

        return trajectory
