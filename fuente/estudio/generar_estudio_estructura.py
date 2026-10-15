# -*- coding: utf-8 -*-
"""Propuesta de estructura del estudio con búnker, adaptada del proyecto del ingeniero (láminas 03, 04 y 05 de
abril de 2026, leídas de sus vectores: fuente/estudio/datos/) a la planta de Gabriel (medidas interiores:
cafetería 6,20 x 10,25, estudio 10,50 x 7,50, baño 2,50 x 1,90, cabina 2,50 x 3,80, bodega 2,50 x 4,30; tabiques de 25; edificio de
10,75 x 17,45 por fuera; búnker bajo la cafetería, al norte; techo al 3,5 % subiendo al sur como la casa).
Genera estudio_estructura.js (DATA_ESTUDIO_EST): acero (mismo formato que estructura.js), hormigón del búnker,
fundaciones, ejes, vanos (ventanas y puertas propuestas), esquema interior, cambios y preguntas.

    python3 generar_estudio_estructura.py ../sitio/estudio.json ../sitio/sitio.json ../../estudio_estructura.js

Marco local del estudio en cm: x al oriente desde la cara exterior poniente, y al sur desde la cara exterior
norte, z desde el piso terminado del estudio (NPOG 0,00 del ingeniero). Se convierte al marco de la app con el
origen del estudio (sitio.json) y su nivel de piso. No es un cálculo: es el sistema del ingeniero acomodado.
"""
import json, sys, math, os
import hormigon as HORM
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sitio'))
from geom import offset_rect_poly

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
H_PILAR = 400.0        # cara inferior de la viga E-O en el lado bajo; el ingeniero la tiene a +400 (lámina 04: +400 en F1): main() la sube con las terminaciones (4,00 libres + piso + cielo)
PEND = 0.035           # pendiente: rotulada 3,5 % (dibujada 4,5 %); Gabriel pide la de la casa, 3,5 %
ALERO_NS = 80.0        # aleros del ingeniero: norte y sur (1.186 = 1.025 + 80 + 80); se reemplazan por los de estudio.json si vienen (Gabriel: como la casa)
ALERO_EO = 52.0        # aleros del ingeniero: oriente y poniente (cota 52)
PASO_COST = 61.0       # costaneras CA 100x50x15x3 cada 61
PASO_PUNTAL = 171.0    # puntales RECT 150x100x3 cada 171 desde donde el cordón se separa de la viga
GAP_PUNTAL = 7.0       # el primer puntal del original tiene 7 cm
Z_CORDON = (400.0, 410.0)   # cordón RECT 150x100x3 y vigas E-O de +400 a +410 en la lámina 04; main() lo sube con las terminaciones
BUNKER_LOSA = 20.0     # losa de techo del búnker
BUNKER_MURO = 25.0     # muros MHA e=25
BUNKER_RADIER = 20.0   # piso −292 a −312 en el original
BUNKER_FUND = 30.0     # losa de fundación de 30 bajo todo el búnker (−312 a −342), 37,5 más ancha que los muros
BUNKER_FUND_MARGEN = 37.5
RADIER = 10.0          # radier de 10 fuera del búnker (lámina 04)
# ---------- Gabriel ----------
MURO = 25.0
BUNKER_H = 280.0       # altura libre terminada (Gabriel); main() le suma piso y cielo para la obra gruesa (el original 272)
ZAPATA = (100.0, 100.0, 100.0)   # zapatas aisladas 1 x 1 x 1 bajo los pilares fuera del búnker, con vigas de fundación (Gabriel, a confirmar)
VIGA_FUND = (25.0, 50.0)
H_VENTANA = 400.0      # todas las ventanas de piso terminado a cielo terminado: 4,00 (Gabriel, 13-10-2026: "dejemos todas las ventanas a 4 m")

def r1(v): return round(float(v), 1)

def main(estudio_json, sitio_json, salida):
    E = json.load(open(estudio_json)); S = json.load(open(sitio_json))
    global ALERO_NS, ALERO_EO, Z_CORDON, H_PILAR, BUNKER_H, T_PISO, T_CIELO, LIBRE
    # terminaciones (estudio.json): la estructura va sobre los 4,00 libres terminados + piso + cielo; el búnker suma lo mismo a sus 2,80 libres
    _A = E['alturas']; T_PISO = float(_A.get('terminacion_piso_cm', 0)); T_CIELO = float(_A.get('terminacion_cielo_cm', 0)); LIBRE = float(_A['interior_cm'])
    Z_CORDON = (LIBRE + T_PISO + T_CIELO, LIBRE + T_PISO + T_CIELO + 10.0); H_PILAR = Z_CORDON[0]
    BUNKER_H = float(E['bunker']['interior_cm']) + T_PISO + T_CIELO
    _al = E.get('alturas', {})   # aleros de estudio.json (Gabriel: como la casa), medidos desde la cara exterior → aquí van desde el eje del pilar
    if _al.get('alero_ns_cm'): ALERO_NS = float(_al['alero_ns_cm']) + MURO / 2
    if _al.get('alero_eo_cm'): ALERO_EO = float(_al['alero_eo_cm']) + MURO / 2
    ox, oy = S['estudio_origen']; z0 = E['nivel_piso']['z_cm']
    W, L = E['exterior']['ancho'], E['exterior']['largo']           # 1055 x 1575
    rec = {r['id']: r['pts'] for r in E['recintos']}                 # caras de obra gruesa (muros y tabiques de 25)
    T = float(E.get('tabique', {}).get('espesor', 0))                # tabique por dentro de los 4 muros del búnker (solo abajo)
    recT = rec                                                        # arriba muros y tabiques de 25 terminado, sin tabique extra (Gabriel, 14-10-2026): el mobiliario va contra las caras de muro
    # ---------- ejes: x 1-5 (el 4 sobre el tabique estudio | baño-bodega), y A-E ----------
    x_tab = (rec['estudio'][1][0] + rec['bano'][0][0]) / 2            # 767,5
    xA = [MURO / 2, MURO / 2 + (x_tab - MURO / 2) / 3, MURO / 2 + 2 * (x_tab - MURO / 2) / 3, x_tab, W - MURO / 2]
    xN = ['1', '2', '3', '4', '5']
    yB = rec['estudio'][0][1] - MURO / 2                               # 637,5: tabique cafetería/estudio = muro sur del búnker (la cafetería es un polígono en L: no usar su punto 5)
    yC = (rec['bano'][2][1] + rec['cabina'][0][1]) / 2                # 872,5: tabique baño/cabina
    yC2 = (rec['cabina'][2][1] + rec['bodega'][0][1]) / 2             # 1277,5: tabique cabina/bodega (eje C2 desde el 14-10-2026, al alargar el estudio a 10,50: ningún tramo N-S pasa de 4,45)
    yA = [MURO / 2, MURO / 2 + 200, yB, yC, yC2, L - MURO / 2 - 200, L - MURO / 2]   # A, A2, B, C, C2, D, E
    yN = ['A', 'A2', 'B', 'C', 'C2', 'D', 'E']
    ejes = dict(x={n: r1(v) for n, v in zip(xN, xA)}, y={n: r1(v) for n, v in zip(yN, yA)},
                nota='Ejes 1-5 de poniente a oriente (el 4 sobre el tabique estudio/baño-bodega) y A-E de norte a sur: B sobre el tabique '
                     'cafetería/estudio (= muro sur del búnker), C sobre el tabique baño/cabina, C2 sobre el tabique cabina/bodega; A2 y D a 2,00 m de las fachadas norte y sur, '
                     'para que las cruces queden en tramos de 2 m como las del original (2,05 y 1,82).')
    def ap(x, y, z): return [r1(ox + x), r1(oy + y), r1(z0 + z)]
    def z_viga(y): return Z_CORDON[1] + PEND * (y - yA[0])           # cara inferior de la viga inclinada: apoyada sobre la viga E-O 100x100 de +400/+410 (lámina 05: +411 en F1)
    # Convención: cada miembro se dibuja centrado en su línea, así que las cotas del ingeniero (caras inferiores) llevan sumado medio perfil.
    Z_CORDON_EJE = (Z_CORDON[0] + Z_CORDON[1]) / 2                     # 405: eje del cordón y de las vigas E-O (de +400 a +410)
    M = []
    def m(id_, c, p, a, b, d, **k): M.append(dict(id=id_, c=c, p=p, a=ap(*a), b=ap(*b), d=d, **k))
    lateral = lambda xn: xn in ('1', '5')

    # ---------- pilares: llegan a la cara inferior de la viga inclinada (lámina 04) ----------
    for yn, y in (('A', yA[0]), ('B', yB), ('E', yA[6])):
        for xn, x in zip(xN, xA):
            pm = 'PM1' if xn in ('2', '3') else 'PM2'
            perfil = 'CUAD 150x150x5' if pm == 'PM1' else 'CUAD 150x150x4'
            apoyo = {'A': 'sobre el muro norte del búnker', 'B': 'sobre el muro sur del búnker', 'E': 'sobre zapata aislada 1 x 1 x 1'}[yn]
            # lámina 05: en el marco bajo (F) el pilar termina a +400 bajo la viga E-O y sobre ella apoya la viga inclinada; en el marco alto (A1) el pilar
            # pasa la viga E-O de +400/+410 y sigue hasta la cara inferior de la viga inclinada (+447). Opción A de Gabriel (12-10-2026): igual aquí.
            zt = z_viga(y) if z_viga(y) - 10 > Z_CORDON[1] + 0.5 else Z_CORDON[0]
            d_t = (f'llega a +{Z_CORDON[0]:.0f}, bajo la viga E-O 100x100 de +{Z_CORDON[0]:.0f}/+{Z_CORDON[1]:.0f}, y sobre ella apoya la viga inclinada (lámina 05, marco F; allá a +400/+410, aquí más arriba por las terminaciones)' if zt == Z_CORDON[0]
                   else f'pasa por la viga E-O de +{Z_CORDON[0]:.0f}/+{Z_CORDON[1]:.0f} y sigue hasta la cara inferior de la viga inclinada (+{zt:.0f}), como los pilares del marco A1 de la lámina 05')
            m(f'P-{xn}{yn}', 'pilar', perfil, (x, y, 0), (x, y, zt), f'{pm} eje {xn} x {yn}, {apoyo}; {d_t}', alma='Y')
    for yn in ('A2', 'C', 'C2', 'D'):
        y = yA[yN.index(yn)]
        for xn, x in (('1', xA[0]), ('5', xA[4])):
            apoyo = 'sobre el muro del búnker' if y < yB else 'sobre zapata aislada'
            m(f'P-{xn}{yn}', 'pilar', 'RECT 150x100x3', (x, y, 0), (x, y, z_viga(y)), f'PM3 eje {xn} x {yn}, pilar intermedio de la fachada lateral, {apoyo}', alma='Y')
    m('P-4C', 'pilar', 'RECT 150x100x3', (xA[3], yC, 0), (xA[3], yC, z_viga(yC)), 'PM3 eje 4 x C, en el encuentro de los tabiques estudio/baño/cabina (recibe la cruz E-O del eje C)', alma='Y')
    m('P-4C2', 'pilar', 'RECT 150x100x3', (xA[3], yC2, 0), (xA[3], yC2, z_viga(yC2)), 'PM3 eje 4 x C2, en el encuentro de los tabiques estudio/cabina/bodega (recibe la cruz E-O del eje C2)', alma='Y')
    # ---------- vigas E-O CUAD 100x100x3: de +400 a +410 en A, B, E y C (4-5), como la lámina 05 (opción A de Gabriel, 12-10-2026) ----------
    for yn, y, tramos in (('A', yA[0], range(4)), ('B', yB, range(4)), ('E', yA[6], range(4)), ('C', yC, [3]), ('C2', yC2, [3])):
        for i in tramos:
            zv = Z_CORDON_EJE
            arriba = 'sobre ella apoya la viga inclinada' if abs(z_viga(y) - Z_CORDON[1]) < 0.5 else f'los pilares siguen hasta la viga inclinada (+{z_viga(y):.0f})'
            m(f'VT-{yn}-{xN[i]}{xN[i+1]}', 'viga', 'CUAD 100x100x3', (xA[i], y, zv), (xA[i + 1], y, zv), f'viga E-O a +{(Z_CORDON[0]/100):.2f}/+{(Z_CORDON[1]/100):.2f} entre pilares {xN[i]} y {xN[i+1]} del eje {yn} (lámina 05); {arriba}')
    # ---------- marcos N-S: cordón RECT 150x100x3 + viga inclinada + puntales (como 1.b y 1.c) ----------
    y_ini, y_fin = yA[0] - ALERO_NS, yA[6] + ALERO_NS   # puntas de los aleros (eje del pilar ± alero)
    for xn, x in zip(xN, xA):
        if not lateral(xn):
            for (ya, yb) in ((yA[0], yB), (yB, yA[6])):
                m(f'VC-{xn}-{int(ya)}', 'viga', 'RECT 150x100x3', (x, ya, Z_CORDON_EJE), (x, yb, Z_CORDON_EJE), f'cordón horizontal RECT 150x100x3 de +{(Z_CORDON[0]/100):.2f} a +{(Z_CORDON[1]/100):.2f} (acostado), eje {xn}, {ya:.0f}..{yb:.0f} (como 1.b y 1.c del original)', acostado=True)   # acostado: el alto de 15 queda horizontal y el cordón va de +4,00 a +4,10 (lámina 04)
        perfil = 'RECT 200x150x3' if lateral(xn) else 'RECT 200x150x5'
        m(f'VI-{xn}', 'cabio', perfil, (x, y_ini, z_viga(y_ini) + h2(perfil)), (x, y_fin, z_viga(y_fin) + h2(perfil)), f'viga inclinada de techo, eje {xn}, 3,5 % subiendo al sur, aleros de 80; cara inferior a +{z_viga(yA[0]):.0f} en A')
        if not lateral(xn):
            for (ya, yb) in ((yA[0], yB), (yB, yA[6])):
                y = ya + PASO_PUNTAL
                while y < yb - 60:
                    gap = z_viga(y) - Z_CORDON[1]
                    if gap >= GAP_PUNTAL:
                        m(f'PT-{xn}-{int(y)}', 'puntal', 'RECT 150x100x3', (x, y, Z_CORDON[1]), (x, y, z_viga(y)), f'puntal RECT 150x100x3 entre cordón y viga inclinada, eje {xn}, {gap:.0f} cm')
                    y += PASO_PUNTAL
    # ---------- costaneras CA 100x50x15x3 cada 61 de alero a alero, continuas sobre las 5 vigas ----------
    x_ini, x_fin = xA[0] - ALERO_EO, xA[4] + ALERO_EO
    n = int(math.floor((y_fin - y_ini - 38) / PASO_COST)) + 1   # la primera a 19 de la punta del alero, como el original (61 del eje con alero de 80)
    for i in range(n):
        y = y_ini + 19 + i * PASO_COST
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
        cruz(f'X-{xn}-DE', (x, yA[5]), (x, yA[6]), f'cruz N-S en la fachada {"poniente" if xn == "1" else "oriente"}, tramo D-E (2,00 m), como A2-A1 del original')
    # en el tabique cafetería/baño (B, 4-5) va la puerta del baño pegada al eje 4: cabe una sola diagonal, del tope del pilar 4 a la base del 5
    m('X-B-45a', 'diagonal', 'C 150x50x3', (xA[3], yB, Z_CORDON[0] - 8), (xA[4], yB, 10), 'diagonal E-O única en el tabique cafetería/baño (eje B, tramo 4-5): la puerta del baño ocupa el lado del eje 4 y una cruz completa la cruzaría; propuesta, revisar')
    cruz('X-C-45', (xA[3], yC), (xA[4], yC), 'cruz E-O en el tabique baño/cabina (eje C, tramo 4-5, muro ciego): propuesta')
    cruz('X-C2-45', (xA[3], yC2), (xA[4], yC2), 'cruz E-O en el tabique cabina/bodega (eje C2, tramo 4-5, muro ciego): propuesta')
    cruz('X-E-12', (xA[0], yA[6]), (xA[1], yA[6]), 'cruz E-O en la fachada sur, tramo 1-2 (muro ciego de los parlantes): propuesta')
    cruz('X-E-45', (xA[3], yA[6]), (xA[4], yA[6]), 'cruz E-O en la fachada sur, tramo 4-5 (bodega, muro ciego): propuesta')
    # ---------- tensores Fe 16 en el plano del techo: X en los paños extremos completos y en los vanos extremos del resto ----------
    panos = [(yA[0], yA[1]), (yA[1], yB), (yB, yC), (yC, yC2), (yC2, yA[5]), (yA[5], yA[6])]
    for pi, (ya, yb) in enumerate(panos):
        vanos = range(4) if pi in (0, len(panos) - 1) else (0, 3)
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
    escalera = dict(pts=rect(ex_h, ey0, ex1, ey1), ancho=r1(ex1 - ex_h), largo=r1(ey1 - ey0), baja=r1(-z_piso), z_arriba=r1(z0), z_abajo=r1(z0 + z_piso), baja_hacia='norte',
        tramo=dict(y_arriba=r1(oy + ey1), y_abajo=r1(oy + y_pie), largo=TRAMO_ESC, peldanos=16),
        muro=dict(pts=rect(ex0, ey0, ex_h, y_desc), espesor=MURO_ESC),           # muro poniente de la caja de escalera, hasta el tabique (con la puerta del descanso)
        muro_norte=dict(pts=rect(ex0, rec['cafeteria'][2][1], ex1, ey0), espesor=ey0 - rec['cafeteria'][2][1]),   # muro hacia la minicocina
        hormigon=True,   # escalera y sus muros en hormigón armado (Gabriel, 2026-10-12)
        descanso=rect(ex_h, ey1, ex1, y_desc),
        nota=f'se entra por el sur (descanso de {(ex1 - ex_h)/100:.2f} x {(y_desc - ey1)/100:.2f}) y baja {-z_piso/100:.2f} m hacia el norte en {TRAMO_ESC/100:.2f} m: 16 peldaños de {TRAMO_ESC/16:.1f} x {-z_piso/16:.2f}; el hueco en la losa mide {(ex1 - ex_h)/100:.2f} x {(ey1 - ey0)/100:.2f} y el último metro va bajo la losa, dentro del búnker (altura libre en el borde norte del hueco ≈ {(-z_piso * (ey1 - ey0) / TRAMO_ESC - BUNKER_LOSA)/100:.2f} m; a revisar)'.replace('.', ','))
    # ---------- hormigón armado, fundaciones, placas base y enfierradura: hormigon.py (láminas 01 rev 1, 02 rev G, 03 rev H, 05 rev H) ----------
    hormigon, fierros, cub_hormigon = HORM.armar(dict(ap=ap, rect=rect, r1=r1, z0=z0, ox=ox, oy=oy, xA=xA, yA=yA, yB=yB, yC=yC, yC2=yC2, W=W, L=L, rec=rec, bk=bk, BUNKER_H=BUNKER_H,
                                                      pilares=[mb for mb in M if mb['c'] == 'pilar'], escalera=escalera, ex0=ex0, ex_h=ex_h, ex1=ex1, ey0=ey0, ey1=ey1, y_desc=y_desc, x3=xA[2], T=T,
                                                      h_caja=z_viga(yB)))
    z_piso = hormigon['niveles']['piso_bunker']; z_losa_inf = hormigon['niveles']['losa_inf']

    # ---------- vanos propuestos (ventanas y puertas) ----------
    V = []
    # alturas de los vanos medidas desde el piso terminado (NPT = NPOG + piso), Gabriel 13-10-2026
    def vano(id_, tipo, muro, x0, y0, x1, y1, z0_, z1_, d, **k): V.append(dict(id=id_, tipo=tipo, muro=muro, a=ap(x0, y0, 0)[:2], b=ap(x1, y1, 0)[:2], z0=r1(z0 + T_PISO + z0_), z1=r1(z0 + T_PISO + z1_), ancho=r1(math.hypot(x1 - x0, y1 - y0)), alto=r1(z1_ - z0_), d=d, **k))
    hol = 20.0   # holgura a cada lado del pilar
    # fachada norte (A): vidrio solo en los dos tramos centrales (Gabriel, 13-10-2026): corredera al patio en el 2-3 y paño fijo en el 3-4; 1-2 y 4-5 ciegos
    for i in (1, 2):
        x0, x1 = xA[i] + hol, xA[i + 1] - hol
        if i == 1: vano(f'V-A-{i+1}', 'puerta corredera', 'norte', x0, yA[0], x1, yA[0], 0, H_VENTANA, 'corredera vidriada de 2 hojas al patio, en el tramo 2-3: alineada con la corredera interior y la ventana sur (eje del estudio)')
        else: vano(f'V-A-{i+1}', 'ventana', 'norte', x0, yA[0], x1, yA[0], 0, H_VENTANA, 'ventana fija de piso terminado a cielo terminado (4,00) en el tramo 3-4; la cafetería mira al patio por los dos tramos centrales')
    # tabique cafetería/estudio (B): vidrio solo en los dos tramos centrales (Gabriel, 13-10-2026): corredera en el 2-3 (centrada en el estudio) y paño fijo en el 3-4; el 1-2 va ciego
    z_vB = z_vE = H_VENTANA   # de piso terminado a cielo terminado (4,00); la viga E-O y el entretecho quedan encima
    gapB, gapE = z_viga(yB) - Z_CORDON[1], z_viga(yA[6]) - Z_CORDON[1]   # franja ciega sobre la viga E-O: 22 en B, 54 en E
    for i in (1, 2):
        x0, x1 = xA[i] + hol, xA[i + 1] - hol
        if i == 1: vano(f'V-B-{i+1}', 'puerta corredera interior', 'tabique B', x0, yB, x1, yB, 0, z_vB, 'corredera vidriada de 2 hojas entre cafetería y estudio, centrada en el estudio')
        else: vano(f'V-B-{i+1}', 'vidrio interior', 'tabique B', x0, yB, x1, yB, 0, z_vB, f'vidrio fijo de piso terminado a cielo terminado ({z_vB/100:.2f} m) entre cafetería y estudio (acústico: doble vidrio); la viga E-O de +{(Z_CORDON[0]/100):.2f} y la franja de {gapB:.0f} cm sobre ella quedan en el entretecho'.replace('.', ','))
    vano('P-B-bano', 'puerta', 'tabique B', xA[3] + 25, yB, xA[3] + 105, yB, 0, 210, 'puerta del baño desde la cafetería (0,80 x 2,10), pegada al eje 4 para que la diagonal pase por encima y no tope con la escalera')
    # fachada sur (E): ventana de piso terminado a cielo terminado centrada en el estudio (tramo 2-3), entre los parlantes
    vano('V-E-2', 'ventana', 'sur', xA[1] + hol, yA[6], xA[2] - hol, yA[6], 0, z_vE, f'ventana de piso terminado a cielo terminado ({z_vE/100:.2f} m) centrada en el estudio; los parlantes van a los lados, en el muro ciego; por fuera la fachada sigue sobre la viga E-O hasta el techo'.replace('.', ','))
    # entrada principal: fachada poniente, lado de la casa, en la cafetería (tramo A2-B)
    # entrada pegada al pilar A2 (el tramo A-A2 lleva cruz); la cabina de grabación queda al sur de la puerta, contra el tabique vidriado
    vano('P-O-entrada', 'puerta', 'poniente', xA[0], yA[1] + 10, xA[0], yA[1] + 190, 0, 240, 'puerta de entrada de 2 hojas (1,80) desde el lado de la casa y el estacionamiento')
    # ventana alta del baño en la fachada oriente (tramo B-C, sin cruces)
    vano('V-5-bano', 'ventana alta', 'oriente', xA[4], (yB + yC) / 2 - 75, xA[4], (yB + yC) / 2 + 75, 230, 290, 'ventana alta del baño (1,50 x 0,60) en la fachada oriente')
    # la bodega va sin ventana (Gabriel, 2026-10-12)
    vano('P-4-bodega', 'puerta', 'tabique 4', xA[3], rec['bodega'][0][1] + 10, xA[3], rec['bodega'][0][1] + 100, 0, 240, 'puerta de la bodega desde el estudio (0,90), en el extremo norte de la bodega: lo más lejos posible de la posición de escucha')
    vano('P-4-cabina', 'puerta', 'tabique 4', xA[3], rec['cabina'][0][1] + 15, xA[3], rec['cabina'][0][1] + 105, 0, 210, 'puerta acústica de la cabina desde el estudio (0,90 x 2,10, hoja maciza con doble burlete), en el extremo norte de la cabina, lejos de la posición de escucha; la cabina es ciega: sin ventana (Gabriel, 14-10-2026)')
    vano('P-esc', 'escalera', 'interior', ex0, ey1, ex0, y_desc, 0, 0, 'bajada al búnker: se entra por el descanso del sur y se baja hacia el norte')
    # puerta con llave al descanso de la escalera (seguridad del búnker), en el muro poniente de la caja de escalera
    vano('P-esc-puerta', 'puerta', 'muro escalera', ex0 + MURO_ESC / 2, y_desc - 95, ex0 + MURO_ESC / 2, y_desc - 5, 0, 210, 'puerta con llave al descanso de la escalera (0,90 x 2,10): la bajada al búnker queda cerrada por seguridad')
    # ---------- esquema interior (idea, para conversar) ----------
    est = recT['estudio']; ce_x = (est[0][0] + est[1][0]) / 2     # el mobiliario va contra las caras terminadas (tabique)
    caf = recT['cafeteria']
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
    for k, yy in enumerate((est[0][1] + 250, est[0][1] + 400, est[0][1] + 640, est[0][1] + 900)):   # entre los pilares C (872), C2 (1277) y D (1532) de la fachada poniente
        mueble(f'panel_o{k+1}', 'panel_acustico', 'estudio', 'Panel acústico 100 × 120', est[0][0], yy, est[0][0] + 6, yy + 100, 220, 'E', 'en el muro poniente, a 1,00 del piso')
    for k, yy in enumerate((est[0][1] + 340, est[0][1] + 470, est[0][1] + 745, est[0][1] + 900)):   # en el oriente, entre la puerta de la cabina (900..990) y la de la bodega (1300..1390), y al sur de esta
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
    ban = recT['bano']; bod = recT['bodega']
    mueble('wc', 'wc', 'bano', 'Inodoro', ban[1][0] - 80, ban[2][1] - 75, ban[1][0] - 40, ban[2][1] - 5, 80, 'N', 'contra el tabique baño/cabina')
    mueble('lavamanos', 'lavamanos', 'bano', 'Lavamanos con mueble', ban[1][0] - 50, ban[0][1] + 30, ban[1][0], ban[0][1] + 90, 85, 'O', 'en el muro oriente, bajo la ventana alta')
    mueble('estante_e', 'estante', 'bodega', 'Estantería metálica 40 de fondo', bod[1][0] - 40, bod[0][1] + 35, bod[1][0], bod[2][1] - 45, 200, 'O', 'en el muro oriente de la bodega')
    mueble('estante_s', 'estante', 'bodega', 'Estantería metálica 40 de fondo', bod[0][0] + 10, bod[2][1] - 40, bod[1][0] - 45, bod[2][1], 200, 'N', 'en el muro sur de la bodega')
    # --- cabina de grabación (Gabriel, 14-10-2026): ciega, cielo a 3,00; alfombra, paneles en los muros y una silla para el músico ---
    cab = recT['cabina']; cx_cab = (cab[0][0] + cab[1][0]) / 2
    mueble('alfombra_cab', 'alfombra', 'cabina', 'Alfombra de la cabina', cab[0][0] + 20, cab[0][1] + 120, cab[1][0] - 20, cab[2][1] - 20, 1, 'S', 'del lado sur de la puerta, casi todo el piso: la cabina es seca')
    for k, yy in enumerate((cab[0][1] + 130, cab[0][1] + 260)):   # al sur de la puerta (cab+15..cab+105)
        mueble(f'panel_cab_o{k+1}', 'panel_acustico', 'cabina', 'Panel acústico 100 × 120', cab[0][0], yy, cab[0][0] + 6, yy + 100, 220, 'E', 'en el muro poniente de la cabina, a 1,00 del piso (por dentro va toda forrada: estos son los paneles visibles)')
        mueble(f'panel_cab_e{k+1}', 'panel_acustico', 'cabina', 'Panel acústico 100 × 120', cab[1][0] - 6, yy, cab[1][0], yy + 100, 220, 'O', 'en el muro oriente de la cabina, a 1,00 del piso')
    mueble('panel_cab_s', 'panel_acustico', 'cabina', 'Panel acústico 100 × 120', cx_cab - 50, cab[2][1] - 6, cx_cab + 50, cab[2][1], 220, 'N', 'en el muro sur de la cabina')
    mueble('silla_cab', 'silla', 'cabina', 'Silla del músico', cx_cab - 22, cab[0][1] + 300, cx_cab + 23, cab[0][1] + 345, 85, 'N', 'al centro, mirando a la puerta')
    # ---------- techo, cielo, cubicación ----------
    cub = {}
    for mb in M: cub[mb['p']] = cub.get(mb['p'], 0) + math.dist(mb['a'], mb['b']) / 100
    cubicacion = [dict(perfil=p, metros=round(cub[p], 1), kg=round(cub[p] * PESO[p])) for p in PESO if cub.get(p, 0) > 0]
    tot = round(sum(c['kg'] for c in cubicacion))
    techo = dict(contorno=[ap(x_ini, y_ini, 0)[:2], ap(x_fin, y_ini, 0)[:2], ap(x_fin, y_fin, 0)[:2], ap(x_ini, y_fin, 0)[:2]],
                 y0=r1(oy + y_ini), y1=r1(oy + y_fin), z0=r1(z0 + z_viga(y_ini) + 30), z1=r1(z0 + z_viga(y_fin) + 30), espesor=5)
    cielo = dict(z_norte=r1(z0 + z_viga(yA[0])), z_sur=r1(z0 + z_viga(yA[6])), y_norte=r1(oy + yA[0]), y_sur=r1(oy + yA[6]))
    cambios = [
        dict(que='Orientación', original='búnker bajo el tramo E1–A1 (lado alto del techo)', nuevo='búnker bajo la cafetería (norte, lado bajo); el techo sube al sur como la casa', por='Gabriel'),
        dict(que='Aleros', original='80 al norte y al sur, 52 al oriente y al poniente', nuevo=f'{ALERO_NS - MURO/2:.0f} cm por todos lados desde la cara exterior del muro, como los de la casa', por='Gabriel: el techo se veía corto'),
        dict(que='Pendiente del techo', original='rotulada 3,5 %, dibujada 4,5 % (+400 en F1, +447 en A1)', nuevo='3,5 % (+400 al norte, +454 al sur), la de la casa; el 4,5 % dibujado se toma como error de la lámina', por='Gabriel'),
        dict(que='Planta', original='11,05 x 10,25 m entre ejes (5 ejes E-O a 205 | 365 | 205 | 330; 6 ejes N-S a 205 | 170 | 125 | 343 | 182)', nuevo=f'{W/100:.2f} x {L/100:.2f} m por fuera (antes 10,55 x 15,75); ejes 1-5 a {xA[1]-xA[0]:.1f} | {xA[2]-xA[1]:.1f} | {xA[3]-xA[2]:.1f} | {xA[4]-xA[3]:.0f} y A-E a 200 | {yB-yA[1]:.0f} | {yC-yB:.0f} | {yC2-yC:.0f} | {yA[5]-yC2:.0f} | 200'.replace('.', ','), por='planta de Gabriel (medidas terminadas) · ejes: propuesta'),
        dict(que='Búnker', original='5,00 x 10,80 interiores (muros 1.a, 3.a, E1, A1), 2,72 de alto, hueco de 3,05 x 1,00 junto al muro A1', nuevo=f'{hormigon["interior"]["largo"]/100:.2f} x {hormigon["interior"]["ancho"]/100:.2f} interiores, 2,80 de alto, hueco de escalera de {hormigon["escalera"]["ancho"]/100:.2f} x {hormigon["escalera"]["largo"]/100:.2f} junto al muro oriente', por='Gabriel'),
        dict(que='Muro sur del búnker', original='—', nuevo='coincide con el tabique cafetería/estudio (eje B) y recibe sus 5 pilares', por='planta de Gabriel'),
        dict(que='Losa del búnker', original='e=20, luz 5,00 (ø10@20 N-S, ø8@20 E-O), VHA 25/40 en 2.a', nuevo='e=20, luz 6,00 (+20 %, +44 % de momento), VHA 25/40 en el eje 3 y viga de borde en la escalera', por='para el ingeniero'),
        dict(que='Marcos interiores', original='1.b y 1.c: pilares solo en F1 y A1 (10,25 m), cordón RECT 150x100x3 a +400, viga 200x150x5, puntales 150x100x3 cada 171', nuevo=f'ejes 2, 3 y 4: pilares en A, B y E; luces de {(yB-yA[0])/100:.2f} y {(yA[6]-yB)/100:.2f} m con el mismo esquema'.replace('.', ','), por='propuesta'),
        dict(que='Largo del estudio', original='9,00 (planta del 11-10); 15,75 por fuera', nuevo=f'10,50: +1,50 al sur para que la bodega quede de 4,30 (los parlantes y la ventana sur se corren con el muro); edificio {W/100:.2f} × {L/100:.2f} por fuera; eje C2 nuevo en el tabique cabina/bodega para que ningún tramo N-S pase de 4,45'.replace('.', ','), por='Gabriel (14-10-2026): "agreguemos 1,5 metro más… la bodega yo creo que quedará chica… el estudio quedará más grande nomás"'),
        dict(que='Franja oriente: baño, cabina y bodega', original='baño 2,50 x 4,10 y bodega 2,50 x 4,65 (planta del 11-10)', nuevo=f'baño 2,50 × 1,90, cabina de grabación 2,50 × 3,80 (cielo bajado a 3,00, ciega, tabiques dobles dentro de los 25) y bodega 2,50 × 2,80; el eje C pasa al tabique baño/cabina y se agrega el eje C2 en el tabique cabina/bodega (B–C {yC-yB:.0f}, C–C2 {yC2-yC:.0f}, C2–D {yA[5]-yC2:.0f}), cada uno con su CF 25/40, su pilar PM3 de 4 × C y una cruz E-O en 4-5; la puerta de la bodega va en su extremo norte y la de la cabina en el suyo, lejos de la posición de escucha', por='Gabriel (14-10-2026): "2,5 x 4,1 será como un baño turco"; cabina al medio, ciega'),
        dict(que='Tabique del búnker y medidas terminadas', original='medidas interiores entre caras de hormigón (muros y tabiques de 25)', nuevo=f'tabique de {T:.0f} por dentro de los 4 muros de hormigón del búnker (del radier a la losa): el búnker mide {hormigon["interior"]["terminado"]["ancho"]/100:.2f} × {hormigon["interior"]["terminado"]["largo"]/100:.2f} terminado ({hormigon["interior"]["ancho"]/100:.2f} × {hormigon["interior"]["largo"]/100:.2f} entre muros); arriba muros y tabiques de 25 terminado, sin tabique extra; para eso los ejes 1–5 pasan de 10,30 a 10,50 y A–B de 6,25 a 6,45 → {W/100:.2f} × {L/100:.2f} m por fuera (antes 10,55 × 15,75); la cafetería queda de 10,25 × 6,20 y el estudio de 7,50 × 9,00'.replace('.', ','), por='Gabriel (14-10-2026): "el búnker tiene que medir lo que dijimos"; opción 1'),
        dict(que='Vigas E-O y cordones', original='todas a +400/+410 (lámina 05); en el marco alto (A1) los pilares pasan la viga y siguen hasta la viga inclinada', nuevo=f'+{Z_CORDON[0]:.0f}/+{Z_CORDON[1]:.0f} en A, B, C y E: {T_PISO + T_CIELO:.1f} cm más arriba, para que el cielo terminado quede a 4,00 sobre el porcelanato (piso {T_PISO:.1f} + cielo {T_CIELO:.1f}); los pilares crecen lo mismo; en B y E pasan la viga y siguen hasta la viga inclinada'.replace('.', ','), por='Gabriel (13-10-2026): 4,00 libres terminados; avisar al ingeniero'),
        dict(que='Fachadas laterales', original='1.a, 2.a, 3.a: pilares cada 1,25–3,43 m, viga 200x150x3, cruces en los tramos de 2,05 y 1,82', nuevo='ejes 1 y 5: pilares en A, A2, B, C, D, E; cruces en A-A2 y D-E (2,00 m)', por='propuesta'),
        dict(que='Pilares', original='21 (13 de 15×15 y 8 de 15×10 en la planta de cubierta)', nuevo=f'{sum(1 for mb in M if mb["c"] == "pilar")}; ninguno dentro de los recintos', por='propuesta'),
        dict(que='Rigidez E-O', original='sin cruces E-O en las láminas', nuevo='cruces en los muros ciegos: tabique baño/cabina (C, 4-5) y fachada sur (1-2 y 4-5), y una sola diagonal en el tabique cafetería/baño (B, 4-5) por la puerta del baño; el vidrio entre cafetería y estudio queda libre', por='propuesta: revisar'),
        dict(que='Costaneras', original='CA 100x50x15x3 @61, 20 por línea; colgadores ø10 en los paños de 3,65 y 3,30', nuevo=f'mismo perfil y paso, {n} por línea; paños de ≤ {max(xA[i+1]-xA[i] for i in range(4))/100:.2f} m: sin colgadores', por='propuesta'),
        dict(que='Fundaciones fuera del búnker', original='sobrecimiento 25 x 50 + cimiento corrido 80 x 25 (de −50 a −75) bajo el perímetro, CF 25/40 bajo el eje interior 2.a, radier 10 sobre poliestireno 10 y relleno 15 (lámina 01 rev 1)', nuevo='lo mismo: sobrecimiento y cimiento corrido bajo las fachadas fuera del búnker, CF 25/40 bajo los tabiques con pilares (ejes 4 y C), radier igual', por='dato del ingeniero, aplicado a la planta nueva'),
        dict(que='Base del búnker', original='zapata corrida de 100 x 30 bajo los muros (ø16@20 + 4ø10), radier 10 sobre relleno granular 10, emplantillado G5', nuevo='igual, con el búnker nuevo (todo 8 cm más abajo por los 2,80 de alto)', por='dato'),
        dict(que='Placas base', original='PLb 200 x 200 x 8 en todos los pilares, anclajes 1+1 ø3/4 en horquilla (L=1200: 140 + 430 + ganchos de 100), Est ø8@20', nuevo='igual, en los 22 pilares (los ganchos doblan hacia adentro: el ancla mide 140 y cabe en el muro de 25)', por='dato'),
        dict(que='CF bajo los tabiques', original='CF 25/40 bajo el eje interior 2.a, de −10 a −50 bajo el radier (3ø12 + 2ø10 + 3ø12, Est ø10@25)', nuevo='el mismo CF 25/40 bajo los ejes 4 y C; el anclaje de 43 de las placas termina dentro del CF con 7 de recubrimiento', por='dato'),
        dict(que='Viga inclinada y viga E-O', original='lámina 04: viga inclinada con la cara inferior a +400 en F1; lámina 05: apoyada sobre la viga E-O 100x100 de +401 a +411', nuevo=f'como la lámina 05 pero {T_PISO + T_CIELO:.0f} cm más arriba: viga E-O de +{Z_CORDON[0]:.0f} a +{Z_CORDON[1]:.0f} en todos los marcos; al norte (lado bajo) los pilares terminan a +{Z_CORDON[0]:.0f} y la viga inclinada apoya sobre la viga E-O; en B y E los pilares pasan la viga y siguen hasta la viga inclinada, como el marco A1', por='dato (lámina 05) + terminaciones de Gabriel'),
        dict(que='Niveles del búnker', original='2,72 libres; radier a −292 por cotas (rótulos −272 / −305 / −342, inconsistentes)', nuevo=f'2,80 libres terminados = {BUNKER_H:.0f} de obra gruesa (piso {T_PISO:.1f} + cielo {T_CIELO:.1f}); losa 0 / −20, piso de obra gruesa −{BUNKER_H + 20:.0f}, radier −{BUNKER_H + 30:.0f}, zapata −{BUNKER_H + 40:.0f} / −{BUNKER_H + 70:.0f}, sello −{BUNKER_H + 80:.0f}'.replace('.', ','), por='Gabriel (13-10-2026): 2,80 terminados; el detalle baja 15 cm respecto del original'),
        dict(que='Costaneras en el alero', original='la primera a 61 del eje: 19 dentro de la punta del alero de 80, con el soporte C 150x50x3 en la punta', nuevo='igual: la primera a 19 de la punta (alero de 100) y luego cada 61', por='dato'),
        dict(que='Enfierradura', original='muros DM ø12@15 / ø10@20, losa ø10@20 + ø8@20, VHA 3ø12+2ø10+3ø16, CF 3ø12+2ø10+3ø12', nuevo='las mismas armaduras, en el modelo 3D barra por barra (capa Enfierradura)', por='dato; largos y cantidades del modelo'),
        dict(que='Acero', original='—', nuevo=f'{tot} kg de perfiles en el modelo (sin placas ni pérdidas)', por='cubicación del modelo'),
    ]
    preguntas = [
        f'Marcos interiores de {(yA[6] - yB) / 100:.2f} m (ejes 2, 3 y 4, tramo B-E):'.replace('.', ',') + ' ¿sirve el mismo esquema de 1.b/1.c (cordón 150x100x3 + viga 200x150x5 + puntales), que salvaba 10,25?',
        f'Losa del búnker: con {hormigon["interior"]["largo"]/100:.2f} m de luz entre muros (antes 5,00), ¿se mantiene e=20 con más armadura o conviene e=25? ¿Basta una VHA 25/40 al centro?'.replace('.', ','),
        'Rigidez E-O: las láminas no muestran cruces E-O. Con vidrio entre cafetería y estudio y ventanas al patio, se proponen cruces en los muros ciegos del lado oriente y de la fachada sur. ¿Van bien, o prefiere marcos rígidos? En el tabique cafetería/baño (B, 4-5) cabe una sola diagonal por la puerta del baño: ¿sirve, o conviene que el baño se abra desde el estudio (eje 4) y poner la cruz completa?',
        f'Ventanas: vidrio de piso terminado a cielo terminado (4,00) en los dos tramos centrales de la fachada norte y del tabique B (2-3 y 3-4) y en el tramo 2-3 de la fachada sur, todas entre pilares; la viga E-O queda a +{Z_CORDON[0]:.0f}/+{Z_CORDON[1]:.0f}, sobre el cielo. ¿Los pilares reciben el marco directamente o hacen falta montantes y un travesaño a +3,00?',
        f'Terminaciones: la estructura va {T_PISO + T_CIELO:.0f} cm más arriba que sus láminas (vigas E-O y cordones a +{Z_CORDON[0]:.0f}/+{Z_CORDON[1]:.0f}, pilares de {Z_CORDON[0]/100:.2f} en el lado bajo) y el radier del búnker {T_PISO + T_CIELO:.0f} cm más abajo (piso de obra gruesa a −{BUNKER_H + 20:.0f}, sello a −{BUNKER_H + 80:.0f}), para que queden 4,00 y 2,80 libres con porcelanato ({T_PISO:.1f}) y cielo de yeso cartón ({T_CIELO:.1f}). ¿Algún reparo?'.replace('.', ','),
        'Escalera del búnker en hormigón, con su caja de muros: ¿muro de 23 con la misma armadura DM del búnker, y losa de escalera de cuánto?',
    ]
    out = dict(
        fuente='Adaptación de las láminas 03, 04 y 05 del ingeniero (proyecto del estudio, abril 2026, leídas de sus vectores) a la planta de Gabriel (medidas interiores, 2026-10-12); propuesta para revisión del ingeniero, no es un cálculo',
        marco='cm del marco de la app; z = 0 en el piso del nivel 1 de la casa; el piso del estudio (NPOG 0,00 del ingeniero) está en z = %s' % z0,
        z_piso=z0, ejes=ejes, perfiles={k: PERFILES[k] for k in sorted(set(mb['p'] for mb in M))}, miembros=M,
        hormigon=hormigon, fierros=fierros, cubicacion_hormigon=cub_hormigon, vanos=V, interior=interior, techo=techo, cielo=cielo,
        cubicacion=cubicacion, total_kg=tot, cambios=cambios, preguntas=preguntas,
        parametros=dict(muro=MURO, tabique=T, h_pilar=H_PILAR, z_viga_inf=Z_CORDON[0], terminaciones=dict(piso=T_PISO, cielo=T_CIELO, libre=LIBRE, capas=E['alturas'].get('capas', {}), dato=E['alturas'].get('dato_terminaciones', '')), pendiente=PEND, alero_ns=ALERO_NS, alero_eo=ALERO_EO, paso_costanera=PASO_COST, paso_puntal=PASO_PUNTAL, h_ventana=H_VENTANA,
                        bunker=dict(losa=BUNKER_LOSA, muro=BUNKER_MURO, radier=BUNKER_RADIER, fundacion=BUNKER_FUND, alto=BUNKER_H)),
    )
    open(salida, 'w').write('const DATA_ESTUDIO_EST = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
    clases = {}
    for mb in M: clases[mb['c']] = clases.get(mb['c'], 0) + 1
    print(f'{salida}: {len(M)} piezas {clases} · acero {tot} kg · búnker {hormigon["interior"]["ancho"]/100:.2f} x {hormigon["interior"]["largo"]/100:.2f} x {BUNKER_H/100:.2f} m · {len(V)} vanos · hormigón {cub_hormigon["total_m3"]} m³ · fierro {cub_hormigon["total_kg"]} kg en {len(fierros)} familias')
    for c in cubicacion: print(f"   {c['perfil']:16s} {c['metros']:7.1f} m  {c['kg']:5d} kg")

if __name__ == '__main__':
    main(*sys.argv[1:4])
