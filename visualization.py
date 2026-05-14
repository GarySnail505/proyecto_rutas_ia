"""Funciones de visualización del grafo para Streamlit con Plotly."""

from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

import plotly.graph_objects as go

Node = str
Graph = Dict[Node, Dict[Node, float]]
Position = Dict[Node, Tuple[float, float]]


def _edge_key(u: Node, v: Node) -> Tuple[Node, Node]:
    return tuple(sorted((u, v)))  # type: ignore[return-value]


def make_graph_figure(
    graph: Graph,
    positions: Position,
    path: List[Node] | None = None,
    explored: Iterable[Node] | None = None,
    start: Node | None = None,
    goal: Node | None = None,
    title: str = "Grafo de rutas",
) -> go.Figure:
    """Crea una figura del grafo resaltando ruta, inicio, meta y nodos explorados."""
    path = path or []
    explored_set = set(explored or [])
    path_set = set(path)
    route_edges = {_edge_key(u, v) for u, v in zip(path, path[1:])}

    normal_x, normal_y = [], []
    route_x, route_y = [], []
    label_x, label_y, label_text = [], [], []
    added_edges = set()

    for u, neighbors in graph.items():
        for v, cost in neighbors.items():
            key = _edge_key(u, v)
            if key in added_edges:
                continue
            added_edges.add(key)

            x0, y0 = positions[u]
            x1, y1 = positions[v]
            target_x = route_x if key in route_edges else normal_x
            target_y = route_y if key in route_edges else normal_y
            target_x.extend([x0, x1, None])
            target_y.extend([y0, y1, None])

            label_x.append((x0 + x1) / 2)
            label_y.append((y0 + y1) / 2)
            label_text.append(str(cost).replace(".0", ""))

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=normal_x,
            y=normal_y,
            mode="lines",
            line=dict(width=1, color="#b7b7b7"),
            hoverinfo="skip",
            name="Aristas",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=route_x,
            y=route_y,
            mode="lines",
            line=dict(width=5, color="#d62728"),
            hoverinfo="skip",
            name="Ruta encontrada",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=label_x,
            y=label_y,
            text=label_text,
            mode="text",
            textfont=dict(size=10, color="#555555"),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    node_x, node_y, node_text, node_color, node_size, node_line = [], [], [], [], [], []
    for node, (x, y) in positions.items():
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

        if node == start:
            node_color.append("#2ca02c")
            node_size.append(22)
            node_line.append(3)
        elif node == goal:
            node_color.append("#ff7f0e")
            node_size.append(22)
            node_line.append(3)
        elif node in path_set:
            node_color.append("#d62728")
            node_size.append(18)
            node_line.append(2)
        elif node in explored_set:
            node_color.append("#9467bd")
            node_size.append(14)
            node_line.append(1)
        else:
            node_color.append("#ffffff")
            node_size.append(13)
            node_line.append(1)

    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=node_text,
            textposition="top center",
            marker=dict(
                color=node_color,
                size=node_size,
                line=dict(color="#333333", width=node_line),
            ),
            hovertext=node_text,
            hoverinfo="text",
            name="Nodos",
        )
    )

    fig.update_layout(
        title=title,
        showlegend=True,
        margin=dict(l=10, r=10, t=45, b=10),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=460,
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    return fig
