# Ingeniería de estructuras — de los PDF al modelo 3D

Fuente: las láminas de estructura de "José Torres Herrera, Ingeniero Civil": plantas de
estructura nivel 1 (rev. 08-04-2026) y nivel 2, planta de techumbre, planta de fundaciones,
y 4 láminas con 25 elevaciones por eje (ejes 1, 1a', 2, 3, 5, 6, K, A, A1, A3, B, C, D, E, E4,
F, F1, F2, G, G2, G3, H, I, J). **Los PDF no están en el repositorio**: su viñeta lleva el
teléfono y el correo del dibujante.

El resultado es `estructura.js` en la raíz: **540 piezas**, cada una con su perfil real
y los extremos de su eje en cm, en el mismo marco de coordenadas que los planos de la app.
`3d.html` las dibuja con la sección de su perfil (I para HEB/IPE, tubo cuadrado o
rectangular, cañería redonda, C y CA para celosías y costaneras, barra para tensores).

## Cómo se hizo (y por qué así)

Las versiones anteriores de la vista de estructura salieron mal: una confundió los íconos
cuadrados de los rótulos de perfil con pilares, a otra le faltaban todas las vigas y la mitad
de cada cruz de San Andrés, y todas dibujaban tubos genéricos. Esta vez se hizo por etapas,
y cada etapa se verificó dibujando el resultado **encima de la lámina original** y mirándolo:

1. **Grilla de ejes.** Se sacó tres veces por caminos independientes: desde las cotas de las
   plantas, desde las cotas de las elevaciones y desde la arquitectura de la app. Las tres se
   reconciliaron en `datos/grilla.json`: todas las líneas de eje dibujadas en las 29 vistas
   calzan con menos de 1 cm, y las 139 cotas leídas con menos de 0,6 cm.
2. **Catálogo de vistas.** Cada lámina trae varias elevaciones pegadas; se delimitó cada una
   para que la extracción de una no se contamine con la vecina.
3. **Extracción pieza por pieza, por vista** (29 vistas). Cada pieza con su clase, perfil
   (leído en el rótulo y siguiendo su flecha) y extremos. Cada vista la revisó después un
   verificador independiente sobre la superposición, con hasta dos rondas de corrección.
4. **Modelo único.** Pilares primero (cruzando plantas, fundaciones y elevaciones), después
   vigas, techumbre y arriostramiento ajustados a esos pilares; se quitaron duplicados.
5. **Re-proyección.** El modelo 3D se dibujó de vuelta sobre las 29 láminas y se corrigió
   en tres rondas hasta que calzara.
6. **Lista de materiales.** El largo total por perfil se comparó con la cubicación del
   ingeniero (ver tabla abajo).

Detalles que importan para entender el modelo:

- **Las láminas vienen rotadas 270°** dentro del PDF: toda coordenada se lee aplicando la
  matriz de rotación de la página.
- **Los rótulos de perfil y las cotas son trazos, no texto**, salvo en la planta nivel 1. Se
  leyeron en imágenes renderizadas a buen zoom.
- **Los pilares se validaron contra la capa CAD "PILARES METALICOS"** de las tres plantas:
  60 símbolos en nivel 1, 33 en nivel 2 y 60 en fundaciones, 1:1 con el modelo. Los íconos de
  rótulo (cuadrado con diagonal) están en otra capa y ninguno se tomó como pilar.
- **Pilar de nivel 1 y de nivel 2 en la misma posición son dos piezas**: cambian de perfil en
  Z = 346 (cara superior de las vigas de entrepiso).
- **Las vigas terminan en la cara exterior del pilar**, como las dibujan las elevaciones.
- **El techo** es de un agua: cabios IPE 400 en los ejes 1, 2, 3 y 5, con eje de Z 656,3
  (Y −100) a Z 739,2 (Y 2280,2), 3,48 % de pendiente; aleros de 110 cm y el quiebre al sur que
  dibuja la planta de techumbre. Encima, 40 costaneras CA 200x50x15x3 cada 61 cm, con
  colgadores Fe 12, tensores Fe 22 en cruz y puntales PV1.

## Cubicación: modelo vs lista del ingeniero

| Perfil | Piezas | Modelo (m) | Ingeniero (m) | Diferencia |
|---|---:|---:|---:|---:|
| HEB 160 | 27 | 83.5 | 99.0 | -16 % |
| CUAD 150x150x4 | 61 | 197.0 | 208.4 | -5 % |
| CUAD 150x150x3 | 33 | 121.6 | 138.7 | -12 % |
| CUAD 150x150x2 | 0 | 0.0 | 63.4 | -100 % |
| CANERIA 310 | 5 | 15.2 | 17.0 | -11 % |
| IPE 220 | 32 | 66.1 | 67.8 | -3 % |
| IPE 270 | 13 | 28.4 | 30.0 | -5 % |
| IPE 300 | 25 | 95.6 | 94.3 | +1 % |
| IPE 360 | 4 | 23.2 | 23.3 | -0 % |
| IPE 400 | 4 | 91.9 | 81.8 | +12 % |
| IPE 450 | 9 | 37.6 | 35.6 | +5 % |
| IPE 500 | 3 | 18.6 | 18.1 | +3 % |
| IPE 600 | 3 | 20.9 | 20.7 | +1 % |
| RECT 200x150x3 | 19 | 97.9 | 112.9 | -13 % |
| C 150x50x3 | 59 | 57.1 | 56.2 | +2 % |
| CA 200x50x15x3 | 40 | 760.0 | 760.0 | +0 % |
| FE 22 | 20 | 156.1 | 160.0 | -2 % |
| FE 12 | 183 | 111.2 | 177.0 | -37 % |

Cómo leer las diferencias:

- **Pilares (HEB 160, tubos 150x150x4, cañerías Ø310):** el modelo mide la pieza real, desde
  la placa base hasta la cara inferior de la viga; la lista mide de nodo a nodo (las cañerías,
  5 × 3,40 m exacto). Medidos de nodo a nodo quedan entre −5 % y +2 %. En HEB 160 quedan
  ~5 m (un pilar y medio) que ningún plano ubica.
- **IPE 400 (+12 %):** los cabios llevan los aleros de 110 cm y el del eje 5 sigue 235 cm
  después de A1, como lo dibujan las plantas. Entre pilares extremos suman 81,77 m, igual a
  la lista: la lista no cuenta los voladizos.
- **Colgadores Fe 12 (−37 %):** son 183, uno en cada tramo entre costaneras donde la planta
  de techumbre los rotula, de 0,61 m cada uno. La lista da 0,97 m por barra: parece contar la
  barra cortada con ganchos o rosca.
- **Puntales RECT 200x150x3 (−14 m):** coincide exacto con un PV1 en A3 entre 1 y 2 más uno en
  A1 entre 3 y 5, que cerrarían el borde sur del techo. Ninguna planta los dibuja: **pregunta
  para el ingeniero**.
- **Tubo 150x150x2 (63 m) y parte del 150x150x3:** ninguna lámina dibuja ni rotula tubo de
  150x150x2, y todas las cruces son 150x150x3. Faltarían ~63–73 m de tubo delgado que los
  planos no detallan: **pregunta para el ingeniero**.

## Diferencias conocidas entre láminas

Cuando dos láminas se contradicen, el modelo sigue la planta nivel 1 (rev. 08-04-2026, la más
nueva) y lo deja anotado en la pieza. Estas son las diferencias que quedaron:

- Techo en el eje H: la elevacion H dibuja la VT, los PV1 y el tope de los tubos del nivel 2 14 cm mas bajos que el modelo; el modelo sigue la cota escrita 14.35 + 280 de las elevaciones 1, 2, 3 y 5 (la H parece medir los 280 cm desde la viga y no desde el piso terminado).
- Elevacion A: dibuja un portico entre los ejes 3 y 3a (tubos en 3a, IPE 220, PV1 e IPE 400 en 3a) que no aparece en ninguna planta ni en la elevacion D; el modelo tiene ese portico entre 2 y 3, como las plantas, y queda la pregunta al ingeniero.
- Elevacion A: la VT sobre 3xA se ve 4 cm mas baja que en el modelo (Z 711 contra 715); esa lamina no tiene cota vertical y el modelo usa la cota escrita 355 de la elevacion 3.
- Quien pasa sobre el pilar en 1xJ, 1xH, 1xF, 1xB, 3xC, 3xB, 3xA1, 4xF2 y 4xE: las elevaciones de letra (J, H, F, B, C, A1, F2, E) dibujan su viga pasando sobre la cabeza del pilar y el pilar cortado bajo ella; la planta nivel 1 rev 08-04-2026 dibuja pasando la viga del eje numerado, y el modelo la sigue: en esas elevaciones la viga del modelo empieza 15-16 cm mas adentro (en la cara del pilar) y el pilar sube 6-38 cm mas (dibujado hasta 286-316, en el modelo hasta 316-324).
- Al reves en los ejes 1 y 2 (1xD, 2xG2, 2xF1, 2xF, 2xE4, 2xD, 2xB): las elevaciones 1 y 2 dibujan el pilar hasta su propia viga (319 y 324); la planta nivel 1 y las elevaciones de letra dibujan la viga de letra pasando encima, y el modelo corta el pilar bajo ella (286-301). Por eso las 4 diagonales de las cruces G2-F1 y E4-D del eje 2 terminan en el costado de esa viga, 2-3 cm antes de lo dibujado.
- Nudo 3xD: la elevacion 3 dibuja el tubo hasta 324 bajo la IPE 220 y la elevacion D hasta 316 bajo la IPE 300; la planta dibuja las dos vigas de corrido; el modelo deja pasar la IPE 300 (la mas alta), asi que en la elevacion 3 el tubo se ve 8 cm mas corto.
- Perfil de las vigas F 1-2 y D 1-2: las elevaciones F, D y 1a' (dic-2025) las rotulan IPE 500; la planta nivel 1 rev 08-04-2026 las rotula IPE 600 y la lista de materiales cuadra exacto con IPE 600; el modelo usa IPE 600, asi que en esas elevaciones la viga baja 10 cm mas y los pilares 2xF, 1xD y 2xD quedan 10 cm mas bajos.
- Viga K 1-2: la elevacion K la rotula IPE 360 (pilar hasta 310); la planta nivel 1 rev 08-04-2026 la rotula IPE 300, y el modelo usa IPE 300 (pilar hasta 316).
- Pilar 2xI (caneria): la elevacion I la dibuja hasta 316 bajo la IPE 300 del eje I; el modelo la corta en 301, bajo la IPE 450 del eje 2, que es mas alta y pasa encima (planta nivel 1).
- Eje D: la elevacion D no dibuja el tubo de X 764 (eje 2 + 111) entre 2 y 3, que si esta en la planta nivel 1 y en fundaciones; el modelo lo tiene y parte ahi la IPE 300.
- Viga D 4-5 en 5xD: la elevacion D la dibuja hasta la cara exterior del HEB (X 1791.7); el modelo la termina en el eje 5 (X 1783.7), en el alma de la IPE 300 del eje 5, que la planta nivel 1 dibuja pasando.

## Archivos

- `datos/grilla.json` — la grilla de ejes en cm, en el marco de la app, con su evidencia.
- `datos/modelo.json` — el modelo completo, con las fuentes (vistas) y notas de cada pieza.
  `estructura.js` (raíz) se genera de aquí con `herramientas/generar_estructura_js.py`.
- `datos/extraccion_por_vista.zip` — lo extraído de cada una de las 29 vistas, antes de unir.
- `herramientas/` — `comun.py` (lectura de láminas), `reproyectar.py` (dibuja el modelo
  sobre cualquier lámina para revisarlo) y `generar_estructura_js.py`. Necesitan los PDF en su
  carpeta de iCloud (rutas en `comun.py`).

Antes de usar el modelo para cálculo o para pedir material, confirmar con el ingeniero:
el modelo representa lo que dicen los planos, no reemplaza al ingeniero.
