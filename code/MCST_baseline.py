import math
import random
import time

from agent import Agent
from oxono import Game, State

"""Facons possible d'améliorer :
        Ordonner les actionsLefts dans Node
        Implémenter de l early Stopping via une heuristic pour les rollout trop long
        Implémenter de l'early stopping en déclarant que la position est un draw
        Faire varier la constante c de UCT
        Utiliser d autre fonctions qu UCT
        Utiliser un dictionnaire dans le début
        Utiliser des playouts plus intelligents
        Faire varier le temps utiliser en fonction de la complexite (=importance) du coup suivant

    
    
    """

class Node:
    """Node représentée par un parent, des enfants, un état, le nombre de playouts et le nombre de wins"""
    # On sait que chaque action va mener a un état différent

    
    def __init__(self, state:State, parent=None, orderActions:bool = False, action=None):
        self.parent = parent
        self.state = state
        self.action = action
        self.children = []
        self.playouts = 0
        self.wins = 0
        self.actionsLeft = Game.actions(state)
        if orderActions:
            self.orderActions()

    def IncrementPlayouts(self):
        self.playouts += 1

    def IncrementBoth(self):
        self.playouts += 1
        self.wins += 1
    
    def addChild(self, child):
        self.children.append(child)
    
    def orderActions(self): # façon d améliorer
        return
    
    def isFullyExpanded(self):
        return len(self.actionsLeft) == 0

    def isTerminal(self):
        return Game.is_terminal(self.state)
    

    def expand(self):
        action = self.actionsLeft.pop()
        newState = self.state.copy()
        Game.apply(newState, action)
        newChild = Node(newState, self, action=action)
        self.addChild(newChild)
        return newChild
    
    def ucb1(self, c:int):
        if(self.playouts == 0): #si un enfant n au aucun playout, on le sélectionne.
            return float('inf')
        return (self.wins/self.playouts) + c * math.sqrt(math.log(self.parent.playouts) / self.playouts)

    def selectChildren(self, c:int):
        """Fonction qui retourne l enfant avec l UCT le plus grand, retourne 0 si aucun enfants"""
        if(len(self.children) == 0):
            return 0
        return max(self.children, key=lambda n: n.ucb1(c))

# partie Heuristic Debut ============================================================================================================
def evaluate( state:State, player:int):
    tableau = state.board
    score = 0

    for row in range(6):
        ligne = tableau[row]
        score += score_ligne(ligne, player)
        score += score_ligne_symbole(ligne,state, player)

    for col in range(6):
        colonne = [tableau[row][col] for row in range(6)]
        score += score_ligne(colonne, player)
        score += score_ligne_symbole(colonne,state, player)
    return 1 / (1 + math.exp(-score / 200))

def score_ligne(ligne, player:int):
    score = 0
    
    adv_player = 1 - player

    count_me = 0
    count_adv = 0

    for cellule in ligne:
        if  cellule is not None and cellule[1] == player:
            count_me += 1
            score -= score_sequence(count_adv)
            count_adv = 0
        elif cellule is not None and cellule[1] == adv_player:
            count_adv += 1
            score += score_sequence(count_me)
            count_me = 0
        else:
            score += score_sequence(count_me)
            score -= score_sequence(count_adv)
            count_me = 0
            count_adv = 0

    score += score_sequence(count_me)
    score -= score_sequence(count_adv)

    return score
    
def score_ligne_symbole(ligne,state, player:int):
    score = 0
    count_x = 0
    count_o = 0

    mon_tour = (Game.to_move(state) == player)
        
    signe = 1 if mon_tour else -1

    for cellule in ligne:
        if cellule is not None and cellule[0] == 'x':
            count_x += 1
            score += signe * score_sequence_symbol(count_o)
            count_o = 0
        elif cellule is not None and cellule[0] == 'o':
            count_o += 1
            score += signe * score_sequence_symbol(count_x)
            count_x = 0
        else:
            score += signe * score_sequence_symbol(count_x)
            score -= signe * score_sequence_symbol(count_o)
            count_x = 0
            count_o = 0
    score += signe * score_sequence_symbol(count_x) 
    score += signe * score_sequence_symbol(count_o)
    return score
    
def score_sequence(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    elif n == 2:
        return 10
    elif n == 3:
        return 100
    elif n >= 4:
        return 10000 
        
def score_sequence_symbol(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    elif n == 2:
        return 5
    elif n == 3:
        return 30
    elif n >= 4:
        return 5000
# partie heuristic fin ===================================================================================================================

def simulate(state:State, intelligentsPlayouts:int, earlyStopping:int, earlyStop:int): #effectue le playout
    s = state.copy()
    depth = 0

    while not Game.is_terminal(s):
        actions = Game.actions(s)

        if intelligentsPlayouts == 0: # playout random
            Game.apply(s, random.choice(actions))
        elif intelligentsPlayouts == 1: # playout intelligent : joue un coup gagnant immédiat si possible
            move = None
            for action in actions:
                tmp = s.copy()
                Game.apply(tmp, action)
                if Game.is_terminal(tmp) and Game.utility(tmp, s.current_player) == 1:
                    move = action
                    break
            Game.apply(s, move if move else random.choice(actions))

        depth += 1

        if earlyStopping == 1 and depth >= earlyStop: # early stopping heuristique 
            score = evaluate(s, s.current_player)
            if(s.current_player == 0):
                return (score, 1-score)
            else:
                return (1-score, score)

        elif earlyStopping == 2 and depth >= earlyStop: # early stopping draw 
            return (0.5, 0.5)

    # retourne les utilités des deux joueurs normalisées en [0, 1]
    return (
        (Game.utility(s, 0) + 1) / 2,
        (Game.utility(s, 1) + 1) / 2,
    )

class AgentMCTSFinal(Agent):
    def __init__(self, player, constanteUCT:int = 1.41, earlyStopping:int = 0, earlyStop:int = 18, intelligentsPlayouts:int = 0, intelligentTimeUse:bool = False, maxTime:int = 300):
        super().__init__(player)
        self.constanteUCT = constanteUCT
        self.intelligentTimeUse = intelligentTimeUse 
        self.earlyStopping = earlyStopping # =0 quand pas d early Stopping, =1 avec Heuristic, =2 avec Draw
        self.earlyStop = earlyStop
        self.maxTime = maxTime
        self.intelligentsPlayouts = intelligentsPlayouts # =0 quand playouts random, =1 avec playouts un tout petit peu malin
        # TODO
        self.sortActions = False
        self.useOrtherfunc = 0 # =0 avec UCT
        self.useDictionnary = 0 # =0 sans dictionnaires
        

    def ComputeTime(self, state:State, remaining_time):
        # nombre total de totems restant pour le joueur
        piecesLeft = state.pieces_x[self.player] + state.pieces_o[self.player]
        
        baseTime = remaining_time / piecesLeft

        numActions = len(Game.actions(state))
        branchScale = min(2.0, numActions / 30)

        # gaussienne centrée a 45% de progression de la partie
        progress = 1.0 - (piecesLeft / 16.0) 
        phaseFactor = 1.0 + 0.6 * math.exp(-8.0 * (progress - 0.45) ** 2)

        allocated = baseTime * branchScale * phaseFactor
        return min(remaining_time * 0.3, max(0.5, allocated))
        
    
    def select(self, node, c:int):
        """Descend dans l'arbre en suivant la formule de sélection"""
        while not node.isTerminal():
            if not node.isFullyExpanded():
                return node
            node = node.selectChildren(c)
        return node
        
    def backPropagate(self, node:Node, utils:tuple[int, int]):
        # Précalcul des deux utilités une seule fois
        
        current = node
        while current.parent is not None:
            player = current.parent.state.current_player
            current.playouts += 1
            current.wins += utils[player]
            current = current.parent
        current.playouts += 1 
    
    def act(self, state, remaining_time):
        if(self.intelligentTimeUse):
            timeUse = self.ComputeTime(state, remaining_time)
        else:
            timeUse = self.maxTime/17
        deadline = time.perf_counter() + timeUse
        root = Node(state)
        if(len(root.actionsLeft) == 1):
            return root.actionsLeft[0]
        while time.perf_counter() < deadline:
            node = self.select(root, self.constanteUCT)
            
            if not node.isTerminal():
                if(self.sortActions):
                    node.orderActions()
                node = node.expand()
            
            utility = simulate(node.state, self.intelligentsPlayouts, self.earlyStopping,  self.earlyStop)
            self.backPropagate(node, utility)
        return max(root.children, key=lambda n: n.playouts).action