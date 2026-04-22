import matplotlib.pyplot as plt
import os
import shutil
from manager import Manager

def analyser_log_complet(fichier_log, time_limit):
    """Extrait la longueur de la partie et le temps de réflexion de chaque joueur par coup."""
    if not os.path.exists(fichier_log):
        return 0, [], []

    temps_p0 = []
    temps_p1 = []
    last_t_p0 = time_limit
    last_t_p1 = time_limit

    with open(fichier_log, 'r') as f:
        lignes = [l for l in f.readlines() if l.strip().startswith('(')]
        longueur = len(lignes)
        for i, ligne in enumerate(lignes):
            try:
                reste = float(ligne.rsplit(', ', 1)[1].strip())
                if i % 2 == 0: 
                    temps_pris = max(0, last_t_p0 - reste)
                    temps_p0.append(temps_pris)
                    last_t_p0 = reste
                else: 
                    temps_pris = max(0, last_t_p1 - reste)
                    temps_p1.append(temps_pris)
                    last_t_p1 = reste
            except:
                pass
    return longueur, temps_p0, temps_p1

def moyenne_profils(profils):
    """Calcule la moyenne temporelle pour chaque tour joué."""
    if not profils: return []
    max_len = max(len(p) for p in profils)
    moyennes = []
    for i in range(max_len):
        valeurs = [p[i] for p in profils if i < len(p)]
        moyennes.append(sum(valeurs) / len(valeurs))
    return moyennes

def run_expert_benchmark():
    # --- PARAMÈTRES DU TEST ---
    time_limits = [10, 30, 60, 120, 200, 300] 
    n_games_per_side = 5
    
    agent_me = "my_agent.py"
    agent_opp = "MCST_optimal.py" # <--- Change ça pour "MCST_simon.py" ou "alpha_beta_baseline.py"
    
    # --- SÉCURITÉ ANTI-FANTÔMES ---
    nom_adversaire = agent_opp.replace('.py', '')
    dossier_logs = f"logs_vs_{nom_adversaire}"
    
    # Si le dossier existe déjà, on le vide complètement pour repartir à zéro !
    if os.path.exists(dossier_logs):
        shutil.rmtree(dossier_logs)
    os.makedirs(dossier_logs)

    stats = {
        "times": time_limits,
        "win_rate": [], "opp_win_rate": [], "draw_rate": [], "avg_length": []
    }

    profils_temps_me = []
    profils_temps_opp = []
    temps_max_test = time_limits[-1] 

    print(f"=== DÉBUT DU BENCHMARK : {agent_me} VS {agent_opp} ===")
    print(f"Logs isolés dans le dossier : {dossier_logs}/\n")

    for t in time_limits:
        print(f"--- ÉVALUATION T = {t}s ---")
        wins, opp_wins, draws, total_len = 0, 0, 0, 0
        total_games = n_games_per_side * 2

        for session in ["Domicile", "Exterieur"]:
            agents = [agent_me, agent_opp] if session == "Domicile" else [agent_opp, agent_me]
            mgr = Manager(agent_files=agents, time_limit=t)
            
            for i in range(n_games_per_side):
                nom_log = f"{dossier_logs}/log_T{t}_{session}_{i+1}.txt"
                res = mgr.play(path_to_file=nom_log)
                
                if session == "Domicile":
                    if res == (1, -1): wins += 1
                    elif res == (-1, 1): opp_wins += 1
                else:
                    if res == (-1, 1): wins += 1
                    elif res == (1, -1): opp_wins += 1
                
                if res == (0, 0): draws += 1
                
                longueur, t_p0, t_p1 = analyser_log_complet(nom_log, t)
                total_len += longueur

                if t == temps_max_test:
                    if session == "Domicile":
                        profils_temps_me.append(t_p0)
                        profils_temps_opp.append(t_p1)
                    else:
                        profils_temps_me.append(t_p1)
                        profils_temps_opp.append(t_p0)

        stats["win_rate"].append((wins / total_games) * 100)
        stats["opp_win_rate"].append((opp_wins / total_games) * 100)
        stats["draw_rate"].append((draws / total_games) * 100)
        stats["avg_length"].append(total_len / total_games)

    # --- GÉNÉRATION DE LA GRANDE FIGURE ---
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))

    ax1.plot(time_limits, stats["win_rate"], marker='o', color='#e91e63', linewidth=2, label="Mon Agent")
    ax1.plot(time_limits, stats["opp_win_rate"], marker='s', color='#333333', linewidth=2, label=f"{nom_adversaire}")
    ax1.plot(time_limits, stats["draw_rate"], marker='x', color='gray', linestyle='--', label="Nuls")
    ax1.set_title("Efficacité et Nuls")
    ax1.set_xlabel("Temps limite (s)")
    ax1.set_ylabel("Pourcentage (%)")
    ax1.set_ylim(-5, 105)
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.bar([str(t) for t in time_limits], stats["avg_length"], color='#3f51b5', alpha=0.7)
    ax2.set_title("Longueur moyenne des parties")
    ax2.set_xlabel("Temps limite (s)")
    ax2.set_ylabel("Nombre de coups total")
    ax2.grid(axis='y', alpha=0.3)

    avg_t_me = moyenne_profils(profils_temps_me)
    avg_t_opp = moyenne_profils(profils_temps_opp)
    
    ax3.plot(range(1, len(avg_t_me) + 1), avg_t_me, marker='o', color='#e91e63', label="Mon Agent")
    ax3.plot(range(1, len(avg_t_opp) + 1), avg_t_opp, marker='s', color='#333333', label=f"{nom_adversaire}")
    ax3.set_title(f"Profil de Complexité (Temps passé par coup, T={temps_max_test}s)")
    ax3.set_xlabel("Numéro du tour")
    ax3.set_ylabel("Temps de réflexion (Secondes)")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    
    # Nom de l'image dynamique !
    nom_image = f"benchmark_resultats_{nom_adversaire}.png"
    plt.savefig(nom_image, dpi=300)
    print(f"\nMAGNIFIQUE ! L'image a été sauvegardée sous le nom : {nom_image} !")
    plt.show()

if __name__ == "__main__":
    run_expert_benchmark()