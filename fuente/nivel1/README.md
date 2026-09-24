# Nivel 1 — cómo se extrajo la geometría

Scripts que reconstruyen la planta del nivel 1 desde el PDF original
(`L2.PLARQ.29.12.2025.pdf`, lámina 2/11 de GVArq). **El PDF no está en el repositorio**:
su viñeta lleva RUT, teléfono y correo, así que se deja fuera. Ponlo junto a los scripts
para poder correrlos.

```bash
pip install pymupdf numpy opencv-python-headless shapely
python3 n1_extract.py   # capas de dibujo y textos del PDF -> cm
python3 n1_walls.py     # muros como polígonos (capa de grosor 1,28)
python3 n1_vanos.py     # vanos: empareja extremos de muro enfrentados
python3 n1_final.py     # recintos, espesores, métricas y n1_data.json (lo que consume la página)
```
`n1_engrosar.py` es el módulo que normaliza espesores; lo llama `n1_final.py`.

El bloque `const DATA_N1 = …` de `index.html` es el contenido de `n1_data.json`.

## Decisiones que no son obvias

- **Origen y escala.** `X0=326.70, Y0=733.46` puntos PDF, escala 1:50 (0,56705 pt/cm).
  Se fijaron haciendo calzar los ejes 1, 2, 3 y 5 del nivel 1 con los mismos del nivel 2:
  el error queda bajo 0,5 cm en los cuatro. Por eso las dos plantas se pueden superponer
  y cambiar de nivel no mueve el dibujo.
- **Sólo la casa.** La lámina trae además la planta del nivel −1 y otra construcción, a la
  derecha. Se descarta todo lo que esté a la derecha de x = 1780 pt.
- **El cerramiento poniente es vidrio**, no muro: por eso el relleno de recintos usa muros
  + ventanas + puertas, y no sólo la capa de muros.
- **La capa de puertas es imprescindible** para cerrar los vanos que el emparejamiento de
  extremos no alcanza; sin ella el relleno se escapa y quedan 4 recintos en vez de 9.
  Como contrapartida, las hojas de puerta dejan espigas en el contorno: las quita
  `quita_espigas()`, que reemplaza por el tramo recto cualquier excursión que salga de la
  línea de muro y vuelva al mismo punto (largo > 3× la recta, área < 2,5 m²).
- **Estar 1, comedor y hall de acceso son un solo recinto** porque en el plano no hay muro
  que los separe. No se inventó una división: se miden juntos y se rotula cada zona donde
  la nombra el arquitecto.
- **Espesores normalizados a 25 cm perimetral y 15 cm interior** (`n1_engrosar.py`), con el
  mismo algoritmo que `build_thick.py` del nivel 2: se sondea cada tramo de recinto, se mide
  el muro que tiene enfrente, se clasifica en perimetral o interior según si más allá hay
  otro recinto, y se corre la cara interior lo necesario. La cara exterior no se mueve: la
  envolvente sigue siendo la del permiso. Los vanos de fachada se redibujan ocupando el
  nuevo espesor para que la ventana no quede flotando dentro del muro.
- **El barrido de las puertas mordía los recintos.** El símbolo de puerta se dibuja dentro
  del recinto, así que el relleno lo rodeaba y dejaba una muesca triangular con un tramo en
  diagonal de ~1 m que no era ninguna medida real. Se elimina toda muesca que contenga un
  tramo diagonal (`quita_espigas`); un nicho de verdad es ortogonal y no se toca.
- **Muros exentos dentro de un recinto** (el arrimo del estar, la esquina del comedor) los
  absorbía el contorno exterior del relleno e inflaban el área en 0,53 m². Se restan como
  hueco del polígono.
- **La terraza cubierta exterior y sus pilares quedaron fuera** por pedido: el recorte de
  capas es sólo la casa (y > 0).
- **Como construido, no como está en el plano** (`OBRA` en `n1_final.py`): la lavandería se
  adelantó hasta el eje H y la sala de máquinas hasta el eje I1, que es la línea de pilares
  de la terraza — se cerró esa crujía. El plano de permiso las tiene a las dos en el eje H1.
  La cara interior se pone a 17,9 cm del eje, que es la relación que el propio plano usa en
  toda la fachada (eje H = 7,1 → cara interior 25,0, igual que la terraza interior). La
  sala de máquinas sobresale 177 cm al norte del rectángulo del permiso. La ventana V7 y
  los rótulos del muro viejo se corren junto con el muro.
- **La envolvente es el contorno de lo construido**, no un rectángulo: se calcula como el
  borde exterior de la unión de muros y recintos (`envPath`/`envBox`), así que sigue el
  perímetro real, con el saliente de la sala de máquinas y el acceso cubierto. Mide
  2.190 × 2.336 cm. En el nivel 2 se sigue usando el rectángulo, que ahí sí es exacto.

## Rediseño de septiembre 2026 (`rediseno()` en `n1_final.py`)

Decisiones de diseño tomadas sobre el plano, no cambios de obra todavía:

- **La terraza interior desaparece.** Justo afuera hay una terraza cubierta de ~80 m², así
  que el recinto se reparte en **oficina** (3,60 × 5,93 = 21,3 m², al poniente, con ventana
  norte y poniente) y **galería** (2,41 × 5,93 = 14,3 m², al oriente): el paso del living a la
  terraza. Tabique de 15 entre ambas con puerta de 0,90 al centro. La salida al patio pasa de
  una puerta de 72 cm a una **corredera de 2,20** centrada en la galería.
- **Franja de servicio.** Lavandería 3,40 de fondo (17,4 m²), despensa el resto (2,68 → 13,7 m²).
  El baño pierde la tina —es el baño de visitas del primer piso, sin ducha— y cede 1,76 al
  poniente para una **bodega de aseo** de 1,76 × 2,88 (5,1 m²) con puerta propia al pasillo de
  servicio (la chiflonera). El baño queda en 3,20 × 2,88 (9,2 m²) y pasa a llamarse Baño Visitas.
- El mobiliario dibujado dentro de los recintos rediseñados se quita (sofás de la terraza,
  tina, mesones bajo tabiques movidos); se redibuja cuando se definan terminaciones.
- **Bug corregido de paso:** los anillos de muro se emiten planos (exterior e interiores por
  igual). Reconstruirlos uniéndolos como sólidos rellena los huecos —la lavandería salía
  negra—. `_desde_anillos()` los ensambla por diferencia simétrica (par-impar), que es lo
  mismo que hace la página con `fill-rule: evenodd`.

## Puertas acordadas (`puertas_v1()` en `n1_final.py`)

Regla de ancho: **0,90 en todo lo que pisa gente, 0,80 sólo en closets de servicio.**
Regla de posición: en recintos de servicio y baño la **bisagra va hacia la esquina más
cercana, con la jamba a 15 cm del muro perpendicular** (la hoja abre plana contra el muro y
el marco cabe); las puertas representativas y exteriores van **centradas** en su muro. Las
jambas de
las puertas existentes salen de los arcos del PDF (bisagra = esquina del cuadrado que
forman los extremos del arco y que cae sobre el muro).

- Galería **abierta al living**: fuera el tabique vidriado y su puerta doble; la galería pasa
  a ser una zona rotulada del recinto abierto. La oficina recibe un muro sur de 15 (antes
  era la mampara).
- Galería → terraza/piscina: **doble batiente 2 × 1,00**, abre hacia afuera (nada de
  correderas por ahora, a pedido).
- Entrada principal: el vano de 1,80 ya existía; **pivotante 1,20 + paño fijo de 0,60**.
- Cocina → despensa 0,90 · cocina → lavandería **0,90 nueva** (y fuera la puerta exterior de
  la lavandería) · cocina → chiflonera 0,90 · comedor → chiflonera 0,90 · chiflonera → baño
  visitas 0,90 · chiflonera → bodega de aseo 0,80 · chiflonera → acceso cubierto oriente 0,90.
- Sala de máquinas: **una hoja de 1,00** centrada en el muro poniente del saliente (hacia la
  terraza norte). Bodega exterior: **doble 2 × 0,80** centrada en el muro sur (al acceso
  cubierto oriente). Ambas abren hacia afuera; los vanos de la fachada oriente se rellenan.
- Paso cocina → living (2,25) centrado en el eje del hall de acceso (x = 8,30).
- Sin tocar: puerta doble de la cocina a la terraza norte (2 × 0,96), el paso cocina–living,
  y las aberturas vidriadas del living y el comedor (van con las ventanas).
