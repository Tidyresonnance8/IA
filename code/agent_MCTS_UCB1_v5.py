from __future__ import annotations

from agent import Agent
from oxono import Game, State
import random
import time
import math
import heapq

PINK_PLAYER = 0
BLACK_PLAYER = 1
REFERENCE_BRANCHING = 30 #typical branching factor (to change maybe)

"""
#####V5

####################################################################################################################################################################
changes made:

V1:
-Simple MCTS with UCB1 selection policy

V2:
-increased the maximum simulation time: 5sec->15sec
-before beginning the MCTS, we check if there's a killer move among the available actions (checks only when the number of turns/move has surpassed 5)
-before returning the recommended action, we check if the recommended action leads to state were a terminal action is availabe for the opponent (checks
only after the number of moves has surpassed 9) (to not get trapped by the opponenent)

V3:
-changes to simulate() simulation policy such as a better rollout/playout policy with a light tactical heuristic 

V4:
-changes to expand_one_child to choose a child according to the tactical heuristic

V5:
-get out of jail free card, returns a safe action, not the second optimal, not a random one
####################################################################################################################################################################

To change:
-in the ucb1 formula, try different values of c
-in select() try a different selection strategie for the opponent (maybe minimizing only the exploitation term) or maximizing its own UCB1-> add field win_opp in MonteCarlo node
-greedy vs explorative ? maybe explore more at the beginning and less at the end 
-tree reuse instead of recreating a tree at each move/turn

-maybe use only heuristic in expand_one_child() when we are player 1
-maybe use only heursitic in simulate() for n simulation instead of always  
-change get out of jail free card, to return a safe action, not the second optimal, not a random one, maybe check the 2nd optimal --> checking doesnt take time and if safe retun it
-allow a different maximum thinking time when the board is getting more devellopped


!!!! v5 clearly has a disavantage over v4 when he is player 0--> maybe 20sec too much, maybe because of using heuristic in expand_one_child() (because v4 had the same probleme against v3)
####################################################################################################################################################################
"""

####helpers

#indepent of the agent, returns winning actions for both players
def immediate_winning_actions(state:State)->list[tuple[str, tuple[int, int], tuple[int, int]]]:
    winning_actions = []
    
    for action in Game.actions(state):
        next_state = state.copy()
        Game.apply(next_state,action)
        
        if Game.is_terminal(next_state) and Game.utility(next_state,state.current_player) == 1:
            winning_actions.append(action)
    
    return winning_actions

#indepent of the agent, returns safe actions for both players
def safe_actions(state:State)->list[tuple[str, tuple[int, int], tuple[int, int]]]:
    safe = []
    
    for action in Game.actions(state):
        next_state = state.copy()
        Game.apply(next_state,action)
        
        #if we win with this action it is fine
        if Game.is_terminal(next_state) and (Game.utility(next_state,state.current_player) == 1 or Game.utility(next_state,state.current_player) == 0): #prefer draw over possible loosing actions
            safe.append(action)
            continue
        
        op_wins = immediate_winning_actions(next_state)
        
        if not op_wins:
            safe.append(action)
    
    return safe

#indepent of the agent, returns tactical actions for both players
def choose_tactical_action(state:State):
    actions = list(Game.actions(state))
    
    if not actions:
        return None
    
    #winning moves
    winning = immediate_winning_actions(state)
    if winning:
        return random.choice(winning)
    
    #avoid opponents winnig states
    safe = safe_actions(state)
    if safe:
        return random.choice(safe)
    
    #otherwise random choice
    return random.choice(actions)



class MonteCarloNode():
    
    def __init__(self,state:State,playouts:int, win:int, player:int, parent: MonteCarloNode|None, action_applied: tuple[str, tuple[int, int], tuple[int, int]]|None): 
        self.state = state
        self.childs: list[MonteCarloNode] = []
        self.playouts = playouts
        self.win = win #utility of root player (i.e our agent), a win for our agent +1, draw +0.5, loss 0.0 (to change maybe)
        self.player = player
        self.parent = parent
        self.action_applied = action_applied
    
    def is_terminal(self):
        return Game.is_terminal(self.state)
    
    def max_child(self):
        """
        selects the child of the current node with the most playouts:
        -action with the most amount of playouts has the highest winrate
        """
        
        """
        top2 = heapq.nlargest(2, self.childs, key=lambda x: x.playouts)
        best_child = top2[0]
        second_best = top2[1] if len(top2) > 1 else None
        """
        
        best_child = max(self.childs,key=lambda x: x.playouts) 
        return best_child
    
    def legal_actions(self):
        return list(Game.actions(self.state))
    
    def is_fully_expanded(self)->bool:
        """
        checks if all possible actions of a node were generated
        """
        
        return len(self.childs) == len(self.legal_actions())
    
    def untried_actions(self):
        """
        returns a list of all the untried actions of the current state/node
        """
        
        legal = self.legal_actions()
        tried = {child.action_applied for child in self.childs}
        
        return [a for a in legal if a not in tried]
    
    def select_tactical_action(self,actions):
        # Prefer immediate winning move if available
        winning = []
        safe = []

        for action in actions:
            next_state = self.state.copy()
            Game.apply(next_state, action)

            if Game.is_terminal(next_state) and Game.utility(next_state, self.state.current_player) == 1:
                winning.append(action)
                continue

            opponent_wins = immediate_winning_actions(next_state)
            if not opponent_wins:
                safe.append(action)

        if winning:
            action = random.choice(winning)
        elif safe:
            action = random.choice(safe)
        else:
            action = random.choice(actions)
        
        return action
    
    def expand_one_child(self)->MonteCarloNode:
        """
        generates one child of a monteCarloNode 
        and returns it 
        """
        
        actions = self.untried_actions()
        
        if not actions:
            raise ValueError("Node is fully expanded")

        #selects a random action among untried actions (to change maybe)
        #action = random.choice(actions
        action = self.select_tactical_action(actions)
        
        new_player = BLACK_PLAYER if self.player == PINK_PLAYER else PINK_PLAYER
        
        next_state = self.state.copy()
        Game.apply(next_state, action)

        child = MonteCarloNode(
            state=next_state,
            playouts=0,
            win=0,
            player=new_player,
            parent=self,
            action_applied=action
        )

        self.childs.append(child)
        return child
    
    def compute_ucb1(self,c:float)->float:
        """
        computes the UCB1 (upper confidence bound formula) value of a node based on the root_player (our agent):
        -higher better for our agent
        -lower better for ennely agent
        """
        
        if self.playouts == 0:
            return float("inf")

        if self.parent is None or self.parent.playouts == 0:
            return float("inf")

        exploitation = self.win / self.playouts
        exploration = c * math.sqrt(math.log(self.parent.playouts) / self.playouts)
        return exploitation + exploration
    
    def winner(self,root_player:int)->int:
        return Game.utility(self.state,root_player)
        
         
class MonteCarloTree():
    def __init__(self, root:MonteCarloNode):
        self.root = root
            
    def select(self,c)->MonteCarloNode:
        """
        selects a leaf node of the tree, by expanding in width first
        and then by selecting a leaf node with optimal UCB1 value
        """
        
        current = self.root
    
        while not current.is_terminal():
            if not current.is_fully_expanded():
                return current

            # select node with maximum UCB1 if its the agents turn
            if (current.player == self.root.player):
                current = max(current.childs,key=lambda child:child.compute_ucb1(c))
            else:
                #select node with minimum UCB1 if its the ennemy agents turn
                current = min(current.childs,key=lambda child:child.compute_ucb1(c))

        return current
        
    def expand(self,leaf:MonteCarloNode)->MonteCarloNode:
        """
        expands a leaf node by adding a child 
        and returns it 
        """
        
        return leaf.expand_one_child()
    
    def simulate(self, child: MonteCarloNode,root_player:int) -> int:
        """
        simulation of a playout until reaching a terminal state
        returns the utility of the final state
        """
        
        current_node = child

        while True:
            if current_node.is_terminal():
                return current_node.winner(root_player)

            current_player = current_node.player
            next_player = BLACK_PLAYER if current_player == PINK_PLAYER else PINK_PLAYER

            next_state = current_node.state.copy()
            actions = list(Game.actions(next_state))

            if not actions:
                return current_node.winner(root_player)

            #action = random.choice(actions) #to change with heuristic
            action = choose_tactical_action(next_state)
            
            Game.apply(next_state, action)

            current_node = MonteCarloNode(
                state=next_state,
                playouts=0,
                win=0,
                player=next_player,
                parent=None,
                action_applied=action
            )
    
    def back_propagate(self,child:MonteCarloNode, result:int):
        """
        updates the result to all the tree nodes going up to the root 
        """
        
        current = child

        if result == 1:
            reward = 1.0
        elif result == 0:
            reward = 0.5
        else:
            reward = 0.0

        while current is not None:
            current.playouts += 1
            current.win += reward
            current = current.parent
              
    def select_best_action(self):
        """
        selects the best action to be applied to the current state
        """
        
        best_child = self.root.max_child()
       
        
        return best_child.action_applied
        
class MCTreeSearch():
    
    def __init__(self,state,remaining_time,player):
        self.state = state
        self.remaining_time = remaining_time
        self.player = player 
    
    def is_time_remaining(self,before_loop, after_loop):
        
        return after_loop - before_loop < self.remaining_time
    
    def tree_search(self,c):
        """
        tree search to selects the optimal action 
        """
        
        #creation of the tree
        root = MonteCarloNode(self.state,playouts=0,win=0,
                              player=self.player, parent=None, action_applied=None)
        
        tree = MonteCarloTree(root)
        
        start = time.perf_counter()
        end = 0
        
        #Monte Carlo Tree Search algorithm
        while self.is_time_remaining(before_loop=start,after_loop=end):
            
            #select a leaf node
            leaf = tree.select(c)
            if leaf.is_terminal():
                result = leaf.winner(self.player)
                tree.back_propagate(leaf, result)
                end = time.perf_counter()
                continue
            
            actions = list(Game.actions(leaf.state))
            if not actions:
                result = leaf.winner(self.player)
                tree.back_propagate(leaf, result)
                end = time.perf_counter()
                continue
            
            #expand the current leaf node
            child = tree.expand(leaf)
            
            #to change: use heuristic for the first n rollouts where n is the number of childrens of the root node
            #begin playout simulation
            result = tree.simulate(child,self.player) #we pass in self.player to have the utility of the root player (our agent)
            
            #update the child parents with the resulting utility of the root player 
            tree.back_propagate(child,result)
            
            end = time.perf_counter()
        
        return tree.select_best_action()
                

class Mcts_agent(Agent):
    
    def __init__(self, player):
        super().__init__(player)
        self.move_number = 0
        self.c = 1.4 #weight of the exploration term (to change maybe)
         
    def compute_time_budget(self,state:State,remaining_time):
        safety_margin = 2.0
        usable = max(0.0,remaining_time-safety_margin)
        
        estimated_total_moves = 20 #jeu ce terminer en +- 20 moves
        moves_left = max(1,estimated_total_moves-self.move_number)
        
        base_time = usable/moves_left #estimation du temps par action
        
        num_actions = len(list(Game.actions(state))) #branching factor 
        #if num_actions < 
        complexity_factor = min(2.0, max(0.6,num_actions/REFERENCE_BRANCHING))  
        
        allocated = base_time*complexity_factor
        
        #minimum simulation time = 0.5sec
        #maximum simulation time = 5sec (to change maybe)
        
        ###to remove !!!
        if self.move_number >= 6: #to change maybe
            return max(0.5,min(allocated,20.0))
        
        return max(0.5,min(allocated,15.0))
    
    def is_time_remaining(self,before_loop, after_loop,remaining_time):
        
        return after_loop - before_loop < remaining_time
    
    def isKillerMove(self,state:State,action):
        """
        checks if the recommended action leads to a terminal state
        """
        
        next_state = state.copy()
        Game.apply(next_state,action)
    
        return Game.is_terminal(next_state) and Game.utility(next_state,state.current_player) == 1
    
    def will_kill(self,state:State,action, remaining_time):
        """
        return true if the recommended action leads to a state where a killer move is present 
        for the opponent 
        """
        
        Game.apply(state,action)
        
        op_actions = Game.actions(state)
        start = time.perf_counter()
        end = 0
        i = 0
        while self.is_time_remaining(start,end,remaining_time):
            action = op_actions[i]
            if self.isKillerMove(state,action):
                return True
            i += 1
            end = time.perf_counter()
            if i == len(op_actions):
                break
        
        return False
    
    def get_killer_move(self,state,actions,remaining_time):
        start = time.perf_counter()
        end = 0
        i = 0
        killer_action = None
        while self.is_time_remaining(start,end,remaining_time):        
            action = actions[i]
            if self.isKillerMove(state,action):
                killer_action = action
                
                end = time.perf_counter()
                break
            
            i += 1
            if i == len(actions):
                
                end = time.perf_counter()
                break
        
        elapsed = end-start
        remaining_time = remaining_time - elapsed
        
        return killer_action,remaining_time
        
    
    def act(self, state:State, remaining_time)->tuple[str, tuple[int, int], tuple[int, int]]:
        #print(self.move_number)
        
        actions = list(Game.actions(state))
        #if self.move_number >= 10:
        #    print(len(actions))
        
        #emergency 
        if (remaining_time < 1):
        
            return random.choice(actions)
        
        #checks among available actions if there is a killermove
        killer_action,remaining_time = self.get_killer_move(state,actions,remaining_time)    
        if killer_action is not None: return killer_action 
        
        
        time_allocated = self.compute_time_budget(state,remaining_time)

        #begin search of the best action
        action_search = MCTreeSearch(state=state,remaining_time=time_allocated,player=self.player) 
        recommended_action = action_search.tree_search(self.c)
        
        state_copy = state.copy()
        remaining_time = remaining_time-time_allocated
        
        #get out of jail free card
        if (self.will_kill(state_copy,recommended_action,remaining_time)):
            
            #instead of the recommended action return a safe action
            safe = safe_actions(state)
            
            if safe:
                return random.choice(safe)
        
        self.move_number += 1
        return recommended_action
        