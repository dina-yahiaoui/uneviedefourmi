import re
from collections import deque

import networkx as nx

# Parsing

# We look at the anthill file and build the corresponding graph.
def parse_anthill(path):
    G = nx.Graph()
    F = 0
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue

        # Line of type "f=50" for the number of ants
        if re.match(r"^[fF]\s*=", line):
            F = int(line.split("=")[1])

        # Line of type "Sv - S1" which is the tunnel between two rooms
        elif "-" in line:
            a, b = (s.strip() for s in line.split("-"))
            G.add_edge(a, b)

        # Line of type "S3 { 5 }" or "S3" which is a room declaration
        else:
            m = re.match(r"(\S+)\s*(?:\{\s*(\d+)\s*\})?", line)
            G.add_node(m.group(1), capacity=int(m.group(2) or 1))

    # A room seen only via a tunnel does not have a capacity yet -> 1 by default
    for room in G:
        G.nodes[room].setdefault("capacity", 1)

    # The vestibule and the dorm can hold all the ants at once
    for room in ("Sv", "Sd"):
        if room in G:
            G.nodes[room]["capacity"] = F

    return F, G



#________________
#  AKRAM HOW TO  
#________________


# Breadth-first search to compute the shortest distance from the end room to all other rooms
def bfs(G, start):
    distances = {start: 0}
    queue = deque([start])
    while queue:
        room = queue.popleft()
        for neighbor in G.neighbors(room):
            if neighbor not in distances:
                distances[neighbor] = distances[room] + 1
                queue.append(neighbor)
    return distances







# Simulation of ants moving through the anthill towards the destination
def simulate(G, F, start="Sv", end="Sd"):
    capacity = nx.get_node_attributes(G, "capacity")
    distance = bfs(G, end)

    pos = {f: start for f in range(F)}
    steps = []

    # Continue moving ants until all of them reach the end room
    while any(room != end for room in pos.values()):
        occupancy = {room: 0 for room in G.nodes}
        for room in pos.values():
            occupancy[room] += 1

        step = []
        # Prioritize ants closest to the end room for movement
        for f in sorted(pos, key=lambda f: distance[pos[f]]):
            room = pos[f]
            if room == end:
                continue
            # Check neighboring rooms and move to the one that brings the ant closer to the end and has available capacity
            for neighbor in sorted(G.neighbors(room), key=lambda v: distance[v]):
                free_space = neighbor == end or occupancy[neighbor] < capacity[neighbor]
                if distance[neighbor] < distance[room] and free_space:
                    occupancy[room] -= 1
                    occupancy[neighbor] += 1
                    pos[f] = neighbor
                    step.append(f"f{f + 1} - {room} - {neighbor}")
                    break

        steps.append(step)

    return steps