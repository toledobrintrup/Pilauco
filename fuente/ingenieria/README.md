# Ingeniería de estructuras — qué se usó y qué no

Fuente: 7 PDF de "José Torres Herrera, Ingeniero Civil" (planta de fundaciones nivel 1 y
nivel 2, 4 láminas de elevaciones por eje, y la lámina de estructura de techumbre).
**Los PDF no están en el repositorio**: su viñeta lleva el teléfono y el correo del
dibujante, igual que los planos de arquitectura.

## Lo que se extrajo

- **Altura de piso a piso: 3,46 m.** Aparece igual, de forma independiente, en las
  elevaciones de los ejes 1, 2, 3 y 5 — no es un dato aislado, es la altura de módulo de
  toda la estructura. Es el primer dato de altura real que tiene el proyecto; hasta ahora
  el plano sólo traía X e Y.
- **La grilla de ejes de la estructura calza con la del plano de arquitectura.** Se verificó
  ajustando una recta (mínimos cuadrados) entre las posiciones de los ejes A, B, C, D, E, F,
  H que aparecen en ambos documentos: el ajuste da residuales por debajo de 0,3 cm. Los ejes
  I, J, K de la estructura (que no existen en el plano de arquitectura del nivel 2) resultan
  calzar punto por punto con los ejes **I1** y **K1** que ya existían en los datos de este
  proyecto — la línea de pilares de la terraza norte. Confirma que esa ampliación de obra
  (lavandería y sala de máquinas hasta I1, ver README de `fuente/nivel1/`) tiene estructura
  real debajo, no es un volumen flotante.
- **El techo es un agua (mono-pendiente), subiendo de norte a sur; plano en la dirección
  oriente-poniente.** Se confirma porque las elevaciones por eje numerado (1, 2, 3, 5) muestran
  la viga de cumbrera inclinada, y todas las elevaciones por eje de letra (D, A, H, I, J, G3,
  etc.) la muestran nivelada.
- **La pendiente real del techo, medida** (ya no esquemática): sube de Z=6,56 m en el
  extremo norte (eje ~I) a Z=7,39 m en el extremo sur (eje A), ~3,5% de pendiente. Se sacó
  directamente de los vectores de las 4 elevaciones por eje numerado — no a ojo de la imagen
  renderizada — ajustando la recta de cada lámina contra las cotas de los ejes de letra que
  aparecen en la misma hoja, y promediando las 3 que dieron una lectura limpia (ejes 2, 3 y
  5; el eje 1 no mostró una línea de cumbrera nítida en esa zona del dibujo). Las tres
  coinciden entre sí con menos de 2 cm de diferencia — es una medición, no una estimación.
- **Pilares, vigas, diagonales (San Andrés) y cabios reales**, extraídos vector por vector
  (ver "Cómo se extrajo" más abajo): 63 pilares desde los símbolos de columna de la planta de
  estructura del nivel 2, y vigas + arriostramiento diagonal desde las 4 elevaciones por eje
  numerado (21 vigas, varias por elevación — el edificio tiene más de un nivel de viga entre
  nivel 1 y el techo, no sólo la del piso de nivel 2). **El arriostramiento en cruz existe sólo
  en el sentido norte-sur**: se revisaron las 10 elevaciones por eje de letra (A, B, C, D, E, F,
  G, G2, G3, H, I, J, etc.) y ninguna trae diagonales — son todos marcos rectangulares simples
  (columna + viga). Esto no es un vacío de datos, es cómo está diseñada la estructura: el
  arriostramiento en cruz resuelve el sentido corto del edificio, y el otro sentido queda
  confiado a los marcos rígidos.
- **Verificado superponiendo los datos extraídos sobre el plano original**, no sólo confiando
  en el número de líneas encontradas: se redibujaron los pilares de la planta de estructura
  encima de la planta de arquitectura (caen justo en las esquinas de muro) y las vigas,
  diagonales y cumbrera del Eje 2 encima de su propia lámina de elevación (calzan con las
  líneas reales del dibujo, cruz por cruz). Esa comparación visual es lo que encontró que a la
  primera versión le faltaba la mitad de cada cruz y las vigas completas — contarlas no
  alcanzaba, había que mirarlas sobre el plano.

## Cómo se extrajo (vectores, no la imagen)

Todo lo de esta sección sale de leer directamente los objetos vectoriales del PDF (líneas,
textos con su posición) con PyMuPDF — no de mirar el render y adivinar coordenadas:

1. Cada lámina trae las cotas de los ejes como texto posicionado (ej. el texto "A" en cierto
   punto del dibujo). Con los valores de eje ya conocidos (en cm, desde la planta de
   arquitectura) se ajusta una recta `posición_pdf = a · valor_cm + b` — es la misma regla de
   tres que calibra cualquier plano a escala, hecha con precisión de máquina en vez de regla.
2. Para evitar que una etiqueta de otro dibujo en la misma hoja contamine el ajuste, la
   pendiente se calcula con la **mediana de todas las pendientes par a par** (Theil-Sen) en
   vez de mínimos cuadrados directo: la mediana ignora una minoría de puntos contaminados,
   mínimos cuadrados no.
3. Con la calibración horizontal y vertical ya ajustadas, cada línea del dibujo se clasifica
   por su ángulo y largo: casi vertical y corta → pilar; inclinada entre 25° y 65° → diagonal;
   casi horizontal y muy larga → viga/cumbrera.
4. Las páginas de estructura vienen rotadas 270° dentro del PDF; hay que aplicar la matriz de
   rotación de la página antes de comparar cualquier coordenada, si no, todo calza desfasado.
5. **Cada cruz de San Andrés no son 2 líneas, son hasta 6.** El dibujo traza una de las dos
   diagonales de corrido, pero la otra la corta en dos donde se cruzan (para que no se dibuje
   "encima" de la primera), y cada una de las dos puede venir doblada en 2 líneas paralelas
   (el ancho del perfil Z150x150 dibujado). El primer intento sólo exigía líneas largas
   (>150 pt) y por eso se perdía la mitad cortada de cada cruz — el San Andrés salía "a medias"
   en el modelo. El umbral de largo se bajó a 75 pt (con 5–8 pt de margen contra el ruido de
   detalles de conexión, que son más cortos) para capturar ambas mitades sin juntar símbolos
   de otra cosa.

Las **costaneras** (perfil CA 200x50x15x3, cada 61 cm) no se leyeron vector por vector —se
generaron en el mismo plano de techo ya medido, al espaciamiento real que indica la lámina de
techumbre— porque la lámina dibuja la planta, no la sección, y el espaciamiento ya es un dato
de catálogo, no algo que haya que medir.

El **ancho real del techo** (y de las costaneras) no es el rectángulo simplificado del nivel 2
(`DATA_N2.W/H`, pensado para los volúmenes de recintos): los 63 pilares reales llegan hasta
X = −117,6 y X = 1.848,3, más ancho que esos 1.790 cm. La Vista 3D usa ese ancho medido (con
un margen de 2 cm) para el plano del techo y las costaneras, así ningún pilar real queda
sobresaliendo del borde dibujado.

**Cada miembro se dibuja con su perfil real, no un caño circular.** Un pilar HEB160 o una viga
IPE no son redondos — se les arma una caja orientada con el ancho real del perfil (en el
sentido del eje mundo X, que es siempre el plano de la elevación de origen) y la altura/
profundidad real del perfil en el otro sentido: pilares 16×16 cm (HEB 160), diagonales una
pletina delgada de 15×1,5 cm (Z150/Z200, sección angosta), cumbrera 18×40 cm (IPE 400, el
ancho de ala y el peralte medido directo de las dos líneas paralelas del dibujo), vigas 15×30 cm
(un IPE representativo — el plano trae perfiles distintos según el tramo, de IPE220 a IPE450, y
no se extrajo el peralte de cada una por separado).

## Lo que NO se modeló (y por qué)

Dentro de cada diagonal, viga o pilar no se modeló el detalle de anclaje ni los tensores, y el
perfil de cada viga usa un tamaño representativo en vez del exacto de cada tramo (ver arriba).
Tampoco se extendió el techo más allá del ancho que marcan los pilares extraídos — el alero/
voladizo real puede ser algo más ancho y no se quiso inventar esa distancia. Y por el umbral de
largo mínimo de la diagonal (75 pt, ver arriba), **al menos una cruz de San Andrés angosta quedó
sin capturar** — se vio al comparar el Eje 2 contra su lámina original; bajar más el umbral
reintroduce ruido de los símbolos de conexión. Antes de usar esto para diseño de interiores o
cálculo, confirmar con el ingeniero cualquier detalle de conexión.

## Qué se integró en la app

`3d.html` — nueva página, enlazada desde el plano ("Vista 3D ↗" en el encabezado). Lee
`data.js` (los mismos `DATA_N1`/`DATA_N2` que usa `index.html`) y `estructura.js` (pilares,
diagonales, cabios y costaneras reales, ver arriba) y arma la escena con Three.js: cada
recinto extruido a su altura real, Nivel 1 de 0 a 3,46 m, Nivel 2 de 3,46 a 6,92 m, el techo
con su pendiente real encima, y un casillero aparte **"Ver estructura"** que superpone el
esqueleto de acero medido. Controles: girar/acercar/desplazar (orbit), mostrar u ocultar cada
capa, y un deslizador para separar los pisos en el aire y ver los dos pisos a la vez sin que
uno tape al otro.
