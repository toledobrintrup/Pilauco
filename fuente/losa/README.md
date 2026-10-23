# Losa colaborante del entrepiso

`losa.html` (en la raíz) muestra la losa del entrepiso pieza por pieza, y `3d.html` la trae como
capa ("Losa colaborante"). Los datos están en `losa.js`, que se genera aquí.

## Qué hay

- **Marco perimetral de perfil C 150×50×3** (canal sin pestañas, 150 de alto, alas de 50, 3 mm) en
  todo el borde de la losa, incluido el hueco de la escalera. Va sobre el ala superior de la viga de
  borde, con el alma vertical en el borde (cara exterior del ala de la viga) y las alas hacia la losa.
  Su alto, 150 mm, es el espesor de la losa que se va a hacer.
- **Placa colaborante Instadeck 0,8** en las 8 áreas marcadas en obra, con la sección real de la
  ficha (sacada del dibujo vectorial, escalada con la cota de 950 mm de avance útil) y la dirección
  de cada paño según el plano del ingeniero.
- **Pernos Nelson Ø19 × 5"** según el ingeniero: van en las vigas receptoras, las perpendiculares a las
  planchas, en los valles de la placa (consulta del 05-10-2026). Su lámina 11 (07-10-2026) marca dónde van
  con 215 puntos sobre 46 vigas. Los puntos son un esquema, no la cantidad (lo aclaró el dueño el 07-10-2026):
  cada viga marcada lleva un perno en todos sus valles. 5 trozos cortos de viga receptora sin ningún punto (12 valles)
  también llevan, por decisión del dueño. Son 596 pernos (la cotización pide 850), uno por valle; los 644 valles
  completos que cruzan vigas receptoras cuentan por separado los dos lados de las juntas a tope.
- **Alzaprimas** con el criterio del ingeniero: luz máxima sin apoyo 1,87 m; cada vano entre vigas
  receptoras se divide en espacios iguales y entre espacio y espacio va una línea: 17 líneas, que en
  terreno son 25 tramos de solera porque algunas pasan bajo una viga.
  Gabriel (23-10-2026): el 1,87 m es la luz de la placa sin apoyo (entre vigas o entre viga y línea); las vigas no se
  alzapriman.
- **Alzaprimas arrendadas** (`alzaprimas.html`, borrador para el ingeniero, 23-10-2026): en las mismas 17 líneas,
  puntales metálicos de arriendo (regulables con tornillo central, placa base y cabezal en U) con solera de dos 2x4 de
  canto (Gabriel: "serán las que se arriendan, con un tornillo central"). La separación de puntales de cada línea
  (55 a 80 cm) la manda la flexión de la solera (cálculo y revisión, `alzaprimas.json`); la carga máxima por puntal
  fija la capacidad que hay que pedir a la empresa. `losa.html` toma de `alzaprimas.js` los tramos y puntales de cada
  línea (planta, tabla y 3D) y en su sección 05 resume y enlaza a la pestaña.
- **Malla ACMA C-188** (detalle del ingeniero) con su cara superior a 2,5 cm de la cara de la losa: paneles de
  2,60 × 5,00 m (18 barras Ø6 de 5,00 m y 33 de 2,60 m, a 15 cm), traslapados según la regla de ACMA (NCh 219: 4
  alambres de cada malla y 30 cm entre los últimos; 50 cm en los costados y 65 en las puntas; el ingeniero no lo
  dio), recortados a 3 cm del borde y a 2 cm de los pilares: 50 paneles (43 con el traslapo de 30 cm de Armacero).
- **Hormigón** hasta los 15 cm: llena los valles de la placa y sube 8,65 cm sobre la cresta (≈ 50 m³).

## Cómo se armó

1. **Paños del plano.** La planta de estructura nivel 1 (rev. 08-04-2026) tiene 31 rótulos "Losa
   Instadek e=14,35 cm", cada uno con su símbolo de doble flecha. Cada paño se ubicó entre las vigas
   que lo cierran y su dirección se leyó del símbolo.
2. **Áreas de obra.** Las 8 áreas marcadas con destacador en el plano impreso se registraron contra
   la grilla de ejes y se asignaron a esos paños.
3. **Contorno y marco.** El borde de la losa va en la cara exterior del ala superior de las vigas de
   borde (`estructura.js`); el marco C sigue ese contorno.
4. **Conciliación y verificación.** Las tres fuentes se juntaron en `losa.json` y dos revisores
   independientes lo dibujaron encima del plano y de la foto para buscar errores.
5. **Planchas.** `generar_losa_js.py` reparte las planchas de cada área: llegan hasta la punta del ala
   del C en el perímetro (5 cm del borde) y hasta el eje de la viga donde un área toca a otra (a tope); se
   ponen cada 95 cm (avance útil) desde un borde (se prueban los dos y queda el reparto con menos
   piezas); la última va cortada. Una franja de menos de 10 cm sobre el ala de una viga no lleva placa.
6. **Pernos y alzaprimas.** `pernos_desde_plano.py` saca los pernos de la lámina 11 (no está en el repositorio:
   la viñeta trae datos personales): cada perno es un punto negro de 12 pt; se buscan por el relleno (la planta se
   pasa a imagen y se erosiona: solo quedan los puntos sólidos; uno no tiene círculo de contorno) y se ubican con
   las burbujas de los ejes, descartando las que están dibujadas fuera de su eje. Quedan en `pernos_ingeniero.json`.
   `generar_losa_js.py` busca, para cada plancha, las vigas perpendiculares que pasan bajo al menos la mitad de su
   ancho (los tramos seguidos de una misma viga cuentan como una línea) y marca cada valle que las cruza (los valles
   salen de la sección de la ficha, medidos desde el borde de la plancha entera aunque esté cortada); sobre una misma
   viga, los candidatos a menos de 12 cm son el mismo valle, y el borde del perno queda al menos a 2,5 cm de la cara
   de los pilares. El perno va al centro del valle (entre las dos mitades que separa el rigidizador, o entre las de
   dos planchas en la unión), con una perforación de Ø35 mm alrededor; donde la plancha termina sobre la viga (en el
   borde, contra el C; entre dos áreas, en el eje) se corre hacia su plancha para que la perforación no corte el ala
   del C ni la plancha vecina, y su centro queda a 31,7 mm o más del borde del ala (AWS D1.1). Cada perno lleva el
   tipo de encuentro de la placa con su viga (borde, mismo sentido, ortogonal o corrida). Después pone un perno en cada valle
   de cada viga receptora (las que tienen puntos en la lámina y, por decisión del dueño, los 5 trozos cortos sin puntos), a 31,7 cm (más de 4 diámetros, AISC 360-16 I8.2d). Donde un
   pilar del nivel 2 tapa un valle no va perno; en las juntas a tope va un perno por valle (los valles de las dos
   planchas quedan a 2 a 4 cm), al lado de la viga donde el ingeniero dibujó sus puntos. Donde se cruzan dos vigas y
   los valles de la esquina dan dos pernos a menos de 4 diámetros, queda uno (2 cruces, en E4 con los ejes 3 y 4). Sin `pernos_ingeniero.json`, pone uno en cada valle.
   Las líneas de alzaprimas se cortan donde pasan bajo una viga paralela a las planchas.
   Dos extracciones independientes de la lámina (por relleno y por imagen) dieron los mismos 215 puntos.
7. **Malla.** `generar_losa_js.py` reparte paneles en filas con su traslapo sobre el contorno de la losa corrido 3 cm
   hacia adentro; prueba las dos orientaciones, las cuatro esquinas de partida y filas desfasadas, y deja el reparto
   con menos paneles. Después lo corre hasta 14 cm en cada sentido, sin sumar paneles, para que las barras pasen lo
   más lejos posible de las cabezas de los pernos. Cada barra se recorta al contorno y alrededor de los pilares (con 2 cm de holgura); quedan en
   `losa.js` como trozos (posición, desde, hasta) por panel.
8. **Pilares del nivel 2.** 30 pilares nacen sobre las vigas y atraviesan la losa (19 en el borde, 11
   adentro). Donde tocan el alma del C, el C se corta en piezas; en el eje 5 y en A1 el alma pasa por
   fuera y solo se recortan las alas. Cada plancha anota qué pilares la tocan.

## Archivos

- `losa.json` — áreas (polígono, dirección, paños del plano, lo anotado en obra), perímetro, tramos
  del marco y hueco de escalera, en cm en el marco de la app.
- `placa.json` — sección de la placa y tablas de la ficha; se arma con `placa_desde_ficha.py`.
- `pernos_ingeniero.json` — pernos de la lámina 11 en cm; se arma con `pernos_desde_plano.py "Plano 11, ubicacion pernos.pdf" pernos_ingeniero.json`.
- `alzaprimas.json` — diseño de las alzaprimas: puntal metálico de arriendo (medidas típicas y capacidad: SUPUESTO
  hasta tener la ficha de la empresa), solera de dos 2x4, cargas, alturas (3,71 m de trabajo), base, la separación de
  puntales de cada línea con su porqué (cálculo con NCh 1198 y revisión independiente, 23-10-2026), datos, supuestos y
  lo que falta confirmar.
- `generar_alzaprimas_js.py` — escribe `alzaprimas.js` (lo leen `alzaprimas.html` y `losa.html`) desde `losa.js`,
  `estructura.js` y `alzaprimas.json`; desde la raíz: `python3 fuente/losa/generar_alzaprimas_js.py`. Recorta cada
  tramo de solera 1 cm antes del ala de la viga, reparte los puntales (el primero a 15 cm de cada punta, los demás
  iguales y a no más de la separación de la línea), ubica las uniones de la solera (piezas de 3,20 m, las dos sobre el
  mismo puntal, nunca en el 1.º ni el 2.º desde cada punta), calcula la carga por puntal (1,25·w·a de diseño, con el
  factor de la revisión tomando la línea como apoyo rígido; y la reacción de cada puntal con su ubicación real, que
  tiene que quedar bajo la de diseño) y la capacidad a pedir, el D/C de la solera y su separación máxima, el apoyo de
  la placa comparado con la ficha (3 o más vanos y 2), la base (radier, tablón sobre piso terminado, durmiente doble
  sobre terreno) y las cantidades (puntales con reserva, aparte los del área 1 si apoyan en terreno; 2x4, tablas de la
  base, cruces de arriostre supuestas y clavos). Correrlo de nuevo cada vez que cambie `losa.js`.
- `generar_losa_js.py` — escribe `losa.js`: `python3 generar_losa_js.py losa.json placa.json ../../losa.js textos.json` (`textos.json` trae las diferencias y notas que muestra la página).

La ficha técnica, el plano y la foto marcada no están en el repositorio (el plano lleva datos
personales en la viñeta). Espesor: el plano dice e = 14,35 cm (placa 6,35 + 8 de hormigón); el detalle
del ingeniero del 05-10-2026, posterior, la acota en 15 cm, la altura del perfil C, y es la que usa el modelo.
