# -*- coding: utf-8 -*-
"""Re-proyecta el modelo 3D (marco de la app, cm) sobre cada vista de los PDF y dibuja la
superposicion. Calibra cada vista DESDE CERO con la grilla (burbujas + lineas de eje), sin
depender de lo que haya escrito cualquier agente.

Uso:
  python3 reproyectar.py <modelo.json> <vid|todas> [prefijo_png]
modelo.json: {"miembros": [{"id","clase","perfil","a":[x,y,z],"b":[x,y,z]}, ...]}
"""
import sys, os, json, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comun
from PIL import Image, ImageDraw, ImageFont

AQUI = comun.AQUI
GRILLA = comun.leer_json('grilla.json')
VISTAS = {v['vid']: v for v in comun.leer_json('vistas_extraccion.json')}

def _nombre(t):
    t = t.replace('´', "'").replace('`', "'").strip()
    return GRILLA.get('alias', {}).get(t, t)

_circ_cache = {}
def _circulos(lamina):
    """Centros (x,y) y radio de los circulos de burbuja (trayectos de 4 curvas, 20-45 pt)."""
    if lamina in _circ_cache:
        return _circ_cache[lamina]
    _, pg, M = comun.abrir(lamina)
    out = []
    for g in pg.get_drawings():
        its = g['items']
        if len(its) < 4 or any(it[0] != 'c' for it in its):
            continue
        r = g['rect'] * M; r.normalize()
        if 20 <= r.width <= 45 and abs(r.width - r.height) < 2:
            out.append(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2, r.width / 2))
    _circ_cache[lamina] = out
    return out

def _burbujas(v, dic):
    """Rotulos de eje = texto con nombre de la grilla DENTRO de un circulo de burbuja."""
    x0, y0, x1, y1 = v['bbox_pt']
    circ = _circulos(v['lamina'])
    out = []
    for (a, b, c, d, t) in comun.palabras(v['lamina']):
        n = _nombre(t)
        if n not in dic or not (x0 <= a <= x1 and y0 <= b <= y1):
            continue
        cx, cy = (a + c) / 2, (b + d) / 2
        cerca = [(ox, oy) for (ox, oy, r) in circ if math.hypot(ox - cx, oy - cy) < r * 0.6]
        if cerca:
            ox, oy = cerca[0]
            out.append((ox, oy, n))
    return out

_ejes_cache = {}
def _lineas_eje(v, vertical):
    """Coordenada de las lineas de eje: segmentos finos colineales cuya extension total es
    grande (las lineas de eje son trazo-punto y cruzan casi todo el dibujo)."""
    key = (v['vid'], vertical)
    if key in _ejes_cache:
        return _ejes_cache[key]
    x0, y0, x1, y1 = v['bbox_pt']
    grupos = {}
    for s in comun.trazos(v['lamina'], clip=(x0, y0, x1, y1)):
        if s['tipo'] != 'l' or s['ancho'] > 0.75:
            continue
        dx, dy = abs(s['x1'] - s['x0']), abs(s['y1'] - s['y0'])
        if vertical and dx < 0.3 and dy > 0.5:
            k = round((s['x0'] + s['x1']) / 2, 1); lo, hi = sorted((s['y0'], s['y1']))
        elif not vertical and dy < 0.3 and dx > 0.5:
            k = round((s['y0'] + s['y1']) / 2, 1); lo, hi = sorted((s['x0'], s['x1']))
        else:
            continue
        g = grupos.setdefault(k, [1e9, -1e9, 0])
        g[0] = min(g[0], lo); g[1] = max(g[1], hi); g[2] += 1
    alto = (y1 - y0) if vertical else (x1 - x0)
    res = [k for k, (lo, hi, n) in grupos.items() if n >= 6 and (hi - lo) > 0.25 * alto]
    out = np.array(sorted(res)) if res else np.array([])
    _ejes_cache[key] = out
    return out

def _ajuste(burb, dic, coord, lineas):
    pts, vals = [], []
    for (cx, cy, n) in burb:
        p = cx if coord == 'x' else cy
        if len(lineas):
            j = np.argmin(np.abs(lineas - p))
            if abs(lineas[j] - p) < 4.0:
                p = float(lineas[j])
        pts.append(p); vals.append(dic[n])
    if len(set(vals)) < 2:
        return None
    a, b, r = comun.theil_sen(vals, pts)  # pt = a*cm + b
    ok = np.abs(r) < 1.5  # pt
    if ok.sum() >= 2:
        A = np.vstack([np.array(vals)[ok], np.ones(ok.sum())]).T
        a, b = np.linalg.lstsq(A, np.array(pts)[ok], rcond=None)[0]
    res_cm = (a * np.array(vals) + b - np.array(pts)) / abs(a)
    return float(a), float(b), [(n, round(float(rc), 2)) for (_, _, n), rc in zip(burb, res_cm)]

def calibrar(vid):
    v = VISTAS[vid]
    if v['tipo'] == 'planta':
        bn = [bb for bb in _burbujas(v, GRILLA['numeros'])]
        bl = [bb for bb in _burbujas(v, GRILLA['letras'])]
        cx = _ajuste(bn, GRILLA['numeros'], 'x', _lineas_eje(v, True))
        cy = _ajuste(bl, GRILLA['letras'], 'y', _lineas_eje(v, False))
        return dict(tipo='planta', x=cx, y=cy)
    if v['tipo'] == 'elevacion_eje_numerado':
        dic, eje_app = GRILLA['letras'], 'Y'
    else:
        dic, eje_app = GRILLA['numeros'], 'X'
    bb = _burbujas(v, dic)
    ch = _ajuste(bb, dic, 'x', _lineas_eje(v, True))
    return dict(tipo='elevacion', eje_app=eje_app, h=ch, suelo=v['suelo_y_pt'], fijo=v['eje_fijo'])

def _fijo_cm(v):
    n = _nombre(v['eje_fijo'])
    return GRILLA['numeros'][n] if v['tipo'] == 'elevacion_eje_numerado' else GRILLA['letras'][n]

FILTRO_PLANTA = {  # que miembros horizontales mostrar en cada planta (rango de z del eje del miembro)
    'nivel1__planta_nivel1_principal': (200, 430),
    'nivel2__planta_nivel2': (430, 900),
    'techumbre__planta_techumbre': (430, 900),
    'fundaciones__planta_fundaciones': (-200, 60),
}

def proyectar(modelo, vid, tol=25.0):
    v = VISTAS[vid]; cal = calibrar(vid)
    segs, cortes = [], []
    if cal['tipo'] == 'planta':
        ax, bx, _ = cal['x']; ay, by, _ = cal['y']
        P = lambda x, y: (ax * x + bx, ay * y + by)
        z0, z1 = FILTRO_PLANTA.get(vid, (-1e9, 1e9))
        for m in modelo['miembros']:
            a, b = m['a'], m['b']
            vertical = math.hypot(a[0] - b[0], a[1] - b[1]) < 5
            if vertical:
                zl, zh = min(a[2], b[2]), max(a[2], b[2])
                if vid.startswith('fundaciones') and zl > 60: continue
                if vid.startswith('nivel1') and not (zl < 300 and zh > 150): continue
                if (vid.startswith('nivel2') or vid.startswith('techumbre')) and zh < 430: continue
                cortes.append((P(a[0], a[1]), m))
            else:
                zm = (a[2] + b[2]) / 2
                if z0 <= zm <= z1:
                    segs.append((P(a[0], a[1]), P(b[0], b[1]), m))
        return cal, segs, cortes
    ah, bh, _ = cal['h']; s = abs(ah); suelo = cal['suelo']; F = _fijo_cm(v)
    k_fijo, k_var = (0, 1) if cal['eje_app'] == 'Y' else (1, 0)  # numerado: fijo X (idx0), var Y (idx1)
    P = lambda u, z: (ah * u + bh, suelo - s * z)
    for m in modelo['miembros']:
        a, b = m['a'], m['b']
        fa, fb = a[k_fijo] - F, b[k_fijo] - F
        if abs(fa) <= tol and abs(fb) <= tol:
            segs.append((P(a[k_var], a[2]), P(b[k_var], b[2]), m))
        elif fa * fb < 0:
            t = fa / (fa - fb)
            u = a[k_var] + t * (b[k_var] - a[k_var]); z = a[2] + t * (b[2] - a[2])
            cortes.append((P(u, z), m))
    return cal, segs, cortes

COLORES = {'pilar': (220, 30, 30), 'viga': (0, 150, 0), 'diagonal': (0, 110, 255), 'puntal': (230, 120, 0),
           'cabio': (200, 0, 200), 'costanera': (0, 170, 170), 'tensor': (120, 60, 0), 'colgador': (120, 120, 120),
           'otro': (90, 90, 90)}

def dibujar(modelo, vid, prefijo, escala=3.0, tile=900):
    """Genera PNG por tiles (tile en pt) con el modelo re-proyectado. Devuelve la lista de PNG."""
    v = VISTAS[vid]; cal, segs, cortes = proyectar(modelo, vid)
    x0, y0, x1, y1 = v['bbox_pt']
    pngs = []
    try:
        fnt = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 14)
    except Exception:
        fnt = ImageFont.load_default()
    ty = y0; i = 0
    while ty < y1:
        tx = x0
        while tx < x1:
            clip = (tx, ty, min(tx + tile, x1), min(ty + tile, y1))
            ruta = os.path.join(AQUI, f'{prefijo}_{vid}_{i:02d}.png')
            f = comun.render(v['lamina'], ruta, clip=clip, escala=escala)
            im = Image.open(ruta).convert('RGB'); d = ImageDraw.Draw(im)
            for (p, q, m) in segs:
                c = COLORES.get(m.get('clase'), (0, 0, 0))
                d.line([f(*p), f(*q)], fill=c, width=3)
                mx, my = f((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
                d.text((mx + 4, my + 2), f"{m['id']} {m.get('perfil','')}", fill=c, font=fnt)
            for (p, m) in cortes:
                c = COLORES.get(m.get('clase'), (0, 0, 0)); px, py = f(*p)
                d.rectangle([px - 7, py - 7, px + 7, py + 7], outline=c, width=3)
                d.text((px + 9, py - 7), f"{m['id']} {m.get('perfil','')}", fill=c, font=fnt)
            im.save(ruta); pngs.append(ruta); i += 1
            tx += tile
        ty += tile
    return cal, pngs

if __name__ == '__main__':
    modelo = json.load(open(sys.argv[1]))
    objetivo = sys.argv[2]
    prefijo = sys.argv[3] if len(sys.argv) > 3 else 'rp'
    vids = list(VISTAS) if objetivo == 'todas' else [objetivo]
    for vid in vids:
        cal, pngs = dibujar(modelo, vid, prefijo)
        res = cal.get('h') or cal.get('x')
        print(vid, 'calibracion', {k: (v[2] if isinstance(v, tuple) else v) for k, v in cal.items() if k in ('h', 'x', 'y')})
        print('  png:', len(pngs), pngs[:2])
