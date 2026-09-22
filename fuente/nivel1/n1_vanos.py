# -*- coding: utf-8 -*-
"""Nivel 1: detecta vanos (pares de extremos de muro enfrentados) y recintos."""
import json, math
import numpy as np, cv2
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union

g = json.load(open('n1_geom.json')); L = json.load(open('n1_layers_cm.json'))
WORDS = json.load(open('n1_words.json'))
MAXGAP = float(__import__('sys').argv[1]) if len(__import__('sys').argv) > 1 else 380.0

walls = [Polygon(w['pts']) for w in g['walls'] if len(w['pts']) >= 4 and Polygon(w['pts']).is_valid]
wall_union = unary_union([w.buffer(0) for w in walls])
caps = []
for wi, w in enumerate(walls):
    pts = list(w.exterior.coords)[:-1]
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        if 8 <= ln <= 30:
            caps.append(dict(wi=wi, a=a, b=b, mid=((a[0]+b[0])/2, (a[1]+b[1])/2),
                             horiz=abs(a[1]-b[1]) < 0.01, ln=ln))
print('extremos de muro:', len(caps))

cand = []
for i, c1 in enumerate(caps):
    for j, c2 in enumerate(caps):
        if j <= i or c1['horiz'] != c2['horiz']: continue
        if c1['horiz']:
            if abs(c1['mid'][0]-c2['mid'][0]) > 4: continue
            gap = abs(c1['mid'][1]-c2['mid'][1])
        else:
            if abs(c1['mid'][1]-c2['mid'][1]) > 4: continue
            gap = abs(c1['mid'][0]-c2['mid'][0])
        if gap < 5 or gap > MAXGAP: continue
        seg = LineString([c1['mid'], c2['mid']])
        if wall_union.intersection(seg.buffer(0.5)).area > 43: continue
        cand.append(dict(a=c1['mid'], b=c2['mid'], gap=round(gap,1), horiz=not c1['horiz'],
                         quad=[c1['a'], c1['b'], c2['b'], c2['a']]))
cand.sort(key=lambda o: o['gap'])
vanos, usados = [], set()
for o in cand:
    ka = (round(o['a'][0]), round(o['a'][1])); kb = (round(o['b'][0]), round(o['b'][1]))
    if ka in usados or kb in usados: continue
    usados.add(ka); usados.add(kb); vanos.append(o)
print('vanos emparejados:', len(vanos))
for o in sorted(vanos, key=lambda o: -o['gap']):
    print(f"   {o['gap']:6.1f} cm  en ({o['a'][0]:.0f},{o['a'][1]:.0f}) -> ({o['b'][0]:.0f},{o['b'][1]:.0f})")

def ordena(q):
    if math.hypot(q[1][0]-q[2][0], q[1][1]-q[2][1]) > math.hypot(q[1][0]-q[3][0], q[1][1]-q[3][1]):
        q = [q[0], q[1], q[3], q[2]]
    return q
json.dump([dict(a=[round(v,1) for v in o['a']], b=[round(v,1) for v in o['b']], gap=o['gap'],
                quad=[[round(v,1) for v in p] for p in ordena(o['quad'])]) for o in vanos],
          open('n1_vanos.json','w'))

PX, OFF, W, H = 4, 40, 2200, 2190
SH = (H*PX+2*PX*OFF, W*PX+2*PX*OFF); px = lambda v: int(round((v+OFF)*PX))
img = np.zeros(SH, np.uint8)
for w in g['walls']:
    cv2.fillPoly(img, [np.array([(px(x), px(y)) for x, y in w['pts']], np.int32)], 255)
for o in vanos:
    cv2.fillPoly(img, [np.array([(px(x), px(y)) for x, y in ordena(o['quad'])], np.int32)], 255)
for k in ['(0.43, 0.5)', '(0.28, 0.53)', '(0.23, 0.53)', '(0.43, 0.0)']:
    for it in L.get(k, []):
        if it[0] == 'l': cv2.line(img, (px(it[1][0]), px(it[1][1])), (px(it[2][0]), px(it[2][1])), 255, 2)
        elif it[0] == 're': cv2.rectangle(img, (px(it[1][0]), px(it[1][1])), (px(it[2][0]), px(it[2][1])), 255, 2)
        elif it[0] == 'c': cv2.line(img, (px(it[1][0]), px(it[1][1])), (px(it[4][0]), px(it[4][1])), 255, 2)
img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, np.ones((13, 13), np.uint8))
inv = (img == 0).astype(np.uint8)
n, lab, stats, cent = cv2.connectedComponentsWithStats(inv, connectivity=4)
fuera = lab[2, 2]
et = [w for w in WORDS if w['size'] < 10 and w['t'].isupper() and len(w['t']) > 2 and not w['t'].replace('.','').isdigit()]
res = []
for i in range(1, n):
    if i == fuera: continue
    x, y, w, h, area = stats[i]; a = area/PX/PX/1e4
    if a < 0.8: continue
    m = (lab == i)
    d = [e['t'] for e in et if 0 <= px(e['y']) < SH[0] and 0 <= px(e['x']) < SH[1] and m[px(e['y']), px(e['x'])]]
    res.append((a, [round(x/PX-OFF), round(y/PX-OFF), round(w/PX), round(h/PX)], d, i))
res.sort(key=lambda c: -c[0])
print(f'\n{len(res)} recintos:')
for a, b, d, i in res: print(f'  {a:7.2f} m2  bbox={b}  ->  {", ".join(d) if d else "(sin etiqueta)"}')
vis = np.full(SH+(3,), 255, np.uint8); rng = np.random.default_rng(7)
for a,b,d,i in res: vis[lab==i] = rng.integers(120,250,3)
vis[img>0] = (30,30,30)
cv2.imwrite('n1_zonas.png', cv2.resize(vis, None, fx=0.13, fy=0.13, interpolation=cv2.INTER_AREA))
