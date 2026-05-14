"""
Implementación de UCS, GBFS y A* usando heapq.

La estructura sigue la idea del notebook entregado:
- Se usa una cola de prioridad con heapq.
- Se guarda un diccionario de padres para reconstruir la ruta.
- Se imprime/almacena la frontera para poder explicar la traza.
"""

from __future__ import annotations

from dataclasses import dataclass
import heapq
import math
import time
from typing import Callable, Dict, List, Optional, Tuple

Node = str
Graph = Dict[Node, Dict[Node, float]]
Position = Dict[Node, Tuple[float, float]]
Heuristic = Callable[[Node, Node], float]


@dataclass
class SearchResult:
    algorithm: str
    start: Node
    goal: Node
    path: List[Node]
    total_cost: float
    path_length_edges: int
    generated_count: int
    expanded_count: int
    expansion_order: List[Node]
    frontier_trace: List[dict]
    time_ms: float
    success: bool
    explanation: str


def euclidean_heuristic(
    node: Node,
    goal: Node,
    positions: Position,
    scale: float = 2.0,
) -> float:
    """
    Calcula h(n) como distancia euclidiana estimada hasta la meta.

    En este proyecto scale=2.0 mantiene la heurística conservadora para el grafo diseñado.
    Así, h(n) ayuda a orientar la búsqueda sin sobreestimar agresivamente el costo real.
    """
    x1, y1 = positions[node]
    x2, y2 = positions[goal]
    return round(math.hypot(x2 - x1, y2 - y1) * scale, 3)


def reconstruct_path(parents: Dict[Node, Optional[Node]], goal: Node) -> List[Node]:
    """Reconstruye el camino desde la meta hasta el inicio usando el diccionario de padres."""
    path: List[Node] = []
    current: Optional[Node] = goal
    while current is not None:
        path.append(current)
        current = parents.get(current)
    path.reverse()
    return path


def calculate_path_cost(graph: Graph, path: List[Node]) -> float:
    """Calcula el costo total de una ruta."""
    if len(path) <= 1:
        return 0.0
    total = 0.0
    for u, v in zip(path, path[1:]):
        total += graph[u][v]
    return round(total, 3)


def _format_frontier(
    heap: List[Tuple[float, int, Node, float]],
    goal: Node,
    heuristic: Heuristic,
    limit: int = 10,
) -> str:
    """Convierte la cola de prioridad en texto corto para mostrarla en Streamlit."""
    ordered = sorted(heap, key=lambda item: (item[0], item[1]))[:limit]
    parts = []
    for priority, _, node, g_cost in ordered:
        h_cost = heuristic(node, goal)
        f_cost = g_cost + h_cost
        parts.append(f"{node} [p={priority:.2f}, g={g_cost:.2f}, h={h_cost:.2f}, f={f_cost:.2f}]")
    return " | ".join(parts) if parts else "Vacía"


def priority_search(
    graph: Graph,
    start: Node,
    goal: Node,
    heuristic: Heuristic,
    algorithm: str,
    max_trace: int = 60,
) -> SearchResult:
    """
    Ejecuta UCS, GBFS o A* sobre el mismo grafo.

    Criterio de prioridad:
        UCS:  p(n) = g(n)
        GBFS: p(n) = h(n)
        A*:   p(n) = g(n) + h(n)

    Args:
        graph: grafo ponderado no dirigido.
        start: nodo inicial.
        goal: nodo objetivo.
        heuristic: función h(n, goal).
        algorithm: "UCS", "GBFS" o "A*".
        max_trace: máximo de iteraciones registradas en la traza.

    Returns:
        SearchResult con ruta, costo y métricas.
    """
    algorithm = algorithm.upper().strip()
    if algorithm not in {"UCS", "GBFS", "A*"}:
        raise ValueError("algorithm debe ser 'UCS', 'GBFS' o 'A*'.")

    def get_priority(node: Node, g_cost: float) -> float:
        h_cost = heuristic(node, goal)
        if algorithm == "UCS":
            return g_cost
        if algorithm == "GBFS":
            return h_cost
        return g_cost + h_cost

    start_time = time.perf_counter()

    counter = 0
    start_priority = get_priority(start, 0.0)
    frontier: List[Tuple[float, int, Node, float]] = [(start_priority, counter, start, 0.0)]
    heapq.heapify(frontier)

    parents: Dict[Node, Optional[Node]] = {start: None}
    best_cost: Dict[Node, float] = {start: 0.0}
    visited = set()
    expansion_order: List[Node] = []
    frontier_trace: List[dict] = []
    generated_count = 1  # incluye el nodo inicial
    iteration = 0

    while frontier:
        frontier_before = _format_frontier(frontier, goal, heuristic)
        priority, _, current, current_g = heapq.heappop(frontier)

        if current in visited:
            continue

        visited.add(current)
        expansion_order.append(current)
        iteration += 1

        current_h = heuristic(current, goal)
        generated_neighbors: List[str] = []

        if current == goal:
            elapsed = (time.perf_counter() - start_time) * 1000
            path = reconstruct_path(parents, goal)
            total_cost = calculate_path_cost(graph, path)

            frontier_trace.append(
                {
                    "iteracion": iteration,
                    "nodo_expandido": current,
                    "g": round(current_g, 3),
                    "h": round(current_h, 3),
                    "f": round(current_g + current_h, 3),
                    "prioridad_usada": round(priority, 3),
                    "vecinos_generados": "Meta alcanzada",
                    "frontera_antes": frontier_before,
                    "frontera_despues": _format_frontier(frontier, goal, heuristic),
                }
            )

            explanation = build_result_explanation(algorithm, path, total_cost)
            return SearchResult(
                algorithm=algorithm,
                start=start,
                goal=goal,
                path=path,
                total_cost=total_cost,
                path_length_edges=max(len(path) - 1, 0),
                generated_count=generated_count,
                expanded_count=len(expansion_order),
                expansion_order=expansion_order,
                frontier_trace=frontier_trace[:max_trace],
                time_ms=round(elapsed, 4),
                success=True,
                explanation=explanation,
            )

        for neighbor, edge_cost in graph[current].items():
            if neighbor in visited:
                continue

            new_g = current_g + edge_cost

            # UCS y A* usan g(n) para garantizar mejoras de costo.
            # GBFS mantiene la misma estructura, pero su prioridad sigue siendo solamente h(n).
            if new_g < best_cost.get(neighbor, math.inf):
                best_cost[neighbor] = new_g
                parents[neighbor] = current
                counter += 1
                neighbor_priority = get_priority(neighbor, new_g)
                heapq.heappush(frontier, (neighbor_priority, counter, neighbor, new_g))
                generated_count += 1
                generated_neighbors.append(
                    f"{neighbor} (costo arista={edge_cost:.2f}, g={new_g:.2f}, h={heuristic(neighbor, goal):.2f}, p={neighbor_priority:.2f})"
                )

        if len(frontier_trace) < max_trace:
            frontier_trace.append(
                {
                    "iteracion": iteration,
                    "nodo_expandido": current,
                    "g": round(current_g, 3),
                    "h": round(current_h, 3),
                    "f": round(current_g + current_h, 3),
                    "prioridad_usada": round(priority, 3),
                    "vecinos_generados": " | ".join(generated_neighbors) if generated_neighbors else "Ninguno",
                    "frontera_antes": frontier_before,
                    "frontera_despues": _format_frontier(frontier, goal, heuristic),
                }
            )

    elapsed = (time.perf_counter() - start_time) * 1000
    return SearchResult(
        algorithm=algorithm,
        start=start,
        goal=goal,
        path=[],
        total_cost=math.inf,
        path_length_edges=0,
        generated_count=generated_count,
        expanded_count=len(expansion_order),
        expansion_order=expansion_order,
        frontier_trace=frontier_trace[:max_trace],
        time_ms=round(elapsed, 4),
        success=False,
        explanation="No se encontró una ruta entre el origen y la meta.",
    )


def ucs(graph: Graph, start: Node, goal: Node, heuristic: Heuristic) -> SearchResult:
    """Uniform Cost Search: expande el nodo con menor costo acumulado g(n)."""
    return priority_search(graph, start, goal, heuristic, "UCS")


def gbfs(graph: Graph, start: Node, goal: Node, heuristic: Heuristic) -> SearchResult:
    """Greedy Best-First Search: expande el nodo aparentemente más cercano a la meta según h(n)."""
    return priority_search(graph, start, goal, heuristic, "GBFS")


def astar(graph: Graph, start: Node, goal: Node, heuristic: Heuristic) -> SearchResult:
    """A*: combina costo acumulado g(n) y estimación h(n) mediante f(n)=g(n)+h(n)."""
    return priority_search(graph, start, goal, heuristic, "A*")


def build_result_explanation(algorithm: str, path: List[Node], total_cost: float) -> str:
    """Genera una explicación corta para mostrar debajo de cada algoritmo."""
    route = " → ".join(path)
    if algorithm == "UCS":
        return f"UCS encontró una ruta de costo {total_cost:.2f}. Prioriza siempre el menor g(n), por eso es óptimo si los costos son positivos. Ruta: {route}."
    if algorithm == "GBFS":
        return f"GBFS encontró una ruta de costo {total_cost:.2f}. Prioriza solo h(n), por eso puede escoger caminos que parecen cercanos pero resultan más costosos. Ruta: {route}."
    return f"A* encontró una ruta de costo {total_cost:.2f}. Usa f(n)=g(n)+h(n), combinando costo recorrido y cercanía estimada a la meta. Ruta: {route}."


def dijkstra_costs(graph: Graph, start: Node) -> Dict[Node, float]:
    """Calcula costos mínimos desde start usando Dijkstra. Sirve para validar heurística."""
    distances = {start: 0.0}
    heap = [(0.0, start)]
    while heap:
        cost, node = heapq.heappop(heap)
        if cost > distances[node]:
            continue
        for neighbor, edge_cost in graph[node].items():
            new_cost = cost + edge_cost
            if new_cost < distances.get(neighbor, math.inf):
                distances[neighbor] = new_cost
                heapq.heappush(heap, (new_cost, neighbor))
    return distances


def check_heuristic_admissibility(
    graph: Graph,
    positions: Position,
    goal: Node,
    scale: float = 2.0,
) -> Tuple[bool, List[dict]]:
    """
    Verifica h(n) <= costo real óptimo desde n hasta la meta.
    Si se cumple para todos los nodos, la heurística es admisible para esa meta.
    """
    problems = []
    for node in graph:
        true_cost = dijkstra_costs(graph, node).get(goal, math.inf)
        h_value = euclidean_heuristic(node, goal, positions, scale)
        if h_value > true_cost + 1e-9:
            problems.append({"nodo": node, "h(n)": h_value, "costo_optimo_real": true_cost})
    return len(problems) == 0, problems


def check_heuristic_consistency(
    graph: Graph,
    positions: Position,
    goal: Node,
    scale: float = 2.0,
) -> Tuple[bool, List[dict]]:
    """
    Verifica h(u) <= c(u,v) + h(v) para cada arista.
    Si se cumple, la heurística es consistente para esa meta.
    """
    problems = []
    checked = set()
    for u, neighbors in graph.items():
        for v, cost in neighbors.items():
            key = tuple(sorted((u, v)))
            if key in checked:
                continue
            checked.add(key)

            hu = euclidean_heuristic(u, goal, positions, scale)
            hv = euclidean_heuristic(v, goal, positions, scale)

            if hu > cost + hv + 1e-9:
                problems.append({"arista": f"{u} - {v}", "caso": f"h({u}) > c + h({v})", "h_u": hu, "costo": cost, "h_v": hv})
            if hv > cost + hu + 1e-9:
                problems.append({"arista": f"{u} - {v}", "caso": f"h({v}) > c + h({u})", "h_u": hv, "costo": cost, "h_v": hu})

    return len(problems) == 0, problems
