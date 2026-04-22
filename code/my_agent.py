from agent import Agent
from oxono import Game
import math
import time

class Myagent(Agent):

    def __init__(self, player):
        
        super().__init__(player)
        #self.max_depth = 3
        self.eval_cache = {}

    def act(self, state, remaining_time):
        start_time = time.time()
        
        pieces_restantes = state.pieces_x[self.player] + state.pieces_o[self.player]

        time_limit = (remaining_time /max(1,pieces_restantes)) - 0.5

        time_limit = max(0.1, time_limit)  # Au cas où on serait super serré au niveau du temps

        best_action = None
        #best_value = -math.inf

        actions = Game.actions(state)

        if len(actions) > 0:
            best_action = actions[0] # au pire du pire on renvoie le premier coup possible
        
        depth = 1

        while True:
            best_action_for_this_depth = None
            best_value_for_this_depth = -math.inf
            
            scored_actions = []

            for action in actions:
                current_time = time.time()
                if (current_time - start_time) > time_limit:
                    return best_action
                
                next_state = state.copy()  # je fais une copie pour éviter des coups fantômes
                Game.apply(next_state,action)
                value, move = self.Min_value(
                    state = next_state,
                    depth = depth - 1,
                    alpha = -math.inf,
                    beta=math.inf,
                )
                scored_actions.append((value,action))

                if value > best_value_for_this_depth:
                    best_value_for_this_depth = value
                    best_action_for_this_depth = action
            
            best_action = best_action_for_this_depth

            depth += 1

            scored_actions.sort(reverse=True)
              
            actions = [act for val, act in scored_actions]

            #return best_action

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
        cle = str(tableau) + "_" + str(Game.to_move(state))  # Le Plateau + A qui le tour

        if cle in self.eval_cache:
            return self.eval_cache[cle]
        
        score = 0
        
        for row in range(6):
            ligne = tableau[row]
            score += self.score_ligne(ligne)
            score += self.score_ligne_symbole(ligne,state)

        for col in range(6):
            colonne = [tableau[row][col] for row in range(6)]
            score += self.score_ligne(colonne)
            score += self.score_ligne_symbole(colonne,state)

        cases_centrales = [(2,2),(2,3),(3,2),(3,3)]  # representatif des cases centrales
        for i,j in cases_centrales:
            cellule = tableau[i][j]
            if cellule is not None:
                if cellule[1] == self.player:
                    score += 4   # Ma pièce est bien au  centre Excellent
                elif cellule[1] == 1 - self.player:
                    score -= 4    # L'adversaire est au centre danger
            
        self.eval_cache[cle] = score
        
        return score
    
    def score_ligne(self,ligne):
        score = 0
        my_player = self.player
        adv_player = 1 - my_player

        count_me = 0
        count_adv = 0

        # si on touche le bord du plateau
        open_left_me = False
        open_left_adv = False

        for cellule in ligne:
            if  cellule is not None and cellule[1] == my_player:
                count_me += 1
                open_right_adv = False
                score -= self.score_sequence(count_adv,open_left_adv,open_right_adv)
                count_adv = 0
                open_left_adv = False
            elif cellule is not None and cellule[1] == adv_player:
                count_adv += 1
                open_right_me = False
                score += self.score_sequence(count_me,open_left_me,open_right_me)
                count_me = 0
                open_left_me = False
            else:
                open_right_me = True
                open_right_adv = True
                score += self.score_sequence(count_me,open_left_me,open_right_me)
                score -= self.score_sequence(count_adv,open_left_adv,open_right_adv)
                count_me = 0
                count_adv = 0
                open_left_me = True
                open_left_adv = True

        score += self.score_sequence(count_me,open_left_me,False)
        score -= self.score_sequence(count_adv,open_left_adv,False)

        return score
    
    def score_ligne_symbole(self,ligne,state):
        score = 0
        count_x = 0
        count_o = 0

        mon_tour = (Game.to_move(state) == self.player)
        
        signe = 1 if mon_tour else -1

        # si on touche le bord du plateau
        open_left_me = False
        open_left_adv = False

        for cellule in ligne:
            if cellule is not None and cellule[0] == 'x':
                count_x += 1
                open_right_adv = False
                score += signe * self.score_sequence_symbol(count_o,open_left_adv,open_right_adv)
                count_o = 0
                open_left_adv = False
            elif cellule is not None and cellule[0] == 'o':
                count_o += 1
                open_right_me = False
                score += signe * self.score_sequence_symbol(count_x,open_left_me,open_right_me)
                count_x = 0
                open_left_me = False
            else:
                open_right_me = True
                open_right_adv = True
                score += signe * self.score_sequence_symbol(count_x,open_left_me,open_right_me)
                score += signe * self.score_sequence_symbol(count_o,open_left_adv,open_right_adv)
                count_x = 0
                count_o = 0
                open_left_me = True
                open_left_adv =  True
        score += signe * self.score_sequence_symbol(count_x,open_left_me,False) 
        score += signe * self.score_sequence_symbol(count_o,open_left_adv,False)
        return score
    
    def score_sequence(self,n,open_left,open_right):
        if n == 0:
            return 0
        elif n >= 4:
            return 100000
        
        score_base = 0
        if n == 1:
            score_base = 1
        elif n == 2:
            score_base = 10
        elif n == 3:
            score_base = 100
        
        openings = 0
        if open_left:
            openings += 1
        if open_right:
            openings += 1
        
        if openings == 0:
            return 0
        elif openings == 1:
            return score_base
        elif openings == 2:
            return score_base * 2
       
    
    def score_sequence_symbol(self,n,open_left,open_right):
        if n == 0:
            return 0
        elif n >= 4:
            return 5000
        
        score_base = 0
        if n == 1:
            score_base = 1
        elif n == 2:
            score_base = 5
        elif n == 3:
            score_base = 30

        openings = 0
        if open_left:
            openings += 1
        if open_right:
            openings += 1

        if openings == 0:
            return 0
        elif openings == 1:
            return score_base 
        elif openings == 2:
            return score_base * 2
        """
        elif n == 1:
            return 1
        elif n == 2:
            return 5
        elif n == 3:
            return 30
        elif n >= 4:
            return 5000
        """
    