# uneviedefourmi

# uneviedefourmi

Projet algorithmique — La Plateforme (B3 IA).
Faire rejoindre le dortoir à toutes les fourmis d'une fourmilière, en un minimum d'étapes.

## Problématique

Une fourmilière est modélisée comme un **graphe** : des salles (nœuds) reliées par des tunnels (arêtes).
Deux salles particulières, le **vestibule** (`Sv`) et le **dortoir** (`Sd`), ont une capacité illimitée.
Toutes les autres salles ne peuvent accueillir qu'un nombre limité de fourmis simultanément (1 par défaut, ou plus si précisé).

Chaque fourmi part du vestibule et doit rejoindre le dortoir. À chaque étape, elle peut :
- rester dans sa salle actuelle,
- ou se déplacer vers une salle adjacente, **si celle-ci est libre** (ou en train de se libérer).

**Objectif :** faire arriver l'ensemble des fourmis au dortoir en **le moins d'étapes possible**.

Le vrai défi n'est pas de trouver le chemin le plus court (un simple BFS suffit pour ça), mais de **synchroniser le déplacement de plusieurs fourmis en parallèle** sans qu'elles se bloquent mutuellement, tout en exploitant les chemins parallèles quand ils existent.

## Solution apportée

Le projet est découpé en deux fichiers :

- **`ants.py`** : la modélisation et l'algorithme
  - `Room` : une salle (nom, capacité, salles voisines)
  - `Ant` : une fourmi (identifiant, salle actuelle)
  - `AntHill` : le graphe complet, avec :
    - `from_file(path)` : parse un fichier de définition de fourmilière (`f=5`, `S1`, `S4 { 2 }`, `Sv - S1`)
    - `distances_to_dormitory()` : un **BFS** partant du dortoir, qui calcule la distance de chaque salle jusqu'à l'arrivée
    - `solve()` / `solve_with_history()` : l'algorithme de résolution

- **`main.py`** : charge chaque fourmilière du dossier `fourmilieres/`, résout, affiche les étapes dans le terminal, et génère les visualisations (`output_images/`).

### L'algorithme de résolution

Approche **gloutonne**, en boucle jusqu'à ce que toutes les fourmis soient au dortoir :

1. À chaque étape, on ne considère que les fourmis pas encore arrivées.
2. On les traite **par ordre de priorité** : les plus proches du dortoir d'abord (distance BFS croissante).
3. Pour chaque fourmi, on cherche la salle voisine qui la rapproche le plus du dortoir et qui est libre à cet instant.
4. Si elle en trouve une, elle avance et on note le mouvement (`f1 - Sv - S1`) ; sinon elle attend.

**Pourquoi cet ordre de priorité ?** Une fourmi proche du dortoir qui avance libère immédiatement de la place pour la fourmi juste derrière elle, dans la **même étape**. Traiter les fourmis dans cet ordre permet cette réaction en chaîne sans code supplémentaire : on met simplement à jour l'occupation des salles au fur et à mesure qu'on traite chaque fourmi.

Cette stratégie donne des résultats corrects et cohérents sur tous les cas testés, y compris des cas particuliers comme `fourmiliere_deux` (un tunnel direct `Sv-Sd`, résolu en 1 seule étape). Elle n'est cependant pas *prouvée* optimale dans l'absolu sur des graphes très ramifiés avec de nombreux chemins concurrents de longueurs différentes — une piste d'amélioration serait de comparer plusieurs répartitions possibles entre les chemins plutôt qu'une seule décision gloutonne par salle.

## Utilisation

```bash
pip install networkx matplotlib imageio numpy
python main.py
```

Le dossier `fourmilieres/` doit contenir les fichiers `.txt` de définition (format `f=N`, salles, tunnels). Pour chacun, le script génère dans `output_images/` :
- `{nom}_structure.png` : le graphe de la fourmilière
- `{nom}_animation.gif` : l'animation du déplacement des fourmis, étape par étape

## Vulgarisation

Imaginez une fourmilière comme un immeuble avec un hall d'entrée au rez-de-chaussée et un dortoir tout en haut, reliés par un réseau de couloirs étroits où une seule fourmi peut passer à la fois. À la tombée de la nuit, toutes les fourmis doivent monter se coucher, le plus vite possible. Plutôt que de foncer sans réfléchir et de se retrouver coincées les unes derrière les autres, les fourmis les plus proches du dortoir montent en premier : en avançant, elles libèrent aussitôt la place pour celles qui les suivent, comme une vague qui remonte le couloir sans jamais s'arrêter inutilement. Quand plusieurs couloirs mènent au dortoir, les fourmis se répartissent naturellement entre eux pour avancer toutes en même temps. Résultat : toute la colonie rejoint le dortoir dans le temps le plus court possible, sans embouteillage.

## Conclusion

Ce projet a permis de manipuler un problème d'algorithmique de graphes concret : modéliser une structure réelle sous forme de graphe, utiliser un BFS pour calculer des distances, puis construire un algorithme d'ordonnancement multi-agents (plusieurs fourmis se déplaçant simultanément sous contrainte de capacité). L'algorithme glouton priorisant la proximité au dortoir s'est révélé simple à implémenter et efficace sur l'ensemble des fourmilières testées, tout en révélant les limites d'une approche purement locale face à des graphes plus complexes à chemins multiples.