# Estudio con búnker: estructura adaptada

El ingeniero proyectó en abril de 2026 (láminas 03, 04 y 05, en iCloud `02_Ingeniería/03_Estudio Pilauco/`; no
entran al repositorio) un estudio de 11,05 × 10,25 m entre ejes con un búnker de 5,00 × 10,55 m interiores bajo
un extremo. La planta nueva de Gabriel (`fuente/sitio/estudio.json`) mide 10,05 × 15,25 m, lleva el búnker bajo la
cafetería (al norte) y el techo subiendo al sur. `generar_estudio_estructura.py` arma la propuesta con el mismo
sistema del ingeniero y escribe `estudio_estructura.js` (DATA_ESTUDIO_EST):

    python3 generar_estudio_estructura.py ../sitio/estudio.json ../sitio/sitio.json ../../estudio_estructura.js

## Lo que se toma del ingeniero (dato)

- Pilares PM1 CUAD 150×150×5 (ejes interiores de las fachadas largas) y PM2 CUAD 150×150×4; intermedios PM3
  RECT 150×100×3; 15×15 centrados en el eje; llegan a la cara inferior de la viga inclinada.
- Vigas E-O CUAD 100×100×3 a +4,01/+4,10 entre pilares; cordón horizontal en los marcos interiores.
- Vigas inclinadas de techo RECT 200×150×5 (marcos interiores, luz de 10,25 m) y 200×150×3 (marcos con pilares
  intermedios), pendiente 3,5 %, aleros de 80 (N-S) y 52 (E-O); puntales cortos RECT 150×100×3 cada 171.
- Costaneras CA 100×50×15×3 cada 61 de alero a alero; soporte C 150×50×3 en los aleros; colgadores ø10 en el
  paño de 3,65; cruces C 150×50×3 en los tramos extremos; tensores Fe 16 en X en el plano del techo.
- Búnker: muros DM e=25 (V ø12@15, H ø10@20), losa e=20 (ø10@20 y ø8@20, borde 3ø12), viga VHA 25/40
  (3ø12 + 2ø10 + 3ø16, Est ø10@20), piso a −292 con radier de 20, zapata corrida de 100 × 30 bajo los muros;
  NPOG 0,00 en la losa, NTN −50. Fuera del búnker, sobrecimiento de 25 y cimiento corrido de 80 × 25.

## Lo que cambia (propuesta)

Ejes 1–5 (245 | 245 | 240 | 250; el 4 sobre el tabique estudio/baño) y A–E (600 | 300 | 300 | 300; B sobre el
tabique cafetería/estudio, que coincide con el muro sur del búnker); 21 pilares, ninguno dentro de los recintos;
cruces en A–A2 y D–E de las fachadas laterales y dos cruces E-O en el tabique B; búnker de 5,75 × 9,55 × 2,80
con VHA 25/40 al centro y viga de borde en la escalera. La tabla completa y las luces que crecieron (losa del
búnker, cruces, tensores) están en `estudio.html`. La cubicación del ingeniero no se usa como referencia.

`datos/`: la lectura de las láminas por los agentes (JSON) para comparar.
