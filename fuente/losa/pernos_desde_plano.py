# -*- coding: utf-8 -*-
"""Saca la ubicación de los pernos Nelson de la lámina 11 del ingeniero ("Losa colaborante. Ubicación pernos
stud", planta 1:50, 07-10-2026) y la deja en pernos_ingeniero.json, en cm en el marco de la app.

En la lámina cada perno es un punto negro de 12 pt (achurado) dibujado sobre su viga. Casi todos tienen además
un círculo de contorno, pero no todos (en la viga H entre 4 y 5 hay uno sin contorno), así que los puntos se
buscan por el relleno: la planta se pasa a imagen, se erosiona con un cuadrado de 7 pt (las líneas, el texto y
los círculos vacíos desaparecen; los puntos sólidos quedan) y cada mancha que queda es un perno. Los círculos de
contorno se cuentan igual, como control. La leyenda (arriba a la derecha) tiene puntos iguales que no son pernos:
queda fuera del recorte. La planta se calibra con las burbujas de los ejes (círculos de 29,5 pt con su nombre),
por mínimos cuadrados en x y en y; las burbujas que quedan a más de 1 cm del ajuste (algunas están dibujadas
1 a 2 pt fuera de su línea de eje) se descartan una a una.

El PDF no va en el repositorio: la viñeta trae datos personales. Este script no copia nada de la viñeta.

Uso (desde fuente/losa): python3 pernos_desde_plano.py "ruta/al/Plano 11, ubicacion pernos.pdf" pernos_ingeniero.json
"""
import sys, json, re, math, os
import fitz   # PyMuPDF
from PIL import Image, ImageFilter

EJES_X = {'1': 6.7, "1a'": 329.8, '2': 653.2, '3': 1007.2, '3a': 1210.2, '4': 1257.3, '4a': 1525.2, '5': 1783.7}
EJES_Y = {'K': -765.1, 'J': -470.2, 'I': -170.0, 'H': 9.9, 'G2': 227.0, 'F2': 412.0, 'F1': 518.9, 'E': 958.5,
          'D': 1104.1, 'C': 1511.9, 'B': 1694.7, 'A3': 1830.6, 'A1': 2045.2, 'A': 2170.3}
D_PERNO = 12.0        # pt, diámetro del círculo de un perno
D_BURBUJA = 29.5      # pt, diámetro de la burbuja de un eje
X_LEYENDA = 2300.0    # pt: a la derecha de esto está la leyenda
PLANTA = (540.0, 60.0, X_LEYENDA, 2060.0)   # pt: recorte de la planta (sin leyenda ni viñeta)
ESCALA = 4            # px por pt al pasar a imagen
EROSION = 29          # px (≈ 7 pt): borra lo que mide menos que eso de ancho

def manchas(pag):
    """Centros (pt) de los puntos sólidos de la planta."""
    clip = fitz.Rect(*PLANTA)
    pix = pag.get_pixmap(matrix=fitz.Matrix(ESCALA, ESCALA), clip=clip, colorspace=fitz.csGRAY)
    im = Image.frombytes('L', (pix.width, pix.height), pix.samples).point(lambda v: 255 if v < 128 else 0)
    er = im.filter(ImageFilter.MinFilter(EROSION))
    w, h = er.size; px = er.load()
    quedan = {(x, y) for y in range(h) for x in range(w) if px[x, y]}
    vistos, centros = set(), []
    for q in quedan:
        if q in vistos: continue
        pila, acc = [q], []; vistos.add(q)
        while pila:
            x, y = pila.pop(); acc.append((x, y))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    r = (x + dx, y + dy)
                    if r in quedan and r not in vistos: vistos.add(r); pila.append(r)
        centros.append((clip.x0 + sum(a for a, _ in acc) / len(acc) / ESCALA, clip.y0 + sum(b for _, b in acc) / len(acc) / ESCALA))
    return centros

def ajuste(pares, tol=1.0):
    pares = list(pares); fuera = []
    while True:
        n = len(pares); sx = sum(a for a, _, _ in pares); sy = sum(b for _, b, _ in pares)
        sxx = sum(a * a for a, _, _ in pares); sxy = sum(a * b for a, b, _ in pares)
        m = (n * sxy - sx * sy) / (n * sxx - sx * sx); c = (sy - m * sx) / n
        peor = max(pares, key=lambda q: abs(m * q[0] + c - q[1]))
        res = abs(m * peor[0] + c - peor[1])
        if res <= tol or n <= 6: return m, c, res, fuera
        pares.remove(peor); fuera.append(peor[2])

def main(pdf, salida):
    pag = fitz.open(pdf)[0]
    circulos = [g['rect'] for g in pag.get_drawings() if len(g['items']) == 4 and all(it[0] == 'c' for it in g['items'])]
    palabras = pag.get_text('words')
    px, py = [], []
    for r in circulos:
        if abs(r.width - D_BURBUJA) > 0.3: continue
        t = ' '.join(w[4] for w in palabras if fitz.Rect(w[:4]).intersects(r) and fitz.Rect(w[:4]).width < r.width).strip()
        cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
        if t in EJES_X and (cy < 150 or cy > 1950): px.append((cx, EJES_X[t], t))      # burbujas de arriba y de abajo
        elif t in EJES_Y and (cx < 650 or cx > 2100): py.append((cy, EJES_Y[t], t))   # burbujas de los costados
    mx, cx, rx, fx = ajuste(px); my, cy, ry, fy = ajuste(py)
    if fx or fy: print('burbujas descartadas por quedar fuera de su eje:', ', '.join(fx + fy))
    raiz = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'estructura.js')
    E = json.loads(re.sub(r'^const DATA_ESTRUCTURA = |;\s*$', '', open(raiz).read().strip()))
    vigas = [m for m in E['miembros'] if m['c'] == 'viga' and 'entrepiso' in (m.get('d') or '')]
    def dist(x, y, m):
        (ax, ay), (bx, by) = m['a'][:2], m['b'][:2]; vx, vy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / (vx * vx + vy * vy)))
        return math.hypot(x - ax - t * vx, y - ay - t * vy)
    centros = manchas(pag)
    contornos = [((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2) for r in circulos if abs(r.width - D_PERNO) <= 0.3 and r.x0 < X_LEYENDA]
    sin_contorno = [c for c in centros if min(math.hypot(c[0] - o[0], c[1] - o[1]) for o in contornos) > 2]
    print(f'{len(centros)} puntos sólidos; {len(contornos)} círculos de contorno; sin contorno: {len(sin_contorno)}')
    puntos = []
    for xp, yp in centros:
        x, y = mx * xp + cx, my * yp + cy
        v = min(vigas, key=lambda m: dist(x, y, m))
        puntos.append({'x': round(x, 1), 'y': round(y, 1), 'viga': v['id'], 'dist_eje': round(dist(x, y, v), 1)})
    puntos.sort(key=lambda p: (p['viga'], p['x'], p['y']))
    out = {'fuente': 'Lámina 11 del ingeniero, "Losa colaborante. Ubicación pernos stud", planta 1:50 (07-10-2026)',
           'calibracion': {'x': [round(mx, 5), round(cx, 2), round(rx, 2)], 'y': [round(my, 5), round(cy, 2), round(ry, 2)],
                           'nota': 'cm = a·pt + b; el tercer valor es el mayor residuo en los ejes (cm)'},
           'puntos': puntos}
    json.dump(out, open(salida, 'w'), ensure_ascii=False, indent=1)
    print(f'{len(puntos)} pernos; calibración x {mx:.5f}·pt{cx:+.1f} (residuo {rx:.1f} cm), y {my:.5f}·pt{cy:+.1f} (residuo {ry:.1f} cm)')
    print('más lejos de su viga:', max(p['dist_eje'] for p in puntos), 'cm')

if __name__ == '__main__':
    main(*sys.argv[1:3])
