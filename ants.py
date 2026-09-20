"""
ants.py
Step 1: modeling the anthill as a graph.
Step 2: BFS to compute each room's distance to the dormitory.
Step 3: resolution algorithm (move every ant to the dormitory in the
minimum number of steps).

An AntHill is a set of Rooms connected by tunnels (a tunnel is just
represented as an adjacency relation between two rooms — no need
for a separate Tunnel class, a neighbor list is enough).
"""

import math
from collections import deque

import networkx as nx


class Room:
    """A room in the anthill.

    - name : room identifier ("Sv", "Sd", "S1", "S2", ...)
    - capacity : how many ants it can hold at once
      (1 by default, unlimited for the entrance and the dormitory)
    - neighbors : list of Rooms connected to this one by a tunnel
    """

    def __init__(self, name: str, capacity: int = 1):
        self.name = name
        self.capacity = capacity
        self.neighbors: list["Room"] = []

    def connect(self, other: "Room") -> None:
        """Creates a bidirectional tunnel between self and other."""
        if other not in self.neighbors:
            self.neighbors.append(other)
        if self not in other.neighbors:
            other.neighbors.append(self)

    def __repr__(self) -> str:
        return f"Room({self.name})"


class Ant:
    """A single ant. Just keeps track of its id and its current room."""

    def __init__(self, ant_id: int, current_room: Room):
        self.id = ant_id
        self.current_room = current_room

    def __repr__(self) -> str:
        return f"Ant(f{self.id}, at {self.current_room.name})"


class AntHill:
    """The full graph: all rooms + the number of ants F."""

    def __init__(self, nb_ants: int):
        self.nb_ants = nb_ants
        self.rooms: dict[str, Room] = {}

        # The entrance and the dormitory have unlimited capacity
        self.entrance = self.add_room("Sv", capacity=math.inf)
        self.dormitory = self.add_room("Sd", capacity=math.inf)

    def add_room(self, name: str, capacity: int = 1) -> Room:
        """Adds a room if it doesn't exist yet, returns it otherwise."""
        if name not in self.rooms:
            self.rooms[name] = Room(name, capacity)
        return self.rooms[name]

    def add_tunnel(self, name1: str, name2: str) -> None:
        """Adds a tunnel between two rooms (creating them if needed)."""
        room1 = self.add_room(name1)
        room2 = self.add_room(name2)
        room1.connect(room2)

    def distances_to_dormitory(self) -> dict[str, int]:
        """BFS starting from the dormitory: returns, for each room,
        its distance (in number of tunnels) to the dormitory.

        We start from the dormitory rather than the entrance because
        it's more convenient later: each ant just has to look at its
        neighbors' distances to know which one gets it closer to the
        dormitory (the one with the smallest distance).
        """
        distances = {self.dormitory.name: 0}
        queue = deque([self.dormitory])

        while queue:
            current_room = queue.popleft()
            for neighbor in current_room.neighbors:
                if neighbor.name not in distances:
                    distances[neighbor.name] = distances[current_room.name] + 1
                    queue.append(neighbor)

        return distances

    @classmethod
    def from_file(cls, path: str) -> "AntHill":
        """Parses an anthill definition file (the format given for the
        assignment) and builds the corresponding AntHill.

        File format, one item per line:
            f=5                 -> number of ants (F= or f=)
            S1                  -> a room with default capacity 1
            S4 { 2 }            -> a room with capacity 2
            Sv - S1             -> a tunnel between two rooms
        """
        nb_ants = None
        capacities: dict[str, int] = {}
        tunnels: list[tuple[str, str]] = []

        with open(path, encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue

                if line[0] in "fF" and "=" in line and "-" not in line:
                    nb_ants = int(line.split("=")[1].strip())
                    continue

                if "-" in line:
                    left, right = line.split("-", maxsplit=1)
                    tunnels.append((left.strip(), right.strip()))
                    continue

                # A room declaration: "S1" or "S4 { 2 }"
                if "{" in line:
                    name_part, capacity_part = line.split("{", maxsplit=1)
                    name = name_part.strip()
                    capacity = int(capacity_part.replace("}", "").strip())
                else:
                    name = line.strip()
                    capacity = 1
                capacities[name] = capacity

        if nb_ants is None:
            raise ValueError(f"{path}: missing 'f=' line (number of ants).")

        hill = cls(nb_ants=nb_ants)
        for name, capacity in capacities.items():
            hill.add_room(name, capacity=capacity)
        for name1, name2 in tunnels:
            hill.add_tunnel(name1, name2)

        return hill

    def to_networkx(self) -> "nx.Graph":
        """Converts the anthill into a NetworkX graph, so it can be
        drawn with nx.draw(...). Each node keeps its capacity as an
        attribute (useful for coloring the entrance/dormitory
        differently in the drawing).
        """
        graph = nx.Graph()
        for name, room in self.rooms.items():
            graph.add_node(name, capacity=room.capacity)
        for name, room in self.rooms.items():
            for neighbor in room.neighbors:
                graph.add_edge(name, neighbor.name)
        return graph

    def solve(self) -> list[list[str]]:
        """Moves every ant from the entrance to the dormitory in the
        minimum number of steps.

        Returns a list of steps; each step is a list of move strings
        like "f1 - Sv - S1".

        Priority rule: at each step, ants closest to the dormitory
        try to move first. This way, if an ant frees up a room, the
        ant right behind it can immediately take that spot in the
        very same step.
        """
        distances = self.distances_to_dormitory()
        ants = [Ant(i + 1, self.entrance) for i in range(self.nb_ants)]

        # How many ants currently sit in each finite-capacity room.
        occupancy = {
            name: 0 for name, room in self.rooms.items()
            if room.capacity != math.inf
        }

        steps: list[list[str]] = []

        while any(ant.current_room is not self.dormitory for ant in ants):
            moves: list[str] = []
            waiting = [a for a in ants if a.current_room is not self.dormitory]
            # Closest to the dormitory move first.
            waiting.sort(key=lambda a: distances[a.current_room.name])

            for ant in waiting:
                current = ant.current_room
                # Neighbors that actually get the ant closer to the
                # dormitory, sorted from closest to farthest.
                candidates = sorted(
                    (r for r in current.neighbors
                     if distances.get(r.name, math.inf) < distances[current.name]),
                    key=lambda r: distances[r.name],
                )

                for target in candidates:
                    is_free = (
                        target.capacity == math.inf
                        or occupancy[target.name] < target.capacity
                    )
                    if not is_free:
                        continue

                    # Leave the current room (if it has limited capacity).
                    if current.capacity != math.inf:
                        occupancy[current.name] -= 1
                    # Enter the target room (if it has limited capacity).
                    if target.capacity != math.inf:
                        occupancy[target.name] += 1

                    moves.append(f"f{ant.id} - {current.name} - {target.name}")
                    ant.current_room = target
                    break  # this ant has moved, go to the next ant

            if not moves:
                # Safety net: nobody could move this round. Should not
                # happen on a connected graph, but avoids an infinite
                # loop while debugging.
                raise RuntimeError("No ant could move — check the anthill graph.")

            steps.append(moves)

        return steps

    def solve_with_history(self) -> tuple[list[list[str]], list[dict[int, str]]]:
        """Same resolution as solve(), but also returns a snapshot of
        every ant's room name after each step. Used for the
        step-by-step visualization.

        Returns (steps, history), where history[i] is a dict
        {ant_id: room_name} describing where every ant stands right
        after step i+1.
        """
        distances = self.distances_to_dormitory()
        ants = [Ant(i + 1, self.entrance) for i in range(self.nb_ants)]
        occupancy = {
            name: 0 for name, room in self.rooms.items()
            if room.capacity != math.inf
        }

        steps: list[list[str]] = []
        history: list[dict[int, str]] = []

        while any(ant.current_room is not self.dormitory for ant in ants):
            moves: list[str] = []
            waiting = [a for a in ants if a.current_room is not self.dormitory]
            waiting.sort(key=lambda a: distances[a.current_room.name])

            for ant in waiting:
                current = ant.current_room
                candidates = sorted(
                    (r for r in current.neighbors
                     if distances.get(r.name, math.inf) < distances[current.name]),
                    key=lambda r: distances[r.name],
                )
                for target in candidates:
                    is_free = (
                        target.capacity == math.inf
                        or occupancy[target.name] < target.capacity
                    )
                    if not is_free:
                        continue
                    if current.capacity != math.inf:
                        occupancy[current.name] -= 1
                    if target.capacity != math.inf:
                        occupancy[target.name] += 1
                    moves.append(f"f{ant.id} - {current.name} - {target.name}")
                    ant.current_room = target
                    break

            if not moves:
                raise RuntimeError("No ant could move — check the anthill graph.")

            steps.append(moves)
            history.append({ant.id: ant.current_room.name for ant in ants})

        return steps, history

    def __repr__(self) -> str:
        return f"AntHill({self.nb_ants} ants, {len(self.rooms)} rooms)"


if __name__ == "__main__":
    # Rebuilding the "simple case" from the assignment:
    # 3 ants, rooms (Sv, S1, S2, Sd)
    # tunnels: Sv-S1, Sv-S2, S1-Sd, S2-Sd
    hill = AntHill(nb_ants=3)
    hill.add_tunnel("Sv", "S1")
    hill.add_tunnel("Sv", "S2")
    hill.add_tunnel("S1", "Sd")
    hill.add_tunnel("S2", "Sd")

    print(hill)
    for name, room in hill.rooms.items():
        print(room, "-> neighbors:", room.neighbors, "| capacity:", room.capacity)

    print()
    print("Distances to dormitory (BFS):")
    distances = hill.distances_to_dormitory()
    for name, d in distances.items():
        print(f"  {name}: {d}")

    print()
    print("Resolution:")
    steps = hill.solve()
    for i, step in enumerate(steps, start=1):
        print(f"+++ E{i} +++")
        for move in step:
            print(" ", move)
    print(f"\nTotal steps: {len(steps)}")