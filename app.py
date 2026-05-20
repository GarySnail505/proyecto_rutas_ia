from __future__ import annotations

import pandas as pd
import streamlit as st

from algorithms import (
    astar,
    check_heuristic_admissibility,
    check_heuristic_consistency,
    euclidean_heuristic,
    gbfs,
    ucs,
)
from graph_data import (
    BASE_EDGES,
    CITY_POSITIONS,
    PREDEFINED_CASES,
    TRAFFIC_PROFILES,
    build_graph,
    get_edge_reasons,
)
from visualization import make_graph_figure

st.set_page_config(
    page_title="Rutas Inteligentes - UCS vs GBFS vs A*",
    page_icon="🧭",
    layout="wide",
)

HEURISTIC_SCALE = 2.0


def h(node: str, goal: str) -> float:
    return euclidean_heuristic(node, goal, CITY_POSITIONS, scale=HEURISTIC_SCALE)


def result_to_dict(result):
    return {
        "Algoritmo": result.algorithm,
        "Ruta": " → ".join(result.path) if result.success else "Sin ruta",
        "Costo total": result.total_cost,
        "N.º pasos": result.path_length_edges,
        "Nodos generados": result.generated_count,
        "Nodos expandidos": result.expanded_count,
        "Tiempo (ms)": result.time_ms,
    }


def trace_dataframe(result):
    if not result.frontier_trace:
        return pd.DataFrame()
    return pd.DataFrame(result.frontier_trace)


st.title("Sistema de rutas inteligentes para entregas o transporte")
st.caption(
    "Comparación de UCS, GBFS y A* sobre un grafo ponderado semi-real basado en Quito."
)

with st.sidebar:
    st.header("Configuración")

    profile = st.selectbox("Perfil de tráfico", list(TRAFFIC_PROFILES.keys()), index=0)
    graph = build_graph(profile)
    nodes = list(CITY_POSITIONS.keys())

    selected_case = st.selectbox("Caso preparado", list(PREDEFINED_CASES.keys()))
    default_start, default_goal = PREDEFINED_CASES[selected_case]

    start = st.selectbox("Origen", nodes, index=nodes.index(default_start))
    goal = st.selectbox("Destino", nodes, index=nodes.index(default_goal))

    st.divider()
    st.metric("Nodos", len(graph))
    st.metric("Aristas", len(BASE_EDGES))
    st.write(
        "**Costo de arista:** distancia aproximada + tráfico + dificultad de circulación."
    )
    st.write(
        "**Heurística:** distancia euclidiana estimada entre coordenadas del mapa."
    )

if start == goal:
    st.warning("El origen y el destino son iguales. Selecciona dos nodos diferentes.")
    st.stop()

# Ejecutar algoritmos
result_ucs = ucs(graph, start, goal, h)
result_gbfs = gbfs(graph, start, goal, h)
result_astar = astar(graph, start, goal, h)
results = [result_ucs, result_gbfs, result_astar]

st.subheader("1. Vista general del grafo")
st.plotly_chart(
    make_graph_figure(
        graph,
        CITY_POSITIONS,
        path=result_astar.path,
        explored=result_astar.expansion_order,
        start=start,
        goal=goal,
        title="Grafo base de Quito - ruta resaltada de A*",
    ),
    use_container_width=True,
)

st.subheader("2. Comparación general")
summary_df = pd.DataFrame([result_to_dict(r) for r in results])
st.dataframe(summary_df, use_container_width=True, hide_index=True)

best_cost = summary_df["Costo total"].min()
gbfs_cost = result_gbfs.total_cost
if gbfs_cost > best_cost:
    st.info(
        f"En esta consulta, GBFS obtuvo costo {gbfs_cost:.2f}, mientras que el mejor costo fue {best_cost:.2f}. "
        "Esto muestra que GBFS puede fallar porque mira solo h(n), no el costo acumulado g(n)."
    )
else:
    st.info(
        "En esta consulta GBFS no fue peor que el mejor costo. Para ver el caso engañoso, usa: "
        "'Caso 1 - GBFS se equivoca: Solanda → Tumbaco'."
    )

st.subheader("3. Resultados divididos por algoritmo")
col1, col2, col3 = st.columns(3)
columns = [(col1, result_ucs), (col2, result_gbfs), (col3, result_astar)]

for col, result in columns:
    with col:
        st.markdown(f"### {result.algorithm}")
        st.plotly_chart(
            make_graph_figure(
                graph,
                CITY_POSITIONS,
                path=result.path,
                explored=result.expansion_order,
                start=start,
                goal=goal,
                title=f"Ruta encontrada por {result.algorithm}",
            ),
            use_container_width=True,
        )
        st.metric("Costo total", f"{result.total_cost:.2f}")
        st.metric("Pasos de la ruta", result.path_length_edges)
        st.metric("Nodos expandidos", result.expanded_count)
        st.metric("Tiempo aproximado", f"{result.time_ms:.4f} ms")
        st.write("**Ruta:**")
        st.code(" → ".join(result.path), language="text")
        st.write(result.explanation)

        with st.expander("Ver orden de expansión"):
            st.write(" → ".join(result.expansion_order))

        with st.expander("Ver frontera / cola de prioridad"):
            st.dataframe(
                trace_dataframe(result), use_container_width=True, hide_index=True
            )

# st.subheader("4. Análisis de heurística")
# admissible, admissibility_problems = check_heuristic_admissibility(graph, CITY_POSITIONS, goal, HEURISTIC_SCALE)
# consistent, consistency_problems = check_heuristic_consistency(graph, CITY_POSITIONS, goal, HEURISTIC_SCALE)

# h_col1, h_col2 = st.columns(2)
# with h_col1:
#     st.metric("Heurística admisible", "Sí" if admissible else "No")
#     st.write(
#         "Una heurística es admisible si nunca sobreestima el costo real mínimo hasta la meta: "
#         "h(n) ≤ costo óptimo real."
#     )
#     if not admissible:
#         st.dataframe(pd.DataFrame(admissibility_problems), use_container_width=True, hide_index=True)

# with h_col2:
#     st.metric("Heurística consistente", "Sí" if consistent else "No")
#     st.write(
#         "Una heurística es consistente si para toda arista se cumple: "
#         "h(u) ≤ c(u,v) + h(v)."
#     )
#     if not consistent:
#         st.dataframe(pd.DataFrame(consistency_problems), use_container_width=True, hide_index=True)

# with st.expander("Justificación de los pesos del grafo"):
#     reasons = get_edge_reasons()
#     rows = []
#     for edge in BASE_EDGES:
#         rows.append(
#             {
#                 "Arista": f"{edge['u']} - {edge['v']}",
#                 "Costo base": edge["cost"],
#                 "Justificación": reasons[(min(edge['u'], edge['v']), max(edge['u'], edge['v']))],
#             }
#         )
#     st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# with st.expander("Cómo defender la demo en clase"):
#     st.markdown(
#         """
# - **UCS** expande el nodo con menor `g(n)`. Por eso encuentra la ruta de menor costo cuando todos los pesos son positivos.
# - **GBFS** expande el nodo con menor `h(n)`. Puede ser rápido, pero no garantiza optimalidad porque ignora el costo ya recorrido.
# - **A\\*** expande con `f(n)=g(n)+h(n)`. Si la heurística es admisible y consistente, mantiene optimalidad y suele expandir menos nodos que UCS.
# - Para explicar la traza, usa la tabla de frontera: muestra qué nodo se expandió, qué vecinos entraron a la cola y qué prioridad tuvo cada uno.
#         """
#     )
