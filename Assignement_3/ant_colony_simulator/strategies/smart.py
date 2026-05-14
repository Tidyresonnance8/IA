from environment import TerrainType, AntPerception, Direction
from ant import AntAction, AntStrategy

import random

class SmartStrategy(AntStrategy):
    """
    # TODO: Insert your code here
    """

    def __init__(self):
        """Initialize the strategy with last action tracking"""
        #self.memoire = [] # memoirecomme dans le non_cooperative.py
        # j'essaie cette fois avec le compas interne pour voir le plus performant
        self.x = 0
        self.y = 0
        self.memoire_fourmis = {}
        self.esquive_mur = 0
        self.direction_esquive = None # elle va nous permettre de longer le mur
       
        
    def _memoire_fourmi(self, perception : AntPerception):
        """Recupere la position memorise de la fourmi actuelle"""
        ant_id = perception.ant_id
        if ant_id not in self.memoire_fourmis:
            self.memoire_fourmis[ant_id] = {"x": 0, "y": 0, "esquive_mur": 0, "direction_esquive": None, "a_vu_mur": False,}
        return self.memoire_fourmis[ant_id]
      
    def decide_action(self, perception: AntPerception) -> AntAction:
        """Decide an action based on current perception"""

        action_a_faire = None
        ma_dir = perception.direction.value
        memoire = self._memoire_fourmi(perception)

        if TerrainType.WALL in perception.visible_cells.values():
            memoire["a_vu_mur"] = True
        
        if memoire["esquive_mur"] > 0:
            memoire["esquive_mur"] -= 1
            # je regarde d'abord si je suis coincé sur un mur
            dx, dy = Direction.get_delta(ma_dir)
            case_devant = perception.visible_cells.get((dx, dy))

            if case_devant is not None and case_devant == TerrainType.WALL:
                action_a_faire = memoire["direction_esquive"]
                # j'esquive pour les 2 prochains tours
                memoire["esquive_mur"] = 2
         
            else:
                action_a_faire = AntAction.MOVE_FORWARD
            #action_a_faire = self._decide_movement(perception)
            # si j'arrive par hasard
            if perception.has_food and perception.visible_cells.get((0, 0)) == TerrainType.COLONY:
                memoire["x"], memoire["y"] = 0, 0
                memoire["esquive_mur"] = 0 # je desactive l'esquive
                return AntAction.DROP_FOOD
            elif not perception.has_food and perception.visible_cells.get((0, 0)) == TerrainType.FOOD:
                memoire["esquive_mur"] = 0
                return AntAction.PICK_UP_FOOD
            
        else:
            if perception.has_food:

            
                if perception.visible_cells.get((0, 0)) == TerrainType.COLONY:
                    # Je vais recaler le compas interne à 0 pour chaque variable initiale pour effacer les petites erreurs de dérive
                    memoire["x"] = 0
                    memoire["y"] = 0
                    return AntAction.DROP_FOOD
                
                if random.random() < 0.2:
                    return  AntAction.DEPOSIT_FOOD_PHEROMONE 
            
                cible_colonie = perception.get_colony_direction()
                if cible_colonie is None:
                    cible_colonie = self._renifler(perception.home_pheromone, perception)
                if cible_colonie is None:
                    cible_colonie = perception._get_direction_from_delta(-memoire["x"], -memoire["y"])
                if cible_colonie is not None:
                    action_a_faire = self._direction_vers(ma_dir, cible_colonie)
                #elif len(self.memoire) > 0:
                    # Je ne vois pas la colonie, donc je suis ma mémoire en l'envers
                    #dernier_pas = self.memoire[-1]
                    #direction_retour = (dernier_pas + 4) % 8
                    #action_a_faire = self._direction_vers(ma_dir, direction_retour)
                else:
                    cible_exploration = self._direction_exploration(perception, memoire)
                    action_a_faire = self._direction_vers(ma_dir,cible_exploration)
       
            else:
                
                # Je cherche la nourriture
                if perception.visible_cells.get((0,0)) == TerrainType.FOOD:
                    return AntAction.PICK_UP_FOOD
                
                if random.random() < 0.2:
                        return AntAction.DEPOSIT_HOME_PHEROMONE
                 
        
                cible_food = perception.get_food_direction()
                if cible_food is None:
                    cible_food = self._renifler(perception.food_pheromone, perception)
                if cible_food is not None:
                    action_a_faire = self._direction_vers(ma_dir, cible_food)
                else:
                    if memoire["a_vu_mur"]:
                        action_a_faire = self._decide_movement(perception)
                    else:
                        cible_exploration = self._direction_exploration(perception, memoire)
                        action_a_faire = self._direction_vers(ma_dir, cible_exploration)

        
        if action_a_faire == AntAction.MOVE_FORWARD:
            #if not perception.has_food:
             #   self.memoire.append(ma_dir)
            #else:
             #   if len(self.memoire) > 0:
              #      self.memoire.pop()
            dx, dy = Direction.get_delta(ma_dir)

            # On regarde ce qu'il y a sur la cse juste devant nous
            case_devant = perception.visible_cells.get((dx, dy))


            if case_devant is  None or case_devant == TerrainType.WALL:
                # j'esquive pour les 3 prochains tours
                memoire["esquive_mur"] = 3
                memoire["direction_esquive"] = random.choice([AntAction.TURN_LEFT, AntAction.TURN_RIGHT])
                action_a_faire = memoire["direction_esquive"]
            else:
                memoire["x"] += dx
                memoire["y"] += dy
        
        #elif action_a_faire == AntAction.DROP_FOOD:
            #self.memoire.clear()

    
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
    
    def _direction_exploration(self, perception, memoire) -> int:
        """Donne une direction differente aux fourmis pour explorer plus vite"""
        
        directions = [
            Direction.NORTHEAST.value,
            Direction.SOUTHEAST.value,
            Direction.SOUTHWEST.value,
            Direction.NORTHWEST.value,
            Direction.EAST.value,
            Direction.SOUTHEAST.value,
            Direction.NORTHEAST.value,
            Direction.EAST.value,
        ]
        return directions[perception.ant_id % len(directions)]
    
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

        #random_direction = random.choice([AntAction.MOVE_FORWARD, AntAction.TURN_LEFT, AntAction.TURN_RIGHT])
        #return random_direction  # Random movement for now, replace with actual logic