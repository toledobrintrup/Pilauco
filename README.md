# Planta Pilauco — plano interactivo

Plano interactivo de la vivienda (proyecto de permiso de edificación), pensado para
consultarlo en obra desde el teléfono. Incluye **nivel 1 y nivel 2**, una **vista 3D** con
los dos niveles a su altura real y la estructura de acero, la **losa colaborante** del
entrepiso pieza por pieza y la ficha del **tablero de básquetbol**. Se pasa de una vista a otra con el menú de arriba (pestañas en pantalla
ancha, menú desplegable en el teléfono).

👉 **Ver el plano:** https://toledobrintrup.github.io/Pilauco/
👉 **Vista 3D:** https://toledobrintrup.github.io/Pilauco/3d.html
👉 **Losa colaborante:** https://toledobrintrup.github.io/Pilauco/losa.html
👉 **Tablero:** https://toledobrintrup.github.io/Pilauco/tablero.html

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

Cada recinto extruido a su altura real (**3,46 m por piso**, dato tomado del plano de
estructura — es el primer número de altura que tiene el proyecto, hasta ahora todo era
planta). Nivel 1 abajo, Nivel 2 arriba, el techo con su pendiente real encima.

- **Arrastrar** gira el modelo, **rueda** acerca, **clic derecho** desplaza.
- Casilleros para mostrar u ocultar cada nivel, el techo y la estructura.
- **Ver estructura** — la estructura de acero completa de los planos del ingeniero, pieza
  por pieza, cada una con la sección de su perfil: pilares (HEB 160, tubos 150x150,
  cañerías Ø310), vigas de entrepiso (IPE 220 a 600), cruces de San Andrés y celosías, y la
  techumbre (cabios IPE 400, puntales, costaneras, tensores y colgadores). Cada grupo se
  prende y apaga por separado, y **tocar una pieza** muestra su perfil, dónde está y su largo.
- **Separar pisos** — un deslizador que levanta el Nivel 2 en el aire para ver los dos
  pisos a la vez sin que uno tape al otro.

El techo es de un agua (sube de norte a sur, 3,5 %), con los aleros y el quiebre que dibuja
la planta de techumbre. La estructura se extrajo de las 29 vistas de los planos y se verificó
dibujándola de vuelta sobre cada lámina original; cómo se hizo, la comparación con la lista
de materiales del ingeniero y las diferencias entre láminas están en
`fuente/ingenieria/README.md`.

## Losa colaborante

El entrepiso, pieza por pieza, sobre las vigas reales de la estructura: el **marco perimetral de
perfil C 150×50×3** (también alrededor del hueco de la escalera, cortado donde lo atraviesan los
pilares del nivel 2) y las **66 planchas Instadeck 0,8** de las 8 áreas marcadas en obra, con la
sección real de la ficha técnica y la dirección de cada paño del plano del ingeniero. Encima, los
**215 pernos Nelson** en las vigas receptoras, con la cantidad y la posición de la lámina 11 del ingeniero
(07-10-2026): cada fila que él dibuja seguida va completa a valles seguidos de su viga, al centro de cada valle, con la placa perforada (Ø35 mm, con un anillo libre
alrededor del perno) y soldado al arco directo al ala; las **17 líneas de alzaprimas** con su
criterio de 1,87 m de luz máxima sin apoyo (bajo la placa; falta que el ingeniero confirme si eran para la
placa o para las vigas); la **malla ACMA C-188** en 50 paneles traslapados según ACMA, y el **hormigón** hasta los
15 cm (≈ 50 m³). Cada capa se prende y se apaga.

- **Armado, despiece y montaje.** El despiece se anima solo o con un deslizador por pieza (hormigón,
  malla, marco, placa, pernos, separación de planchas y cada área). El montaje coloca el marco tramo
  por tramo, las planchas una por una y los pernos área por área, las alzaprimas, la malla panel por
  panel y al final se ve el vaciado del hormigón, con una línea de tiempo.
- **Navegación:** la rueda o el pellizco acercan hacia donde apunta el cursor o los dedos, doble clic
  se acerca a ese punto, y hay botones para acercar, alejar, volver al inicio y ver en planta.
- **Detalle de cada pieza:** sección del C con su peso por metro, detalle del borde sobre la viga,
  sección de la placa con las tablas de la ficha, plan de corte del C en barras de 6 m, y tabla de
  luces y alzaprimas por área según la ficha.
- **Diferencias con lo anotado en obra** (largos, cantidades y la cotización), cada una explicada.
- En la vista 3D aparece como la capa "Losa colaborante".

Cómo se armó cada parte está en `fuente/losa/README.md`.

## Pernos: instalación

`pernos.html` muestra, en 2D y en 3D, cómo se instala cada perno Nelson según cómo llega la placa a la viga: en el
borde contra el perfil C, donde se juntan planchas en el mismo sentido (a tope, con los nervios alineados), donde se
juntan planchas ortogonales (hasta tocarse, con los nervios sellados) y donde la plancha pasa corrida. Trae la
perforación de Ø35 mm con su anillo libre y la instalación paso a paso (viga, planchas, perforación, soldadura,
revisión y sellado, malla y hormigón). La placa con sus perforaciones se
arma con `placa3d.js`, que usa también la vista de la losa.

## Tablero de básquetbol

Todo el manual del aro (Dunking, de poste empotrado, 9 páginas en inglés) traducido, ordenado
y dibujado de nuevo, junto a un **3D que se mueve como el real**:

- **Control de altura** de 1,50 a 3,05 m: el brazo y la barra de tiro forman un paralelogramo,
  el tablero baja sin inclinarse, el tornillo de elevación se alarga, la manivela gira y la
  regla marca la altura sobre la escala de la barra auxiliar.
- **Armado paso a paso** (fundación y pasos 1 a 8): cada paso muestra en el 3D lo ya armado y
  destaca en naranjo lo que se agrega, con sus pernos. En pantalla ancha el 3D sigue solo al
  paso que se está leyendo.
- **Capas**: etiquetas con las letras del manual, medidas (altura del aro, alcance, distancia
  a la línea de fondo), despiece y vista bajo tierra con la fundación y el anclaje.
- **Piezas, pernería a escala y cuadratura del kit**: cuánto usa cada paso contra lo que trae
  la caja (cuadra todo), llaves necesarias y una lista para revisar la caja (queda guardada en
  el navegador).
- **Fundación y ubicación**: corte del hoyo de 80 × 80 × 80 cm con el anclaje M24, y planta
  con la línea de fondo (527 mm), el espacio libre detrás (500 mm) y el alcance (1,227 m).

El manual no trae medidas del tablero, del poste ni del brazo: se midieron en su dibujo lateral
con una escala fijada por el aro a 3,05 m, y se comprobaron contra lo que el manual sí dice (el
alcance da 1,227 m, igual al manual). El modelo se dibujó de vuelta sobre esa lámina para
verificar que calza. Qué es dato del manual y qué es medido está marcado en la página.

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
- `tablero.html` — el tablero de básquetbol: manual traducido, figuras y 3D animado, todo en un archivo.
- `losa.html` — la losa colaborante: 3D con despiece y montaje, y el detalle de cada pieza.
- `losa.js` — los datos de la losa (áreas, planchas, marco C, pilares que la atraviesan); se genera con `fuente/losa/generar_losa_js.py`.
- `pernos.html` — cómo se instalan los pernos Nelson, caso por caso, en 2D y 3D.
- `menu.js` — el menú común a todas las vistas; para sumar una vista se agrega a su lista.
- `nav3d.js` — la navegación común de los 3D: zoom hacia el cursor, doble clic, botones de inicio y planta, teclado.
- `placa3d.js` — la placa colaborante en 3D con las perforaciones de los pernos (losa y pernos).
- `fuente/losa/` — cómo se sacó la losa del plano, de las áreas marcadas en obra y de la ficha Instadeck.
- `data.js` — los datos de ambas plantas (`DATA_N1`, `DATA_N2`), compartidos por `index.html` y `3d.html`: una sola fuente, nada duplicado.
- `estructura.js` — la estructura de acero pieza por pieza (perfil y extremos de cada una) para la capa "Ver estructura" de `3d.html`; se genera desde `fuente/ingenieria/datos/modelo.json`.
- `fuente/nivel1/` — scripts que extraen la planta del nivel 1 desde el PDF, con las decisiones documentadas.
- `fuente/planta-nivel2-proyecto.zip` — proyecto del nivel 2: pipeline de extracción (Python) y datos JSON.
- `fuente/ingenieria/` — cómo se armó la estructura 3D desde los planos del ingeniero: grilla de ejes, modelo completo, herramientas para re-proyectarlo sobre las láminas y la comparación con la lista de materiales.

Los **PDF originales no están en el repositorio**: su viñeta lleva RUT, teléfono y correo. Tampoco
el manual del tablero: sus dibujos se rehicieron, no se copiaron.
