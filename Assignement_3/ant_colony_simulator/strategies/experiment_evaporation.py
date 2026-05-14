"""
Q2 — Expérience : Taux d'évaporation des phéromones
=====================================================
Fait varier le taux d'évaporation entre 0.500 et 0.999 (20 points).
Pour chaque point : 10 runs avec 70 fourmis sur l'environnement
05_square_four_food_spots (300s max, 10 000 steps max).

Lance avec :
    python3 experiment_evaporation.py
"""

import sys
import time
import math
import random
import copy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

sys.path.insert(0, '.')  # Ajouter le répertoire courant

from environment import Environment, EnvironmentBuilder
from utils import create_environment, add_ants

# ================================================================
# CONFIGURATION DE L'EXPÉRIENCE
# ================================================================

ENV_FILE         = "envs/05_square_four_food_spots.txt"   # Nom de l'environnement
N_ANTS           = 70                             # Nombre de fourmis
N_RUNS           = 10                             # Runs par taux
MAX_STEPS        = 10_000                         # Steps max par run
TIME_LIMIT       = 300                            # Secondes max par run
N_POINTS         = 20                             # Nombre de taux à tester
TAUX_MIN         = 0.500                          # Taux minimum
TAUX_MAX         = 0.999                          # Taux maximum
STRATEGY_FILE    = "strategies/smart.py"                     # Fichier de stratégie

# ================================================================
# FONCTIONS UTILITAIRES
# ================================================================

def creer_environnement():
    """Crée l'environnement de l'expérience"""
    try:
        env = create_environment(ENV_FILE, 100, 100, verbose=False)
        print(f"✅ Environnement '{ENV_FILE}' chargé")
        return env
    except Exception:
        # Si le fichier n'existe pas, créer un environnement simple équivalent
        print(f"⚠️  Fichier '{ENV_FILE}' non trouvé, utilisation de l'environnement 'simple'")
        env = create_environment("simple", 100, 100, verbose=False)
        return env


def modifier_taux_evaporation(env, taux: float):
    """Modifie le taux d'évaporation des phéromones dans l'environnement"""
    env.home_pheromones.evaporation_rate = taux
    env.food_pheromones.evaporation_rate = taux


def copier_environnement_propre(env_template) -> Environment:
    """
    Crée une copie propre de l'environnement (sans fourmis ni phéromones)
    pour chaque run.
    """
    new_env = Environment(env_template.width, env_template.height)
    
    # Copie de la grille
    for y in range(env_template.height):
        for x in range(env_template.width):
            new_env.grid[y][x] = env_template.grid[y][x]
    
    # Copie des positions de nourriture et quantités
    for pos in env_template.food_positions:
        x, y = pos
        new_env.food_positions.add(pos)
        new_env.food_amounts[y][x] = env_template.food_amounts[y][x]
    
    # Recalculer la quantité initiale de nourriture
    new_env.initial_food_amount = sum(
        new_env.food_amounts[y][x]
        for y in range(new_env.height)
        for x in range(new_env.width)
    )
    
    # Copie des positions de colonie
    for pos in env_template.colony_positions:
        new_env.colony_positions.append(pos)
        x, y = pos
        new_env.grid[y][x] = env_template.grid[y][x]
    
    return new_env


def run_simulation(env_template, taux: float, strategy_file: str, n_ants: int,
                   max_steps: int, time_limit: float) -> int:
    """
    Lance une simulation avec un taux d'évaporation donné.
    
    Retourne:
        Le nombre de steps pour atteindre l'objectif,
        ou max_steps si l'objectif n'est pas atteint.
    """
    # Créer une copie propre de l'environnement
    env = copier_environnement_propre(env_template)
    
    # Modifier le taux d'évaporation
    modifier_taux_evaporation(env, taux)
    
    # Ajouter les fourmis
    add_ants(env, "cooperative", strategy_file, n_ants, verbose=False)
    
    # Lancer la simulation
    start_time = time.time()
    step = 0
    
    while step < max_steps:
        # Vérifier le temps
        if time.time() - start_time > time_limit:
            break
        
        env.update()
        step += 1
        
        # Vérifier la condition d'arrêt
        if env.is_complete():
            return step
    
    # Objectif non atteint : retourner max_steps
    return max_steps


# ================================================================
# EXPÉRIENCE PRINCIPALE
# ================================================================

def run_experiment():
    """Lance l'expérience complète et retourne les résultats"""
    
    print("=" * 60)
    print("Q2 — EXPÉRIENCE : TAUX D'ÉVAPORATION DES PHÉROMONES")
    print("=" * 60)
    print(f"Environnement : {ENV_FILE}")
    print(f"Fourmis : {N_ANTS}")
    print(f"Points de taux : {N_POINTS} (de {TAUX_MIN} à {TAUX_MAX})")
    print(f"Runs par point : {N_RUNS}")
    print(f"Steps max : {MAX_STEPS}")
    print(f"Temps max : {TIME_LIMIT}s")
    print()
    
    # Charger l'environnement template
    env_template = creer_environnement()
    print(f"Nourriture initiale : {env_template.initial_food_amount} unités")
    print()
    
    # Générer les 20 taux régulièrement espacés
    taux_list = np.linspace(TAUX_MIN, TAUX_MAX, N_POINTS)
    
    moyennes = []
    ecarts_types = []
    
    total_runs = N_POINTS * N_RUNS
    run_done = 0
    experiment_start = time.time()
    
    for i, taux in enumerate(taux_list):
        steps_par_run = []
        
        print(f"Taux {i+1:2d}/{N_POINTS} : evaporation_rate = {taux:.4f}")
        
        for run in range(N_RUNS):
            steps = run_simulation(
                env_template, taux, STRATEGY_FILE, N_ANTS,
                MAX_STEPS, TIME_LIMIT
            )
            steps_par_run.append(steps)
            run_done += 1
            
            # Affichage du progrès
            pct = steps / MAX_STEPS * 100 if steps < MAX_STEPS else 100
            status = "✅" if steps < MAX_STEPS else "⏱️ "
            print(f"  Run {run+1:2d}/{N_RUNS} : {steps:6d} steps {status}")
        
        moyenne = np.mean(steps_par_run)
        ecart_type = np.std(steps_par_run)
        moyennes.append(moyenne)
        ecarts_types.append(ecart_type)
        
        # Temps estimé restant
        elapsed = time.time() - experiment_start
        time_per_run = elapsed / run_done
        runs_left = total_runs - run_done
        eta = time_per_run * runs_left
        
        print(f"  → Moyenne : {moyenne:.0f} steps | Écart-type : {ecart_type:.0f}")
        print(f"  → Temps restant estimé : {eta:.0f}s")
        print()
    
    total_time = time.time() - experiment_start
    print(f"✅ Expérience terminée en {total_time:.1f}s")
    
    return taux_list, np.array(moyennes), np.array(ecarts_types)


# ================================================================
# GÉNÉRATION DE LA COURBE
# ================================================================

def plot_results(taux_list, moyennes, ecarts_types, save_path="q2_evaporation.png"):
    """Génère et sauvegarde la courbe de performances"""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Courbe principale
    ax.plot(taux_list, moyennes, 'b-o', linewidth=2, markersize=6,
            label='Steps moyens', zorder=3)
    
    # Zone d'écart-type (±1σ)
    ax.fill_between(
        taux_list,
        moyennes - ecarts_types,
        moyennes + ecarts_types,
        alpha=0.25, color='blue', label='±1 écart-type'
    )
    
    # Trouver et marquer l'optimum
    idx_opt = np.argmin(moyennes)
    ax.axvline(x=taux_list[idx_opt], color='red', linestyle='--',
               linewidth=1.5, alpha=0.7, label=f'Optimum ≈ {taux_list[idx_opt]:.3f}')
    ax.scatter([taux_list[idx_opt]], [moyennes[idx_opt]],
               color='red', s=120, zorder=5)
    
    # Annotations des zones
    ax.text(0.52, moyennes.max() * 0.95,
            "Évaporation\ntrop rapide\n→ pas de pistes",
            ha='left', fontsize=9, color='darkred',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))
    
    ax.text(0.96, moyennes.max() * 0.95,
            "Évaporation\ntrop lente\n→ pistes trop vieilles",
            ha='right', fontsize=9, color='darkred',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))
    
    # Formatage
    ax.set_xlabel("Taux d'évaporation des phéromones", fontsize=12)
    ax.set_ylabel("Steps pour atteindre l'objectif", fontsize=12)
    ax.set_title(
        "Q2 — Performance en fonction du taux d'évaporation\n"
        f"(70 fourmis, {N_RUNS} runs par point, env. {ENV_FILE})",
        fontsize=13
    )
    
    ax.set_xlim(TAUX_MIN - 0.02, TAUX_MAX + 0.01)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\n📊 Courbe sauvegardée : {save_path}")
    
    return fig


# ================================================================
# SAUVEGARDE DES DONNÉES
# ================================================================

def sauvegarder_donnees(taux_list, moyennes, ecarts_types, path="q2_data.csv"):
    """Sauvegarde les données brutes en CSV"""
    with open(path, "w") as f:
        f.write("taux_evaporation,steps_moyens,ecart_type\n")
        for taux, moy, std in zip(taux_list, moyennes, ecarts_types):
            f.write(f"{taux:.4f},{moy:.2f},{std:.2f}\n")
    print(f"💾 Données sauvegardées : {path}")


# ================================================================
# POINT D'ENTRÉE
# ================================================================

if __name__ == "__main__":
    
    # Lancer l'expérience
    taux_list, moyennes, ecarts_types = run_experiment()
    
    # Afficher les résultats
    print("\n" + "=" * 60)
    print("RÉSULTATS")
    print("=" * 60)
    print(f"{'Taux':>8} | {'Moyenne':>10} | {'Écart-type':>12}")
    print("-" * 38)
    for t, m, s in zip(taux_list, moyennes, ecarts_types):
        print(f"{t:8.4f} | {m:10.0f} | {s:12.0f}")
    
    idx_opt = np.argmin(moyennes)
    print(f"\n🏆 Optimum : taux = {taux_list[idx_opt]:.4f} "
          f"({moyennes[idx_opt]:.0f} steps en moyenne)")
    
    # Générer la courbe
    plot_results(taux_list, moyennes, ecarts_types)
    
    # Sauvegarder les données
    sauvegarder_donnees(taux_list, moyennes, ecarts_types)
    
    print("\n✅ Tout est terminé ! Fichiers générés :")
    print("  - q2_evaporation.png  (la courbe)")
    print("  - q2_data.csv         (les données brutes)")
