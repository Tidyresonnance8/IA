from agent import Agent
from oxono import Game
import random
import math


class MCSTNode:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.children = []
        self.parent = parent
        self.visits = 0
        self.Q = 0
        self.actions_to_try = Game.actions(state)
        self.action = action

    @staticmethod
    def simulate_act(state):
        actions = list(Game.actions(state))
        return random.choice(actions)

    """Return winner (0 or 1)"""
    def simulate(self):
        state = self.state.copy()
        while not Game.is_terminal(state):
            Game.apply(state, self.simulate_act(state))

        score = Game.utility(state, 1)
        if score == 0:
            return random.randint(0, 1)
        return int(score == 1)

    # todo: adapt as its taken from internet
    def best_leaf(self, c=1.4):
        for child in self.children:
            if child.visits == 0:
                return child

        def ucb(child):
            exploit = child.Q / child.visits
            explore = c * math.sqrt(2*math.log(self.visits) / child.visits)
            return exploit + explore

        return max(self.children, key=ucb)

    def best_move(self):
        return max(self.children, key=lambda c: c.visits).action

    def is_terminal(self):
        return Game.is_terminal(self.state)

    def is_expanded(self):
        return not bool(self.actions_to_try)

    def expand(self):
        action = self.actions_to_try.pop()
        new_state = self.state.copy()
        Game.apply(new_state, action)
        node = MCSTNode(new_state, parent=self, action=action)
        self.children.append(node)
        return node

    def backpropagate(self, winner):
        self.visits += 1

        if self.state.current_player == winner:
            self.Q -= 1
        else:
            self.Q += 1

        if self.parent:
            self.parent.backpropagate(winner)


class MCSTAgent(Agent):
    def __init__(self, player):
        super().__init__(player)
        # todo keep tree
        self.root = None

    def search(self, state, iterations):
        root = MCSTNode(state)
        self.root = root
        for _ in range(iterations):
            # Selection: find most interesting node to expand
            leaf = root
            while not leaf.is_terminal() and leaf.is_expanded():
                leaf = leaf.best_leaf()
            # Expansion: add 1 node
            if not leaf.is_terminal():
                leaf = leaf.expand()
            # Simulation
            result = leaf.simulate()
            # Backpropagate
            leaf.backpropagate(result)

        return root.best_move()

    def act(self, state, remaining_time):
        action = self.search(state, 20000)
        #G = build_graph(self.root)
        #draw_graph(G)
        return action


# chatpgt
"""
import networkx as nx
import matplotlib.pyplot as plt
def build_graph(root):
    G = nx.DiGraph()  # directed graph

    def add_nodes_edges(node, depth=0, max_depth=0):
        node_id = id(node)  # unique identifier

        # Add node with label
        label = f"{node.Q}/{node.visits}"
        G.add_node(node_id, label=label)

        if depth > max_depth:
            return
        for child in node.children:
            child_id = id(child)

            # Add edge (parent -> child)
            G.add_edge(node_id, child_id)

            # Recursive call
            add_nodes_edges(child, depth+1, max_depth)

    add_nodes_edges(root)
    return G

# chatgpt
def draw_graph(G):
    #pos = nx.spring_layout(G)  # layout algorithm
    pos = nx.nx_agraph.graphviz_layout(G, prog="dot")

    labels = nx.get_node_attributes(G, 'label')

    nx.draw(G, pos, with_labels=False, node_size=200)
    nx.draw_networkx_labels(G, pos, labels)

    plt.show()
"""