"""NAMES OF THE AUTHOR(S): Alice Burlats <alice.burlats@uclouvain.be>"""

from search import *

#####################
#       Launch      #
#####################
if __name__ == '__main__':
    problem = AtomPlacement("instances/i01.txt")
    init_state = problem.init_state()
    step_limit = 100
    node = random_walk(problem, step_limit)
    # node = maxvalue(problem, step_limit)
    # node = randomized_maxvalue(problem, step_limit)
    print("Best solution found:")
    print(f"Objective: {node.value()}")
    print(f"State: {node.state}")
    print(f"Steps: {node.step}")