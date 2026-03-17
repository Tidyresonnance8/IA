"""NAMES OF THE AUTHOR(S): Alice Burlats <alice.burlats@uclouvain.be>"""

from atom_placement_state import AtomPlacementState


class AtomPlacement:

    # An init state building is provided here but you can change it at will
    def init_state(self) -> AtomPlacementState:
        sites = []
        for atom_type, quantity in enumerate(self.n_types):
            for i in range(quantity):
                sites.append(atom_type)

        return AtomPlacementState(sites)

    # Returns the neighbor states of the given state as a list of AtomPlacementState
    def neighbors(self, state: AtomPlacementState) -> list[AtomPlacementState]:
        my_neighbors = []
        N = len(state.sites_assignment)
        element = state.sites_assignment
        for i in range(N):
            for j in range(i+1,N):
                if element[i] != element[j]:
                    nouvel_etat = state.__deepcopy__()
                    nouvel_etat.sites_assignment[i], nouvel_etat.sites_assignment[j] = nouvel_etat.sites_assignment[j], nouvel_etat.sites_assignment[i]
                    my_neighbors.append(nouvel_etat)

        return my_neighbors

    # Returns the objective value of the given state
    def value(self, state: AtomPlacementState) -> int:
        count = 0
        for lien in self.edges:
            # identification des sites
            site1 = lien[0]
            site2 = lien[1]
            # état des atomes
            type1 = state.sites_assignment[site1]
            type2 = state.sites_assignment[site2]
            # extraction de l'énergie correspondant au lien avec les atomes
            energie = self.energy_matrix[type1][type2]
            count += energie
        return count

    def __init__(self, filename: str):
        file = open(filename)
        line = file.readline()
        self.n_sites = int(line.split(' ')[0])
        self.k = int(line.split(' ')[1])
        self.n_edges = int(line.split(' ')[2])
        self.edges = []
        file.readline()

        self.n_types = [int(val) for val in file.readline().split(' ')]
        if sum(self.n_types) != self.n_sites:
            print('Invalid instance, wrong number of sites')
        file.readline()

        self.energy_matrix = []
        for i in range(self.k):
            self.energy_matrix.append([int(val) for val in file.readline().split(' ')])
        file.readline()

        for i in range(self.n_edges):
            self.edges.append([int(val) for val in file.readline().split(' ')])



