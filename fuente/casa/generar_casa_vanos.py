#!/usr/bin/env python3
"""Muros, puertas y ventanas de la casa para el 3D, a partir del plano (data.js).
- Muros: los polígonos de wallsPath (ya traen los huecos de puertas y ventanas) partidos en rectángulos; a los que no traen hueco se les resta el vano.
- Puertas y pasos: openings de cada variante (eje y ancho), con el espesor del muro vecino.
- Ventanas: tabla de la propuesta de ventanas de la casa (Gabriel, 15-10-2026 tarde: "implementalo"), hecha sobre la tabla curada del plano
  (V1..V28, P1, P4, P6): todo piso a cielo, módulo 2,4, jambas en la cara de los pilares y fuera de las cruces y celosías del ingeniero;
  láminas en fuente/casa/propuesta-ventanas/ (propuesta.py, elev.py) y en Descargas → "Propuesta ventanas casa".
Alturas (nivel 1 de 3,80 a la viga de entrepiso, medido en terreno el 16-10-2026): nivel 1 del piso a 3,40 (lo máximo bajo la viga; Gabriel, 16-10-2026), todas iguales; nivel 2 de 3,00 salvo la fachada norte, de 2,80 (Gabriel, 16-10-2026: "pongamos todas las
  ventanas del 2do piso a 3 m… solo esa pared déjalo de 2,80, todo lo demás de 3"; antes 2,80: "ojo que las ventanas del segundo piso no miden lo mismo en altura" y "el segundo piso lo dejamos
  más alto, 3 metros en la parte más baja": el techo y su estructura suben 20 cm en generar_estructura_js.py, así que bajo el puntal del
  eje H quedan 3,00 justos en el norte y la ventana de 3,00 llega hasta ahí); puertas interiores y opacas 2,80; el ventanal de doble altura del hall hasta el cielo del nivel 2 (bajo las
  vigas, no entre costaneras: ≈7,6 m).
- Muros perimetrales centrados en los ejes del ingeniero (grilla.json): el arquitecto dejó el eje a 6,7 de la cara exterior, así que los muros
  de 25 se corren ~5,8 hacia afuera (Gabriel, 15-10-2026: "lo correcto es lo del ingeniero"); `caras` trae las caras viejas → nuevas para las losas.
Uso: python3 fuente/casa/generar_casa_vanos.py  →  casa_vanos.js (DATA_CASA)"""
import json, re, pathlib
raiz = pathlib.Path(__file__).resolve().parents[2]
s = open(raiz / 'data.js', encoding='utf-8').read()
import math
H_PUERTA = 280.0   # dintel de puertas interiores y opacas, y de los pasos (cm sobre el piso del nivel)
PISO_N1 = 380.0    # cm: del piso terminado del nivel 1 a la cara superior de la viga de entrepiso (Gabriel lo midió en terreno el 16-10-2026: 3,80; las elevaciones del ingeniero dibujan 3,46)
PISO_N2 = PISO_N1 + 15   # piso terminado del nivel 2: hormigón de 15 sobre la placa colaborante (+3,95)
H_N1 = 340.0       # vidrios del nivel 1, todos iguales de 3,40: lo máximo bajo la IPE 300 del entrepiso (cara inferior a 3,50) dejando 10 para el cabezal (Gabriel, 16-10-2026: "entonces 3,60" no cabe)
BANDA_N2 = 59 + PISO_N2   # cielo del nivel 2 = cara inferior de la estructura del techo (puntal RECT 200 en el eje H, cabios IPE 400 en los ejes 1 y 5): techo(y) − 59, medido desde el piso +3,95
H_N2 = 300.0       # vidrios del nivel 2 de 3,00 (Gabriel, 16-10-2026: "pongamos todas las ventanas del 2do piso a 3 m")
H_N2_NORTE = 280.0 # salvo la fachada norte, donde el puntal del techo queda a 3,00 justos sobre el piso (Gabriel: "solo esa pared déjalo de 2,80, todo lo demás de 3")
EST = json.loads(re.search(r'const DATA_ESTRUCTURA = (\{.*\});?\s*$', open(raiz / 'estructura.js', encoding='utf-8').read(), re.S).group(1)); T = EST['techo']
def techo(y): return T['z0'] + (T['z1'] - T['z0']) * (max(T['y0'], min(T['y1'], y)) - T['y0']) / (T['y1'] - T['y0'])   # cara inferior del plano del techo (cm app), como alturaTecho en 3d.html
def cielo_n2(y): return math.floor((techo(y) - BANDA_N2) / 5) * 5   # cielo real bajo los cabios (2,65 al norte → 3,35 al sur), por si se vuelve a "piso a cielo"
def dintel_n2(y, o='v', p=9999):
    h = H_N2_NORTE if (o == 'h' and p < 30) else H_N2   # fachada norte (muro en y ≈ 10): 2,80
    assert h <= cielo_n2(y), f'el dintel de {h:.0f} no cabe bajo la estructura del techo en y={y} (cielo {cielo_n2(y)})'
    return h
GRILLA = json.load(open(raiz / 'fuente/ingenieria/datos/grilla.json', encoding='utf-8'))   # ejes del ingeniero en el marco de la app (cm)
EJES_X = sorted(float(v) for v in GRILLA['numeros'].values()); EJES_Y = sorted(float(v) for v in GRILLA['letras'].values())
TOL_EJE = 12.0   # un muro cuyo centro queda a menos de 12 de un eje se centra en el eje (Gabriel, 15-10-2026: "lo correcto es lo del ingeniero"); el muro poniente de 30 del plano queda a 10,6
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
def centrar_en_ejes(rects):
    """Muros perimetrales (espesor 20..30) centrados en los ejes del ingeniero: el plano del arquitecto deja el eje a 6,7 de la cara
    exterior (no al centro del muro), así que los pilares asomaban 1,3 por fuera. Devuelve (rects, caras) con caras = {'x': {vieja: nueva}, 'y': {...}}
    para correr también las losas y lo que se apoya en esas caras."""
    caras = {'x': {}, 'y': {}}; out = []
    for r in rects:
        x0, y0, x1, y1 = r; ex, ey = x1 - x0, y1 - y0
        if 20 <= ex <= 30 and ey > ex:      # muro vertical (delgado en x)
            c = (x0 + x1) / 2; a = min(EJES_X, key=lambda v: abs(v - c))
            if abs(a - c) <= TOL_EJE and abs(a - c) > 0.3:
                d = a - c; caras['x'][round(x0, 1)] = round(x0 + d, 1); caras['x'][round(x1, 1)] = round(x1 + d, 1); r = [x0 + d, y0, x1 + d, y1]
        elif 20 <= ey <= 30 and ex > ey:    # muro horizontal (delgado en y)
            c = (y0 + y1) / 2; a = min(EJES_Y, key=lambda v: abs(v - c))
            if abs(a - c) <= TOL_EJE and abs(a - c) > 0.3:
                d = a - c; caras['y'][round(y0, 1)] = round(y0 + d, 1); caras['y'][round(y1, 1)] = round(y1 + d, 1); r = [x0, y0 + d, x1, y1 + d]
        out.append(r)
    # lo que termina en una cara corrida (muros perpendiculares, esquinas) se alarga hasta la cara nueva
    def ajusta(v, m):
        for k, n in m.items():
            if abs(v - k) < 1.0: return n
        return v
    out2 = []
    for x0, y0, x1, y1 in out:
        ex, ey = x1 - x0, y1 - y0
        nx0, nx1 = (ajusta(x0, caras['x']), ajusta(x1, caras['x'])) if not (20 <= ex <= 30 and ey > ex) else (x0, x1)
        ny0, ny1 = (ajusta(y0, caras['y']), ajusta(y1, caras['y'])) if not (20 <= ey <= 30 and ex > ey) else (y0, y1)
        if nx1 - nx0 < 0.5 or ny1 - ny0 < 0.5: continue   # resto que quedó dentro del muro corrido (p. ej. una franja de 5 del detalle de esquina)
        out2.append([nx0, ny0, nx1, ny1])
    return out2, caras
def perimetro_desde_recintos(rooms, env, rects):
    """Muros de fachada de 25 construidos desde los bordes exteriores de los recintos (cara interior = borde del recinto; hacia afuera
    donde no hay otro recinto y se sale de la envolvente), centrados en el eje del ingeniero si lo hay a menos de TOL_EJE y
    alargados a través de las esquinas. Reemplazan a los trozos de wallsPath de la fachada (el detalle de esquina del arquitecto
    dejaba huecos de 2-5 cm por donde asomaba el acero). Devuelve (rects, caras); caras = {'x': {vieja: nueva}, 'y': {...}}."""
    E = 25.0
    def dentro(poly, x, y):
        n = len(poly); ins = False; j = n - 1
        for i in range(n):
            xi, yi = poly[i]; xj, yj = poly[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi: ins = not ins
            j = i
        return ins
    polys = [[tuple(p) for p in r['pts']] for r in rooms]
    en_recinto = lambda x, y: any(dentro(pl, x, y) for pl in polys)
    envc = {'x': sorted(set(round(p[0], 1) for p in env)), 'y': sorted(set(round(p[1], 1) for p in env))}
    fach = []   # [x0, y0, x1, y1, vert, cara_int_vieja, cara_ext_vieja]
    for pl in polys:
        n = len(pl)
        for i in range(n):
            (x0, y0), (x1, y1) = pl[i], pl[(i + 1) % n]
            if abs(x0 - x1) > 1 and abs(y0 - y1) > 1: continue
            if max(abs(x0 - x1), abs(y0 - y1)) < 30: continue
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            if abs(x0 - x1) < 1:
                for sgn in (1, -1):
                    px = mx + sgn * 40   # 40 > 30 (el muro más grueso del plano): fuera del muro y de la envolvente
                    if not en_recinto(px, my) and not dentro(env, px, my):
                        cara = x0; ext = cara + sgn * E; cen = cara + sgn * E / 2
                        a = min(EJES_X, key=lambda v: abs(v - cen)); cen2 = a if abs(a - cen) <= TOL_EJE else cen
                        fach.append([cen2 - E / 2, min(y0, y1), cen2 + E / 2, max(y0, y1), True, cara, ext, cen2 - sgn * E / 2, cen2 + sgn * E / 2])
            else:
                for sgn in (1, -1):
                    py = my + sgn * 40
                    if not en_recinto(mx, py) and not dentro(env, mx, py):
                        cara = y0; ext = cara + sgn * E; cen = cara + sgn * E / 2
                        a = min(EJES_Y, key=lambda v: abs(v - cen)); cen2 = a if abs(a - cen) <= TOL_EJE else cen
                        fach.append([min(x0, x1), cen2 - E / 2, max(x0, x1), cen2 + E / 2, False, cara, ext, cen2 - sgn * E / 2, cen2 + sgn * E / 2])
    caras = {'x': {}, 'y': {}}
    for f in fach:
        m = caras['x'] if f[4] else caras['y']
        m[round(f[5], 1)] = round(f[7], 1); m[round(f[6], 1)] = round(f[8], 1)
        for c in envc['x' if f[4] else 'y']:                     # la línea de la envolvente del arquitecto cerca de la cara exterior vieja → cara nueva
            if abs(c - f[6]) <= 6 and abs(c - f[6]) > 0.05: m[c] = round(f[8], 1)
    per = [f[:4] for f in fach]
    viejos = [[min(f[5], f[6]), f[1], max(f[5], f[6]), f[3]] if f[4] else [f[0], min(f[5], f[6]), f[2], max(f[5], f[6])] for f in fach]
    # los trozos de wallsPath que están en la banda de una fachada (vieja o nueva) se absorben: la fachada se alarga para cubrirlos
    # (muñones entre recintos, tramos frente a tabiques) y el trozo se descarta
    resto = []
    for r in rects:
        cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2; ex, ey = r[2] - r[0], r[3] - r[1]; absorbido = False
        for k, f in enumerate(fach):
            pn, po = per[k], viejos[k]
            if f[4] and ey >= ex and ((pn[0] - 1 <= cx <= pn[2] + 1) or (po[0] - 1 <= cx <= po[2] + 1)) and r[1] < pn[3] + 1 and r[3] > pn[1] - 1:
                pn[1] = min(pn[1], r[1]); pn[3] = max(pn[3], r[3]); absorbido = True
            elif (not f[4]) and ex > ey and ((pn[1] - 1 <= cy <= pn[3] + 1) or (po[1] - 1 <= cy <= po[3] + 1)) and r[0] < pn[2] + 1 and r[2] > pn[0] - 1:
                pn[0] = min(pn[0], r[0]); pn[2] = max(pn[2], r[2]); absorbido = True
        if not absorbido: resto.append(r)
    # esquinas y T macizas: donde un muro vertical y uno horizontal se tocan, cada uno se alarga para cubrir el espesor del otro
    V = [pn for pn, f in zip(per, fach) if f[4]]; Hh = [pn for pn, f in zip(per, fach) if not f[4]]
    for v in V:
        for h in Hh:
            if h[0] - 12 <= v[2] and v[0] - 12 <= h[2] and h[1] - 12 <= v[3] and v[1] - 12 <= h[3]:   # 12 ≥ el mayor corrimiento al eje: los muros corridos siguen tocándose
                v[1] = min(v[1], h[1]); v[3] = max(v[3], h[3]); h[0] = min(h[0], v[0]); h[2] = max(h[2], v[2])
    def en_fach(r):
        cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        return any(p[0] - 1 <= cx <= p[2] + 1 and p[1] - 1 <= cy <= p[3] + 1 for p in per + viejos)
    def ajusta(v, m):
        for k, n in m.items():
            if abs(v - k) < 1.0: return n
        return v
    out = []
    for x0, y0, x1, y1 in resto:
        if en_fach([x0, y0, x1, y1]): continue
        ex, ey = x1 - x0, y1 - y0
        # los EXTREMOS del trozo (x en los horizontales, y en los verticales) se alargan hasta la cara nueva de la fachada que tocan
        nx0, nx1 = (ajusta(x0, caras['x']), ajusta(x1, caras['x'])) if ex > ey else (x0, x1)
        ny0, ny1 = (ajusta(y0, caras['y']), ajusta(y1, caras['y'])) if ey >= ex else (y0, y1)
        if nx1 - nx0 < 0.5 or ny1 - ny0 < 0.5: continue
        out.append([nx0, ny0, nx1, ny1])
    # muros interiores de 25 (p. ej. cocina | lavandería en el eje 4) también al eje del ingeniero
    out, caras2 = centrar_en_ejes(out)
    return per + out, caras
def eje_cercano(o, p):
    ejes = EJES_X if o == 'v' else EJES_Y; a = min(ejes, key=lambda v: abs(v - p))
    return a if abs(a - p) <= TOL_EJE else p
def centro_muro(o, p, lo, hi, rects):
    """centro real del muro grueso donde cae el vano: si el muro no está en el eje del ingeniero (p. ej. el muro sur del dormitorio de visitas y el
    family room, que es un retranqueo interior del nivel 2 y no una fachada rearmada), el vano no se corre al eje y no deja astillas de muro"""
    for r in rects:
        if o == 'h' and r[3] - r[1] >= 20 and r[1] - 2 <= p <= r[3] + 2 and min(r[2], hi) - max(r[0], lo) > 0.3 * (hi - lo): return (r[1] + r[3]) / 2
        if o == 'v' and r[2] - r[0] >= 20 and r[0] - 2 <= p <= r[2] + 2 and min(r[3], hi) - max(r[1], lo) > 0.3 * (hi - lo): return (r[0] + r[2]) / 2
    return None
def fusionar_franjas(rects):
    """une las franjas paralelas y pegadas que el plano deja en un mismo muro (las líneas de alféizar y dintel de sus ventanas parten el polígono
    del muro en 2 o 3 tiras): dos rectángulos con el mismo largo (±2) y pegados en el otro sentido (±1) pasan a ser uno solo"""
    rs = [list(r) for r in rects]; cambio = True
    while cambio:
        cambio = False
        for i in range(len(rs)):
            for j in range(i + 1, len(rs)):
                a, b = rs[i], rs[j]
                if abs(a[0] - b[0]) <= 2 and abs(a[2] - b[2]) <= 2 and (abs(a[3] - b[1]) <= 1 or abs(b[3] - a[1]) <= 1):
                    rs[i] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]; del rs[j]; cambio = True; break
                if abs(a[1] - b[1]) <= 2 and abs(a[3] - b[3]) <= 2 and (abs(a[2] - b[0]) <= 1 or abs(b[2] - a[0]) <= 1):
                    rs[i] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]; del rs[j]; cambio = True; break
            if cambio: break
    return rs
def rellenar_huecos(rects, cortes):
    """rellena los huecos de menos de 40 cm que quedan en una banda de muro grueso y que no son un vano: el encuentro en T de un tabique con la
    fachada (la fachada rearmada termina en la cara del tabique) y los restos de ventanas del plano que la propuesta movió o achicó"""
    out = list(rects); bandas = {}
    for r in rects:
        w, h = r[2] - r[0], r[3] - r[1]
        if not (20 <= min(w, h) <= 30): continue   # solo muros de 20 a 30 (perimetrales)
        if w >= h: bandas.setdefault(('h', round(r[1], 1), round(r[3], 1)), []).append(r)
        else: bandas.setdefault(('v', round(r[0], 1), round(r[2], 1)), []).append(r)
    rellenos = []
    for (o, a, b), rs in bandas.items():
        # cobertura a lo largo: cualquier rectángulo (grueso o fino) o vano que ocupe más de la mitad del espesor de la banda; lo que queda
        # sin cubrir y mide menos de 40 es un hueco que no debería estar
        cov = []
        for r in list(rects) + list(cortes):
            if o == 'h' and min(r[3], b) - max(r[1], a) > 0.5 * (b - a): cov.append((r[0], r[2]))
            if o == 'v' and min(r[2], b) - max(r[0], a) > 0.5 * (b - a): cov.append((r[1], r[3]))
        cov.sort(); union = []
        for c in cov:
            if union and c[0] <= union[-1][1] + 0.5: union[-1] = (union[-1][0], max(union[-1][1], c[1]))
            else: union.append(c)
        for (l0, l1), (m0, m1) in zip(union, union[1:]):
            gap = m0 - l1
            if not (0.5 < gap < 40): continue
            g = [l1, a, m0, b] if o == 'h' else [a, l1, b, m0]
            rellenos.append([round(v, 1) for v in g])
    return out + rellenos, rellenos
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
# ---------- ventanas y vanos vidriados de la propuesta (cm; p = eje del muro, e = espesor, lo..hi = extensión a lo largo) ----------
# tipo: ventana (fija) · puerta vidriada (1 o 2 hojas según ancho) · puerta corredera (vidriada, 2 hojas) · puerta (opaca) · vidrio doble altura · hueco
# Código de la lámina entre paréntesis (N = norte, S = sur, E = oriente, O = poniente). Paños ciegos del ingeniero (no llevan vidrio): poniente N1 10–107,
# 625–736, 991–1104, 1634–1695; poniente N2 10–238 (cruz), 991–1104, 1634–1695; oriente N2 10–82 y 690–958 (cruz).
VENT = {
 1: [
  ('V1',  'h', 1688.2, 25, 144.6, 541.6, 'ventana', 'S1 · ventana fija del living a la terraza sur (V1 del plano, entre los pilares 110 y 575)'),
  ('V2',  'v', 658.7,  25, 1979.7, 2158.7, 'vidrio doble altura', 'O4 · ventanal del hall de acceso, poniente: vidrio continuo del piso del nivel 1 al cielo del nivel 2 (bajo las vigas), marco solo de acero fino'),
  ('V3',  'h', 2171.6, 25, 671.3, 989.1, 'vidrio doble altura', 'S2 · ventanal principal del hall de acceso al sur: vidrio continuo del piso del nivel 1 al cielo del nivel 2 (≈7,1 m, bajo las vigas y no entre costaneras), sin travesaño entre pisos; marco solo de acero fino (Gabriel, 15-10-2026)'),
  ('V4',  'v', 1001.7, 25, 2049.8, 2158.8, 'vidrio doble altura', 'E7 · ventanal del hall de acceso, oriente: vidrio continuo del piso del nivel 1 al cielo del nivel 2, marco solo de acero fino'),
  ('V5',  'h', 1505.3, 25, 1253.2, 1550.2, 'ventana', 'S3 · ventana fija del comedor al acceso cubierto (V5 del plano)'),
  ('V6a', 'v', 1777.2, 25, 1120.0, 1165.0, 'ventana', 'E5 · comedor al oriente, paño 1 de 3 (0,45): los pilares Y1173 y Y1438 quedan a la vista como parantes'),
  ('V6',  'v', 1777.2, 25, 1182.3, 1429.3, 'ventana', 'E5 · comedor al oriente, paño central (V6 del plano, entre las caras de los pilares)'),
  ('V6b', 'v', 1777.2, 25, 1446.0, 1490.0, 'ventana', 'E5 · comedor al oriente, paño 3 de 3 (0,44, hasta la esquina)'),
  ('V7',  'h', 12.7,   25, 1290.0, 1530.0, 'ventana', 'N4 · ventana de la lavandería al patio cubierto del norte (antes no tenía), alineada con N8 del WKC Maggie; una hoja proyectante'),
  ('P-L', 'h', 12.7,   25, 1620.0, 1710.0, 'puerta', 'N4b · puerta de servicio de la lavandería al patio cubierto del norte (tendedero bajo el pasillo-balcón)'),
  ('V8',  'h', 12.7,   25, 40.0, 370.0, 'ventana', 'N1 · oficina: toda la pared norte en vidrio, a la piscina (Gabriel: "la vista más linda de la casa")'),
  ('P-N', 'h', 12.7,   25, 425.1, 625.1, 'puerta vidriada', 'N2 · puerta vidriada de 2 hojas de la galería al porche cubierto (P 200 del plano)'),
  ('V9',  'v', 17.5,   25, 250.0, 600.0, 'ventana', 'O1 · oficina al poniente, 3,5 (antes 6,0, toda la pared): misma jamba que O5 del dormitorio matrimonial; quedan 2,2 de muro para estantes'),
  ('T-OL', 'h', 625.6, 15, 40.0, 370.0, 'ventana', 'oficina abierta: tabique vidriado hacia el living (vidrio laminado acústico 6+6), para que se vea que alguien trabaja'),
  ('T-OGa', 'v', 397.3, 15, 150.0, 270.0, 'ventana', 'oficina abierta: tabique vidriado hacia la galería, paño norte'),
  ('P-OG', 'v', 397.3, 15, 276.6, 366.6, 'puerta vidriada', 'oficina abierta: puerta vidriada a la galería (la puerta del plano, ahora de vidrio)'),
  ('T-OGb', 'v', 397.3, 15, 375.0, 510.0, 'ventana', 'oficina abierta: tabique vidriado hacia la galería, paño sur'),
  ('V10', 'v', 12.3,   25, 745.4, 982.4, 'ventana', 'O2 · ventana fija del living al poniente (V10 del plano)'),
  ('V11', 'v', 12.3,   25, 1112.4, 1626.4, 'ventana', 'O3 · ventana fija del living al poniente (V11 del plano)'),
  ('P4a', 'h', 12.7,   25, 687.8, 858.9, 'ventana', 'N3 · paño fijo de la cocina al patio norte (P4 del plano, al plomo de la fachada: la cocina creció 2,2 m al norte, Gabriel 16-10-2026)'),
  ('P4',  'h', 12.7,   25, 858.9, 1050.9, 'puerta corredera', 'N3 · corredera vidriada de la cocina al patio norte (P4 del plano, al plomo de la fachada)'),
  ('P4b', 'h', 12.7,   25, 1050.9, 1222.8, 'ventana', 'N3 · paño fijo de la cocina al patio norte (P4 del plano, al plomo de la fachada)'),
  ('P2',  'v', 1777.2, 25, 991.8, 1081.8, 'puerta vidriada', 'E4 · puerta vidriada 0,9 de la chiflonera al estacionamiento cubierto (P2 del plano; vidrio laminado y cerradura multipunto)'),
  ('P1f', 'v', 1001.7, 25, 1532.8, 1553.0, 'ventana', 'E6 · paño fijo de 0,2 junto a la puerta de entrada'),
  ('P1',  'v', 1001.7, 25, 1553.0, 1673.0, 'puerta vidriada', 'E6 · puerta de entrada vidriada de 1,2 desde el acceso cubierto (P 120 del plano), piso a cielo como el resto del nivel 1 (3,40)'),
  ('P3a', 'v', 2177.1, 25, 235.5, 325.5, 'puerta', 'E1 · puerta de la sala de máquinas al oriente (P3)'),
  ('P3b', 'v', 2177.1, 25, 357.4, 447.4, 'puerta', 'E2 · puerta de la bodega al oriente (P3)'),
 ],
 2: [
  ('V2',  'v', 658.8,  25, 1979.5, 2158.5, 'hueco', 'hueco del ventanal de doble altura (se dibuja desde el nivel 1)'),
  ('V3',  'h', 2171.6, 25, 671.3, 989.1, 'hueco', 'hueco del ventanal de doble altura (se dibuja desde el nivel 1)'),
  ('V4',  'v', 1001.8, 25, 2049.8, 2158.8, 'hueco', 'hueco del ventanal de doble altura (se dibuja desde el nivel 1)'),
  ('V12', 'h', 1825.0, 25, 90.0, 330.0, 'ventana', 'S5 · dormitorio de visitas al sur, piso a cielo con vidrio laminado como baranda (el plano tenía una puerta a una terraza que no existe)'),
  ('V13', 'h', 1825.0, 25, 390.0, 630.0, 'ventana', 'S6 · family room al sur (antes 1,77)'),
  ('V14', 'h', 2036.7, 25, 1090.0, 1210.0, 'ventana', 'S7 · WKC hijo 2 al sur (antes 0,95)'),
  ('V15', 'h', 2036.7, 25, 1361.1, 1657.1, 'ventana', 'S8 · dormitorio hijo 2 al sur (V15 del plano, se mantiene)'),
  ('V16', 'v', 1777.5, 25, 1480.0, 1720.0, 'ventana', 'E11 · dormitorio hijo 2 al oriente (antes 1,47)'),
  ('V17', 'v', 1777.5, 25, 1180.0, 1330.0, 'ventana', 'E10 · baño de los hijos al oriente, piso a cielo con vidrio satinado hasta 1,8 (tina frente al vidrio)'),
  ('V18', 'v', 1777.5, 25, 975.0, 1125.0, 'ventana', 'E9 · dormitorio hijo 1 al oriente, paño sur, entre el pilar E y el hall (el paño 690–958 lleva la cruz del ingeniero)'),
  ('V19', 'v', 1777.5, 25, 540.0, 680.0, 'ventana', 'E9 · dormitorio hijo 1 al oriente, paño norte, entre el closet y el pilar E3'),
  ('V20', 'v', 1777.5, 25, 120.0, 360.0, 'ventana', 'E8 · WKC Maggie al oriente, 2,4 piso a cielo sobre la cubierta del ala (antes 3,5); la salida al balcón va por el norte'),
  ('V21', 'h', 12.5,   25, 1290.0, 1530.0, 'puerta corredera', 'N8 · WKC Maggie al pasillo-balcón del norte: corredera de 2 hojas (desde el closet se sale al balcón y por él a la terraza grande; Gabriel, 15-10-2026), alineada con la lavandería'),
  ('V22', 'h', 12.5,   25, 710.0, 950.0, 'ventana', 'N7 · WKC Gabriel al norte, 2,4 centrada en el paño 2–3 (antes 1,9)'),
  ('P6',  'h', 12.5,   25, 130.0, 370.0, 'puerta corredera', 'N6 · dormitorio matrimonial a la terraza norte: corredera elevable de 2 hojas (reemplaza V24 + P6 del plano)'),
  ('V24', 'h', 12.5,   25, 380.0, 570.0, 'ventana', 'N6 · dormitorio matrimonial al norte, fijo 1,9 (4,4 de vidrio con la corredera)'),
  ('V25', 'v', 12.5,   25, 250.0, 535.0, 'ventana', 'O5 · dormitorio matrimonial al poniente (antes 1,47), alineado con O1 de la oficina; esquiva la cruz H–G1 del eje 1'),
  ('V26', 'v', 12.5,   25, 580.0, 860.0, 'ventana', 'O6 · baño matrimonial al poniente, piso a cielo con vidrio satinado hasta 1,8 (tina bajo el vidrio)'),
  ('V27', 'v', 12.5,   25, 1115.0, 1255.0, 'ventana', 'O7 · baño de visitas al poniente, piso a cielo con vidrio satinado hasta 1,8 (fuera de la celosía 991–1104)'),
  ('V28', 'v', 12.5,   25, 1386.0, 1625.8, 'ventana', 'O8 · dormitorio de visitas al poniente (antes 1,47), jamba en la cara del pilar B1'),
 ]}
salida = {'fuente': 'muros de wallsPath y puertas de openings (data.js, plano); ventanas curadas de windowsPath contra el plano (fuente/casa/generar_casa_vanos.py, 2026-10-15)',
          'alturas': dict(n1=H_N1, n2=H_N2, puertas=H_PUERTA, antepecho=ANTEPECHO, dato='Gabriel (15-10-2026, tarde): todas las ventanas piso a cielo e iguales por nivel; nivel 1 de 3,40 (lo máximo bajo la viga, con el nivel 1 de 3,80 medido en terreno), nivel 2 de 3,00 salvo la fachada norte, de 2,80 (ahí el puntal del techo queda a 3,00 justos); puertas 2,80; marcos europeos gruesos; el hall hasta el cielo del nivel 2 con marco de acero fino')}
for nivel, name, vn in ((1, 'DATA_N1', 'v1'), (2, 'DATA_N2', 'v2')):
    d = datos(name); v = d['variants'][vn]
    rects = [r for poly in subpolys(v['wallsPath']) for r in rect_strips(poly)]
    rects = [r for r in rects if (r[2] - r[0]) > 1 and (r[3] - r[1]) > 1]
    env = subpolys(d['envPath'])[0] if 'envPath' in d else [(0.0, 0.0), (float(d['W']), 0.0), (float(d['W']), float(d['H'])), (0.0, float(d['H']))]
    rects, caras = perimetro_desde_recintos(v['rooms'], env, rects)
    rects = fusionar_franjas(rects)
    vanos = []; cortes = []
    def rect_vano(o, p, e, lo, hi): return [lo, p - e / 2, hi, p + e / 2] if o == 'h' else [p - e / 2, lo, p + e / 2, hi]
    for id_, o, p, e, lo, hi, tipo, nota in VENT[nivel]:
        if e >= 20:   # ventanas de fachada: al centro real del muro (que en las fachadas rearmadas es el eje del ingeniero)
            c = centro_muro(o, p, lo, hi, rects); p = c if c is not None else eje_cercano(o, p)
        a, b = ([lo, p], [hi, p]) if o == 'h' else ([p, lo], [p, hi])
        z0 = 0.0 if tipo != 'ventana' else ANTEPECHO
        doble = tipo in ('vidrio doble altura', 'hueco')
        ym = p if o == 'h' else (lo + hi) / 2   # y del vano, para el cielo del nivel 2 (sigue el techo)
        z1 = 9999.0 if doble else (H_PUERTA if tipo == 'puerta' else (H_N1 if nivel == 1 else float(dintel_n2(ym, o, p))))
        vanos.append(dict(id=id_, tipo=tipo, a=a, b=b, e=e, z0=z0, z1=z1, ancho=round(hi - lo, 1), alto=(None if doble else round(z1 - z0, 1)), d=nota, **({'marco': 5} if doble else {})))   # 9999 = hasta el cielo del nivel 2 (el 3D lo resuelve con la pendiente del techo)
        cortes.append(rect_vano(o, p, e, lo, hi)); rects = restar(rects, rect_vano(o, p, e, lo, hi))
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
        vanos.append(dict(id=id_, tipo=tipo, a=aa, b=bb, e=round(e, 1), z0=0.0, z1=H_PUERTA, ancho=round(hi - lo, 1), alto=H_PUERTA, d=('paso abierto' if tipo == 'paso' else f"puerta de {op['gap'] / 100:.2f}".replace('.', ',') + ' (plano)') + ' · dintel a 2,80'))
        cortes.append(rect_vano('v' if vert else 'h', pc, e, lo, hi)); rects = restar(rects, rect_vano('v' if vert else 'h', pc, e, lo, hi))
    rects, rellenos = rellenar_huecos(rects, cortes)
    if rellenos: print(f'nivel {nivel}: {len(rellenos)} rellenos de muro (encuentros en T y restos de ventanas del plano): {rellenos}')
    salida[f'n{nivel}'] = dict(muros=[[round(c, 1) for c in r] for r in rects], vanos=vanos, caras=caras)
    print(f'nivel {nivel}: caras corridas al eje del ingeniero → x {caras["x"]} · y {caras["y"]}')
    print(f'nivel {nivel}: {len(rects)} rectángulos de muro · {len(vanos)} vanos ({sum(1 for x in vanos if x["tipo"] == "ventana")} ventanas, {sum(1 for x in vanos if "puerta" in x["tipo"])} puertas, {sum(1 for x in vanos if x["tipo"] == "paso")} pasos) · espesores de puertas: {sorted(set(x["e"] for x in vanos if x["tipo"] != "ventana"))}')
js = 'const DATA_CASA = ' + json.dumps(salida, ensure_ascii=False, separators=(',', ':')) + ';\n'
(raiz / 'casa_vanos.js').write_text(js, encoding='utf-8'); print('casa_vanos.js', len(js), 'bytes')
