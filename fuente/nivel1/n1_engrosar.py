# -*- coding: utf-8 -*-
"""Normaliza espesores del nivel 1: perimetrales 25 cm (cara exterior fija) e
interiores 15 cm (centrados). Mismo criterio y mismo algoritmo que build_thick.py
del nivel 2: se sondea cada tramo de recinto, se mide el muro real que tiene
enfrente y se desplaza la cara interior lo necesario."""
import math
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union

T_EXT, T_INT = 25.0, 15.0

def _ring(p, nd=2):
    if p.geom_type != 'Polygon': p = max(p.geoms, key=lambda g: g.area)
    return [(round(x, nd), round(y, nd)) for x, y in list(p.exterior.coords)[:-1]]
def _despike(P):
    Q = P.buffer(1.6, join_style='mitre').buffer(-3.2, join_style='mitre').buffer(1.6, join_style='mitre').simplify(0.25)
    if Q.geom_type != 'Polygon': Q = max(Q.geoms, key=lambda g: g.area)
    return Q
def _cuadra_diagonales(pts, tol=1.5):
    """Un tramo realmente diagonal es el barrido de una puerta que mordio el recinto.
    Se restituye insertando la esquina que queda FUERA del poligono."""
    P = [tuple(p) for p in pts]
    i = 0
    while i < len(P) and len(P) < 80:
        a, b = P[i - 1], P[i]
        dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
        if dx > tol and dy > tol:
            poly = Polygon(P)
            c1, c2 = (b[0], a[1]), (a[0], b[1])
            c = c1 if not poly.contains(Point(*c1)) else c2
            P.insert(i, c); i += 1
        i += 1
    return P

def _rectificar(pts, tol=1.5):
    """Endereza el anillo promediando (no arrastrando vertices, que deforma el recinto):
    colapsa tramos de menos de tol, pone rectos los casi rectos y quita colineales."""
    P = [[float(x), float(y)] for x, y in pts]
    for _ in range(4):
        i = 0
        while i < len(P) and len(P) > 4:
            a, b = P[i - 1], P[i]
            if math.hypot(a[0] - b[0], a[1] - b[1]) < tol:
                a[0] = b[0] = (a[0] + b[0]) / 2; a[1] = b[1] = (a[1] + b[1]) / 2
                del P[i]
            else: i += 1
        for i in range(len(P)):
            a, b = P[i - 1], P[i]
            dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
            if dx < tol <= dy: m = (a[0] + b[0]) / 2; a[0] = b[0] = m
            elif dy < tol <= dx: m = (a[1] + b[1]) / 2; a[1] = b[1] = m
        cambio = True
        while cambio and len(P) > 4:
            cambio = False
            for k in range(len(P)):
                p0, p1, p2 = P[k - 1], P[k], P[(k + 1) % len(P)]
                if (abs(p1[0] - p0[0]) < 0.05 and abs(p1[0] - p2[0]) < 0.05) or \
                   (abs(p1[1] - p0[1]) < 0.05 and abs(p1[1] - p2[1]) < 0.05):
                    del P[k]; cambio = True; break
    return [(round(x, 2), round(y, 2)) for x, y in P]

def _clean(pts):
    return _rectificar(_cuadra_diagonales(pts))

def engrosar(rooms, wall_polys, verbose=True):
    muros = unary_union([Polygon(w['pts']).buffer(0) for w in wall_polys if len(w['pts']) >= 4])
    def espesor(p, n):
        probe = LineString([(p[0] + n[0] * 0.05, p[1] + n[1] * 0.05), (p[0] + n[0] * 60, p[1] + n[1] * 60)])
        inter = probe.intersection(muros)
        piezas = [inter] if inter.geom_type == 'LineString' else [g for g in getattr(inter, 'geoms', []) if g.geom_type == 'LineString']
        ini = Point(probe.coords[0]); best = None
        for g in piezas:
            d = ini.distance(g)
            if d < 1.0 and (best is None or d < best[0]): best = (d, g.length)
        return best if best else (0.0, 0.0)

    # Sin _despike: ese suavizado del nivel 2 se come escalones reales de ~13 cm y los
    # deja como diagonal. Los poligonos del nivel 1 ya vienen limpios del rasterizado.
    Ps = [Polygon(_clean(_ring(Polygon(r['pts'])))) for r in rooms]
    union = unary_union([p.buffer(0) for p in Ps])
    strips, wins, informe = [], [], []
    for r, P in zip(rooms, Ps):
        pts = _ring(P); n = len(pts); deltas = []
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            vert = abs(a[0] - b[0]) < 0.01
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            nrm = (1, 0) if vert else (0, 1)
            if P.contains(Point(mid[0] + nrm[0] * 1.5, mid[1] + nrm[1] * 1.5)): nrm = (-nrm[0], -nrm[1])
            lo, hi = (min(a[1], b[1]), max(a[1], b[1])) if vert else (min(a[0], b[0]), max(a[0], b[0]))
            c = a[0] if vert else a[1]
            muestras = []
            s = lo + 0.5
            while s < hi:
                p = (c, s) if vert else (s, c)
                gp, t = espesor(p, nrm)
                muestras.append((s, t, gp)); s += 1.0
            def clase(m):
                s_, t, gp = m
                if t < 5: return ('vano', 0.0)
                p = (c, s_) if vert else (s_, c)
                alla = Point(p[0] + nrm[0] * (gp + t + 2.5), p[1] + nrm[1] * (gp + t + 2.5))
                if union.contains(alla): return ('int', max(0.0, (T_INT - t) / 2))
                return ('ext', max(0.0, T_EXT - t))
            clases = [clase(m) for m in muestras]
            solidos = [k for k, d in clases if k != 'vano']
            if solidos:
                mayor = max(set(solidos), key=solidos.count)
                ds = sorted(d for k, d in clases if k == mayor); d_edge = ds[len(ds) // 2]
                gs = sorted(gp for (k, d), (_, _, gp) in zip(clases, muestras) if k == mayor); g_edge = gs[len(gs) // 2]
                ts = sorted(t for (k, d), (_, t, _) in zip(clases, muestras) if k == mayor); t_edge = ts[len(ts) // 2]
            else:
                mayor, d_edge, g_edge, t_edge = 'vano', 0.0, 0.0, 0.0
            d_eff = d_edge - g_edge
            deltas.append((mayor, d_eff, nrm))
            if mayor != 'vano' and d_edge > 0.05:
                informe.append((r['nombres'][0] if r['nombres'] else '?', mayor, round(t_edge, 1), round(d_edge, 1)))
            # franjas de muro nuevo y, en los vanos de fachada, ventana redibujada al nuevo espesor
            ini_run, tipo_run, prev = None, None, None
            def volcar(s0, s1, tipo):
                if tipo is None: return
                s0e, s1e = s0 - 0.5, s1 + 0.5
                if tipo != 'vano':
                    if d_edge <= 0.05: return
                    if vert:
                        x0, x1 = sorted([c + nrm[0] * (g_edge + 0.6), c - nrm[0] * d_eff]); strips.append(box(x0, s0e, x1, s1e))
                    else:
                        y0, y1 = sorted([c + nrm[1] * (g_edge + 0.6), c - nrm[1] * d_eff]); strips.append(box(s0e, y0, s1e, y1))
                elif mayor == 'ext' and t_edge > 5 and d_edge > 0.05:
                    fuera = c + (nrm[0] if vert else nrm[1]) * (g_edge + t_edge)
                    dentro = c - (nrm[0] if vert else nrm[1]) * d_eff
                    lo_, hi_ = sorted([fuera, dentro])
                    wins.append(dict(a=lo_, b=hi_, s0=s0e, s1=s1e, vert=vert))
            for (s, t, gp), (k, d) in zip(muestras, clases):
                tipo = 'vano' if k == 'vano' else 'muro'
                if tipo != tipo_run:
                    if tipo_run is not None: volcar(ini_run, prev, tipo_run)
                    ini_run, tipo_run = s, tipo
                prev = s
            if tipo_run is not None: volcar(ini_run, prev, tipo_run)
        lineas = []
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            vert = abs(a[0] - b[0]) < 0.01
            mayor, d, nrm = deltas[i]
            c = a[0] if vert else a[1]
            lineas.append((vert, c - (nrm[0] if vert else nrm[1]) * d))
        nuevos = []
        for i in range(n):
            v0, c0 = lineas[i - 1]; v1, c1 = lineas[i]
            if v0 == v1: raise SystemExit('tramos no alternados en ' + str(r['nombres']))
            x = c0 if v0 else c1; y = c1 if v0 else c0
            nuevos.append((round(x, 2), round(y, 2)))
        r['pts'] = [list(p) for p in _clean(nuevos)]
    muros_new = unary_union([muros] + strips)
    anillos = []
    for g in ([muros_new] if muros_new.geom_type == 'Polygon' else list(muros_new.geoms)):
        if g.geom_type != 'Polygon': continue
        q = g.simplify(0.05)
        anillos.append([[round(x, 1), round(y, 1)] for x, y in list(q.exterior.coords)[:-1]])
        for h in q.interiors:
            anillos.append([[round(x, 1), round(y, 1)] for x, y in list(h.coords)[:-1]])
    if verbose:
        import collections
        c = collections.Counter((k, t) for _, k, t, _ in informe)
        print('  tramos desplazados por espesor medido (tipo, cm originales): ',
              dict(sorted(c.items(), key=lambda kv: -kv[1])))
    return rooms, anillos, wins
