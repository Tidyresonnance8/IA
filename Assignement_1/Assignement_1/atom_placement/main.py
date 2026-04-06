"""NAMES OF THE AUTHOR(S): Alice Burlats <alice.burlats@uclouvain.be>"""
from search import *

#####################
#       Launch      #
#####################
if __name__ == '__main__':
    step_limit = 100

    for i in range(1, 11):
        instance = f"instances/i{i:02d}.txt"
        print(f"\n{'='*40}")
        print(f"Instance: {instance}")
        print(f"{'='*40}")

        problem = AtomPlacement(instance)
        init_state = problem.init_state()

        node = random_walk(problem, step_limit)
        # node = maxvalue(problem, step_limit)
        # node = randomized_maxvalue(problem, step_limit)

        print("Best solution found:")
        print(f"Objective: {node.value()}")
        print(f"State:     {node.state}")
        print(f"Steps:     {node.step}")