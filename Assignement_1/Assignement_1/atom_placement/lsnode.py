"""NAMES OF THE AUTHOR(S): Alice Burlats <alice.burlats@uclouvain.be>"""

class LSNode:


    def __init__(self, problem, state, step):
        """Create a local search Node."""
        self.problem = problem
        self.state = state
        self.step = step
        self._value = None

    def __repr__(self):
        return "<Node %s>" % (self.state,)

    def value(self):
        """Returns the value of the state contained in this node."""
        if self._value is None:
            self._value = self.problem.value(self.state)
        return self._value

    def expand(self):
        """Yields nodes reachable from this node. [Fig. 3.8]"""
        # end = []
        for neighbor in self.problem.neighbors(self.state):
            # end.append(LSNode(self.problem, next, self.step + 1))
            yield LSNode(self.problem, neighbor, self.step + 1)
        # return end
