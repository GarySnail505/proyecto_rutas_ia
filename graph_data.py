"""
Datos del grafo semi-real de Quito para el proyecto de rutas inteligentes.

El grafo representa sectores/paradas importantes de Quito y valles cercanos.
Los pesos NO son distancias reales exactas; son un costo académico combinado:
    costo = distancia aproximada + tráfico + dificultad de circulación.

Ese costo puede interpretarse como minutos aproximados o unidades de esfuerzo.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

Node = str
Graph = Dict[Node, Dict[Node, float]]
Position = Dict[Node, Tuple[float, float]]

# Coordenadas ficticias coherentes con la posición relativa de los sectores.
# Sirven para dibujar el grafo y calcular la heurística por distancia euclidiana.
CITY_POSITIONS: Position = {
    "Quitumbe": (0.0, 0.0),
    "Chillogallo": (-1.0, 1.1),
    "Solanda": (0.6, 1.2),
    "Villaflora": (1.0, 2.4),
    "El Recreo": (1.4, 3.3),
    "La Magdalena": (0.5, 4.1),
    "Loma de Puengasí": (0.0, 4.5),
    "Centro Histórico": (1.6, 5.0),
    "La Marín": (2.3, 5.2),
    "Universidad Central": (1.1, 6.3),
    "La Floresta": (2.8, 6.6),
    "La Carolina": (2.1, 8.0),
    "Iñaquito": (2.3, 8.8),
    "El Labrador": (2.2, 10.0),
    "Cotocollao": (1.1, 12.0),
    "Carcelén": (2.3, 13.1),
    "Cumbayá": (5.5, 6.8),
    "Tumbaco": (7.1, 7.4),
}

# 17 nodos y 31 aristas: cumple el requisito de mínimo 15 nodos y 25 aristas.
# Cada arista es no dirigida.
BASE_EDGES: List[dict] = [
    {
        "u": "Quitumbe",
        "v": "Chillogallo",
        "cost": 8,
    },
    {
        "u": "Quitumbe",
        "v": "Solanda",
        "cost": 7,
    },
    {
        "u": "Quitumbe",
        "v": "Villaflora",
        "cost": 15,
    },
    {
        "u": "Chillogallo",
        "v": "Solanda",
        "cost": 6,
    },
    {
        "u": "Chillogallo",
        "v": "Villaflora",
        "cost": 11,
    },
    {
        "u": "Solanda",
        "v": "Villaflora",
        "cost": 6,
    },
    {
        "u": "Solanda",
        "v": "El Recreo",
        "cost": 9,
    },
    {
        "u": "Villaflora",
        "v": "El Recreo",
        "cost": 5,
    },
    {
        "u": "El Recreo",
        "v": "La Magdalena",
        "cost": 7,
    },
    {
        "u": "El Recreo",
        "v": "La Marín",
        "cost": 9,
    },
    {
        "u": "La Magdalena",
        "v": "Centro Histórico",
        "cost": 7,
    },
    {
        "u": "Centro Histórico",
        "v": "La Marín",
        "cost": 3,
    },
    {
        "u": "Centro Histórico",
        "v": "Universidad Central",
        "cost": 6,
    },
    {
        "u": "La Marín",
        "v": "Universidad Central",
        "cost": 7,
    },
    {
        "u": "La Marín",
        "v": "La Floresta",
        "cost": 8,
    },
    {
        "u": "Universidad Central",
        "v": "La Floresta",
        "cost": 8,
    },
    {
        "u": "Universidad Central",
        "v": "La Carolina",
        "cost": 9,
    },
    {
        "u": "La Floresta",
        "v": "La Carolina",
        "cost": 7,
    },
    {
        "u": "La Carolina",
        "v": "Iñaquito",
        "cost": 4,
    },
    {
        "u": "Iñaquito",
        "v": "El Labrador",
        "cost": 5,
    },
    {
        "u": "La Carolina",
        "v": "El Labrador",
        "cost": 8,
    },
    {
        "u": "El Labrador",
        "v": "Cotocollao",
        "cost": 12,
    },
    {
        "u": "Cotocollao",
        "v": "Carcelén",
        "cost": 7,
    },
    {
        "u": "El Labrador",
        "v": "Carcelén",
        "cost": 8,
    },
    {
        "u": "Iñaquito",
        "v": "Cotocollao",
        "cost": 14,
    },
    {
        "u": "Cotocollao",
        "v": "Chillogallo",
        "cost": 26,
    },
    {
        "u": "La Floresta",
        "v": "Cumbayá",
        "cost": 12,
    },
    {
        "u": "La Marín",
        "v": "Cumbayá",
        "cost": 30,
    },
    {
        "u": "La Carolina",
        "v": "Cumbayá",
        "cost": 20,
    },
    {
        "u": "Cumbayá",
        "v": "Tumbaco",
        "cost": 10,
    },
    {
        "u": "La Floresta",
        "v": "Tumbaco",
        "cost": 27,
    },
    {
        "u": "La Magdalena",
        "v": "Loma de Puengasí",
        "cost": 35,
    },
]

# Casos preparados para la exposición y pruebas.
# El primero está diseñado para mostrar que GBFS puede equivocarse.
PREDEFINED_CASES = {
    "Caso 1 - GBFS se equivoca: Solanda → Tumbaco": ("Solanda", "Tumbaco"),
    "Caso 2 - Ruta sur a valle: Quitumbe → Tumbaco": ("Quitumbe", "Tumbaco"),
    "Caso 3 - Norte a valle: Cotocollao → Cumbayá": ("Cotocollao", "Cumbayá"),
    "Caso 4 - Ruta corta urbana: Universidad Central → El Labrador": (
        "Universidad Central",
        "El Labrador",
    ),
}

TRAFFIC_PROFILES = {
    "Normal": {},
    "Hora pico hacia valles": {
        ("La Marín", "Cumbayá"): 1.35,
        ("La Carolina", "Cumbayá"): 1.25,
        ("Cumbayá", "Tumbaco"): 1.15,
    },
    "Accidente en eje centro-oriente": {
        ("La Marín", "La Floresta"): 1.60,
        ("La Marín", "Cumbayá"): 1.50,
        ("Centro Histórico", "La Marín"): 1.35,
    },
}


def normalize_edge(u: Node, v: Node) -> Tuple[Node, Node]:
    """Devuelve una arista en orden alfabético para comparar aristas no dirigidas."""
    return tuple(sorted((u, v)))  # type: ignore[return-value]


def build_graph(profile_name: str = "Normal") -> Graph:
    """
    Construye el grafo no dirigido aplicando, si corresponde, un perfil de tráfico.

    Args:
        profile_name: nombre del perfil definido en TRAFFIC_PROFILES.

    Returns:
        Diccionario de adyacencia: {nodo: {vecino: costo}}.
    """
    graph: Graph = {node: {} for node in CITY_POSITIONS}
    profile = TRAFFIC_PROFILES.get(profile_name, {})
    normalized_profile = {
        normalize_edge(u, v): factor for (u, v), factor in profile.items()
    }

    for edge in BASE_EDGES:
        u, v = edge["u"], edge["v"]
        base_cost = float(edge["cost"])
        factor = normalized_profile.get(normalize_edge(u, v), 1.0)
        cost = round(base_cost * factor, 2)
        graph[u][v] = cost
        graph[v][u] = cost

    return graph


def get_edge_reasons() -> Dict[Tuple[Node, Node], str]:
    """Devuelve la justificación textual de cada arista."""
    return {normalize_edge(e["u"], e["v"]): e["reason"] for e in BASE_EDGES}
