# -*- coding: utf-8 -*-
"""Escribe suples.js (lo leen losa.html y 3d.html): los suples superiores de la losa colaborante.

Del ingeniero (lámina «Suples para losa colaborante», rev. 3, 03-11-2026, y sus mensajes del mismo día):
- cada marca «SS n» de la planta dice qué suple lleva esa viga en ese tramo (suples_ingeniero.json);
- la tabla da el diámetro y el largo: a (tramo de arriba) y L = a + 30, con dos patas de 10 y dos pies de 5 hacia adentro;
- 2 suples por cada valle de la placa, separados entre 5 y 10 cm (la lámina: «5 cm como mínimo»);
- recubrimiento de 2,5 cm arriba y abajo: un separador de 2,5 cm bajo cada pie, y la barra de arriba queda a 2,5 cm de la cara de
  la losa de 15 (la lámina todavía dice 14,35; el ingeniero corrigió a 15, que deja el canal de contención en los bordes).

Supuestos de este modelo (el plano no los acota):
- cada suple va centrado sobre el eje de su viga (las cotas de la planta son esquemáticas: casi todas miden lo mismo);
- el tramo de la marca va entre las vigas perpendiculares que llegan a la viga o la cruzan, y lleva suples en todos sus valles;
- los valles son los de los pernos Nelson de esa viga (losa.js: uno por valle); los 2 suples van a ±3,5 cm del centro del valle
  (7 cm entre ellos), uno a cada lado del perno.

Uso (desde la raíz): python3 fuente/losa/generar_suples_js.py
"""
import json, math, os, re

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, '..', '..')
SEP = 7.0          # cm entre los dos suples de un valle (el ingeniero: 5 a 10)
SEPARADOR = 2.5    # cm bajo los pies
RECUB = 2.5        # cm sobre la barra de arriba
KG_M = {8: 0.395, 10: 0.617, 12: 0.888, 16: 1.578}
HOLGURA_PILAR = 2.0


def leer_js(nombre, var):
    s = open(os.path.join(RAIZ, nombre)).read()
    return json.loads(s[s.index('{'):s.rindex('}') + 1]) if var else None


def dentro(p, poly):
    x, y = p; c = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[i - 1]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def main():
    SI = json.load(open(os.path.join(AQUI, 'suples_ingeniero.json')))
    L = leer_js('losa.js', 'DATA_LOSA')
    E = json.loads(re.sub(r'^const DATA_ESTRUCTURA = |;\s*$', '', open(os.path.join(RAIZ, 'estructura.js')).read().strip()))
    vigas = {m['id']: m for m in E['miembros'] if m['c'] == 'viga' and 'entrepiso' in (m.get('d') or '')}
    z_viga, esp = L['z_viga'], L['espesor']
    z_pie = z_viga + SEPARADOR              # cara inferior de los pies
    z_tope = z_viga + esp - RECUB           # cara superior de la barra de arriba
    pata = SI['forma']['pata']; pie = SI['forma']['pie']
    if abs((z_tope - z_pie) - pata) > 0.05:
        raise SystemExit(f'la pata ({pata}) no calza con 15 − 2,5 − 2,5 = {z_tope - z_pie}')

    marcas, avisos = [], []
    for m in SI['marcas']:
        t = SI['tabla'][m['tipo']]; d, a = t['d'], t['a']
        en_x = m['tramo_en'] == 'x'          # la viga corre en x: el suple corre en y (NS)
        w = m['y'] if en_x else m['x']         # eje de la viga
        u0, u1 = m['tramo']
        piezas = set(m['vigas_tramo'])
        # valles: los pernos de las piezas de la viga dentro del tramo (el perno va al centro del valle)
        valles = sorted({round(p['x'] if en_x else p['y'], 1) for p in L['pernos']
                         if p['viga'] in piezas and u0 - 1 <= (p['x'] if en_x else p['y']) <= u1 + 1})
        # dos pernos a menos de 12 cm son el mismo valle visto desde dos planchas (junta a tope): queda uno
        uv = []
        for v in valles:
            if uv and v - uv[-1] < 12:
                uv[-1] = round((uv[-1] + v) / 2, 1)
            else:
                uv.append(v)
        if not uv:
            avisos.append(f"{m['tipo']} en {m['viga']} {m['tramo']}: la viga no tiene pernos (valles) en ese tramo")
        suples, fuera, cruzan = [], [], []
        for v in uv:
            for s in (-1, 1):
                u = round(v + s * SEP / 2, 1)
                w0, w1 = w - a / 2, w + a / 2
                pts = [(u, w0), (u, w1)] if not en_x else [(u, w0), (u, w1)]
                # en el marco de la app: (x, y)
                xy = [(q[0], q[1]) if en_x else (q[1], q[0]) for q in pts]
                xy = [(p[0], p[1]) for p in [(pt[0], pt[1]) for pt in xy]]
                # chequeos: los dos extremos dentro de la losa (fuera del hueco); si un extremo cae en un área con las
                # planchas en el otro sentido, el suple va igual (lo dibujó el ingeniero) pero ahí cruza los nervios: se avisa
                motivo, cruza = None, None
                for p in xy:
                    if not dentro(p, L['perimetro']) or dentro(p, L['hueco_escalera']):
                        motivo = 'sale de la losa'
                    else:
                        ar = [A for A in L['areas'] if dentro(p, A['poligono'])]
                        if ar and ar[0]['dir'] != ('NS' if en_x else 'EO'):
                            cruza = ar[0]['n']
                # pilares del nivel 2: el suple no puede pasar por su sección
                for P in L['pilares_n2']:
                    x0, y0, x1, y1 = P['seccion']
                    (ax, ay), (bx, by) = xy
                    if (min(ax, bx) - 0.8 < x1 + HOLGURA_PILAR and max(ax, bx) + 0.8 > x0 - HOLGURA_PILAR and
                            min(ay, by) - 0.8 < y1 + HOLGURA_PILAR and max(ay, by) + 0.8 > y0 - HOLGURA_PILAR):
                        motivo = f"choca con el pilar {P['id']}"
                if motivo:
                    fuera.append({'u': u, 'motivo': motivo})
                else:
                    suples.append(u)
                    if cruza:
                        cruzan.append({'u': u, 'area': cruza})
        if fuera:
            avisos.append(f"{m['tipo']} en {m['viga']}: {len(fuera)} suples fuera ({'; '.join(sorted({f['motivo'] for f in fuera}))})")
        if cruzan:
            avisos.append(f"{m['tipo']} en {m['viga']}: {len(cruzan)} suples con una punta en el área {', '.join(str(c) for c in sorted({c['area'] for c in cruzan}))}, donde las planchas van en el otro sentido (cruzan los nervios)")
        L_barra = a + 2 * pata + 2 * pie
        marcas.append({'tipo': m['tipo'], 'd': d, 'a': a, 'L': L_barra, 'viga': m['viga'], 'perfil': m['perfil'],
                       'sentido': 'NS' if en_x else 'EO', 'eje': round(w, 1), 'tramo': [round(u0, 1), round(u1, 1)],
                       'marca': [m['x'], m['y']], 'valles': len(uv), 'suples': suples, 'fuera': fuera, 'cruzan': cruzan,
                       'piezas': m['vigas_tramo']})

    # totales por tipo
    tipos = {}
    for k, t in SI['tabla'].items():
        ms = [m for m in marcas if m['tipo'] == k]
        n = sum(len(m['suples']) for m in ms)
        tipos[k] = {'d': t['d'], 'a': t['a'], 'L': t['L'], 'n': n, 'marcas': len(ms),
                    'm': round(n * t['L'] / 100, 2), 'kg': round(n * t['L'] / 100 * KG_M[t['d']], 1),
                    'vigas': sorted({m['viga'] for m in ms})}
    por_d = {}
    for k, t in tipos.items():
        q = por_d.setdefault(t['d'], {'n': 0, 'm': 0.0, 'kg': 0.0})
        q['n'] += t['n']; q['m'] = round(q['m'] + t['m'], 2); q['kg'] = round(q['kg'] + t['kg'], 1)
    total = {'n': sum(t['n'] for t in tipos.values()), 'm': round(sum(t['m'] for t in tipos.values()), 1),
             'kg': round(sum(t['kg'] for t in tipos.values()), 1)}

    # suples de dos marcas que se cruzan en planta (uno NS y otro EO): van a la misma altura, uno tiene que pasar sobre el otro
    def segs(m):
        for u in m['suples']:
            w0, w1 = m['eje'] - m['a'] / 2, m['eje'] + m['a'] / 2
            yield ((u, w0), (u, w1)) if m['sentido'] == 'NS' else ((w0, u), (w1, u))
    cruces = []
    for i, m in enumerate(marcas):
        for q in marcas[i + 1:]:
            if m['sentido'] == q['sentido']:
                continue
            n = 0; zona = []
            for (a0, a1) in segs(m):
                for (b0, b1) in segs(q):
                    ns, eo = ((a0, a1), (b0, b1)) if m['sentido'] == 'NS' else ((b0, b1), (a0, a1))
                    x = ns[0][0]; y = eo[0][1]
                    if min(eo[0][0], eo[1][0]) <= x <= max(eo[0][0], eo[1][0]) and min(ns[0][1], ns[1][1]) <= y <= max(ns[0][1], ns[1][1]):
                        n += 1; zona.append((x, y))
            if n:
                cruces.append({'a': m['tipo'], 'viga_a': m['viga'], 'b': q['tipo'], 'viga_b': q['viga'], 'n': n,
                               'centro': [round(sum(z[0] for z in zona) / n, 1), round(sum(z[1] for z in zona) / n, 1)]})

    # cruces con la malla: la cara de arriba de los suples y de la malla quedan a la misma altura (2,5 cm de la cara)
    malla = L.get('malla') or {}
    choque_malla = malla and abs(malla.get('recubrimiento', 0) - RECUB) < 0.05

    out = {
        'fuente': SI['fuente'] + ' · mensajes del ingeniero del 03-11-2026',
        'tabla': SI['tabla'], 'forma': SI['forma'],
        'sep': SEP, 'separador': SEPARADOR, 'recubrimiento': RECUB,
        'z': {'viga': z_viga, 'pie': z_pie, 'tope': z_tope, 'cara': z_viga + esp},
        'kg_m': {str(k): v for k, v in KG_M.items()},
        'marcas': marcas, 'tipos': tipos, 'por_diametro': {str(k): v for k, v in sorted(por_d.items())}, 'total': total,
        'choque_malla': bool(choque_malla), 'cruces': cruces, 'avisos': avisos,
        'supuestos': [
            'Cada suple va centrado sobre el eje de su viga: la planta no lo acota y sus cotas son esquemáticas (casi todas miden lo mismo).',
            'Cada marca vale para su tramo de viga, entre las vigas perpendiculares que llegan a ella o la cruzan, en todos sus valles.',
            f'Los 2 suples de cada valle van a {SEP:g} cm entre sí (el ingeniero: entre 5 y 10), uno a cada lado del perno Nelson del centro del valle.',
        ],
    }
    dst = os.path.join(RAIZ, 'suples.js')
    with open(dst, 'w') as f:
        f.write('// Generado por fuente/losa/generar_suples_js.py — no editar a mano.\n')
        f.write('const DATA_SUPLES = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
    print(f"{total['n']} suples, {total['m']} m, {total['kg']} kg en {len(marcas)} marcas")
    for k, t in tipos.items():
        print(f"  {k:5} ø{t['d']:2} a {t['a']:3} L {t['L']:3}: {t['n']:4} suples en {t['marcas']} marcas · {t['m']:7.1f} m · {t['kg']:6.1f} kg")
    for m in marcas:
        print(f"  {m['tipo']:5} {m['viga']:16} {m['sentido']} eje {m['eje']:7} tramo {m['tramo']} valles {m['valles']:3} suples {len(m['suples']):3} fuera {len(m['fuera'])} cruzan {len(m['cruzan'])}")
    for a in avisos:
        print('AVISO:', a)
    print('cara de arriba de suples y malla a la misma altura:', bool(choque_malla))
    for c in cruces:
        print(f"cruce: {c['a']} ({c['viga_a']}) × {c['b']} ({c['viga_b']}): {c['n']} cruces cerca de {c['centro']}")


if __name__ == '__main__':
    main()
