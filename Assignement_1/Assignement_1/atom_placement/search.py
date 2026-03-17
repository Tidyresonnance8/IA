"""NAMES OF THE AUTHOR(S): Alice Burlats <alice.burlats@uclouvain.be>"""

import random
from lsnode import LSNode
from atom_placement import AtomPlacement


def random_walk(problem, limit=100) -> LSNode:
    """
    Perform a random walk in the search space and returns a LSNode corresponding to the best found solution.
    """
    current = LSNode(problem, problem.init_state(), 0)
    best = current
    for step in range(limit):
        current = random.choice(list(current.expand()))
        if current.value() < best.value():
            best = current
    return best


def max_value(problem: AtomPlacement, limit=100) -> LSNode:
    """
    Perform a local search by selecting at each iteration the best neighbor of the current state.
    Returns a LSNode corresponding to the best found solution
    """
    current = LSNode(problem, problem.init_state(), 0)
    for step in range(limit):
        best_neighbor = None
        for neighbor in current.expand():
            if best_neighbor is None or neighbor.value() > best_neighbor.value():
                best_neighbor = neighbor
        if best_neighbor is None or best_neighbor.value() > current.value():
            current = best_neighbor
        else:
            break
    return current


def randomized_max_value(problem: AtomPlacement, limit=100) -> LSNode:
    """
    Perform a local search by randomly selecting a neighbor among the 5 bests
    at each iteration.
    Returns a LSNode corresponding to the best found solution
    """
    current = LSNode(problem, problem.init_state(), 0)
    for step in range(limit):
        all_neighbor = list(current.expand())
        unique = sorted(all_neighbor, key=lambda noeud: noeud.value(), reverse=True)
        best_unique = unique[:5]
        neighbor = random.choice(best_unique)
        if neighbor.value() > current.value():
            current =  neighbor
        else:
            break
    return current