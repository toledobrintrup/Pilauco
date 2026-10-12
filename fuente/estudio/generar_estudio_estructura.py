# -*- coding: utf-8 -*-
"""Propuesta de estructura del estudio con búnker, adaptada del proyecto del ingeniero (láminas 03, 04 y 05 de
abril de 2026) a la planta nueva de Gabriel (10,05 x 15,25 m; búnker bajo la cafetería, al norte; techo que sube
hacia el sur como la casa). Genera estudio_estructura.js (DATA_ESTUDIO_EST) con el mismo formato de miembros que
estructura.js, más el hormigón del búnker, los ejes, los cambios respecto del original y las preguntas al ingeniero.

    python3 generar_estudio_estructura.py ../sitio/estudio.json ../sitio/sitio.json ../../estudio_estructura.js

Todo en cm. Marco local del estudio: x hacia el oriente desde la cara exterior poniente, y hacia el sur desde la cara
exterior norte, z desde el piso terminado del estudio (NPOG 0,00 del ingeniero). Se convierte al marco de la app con
el origen del estudio (sitio.json) y su nivel de piso.

Qué viene del ingeniero (dato) y qué es adaptación (supuesto) está en CAMBIOS y en la descripción de cada pieza.
"""
import json, sys, math

# ---------- perfiles (cm): los de la casa más los del proyecto del estudio ----------
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
PESO = {  # kg/m, de la cubicación del ingeniero
    'C 150x50x3': 5.65, 'CUAD 100x100x3': 8.94, 'CUAD 150x150x4': 18.0, 'CUAD 150x150x5': 22.2, 'FE 16': 1.58,
    'RECT 150x100x3': 11.3, 'RECT 200x150x3': 16.0, 'RECT 200x150x5': 26.1, 'CA 100x50x15x3': 4.95, 'FE 10': 0.62,
}
ORIGINAL_M = {  # metros por perfil en la cubicación original (abril 2026)
    'C 150x50x3': 77.5, 'CUAD 100x100x3': 44.2, 'CUAD 150x150x4': 37.8, 'CUAD 150x150x5': 16.9, 'FE 16': 87.4,
    'RECT 150x100x3': 16.9, 'RECT 200x150x3': 30.0, 'RECT 200x150x5': 20.0, 'CA 100x50x15x3': 233.0, 'FE 10': 24.0,
}

# ---------- parámetros de la adaptación (los del ingeniero salvo que se diga lo contrario) ----------
MURO = 25.0            # muros del estudio (la planta de Gabriel deja bandas de 25)
H_PILAR = 401.0        # altura de pilares sobre NPOG 0,00 (dato, elevaciones)
PEND = 0.035           # pendiente del techo (dato: 3,5 %), sube hacia el sur (nuevo)
ALERO_NS = 80.0        # alero norte y sur (dato: 1.186 = 1.025 + 80 + 80)
ALERO_EO = 52.0        # alero oriente y poniente (dato: cota 52 de la planta de cubierta)
PASO_COST = 61.0       # costaneras cada 61 (dato)
PASO_PUNTAL = 171.0    # puntales cortos entre cordón y viga inclinada (dato: 171 | 171)
GAP_PUNTAL = 15.0      # desde qué separación cordón-viga se ponen puntales (supuesto)
BUNKER_LOSA = 20.0     # losa del búnker (dato)
BUNKER_MURO = 25.0     # muros del búnker (dato)
BUNKER_PISO = 20.0     # radier (dato lámina 05: piso −292, radier a −312)
BUNKER_ZAPATA = (100.0, 30.0)   # zapata corrida bajo los muros, ancho x alto (dato lámina 05: 100 de ancho, −312 a −342)
BUNKER_H = 280.0       # altura interior terminada (Gabriel; el original tenía 272)

def r1(v): return round(float(v), 1)

def main(estudio_json, sitio_json, salida):
    E = json.load(open(estudio_json)); S = json.load(open(sitio_json))
    ox, oy = S['estudio_origen']; z0 = E['nivel_piso']['z_cm']
    W, L = E['exterior']['ancho'], E['exterior']['largo']           # 1005 x 1525
    # ---------- ejes ----------
    xA = [MURO / 2, 257.5, 502.5, 742.5, W - MURO / 2]               # 1..5 (el 4 sobre el tabique estudio | baño-bodega)
    xN = ['1', '2', '3', '4', '5']
    yB = 612.5                                                        # tabique cafetería | estudio (y muro sur del búnker)
    yA = [MURO / 2, 312.5, yB, 912.5, 1212.5, L - MURO / 2]           # A, A2, B, C, D, E
    yN = ['A', 'A2', 'B', 'C', 'D', 'E']
    ejes = dict(x={n: r1(v) for n, v in zip(xN, xA)}, y={n: r1(v) for n, v in zip(yN, yA)},
                nota='Ejes nuevos (1-5 de poniente a oriente, A-E de norte a sur). El 4 va sobre el tabique estudio/baño-bodega; '
                     'B sobre el tabique cafetería/estudio, que coincide con el muro sur del búnker; A2, C y D solo tienen pilares en las fachadas laterales.')
    def ap(x, y, z): return [r1(ox + x), r1(oy + y), r1(z0 + z)]
    def z_viga(y): return H_PILAR + PEND * (y - yA[0])               # cara inferior de la viga inclinada (401 en el eje A)
    M = []
    def m(id_, c, p, a, b, d, **k): M.append(dict(id=id_, c=c, p=p, a=ap(*a), b=ap(*b), d=d, **k))

    # ---------- pilares ----------
    # fachadas norte (A), tabique (B) y sur (E): 5 pilares cada una. PM1 150x150x5 en los ejes 2 y 3 (como 1.b y 1.c del
    # original), PM2 150x150x4 en el resto. Laterales (ejes 1 y 5) en A2, C y D: PM3 RECT 150x100x3 (como los intermedios de 2.a/3.a).
    for yn, y in (('A', yA[0]), ('B', yB), ('E', yA[5])):
        for xn, x in zip(xN, xA):
            pm = 'PM1' if xn in ('2', '3') else 'PM2'
            perfil = 'CUAD 150x150x5' if pm == 'PM1' else 'CUAD 150x150x4'
            apoyo = 'sobre el muro norte del búnker' if yn == 'A' else ('sobre el muro sur del búnker' if yn == 'B' else 'sobre cimiento corrido')
            # el pilar llega hasta la cara inferior de la viga inclinada (lámina 05: +447 en el lado alto, +411 en el bajo)
            m(f'P-{xn}{yn}', 'pilar', perfil, (x, y, 0), (x, y, z_viga(y)), f'{pm} eje {xn} x {yn}, {apoyo}; llega a la viga inclinada (+{z_viga(y):.0f})', alma='Y')
    for yn in ('A2', 'C', 'D'):
        y = yA[yN.index(yn)]
        for xn, x in (('1', xA[0]), ('5', xA[4])):
            m(f'P-{xn}{yn}', 'pilar', 'RECT 150x100x3', (x, y, 0), (x, y, z_viga(y)), f'PM3 eje {xn} x {yn}, pilar intermedio de la fachada lateral; llega a la viga inclinada', alma='Y')
    # ---------- vigas E-O a +401 (CUAD 100x100x3) en A, B y E ----------
    for yn, y in (('A', yA[0]), ('B', yB), ('E', yA[5])):
        for i in range(4):
            m(f'VT-{yn}-{xN[i]}{xN[i+1]}', 'viga', 'CUAD 100x100x3', (xA[i], y, H_PILAR), (xA[i + 1], y, H_PILAR), f'viga E-O a +4,01 entre pilares {xN[i]} y {xN[i+1]} del eje {yn}')
    # vigas E-O a +401 en A2, C y D solo existen como dinteles de las fachadas laterales: no cruzan los recintos
    # ---------- marcos N-S: cordón horizontal a +401, viga inclinada de techo y puntales ----------
    y_ini, y_fin = yA[0] - ALERO_NS, yA[5] + ALERO_NS                  # con aleros
    for xn, x in zip(xN, xA):
        lateral = xn in ('1', '5')
        # cordón horizontal CUAD 100x100x3 a +4,01 solo en los marcos interiores (como 1.b y 1.c del original: los 44,2 m de
        # CUAD 100x100x3 de la cubicación son las dos fachadas largas más los dos cordones); en los ejes laterales los
        # pilares llegan directo a la viga inclinada, como en 1.a, 2.a y 3.a
        if not lateral:
            for (ya, yb) in ((yA[0], yB), (yB, yA[5])):
                m(f'VC-{xn}-{int(ya)}', 'viga', 'CUAD 100x100x3', (x, ya, H_PILAR), (x, yb, H_PILAR), f'cordón horizontal a +4,01, eje {xn}, {ya:.0f}..{yb:.0f} (luz sin pilares intermedios, como 1.b y 1.c del original)')
        # viga inclinada de alero a alero: 200x150x5 en los marcos interiores (luz de 9,0 m en el estudio), 200x150x3 en los laterales
        perfil = 'RECT 200x150x3' if lateral else 'RECT 200x150x5'
        m(f'VI-{xn}', 'cabio', perfil, (x, y_ini, z_viga(y_ini)), (x, y_fin, z_viga(y_fin)), f'viga inclinada de techo, eje {xn}, 3,5 % subiendo al sur, aleros de 80')
        # puntales cortos donde la viga se separa del cordón (cada 171 desde donde la separación pasa de 15 cm); solo en los marcos interiores
        y = yA[0]
        while y <= yA[5] + 1 and not lateral:
            gap = z_viga(y) - H_PILAR
            if gap >= GAP_PUNTAL and all(abs(y - yy) > 30 for yy in (yA[0], yB, yA[5])):
                m(f'PT-{xn}-{int(y)}', 'puntal', 'RECT 150x100x3', (x, y, H_PILAR), (x, y, z_viga(y)), f'puntal entre cordón y viga inclinada, eje {xn}, separación {gap:.0f} cm')
            y += PASO_PUNTAL
    # ---------- costaneras CA 100x50x15x3 cada 61, de alero a alero, continuas sobre las 5 vigas ----------
    x_ini, x_fin = xA[0] - ALERO_EO, xA[4] + ALERO_EO
    n = int(math.floor((y_fin - y_ini) / PASO_COST)) + 1
    for i in range(n):
        y = y_ini + i * PASO_COST
        z = z_viga(y) + PERFILES['RECT 200x150x5']['h']
        m(f'CO-{i+1:02d}', 'costanera', 'CA 100x50x15x3', (x_ini, y, z), (x_fin, y, z), f'costanera {i+1} de {n}, y = {y:.0f}')
    # soporte del alero C150x50x3 en los bordes norte y sur (dato: "C150x50x3 soporte")
    for yn, y in (('norte', y_ini), ('sur', y_fin)):
        m(f'SA-{yn}', 'otro', 'C 150x50x3', (x_ini, y, z_viga(y) + 10), (x_fin, y, z_viga(y) + 10), f'soporte C 150x50x3 del alero {yn}')
    # ---------- cruces de San Andrés C150x50x3 en muros ciegos ----------
    def cruz(id_, a, b, d):
        (xa, ya), (xb, yb) = a, b
        m(f'{id_}a', 'diagonal', 'C 150x50x3', (xa, ya, 0), (xb, yb, H_PILAR), d)
        m(f'{id_}b', 'diagonal', 'C 150x50x3', (xa, ya, H_PILAR), (xb, yb, 0), d)
    for xn, x in (('1', xA[0]), ('5', xA[4])):
        cruz(f'X-{xn}-AA2', (x, yA[0]), (x, yA[1]), f'cruz en la fachada lateral {xn}, tramo A-A2 (norte), como las de los extremos del original')
        cruz(f'X-{xn}-DE', (x, yA[4]), (x, yA[5]), f'cruz en la fachada lateral {xn}, tramo D-E (sur)')
    cruz('X-B-12', (xA[0], yB), (xA[1], yB), 'cruz E-O en el tabique cafetería/estudio, tramo 1-2 (muro ciego): propuesta para la rigidez E-O')
    cruz('X-B-45', (xA[3], yB), (xA[4], yB), 'cruz E-O en el tabique cafetería/baño, tramo 4-5 (muro ciego): propuesta para la rigidez E-O')
    # ---------- tensores Fe 16 en el plano del techo (X en los paños extremos, como en la planta de cubierta) ----------
    paños = [(yA[0], yA[1]), (yA[1], yB), (yB, yA[3]), (yA[3], yA[4]), (yA[4], yA[5])]
    for (xa, xb, et) in ((xA[0], xA[1], '12'), (xA[3], xA[4], '45')):
        for (ya, yb) in paños:
            zt = lambda y: z_viga(y) + 20
            m(f'T-{et}-{int(ya)}a', 'tensor', 'FE 16', (xa, ya, zt(ya)), (xb, yb, zt(yb)), f'tensor Fe 16 del techo, paño {et} x {ya:.0f}..{yb:.0f}')
            m(f'T-{et}-{int(ya)}b', 'tensor', 'FE 16', (xb, ya, zt(ya)), (xa, yb, zt(yb)), f'tensor Fe 16 del techo, paño {et} x {ya:.0f}..{yb:.0f}')
    # colgadores Fe 10 no hacen falta: las costaneras salvan 2,4-2,5 m (el original los tenía en el paño de 3,65)

    # ---------- hormigón del búnker ----------
    bx0, bx1, by0, by1 = 0.0, W, 0.0, yB + MURO / 2                     # exterior 1005 x 625: el muro sur queda bajo el tabique B
    z_losa_sup, z_losa_inf = 0.0, -BUNKER_LOSA
    z_piso_sup = z_losa_inf - BUNKER_H; z_piso_inf = z_piso_sup - BUNKER_PISO
    def rect(x0, y0, x1, y1): return [ap(x0, y0, 0)[:2], ap(x1, y0, 0)[:2], ap(x1, y1, 0)[:2], ap(x0, y1, 0)[:2]]
    muros = [
        dict(id='M-N', pts=rect(bx0, by0, bx1, by0 + BUNKER_MURO), lado='norte'),
        dict(id='M-S', pts=rect(bx0, by1 - BUNKER_MURO, bx1, by1), lado='sur (bajo el tabique B: recibe los 5 pilares del eje B)'),
        dict(id='M-O', pts=rect(bx0, by0, bx0 + BUNKER_MURO, by1), lado='poniente'),
        dict(id='M-E', pts=rect(bx1 - BUNKER_MURO, by0, bx1, by1), lado='oriente'),
    ]
    esc = E['recintos'][[r['id'] for r in E['recintos']].index('escalera')]['pts']
    ex0, ey0, ex1, ey1 = esc[0][0], esc[0][1], esc[1][0], esc[2][1]       # 851,7..980 x 200..575 (interior)
    hormigon = dict(
        muros=dict(espesor=BUNKER_MURO, armadura='V ø12@15, H ø10@20 (dato: DM muro e=25)', z_inf=r1(z0 + z_piso_sup), z_sup=r1(z0 + z_losa_inf), piezas=muros),
        losa=dict(espesor=BUNKER_LOSA, pts=rect(bx0, by0, bx1, by1), hueco=rect(ex0, ey0, ex1, ey1), z_inf=r1(z0 + z_losa_inf), z_sup=r1(z0 + z_losa_sup),
                  armadura='ø10@20 en la luz corta y ø8@20 en la larga, borde 3ø12 (dato del original; la luz corta pasa de 5,00 a 5,75 m: recalcular)'),
        piso=dict(espesor=BUNKER_PISO, pts=rect(bx0, by0, bx1, by1), z_inf=r1(z0 + z_piso_inf), z_sup=r1(z0 + z_piso_sup), armadura='radier de 20 (dato lámina 05: piso a −292, radier a −312)'),
        zapatas=dict(ancho=BUNKER_ZAPATA[0], alto=BUNKER_ZAPATA[1], z_sup=r1(z0 + z_piso_inf), z_inf=r1(z0 + z_piso_inf - BUNKER_ZAPATA[1]),
                     piezas=[dict(id='Z-N', pts=rect(bx0 - 37.5, by0 + 12.5 - 50, bx1 + 37.5, by0 + 12.5 + 50)), dict(id='Z-S', pts=rect(bx0 - 37.5, by1 - 12.5 - 50, bx1 + 37.5, by1 - 12.5 + 50)),
                             dict(id='Z-O', pts=rect(bx0 + 12.5 - 50, by0, bx0 + 12.5 + 50, by1)), dict(id='Z-E', pts=rect(bx1 - 12.5 - 50, by0, bx1 - 12.5 + 50, by1))],
                     dato='zapata corrida de 100 de ancho y 30 de alto bajo los muros del búnker (dato lámina 05: −312 a −342, más 5 de emplantillado)'),
        vigas=[dict(id='VHA-3', nombre='VHA 25/40', pts=rect(xA[2] - 12.5, by0 + BUNKER_MURO, xA[2] + 12.5, by1 - BUNKER_MURO), z_inf=r1(z0 + z_losa_inf - 20), z_sup=r1(z0 + z_losa_inf),
                    armadura='3ø12 + 2ø10 + 3ø16, Est ø10@20 (dato: detalle VHA 25/40)', d='viga bajo la losa en el eje 3, de muro a muro (575): parte la losa en dos paños de 4,8 x 5,75 como la del eje 2.a original'),
               dict(id='VHA-esc', nombre='VHA 25/40 de borde', pts=rect(ex0 - 25, ey0 - 25, ex0, ey1), z_inf=r1(z0 + z_losa_inf - 20), z_sup=r1(z0 + z_losa_inf),
                    armadura='como VHA 25/40 (propuesta)', d='viga de borde del hueco de la escalera (propuesta: el original llevaba armadura de borde 3ø12)')],
        escalera=dict(pts=rect(ex0, ey0, ex1, ey1), ancho=r1(ex1 - ex0), largo=r1(ey1 - ey0), baja=r1(BUNKER_LOSA + BUNKER_H), z_arriba=r1(z0), z_abajo=r1(z0 + z_piso_sup),
                      nota=f'baja {(BUNKER_LOSA + BUNKER_H)/100:.2f} m en {(ey1 - ey0)/100:.2f} m: con 16 peldaños salen huellas de {(ey1 - ey0)/16:.0f} cm y contrahuellas de {(BUNKER_LOSA + BUNKER_H)/16:.1f} cm (revisar: lo cómodo es 28/18)'),
        interior=dict(ancho=r1(bx1 - bx0 - 2 * BUNKER_MURO), largo=r1(by1 - by0 - 2 * BUNKER_MURO), alto=BUNKER_H),
    )
    # ---------- cimientos corridos CF 25/40 bajo los pilares que no apoyan en el búnker ----------
    # fuera del búnker, como bajo el eje F del original: sobrecimiento de 25 (0 a −50) y cimiento corrido de 80 x 25 (−50 a −75)
    cimientos = [dict(id='CF-1', pts=rect(xA[0] - 40, yB, xA[0] + 40, L), d='bajo el eje 1, de B a E'),
                 dict(id='CF-5', pts=rect(xA[4] - 40, yB, xA[4] + 40, L), d='bajo el eje 5, de B a E'),
                 dict(id='CF-E', pts=rect(-27.5, yA[5] - 40, W + 27.5, yA[5] + 40), d='bajo la fachada sur (eje E)')]
    cimiento_dato = 'sobrecimiento de 25 de 0 a −50 y cimiento corrido de 80 x 25 de −50 a −75 (dato lámina 05, eje F; el detalle está en el plano 01, que no está en la carpeta)'
    # ---------- cubicación ----------
    cub = {}
    for mb in M:
        a, b = mb['a'], mb['b']; L_ = math.dist(a, b) / 100
        cub[mb['p']] = cub.get(mb['p'], 0) + L_
    # solo los largos del modelo (la cubicación del ingeniero no se usa como referencia: Gabriel, 2026-10-12)
    cubicacion = [dict(perfil=p, metros=round(cub.get(p, 0), 1), kg=round(cub.get(p, 0) * PESO[p])) for p in PESO if cub.get(p, 0) > 0]
    tot = round(sum(c['kg'] for c in cubicacion)); tot_o = None
    # ---------- techo (para dibujar la cubierta y para la ficha) ----------
    techo = dict(contorno=[ap(x_ini, y_ini, 0)[:2], ap(x_fin, y_ini, 0)[:2], ap(x_fin, y_fin, 0)[:2], ap(x_ini, y_fin, 0)[:2]],
                 y0=r1(oy + y_ini), y1=r1(oy + y_fin), z0=r1(z0 + z_viga(y_ini) + 30), z1=r1(z0 + z_viga(y_fin) + 30), espesor=5,
                 nota='cubierta sobre las costaneras (a 30 cm sobre la cara inferior de la viga inclinada)')
    cielo = dict(z_norte=r1(z0 + z_viga(yA[0])), z_sur=r1(z0 + z_viga(yA[5])), y_norte=r1(oy + yA[0]), y_sur=r1(oy + yA[5]))
    # ---------- cambios y preguntas ----------
    cambios = [
        dict(que='Orientación', original='búnker bajo el tramo E1–A1 y techo subiendo hacia A1', nuevo='búnker bajo la cafetería (norte) y techo subiendo hacia el sur, igual que la casa', por='Gabriel'),
        dict(que='Planta', original='11,05 x 10,25 m entre ejes (5 ejes E-O a 205 | 365 | 205 | 330)', nuevo='10,05 x 15,25 m exteriores (ejes 1-5 a 245 | 245 | 240 | 250 y A-E a 600 | 300 | 300 | 300)', por='planta de Gabriel; separación de ejes: propuesta'),
        dict(que='Búnker', original='5,00 x 10,55 m interiores, 2,72 m de altura, losa 20, muros 25, viga VHA 25/40 en 2.a', nuevo='5,75 x 9,55 m interiores, 2,80 m de altura; mismos muros y losa; VHA 25/40 en el eje 3 y viga de borde en la escalera', por='Gabriel (medidas) · propuesta (vigas)'),
        dict(que='Muro sur del búnker', original='—', nuevo='queda exactamente bajo el tabique cafetería/estudio (eje B): recibe los 5 pilares de ese eje. Para eso el búnker mide 6,25 m exteriores (el muro sale 25 cm bajo el tabique)', por='propuesta'),
        dict(que='Luz de la losa del búnker', original='5,00 m (ø10@20)', nuevo='5,75 m: +15 % de luz, +32 % de momento; recalcular armadura o espesor', por='para el ingeniero'),
        dict(que='Marcos interiores', original='1.b y 1.c salvan 10,25 m sin pilares (cordón + viga inclinada 200x150x5 + puntales)', nuevo='los ejes 2, 3 y 4 salvan 9,0 m en el estudio (B–E) con el mismo esquema, y 6,0 m en la cafetería (A–B)', por='propuesta'),
        dict(que='Pilares', original='18 (5 por fachada larga + intermedios en 2.a y 3.a)', nuevo='21 (5 en A, 5 en B, 5 en E y 6 en las fachadas laterales); ninguno dentro de los recintos', por='propuesta'),
        dict(que='Costaneras', original='CA 100x50x15x3 @61, paño mayor 3,65 con colgadores ø10', nuevo='mismo perfil y paso; paño mayor 2,50: sin colgadores', por='propuesta'),
        dict(que='Cruces C 150x50x3', original='en los tramos extremos de las fachadas N-S (1.a, 2.a, 3.a)', nuevo='en los tramos extremos de las fachadas laterales (A–A2 y D–E) y dos cruces E-O en el tabique B (muros ciegos)', por='propuesta: el original no mostraba cruces E-O'),
        dict(que='Tensores Fe 16', original='X en el plano del techo', nuevo='X en los paños 1-2 y 4-5, de norte a sur', por='propuesta'),
        dict(que='Escalera al búnker', original='no estaba', nuevo='hueco de 1,28 x 3,75 junto al muro oriente, con viga de borde; baja 3,00 m', por='planta de Gabriel'),
        dict(que='Aleros', original='80 N-S y 52 E-O', nuevo='iguales', por='dato'),
        dict(que='Acero', original='—', nuevo=f'{tot} kg de perfiles en el modelo (sin pérdidas ni placas)', por='cubicación del modelo'),
    ]
    preguntas = [
        '¿Sirve el esquema de cordón horizontal + viga inclinada 200x150x5 + puntales para los 9,0 m del estudio (el original salvaba 10,25 m)?',
        'Losa del búnker: con 5,75 m de luz, ¿se mantiene e=20 con más armadura o conviene e=25? ¿Basta una VHA 25/40 al centro (paños de 4,8 x 5,75)?',
        '¿Acepta que los pilares del eje B apoyen sobre el muro sur del búnker (el búnker crece a 6,25 m exteriores)?',
        'Rigidez E-O: el original no mostraba cruces en las fachadas largas. ¿Van bien las dos cruces propuestas en el tabique B, o prefiere marcos rígidos?',
        'Escalera: 3,75 m de desarrollo para bajar 3,00 m da huellas de 23 cm. ¿Se alarga el hueco o se acepta?',
        'Fundaciones fuera del búnker: ¿sobrecimiento y cimiento corrido bajo los ejes 1, 5 y E como bajo el eje F del original, o zapatas aisladas bajo los PM1? (falta el plano 01)',
        'Altura interior del búnker 2,80 (el original tenía 2,72): el radier baja 8 cm; ¿cambia algo en los muros?',
    ]
    out = dict(
        fuente='Adaptación de las láminas 03, 04 y 05 del ingeniero (proyecto del estudio, abril 2026) a la planta de Gabriel (2026-10-11); propuesta para revisión del ingeniero, no es un cálculo',
        marco='cm del marco de la app; z = 0 en el piso del nivel 1 de la casa; el piso del estudio (NPOG 0,00 del ingeniero) está en z = %s' % z0,
        z_piso=z0, ejes=ejes, perfiles={k: PERFILES[k] for k in sorted(set(mb['p'] for mb in M))}, miembros=M,
        hormigon=hormigon, cimientos=cimientos, cimiento_dato=cimiento_dato, techo=techo, cielo=cielo, cubicacion=cubicacion, total_kg=tot,
        cambios=cambios, preguntas=preguntas,
        parametros=dict(muro=MURO, h_pilar=H_PILAR, pendiente=PEND, alero_ns=ALERO_NS, alero_eo=ALERO_EO, paso_costanera=PASO_COST, paso_puntal=PASO_PUNTAL,
                        bunker=dict(losa=BUNKER_LOSA, muro=BUNKER_MURO, piso=BUNKER_PISO, alto=BUNKER_H)),
    )
    js = 'const DATA_ESTUDIO_EST = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n'
    open(salida, 'w').write(js)
    clases = {}
    for mb in M: clases[mb['c']] = clases.get(mb['c'], 0) + 1
    print(f'{salida}: {len(M)} piezas {clases} · acero {tot} kg · búnker {hormigon["interior"]["ancho"]/100:.2f} x {hormigon["interior"]["largo"]/100:.2f} x {BUNKER_H/100:.2f} m')
    for c in cubicacion: print(f"   {c['perfil']:16s} {c['metros']:7.1f} m  {c['kg']:5d} kg")

if __name__ == '__main__':
    main(*sys.argv[1:4])
