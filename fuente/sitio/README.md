# Terreno de Casa Pilauco (sitio.js)

Datos del lote, el gimnasio, el estudio con búnker, el estacionamiento futuro y el urbanismo que se dibujan
en la Vista 3D (`sitio3d.js`). Todo en cm, en el marco de la app: X hacia el oriente (eje 6 de la casa),
Y hacia el sur (eje A), Z hacia arriba con Z = 0 en el piso terminado del nivel 1 (NPT +0,70 del emplazamiento).

## Fuentes (ninguna entra al repositorio: las viñetas traen datos personales)

- **L1. EMPLAZAMIENTO.29.12.2025.pdf** (arquitecto, 1:200): lote 6 "a11" con sus deslindes, cierros y acceso,
  el edificio B (estudio, versión del arquitecto), el estacionamiento H, el gimnasio C, senderos, grava y pasto.
  Calibración al marco de la app: `cm = (pt − t) / s`, con `s = 0,14172 pt/cm` (1:200 exacto, confirmado con los
  deslindes 61,09 / 90,50 / 87,64 m), `tx = 322,48`, `ty = 728,12`, sin rotación. Se ajustó por correlación de los
  muros de la casa con la lámina L2 y se comprobó mirando la superposición.
- **L11.GIM.29.12.2025.pdf** (arquitecto, 1:50): planta, cubierta y elevaciones del gimnasio (902 × 700 en L,
  cielo +297 a +324, cubierta +345/+391, 2,20°, aleros 981 × 1185) y su distancia a cada deslinde.
- **Planta del estudio** (Gabriel, 2026-10-11): 10050 × 15250 mm con la cafetería y cowork + sala de grabación,
  la escalera al búnker, el estudio de producción, baño y bodega. Alturas: 4,00 m interiores; búnker 2,80 m
  bajo la cafetería con las mismas medidas; techo con la pendiente de la casa (3,5 %).
- **Foto y video de dron** (agosto y octubre 2026): lo que existe de verdad (piscina, jacuzzi, laguna, sendero
  en U, radier del gimnasio, galpón de obra, caseta de bombas, portón), rectificados con las esquinas del lote.

## Archivos

- `estudio.json`: la planta del estudio en su marco local, con cada dato y cada supuesto marcados.
- `sitio.json`: el terreno armado (lote, cierros, acceso, gimnasio, estacionamiento, urbanismo, lo real) y el
  anclaje del estudio (`estudio_origen`, esquina noroeste en cm app).
- `generar_sitio_js.py`: arma `sitio.js` (DATA_SITIO) desde los dos JSON.
- `datos/`: extracciones intermedias.

Regenerar: `cd fuente/sitio && python3 generar_sitio_js.py sitio.json estudio.json ../../sitio.js`.
`sitio.js` no se edita a mano.

## Hallazgo: la casa del emplazamiento está corrida

El bloque de la vivienda dibujado en L1 queda 3,28 m al sur de la casa construida (comparado con los muros de la
lámina L2 por correlación, con los ejes de las fundaciones en la ortofoto de topografía y con la losa en la foto de
dron; en x calza). El lote, los cierros, el acceso y el gimnasio de L1 sí calzan con la realidad (el cierro sur cae
sobre sus postes reales a ±20 cm), así que el modelo los usa tal cual; el estacionamiento H y el edificio B se dibujan
donde el arquitecto los puso respecto del lote. Pendiente preguntarle al arquitecto.

## Supuestos abiertos (marcados también en las fichas del 3D)

- Terreno plano en Z = −70 cm (NPT +0,70 de la casa sobre el ±0,00 del acceso).
- Estudio: el búnker centrado en la excavación que se ve en la foto de dron (Gabriel, 2026-10-11), la cafetería
  hacia el patio (norte) y el estudio hacia el camino (sur); losa terminada 50 cm sobre el NPT de la casa; cielo de
  4,00 m al norte que sube a 4,53 m al sur (datos de Gabriel). Aleros de 80 (N-S) y 52 (E-O) del ingeniero. Supuestos: muros de 25 cm, losa de
  15 cm sobre el búnker, excavación digitalizada a ±30 cm. Estructura y fundaciones las define el ingeniero.
- Gimnasio con su piso 10 cm sobre el terreno (NTN −10 de su lámina).
