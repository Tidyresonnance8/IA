"""
Q3 — Cheater Sweep
==================
Génère les 3 graphiques en fonction du pourcentage de cheaters :
  Figure 4 : Steps nécessaires pour atteindre l'objectif
  Figure 5 : Temps d'exécution réel (secondes)
  Figure 6 : Throughput (steps/seconde)

Colonie mixte : cheaters (cheater.py) + non-cheaters (smart.py)
Environnement : 05_square_four_food_spots
10 runs par point, pas de 10%

Lance avec :
    python3 cheater_sweep.py
"""

import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

sys.path.insert(0, '.')

from environment import Environment
from utils import create_environment, add_ants

# ================================================================
# CONFIGURATION
# ================================================================

ENV_FILE      = "envs/05_square_four_food_spots.txt"
N_ANTS        = 70
N_RUNS        = 10
MAX_STEPS     = 10_000
TIME_LIMIT    = 300
SMART_FILE    = "strategies/smart.py"
CHEATER_FILE  = "strategies/cheater.py"
POURCENTAGES  = list(range(0, 101, 10))   # 0%, 10%, ..., 100%

# ================================================================
# COPIE PROPRE DE L'ENVIRONNEMENT
# ================================================================

def copier_environnement(env_template) -> Environment:
    """Crée une copie propre (sans fourmis ni phéromones) pour chaque run."""
    new_env = Environment(env_template.width, env_template.height)

    for y in range(env_template.height):
        for x in range(env_template.width):
            new_env.grid[y][x] = env_template.grid[y][x]

    for pos in env_template.food_positions:
        x, y = pos
        new_env.food_positions.add(pos)
        new_env.food_amounts[y][x] = env_template.food_amounts[y][x]

    new_env.initial_food_amount = sum(
        new_env.food_amounts[y][x]
        for y in range(new_env.height)
        for x in range(new_env.width)
    )

    for pos in env_template.colony_positions:
        new_env.colony_positions.append(pos)
        x, y = pos
        new_env.grid[y][x] = env_template.grid[y][x]

    return new_env

# ================================================================
# UN SEUL RUN
# ================================================================

def run_simulation(env_template, pct_cheaters: float) -> dict:
    """
    Lance une simulation avec une proportion donnée de cheaters.

    Retourne un dict avec :
        steps      : steps pour atteindre l'objectif (ou MAX_STEPS)
        temps      : temps réel en secondes
        throughput : steps / temps
        success    : True si objectif atteint
    """
    env = copier_environnement(env_template)

    n_cheaters = round(N_ANTS * pct_cheaters / 100)
    n_smart    = N_ANTS - n_cheaters

    # Ajouter les fourmis non-cheaters (smart.py)
    if n_smart > 0:
        add_ants(env, "cooperative", SMART_FILE, n_smart, verbose=False)

    # Ajouter les fourmis cheaters (cheater.py)
    if n_cheaters > 0:
        add_ants(env, "cooperative", CHEATER_FILE, n_cheaters, verbose=False)

    # Lancer la simulation
    start = time.perf_counter()
    step  = 0

    while step < MAX_STEPS:
        if time.perf_counter() - start > TIME_LIMIT:
            break
        env.update()
        step += 1
        if env.is_complete():
            break

    elapsed = time.perf_counter() - start
    success = env.is_complete()
    throughput = step / elapsed if elapsed > 0 else 0

    return {
        "steps":      step,
        "temps":      elapsed,
        "throughput": throughput,
        "success":    success,
    }

# ================================================================
# EXPÉRIENCE COMPLÈTE
# ================================================================

def run_sweep():
    """Lance le sweep complet et retourne les résultats."""

    print("=" * 60)
    print("Q3 — CHEATER SWEEP")
    print("=" * 60)
    print(f"Environnement : {ENV_FILE}")
    print(f"Fourmis totales : {N_ANTS}")
    print(f"Pourcentages : {POURCENTAGES}")
    print(f"Runs par point : {N_RUNS}")
    print()

    env_template = create_environment(ENV_FILE, 100, 100, verbose=False)
    print(f"✅ Environnement chargé ({env_template.initial_food_amount} unités de nourriture)")
    print()

    resultats = {pct: {"steps": [], "temps": [], "throughput": []}
                 for pct in POURCENTAGES}

    total = len(POURCENTAGES) * N_RUNS
    done  = 0
    t0    = time.time()

    for pct in POURCENTAGES:
        n_ch = round(N_ANTS * pct / 100)
        n_sm = N_ANTS - n_ch
        print(f"Cheaters : {pct:3d}%  ({n_ch} cheaters + {n_sm} smart)")

        for run in range(N_RUNS):
            r = run_simulation(env_template, pct)
            resultats[pct]["steps"].append(r["steps"])
            resultats[pct]["temps"].append(r["temps"])
            resultats[pct]["throughput"].append(r["throughput"])
            done += 1

            status = "✅" if r["success"] else "⏱️ "
            eta = (time.time() - t0) / done * (total - done)
            print(f"  Run {run+1:2d}/{N_RUNS} : {r['steps']:6d} steps | "
                  f"{r['temps']:6.2f}s | {r['throughput']:7.1f} s/s {status}  "
                  f"(ETA {eta:.0f}s)")

        moy_s = np.mean(resultats[pct]["steps"])
        moy_t = np.mean(resultats[pct]["temps"])
        moy_th = np.mean(resultats[pct]["throughput"])
        print(f"  → moy steps={moy_s:.0f}  temps={moy_t:.2f}s  throughput={moy_th:.1f}\n")

    return resultats

# ================================================================
# GÉNÉRATION DES 3 GRAPHIQUES
# ================================================================

def plot_all(resultats):
    """Génère et sauvegarde les 3 figures."""

    pcts  = POURCENTAGES
    moy_s  = [np.mean(resultats[p]["steps"])      for p in pcts]
    std_s  = [np.std(resultats[p]["steps"])       for p in pcts]
    moy_t  = [np.mean(resultats[p]["temps"])      for p in pcts]
    std_t  = [np.std(resultats[p]["temps"])       for p in pcts]
    moy_th = [np.mean(resultats[p]["throughput"]) for p in pcts]
    std_th = [np.std(resultats[p]["throughput"])  for p in pcts]

    # Optimum steps
    idx_s  = int(np.argmin(moy_s))
    # Optimum temps
    idx_t  = int(np.argmin(moy_t))
    # Optimum throughput
    idx_th = int(np.argmax(moy_th))

    x = np.array(pcts)

    # ---- Figure 4 : Steps ----------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(x, moy_s, 'b-o', linewidth=2, markersize=6, label='Steps moyens')
    ax.fill_between(x, np.array(moy_s)-np.array(std_s),
                       np.array(moy_s)+np.array(std_s),
                    alpha=0.25, color='blue', label='±1 écart-type')
    ax.axvline(x[idx_s], color='red', linestyle='--', linewidth=1.5,
               label=f'Optimum : {x[idx_s]}%')
    ax.scatter([x[idx_s]], [moy_s[idx_s]], color='red', s=120, zorder=5)
    ax.set_xlabel("Pourcentage de cheaters (%)", fontsize=12)
    ax.set_ylabel("Steps pour atteindre l'objectif", fontsize=12)
    ax.set_title(
        "Figure 4 — Steps nécessaires en fonction du % de cheaters\n"
        f"70 fourmis, 10 runs par point, env. 05_square_four_food_spots",
        fontsize=12)
    ax.set_xticks(x)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("q3_steps.png", dpi=150, bbox_inches='tight')
    print("📊 Sauvegardé : q3_steps.png")
    plt.close()

    # ---- Figure 5 : Temps ----------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(x, moy_t, 'g-o', linewidth=2, markersize=6, label='Temps moyen (s)')
    ax.fill_between(x, np.array(moy_t)-np.array(std_t),
                       np.array(moy_t)+np.array(std_t),
                    alpha=0.25, color='green', label='±1 écart-type')
    ax.axvline(x[idx_t], color='red', linestyle='--', linewidth=1.5,
               label=f'Optimum : {x[idx_t]}%')
    ax.scatter([x[idx_t]], [moy_t[idx_t]], color='red', s=120, zorder=5)
    ax.set_xlabel("Pourcentage de cheaters (%)", fontsize=12)
    ax.set_ylabel("Temps d'exécution réel (s)", fontsize=12)
    ax.set_title(
        "Figure 5 — Temps d'exécution en fonction du % de cheaters\n"
        f"70 fourmis, 10 runs par point, env. 05_square_four_food_spots",
        fontsize=12)
    ax.set_xticks(x)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("q3_temps.png", dpi=150, bbox_inches='tight')
    print("📊 Sauvegardé : q3_temps.png")
    plt.close()

    # ---- Figure 6 : Throughput -----------------------------------
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(x, moy_th, 'r-o', linewidth=2, markersize=6, label='Throughput moyen (steps/s)')
    ax.fill_between(x, np.array(moy_th)-np.array(std_th),
                       np.array(moy_th)+np.array(std_th),
                    alpha=0.25, color='red', label='±1 écart-type')
    ax.axvline(x[idx_th], color='blue', linestyle='--', linewidth=1.5,
               label=f'Optimum : {x[idx_th]}%')
    ax.scatter([x[idx_th]], [moy_th[idx_th]], color='blue', s=120, zorder=5)
    ax.set_xlabel("Pourcentage de cheaters (%)", fontsize=12)
    ax.set_ylabel("Throughput (steps/seconde)", fontsize=12)
    ax.set_title(
        "Figure 6 — Throughput en fonction du % de cheaters\n"
        f"70 fourmis, 10 runs par point, env. 05_square_four_food_spots",
        fontsize=12)
    ax.set_xticks(x)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("q3_throughput.png", dpi=150, bbox_inches='tight')
    print("📊 Sauvegardé : q3_throughput.png")
    plt.close()

    # ---- Tableau récapitulatif -----------------------------------
    print("\n" + "=" * 70)
    print(f"{'%':>5} | {'Steps moy':>10} | {'Steps σ':>8} | "
          f"{'Temps moy':>10} | {'Temps σ':>8} | {'Throughput':>12}")
    print("-" * 70)
    for i, p in enumerate(pcts):
        print(f"{p:5d} | {moy_s[i]:10.0f} | {std_s[i]:8.0f} | "
              f"{moy_t[i]:10.2f} | {std_t[i]:8.2f} | {moy_th[i]:12.1f}")

    print(f"\n🏆 Optimum steps      : {x[idx_s]}%  ({moy_s[idx_s]:.0f} steps)")
    print(f"🏆 Optimum temps      : {x[idx_t]}%  ({moy_t[idx_t]:.2f}s)")
    print(f"🏆 Optimum throughput : {x[idx_th]}%  ({moy_th[idx_th]:.1f} steps/s)")

# ================================================================
# SAUVEGARDE CSV
# ================================================================

def sauvegarder_csv(resultats):
    with open("q3_data.csv", "w") as f:
        f.write("pct_cheaters,steps_moy,steps_std,temps_moy,temps_std,throughput_moy,throughput_std\n")
        for p in POURCENTAGES:
            f.write(f"{p},"
                    f"{np.mean(resultats[p]['steps']):.2f},{np.std(resultats[p]['steps']):.2f},"
                    f"{np.mean(resultats[p]['temps']):.4f},{np.std(resultats[p]['temps']):.4f},"
                    f"{np.mean(resultats[p]['throughput']):.2f},{np.std(resultats[p]['throughput']):.2f}\n")
    print("💾 Données sauvegardées : q3_data.csv")

# ================================================================
# MAIN
# ================================================================

if __name__ == "__main__":
    resultats = run_sweep()
    plot_all(resultats)
    sauvegarder_csv(resultats)

    print("\n✅ Tout est terminé ! Fichiers générés :")
    print("  - q3_steps.png")
    print("  - q3_temps.png")
    print("  - q3_throughput.png")
    print("  - q3_data.csv")
