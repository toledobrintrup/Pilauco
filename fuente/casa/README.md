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
- **Doble altura del hall**: V2, V3 y V4 se repiten en el nivel 2 (el plano las rotula en las dos plantas).
- **Supuesto**: el ala oriente (sala de máquinas y bodega) no tiene cubierta en los planos del modelo; el 3D le pone una
  losa plana a 3,46 para cerrarla.

    python3 fuente/casa/generar_casa_vanos.py      # → casa_vanos.js (DATA_CASA)
