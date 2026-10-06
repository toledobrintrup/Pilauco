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
- Pendiente: pernos Nelson, malla de retracción y hormigón.

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
6. **Pilares del nivel 2.** 30 pilares nacen sobre las vigas y atraviesan la losa (19 en el borde, 11
   adentro). Donde tocan el alma del C, el C se corta en piezas; en el eje 5 y en A1 el alma pasa por
   fuera y solo se recortan las alas. Cada plancha anota qué pilares la tocan.

## Archivos

- `losa.json` — áreas (polígono, dirección, paños del plano, lo anotado en obra), perímetro, tramos
  del marco y hueco de escalera, en cm en el marco de la app.
- `placa.json` — sección de la placa y tablas de la ficha; se arma con `placa_desde_ficha.py`.
- `generar_losa_js.py` — escribe `losa.js`: `python3 generar_losa_js.py losa.json placa.json ../../losa.js textos.json` (`textos.json` trae las diferencias y notas que muestra la página).

La ficha técnica, el plano y la foto marcada no están en el repositorio (el plano lleva datos
personales en la viñeta). Espesor: el plano dice e = 14,35 cm (placa 6,35 + 8 de hormigón); la losa
que se va a hacer es de 15 cm, la altura del perfil C. Confirmar con el ingeniero.
