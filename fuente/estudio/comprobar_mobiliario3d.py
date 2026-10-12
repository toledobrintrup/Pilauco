#!/usr/bin/env python3
"""Autocomprobación de mobiliario3d.js contra los datos del estudio.

Lee estudio_estructura.js (DATA_ESTUDIO_EST.interior) y sitio.js (DATA_SITIO.estudio) y revisa, sin
Three.js, que el módulo interpreta bien cada pieza:
  1. cada 'tipo' de D.interior tiene constructor (C.<tipo> en el JS) y la lista TIPOS coincide;
  2. el rectángulo 'pts' es un rectángulo alineado a los ejes y cabe dentro de su recinto;
  3. ancho/fondo locales (con el intercambio cuando mira es E u O) y la rotación según 'mira' devuelven
     exactamente el rectángulo original (simulación de la caja envolvente de la pieza);
  4. sentido común del 'mira': los parlantes miran a la consola, la silla del productor queda detrás de la
     consola, los taburetes miran a la barra, las sillas a su mesa, los paneles y estantes pegan su espalda
     a un muro, la cabina pega su fondo al tabique y abre al norte, el espejo del lavamanos va al oriente;
  5. las lámparas cuelgan de un cielo más alto que su 'alto'.
Uso:  python3 -I fuente/estudio/comprobar_mobiliario3d.py   (desde la raíz del repo)
Sale con código 1 si algo falla.
"""
import json, math, os, re, sys

RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


def carga(nombre):
    s = open(os.path.join(RAIZ, nombre), encoding='utf-8').read()
    return json.loads(s[s.index('=') + 1:].strip().rstrip(';'))


D = carga('estudio_estructura.js')
E = carga('sitio.js')['estudio']
JS = open(os.path.join(RAIZ, 'mobiliario3d.js'), encoding='utf-8').read()

fallas, avisos = [], []
ok = lambda cond, msg: (None if cond else fallas.append(msg))

# ---------- 1. constructores ----------
constructores = set(re.findall(r'^\s*C\.(\w+)\s*=\s*\(g,\s*p\)\s*=>', JS, re.M))
tipos_lista = set(re.search(r"TIPOS:\s*\[([^\]]*)\]", JS).group(1).replace("'", '').replace(' ', '').split(','))
tipos_datos = {it['tipo'] for it in D['interior']}
ok(tipos_datos <= constructores, f'tipos sin constructor: {sorted(tipos_datos - constructores)}')
ok(tipos_lista == constructores, f'TIPOS no coincide con los constructores: {sorted(tipos_lista ^ constructores)}')
ok(re.search(r'const ROT = \{ S: 0, N: Math\.PI, E: Math\.PI / 2, O: -Math\.PI / 2 \}', JS) is not None, 'tabla ROT distinta de la convención (S 0, N π, E π/2, O −π/2)')

# ---------- marco: rotación local → app (x al oriente, y al sur) ----------
# local: x = ancho, z = fondo, frente en +z (= sur). rotation.y = θ: x' = x cosθ + z sinθ ; z' = −x sinθ + z cosθ
ROT = {'S': 0.0, 'N': math.pi, 'E': math.pi / 2, 'O': -math.pi / 2}


def local_a_app(mira, lx, lz):
    t = ROT[mira]
    return (round(lx * math.cos(t) + lz * math.sin(t), 6), round(-lx * math.sin(t) + lz * math.cos(t), 6))


FRENTE = {m: local_a_app(m, 0, 1) for m in ROT}          # hacia dónde cae el +z local
assert FRENTE == {'S': (0, 1), 'N': (0, -1), 'E': (1, 0), 'O': (-1, 0)}, FRENTE

recintos = {r['id']: r['pts'] for r in E['recintos']}


def caja_pts(pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def dentro(a, b, tol=0.6):
    return a[0] >= b[0] - tol and a[1] >= b[1] - tol and a[2] <= b[2] + tol and a[3] <= b[3] + tol


piezas = {it['id']: it for it in D['interior']}
info = {}
for it in D['interior']:
    pts, mira = it['pts'], it['mira']
    r = caja_pts(pts)
    # 2. rectángulo alineado a los ejes, con 4 esquinas distintas
    esquinas = {(round(p[0], 1), round(p[1], 1)) for p in pts}
    ok(len(pts) == 4 and len(esquinas) == 4 and all(round(p[0], 1) in (round(r[0], 1), round(r[2], 1)) and round(p[1], 1) in (round(r[1], 1), round(r[3], 1)) for p in pts),
       f'{it["id"]}: pts no es un rectángulo alineado a los ejes')
    ok(it['recinto'] in recintos and dentro(r, caja_pts(recintos[it['recinto']])), f'{it["id"]}: se sale de su recinto {it["recinto"]}')
    ok(mira in ROT, f'{it["id"]}: mira {mira!r} desconocido')
    ex, ey = r[2] - r[0], r[3] - r[1]
    lateral = mira in ('E', 'O')
    w, d = (ey, ex) if lateral else (ex, ey)
    cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
    # 3. caja local [−w/2, w/2] × [−d/2, d/2] girada y trasladada = rectángulo original
    esq = [local_a_app(mira, sx * w / 2, sz * d / 2) for sx in (-1, 1) for sz in (-1, 1)]
    sim = (min(cx + e[0] for e in esq), min(cy + e[1] for e in esq), max(cx + e[0] for e in esq), max(cy + e[1] for e in esq))
    ok(all(abs(a - b) < 1e-6 for a, b in zip(sim, r)), f'{it["id"]}: la caja simulada {sim} no coincide con el rectángulo {r}')
    f = FRENTE[mira]
    espalda = (cx - f[0] * d / 2, cy - f[1] * d / 2)       # centro de la cara trasera (−z local)
    frente = (cx + f[0] * d / 2, cy + f[1] * d / 2)
    info[it['id']] = dict(it=it, r=r, w=w, d=d, c=(cx, cy), f=f, espalda=espalda, frente=frente)


def hacia(a, b):
    """vector unitario de a hacia b (centros)"""
    dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1
    return dx / L, dy / L


def mira_a(idp, idq, nombre_q=None):
    p, q = info[idp], info[idq]
    v = hacia(p['c'], q['c'])
    ok(v[0] * p['f'][0] + v[1] * p['f'][1] > 0.5, f'{idp}: mira {p["it"]["mira"]} pero {nombre_q or idq} queda hacia ({v[0]:.1f}, {v[1]:.1f})')


def pegado(idp, linea, eje, tol=0.6, que='espalda'):
    """la cara 'que' de la pieza está sobre la recta x=linea (eje 0) o y=linea (eje 1)"""
    p = info[idp]; v = p[que][eje]
    if abs(v - linea) > tol:
        avisos.append(f'{idp}: su {que} queda a {abs(v - linea):.1f} cm de la línea {"xy"[eje]}={linea}')


# ---------- 4. sentido común del 'mira' ----------
est, caf, ban, bod, esc = (caja_pts(recintos[k]) for k in ('estudio', 'cafeteria', 'bano', 'bodega', 'escalera'))
for pid, it in piezas.items():
    t = it['tipo']
    if t == 'parlante': mira_a(pid, 'consola', 'la consola')
    if t == 'silla_oficina':
        mira_a(pid, 'consola', 'la consola')
        c, s = info['consola'], info[pid]
        v = hacia(c['c'], s['c']); ok(v[0] * c['f'][0] + v[1] * c['f'][1] < -0.5, 'consola: la silla no queda detrás (los monitores irían al lado del productor)')
    if t in ('sofa', 'rack'): mira_a(pid, 'consola', 'la consola')
    if t == 'taburete': mira_a(pid, 'barra', 'la barra')
    if t == 'silla':
        mesa = min((m for m in piezas if piezas[m]['tipo'] == 'mesa'), key=lambda m: math.dist(info[m]['c'], info[pid]['c']))
        mira_a(pid, mesa, 'su mesa')
    if t == 'panel_acustico':
        ok(info[pid]['d'] == 6 and info[pid]['w'] == 100, f'{pid}: el panel no es de 6 × 100 en planta ({info[pid]["d"]} × {info[pid]["w"]})')
        ok(it['alto'] - 120 >= 0, f'{pid}: alto {it["alto"]} < 120')
        lado = est[0] if it['mira'] == 'E' else est[2]
        ok(abs(info[pid]['espalda'][0] - lado) < 0.6, f'{pid}: la espalda del panel no queda en el muro x={lado}')
    if t == 'cabina':
        ok(info[pid]['f'] == (0, -1), 'cabina: el frente vidriado no da al norte (cafetería)')
        pegado(pid, caf[3], 1)                               # fondo contra el tabique B (y = 635,5)
        ok(info[pid]['w'] >= 239 and info[pid]['d'] >= 219, f'cabina: menor que 2,40 × 2,20 ({info[pid]["w"]} × {info[pid]["d"]})')
    if t == 'barra':
        pegado(pid, esc[0] - E['muro'], 0)                   # espalda contra el muro de la escalera (x = 4157,9)
        for tb in (q for q in piezas if piezas[q]['tipo'] == 'taburete'):
            v = hacia(info[pid]['c'], info[tb]['c']); ok(v[0] * info[pid]['f'][0] > 0.5, f'barra: {tb} no queda por el lado del cliente')
    if t == 'wc': pegado(pid, ban[3], 1)                      # estanque contra el tabique baño/bodega
    if t == 'lavamanos':
        ok(info[pid]['f'] == (-1, 0), 'lavamanos: el espejo no queda en la cara oriente'); pegado(pid, ban[2], 0)
    if t == 'estante':
        rb = bod
        lado = {'O': ('x', rb[2]), 'E': ('x', rb[0]), 'N': ('y', rb[3]), 'S': ('y', rb[1])}[it['mira']]
        pegado(pid, lado[1], 0 if lado[0] == 'x' else 1)
    if t == 'alfombra':
        ok(dentro(info['consola']['r'], info[pid]['r']), 'alfombra: la consola no queda sobre ella')
    if t == 'lampara':
        c = E['cielo']; y = info[pid]['c'][1]
        z_cielo = c['z_norte'] + (c['z_sur'] - c['z_norte']) * (y - c['y_norte']) / (c['y_sur'] - c['y_norte'])
        h_cielo = z_cielo - D['z_piso']
        ok(h_cielo > it['alto'] + 20, f'{pid}: el cielo ({h_cielo:.1f}) no deja cable sobre la pantalla ({it["alto"]})')
        info[pid]['h_cielo'] = h_cielo

# ---------- resumen ----------
print(f'piezas: {len(piezas)} · tipos en datos: {len(tipos_datos)} · constructores: {len(constructores)}')
for pid, p in info.items():
    it = p['it']
    extra = f' · cielo a {p["h_cielo"]:.1f} sobre el piso' if 'h_cielo' in p else ''
    print(f'  {pid:14} {it["tipo"]:15} mira {it["mira"]}  {p["w"]/100:.2f} × {p["d"]/100:.2f} m · alto {it["alto"]/100:.2f}  centro ({p["c"][0]:.1f}, {p["c"][1]:.1f}){extra}')
for a in avisos: print('aviso:', a)
for f in fallas: print('FALLA:', f)
print('resultado:', 'OK' if not fallas else f'{len(fallas)} fallas')
sys.exit(1 if fallas else 0)
