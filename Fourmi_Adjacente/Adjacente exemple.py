
# Ce .py est uniquement pour le fichier .txt de la fourmiliere un ( ceci est en guise d'exemple bonus pour la soutenance )


from collections import deque
import networkx as nx

def charger_fourmiliere():
    # 1. Définissez le nombre de fourmis pour ce graphe
    F = 5
    
    # 2. Créez le graphe
    G = nx.Graph()
    
    # 3. Déclarez les tunnels (arêtes)
    liaisons = [
        ("Sv", "S1"),
        ("S1", "S2"),
        ("S2", "Sd")
    ]
    G.add_edges_from(liaisons)
    
    # Capacités par défaut des salles (1 pour les salles normales)
    for salle in G:
        G.nodes[salle]["capacite"] = 1
        
    # Le vestibule (Sv) et le dortoir (Sd) peuvent contenir toutes les fourmis à la fois
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


# Exécution de la simulation
if __name__ == "__main__":
    F, G = charger_fourmiliere()
    resultats = simuler(G, F)
    
    print(f"Nombre de fourmis : {F}")
    print("Lancement de la simulation :")
    for i, etape in enumerate(resultats, 1):
        print(f"Étape {i} : {etape}")