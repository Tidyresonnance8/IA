from environment import TerrainType, Direction
from ant import AntStrategy
from common import AntPerception, AntAction
from collections import deque
import random


class SmartStrategy(AntStrategy):
    """
    Stratégie Cheater : accès illégal à l'environnement complet.

    Améliorations par rapport à smart1.py :
    - set_environment() : reçoit l'environnement global
    - Position exacte de chaque fourmi via env.ants
    - Cible optimale via env.food_positions / env.colony_positions
    - Algorithme BFS pour le chemin le plus court sur la grille complète
    - Dépôt de phéromones pour guider les fourmis non-cheaters
    """

    def __init__(self):
        self.env = None               # Référence à l'environnement global
        self.compteur_depot = {}      # Compteur de pas par fourmi (pour le dépôt)

    # ================================================================
    # ACCÈS À L'ENVIRONNEMENT GLOBAL (obligatoire pour le cheater)
    # ================================================================

    def set_environment(self, environment) -> None:
        """
        Reçoit une référence directe à l'environnement global.
        Appelé une seule fois par utils.add_ants avant la simulation.
        """
        self.env = environment

    # ================================================================
    # DÉCISION PRINCIPALE
    # ================================================================

    def decide_action(self, perception: AntPerception) -> AntAction:
        ant_id = perception.ant_id

        # Initialiser le compteur de cette fourmi
        if ant_id not in self.compteur_depot:
            self.compteur_depot[ant_id] = 0
        self.compteur_depot[ant_id] += 1

        # --- Priorité absolue : ramasser / déposer si sur la case ---
        if perception.has_food and perception.visible_cells.get((0, 0)) == TerrainType.COLONY:
            return AntAction.DROP_FOOD

        if not perception.has_food and perception.visible_cells.get((0, 0)) == TerrainType.FOOD:
            return AntAction.PICK_UP_FOOD

        # --- Dépôt de phéromones tous les 3 pas ---
        # Permet aux fourmis non-cheaters de profiter des pistes
        if self.compteur_depot[ant_id] % 3 == 0:
            if perception.has_food:
                return AntAction.DEPOSIT_FOOD_PHEROMONE
            else:
                return AntAction.DEPOSIT_HOME_PHEROMONE

        # --- Navigation optimale via BFS si env disponible ---
        if self.env is not None:
            ant = self._trouver_fourmi(ant_id)
            if ant is not None:
                cible = self._choisir_cible(ant)
                if cible is not None:
                    direction_bfs = self._bfs(int(ant.x), int(ant.y), cible[0], cible[1])
                    if direction_bfs is not None:
                        return self._direction_vers_action(perception, direction_bfs)

        # --- Fallback : navigation par perception (comme smart1) ---
        return self._fallback_perception(perception)

    # ================================================================
    # ACCÈS AUX DONNÉES GLOBALES DE L'ENVIRONNEMENT
    # ================================================================

    def _trouver_fourmi(self, ant_id):
        """
        Trouve l'objet Ant correspondant à l'ant_id dans env.ants.
        Permet de connaître la position exacte (ant.x, ant.y) dans la grille.
        """
        for ant in self.env.ants:
            if ant.id == ant_id:
                return ant
        return None

    def _choisir_cible(self, ant) -> tuple:
        """
        Sélectionne la cible optimale selon l'état de la fourmi :
        - Porte de la nourriture → colonie la plus proche (distance Manhattan)
        - Cherche de la nourriture → source de nourriture la plus proche
        """
        x, y = int(ant.x), int(ant.y)

        if ant.has_food:
            positions = self.env.colony_positions
        else:
            positions = list(self.env.food_positions)

        if not positions:
            return None

        # Distance Manhattan pour choisir la plus proche
        return min(positions, key=lambda p: abs(p[0] - x) + abs(p[1] - y))

    # ================================================================
    # ALGORITHME BFS (chemin optimal sur la grille complète)
    # ================================================================

    def _bfs(self, start_x: int, start_y: int, cible_x: int, cible_y: int):
        """
        Breadth-First Search sur la grille complète pour trouver le chemin
        le plus court (en nombre de pas) de (start_x, start_y) à (cible_x, cible_y).

        Retourne la direction (int 0-7) du premier pas optimal,
        ou None si aucun chemin n'existe.

        La cible est atteinte même si c'est une case FOOD ou COLONY
        (non walkable selon is_walkable mais accessible pour l'action).
        """
        if start_x == cible_x and start_y == cible_y:
            return None  # Déjà sur la cible

        visited = {(start_x, start_y)}
        # File : (x, y, première direction prise depuis le départ)
        queue = deque()

        for direction in range(8):
            dx, dy = Direction.get_delta(direction)
            nx, ny = start_x + dx, start_y + dy

            if (nx, ny) not in visited:
                est_cible = (nx == cible_x and ny == cible_y)
                if est_cible or self.env.is_walkable(nx, ny):
                    visited.add((nx, ny))
                    queue.append((nx, ny, direction))

        while queue:
            x, y, first_dir = queue.popleft()

            if x == cible_x and y == cible_y:
                return first_dir   # Premier pas optimal trouvé

            for direction in range(8):
                dx, dy = Direction.get_delta(direction)
                nx, ny = x + dx, y + dy

                if (nx, ny) not in visited:
                    est_cible = (nx == cible_x and ny == cible_y)
                    if est_cible or self.env.is_walkable(nx, ny):
                        visited.add((nx, ny))
                        queue.append((nx, ny, first_dir))

        return None  # Pas de chemin accessible

    # ================================================================
    # CONVERSION DIRECTION BFS → ANTACTION
    # ================================================================

    def _direction_vers_action(self, perception: AntPerception, direction_cible: int) -> AntAction:
        """
        Convertit une direction globale (int 0-7 retournée par BFS)
        en AntAction : avance si déjà aligné, tourne sinon.
        """
        direction_actuelle = perception.direction.value

        if direction_actuelle == direction_cible:
            return self._avancer_si_possible(perception)

        diff = (direction_cible - direction_actuelle) % 8
        if diff <= 4:
            return AntAction.TURN_RIGHT
        else:
            return AntAction.TURN_LEFT

    def _avancer_si_possible(self, perception: AntPerception) -> AntAction:
        """Avance seulement s'il n'y a pas de mur juste devant (garde-fou)."""
        dx, dy = Direction.get_delta(perception.direction)
        case_devant = perception.visible_cells.get((dx, dy))

        if case_devant == TerrainType.WALL:
            return AntAction.TURN_RIGHT if random.random() < 0.5 else AntAction.TURN_LEFT

        return AntAction.MOVE_FORWARD

    # ================================================================
    # FALLBACK : navigation par perception (identique à smart1.py)
    # ================================================================

    def _fallback_perception(self, perception: AntPerception) -> AntAction:
        """
        Utilisé si l'environnement n'est pas disponible ou si BFS échoue.
        Navigation basée uniquement sur AntPerception (comme smart1).
        """
        if perception.has_food:
            cible = perception.get_colony_direction()
            if cible is None:
                cible = self._renifler(perception.home_pheromone, perception)
        else:
            cible = perception.get_food_direction()
            if cible is None:
                cible = self._renifler(perception.food_pheromone, perception)

        if cible is not None:
            return self._direction_vers_safe(perception, cible)
        return self._decide_movement(perception)

    def _direction_vers_safe(self, perception: AntPerception, direction_cible: int) -> AntAction:
        """Tourne vers la cible et vérifie les obstacles avant d'avancer."""
        direction_actuelle = perception.direction.value

        if direction_actuelle == direction_cible:
            return self._avancer_si_possible(perception)

        diff = (direction_cible - direction_actuelle) % 8
        if diff <= 4:
            return AntAction.TURN_RIGHT
        else:
            return AntAction.TURN_LEFT

    def _renifler(self, dict_pheromones: dict, perception: AntPerception):
        """Trouve la direction de la phéromone la plus forte dans le champ de vision."""
        meilleur_direction = None
        max_intensite = 0.1

        for (dx, dy), intensite in dict_pheromones.items():
            if intensite > max_intensite:
                max_intensite = intensite
                meilleur_direction = perception._get_direction_from_delta(dx, dy)

        return meilleur_direction

    def _decide_movement(self, perception: AntPerception) -> AntAction:
        """Mouvement d'exploration aléatoire quand aucune cible n'est détectée."""
        dx, dy = Direction.get_delta(perception.direction)
        case_devant = perception.visible_cells.get((dx, dy))

        if case_devant == TerrainType.WALL:
            return AntAction.TURN_RIGHT if random.random() < 0.5 else AntAction.TURN_LEFT

        choix = random.random()
        if choix < 0.75:
            return AntAction.MOVE_FORWARD
        elif choix < 0.875:
            return AntAction.TURN_LEFT
        else:
            return AntAction.TURN_RIGHT