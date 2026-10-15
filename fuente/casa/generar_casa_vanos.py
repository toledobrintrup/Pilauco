#!/usr/bin/env python3
"""Muros, puertas y ventanas de la casa para el 3D, a partir del plano (data.js).
- Muros: los polígonos de wallsPath (ya traen los huecos de puertas y ventanas) partidos en rectángulos; a los que no traen hueco se les resta el vano.
- Puertas y pasos: openings de cada variante (eje y ancho), con el espesor del muro vecino.
- Ventanas: tabla curada de las líneas de windowsPath (V1..V28, P1, P4, P6) revisada contra el plano el 2026-10-15.
Alturas (Gabriel, 15-10-2026): todas las ventanas de 2,80 (del piso al dintel, mismo dintel que las puertas), puertas 2,80, pasos 2,80.
Uso: python3 fuente/casa/generar_casa_vanos.py  →  casa_vanos.js (DATA_CASA)"""
import json, re, pathlib
raiz = pathlib.Path(__file__).resolve().parents[2]
s = open(raiz / 'data.js', encoding='utf-8').read()
H_VANO = 280.0   # dintel de ventanas, puertas y pasos (cm sobre el piso del nivel)
ANTEPECHO = 0.0  # las ventanas parten en el piso (cambiar aquí si se quiere antepecho)
def datos(name):
    m = re.search(r'const ' + name + r' = (\{.*?\});?\n', s, re.S); return json.loads(m.group(1))
def subpolys(path):
    return [[(float(a), float(b)) for a, b in re.findall(r'([\d.\-]+) ([\d.\-]+)', p)] for p in path.split('M') if p.strip()]
def rect_strips(poly):
    """polígono rectilíneo → rectángulos [x0, y0, x1, y1] por bandas de y, unidos verticalmente cuando comparten x0..x1"""
    pts = [p for i, p in enumerate(poly) if i == 0 or (abs(p[0] - poly[i - 1][0]) > 0.05 or abs(p[1] - poly[i - 1][1]) > 0.05)]
    if len(pts) > 1 and abs(pts[0][0] - pts[-1][0]) < 0.05 and abs(pts[0][1] - pts[-1][1]) < 0.05: pts = pts[:-1]
    if len(pts) < 3: return []
    ys = sorted(set(round(p[1], 2) for p in pts)); out = []
    for ya, yb in zip(ys, ys[1:]):
        if yb - ya < 0.5: continue
        ym = (ya + yb) / 2; xs = []
        for i in range(len(pts)):
            (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
            if abs(x0 - x1) < 0.05 and min(y0, y1) < ym < max(y0, y1): xs.append(x0)
        xs.sort()
        for a, b in zip(xs[0::2], xs[1::2]):
            if b - a > 0.5: out.append([a, ya, b, yb])
    out.sort(key=lambda r: (round(r[0], 1), round(r[2], 1), r[1])); merged = []
    for r in out:
        if merged and abs(merged[-1][0] - r[0]) < 0.3 and abs(merged[-1][2] - r[2]) < 0.3 and abs(merged[-1][3] - r[1]) < 0.3: merged[-1][3] = r[3]
        else: merged.append(list(r))
    return merged
def restar(rects, o):
    """quita el rectángulo o=[x0,y0,x1,y1] de la lista de rectángulos"""
    out = []
    for r in rects:
        ix0, iy0, ix1, iy1 = max(r[0], o[0]), max(r[1], o[1]), min(r[2], o[2]), min(r[3], o[3])
        if ix1 - ix0 < 0.5 or iy1 - iy0 < 0.5: out.append(r); continue
        if ix0 - r[0] > 0.5: out.append([r[0], r[1], ix0, r[3]])
        if r[2] - ix1 > 0.5: out.append([ix1, r[1], r[2], r[3]])
        if iy0 - r[1] > 0.5: out.append([ix0, r[1], ix1, iy0])
        if r[3] - iy1 > 0.5: out.append([ix0, iy1, ix1, r[3]])
    return out
# ---------- ventanas y vanos vidriados, curados del plano (cm; p = eje del muro, e = espesor, lo..hi = extensión a lo largo) ----------
# tipo: ventana (fija) · puerta vidriada (1 o 2 hojas según ancho) · puerta corredera (vidriada, 2 hojas)
VENT = {
 1: [
  ('V1',  'h', 1688.2, 25, 144.6, 541.6, 'ventana', 'ventana fija del living a la terraza sur'),
  ('V2',  'v', 658.7,  25, 1979.7, 2158.7, 'ventana', 'ventana fija del hall de acceso, poniente'),
  ('V3',  'h', 2171.6, 25, 671.3, 989.1, 'ventana', 'vidrio fijo del hall de acceso al sur (doble altura: sigue en el nivel 2)'),
  ('V4',  'v', 1001.7, 25, 2049.8, 2158.8, 'ventana', 'ventana fija del hall de acceso, oriente'),
  ('V5',  'h', 1505.3, 25, 1253.2, 1550.2, 'ventana', 'ventana fija del comedor al acceso cubierto'),
  ('V6',  'v', 1777.2, 25, 1182.3, 1429.3, 'ventana', 'ventana fija del comedor, oriente'),
  ('V7',  'h', 113.0,  25, 1386.9, 1602.9, 'ventana', 'ventana de la lavandería al norte'),
  ('V8',  'h', 12.7,   25, 41.6, 425.1, 'ventana', 'ventana fija de la oficina al norte, hasta la puerta doble'),
  ('P-N', 'h', 12.7,   25, 425.1, 625.1, 'puerta vidriada', 'puerta vidriada de 2 hojas de la galería al norte (P 200 del plano)'),
  ('V9',  'v', 17.5,   25, 20.2, 617.2, 'ventana', 'vidrio fijo de la oficina al poniente (todo el muro)'),
  ('V10', 'v', 12.3,   25, 745.4, 982.4, 'ventana', 'ventana fija del living al poniente'),
  ('V11', 'v', 12.3,   25, 1112.4, 1626.4, 'ventana', 'ventana fija del living al poniente'),
  ('P4a', 'h', 232.9,  25, 687.8, 858.9, 'ventana', 'paño fijo de la cocina al patio norte'),
  ('P4',  'h', 232.9,  25, 858.9, 1050.9, 'puerta corredera', 'corredera vidriada de la cocina al patio norte (P4 del plano)'),
  ('P4b', 'h', 232.9,  25, 1050.9, 1222.8, 'ventana', 'paño fijo de la cocina al patio norte'),
  ('P1f', 'v', 1001.7, 25, 1532.8, 1553.0, 'ventana', 'paño fijo junto a la puerta de entrada'),
  ('P1',  'v', 1001.7, 25, 1553.0, 1673.0, 'puerta vidriada', 'puerta de entrada desde el acceso cubierto (P 120 del plano)'),
  ('P3a', 'v', 2177.1, 25, 235.5, 325.5, 'puerta', 'puerta de la sala de máquinas al oriente (P3)'),
  ('P3b', 'v', 2177.1, 25, 357.4, 447.4, 'puerta', 'puerta de la bodega al oriente (P3)'),
 ],
 2: [
  ('V2',  'v', 658.8,  25, 1979.5, 2158.5, 'ventana', 'ventana fija del hall de doble altura, poniente (nivel 2)'),
  ('V3',  'h', 2171.6, 25, 671.3, 989.1, 'ventana', 'vidrio fijo del hall de doble altura al sur (nivel 2)'),
  ('V4',  'v', 1001.8, 25, 2049.8, 2158.8, 'ventana', 'ventana fija del hall de doble altura, oriente (nivel 2)'),
  ('V12', 'h', 1825.0, 25, 145.0, 242.0, 'puerta vidriada', 'puerta vidriada del dormitorio de visitas a la terraza sur (P 97 del plano)'),
  ('V13', 'h', 1825.0, 25, 364.7, 541.7, 'ventana', 'ventana del family room a la terraza sur'),
  ('V14', 'h', 2036.7, 25, 1100.1, 1197.1, 'ventana', 'ventana del WKC hijo 2 al sur'),
  ('V15', 'h', 2036.7, 25, 1361.1, 1657.1, 'ventana', 'ventana del dormitorio hijo 2 al sur'),
  ('V16', 'v', 1777.5, 25, 1470.3, 1617.3, 'ventana', 'ventana del dormitorio hijo 2 al oriente'),
  ('V17', 'v', 1777.5, 25, 1205.6, 1352.6, 'ventana', 'ventana del baño hijos al oriente'),
  ('V18', 'v', 1777.5, 25, 941.2, 1088.2, 'ventana', 'ventana del dormitorio hijo 1 al oriente'),
  ('V19', 'v', 1777.5, 25, 535.4, 682.4, 'ventana', 'ventana del dormitorio hijo 1 al oriente'),
  ('V20', 'v', 1777.5, 25, 91.0, 438.0, 'ventana', 'ventana del WKC Maggie al oriente'),
  ('V21', 'h', 12.5,   25, 1066.1, 1413.1, 'ventana', 'ventana del WKC Maggie al norte'),
  ('V22', 'h', 12.5,   25, 383.9, 572.9, 'ventana', 'ventana del WKC Gabriel al norte'),
  ('V24', 'h', 12.5,   25, 112.0, 258.0, 'ventana', 'ventana del dormitorio matrimonial al norte'),
  ('P6',  'h', 12.5,   25, 270.0, 360.0, 'puerta vidriada', 'puerta vidriada del dormitorio matrimonial a la terraza norte (P6 + V23 del plano)'),
  ('V25', 'v', 12.5,   25, 247.0, 394.0, 'ventana', 'ventana del dormitorio matrimonial al poniente'),
  ('V26', 'v', 12.5,   25, 572.8, 870.8, 'ventana', 'ventana del baño matrimonial al poniente'),
  ('V27', 'v', 12.5,   25, 1113.1, 1259.1, 'ventana', 'ventana del baño de visitas al poniente'),
  ('V28', 'v', 12.5,   25, 1479.1, 1626.1, 'ventana', 'ventana del dormitorio de visitas al poniente'),
 ]}
OPACAS = {1: {'P3a', 'P3b'}, 2: set()}
salida = {'fuente': 'muros de wallsPath y puertas de openings (data.js, plano); ventanas curadas de windowsPath contra el plano (fuente/casa/generar_casa_vanos.py, 2026-10-15)',
          'alturas': dict(dintel=H_VANO, antepecho=ANTEPECHO, dato='Gabriel (15-10-2026): ventanas de 2,80 iguales en los dos niveles, del piso al dintel; puertas de 2,80 (recomendación anterior); marcos europeos gruesos')}
for nivel, name, vn in ((1, 'DATA_N1', 'v1'), (2, 'DATA_N2', 'v2')):
    d = datos(name); v = d['variants'][vn]
    rects = [r for poly in subpolys(v['wallsPath']) for r in rect_strips(poly)]
    rects = [r for r in rects if (r[2] - r[0]) > 1 and (r[3] - r[1]) > 1]
    vanos = []
    def rect_vano(o, p, e, lo, hi): return [lo, p - e / 2, hi, p + e / 2] if o == 'h' else [p - e / 2, lo, p + e / 2, hi]
    for id_, o, p, e, lo, hi, tipo, nota in VENT[nivel]:
        a, b = ([lo, p], [hi, p]) if o == 'h' else ([p, lo], [p, hi])
        z0 = 0.0 if tipo != 'ventana' else ANTEPECHO
        vanos.append(dict(id=id_, tipo=tipo, a=a, b=b, e=e, z0=z0, z1=H_VANO, ancho=round(hi - lo, 1), alto=round(H_VANO - z0, 1), d=nota))
        rects = restar(rects, rect_vano(o, p, e, lo, hi))
    # puertas y pasos del plano (openings), menos los que ya son ventanas
    for k, op in enumerate(v['openings']):
        a, b = op['a'], op['b']; vert = abs(a[0] - b[0]) < 1
        lo, hi = sorted([a[1], b[1]]) if vert else sorted([a[0], b[0]]); p = a[0] if vert else a[1]
        dup = any((vn_['b'][0] - vn_['a'][0] < 1) == vert and abs((vn_['a'][0] if vert else vn_['a'][1]) - p) < 15 and min(hi, max(vn_['a'][1] if vert else vn_['a'][0], vn_['b'][1] if vert else vn_['b'][0])) - max(lo, min(vn_['a'][1] if vert else vn_['a'][0], vn_['b'][1] if vert else vn_['b'][0])) > 0.5 * (hi - lo) for vn_ in vanos)
        if dup: continue
        # espesor: el muro vecino que toca un extremo del vano; si no hay, el que lo contiene; si no, 15 centrado
        e, pc = None, p
        # solo muros delgados (≤ 30) en el sentido del vano, con el eje del vano dentro de su espesor
        for r in rects:
            if vert and r[2] - r[0] <= 30 and r[0] - 2 <= p <= r[2] + 2 and (abs(r[3] - lo) < 3 or abs(r[1] - hi) < 3): e, pc = r[2] - r[0], (r[0] + r[2]) / 2; break
            if not vert and r[3] - r[1] <= 30 and r[1] - 2 <= p <= r[3] + 2 and (abs(r[2] - lo) < 3 or abs(r[0] - hi) < 3): e, pc = r[3] - r[1], (r[1] + r[3]) / 2; break
        if e is None:
            for r in rects:
                if vert and r[2] - r[0] <= 30 and r[0] <= p <= r[2] and r[1] < (lo + hi) / 2 < r[3]: e, pc = r[2] - r[0], (r[0] + r[2]) / 2; break
                if not vert and r[3] - r[1] <= 30 and r[1] <= p <= r[3] and r[0] < (lo + hi) / 2 < r[2]: e, pc = r[3] - r[1], (r[1] + r[3]) / 2; break
        if e is None: e = 15.0
        e = min(e, 25.0)
        tipo = 'paso' if op['type'] == 'passage' else 'puerta'
        id_ = f"{'paso' if tipo == 'paso' else 'P'}{nivel}-{k + 1}"
        aa, bb = ([pc, lo], [pc, hi]) if vert else ([lo, pc], [hi, pc])
        vanos.append(dict(id=id_, tipo=tipo, a=aa, b=bb, e=round(e, 1), z0=0.0, z1=H_VANO, ancho=round(hi - lo, 1), alto=H_VANO, d=('paso abierto' if tipo == 'paso' else f"puerta de {op['gap'] / 100:.2f}".replace('.', ',') + ' (plano)') + ' · dintel a 2,80'))
        rects = restar(rects, rect_vano('v' if vert else 'h', pc, e, lo, hi))
    salida[f'n{nivel}'] = dict(muros=[[round(c, 1) for c in r] for r in rects], vanos=vanos)
    print(f'nivel {nivel}: {len(rects)} rectángulos de muro · {len(vanos)} vanos ({sum(1 for x in vanos if x["tipo"] == "ventana")} ventanas, {sum(1 for x in vanos if "puerta" in x["tipo"])} puertas, {sum(1 for x in vanos if x["tipo"] == "paso")} pasos) · espesores de puertas: {sorted(set(x["e"] for x in vanos if x["tipo"] != "ventana"))}')
js = 'const DATA_CASA = ' + json.dumps(salida, ensure_ascii=False, separators=(',', ':')) + ';\n'
(raiz / 'casa_vanos.js').write_text(js, encoding='utf-8'); print('casa_vanos.js', len(js), 'bytes')
