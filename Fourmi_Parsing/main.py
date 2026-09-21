import glob
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

from ants import parse_anthill, simulate

ANTHILL_DIR = "anthills"
OUTPUT_DIR = "outputs"


def display_steps(steps):
    for i, step in enumerate(steps, start=1):
        print(f"+++ S{i} +++")
        for line in step:
            print(line)


def draw_graph(G, name):
    pos = nx.spring_layout(G, seed=42)
    colors = ["#8ecae6" if s == "Sv" else "#219ebc" if s == "Sd" else "#e9ecef" for s in G.nodes]
    nx.draw(G, pos, with_labels=True, node_color=colors, node_size=800)
    plt.title(name)
    plt.savefig(os.path.join(OUTPUT_DIR, f"{name}_graph.png"))
    plt.close()


def draw_progression(steps, F, name):
    arrivals = 0
    values = [0]
    for step in steps:
        arrivals += sum(1 for line in step if line.endswith("Sd"))
        values.append(arrivals)
    plt.plot(range(len(values)), values, marker="o")
    plt.xlabel("step")
    plt.ylabel("ants arrived at the dorm")
    plt.title(name)
    plt.savefig(os.path.join(OUTPUT_DIR, f"{name}_progression.png"))
    plt.close()


def process_anthill(file_path):
    name = os.path.splitext(os.path.basename(file_path))[0]
    F, G = parse_anthill(file_path)

    print(f"\n===== {name} (F={F}) =====")
    steps = simulate(G, F)
    display_steps(steps)
    print(f"-> {len(steps)} steps needed for the {F} ants to reach the dorm.")

    draw_graph(G, name)
    draw_progression(steps, F, name)

    return name, len(steps)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    files = sys.argv[1:] or sorted(glob.glob(os.path.join(ANTHILL_DIR, "*.txt")))
    if not files:
        print(f"No anthill file found in '{ANTHILL_DIR}/'.")
        return

    results = [process_anthill(path) for path in files]

    print("\n===== SUMMARY =====")
    for name, nb_steps in results:
        print(f"{name:35s} -> {nb_steps} steps")


if __name__ == "__main__":
    main()