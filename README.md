# Sistema de rutas inteligentes para entregas o transporte

Proyecto de Inteligencia Artificial para comparar tres algoritmos de búsqueda sobre un grafo ponderado:

- **UCS**: Uniform Cost Search
- **GBFS**: Greedy Best-First Search
- **A\***: A estrella

El escenario usado es un grafo semi-real basado en sectores de Quito. Los pesos de las aristas representan un costo combinado de traslado:

```text
costo = distancia aproximada + tráfico + dificultad de circulación
```

El proyecto está preparado para ejecutarse con **Streamlit** y presentar una comparación visual en tres espacios divididos: UCS, GBFS y A\*.

---

## 1. Estructura del proyecto

```text
proyecto_rutas_ia/
│
├── app.py                         # Interfaz principal en Streamlit
├── algorithms.py                  # Implementación de UCS, GBFS y A*
├── graph_data.py                  # Grafo de Quito, nodos, aristas, pesos y casos de prueba
├── visualization.py               # Visualización del grafo con Plotly
├── test_algorithms.py             # Prueba rápida por consola
├── requirements.txt               # Librerías necesarias
├── run_app.bat                    # Ejecutor para Windows
├── README.md                      # Instrucciones del proyecto
├── EXPLICACION_FUNCIONAMIENTO.md  # Explicación detallada del funcionamiento
└── .streamlit/
    └── config.toml                # Configuración visual de Streamlit
```

---

## 2. Instalación

Abre una terminal dentro de la carpeta del proyecto y ejecuta:

```bash
pip install -r requirements.txt
```

---

## 3. Ejecución

### Opción A: desde terminal

```bash
streamlit run app.py
```

### Opción B: en Windows

Haz doble clic en:

```text
run_app.bat
```

---

## 4. Funcionamiento general

La aplicación permite:

1. Seleccionar un **origen** y un **destino**.
2. Elegir un **perfil de tráfico**.
3. Ejecutar automáticamente los tres algoritmos.
4. Visualizar el grafo y la ruta encontrada.
5. Comparar:
   - Ruta obtenida.
   - Costo total.
   - Número de pasos.
   - Nodos generados.
   - Nodos expandidos.
   - Tiempo aproximado.
   - Orden de expansión.
   - Frontera o cola de prioridad.

---

## 5. Casos de prueba incluidos

La interfaz incluye casos preparados:

| Caso | Origen | Destino | Objetivo académico |
|---|---|---|---|
| Caso 1 | Solanda | Tumbaco | Mostrar que GBFS puede encontrar una ruta peor |
| Caso 2 | Quitumbe | Tumbaco | Comparar ruta larga desde el sur al valle |
| Caso 3 | Cotocollao | Cumbayá | Analizar ruta norte-valle |
| Caso 4 | Universidad Central | El Labrador | Ruta urbana corta |

---

## 6. Algoritmos implementados

### UCS

Prioridad:

```text
p(n) = g(n)
```

Expande primero el nodo con menor costo acumulado desde el origen. Con costos positivos, UCS encuentra la ruta de menor costo.

### GBFS

Prioridad:

```text
p(n) = h(n)
```

Expande el nodo que parece más cercano al objetivo según la heurística. Puede ser rápido, pero no garantiza encontrar la ruta más barata.

### A\*

Prioridad:

```text
f(n) = g(n) + h(n)
```

Combina el costo ya recorrido con la estimación hacia la meta. Si la heurística es admisible y consistente, A\* conserva optimalidad.

---

## 7. Heurística usada

La heurística se calcula mediante distancia euclidiana entre las coordenadas ficticias de los nodos:

```text
h(n) = distancia_euclidiana(n, meta) × 2.0
```

La escala 2.0 se usa para que la heurística sea conservadora dentro del grafo diseñado. La interfaz verifica si la heurística es:

- **Admisible**: no sobreestima el costo óptimo real.
- **Consistente**: cumple `h(u) ≤ c(u,v) + h(v)` para cada arista.

---

## 8. Caso donde GBFS falla

Caso recomendado:

```text
Solanda → Tumbaco
```

Normalmente se observa algo similar a:

```text
UCS:  Solanda → El Recreo → La Marín → La Floresta → Cumbayá → Tumbaco
GBFS: Solanda → El Recreo → La Marín → Cumbayá → Tumbaco
A*:   Solanda → El Recreo → La Marín → La Floresta → Cumbayá → Tumbaco
```

GBFS escoge `La Marín → Cumbayá` porque Cumbayá parece más cercano al destino. Sin embargo, esa arista tiene costo alto por tráfico y pendiente. Por eso GBFS puede producir una ruta más costosa.

---

## 9. Archivo principal

El archivo que se ejecuta es:

```text
app.py
```

No es necesario modificar el código para cambiar origen o destino. Todo se hace desde la interfaz.
