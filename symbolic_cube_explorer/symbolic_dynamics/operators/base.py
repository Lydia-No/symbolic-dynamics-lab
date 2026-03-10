class Operator:
    """
    Base transformation operator.
    """

    def apply(self, state):
        raise NotImplementedError
