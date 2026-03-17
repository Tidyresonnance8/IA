"""NAMES OF THE AUTHOR(S): Alice Burlats <alice.burlats@uclouvain.be>"""

from copy import deepcopy


class AtomPlacementState:
    sites_assignment: list[int]

    def __init__(self, sites_assignment: list[int]):
        self.sites_assignment = sites_assignment

    def __deepcopy__(self):
        return AtomPlacementState(deepcopy(self.sites_assignment))

    def __str__(self):
        s = ''
        for v in self.sites_assignment:
            s += ' ' + str(v)
        return s