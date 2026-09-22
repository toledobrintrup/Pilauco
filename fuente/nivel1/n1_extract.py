# -*- coding: utf-8 -*-
"""Nivel 1: extrae capas de dibujo y texto del PDF, en cm, en el sistema del nivel 2."""
import fitz, json, collections, os

PDF = '/Users/gabrieltoledobrintrup/Library/Mobile Documents/com~apple~CloudDocs/04_Negocios/N03_Inversión Inmobiliaria/06_Casa Pilauco/01_Arquitectura/01_Planos/L2.PLARQ.29.12.2025.pdf'
# Origen y escala: fijados haciendo calzar los ejes 1,2,3,5 y A del nivel 1 con los del
# nivel 2 (error < 0,5 cm). S es la escala 1:50 del proyecto, igual en ambas láminas.
S = (1317.24 - 302.23) / 1790.0
X0, Y0 = 326.70, 733.46
XMAX_PT = 1780          # descarta la planta Nivel -1 y la otra construcción (derecha)

def cm(p): return (round((p[0] - X0) / S, 2), round((p[1] - Y0) / S, 2))

pg = fitz.open(PDF)[0]
layers = collections.defaultdict(list)
for p in pg.get_drawings():
    if p['rect'].x0 > XMAX_PT: continue
    w = p.get('width'); c = p.get('color')
    key = f"({round(w,2) if w is not None else 0}, {round(c[0],2) if c else 'f'})"
    for it in p['items']:
        if it[0] == 'l':    layers[key].append(['l', cm(it[1]), cm(it[2])])
        elif it[0] == 'c':  layers[key].append(['c', cm(it[1]), cm(it[2]), cm(it[3]), cm(it[4])])
        elif it[0] == 're': layers[key].append(['re', cm((it[1].x0, it[1].y0)), cm((it[1].x1, it[1].y1))])
        elif it[0] == 'qu': layers[key].append(['qu'] + [cm(pt) for pt in it[1]])

words = []
for b in pg.get_text('dict')['blocks']:
    for l in b.get('lines', []):
        for s in l['spans']:
            t = s['text'].strip()
            if not t or s['bbox'][0] > XMAX_PT: continue
            x, y = cm((s['bbox'][0], s['bbox'][3]))
            words.append(dict(t=t, x=x, y=y, size=round(s['size'], 1), dir=[round(v, 2) for v in l['dir']],
                              w=round((s['bbox'][2] - s['bbox'][0]) / S, 1)))

json.dump(layers, open('n1_layers_cm.json', 'w'))
json.dump(words, open('n1_words.json', 'w'), ensure_ascii=False)
print('capas:', len(layers), ' items:', sum(len(v) for v in layers.values()), ' palabras:', len(words))
seg = [it for it in layers.get('(1.28, 0.0)', []) if it[0] == 'l']
xs = [v for it in seg for v in (it[1][0], it[2][0])]; ys = [v for it in seg for v in (it[1][1], it[2][1])]
print(f'muros(1.28): {len(seg)} seg   x {min(xs):.1f}..{max(xs):.1f}   y {min(ys):.1f}..{max(ys):.1f}')
for k in ['(0.23, 0.53)', '(0.28, 0.53)', '(0.43, 0.5)', '(0.57, 0.38)', '(0.57, 0.41)', '(0.01, 0.3)', '(0.99, 0.0)', '(0.03, 0.0)']:
    print(f'  {k:>16}: {len(layers.get(k, []))}')
