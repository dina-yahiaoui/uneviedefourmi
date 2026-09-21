import re
from collections import deque

import networkx as nx

# Parsing

# On regarde le fichier de fourmilière et on construit le graphe correspondant.
def parse_fourmiliere(chemin):
    G = nx.Graph()
    F = 0
    for ligne in open(chemin, encoding="utf-8"):
        ligne = ligne.strip()
        if not ligne:
            continue

# ligne du type "f=50" pour le nombre de fourmis
        if re.match(r"^[fF]\s*=", ligne):
            F = int(ligne.split("=")[1])

# ligne du type "Sv - S1" c'est le tunnel entre deux salles
        elif "-" in ligne:
            a, b = (s.strip() for s in ligne.split("-"))
            G.add_edge(a, b)

# ligne du type "S3 { 5 }" ou "S3" c'est pour une declaration de salle
        else:
            m = re.match(r"(\S+)\s*(?:\{\s*(\d+)\s*\})?", ligne)
            G.add_node(m.group(1), capacite=int(m.group(2) or 1))

# Une salle vue uniquement via un tunnel n'a pas encore de capacite -> 1 par defaut
    for salle in G:
        G.nodes[salle].setdefault("capacite", 1)

# Le vestibule et le dortoir peuvent contenir toutes les fourmis a la fois
    for salle in ("Sv", "Sd"):
        if salle in G:
            G.nodes[salle]["capacite"] = F

    return F, G


def bfs(G, depart):
    distances = {depart: 0}
    queue = deque([depart])
    while queue:
        salle = queue.popleft()
        for voisin in G.neighbors(salle):
            if voisin not in distances:
                distances[voisin] = distances[salle] + 1
                queue.append(voisin)
    return distances


def simuler(G, F, depart="Sv", arrivee="Sd"):
    capacite = nx.get_node_attributes(G, "capacite")
    distance = bfs(G, arrivee)

    pos = {f: depart for f in range(F)}
    etapes = []

    while any(salle != arrivee for salle in pos.values()):
        occupation = {salle: 0 for salle in G.nodes}
        for salle in pos.values():
            occupation[salle] += 1

        etape = []
        for f in sorted(pos, key=lambda f: distance[pos[f]]):
            salle = pos[f]
            if salle == arrivee:
                continue
            for voisin in sorted(G.neighbors(salle), key=lambda v: distance[v]):
                place_libre = voisin == arrivee or occupation[voisin] < capacite[voisin]
                if distance[voisin] < distance[salle] and place_libre:
                    occupation[salle] -= 1
                    occupation[voisin] += 1
                    pos[f] = voisin
                    etape.append(f"f{f + 1} - {salle} - {voisin}")
                    break

        etapes.append(etape)

    return etapes
