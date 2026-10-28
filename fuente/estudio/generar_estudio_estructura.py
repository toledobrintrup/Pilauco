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
    'RECT 200x150x6': dict(forma='tubo_rect', h=20, b=15, t=0.6),
    'CA 100x50x15x2': dict(forma='CA', h=10, b=5, c=1.5, t=0.2),
    'CUAD 100x100x3': dict(forma='tubo_rect', h=10, b=10, t=0.3),
    'C 150x50x3':     dict(forma='C', h=15, b=5, t=0.3),
    'C 150x50x4':     dict(forma='C', h=15, b=5, t=0.4),
    'RECT 150x50x3':  dict(forma='tubo_rect', h=15, b=5, t=0.3),
    'CA 100x50x15x3': dict(forma='CA', h=10, b=5, c=1.5, t=0.3),
    'FE 16':          dict(forma='barra', d=1.6),
    'FE 22':          dict(forma='barra', d=2.2),
    'FE 10':          dict(forma='barra', d=1.0),
}
PESO = {'C 150x50x3': 5.65, 'C 150x50x4': 7.47, 'FE 22': 2.98, 'CUAD 100x100x3': 8.94, 'CUAD 150x150x4': 18.0, 'CUAD 150x150x5': 22.2, 'FE 16': 1.58,
        'RECT 150x100x3': 11.3, 'RECT 200x150x3': 16.0, 'RECT 200x150x5': 26.1, 'RECT 200x150x6': 31.0, 'CA 100x50x15x3': 4.95, 'CA 100x50x15x2': 3.38, 'RECT 150x50x3': 9.12, 'FE 10': 0.62}

h2 = lambda p: PERFILES[p]['h'] / 2   # medio alto del perfil: las líneas de los miembros van por el EJE del perfil (como en estructura.js)

# ---------- lo que dicen las láminas (dato) ----------
H_PILAR = 400.0        # cara inferior de la viga E-O en el lado bajo; el ingeniero la tiene a +400 (lámina 04: +400 en F1): main() la sube con las terminaciones (4,00 libres + piso + cielo)
PEND = 0.035           # pendiente: rotulada 3,5 % (dibujada 4,5 %); Gabriel pide la de la casa, 3,5 %
ALERO_NS = 80.0        # aleros del ingeniero: norte y sur (1.186 = 1.025 + 80 + 80); se reemplazan por los de estudio.json si vienen (Gabriel: como la casa)
ALERO_EO = 52.0        # aleros del ingeniero: oriente y poniente (cota 52)
PASO_COST = 61.0       # costaneras CA 100x50x15x3 cada 61
P_REFUERZO = {'P-1C': 'CUAD 150x150x4'}   # pilar 1C reforzado (cabina de 4,15, 24-10-2026): mismo perfil que los PM2, ya usado en el proyecto
PASO_PUNTAL = 171.0    # puntales RECT 150x100x3 cada 171 desde donde el cordón se separa de la viga
GAP_PUNTAL = 7.0       # el primer puntal del original tiene 7 cm
Z_CORDON = (400.0, 410.0)   # cordón RECT 150x100x3 y vigas E-O de +400 a +410 en la lámina 04; main() lo sube con las terminaciones
BUNKER_LOSA = 25.0     # losa de techo del búnker: 20 en la lámina 03; 25 desde la revisión estructural del 23-10-2026 (Gabriel: "haz los cambios, me cuadra todo")
BUNKER_MURO = 30.0     # muros MHA: e=25 en las láminas; 30 desde la revisión del 23-10-2026 (crecen hacia afuera: el interior no cambia)
BUNKER_RADIER = 0.0    # sin radier aparte desde el 15-10-2026: el piso es la cara superior de la losa de fundación (el original tenía radier 20 sobre la zapata)
BUNKER_FUND = 35.0     # losa de fundación armada bajo todo el búnker, unida a los muros, 37,5 más ancha que ellos (ingeniero vía Gabriel, 15-10-2026: 30; 35 desde la revisión del 23-10-2026)
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
                nota='Ejes 1-5 (el 4 sobre el tabique estudio/baño-bodega) y A-E (A en la fachada del patio): B sobre el tabique '
                     'cafetería/estudio (sobre el muro del búnker), C sobre el tabique baño/cabina, C2 sobre el tabique cabina/bodega; A2 y D a 2,00 m de las fachadas A y E, '
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
            apoyo = {'A': 'sobre el muro del eje A del búnker', 'B': 'sobre el muro del eje B del búnker', 'E': 'sobre el sobrecimiento de la fachada del eje E'}[yn]
            # lámina 05: en el marco bajo (F) el pilar termina a +400 bajo la viga E-O y sobre ella apoya la viga inclinada; en el marco alto (A1) el pilar
            # pasa la viga E-O de +400/+410 y sigue hasta la cara inferior de la viga inclinada (+447). Opción A de Gabriel (12-10-2026): igual aquí.
            zt = z_viga(y) if z_viga(y) - 10 > Z_CORDON[1] + 0.5 else Z_CORDON[0]
            if yn == 'A' and xn in ('1', '5'): zt = z_viga(y)   # revisión 23-10-2026: en las esquinas 1A y 5A el pilar pasa la viga E-O y llega a la viga inclinada (placa de tope), para que el corte de la cruz N-S no atraviese el tubo de 3 mm
            d_t = (f'llega a +{Z_CORDON[0]:.0f}, bajo la viga 100x100 de +{Z_CORDON[0]:.0f}/+{Z_CORDON[1]:.0f}, y sobre ella apoya la viga inclinada (lámina 05, marco F; allá a +400/+410, aquí más arriba por las terminaciones)' if zt == Z_CORDON[0]
                   else f'pasa por la viga 100x100 de +{Z_CORDON[0]:.0f}/+{Z_CORDON[1]:.0f} y sigue hasta la cara inferior de la viga inclinada (+{zt:.0f}), como los pilares del marco A1 de la lámina 05')
            m(f'P-{xn}{yn}', 'pilar', perfil, (x, y, 0), (x, y, zt), f'{pm} eje {xn} x {yn}, {apoyo}; {d_t}', alma='Y')
    for yn in ('A2', 'C', 'C2', 'D'):
        y = yA[yN.index(yn)]
        for xn, x in (('1', xA[0]), ('5', xA[4])):
            apoyo = 'sobre el muro del búnker' if y < yB else 'sobre zapata aislada'
            apoyo = 'sobre el muro del búnker' if y < yB else 'sobre el sobrecimiento'
            pp = P_REFUERZO.get(f'P-{xn}{yn}', 'RECT 150x100x3')
            m(f'P-{xn}{yn}', 'pilar', pp, (x, y, 0), (x, y, z_viga(y)), f'PM3 eje {xn} x {yn}, pilar intermedio de la fachada lateral, {apoyo}; el lado de 150 va perpendicular a la fachada (toma el viento por su eje fuerte; revisión 23-10-2026)' + (f'; {pp} desde el 24-10-2026: con la cabina de 4,15 el tramo C–C2 creció a 4,40 y este pilar recibe más viento (con 150x100x3 daba 1,08)' if pp != 'RECT 150x100x3' else ''), alma='X')
    m('P-4C', 'pilar', 'RECT 150x100x3', (xA[3], yC, 0), (xA[3], yC, z_viga(yC)), 'PM3 eje 4 x C, en el encuentro de los tabiques estudio/baño/cabina (recibe la cruz del eje C), sobre el CF-4 y su zapata corrida ZC-4 de 45 x 80 (opción A, 28-10-2026; antes un dado de 1,40 x 1,40)', alma='Y')
    m('P-4C2', 'pilar', 'RECT 150x100x3', (xA[3], yC2, 0), (xA[3], yC2, z_viga(yC2)), 'PM3 eje 4 x C2, en el encuentro de los tabiques estudio/cabina/bodega (recibe la diagonal del tabique C2 en su pie), sobre el CF-4 y su zapata corrida ZC-4 de 45 x 80 (opción A, 28-10-2026; antes un dado de 1,40 x 1,40)', alma='Y')
    # ---------- vigas E-O CUAD 100x100x3: de +400 a +410 en A, B, E y C (4-5), como la lámina 05 (opción A de Gabriel, 12-10-2026) ----------
    for yn, y, tramos in (('A', yA[0], range(4)), ('B', yB, range(4)), ('E', yA[6], range(4)), ('C', yC, [3]), ('C2', yC2, [3])):
        for i in tramos:
            zv = Z_CORDON_EJE
            arriba = 'sobre ella apoya la viga inclinada' if abs(z_viga(y) - Z_CORDON[1]) < 0.5 else f'los pilares siguen hasta la viga inclinada (+{z_viga(y):.0f})'
            # uniones UM (27-10-2026): en los pilares 2 y 3 de los ejes B y E la viga llega a la plancha lateral de la unión del cordón (detalle UM)
            um = [xN[k] for k in (i, i + 1) if yn in ('B', 'E') and xN[k] in ('2', '3')]
            um_t = (f'; en el pilar {" y en el ".join(um)}: 8 mm más corta, soldada a la cara exterior de la plancha de la unión UM con filete 3 arriba y en los 2 costados' if um else '')
            m(f'VT-{yn}-{xN[i]}{xN[i+1]}', 'viga', 'CUAD 100x100x3', (xA[i], y, zv), (xA[i + 1], y, zv), f'viga 100x100 a +{(Z_CORDON[0]/100):.2f}/+{(Z_CORDON[1]/100):.2f} entre pilares {xN[i]} y {xN[i+1]} del eje {yn} (lámina 05); {arriba}{um_t}')
    # ---------- marcos N-S: cordón RECT 150x100x3 + viga inclinada + puntales (como 1.b y 1.c) ----------
    y_ini, y_fin = yA[0] - ALERO_NS, yA[6] + ALERO_NS   # puntas de los aleros (eje del pilar ± alero)
    for xn, x in zip(xN, xA):
        if not lateral(xn):
            for (ya, yb) in ((yA[0], yB), (yB, yA[6])):
                # ejes 2 y 3 (marcos de 10,75): unión de momento UM con el pilar en B y en E (el ingeniero, V121: «reforzar unión de momento en pilares con plancha
                # e=8 mm … soldadura AWS 6011»; diseño 27-10-2026); en A y en el eje 4 el cordón queda articulado
                um_c = '' if xn not in ('2', '3') else (f'; en el pilar B soldado a momento con 2 planchas laterales PL 8×150 (detalle UM-{xn}B); en A, articulado' if ya == yA[0]
                                                         else f'; en los pilares B y E soldado a momento con 2 planchas laterales PL 8×150 (detalles UM-{xn}B y UM-{xn}E)')
                m(f'VC-{xn}-{int(ya)}', 'viga', 'RECT 150x100x3', (x, ya, Z_CORDON_EJE), (x, yb, Z_CORDON_EJE), f'cordón horizontal RECT 150x100x3 de +{(Z_CORDON[0]/100):.2f} a +{(Z_CORDON[1]/100):.2f} (acostado), eje {xn}, {ya:.0f}..{yb:.0f} (como 1.b y 1.c del original){um_c}', acostado=True)   # acostado: el alto de 15 queda horizontal y el cordón va de +4,00 a +4,10 (lámina 04)
        perfil = 'RECT 200x150x3' if lateral(xn) else ('RECT 200x150x6' if xn in ('2', '3') else 'RECT 200x150x5')   # ejes 2 y 3: 6 mm desde la revisión del 23-10-2026 (uniones de los puntales dentro de la norma)
        m(f'VI-{xn}', 'cabio', perfil, (x, y_ini, z_viga(y_ini) + h2(perfil)), (x, y_fin, z_viga(y_fin) + h2(perfil)), f'viga inclinada de techo, eje {xn}, 3,5 % subiendo hacia el eje E, aleros de {ALERO_NS:.1f}; cara inferior a +{z_viga(yA[0]):.0f} en A'.replace('.', ','))
        if not lateral(xn):
            for (ya, yb) in ((yA[0], yB), (yB, yA[6])):
                y = ya + PASO_PUNTAL
                ys_p = []
                while y < yb - 60:
                    junto_pilar = any(mb['c'] == 'pilar' and abs(mb['a'][0] - ap(x, y, 0)[0]) < 1 and abs(mb['a'][1] - ap(x, y, 0)[1]) < 16 for mb in M)   # a menos de 16 del eje de un pilar del mismo eje chocaría con él (pasó en la V119 con PT-4-1341 y P-4C2): ahí sobra
                    if z_viga(y) - Z_CORDON[1] >= GAP_PUNTAL and not junto_pilar: ys_p.append(y)
                    y += PASO_PUNTAL
                for k, y in enumerate(ys_p):
                    gap = z_viga(y) - Z_CORDON[1]
                    # revisión 23-10-2026: en los ejes 2 y 3, tramo B-E (10,75 m), los puntales que no son el central pasan a CUAD 150x150x5 (con 150x100x3 no aguantaban la flexión Vierendeel ni sus uniones)
                    fuerte = xn in ('2', '3') and ya == yB and k != len(ys_p) // 2
                    pp = 'CUAD 150x150x5' if fuerte else 'RECT 150x100x3'
                    m(f'PT-{xn}-{int(y)}', 'puntal', pp, (x, y, Z_CORDON[1]), (x, y, z_viga(y)), f'puntal {pp} entre cordón y viga inclinada, eje {xn}, {gap:.0f} cm' + ('; soldadura de penetración completa en todo el contorno y planchas laterales de 6 × 250 mm en la viga y en el cordón en sus nudos (uniones fuera del rango de AISC con paredes delgadas)' if fuerte else ''))
    # ---------- costaneras CA 100x50x15x3 cada 61 de alero a alero, continuas sobre las 5 vigas ----------
    x_ini, x_fin = xA[0] - ALERO_EO, xA[4] + ALERO_EO
    n = int(math.floor((y_fin - y_ini - 38) / PASO_COST)) + 1   # la primera a 19 de la punta del alero, como el original (61 del eje con alero de 80)
    for i in range(n):
        y = y_ini + 19 + i * PASO_COST
        z = z_viga(y) + PERFILES['RECT 200x150x5']['h'] + h2('CA 100x50x15x3')   # apoyada sobre la viga inclinada
        m(f'CO-{i+1:02d}', 'costanera', 'CA 100x50x15x3', (x_ini, y, z), (x_fin, y, z), f'costanera {i+1} de {n}, y = {y:.0f}')
    for yn, y in (('norte', y_ini), ('sur', y_fin)):
        m(f'SA-{yn}', 'otro', 'RECT 150x50x3', (x_ini, y, z_viga(y) + h2('RECT 200x150x5')), (x_fin, y, z_viga(y) + h2('RECT 200x150x5')), f'soporte del alero del eje {"A" if yn == "norte" else "E"} en la punta de las vigas inclinadas: RECT 150x50x3 (el original lleva un C 150x50x3; revisión 23-10-2026: el C abierto no aguanta la torsión del voladizo de esquina)')
    # ---------- cruces C 150x50x3 (tramos de 2 m, como F1-E3 y A2-A1) ----------
    # Revisión 23-10-2026: el punto de trabajo de cada diagonal va a los nudos: abajo, a la placa base (cartela soldada a la placa);
    # arriba, a la viga E-O en las cruces E-O y a la cara inferior de la viga inclinada en las cruces N-S de las fachadas (antes
    # terminaban en +4,03, bajo la viga, y doblaban los pilares como una rodilla).
    UNION_X = '; en cada extremo, cartela de 8 mm soldada a la placa base o a la viga (no a la cara del tubo de 3 mm) con 4 pernos M16 A325 al alma del C'
    def cruz(id_, a, b, d, ns=False, perfil='C 150x50x3'):
        (xa, ya), (xb, yb) = a, b; d = d + UNION_X
        za = z_viga(ya) if ns else Z_CORDON_EJE; zb = z_viga(yb) if ns else Z_CORDON_EJE
        m(f'{id_}a', 'diagonal', perfil, (xa, ya, 0), (xb, yb, zb), d)
        m(f'{id_}b', 'diagonal', perfil, (xa, ya, za), (xb, yb, 0), d)
    for xn, x in (('1', xA[0]), ('5', xA[4])):
        cruz(f'X-{xn}-AA2', (x, yA[0]), (x, yA[1]), f'cruz en la fachada del eje {xn}, tramo A-A2 (2,00 m), como F1-E3 del original; de la placa base a la viga inclinada', ns=True)
        cruz(f'X-{xn}-DE', (x, yA[5]), (x, yA[6]), f'cruz en la fachada del eje {xn}, tramo D-E (2,00 m), como A2-A1 del original; de la placa base a la viga inclinada', ns=True)
        # sismo con la masa de los tabiques y la torsión accidental (ingeniero, 27-10-2026: "HACERLO"): la deriva en A-E daba 1,13 en el centro de masas; con una cruz más
        # en cada fachada lateral, en el tramo ciego C-C2 (4,40 m: a 45°, rinde mucho más que las de 2,00), queda en 0,59
        cruz(f'X-{xn}-CC2', (x, yC), (x, yC2), f'cruz en la fachada del eje {xn}, tramo C-C2 (4,40 m, muro ciego {"del estudio" if xn == "1" else "de la cabina"}): sismo con tabiques y torsión accidental (27-10-2026); de la placa base a la viga inclinada', ns=True)
    # en el tabique cafetería/distribuidor (B, 4-5) van la puerta del distribuidor junto al eje 4 y la de la escalera junto al 5 (23-10-2026): no cabe diagonal;
    # la fuerza de esa línea la toman la cruz de A 4-5, la de C 4-5 y la diagonal de C2 4-5 a través de los tensores del techo
    cruz('X-A-45', (xA[3], yA[0]), (xA[4], yA[0]), 'cruz en la fachada del eje A, tramo 4-5 (muro ciego de la cocina y la escalera, sin vidrio): revisión 23-10-2026, sin ella el techo se movía 2 a 4 cm con sismo en 1–5; C 150x50x4 desde el 27-10-2026 (es la única cruz 1–5 del lado de la cafetería: con tabiques y torsión llega a 15 t, y en el alma de 3 mm los 4 pernos M16 daban 14 t al aplastamiento)', perfil='C 150x50x4')
    cruz('X-C-45', (xA[3], yC), (xA[4], yC), 'cruz en el tabique baño/cabina (eje C, tramo 4-5, muro ciego)')
    # tabique cabina/bodega (C2, 4-5): desde el 24-10-2026 se entra a la bodega desde la cabina por una puerta de 0,80 junto al eje 5 (Gabriel: "así evitamos esa puerta al lado
    # de los parlantes"): queda una sola diagonal, de la placa base de 4C2 a la viga en 5C2, que pasa sobre la puerta (trabaja solo a tracción; la deriva en 1–5 quedaba en 0,94; con tabiques y torsión accidental, 0,87 desde el 27-10-2026)
    m('X-C2-45a', 'diagonal', 'C 150x50x3', (xA[3], yC2, 0), (xA[4], yC2, Z_CORDON_EJE), 'diagonal única en el tabique cabina/bodega (eje C2, tramo 4-5): la puerta de la bodega va junto al eje 5, bajo la diagonal' + UNION_X)
    cruz('X-E-12', (xA[0], yA[6]), (xA[1], yA[6]), 'cruz en la fachada del eje E, tramo 1-2 (muro ciego de los parlantes)')
    cruz('X-E-45', (xA[3], yA[6]), (xA[4], yA[6]), 'cruz en la fachada del eje E, tramo 4-5 (bodega, muro ciego)')
    # faja entre la viga E-O y la viga inclinada en el eje E (27-10-2026, sismo con tabiques y torsión accidental): ahí la viga inclinada va 60 cm sobre la viga E-O y el techo le
    # pasaba la fuerza a las cruces E 1-2 y E 4-5 a través de esa punta de pilar en flexión (el techo se movía 3 veces lo que la viga E-O); una X de tensores Fe 22 en la faja,
    # del nudo viga E-O–pilar a la cabeza del otro pilar, se la lleva directo. En C 4-5 (35 cm) no se pone: la cruz C toma más y el dado de 4C se levantaba 7 mm
    def faja(id_, xa, xb, y, d):
        za, zb = z_viga(y), Z_CORDON_EJE
        m(f'{id_}a', 'diagonal', 'FE 22', (xa, y, zb), (xb, y, za), d)
        m(f'{id_}b', 'diagonal', 'FE 22', (xa, y, za), (xb, y, zb), d)
    UNION_F = '; tensor Fe 22 con templador, a cartelas de 8 mm soldadas a la cabeza del pilar (bajo la viga inclinada) y al nudo de la viga E-O con el pilar; trabaja solo a tracción'
    faja('XF-E-12', xA[0], xA[1], yA[6], f'X de tensores en la faja de {z_viga(yA[6]) - Z_CORDON[1]:.0f} cm entre la viga E-O y la viga inclinada, eje E, tramo 1-2 (sobre la cruz X-E-12)' + UNION_F)
    faja('XF-E-45', xA[3], xA[4], yA[6], f'X de tensores en la faja de {z_viga(yA[6]) - Z_CORDON[1]:.0f} cm entre la viga E-O y la viga inclinada, eje E, tramo 4-5 (sobre la cruz X-E-45)' + UNION_F)
    # ---------- tensores Fe 16 en el plano del techo: X en los paños extremos completos y en los vanos extremos del resto ----------
    panos = [(yA[0], yA[1]), (yA[1], yB), (yB, yC), (yC, yC2), (yC2, yA[5]), (yA[5], yA[6])]
    nudos = set()
    for pi, (ya, yb) in enumerate(panos):
        vanos = range(4) if pi in (0, len(panos) - 1) else (0, 3)
        for i in vanos:
            xa, xb = xA[i], xA[i + 1]; zt = lambda y: z_viga(y) + 20
            # paños A2-B y B-C (la cercha del techo que lleva el sismo 1–5 de la línea B, con el vidrio, a las cruces de A y C): Fe 22 desde el 27-10-2026
            fe = 'FE 22' if pi in (1, 2) else 'FE 16'; nfe = fe.replace('FE', 'Fe')
            m(f'T-{xN[i]}{xN[i+1]}-{int(ya)}a', 'tensor', fe, (xa, ya, zt(ya)), (xb, yb, zt(yb)), f'tensor {nfe} del techo, vano {xN[i]}-{xN[i+1]}, paño {ya:.0f}..{yb:.0f}')
            m(f'T-{xN[i]}{xN[i+1]}-{int(ya)}b', 'tensor', fe, (xb, ya, zt(ya)), (xa, yb, zt(yb)), f'tensor {nfe} del techo, vano {xN[i]}-{xN[i+1]}, paño {ya:.0f}..{yb:.0f}')
            nudos.add((i, ya)); nudos.add((i, yb))
    # puntales de techo CUAD 100x100x3 en cada línea de nudos de los tensores, entre vigas inclinadas, a la altura de su eje (revisión 23-10-2026:
    # las costaneras no caen en esos nudos y la cercha del techo quedaba sin montante; en A la cuerda real era la viga E-O, 20-30 cm más abajo)
    yNom = dict(zip(yA, yN))
    for (i, y) in sorted(nudos):
        zc_ = z_viga(y) + h2('RECT 200x150x5')
        m(f'PR-{yNom[y]}-{xN[i]}{xN[i+1]}', 'puntal', 'CUAD 100x100x3', (xA[i], y, zc_), (xA[i + 1], y, zc_), f'puntal de techo CUAD 100x100x3 en la línea {yNom[y]}, vano {xN[i]}-{xN[i+1]}: montante de la cercha de tensores, soldado al alma de las vigas inclinadas')
    # remate de borde de los aleros oriente y poniente: amarra las puntas de las costaneras (revisión 23-10-2026)
    yc0, yc1 = y_ini + 19, y_ini + 19 + (n - 1) * PASO_COST
    for nm_, x_ in (('poniente', x_ini), ('oriente', x_fin)):
        zr = lambda y: z_viga(y) + PERFILES['RECT 200x150x5']['h'] + h2('CA 100x50x15x3')
        m(f'RB-{nm_}', 'otro', 'CA 100x50x15x2', (x_, yc0, zr(yc0)), (x_, yc1, zr(yc1)), f'remate de borde (tapacán) CA 100x50x15x2 del alero del eje {"1" if nm_ == "poniente" else "5"}: amarra las puntas de las costaneras en voladizo')

    # ---------- hormigón del búnker ----------
    bk = E['bunker']['pts']; bx0, by0, bx1, by1 = bk[0][0] - BUNKER_MURO, bk[0][1] - BUNKER_MURO, bk[1][0] + BUNKER_MURO, bk[2][1] + BUNKER_MURO   # exterior 0..1055 x 0..650
    z_losa_inf = -BUNKER_LOSA; z_piso = z_losa_inf - BUNKER_H; z_rad_inf = z_piso - BUNKER_RADIER; z_fund_inf = z_rad_inf - BUNKER_FUND
    def rect(x0, y0, x1, y1): return [ap(x0, y0, 0)[:2], ap(x1, y0, 0)[:2], ap(x1, y1, 0)[:2], ap(x0, y1, 0)[:2]]
    # escalera (Gabriel con el ingeniero, 23-10-2026): hueco libre ex_h..ex1 x ey0..ey1 de 1,20 x 3,97, del muro de 23,3 al tabique de 10 del muro del eje 5 y hasta la cara
    # del muro del eje B; sin descanso: se entra desde el distribuidor por el eje B y se baja hacia el eje A; el pie queda donde estaba (y = 147) y el último metro va bajo la losa
    MURO_ESC = 23.3
    esc = rec['escalera']; ex_h, ey0, ex1, ey1 = esc[0][0], esc[0][1], esc[1][0], esc[2][1]
    ex0 = ex_h - MURO_ESC                      # cara poniente del muro de la escalera
    y_pie = 147.0; TRAMO_ESC = ey1 - y_pie     # el tramo parte en ey1 (cara del muro del eje B) y termina en el piso del búnker, 1,12 antes de su tabique del eje A
    N_PELD = min(range(15, 25), key=lambda n: abs((2 * -z_piso + TRAMO_ESC) / n - 63))   # 2 contrahuellas + 1 huella ≈ 63: 19 de 26,2 x 18,2
    y_desc = rec['cafeteria'][-1][1]           # cara norte del tabique B (= ey1: ya no hay descanso)
    escalera = dict(pts=rect(ex_h, ey0, ex1, ey1), ancho=r1(ex1 - ex_h), largo=r1(ey1 - ey0), baja=r1(-z_piso), z_arriba=r1(z0), z_abajo=r1(z0 + z_piso), baja_hacia='norte',
        tramo=dict(y_arriba=r1(oy + ey1), y_abajo=r1(oy + y_pie), largo=TRAMO_ESC, peldanos=N_PELD),
        muro=dict(pts=rect(ex0, ey0, ex_h, y_desc), espesor=MURO_ESC),           # muro poniente de la caja de escalera, hasta el tabique B
        muro_norte=dict(pts=rect(ex0, rec['cafeteria'][2][1], ex1, ey0), espesor=ey0 - rec['cafeteria'][2][1]),   # muro hacia la minicocina
        hormigon=True,   # escalera y sus muros en hormigón armado (Gabriel, 2026-10-12)
        descanso=None,
        nota=f'se entra desde el distribuidor por el eje B (puerta con llave) y baja {-z_piso/100:.2f} m hacia el eje A en {TRAMO_ESC/100:.2f} m: {N_PELD} peldaños de {TRAMO_ESC/N_PELD:.1f} x {-z_piso/N_PELD:.2f}; el hueco en la losa mide {(ex1 - ex_h)/100:.2f} x {(ey1 - ey0)/100:.2f} y el último metro va bajo la losa, dentro del búnker (altura libre en el borde del hueco del lado del eje A, desde la línea de las narices de obra gruesa: ≈ {(-z_piso * (ey1 - ey0) / TRAMO_ESC + z_piso / N_PELD - BUNKER_LOSA)/100:.2f} m hasta la losa y {(-z_piso * (ey1 - ey0) / TRAMO_ESC + z_piso / N_PELD - BUNKER_LOSA - T_CIELO)/100:.2f} m hasta el cielo; las vigas botadas VBL y VBC van dentro de la losa; cada cm de terminación en los peldaños la baja 1 cm)'.replace('.', ','))
    # ---------- hormigón armado, fundaciones, placas base y enfierradura: hormigon.py (láminas 01 rev 1, 02 rev G, 03 rev H, 05 rev H) ----------
    pils = [mb for mb in M if mb['c'] == 'pilar']
    def toca(mb, p):   # el extremo p de una diagonal cae en la línea del pilar
        return abs(mb['a'][0] - p[0]) < 1 and abs(mb['a'][1] - p[1]) < 1
    pilares_cruz = sorted({mb['id'] for mb in pils for d in M if d['c'] == 'diagonal' and not d['id'].startswith('XF-') for p in (d['a'], d['b']) if toca(mb, p)})   # los tensores de faja (XF) no llegan a la placa   # pilares a los que llega una diagonal (pie o cabeza): placa PLc
    pilares_pie = sorted({mb['id'] for mb in pils for d in M if d['c'] == 'diagonal' for p in (d['a'], d['b']) if toca(mb, p) and abs(p[2] - mb['a'][2]) < 5})   # los que la reciben en su pie: cartela en la placa
    # sentido (en planta) de cada diagonal que llega al pie de un pilar: la placa embebida se alarga de ese lado para la cartela (27-10-2026)
    diag_pie = {}
    for mb in pils:
        for d in M:
            if d['c'] != 'diagonal': continue
            for p, o in ((d['a'], d['b']), (d['b'], d['a'])):
                if toca(mb, p) and abs(p[2] - mb['a'][2]) < 5:
                    hx, hy = o[0] - p[0], o[1] - p[1]; n_ = math.hypot(hx, hy)
                    diag_pie.setdefault(mb['id'], []).append((hx / n_, hy / n_))
    hormigon, fierros, cub_hormigon = HORM.armar(dict(ap=ap, rect=rect, r1=r1, z0=z0, ox=ox, oy=oy, xA=xA, yA=yA, yB=yB, yC=yC, yC2=yC2, W=W, L=L, rec=rec, bk=bk, BUNKER_H=BUNKER_H,
                                                      pilares=pils, pilares_cruz=pilares_cruz, pilares_pie=pilares_pie, diag_pie=diag_pie, escalera=escalera, ex0=ex0, ex_h=ex_h, ex1=ex1, ey0=ey0, ey1=ey1, y_desc=y_desc, x3=xA[2], T=T,
                                                      h_caja=z_viga(yB)))
    z_piso = hormigon['niveles']['piso_bunker']; z_losa_inf = hormigon['niveles']['losa_inf']

    # ---------- vanos propuestos (ventanas y puertas) ----------
    V = []
    # alturas de los vanos medidas desde el piso terminado (NPT = NPOG + piso), Gabriel 13-10-2026
    def vano(id_, tipo, muro, x0, y0, x1, y1, z0_, z1_, d, **k): V.append(dict(id=id_, tipo=tipo, muro=muro, a=ap(x0, y0, 0)[:2], b=ap(x1, y1, 0)[:2], z0=r1(z0 + T_PISO + z0_), z1=r1(z0 + T_PISO + z1_), ancho=r1(math.hypot(x1 - x0, y1 - y0)), alto=r1(z1_ - z0_), d=d, **k))
    hol = 20.0   # holgura a cada lado del pilar
    # fachada norte (A): vidrio de piso a cielo en los tramos 1-2, 2-3 y 3-4 (Gabriel, 14-10-2026, opción 2: "vamos con la tuya"); el 4-5 queda ciego porque es la esquina de servicio (cocina, minibar y escalera); corredera al patio en el 2-3
    for i in (0, 1, 2):
        x0, x1 = xA[i] + hol, xA[i + 1] - hol
        if i == 1: vano(f'V-A-{i+1}', 'puerta corredera', 'norte', x0, yA[0], x1, yA[0], 0, H_VENTANA, 'corredera vidriada de 2 hojas al patio, en el tramo 2-3: alineada con la corredera interior (eje del estudio)')
        else: vano(f'V-A-{i+1}', 'ventana', 'norte', x0, yA[0], x1, yA[0], 0, H_VENTANA, f'ventana fija de piso terminado a cielo terminado (4,00) en el tramo {xN[i]}-{xN[i+1]}: la cafetería mira al patio por los tramos 1-2, 2-3 y 3-4; el 4-5 es ciego (esquina de la cocina y la escalera; Gabriel, 14-10-2026)')
    # tabique cafetería/estudio (B): todo de vidrio en los tramos 1-2, 2-3 y 3-4 (Gabriel, 14-10-2026, opción 1: la luz del norte entra a través de la cafetería; cortina gruesa atrás para mezclar): corredera en el 2-3 (centrada en el estudio) y paños fijos en el 1-2 y el 3-4; el 4-5 es el baño
    z_vB = z_vE = H_VENTANA   # de piso terminado a cielo terminado (4,00); la viga E-O y el entretecho quedan encima
    gapB, gapE = z_viga(yB) - Z_CORDON[1], z_viga(yA[6]) - Z_CORDON[1]   # franja ciega sobre la viga E-O: 22 en B, 54 en E
    for i in (0, 1, 2):
        x0, x1 = xA[i] + hol, xA[i + 1] - hol
        if i == 1: vano(f'V-B-{i+1}', 'puerta corredera interior', 'tabique B', x0, yB, x1, yB, 0, z_vB, 'corredera vidriada de 2 hojas entre cafetería y estudio, centrada en el estudio')
        else: vano(f'V-B-{i+1}', 'vidrio interior', 'tabique B', x0, yB, x1, yB, 0, z_vB, f'vidrio fijo de piso terminado a cielo terminado ({z_vB/100:.2f} m) entre cafetería y estudio (acústico: doble vidrio); la viga 100x100 de +{(Z_CORDON[0]/100):.2f} y la franja de {gapB:.0f} cm sobre ella quedan en el entretecho'.replace('.', ','))
    vano('P-B-dist', 'puerta', 'tabique B', xA[3] + 25, yB, xA[3] + 105, yB, 0, 210, 'puerta del distribuidor desde la cafetería (0,80 x 2,10), junto al eje 4; el distribuidor reparte al baño y a la escalera del búnker (23-10-2026)')
    yDB = (rec['distribuidor'][2][1] + rec['bano'][0][1]) / 2      # tabique distribuidor/baño (25, nuevo el 23-10-2026)
    vano('P-dist-bano', 'puerta', 'tabique distribuidor', xA[3] + 25, yDB, xA[3] + 105, yDB, 0, 210, 'puerta del baño desde el distribuidor (0,80 x 2,10), junto al eje 4 (propuesta, 23-10-2026)')
    # fachada sur (E): ventana de piso terminado a cielo terminado centrada en el estudio (tramo 2-3), entre los parlantes. Se sacó y volvió el 14-10-2026: la luz prestada por la cafetería no alcanza al escritorio; Gabriel eligió vivir con cortina acústica para mezclar fino
    vano('V-E-2', 'ventana', 'sur', xA[1] + hol, yA[6], xA[2] - hol, yA[6], 0, z_vE, f'ventana fija de piso terminado a cielo terminado ({z_vE/100:.2f} m) centrada en el estudio, entre los parlantes: luz pareja y sin sol directo, buena para las pantallas; cortina acústica pesada para mezclar fino (Gabriel, 14-10-2026)'.replace('.', ','))
    # entrada principal: fachada poniente, lado de la casa, en la cafetería (tramo A2-B)
    # entrada pegada al pilar A2 (el tramo A-A2 lleva cruz); la cabina de grabación queda al sur de la puerta, contra el tabique vidriado
    vano('P-O-entrada', 'puerta', 'poniente', xA[0], yA[1] + 10, xA[0], yA[1] + 190, 0, 240, 'puerta de entrada de 2 hojas (1,80) desde el lado de la casa y el estacionamiento')
    # ventana alta del baño en la fachada oriente (tramo B-C, sin cruces)
    yBn = (rec['bano'][0][1] + rec['bano'][2][1]) / 2
    vano('V-5-bano', 'ventana alta', 'oriente', xA[4], yBn - 75, xA[4], yBn + 75, 230, 290, 'ventana alta del baño (1,50 x 0,60) en la fachada del eje 5')
    # la bodega va sin ventana (Gabriel, 2026-10-12)
    vano('P-C2-bodega', 'puerta', 'tabique C2', xA[4] - 12.5 - 15 - 80, (rec['cabina'][2][1] + rec['bodega'][0][1]) / 2, xA[4] - 12.5 - 15, (rec['cabina'][2][1] + rec['bodega'][0][1]) / 2, 0, 210, 'puerta acústica de la bodega desde la cabina (0,80 x 2,10), junto al eje 5, bajo la diagonal del tabique C2; abre hacia la bodega (Gabriel, 24-10-2026: "hagamos que se entre a la bodega por la sala de grabación"; antes, puerta desde el estudio junto a los parlantes)')
    vano('P-4-cabina', 'puerta', 'tabique 4', xA[3], rec['cabina'][0][1] + 15, xA[3], rec['cabina'][0][1] + 105, 0, 210, 'puerta acústica de la cabina desde el estudio (0,90 x 2,10, hoja maciza con doble burlete), en el extremo de la cabina junto al eje C, lejos de la posición de escucha; la cabina es ciega: sin ventana (Gabriel, 14-10-2026)')
    vano('P-esc', 'escalera', 'tabique B', ex_h, yB, ex1, yB, 0, 0, 'bajada al búnker: se entra desde el distribuidor por el eje B y se baja hacia el eje A')
    # puerta con llave a la escalera (seguridad del búnker), en el tabique B, centrada entre el muro de la caja y el muro del eje 5
    xPe = (ex_h + rec['escalera'][1][0] + 10) / 2
    vano('P-esc-puerta', 'puerta', 'tabique B', xPe - 45, yB, xPe + 45, yB, 0, 210, 'puerta con llave a la escalera desde el distribuidor (0,90 x 2,10): la bajada al búnker queda cerrada por seguridad')
    # ---------- esquema interior (idea, para conversar) ----------
    est = recT['estudio']; ce_x = (est[0][0] + est[1][0]) / 2     # el mobiliario va contra las caras terminadas (tabique)
    caf = recT['cafeteria']
    # Cada mueble: tipo (lo dibuja mobiliario3d.js), recinto, pts = rectángulo en planta (app, cm), alto (cm, desde el piso) y
    # mira = hacia dónde da el frente ('N', 'S', 'E', 'O'). Solo es una idea para conversar; Gabriel decide el amoblado.
    interior = []
    def mueble(id_, tipo, recinto, nombre, x0, y0, x1, y1, alto, mira, nota=''):
        interior.append(dict(id=id_, tipo=tipo, recinto=recinto, nombre=nombre, pts=rect(x0, y0, x1, y1), alto=alto, mira=mira, nota=nota))
    # --- estudio de producción: triángulo de escucha mirando al sur ---
    mueble('parlantes', 'parlante', 'estudio', 'Parlante principal (monitor de campo medio)', ce_x - 300, est[2][1] - 60, ce_x - 220, est[2][1] - 5, 150, 'N', 'en el muro del eje E, a los lados de la ventana central (la ventana volvió el 14-10-2026 por la luz del escritorio; cortina acústica para mezclar)')
    mueble('parlantes2', 'parlante', 'estudio', 'Parlante principal (monitor de campo medio)', ce_x + 220, est[2][1] - 60, ce_x + 300, est[2][1] - 5, 150, 'N', '')
    mueble('consola', 'consola', 'estudio', 'Consola / escritorio de producción', ce_x - 120, est[2][1] - 320, ce_x + 120, est[2][1] - 240, 75, 'S', 'mirando hacia el eje E, a unos 2,5 m de los parlantes (triángulo de escucha); con dos monitores y controlador')
    mueble('silla_consola', 'silla_oficina', 'estudio', 'Silla del productor', ce_x - 30, est[2][1] - 400, ce_x + 30, est[2][1] - 340, 110, 'S', '')
    mueble('rack', 'rack', 'estudio', 'Rack de equipos (12U)', ce_x + 170, est[2][1] - 330, ce_x + 230, est[2][1] - 230, 90, 'O', 'al lado del escritorio')
    mueble('sofa', 'sofa', 'estudio', 'Sofá de clientes', ce_x - 130, est[0][1] + 120, ce_x + 130, est[0][1] + 210, 85, 'S', 'hacia el eje B, junto al vidrio de la cafetería')
    for k, yy in enumerate((est[0][1] + 250, est[0][1] + 400, est[0][1] + 640, est[0][1] + 900)):   # entre los pilares C (872), C2 (1277) y D (1532) de la fachada poniente
        mueble(f'panel_o{k+1}', 'panel_acustico', 'estudio', 'Panel acústico 100 × 120', est[0][0], yy, est[0][0] + 6, yy + 100, 220, 'E', 'en el muro del eje 1, a 1,00 del piso')
    y_pc = rec['cabina'][0][1] + 105   # fin de la puerta de la cabina (tabique 4); la bodega ya no tiene puerta a este lado (24-10-2026)
    for k, yy in enumerate((y_pc + 15, y_pc + 125, 1430.0, 1560.0)):   # 2 junto a la puerta de la cabina y 2 en las primeras reflexiones de los parlantes en este tabique (≈ 1480 y 1610)
        mueble(f'panel_e{k+1}', 'panel_acustico', 'estudio', 'Panel acústico 100 × 120', est[1][0] - 6, yy, est[1][0], yy + 100, 220, 'O', 'en el tabique del eje 4, a 1,00 del piso')
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
    mueble('cocina', 'cocina', 'cafeteria', 'Cocina chica con lavaplatos', ex1 - 60, caf[0][1] + 75, ex1, ey0 - MURO_ESC - 10, 90, 'O', 'mueble de 0,60 de fondo contra el muro del eje 5, entre la fachada del eje A y la escalera; lavaplatos pequeño para lavar lo que se use')
    mueble('minibar', 'minibar', 'cafeteria', 'Minibar', ex1 - 55, caf[0][1] + 15, ex1 - 5, caf[0][1] + 65, 85, 'O', 'frigobar de 0,50 x 0,50 con puerta de vidrio, en la esquina de los ejes A y 5, junto a la cocina')
    mueble('lampara_barra', 'lampara', 'cafeteria', 'Lámpara colgante', ex0 - 75, ey0 + 125, ex0 - 45, ey0 + 155, 230, 'S', 'sobre la barra; cuelga del cielo')
    for k, (mx, my) in enumerate(mesas):
        mueble(f'lampara_mesa{k+1}', 'lampara', 'cafeteria', 'Lámpara colgante', mx + 65, my + 25, mx + 95, my + 55, 230, 'S', 'sobre la mesa; cuelga del cielo')
    # --- baño y bodega ---
    ban = recT['bano']; bod = recT['bodega']
    mueble('wc', 'wc', 'bano', 'Inodoro', ban[1][0] - 80, ban[2][1] - 75, ban[1][0] - 40, ban[2][1] - 5, 80, 'N', 'contra el tabique baño/cabina')
    mueble('lavamanos', 'lavamanos', 'bano', 'Lavamanos con mueble', ban[1][0] - 50, ban[0][1] + 30, ban[1][0], ban[0][1] + 90, 85, 'O', 'en el muro del eje 5, bajo la ventana alta')
    # bodega de 2,50 × 2,50 para las cosas chicas (24-10-2026): estanterías de 40 en U en los 3 muros sin puerta; la del eje 5 parte después del barrido de la puerta (0,80 desde C2)
    mueble('estante_o', 'estante', 'bodega', 'Estantería metálica 40 de fondo', bod[0][0], bod[0][1] + 5, bod[0][0] + 40, bod[2][1] - 40, 200, 'E', 'en el tabique del eje 4 de la bodega (sin puerta desde el 24-10-2026)')
    mueble('estante_e', 'estante', 'bodega', 'Estantería metálica 40 de fondo', bod[1][0] - 40, bod[0][1] + 90, bod[1][0], bod[2][1] - 40, 200, 'O', 'en el muro del eje 5 de la bodega, después del barrido de la puerta')
    mueble('estante_s', 'estante', 'bodega', 'Estantería metálica 40 de fondo', bod[0][0] + 40, bod[2][1] - 40, bod[1][0], bod[2][1], 200, 'N', 'en el muro del eje E de la bodega')
    # --- cabina de grabación (Gabriel, 14-10-2026): ciega; 4,15 con cielo a 3,35 desde el 24-10-2026 (acústica); alfombra, paneles en los muros y una silla para el músico ---
    cab = recT['cabina']; cx_cab = (cab[0][0] + cab[1][0]) / 2
    mueble('alfombra_cab', 'alfombra', 'cabina', 'Alfombra de la cabina', cab[0][0] + 20, cab[0][1] + 120, cab[1][0] - 20, cab[2][1] - 20, 1, 'S', 'entre la puerta y el tabique del eje C2, casi todo el piso: la cabina es seca')
    for k, yy in enumerate((cab[0][1] + 130, cab[2][1] - 145)):   # al sur de la puerta (cab+15..cab+105) y a 0,45 del tabique C2
        mueble(f'panel_cab_o{k+1}', 'panel_acustico', 'cabina', 'Panel acústico 100 × 120', cab[0][0], yy, cab[0][0] + 6, yy + 100, 220, 'E', 'en el tabique del eje 4 de la cabina, a 1,00 del piso (por dentro va toda forrada: estos son los paneles visibles)')
        mueble(f'panel_cab_e{k+1}', 'panel_acustico', 'cabina', 'Panel acústico 100 × 120', cab[1][0] - 6, yy, cab[1][0], yy + 100, 220, 'O', 'en el muro del eje 5 de la cabina, a 1,00 del piso')
    mueble('panel_cab_s', 'panel_acustico', 'cabina', 'Panel acústico 100 × 120', cab[0][0] + 20, cab[2][1] - 6, cab[0][0] + 120, cab[2][1], 220, 'N', 'en el tabique del eje C2 de la cabina, al lado de la puerta de la bodega')
    cy_cab = (cab[0][1] + cab[2][1]) / 2
    mueble('silla_cab', 'silla', 'cabina', 'Silla del músico', cx_cab - 22, cy_cab - 22, cx_cab + 23, cy_cab + 23, 85, 'N', 'al centro, mirando a la puerta')
    # ---------- uniones de momento UM del cordón con los pilares B y E de los ejes 2 y 3 (27-10-2026) ----------
    # El ingeniero (V121): «Reforzar unión de momento en pilares con plancha e=8 mm. Diseñar y hacer detalle de ese encuentro. Considerar soldadura AWS 6011».
    # 2 planchas laterales PL 8×150 A270ES (una por costado del cordón y del pilar), de +4,11 (a ras con la cara inferior del cordón) a +4,26, 300 sobre el cordón
    # desde la cara del pilar: continua de 750 en B (cruz) y de 435 en E (T, termina a 15 de la cara de fachada). Cajas en cm de la app (a = mínimo, b = máximo).
    # D/C de calculo/union_cordon/union_cordon_pilar.py con los esfuerzos del modelo con UM, tabiques y torsión accidental (extraer_marcos.py planchas)
    UM_DC = {'2B': (0.54, 0.48, 0.30, 0.20), '2E': (0.49, 0.47, 0.44, 0.33), '3B': (0.54, 0.48, 0.30, 0.19), '3E': (0.48, 0.46, 0.43, 0.32)}  # soldadura al cordón, plancha, soldadura al pilar, pilar en el nudo
    TPL, HPL, LPL = 0.8, 15.0, 30.0
    uniones = []
    for xn in ('2', '3'):
        x = xA[xN.index(xn)]
        for yn, y in (('B', yB), ('E', yA[6])):
            y0, y1 = (y - 7.5 - LPL, y + 7.5 + LPL) if yn == 'B' else (y - 7.5 - LPL, y + 7.5 - 1.5)
            cajas = [dict(a=ap(xa_, y0, Z_CORDON[0]), b=ap(xa_ + TPL, y1, Z_CORDON[0] + HPL)) for xa_ in (x - 7.5 - TPL, x + 7.5)]   # una plancha a cada costado
            sc, pl, sp, zp = UM_DC[xn + yn]
            uniones.append(dict(id=f'UM-{xn}{yn}', pilar=f'P-{xn}{yn}', tipo='cruz' if yn == 'B' else 'T', plancha=f'2 PL 8×150×{(y1 - y0) * 10:.0f} A270ES', largo=r1(y1 - y0), cajas=cajas,
                                soldadura='SMAW E6011: al cordón, canal de la esquina superior relleno a ras + filete 3 (300) y filete 3 vertical en la punta (88); abajo no se suelda. '
                                          + ('Al pilar, filete 5 abajo y arriba (130 c/u)' if yn == 'B' else 'Al pilar, filete 5 abajo y arriba (125 c/u) y vertical en el extremo (150)')
                                          + '. Cordón a la cara del pilar con filete 3 arriba y abajo. Viga VT 8 mm más corta, soldada a la plancha con filete 3 en 3 lados',
                                dc=dict(soldadura_cordon=sc, plancha=pl, soldadura_pilar=sp, pilar_nudo=zp), dc_max=max(sc, pl, sp, zp),
                                nota='resiste más que el cordón: con su φMn (1.186 kgf·m, 11,6 kN·m) da 0,87',
                                fuente='ingeniero V121 (plancha de 8 y E6011); diseño 27-10-2026 (calculo/union_cordon/union_cordon_pilar.py, AISC 360-16 J2, J4, J10, K)'))
    # ---------- techo, cielo, cubicación ----------
    cub = {}
    for mb in M: cub[mb['p']] = cub.get(mb['p'], 0) + math.dist(mb['a'], mb['b']) / 100
    cubicacion = [dict(perfil=p, metros=round(cub[p], 1), kg=round(cub[p] * PESO[p])) for p in PESO if cub.get(p, 0) > 0]
    m_um = sum(2 * u['largo'] for u in uniones) / 100            # 4 × 0,75 + 4 × 0,435 = 4,74 m de PL 8×150
    cubicacion.append(dict(perfil='PL 8 uniones UM', metros=round(m_um, 1), kg=round(m_um * 0.15 * 0.008 * 7850), donde='planchas laterales de las uniones UM del cordón con los pilares B y E (ejes 2 y 3)'))
    tot = round(sum(c['kg'] for c in cubicacion))
    techo = dict(contorno=[ap(x_ini, y_ini, 0)[:2], ap(x_fin, y_ini, 0)[:2], ap(x_fin, y_fin, 0)[:2], ap(x_ini, y_fin, 0)[:2]],
                 y0=r1(oy + y_ini), y1=r1(oy + y_fin), z0=r1(z0 + z_viga(y_ini) + 30), z1=r1(z0 + z_viga(y_fin) + 30), espesor=5)
    cielo = dict(z_norte=r1(z0 + z_viga(yA[0])), z_sur=r1(z0 + z_viga(yA[6])), y_norte=r1(oy + yA[0]), y_sur=r1(oy + yA[6]))
    largo_r = lambda i: (lambda v: (f'{v:.3f}' if round(v * 1000) % 10 else f'{v:.2f}').replace('.', ','))((rec[i][2][1] - rec[i][0][1]) / 100)   # 1,90 · 4,15 · 3,075   # largo entre tabiques (dirección A–E) de un recinto de la franja 4–5
    cambios = [
        dict(que='Ubicación del búnker', original='búnker bajo el tramo E1–A1 (lado alto del techo)', nuevo='búnker bajo la cafetería (ejes A–B, lado bajo); el techo sube hacia el eje E como la casa', por='Gabriel'),
        dict(que='Aleros', original='80 en las fachadas de los ejes A y E, 52 en las de los ejes 1 y 5', nuevo=f'{ALERO_NS - MURO/2:.0f} cm por todos lados desde la cara exterior del muro, como los de la casa', por='Gabriel: el techo se veía corto'),
        dict(que='Pendiente del techo', original='rotulada 3,5 %, dibujada 4,5 % (+400 en F1, +447 en A1)', nuevo='3,5 % (+400 en el eje A, +454 en el eje E), la de la casa; el 4,5 % dibujado se toma como error de la lámina', por='Gabriel'),
        dict(que='Planta', original='11,05 x 10,25 m entre ejes (5 ejes a lo largo de los 11,05: 205 | 365 | 205 | 330; 6 a lo largo de los 10,25: 205 | 170 | 125 | 343 | 182)', nuevo=f'{W/100:.2f} x {L/100:.2f} m por fuera (antes 10,55 x 15,75); ejes 1-5 a {xA[1]-xA[0]:.1f} | {xA[2]-xA[1]:.1f} | {xA[3]-xA[2]:.1f} | {xA[4]-xA[3]:.0f} y A-E a 200 | {yB-yA[1]:.0f} | {yC-yB:.0f} | {yC2-yC:.0f} | {yA[5]-yC2:.0f} | 200'.replace('.', ','), por='planta de Gabriel (medidas terminadas) · ejes: propuesta'),
        dict(que='Búnker', original='5,00 x 10,80 interiores (muros 1.a, 3.a, E1, A1), 2,72 de alto, hueco de 3,05 x 1,00 junto al muro A1', nuevo=f'{hormigon["interior"]["largo"]/100:.2f} x {hormigon["interior"]["ancho"]/100:.2f} interiores, 2,80 de alto, hueco de escalera de {hormigon["escalera"]["ancho"]/100:.2f} x {hormigon["escalera"]["largo"]/100:.2f} junto al muro del eje 5', por='Gabriel'),
        dict(que='Muro del eje B del búnker', original='—', nuevo='coincide con el tabique cafetería/estudio (eje B) y recibe sus 5 pilares', por='planta de Gabriel'),
        dict(que='Losa del búnker', original='e=20, luz 5,00 (ø10@20 en la luz corta, ø8@20 en la larga), VHA 25/40 en 2.a', nuevo='e=20, luz 6,00 (+20 %, +44 % de momento), VHA 25/40 en el eje 3 y viga de borde en la escalera', por='para el ingeniero'),
        dict(que='Marcos interiores', original='1.b y 1.c: pilares solo en F1 y A1 (10,25 m), cordón RECT 150x100x3 a +400, viga 200x150x5, puntales 150x100x3 cada 171', nuevo=f'ejes 2, 3 y 4: pilares en A, B y E; luces de {(yB-yA[0])/100:.2f} y {(yA[6]-yB)/100:.2f} m con el mismo esquema'.replace('.', ','), por='propuesta'),
        dict(que='Largo del estudio', original='9,00 (planta del 11-10); 15,75 por fuera', nuevo=f'10,50: +1,50 hacia el eje E para que la bodega quede de 4,30 (los parlantes se corren con el muro); edificio {W/100:.2f} × {L/100:.2f} por fuera; eje C2 nuevo en el tabique cabina/bodega para que ningún tramo en A–E pase de 4,45'.replace('.', ','), por='Gabriel (14-10-2026): "agreguemos 1,5 metro más… la bodega yo creo que quedará chica… el estudio quedará más grande nomás"'),
        dict(que='Ventanas de la cafetería al patio', original='vidrio solo en los tramos 2-3 y 3-4 de la fachada del eje A (13-10-2026)', nuevo='vidrio de piso a cielo en los tramos 1-2, 2-3 y 3-4 de la fachada del eje A (corredera en el 2-3) y el 4-5 ciego: es la esquina de servicio (cocina, minibar y escalera) y da muro para los muebles altos; ese muro no lleva cruces, así que no cambia la estructura', por='Gabriel (14-10-2026): primero "pongamos 4 ventanas igual", luego eligió la opción 2 (3 vidrios y la esquina ciega) entre 4 láminas'),
        dict(que='Ventanas del estudio', original='ventana de piso a cielo en la fachada del eje E, entre los parlantes, y vidrio al tabique B solo en los tramos 2-3 y 3-4 (13-10-2026)', nuevo='todo el tabique B de vidrio (tramos 1-2, 2-3 y 3-4, corredera en el 2-3) y la ventana de piso a cielo de la fachada del eje E en el tramo 2-3, entre los parlantes, con cortina acústica pesada para mezclar fino: la luz del patio entra a través de la cafetería y la de la fachada del eje E, pareja y sin sol, llega al escritorio', por='Gabriel (14-10-2026): "la luz es un temón… no puedo hacer lo de no tener ventanas"; sacó la ventana de la fachada del eje E y la devolvió la misma noche porque la luz prestada no alcanza al escritorio'),
        dict(que='Franja 4–5: baño, cabina y bodega', original='baño 2,50 x 4,10 y bodega 2,50 x 4,65 (planta del 11-10)', nuevo=f'distribuidor 2,50 × {largo_r("distribuidor")} (se entra desde la cafetería; reparte al baño y a la escalera del búnker), baño 2,50 × {largo_r("bano")}, cabina de grabación 2,50 × {largo_r("cabina")} (cielo bajado a 3,35, ciega, tabiques dobles dentro de los 25) y bodega 2,50 × {largo_r("bodega")}; el eje C pasa al tabique baño/cabina y se agrega el eje C2 en el tabique cabina/bodega (B–C {yC-yB:.0f}, C–C2 {yC2-yC:.0f}, C2–D {yA[5]-yC2:.0f}), cada uno con su CF, su pilar PM3 en el eje 4 y, en el tramo 4-5, una cruz (C) o una sola diagonal (C2, por la puerta de la bodega); la puerta de la cabina va desde el estudio en su extremo junto al eje C, lejos de la posición de escucha, y la de la bodega desde la cabina, en el tabique C2 junto al eje 5', por='Gabriel (14-10-2026): "2,5 x 4,1 será como un baño turco"; cabina al medio, ciega; distribuidor de 1,20 el 23-10-2026 (con el ingeniero); cabina de 4,15 con cielo a 3,35 el 24-10-2026 (acústica, opción 3 de 4): la bodega queda de 2,50'),
        dict(que='Cabina de grabación (acústica)', original='2,50 × 3,075 con cielo a 3,00 (con el distribuidor): largo casi igual al alto, los modos de 56, 113 y 169 Hz se sumaban de a pares', nuevo=f'2,50 × {largo_r("cabina")} con cielo a 3,35 (proporción 1 : 1,34 : 1,66): 0 pares de modos bajo 200 Hz y nota 95/100 en los criterios de salas (EBU, Bolt, Bonello); el eje C2 se corre 1,075 hacia el eje E con sus pilares, CF y dado, y el pilar 1C de la fachada pasa a {P_REFUERZO["P-1C"]}; la bodega (2,50) se entra desde la cabina y el tabique C2 lleva una sola diagonal', por='Gabriel (24-10-2026): "vamos con la 3"; "hagamos que se entre a la bodega por la sala de grabación"'),
        dict(que='Fundación del búnker', original='zapata corrida 100 × 30 bajo los muros, relleno 10 y radier 10 adentro (corte a-a); 2,72 libres', nuevo=f'losa de fundación armada e={BUNKER_FUND:.0f} bajo todo el búnker, unida a los muros y sobresaliendo {BUNKER_FUND_MARGEN:.1f} de su cara exterior; su cara superior es el piso del búnker (sin relleno ni radier aparte). Con el mismo sello, el búnker gana {BUNKER_FUND:.0f} cm: {E["bunker"]["interior_cm"]/100:.2f} libres terminados ({BUNKER_H/100:.2f} de obra gruesa). Armadura propuesta: doble malla ø12@15 en los dos sentidos (la misma barra de los muros), recubrimiento 5'.replace('.', ','), por='ingeniero (vía Gabriel, 15-10-2026); armadura por confirmar'),
        dict(que='Tabique del búnker y medidas terminadas', original='medidas interiores entre caras de hormigón (muros y tabiques de 25)', nuevo=f'tabique de {T:.0f} por dentro de los 4 muros de hormigón del búnker (del radier a la losa): el búnker mide {hormigon["interior"]["terminado"]["ancho"]/100:.2f} × {hormigon["interior"]["terminado"]["largo"]/100:.2f} terminado ({hormigon["interior"]["ancho"]/100:.2f} × {hormigon["interior"]["largo"]/100:.2f} entre muros); arriba muros y tabiques de 25 terminado, sin tabique extra; para eso los ejes 1–5 pasan de 10,30 a 10,50 y A–B de 6,25 a 6,45 → {W/100:.2f} × {L/100:.2f} m por fuera (antes 10,55 × 15,75); la cafetería queda de 10,25 × 6,20 y el estudio de 7,50 × 9,00'.replace('.', ','), por='Gabriel (14-10-2026): "el búnker tiene que medir lo que dijimos"; opción 1'),
        dict(que='Vigas 100x100 y cordones', original='todas a +400/+410 (lámina 05); en el marco alto (A1) los pilares pasan la viga y siguen hasta la viga inclinada', nuevo=f'+{Z_CORDON[0]:.0f}/+{Z_CORDON[1]:.0f} en A, B, C y E: {T_PISO + T_CIELO:.1f} cm más arriba, para que el cielo terminado quede a 4,00 sobre el porcelanato (piso {T_PISO:.1f} + cielo {T_CIELO:.1f}); los pilares crecen lo mismo; en B y E pasan la viga y siguen hasta la viga inclinada'.replace('.', ','), por='Gabriel (13-10-2026): 4,00 libres terminados; avisar al ingeniero'),
        dict(que='Fachadas laterales', original='1.a, 2.a, 3.a: pilares cada 1,25–3,43 m, viga 200x150x3, cruces en los tramos de 2,05 y 1,82', nuevo='ejes 1 y 5: pilares en A, A2, B, C, D, E; cruces en A-A2 y D-E (2,00 m)', por='propuesta'),
        dict(que='Pilares', original='21 (13 de 15×15 y 8 de 15×10 en la planta de cubierta)', nuevo=f'{sum(1 for mb in M if mb["c"] == "pilar")}; ninguno dentro de los recintos', por='propuesta'),
        dict(que='Rigidez en 1–5', original='sin cruces en la dirección 1–5 en las láminas', nuevo='cruces en los muros ciegos: tabique baño/cabina (C, 4-5), muro A 4-5 y fachada del eje E (1-2 y 4-5); una sola diagonal en el tabique cabina/bodega (C2, 4-5) por la puerta de la bodega (24-10-2026); el tabique B 4-5 queda sin diagonal por las puertas del distribuidor y de la escalera (23-10-2026); el vidrio entre cafetería y estudio queda libre', por='propuesta: revisar'),
        dict(que='Costaneras', original='CA 100x50x15x3 @61, 20 por línea; colgadores ø10 en los paños de 3,65 y 3,30', nuevo=f'mismo perfil y paso, {n} por línea; paños de ≤ {max(xA[i+1]-xA[i] for i in range(4))/100:.2f} m: sin colgadores', por='propuesta'),
        dict(que='Fundaciones fuera del búnker', original='sobrecimiento 25 x 50 + cimiento corrido 80 x 25 (de −50 a −75) bajo el perímetro, CF 25/40 bajo el eje interior 2.a, radier 10 sobre poliestireno 10 y relleno 15 (lámina 01 rev 1)', nuevo='lo mismo: sobrecimiento y cimiento corrido bajo las fachadas fuera del búnker, CF 25 × 50 de 0 a −50 bajo los tabiques con pilares (ejes 4, C y C2), hasta la cara del radier (hace de perímetro de cada paño), radier igual', por='dato del ingeniero, aplicado a la planta nueva; el CF hasta la cara del radier es de Gabriel (19-10-2026)'),
        dict(que='Base del búnker', original='zapata corrida de 100 x 30 bajo los muros (ø16@20 + 4ø10), radier 10 sobre relleno granular 10, emplantillado G5', nuevo='igual, con el búnker nuevo (todo 8 cm más abajo por los 2,80 de alto)', por='dato'),
        dict(que='Placas base', original='PLb 200 x 200 x 8 en todos los pilares, anclajes 1+1 ø3/4 en horquilla (L=1200: 140 + 430 + ganchos de 100), Est ø8@20', nuevo='igual, en los 25 pilares (los ganchos doblan hacia adentro: el ancla mide 140 y cabe en el muro de 25)', por='dato'),
        dict(que='CF bajo los tabiques', original='CF 25/40 bajo el eje interior 2.a, de −10 a −50 bajo el radier (3ø12 + 2ø10 + 3ø12, Est ø10@25)', nuevo='CF 25 × 50 de 0 a −50 bajo los ejes 4, C y C2 (los de C y C2 iguales en todo), con la misma armadura: llega hasta la cara del radier y hace de perímetro de los paños del radier; el anclaje de 43 de las placas termina dentro del CF con 7 de recubrimiento', por='Gabriel, 19-10-2026 ("las fundaciones tienen que llegar hasta la losa terminada, hacen de perímetro de la losa"); por confirmar con el ingeniero'),
        dict(que='Viga inclinada y viga 100x100', original='lámina 04: viga inclinada con la cara inferior a +400 en F1; lámina 05: apoyada sobre la viga 100x100 de +401 a +411', nuevo=f'como la lámina 05 pero {T_PISO + T_CIELO:.0f} cm más arriba: viga 100x100 de +{Z_CORDON[0]:.0f} a +{Z_CORDON[1]:.0f} en todos los marcos; en el eje A (lado bajo) los pilares terminan a +{Z_CORDON[0]:.0f} y la viga inclinada apoya sobre la viga 100x100; en B y E los pilares pasan la viga y siguen hasta la viga inclinada, como el marco A1', por='dato (lámina 05) + terminaciones de Gabriel'),
        dict(que='Niveles del búnker', original='2,72 libres; radier a −292 por cotas (rótulos −272 / −305 / −342, inconsistentes)', nuevo=f'2,80 libres terminados = {BUNKER_H:.0f} de obra gruesa (piso {T_PISO:.1f} + cielo {T_CIELO:.1f}); losa 0 / −20, piso de obra gruesa −{BUNKER_H + 20:.0f}, radier −{BUNKER_H + 30:.0f}, zapata −{BUNKER_H + 40:.0f} / −{BUNKER_H + 70:.0f}, sello −{BUNKER_H + 80:.0f}'.replace('.', ','), por='Gabriel (13-10-2026): 2,80 terminados; el detalle baja 15 cm respecto del original'),
        dict(que='Costaneras en el alero', original='la primera a 61 del eje: 19 dentro de la punta del alero de 80, con el soporte C 150x50x3 en la punta', nuevo='igual: la primera a 19 de la punta (alero de 100) y luego cada 61', por='dato'),
        dict(que='Enfierradura', original='muros DM ø12@15 / ø10@20, losa ø10@20 + ø8@20, VHA 3ø12+2ø10+3ø16, CF 3ø12+2ø10+3ø12', nuevo='las del ingeniero, reforzadas en la revisión del 23-10-2026 (ver abajo), en el modelo 3D barra por barra (capa Enfierradura)', por='dato y revisión; largos y cantidades del modelo'),
        dict(que='Acero', original='—', nuevo=f'{tot} kg de perfiles y planchas de las uniones UM en el modelo (sin placas base ni pérdidas)', por='cubicación del modelo'),
        # ---- revisión estructural (Gabriel, 23-10-2026: "haz los cambios. me cuadra todo"); detalle en la pestaña Revisión ----
        dict(que='Revisión: losa de techo del búnker', original='e=20, ø10@20 en A–B y ø8@20 en 1–5, sin fierro arriba en los muros (diseñada para 5,00 m)', nuevo=f'e={BUNKER_LOSA:.0f} continua con los muros: abajo ø10@15 en los dos sentidos; arriba ø12@15 en L sobre los 4 muros (180 dentro de la losa) y ø10@20 sobre la VHA', por='revisión 23-10-2026: no pasaba (colapso ≈ 11 kPa contra 14)'),
        dict(que='Revisión: VHA y hueco de la escalera', original='VHA 25/40 con estribos @20; 2ø12 de borde en el hueco', nuevo='VHA-3 25/50 (3ø16 abajo, 3ø12 arriba, E ø10@15); el hueco llega al muro del eje B, que hace de borde, y en los otros 2 lados lleva vigas botadas VBL y VBC 40/25 dentro de la losa, con un pilar CUAD 100x100x4 en la esquina libre (placas 250x250x16 arriba y abajo) y suple ø12@15 bajo él en la losa de fundación; ø10@20 arriba en 1–5 junto a los muros A y B; altura libre de la escalera 2,27 hasta el cielo, desde las narices (antes 2,13 bajo las vigas de borde 25/45)', por='revisión 23-10-2026; ingeniero (V121, 25/26-10-2026, y 27-10-2026): VHA 25/50, pilar en la esquina y vigas botadas en la losa de 25; medidas, armaduras y suples: propuesta 27-10-2026 por aprobar'),
        dict(que='Escalera al búnker', original='hueco 1,30 × 2,74 con descanso de 1,23 del lado del eje B y puerta con llave en el muro de la caja; 17 peldaños de 22,1 × 20,35', nuevo=f'hueco {(ex1 - ex_h) / 100:.2f} × {(ey1 - ey0) / 100:.2f} hasta el muro del eje B, sin descanso: se entra desde el distribuidor por una puerta con llave en el tabique B; {N_PELD} peldaños de {TRAMO_ESC / N_PELD:.1f} × {-z_piso / N_PELD:.1f}; el pie queda donde estaba'.replace('.', ','), por='Gabriel con el ingeniero (23-10-2026): "dejar la escalera con el vano más largo, con eso ganamos una huella mejor"'),
        dict(que='Revisión: losa de fundación', original='e=30, doble malla ø12@15 (propuesta)', nuevo=f'e={BUNKER_FUND:.0f}, ø16@15 en A–B y ø12@15 en 1–5, abajo y arriba; los 3,10 libres se mantienen y el sello baja 10 cm', por='revisión 23-10-2026'),
        dict(que='Revisión: muros del búnker', original='e=25, ø12@15 vertical y ø10@20 horizontal, recubrimiento 3', nuevo='e=30 hacia afuera (el interior no cambia; queda un zócalo de 5 bajo la fachada): ø16@15 vertical por fuera (pata de 60 traslapada en la losa de fundación) y ø12@15 por dentro; ø12@15 horizontal; recubrimiento 4 por fuera', por='revisión 23-10-2026; e=30 por Gabriel ("había un tema con el ancho del muro y los fierros"): con 25 no cabían el water-stop ni los pernos, y ACI 350 pide 30'),
        dict(que='Revisión: hormigón y humedad', original='G25; sin impermeabilización ni dren', nuevo='G30 con cristalizante en el búnker, water-stop en la junta losa–muro, membrana por fuera y dren perimetral ø110 al nivel del sello', por='revisión 23-10-2026'),
        dict(que='Revisión: marcos de 10,75 m (ejes 2 y 3)', original='viga 200x150x5 y puntales 150x100x3', nuevo='viga 200x150x6 y los 4 puntales del tramo B-E que no son el central en CUAD 150x150x5', por='revisión 23-10-2026'),
        dict(que='Revisión: arriostramiento', original='sin cruz en la fachada del eje A; cruces hasta +4,03; tensores sin montante', nuevo='cruz en el muro ciego A 4-5; cruces de la placa base a la viga; puntales de techo CUAD 100x100x3 en cada línea de nudos de los tensores', por='revisión 23-10-2026'),
        dict(que='Revisión: placas y anclajes', original='PLb 200x200x8 con 1+1 ø3/4" en horquilla cruzada en los 25 pilares', nuevo='PLc 250x250x12 con 4 pernos ø3/4" con golilla en los 15 pilares con cruz, con armadura de anclaje (verticales del muro, estribos extra del sobrecimiento o 4ø16 en los dados); horquillas paralelas en el resto; dados de 1,40 x 1,40 bajo 4C y 4C2, hasta 10 sobre el sello', por='revisión 23-10-2026'),
        dict(que='Placas embebidas con anclajes soldados', original='PLc 250x250x12 con 4 pernos ø3/4" con hilo, tuerca arriba (chocaba con el tubo) y llave de corte; PLb 200x200x8 con horquillas ø3/4" A630 soldadas', nuevo='insertos: 17 PLc A36 e=16 (250 a 400) con 4 barras lisas A36 ø22 soldadas bajo las paredes del tubo (hef 1000 en los muros del búnker, 450 en el resto), cabeza 60x45x12, filete 12 E7018, y horquillas de corte ø16 en 11 placas; PLc-4A de 550x250x30 con 8 barras (hef 1200, cabeza 100x45x12); 8 PLb A36 200x200x12 con 4 barras ø3/4" a 80x80 (hef 450; 500 en 3A y 3B); sin tuercas ni llave de corte; cartela soldada a la placa y a la cara del tubo', por='ingeniero (V121, 25-10-2026): "insertos con anclajes soldados ... ACEPTADO"; dimensiones: propuesta 27-10-2026 por aprobar (con las reacciones del sismo con tabiques y torsión y la unión UM: máx. 0,96)'),
        dict(que='Revisión: pilares y techo', original='RECT 150x100 de fachada con el lado de 150 a lo largo; 1A y 5A bajo la viga 100x100; aleros de los ejes 1 y 5 sin remate', nuevo='RECT de fachada girados (150 contra el viento); 1A y 5A hasta la viga inclinada; remate CA 100x50x15x2 en los aleros de los ejes 1 y 5; costaneras de 3 mm con silla y 2 pernos M12', por='revisión 23-10-2026'),
        dict(que='Revisión: fundaciones del estudio', original='sello a −0,85 (−0,60 en los CF); anclados al muro del búnker; radier sin malla', nuevo='hormigón pobre hasta −1,40 (0,90 bajo el terreno); junta de 2 con el búnker y 2ø16 arriba en los sobrecimientos; relleno granular al 95 % junto al búnker; radier con malla C139 y juntas cada 3 m', por='revisión 23-10-2026'),
        dict(que='Revisión: fierro armable', original='barras que se cruzaban en las esquinas y nudos, y recubrimientos cortos en bordes y esquinas', nuevo='0 choques y todos los recubrimientos (revisión barra por barra): esquinas en L de cara exterior a exterior, CF con gancho de 90° en lo que los recibe, ganchos de los estribos por fuera de la barra de esquina, verticales y estribos corridos unos cm donde topaban', por='revisión 23-10-2026 (Gabriel: "¿qué más no has revisado?")'),
        dict(que='Revisión: fundaciones como vigas', original='cimiento corrido con 4ø10; dado de 0,80 sobre hormigón pobre', nuevo='4ø12 en el cimiento corrido (el sismo en A–E le pide 86 kN·m; con 4ø10 aguantaba 80) y el dado baja hasta 10 sobre el sello (con 0,80 el sismo lo levantaba ~5 mm)', por='revisión 23-10-2026: emparrillado sobre el suelo'),
        # ---- respuestas al ingeniero (V121, 25/26-10-2026, y 27-10-2026; Gabriel: "aplica nomás") ----
        dict(que='Revisión: sismo con tabiques y torsión accidental', original='sismo sin la masa de los tabiques ni la torsión accidental: deriva 0,94 en el centro de masas', nuevo='masa de los tabiques y del cielo de la cabina (4,4 t al techo: P de 24,7 a 29,4 t) y torsión accidental ±0,10·b (NCh 433 §6.2.8: 23.990 kgf·m en 1–5 y 14.780 kgf·m en A–E); sin arreglo la deriva daba 1,09 y 1,13. Arreglo (+249 kg): cruz C 150x50x3 nueva en el tramo C–C2 de las fachadas 1 y 5 (PLc en 1C y 1C2), X de tensores Fe 22 en la faja de 60 cm entre la viga E-O y la viga inclinada del eje E (1-2 y 4-5), cruz A 4-5 en C 150x50x4 y los 8 tensores de techo de los paños A2–B y B–C de los vanos 1-2 y 4-5 en Fe 22. Deriva en el centro de masas 0,87 en 1–5 y 0,59 en A–E', por='ingeniero (27-10-2026): sumar al modelo sísmico la masa de los tabiques y la torsión accidental; pesos de los tabiques supuestos (falta su ficha)'),
        dict(que='Unión cordón–pilar (marcos 2 y 3)', original='cordón soldado directo a los pilares, articulado en el cálculo (puntal→viga 1,07)', nuevo='unión de momento UM en los pilares B y E de los ejes 2 y 3: 2 planchas laterales PL 8×150 A270ES (750 en B, 435 en E) de +4,11 a +4,26, soldadura E6011 (filete 3 al cordón, 5 al pilar); plancha 0,48, soldadura al cordón 0,54, al pilar 0,44, pilar en el nudo 0,33; puntal→viga 0,80, puntal→cordón 0,87, cordón 0,81. En A y en el eje 4 sigue articulado. Las vigas VT de B y E quedan 8 mm más cortas y se sueldan a la plancha', por='ingeniero V121 (25-10-2026): «reforzar unión de momento en pilares con plancha e=8 mm … considerar soldadura AWS 6011»; diseño 27-10-2026'),
        dict(que='Zapata corrida bajo el CF-4 (opción A)', original='dados de 1,40 × 1,40 bajo 4C y 4C2 (hasta 10 sobre el sello) y hormigón pobre G5 bajo el CF-4 hasta −1,40',
             nuevo='zapata corrida ZC-4 de 45 × 80 armada en todo el eje 4 (G25, de −0,50 a −1,30, con 10 de emplantillado hasta el sello), monolítica con el CF 30/50, que no cambia: sus estribos ø10@25 bajan '
                   'hasta el fondo, 3ø12 abajo, 4ø10 de piel y 4ø12 de anclaje bajo PLc-4C y PLc-4C2 (en vez de las 4ø16 de los dados). El eje 4 ya no se levanta (4C y 4C2 siempre apretando el suelo, también con ks 7.000 y 28.000); '
                   'zapata 0,31, SC-E 0,90, suelo 0,52 / 0,54 kgf/cm², PLc-4C 0,87 y PLc-4C2 0,42', por='Gabriel, 28-10-2026: opción A, «que todo sea zapata corrida»; propuesta, falta el VºBº del ingeniero'),
    ]
    # Gabriel, 22-10-2026: "en las preguntas al ingeniero al final, reduce el texto al 30 %, demasiado texto" (2.520 → ~750 caracteres)
    # Desde la revisión del 23-10-2026 ya no son preguntas al ingeniero: son los datos que faltan para cerrar el cálculo y firmarlo
    # Gabriel, 28-10-2026: "dejemos solo las preguntas que faltan responder y lo demás elimínalo todo" (no habrá más mediciones: agua, sondaje,
    # colectores y pesos quedan con los supuestos del lado seguro de la pestaña Revisión)
    preguntas = [
        'Visto bueno del ingeniero a los cambios «Por aprobar» (pestaña Ingeniero).',
        'Viento: ¿basta la NCh 432:2010? Con la 2025 (+60 %) el pilar P-5C llega a 1,32.',
        'Escalera: ¿el 25/40 de la viga central es alto total (10 de losa + 30 colgados)?',
        'Firma de un ingeniero civil.',
    ]
    out = dict(
        fuente='Adaptación de las láminas 03, 04 y 05 del ingeniero (proyecto del estudio, abril 2026, leídas de sus vectores) a la planta de Gabriel (medidas interiores, 2026-10-12); propuesta para revisión del ingeniero, no es un cálculo',
        marco='cm del marco de la app; z = 0 en el piso del nivel 1 de la casa; el piso del estudio (NPOG 0,00 del ingeniero) está en z = %s' % z0,
        z_piso=z0, ejes=ejes, perfiles={k: PERFILES[k] for k in sorted(set(mb['p'] for mb in M))}, miembros=M,
        hormigon=hormigon, fierros=fierros, cubicacion_hormigon=cub_hormigon, vanos=V, interior=interior, techo=techo, cielo=cielo,
        cubicacion=cubicacion, total_kg=tot, uniones=uniones, cambios=cambios, preguntas=preguntas,
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
