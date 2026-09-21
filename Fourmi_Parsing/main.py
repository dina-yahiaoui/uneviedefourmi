import glob
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

from ants import parse_fourmiliere, simuler

DOSSIER_FOURMILIERES = "fourmilieres"
DOSSIER_SORTIE = "sorties"


def afficher_etapes(etapes):
    for i, etape in enumerate(etapes, start=1):
        print(f"+++ E{i} +++")
        for ligne in etape:
            print(ligne)


def dessiner_graphe(G, nom):
    pos = nx.spring_layout(G, seed=42)
    couleurs = ["#8ecae6" if s == "Sv" else "#219ebc" if s == "Sd" else "#e9ecef" for s in G.nodes]
    nx.draw(G, pos, with_labels=True, node_color=couleurs, node_size=800)
    plt.title(nom)
    plt.savefig(os.path.join(DOSSIER_SORTIE, f"{nom}_graphe.png"))
    plt.close()


def dessiner_progression(etapes, F, nom):
    arrivees = 0
    valeurs = [0]
    for etape in etapes:
        arrivees += sum(1 for ligne in etape if ligne.endswith("Sd"))
        valeurs.append(arrivees)
    plt.plot(range(len(valeurs)), valeurs, marker="o")
    plt.xlabel("etape")
    plt.ylabel("fourmis arrivees au dortoir")
    plt.title(nom)
    plt.savefig(os.path.join(DOSSIER_SORTIE, f"{nom}_progression.png"))
    plt.close()


def traiter_fourmiliere(chemin_fichier):
    nom = os.path.splitext(os.path.basename(chemin_fichier))[0]
    F, G = parse_fourmiliere(chemin_fichier)

    print(f"\n===== {nom} (F={F}) =====")
    etapes = simuler(G, F)
    afficher_etapes(etapes)
    print(f"-> {len(etapes)} etapes necessaires pour que les {F} fourmis rejoignent le dortoir.")

    dessiner_graphe(G, nom)
    dessiner_progression(etapes, F, nom)

    return nom, len(etapes)


def main():
    os.makedirs(DOSSIER_SORTIE, exist_ok=True)

    fichiers = sys.argv[1:] or sorted(glob.glob(os.path.join(DOSSIER_FOURMILIERES, "*.txt")))
    if not fichiers:
        print(f"Aucun fichier fourmiliere trouve dans '{DOSSIER_FOURMILIERES}/'.")
        return

    resultats = [traiter_fourmiliere(chemin) for chemin in fichiers]

    print("\n===== RECAPITULATIF =====")
    for nom, nb_etapes in resultats:
        print(f"{nom:35s} -> {nb_etapes} etapes")


if __name__ == "__main__":
    main()
