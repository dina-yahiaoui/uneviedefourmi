"""
main.py
Entry point: loads every anthill file, solves each one, prints the
resolution, and generates a static graph image + an animated GIF of
the ants moving step by step.
"""

import glob
import os

import imageio.v2 as imageio
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from ants import AntHill

# Chemins ancrés sur l'emplacement de ce fichier, pas sur le
# répertoire depuis lequel on lance le script (évite les surprises
# selon l'endroit où on exécute "python main.py").
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "fourmilieres")
OUTPUT_DIR = os.path.join(BASE_DIR, "output_images")


def print_resolution(name: str, steps: list[list[str]]) -> None:
    """Prints each step the same way as the assignment's examples
    (+++ E1 +++, f1 - Sv - S1, ...)."""
    print(f"=== {name} ===")
    for i, step in enumerate(steps, start=1):
        print(f"+++ E{i} +++")
        for move in step:
            print(move)
    print(f"Total steps: {len(steps)}\n")


def draw_structure(hill: AntHill, pos: dict, output_path: str) -> None:
    """Draws the anthill graph on its own (no ants)."""
    graph = hill.to_networkx()
    colors = [
        "tab:orange" if graph.nodes[n]["capacity"] == float("inf") else "tab:blue"
        for n in graph.nodes
    ]
    plt.figure(figsize=(7, 6))
    nx.draw(
        graph, pos, with_labels=True, node_color=colors,
        node_size=900, font_size=7, font_color="white", font_weight="bold",
    )
    plt.title("Anthill structure (orange = entrance/dormitory)")
    plt.savefig(output_path)
    plt.close()


def make_animation(hill: AntHill, history: list[dict[int, str]], pos: dict,
                    output_path: str) -> None:
    """Builds an animated GIF: one frame per step, ants highlighted in
    the room they're currently in."""
    graph = hill.to_networkx()
    frames = []

    for i, positions in enumerate(history, start=1):
        ants_per_room: dict[str, list[int]] = {}
        for ant_id, room_name in positions.items():
            ants_per_room.setdefault(room_name, []).append(ant_id)

        labels, node_colors = {}, []
        for node in graph.nodes:
            ants_here = ants_per_room.get(node, [])
            label = node
            if ants_here:
                label += "\n" + ",".join(f"f{a}" for a in ants_here)
            labels[node] = label
            node_colors.append("tab:green" if ants_here else "lightgray")

        fig = plt.figure(figsize=(7, 6))
        nx.draw(
            graph, pos, labels=labels, node_color=node_colors,
            node_size=1000, font_size=6, font_weight="bold",
        )
        plt.title(f"Step {i}/{len(history)}")
        fig.canvas.draw()
        frame = np.asarray(fig.canvas.buffer_rgba())
        frames.append(frame)
        plt.close(fig)

    imageio.mimsave(output_path, frames, duration=0.8, loop=0)


def solve_and_visualize(path: str) -> None:
    name = os.path.splitext(os.path.basename(path))[0]
    hill = AntHill.from_file(path)

    steps, history = hill.solve_with_history()
    print_resolution(name, steps)

    pos = nx.spring_layout(hill.to_networkx(), seed=42)  # same layout for both images
    draw_structure(hill, pos, os.path.join(OUTPUT_DIR, f"{name}_structure.png"))
    make_animation(hill, history, pos, os.path.join(OUTPUT_DIR, f"{name}_animation.gif"))


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    files = sorted(glob.glob(os.path.join(INPUT_DIR, "*.txt")))
    if not files:
        print(f"No anthill file found in ./{INPUT_DIR}/")
        return

    for path in files:
        solve_and_visualize(path)

    print(f"Done. Images and GIFs saved in ./{OUTPUT_DIR}/")


if __name__ == "__main__":
    main()