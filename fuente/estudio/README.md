# Estudio con búnker: estructura adaptada

El ingeniero proyectó en abril de 2026 (láminas 03, 04 y 05, en iCloud `02_Ingeniería/03_Estudio Pilauco/`; no
entran al repositorio) un estudio de 11,05 × 10,25 m entre ejes con un búnker de 5,00 × 10,55 m interiores bajo
un extremo. La planta nueva de Gabriel (`fuente/sitio/estudio.json`) mide 10,05 × 15,25 m interiores, lleva el búnker bajo la
cafetería (al norte) y el techo subiendo al sur. `generar_estudio_estructura.py` arma la propuesta con el mismo
sistema del ingeniero y escribe `estudio_estructura.js` (DATA_ESTUDIO_EST):

    python3 generar_estudio_estructura.py ../sitio/estudio.json ../sitio/sitio.json ../../estudio_estructura.js

## Lo que se toma del ingeniero (dato)

- Pilares PM1 CUAD 150×150×5 (ejes interiores de las fachadas largas) y PM2 CUAD 150×150×4; intermedios PM3
  RECT 150×100×3; 15×15 centrados en el eje; llegan a la cara inferior de la viga inclinada.
- Vigas E-O CUAD 100×100×3 entre pilares, dibujadas de +401 a +411 y rotuladas +410 (lámina 05); el modelo las pone de +400 a +410 como el cordón
  horizontal de los marcos interiores (lámina 04). Las líneas de todos los miembros van por el eje del perfil, como en `estructura.js`.
- Vigas inclinadas de techo RECT 200×150×5 (marcos interiores, luz de 10,25 m) y 200×150×3 (marcos con pilares
  intermedios), pendiente 3,5 %, aleros de 80 (N-S) y 52 (E-O); puntales cortos RECT 150×100×3 cada 171.
- Costaneras CA 100×50×15×3 cada 61 de alero a alero; soporte C 150×50×3 en los aleros; colgadores ø10 en el
  paño de 3,65; cruces C 150×50×3 en los tramos extremos; tensores Fe 16 en X en el plano del techo.
- Búnker: muros DM e=25 (V ø12@15, H ø10@20), losa e=20 (ø10@20 y ø8@20, borde 3ø12), viga VHA 25/40
  (3ø12 + 2ø10 + 3ø16, Est ø10@20), piso a −292 con radier de 20, zapata corrida de 100 × 30 bajo los muros;
  NPOG 0,00 en la losa, NTN −50. Fuera del búnker, sobrecimiento de 25 y cimiento corrido de 80 × 25.

## Lo que cambia (propuesta)

La planta de Gabriel se toma con medidas interiores (2026-10-12: "la cafetería tiene que medir 6 m interiores, estas son
las medidas, no otras"), así que el edificio mide 10,55 × 15,75 por fuera con muros de 25. Ejes 1–5 a 252 | 252 | 252 | 275
(el 4 sobre el tabique estudio/baño) y A–E a 200 | 425 | 435 | 290 | 200 (B sobre el tabique cafetería/estudio, que
coincide con el muro sur del búnker; C sobre el tabique baño/bodega; A2 y D a 2 m de las fachadas para que las cruces
queden en tramos de 2 m como las del original); 22 pilares, ninguno dentro de los recintos; cruces N-S en A–A2 y D–E de
las fachadas laterales y E-O solo en muros ciegos (C 4-5, fachada sur 1-2 y 4-5, y una sola diagonal en B 4-5 por la
puerta del baño); búnker de 10,05 × 6,00 × 2,80 con VHA 25/40 en el eje 3 y viga de borde en la escalera. Fuera del
búnker, zapatas aisladas 1 × 1 × 1 con vigas de fundación 25 × 50 y radier de 10 (lo que Gabriel espera, como en el
gimnasio; a confirmar con el plano 01 del ingeniero). La tabla completa y las luces que crecieron están en `estudio.html`.
La cubicación del ingeniero no se usa como referencia.

## Ventanas, puertas y esquema interior (propuesta, 2026-10-12)

`vanos`: vidrio de piso a 3,00 en los cuatro tramos de la fachada norte (corredera en el tramo 2-3, en el eje del estudio), tabique vidriado de piso
a cielo (hasta la viga E-O, que en B y E va pegada bajo la viga inclinada) entre cafetería y estudio con corredera centrada en el estudio, una ventana de piso a cielo centrada en la
fachada sur entre los parlantes, entrada de 1,80 por el poniente (pegada al pilar A2), puertas del baño (desde la cafetería, pegada al eje 4)
y de la bodega (desde el estudio), ventanas altas del baño y la bodega al oriente. `interior`: parlantes, consola, sofá,
cabina de grabación 2,40 × 2,20 en el tramo 1-2, entre la entrada y el tabique vidriado, barra y mesas, solo
como idea para conversar. `zapatas`, `vigas_fundacion` y `radier`: las fundaciones fuera del búnker. Todo se dibuja en
`estudio.html` (sección 04 y elevaciones) y en el 3D con la capa "Ventanas y muros del estudio" (`3d.html?estudio=2`).

`datos/`: la lectura de las láminas por los agentes (JSON) para comparar.
