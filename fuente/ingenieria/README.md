# Ingeniería de estructuras — qué se usó y qué no

Fuente: 6 PDF de "José Torres Herrera, Ingeniero Civil" (planta de fundaciones nivel 1 y
nivel 2, más 4 láminas de elevaciones por eje). **Los PDF no están en el repositorio**:
su viñeta lleva el teléfono y el correo del dibujante, igual que los planos de arquitectura.

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

## Lo que NO se modeló (y por qué)

La estructura real tiene, sobre el nivel de 3,46 m, unas torres arriostradas en cruz de
~2,80 m de alto que sostienen la viga de cumbrera a intervalos — no una viga apoyada
directamente en los muros. No se pudo confirmar con certeza desde el PDF (los valores de
cota están dibujados como trazos vectoriales, no como texto: no se pueden extraer de forma
confiable, sólo leer a ojo en la imagen renderizada). Por eso la Vista 3D dibuja el techo
como una tapa plana y lo marca explícitamente como esquemático — es una decisión deliberada
de no presentar como hecho algo que no se pudo verificar con la misma rigurosidad que el
resto del proyecto. Antes de darlo por bueno para diseño de interiores, confirmar con el
ingeniero: la pendiente real, la altura de cumbrera, y qué son esas torres.

## Qué se integró en la app

`3d.html` — nueva página, enlazada desde el plano ("Vista 3D ↗" en el encabezado). Lee
`data.js` (los mismos `DATA_N1`/`DATA_N2` que usa `index.html` — se separaron a un archivo
aparte para que las dos páginas compartan una sola fuente de datos) y extruye cada recinto
a su altura real con Three.js. Nivel 1 de 0 a 3,46 m, Nivel 2 de 3,46 a 6,92 m, con un
techo esquemático encima. Controles: girar/acercar/desplazar (orbit), mostrar u ocultar
cada nivel y el techo, y un deslizador para separar los pisos en el aire y ver los dos
pisos a la vez sin que uno tape al otro.
