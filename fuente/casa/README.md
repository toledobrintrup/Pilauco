# Muros, puertas y ventanas de la casa (3D)

Desde el 15-10-2026 la vista 3D dibuja la casa con sus muros reales en vez de un volumen por recinto (Gabriel:
"elimina los volúmenes de cada espacio de la casa y pongamos tabiques con ventanas"). Todo sale del plano (`data.js`):

- **Muros**: los polígonos de `wallsPath` de cada planta (ya traen los huecos de puertas y ventanas), partidos en
  rectángulos por bandas. Nivel 1 de 0 a 3,68 (bajo la losa de 12; el nivel 1 mide 3,80 a la viga, medido en terreno); nivel 2 de 3,95 hasta la cara inferior del techo,
  siguiendo su pendiente. Perimetrales de 25, tabiques de 15 (los espesores salen del dibujo).
- **Puertas y pasos**: `openings` de cada variante (eje y ancho); el espesor del muro se toma del muro vecino.
  Las que coinciden con una ventana del plano (V5, V6, V10, V12, V13) se tratan como ventana o puerta vidriada.
- **Ventanas**: tabla en `generar_casa_vanos.py` con la **propuesta de ventanas de la casa** que Gabriel aprobó el 15-10-2026 por la
  tarde ("implementalo"), construida sobre la tabla curada del plano (V1–V28, P1, P4, P6, P-N, P3; `extraer_vanos.py` imprime los
  candidatos). Cada entrada lleva el código de las láminas (N, S, E, O) que están en `propuesta-ventanas/` (`propuesta.py` calcula la luz
  por recinto, `elev.py` dibuja las cuatro fachadas, `critica.txt` es la revisión de dos revisores). Reglas: todo piso a cielo; módulo de
  2,4; jambas en la cara de los pilares; nada de vidrio en los paños con cruces o celosías del ingeniero (poniente N1 10–107, 625–736,
  991–1104, 1634–1695; N2 10–238, 991–1104, 1634–1695; oriente N2 10–82 y 690–958). Cambios principales: oficina con toda la pared
  norte a la piscina (V8), 3,5 al poniente (V9, antes 6,0) y tabiques vidriados al living (T-OL) y a la galería (T-OGa/b + puerta P-OG);
  comedor al oriente en 3 paños con los pilares Y1173 y Y1438 a la vista (V6a/V6/V6b); lavandería con ventana (V7, antes estaba mal
  dentro del recinto) y puerta de servicio (P-L); dormitorios con ventanas de 2,4 (V16, V28, V12, V13) y 2,85 (V25); baños piso a cielo con vidrio
  satinado hasta 1,8 (V17, V26, V27; el satinado va en la ficha, el 3D dibuja el mismo vidrio); closets con ventana de 2,4 (V22, V20) y el WKC Maggie con corredera al pasillo-balcón (V21).
- **Alturas**: nivel 1 del piso a 3,40 (`H_N1`: lo máximo bajo la IPE 300 del entrepiso, cuya cara inferior queda a 3,50 con el nivel 1 de 3,80
  medido en terreno por Gabriel el 16-10-2026, `PISO_N1`; Gabriel pidió 3,20 y después 3,60, que no cabe), todas iguales; nivel 2 todas iguales de 2,80 (`H_N2`). Primero se
  habían hecho "hasta el cielo" siguiendo el techo (2,65 al norte → 3,35 al sur, como las ventanas del arquitecto en su lámina 9); Gabriel
  pidió la misma altura en todo el nivel ("ojo que las ventanas del segundo piso no miden lo mismo en altura") y recordó que el nivel 2
  quedó con **3,00 libres en la parte más baja** ("lo dejamos más alto… ajusta manteniendo la pendiente"): el techo y su estructura suben
  20 cm en `fuente/ingenieria/herramientas/generar_estructura_js.py` (las elevaciones del ingeniero dibujan 2,80 bajo los cabios), así
  que la ventana de 2,80 deja 20 cm para el cabezal. `cielo_n2(y)` = techo(y) − 0,74 sobre el piso +3,95 (`PISO_N2`) y `dintel_n2` comprueba que
  2,80 quepa en cada vano. Puertas interiores y opacas 2,80 (`H_PUERTA`); `ANTEPECHO = 0`. Marcos europeos gruesos de 10 × 8 (los
  mismos del estudio: `kitCerramiento` en `3d.html`).
- **Doble altura del hall**: V2, V3 y V4 son un solo vidrio continuo del piso del nivel 1 al cielo del nivel 2 (techo − 74, ≈7,15 m), bajo
  las vigas del techo y no entre las costaneras (Gabriel, 15-10-2026: "dejaste la ventana metida en medio de las costaneras"), sin travesaño
  entre pisos y con marco de acero fino; en el nivel 2 queda el hueco y, encima del vidrio, la banda de las vigas (`CIELO_HALL = 74` en
  `3d.html`, el mismo cielo que `cielo_n2` del generador). La puerta de entrada (P1, vidriada de 1,2 con fijo lateral de 0,2) y la puerta
  vidriada oficina–galería (P-OG) van piso a cielo como el resto de los vidrios del nivel 1 (3,40); las puertas opacas y las interiores, 2,80.
- **Pasillo-balcón del norte** (Gabriel, 15-10-2026: "un balcón pasillo de 1,5 m aprox que llega al balcón grande"): la losa del ingeniero
  ya trae la franja de ≈1,75 m (de la cara del muro norte, −2,6, al borde de la losa, −177,5) sobre los pilares del eje I (y −170), desde la
  terraza grande hasta el ala oriente; el 3D le pone baranda de vidrio de 1,05 con pasamanos, y a la terraza también (como el render del
  arquitecto). Bajo ella queda el patio de servicio cubierto del norte (tendedero de la lavandería). El generador rellena los huecos de
  menos de 40 cm que dejan los encuentros en T de un tabique con la fachada y los restos de ventanas del plano que la propuesta movió
  (`rellenar_huecos`), y corta cada vano en el centro real de su muro (`centro_muro`): el muro sur del dormitorio de visitas y el family
  room es un retranqueo interior que no está en el eje A3 del ingeniero (su pilar asoma 1 cm por la cara sur, como en V99).
- **Muros de fachada centrados en los ejes del ingeniero** (Gabriel, 15-10-2026: "lo correcto es lo del ingeniero, nadie pondría un pilar
  no centrado"): el plano del arquitecto deja el eje 1 a 6,7 de la cara exterior (H a 7,2) y su muro de 25 va de la línea de fachada
  hacia adentro, así que un HEB 160 centrado en el eje asomaba 1,3 cm. `perimetro_desde_recintos` arma las fachadas desde los
  bordes exteriores de los recintos (25 hacia afuera), las centra en el eje del ingeniero si está a menos de 12 cm (`TOL_EJE`),
  absorbe los muñones de wallsPath, maciza esquinas y encuentros en T, y devuelve `caras` (cara vieja → nueva) para correr las
  losas, el zócalo y los pisos de los recintos. Resultado: fachadas corridas ~5,8 hacia afuera (poniente/oriente) y ~2,6 (norte).
  El plano 2D (`index.html`) sigue mostrando la línea del arquitecto; el permiso tendría que absorber esos centímetros.
- **Pilares dentro de ventanas del plano** (arquitecto vs ingeniero, sin resolver): V9 (oficina: el pilar 1×G3 y la cruz del eje 1
  quedan en el vidrio) y V18 (dormitorio hijo 1, nivel 2: el pilar 5×E). Las cañerías Ø310 de los accesos son columnas libres y no
  caben en un muro de 25.
- **Cubierta del ala oriente** (sala de máquinas y bodega): el ingeniero tiene sus vigas RECT 200×150 a +2,78 de eje (`V-G-5-6`,
  `V-E-5-6`, `V-6-G-E` en `estructura.js`), así que la cubierta apoya a +2,88 y los muros del ala terminan ahí (`ALA_TOP` en `3d.html`;
  `zTop` del nivel 1 recibe la x del muro para distinguir el ala). Antes el 3D le suponía una losa a +3,46. El espesor de 12 sigue
  siendo supuesto: el plano no define esa cubierta.
- **Escalera de obra** (Gabriel, 16-10-2026: "380 altura por 370 de avance, ancho 1,5 con baranda, plataforma de 1,5 × 1,5 arriba y el
  quiebre… toda de fierro, cómoda y segura para subir materiales"; después: "justo llega hasta el borde, córrela más atrás, pegado al fierro
  de atrás"): capa propia del 3D (`chk-escalera`, `grupoEscalera`). Va en la bodega pegada al muro de la casa, subiendo hacia el norte, con
  la plataforma de 1,50 × 1,50 pegada al fierro del eje G (y 3,49–4,99): 17 huellas de 24 (avance 4,08; el pie queda a 0,33 del muro sur) y
  18 contrahuellas de 21,9 hasta el piso del nivel 2 (+3,95 = viga de entrepiso a 3,80, medida en terreno, + hormigón 15), 42°. El pilar F2
  (y 4,12) queda en el borde de entrada al nivel 2: 0,55 libres al norte y 0,79 al sur. Zancas C 200×50×4, peldaños de plancha estriada de 4,
  marco C 150 con 2 postes tubo 100×100×3 al oriente y el lado poniente apernado a la viga IPE 270 del eje 5, baranda de 1,00 con barra a
  0,50 y rodapié (unos 550 kg). Con la capa prendida, la cubierta baja del ala se dibuja con el hueco provisorio de 1,6 × 5,7 (`ESC_HUECO`)
  por donde pasa. Lámina en `propuesta-ventanas/escalera.py`.
