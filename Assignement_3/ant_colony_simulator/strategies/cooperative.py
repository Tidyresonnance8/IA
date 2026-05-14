from environment import TerrainType, AntPerception, Direction
from ant import AntAction, AntStrategy

import random

class CooperativeStrategy(AntStrategy):
    """
    # TODO: Insert your code here
    """

    def __init__(self):
        """Initialize the strategy with last action tracking"""
        # TODO: Insert your code here

    def decide_action(self, perception: AntPerception) -> AntAction:
        """Decide an action based on current perception"""
        action_a_faire = None

        if perception.has_food:
           
            # je cherche la colonie
            if perception.visible_cells.get((0, 0)) == TerrainType.COLONY:
                return AntAction.DROP_FOOD
            
            # Je dépose ma piste "Nourriture" derrière moi  pour guider les autres
            if random.random() < 0.2:
                return AntAction.DEPOSIT_FOOD_PHEROMONE
            else:
                # je renifle les phéromones de  "Maison"
                cible_colonie = perception.get_colony_direction()
                if cible_colonie is  None:
                    cible_colonie = self._renifler(perception.home_pheromone, perception)
                if cible_colonie is not None:
                    action_a_faire = self._direction_vers(perception.direction.value, cible_colonie)
                else:
                    action_a_faire = self._decide_movement(perception)
                
        else:
            
            # je cherche la nourriture
            if perception.visible_cells.get((0, 0)) == TerrainType.FOOD:
                return AntAction.PICK_UP_FOOD
            #Je dépose ma piste maison derrière moi pour m'assurer un retour
            if random.random() < 0.2:
                return AntAction.DEPOSIT_HOME_PHEROMONE
            else:
                cible_food = perception.get_food_direction()
                if cible_food is None:
                    cible_food = self._renifler(perception.food_pheromone, perception)
                if cible_food is not None:
                    action_a_faire = self._direction_vers(perception.direction.value, cible_food)
                else:
                    action_a_faire = self._decide_movement(perception)
                    
        return action_a_faire
        #return self._decide_movement(perception)

    def _renifler(self, dict_pheromones, perception) -> int:
        """ Trouve la direction de la phéromone la plus forte"""
        meilleur_direction = None
        max_intensite = 0.1

        for (dx, dy), intensite in dict_pheromones.items():
            if intensite > max_intensite:
                max_intensite = intensite
                meilleur_direction = perception._get_direction_from_delta(dx, dy)

        return meilleur_direction

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
        if perception.has_food:
            return self._direction_vers(perception.direction.value, Direction.NORTHWEST.value)
        else:
            return self._direction_vers(perception.direction.value, Direction.SOUTHEAST.value)


      