# -*- coding: utf-8 -*-
"""Escribe losa.js (lo que lee losa.html) desde losa.json (áreas, perímetro y marco C ya
conciliados contra el plano, la foto marcada en obra y las vigas) y placa.json (sección de la
Instadeck sacada del dibujo vectorial de la ficha).

La distribución de planchas NO viene del JSON: se calcula aquí, igual para todas las áreas:
- la plancha llega hasta la punta del ala del perfil C en los bordes del perímetro (5 cm desde
  el borde + 2 mm de holgura) y hasta 5 mm del eje de la viga donde el área toca a otra área;
- se ponen de a 95 cm (avance útil) desde el borde oeste (planchas N-S) o sur (planchas E-O);
  la última va cortada a lo largo;
- si el área tiene un quiebre dentro de una franja, la plancha se corta en piezas.

Uso (desde fuente/losa): python3 generar_losa_js.py losa.json placa.json ../../losa.js textos.json
"""
import sys, json, math, functools

UTIL = 95.0          # cm, avance útil
ALA_C = 5.0          # cm, ala del perfil C (la plancha llega a su punta)
HOLGURA_BORDE = 0.2  # cm
HOLGURA_EJE = 0.5    # cm, a cada lado del eje de la viga entre dos áreas

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
JUNTAR_VALLE = 12.0       # cm: dos candidatos más cerca que esto sobre la misma viga son el mismo valle
                          # (los valles de una plancha están a 24,4 cm o más entre sí)

def pernos_y_alzaprimas(areas, pilares, perfil):
    VAL = valles_mm(perfil)
    cand, alz = [], []
    for a in areas:
        ns = a['dir'] == 'NS'
        # origen de cada plancha completa (k): las piezas de una plancha partida conservan sus valles
        origen = {}
        for q in a['piezas']:
            o = q['x0'] if ns else q['y1']
            origen[q['k']] = min(origen.get(q['k'], o), o) if ns else max(origen.get(q['k'], o), o)
        for q in a['piezas']:
            o = origen[q['k']]
            c0, c1 = (q['x0'], q['x1']) if ns else (q['y0'], q['y1'])
            vs = receptoras(a, q)
            for vi, v in enumerate(VAL):
                c = o + v / 10 if ns else o - v / 10
                if not (c0 + 1.0 <= c <= c1 - 1.0): continue       # el valle tiene que caer en esta pieza
                for L in vs:
                    t = tramo_en(L, c)
                    if not t: continue
                    x, y = (c, L['pos']) if ns else (L['pos'], c)
                    if any(_dist_rect(x, y, p['seccion']) < HOLGURA_PILAR + PERNO_D / 2 for p in pilares): continue
                    cand.append({'x': round(x, 1), 'y': round(y, 1), 'area': a['n'], 'viga': t['id'], 'perfil': t['p'],
                                 'linea': (L['dir'], round(L['pos'], 1)), 'c': c, 'union': vi == len(VAL) - 1})
            # alzaprimas: vanos entre vigas receptoras consecutivas de esta plancha
            pos = sorted(set(round(v['pos'], 1) for v in vs))
            for p0, p1 in zip(pos, pos[1:]):
                Lv = p1 - p0
                n = math.ceil(Lv / LUZ_MAX_ALZ - 1e-9)
                for k in range(1, n):
                    alz.append({'area': a['n'], 'dir': a['dir'], 'pos': round(p0 + Lv * k / n, 1), 'a0': c0, 'a1': c1, 'vano': round(Lv, 1), 'espacios': n})
    # un perno por valle real en cada línea de viga, sin importar de qué área venga el candidato;
    # en el valle de la unión se prefiere la mitad derecha de la plancha anterior (918,9 mm), igual en todas las áreas
    pernos = []
    por_linea = {}
    for c in cand: por_linea.setdefault(c['linea'], []).append(c)
    for linea, cs in por_linea.items():
        cs.sort(key=lambda c: c['c'])
        grupo = []
        def cerrar(g):
            if not g: return
            elegido = next((c for c in g if c['union']), g[0])
            pernos.append({k: elegido[k] for k in ('x', 'y', 'area', 'viga', 'perfil')})
        for c in cs:
            if grupo and abs(c['c'] - grupo[0]['c']) >= JUNTAR_VALLE:
                cerrar(grupo); grupo = []
            grupo.append(c)
        cerrar(grupo)
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
        out.append(l)
    return VAL, pernos, out

def main(f_losa, f_placa, salida, f_extra=None):
    L = json.load(open(f_losa)); P = json.load(open(f_placa))
    X = json.load(open(f_extra)) if f_extra else {}
    perim = L['perimetro']
    pil = L.get('pilares_nivel2', {})
    pil_borde, pil_dentro = pil.get('en_el_borde', []), pil.get('dentro_de_la_losa', [])
    areas = []
    for a in L['areas']:
        F, ancho, n, piezas = planchas(a, perim)
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
    valles, pernos, alzaprimas = pernos_y_alzaprimas(areas, pil_borde + pil_dentro, P['perfil'])
    out = {
        'fuente': L.get('fuentes', ''),
        'z_viga': 346, 'espesor': 15, 'espesor_plano': 14.35,
        'perimetro': perim, 'hueco_escalera': L.get('hueco_escalera'), 'hueco_interior': None,
        'marco': marco, 'areas': areas, 'pilares_n2': pilares, 'grilla': X.get('grilla', {}),
        'perfilC': {'h': 150, 'b': 50, 't': 3, 'r': 3},
        'pernos': pernos, 'valles_mm': valles, 'perno': {'d': 19.05, 'largo': 127.0, 'largo_compra': 131.8, 'cabeza_d': 31.75, 'cabeza_h': 9.5},
        'alzaprimas': alzaprimas, 'luz_max_alzaprima': LUZ_MAX_ALZ,
        'placa': P, 'diferencias': X.get('diferencias', []), 'notas': X.get('notas', []), 'cotizacion': X.get('cotizacion'),
        'cotizacion_pernos': X.get('cotizacion_pernos'),
    }
    cifras = {'{pernos}': str(len(pernos)), '{alz_lineas}': str(len(alzaprimas)), '{alz_tramos}': str(sum(len(l['tramos']) for l in alzaprimas)),
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
    print('PERNOS', len(pernos), dict(sorted(pa.items())))
    print('ALZAPRIMAS (líneas)', len(alzaprimas), 'tramos', sum(len(l['tramos']) for l in alzaprimas), dict(sorted(collections.Counter(l['area'] for l in alzaprimas).items())), 'metros', round(sum(t[1] - t[0] for l in alzaprimas for t in l['tramos']) / 100, 1))
    print(salida, len(js), 'bytes')

if __name__ == '__main__':
    main(*sys.argv[1:5])
