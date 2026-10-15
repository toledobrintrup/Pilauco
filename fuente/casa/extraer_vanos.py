#!/usr/bin/env python3
"""Candidatos a ventanas de la casa, desde windowsPath de data.js (líneas paralelas dentro del muro) y openings (puertas y pasos).
Imprime por nivel: cada grupo de líneas paralelas (ventana) con su muro, extensión y etiqueta V más cercana. Uso: python3 extraer_vanos.py"""
import json, re, sys, pathlib
raiz = pathlib.Path(__file__).resolve().parents[2]
s = open(raiz / 'data.js', encoding='utf-8').read()
def datos(name):
    m = re.search(r'const ' + name + r' = (\{.*?\});?\n', s, re.S); return json.loads(m.group(1))
def segs(path):
    out = []; cur = None
    for m in re.finditer(r'([ML])([\d.\-]+) ([\d.\-]+)', path):
        c, x, y = m.group(1), float(m.group(2)), float(m.group(3))
        if c == 'M': cur = (x, y)
        else: out.append((cur, (x, y))); cur = (x, y)
    return out
def subpolys(path):
    return [[(float(a), float(b)) for a, b in re.findall(r'([\d.\-]+) ([\d.\-]+)', p)] for p in path.split('M') if p.strip()]
def dentro(poly, x, y):
    n = len(poly); ins = False; j = n - 1
    for i in range(n):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi: ins = not ins
        j = i
    return ins
for name, vn in (('DATA_N1', 'v1'), ('DATA_N2', 'v2')):
    d = datos(name); v = d['variants'][vn]; muros = subpolys(v['wallsPath'])
    # 1) líneas colineales (horizontales por y, verticales por x), unidas si se tocan
    lines = {}
    for a, b in segs(v['windowsPath']):
        if abs(a[1] - b[1]) < 0.6: key = ('h', round(a[1] * 2) / 2); lo, hi = sorted([a[0], b[0]])
        elif abs(a[0] - b[0]) < 0.6: key = ('v', round(a[0] * 2) / 2); lo, hi = sorted([a[1], b[1]])
        else: continue
        lines.setdefault(key, []).append((lo, hi))
    lineas = []
    for key, iv in lines.items():
        iv.sort(); cur = list(iv[0])
        for lo, hi in iv[1:]:
            if lo <= cur[1] + 12: cur[1] = max(cur[1], hi)
            else: lineas.append((key[0], key[1], cur[0], cur[1])); cur = [lo, hi]
        lineas.append((key[0], key[1], cur[0], cur[1]))
    lineas = [l for l in lineas if l[3] - l[2] > 40]
    # 2) grupos: misma orientación, perpendicular a menos de 30 cm, extensiones que se solapan ≥ 60 %
    grupos = []
    for l in sorted(lineas, key=lambda l: (l[0], l[1])):
        for g in grupos:
            if g['o'] == l[0] and abs(g['p'] - l[1]) <= 30:
                sol = min(g['hi'], l[3]) - max(g['lo'], l[2])
                if sol > 0.6 * min(g['hi'] - g['lo'], l[3] - l[2]): g['ls'].append(l); g['p'] = sum(x[1] for x in g['ls']) / len(g['ls']); g['lo'] = sorted(x[2] for x in g['ls'])[len(g['ls']) // 2]; g['hi'] = sorted(x[3] for x in g['ls'])[len(g['ls']) // 2]; break
        else: grupos.append(dict(o=l[0], p=l[1], lo=l[2], hi=l[3], ls=[l]))
    print('=====', name, vn, '· muros:', len(muros), '· grupos:', len(grupos))
    for g in sorted(grupos, key=lambda g: (g['o'], g['p'], g['lo'])):
        if len(g['ls']) < 2: continue
        cx, cy = ((g['lo'] + g['hi']) / 2, g['p']) if g['o'] == 'h' else (g['p'], (g['lo'] + g['hi']) / 2)
        en_muro = any(dentro(m, cx, cy) for m in muros)
        et = min(v['windows'], key=lambda w: (w['x'] - cx) ** 2 + (w['y'] - cy) ** 2); dist = ((et['x'] - cx) ** 2 + (et['y'] - cy) ** 2) ** .5
        ab = [o for o in v['openings'] if (abs(o['a'][1] - g['p']) < 15 and abs(o['a'][1] - o['b'][1]) < 1 and g['o'] == 'h') or (abs(o['a'][0] - g['p']) < 15 and abs(o['a'][0] - o['b'][0]) < 1 and g['o'] == 'v')]
        print(f"  {g['o']} p={g['p']:7.1f}  {g['lo']:7.1f}..{g['hi']:7.1f}  ancho {g['hi']-g['lo']:6.1f}  líneas {len(g['ls'])}  {'EN MURO' if en_muro else 'fuera  '}  etiqueta {et['t']:>9} a {dist:5.0f}  {'abertura: ' + ', '.join(o['type']+' '+str(o['gap']) for o in ab) if ab else ''}")
