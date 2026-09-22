# Planta Pilauco — plano interactivo

Plano interactivo de la vivienda (proyecto de permiso de edificación), pensado para
consultarlo en obra desde el teléfono. Incluye **nivel 1 y nivel 2**, y se cambia de
planta desde la barra de arriba.

👉 **Ver el plano:** https://toledobrintrup.github.io/Pilauco/

## Qué se puede hacer

- **Nivel 1 / Nivel 2** — cambia de planta. Las dos están montadas en el mismo sistema de
  coordenadas, así que si estás con zoom en un punto y cambias de nivel, el dibujo no se
  mueve: ves exactamente lo que hay arriba o abajo de donde estabas.
- **Versión 1 / Versión 2** (sólo nivel 2) — alterna entre la distribución vigente y la
  alternativa sin oficinas.
- **Capas** — recintos, medidas, puertas y ventanas, mobiliario y ejes se prenden y apagan por separado.
- **Medir** — toca el punto A y luego el punto B: la punta se ajusta sola a las esquinas de muro
  y muestra la distancia en centímetros (con Δx y Δy si la medida es diagonal).
- **Tocar un recinto** — abre su ficha: caja, superficie, perímetro y el largo de cada tramo con sus coordenadas.
- **Pellizcar** para acercar, **arrastrar** para moverse, **Ajustar vista** para volver al encuadre completo.

En el teléfono, la lista de recintos vive en la hoja inferior: se sube tocando la barra
"Recintos y medidas" y se baja al elegir un recinto.

## Qué trae cada planta

| | Recintos | Sup. interior útil | Envolvente |
|---|---|---|---|
| **Nivel 1** | 9 | 307,95 m² | 21,90 × 21,78 m |
| **Nivel 2** (versión 1) | 15 | 321,71 m² | 17,90 × 21,77 m |
| **Nivel 2** (versión 2) | 15 | 322,71 m² | 17,90 × 21,77 m |

En el nivel 1, **estar 1, comedor y hall de acceso son un solo recinto de 128,72 m²**:
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

Base: plano L3 PLARQ2 (Planta Arquitectura Nivel 2, GVArq, dic. 2025, esc. 1:50).

## Archivos

- `index.html` — la página completa, sin dependencias: geometría, datos y lógica de las dos plantas en un solo archivo.
- `fuente/nivel1/` — scripts que extraen la planta del nivel 1 desde el PDF, con las decisiones documentadas.
- `fuente/planta-nivel2-proyecto.zip` — proyecto del nivel 2: pipeline de extracción (Python) y datos JSON.

Los **PDF originales no están en el repositorio**: su viñeta lleva RUT, teléfono y correo.
