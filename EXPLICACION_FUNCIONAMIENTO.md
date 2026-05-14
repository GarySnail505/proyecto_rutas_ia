# Explicación detallada del funcionamiento del proyecto

## 1. Idea general

El proyecto implementa un sistema de rutas inteligentes sobre un grafo ponderado inspirado en Quito. El usuario selecciona un origen y un destino, y el sistema calcula tres rutas usando:

- UCS
- GBFS
- A\*

Luego presenta los resultados en una interfaz visual de Streamlit. La pantalla se divide en tres espacios principales, uno para cada algoritmo, con su ruta, costo, nodos expandidos, nodos generados, tiempo y traza de la frontera.

---

## 2. Representación del problema

### 2.1 Estados

Cada estado es un nodo del grafo. En este proyecto, un nodo representa un sector o punto de Quito, por ejemplo:

```text
Solanda, El Recreo, La Marín, La Floresta, Cumbayá, Tumbaco
```

### 2.2 Estado inicial

Es el punto de partida seleccionado por el usuario en la barra lateral de Streamlit.

Ejemplo:

```text
Origen = Solanda
```

### 2.3 Estado objetivo

Es el destino seleccionado por el usuario.

Ejemplo:

```text
Destino = Tumbaco
```

### 2.4 Acciones

Una acción consiste en moverse desde un nodo hacia uno de sus vecinos conectados por una arista.

Ejemplo:

```text
Solanda → El Recreo
```

### 2.5 Costos

Cada arista tiene un peso. Ese peso representa un costo combinado:

```text
costo = distancia aproximada + tráfico + dificultad de circulación
```

Por ejemplo:

```text
La Marín → Cumbayá = 30
La Marín → La Floresta = 8
La Floresta → Cumbayá = 12
```

Esto permite crear casos en los que una ruta aparentemente directa no es necesariamente la más barata.

---

## 3. Archivos principales

### 3.1 `graph_data.py`

Contiene:

- Los nodos del grafo.
- Las coordenadas ficticias de cada nodo.
- Las aristas.
- Los costos.
- La justificación de cada peso.
- Los casos preparados de prueba.
- Los perfiles de tráfico.

La función más importante es:

```python
build_graph(profile_name="Normal")
```

Esta función construye el grafo como diccionario de adyacencia.

Ejemplo de estructura interna:

```python
graph["Solanda"]["El Recreo"] = 9
```

Esto significa que desde Solanda se puede ir a El Recreo con costo 9.

---

### 3.2 `algorithms.py`

Contiene la implementación de:

```python
ucs()
gbfs()
astar()
```

Los tres algoritmos usan una función general llamada:

```python
priority_search()
```

Esta función recibe el tipo de algoritmo y cambia la prioridad usada en la cola.

---

### 3.3 `visualization.py`

Genera la visualización del grafo con Plotly.

La función principal es:

```python
make_graph_figure()
```

Esta función dibuja:

- Nodos.
- Aristas.
- Pesos.
- Ruta encontrada.
- Nodo inicial.
- Nodo objetivo.
- Nodos explorados.

---

### 3.4 `app.py`

Es el archivo principal de la interfaz. Hace lo siguiente:

1. Carga el grafo.
2. Lee el origen y destino seleccionados.
3. Ejecuta UCS, GBFS y A\*.
4. Muestra la tabla comparativa.
5. Dibuja tres espacios divididos, uno por cada algoritmo.
6. Muestra la frontera o cola de prioridad.
7. Verifica admisibilidad y consistencia de la heurística.

---

## 4. Funcionamiento de la cola de prioridad

Los tres algoritmos usan una cola de prioridad con `heapq`, igual que en el notebook base.

La cola guarda elementos de esta forma:

```python
(prioridad, contador, nodo, costo_acumulado)
```

Donde:

- `prioridad`: valor que decide qué nodo se expande primero.
- `contador`: evita empates problemáticos en la cola.
- `nodo`: estado actual.
- `costo_acumulado`: valor de `g(n)`.

---

## 5. UCS

UCS significa Uniform Cost Search.

Su prioridad es:

```text
p(n) = g(n)
```

Donde `g(n)` es el costo acumulado desde el origen hasta el nodo actual.

### Cómo decide UCS

UCS siempre expande el nodo con menor costo acumulado.

Ejemplo:

```text
Si en la frontera están:
A con g=10
B con g=5
C con g=15
```

UCS expande primero B, porque tiene el menor costo acumulado.

### Ventaja

Encuentra la ruta más barata si todos los costos son positivos.

### Limitación

Puede expandir más nodos que A\*, porque no usa información sobre la cercanía al objetivo.

---

## 6. GBFS

GBFS significa Greedy Best-First Search.

Su prioridad es:

```text
p(n) = h(n)
```

Donde `h(n)` es la estimación de cercanía desde el nodo actual hasta la meta.

### Cómo decide GBFS

GBFS solo mira qué nodo parece más cercano al destino.

Ejemplo:

```text
Si en la frontera están:
A con h=10
B con h=3
C con h=8
```

GBFS expande primero B, aunque llegar a B haya sido caro.

### Ventaja

Suele ser rápido porque se dirige directamente hacia la meta.

### Limitación

No garantiza la ruta más barata porque ignora `g(n)`.

---

## 7. A\*

A\* combina UCS y GBFS.

Su prioridad es:

```text
f(n) = g(n) + h(n)
```

Donde:

- `g(n)` es el costo acumulado desde el origen.
- `h(n)` es la estimación desde el nodo actual hasta la meta.
- `f(n)` es la prioridad total.

### Cómo decide A\*

A\* prefiere nodos que tengan buen costo acumulado y además estén cerca de la meta.

Ejemplo:

```text
Nodo A: g=10, h=5, f=15
Nodo B: g=4, h=14, f=18
Nodo C: g=8, h=3, f=11
```

A\* expande primero C, porque tiene menor `f(n)`.

### Ventaja

Si la heurística es admisible y consistente, A\* encuentra la ruta óptima y normalmente expande menos nodos que UCS.

---

## 8. Heurística del proyecto

La heurística usada es distancia euclidiana entre coordenadas ficticias del mapa.

Fórmula:

```text
h(n) = sqrt((x_meta - x_n)^2 + (y_meta - y_n)^2) × 2.0
```

El factor 2.0 se usa para que la estimación sea conservadora.

La aplicación verifica automáticamente:

### 8.1 Admisibilidad

Una heurística es admisible si:

```text
h(n) ≤ costo real óptimo desde n hasta la meta
```

Es decir, no debe sobreestimar.

### 8.2 Consistencia

Una heurística es consistente si para toda arista se cumple:

```text
h(u) ≤ c(u,v) + h(v)
```

Esto significa que la estimación respeta la desigualdad triangular del grafo.

---

## 9. Caso principal donde GBFS falla

El caso preparado más importante es:

```text
Solanda → Tumbaco
```

Una posible comparación es:

```text
UCS:  Solanda → El Recreo → La Marín → La Floresta → Cumbayá → Tumbaco
GBFS: Solanda → El Recreo → La Marín → Cumbayá → Tumbaco
A*:   Solanda → El Recreo → La Marín → La Floresta → Cumbayá → Tumbaco
```

### Por qué GBFS falla

Cuando GBFS llega a La Marín, ve que Cumbayá está más cerca de Tumbaco que La Floresta. Entonces elige Cumbayá directamente.

El problema es que la arista:

```text
La Marín → Cumbayá
```

Tiene costo alto.

En cambio, la ruta:

```text
La Marín → La Floresta → Cumbayá
```

puede ser más barata aunque tenga un paso adicional.

Por eso GBFS puede escoger una ruta que parece buena por cercanía, pero es peor en costo total.

---

## 10. Métricas mostradas en la interfaz

Cada algoritmo muestra:

### Ruta encontrada

Secuencia de nodos desde origen hasta destino.

Ejemplo:

```text
Solanda → El Recreo → La Marín → La Floresta → Cumbayá → Tumbaco
```

### Costo total

Suma de los pesos de las aristas usadas.

### Número de pasos

Cantidad de aristas recorridas.

### Nodos generados

Cantidad de nodos que entraron a la frontera.

### Nodos expandidos

Cantidad de nodos sacados de la frontera para analizar sus vecinos.

### Tiempo aproximado

Tiempo de ejecución del algoritmo en milisegundos.

### Orden de expansión

Secuencia de nodos que el algoritmo fue expandiendo.

### Frontera / cola de prioridad

Tabla que permite explicar la traza. Muestra:

- Iteración.
- Nodo expandido.
- Valor `g(n)`.
- Valor `h(n)`.
- Valor `f(n)`.
- Prioridad usada.
- Vecinos generados.
- Frontera antes de expandir.
- Frontera después de expandir.

---

## 11. Cómo explicar la demo

Para defender el proyecto en clase, puedes explicar así:

1. El problema se representa como un grafo ponderado.
2. Cada nodo es un sector de Quito.
3. Cada arista es una conexión vial.
4. Cada peso representa costo de traslado.
5. UCS busca la ruta con menor costo acumulado.
6. GBFS busca la ruta que parece más cercana a la meta.
7. A\* combina costo acumulado y cercanía estimada.
8. La tabla de frontera demuestra qué nodo se expandió y por qué.
9. El caso Solanda → Tumbaco demuestra que GBFS puede fallar.
10. La heurística se valida con admisibilidad y consistencia.

---

## 12. Frase corta para exposición

Este proyecto compara tres algoritmos de búsqueda aplicados a rutas en Quito. UCS prioriza el costo acumulado, GBFS prioriza la cercanía estimada al destino y A\* combina ambos criterios. La comparación muestra que GBFS puede tomar una mala decisión cuando una ruta parece cercana, pero tiene mayor costo real.
