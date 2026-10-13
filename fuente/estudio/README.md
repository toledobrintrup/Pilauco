# Estudio con búnker: estructura adaptada

El ingeniero proyectó en abril de 2026 (láminas 03, 04 y 05, en iCloud `02_Ingeniería/03_Estudio Pilauco/`; no
entran al repositorio) un estudio de 11,05 × 10,25 m entre ejes con un búnker de 5,00 × 10,55 m interiores bajo
un extremo. La planta nueva de Gabriel (`fuente/sitio/estudio.json`) mide 10,05 × 15,25 m interiores, lleva el búnker bajo la
cafetería (al norte) y el techo subiendo al sur. `generar_estudio_estructura.py` arma la propuesta con el mismo
sistema del ingeniero y escribe `estudio_estructura.js` (DATA_ESTUDIO_EST):

    python3 generar_estudio_estructura.py ../sitio/estudio.json ../sitio/sitio.json ../../estudio_estructura.js

## Lo que se toma del ingeniero (dato)

Láminas (en iCloud `02_Ingeniería/03_Estudio Pilauco/` y en Descargas; nunca al repositorio): 01 PLANTA FUNDACIONES rev 0 (06-04-2026)
y rev 1 (27-04-2026); 02 rev G (07-04); 03 rev G/H; 04 rev G/H/I (11-04); 05 rev H (11-04). Lo que manda: 01 rev 1, 02 rev G, 03 rev H,
04 rev I, 05 rev H. Se leyeron por recortes de imagen a 200-400 dpi con lectores y verificadores independientes.

- Pilares PM1 CUAD 150×150×5 (ejes interiores de las fachadas largas) y PM2 CUAD 150×150×4; intermedios PM3
  RECT 150×100×3; 15×15 centrados en el eje; llegan a la cara inferior de la viga inclinada.
- Vigas E-O CUAD 100×100×3 entre pilares, de +400 a +410 (lámina 05: tope +410); cordón horizontal RECT 150×100×3 en los marcos
  interiores. Las líneas de todos los miembros van por el eje del perfil, como en `estructura.js`.
- Vigas inclinadas de techo RECT 200×150×5 (marcos interiores, luz de 10,25 m) y 200×150×3 (marcos con pilares
  intermedios), pendiente 3,5 % (dibujada 4,5 %), aleros de 80 (N-S) y 52 (E-O); puntales cortos RECT 150×100×3 cada 171.
- Costaneras CA 100×50×15×3 cada 61 de alero a alero; soporte C 150×50×3 en los aleros; colgadores ø10 en el
  paño de 3,65; cruces C 150×50×3 en los tramos extremos; tensores Fe 16 en X en el plano del techo.
- Búnker (láminas 01 rev 1 y 03 rev H): muros DM e=25 (V ø12@15 L=384 con ganchos de 20 en la losa y 30 en la zapata, H ø10@20,
  2ø12 de coronamiento), losa e=20 (ø10@20 en la luz corta con ganchos de 13,5, ø8@20 en la larga, ø8@15 junto al hueco,
  2ø12 L=456 de borde), VHA 25/40 (3ø12 + 2ø10 + 3ø16, Est ø10@20; 20 en la losa + 20 bajo ella), radier 10 sobre relleno granular
  10, **zapata corrida 100 × 30** bajo los muros (37,5 + 25 + 37,5; ø16@20 L=130 en U + 4ø10) sobre emplantillado G5 ≥ 10
  (sello 20 cm en el estrato de la memoria de cálculo). Niveles del original: 0 / −20 / −292 / −312 / −342.
- Fuera del búnker (lámina 01 rev 1, corte b-b): **sobrecimiento 25 × 50** (2ø12 arriba, ø10@20 L=211 en U, ø8@20) hasta el NTN −50,
  **cimiento corrido 80 × 25** de −50 a −75 (ø12@20 L=100 en U + 4ø10), emplantillado ≥ 10; **CF 25/40** bajo el eje interior 2.a
  (3ø12 + 2ø10 + 3ø12, Est ø10@25, emplantillado 40 × 10, de 0 a −40); radier 10 sobre poliestireno expandido de alta densidad e=100 mm,
  relleno granular 15 (T.máx 1 1/2", 90 % Proctor modificado) y sub base granular compactada.
- Placas base PLb 200 × 200 × 8 mm en todos los pilares, soldadas al tubo; anclaje 1+1 ø3/4" en horquilla (L=1200 mm: 140 bajo la
  placa, ramas de 430 y ganchos de 100), estribos ø8@20, embebido en el muro o sobrecimiento (sin pedestal).
- Especificaciones (lámina 02): emplantillado G5, hormigón G25, acero A630-420H, recubrimientos 5 (fundaciones) / 3 (h.a.) / 2 (losa),
  traslapo mínimo 60 ø.
- Contradicciones de sus láminas, para preguntarle: la planta de 01 rev 1 es 1,00 m más larga (1125 / 625) que las de estructura
  (1025 / 525); el nivel del radier del búnker sale −292 por cotas pero −272 / −305 / −342 por rótulos; el anclaje de 43 baja más que el
  CF de 40; los ganchos de 100 de la horquilla no caben en un muro de 25 si no van girados.

## Lo que cambia (propuesta)

La planta de Gabriel se toma con medidas interiores (2026-10-12: "la cafetería tiene que medir 6 m interiores, estas son
las medidas, no otras"), así que el edificio mide 10,55 × 15,75 por fuera con muros de 25. Ejes 1–5 a 252 | 252 | 252 | 275
(el 4 sobre el tabique estudio/baño) y A–E a 200 | 425 | 435 | 290 | 200 (B sobre el tabique cafetería/estudio, que
coincide con el muro sur del búnker; C sobre el tabique baño/bodega; A2 y D a 2 m de las fachadas para que las cruces
queden en tramos de 2 m como las del original); 22 pilares, ninguno dentro de los recintos; cruces N-S en A–A2 y D–E de
las fachadas laterales y E-O solo en muros ciegos (C 4-5, fachada sur 1-2 y 4-5, y una sola diagonal en B 4-5 por la
puerta del baño); búnker de 10,05 × 6,00 × 2,80 con VHA 25/40 en el eje 3 y viga de borde en la escalera. Fuera del
búnker, las fundaciones del ingeniero (sobrecimiento + cimiento corrido bajo las fachadas, CF 25/40 bajo los tabiques con pilares):
ver arriba. La tabla completa y las luces que crecieron están en `estudio.html`.
La cubicación del ingeniero no se usa como referencia.

## Ventanas, puertas y esquema interior (propuesta, 2026-10-12)

`vanos`: vidrio de piso a 3,00 en los cuatro tramos de la fachada norte (corredera en el tramo 2-3, en el eje del estudio), tabique vidriado de piso
a cielo (hasta la viga E-O, que en B y E va pegada bajo la viga inclinada) entre cafetería y estudio con corredera centrada en el estudio, una ventana de piso a cielo centrada en la
fachada sur entre los parlantes, entrada de 1,80 por el poniente (pegada al pilar A2), puertas del baño (desde la cafetería, pegada al eje 4)
y de la bodega (desde el estudio), ventana alta del baño al oriente (la bodega sin ventana). La escalera (de hormigón, en su caja de muros de 23,3 con puerta con llave en el descanso) se entra por el sur y baja hacia el norte. Aleros de 1,00 m como la casa (Gabriel). `interior`: parlantes, consola, rack, silla, sofá, paneles acústicos,
alfombra, barra con taburetes, mesas con sillas, lámparas, cocina chica con lavaplatos y minibar en la esquina nororiente, baño y estanterías (sin
cabina de grabación por ahora, Gabriel 2026-10-12), solo
como idea para conversar. `hormigon` (muros, losa, zapata corrida, cimiento, CF, radieres, placas, niveles), `fierros` (familias de barras para la capa Enfierradura del 3D) y `cubicacion_hormigon` (m³ y kg): `hormigon.py`. Todo se dibuja en
`estudio.html` (sección 04 y elevaciones) y en el 3D con la capa "Ventanas y muros del estudio" (`3d.html?estudio=2`).

`datos/`: la lectura de las láminas por los agentes (JSON) para comparar.
