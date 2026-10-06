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
- **Pernos Nelson Ø19 × 5"** según la indicación del ingeniero (consulta del 05-10-2026): van en las
  vigas receptoras, las perpendiculares a las planchas, en los valles de la placa. Sus hojas no dan la
  separación, así que el modelo pone uno en cada valle: 610 pernos (la cotización pide 850).
- **Alzaprimas** con el criterio del ingeniero: luz máxima sin apoyo 1,87 m; cada vano entre vigas
  receptoras se divide en espacios iguales y entre espacio y espacio va una línea: 17 líneas, que en
  terreno son 25 tramos de solera porque algunas pasan bajo una viga.
  Falta que el ingeniero confirme si las alzaprimas eran para la placa o para las vigas: su ejemplo habla de
  6,88 m "entre pilar y pilar".
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
   del C en el perímetro (5 cm del borde) y hasta 5 mm del eje de la viga donde un área toca a otra; se
   ponen cada 95 cm (avance útil) desde un borde (se prueban los dos y queda el reparto con menos
   piezas); la última va cortada. Una franja de menos de 10 cm sobre el ala de una viga no lleva placa.
6. **Pernos y alzaprimas.** `generar_losa_js.py` busca, para cada plancha, las vigas perpendiculares que
   pasan bajo al menos la mitad de su ancho (los tramos seguidos de una misma viga cuentan como una línea)
   y pone un perno en cada valle que las cruza (los valles salen de la sección de la ficha, medidos desde el
   borde de la plancha entera aunque esté cortada). Sobre una misma viga, los candidatos a menos de 12 cm son
   el mismo valle y llevan un solo perno, venga de un área o de otra; el borde del perno queda al menos a
   2,5 cm de la cara de los pilares. "Uno por valle" es un criterio del modelo: las hojas del ingeniero dicen
   que van en los valles pero no cada cuánto; si especificó otra separación, se cambia ahí.
   Las líneas de alzaprimas se cortan donde pasan bajo una viga paralela a las planchas.
   Dos revisiones independientes recontaron pernos y alzaprimas y los dibujaron sobre el plano.
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
- `generar_losa_js.py` — escribe `losa.js`: `python3 generar_losa_js.py losa.json placa.json ../../losa.js textos.json` (`textos.json` trae las diferencias y notas que muestra la página).

La ficha técnica, el plano y la foto marcada no están en el repositorio (el plano lleva datos
personales en la viñeta). Espesor: el plano dice e = 14,35 cm (placa 6,35 + 8 de hormigón); el detalle
del ingeniero del 05-10-2026, posterior, la acota en 15 cm, la altura del perfil C, y es la que usa el modelo.
