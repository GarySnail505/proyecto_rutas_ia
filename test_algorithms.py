"""Prueba rápida de consola para verificar los algoritmos sin abrir Streamlit."""

from algorithms import astar, euclidean_heuristic, gbfs, ucs
from graph_data import CITY_POSITIONS, build_graph


def h(node, goal):
    return euclidean_heuristic(node, goal, CITY_POSITIONS, scale=2.0)


def main():
    graph = build_graph("Normal")
    start, goal = "Solanda", "Tumbaco"
    for algorithm in [ucs, gbfs, astar]:
        result = algorithm(graph, start, goal, h)
        print("=" * 70)
        print(result.algorithm)
        print("Ruta:", " -> ".join(result.path))
        print("Costo total:", result.total_cost)
        print("Nodos generados:", result.generated_count)
        print("Nodos expandidos:", result.expanded_count)
        print("Orden de expansión:", " -> ".join(result.expansion_order))


if __name__ == "__main__":
    main()
