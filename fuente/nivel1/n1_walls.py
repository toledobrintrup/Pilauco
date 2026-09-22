# -*- coding: utf-8 -*-
"""Nivel 1: muros como poligonos, a partir de los segmentos de la capa 1.28."""
import json, math, bisect
import numpy as np, cv2

L = json.load(open('n1_layers_cm.json'))
segs = [(it[1][0], it[1][1], it[2][0], it[2][1]) for k in ('(1.28, 0.0)', '(1.7, 0.0)') for it in L.get(k, []) if it[0] == 'l']

PX, OFF = 4, 30
W, H = 2200, 2190
img = np.zeros((H * PX + 2 * PX * OFF, W * PX + 2 * PX * OFF), np.uint8)
px = lambda v: int(round((v + OFF) * PX))
for x0, y0, x1, y1 in segs:
    cv2.line(img, (px(x0), px(y0)), (px(x1), px(y1)), 255, 1)
img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))

VX = sorted(set(round(s[0], 2) for s in segs if abs(s[0] - s[2]) < 0.05))
HY = sorted(set(round(s[1], 2) for s in segs if abs(s[1] - s[3]) < 0.05))
def snap(v, arr, tol=1.2):
    i = bisect.bisect_left(arr, v); best = None
    for j in (i - 1, i):
        if 0 <= j < len(arr) and abs(arr[j] - v) <= tol:
            if best is None or abs(arr[j] - v) < abs(best - v): best = arr[j]
    return best if best is not None else v

inv = (img == 0).astype(np.uint8)
n, lab, stats, cent = cv2.connectedComponentsWithStats(inv, connectivity=4)
dist = cv2.distanceTransform(inv, cv2.DIST_L2, 5)
walls, rooms, small = [], [], []
for i in range(1, n):
    x, y, w, h, area = stats[i]
    if x == 0 or y == 0 or x + w >= img.shape[1] or y + h >= img.shape[0]: continue
    m = (lab == i)
    maxr = dist[m].max() / PX
    area_cm2 = area / PX / PX
    cnts, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    approx = cv2.approxPolyDP(max(cnts, key=cv2.contourArea), 1.5, True)
    pts = [(round(snap(p[0][0] / PX - OFF, VX), 1), round(snap(p[0][1] / PX - OFF, HY), 1)) for p in approx]
    clean = []
    for k in range(len(pts)):
        p0, p1, p2 = pts[k - 1], pts[k], pts[(k + 1) % len(pts)]
        if (p1[0] == p0[0] == p2[0]) or (p1[1] == p0[1] == p2[1]): continue
        clean.append(p1)
    e = dict(pts=clean, area_m2=round(float(area_cm2) / 1e4, 3), maxr=round(float(maxr), 1),
             bbox=[round(float(x / PX - OFF), 1), round(float(y / PX - OFF), 1), round(float(w / PX), 1), round(float(h / PX), 1)])
    if maxr <= 12 and area_cm2 < 60000: walls.append(e)
    elif area_cm2 < 10000: small.append(e)
    else: rooms.append(e)
print('muros', len(walls), ' zonas grandes', len(rooms), ' chicas', len(small))
for r in sorted(rooms, key=lambda r: -r['area_m2']):
    print(f"  ZONA bbox={r['bbox']} area={r['area_m2']:7.2f} m2 maxr={r['maxr']:5.1f} pts={len(r['pts'])}")
json.dump(dict(walls=walls, rooms=rooms, small=small, segs=segs), open('n1_geom.json', 'w'))
