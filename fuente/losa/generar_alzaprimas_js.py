# -*- coding: utf-8 -*-
"""Escribe alzaprimas.js (lo que lee alzaprimas.html): las alzaprimas bajo la placa colaborante, con PUNTALES
METÁLICOS ARRENDADOS (telescópicos, con tornillo central) y solera de DOS 2x4 de canto.

Lee:
  losa.js            líneas de alzaprimas (área, dirección, posición, vano, tramos cortados bajo las vigas paralelas a
                     las planchas), áreas, ejes y z_viga (lo arma generar_losa_js.py)
  estructura.js      vigas de entrepiso (perfil y ancho de ala) y pilares del nivel 1
  alzaprimas.json    el diseño: puntal (medidas típicas y capacidad, SUPUESTO), solera, cargas, alturas, separación de
                     puntales de cada línea con su porqué, factor de la revisión, datos, supuestos y lo que falta confirmar

Aplica el diseño (borrador para el ingeniero, 23-10-2026):
  - cada tramo de solera termina 1 cm antes del ala de la viga (de las que llegan a sus puntas);
  - puntales: el primero a 15 cm de cada extremo del tramo y los demás iguales entre sí, a no más de la separación
    de la línea; si uno cae sobre un pilar del nivel 1 se corre a su borde;
  - uniones de la solera (piezas de 3,20 m): las dos piezas sobre el MISMO puntal (dentro del cabezal en U), nunca en
    el 1.º ni en el 2.º desde cada punta; el menor número de uniones y, entre esos, los trozos más parejos;
  - carga por puntal con madera seca + ACI 347 y la carga de la revisión (max(1, f_rev), la línea como apoyo rígido):
    1,25·w·a de diseño (envolvente) y ≈ 1,10·w·a en uno cualquiera; además la reacción de cada puntal con su ubicación
    real (solera continua por pieza, con rótula donde se unen las dos piezas: ecuación de los tres momentos), que tiene
    que quedar bajo la de diseño; la capacidad a pedir es la mayor de diseño, redondeada a la centena de arriba;
  - D/C de la solera (w·a²/8), la separación máxima que la deja en 1 (seca + ACI 347 y verde + carga base) y el apoyo
    de la placa sobre la solera comparado con lo que la ficha acepta sobre el ala de una IPE 220 (3 o más vanos y 2);
  - base: placa base sobre radier, tablón sobre piso terminado y durmiente doble sobre terreno (viga sobre suelo
    elástico, supuesto);
  - cantidades: puntales a arrendar (con reserva; aparte los del área 1 si apoyan en terreno), 2x4 de la solera y de
    las tablillas, tablas de la base, cruces de arriostre (supuesto) y clavos.

Uso (desde la raíz del repositorio):  python3 fuente/losa/generar_alzaprimas_js.py
"""
import json, math, os

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..'))
G_ACC = 9.81


def cargar_js(nombre):
    s = open(os.path.join(RAIZ, nombre), encoding='utf-8').read()
    return json.loads(s[s.index('{'):s.rindex('}') + 1])


L = cargar_js('losa.js')
E = cargar_js('estructura.js')
C = json.load(open(os.path.join(AQUI, 'alzaprimas.json'), encoding='utf-8'))
PERF = E['perfiles']
VIG = [m for m in E['miembros'] if m['c'] == 'viga' and 'entrepiso' in (m.get('d') or '')]
PIL = [m for m in E['miembros'] if m['c'] == 'pilar' and m['a'][2] < 10]
GR = L['grilla']
GEO, ALT, MAD, CAR, PUN, SOL, AP, BASE = C['geometria'], C['alturas'], C['madera'], C['cargas'], C['puntal'], C['solera'], C['apoyo_placa'], C['base']


def r1(v): return round(v, 1)


def r2(v): return round(v, 2)


def cm(v, d=2):
    """cm → texto en m con coma (3,71)."""
    return f'{v / 100:.{d}f}'.replace('.', ',')


def miles(v):
    return f'{v:,.0f}'.replace(',', '.')


# ------------------------------------------------------------------ ejes
def eje_cercano(v, ejes, tol):
    k, d = min(((k, abs(x - v)) for k, x in ejes.items()), key=lambda t: t[1])
    return k if d <= tol else None


def viga_en(pos, horiz, u):
    """Viga de entrepiso a 'pos' (y si horiz, x si no) que pasa por la coordenada u a lo largo."""
    for m in VIG:
        (ax, ay), (bx, by) = m['a'][:2], m['b'][:2]
        if horiz and abs(ay - by) < 1 and abs(ay - pos) < 1.5 and min(ax, bx) - 1 <= u <= max(ax, bx) + 1: return m
        if (not horiz) and abs(ax - bx) < 1 and abs(ax - pos) < 1.5 and min(ay, by) - 1 <= u <= max(ay, by) + 1: return m
    return None


def nombre_linea_viga(pos, horiz, u):
    """Nombre del eje de una viga receptora: el de la grilla, o el que trae el id de la viga (p. ej. F2+273)."""
    ejes = GR['letras'] if horiz else GR['numeros']
    n = eje_cercano(pos, ejes, 3.0)
    if n: return n
    m = viga_en(pos, horiz, u)
    if m: return m['id'].split('-')[1].replace('ap', "a'")
    return f'{pos:.0f}'


# ------------------------------------------------------------------ recorte de los tramos (1 cm antes del ala)
def recortar(l):
    """Igual que el cálculo (madera.py): cada punta de tramo que cae en el ala (o a menos de 1 cm) de una viga que la
    atraviesa se corre a 1 cm de la punta del ala. Devuelve los tramos recortados y cuántas puntas se metían en el ala."""
    ns = l['dir'] == 'NS'
    out, dentro = [], 0
    for t0, t1 in l['tramos']:
        n0, n1 = t0, t1
        for m in VIG:
            vert = abs(m['a'][0] - m['b'][0]) < 1
            hz = abs(m['a'][1] - m['b'][1]) < 1
            b = PERF[m['p']]['b']
            if ns and vert:
                lo, hi = sorted([m['a'][1], m['b'][1]]); eje = m['a'][0]
            elif (not ns) and hz:
                lo, hi = sorted([m['a'][0], m['b'][0]]); eje = m['a'][1]
            else:
                continue
            if not (lo - 0.5 <= l['pos'] <= hi + 0.5): continue
            if abs(t0 - eje) < b / 2 + GEO['holgura_ala']:
                if abs(t0 - eje) < b / 2 - 0.05: dentro += 1
                n0 = max(n0, eje + b / 2 + GEO['holgura_ala'])
            if abs(t1 - eje) < b / 2 + GEO['holgura_ala']:
                if abs(t1 - eje) < b / 2 - 0.05: dentro += 1
                n1 = min(n1, eje - b / 2 - GEO['holgura_ala'])
        out.append([r1(n0), r1(n1)])
    return out, dentro


def obstaculos(l, medio_p=None, holg=2.0):
    """Intervalos a lo largo de la línea donde no puede ir el centro de un puntal: pilares del nivel 1 (con media placa
    base de holgura)."""
    medio_p = medio_p if medio_p is not None else PUN['placa_base'] / 20
    ns = l['dir'] == 'NS'
    out = []
    for p in PIL:
        pr = PERF[p['p']]
        px, py = p['a'][0], p['a'][1]
        hx = (pr.get('b') or pr.get('d') or pr.get('h') or 15) / 2
        hy = (pr.get('h') or pr.get('d') or pr.get('b') or 15) / 2
        if 'CANERIA' in p['p'] or 'TUBO' in p['p']:
            hx = hy = (pr.get('d') or 31) / 2
        if ns and abs(l['pos'] - py) < hy + medio_p + holg:
            out.append((px - hx - medio_p - holg, px + hx + medio_p + holg, p['id']))
        if (not ns) and abs(l['pos'] - px) < hx + medio_p + holg:
            out.append((py - hy - medio_p - holg, py + hy + medio_p + holg, p['id']))
    return out


def ubicar(t0, t1, a, obs):
    u0, u1 = t0 + GEO['borde'], t1 - GEO['borde']
    for o0, o1, _ in obs:
        if o0 < u0 < o1: u0 = o1
        if o0 < u1 < o1: u1 = o0
    if u1 <= u0: return [r1((t0 + t1) / 2)]
    n = max(1, math.ceil((u1 - u0) / a - 1e-9))
    res = []
    for i in range(n + 1):
        c = u0 + (u1 - u0) * i / n
        for o0, o1, _ in obs:
            if o0 < c < o1: c = o0 if c - o0 < o1 - c else o1
        res.append(r1(c))
    return res


def uniones(t0, t1, pun, lmax):
    """Puntales donde se unen las dos piezas de la solera: el menor número de uniones con trozos de lmax o menos y,
    entre esos, los trozos más parejos. Nunca en el 1.º ni en el 2.º puntal desde cada punta (si se puede)."""
    if t1 - t0 <= lmax + 1e-6: return []
    n = len(pun)
    for permitidos in (list(range(2, n - 2)), list(range(1, n - 1))):
        nodos = [(None, t0)] + [(j, pun[j]) for j in permitidos]
        mejor = {0: (0, 0.0, [])}            # índice de nodo -> (trozos, trozo más largo, uniones)
        for i in range(len(nodos)):
            if i not in mejor: continue
            k, mx, cam = mejor[i]
            for j in range(i + 1, len(nodos)):
                d = nodos[j][1] - nodos[i][1]
                if d > lmax + 1e-6: break
                cand = (k + 1, max(mx, d), cam + [nodos[j][0]])
                if j not in mejor or cand[:2] < mejor[j][:2]: mejor[j] = cand
        fin = []
        for i, (k, mx, cam) in mejor.items():
            d = t1 - nodos[i][1]
            if d <= lmax + 1e-6: fin.append((k + 1, max(mx, d), cam))
        if fin: return sorted(min(fin)[2])
    raise SystemExit(f'tramo {t0}-{t1}: no hay cómo unir la solera con piezas de {lmax}')


def vanos_arriostrados(pun, cada):
    """Vanos (entre puntal k y k+1) con arriostre (supuesto): el primero, el último y a no más de 'cada'."""
    nv = len(pun) - 1
    if nv < 1: return []
    c = [(pun[k] + pun[k + 1]) / 2 for k in range(nv)]
    sel = [0]
    while sel[-1] < nv - 1:
        if c[nv - 1] - c[sel[-1]] <= cada + 1e-6:
            sel.append(nv - 1); break
        cand = [k for k in range(sel[-1] + 1, nv) if c[k] - c[sel[-1]] <= cada + 1e-6]
        sel.append(max(cand) if cand else sel[-1] + 1)
    return sel


# ------------------------------------------------------------------ cargas y resistencias
D_kPa = (L['espesor'] / 100 - L['placa']['vacio_m3m2']) * CAR['gamma_hormigon'] + L['placa']['peso'] * G_ACC / 1000
Q = {'base': D_kPa + CAR['trabajo_kPa'], 'aci': D_kPa + CAR['aci_kPa']}
b2, h = MAD['b'] * SOL['piezas'], MAD['h']
S_SOL = b2 * h * h / 6                                   # mm³, solera de dos 2x4 de canto (seca cepillada)
FF = MAD['Ff'] * MAD['KD'] * MAD['Khf']                   # MPa
VE = MAD['verde']
S_SOL_V = VE['b'] * SOL['piezas'] * VE['h'] ** 2 / 6       # verde aserrada 45×94
FF_V = FF * VE['kFf']
H_TRAB = ALT['libre'] - ALT['solera']                     # cm: piso terminado del nivel 1 a cara inferior de la solera
H_TABLA = H_TRAB - ALT['tabla']                           # con un trozo de tablón bajo la placa base
H_TERRENO = ALT['libre'] + ALT['terreno_area1'] - ALT['solera'] - ALT['durmiente']   # área 1 sobre terreno (supuesto)


def abolladura(N):  # factor de AISI S100 (1 + CN·√(N/t)), solo relativo
    return 1 + AP['CN'] * math.sqrt(N / AP['t_placa'])


def interp(fila, x, xs):
    if x <= xs[0]: return fila[0]
    for i in range(1, len(xs)):
        if x <= xs[i]: return fila[i - 1] + (fila[i] - fila[i - 1]) * (x - xs[i - 1]) / (xs[i] - xs[i - 1])
    return fila[-1]


HC = L['espesor'] - L['placa']['alto'] / 10                # hormigón sobre la cresta (cm)
SA = L['placa']['sin_alzaprima']
LUZ2, LUZ3 = interp(SA['filas'][1], HC, SA['hc']), interp(SA['filas'][2], HC, SA['hc'])   # cm, ficha: 2 vanos y 3 o más
R_FICHA3, R_FICHA2 = AP['k_ficha_3v'] * LUZ3, AP['k_ficha_2v'] * LUZ2                    # reacción que acepta (× q)


def tres_momentos(xs, c0, c1, w):
    """Viga continua sobre apoyos rígidos en xs (cm), voladizos c0 y c1 en las puntas, carga w (N/cm). Reacciones (N)."""
    n = len(xs)
    if n == 1: return [w * (c0 + c1)]
    Ls = [xs[i + 1] - xs[i] for i in range(n - 1)]
    M = [0.0] * n
    M[0], M[-1] = -w * c0 * c0 / 2, -w * c1 * c1 / 2           # momentos en los apoyos (negativo = sobre el apoyo)
    if n > 2:                                                  # ecuaciones de los apoyos interiores (Thomas)
        a_, b_, c_, d_ = [], [], [], []
        for i in range(1, n - 1):
            Li, Lj = Ls[i - 1], Ls[i]
            a_.append(Li); b_.append(2 * (Li + Lj)); c_.append(Lj); d_.append(-w * (Li ** 3 + Lj ** 3) / 4)
        d_[0] -= Ls[0] * M[0]; d_[-1] -= Ls[-1] * M[-1]
        m = len(b_)
        for i in range(1, m):
            k = a_[i] / b_[i - 1]; b_[i] -= k * c_[i - 1]; d_[i] -= k * d_[i - 1]
        x = [0.0] * m; x[-1] = d_[-1] / b_[-1]
        for i in range(m - 2, -1, -1): x[i] = (d_[i] - c_[i] * x[i + 1]) / b_[i]
        M[1:n - 1] = x
    R = [0.0] * n
    for i, Li in enumerate(Ls):
        v = (M[i + 1] - M[i]) / Li
        R[i] += w * Li / 2 + v; R[i + 1] += w * Li / 2 - v
    R[0] += w * c0; R[-1] += w * c1
    return R


def reacciones(t0, t1, pun, uni, w):
    """Reacción de cada puntal de un tramo: la solera es continua dentro de cada pieza y las dos piezas se apoyan, cada
    una, sobre el puntal de la unión (rótula: el empalme no da momento)."""
    cortes = [t0] + [pun[j] for j in uni] + [t1]
    R = [0.0] * len(pun)
    for k in range(len(cortes) - 1):
        s0, s1 = cortes[k], cortes[k + 1]
        idx = [i for i, p in enumerate(pun) if s0 - 1e-6 <= p <= s1 + 1e-6]
        xs = [pun[i] for i in idx]
        for i, r in zip(idx, tres_momentos(xs, xs[0] - s0, s1 - xs[-1], w)): R[i] += r
    return R


def a_max_solera(w_aci, w_base, k_u):
    """Separación (cm) que deja la solera en D/C = 1 con seca + ACI 347 y con verde + carga base (w en N/mm)."""
    return min(math.sqrt(8 * S_SOL * FF / (w_aci * k_u)), math.sqrt(8 * S_SOL_V * FF_V / (w_base * k_u))) / 10


def durmiente(P_kgf, capas):
    """Placa base sobre un durmiente corrido de 'capas' tablones 2x10 sobre suelo elástico (Hetényi, viga infinita):
    presión bajo el puntal (kg/cm²) y D/C en flexión de la madera verde (el ancho de la placa base reparte la carga)."""
    P, b, t = P_kgf * G_ACC, BASE['tablon_ancho_2x10'] * 10, MAD['b']
    EI = capas * MAD['E'] * VE['kE'] * b * t ** 3 / 12
    beta = (BASE['k_suelo'] * b / (4 * EI)) ** 0.25
    p = P * beta / (2 * b)                                             # MPa
    M = P / (4 * beta) - P * PUN['placa_base'] / 8
    return p * 100 / G_ACC, M / (capas * b * t * t / 6) / FF_V           # kg/cm², D/C


REGLA = {(x['area'], x['pos']): x for x in C['lineas']}

# ------------------------------------------------------------------ líneas
lineas, tot_dentro, n_por_area = [], 0, {}
for l in sorted(L['alzaprimas'], key=lambda l: (l['area'], l['pos'])):
    ns = l['dir'] == 'NS'                 # NS: la línea corre a lo largo de x, a y = pos (marco de la app)
    reg = REGLA[(l['area'], l['pos'])]
    a = reg['a']
    n_por_area[l['area']] = n_por_area.get(l['area'], 0) + 1
    lid = f"{l['area']}-{n_por_area[l['area']]}"
    s = l['vano'] / l['espacios']                         # cm, luz de placa a cada lado
    # vigas receptoras que cierran el vano: la línea está en el k-ésimo espacio
    um = (l['a0'] + l['a1']) / 2
    p0 = None
    for k in range(1, l['espacios']):
        c0 = l['pos'] - l['vano'] * k / l['espacios']
        if viga_en(c0, ns, um) or eje_cercano(c0, GR['letras'] if ns else GR['numeros'], 3.0):
            p0 = c0; break
    if p0 is None: p0 = l['pos'] - s
    p1 = p0 + l['vano']
    entre = [nombre_linea_viga(p0, ns, um), nombre_linea_viga(p1, ns, um)]
    ejes_largo = GR['numeros'] if ns else GR['letras']
    de = [eje_cercano(l['a0'], ejes_largo, 10.0) or f"{l['a0']:.0f}", eje_cercano(l['a1'], ejes_largo, 10.0) or f"{l['a1']:.0f}"]

    tr, dentro = recortar(l)
    tot_dentro += dentro
    obs = obstaculos(l)
    tramos, seps, todos = [], [], []
    for (t0, t1), (m0, m1) in zip(tr, l['tramos']):
        pun = ubicar(t0, t1, a, obs)
        uni = uniones(t0, t1, pun, SOL['largo_pieza'])
        cortes = [t0] + [pun[j] for j in uni] + [t1]
        seg = [r1(cortes[i + 1] - cortes[i]) for i in range(len(cortes) - 1)]
        arr = vanos_arriostrados(pun, GEO['arriostre_cada'])
        seps += [pun[i + 1] - pun[i] for i in range(len(pun) - 1)]
        tramos.append(dict(t0=t0, t1=t1, modelo=[m0, m1], largo=r1(t1 - t0), puntales=pun, uniones=uni, piezas=seg,
                           arriostre=arr, vanos=[r1(pun[i + 1] - pun[i]) for i in range(len(pun) - 1)]))
        todos += pun
    a_real = max(seps) if seps else a
    f = max(1.0, reg['f_rev'])
    w = {k: CAR['k_reaccion_placa'] * q * s / 100 * f for k, q in Q.items()}    # kN/m = N/mm
    hay_union = any(t['uniones'] for t in tramos)
    k_u = SOL['k_union_flexion'] if hay_union else 1.0
    am = a_real * 10                                                             # mm
    dc_sol = w['aci'] * am * am / 8 / S_SOL / FF * k_u
    a_max = math.floor(a_max_solera(w['aci'], w['base'], k_u) * 10) / 10
    P = PUN['k_tipico'] * w['aci'] * am                                          # N
    P_d = PUN['k_union'] * w['aci'] * am                                         # N, diseño (envolvente)
    R = []
    for t in tramos:
        t['R_kgf'] = [round(r / G_ACC) for r in reacciones(t['t0'], t['t1'], t['puntales'], t['uniones'], w['aci'] * 10)]
        R += t['R_kgf']
    dem = CAR['k_reaccion_placa'] * s * f
    apoyo = dem / R_FICHA3 * abolladura(AP['ala_ipe220']) / abolladura(AP['ancho_solera'])
    apoyo2 = dem / R_FICHA2 * abolladura(AP['ala_ipe220']) / abolladura(AP['ancho_solera'])
    apoyo3 = dem / R_FICHA3 * abolladura(AP['ala_ipe220']) / abolladura(AP['ancho_solera'] * 1.5)     # solera de 3 piezas (123 mm)
    por = [reg['porque'].format(f=f'{f:.2f}'.replace('.', ','))] if reg['porque'] else []
    c1 = lambda v: f'{v:.1f}'.replace('.', ',')
    por.append(f'a máx. por la solera {c1(a_max)}')
    if a_max < a: por.append(f'bajo la @{a}: manda la @ real, {c1(a_real)}')
    lineas.append(dict(
        id=lid, area=l['area'], dir=l['dir'], pos=l['pos'], vano=l['vano'], espacios=l['espacios'],
        entre=entre, desde=entre[0], dist=r1(l['pos'] - p0), de=de, a0=l['a0'], a1=l['a1'],
        luz=[r1(s), r1(s)], a=a, a_max=a_max, a_real=r1(a_real), porque=' · '.join(por),
        tramos=tramos, n_puntales=len(todos), solera_m=r2(sum(t['largo'] for t in tramos) / 100), extremos_en_ala=dentro,
        obstaculos=[o[2] for o in obs],
        f_rev=reg['f_rev'], f_rev_madera=reg['f_rev_madera'], f=f, w_aci=r2(w['aci']), P_kgf=round(P / G_ACC), P_max_kgf=round(P_d / G_ACC),
        R_max_kgf=max(R), R_k=r2(max(R) * G_ACC / (w['aci'] * am)),
        H=r1(H_TRAB), H_terreno=r1(H_TERRENO) if l['area'] == 1 else None,
        dc=dict(solera=r2(dc_sol), puntal_sup=r2(P_d / G_ACC / PUN['Nadm_sup_kgf']), apoyo_placa=r2(apoyo), apoyo_placa_2v=r2(apoyo2),
                apoyo_placa_3=r2(apoyo3)),
        uniones=sum(len(t['uniones']) for t in tramos), arriostres=sum(len(t['arriostre']) for t in tramos)))
    assert max(R) <= P_d / G_ACC + 0.5, (lid, max(R), P_d / G_ACC)
    assert a_real <= a_max + 1e-6, (lid, a_real, a_max)

# ------------------------------------------------------------------ cantidades y recomendación
NP = sum(x['n_puntales'] for x in lineas)
RES = math.ceil(NP * PUN['reserva_pct'] / 100 - 1e-9)
TR = [t for x in lineas for t in x['tramos']]
n_arr = sum(len(t['arriostre']) for t in TR)
n_cruz = 2 * n_arr                                                   # a lo largo y de lado (supuesto)
n_union = sum(len(t['uniones']) for t in TR)
n_seg = sum(len(t['piezas']) for t in TR)
sol_m = sum(t['largo'] for t in TR) / 100
P_MAX = max(x['P_max_kgf'] for x in lineas)
L_MAX = max(lineas, key=lambda x: x['P_max_kgf'])
R_MAX = max(x['R_max_kgf'] for x in lineas)
L_RMAX = max(lineas, key=lambda x: x['R_max_kgf'])
CAP = int(math.ceil(P_MAX / 100 - 1e-9) * 100)              # kgf admisibles a pedir
A1 = [x for x in lineas if x['area'] == 1]
NP1 = sum(x['n_puntales'] for x in A1)
RES1 = math.ceil(NP1 * PUN['reserva_pct'] / 100 - 1e-9)
RES_RESTO = math.ceil((NP - NP1) * PUN['reserva_pct'] / 100 - 1e-9)
P1 = max(x['P_max_kgf'] for x in A1)
PEOR_AP = max(lineas, key=lambda x: x['dc']['apoyo_placa'])
APOYO_MIN = P_MAX * G_ACC / 2 / (b2 * MAD['Fcn'] * MAD['Kcn_union'])   # mm: lo que cada pieza tiene que apoyar en el cabezal
n_tabl_pz = math.ceil(n_union / SOL['tablillas_por_pieza'] - 1e-9)
P_TERR, DC_TERR = durmiente(P1, 2)
P_TERR1, DC_TERR1 = durmiente(P1, 1)
n_tablon = math.ceil(NP / int(320 // BASE['tabla_largo']) - 1e-9)
n_durm = sum(2 * math.ceil(t['largo'] / 320 - 1e-9) for x in A1 for t in x['tramos'])
ml_durm = sum(2 * t['largo'] for x in A1 for t in x['tramos']) / 100

CLAVOS = {
    'c35_solera': sum(math.ceil(t['largo'] / 30) + 1 for t in TR),      # las dos piezas entre sí, @30
    'c4_tablilla': 6 * n_union,                                          # 3 por lado de la unión
    'c3_cabezal': 4 * NP,                                                # por los agujeros del cabezal, 2 por lado
}
MAT = [
    dict(k='puntal', mat='Puntal metálico regulable', uso=f'arriendo · trabaja a {cm(H_TRAB)} m', n=NP + RES, largo=None, ml=None,
         nota=f'{NP} + {RES} de reserva'),
    dict(k='solera', mat='2x4 G2 seco cepillado', uso='solera doble de canto', n=2 * n_seg, largo=3.2, ml=r1(2 * n_seg * 3.2),
         nota=f'{n_seg} trozos × 2 · {n_union} uniones'),
    dict(k='tablilla', mat='2x4 G2 seco cepillado', uso=f'tablillas de {SOL["tablilla"]} cm en las uniones', n=n_tabl_pz, largo=3.2,
         ml=r1(n_tabl_pz * 3.2), nota=f'{n_union} tablillas + 2 calzos de terciado c/u'),
    dict(k='tablon', mat='Tablón 2x8', uso='bajo la placa base, si es piso terminado', n=n_tablon, largo=3.2, ml=r1(n_tablon * 3.2),
         nota=f'{NP} trozos de {BASE["tabla_largo"]} cm'),
    dict(k='durmiente', mat='Tablón 2x10', uso='durmiente doble, área 1 si es terreno', n=n_durm, largo=3.2, ml=r1(n_durm * 3.2),
         nota=f'{len(A1)} líneas × 2 capas · {cm(ml_durm * 100 / 2, 1)} m corridos'),
    dict(k='arriostre', mat='Cruz de arriostre', uso='a lo largo y de lado', n=n_cruz, largo=None, ml=None,
         nota=f'estimación · tubos y abrazaderas de la empresa, o 2 × 2x4 de 3,2 por cruz ({2 * n_cruz})'),
]
M24 = [m for m in MAT if m['mat'].startswith('2x4')]
BASES = dict(
    radier=dict(p=r1(P_MAX / (PUN['placa_base'] / 10) ** 2), H=r1(H_TRAB)),
    piso=dict(H=r1(H_TABLA), largo=BASE['tabla_largo']),
    terreno=dict(p=r2(P_TERR), dc=r2(DC_TERR), p1=r2(P_TERR1), dc1=r2(DC_TERR1), H=r1(H_TERRENO), n=NP1),
)
RECO = [
    ['Cantidad', f'{NP + RES} puntales ({NP} + {RES} de reserva)'],
    ['Largo', f'regulables de ~{cm(PUN["rango"][0], 1)}–{cm(PUN["rango"][1], 1)} m: trabajan a {cm(H_TRAB)} m'],
    ['Capacidad', f'≥ {miles(CAP)} kgf admisibles a {cm(H_TRAB)} m extendido (carga máx. {miles(P_MAX)})'],
    ['Cabezal', f'en U, ≥ {PUN["ancho_min_cabezal"]} mm por dentro, para 2 × 2x4'],
    ['Placa base', f'≈ {PUN["placa_base"] // 10} × {PUN["placa_base"] // 10} cm'],
    ['Arriostre', f'su regla: tubos y abrazaderas (≈ {n_cruz} cruces, estimación)'],
    ['Además', 'su tabla de carga según la altura'],
    ['Área 1', f'si apoya en terreno: {NP1} + {RES1} de ~{cm(PUN["rango_largo"][0], 1)}–{cm(PUN["rango_largo"][1], 1)} m con ≥ {miles(CAP)} kgf a '
               f'{cm(H_TERRENO)} m, y {NP - NP1} + {RES_RESTO} de los otros'],
]
VALS = dict(H=cm(H_TRAB), cap=miles(CAP), H1=cm(H_TERRENO), n1=NP1,
            apoyo=(f'{PEOR_AP["id"]} llega a {PEOR_AP["dc"]["apoyo_placa"]:.2f} de lo que acepta la ficha con 3 o más vanos '
                   f'({PEOR_AP["dc"]["apoyo_placa_2v"]:.2f} con 2 vanos); con 3 piezas {PEOR_AP["dc"]["apoyo_placa_3"]:.2f} '
                   f'(si el cabezal recibe 123 mm)').replace('.', ',')
            if PEOR_AP['dc']['apoyo_placa'] > 1 else f'máx. {PEOR_AP["dc"]["apoyo_placa"]:.2f}'.replace('.', ','))
POR_CONF = [[t.format(**VALS), q] for t, q in C['por_confirmar']]
AP_TXT = AP['porque'].format(L3=cm(LUZ3), L2=cm(LUZ2), hc=f'{HC:.2f}'.replace('.', ','))

TOT = dict(lineas=len(lineas), tramos=len(TR), puntales=NP, reserva=RES, arrendar=NP + RES, P_max=P_MAX, P_max_linea=L_MAX['id'],
           R_max=R_MAX, R_max_linea=L_RMAX['id'], R_k_max=max(x['R_k'] for x in lineas),
           capacidad=CAP, H_trabajo=r1(H_TRAB), H_tabla=r1(H_TABLA), H_terreno=r1(H_TERRENO), puntales_area1=NP1,
           reserva_area1=RES1, reserva_resto=RES_RESTO,
           solera_m=r1(sol_m), uniones=n_union, trozos=n_seg, arriostres=n_arr, cruces=n_cruz,
           ml_2x4=r1(sum(m['ml'] for m in M24)), piezas_2x4=sum(m['n'] for m in M24),
           extremos_en_ala=tot_dentro, extremos=2 * len(TR), clavos=CLAVOS, apoyo_min_mm=r1(APOYO_MIN),
           apoyo_pieza_mm=PUN['cabezal_largo'] / 2,
           dc_solera_max=max(x['dc']['solera'] for x in lineas), dc_puntal_sup_max=max(x['dc']['puntal_sup'] for x in lineas),
           apoyo_max=PEOR_AP['dc']['apoyo_placa'], apoyo_max_2v=PEOR_AP['dc']['apoyo_placa_2v'], apoyo_max_linea=PEOR_AP['id'],
           f_min=min(x['f'] for x in lineas if x['f'] > 1), f_max=max(x['f'] for x in lineas),
           n_f=sum(1 for x in lineas if x['f'] > 1))

# vigas de entrepiso para la planta: receptora = perpendicular a las planchas de un área que cruza
def receptora(m):
    (ax, ay), (bx, by) = m['a'][:2], m['b'][:2]
    hz = abs(ay - by) < 1
    for ar in L['areas']:
        xs = [p[0] for p in ar['huella']]; ys = [p[1] for p in ar['huella']]
        if ar['dir'] == 'NS' and hz and min(ys) - 3 <= ay <= max(ys) + 3 and min(max(ax, bx), max(xs)) - max(min(ax, bx), min(xs)) > 20: return True
        if ar['dir'] == 'EO' and not hz and min(xs) - 3 <= ax <= max(xs) + 3 and min(max(ay, by), max(ys)) - max(min(ay, by), min(ys)) > 20: return True
    return False


VIGAS = [dict(id=m['id'], p=m['p'], b=PERF[m['p']]['b'], a=m['a'][:2], c=m['b'][:2], rec=receptora(m)) for m in VIG]
PILARES = []
for p in PIL:
    pr = PERF[p['p']]
    if pr.get('forma') == 'tubo_circ': PILARES.append(dict(id=p['id'], x=p['a'][0], y=p['a'][1], d=pr['d']))
    else: PILARES.append(dict(id=p['id'], x=p['a'][0], y=p['a'][1], b=pr.get('b', 15), h=pr.get('h', 15), alma=p.get('alma')))

out = dict(
    fuente='fuente/losa/generar_alzaprimas_js.py: losa.js + estructura.js + fuente/losa/alzaprimas.json',
    fecha=C['fecha'], pedido=C['pedido'],
    madera=MAD, cargas=dict(D_kgm2=round(D_kPa * 1000 / G_ACC), q_base_kgm2=round(Q['base'] * 1000 / G_ACC),
                            q_aci_kgm2=round(Q['aci'] * 1000 / G_ACC), k_reaccion_placa=CAR['k_reaccion_placa']),
    puntal=PUN, solera=SOL, alturas=dict(ALT, trabajo=r1(H_TRAB), con_tabla=r1(H_TABLA), terreno=r1(H_TERRENO)),
    apoyo_placa=dict(AP, porque=AP_TXT, luz_3v=r1(LUZ3), luz_2v=r1(LUZ2), hc=r2(HC)),
    geometria=GEO, regla=C['separacion_regla'], f_rev_porque=C['f_rev_porque'], arriostre=C['arriostre'], base=BASES,
    base_porque=BASE['porque'].format(**{k: f'{v:.2f}'.replace('.', ',') for k, v in BASES['terreno'].items() if k in ('p', 'dc', 'p1', 'dc1')}),
    lineas=lineas, totales=TOT, materiales=MAT, recomendacion=RECO, vigas=VIGAS, pilares_n1=PILARES,
    datos=C['datos'], supuestos=C['supuestos'], por_confirmar=POR_CONF,
)
js = '// Generado por fuente/losa/generar_alzaprimas_js.py — no editar a mano.\nconst DATA_ALZAPRIMAS = ' + \
     json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n'
open(os.path.join(RAIZ, 'alzaprimas.js'), 'w', encoding='utf-8').write(js)

print(f"{len(lineas)} líneas · {len(TR)} tramos · {NP} puntales (+{RES} de reserva = {NP + RES}; área 1 {NP1}+{RES1}, resto {NP - NP1}+{RES_RESTO}) · solera {sol_m:.1f} m · {n_union} uniones · {n_arr} puntos de arriostre ({n_cruz} cruces)")
print(f"carga de diseño máx. por puntal {P_MAX} kgf ({L_MAX['id']}) → pedir ≥ {CAP} kgf a {H_TRAB:.1f} cm · ubicación real máx. {R_MAX} ({L_RMAX['id']}, {TOT['R_k_max']}·w·a) · con tabla {H_TABLA:.1f} · área 1 sobre terreno {H_TERRENO:.1f} ({NP1} puntales, {P1} kgf)")
print(f"2x4: {TOT['ml_2x4']:.0f} ml ({TOT['piezas_2x4']} piezas de 3,2 m) · tablón 2x8 {n_tablon} · 2x10 {n_durm} · clavos {CLAVOS} · apoyo mín. por pieza en una unión {APOYO_MIN:.1f} mm")
print(f"D/C máx: solera {TOT['dc_solera_max']} · puntal (supuesto {PUN['Nadm_sup_kgf']}) {TOT['dc_puntal_sup_max']} · apoyo placa {TOT['apoyo_max']} (2 vanos {TOT['apoyo_max_2v']}) · ficha L3 {LUZ3:.1f} L2 {LUZ2:.1f} · extremos en el ala {tot_dentro} de {2 * len(TR)}")
print(BASES)
for x in lineas:
    print(f"{x['id']:>4} {x['entre'][0]}–{x['entre'][1]} de {x['de'][0]} a {x['de'][1]} luz {x['luz'][0]} @{x['a']} real {x['a_real']} máx {x['a_max']} n {x['n_puntales']} "
          f"sol {x['solera_m']} uni {x['uniones']} P {x['P_kgf']}/{x['P_max_kgf']} R {x['R_max_kgf']} ({x['R_k']}) f {x['f']} dc {x['dc']} arr {x['arriostres']}")
