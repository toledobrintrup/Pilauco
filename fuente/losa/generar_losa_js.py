# -*- coding: utf-8 -*-
"""Escribe losa.js (lo que lee losa.html) desde losa.json (áreas, perímetro y marco C ya
conciliados contra el plano, la foto marcada en obra y las vigas) y placa.json (sección de la
Instadeck sacada del dibujo vectorial de la ficha).

La distribución de planchas NO viene del JSON: se calcula aquí, igual para todas las áreas:
- la plancha llega hasta la punta del ala del perfil C en los bordes del perímetro (5 cm desde
  el borde + 2 mm de holgura) y hasta el eje de la viga donde el área toca a otra área (a tope);
- se ponen de a 95 cm (avance útil) desde el borde oeste (planchas N-S) o sur (planchas E-O);
  la última va cortada a lo largo;
- si el área tiene un quiebre dentro de una franja, la plancha se corta en piezas.

Uso (desde fuente/losa): python3 generar_losa_js.py losa.json placa.json ../../losa.js textos.json
"""
import sys, json, math, functools

UTIL = 95.0          # cm, avance útil
ALA_C = 5.0          # cm, ala del perfil C (la plancha llega a su punta)
HOLGURA_BORDE = 0.2  # cm
HOLGURA_EJE = 0.0    # cm: entre dos áreas las planchas llegan hasta el eje de la viga (a tope, como pide SDI para las
                     # juntas en el mismo sentido y "hasta que se tocan" en las ortogonales)

def area_firmada(p):
    return sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p))) / 2

def centroide(p):
    a = area_firmada(p); cx = cy = 0
    for i in range(len(p)):
        x0, y0 = p[i]; x1, y1 = p[(i + 1) % len(p)]; f = x0 * y1 - x1 * y0
        cx += (x0 + x1) * f; cy += (y0 + y1) * f
    return [cx / (6 * a), cy / (6 * a)]

def en_perimetro(a, b, perim, tol=1.5):
    """¿el lado a-b del área cae sobre algún lado del perímetro (colineal y traslapado)?"""
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    for i in range(len(perim)):
        p, q = perim[i], perim[(i + 1) % len(perim)]
        if abs(p[0] - q[0]) < 0.01 and abs(a[0] - b[0]) < 0.01 and abs(a[0] - p[0]) < tol:
            if min(p[1], q[1]) - tol <= my <= max(p[1], q[1]) + tol: return True
        if abs(p[1] - q[1]) < 0.01 and abs(a[1] - b[1]) < 0.01 and abs(a[1] - p[1]) < tol:
            if min(p[0], q[0]) - tol <= mx <= max(p[0], q[0]) + tol: return True
    return False

def huella(pol, perim):
    """Polígono rectilíneo de la plancha: cada lado se corre hacia adentro según sea borde o eje."""
    p = pol[:] if area_firmada(pol) > 0 else pol[::-1]      # antihorario en (x, y) con y hacia abajo = horario visual; da igual: normal "adentro" = izquierda
    n = len(p); lineas = []
    for i in range(n):
        a, b = p[i], p[(i + 1) % n]
        d = HOLGURA_BORDE + ALA_C if en_perimetro(a, b, perim) else HOLGURA_EJE
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L                              # normal a la izquierda = hacia adentro (polígono positivo)
        lineas.append(((a[0] + nx * d, a[1] + ny * d), (dx / L, dy / L)))
    out = []
    for i in range(n):
        (p1, d1), (p2, d2) = lineas[i - 1], lineas[i]
        den = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(den) < 1e-9: out.append(list(p2)); continue
        t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
        out.append([round(p1[0] + d1[0] * t, 2), round(p1[1] + d1[1] * t, 2)])
    return out

def intervalos(pol, eje, c):
    """Intervalos del polígono sobre la recta eje=c ('x': recta vertical x=c → intervalos en y)."""
    k, o = (0, 1) if eje == 'x' else (1, 0)
    cortes = []
    for i in range(len(pol)):
        a, b = pol[i], pol[(i + 1) % len(pol)]
        if (a[k] - c) * (b[k] - c) < 0:
            t = (c - a[k]) / (b[k] - a[k]); cortes.append(a[o] + (b[o] - a[o]) * t)
    cortes.sort()
    return [(cortes[i], cortes[i + 1]) for i in range(0, len(cortes) - 1, 2)]

# alas superiores de las vigas de entrepiso (rectángulos en planta): una franja angosta que cae sobre un ala no lleva placa
def _alas():
    import os, re
    raiz = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'estructura.js')
    E = json.loads(re.sub(r'^const DATA_ESTRUCTURA = |;\s*$', '', open(raiz).read().strip()))
    out = []
    for m in E['miembros']:
        if m['c'] != 'viga' or 'entrepiso' not in (m.get('d') or ''): continue
        b = E['perfiles'].get(m['p'], {}).get('b', 10) / 2
        (x0, y0), (x1, y1) = m['a'][:2], m['b'][:2]
        if abs(y0 - y1) < 1: out.append((min(x0, x1), y0 - b, max(x0, x1), y0 + b))
        elif abs(x0 - x1) < 1: out.append((x0 - b, min(y0, y1), x0 + b, max(y0, y1)))
    return out
ALAS = _alas()

def sobre_ala(r):
    """¿el rectángulo r (x0,y0,x1,y1) queda casi entero (90 %) sobre alas de vigas?"""
    A = (r[2] - r[0]) * (r[3] - r[1])
    if A <= 0: return True
    cub = sum(max(0, min(r[2], a[2]) - max(r[0], a[0])) * max(0, min(r[3], a[3]) - max(r[1], a[1])) for a in ALAS)
    return cub >= 0.9 * A

def planchas(area, perim):
    a1 = _planchas(area, perim, False); a2 = _planchas(area, perim, True)
    # la distribución con menos piezas (y menos piezas angostas) gana; a igualdad, la de siempre
    nota = lambda r: (len(r[3]), sum(1 for q in r[3] if q['ancho'] < 30))
    return a1 if nota(a1) <= nota(a2) else a2

def _planchas(area, perim, al_reves):
    F = huella(area['poligono'], perim)
    ns = area['dir'] == 'NS'
    k = 0 if ns else 1                       # coordenada a lo ancho de la plancha
    vals = sorted(set(round(v[k], 2) for v in F))
    lo, hi = vals[0], vals[-1]
    ancho = hi - lo
    n = math.ceil(ancho / UTIL - 1e-6)
    piezas = []
    desde_min = ns != al_reves      # N-S: de oeste a este; E-O: de sur a norte (o al revés)
    for i in range(n):
        if desde_min: s0 = lo + i * UTIL; s1 = min(hi, s0 + UTIL)
        else: s1 = hi - i * UTIL; s0 = max(lo, s1 - UTIL)
        cortes = sorted(set([s0, s1] + [v for v in vals if s0 < v < s1]))
        trozos = []
        for j in range(len(cortes) - 1):
            a, b = cortes[j], cortes[j + 1]
            iv = intervalos(F, 'x' if ns else 'y', (a + b) / 2)
            if not iv: continue
            for (u0, u1) in iv:
                # mismo intervalo (o casi: menos de 2 cm en cada punta) → la misma pieza, cortada a lo más corto
                if trozos and abs(trozos[-1]['u'][0] - u0) < 2.0 and abs(trozos[-1]['u'][1] - u1) < 2.0 and abs(trozos[-1]['s'][1] - a) < 0.05:
                    trozos[-1]['s'][1] = b
                    trozos[-1]['u'] = [max(trozos[-1]['u'][0], u0), min(trozos[-1]['u'][1], u1)]
                else:
                    trozos.append({'s': [a, b], 'u': [u0, u1]})
        # una franja de menos de 10 cm que cae sobre el ala de una viga (escalón entre cara y eje) no lleva placa
        def _rect(t):
            (a, b), (u0, u1) = t['s'], t['u']
            return (a, u0, b, u1) if ns else (u0, a, u1, b)
        if len(trozos) > 1: trozos = [t for t in trozos if t['s'][1] - t['s'][0] >= 10.0 or not sobre_ala(_rect(t))] or trozos
        for t in trozos:
            (a, b), (u0, u1) = t['s'], t['u']
            if ns: x0, x1, y0, y1 = a, b, u0, u1
            else:  x0, x1, y0, y1 = u0, u1, a, b
            w = b - a
            piezas.append({'k': i + 1, 'x0': round(x0, 1), 'x1': round(x1, 1), 'y0': round(y0, 1), 'y1': round(y1, 1),
                           'ancho': round(w, 1), 'largo': round(u1 - u0, 1),
                           'cortada': bool(w < UTIL - 0.05 or len(trozos) > 1)})
    return F, ancho, n, piezas

COLORES = {1: '#A8C935', 2: '#F39A2B', 3: '#EE5D8C', 4: '#3FBF5A', 5: '#2FA84F', 6: '#D8D93A', 7: '#F5A23A', 8: '#55C66A'}  # los destacadores de obra
EJES = {1: '1–2 · K–H', 2: '1–2 · H–F', 3: '1–3 · F/E4–B', 4: '1–2 · B–A3', 5: '2–5 · I–E4/F2+273', 6: '3–4 · E4–D', 7: '4–5 · F2+273–D', 8: '3–5 · D–A1'}

def rect_inter(r1, r2):
    return min(r1[2], r2[2]) - max(r1[0], r2[0]) > 0.05 and min(r1[3], r2[3]) - max(r1[1], r2[1]) > 0.05

def piezas_marco(c, pilares):
    """El C ocupa la franja de 5 cm desde el borde hacia adentro (alma de 3 mm en la cara exterior).
    Si un pilar del borde toca el plano del alma, el C se corta y se suelda al pilar a cada lado.
    Si el pilar queda por dentro del alma (eje 5 y A1: el alma pasa 1,7 a 3,5 cm por fuera de la cara del
    pilar), el C sigue corrido y solo se le recortan las alas alrededor del pilar."""
    ax, ay = c['a']; bx, by = c['b']; L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
    nx, ny = c['interior']
    cortes, muescas = [], []
    for p in pilares:
        x0, y0, x1, y1 = p['seccion']
        ss, ts = [], []
        for (x, y) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            ss.append((x - ax) * ux + (y - ay) * uy); ts.append((x - ax) * nx + (y - ay) * ny)
        if max(ts) <= 0.05 or min(ts) >= ALA_C - 0.05: continue
        s0, s1 = max(0.0, min(ss)), min(L, max(ss))
        if s1 - s0 <= 0.05: continue
        if min(ts) <= 0.3: cortes.append((s0, s1, p['id']))
        else: muescas.append({'pilar': p['id'], 's0': round(s0, 1), 's1': round(s1, 1), 'hueco_alma_cm': round(min(ts), 1)})
    cortes.sort()
    trozos, cur = [], 0.0
    # trozos de menos de 10 cm (entre un pilar y la esquina) no se ponen: los cubre el tramo que llega a esa esquina
    for s0, s1, pid in cortes:
        if s0 - cur >= 10.0: trozos.append([round(cur, 1), round(s0, 1)])
        cur = max(cur, s1)
    if L - cur >= 10.0: trozos.append([round(cur, 1), round(L, 1)])
    return [{'s0': t[0], 's1': t[1], 'largo': round(t[1] - t[0], 1)} for t in trozos], [h[2] for h in cortes], muescas


# ---------------------------------------------------------------------------------------------
# Pernos Nelson (indicación del ingeniero, consulta del 05-10-2026): van en las VIGAS RECEPTORAS,
# las que reciben la carga de la losa = las perpendiculares a las planchas (no las paralelas), uno
# en cada valle de la placa que cruza la viga. Perno Ø19 (3/4") x 5" sobre el ala de la IPE.
# Alzaprimas: luz máxima sin apoyo 1,87 m → cada vano entre vigas receptoras se divide en
# ceil(L / 1,87) espacios iguales y lleva ese número menos uno de líneas de alzaprimas.
# ---------------------------------------------------------------------------------------------
LUZ_MAX_ALZ = 187.0
# Separación máxima entre puntales A LO LARGO de cada línea (bajo la solera). El ingeniero no la indicó:
# 1,0 m es una referencia a confirmar con él.
PUNTAL_SEP_MAX = 100.0
PUNTAL_BORDE = 15.0       # cm desde el extremo de cada tramo de solera al primer puntal

def _vigas_ejes():
    import os, re
    raiz = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'estructura.js')
    E = json.loads(re.sub(r'^const DATA_ESTRUCTURA = |;\s*$', '', open(raiz).read().strip()))
    out = []
    for m in E['miembros']:
        if m['c'] != 'viga' or 'entrepiso' not in (m.get('d') or ''): continue
        (x0, y0), (x1, y1) = m['a'][:2], m['b'][:2]
        b = E['perfiles'].get(m['p'], {}).get('b', 10)
        if abs(y0 - y1) < 1: out.append({'id': m['id'], 'p': m['p'], 'b': b, 'dir': 'EO', 'pos': y0, 'lo': min(x0, x1), 'hi': max(x0, x1)})
        elif abs(x0 - x1) < 1: out.append({'id': m['id'], 'p': m['p'], 'b': b, 'dir': 'NS', 'pos': x0, 'lo': min(y0, y1), 'hi': max(y0, y1)})
    return out
VIGAS = _vigas_ejes()

def _lineas(vigas):
    """Une los tramos colineales y seguidos de una misma viga (el eje 1 viene en 5 piezas entre F y B)."""
    out = []
    for v in sorted(vigas, key=lambda v: (v['dir'], round(v['pos'], 1), v['lo'])):
        u = out[-1] if out else None
        if u and u['dir'] == v['dir'] and abs(u['pos'] - v['pos']) < 0.6 and v['lo'] <= u['hi'] + 1.0:
            u['hi'] = max(u['hi'], v['hi']); u['tramos'].append(v)
        else:
            out.append({'dir': v['dir'], 'pos': v['pos'], 'lo': v['lo'], 'hi': v['hi'], 'tramos': [v]})
    return out
LINEAS = _lineas(VIGAS)

def tramo_en(linea, c):
    for v in linea['tramos']:
        if v['lo'] - 0.5 <= c <= v['hi'] + 0.5: return v
    return None

def valles_mm(perfil):
    """Centro del tramo plano de cada valle donde va el perno (en los valles partidos por el rigidizador,
    el primer lado). Devuelve [42.1, 286.1, 603.1, 918.9] para la Instadeck."""
    flats = [[x0, x1] for (x0, y0), (x1, y1) in zip(perfil, perfil[1:]) if y0 <= 0.7 and y1 <= 0.7 and x1 - x0 > 5]
    valles = []
    for f in flats:
        if valles and f[0] - valles[-1][-1][1] < 20: valles[-1].append(f)
        else: valles.append([f])
    return [round((v[0][0] + v[0][1]) / 2, 1) for v in valles]

def centros_mm(perfil, util=950.0):
    """Centros de los valles completos de una plancha (mm desde su origen): los interiores, entre las dos mitades que
    separa el rigidizador, y el de la unión con la plancha siguiente: [321.7, 638.7, 955.2] en la Instadeck."""
    fl = [[x0, x1] for (x0, y0), (x1, y1) in zip(perfil, perfil[1:]) if y0 <= 0.7 and y1 <= 0.7 and x1 - x0 > 5]
    g = []
    for f in fl:
        if g and f[0] - g[-1][1] < 20: g[-1][1] = f[1]
        else: g.append(list(f))
    return [round((v[0] + v[1]) / 2, 1) for v in g[1:-1]] + [round((g[-1][0] + util + g[0][1]) / 2, 1)]

def mitades_mm(perfil):
    """Centro de cada tramo plano de los valles (los valles partidos por el rigidizador tienen dos, y el valle de
    la unión entre planchas tiene uno en cada plancha): [42.1, 286.1, 357.3, 603.1, 674.3, 918.9] en la Instadeck."""
    return [round((x0 + x1) / 2, 1) for (x0, y0), (x1, y1) in zip(perfil, perfil[1:]) if y0 <= 0.7 and y1 <= 0.7 and x1 - x0 > 5]

def receptoras(area, q):
    """Vigas perpendiculares a la plancha q que caen dentro de su largo (± 12 cm) y pasan bajo ella
    (cubren al menos la mitad de su ancho)."""
    ns = area['dir'] == 'NS'
    l0, l1 = (q['y0'], q['y1']) if ns else (q['x0'], q['x1'])
    c0, c1 = (q['x0'], q['x1']) if ns else (q['y0'], q['y1'])
    return [v for v in LINEAS if v['dir'] == ('EO' if ns else 'NS') and l0 - 12 <= v['pos'] <= l1 + 12
            and min(v['hi'], c1) - max(v['lo'], c0) >= 0.5 * (c1 - c0)]

def _dist_rect(x, y, r):
    dx = max(r[0] - x, 0, x - r[2]); dy = max(r[1] - y, 0, y - r[3])
    return math.hypot(dx, dy)

PERNO_D = 1.905           # cm, vástago Ø19 (3/4")
HOLGURA_PILAR = 2.5       # cm entre el borde del vástago y la cara del pilar
PERFORACION = 3.5         # cm, diámetro del agujero que se hace con broca de copa en la placa alrededor de cada perno
HOLGURA_PLACA = 0.2       # cm entre el borde del agujero y el extremo de la plancha (no se corta el ala del C ni la plancha vecina)
SEP_MIN = 4 * PERNO_D     # cm, separación mínima entre pernos (4 d en cualquier dirección, AISC 360-16 I8.2d)
BORDE_ALA = 3.17          # cm del centro del perno al borde del ala de la viga (base del perno a 22,2 mm o más, AWS D1.1 7.4.5)
JUNTAR_VALLE = 12.0       # cm: candidatos seguidos (a menos de 9 cm uno de otro) que caben en 12 cm sobre la misma viga
                          # son el mismo valle: sus dos mitades están a 7,1–7,3 cm y los valles de una plancha a 24,4 cm o más

def _dentro(pt, pol):
    x, y = pt; ok = False
    for i in range(len(pol)):
        (x0, y0), (x1, y1) = pol[i], pol[(i + 1) % len(pol)]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0): ok = not ok
    return ok

def tipo_union(c, s_, l0, l1, areas):
    """Cómo llega la placa a la viga donde va el perno: 'corrida' (la plancha pasa sobre la viga), 'borde' (termina
    contra el perfil C del perímetro), 'mismo' (al otro lado hay planchas en el mismo sentido) u 'ortogonal'."""
    eje = c['eje']
    if l0 <= eje - c['b'] / 2 + 1.0 and l1 >= eje + c['b'] / 2 - 1.0: return 'corrida'   # la plancha pasa sobre toda el ala
    lado = 1 if abs(l1 - eje) <= abs(l0 - eje) else -1        # la plancha termina en l1: al otro lado de la viga, hacia +
    p = eje + lado * (c['b'] / 2 + 3.0)
    pt = (c['c'], p) if c['dir'] == 'NS' else (p, c['c'])
    otra = next((a for a in areas if a['n'] != c['area'] and _dentro(pt, a['poligono'])), None)
    if otra is None: return 'borde'
    return 'mismo' if otra['dir'] == c['dir'] else 'ortogonal'

def pernos_y_alzaprimas(areas, pilares, perfil):
    VAL = valles_mm(perfil)
    CENTROS = centros_mm(perfil)
    cand, alz = [], []
    for a in areas:
        ns = a['dir'] == 'NS'
        for q in a['piezas']:
            o = q['x0'] - q.get('d0', 0) / 10 if ns else q['y1'] + q.get('d0', 0) / 10   # origen de su plancha (grilla)
            c0, c1 = (q['x0'], q['x1']) if ns else (q['y0'], q['y1'])
            vs = receptoras(a, q)
            l0, l1 = (q['y0'], q['y1']) if ns else (q['x0'], q['x1'])   # la plancha a lo largo
            for v in [CENTROS[-1] - UTIL * 10] + CENTROS[:-1]:   # la unión con la plancha anterior (≈ 5 mm) y los dos interiores
                c = o + v / 10 if ns else o - v / 10
                # el fondo del valle tiene que estar entero (3 cm a cada lado del centro) en planchas de esta área que
                # cubren el mismo largo: así no quedan medios valles de borde ni valles de una plancha cortada
                lo_, hi_ = c - 3.0, c + 3.0
                cub = [(p['x0'], p['x1']) if ns else (p['y0'], p['y1']) for p in a['piezas']
                       if min(l1, (p['y1'] if ns else p['x1'])) - max(l0, (p['y0'] if ns else p['x0'])) > 1.0]
                if not (any(u0 <= lo_ <= u1 for u0, u1 in cub) and any(u0 <= hi_ <= u1 for u0, u1 in cub)): continue
                if not (c0 - 1e-6 <= c <= c1 + 1e-6): continue                # cada valle lo propone la pieza donde cae su centro
                for L in vs:
                    t = tramo_en(L, c)
                    if not t: continue
                    cand.append({'area': a['n'], 'dir': a['dir'], 'viga': t['id'], 'perfil': t['p'], 'b': t['b'], 'eje': L['pos'],
                                 'linea': (L['dir'], round(L['pos'], 1)), 'c': c, 'l0': l0, 'l1': l1})
            # alzaprimas: vanos entre vigas receptoras consecutivas de esta plancha
            pos = sorted(set(round(v['pos'], 1) for v in vs))
            for p0, p1 in zip(pos, pos[1:]):
                Lv = p1 - p0
                n = math.ceil(Lv / LUZ_MAX_ALZ - 1e-9)
                for k in range(1, n):
                    alz.append({'area': a['n'], 'dir': a['dir'], 'pos': round(p0 + Lv * k / n, 1), 'a0': c0, 'a1': c1, 'vano': round(Lv, 1), 'espacios': n})
    # cada valle real de cada línea de viga da una posición, al CENTRO del valle (entre sus dos mitades, partidas por el
    # rigidizador, o entre las mitades de dos planchas en la unión). Alrededor del perno la placa se perfora con broca
    # de copa (PERFORACION) y el perno se suelda directo al ala. A lo ancho de la viga va en el eje, salvo donde la
    # plancha termina sobre la viga: ahí se corre hacia su plancha para que el agujero no corte el ala del C ni la
    # plancha vecina.
    pernos = []
    por_linea = {}
    for c in cand: por_linea.setdefault(c['linea'], []).append(c)
    R = PERFORACION / 2 + HOLGURA_PLACA
    for linea, cs in por_linea.items():
        cs.sort(key=lambda c: c['c'])
        valles = []
        for area in sorted(set(c['area'] for c in cs)):
            grupos = []
            for c in (c for c in cs if c['area'] == area):
                if grupos and c['c'] - grupos[-1][-1]['c'] < 9.0 and c['c'] - grupos[-1][0]['c'] < JUNTAR_VALLE: grupos[-1].append(c)
                else: grupos.append([c])
            for g in grupos:
                c0 = sum(q['c'] for q in g) / len(g)
                l0, l1 = max(q['l0'] for q in g), min(q['l1'] for q in g)
                s_ = min(max(g[0]['eje'], l0 + R), l1 - R)
                if abs(s_ - g[0]['eje']) > g[0]['b'] / 2 - BORDE_ALA: continue   # el perno quedaría muy cerca del borde del ala
                ns = g[0]['dir'] == 'NS'
                x, y = (c0, s_) if ns else (s_, c0)
                if any(_dist_rect(x, y, p['seccion']) < HOLGURA_PILAR + PERNO_D / 2 for p in pilares): continue
                tipo = tipo_union(g[0], s_, l0, l1, areas)
                valles.append(dict(x=round(x, 2), y=round(y, 2), area=area, viga=g[0]['viga'], perfil=g[0]['perfil'],
                                   corrido=round(s_ - g[0]['eje'], 2), tipo=tipo, linea=linea, c=c0))
        # en las juntas a tope quedan los valles de los dos lados; el ajuste elige (a 4 d o más entre pernos)
        valles.sort(key=lambda v: v['c'])
        pernos.extend(valles)
    pernos.sort(key=lambda p: (p['area'], p['viga'], p['x'], p['y']))
    # líneas de alzaprimas: juntar las de planchas vecinas en una sola línea y cortarla donde pasa
    # bajo una viga paralela a las planchas (la solera no puede atravesarla)
    lineas = {}
    for l in alz:
        k = (l['area'], l['dir'], l['pos'])
        if k in lineas: lineas[k]['a0'] = min(lineas[k]['a0'], l['a0']); lineas[k]['a1'] = max(lineas[k]['a1'], l['a1'])
        else: lineas[k] = dict(l)
    out = []
    for l in sorted(lineas.values(), key=lambda l: (l['area'], l['pos'])):
        ns = l['dir'] == 'NS'
        cortes = []
        for v in VIGAS:
            if v['dir'] != ('NS' if ns else 'EO'): continue           # vigas paralelas a las planchas
            if not (v['lo'] - 0.5 <= l['pos'] <= v['hi'] + 0.5): continue
            if l['a0'] + 5 < v['pos'] < l['a1'] - 5: cortes.append((v['pos'] - v['b'] / 2, v['pos'] + v['b'] / 2))
        tramos, cur = [], l['a0']
        for c0, c1 in sorted(cortes):
            if c0 - cur > 5: tramos.append([round(cur, 1), round(c0, 1)])
            cur = max(cur, c1)
        if l['a1'] - cur > 5: tramos.append([round(cur, 1), round(l['a1'], 1)])
        l['tramos'] = tramos
        # puntales repartidos parejo a lo largo de cada tramo, a no más de PUNTAL_SEP_MAX entre sí
        pun = []
        for t0, t1 in tramos:
            u0, u1 = t0 + PUNTAL_BORDE, t1 - PUNTAL_BORDE
            if u1 <= u0: pun.append(round((t0 + t1) / 2, 1)); continue
            n = max(1, math.ceil((u1 - u0) / PUNTAL_SEP_MAX - 1e-9))
            pun += [round(u0 + (u1 - u0) * i / n, 1) for i in range(n + 1)]
        l['puntales'] = pun
        out.append(l)
    return VAL, pernos, out

# ---------------------------------------------------------------------------------------------
# Malla (detalle del ingeniero): ACMA C-188 con su cara superior a 2,5 cm de la cara de la losa.
# Paneles estándar en filas traslapadas; cada panel se recorta al contorno de la losa (MALLA_BORDE desde la
# cara exterior del alma del C) y alrededor de los pilares del nivel 2.
# ---------------------------------------------------------------------------------------------
# Panel estándar (catálogo): 2,60 × 5,00 m; 18 barras de 5,00 m (la primera a 2,5 cm del costado) y 33 de 2,60 m
# (la primera a 10 cm de cada punta); Ø6 a 15 cm; 39,03 kg por panel.
# Traslapo según ACMA (NCh 219): al menos 4 alambres transversales de cada malla y no menos de 30 cm entre los
# últimos alambres. Con cuadrícula de 15 cm son 3 cuadrículas (45 cm) más las puntas de los dos paneles:
# 45 + 2 × 10 = 65 cm donde se juntan las puntas y 45 + 2 × 2,5 = 50 cm en los costados. El ingeniero no lo
# indicó; si acepta el de Armacero (30 cm entre bordes de panel), salen los paneles de 'alternativas'.
MALLA = {'tipo': 'ACMA C-188', 'd': 0.6, 'sep': 15.0, 'panel': [260.0, 500.0], 'traslapo': {'costado': 50.0, 'punta': 65.0},
         'n_largas': 18, 'sal_largas': 2.5, 'n_cortas': 33, 'sal_cortas': 10.0,
         'kg_m': 0.222, 'kg_panel': 39.03, 'recubrimiento': 2.5}
ALTERNATIVAS = [('Armacero: 30 cm entre bordes de panel', 30.0, 30.0)]
MALLA_BORDE = 3.0       # cm desde el borde de la losa hasta la punta de las barras (alma de 3 mm + recubrimiento)
MALLA_PILAR = 2.0       # cm de holgura alrededor de cada pilar que atraviesa la losa
MALLA_MIN = 5.0         # cm: un trozo de barra más corto que esto no se pone
DESFASE = 225.0         # cm (15 cuadrículas): las filas impares se corren a lo largo para que no se junten 4 paneles
CHOQUE = 31.75 / 20 + 0.3   # cm: una barra a menos de esto del eje de un perno toca su cabeza (Ø31,75 + Ø6)

def inset(pol, d):
    """Polígono rectilíneo corrido d hacia adentro en todos sus lados."""
    p = pol[:] if area_firmada(pol) > 0 else pol[::-1]
    n = len(p); lineas = []
    for i in range(n):
        a, b = p[i], p[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy)
        lineas.append(((a[0] - dy / L * d, a[1] + dx / L * d), (dx / L, dy / L)))
    out = []
    for i in range(n):
        (p1, d1), (p2, d2) = lineas[i - 1], lineas[i]
        den = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(den) < 1e-9: out.append(list(p2)); continue
        t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
        out.append([round(p1[0] + d1[0] * t, 2), round(p1[1] + d1[1] * t, 2)])
    return out

def _unir(iv):
    out = []
    for a, b in sorted(iv):
        if out and a <= out[-1][1] + 1e-6: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out

def _barra(R, pilares, eje, c, t0, t1):
    """Trozos de la barra eje=c ('y': barra horizontal y=c entre x=t0 y x=t1) dentro de R y fuera de los pilares.
    Una barra que cae justo sobre el contorno cuenta como de adentro (se miran los dos lados de la recta)."""
    k = 'y' if eje == 'y' else 'x'
    iv = _unir(intervalos(R, k, c - 1e-4) + intervalos(R, k, c + 1e-4))
    tr = [(max(a, t0), min(b, t1)) for a, b in iv if min(b, t1) > max(a, t0)]
    for p in pilares:
        x0, y0, x1, y1 = p['seccion']
        x0 -= MALLA_PILAR; y0 -= MALLA_PILAR; x1 += MALLA_PILAR; y1 += MALLA_PILAR
        lo, hi, q0, q1 = (y0, y1, x0, x1) if eje == 'y' else (x0, x1, y0, y1)
        if not (lo < c < hi): continue
        nuevo = []
        for a, b in tr:
            if b <= q0 or a >= q1: nuevo.append((a, b)); continue
            if q0 > a: nuevo.append((a, q0))
            if q1 < b: nuevo.append((q1, b))
        tr = nuevo
    return [[round(c, 1), round(a, 1), round(b, 1)] for a, b in tr if b - a >= MALLA_MIN]

def _recorte_area(R, r):
    """Área del contorno R recortado al rectángulo r = (x0, y0, x1, y1) (Sutherland–Hodgman)."""
    P = R
    for k, v, sg in ((0, r[0], 1), (0, r[2], -1), (1, r[1], 1), (1, r[3], -1)):
        out = []
        for i, a in enumerate(P):
            b = P[(i + 1) % len(P)]; ina = sg * (a[k] - v) >= 0; inb = sg * (b[k] - v) >= 0
            if ina: out.append(a)
            if ina != inb:
                t = (v - a[k]) / (b[k] - a[k]); out.append([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t])
        P = out
        if not P: return 0.0
    return abs(area_firmada(P)) if len(P) >= 3 else 0.0

def _rects(R, largo_en_x, desde_max_x, desde_max_y, desfase, sx, sy, tc, tp):
    """Rectángulos de panel de un reparto: filas a lo ancho del panel, paneles a lo largo; las filas impares se corren
    'desfase' a lo largo. (sx, sy) corre todo el reparto hacia afuera de la esquina de partida. Un panel solo se pone
    si el anterior de su fila (o la fila anterior) no alcanza el borde."""
    w, l = MALLA['panel']
    xs = [p[0] for p in R]; ys = [p[1] for p in R]
    X0, X1, Y0, Y1 = min(xs) - sx, max(xs) + sx, min(ys) - sy, max(ys) + sy
    # coordenadas locales: a = a lo largo del panel, b = a lo ancho, medidas desde la esquina de partida
    A = (X1 - X0) if largo_en_x else (Y1 - Y0); B = (Y1 - Y0) if largo_en_x else (X1 - X0)
    out = []
    j = 0
    while j == 0 or j * (w - tc) + tc < B:
        b = j * (w - tc); corr = desfase if j % 2 else 0.0
        i = 0
        while True:
            a = i * (l - tp) - corr
            if i > 0 and a + tp >= A: break
            if a + l > 0:
                u, v = (a, b) if largo_en_x else (b, a)
                dx, dy = (l, w) if largo_en_x else (w, l)
                px0 = X1 - dx - u if desde_max_x else X0 + u
                py0 = Y1 - dy - v if desde_max_y else Y0 + v
                out.append((i, j, px0, py0, dx, dy))
            i += 1
        j += 1
    return out

def _lineas_barras(rects, largo_en_x):
    s = MALLA['sep']
    larg = (MALLA['n_largas'], MALLA['sal_largas']); cort = (MALLA['n_cortas'], MALLA['sal_cortas'])
    (n_x, o_x), (n_y, o_y) = (larg, cort) if largo_en_x else (cort, larg)
    ly = sorted(set(round(r[3] + o_x + k * s, 1) for r in rects for k in range(n_x)))
    lx = sorted(set(round(r[2] + o_y + k * s, 1) for r in rects for k in range(n_y)))
    return lx, ly

def _choques(pernos, lx, ly):
    import bisect
    def cerca(v, ls):
        i = bisect.bisect_left(ls, v)
        return min([abs(v - ls[k]) for k in (i - 1, i) if 0 <= k < len(ls)] or [1e9]) < CHOQUE
    return sum(1 for p in pernos if cerca(p['x'], lx) or cerca(p['y'], ly))

def _paneles(R, pilares, rects, largo_en_x):
    s = MALLA['sep']
    larg = (MALLA['n_largas'], MALLA['sal_largas']); cort = (MALLA['n_cortas'], MALLA['sal_cortas'])
    (n_x, o_x), (n_y, o_y) = (larg, cort) if largo_en_x else (cort, larg)   # n_x barras paralelas a x, repartidas en y
    paneles = []
    for (i, j, px0, py0, dx, dy) in rects:
        bx = [b for k in range(n_x) for b in _barra(R, pilares, 'y', py0 + o_x + k * s, px0, px0 + dx)]
        by = [b for k in range(n_y) for b in _barra(R, pilares, 'x', px0 + o_y + k * s, py0, py0 + dy)]
        if not bx and not by: continue
        largo = sum(b[2] - b[1] for b in bx + by)
        # entero: todas sus barras, completas (ni el borde ni un pilar le cortan nada)
        entero = len(bx) == n_x and len(by) == n_y and largo >= n_x * dx + n_y * dy - 0.5
        paneles.append({'i': i, 'j': j, 'x0': round(px0, 1), 'y0': round(py0, 1), 'x1': round(px0 + dx, 1), 'y1': round(py0 + dy, 1),
                        'cortado': not entero, 'bx': bx, 'by': by, 'm': round(largo / 100, 2)})
    return paneles

def _repartos(R, tc, tp):
    for largo_en_x in (True, False):
        for mx in (False, True):
            for my in (False, True):
                for des in (DESFASE, 0.0):
                    yield largo_en_x, mx, my, des

def _contar(R, rects):
    return sum(1 for r in rects if _recorte_area(R, (r[2], r[3], r[2] + r[4], r[3] + r[5])) > 150.0)

def malla(perim, pilares, pernos):
    R = inset(perim, MALLA_BORDE)
    tc, tp = MALLA['traslapo']['costado'], MALLA['traslapo']['punta']
    # 1) el reparto con menos paneles (a igualdad, con filas desfasadas: no se juntan 4 paneles en una esquina)
    mejor = None
    for largo_en_x, mx, my, des in _repartos(R, tc, tp):
        ps = _paneles(R, pilares, _rects(R, largo_en_x, mx, my, des, 0, 0, tc, tp), largo_en_x)
        nota = (len(ps), 0 if des else 1, sum(1 for p in ps if p['cortado']))
        if mejor is None or nota < mejor[0]: mejor = (nota, (largo_en_x, mx, my, des), ps)
    (n0, _, _), (largo_en_x, mx, my, des), ps = mejor
    # 2) correr el reparto (0 a 14 cm en cada sentido) para que las barras toquen la menor cantidad de cabezas de perno,
    #    sin agregar paneles
    cand = []
    for sx in range(15):
        for sy in range(15):
            rs = _rects(R, largo_en_x, mx, my, des, sx, sy, tc, tp)
            if _contar(R, rs) > n0: continue
            cand.append((_choques(pernos, *_lineas_barras(rs, largo_en_x)), sx, sy, rs))
    cand.sort(key=lambda c: (c[0], c[1] + c[2]))
    choques0 = _choques(pernos, *_lineas_barras(_rects(R, largo_en_x, mx, my, des, 0, 0, tc, tp), largo_en_x))
    corr = (0, 0)
    for ch, sx, sy, rs in cand[:12]:
        p2 = _paneles(R, pilares, rs, largo_en_x)
        if len(p2) <= n0: ps, corr = p2, (sx, sy); break
    lx, ly = _lineas_barras([(0, 0, p['x0'], p['y0'], p['x1'] - p['x0'], p['y1'] - p['y0']) for p in ps], largo_en_x)
    choques = _choques(pernos, lx, ly)
    # orden de colocación: fila por fila y, en cada fila, a lo largo
    ps.sort(key=lambda p: (p['j'], p['x0'] if largo_en_x else p['y0']))
    for k, p in enumerate(ps): p['n'] = k + 1
    m_barra = sum(p['m'] for p in ps)
    # cuántos paneles saldrían con otros traslapos (mismo método, sin correr el reparto)
    alt = []
    for nombre, c2, p2 in ALTERNATIVAS:
        n = min(len(_paneles(R, pilares, _rects(R, lx_, mx_, my_, d_, 0, 0, c2, p2), lx_)) for lx_, mx_, my_, d_ in _repartos(R, c2, p2))
        alt.append({'criterio': nombre, 'costado': c2, 'punta': p2, 'paneles': n})
    return dict(MALLA, borde=MALLA_BORDE, largo_en='x' if largo_en_x else 'y', desfase=des, corrimiento=list(corr),
                contorno=R, paneles=ps, m_barra=round(m_barra, 1), kg_obra=round(m_barra * MALLA['kg_m'], 0),
                choques=choques, choques_sin_correr=choques0, alternativas=alt)

# ---------------------------------------------------------------------------------------------
# Pernos del ingeniero (lámina 11, 07-10-2026): pernos_ingeniero.json (sacado del plano con pernos_desde_plano.py)
# trae los puntos que dibujó sobre cada viga. Los puntos son una marca, no la cantidad: cada fila de puntos indica
# el tramo de viga que lleva pernos, y van en TODOS los valles de ese tramo.
# ---------------------------------------------------------------------------------------------
def linea_de(viga_id):
    for L in LINEAS:
        if any(v['id'] == viga_id for v in L['tramos']): return (L['dir'], round(L['pos'], 1))
    return None

RACHA = 80.0     # cm: en la lámina los puntos de una fila van a ≈ 50 cm; entre una fila y la siguiente hay 1 m o más
CASILLA = 9.0    # cm: candidatos más cerca que esto son el mismo valle, a los dos lados de una junta a tope
SALTO = 44.0     # cm: dos valles seguidos de una viga están a 31,7 cm; más que esto es que falta uno (pilar, cambio de área)

def ajustar_a_valles(puntos, valles):
    """Cada fila de puntos de la lámina marca un tramo de su línea de viga: lleva un perno en cada valle, desde el
    valle más cercano al primer punto hasta el más cercano al último (un punto suelto, un perno en su valle). Donde
    la fila cruza un pilar del nivel 2 (la lámina no los dibuja) no hay valle libre y ahí no va perno. En una junta a
    tope (valles a los dos lados de la viga) va un perno por valle, y toda la fila al mismo lado: al que la dibujó el
    ingeniero. Devuelve los pernos y las marcas de la lámina (con la fila a la que pertenecen)."""
    por_linea = {}
    for v in valles: por_linea.setdefault(v['linea'], []).append(v)
    grupos = {}
    for p in puntos: grupos.setdefault(linea_de(p['viga']), []).append(p)
    pernos, marcas, problemas, avisos, nf = [], [], [], [], 0
    for linea, ps in sorted(grupos.items(), key=lambda kv: str(kv[0])):
        eo = bool(linea) and linea[0] == 'EO'
        coord = (lambda p: p['x']) if eo else (lambda p: p['y'])
        perp = (lambda p: p['y']) if eo else (lambda p: p['x'])
        ps = sorted(ps, key=coord)
        casillas = []   # un valle de la línea cada una (en una junta a tope, con los candidatos de los dos lados)
        for v in sorted(por_linea.get(linea, []), key=lambda v: v['c']):
            if casillas and v['c'] - casillas[-1][0]['c'] < CASILLA: casillas[-1].append(v)
            else: casillas.append([v])
        cc = [sum(v['c'] for v in k) / len(k) for k in casillas]
        if not cc:
            problemas.append(f'{linea}: {len(ps)} puntos de la lámina y ningún valle'); continue
        filas = []
        for p in ps:
            if filas and coord(p) - coord(filas[-1][-1]) <= RACHA: filas[-1].append(p)
            else: filas.append([p])
        cerca = lambda x: min(range(len(cc)), key=lambda j: abs(cc[j] - x))
        fin = -1
        for f in filas:
            nf += 1
            s0, s1 = max(cerca(coord(f[0])), fin + 1), cerca(coord(f[-1]))
            for p in f: marcas.append({'x': p['x'], 'y': p['y'], 'fila': nf})
            if s1 < s0:
                problemas.append(f'{linea}: la fila de {len(f)} puntos cae en los valles de la anterior'); continue
            fin = s1
            if any(cc[j + 1] - cc[j] > SALTO for j in range(s0, s1)):
                avisos.append(f'{linea}: la fila de {len(f)} puntos cruza un valle que falta (pilar o cambio de área)')
            lado = sum(perp(p) - linea[1] for p in f) / len(f)   # dónde dibujó la fila el ingeniero, respecto del eje
            for j in range(s0, s1 + 1):
                k = casillas[j]
                v = min(k, key=lambda v: (0 if len(k) == 1 or v['corrido'] * lado > 0 else 1, abs(v['c'] - cc[j])))
                pernos.append({'x': v['x'], 'y': v['y'], 'area': v['area'], 'viga': v['viga'], 'perfil': v['perfil'],
                               'corrido': v['corrido'], 'tipo': v['tipo'], 'fila': nf})
    pernos.sort(key=lambda p: (p['area'], p['viga'], p['x'], p['y']))
    return pernos, marcas, problemas + avisos

def poner_d0(area):
    """Origen de cada plancha según la grilla del área: las planchas se ponen de a UTIL desde un borde, así que el
    origen del perfil (borde oeste en NS, borde sur en EO) de la plancha k sale de las planchas enteras. La pieza de
    una plancha cortada conserva el tramo de perfil que le toca (d0 = mm desde el origen de su plancha): si el reparto
    parte del lado opuesto al origen del perfil, a la última plancha se le corta el lado del origen."""
    ns = area['dir'] == 'NS'
    o = lambda q: q['x0'] if ns else q['y1']
    llenas = {}
    for q in area['piezas']:
        if q['ancho'] >= UTIL - 0.05: llenas.setdefault(q['k'], o(q))
    ks = sorted(llenas)
    sg = 1.0 if (llenas[ks[-1]] - llenas[ks[0]]) * (1 if ns else -1) > 0 else -1.0   # sentido del reparto respecto del perfil
    base_k, base = ks[0], llenas[ks[0]]
    for q in area['piezas']:
        org = base + (q['k'] - base_k) * UTIL * sg * (1 if ns else -1)
        d0 = (q['x0'] - org) * 10 if ns else (org - q['y1']) * 10
        q['d0'] = round(max(0.0, d0), 1)

def main(f_losa, f_placa, salida, f_extra=None):
    L = json.load(open(f_losa)); P = json.load(open(f_placa))
    X = json.load(open(f_extra)) if f_extra else {}
    perim = L['perimetro']
    pil = L.get('pilares_nivel2', {})
    pil_borde, pil_dentro = pil.get('en_el_borde', []), pil.get('dentro_de_la_losa', [])
    areas = []
    for a in L['areas']:
        F, ancho, n, piezas = planchas(a, perim)
        poner_d0({'dir': a['dir'], 'piezas': piezas})
        for q in piezas:
            r = (q['x0'], q['y0'], q['x1'], q['y1'])
            q['pilares'] = [p['id'] for p in pil_borde + pil_dentro if rect_inter(r, p['seccion'])]
        d = a.get('dueno', {})
        areas.append({'n': a['n'], 'nombre': f"Área {a['n']}", 'color': COLORES[a['n']], 'ejes': EJES[a['n']],
                      'dir': a['dir'], 'poligono': a['poligono'], 'huella': F, 'centro': [round(v, 1) for v in centroide(a['poligono'])],
                      'ancho': round(ancho, 1), 'planchas': n, 'piezas': piezas, 'bahias': a.get('bahias', []),
                      'dueno': {'largo_m': d.get('largo_m'), 'ancho_m': d.get('ancho_m'), 'n': d.get('n'), 'texto': d.get('texto', '')}})
    marco = []
    for c in L['marco_c']:
        pz, cortan, muescas = piezas_marco(c, pil_borde)
        marco.append({'id': c['id'], 'a': c['a'], 'b': c['b'], 'interior': c['interior'], 'largo': c['largo_cm'],
                      'vigas': c['vigas'], 'piezas': pz, 'pilares': cortan, 'muescas': muescas})
    pilares = [{'id': p['id'], 'perfil': p['perfil'], 'x': p['x'], 'y': p['y'], 'seccion': p['seccion'], 'borde': p in pil_borde}
               for p in pil_borde + pil_dentro]
    valles, valles_libres, alzaprimas = pernos_y_alzaprimas(areas, pil_borde + pil_dentro, P['perfil'])
    import os
    f_ing = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pernos_ingeniero.json')
    ING = json.load(open(f_ing)) if os.path.exists(f_ing) else None
    if ING:
        pernos, marcas, problemas = ajustar_a_valles(ING['puntos'], valles_libres)
        for t in problemas: print('OJO pernos:', t)
    else:
        marcas, pernos = [], []   # sin la lámina: uno por valle, y en las juntas a tope uno solo para los dos lados
        for p in sorted(valles_libres, key=lambda p: (p['linea'], p['c'])):
            if pernos and pernos[-1]['linea'] == p['linea'] and p['c'] - pernos[-1]['c'] < JUNTAR_VALLE: continue
            pernos.append(p)
        pernos = [{k: v for k, v in p.items() if k not in ('linea', 'c')} for p in pernos]
    # control: separación mínima entre pernos de una misma línea de viga
    for lin in set(linea_de(p['viga']) for p in pernos):
        cs = sorted((p['x'] if lin[0] == 'EO' else p['y']) for p in pernos if linea_de(p['viga']) == lin)
        if any(b - a < SEP_MIN for a, b in zip(cs, cs[1:])): print('OJO pernos a menos de 4 d en', lin)
    out = {
        'fuente': L.get('fuentes', ''),
        'z_viga': 346, 'espesor': 15, 'espesor_plano': 14.35,
        'perimetro': perim, 'hueco_escalera': L.get('hueco_escalera'), 'hueco_interior': None,
        'marco': marco, 'areas': areas, 'pilares_n2': pilares, 'grilla': X.get('grilla', {}),
        'perfilC': {'h': 150, 'b': 50, 't': 3, 'r': 3},
        'pernos': pernos, 'marcas_plano': marcas, 'valles_mm': valles, 'valles_receptoras': len(valles_libres), 'perforacion': PERFORACION,
        'pernos_fuente': ING['fuente'] if ING else None, 'perno': {'d': 19.05, 'largo': 127.0, 'largo_compra': 131.8, 'cabeza_d': 31.75, 'cabeza_h': 9.5,
                                                      'sold_d': 27.0, 'sold_h': 6.4, 'quema_desnudo': 4.8, 'quema_placa': [9.5, 11.1]},
        'alzaprimas': alzaprimas, 'luz_max_alzaprima': LUZ_MAX_ALZ, 'puntal_sep_max': PUNTAL_SEP_MAX,
        'malla': malla(perim, pil_borde + pil_dentro, pernos),
        'placa': P, 'diferencias': X.get('diferencias', []), 'notas': X.get('notas', []), 'cotizacion': X.get('cotizacion'),
        'cotizacion_pernos': X.get('cotizacion_pernos'),
    }
    cifras = {'{pernos}': str(len(pernos)), '{valles}': str(len(valles_libres)), '{alz_lineas}': str(len(alzaprimas)), '{alz_tramos}': str(sum(len(l['tramos']) for l in alzaprimas)),
              '{puntales}': str(sum(len(l['puntales']) for l in alzaprimas)),
              '{alz_metros}': f"{sum(t[1] - t[0] for l in alzaprimas for t in l['tramos']) / 100:.0f}".replace('.', ',')}
    for clave in ('diferencias', 'notas'):
        out[clave] = [functools.reduce(lambda t, kv: t.replace(*kv), cifras.items(), x) for x in out[clave]]
    js = '// Generado por fuente/losa/generar_losa_js.py — no editar a mano.\nconst DATA_LOSA = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n'
    open(salida, 'w').write(js)
    for a in areas:
        print(f"Área {a['n']}: {a['dir']} ancho {a['ancho']/100:.2f} m → {a['planchas']} planchas; piezas {len(a['piezas'])}; largos {sorted(set(p['largo'] for p in a['piezas']))}; con pilar {sum(1 for p in a['piezas'] if p['pilares'])}")
    for c in marco: print(c['id'], c['largo'], '→', [p['largo'] for p in c['piezas']], 'cortan', c['pilares'], 'muescas', [m['pilar'] for m in c['muescas']])
    import collections
    pa = collections.Counter(p['area'] for p in pernos)
    print('PERNOS', len(pernos), dict(sorted(pa.items())), 'de', len(valles_libres), 'valles')
    if ING: print('  marcas de la lámina:', len(marcas), 'en', len(set(m['fila'] for m in marcas)), 'filas;',
                  'corridos hacia su plancha:', sum(1 for p in pernos if p['corrido']), '(máx', max(abs(p['corrido']) for p in pernos), 'cm);',
                  'por tipo:', dict(collections.Counter(p['tipo'] for p in pernos)))
    print('PUNTALES', sum(len(l['puntales']) for l in alzaprimas), dict(sorted(collections.Counter(l['area'] for l in alzaprimas for _ in l['puntales']).items())))
    print('ALZAPRIMAS (líneas)', len(alzaprimas), 'tramos', sum(len(l['tramos']) for l in alzaprimas), dict(sorted(collections.Counter(l['area'] for l in alzaprimas).items())), 'metros', round(sum(t[1] - t[0] for l in alzaprimas for t in l['tramos']) / 100, 1))
    M = out['malla']
    print('MALLA', M['tipo'], 'paneles', len(M['paneles']), 'cortados', sum(1 for p in M['paneles'] if p['cortado']), 'largo en', M['largo_en'],
          'desfase', M['desfase'], 'corrimiento', M['corrimiento'], 'choques', M['choques'], 'sin correr', M['choques_sin_correr'], 'alternativas', M['alternativas'],
          'barras', sum(len(p['bx']) + len(p['by']) for p in M['paneles']), 'm', M['m_barra'], 'kg', M['kg_obra'])
    print(salida, len(js), 'bytes')

if __name__ == '__main__':
    main(*sys.argv[1:5])
