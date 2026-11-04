# -*- coding: utf-8 -*-
"""Escribe alzaprimas.js (lo que lee alzaprimas.html): las alzaprimas bajo la placa colaborante con PALOS DE PINO 3x9
SECO armados como tabiques (Gabriel, 04-11-2026: no se arriendan puntales; sin cuñas; amarre a media altura y
diagonales 3x9).

Lee:
  losa.js            líneas de alzaprimas (área, dirección, posición, vano, tramos cortados bajo las vigas paralelas a
                     las planchas), áreas, ejes y la ficha de la placa (lo arma generar_losa_js.py)
  estructura.js      vigas de entrepiso (perfil y ancho de ala) y pilares del nivel 1
  alzaprimas.json    el diseño: madera (NCh 1198 vía INFOR), cargas, palo, solera doble, solera abajo, amarre,
                     diagonales, cruces de lado, alturas, datos, supuestos y lo que falta confirmar

Aplica el diseño (borrador para el ingeniero, 04-11-2026):
  - cada tramo de solera termina 1 cm antes del ala de la viga (de las que llegan a sus puntas);
  - separación de palos de cada línea: la mayor del módulo (de 5 en 5 cm) que deja la solera doble de canto en
    flexión ≤ 1 y el palo (pandeo con el amarre a media altura) y su apoyo bajo la solera en ≤ 0,90 con
    P = 1,25·w·a; primer palo a 15 cm de cada extremo y los demás iguales; si uno cae sobre un pilar se corre;
  - solera de arriba: dos piezas de hasta 4,00 m, uniones a tope sobre un palo, trabadas entre las dos piezas;
    reacción de cada palo con su ubicación real (cada pieza continua, rótula en sus uniones, media carga cada una);
  - solera abajo: un 3x9 plano, uniones a medio camino entre palos; amarre de canto a media altura con
    cubrejuntas sobre un palo; diagonales sobre 2 vanos (pie de un palo → cabeza del que sigue al siguiente) en las
    puntas del tramo, con lo que tiran sumado al palo de su cabeza;
  - cruces de lado (X de 3x9) entre palos enfrentados de líneas vecinas (pares de alzaprimas.json): los palos de la
    vecina se ubican frente a los de la cruz; cerca de las puntas de cada tramo y donde la solera, cargada de lado,
    lo pida; nunca sobre el acero del nivel 1 ni un pilar (los muros del plano se avisan);
  - cantidades: palos, metros y piezas de compra de 3x9 (de 4,00 m; las más largas se piden a su largo) y tornillos.

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
MAD, CAR, PAL, SOL, ABJ, AMA, DIA, LADO = C['madera'], C['cargas'], C['palo'], C['solera'], C['abajo'], C['amarre'], C['diagonal'], C['lado']
ALT, GEO, BASE, AP = C['alturas'], C['geometria'], C['base'], C['apoyo_placa']


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
    """Cada punta de tramo que cae en el ala (o a menos de 1 cm) de una viga que la atraviesa se corre a 1 cm de la
    punta del ala. Devuelve los tramos recortados y cuántas puntas se metían en el ala."""
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


def obstaculos(l, holg=2.0):
    """Intervalos a lo largo de la línea donde no puede ir el centro de un palo: pilares del nivel 1. El palo va
    atravesado: mide b (6,5) a lo largo de la línea y h (21) de lado."""
    m_largo, m_lado = MAD['b'] / 20, MAD['h'] / 20
    ns = l['dir'] == 'NS'
    out = []
    for p in PIL:
        pr = PERF[p['p']]
        px, py = p['a'][0], p['a'][1]
        hx = (pr.get('b') or pr.get('d') or pr.get('h') or 15) / 2
        hy = (pr.get('h') or pr.get('d') or pr.get('b') or 15) / 2
        if 'CANERIA' in p['p'] or 'TUBO' in p['p']:
            hx = hy = (pr.get('d') or 31) / 2
        if ns and abs(l['pos'] - py) < hy + m_lado + holg:
            out.append((px - hx - m_largo - holg, px + hx + m_largo + holg, p['id']))
        if (not ns) and abs(l['pos'] - px) < hx + m_lado + holg:
            out.append((py - hy - m_largo - holg, py + hy + m_largo + holg, p['id']))
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


def cortes(t0, t1, nodos, lmax, prohibidos=()):
    """Menor número de cortes (en 'nodos': lista de (índice, u)) que deja trozos de lmax o menos y, entre esos, los
    trozos más parejos. Devuelve los índices de los nodos donde se corta."""
    if t1 - t0 <= lmax + 1e-6: return []
    nod = [(None, t0)] + [(j, u) for j, u in nodos if j not in prohibidos]
    mejor = {0: (0, 0.0, [])}
    for i in range(len(nod)):
        if i not in mejor: continue
        k, mx, cam = mejor[i]
        for j in range(i + 1, len(nod)):
            d = nod[j][1] - nod[i][1]
            if d > lmax + 1e-6: break
            cand = (k + 1, max(mx, d), cam + [nod[j][0]])
            if j not in mejor or cand[:2] < mejor[j][:2]: mejor[j] = cand
    fin = [(k + 1, max(mx, t1 - nod[i][1]), cam) for i, (k, mx, cam) in mejor.items() if t1 - nod[i][1] <= lmax + 1e-6]
    return sorted(min(fin)[2]) if fin else None


def uniones_solera(t0, t1, pun, lmax):
    """Uniones de las dos piezas de la solera de arriba, sobre palos, trabadas (una pieza no se une donde la otra) y,
    si se puede, nunca en el 1.º ni en el 2.º palo de cada punta."""
    n = len(pun)
    for perm in (range(2, n - 2), range(1, n - 1)):
        nod = [(j, pun[j]) for j in perm]
        ua = cortes(t0, t1, nod, lmax)
        if ua is None: continue
        ub = cortes(t0, t1, nod, lmax, prohibidos=set(ua))
        if ub is None: continue
        return ua, ub
    raise SystemExit(f'tramo {t0}-{t1}: no hay cómo trabar la solera doble con piezas de {lmax}')


def trozos(t0, t1, us):
    c = [t0] + list(us) + [t1]
    return [r1(c[i + 1] - c[i]) for i in range(len(c) - 1)]


def tres_momentos(xs, c0, c1, w):
    """Viga continua sobre apoyos rígidos en xs (cm), voladizos c0 y c1 en las puntas, carga w (N/cm). Reacciones (N)."""
    n = len(xs)
    if n == 1: return [w * (c0 + c1)]
    Ls = [xs[i + 1] - xs[i] for i in range(n - 1)]
    M = [0.0] * n
    M[0], M[-1] = -w * c0 * c0 / 2, -w * c1 * c1 / 2
    if n > 2:
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
    """Reacción de cada palo para UNA pieza de la solera con carga w: continua entre sus uniones, y en cada unión las
    dos partes se apoyan en el mismo palo (rótula)."""
    cs = [t0] + [pun[j] for j in uni] + [t1]
    R = [0.0] * len(pun)
    for k in range(len(cs) - 1):
        s0, s1 = cs[k], cs[k + 1]
        idx = [i for i, p in enumerate(pun) if s0 - 1e-6 <= p <= s1 + 1e-6]
        xs = [pun[i] for i in idx]
        for i, r in zip(idx, tres_momentos(xs, xs[0] - s0, s1 - xs[-1], w)): R[i] += r
    return R


# ------------------------------------------------------------------ madera (NCh 1198 vía INFOR; N, mm, MPa)
b, h = MAD['b'], MAD['h']
KH, KD = MAD['KH'], MAD['KD']
FF = MAD['Ff'] * KD * KH['f'] * (90 / h) ** 0.2            # solera de canto (alto h)
FF_LADO = MAD['Ff'] * KD * KH['f'] * (90 / (2 * b)) ** 0.2  # la solera doble cargada de lado (alto 2b)
FF_PLANO = MAD['Ff'] * KD * KH['f']                         # pieza plana (alto b < 90)
FCZ = MAD['Fcz'] * KD * KH['cz']
FCP = MAD['Fcp'] * KD * KH['cp']
FCN = MAD['Fcn'] * KH['cn']
E_D = MAD['E'] * KH['E']
TOR = MAD['tornillo_kN'] * 1000


def Kcn(l): return (150 / l) ** 0.25 if l < 150 else 1.0


def columna(Lp, d, area=None):
    """(λ, N admisible) de una pieza b × h que pandea con el lado d en su plano, largo de pandeo Lp (mm)."""
    lam = Lp * math.sqrt(12) / d
    Ed = E_D * min(1.0, (d / 180) ** 0.25)
    r = 3.6 * Ed / lam ** 2 / FCP
    A = (r * (1 + lam / 200) + 1) / (2 * MAD['c']); B = r / MAD['c']
    return lam, FCP * (A - math.sqrt(A * A - B)) * (area or b * h)


H_PALO = ALT['libre'] - ALT['solera'] - ALT['abajo']                 # cm
H_PALO1 = H_PALO + ALT['terreno_area1']                              # área 1 sobre terreno (supuesto)
Z_AMARRE = ALT['abajo'] + H_PALO / 2                                 # cm, centro del amarre


def palo(Hc):
    """Capacidad del palo de Hc cm: lado delgado con el amarre a media altura; lado ancho entero."""
    ld, nd = columna(Hc * 10 / 2, b)
    lf, nf = columna(Hc * 10, h)
    return dict(lam_d=ld, lam_f=lf, lam_suelto=Hc * 10 * math.sqrt(12) / b, N=min(nd, nf))


PALO, PALO1 = palo(H_PALO), palo(H_PALO1)
N_APOYO = FCN * Kcn(b) * (SOL['piezas'] * b) * b                     # solera doble (13) sobre el palo (6,5 a lo largo)
N_APOYO_ABAJO = FCN * Kcn(b) * h * b                                 # palo entero sobre la solera abajo plana
W_SOL = SOL['piezas'] * b * h * h / 6
M_SOL = FF * W_SOL                                                   # N·mm
V_SOL = FCZ * SOL['piezas'] * b * h / 1.5                            # N
EI_SOL = E_D * SOL['piezas'] * b * h ** 3 / 12
W_LADO = SOL['piezas'] * h * b * b / 6                               # de lado, las dos piezas sin trabajar juntas

D_kPa = (L['espesor'] / 100 - L['placa']['vacio_m3m2']) * CAR['gamma_hormigon'] + L['placa']['peso'] * G_ACC / 1000
Q = {'base': D_kPa + CAR['trabajo_kPa'], 'aci': D_kPa + CAR['aci_kPa']}
KAP = CAR['k_apoyo']


def abolladura(N):  # factor de AISI S100 (1 + CN·√(N/t)), solo relativo
    return 1 + AP['CN'] * math.sqrt(N / AP['t_placa'])


def interp(fila, x, xs):
    if x <= xs[0]: return fila[0]
    for i in range(1, len(xs)):
        if x <= xs[i]: return fila[i - 1] + (fila[i] - fila[i - 1]) * (x - xs[i - 1]) / (xs[i] - xs[i - 1])
    return fila[-1]


HC = L['espesor'] - L['placa']['alto'] / 10
SA = L['placa']['sin_alzaprima']
LUZ2, LUZ3 = interp(SA['filas'][1], HC, SA['hc']), interp(SA['filas'][2], HC, SA['hc'])
R_FICHA3, R_FICHA2 = AP['k_ficha_3v'] * LUZ3, AP['k_ficha_2v'] * LUZ2


def a_max(w, Np):
    """Separación máxima (cm) por la flexión de la solera (≤ 1) y por el palo y su apoyo (≤ holgura); w en N/mm."""
    a_f = math.sqrt(8 * M_SOL / w)
    a_p = PAL['holgura'] * min(Np, N_APOYO) / (KAP * w)
    return min(a_f, a_p) / 10, ('la solera' if a_f <= a_p else ('el apoyo del palo' if N_APOYO < Np else 'el palo'))


REGLA = {(x['area'], x['pos']): x for x in C['lineas']}
N_UNION = FCN * (Kcn(b) * b * b + 0.8 * b * b)          # palo de una unión: una pieza corrida y las dos puntas de la otra
W_UNA, W_LADO_UNA = b * h * h / 6, h * b * b / 6          # una sola pieza de la solera (en la unión)
FF_LADO_UNA = MAD['Ff'] * KD * KH['f']                   # una pieza de lado (alto b < 90)
Z_PIE, Z_CAB = ALT['abajo'] + 20, ALT['libre'] - ALT['solera'] - 20       # cm, uniones de la diagonal (pie y cabeza)
BANDAS = LADO['bandas']                                  # [[z abajo, z arriba], ...] uniones de la cruz en el palo

# ------------------------------------------------------------------ choques en planta: acero y muros del nivel 1, pilares
ACERO1 = [m for m in E['miembros'] if m['c'] in ('diagonal', 'otro') and min(m['a'][2], m['b'][2]) < ALT['libre']]
MUROS1 = cargar_js('casa_vanos.js')['n1']['muros']       # [x0, y0, x1, y1]


def d_seg(p, q, r, t):
    """Distancia mínima entre los segmentos pq y rt (planta, cm)."""
    def d_pt(a, b0, b1):
        vx, vy = b1[0] - b0[0], b1[1] - b0[1]; L2 = vx * vx + vy * vy
        k = 0 if L2 == 0 else max(0, min(1, ((a[0] - b0[0]) * vx + (a[1] - b0[1]) * vy) / L2))
        return math.hypot(a[0] - b0[0] - k * vx, a[1] - b0[1] - k * vy)
    def corta(a, b0, c, d):
        o = lambda p_, q_, r_: (q_[0] - p_[0]) * (r_[1] - p_[1]) - (q_[1] - p_[1]) * (r_[0] - p_[0])
        return o(a, b0, c) * o(a, b0, d) < 0 and o(c, d, a) * o(c, d, b0) < 0
    if corta(p, q, r, t): return 0.0
    return min(d_pt(p, r, t), d_pt(q, r, t), d_pt(r, p, q), d_pt(t, p, q))


def choques(p, q):
    """Lo que toca una cruz de planta p → q: acero del nivel 1 y pilares (se evitan); muros del plano (se avisan)."""
    acero = [m['id'] for m in ACERO1 if d_seg(p, q, m['a'][:2], m['b'][:2]) < 7.5 + 10]
    for m in PIL:
        pr = PERF[m['p']]; r = max(pr.get('b') or 0, pr.get('h') or 0, pr.get('d') or 0) / 2 or 7.5
        if d_seg(p, q, m['a'][:2], m['a'][:2]) < r + 10: acero.append(m['id'])
    muros = []
    for k, (x0, y0, x1, y1) in enumerate(MUROS1):
        for i in range(41):
            x, y = p[0] + (q[0] - p[0]) * i / 40, p[1] + (q[1] - p[1]) * i / 40
            if min(x0, x1) - 10 <= x <= max(x0, x1) + 10 and min(y0, y1) - 10 <= y <= max(y0, y1) + 10: muros.append(k); break
    return acero, muros


def diagonales_de(nv):
    """Diagonales de un tramo (índices de palos): sobre 2 vanos, del pie de un palo a la cabeza del que sigue al
    siguiente, atornillada al del medio a media altura; una en cada punta si hay 4 vanos o más."""
    if nv < 1: return []
    if nv == 1: return [dict(pie=0, cab=1, medio=None, s=1)]
    if nv <= 3: return [dict(pie=0, cab=2, medio=1, s=1)]
    return [dict(pie=0, cab=2, medio=1, s=1), dict(pie=nv, cab=nv - 2, medio=nv - 1, s=-1)]


def reservados(t):
    return {d[k] for d in t['diagonales'] for k in ('pie', 'cab')}


def ubicar_anclas(t0, t1, a, obs, anclas):
    """Palos a no más de a: el primero a 15 cm de cada punta, uno en cada ancla (donde va una cruz con la línea
    vecina) y los demás iguales entre anclas; si uno cae sobre un pilar se corre a su borde."""
    u0, u1 = t0 + GEO['borde'], t1 - GEO['borde']
    for o0, o1, _ in obs:
        if o0 < u0 < o1: u0 = o1
        if o0 < u1 < o1: u1 = o0
    if u1 <= u0: return [r1((t0 + t1) / 2)]
    for c in anclas:                                       # un ancla junto a la punta corre el palo de punta (a 15 cm o más del extremo)
        if t0 + GEO['borde'] - 0.05 <= c < u0 + 20: u0 = c
        if u1 - 20 < c <= t1 - GEO['borde'] + 0.05: u1 = c
    fijos = sorted(set([u0, u1] + [c for c in anclas if u0 + 20 <= c <= u1 - 20]))
    fijos = [c for i, c in enumerate(fijos) if i == 0 or c - fijos[i - 1] > 1]
    res = []
    for i in range(len(fijos) - 1):
        p, q = fijos[i], fijos[i + 1]
        n = max(1, math.ceil((q - p) / a - 1e-9))
        for k in range(0 if i == 0 else 1, n + 1):
            c = p + (q - p) * k / n
            if 0 < k < n:
                for o0, o1, _ in obs:
                    if o0 < c < o1: c = o0 if c - o0 < o1 - c else o1
            res.append(r1(c))
    return res


# ------------------------------------------------------------------ datos de cada línea (no dependen de las cruces)
BASES_L = []
n_por_area = {}
for l in sorted(L['alzaprimas'], key=lambda l: (l['area'], l['pos'])):
    ns = l['dir'] == 'NS'
    reg = REGLA[(l['area'], l['pos'])]
    n_por_area[l['area']] = n_por_area.get(l['area'], 0) + 1
    lid = f"{l['area']}-{n_por_area[l['area']]}"
    s_ = l['vano'] / l['espacios']
    um = (l['a0'] + l['a1']) / 2
    p0 = None
    for k in range(1, l['espacios']):
        c0 = l['pos'] - l['vano'] * k / l['espacios']
        if viga_en(c0, ns, um) or eje_cercano(c0, GR['letras'] if ns else GR['numeros'], 3.0):
            p0 = c0; break
    if p0 is None: p0 = l['pos'] - s_
    p1 = p0 + l['vano']
    ejes_largo = GR['numeros'] if ns else GR['letras']
    f = max(1.0, reg['f_rev'])
    w = {k: CAR['k_reaccion_placa'] * q * s_ / 100 * f for k, q in Q.items()}
    Np = (PALO1 if l['area'] == 1 else PALO)['N']                               # área 1: para terreno (lo más largo)
    am, manda = a_max(w['aci'], Np)
    tr, dentro = recortar(l)
    BASES_L.append(dict(l=l, id=lid, ns=ns, s=s_, p0=p0, f=f, w=w, Np=Np, am=am, manda=manda, a=int(am // GEO['modulo'] * GEO['modulo']),
                        tr=tr, dentro=dentro, obs=obstaculos(l), reg=reg,
                        entre=[nombre_linea_viga(p0, ns, um), nombre_linea_viga(p1, ns, um)],
                        de=[eje_cercano(l['a0'], ejes_largo, 10.0) or f"{l['a0']:.0f}", eje_cercano(l['a1'], ejes_largo, 10.0) or f"{l['a1']:.0f}"]))
BL = {x['id']: x for x in BASES_L}

# orden: cada línea se arma después de la vecina con que se cruza (las cruces de la vecina fijan sus palos)
VEC = {}
for A_id, B_id in LADO['pares']:
    assert BL[A_id]['l']['dir'] == BL[B_id]['l']['dir'], (A_id, B_id)
    VEC.setdefault(A_id, []).append(B_id); VEC.setdefault(B_id, []).append(A_id)
ORDEN = []
for x in BASES_L:
    if x['id'] in ORDEN: continue
    cola = [x['id']]
    while cola:
        u = cola.pop(0)
        if u in ORDEN: continue
        ORDEN.append(u); cola += [v for v in VEC.get(u, []) if v not in ORDEN]


def armar_linea(B, anclas):
    """Palos, uniones, diagonales y reacciones de una línea con sus anclas."""
    l, w, a = B['l'], B['w'], B['a']
    tramos = []
    for (t0, t1), (m0, m1) in zip(B['tr'], l['tramos']):
        pun = ubicar_anclas(t0, t1, a, B['obs'], [u for u in anclas if t0 <= u <= t1])
        nv = len(pun) - 1
        ua, ub = uniones_solera(t0, t1, pun, SOL['largo_max'])
        a0b, a1b = pun[0] - b / 20 - ABJ['vuelo'], pun[-1] + b / 20 + ABJ['vuelo']          # solera abajo: hasta 10 cm pasado el palo de punta
        medios = [(k, (pun[k] + pun[k + 1]) / 2) for k in range(nv)]
        cab = cortes(a0b, a1b, medios, ABJ['largo_max'])
        jab = [r1(dict(medios)[k]) for k in cab]
        m0a, m1a = pun[0] - b / 20 - 5, pun[-1] + b / 20 + 5
        uam = cortes(m0a, m1a, [(j, pun[j]) for j in range(1, len(pun) - 1)], AMA['largo_max'])
        if uam is None: raise SystemExit(f"{B['id']}: amarre sin cortes posibles")
        R = [x + y for x, y in zip(reacciones(t0, t1, pun, ua, w['aci'] * 10 / 2), reacciones(t0, t1, pun, ub, w['aci'] * 10 / 2))]
        tramos.append(dict(t0=t0, t1=t1, modelo=[m0, m1], largo=r1(t1 - t0), palos=pun, vanos=[r1(pun[i + 1] - pun[i]) for i in range(nv)],
                           uniones_a=ua, uniones_b=ub, piezas_a=trozos(t0, t1, [pun[j] for j in ua]), piezas_b=trozos(t0, t1, [pun[j] for j in ub]),
                           abajo=jab, abajo_ext=[r1(a0b), r1(a1b)], piezas_abajo=trozos(a0b, a1b, jab), amarre=[r1(m0a), r1(m1a)], uniones_amarre=uam,
                           piezas_amarre=trozos(m0a, m1a, [pun[j] for j in uam]), diagonales=diagonales_de(nv), R_N=R, extra_V=[0.0] * len(pun),
                           cruces_en={}))
    return tramos


def solapes(A, B):
    for ta in A['tramos']:
        for tb in B['tramos']:
            o0, o1 = max(ta['t0'], tb['t0']), min(ta['t1'], tb['t1'])
            if o1 - o0 >= 100: yield ta, tb, o0, o1


EXTRA = {}            # (A, B, o0 redondeado) -> cruces intermedias pedidas por la flexión de lado
for vuelta in range(12):
    LINS, CRUCES, AVISOS = {}, [], []
    anclas = {x['id']: [] for x in BASES_L}
    for lid in ORDEN:
        B = BL[lid]
        LINS[lid] = dict(B, tramos=armar_linea(B, anclas[lid]))
        X = LINS[lid]
        for vid in VEC.get(lid, []):
            if vid in LINS: continue                         # esa vecina ya está armada: la cruz la puso ella
            V_ = BL[vid]
            for ta, tb, o0, o1 in solapes(X, dict(tramos=[dict(t0=t0, t1=t1) for t0, t1 in V_['tr']])):
                lado = 1 if V_['l']['pos'] > B['l']['pos'] else -1
                ocupados = set(ta['cruces_en'])
                res = reservados(ta)
                cand = []
                for j, u in enumerate(ta['palos']):
                    if u in ocupados or not (o0 + GEO['borde'] - 1 <= u <= o1 - GEO['borde'] + 1): continue
                    P = (u, B['l']['pos']) if B['ns'] else (B['l']['pos'], u)
                    Q_ = (u, V_['l']['pos']) if B['ns'] else (V_['l']['pos'], u)
                    ac, mu = choques(P, Q_)
                    if ac: continue
                    cand.append((j, u, mu, j in res))
                if not cand: AVISOS.append(f'{lid}–{vid} en {o0:.0f}–{o1:.0f}: sin palo libre para la cruz'); continue
                n = 1 if o1 - o0 < 200 else 2 + EXTRA.get((lid, vid, round(o0)), 0)
                metas = [(o0 + o1) / 2] if n == 1 else [o0 + (o1 - o0) * i / (n - 1) for i in range(n)]
                elegidos = []
                for m in metas:
                    libres = [c for c in cand if c[1] not in [e[1] for e in elegidos]]
                    if not libres: break
                    elegidos.append(min(libres, key=lambda c: abs(c[1] - m) + (40 if c[3] else 0)))   # mejor un palo sin diagonal
                for j, u, mu, rv in sorted(elegidos, key=lambda c: c[1]):
                    anclas[vid].append(u)
                    ta['cruces_en'][u] = lado
                    CRUCES.append(dict(par=[lid, vid], dir=B['l']['dir'], pos=[B['l']['pos'], V_['l']['pos']], u=u,
                                       D=r1(abs(V_['l']['pos'] - B['l']['pos'])), muros=mu, ta=ta, tb_o=(o0, o1), en_diag=rv))
    # tramo de la vecina que recibe cada cruz (ya armada), y banda de alturas
    for c in CRUCES:
        V_ = LINS[c['par'][1]]
        tb = next(t for t in V_['tramos'] if t['t0'] - 1 <= c['u'] <= t['t1'] + 1)
        if c['u'] not in tb['palos']: AVISOS.append(f"{c['par'][1]}: la cruz con {c['par'][0]} en {c['u']} no cae en un palo"); c['tb'] = tb; c['banda'] = 0; continue
        c['tb'] = tb
        otra = tb['cruces_en'].get(c['u'])
        lado_b = 1 if c['pos'][0] > c['pos'][1] else -1
        # banda baja (uniones a 70 y 295) si el palo ya tiene una cruz del otro lado o es el pie o la cabeza de una diagonal
        c['banda'] = 1 if (otra is not None and otra != lado_b) or c['en_diag'] or tb['palos'].index(c['u']) in reservados(tb) else 0
        tb['cruces_en'][c['u']] = lado_b
    # fuerzas horizontales por tramo (la de ACI 347 de lado va a las cruces solo si 'aci_a_alzaprimas')
    K_ACI = 1.0 if CAR.get('aci_a_alzaprimas', True) else 0.0
    TR = [(LINS[i], t) for i in ORDEN for t in LINS[i]['tramos']]
    xs_ = [p[0] for p in L['perimetro']]; ys_ = [p[1] for p in L['perimetro']]
    H_ACI = {'x': CAR['aci_borde_kN_m'] * (max(ys_) - min(ys_)) / 100 * 1000, 'y': CAR['aci_borde_kN_m'] * (max(xs_) - min(xs_)) / 100 * 1000}
    WL = sum(x['w']['aci'] * (t['t1'] - t['t0']) for x, t in TR)
    for x, t in TR:
        parte = x['w']['aci'] * (t['t1'] - t['t0']) / WL
        sumR = sum(t['R_N'])
        largo, lado = ('x', 'y') if x['ns'] else ('y', 'x')
        t['H_arr_N'] = round(CAR['h_arriostre'] * sumR)                               # arriostre del amarre: lo llevan las diagonales
        t['H_largo_N'] = round(CAR['h_arriostre'] * sumR + H_ACI[largo] * parte)     # todo a lo largo: lo llevan los calces al acero
        t['H_lado_N'] = round(CAR['h_arriostre'] * sumR + K_ACI * H_ACI[lado] * parte)   # de lado: lo llevan las cruces
        t['cruces'] = sorted(t['cruces_en'])
    # flexión de la solera de arriba de lado, entre cruces (sección corriente y uniones con una sola pieza)
    malos = []
    for x, t in TR:
        us = t['cruces']
        cortes_l = [t['t0']] + us + [t['t1']]
        q = t['H_lado_N'] / (t['largo'] * 10)
        def M_lado(u):
            for i in range(len(cortes_l) - 1):
                if cortes_l[i] <= u <= cortes_l[i + 1]:
                    L_ = (cortes_l[i + 1] - cortes_l[i]) * 10; xx = (u - cortes_l[i]) * 10
                    return q * xx * (L_ - xx) / 2
            return 0.0
        luz = max(cortes_l[i + 1] - cortes_l[i] for i in range(len(cortes_l) - 1))
        sv = x['w']['aci'] * (max(t['vanos']) * 10 if t['vanos'] else 0) ** 2 / 8 / W_SOL / FF
        sl = q * (luz * 10) ** 2 / 8 / W_LADO / FF_LADO
        peor = sv + sl
        if not SOL.get('cubrejunta'):                                               # sin cubrejunta: en la unión, la otra pieza sola
            for j in t['uniones_a'] + t['uniones_b']:
                vv = max(t['vanos'][max(0, j - 1)], t['vanos'][min(len(t['vanos']) - 1, j)]) * 10
                peor = max(peor, (x['w']['aci'] / 2) * vv ** 2 / 8 / W_UNA / FF + M_lado(t['palos'][j]) / W_LADO_UNA / FF_LADO_UNA)
        t['dc_biaxial'] = r2(peor); t['luz_lado'] = r1(luz)
        if peor > 1.0: malos.append((x, t))
    if not malos and not [t for _, t in TR if len(t['cruces']) < (2 if t['largo'] >= 200 else 1)]: break
    for x, t in malos + [(x, t) for x, t in TR if len(t['cruces']) < (2 if t['largo'] >= 200 else 1)]:
        for c in CRUCES:
            if c['ta'] is t or c['tb'] is t:
                k = (c['par'][0], c['par'][1], round(c['tb_o'][0])); EXTRA[k] = EXTRA.get(k, 0) + 1; break
else:
    raise SystemExit('la solera no da de lado ni con 12 vueltas de cruces: ' + str([(x['id'], t['t0'], t['dc_biaxial'], t['cruces']) for x, t in malos]))

# ------------------------------------------------------------------ diagonales, cruces y cargas extra en los palos
def geo_diag(t, d, dz):
    up, uc = t['palos'][d['pie']], t['palos'][d['cab']]
    run = abs(uc - up); sube = Z_CAB - Z_PIE + dz
    return up, uc, run, sube, math.hypot(run, sube)


for x, t in TR:
    nd = len(t['diagonales'])
    for d in t['diagonales']:
        out = {}
        for caso, dz in (('', 0), ('_t', ALT['terreno_area1'] if x['l']['area'] == 1 else 0)):
            up, uc, run, sube, Lc = geo_diag(t, d, dz)
            N = (0.6 if nd == 2 else 1.0) * t['H_arr_N'] * Lc / run
            Lp = Lc / 2                                                         # atornillada al palo del medio (o al taco, si es de 1 vano)
            ld, nd_ = columna(Lp * 10, b); lf, nf = columna(Lp * 10, h)
            out[caso] = dict(Lc=Lc, N=N, V=N * sube / Lc, H=N * run / Lc, lam=max(ld, lf), dc=N / min(nd_, nf))
        o, ot = out[''], out['_t']
        d.update(u=[t['palos'][d['pie']], t['palos'][d['cab']]], z=[Z_PIE, Z_CAB], L=r1(o['Lc'] + 30), L_t=r1(ot['Lc'] + 30), Lc=r1(o['Lc']),
                 N_N=round(max(o['N'], ot['N'])), V_N=round(max(o['V'], ot['V'])), H_N=round(o['H']), lam=r1(max(o['lam'], ot['lam'])),
                 dc=r2(max(o['dc'], ot['dc'])), torn=max(3, math.ceil(max(o['N'], ot['N']) / TOR - 1e-9)), taco=d['medio'] is None)
        assert d['lam'] <= MAD['lambda_max_arriostre'], (x['id'], d)
        assert d['torn'] <= LADO['torn_max_65'], (x['id'], d)
        t['extra_V'][d['cab']] += d['V_N']                                     # en tracción carga la cabeza del palo de la cabeza
        t.setdefault('levante', []).append((d['pie'], d['V_N']))
for c in CRUCES:
    ta, tb = c['ta'], c['tb']
    F = ta['H_lado_N'] / max(1, len(ta['cruces'])) + tb['H_lado_N'] / max(1, len(tb['cruces']))
    zb, zt = BANDAS[c['banda']]
    out = {}
    for caso, dz in (('', 0), ('_t', ALT['terreno_area1'] if BL[c['par'][0]]['l']['area'] == 1 else 0)):
        sube = zt - zb + dz; Lc = math.hypot(c['D'], sube); N = F * Lc / c['D']
        ld, nd_ = columna(Lc * 10 / 2, b); lf, nf = columna(Lc * 10 / 2, h)              # atornilladas entre sí en el cruce (taco)
        out[caso] = dict(Lc=Lc, N=N, V=N * sube / Lc, lam=max(ld, lf), dc=N / min(nd_, nf))
    o, ot = out[''], out['_t']
    c.update(F_N=round(F), Lc=r1(o['Lc']), L=r1(o['Lc'] + 30), L_t=r1(ot['Lc'] + 30), N_N=round(max(o['N'], ot['N'])), V_N=round(max(o['V'], ot['V'])),
             lam=r1(max(o['lam'], ot['lam'])), dc=r2(max(o['dc'], ot['dc'])), torn=max(3, math.ceil(max(o['N'], ot['N']) / TOR - 1e-9)), z=[zb, zt])
    assert c['lam'] <= MAD['lambda_max_arriostre'], c
    for t_ in (ta, tb):                                                          # en tracción carga la cabeza de un palo y levanta el pie del otro
        k = t_['palos'].index(c['u']); t_['extra_V'][k] += c['V_N']; t_.setdefault('levante', []).append((k, c['V_N']))

# ------------------------------------------------------------------ resultado por línea
lineas, tot_dentro = [], 0
for x in BASES_L:
    X = LINS[x['id']]; l, w, Np = x['l'], x['w'], x['Np']
    tramos = X['tramos']
    seps = [v for t in tramos for v in t['vanos']]
    a_real = max(seps) if seps else x['a']
    amm = a_real * 10
    P_d = KAP * w['aci'] * amm
    carga = max(max(r + v for r, v in zip(t['R_N'], t['extra_V'])) for t in tramos)       # palo más cargado, con diagonales y cruces
    R_max = max(max(t['R_N']) for t in tramos)
    R_union = max([t['R_N'][j] for t in tramos for j in t['uniones_a'] + t['uniones_b']] or [0])
    lev = min([t['R_N'][k] - V for t in tramos for k, V in t.get('levante', [])] or [1e9])
    dem = CAR['k_reaccion_placa'] * x['s'] * x['f']
    dc = dict(
        solera=w['aci'] * amm ** 2 / 8 / M_SOL,
        corte=0.625 * w['aci'] * amm / V_SOL,
        palo=max(P_d, carga) / Np,
        apoyo=max(max(P_d, R_max) / N_APOYO, R_union / N_UNION),
        apoyo_abajo=max(P_d, carga) / N_APOYO_ABAJO,
        apoyo_placa=dem / R_FICHA3 * abolladura(AP['ala_ipe220']) / abolladura(AP['ancho_solera']),
        apoyo_placa_2v=dem / R_FICHA2 * abolladura(AP['ala_ipe220']) / abolladura(AP['ancho_solera']),
        biaxial=max(t['dc_biaxial'] for t in tramos),
        diagonal=max([d['dc'] for t in tramos for d in t['diagonales']] or [0]),
        calce=max(t['H_largo_N'] for t in tramos) / (FCP * LADO['ala_min_mm'] * SOL['piezas'] * b),
    )
    assert dc['solera'] <= 1.0 + 1e-6 and dc['palo'] <= PAL['holgura'] + 0.02 and dc['apoyo'] <= PAL['holgura'] + 0.02 and dc['biaxial'] <= 1.0, (x['id'], dc)
    assert lev >= 0, (x['id'], 'levanta un pie', lev)
    tot_dentro += x['dentro']
    for t in tramos:
        t['R_kgf'] = [round(r / G_ACC) for r in t['R_N']]
        t['V_kgf'] = [round(v / G_ACC) for v in t['extra_V']]
        t['cruces_lado'] = [t['cruces_en'][u] for u in t['cruces']]
        for k_ in ('R_N', 'extra_V', 'cruces_en', 'levante'): t.pop(k_, None)
    lineas.append(dict(
        id=x['id'], area=l['area'], dir=l['dir'], pos=l['pos'], vano=l['vano'], espacios=l['espacios'],
        entre=x['entre'], desde=x['entre'][0], dist=r1(l['pos'] - x['p0']), de=x['de'], a0=l['a0'], a1=l['a1'],
        luz=[r1(x['s']), r1(x['s'])], a=x['a'], a_max=r1(x['am']), manda=x['manda'], a_real=r1(a_real),
        tramos=tramos, n_palos=sum(len(t['palos']) for t in tramos), solera_m=r2(sum(t['largo'] for t in tramos) / 100),
        extremos_en_ala=x['dentro'], obstaculos=[o[2] for o in x['obs']],
        f_rev=x['reg']['f_rev'], f=x['f'], w_aci=r2(w['aci']), w_base=r2(w['base']),
        P_kgf=round(w['aci'] * amm / G_ACC), P_max_kgf=round(P_d / G_ACC), R_max_kgf=round(R_max / G_ACC), R_k=r2(R_max / (w['aci'] * amm)),
        carga_max_kgf=round(max(P_d, carga) / G_ACC), levante_min_kgf=round(lev / G_ACC),
        H=r1(H_PALO), H_terreno=r1(H_PALO1) if l['area'] == 1 else None, N_palo_kgf=round(Np / G_ACC),
        flecha_mm=r1(5 * w['base'] * amm ** 4 / (384 * EI_SOL)), dc={k: r2(v) for k, v in dc.items()},
        uniones=sum(len(t['uniones_a']) + len(t['uniones_b']) for t in tramos), diagonales=sum(len(t['diagonales']) for t in tramos),
        cruces=sum(1 for c in CRUCES if x['id'] in c['par'])))
LIN = {x['id']: x for x in lineas}
TR = [(x, t) for x in lineas for t in x['tramos']]
for c in CRUCES:
    c.pop('ta'); c.pop('tb'); c.pop('tb_o')
CRUCES.sort(key=lambda c: (c['par'], c['u']))
CHOQUES_MUROS = sorted({k for c in CRUCES for k in c['muros']})

# ------------------------------------------------------------------ cantidades
NP = sum(x['n_palos'] for x in lineas)
A1 = [x for x in lineas if x['area'] == 1]
NP1 = sum(x['n_palos'] for x in A1)
TRS = [t for _, t in TR]
n_ua = sum(len(t['uniones_a']) + len(t['uniones_b']) for t in TRS)
n_uam = sum(len(t['uniones_amarre']) for t in TRS)
n_diag = sum(len(t['diagonales']) for t in TRS)
sol_m = sum(t['largo'] for t in TRS) / 100
PIEZAS = []          # (uso, largo cm)
for x in lineas:
    for t in x['tramos']:
        PIEZAS += [('palo', H_PALO)] * len(t['palos'])
        PIEZAS += [('solera', p) for p in t['piezas_a'] + t['piezas_b']]
        PIEZAS += [('abajo', p) for p in t['piezas_abajo']]
        PIEZAS += [('amarre', p) for p in t['piezas_amarre']]
        PIEZAS += [('cubrejunta', AMA['cubrejunta'])] * len(t['uniones_amarre'])
        PIEZAS += [('cubrejunta_s', SOL['cubrejunta'])] * (len(t['uniones_a']) + len(t['uniones_b']))
        a1 = x['area'] == 1                                                   # área 1: largos para terreno (lo más largo)
        PIEZAS += [('diagonal', d['L_t'] if a1 else d['L']) for d in t['diagonales']]
        PIEZAS += [('taco', h / 10) for d in t['diagonales'] if d['taco']]      # taco del cruce diagonal–amarre (diagonal de 1 vano)
        PIEZAS += [('tope', LADO['tope'])] * len(t['diagonales'])               # tope en el pie del palo donde nace la diagonal
PIEZAS += [('cruz', c['L_t'] if LIN[c['par'][0]]['area'] == 1 else c['L']) for c in CRUCES for _ in (0, 1)]
PIEZAS += [('taco_x', LADO['taco_cruz'])] * len(CRUCES)                       # taco de 6,5 entre las dos piezas de la X
COMPRA = 400


def empacar(piezas, largo):
    """Primero el más largo en la pieza de compra donde quepa (con 0,5 cm de corte). Piezas de más del largo de
    compra se piden a su largo (redondeado a 10 cm)."""
    barras, largas = [], []
    for uso, p in sorted(piezas, key=lambda t: -t[1]):
        if p > largo: largas.append((uso, p)); continue
        for bar in barras:
            if bar['libre'] >= p + 0.5: bar['libre'] -= p + 0.5; bar['usos'].append(uso); break
        else: barras.append(dict(libre=largo - p - 0.5, usos=[uso]))
    return barras, largas


BARRAS, LARGAS = empacar(PIEZAS, COMPRA)
USOS = [('palo', 'Palos', f'atravesados, de {cm(H_PALO, 3)} m (área 1 en terreno: {cm(H_PALO1, 3)})'),
        ('solera', 'Solera de arriba', '2 piezas de canto lado a lado, trabadas'),
        ('abajo', 'Solera abajo', 'plana, suelta en el piso'),
        ('amarre', 'Amarre', 'de canto a media altura, cara A'),
        ('cubrejunta', 'Cubrejuntas', f'{AMA["cubrejunta"]} cm, en las uniones del amarre'),
        ('cubrejunta_s', 'Cubrejuntas de solera', f'{SOL["cubrejunta"]} cm, por fuera de cada unión de la solera de arriba'),
        ('diagonal', 'Diagonales', 'sobre 2 vanos: pie de un palo → cabeza del que sigue al siguiente, cara B'),
        ('taco', 'Tacos', f'{h / 10:.0f} cm, entre diagonal y amarre (diagonales de 1 vano)'),
        ('tope', 'Topes', f'{LADO["tope"]} cm, en el pie del palo donde nace cada diagonal'),
        ('cruz', 'Cruces de lado', 'X entre palos de líneas vecinas, 2 por cruz'),
        ('taco_x', 'Tacos de cruz', f'{LADO["taco_cruz"]} cm, entre las dos piezas de cada X')]
MAT = []
for k, nom, uso in USOS:
    ps = [p for u, p in PIEZAS if u == k]
    if not ps: continue
    MAT.append(dict(k=k, mat=nom, uso=uso, n=len(ps), ml=r1(sum(ps) / 100), min=r1(min(ps)), max=r1(max(ps))))
ML = sum(m['ml'] for m in MAT)
LARGAS_10 = sorted({math.ceil(p / 10) * 10 for _, p in LARGAS})
n_largas = {L_: sum(1 for _, p in LARGAS if math.ceil(p / 10) * 10 == L_) for L_ in LARGAS_10}
# área 1 en terreno: palos de 4,40 y solera abajo doble (cuenta aparte, supuesto)
A1_extra = dict(palos=NP1, largo_palo=r1(H_PALO1), compra_palo=440, abajo_m=r1(sum(t['largo'] for x in A1 for t in x['tramos']) / 100))

TORN = {             # ø6 × 120: lanceros y solera; ø6 × 150 con caña lisa ≥ 70 mm: lo que trabaja a corte entre dos piezas
    'cabeza': 2 * NP,                                                     # 120: palo a la solera de arriba, 2 lanceros
    'pie': 2 * NP,                                                        # 120: palo a la solera abajo, 2 lanceros
    'solera': sum(math.ceil(t['largo'] / 60) + 1 for t in TRS),          # 120: las dos piezas de arriba entre sí, @60
    'cubrejunta_s': 6 * n_ua,                                             # 150: cubrejunta de la solera, 3 + 3
    'amarre': 2 * NP + 6 * n_uam,                                         # 150: 2 por palo + cubrejuntas 3 + 3
    'diagonal': sum(2 * d['torn'] + (4 if d['taco'] else 2) for t in TRS for d in t['diagonales']),   # 150: 2 puntas + palo del medio (o taco)
    'tope': 4 * n_diag,                                                   # 150: tope a la solera abajo
    'cruz': sum(4 * c['torn'] + 4 for c in CRUCES),                       # 150: 2 piezas × 2 puntas + taco del cruce (2 + 2)
}
TORN_120 = TORN['cabeza'] + TORN['pie'] + TORN['solera']
N_CALCES = 4 * len(TRS)                                                   # terciado de 1 cm: las dos piezas, en las dos puntas

# ------------------------------------------------------------------ base sobre terreno (área 1, supuesto)
def solera_terreno(P_N, piezas):
    """Solera abajo de 'piezas' 3x9 planos lado a lado sobre suelo elástico (Hetényi, viga infinita): presión bajo el
    palo (kg/cm²) y D/C en flexión con madera húmeda (Ff × 0,75, E × 0,83)."""
    bb = piezas * h
    EI = MAD['E'] * 0.83 * bb * b ** 3 / 12
    beta = (BASE['k_suelo'] * bb / (4 * EI)) ** 0.25
    p = P_N * beta / (2 * bb)
    M = P_N / (4 * beta) - P_N * (b / 10 * 10) / 8
    return p * 100 / G_ACC, M / (bb * b * b / 6) / (MAD['Ff'] * KD * 0.75)


P1 = max(x['P_max_kgf'] for x in A1) * G_ACC
P_TERR, DC_TERR = solera_terreno(P1, 2)
P_TERR1, DC_TERR1 = solera_terreno(P1, 1)

P_MAX = max(x['P_max_kgf'] for x in lineas)
L_MAX = max(lineas, key=lambda x: x['P_max_kgf'])
R_MAX = max(x['R_max_kgf'] for x in lineas)
L_RMAX = max(lineas, key=lambda x: x['R_max_kgf'])
PEOR_AP = max(lineas, key=lambda x: x['dc']['apoyo_placa'])
VALS = dict(n_muros=sum(1 for c in CRUCES if c['muros']), muros=', '.join(f"{c['par'][0]}/{c['par'][1]} en {cm(c['u'])}" for c in CRUCES if c['muros']),
            H1=cm(H_PALO1), n1=NP1, a_min=cm(min(v for x in lineas for t in x['tramos'] for v in t['vanos'])), a_max=cm(max(x['a_real'] for x in lineas)), P=miles(max(x['P_max_kgf'] for x in lineas)),
            apoyo=f'máx. {PEOR_AP["dc"]["apoyo_placa"]:.2f} de lo que acepta la ficha ({PEOR_AP["id"]}; con 2 vanos {PEOR_AP["dc"]["apoyo_placa_2v"]:.2f})'.replace('.', ','))
POR_CONF = [[t.format(**VALS), q] for t, q in C['por_confirmar']]
AP_TXT = AP['porque'].format(L3=cm(LUZ3), L2=cm(LUZ2), hc=f'{HC:.2f}'.replace('.', ','))

TOT = dict(lineas=len(lineas), tramos=len(TRS), palos=NP, palos_area1=NP1, P_max=P_MAX, P_max_linea=L_MAX['id'],
           carga_max=max(x['carga_max_kgf'] for x in lineas), carga_max_linea=max(lineas, key=lambda x: x['carga_max_kgf'])['id'], n_calces=N_CALCES,
           R_max=R_MAX, R_max_linea=L_RMAX['id'], R_k_max=max(x['R_k'] for x in lineas),
           N_palo=round(PALO['N'] / G_ACC), N_palo1=round(PALO1['N'] / G_ACC), N_apoyo=round(N_APOYO / G_ACC), N_apoyo_abajo=round(N_APOYO_ABAJO / G_ACC),
           lam_d=r1(PALO['lam_d']), lam_f=r1(PALO['lam_f']), lam_suelto=r1(PALO['lam_suelto']), lam_d1=r1(PALO1['lam_d']), lam_suelto1=r1(PALO1['lam_suelto']),
           H_palo=r1(H_PALO), H_palo1=r1(H_PALO1), z_amarre=r1(Z_AMARRE),
           solera_m=r1(sol_m), uniones_solera=n_ua, uniones_amarre=n_uam, diagonales=n_diag, cruces=len(CRUCES),
           ml=r1(ML), compra=COMPRA, barras=len(BARRAS), largas=[[k_, v] for k_, v in n_largas.items()],
           m3=r2(ML / 100 * b * h / 1e6 * 100) if False else r2(ML * b * h / 1e6), torn=TORN, torn_total=sum(TORN.values()),
           extremos_en_ala=tot_dentro, extremos=2 * len(TRS),
           dc_solera_max=max(x['dc']['solera'] for x in lineas), dc_palo_max=max(x['dc']['palo'] for x in lineas),
           dc_apoyo_max=max(x['dc']['apoyo'] for x in lineas), dc_biaxial_max=max(x['dc']['biaxial'] for x in lineas),
           dc_diag_max=max(x['dc']['diagonal'] for x in lineas), dc_cruz_max=max(c['dc'] for c in CRUCES),
           apoyo_max=PEOR_AP['dc']['apoyo_placa'], apoyo_max_2v=PEOR_AP['dc']['apoyo_placa_2v'], apoyo_max_linea=PEOR_AP['id'],
           flecha_max=max(x['flecha_mm'] for x in lineas), a_min=round(min(v for x in lineas for t in x['tramos'] for v in t['vanos'])), a_max=round(max(x['a_real'] for x in lineas)),
           H_aci_kN=[r1(H_ACI['x'] / 1000), r1(H_ACI['y'] / 1000)],
           f_min=min(x['f'] for x in lineas if x['f'] > 1), f_max=max(x['f'] for x in lineas), n_f=sum(1 for x in lineas if x['f'] > 1),
           peso_pieza=round(COMPRA / 100 * b * h / 1e6 * 476))
BASES = dict(p=r2(P_TERR), dc=r2(DC_TERR), p1=r2(P_TERR1), dc1=r2(DC_TERR1), **A1_extra)


# vigas de entrepiso para la planta: receptora = perpendicular a las planchas de un área que cruza
def receptora(m):
    (ax, ay), (bx, by) = m['a'][:2], m['b'][:2]
    hz = abs(ay - by) < 1
    for ar in L['areas']:
        xs_ = [p[0] for p in ar['huella']]; ys_ = [p[1] for p in ar['huella']]
        if ar['dir'] == 'NS' and hz and min(ys_) - 3 <= ay <= max(ys_) + 3 and min(max(ax, bx), max(xs_)) - max(min(ax, bx), min(xs_)) > 20: return True
        if ar['dir'] == 'EO' and not hz and min(xs_) - 3 <= ax <= max(xs_) + 3 and min(max(ay, by), max(ys_)) - max(min(ay, by), min(ys_)) > 20: return True
    return False


VIGAS = [dict(id=m['id'], p=m['p'], b=PERF[m['p']]['b'], a=m['a'][:2], c=m['b'][:2], rec=receptora(m)) for m in VIG]
PILARES = []
for p in PIL:
    pr = PERF[p['p']]
    if pr.get('forma') == 'tubo_circ': PILARES.append(dict(id=p['id'], x=p['a'][0], y=p['a'][1], d=pr['d']))
    else: PILARES.append(dict(id=p['id'], x=p['a'][0], y=p['a'][1], b=pr.get('b', 15), h=pr.get('h', 15), alma=p.get('alma')))

MADERA = dict(MAD, Ff_dis=r2(FF), Ff_plano=r2(FF_PLANO), Fcp_dis=r2(FCP), Fcn_dis=r2(FCN), Fcz_dis=r2(FCZ), E_dis=round(E_D),
              Kcn=r2(Kcn(b)), M_solera_kNm=r2(M_SOL / 1e6), V_solera_kN=r1(V_SOL / 1000))
out = dict(
    fuente='fuente/losa/generar_alzaprimas_js.py: losa.js + estructura.js + fuente/losa/alzaprimas.json',
    fecha=C['fecha'], pedido=C['pedido'],
    madera=MADERA, cargas=dict(D_kgm2=round(D_kPa * 1000 / G_ACC), q_base_kgm2=round(Q['base'] * 1000 / G_ACC),
                               q_aci_kgm2=round(Q['aci'] * 1000 / G_ACC), k_reaccion_placa=CAR['k_reaccion_placa'], k_apoyo=KAP,
                               h_arriostre=CAR['h_arriostre'], porque=CAR['porque']),
    antes=C['antes'], W_solera_mm3=round(W_SOL), palo=PAL, solera=SOL, abajo=ABJ, amarre=AMA, diagonal=DIA, lado=dict(LADO), alturas=dict(ALT, palo=r1(H_PALO), palo1=r1(H_PALO1), amarre=r1(Z_AMARRE)),
    apoyo_placa=dict(AP, porque=AP_TXT, luz_3v=r1(LUZ3), luz_2v=r1(LUZ2), hc=r2(HC)),
    geometria=GEO, f_rev_porque=C['f_rev_porque'], base=BASES,
    base_porque=BASE['porque'].format(**{k: f'{v:.2f}'.replace('.', ',') for k, v in BASES.items() if k in ('p', 'dc', 'p1', 'dc1')}),
    lineas=lineas, cruces=CRUCES, totales=TOT, materiales=MAT, vigas=VIGAS, pilares_n1=PILARES,
    datos=C['datos'], supuestos=C['supuestos'], por_confirmar=POR_CONF,
)
js = '// Generado por fuente/losa/generar_alzaprimas_js.py — no editar a mano.\nconst DATA_ALZAPRIMAS = ' + \
     json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n'
open(os.path.join(RAIZ, 'alzaprimas.js'), 'w', encoding='utf-8').write(js)

print(f"{len(lineas)} líneas · {len(TRS)} tramos · {NP} palos de {H_PALO:.1f} cm (área 1 {NP1}, {H_PALO1:.1f} si es terreno) · solera {sol_m:.1f} m · "
      f"{n_ua} uniones de solera · {n_uam} del amarre · {n_diag} diagonales · {len(CRUCES)} cruces")
print(f"palo: λ suelto {PALO['lam_suelto']:.0f} · con amarre {PALO['lam_d']:.0f}/{PALO['lam_f']:.0f} → {PALO['N'] / 1000:.1f} kN; área 1 {PALO1['N'] / 1000:.1f} kN · "
      f"apoyo arriba {N_APOYO / 1000:.1f} kN · abajo {N_APOYO_ABAJO / 1000:.1f} kN · solera M {M_SOL / 1e6:.2f} kN·m V {V_SOL / 1000:.1f} kN")
print(f"P máx {P_MAX} kgf ({L_MAX['id']}) · R máx {R_MAX} ({L_RMAX['id']}, {TOT['R_k_max']}·w·a) · D/C máx solera {TOT['dc_solera_max']} palo {TOT['dc_palo_max']} "
      f"apoyo {TOT['dc_apoyo_max']} biaxial {TOT['dc_biaxial_max']} diagonal {TOT['dc_diag_max']} cruz {TOT['dc_cruz_max']} · placa {TOT['apoyo_max']} ({TOT['apoyo_max_linea']})")
print(f"3x9: {ML:.1f} m ({TOT['m3']} m³) en {len(BARRAS)} piezas de {COMPRA / 100:.2f} m + largas {n_largas} · tornillos {TORN} = {TOT['torn_total']}")
print('materiales', [(m['mat'], m['n'], m['ml']) for m in MAT])
print('base terreno', BASES, 'H ACI kN', TOT['H_aci_kN'])
print('avisos', AVISOS)
print('cruces que tocan muros del plano', [(c['par'], c['u'], c['muros']) for c in CRUCES if c['muros']])
print('bandas', sum(c['banda'] for c in CRUCES), 'de', len(CRUCES), '· largos cruz', sorted({c['L'] for c in CRUCES}))
for x in lineas:
    print(f"{x['id']:>4} w {x['w_aci']:5.2f} @{x['a']} (máx {x['a_max']} por {x['manda']}) real {x['a_real']} n {x['n_palos']} P {x['P_max_kgf']} R {x['R_max_kgf']} ({x['R_k']}) "
          f"dc {x['dc']} flecha {x['flecha_mm']} uni {x['uniones']} diag {x['diagonales']} cruces {x['cruces']}")
