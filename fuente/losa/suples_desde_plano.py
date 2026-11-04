# -*- coding: utf-8 -*-
"""Saca de la lámina de suples del ingeniero ("Suples para losa colaborante", planta 1:50, rev. 3, 03-11-2026) dónde
va cada suple y la tabla de suples, y lo deja en suples_ingeniero.json, en cm en el marco de la app.

En la planta cada marca es un rótulo «SS n» con una línea de cota a su lado ([, del largo dibujado del suple) que
cruza la viga sobre la que va. La marca dice qué tipo de suple lleva esa viga; el largo, el diámetro y la forma salen
de la tabla «Armaduras de suples superiores en losa» (a, L = a + 30, patas de 10 y pies de 5). La planta se calibra
con las burbujas de los ejes, igual que en pernos_desde_plano.py (mínimos cuadrados en x y en y, descartando las que
quedan a más de 1 cm del ajuste).

El PDF no va en el repositorio: la viñeta trae datos personales. Este script no copia nada de la viñeta.

Uso (desde fuente/losa): python3 suples_desde_plano.py "ruta/al/suples.pdf" suples_ingeniero.json
"""
import sys, json, re, math, os
import fitz   # PyMuPDF

from pernos_desde_plano import EJES_X, EJES_Y, D_BURBUJA, ajuste

# tabla de la lámina (también se lee del PDF y se compara)
TABLA = {'ss1': (16, 130), 'ss2': (16, 140), 'ss3': (12, 120), 'ss4': (16, 120), 'ss5': (16, 270),
         'ss6': (12, 100), 'ss7': (16, 120), 'ss8': (10, 100), 'ss9': (12, 120), 'ss10': (10, 100)}
X_TABLA = 2300.0      # pt: a la derecha de esto están los detalles, la tabla y la viñeta


def leer_tabla(pag):
    """filas «ssN ø a L» de la tabla de la lámina"""
    pal = [w for w in pag.get_text('words') if w[0] > X_TABLA]
    filas = {}
    for w in pal:
        if re.fullmatch(r'ss\d+', w[4]):
            yc = (w[1] + w[3]) / 2
            nums = sorted([v for v in pal if v[4].isdigit() and abs((v[1] + v[3]) / 2 - yc) < 3 and v[0] > w[2]], key=lambda v: v[0])
            filas[w[4]] = [int(v[4]) for v in nums]
    return filas


def main(pdf, salida):
    pag = fitz.open(pdf)[0]
    # calibración con las burbujas de los ejes (las de las filas y columnas de afuera)
    circulos = [g['rect'] for g in pag.get_drawings() if len(g['items']) == 4 and all(it[0] == 'c' for it in g['items'])]
    burbujas = [r for r in circulos if abs(r.width - D_BURBUJA) <= 0.3 and r.x0 < X_TABLA]
    palabras = pag.get_text('words')
    ys = sorted((r.y0 + r.y1) / 2 for r in burbujas); xs = sorted((r.x0 + r.x1) / 2 for r in burbujas)
    px, py = [], []
    for r in burbujas:
        t = ' '.join(w[4] for w in palabras if fitz.Rect(w[:4]).intersects(r) and fitz.Rect(w[:4]).width < r.width).strip()
        cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
        if t in EJES_X and (cy < ys[0] + 5 or cy > ys[-1] - 5):
            px.append((cx, EJES_X[t], t))
        elif t in EJES_Y and (cx < xs[0] + 5 or cx > xs[-1] - 5):
            py.append((cy, EJES_Y[t], t))
    mx, bx, rx, fx = ajuste(px); my, by, ry, fy = ajuste(py)
    if fx or fy:
        print('burbujas descartadas por quedar fuera de su eje:', ', '.join(fx + fy))
    print(f'calibración: x {mx:.5f}·pt{bx:+.1f} ({len(px) - len(fx)} burbujas, residuo {rx:.1f} cm) · '
          f'y {my:.5f}·pt{by:+.1f} ({len(py) - len(fy)} burbujas, residuo {ry:.1f} cm)')
    cm = lambda x, y: (mx * x + bx, my * y + by)

    # tabla de la lámina contra la copiada arriba
    tabla_pdf = leer_tabla(pag)
    for k, (d, a) in TABLA.items():
        f = tabla_pdf.get(k)
        if not f or f[:3] != [d, a, a + 30]:
            raise SystemExit(f'la tabla de la lámina no calza en {k}: {f} (esperado {d}, {a}, {a + 30})')
    print('tabla de la lámina: 10 suples, igual a la copiada')

    # vigas de entrepiso (marco de la app)
    raiz = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'estructura.js')
    E = json.loads(re.sub(r'^const DATA_ESTRUCTURA = |;\s*$', '', open(raiz).read().strip()))
    vigas = [m for m in E['miembros'] if m['c'] == 'viga' and 'entrepiso' in (m.get('d') or '')]

    # líneas sueltas largas (las cotas de los suples)
    segs = []
    for g in pag.get_drawings():
        for it in g['items']:
            if it[0] == 'l':
                a, b = it[1], it[2]
                L = math.hypot(b.x - a.x, b.y - a.y)
                if 40 <= L <= 200 and (abs(a.x - b.x) < 0.2 or abs(a.y - b.y) < 0.2):
                    segs.append((a.x, a.y, b.x, b.y, L))

    marcas = []
    for i, w in enumerate(palabras):
        if w[4] != 'SS' or w[0] > X_TABLA:
            continue
        r = fitz.Rect(w[:4])
        vertical = r.height > r.width
        num = [v for v in palabras if v[4].isdigit() and v[0] < X_TABLA and
               (abs(v[0] - w[0]) < 1.5 and (0 < v[1] - w[3] < 15 or 0 < w[1] - v[3] < 15) if vertical else abs(v[1] - w[1]) < 1.5 and 0 < v[0] - w[2] < 15)]
        if not num:
            raise SystemExit(f'rótulo SS sin número en {w[:4]}')
        n = int(num[0][4]); tipo = f'ss{n}'
        # el rótulo ocupa «SS n»; la cota es paralela, a menos de 6 pt y lo acompaña a lo largo
        c0 = (w[0] + w[2]) / 2, (w[1] + w[3]) / 2
        mejores = []
        for s in segs:
            if vertical and abs(s[0] - s[2]) < 0.2 and abs(s[0] - c0[0]) < 6 and min(s[1], s[3]) - 5 < c0[1] < max(s[1], s[3]) + 5:
                mejores.append((abs(s[0] - c0[0]), s))
            if not vertical and abs(s[1] - s[3]) < 0.2 and abs(s[1] - c0[1]) < 6 and min(s[0], s[2]) - 5 < c0[0] < max(s[0], s[2]) + 5:
                mejores.append((abs(s[1] - c0[1]), s))
        if not mejores:
            raise SystemExit(f'{tipo} en {c0}: sin línea de cota')
        s = min(mejores)[1]
        p0, p1 = cm(s[0], s[1]), cm(s[2], s[3])
        # viga que cruza la cota (perpendicular a ella)
        cruces = []
        for v in vigas:
            (ax, ay), (bx_, by_) = v['a'][:2], v['b'][:2]
            if vertical and abs(ay - by_) < 1 and min(ax, bx_) - 1 <= p0[0] <= max(ax, bx_) + 1 and min(p0[1], p1[1]) <= ay <= max(p0[1], p1[1]):
                cruces.append((v, (p0[0], ay)))
            if not vertical and abs(ax - bx_) < 1 and min(ay, by_) - 1 <= p0[1] <= max(ay, by_) + 1 and min(p0[0], p1[0]) <= ax <= max(p0[0], p1[0]):
                cruces.append((v, (ax, p0[1])))
        if not cruces:
            raise SystemExit(f'{tipo} en {[round(c, 1) for c in p0]}: no cruza ninguna viga')
        # si toca dos (la cota de ss5 llega justo a la viga del borde), manda la más cercana a su centro
        pm = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
        cruces.sort(key=lambda c: math.hypot(c[1][0] - pm[0], c[1][1] - pm[1]))
        if len(cruces) > 1:
            print(f'  {tipo}: la cota toca también ' + ', '.join(c[0]['id'] for c in cruces[1:]) + f'; va sobre {cruces[0][0]["id"]}')
        v, (xc, yc) = cruces[0]
        d, a = TABLA[tipo]
        largo = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        # el tramo donde va el suple: la línea de vigas de la marca (las piezas seguidas del mismo eje, que en
        # estructura.js se cortan en cada pilar o nudo) entre las vigas perpendiculares que llegan a ella o la cruzan
        en_x = abs(v['a'][1] - v['b'][1]) < 1          # la viga corre en x (la marca es NS)
        w_v = v['a'][1] if en_x else v['a'][0]
        k_u, k_w = (0, 1) if en_x else (1, 0)
        linea = [q for q in vigas if abs(q['a'][k_w] - w_v) < 1 and abs(q['b'][k_w] - w_v) < 1]
        uc = xc if en_x else yc
        # piezas seguidas que contienen la marca
        tramos_l = sorted([sorted((q['a'][k_u], q['b'][k_u])) + [q['id']] for q in linea])
        u0, u1 = next((t[0], t[1]) for t in tramos_l if t[0] - 0.5 <= uc <= t[1] + 0.5)
        cambio = True
        while cambio:
            cambio = False
            for t in tramos_l:
                if abs(t[1] - u0) < 2 and t[0] < u0: u0 = t[0]; cambio = True
                if abs(t[0] - u1) < 2 and t[1] > u1: u1 = t[1]; cambio = True
        cortes = {u0, u1}
        for q in vigas:
            (qa, qb) = q['a'][:2], q['b'][:2]
            # las vigas que llegan a la línea terminan en la cara del pilar (7,5 cm antes del eje): 12 cm de tolerancia
            if abs(qa[k_u] - qb[k_u]) < 1 and u0 < qa[k_u] < u1 and min(qa[k_w], qb[k_w]) - 12 <= w_v <= max(qa[k_w], qb[k_w]) + 12:
                cortes.add(qa[k_u])
        cortes = sorted(cortes)
        tramo = next([c0_, c1_] for c0_, c1_ in zip(cortes, cortes[1:]) if c0_ <= uc <= c1_)
        piezas = [t[2] for t in tramos_l if t[1] > tramo[0] + 0.5 and t[0] < tramo[1] - 0.5]
        k0, k1 = (p0[1], p1[1]) if vertical else (p0[0], p1[0])
        kc = yc if vertical else xc
        marcas.append({'tipo': tipo, 'viga': v['id'], 'perfil': v['p'], 'x': round(xc, 1), 'y': round(yc, 1),
                       'sentido': 'NS' if vertical else 'EO',
                       'cota': [[round(c, 1) for c in p0], [round(c, 1) for c in p1]], 'largo_dibujado': round(largo, 1),
                       'tramo': [round(t, 1) for t in tramo], 'tramo_en': 'x' if en_x else 'y', 'vigas_tramo': piezas,
                       'a': a, 'lado_menor': round(min(abs(kc - k0), abs(kc - k1)), 1), 'lado_mayor': round(max(abs(kc - k0), abs(kc - k1)), 1)})
    marcas.sort(key=lambda m: (int(m['tipo'][2:]), m['viga']))
    # dos marcas en el mismo tramo de una viga, o de distinto tipo en la misma viga: avisar
    for m in marcas:
        for q in marcas:
            if q is not m and q['viga'] == m['viga'] and q['tramo'] == m['tramo']:
                raise SystemExit(f"{m['viga']}: dos marcas en el mismo tramo {m['tramo']}")
            if q is not m and q['viga'] == m['viga'] and q['tipo'] != m['tipo']:
                print(f"  ojo: {m['viga']} lleva {m['tipo']} y {q['tipo']} en tramos distintos")
    out = {'fuente': 'Lámina del ingeniero «Suples para losa colaborante», planta 1:50, rev. 3 (03-11-2026)',
           'calibracion': {'x': [round(mx, 5), round(bx, 2), round(rx, 2)], 'y': [round(my, 5), round(by, 2), round(ry, 2)],
                           'nota': 'cm = a·pt + b; el tercer valor es el mayor residuo en los ejes (cm)'},
           'tabla': {k: {'d': d, 'a': a, 'L': a + 30} for k, (d, a) in TABLA.items()},
           'forma': {'pata': 10, 'pie': 5, 'nota': 'L = a + 30: dos patas de 10 y dos pies de 5 hacia adentro (detalle de la lámina)'},
           'marcas': marcas}
    json.dump(out, open(salida, 'w'), ensure_ascii=False, indent=1)
    print(f'{len(marcas)} marcas:')
    for m in marcas:
        print(f"  {m['tipo']:5} {m['viga']:14} {m['perfil']:8} {m['sentido']} tramo {m['tramo_en']} {m['tramo']} cota {m['largo_dibujado']:6.1f} (a {m['a']}) lados {m['lado_menor']}/{m['lado_mayor']}")


if __name__ == '__main__':
    main(*sys.argv[1:3])
