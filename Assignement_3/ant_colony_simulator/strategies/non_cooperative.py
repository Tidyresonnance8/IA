from environment import TerrainType, AntPerception, Direction
from ant import AntAction, AntStrategy

import random


class NonCooperativeStrategy(AntStrategy):
    """
    # TODO: Insert your code here
    """

    def __init__(self):
        """Initialize the strategy with last action tracking"""
        #self.x = 0
        #self.y = 0
        self.memoire_fourmis = {}
        
    def _memoire_fourmi(self, perception :  AntPerception):
        """Recupere la position memorise de la fourmi actuelle"""
        ant_id = perception.ant_id
        if ant_id not in self.memoire_fourmis:
            self.memoire_fourmis[ant_id]  =  {"x": 0, "y": 0}
        return self.memoire_fourmis[ant_id]

    def decide_action(self, perception: AntPerception) -> AntAction:
        """Decide an action based on current perception"""
        action_a_faire = None
        memoire = self._memoire_fourmi(perception)
        ma_dir = perception.direction.value  # On récupère la valeur entière entre 0 à 7

        if perception.has_food:
            # Je cherche la colonie
            if perception.visible_cells.get((0, 0)) == TerrainType.COLONY:
                    action_a_faire = AntAction.DROP_FOOD
            else:

                direction_colonie = perception.get_colony_direction()

                if direction_colonie is not None:
                    # I je suis à la colonie
                    action_a_faire = self._direction_vers(ma_dir, direction_colonie)
               
                else:
                    direction_retour = perception._get_direction_from_delta(-memoire["x"], -memoire["y"])
                    
                    action_a_faire = self._direction_vers(ma_dir, direction_retour)
                    
                # j'essaie de m'orienter vers la colonie
                #cible_colonie = perception.get_colony_direction()
                #if cible_colonie is not None:
                    #return self._direction_vers(perception.direction.value, cible_colonie)
                
            # je me demande maintenant si j'ai de la mémoire
                
        
        else:
            # Je cherche la nourriture
            if perception.visible_cells.get((0,0)) == TerrainType.FOOD:
                action_a_faire = AntAction.PICK_UP_FOOD
            else:
                direction_food = perception.get_food_direction()
                if direction_food is not None:
                    # si je suis à la nourriture
                    action_a_faire = self._direction_vers(ma_dir, direction_food)
                else:
                    action_a_faire = self._direction_vers(ma_dir, Direction.SOUTHEAST.value)
                
                # j'essaie de  m'orienter vers la nourriture si je la vois de loin
                #cible_food = perception.get_food_direction()
                #if cible_food is not None:
                     #return self._direction_vers(perception.direction.value, cible_food)

        if action_a_faire == AntAction.MOVE_FORWARD:
           
            dx, dy = Direction.get_delta(ma_dir)

            # On regarde ce qu'il y a sur la cse juste devant nous
            case_devant = perception.visible_cells.get((dx, dy))

            if case_devant is not None and case_devant != TerrainType.WALL:
                memoire["x"] += dx
                memoire["y"] += dy
           
            else:
                action_a_faire = random.choice([AntAction.TURN_LEFT, AntAction.TURN_RIGHT])
        
       
        
        elif action_a_faire == AntAction.DROP_FOOD:
            memoire["x"] = 0
            memoire["y"] = 0

    
        return action_a_faire
        
    
    def _direction_vers(self, direction_actuelle, direction_cible) -> AntAction:
        """
        décide s'il faut avancer ou tourner pour atteindre une cible
        """
        if direction_actuelle == direction_cible:
            return AntAction.MOVE_FORWARD
        
        # sinon je calcule le chemin le plus court pour tourner
        diff = (direction_cible - direction_actuelle) % 8
        if diff <= 4:
            return AntAction.TURN_RIGHT
        else:
            return AntAction.TURN_LEFT

    def _decide_movement(self, perception: AntPerception) -> AntAction:
        """Decide which direction to move based on current state"""
        choix = random.random()
        if choix < 0.80:
            return AntAction.MOVE_FORWARD
        elif choix < 0.90:
            return AntAction.TURN_LEFT
        else:
            return AntAction.TURN_RIGHT

        