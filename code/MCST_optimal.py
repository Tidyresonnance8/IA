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
        Stocker en mémoire l arbre entre les coups
    
    
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
    def setRoot(self):
        self.parent = None

    def findChild(self, stateChild:State):
        for child in self.children:
            if(child.state == stateChild):
                return child
        return -1
        
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
    i = 0
    EStop = False
    while not Game.is_terminal(s):
        actions = Game.actions(s)
        i += 1
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
            EStop = True
            score = evaluate(s, s.current_player)
            if(s.current_player == 0):
                return (score, 1-score), i, EStop
            else:
                return (1-score, score), i, EStop

        elif earlyStopping == 2 and depth >= earlyStop: # early stopping draw 
            EStop = True
            return (0.5, 0.5), i, EStop

    # retourne les utilités des deux joueurs normalisées en [0, 1]
    return (
        (Game.utility(s, 0) + 1) / 2,
        (Game.utility(s, 1) + 1) / 2,
    ), i, EStop

class AgentMCTSFinal(Agent):
    def __init__(self, player, constanteUCT:int = 0.6, earlyStopping:int = 2, earlyStop:int = 18, intelligentsPlayouts:int = 0, intelligentTimeUse:bool = True, rememberTree:bool = False, maxTime:int = 300, selectPerBatch:int = 0):
        super().__init__(player)
        self.constanteUCT = constanteUCT
        self.intelligentTimeUse = intelligentTimeUse 
        self.earlyStopping = earlyStopping # =0 quand pas d early Stopping, =1 avec Heuristic, =2 avec Draw
        self.earlyStop = earlyStop
        self.maxTime = maxTime
        self.intelligentsPlayouts = intelligentsPlayouts # =0 quand playouts random, =1 avec playouts un tout petit peu malin
        self.rememberTree = rememberTree # se souvient de l arbre du coup précédent.
        self.root:Node = None
        self.selectPerBatch = selectPerBatch
        self.oldSelected:Node = None
        self.intSelect = 0
        # TODO, pas encore implémentées. idées possibles. (pour la contest?)
        self.sortActions = False
        self.useOrtherfunc = 0 # =0 avec UCT
        self.useDictionnary = 0 # =0 sans dictionnaires
        # améliorer l'heuristic
        # end TODO
        self.iterCount = 0
        self.nbChildFound = 0
        self.nbOfRollouts = 0
        self.nbEarlyStop = 0
        

    def ComputeTime(self, state:State, remaining_time):
        piecesLeft = state.pieces_x[self.player] + state.pieces_o[self.player]

        # Baseline identique au flat (maxTime/17) : ITU redistribue le meme budget total en moyenne.
        baseTime = self.maxTime / 17.0

        # Complexite : plus d'actions = coup plus difficile. Centre sur 35 actions.
        numActions = len(Game.actions(state))
        complexityFactor = min(2.0, max(0.5, numActions / 35.0))

        # Phase : gaussienne centree a 40% de progression (debut du milieu de partie).
        progress = 1.0 - (piecesLeft / 16.0)
        phaseFactor = 1.0 + 0.8 * math.exp(-10.0 * (progress - 0.40) ** 2)

        allocated = baseTime * complexityFactor * phaseFactor
        return min(remaining_time * 0.90, max(remaining_time * 0.01, allocated))
    
    
    
    def select(self, node:Node, c:int):
        """Descend dans l'arbre en suivant la formule de sélection"""
        if(self.selectPerBatch == 0):
            while not node.isTerminal():
                if not node.isFullyExpanded():
                    return node
                node = node.selectChildren(c)
            return node
        else:
            if(self.intSelect % self.selectPerBatch == 0): #pas besoin de géré l initialisation car inSelect est fixée a 0 au depart
                while not node.isTerminal():
                    if not node.isFullyExpanded():
                        self.oldSelected = node
                        self.intSelect = 1 #évite de calculer le modulo sur de gros nombres, peut être omis
                        return node
                    node = node.selectChildren(c)
                return node
            else:
                self.intSelect += 1
                return self.oldSelected
            
            
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
        self.intSelect = 0

        if(not self.rememberTree): 
            root = Node(state)
            if(len(root.actionsLeft) == 1):
                return root.actionsLeft[0]
            while time.perf_counter() < deadline:
                node = self.select(root, self.constanteUCT)
                
                if not node.isTerminal() and not node.isFullyExpanded():
                    if(self.sortActions):
                        node.orderActions()
                    node = node.expand()
                
                utility, i, Estop  = simulate(node.state, self.intelligentsPlayouts, self.earlyStopping,  self.earlyStop)
                self.iterCount += i
                self.nbOfRollouts += 1
                if(Estop):
                    self.nbEarlyStop += 1
                self.backPropagate(node, utility)
            return max(root.children, key=lambda n: n.playouts).action
        

        elif(self.rememberTree and self.iterCount == 0):
            root = Node(state)
            if(len(root.actionsLeft) == 1):
                return root.actionsLeft[0]
            while time.perf_counter() < deadline:
                node = self.select(root, self.constanteUCT)
                
                if not node.isTerminal() and not node.isFullyExpanded():
                    if(self.sortActions):
                        node.orderActions()
                    node = node.expand()
                
                utility, i, Estop = simulate(node.state, self.intelligentsPlayouts, self.earlyStopping,  self.earlyStop)
                self.iterCount += i
                self.nbOfRollouts += 1
                if(Estop):
                    self.nbEarlyStop += 1
                self.backPropagate(node, utility)
            self.root = max(root.children, key=lambda n: n.playouts)
            return self.root.action     
        

        else:
            found = self.root.findChild(state)
            if found == -1:
                self.root = Node(state)
            else:
                self.nbChildFound += 1
                self.root = found
            self.root.setRoot()
            root = self.root
            if(len(root.actionsLeft) == 1):
                return root.actionsLeft[0]
            while time.perf_counter() < deadline:
                node = self.select(root, self.constanteUCT)
                
                if not node.isTerminal() and not node.isFullyExpanded():
                    if(self.sortActions):
                        node.orderActions()
                    node = node.expand()
                
                utility, i, Estop  = simulate(node.state, self.intelligentsPlayouts, self.earlyStopping,  self.earlyStop)
                self.iterCount += i
                self.nbOfRollouts += 1
                if(Estop):
                    self.nbEarlyStop += 1
                self.backPropagate(node, utility)
            self.root = max(root.children, key=lambda n: n.playouts)
            return self.root.action  
