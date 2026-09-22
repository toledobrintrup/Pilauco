# Nivel 1 — cómo se extrajo la geometría

Scripts que reconstruyen la planta del nivel 1 desde el PDF original
(`L2.PLARQ.29.12.2025.pdf`, lámina 2/11 de GVArq). **El PDF no está en el repositorio**:
su viñeta lleva RUT, teléfono y correo, así que se deja fuera. Ponlo junto a los scripts
para poder correrlos.

```bash
pip install pymupdf numpy opencv-python-headless shapely
python3 n1_extract.py   # capas de dibujo y textos del PDF -> cm
python3 n1_walls.py     # muros como polígonos (capa de grosor 1,28)
python3 n1_vanos.py     # vanos: empareja extremos de muro enfrentados
python3 n1_final.py     # recintos, métricas y n1_data.json (lo que consume la página)
```

El bloque `const DATA_N1 = …` de `index.html` es el contenido de `n1_data.json`.

## Decisiones que no son obvias

- **Origen y escala.** `X0=326.70, Y0=733.46` puntos PDF, escala 1:50 (0,56705 pt/cm).
  Se fijaron haciendo calzar los ejes 1, 2, 3 y 5 del nivel 1 con los mismos del nivel 2:
  el error queda bajo 0,5 cm en los cuatro. Por eso las dos plantas se pueden superponer
  y cambiar de nivel no mueve el dibujo.
- **Sólo la casa.** La lámina trae además la planta del nivel −1 y otra construcción, a la
  derecha. Se descarta todo lo que esté a la derecha de x = 1780 pt.
- **El cerramiento poniente es vidrio**, no muro: por eso el relleno de recintos usa muros
  + ventanas + puertas, y no sólo la capa de muros.
- **La capa de puertas es imprescindible** para cerrar los vanos que el emparejamiento de
  extremos no alcanza; sin ella el relleno se escapa y quedan 4 recintos en vez de 9.
  Como contrapartida, las hojas de puerta dejan espigas en el contorno: las quita
  `quita_espigas()`, que reemplaza por el tramo recto cualquier excursión que salga de la
  línea de muro y vuelva al mismo punto (largo > 3× la recta, área < 2,5 m²).
- **Estar 1, comedor y hall de acceso son un solo recinto** porque en el plano no hay muro
  que los separe. No se inventó una división: se miden juntos y se rotula cada zona donde
  la nombra el arquitecto.
