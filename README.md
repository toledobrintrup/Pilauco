# Planta Pilauco — plano interactivo

Plano interactivo de la vivienda (proyecto de permiso de edificación), pensado para
consultarlo en obra desde el teléfono. Incluye **nivel 1 y nivel 2**, y se cambia de
planta desde la barra de arriba. Desde ahí también se entra a una **vista 3D** con los
dos niveles a su altura real.

👉 **Ver el plano:** https://toledobrintrup.github.io/Pilauco/
👉 **Vista 3D:** https://toledobrintrup.github.io/Pilauco/3d.html

## Qué se puede hacer

- **Nivel 1 / Nivel 2** — cambia de planta. Las dos están montadas en el mismo sistema de
  coordenadas, así que si estás con zoom en un punto y cambias de nivel, el dibujo no se
  mueve: ves exactamente lo que hay arriba o abajo de donde estabas.
- **Ejes del otro nivel** — capa aparte, en violeta: dibuja la grilla de ejes de la otra
  planta sobre la que estás viendo, como referencia. Se apaga con su propio chip.
- **Versión 1 / Versión 2** (sólo nivel 2) — alterna entre la distribución vigente y la
  alternativa sin oficinas.
- **Capas** — recintos, medidas, puertas y ventanas, mobiliario y ejes se prenden y apagan por separado.
- **Medir** — toca el punto A y luego el punto B: la punta se ajusta sola a las esquinas de muro
  y muestra la distancia en centímetros (con Δx y Δy si la medida es diagonal).
- **Tocar un recinto** — abre su ficha: caja, superficie, perímetro y el largo de cada tramo con sus coordenadas.
- **Pellizcar** para acercar, **arrastrar** para moverse, **Ajustar vista** para volver al encuadre completo.

En el teléfono, la lista de recintos vive en la hoja inferior: se sube tocando la barra
"Recintos y medidas" y se baja al elegir un recinto.

## Vista 3D

Un primer modelo volumétrico: cada recinto extruido a su altura real (**3,46 m por piso**,
dato tomado del plano de estructura — es el primer número de altura que tiene el proyecto,
hasta ahora todo era planta). Nivel 1 abajo, Nivel 2 arriba, un techo esquemático encima.

- **Arrastrar** gira el modelo, **rueda** acerca, **clic derecho** desplaza.
- Casilleros para mostrar u ocultar cada nivel y el techo.
- **Separar pisos** — un deslizador que levanta el Nivel 2 en el aire para ver los dos
  pisos a la vez sin que uno tape al otro.

El techo es deliberadamente esquemático (una tapa plana): la cubierta real tiene pendiente
y unas torres de arriostramiento que no se pudieron leer con certeza del plano de estructura
(ver `fuente/ingenieria/README.md`) — se prefirió dejarlo marcado como pendiente de revisar
antes que adivinar. Es un primer paso hacia un modelo más completo para diseño de interiores,
no el modelo final.

## Qué trae cada planta

| | Recintos | Sup. interior útil | Envolvente |
|---|---|---|---|
| **Nivel 1** | 10 | 306,99 m² | 21,90 × 23,36 m |
| **Nivel 2** (versión 1) | 15 | 321,71 m² | 17,90 × 21,77 m |
| **Nivel 2** (versión 2) | 15 | 322,71 m² | 17,90 × 21,77 m |

En el nivel 1, **living, comedor, hall de acceso y galería son un solo recinto de 143,33 m²**:
en el plano no hay muro que los separe, así que se miden juntos y se rotula cada zona
donde la nombra el arquitecto, sin inventar divisiones. El acceso cubierto se dibuja y
rotula, pero no se mide como recinto. La terraza cubierta exterior del norte y sus
pilares quedaron fuera del dibujo.

## Criterio de las medidas

- Medidas **en centímetros**, entre caras de muro terminadas.
- Superficies calculadas del polígono interior exacto.
- Envolvente exterior 1.790 × 2.177 cm (17,90 × 21,77 m), cara exterior a cara exterior.
- **Muros perimetrales de 25 cm** con la cara exterior fija en la línea de fachada, y
  tabiques interiores de 15 cm centrados en su eje, en las dos plantas. Mantener fija la
  cara exterior significa que la envolvente del permiso no cambia y que cada recinto que
  toca fachada pierde espesor por ese lado.
- En la Versión 2 el muro dormitorio/baño está **estimado** (eje y = 557) y se ajusta después.
- **Puertas:** 0,90 en todo lo que pisa gente, 0,80 en closets, en las dos plantas. En el
  nivel 1 se rediseñaron posiciones (jamba a 15 cm de la esquina en servicio/baño,
  centradas en representativas/exteriores). En el nivel 2 se ajustaron las que ya traía el
  plano del arquitecto con el mismo ancho; la posición sólo se corrigió donde sobraba
  margen confirmado contra el muro real.

Base: plano L3 PLARQ2 (Planta Arquitectura Nivel 2, GVArq, dic. 2025, esc. 1:50).

## Archivos

- `index.html` — el plano: geometría, lógica e interfaz de las dos plantas en un solo archivo.
- `3d.html` — la vista 3D (Three.js vía CDN, sin paso de compilación).
- `data.js` — los datos de ambas plantas (`DATA_N1`, `DATA_N2`), compartidos por `index.html` y `3d.html`: una sola fuente, nada duplicado.
- `fuente/nivel1/` — scripts que extraen la planta del nivel 1 desde el PDF, con las decisiones documentadas.
- `fuente/planta-nivel2-proyecto.zip` — proyecto del nivel 2: pipeline de extracción (Python) y datos JSON.
- `fuente/ingenieria/` — qué se sacó de los planos de estructura (altura de piso, calce de ejes) y qué se dejó fuera.

Los **PDF originales no están en el repositorio**: su viñeta lleva RUT, teléfono y correo.
