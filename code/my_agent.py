from agent import Agent
from oxono import Game
import math

class Myagent(Agent):

    def __init__(self, player):
        super().__init__(player)
        self.max_depth = 3

    def act(self, state, remaining_time):
        best_action = None
        best_value = -math.inf

        actions = Game.actions(state)

        for action in actions:
            next_state = state.copy()  # je fais une copie pour éviter des coups fantômes
            Game.apply(next_state,action)
            value, move = self.Min_value(
                state = next_state,
                depth = self.max_depth - 1,
                alpha = -math.inf,
                beta=math.inf,
            )
            if value > best_value:
                best_value = value
                best_action = action

        return best_action

    def Max_value(self,state,alpha,beta,depth):
        if Game.is_terminal(state):
            return (Game.utility(state,self.player )* 1000000), None
        elif depth == 0:
            return self.evaluate(state), None
        v = -math.inf
        move = None
        for action in Game.actions(state):
            next_state = state.copy()
            Game.apply(next_state, action)
            v2,action2 = self.Min_value(next_state,alpha,beta,depth - 1)
            if v2 > v:
                v, move = v2, action 
                alpha = max(alpha,v)
            if v >= beta:
                return v, move
        return v, move
    
    def Min_value(self,state,alpha,beta,depth):
        if Game.is_terminal(state):
            return (Game.utility(state,self.player)* 1000000), None
        elif depth == 0:
            return self.evaluate(state), None
        v = math.inf
        move = None
        for action in Game.actions(state):
            next_state = state.copy()
            Game.apply(next_state, action)
            v2, action2 = self.Max_value(next_state,alpha,beta,depth-1)
            if v2 < v:
                v,move = v2,action
                beta = min(beta,v)
            if v <= alpha:
                return v, move
        return v, move
    

    
    
    def evaluate(self, state):
        tableau = state.board
        score = 0

        for row in range(6):
            ligne = tableau[row]
            score += self.score_ligne(ligne)
            score += self.score_ligne_symbole(ligne,state)

        for col in range(6):
            colonne = [tableau[row][col] for row in range(6)]
            score += self.score_ligne(colonne)
            score += self.score_ligne_symbole(colonne,state)
        return score
    
    def score_ligne(self,ligne):
        score = 0
        my_player = self.player
        adv_player = 1 - my_player

        count_me = 0
        count_adv = 0

        for cellule in ligne:
            if  cellule is not None and cellule[1] == my_player:
                count_me += 1
                score -= self.score_sequence(count_adv)
                count_adv = 0
            elif cellule is not None and cellule[1] == adv_player:
                count_adv += 1
                score += self.score_sequence(count_me)
                count_me = 0
            else:
                score += self.score_sequence(count_me)
                score -= self.score_sequence(count_adv)
                count_me = 0
                count_adv = 0

        score += self.score_sequence(count_me)
        score -= self.score_sequence(count_adv)

        return score
    
    def score_ligne_symbole(self,ligne,state):
        score = 0
        count_x = 0
        count_o = 0

        mon_tour = (Game.to_move(state) == self.player)
        
        signe = 1 if mon_tour else -1

        for cellule in ligne:
            if cellule is not None and cellule[0] == 'x':
                count_x += 1
                score += signe * self.score_sequence_symbol(count_o)
                count_o = 0
            elif cellule is not None and cellule[0] == 'o':
                count_o += 1
                score += signe * self.score_sequence_symbol(count_x)
                count_x = 0
            else:
                score += signe * self.score_sequence_symbol(count_x)
                score -= signe * self.score_sequence_symbol(count_o)
                count_x = 0
                count_o = 0
        score += signe * self.score_sequence_symbol(count_x) 
        score += signe * self.score_sequence_symbol(count_o)
        return score
    
    def score_sequence(self,n):
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
        
    def score_sequence_symbol(self,n):
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
    