# Muros, puertas y ventanas de la casa (3D)

Desde el 15-10-2026 la vista 3D dibuja la casa con sus muros reales en vez de un volumen por recinto (Gabriel:
"elimina los volúmenes de cada espacio de la casa y pongamos tabiques con ventanas"). Todo sale del plano (`data.js`):

- **Muros**: los polígonos de `wallsPath` de cada planta (ya traen los huecos de puertas y ventanas), partidos en
  rectángulos por bandas. Nivel 1 de 0 a 3,34 (bajo la losa de 12); nivel 2 de 3,46 hasta la cara inferior del techo,
  siguiendo su pendiente. Perimetrales de 25, tabiques de 15 (los espesores salen del dibujo).
- **Puertas y pasos**: `openings` de cada variante (eje y ancho); el espesor del muro se toma del muro vecino.
  Las que coinciden con una ventana del plano (V5, V6, V10, V12, V13) se tratan como ventana o puerta vidriada.
- **Ventanas**: tabla curada en `generar_casa_vanos.py` (V1–V28, P1, P4, P6, P-N, P3) leída de `windowsPath` y revisada
  contra el plano; `extraer_vanos.py` imprime los candidatos. Las dos P3 (sala de máquinas y bodega al oriente) no
  tenían hueco en `wallsPath`: se les resta el vano.
- **Alturas** (Gabriel, 15-10-2026): todas las ventanas de 2,80 iguales en los dos niveles, del piso al dintel
  (`ANTEPECHO = 0`; cambiar ahí si se quiere antepecho); puertas y pasos con dintel a 2,80. Marcos europeos gruesos
  de 10 × 8 (los mismos del estudio: `kitCerramiento` en `3d.html`).
- **Doble altura del hall**: V2, V3 y V4 son un solo vidrio continuo del piso del nivel 1 al techo (≈7,7 m), sin travesaño entre pisos y con marco de acero fino
  (Gabriel, 15-10-2026: "completamente vidriadas de piso a techo, el marco solo el fierro"); en el nivel 2 solo se abre el hueco.
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
- **Supuesto**: el ala oriente (sala de máquinas y bodega) no tiene cubierta en los planos del modelo; el 3D le pone una
  losa plana a 3,46 para cerrarla.

    python3 fuente/casa/generar_casa_vanos.py      # → casa_vanos.js (DATA_CASA)
