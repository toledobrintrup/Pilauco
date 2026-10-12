# -*- coding: utf-8 -*-
"""Propuesta de estructura del estudio con búnker, adaptada del proyecto del ingeniero (láminas 03, 04 y 05 de
abril de 2026, leídas de sus vectores: fuente/estudio/datos/) a la planta de Gabriel (medidas interiores:
cafetería 6,00 x 10,05, estudio 9,00 x 7,30, baño 2,50 x 4,10, bodega 2,50 x 4,65; tabiques de 25; edificio de
10,55 x 15,75 por fuera; búnker bajo la cafetería, al norte; techo al 3,5 % subiendo al sur como la casa).
Genera estudio_estructura.js (DATA_ESTUDIO_EST): acero (mismo formato que estructura.js), hormigón del búnker,
fundaciones, ejes, vanos (ventanas y puertas propuestas), esquema interior, cambios y preguntas.

    python3 generar_estudio_estructura.py ../sitio/estudio.json ../sitio/sitio.json ../../estudio_estructura.js

Marco local del estudio en cm: x al oriente desde la cara exterior poniente, y al sur desde la cara exterior
norte, z desde el piso terminado del estudio (NPOG 0,00 del ingeniero). Se convierte al marco de la app con el
origen del estudio (sitio.json) y su nivel de piso. No es un cálculo: es el sistema del ingeniero acomodado.
"""
import json, sys, math

PERFILES = {
    'CUAD 150x150x5': dict(forma='tubo_rect', h=15, b=15, t=0.5),
    'CUAD 150x150x4': dict(forma='tubo_rect', h=15, b=15, t=0.4),
    'RECT 150x100x3': dict(forma='tubo_rect', h=15, b=10, t=0.3),
    'RECT 200x150x3': dict(forma='tubo_rect', h=20, b=15, t=0.3),
    'RECT 200x150x5': dict(forma='tubo_rect', h=20, b=15, t=0.5),
    'CUAD 100x100x3': dict(forma='tubo_rect', h=10, b=10, t=0.3),
    'C 150x50x3':     dict(forma='C', h=15, b=5, t=0.3),
    'CA 100x50x15x3': dict(forma='CA', h=10, b=5, c=1.5, t=0.3),
    'FE 16':          dict(forma='barra', d=1.6),
    'FE 10':          dict(forma='barra', d=1.0),
}
PESO = {'C 150x50x3': 5.65, 'CUAD 100x100x3': 8.94, 'CUAD 150x150x4': 18.0, 'CUAD 150x150x5': 22.2, 'FE 16': 1.58,
        'RECT 150x100x3': 11.3, 'RECT 200x150x3': 16.0, 'RECT 200x150x5': 26.1, 'CA 100x50x15x3': 4.95, 'FE 10': 0.62}

h2 = lambda p: PERFILES[p]['h'] / 2   # medio alto del perfil: las líneas de los miembros van por el EJE del perfil (como en estructura.js)

# ---------- lo que dicen las láminas (dato) ----------
H_PILAR = 400.0        # cara inferior de la viga inclinada en el lado bajo (lámina 04: +400 en F1, +447 en A1)
PEND = 0.035           # pendiente: rotulada 3,5 % (dibujada 4,5 %); Gabriel pide la de la casa, 3,5 %
ALERO_NS = 80.0        # aleros del ingeniero: norte y sur (1.186 = 1.025 + 80 + 80); se reemplazan por los de estudio.json si vienen (Gabriel: como la casa)
ALERO_EO = 52.0        # aleros del ingeniero: oriente y poniente (cota 52)
PASO_COST = 61.0       # costaneras CA 100x50x15x3 cada 61
PASO_PUNTAL = 171.0    # puntales RECT 150x100x3 cada 171 desde donde el cordón se separa de la viga
GAP_PUNTAL = 7.0       # el primer puntal del original tiene 7 cm
Z_CORDON = (400.0, 410.0)   # cordón RECT 150x100x3 de +400 a +410 (lámina 04)
BUNKER_LOSA = 20.0     # losa de techo del búnker
BUNKER_MURO = 25.0     # muros MHA e=25
BUNKER_RADIER = 20.0   # piso −292 a −312 en el original
BUNKER_FUND = 30.0     # losa de fundación de 30 bajo todo el búnker (−312 a −342), 37,5 más ancha que los muros
BUNKER_FUND_MARGEN = 37.5
RADIER = 10.0          # radier de 10 fuera del búnker (lámina 04)
# ---------- Gabriel ----------
MURO = 25.0
BUNKER_H = 280.0       # altura libre (el original 272)
ZAPATA = (100.0, 100.0, 100.0)   # zapatas aisladas 1 x 1 x 1 bajo los pilares fuera del búnker, con vigas de fundación (Gabriel, a confirmar)
VIGA_FUND = (25.0, 50.0)
H_VENTANA = 300.0      # ventanas hasta 3,00 (Gabriel: 4,00 puede ser mucho; se ve estéticamente)

def r1(v): return round(float(v), 1)

def main(estudio_json, sitio_json, salida):
    E = json.load(open(estudio_json)); S = json.load(open(sitio_json))
    global ALERO_NS, ALERO_EO
    _al = E.get('alturas', {})   # aleros de estudio.json (Gabriel: como la casa), medidos desde la cara exterior → aquí van desde el eje del pilar
    if _al.get('alero_ns_cm'): ALERO_NS = float(_al['alero_ns_cm']) + MURO / 2
    if _al.get('alero_eo_cm'): ALERO_EO = float(_al['alero_eo_cm']) + MURO / 2
    ox, oy = S['estudio_origen']; z0 = E['nivel_piso']['z_cm']
    W, L = E['exterior']['ancho'], E['exterior']['largo']           # 1055 x 1575
    rec = {r['id']: r['pts'] for r in E['recintos']}
    # ---------- ejes: x 1-5 (el 4 sobre el tabique estudio | baño-bodega), y A-E ----------
    x_tab = (rec['estudio'][1][0] + rec['bano'][0][0]) / 2            # 767,5
    xA = [MURO / 2, MURO / 2 + (x_tab - MURO / 2) / 3, MURO / 2 + 2 * (x_tab - MURO / 2) / 3, x_tab, W - MURO / 2]
    xN = ['1', '2', '3', '4', '5']
    yB = (rec['cafeteria'][5][1] + rec['estudio'][0][1]) / 2          # 637,5: tabique cafetería/estudio = muro sur del búnker
    yC = (rec['bano'][2][1] + rec['bodega'][0][1]) / 2                # 1072,5: tabique baño/bodega
    yA = [MURO / 2, MURO / 2 + 200, yB, yC, L - MURO / 2 - 200, L - MURO / 2]   # A, A2, B, C, D, E
    yN = ['A', 'A2', 'B', 'C', 'D', 'E']
    ejes = dict(x={n: r1(v) for n, v in zip(xN, xA)}, y={n: r1(v) for n, v in zip(yN, yA)},
                nota='Ejes 1-5 de poniente a oriente (el 4 sobre el tabique estudio/baño-bodega) y A-E de norte a sur: B sobre el tabique '
                     'cafetería/estudio (= muro sur del búnker), C sobre el tabique baño/bodega; A2 y D a 2,00 m de las fachadas norte y sur, '
                     'para que las cruces queden en tramos de 2 m como las del original (2,05 y 1,82).')
    def ap(x, y, z): return [r1(ox + x), r1(oy + y), r1(z0 + z)]
    def z_viga(y): return H_PILAR + PEND * (y - yA[0])               # cara inferior de la viga inclinada (cota del ingeniero)
    # Convención: cada miembro se dibuja centrado en su línea, así que las cotas del ingeniero (caras inferiores) llevan sumado medio perfil.
    Z_CORDON_EJE = (Z_CORDON[0] + Z_CORDON[1]) / 2                     # 405: eje del cordón y de las vigas E-O (de +400 a +410)
    def z_tope(y): return z_viga(y) - 5                                # eje de una viga E-O CUAD 100 pegada bajo la viga inclinada
    M = []
    def m(id_, c, p, a, b, d, **k): M.append(dict(id=id_, c=c, p=p, a=ap(*a), b=ap(*b), d=d, **k))
    lateral = lambda xn: xn in ('1', '5')

    # ---------- pilares: llegan a la cara inferior de la viga inclinada (lámina 04) ----------
    for yn, y in (('A', yA[0]), ('B', yB), ('E', yA[5])):
        for xn, x in zip(xN, xA):
            pm = 'PM1' if xn in ('2', '3') else 'PM2'
            perfil = 'CUAD 150x150x5' if pm == 'PM1' else 'CUAD 150x150x4'
            apoyo = {'A': 'sobre el muro norte del búnker', 'B': 'sobre el muro sur del búnker', 'E': 'sobre zapata aislada 1 x 1 x 1'}[yn]
            m(f'P-{xn}{yn}', 'pilar', perfil, (x, y, 0), (x, y, z_viga(y)), f'{pm} eje {xn} x {yn}, {apoyo}; llega a la viga inclinada (+{z_viga(y):.0f})', alma='Y')
    for yn in ('A2', 'C', 'D'):
        y = yA[yN.index(yn)]
        for xn, x in (('1', xA[0]), ('5', xA[4])):
            apoyo = 'sobre el muro del búnker' if y < yB else 'sobre zapata aislada'
            m(f'P-{xn}{yn}', 'pilar', 'RECT 150x100x3', (x, y, 0), (x, y, z_viga(y)), f'PM3 eje {xn} x {yn}, pilar intermedio de la fachada lateral, {apoyo}', alma='Y')
    m('P-4C', 'pilar', 'RECT 150x100x3', (xA[3], yC, 0), (xA[3], yC, z_viga(yC)), 'PM3 eje 4 x C, en el encuentro de los tabiques estudio/baño/bodega (recibe la cruz E-O del eje C)', alma='Y')
    # ---------- vigas E-O CUAD 100x100x3: de +400 a +410 en A y C (4-5); en B y E pegadas bajo la viga inclinada, para que el vidrio llegue al cielo ----------
    for yn, y, tramos, alta in (('A', yA[0], range(4), False), ('B', yB, range(4), True), ('E', yA[5], range(4), True), ('C', yC, [3], False)):
        for i in tramos:
            zv = z_tope(y) if alta else Z_CORDON_EJE
            m(f'VT-{yn}-{xN[i]}{xN[i+1]}', 'viga', 'CUAD 100x100x3', (xA[i], y, zv), (xA[i + 1], y, zv), (f'viga E-O bajo la viga inclinada (+{zv-5:.0f}/+{zv+5:.0f}) entre pilares {xN[i]} y {xN[i+1]} del eje {yn}: va arriba para que el vidrio llegue al cielo (propuesta)' if alta else f'viga E-O a +4,00/+4,10 entre pilares {xN[i]} y {xN[i+1]} del eje {yn}'))
    # ---------- marcos N-S: cordón RECT 150x100x3 + viga inclinada + puntales (como 1.b y 1.c) ----------
    y_ini, y_fin = yA[0] - ALERO_NS, yA[5] + ALERO_NS
    for xn, x in zip(xN, xA):
        if not lateral(xn):
            for (ya, yb) in ((yA[0], yB), (yB, yA[5])):
                m(f'VC-{xn}-{int(ya)}', 'viga', 'RECT 150x100x3', (x, ya, Z_CORDON_EJE), (x, yb, Z_CORDON_EJE), f'cordón horizontal RECT 150x100x3 de +4,00 a +4,10 (acostado), eje {xn}, {ya:.0f}..{yb:.0f} (como 1.b y 1.c del original)')
        perfil = 'RECT 200x150x3' if lateral(xn) else 'RECT 200x150x5'
        m(f'VI-{xn}', 'cabio', perfil, (x, y_ini, z_viga(y_ini) + h2(perfil)), (x, y_fin, z_viga(y_fin) + h2(perfil)), f'viga inclinada de techo, eje {xn}, 3,5 % subiendo al sur, aleros de 80; cara inferior a +{z_viga(yA[0]):.0f} en A')
        if not lateral(xn):
            for (ya, yb) in ((yA[0], yB), (yB, yA[5])):
                y = ya + PASO_PUNTAL
                while y < yb - 60:
                    gap = z_viga(y) - Z_CORDON[1]
                    if gap >= GAP_PUNTAL:
                        m(f'PT-{xn}-{int(y)}', 'puntal', 'RECT 150x100x3', (x, y, Z_CORDON[1]), (x, y, z_viga(y)), f'puntal RECT 150x100x3 entre cordón y viga inclinada, eje {xn}, {gap:.0f} cm')
                    y += PASO_PUNTAL
    # ---------- costaneras CA 100x50x15x3 cada 61 de alero a alero, continuas sobre las 5 vigas ----------
    x_ini, x_fin = xA[0] - ALERO_EO, xA[4] + ALERO_EO
    n = int(math.floor((y_fin - y_ini - 6) / PASO_COST)) + 1
    for i in range(n):
        y = y_ini + 3 + i * PASO_COST
        z = z_viga(y) + PERFILES['RECT 200x150x5']['h'] + h2('CA 100x50x15x3')   # apoyada sobre la viga inclinada
        m(f'CO-{i+1:02d}', 'costanera', 'CA 100x50x15x3', (x_ini, y, z), (x_fin, y, z), f'costanera {i+1} de {n}, y = {y:.0f}')
    for yn, y in (('norte', y_ini), ('sur', y_fin)):
        m(f'SA-{yn}', 'otro', 'C 150x50x3', (x_ini, y, z_viga(y) + h2('RECT 200x150x5')), (x_fin, y, z_viga(y) + h2('RECT 200x150x5')), f'soporte C 150x50x3 del alero {yn} (el original lo lleva en la punta del alero bajo)')
    # ---------- cruces C 150x50x3 (tramos de 2 m, como F1-E3 y A2-A1) ----------
    def cruz(id_, a, b, d):
        (xa, ya), (xb, yb) = a, b
        m(f'{id_}a', 'diagonal', 'C 150x50x3', (xa, ya, 10), (xb, yb, Z_CORDON[0] - 8), d)
        m(f'{id_}b', 'diagonal', 'C 150x50x3', (xa, ya, Z_CORDON[0] - 8), (xb, yb, 10), d)
    for xn, x in (('1', xA[0]), ('5', xA[4])):
        cruz(f'X-{xn}-AA2', (x, yA[0]), (x, yA[1]), f'cruz N-S en la fachada {"poniente" if xn == "1" else "oriente"}, tramo A-A2 (2,00 m), como F1-E3 del original')
        cruz(f'X-{xn}-DE', (x, yA[4]), (x, yA[5]), f'cruz N-S en la fachada {"poniente" if xn == "1" else "oriente"}, tramo D-E (2,00 m), como A2-A1 del original')
    # en el tabique cafetería/baño (B, 4-5) va la puerta del baño pegada al eje 4: cabe una sola diagonal, del tope del pilar 4 a la base del 5
    m('X-B-45a', 'diagonal', 'C 150x50x3', (xA[3], yB, Z_CORDON[0] - 8), (xA[4], yB, 10), 'diagonal E-O única en el tabique cafetería/baño (eje B, tramo 4-5): la puerta del baño ocupa el lado del eje 4 y una cruz completa la cruzaría; propuesta, revisar')
    cruz('X-C-45', (xA[3], yC), (xA[4], yC), 'cruz E-O en el tabique baño/bodega (eje C, tramo 4-5, muro ciego): propuesta')
    cruz('X-E-12', (xA[0], yA[5]), (xA[1], yA[5]), 'cruz E-O en la fachada sur, tramo 1-2 (muro ciego de los parlantes): propuesta')
    cruz('X-E-45', (xA[3], yA[5]), (xA[4], yA[5]), 'cruz E-O en la fachada sur, tramo 4-5 (bodega, muro ciego): propuesta')
    # ---------- tensores Fe 16 en el plano del techo: X en los paños extremos completos y en los vanos extremos del resto ----------
    panos = [(yA[0], yA[1]), (yA[1], yB), (yB, yC), (yC, yA[4]), (yA[4], yA[5])]
    for pi, (ya, yb) in enumerate(panos):
        vanos = range(4) if pi in (0, 4) else (0, 3)
        for i in vanos:
            xa, xb = xA[i], xA[i + 1]; zt = lambda y: z_viga(y) + 20
            m(f'T-{xN[i]}{xN[i+1]}-{int(ya)}a', 'tensor', 'FE 16', (xa, ya, zt(ya)), (xb, yb, zt(yb)), f'tensor Fe 16 del techo, vano {xN[i]}-{xN[i+1]}, paño {ya:.0f}..{yb:.0f}')
            m(f'T-{xN[i]}{xN[i+1]}-{int(ya)}b', 'tensor', 'FE 16', (xb, ya, zt(ya)), (xa, yb, zt(yb)), f'tensor Fe 16 del techo, vano {xN[i]}-{xN[i+1]}, paño {ya:.0f}..{yb:.0f}')

    # ---------- hormigón del búnker ----------
    bk = E['bunker']['pts']; bx0, by0, bx1, by1 = bk[0][0] - BUNKER_MURO, bk[0][1] - BUNKER_MURO, bk[1][0] + BUNKER_MURO, bk[2][1] + BUNKER_MURO   # exterior 0..1055 x 0..650
    z_losa_inf = -BUNKER_LOSA; z_piso = z_losa_inf - BUNKER_H; z_rad_inf = z_piso - BUNKER_RADIER; z_fund_inf = z_rad_inf - BUNKER_FUND
    def rect(x0, y0, x1, y1): return [ap(x0, y0, 0)[:2], ap(x1, y0, 0)[:2], ap(x1, y1, 0)[:2], ap(x0, y1, 0)[:2]]
    # escalera (planta de Gabriel): el 1.533 incluye el muro de 23,3 por el poniente; hueco libre ex_h..ex1 x ey0..ey1 (1,30 x 2,75);
    # se entra por el descanso del sur (ey1..cara del tabique) y se baja hacia el norte en 3,75 m: el último metro queda bajo la losa
    MURO_ESC = 23.3
    esc = rec['escalera']; ex_h, ey0, ex1, ey1 = esc[0][0], esc[0][1], esc[1][0], esc[2][1]
    ex0 = ex_h - MURO_ESC                      # cara poniente del muro de la escalera
    TRAMO_ESC = 375.0; y_pie = ey1 - TRAMO_ESC  # el tramo parte en ey1 (arriba) y termina 3,75 m al norte, en el piso del búnker
    y_desc = rec['cafeteria'][6][1]            # cara norte del tabique B: fin del descanso de entrada
    hormigon = dict(
        muros=dict(espesor=BUNKER_MURO, armadura='V ø12@15, H ø10@20 (dato: muro DM e=25)', z_inf=r1(z0 + z_piso), z_sup=r1(z0 + z_losa_inf),
                   piezas=[dict(id='M-N', pts=rect(bx0, by0, bx1, by0 + BUNKER_MURO), lado='norte (recibe los 5 pilares del eje A)'),
                           dict(id='M-S', pts=rect(bx0, by1 - BUNKER_MURO, bx1, by1), lado='sur, bajo el tabique cafetería/estudio (recibe los 5 pilares del eje B)'),
                           dict(id='M-O', pts=rect(bx0, by0 + BUNKER_MURO, bx0 + BUNKER_MURO, by1 - BUNKER_MURO), lado='poniente'), dict(id='M-E', pts=rect(bx1 - BUNKER_MURO, by0 + BUNKER_MURO, bx1, by1 - BUNKER_MURO), lado='oriente')]),   # entre los muros norte y sur, sin montarse (caras coplanares parpadean)
        losa=dict(espesor=BUNKER_LOSA, pts=rect(bx0, by0, bx1, by1), hueco=rect(ex_h, ey0, ex1, ey1), z_inf=r1(z0 + z_losa_inf), z_sup=r1(z0),
                  armadura='ø10@20 en la luz corta (N-S) y ø8@20 en la larga, borde del hueco 2ø12 (dato del original, luz de 5,00; ahora 6,00: recalcular)'),
        piso=dict(espesor=BUNKER_RADIER, pts=rect(bx0, by0, bx1, by1), z_inf=r1(z0 + z_rad_inf), z_sup=r1(z0 + z_piso), armadura='radier de 20 (dato: piso −292, fondo −312)'),
        fundacion=dict(espesor=BUNKER_FUND, pts=rect(bx0 - BUNKER_FUND_MARGEN, by0 - BUNKER_FUND_MARGEN, bx1 + BUNKER_FUND_MARGEN, by1 + BUNKER_FUND_MARGEN),
                       z_inf=r1(z0 + z_fund_inf), z_sup=r1(z0 + z_rad_inf), dato='losa de fundación de 30 bajo todo el búnker, 37,5 más ancha que los muros, más 5 de emplantillado (dato láminas 04 y 05: −312 a −342, −347)'),
        vigas=[dict(id='VHA-3', nombre='VHA 25/40', pts=rect(xA[2] - 12.5, by0 + BUNKER_MURO, xA[2] + 12.5, by1 - BUNKER_MURO), z_inf=r1(z0 + z_losa_inf - 20), z_sup=r1(z0 + z_losa_inf),
                    armadura='3ø12 sup, 2ø10 medios, 3ø16 inf, Est ø10@20 (dato: detalle VHA 25/40)', d=f'viga bajo la losa en el eje 3, de muro a muro ({by1 - by0 - 2 * BUNKER_MURO:.0f}): parte la losa en dos paños como la del eje 2.a original'),
               dict(id='VHA-esc', nombre='VHA 25/40 de borde', pts=rect(ex0, ey0 - 25, ex_h, ey1), z_inf=r1(z0 + z_losa_inf - 20), z_sup=r1(z0 + z_losa_inf),
                    armadura='como VHA 25/40 (propuesta)', d='viga de borde del hueco de la escalera (el original llevaba 2ø12 de borde en un hueco de 3,05 x 1,00)')],
        escalera=dict(pts=rect(ex_h, ey0, ex1, ey1), ancho=r1(ex1 - ex_h), largo=r1(ey1 - ey0), baja=r1(-z_piso), z_arriba=r1(z0), z_abajo=r1(z0 + z_piso), baja_hacia='norte',
                      tramo=dict(y_arriba=r1(oy + ey1), y_abajo=r1(oy + y_pie), largo=TRAMO_ESC, peldanos=16),
                      muro=dict(pts=rect(ex0, ey0, ex_h, y_desc), espesor=MURO_ESC),           # muro poniente de la caja de escalera, hasta el tabique (con la puerta del descanso)
                      muro_norte=dict(pts=rect(ex0, rec['cafeteria'][2][1], ex1, ey0), espesor=ey0 - rec['cafeteria'][2][1]),   # muro hacia la minicocina
                      hormigon=True,   # escalera y sus muros en hormigón armado (Gabriel, 2026-10-12)
                      descanso=rect(ex_h, ey1, ex1, y_desc),
                      nota=f'se entra por el sur (descanso de {(ex1 - ex_h)/100:.2f} x {(y_desc - ey1)/100:.2f}) y baja {-z_piso/100:.2f} m hacia el norte en {TRAMO_ESC/100:.2f} m: 16 peldaños de {TRAMO_ESC/16:.1f} x {-z_piso/16:.2f}; el hueco en la losa mide {(ex1 - ex_h)/100:.2f} x {(ey1 - ey0)/100:.2f} y el último metro va bajo la losa, dentro del búnker (altura libre en el borde norte del hueco ≈ {(-z_piso * (ey1 - ey0) / TRAMO_ESC - BUNKER_LOSA)/100:.2f} m; a revisar)'.replace('.', ',')),
        interior=dict(ancho=r1(bx1 - bx0 - 2 * BUNKER_MURO), largo=r1(by1 - by0 - 2 * BUNKER_MURO), alto=BUNKER_H),
        placas='placa de 15x15 bajo los PM1/PM2 y 15x10 bajo los PM3, sobre los muros (dato planta losa)',
    )
    # ---------- fundaciones fuera del búnker: zapatas aisladas 1x1x1 y vigas de fundación (Gabriel, a confirmar) ----------
    zap = []
    for mb in M:
        if mb['c'] != 'pilar': continue
        x, y = mb['a'][0] - ox, mb['a'][1] - oy
        if y > by1 + 1:
            # enterrada: tope en el terreno natural (50 bajo el piso), sello a 1,00 m; pedestal de 30 x 30 hasta la placa base del pilar
            zap.append(dict(id='Z-' + mb['id'][2:], pts=rect(x - ZAPATA[0] / 2, y - ZAPATA[1] / 2, x + ZAPATA[0] / 2, y + ZAPATA[1] / 2), z_sup=r1(z0 - 55), z_inf=r1(z0 - 55 - ZAPATA[2]),   # 5 cm bajo el terreno natural, para que el pasto la tape
                            pedestal=dict(pts=rect(x - 12, y - 12, x + 12, y + 12), z_sup=r1(z0), z_inf=r1(z0 - 55)),   # 24 x 24: queda medio centímetro adentro de las caras de la viga de fundación y del radier (si coincidieran, parpadean)
                            d=f'zapata aislada 1 x 1 x 1 bajo el pilar {mb["id"][2:]}, tope en el terreno natural y pedestal 24 x 24 hasta el pilar (Gabriel, como las del gimnasio; a confirmar)'))
    vf = []
    def vfund(id_, x0, y0, x1, y1, d): vf.append(dict(id=id_, pts=rect(min(x0, x1) - VIGA_FUND[0] / 2, min(y0, y1) - VIGA_FUND[0] / 2, max(x0, x1) + VIGA_FUND[0] / 2, max(y0, y1) + VIGA_FUND[0] / 2), z_sup=r1(z0 - RADIER), z_inf=r1(z0 - RADIER - VIGA_FUND[1]), d=d))
    # cada viga termina donde empieza la otra (o el muro sur del búnker): se tocan, no se montan, para que no parpadeen
    hv = VIGA_FUND[0] / 2
    vfund('VF-E', xA[0], yA[5], xA[4], yA[5], 'viga de fundación 25 x 50 bajo la fachada sur')
    vfund('VF-1', xA[0], by1 + hv, xA[0], yA[5] - 2 * hv, 'viga de fundación 25 x 50 bajo el eje 1 (B-E)'); vfund('VF-5', xA[4], by1 + hv, xA[4], yA[5] - 2 * hv, 'viga de fundación 25 x 50 bajo el eje 5 (B-E)')
    vfund('VF-4', xA[3], by1 + hv, xA[3], yA[5] - 2 * hv, 'viga de fundación 25 x 50 bajo el tabique del eje 4')
    vfund('VF-C', xA[3] + 2 * hv, yC, xA[4] - 2 * hv, yC, 'viga de fundación 25 x 50 bajo el tabique baño/bodega')
    radier = dict(espesor=RADIER, pts=rect(bx0, by1, bx1, L), z_sup=r1(z0), z_inf=r1(z0 - RADIER), dato='radier de 10 fuera del búnker (dato lámina 04)')

    # ---------- vanos propuestos (ventanas y puertas) ----------
    V = []
    def vano(id_, tipo, muro, x0, y0, x1, y1, z0_, z1_, d, **k): V.append(dict(id=id_, tipo=tipo, muro=muro, a=ap(x0, y0, 0)[:2], b=ap(x1, y1, 0)[:2], z0=r1(z0 + z0_), z1=r1(z0 + z1_), ancho=r1(math.hypot(x1 - x0, y1 - y0)), alto=r1(z1_ - z0_), d=d, **k))
    hol = 20.0   # holgura a cada lado del pilar
    # fachada norte (A): vidrio de piso a 3,00 en los 4 tramos; corredera al patio en el tramo 2-3
    for i in range(4):
        x0, x1 = xA[i] + hol, xA[i + 1] - hol
        if i == 1: vano(f'V-A-{i+1}', 'puerta corredera', 'norte', x0, yA[0], x1, yA[0], 0, H_VENTANA, 'corredera vidriada de 2 hojas al patio, en el tramo 2-3: alineada con la corredera interior y la ventana sur (eje del estudio)')
        else: vano(f'V-A-{i+1}', 'ventana', 'norte', x0, yA[0], x1, yA[0], 0, H_VENTANA, 'ventana fija de piso a 3,00 entre pilares; la cafetería mira al patio')
    # tabique cafetería/estudio (B): vidrio de piso a la viga E-O (que va pegada bajo la viga inclinada) en los tramos 1-2 y 3-4, corredera en el 2-3 (centrada en el estudio)
    z_vB, z_vE = z_tope(yB) - 5 - 5, z_tope(yA[5]) - 5 - 5   # 5 cm bajo la cara inferior de la viga E-O
    for i in range(3):
        x0, x1 = xA[i] + hol, xA[i + 1] - hol
        if i == 1: vano(f'V-B-{i+1}', 'puerta corredera interior', 'tabique B', x0, yB, x1, yB, 0, z_vB, 'corredera vidriada de 2 hojas entre cafetería y estudio, centrada en el estudio')
        else: vano(f'V-B-{i+1}', 'vidrio interior', 'tabique B', x0, yB, x1, yB, 0, z_vB, f'vidrio fijo de piso a cielo ({z_vB/100:.2f} m, hasta la viga E-O bajo el techo) entre cafetería y estudio (acústico: doble vidrio)'.replace('.', ','))
    vano('P-B-bano', 'puerta', 'tabique B', xA[3] + 25, yB, xA[3] + 105, yB, 0, 210, 'puerta del baño desde la cafetería (0,80 x 2,10), pegada al eje 4 para que la diagonal pase por encima y no tope con la escalera')
    # fachada sur (E): ventana de piso a cielo centrada en el estudio (tramo 2-3), entre los parlantes; la viga E-O del eje E va arriba para no cortarla
    vano('V-E-2', 'ventana', 'sur', xA[1] + hol, yA[5], xA[2] - hol, yA[5], 0, z_vE, f'ventana de piso a cielo ({z_vE/100:.2f} m, hasta la viga E-O bajo el techo) centrada en el estudio; los parlantes van a los lados, en el muro ciego'.replace('.', ','))
    # entrada principal: fachada poniente, lado de la casa, en la cafetería (tramo A2-B)
    # entrada pegada al pilar A2 (el tramo A-A2 lleva cruz); la cabina de grabación queda al sur de la puerta, contra el tabique vidriado
    vano('P-O-entrada', 'puerta', 'poniente', xA[0], yA[1] + 10, xA[0], yA[1] + 190, 0, 240, 'puerta de entrada de 2 hojas (1,80) desde el lado de la casa y el estacionamiento')
    # ventana alta del baño en la fachada oriente (tramo B-C, sin cruces)
    vano('V-5-bano', 'ventana alta', 'oriente', xA[4], (yB + yC) / 2 - 75, xA[4], (yB + yC) / 2 + 75, 230, 290, 'ventana alta del baño (1,50 x 0,60) en la fachada oriente')
    # la bodega va sin ventana (Gabriel, 2026-10-12)
    vano('P-4-bodega', 'puerta', 'tabique 4', xA[3], yC + 40, xA[3], yC + 130, 0, 240, 'puerta de la bodega desde el estudio (0,90)')
    vano('P-esc', 'escalera', 'interior', ex0, ey1, ex0, y_desc, 0, 0, 'bajada al búnker: se entra por el descanso del sur y se baja hacia el norte')
    # puerta con llave al descanso de la escalera (seguridad del búnker), en el muro poniente de la caja de escalera
    vano('P-esc-puerta', 'puerta', 'muro escalera', ex0 + MURO_ESC / 2, y_desc - 95, ex0 + MURO_ESC / 2, y_desc - 5, 0, 210, 'puerta con llave al descanso de la escalera (0,90 x 2,10): la bajada al búnker queda cerrada por seguridad')
    # ---------- esquema interior (idea, para conversar) ----------
    est = rec['estudio']; ce_x = (est[0][0] + est[1][0]) / 2
    caf = rec['cafeteria']
    # Cada mueble: tipo (lo dibuja mobiliario3d.js), recinto, pts = rectángulo en planta (app, cm), alto (cm, desde el piso) y
    # mira = hacia dónde da el frente ('N', 'S', 'E', 'O'). Solo es una idea para conversar; Gabriel decide el amoblado.
    interior = []
    def mueble(id_, tipo, recinto, nombre, x0, y0, x1, y1, alto, mira, nota=''):
        interior.append(dict(id=id_, tipo=tipo, recinto=recinto, nombre=nombre, pts=rect(x0, y0, x1, y1), alto=alto, mira=mira, nota=nota))
    # --- estudio de producción: triángulo de escucha mirando al sur ---
    mueble('parlantes', 'parlante', 'estudio', 'Parlante principal (monitor de campo medio)', ce_x - 300, est[2][1] - 60, ce_x - 220, est[2][1] - 5, 150, 'N', 'en el muro sur, a los lados de la ventana central')
    mueble('parlantes2', 'parlante', 'estudio', 'Parlante principal (monitor de campo medio)', ce_x + 220, est[2][1] - 60, ce_x + 300, est[2][1] - 5, 150, 'N', '')
    mueble('consola', 'consola', 'estudio', 'Consola / escritorio de producción', ce_x - 120, est[2][1] - 320, ce_x + 120, est[2][1] - 240, 75, 'S', 'mirando al sur, a unos 2,5 m de los parlantes (triángulo de escucha); con dos monitores y controlador')
    mueble('silla_consola', 'silla_oficina', 'estudio', 'Silla del productor', ce_x - 30, est[2][1] - 400, ce_x + 30, est[2][1] - 340, 110, 'S', '')
    mueble('rack', 'rack', 'estudio', 'Rack de equipos (12U)', ce_x + 170, est[2][1] - 330, ce_x + 230, est[2][1] - 230, 90, 'O', 'al lado del escritorio')
    mueble('sofa', 'sofa', 'estudio', 'Sofá de clientes', ce_x - 130, est[0][1] + 120, ce_x + 130, est[0][1] + 210, 85, 'S', 'al norte, junto al vidrio hacia la cafetería')
    for k, yy in enumerate((est[0][1] + 280, est[0][1] + 430, est[0][1] + 580)):
        mueble(f'panel_o{k+1}', 'panel_acustico', 'estudio', 'Panel acústico 100 × 120', est[0][0], yy, est[0][0] + 6, yy + 100, 220, 'E', 'en el muro poniente, a 1,00 del piso')
    for k, yy in enumerate((est[0][1] + 230, est[0][1] + 350, est[0][1] + 600)):   # en el oriente, lejos de la puerta de la bodega (yC+40..yC+130)
        mueble(f'panel_e{k+1}', 'panel_acustico', 'estudio', 'Panel acústico 100 × 120', est[1][0] - 6, yy, est[1][0], yy + 100, 220, 'O', 'en el muro oriente, a 1,00 del piso')
    mueble('alfombra', 'alfombra', 'estudio', 'Alfombra', ce_x - 200, est[2][1] - 460, ce_x + 200, est[2][1] - 100, 1, 'S', 'bajo la consola')
    # --- cafetería: cabina en el tramo 1-2, barra contra el muro de la escalera, mesas al centro ---
    # la cabina de grabación de la cafetería se sacó por ahora (Gabriel, 2026-10-12)
    mueble('barra', 'barra', 'cafeteria', 'Barra de la cafetería', ex0 - 100, ey0 + 10, ex0 - 20, ey0 + 270, 105, 'O', 'de espaldas al muro de la escalera (2,60 x 0,80), sin tapar las ventanas del patio ni la puerta del baño')
    for k, yy in enumerate((ey0 + 40, ey0 + 130, ey0 + 220)):
        mueble(f'taburete{k+1}', 'taburete', 'cafeteria', 'Taburete de la barra', ex0 - 165, yy, ex0 - 130, yy + 35, 75, 'E', '')
    mesas = [(caf[0][0] + 300, caf[0][1] + 250), (caf[0][0] + 480, caf[0][1] + 250)]   # dos mesas de 160 x 80 en fila frente al patio, lejos de la barra
    for k, (mx, my) in enumerate(mesas):
        mueble(f'mesa{k+1}', 'mesa', 'cafeteria', 'Mesa de cowork 160 × 80', mx, my, mx + 160, my + 80, 75, 'N', 'al centro, frente a las ventanas del patio')
        for j, cx_ in enumerate((mx + 20, mx + 95)):
            mueble(f'silla{k+1}{j+1}n', 'silla', 'cafeteria', 'Silla', cx_, my - 50, cx_ + 45, my - 5, 85, 'S', '')
            mueble(f'silla{k+1}{j+1}s', 'silla', 'cafeteria', 'Silla', cx_, my + 85, cx_ + 45, my + 130, 85, 'N', '')
    # cocina chica en la esquina nororiente (Gabriel, 2026-10-12): mueble con lavaplatos contra el muro oriente y refrigerador pequeño al lado
    mueble('cocina', 'cocina', 'cafeteria', 'Cocina chica con lavaplatos', ex1 - 60, caf[0][1] + 75, ex1, ey0 - 15, 90, 'O', 'mueble de 0,60 de fondo contra el muro oriente, al norte de la escalera; lavaplatos pequeño para lavar lo que se use')
    mueble('minibar', 'minibar', 'cafeteria', 'Minibar', ex1 - 55, caf[0][1] + 15, ex1 - 5, caf[0][1] + 65, 85, 'O', 'frigobar de 0,50 x 0,50 con puerta de vidrio, en la esquina nororiente junto a la cocina')
    mueble('lampara_barra', 'lampara', 'cafeteria', 'Lámpara colgante', ex0 - 75, ey0 + 125, ex0 - 45, ey0 + 155, 230, 'S', 'sobre la barra; cuelga del cielo')
    for k, (mx, my) in enumerate(mesas):
        mueble(f'lampara_mesa{k+1}', 'lampara', 'cafeteria', 'Lámpara colgante', mx + 65, my + 25, mx + 95, my + 55, 230, 'S', 'sobre la mesa; cuelga del cielo')
    # --- baño y bodega ---
    ban = rec['bano']; bod = rec['bodega']
    mueble('wc', 'wc', 'bano', 'Inodoro', ban[1][0] - 80, ban[2][1] - 75, ban[1][0] - 40, ban[2][1] - 5, 80, 'N', 'contra el tabique baño/bodega')
    mueble('lavamanos', 'lavamanos', 'bano', 'Lavamanos con mueble', ban[1][0] - 50, ban[0][1] + 150, ban[1][0], ban[0][1] + 210, 85, 'O', 'en el muro oriente, bajo la ventana alta')
    mueble('estante_e', 'estante', 'bodega', 'Estantería metálica 40 de fondo', bod[1][0] - 40, bod[0][1] + 35, bod[1][0], bod[2][1] - 45, 200, 'O', 'en el muro oriente de la bodega')
    mueble('estante_s', 'estante', 'bodega', 'Estantería metálica 40 de fondo', bod[0][0] + 10, bod[2][1] - 40, bod[1][0] - 45, bod[2][1], 200, 'N', 'en el muro sur de la bodega')
    # ---------- techo, cielo, cubicación ----------
    cub = {}
    for mb in M: cub[mb['p']] = cub.get(mb['p'], 0) + math.dist(mb['a'], mb['b']) / 100
    cubicacion = [dict(perfil=p, metros=round(cub[p], 1), kg=round(cub[p] * PESO[p])) for p in PESO if cub.get(p, 0) > 0]
    tot = round(sum(c['kg'] for c in cubicacion))
    techo = dict(contorno=[ap(x_ini, y_ini, 0)[:2], ap(x_fin, y_ini, 0)[:2], ap(x_fin, y_fin, 0)[:2], ap(x_ini, y_fin, 0)[:2]],
                 y0=r1(oy + y_ini), y1=r1(oy + y_fin), z0=r1(z0 + z_viga(y_ini) + 30), z1=r1(z0 + z_viga(y_fin) + 30), espesor=5)
    cielo = dict(z_norte=r1(z0 + z_viga(yA[0])), z_sur=r1(z0 + z_viga(yA[5])), y_norte=r1(oy + yA[0]), y_sur=r1(oy + yA[5]))
    cambios = [
        dict(que='Orientación', original='búnker bajo el tramo E1–A1 (lado alto del techo)', nuevo='búnker bajo la cafetería (norte, lado bajo); el techo sube al sur como la casa', por='Gabriel'),
        dict(que='Aleros', original='80 al norte y al sur, 52 al oriente y al poniente', nuevo=f'{ALERO_NS - MURO/2:.0f} cm por todos lados desde la cara exterior del muro, como los de la casa', por='Gabriel: el techo se veía corto'),
        dict(que='Pendiente del techo', original='rotulada 3,5 %, dibujada 4,5 % (+400 en F1, +447 en A1)', nuevo='3,5 % (+400 al norte, +454 al sur)', por='Gabriel: la de la casa · preguntar cuál manda'),
        dict(que='Planta', original='11,05 x 10,25 m entre ejes (5 ejes E-O a 205 | 365 | 205 | 330; 6 ejes N-S a 205 | 170 | 125 | 343 | 182)', nuevo=f'10,55 x 15,75 m por fuera; ejes 1-5 a {xA[1]-xA[0]:.0f} | {xA[2]-xA[1]:.0f} | {xA[3]-xA[2]:.0f} | {xA[4]-xA[3]:.0f} y A-E a 200 | {yB-yA[1]:.0f} | {yC-yB:.0f} | {yA[4]-yC:.0f} | 200', por='planta de Gabriel (medidas interiores) · ejes: propuesta'),
        dict(que='Búnker', original='5,00 x 10,80 interiores (muros 1.a, 3.a, E1, A1), 2,72 de alto, hueco de 3,05 x 1,00 junto al muro A1', nuevo=f'{hormigon["interior"]["largo"]/100:.2f} x {hormigon["interior"]["ancho"]/100:.2f} interiores, 2,80 de alto, hueco de escalera de {hormigon["escalera"]["ancho"]/100:.2f} x {hormigon["escalera"]["largo"]/100:.2f} junto al muro oriente', por='Gabriel'),
        dict(que='Muro sur del búnker', original='—', nuevo='coincide con el tabique cafetería/estudio (eje B) y recibe sus 5 pilares', por='planta de Gabriel'),
        dict(que='Losa del búnker', original='e=20, luz 5,00 (ø10@20 N-S, ø8@20 E-O), VHA 25/40 en 2.a', nuevo='e=20, luz 6,00 (+20 %, +44 % de momento), VHA 25/40 en el eje 3 y viga de borde en la escalera', por='para el ingeniero'),
        dict(que='Marcos interiores', original='1.b y 1.c: pilares solo en F1 y A1 (10,25 m), cordón RECT 150x100x3 a +400, viga 200x150x5, puntales 150x100x3 cada 171', nuevo=f'ejes 2, 3 y 4: pilares en A, B y E; luces de {(yB-yA[0])/100:.2f} y {(yA[5]-yB)/100:.2f} m con el mismo esquema'.replace('.', ','), por='propuesta'),
        dict(que='Vigas E-O de B y E', original='todas a +400/+410', nuevo=f'en B y E van pegadas bajo la viga inclinada (+{z_tope(yB)-5:.0f} en B, +{z_tope(yA[5])-5:.0f} en E) para que el vidrio del tabique y la ventana sur lleguen al cielo; A y C siguen a +400', por='propuesta: Gabriel quiere la ventana sur de piso a cielo'),
        dict(que='Fachadas laterales', original='1.a, 2.a, 3.a: pilares cada 1,25–3,43 m, viga 200x150x3, cruces en los tramos de 2,05 y 1,82', nuevo='ejes 1 y 5: pilares en A, A2, B, C, D, E; cruces en A-A2 y D-E (2,00 m)', por='propuesta'),
        dict(que='Pilares', original='21 (13 de 15×15 y 8 de 15×10 en la planta de cubierta)', nuevo=f'{sum(1 for mb in M if mb["c"] == "pilar")}; ninguno dentro de los recintos', por='propuesta'),
        dict(que='Rigidez E-O', original='sin cruces E-O en las láminas', nuevo='cruces en los muros ciegos: tabique baño/bodega (C, 4-5) y fachada sur (1-2 y 4-5), y una sola diagonal en el tabique cafetería/baño (B, 4-5) por la puerta del baño; el vidrio entre cafetería y estudio queda libre', por='propuesta: revisar'),
        dict(que='Costaneras', original='CA 100x50x15x3 @61, 20 por línea; colgadores ø10 en los paños de 3,65 y 3,30', nuevo=f'mismo perfil y paso, {n} por línea; paños de ≤ {max(xA[i+1]-xA[i] for i in range(4))/100:.2f} m: sin colgadores', por='propuesta'),
        dict(que='Fundaciones fuera del búnker', original='pedestal 25x50 y zapata corrida 75x25 (CF 25/40), radier de 10', nuevo='zapatas aisladas 1x1x1 con vigas de fundación 25x50, radier de 10', por='Gabriel: como las del gimnasio; pendiente'),
        dict(que='Base del búnker', original='losa de fundación de 30 bajo todo el búnker, radier de 20', nuevo='igual, con el búnker nuevo', por='dato'),
        dict(que='Acero', original='—', nuevo=f'{tot} kg de perfiles en el modelo (sin placas ni pérdidas)', por='cubicación del modelo'),
    ]
    preguntas = [
        'Pendiente del techo: sus láminas la rotulan 3,5 % pero la dibujan 4,5 %. Gabriel quiere la de la casa (3,5 %). ¿Cuál manda?',
        f'Marcos interiores de {(yA[5] - yB) / 100:.2f} m (ejes 2, 3 y 4, tramo B-E):'.replace('.', ',') + ' ¿sirve el mismo esquema de 1.b/1.c (cordón 150x100x3 + viga 200x150x5 + puntales), que salvaba 10,25?',
        'Losa del búnker: con 6,00 m de luz (antes 5,00), ¿se mantiene e=20 con más armadura o conviene e=25? ¿Basta una VHA 25/40 al centro?',
        'Rigidez E-O: las láminas no muestran cruces E-O. Con vidrio entre cafetería y estudio y ventanas al patio, se proponen cruces en los muros ciegos del lado oriente y de la fachada sur. ¿Van bien, o prefiere marcos rígidos? En el tabique cafetería/baño (B, 4-5) cabe una sola diagonal por la puerta del baño: ¿sirve, o conviene que el baño se abra desde el estudio (eje 4) y poner la cruz completa?',
        f'Ventanas: vidrio de piso a 3,00 en los cuatro tramos de la fachada norte y de piso a cielo en el tabique B ({z_vB/100:.2f}) y en el tramo 2-3 de la fachada sur ({z_vE/100:.2f}), todas entre pilares; para eso las vigas E-O de B y E se subieron hasta quedar bajo la viga inclinada. ¿Sirve así, o la viga E-O tiene que quedar a +4,00 y el vidrio para ahí? ¿Los pilares reciben el marco directamente o hacen falta montantes y un travesaño a +3,00?'.replace('.', ','),
        'Fundaciones fuera del búnker: Gabriel piensa en zapatas aisladas 1x1x1 con vigas de fundación, como las del gimnasio. ¿O se repite el cimiento corrido del original?',
        'Búnker de 2,80 de alto (antes 2,72): ¿cambia algo en los muros o en la losa de fundación?',
    ]
    out = dict(
        fuente='Adaptación de las láminas 03, 04 y 05 del ingeniero (proyecto del estudio, abril 2026, leídas de sus vectores) a la planta de Gabriel (medidas interiores, 2026-10-12); propuesta para revisión del ingeniero, no es un cálculo',
        marco='cm del marco de la app; z = 0 en el piso del nivel 1 de la casa; el piso del estudio (NPOG 0,00 del ingeniero) está en z = %s' % z0,
        z_piso=z0, ejes=ejes, perfiles={k: PERFILES[k] for k in sorted(set(mb['p'] for mb in M))}, miembros=M,
        hormigon=hormigon, zapatas=zap, vigas_fundacion=vf, radier=radier, vanos=V, interior=interior, techo=techo, cielo=cielo,
        cubicacion=cubicacion, total_kg=tot, cambios=cambios, preguntas=preguntas,
        parametros=dict(muro=MURO, h_pilar=H_PILAR, pendiente=PEND, alero_ns=ALERO_NS, alero_eo=ALERO_EO, paso_costanera=PASO_COST, paso_puntal=PASO_PUNTAL, h_ventana=H_VENTANA,
                        bunker=dict(losa=BUNKER_LOSA, muro=BUNKER_MURO, radier=BUNKER_RADIER, fundacion=BUNKER_FUND, alto=BUNKER_H)),
    )
    open(salida, 'w').write('const DATA_ESTUDIO_EST = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
    clases = {}
    for mb in M: clases[mb['c']] = clases.get(mb['c'], 0) + 1
    print(f'{salida}: {len(M)} piezas {clases} · acero {tot} kg · búnker {hormigon["interior"]["ancho"]/100:.2f} x {hormigon["interior"]["largo"]/100:.2f} x {BUNKER_H/100:.2f} m · {len(V)} vanos · {len(zap)} zapatas')
    for c in cubicacion: print(f"   {c['perfil']:16s} {c['metros']:7.1f} m  {c['kg']:5d} kg")

if __name__ == '__main__':
    main(*sys.argv[1:4])
