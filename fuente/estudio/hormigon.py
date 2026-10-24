# -*- coding: utf-8 -*-
"""Hormigón armado del estudio: búnker, fundaciones, radieres, placas base y enfierradura, con los datos de las
láminas del ingeniero (abril 2026) aplicados a la planta de Gabriel. Lo llama generar_estudio_estructura.py.

Fuentes (dato): lámina 01 PLANTA FUNDACIONES rev 1 (27-04-2026) y rev 0 (06-04-2026): cortes a-a / b-b / c-c,
detalle placa base PLb, CF 25/40; lámina 02 rev G: especificaciones técnicas; lámina 03 rev H: planta losa, VHA 25/40,
elevación 1.a; lámina 05 rev H: elevaciones E-O. Las medidas de la planta (búnker 10,05 x 6,00 x 2,80, losa 20,
muros 25, niveles) son las de Gabriel y no se tocan: lo que se toma del ingeniero son secciones, armaduras, niveles
relativos y detalles.

Todo en cm. Las coordenadas que salen van en el marco de la app (función ap del generador); los niveles se dan
respecto del NPOG 0,00 (piso terminado del estudio) y se convierten con z0.
"""
import math

# ---------- lo que dicen las láminas (dato), con los cambios de la revisión estructural (Gabriel, 23-10-2026: "haz los cambios, me cuadra todo") ----------
# Revisión: modelo 3D propio (fuente/estudio/calculo/) + 14 revisores independientes; agua 1,50 m sobre el piso del búnker.
LOSA = 25.0                 # losa de techo del búnker: e=20 (corte a-a, diseñada para 5,00 m) → 25 continua con los muros (aquí salva 6,45; revisión 23-10-2026)
MURO = 30.0                 # muro DM del búnker: e=25 en el corte a-a; 30 desde la revisión del 23-10-2026 (Gabriel: "había un tema con el ancho del muro y los fierros"): con ø16 por fuera, ø12 por dentro y sus
                            # horizontales no cabían el water-stop ni los pernos de las placas, y ACI 350 pide 30 en muros de 3 m o más con agua. Crece hacia afuera: el interior no cambia
RADIER_BUNKER = 10.0        # radier e=10 (corte a-a / c-c)
RELLENO_BUNKER = 10.0       # relleno granular T.máx 1 1/2", 90 % Proctor modificado, bajo el radier (corte a-a)
ZAPATA_B = (100.0, 30.0)    # zapata corrida del corte a-a (37,5 + 25 + 37,5 = 100, 30 de alto): desde el 15-10-2026 es la franja bajo cada muro de la LOSA DE FUNDACIÓN
LOSA_FUND = 35.0            # losa de fundación armada bajo TODO el búnker, unida a los muros (ingeniero vía Gabriel, 15-10-2026: e=30); 35 desde la revisión del 23-10-2026 (con 30 y ø12@15 no pasaba ni en fisuras)
LOSA_FUND_MARGEN = 37.5     # sobresale 37,5 de la cara exterior de los muros, como la zapata corrida
EMPLANTILLADO = 10.0        # emplantillado G5 "Var. / Mn. 10" (sello 20 cm en el estrato indicado en la memoria de cálculo)
SOBRECIM = (30.0, 50.0)     # 30 desde la revisión del 23-10-2026 (con 25 no cabían los 4 pernos de las placas PLc entre su fierro); antes: sobrecimiento de 25 x 50 bajo los pilares fuera del búnker (corte b-b: cadena 50 | 25 | var. mín. 10 = 75 hasta el sello)
CIMIENTO = (80.0, 25.0)     # cimiento corrido 27,5 + 25 + 27,5 = 80 de ancho, 25 de alto, de −50 (NTN) a −75 (corte b-b)
CF = (30.0, 50.0)           # 30 desde la revisión del 23-10-2026 (mismo motivo); antes 25 × CF bajo los ejes interiores con pilares: 25 × 50 de 0 a −50 (fondo en el NTN). El ingeniero lo dibuja 25/40 de −10 a −50 bajo el radier de 10 (elevación 2.a: cadena 10 + 40);
                            # Gabriel (19-10-2026): "las fundaciones tienen que llegar hasta la losa terminada, hacen de perímetro de la losa" → llega hasta la cara del radier y el radier va entre los CF
CF_TOPE = 0.0               # cara superior del CF = cara del radier (NPOG 0,00); el anclaje de 43 de la placa queda dentro con 7 de recubrimiento
RADIER_EST = 10.0           # radier e=10 del estudio (corte b-b)
POLIESTIRENO = 10.0         # poliestireno expandido de alta densidad e=100 mm bajo el radier (corte b-b)
RELLENO_EST = 15.0          # relleno granular 15 bajo el poliestireno, sobre sub base granular compactada (corte b-b)
VHA = (25.0, 45.0)          # VHA 25/45: 25 dentro de la losa + 20 bajo ella (el detalle VHA 25/40 colgaba 20 de una losa de 20; revisión 23-10-2026)
PLACA = (20.0, 20.0, 0.8)   # PLb 200 x 200 x 8 mm (detalle placa base) en los pilares sin cruz
ANCLAJE = dict(diam=19, n=2, sep=14.0, largo=43.0, gancho=10.0, estribos='ø8@20')   # 1+1 ø3/4 en horquilla de L=1200 mm (140 bajo la placa, ramas de 430 y ganchos de 100); desde la revisión van PARALELAS (una al lado de la otra) para que las dos coronas toquen la placa
PLACA_C = (25.0, 25.0, 1.2) # PLc 250 x 250 x 12 mm en los pilares con cruz (revisión 23-10-2026: con la horquilla fallaban 14 de 25 anclajes)
ANCLAJE_C = dict(diam=19, n=4, sep=12.0, largo=45.0, golilla=5.0)   # 4 pernos ø3/4" A36 con tuerca y golilla 50 x 50 x 10 abajo (hef 45), bajo las paredes del tubo
DADO = (140.0, 140.0, 119.5) # dado 1,40 x 1,40 bajo los pilares 4C y 4C2 (el CF solo no tiene peso para el arranque de las cruces); baja hasta 10 sobre el sello de −140
                            # (revisión de fundaciones del 23-10-2026: con 0,80 y hormigón pobre debajo, el sismo EX+ lo levantaba ~5 mm; el hormigón pobre no cuenta: no está amarrado)
SELLO_EXT = -140.0          # sello de las fundaciones fuera del búnker: 0,90 bajo el NTN (−50), como pide el informe de suelos; hasta ahí hormigón pobre G5
JUNTA = 2.0                 # junta de 2 cm entre el búnker y los sobrecimientos / CF que nacen en su muro sur (sin barras ancladas al muro)
GAP = 0.5                   # separación entre piezas apiladas, para que las caras no parpadeen en el 3D

ESPECIFICACIONES = dict(
    emplantillado='Hormigón G5 (y hormigón pobre G5 hasta el sello de las fundaciones de fachada)', hormigon='Hormigón G30 en el búnker (a/c ≤ 0,45, aditivo cristalizante, curado húmedo 7 días); G25 en el resto', acero='Acero A630-420H',
    recubrimientos={'fundaciones': 5, 'muros del búnker, cara exterior': 4, 'elementos de hormigón armado': 3, 'losa': 2}, traslapo='60 diámetros',
    fuente='lámina 02 rev G (07-04-2026), especificaciones técnicas generales; G30, cristalizante y recubrimiento exterior 4: revisión 23-10-2026')
IMPERMEABILIZACION = dict(
    membrana='por fuera: membrana HDPE pre-adherida bajo la losa de fundación (sobre el emplantillado, sube por el canto del vuelo) y membrana adherida en los muros, con chaflán de 5 × 5 en los rincones, hasta 30 cm sobre el terreno; encima, lámina drenante de nódulos con geotextil',
    junta='junta losa–muro con water-stop de PVC de 15 a 23 cm con bulbo, en un cuello de 15 cm hormigonado junto con la losa, más manguera de inyección de respaldo; los 4 muros en una sola faena, sin juntas verticales',
    pasadas='pasadas con pasamuros de aleta embebidos (de preferencia por la losa de techo); amarras de moldaje con sello; nada se perfora bajo el nivel del agua',
    dren='dren perimetral ø110 ranurado en grava con geotextil, al nivel del sello, con registros en las esquinas y salida por gravedad (o cámara con 2 bombas alternadas y alarma); relleno granular compactado al 95 % con tapa de suelo fino y pendiente hacia afuera',
    interior='opcional: cámara drenada (lámina de nódulos y canaleta a un pozo de achique) detrás de la sala acústica, y deshumidificador',
    fuente='revisión 23-10-2026 (BS 8102, grado 3: recinto habitable seco)')
KGM = {6: 0.222, 8: 0.395, 10: 0.617, 12: 0.888, 16: 1.578, 19: 2.235}   # kg/m por diámetro (ø19 = 3/4")
EJE_MURO = {'N': 'A', 'S': 'B', 'O': '1', 'E': '5'}   # muros del búnker por su eje: los textos no llevan orientación (Gabriel, por consejo de José, 23-10-2026)

def armar(c):
    """c: dict con ap, rect, r1, z0, ox, oy, xA, yA, yB, yC, W, L, rec, bk (pts del búnker interior, local), BUNKER_H,
    pilares (lista de miembros 'pilar' con a=[x,y,z] app y p=perfil), escalera (dict ya armado), ex0, ex_h, ey0, ey1,
    y_desc, x3 (eje 3). Devuelve (hormigon, fierros, cubicacion)."""
    ap, rect, r1 = c['ap'], c['rect'], c['r1']
    z0, xA, yA, yB, yC, W, L = c['z0'], c['xA'], c['yA'], c['yB'], c['yC'], c['W'], c['L']
    yC2 = c.get('yC2', yC)                        # tabique cabina/bodega (eje C2, con pilares y CF desde el 14-10-2026)
    bk = c['bk']; H = c['BUNKER_H']
    bx0, by0, bx1, by1 = bk[0][0] - MURO, bk[0][1] - MURO, bk[1][0] + MURO, bk[2][1] + MURO   # exterior del búnker (local)
    ex0, ex_h, ey0, ey1, y_desc = c['ex0'], c['ex_h'], c['ey0'], c['ey1'], c['y_desc']
    x3 = c['x3']
    # ---------- niveles (NPOG, cm): 0 = piso terminado del estudio = cara superior de la losa ----------
    z_losa_inf = -LOSA; z_piso = z_losa_inf - H                      # −20, −341 (H = 3,10 libres terminados + piso + cielo)
    # losa de fundación de 30 bajo todo el búnker (ingeniero, 15-10-2026): su cara superior ES el piso del búnker; no hay relleno ni radier aparte
    z_rad_inf = z_piso; z_rell_inf = z_piso                           # (sin radier ni relleno: quedan iguales al piso por compatibilidad)
    z_zap_sup = z_piso; z_zap_inf = z_zap_sup - LOSA_FUND            # −341, −371 (el sello no cambia respecto de la zapata corrida anterior)
    z_emp_inf = z_zap_inf - EMPLANTILLADO                            # −381
    Z = lambda z: r1(z0 + z)
    hb = ZAPATA_B[0] / 2                                             # 50: media zapata

    def pieza(id_, x0, y0, x1, y1, zi, zs, nombre, d, **k):
        return dict(id=id_, pts=rect(x0, y0, x1, y1), z_inf=Z(zi), z_sup=Z(zs), nombre=nombre, d=d, **k)

    # ---------- búnker ----------
    muros = dict(espesor=MURO, z_inf=Z(z_zap_sup + GAP), z_sup=Z(z_losa_inf), alto=r1(z_losa_inf - z_zap_sup),
                 armadura='e=30, DM (doble malla): V ø16@15 por fuera (bajan a la malla inferior de la losa de fundación con pata de 60 traslapada) y ø12@15 por dentro (pata de 30), con gancho de 20 en la losa de techo; H ø12@15 en las dos caras; 2ø12 de coronamiento; recubrimiento 4 por fuera y 3 por dentro; G30',
                 fuente='lámina 01 rev 1, cortes a-a y c-c; lámina 03 rev H, elevación 1.a; armadura de la revisión del 23-10-2026 (el ø12@15 / ø10@20 de la lámina no pasaba en la base ni en fisuras)',
                 piezas=[dict(id='M-N', pts=rect(bx0, by0, bx1, by0 + MURO), lado='del eje A (recibe sus 5 pilares)'),
                         dict(id='M-S', pts=rect(bx0, by1 - MURO, bx1, by1), lado='del eje B, bajo el tabique cafetería/estudio (recibe sus 5 pilares)'),
                         dict(id='M-O', pts=rect(bx0, by0 + MURO, bx0 + MURO, by1 - MURO), lado='del eje 1'),
                         dict(id='M-E', pts=rect(bx1 - MURO, by0 + MURO, bx1, by1 - MURO), lado='del eje 5')])
    losa = dict(espesor=LOSA, pts=rect(bx0, by0, bx1, by1), hueco=rect(ex_h, ey0, ex1 := c['ex1'], ey1), z_inf=Z(z_losa_inf), z_sup=Z(0),
                armadura='inferior: ø10@15 en los dos sentidos (ganchos en los muros); superior: ø12@15 en L sobre los 4 muros (pata de 72 por la cara exterior del muro y 180 dentro de la losa) y ø10@20 L=160 sobre la VHA; '
                         'vigas de borde 25/45 en los lados del hueco de la escalera hacia el eje 4 y hacia el eje A (el del eje B es el muro) y suples ø10@15 arriba y abajo en 1,50 × 1,50 en sus 2 esquinas libres; recubrimiento 2; G30',
                fuente='revisión 23-10-2026: la losa de 20 de la lámina 03 rev H (L001/L002, diseñada para 5,00 m) no pasaba con 6,45 m; ahora e=25 y continua con los muros')
    piso = None; relleno_b = None   # sin radier ni relleno desde el 15-10-2026: el piso es la cara superior de la losa de fundación
    # losa de fundación armada e=30 bajo todo el búnker, unida a los muros y sobresaliendo 37,5 (ingeniero vía Gabriel, 15-10-2026).
    # Las cuatro franjas bajo los muros (37,5 + 25 + 37,5 = 100) se mantienen como contornos para las láminas y las elevaciones.
    zx0, zy0, zx1, zy1 = bx0 - LOSA_FUND_MARGEN, by0 - LOSA_FUND_MARGEN, bx1 + LOSA_FUND_MARGEN, by1 + LOSA_FUND_MARGEN
    emp_lf = dict(espesor=EMPLANTILLADO, z_sup=Z(z_zap_inf - GAP), z_inf=Z(z_emp_inf), hormigon='G5', piezas=[dict(id='EMP-LF', pts=rect(zx0, zy0, zx1, zy1))],
                  nota='Var. / mín. 10 bajo toda la losa de fundación: el sello va 20 cm dentro del estrato indicado en la memoria de cálculo')
    losa_fundacion = dict(espesor=LOSA_FUND, margen=LOSA_FUND_MARGEN, pts=rect(zx0, zy0, zx1, zy1), z_sup=Z(z_zap_sup), z_inf=Z(z_zap_inf),
                          piezas=[pieza('LF', zx0, zy0, zx1, zy1, z_zap_inf, z_zap_sup, 'Losa de fundación del búnker', f'e={LOSA_FUND:.0f} bajo todo el búnker, unida a los muros; sobresale {LOSA_FUND_MARGEN:.1f} de su cara exterior; su cara superior es el piso del búnker'.replace('.', ','))],
                          armadura='doble malla: ø16@15 en A–B (luz corta) y ø12@15 en 1–5, abajo (con ganchos de 15 hacia arriba en los bordes) y arriba; las verticales exteriores de los muros bajan con pata de 60 traslapada sobre la malla inferior; recubrimiento 5; G30',
                          fuente='ingeniero (vía Gabriel, 15-10-2026): losa armada unida con la zapata de toda la fundación; e=35 y armadura de la revisión del 23-10-2026', emplantillado=emp_lf)
    zap_piezas = [pieza('ZC-N', zx0, zy0, zx1, zy0 + ZAPATA_B[0], z_zap_inf, z_zap_sup, 'Losa de fundación: franja bajo el muro del eje A', 'parte de la losa de fundación'),
                  pieza('ZC-S', zx0, zy1 - ZAPATA_B[0], zx1, zy1, z_zap_inf, z_zap_sup, 'Losa de fundación: franja bajo el muro del eje B', 'parte de la losa de fundación'),
                  pieza('ZC-O', zx0, zy0 + ZAPATA_B[0], zx0 + ZAPATA_B[0], zy1 - ZAPATA_B[0], z_zap_inf, z_zap_sup, 'Losa de fundación: franja bajo el muro del eje 1', 'parte de la losa de fundación'),
                  pieza('ZC-E', zx1 - ZAPATA_B[0], zy0 + ZAPATA_B[0], zx1, zy1 - ZAPATA_B[0], z_zap_inf, z_zap_sup, 'Losa de fundación: franja bajo el muro del eje 5', 'parte de la losa de fundación')]
    zapata_corrida = dict(ancho=ZAPATA_B[0], espesor=LOSA_FUND, z_sup=Z(z_zap_sup), z_inf=Z(z_zap_inf), piezas=zap_piezas, armadura=losa_fundacion['armadura'], emplantillado=emp_lf, fuente=losa_fundacion['fuente'],
                          nota='franjas de 100 (37,5 + 25 + 37,5) de la losa de fundación bajo cada muro, solo para contornos y cotas; el hormigón y la cubicación usan la losa completa (losa_fundacion)')
    # vigas bajo la losa
    NV = f'VHA {VHA[0]:.0f}/{VHA[1]:.0f}'
    arm_v = f'3ø12 arriba, 2ø10 al medio, 3ø16 abajo, Est ø10@15 ({LOSA:.0f} dentro de la losa + {VHA[1] - LOSA:.0f} bajo ella)'
    zv_inf, zv_sup = Z(z_losa_inf - (VHA[1] - LOSA)), Z(z_losa_inf)
    vigas = [dict(id='VHA-3', nombre=NV, pts=rect(x3 - 12.5, by0 + MURO, x3 + 12.5, by1 - MURO), z_inf=zv_inf, z_sup=zv_sup, armadura=arm_v,
                  d=f'viga bajo la losa en el eje 3, de muro a muro ({by1 - by0 - 2 * MURO:.0f})', fuente='lámina 03 rev H, detalle VHA 25/40; 25/45 y estribos @15 de la revisión del 23-10-2026'),
             dict(id='VHA-esc', nombre=f'{NV} de borde', pts=rect(ex0, ey0 - 25, ex_h, ey1), z_inf=zv_inf, z_sup=zv_sup, armadura=arm_v,
                  d='viga de borde del hueco de la escalera en su lado hacia el eje 4, bajo el muro de la caja; apoya en la viga de borde del lado A y en el muro del eje B', fuente='revisión 23-10-2026'),
             dict(id='VB-N', nombre=f'{NV} de borde', pts=rect(ex_h, ey0 - 25, bx1 - MURO, ey0), z_inf=zv_inf, z_sup=zv_sup, armadura=arm_v,
                  d='viga de borde del hueco de la escalera en su lado hacia el eje A, bajo el muro de la caja de ese lado, de la VHA de borde al muro del eje 5', fuente='revisión 23-10-2026')]
    if ey1 < by1 - MURO - 1:   # hasta el 23-10-2026 el hueco terminaba antes del muro del eje B y llevaba viga de borde también en ese lado
        vigas.append(dict(id='VB-S', nombre=f'{NV} de borde', pts=rect(ex0, ey1, bx1 - MURO, ey1 + 25), z_inf=zv_inf, z_sup=zv_sup, armadura=arm_v,
                          d='viga de borde del hueco de la escalera en su lado hacia el eje B, de la VHA de borde al muro del eje 5', fuente='revisión 23-10-2026'))
    hueco_al_muro = ey1 >= by1 - MURO - 1   # el hueco llega a la cara del muro del eje B: ese muro hace de borde (23-10-2026)
    for v_ in vigas:
        if hueco_al_muro and v_['id'] in ('VHA-esc', 'VB-N'): v_['armadura'] = arm_v.replace('3ø12 arriba', '3ø16 arriba')   # la VHA de borde se empotra en el muro del eje B

    # ---------- fuera del búnker: sobrecimiento + cimiento corrido bajo las fachadas; CF 25/50 bajo los tabiques con pilares, hasta la cara del radier ----------
    z_sc_inf = -SOBRECIM[1]; z_ci_inf = z_sc_inf - CIMIENTO[1]; z_cemp_inf = z_ci_inf - EMPLANTILLADO   # −75, −100, −110
    hs, hc = SOBRECIM[0] / 2, CIMIENTO[0] / 2
    NSC, NCF = f'Sobrecimiento {SOBRECIM[0]:.0f} × {SOBRECIM[1]:.0f}', f'CF {CF[0]:.0f}/{CF[1]:.0f}'
    yJ = by1 + JUNTA   # los sobrecimientos y CF que nacen en el muro sur del búnker parten tras una junta de 2 (revisión 23-10-2026)
    tramos_sc = [('1', xA[0], yJ, xA[0], yA[6] - hs, 'bajo la fachada del eje 1, del búnker (junta de 2) a la fachada del eje E'),
                 ('5', xA[4], yJ, xA[4], yA[6] - hs, 'bajo la fachada del eje 5, del búnker (junta de 2) a la fachada del eje E'),
                 ('E', xA[0] - hs, yA[6], xA[4] + hs, yA[6], 'bajo la fachada del eje E')]
    sc_piezas, ci_piezas, cemp_piezas = [], [], []
    for n, x0, y0, x1, y1, d in tramos_sc:
        vert = abs(x1 - x0) < 1
        if vert:
            sc_piezas.append(pieza(f'SC-{n}', x0 - hs, y0, x0 + hs, y1, z_sc_inf, 0, NSC, d))
            ci_piezas.append(pieza(f'CC-{n}', x0 - hc, y0, x0 + hc, y1 - (hc - hs), z_ci_inf, z_sc_inf - GAP, 'Cimiento corrido 80 × 25', d))
        else:
            sc_piezas.append(pieza(f'SC-{n}', x0, y0 - hs, x1, y0 + hs, z_sc_inf, 0, NSC, d))
            ci_piezas.append(pieza(f'CC-{n}', x0 - (hc - hs), y0 - hc, x1 + (hc - hs), y0 + hc, z_ci_inf, z_sc_inf - GAP, 'Cimiento corrido 80 × 25', d))
    for p in ci_piezas: cemp_piezas.append(dict(id=p['id'].replace('CC', 'EMP'), pts=p['pts'], z_inf=Z(z_cemp_inf), z_sup=Z(z_ci_inf - GAP)))
    # hormigón pobre G5 del emplantillado al sello de −140 (0,90 bajo el NTN, como pide el informe de suelos; revisión 23-10-2026)
    hp_piezas = [dict(id=p['id'].replace('CC', 'HP'), pts=p['pts'], z_inf=Z(SELLO_EXT), z_sup=Z(z_cemp_inf - GAP), nombre='Hormigón pobre G5 bajo el cimiento corrido') for p in ci_piezas]
    cimiento = dict(sobrecimiento=dict(ancho=SOBRECIM[0], alto=SOBRECIM[1], z_sup=Z(0), z_inf=Z(z_sc_inf), piezas=sc_piezas,
                                       armadura='2ø16 arriba, estribos ø10@20 (cerrados arriba, ramas hasta el cimiento y patas hacia afuera con recubrimiento 5; la lámina 01 los da de L=211 para el sobrecimiento de 25), ø8@20 horizontales; recubrimiento 3; junta de 2 con el muro del búnker, sin barras ancladas a él'),
                    zapata=dict(ancho=CIMIENTO[0], espesor=CIMIENTO[1], z_sup=Z(z_sc_inf - GAP), z_inf=Z(z_ci_inf), piezas=ci_piezas,
                                armadura='U ø12@20 + 4ø12 longitudinales (revisión 23-10-2026: antes 4ø10; el sismo en A–E le pide 86 kN·m y con 4ø10 aguanta 80); recubrimiento 5'),
                    emplantillado=dict(espesor=EMPLANTILLADO, z_sup=Z(z_ci_inf - GAP), z_inf=Z(z_cemp_inf), hormigon='G5', piezas=cemp_piezas),
                    hormigon_pobre=dict(z_sup=Z(z_cemp_inf - GAP), z_inf=Z(SELLO_EXT), hormigon='G5', piezas=hp_piezas, nota=f'del emplantillado al sello de −{-SELLO_EXT:.0f} (0,90 bajo el NTN, como el informe de suelos)'),
                    fuente='lámina 01 rev 1, corte b-b (cadena 50 | 25 | var. mín. 10: sobrecimiento 25 x 50 hasta el NTN −50, zapata 27,5 + 25 + 27,5 = 80 x 25 de −50 a −75, emplantillado); sello a −140 con hormigón pobre, 2ø16 arriba y junta con el búnker: revisión 23-10-2026',
                    nota='bajo las fachadas fuera del búnker; el original lo lleva bajo todo su perímetro F1 y sus esquinas, con placas encima de cada pilar')
    hcf = CF[0] / 2; z_cf_sup = CF_TOPE - GAP; z_cf_inf = CF_TOPE - CF[1]; z_cfe_inf = z_cf_inf - EMPLANTILLADO   # −0,5, −50 (= NTN), −60
    cf_piezas = [pieza('CF-4', xA[3] - hcf, yJ, xA[3] + hcf, yA[6] - hs, z_cf_inf, z_cf_sup, NCF, 'bajo el tabique estudio/baño-bodega (eje 4), del búnker (junta de 2) a la fachada del eje E, hasta la cara del radier'),
                 pieza('CF-C', xA[3] + hcf, yC - hcf, xA[4] - hs, yC + hcf, z_cf_inf, z_cf_sup, NCF, 'bajo el tabique baño/cabina (eje C), del eje 4 a la fachada del eje 5, hasta la cara del radier'),
                 pieza('CF-C2', xA[3] + hcf, yC2 - hcf, xA[4] - hs, yC2 + hcf, z_cf_inf, z_cf_sup, NCF, 'bajo el tabique cabina/bodega (eje C2), del eje 4 a la fachada del eje 5, hasta la cara del radier')]
    cf = dict(ancho=CF[0], alto=CF[1], z_sup=Z(CF_TOPE), z_inf=Z(z_cf_inf), piezas=cf_piezas,
              emplantillado=dict(espesor=EMPLANTILLADO, z_sup=Z(z_cf_inf - GAP), z_inf=Z(z_cfe_inf), hormigon='G5',
                                 piezas=[dict(id=p['id'].replace('CF', 'EMP'), pts=rect(min(q[0] for q in p['pts']) - 7.5 - c['ox'], min(q[1] for q in p['pts']) - 7.5 - c['oy'], max(q[0] for q in p['pts']) + 7.5 - c['ox'], max(q[1] for q in p['pts']) + 7.5 - c['oy'])) for p in cf_piezas]),
              hormigon_pobre=dict(z_sup=Z(z_cfe_inf - GAP), z_inf=Z(SELLO_EXT), hormigon='G5', nota=f'del emplantillado al sello de −{-SELLO_EXT:.0f} (0,90 bajo el NTN)',
                                  piezas=[dict(id=p['id'].replace('CF', 'HPF'), pts=rect(min(q[0] for q in p['pts']) - 7.5 - c['ox'], min(q[1] for q in p['pts']) - 7.5 - c['oy'], max(q[0] for q in p['pts']) + 7.5 - c['ox'], max(q[1] for q in p['pts']) + 7.5 - c['oy'])) for p in cf_piezas]),
              armadura='3ø12 arriba, 2ø10 al medio, 3ø12 abajo, Est ø10@25; emplantillado de 45 x 10 y hormigón pobre hasta −140; junta de 2 con el muro del búnker',
              fuente='lámina 01 rev 1, detalle CF 25/40 y planta (bajo el eje 2.a del original); lámina 04 rev I, elevación 2.a (cadena 10 + 40: el radier de 10 va encima, el fondo del CF en el NTN −50). Aquí 25 × 50 de 0 a −50: llega hasta la cara del radier y hace de perímetro de cada paño del radier (Gabriel, 19-10-2026), con la misma armadura; por confirmar con el ingeniero',
              nota='el ingeniero lo usa bajo su eje interior 2.a; aquí va bajo los tres tabiques con pilares (ejes 4, C y C2; los de C y C2 son iguales). Con la placa en NPOG 0, el anclaje de 43 termina a −43, dentro del CF (0 a −50) con 7 de recubrimiento')
    # dados bajo los pilares 4C y 4C2 (revisión 23-10-2026): bajo el radier, unidos al CF que pasa por encima; hormigón pobre hasta el sello
    z_da_sup, z_da_inf = -RADIER_EST - GAP, -RADIER_EST - GAP - DADO[2]
    da_piezas = [pieza(f'DA-{n}', xA[3] - DADO[0] / 2, yy - DADO[1] / 2, xA[3] + DADO[0] / 2, yy + DADO[1] / 2, z_da_inf, z_da_sup,
                       f'Dado {DADO[0] / 100:.2f} × {DADO[1] / 100:.2f} × {DADO[2] / 100:.2f}'.replace('.', ','), f'bajo el pilar P-{n}: le da peso al arranque del arriostre del eje {n[1:]}; el CF pasa por encima y lo amarra')
                 for n, yy in (('4C', yC), ('4C2', yC2))]
    dados = dict(lado=DADO[0], alto=DADO[2], z_sup=Z(z_da_sup), z_inf=Z(z_da_inf), piezas=da_piezas,
                 armadura='malla inferior ø12@15 en los dos sentidos y estribos perimetrales ø10; los 4 pernos de la placa PLc y su armadura de anclaje quedan dentro',
                 hormigon_pobre=dict(z_sup=Z(z_da_inf - GAP), z_inf=Z(SELLO_EXT), piezas=[dict(id=p['id'].replace('DA', 'HPD'), pts=p['pts']) for p in da_piezas]),
                 fuente='revisión 23-10-2026: el CF pesa ~4 kN/m y el sismo levanta hasta 55 kN en 4C (0,9D + 1,4E); emparrillado sobre resortes que solo trabajan a compresión (calculo/fundaciones_lineales.py)')
    # dren perimetral ø110 al nivel del sello, a 25 cm del borde de la losa de fundación (revisión 23-10-2026)
    od = 25.0
    dren = dict(diam=11.0, z=Z(z_emp_inf + 5.5), pts=[ap(zx0 - od, zy0 - od, 0)[:2], ap(zx1 + od, zy0 - od, 0)[:2], ap(zx1 + od, zy1 + od, 0)[:2], ap(zx0 - od, zy1 + od, 0)[:2]],
                nota=IMPERMEABILIZACION['dren'])
    # radier del estudio (fuera del búnker) en tres paños, dejando las franjas del sobrecimiento y de los CF (caras coplanares parpadean)
    g = GAP
    rad_pts = [('estudio', xA[0] + hs + g, by1 + g, xA[3] - hcf - g, yA[6] - hs - g),
               ('bano', xA[3] + hcf + g, by1 + g, xA[4] - hs - g, yC - hcf - g),
               ('cabina', xA[3] + hcf + g, yC + hcf + g, xA[4] - hs - g, yC2 - hcf - g),
               ('bodega', xA[3] + hcf + g, yC2 + hcf + g, xA[4] - hs - g, yA[6] - hs - g)]
    capas = [('radier', 'Radier e=10', 0, -RADIER_EST), ('poliestireno', 'Poliestireno expandido de alta densidad e=100', -RADIER_EST - g, -RADIER_EST - POLIESTIRENO),
             ('relleno', 'Relleno granular 15 (T.máx 1 1/2", 90 % Proctor modificado) sobre sub base granular compactada', -RADIER_EST - POLIESTIRENO - g, -RADIER_EST - POLIESTIRENO - RELLENO_EST)]
    # el radier va en 4 paños entre los CF, que llegan hasta su cara (Gabriel, 19-10-2026); antes era continuo y pasaba sobre los CF
    radier_estudio = dict(capas=[dict(id=k, nombre=nm, z_sup=Z(zs), z_inf=Z(zi), piezas=[dict(id=f'{k}-{r}', pts=rect(x0, y0, x1, y1), recinto=r) for r, x0, y0, x1, y1 in rad_pts]) for k, nm, zs, zi in capas],
                          armadura='malla ACMA C139 a media altura; juntas aserradas cada 3,0 m como máximo; polietileno de 0,2 mm bajo el poliestireno; se hace después de asentado el relleno junto al búnker',
                          fuente='lámina 01 rev 1, corte b-b (radier 10 sobre poliestireno 10, relleno 15 y sub base); malla y juntas: revisión 23-10-2026')
    relleno = dict(nota='relleno de la excavación del búnker: granular importado (Tmáx 50 mm, finos ≤ 10 %, IP ≤ 6) compactado en capas de 20 cm al 95 % del Proctor modificado, o relleno fluido (CLSM) bajo las fundaciones del estudio; '
                        'no reutilizar el limo MH excavado; tapa de suelo fino con pendiente hacia afuera', fuente='revisión 23-10-2026 (el informe de suelos no lo define)')

    # ---------- placas base PLb en todos los pilares ----------
    placas = []
    cruz = set(c.get('pilares_cruz', ())); pie = set(c.get('pilares_pie', cruz))
    for mb in c['pilares']:
        x, y = mb['a'][0], mb['a'][1]
        yl = y - c['oy']
        xl = mb['a'][0] - c['ox']
        en_eje4 = abs(xl - xA[3]) < 1
        sobre = 'muro del búnker' if yl <= by1 + 1 else (f'dado + {NCF}' if en_eje4 and (abs(yl - yC) < 1 or abs(yl - yC2) < 1) else (NCF if en_eje4 and yl < yA[6] - 1 else 'sobrecimiento'))
        muro_dir0 = None
        muro_dir = 'y' if (abs(xl - xA[0]) < 1 or abs(xl - xA[4]) < 1 or (en_eje4 and yl > by1 + 1 and abs(yl - yC) > 1 and abs(yl - yC2) > 1 and yl < yA[6] - 1)) else 'x'   # sentido del muro bajo el pilar
        desf = 0.0   # eje del muro − eje del pilar, medido a través del muro (el muro de 30 creció 5 hacia afuera)
        if sobre == 'muro del búnker':
            if muro_dir == 'x': desf = ((by0 + MURO / 2) if yl < (by0 + by1) / 2 else (by1 - MURO / 2)) - yl
            else: desf = ((bx0 + MURO / 2) if xl < (bx0 + bx1) / 2 else (bx1 - MURO / 2)) - xl
        if mb['id'] in cruz:
            placas.append(dict(id='PLc-' + mb['id'][2:], tipo='PLc', desfase=r1(desf), pilar=mb['id'], perfil=mb['p'], centro=[r1(x), r1(y)], z=Z(0), lado=PLACA_C[0], espesor=PLACA_C[2], sobre=sobre, muro_dir=muro_dir,
                               anclajes=f'4 pernos ø3/4" A36 con tuerca y golilla 50 × 50 × 10 abajo (hef {ANCLAJE_C["largo"]:.0f}), bajo las paredes del tubo; armadura de anclaje: '
                                        + ('las verticales del muro (ø16@15 y ø12@15)' if sobre == 'muro del búnker' else ('4ø16 verticales a 20 de los pernos' if sobre.startswith('dado') else 'estribos extra ø10 (quedan @10 en ±25)'))
                                        + '; llave de corte bajo la placa; ' + ('cartela de la diagonal soldada a la placa' if mb['id'] in pie else 'sin cartela: la diagonal llega a la cabeza de este pilar, no a su pie')))
        else:
            placas.append(dict(id='PLb-' + mb['id'][2:], tipo='PLb', desfase=r1(desf), pilar=mb['id'], perfil=mb['p'], centro=[r1(x), r1(y)], z=Z(0), lado=PLACA[0], espesor=PLACA[2], sobre=sobre, muro_dir=muro_dir,
                               anclajes=(f'1+1 ø3/4" en horquilla, paralelas y angostas sobre la VHA del eje 3 (L=114: 7,7 bajo la placa, entre las barras de la viga, ramas de {ANCLAJE["largo"]:.0f} y ganchos de {ANCLAJE["gancho"]:.0f} hacia afuera)'
                                         if sobre == 'muro del búnker' and muro_dir == 'x' and abs(xl - x3) < 15 else
                                         f'1+1 ø3/4" en horquilla, paralelas (L=120: {ANCLAJE["sep"]:.0f} bajo la placa, ramas de {ANCLAJE["largo"]:.0f} y ganchos de {ANCLAJE["gancho"]:.0f} hacia afuera)') + f', doblez interior ≤ 1ø; Est. {ANCLAJE["estribos"]}'))
    n_c = sum(1 for p in placas if p['tipo'] == 'PLc')
    placas_info = dict(detalle=f'PLc 250 x 250 x 12 mm con 4 pernos ø3/4" con golilla, armadura de anclaje (verticales del muro, estribos extra del sobrecimiento o 4ø16 en los dados) y llave de corte en los {n_c} pilares con cruz; '
                              f'PLb 200 x 200 x 8 mm con 1+1 ø3/4" en horquilla (paralelas, doblez ≤ 1ø) en los otros {len(placas) - n_c}; placas soldadas al tubo en todo el contorno (filete igual al espesor del tubo), embebidas en el muro, sobrecimiento, CF o dado',
                       fuente='lámina 01 rev 1, detalle placa base PLb; PLc, pernos y horquillas paralelas: revisión 23-10-2026', lista=placas)

    hormigon = dict(especificaciones=ESPECIFICACIONES, impermeabilizacion=IMPERMEABILIZACION, muros=muros, losa=losa, piso=piso, relleno=relleno_b, relleno_excavacion=relleno, losa_fundacion=losa_fundacion, zapata_corrida=zapata_corrida, vigas=vigas,
                    cimiento=cimiento, cf=cf, dados=dados, dren=dren, radier_estudio=radier_estudio, placas=placas_info, escalera=c['escalera'],
                    interior=dict(ancho=r1(bx1 - bx0 - 2 * MURO), largo=r1(by1 - by0 - 2 * MURO), alto=H,
                                  terminado=dict(ancho=r1(bx1 - bx0 - 2 * MURO - 2 * c.get('T', 0)), largo=r1(by1 - by0 - 2 * MURO - 2 * c.get('T', 0)), tabique=c.get('T', 0), nota='entre los tabiques de 10 que van por dentro de los muros (Gabriel, 14-10-2026)')),
                    niveles=dict(npog_0='NPOG 0,00 = cara superior de la losa del búnker y del radier (obra gruesa); el piso terminado va más arriba (sobrelosa + adhesivo + porcelanato)', losa_inf=z_losa_inf, piso_bunker=z_piso, radier_bunker_inf=z_rad_inf, losa_fund_sup=z_zap_sup, losa_fund_inf=z_zap_inf,
                                 zapata_sup=z_zap_sup, zapata_inf=z_zap_inf, emplantillado_inf=z_emp_inf, ntn=-50, sobrecimiento_inf=z_sc_inf, cimiento_inf=z_ci_inf, cf_sup=CF_TOPE, cf_inf=z_cf_inf, sello_fachadas=SELLO_EXT,
                                 nota=f'el original tiene el búnker de 2,72 libres (−272 piso, −292 radier, −312 zapata, −342 sello); con los 2,80 de Gabriel todo bajó 8 cm; desde el 15-10-2026 la losa de fundación ocupa el lugar de la zapata y el piso es su cara superior; '
                                      f'con la revisión del 23-10-2026 (losa de techo {LOSA:.0f} y losa de fundación {LOSA_FUND:.0f}) se mantienen los 3,10 libres y el sello baja a {z_emp_inf:.0f}'))

    # ---------- enfierradura (familias de barras para el 3D; polilíneas en cm app) ----------
    fierros = []
    def P(x, y, z): return ap(x, y, z)
    L60 = lambda diam: 6.0 * diam          # traslapo / anclaje mínimo: 60 diámetros (especificaciones), en cm
    def barra_L(eje, c, off, t0, t1, z, ini, fin):
        # barra recta a lo largo de 'eje' ('x' o 'y') en la coordenada perpendicular c + off, de t0 a t1 (a lo largo), a la cota z.
        # ini / fin: None o (t_ext, leg_dx, leg_dy): la barra se alarga hasta t_ext (hasta el recubrimiento lejano del elemento
        # perpendicular) y ahí dobla 90° con una pata (leg) que corre dentro de ese elemento. Devuelve la polilínea (x, y, z).
        def pt(t): return (c + off, t, z) if eje == 'y' else (t, c + off, z)
        pts = []
        if ini: pts.append((pt(ini[0])[0] + ini[1], pt(ini[0])[1] + ini[2], z)); pts.append(pt(ini[0]))
        else: pts.append(pt(t0))
        if fin: pts.append(pt(fin[0])); pts.append((pt(fin[0])[0] + fin[1], pt(fin[0])[1] + fin[2], z))
        else: pts.append(pt(t1))
        return pts
    def fam(id_, elemento, diam, poli, n=1, paso=(0, 0, 0), d='', polis=None):
        f = dict(id=id_, elemento=elemento, diam=diam, d=d)
        if polis is not None: f['polilineas'] = [[P(*q) for q in pl] for pl in polis]; f['largo'] = r1(sum(_largo(pl) for pl in polis))
        else: f['polilinea'] = [P(*q) for q in poli]; f['n'] = n; f['paso'] = list(paso); f['largo'] = r1(_largo(poli) * n)
        fierros.append(f)

    def estribo(pts, g=10.0, s_=2.0):
        # estribo cerrado A-B-C-D-A con ganchos de 135° de g cm en la esquina A, hacia el interior (propuesta: NCh 430 / ACI 318 piden
        # gancho sísmico de 135° con extensión de 6ø y no menos de 7,5 cm; con el doblez queda ~10). Gabriel, 22-10-2026: "detalles de ingeniería"
        # las dos colas abrazan la barra de esquina: parten de los lados AB y DA a s_ de la esquina y entran en diagonal, una a cada lado de ella
        # (hasta la revisión de choques del 23-10-2026 salían de la esquina misma y atravesaban esa barra)
        A, B, D = pts[0], pts[1], pts[3]
        u = [B[i] - A[i] for i in range(3)]; v = [D[i] - A[i] for i in range(3)]
        lu, lv = math.sqrt(sum(c * c for c in u)), math.sqrt(sum(c * c for c in v))
        u = [c / lu for c in u]; v = [c / lv for c in v]
        b = [u[i] + v[i] for i in range(3)]; lb = math.sqrt(sum(c * c for c in b)); b = [c / lb for c in b]
        S1 = tuple(A[i] + s_ * u[i] for i in range(3)); S2 = tuple(A[i] + s_ * v[i] for i in range(3))
        return [tuple(S1[i] + g * b[i] for i in range(3)), S1] + [tuple(q) for q in pts[1:4]] + [S2, tuple(S2[i] + g * b[i] for i in range(3))]
    # muros del búnker: por muro, eje y normal hacia adentro
    murosL = [('N', (bx0, by0 + MURO / 2), (bx1, by0 + MURO / 2), (0, 1)), ('S', (bx0, by1 - MURO / 2), (bx1, by1 - MURO / 2), (0, -1)),
              ('O', (bx0 + MURO / 2, by0 + MURO), (bx0 + MURO / 2, by1 - MURO), (1, 0)), ('E', (bx1 - MURO / 2, by0 + MURO), (bx1 - MURO / 2, by1 - MURO), (-1, 0))]   # O/E entre los muros N y S (sus verticales se alargan a las esquinas abajo)
    zfp = z_zap_inf + 5 + 1.6 + 1.2 + 0.8   # pie de las verticales: sobre las dos capas de la malla inferior (ø16 N-S y ø12 E-O); 0,8 = radio de la ø16 exterior
    for nm, a, b, nrm in murosL:
        dx, dy = b[0] - a[0], b[1] - a[1]; ln = math.hypot(dx, dy); ux, uy = dx / ln, dy / ln
        extV = 0.0   # las esquinas las arman las verticales de los muros norte y sur (corren de cara a cara); las de poniente y oriente parten después
        nV = int((ln + 2 * extV) // 15)
        for cara, s in (('exterior', -1), ('interior', 1)):
            ext = cara == 'exterior'
            dV = 16 if ext else 12                          # verticales ø16@15 por fuera y ø12@15 por dentro (revisión 23-10-2026)
            rec_ = 4.0 if ext else 3.0                      # recubrimiento 4 por la cara contra el suelo y el agua, 3 por dentro
            dist = MURO / 2 - rec_ - dV / 20                # 7,7 por fuera, 8,9 por dentro (desde el eje del muro)
            fx, fy = nrm[0] * dist * s, nrm[1] * dist * s
            pata = 60.0 if ext else 30.0                    # por fuera, pata de 60 traslapada con la malla inferior (cierre del nudo muro–losa)
            gx, gy = nrm[0] * pata, nrm[1] * pata         # las dos patas van hacia adentro del búnker: la interior no cruza la vertical exterior
            hx, hy = nrm[0] * 20, nrm[1] * 20               # gancho superior de 20 en la losa, hacia adentro
            alt = 0.0
            x0, y0 = a[0] - ux * extV + ux * (7.5 + alt) + fx, a[1] - uy * extV + uy * (7.5 + alt) + fy
            zp_ = zfp + (0.0 if ext else 1.8) + (0.0 if nm in ('N', 'S') else 3.6)   # pies en capas: N/S abajo, O/E encima; exteriores bajo las interiores
            zg = -5.0 if nm in ('N', 'S') else -6.4   # ganchos superiores en capas, bajo las dos mallas superiores de la losa: N/S arriba, O/E debajo
            barrasV = []
            for k in range(nV):
                X_, Y_ = x0 + ux * 15 * k, y0 + uy * 15 * k
                esquina = nm in ('N', 'S') and (X_ < bx0 + MURO or X_ > bx1 - MURO)   # en la esquina el gancho chocaría con el muro perpendicular: va recta
                zg_ = -6.0 if nm in ('N', 'S') and abs(X_ - x3) < 12.5 else zg   # bajo la VHA-3 el gancho pasa bajo la rama superior de sus estribos, entre sus 3ø12
                hx_g, hy_g = hx, hy
                frente_hueco = (nm == 'E' and ey0 - 8 <= Y_ <= ey1 + 8) or (nm == 'S' and ey1 >= by1 - MURO - 1 and ex_h - 8 <= X_ <= ex1 + 8)   # con margen: la vertical puede correrse unos cm al revisar los choques
                if frente_hueco and not ext:
                    hx_g, hy_g, zg_ = -hx, -hy, zg - (2.8 if nm == 'S' else 1.4)   # frente al hueco de la escalera el gancho vuelve hacia el muro, bajo el de la vertical exterior (en el muro B, también bajo las ø16 de la VHA de borde)
                barrasV.append([(X_ + gx, Y_ + gy, zp_), (X_, Y_, zp_), (X_, Y_, zg_)] + ([] if esquina else [(X_ + hx_g, Y_ + hy_g, zg_)]))
            fam(f'MV-{nm}-{cara[:3]}', 'muro del búnker', dV, None, polis=barrasV, d=f'verticales ø{dV}@15 del muro del eje {EJE_MURO[nm]}, malla {cara}' + f': bajan dentro de la losa de fundación con pata de {pata:.0f} sobre la malla inferior y terminan con gancho de 20 en la losa de techo (L≈{(-4 - zfp + pata + 20)/100:.2f} m)'.replace('.', ','))
            dH = 12; offH = MURO / 2 - rec_ - dV / 10 - dH / 20      # horizontales ø12@15 por dentro de las verticales: 6,3 / 7,7 desde el eje
            hx_, hy_ = nrm[0] * offH * s, nrm[1] * offH * s
            nH = int((z_losa_inf - 6 - (z_zap_sup + 8)) // 15) + 1
            zh0 = z_zap_sup + 8 + (0.0 if nm in ('N', 'S') else 2.0)   # las de poniente y oriente 2 cm más arriba: en las esquinas pasan sobre las de norte y sur
            if nm in ('N', 'S'):
                polH = [(a[0] + 4.6, a[1] + hy_, zh0), (b[0] - 4.6, b[1] + hy_, zh0)]   # de recubrimiento (4) a recubrimiento en las caras exteriores de O y E
                polC = [(a[0] + 4.6, a[1] + hy_, z_losa_inf - 4), (b[0] - 4.6, b[1] + hy_, z_losa_inf - 4)]
                dHt = f'horizontales ø12@15 del muro del eje {EJE_MURO[nm]}, malla {cara} (corren de esquina a esquina)'
            else:
                # muros poniente y oriente: las barras entran al muro N y al muro S hasta su recubrimiento lejano y doblan 60ø a lo largo de ellos
                sx = 1 if nm == 'O' else -1
                # la horizontal exterior dobla por el plano de las horizontales exteriores de los muros N y S, y la interior por el de sus interiores
                tN = (by0 + MURO / 2 - offH) if ext else (by0 + MURO / 2 + offH); tS = (by1 - MURO / 2 + offH) if ext else (by1 - MURO / 2 - offH)
                polH = barra_L('y', a[0], hx_, a[1], b[1], zh0, (tN, sx * L60(12), 0), (tS, sx * L60(12), 0))
                polC = barra_L('y', a[0], hx_, a[1], b[1], z_losa_inf - 4 + 1.4, (tN, sx * L60(12), 0), (tS, sx * L60(12), 0))
                dHt = f'horizontales ø12@15 del muro del eje {EJE_MURO[nm]}, malla {cara}, con patas de {L60(12):.0f} dentro de los muros de los ejes A y B (60ø, esquinas en L)'
            fam(f'MH-{nm}-{cara[:3]}', 'muro del búnker', dH, polH, n=nH, paso=(0, 0, 15), d=dHt)
            fam(f'MC-{nm}-{cara[:3]}', 'muro del búnker', 12, polC, d=f'2ø12 de coronamiento del muro del eje {EJE_MURO[nm]} (bajo la losa)' + ('' if nm in ('N', 'S') else f', con patas de {L60(12):.0f} en las esquinas'))
    # puntos (x, y) de los anclajes de las placas que van sobre los muros del búnker: las barras de la losa de techo se corren para darles paso
    anc = []
    for pl in placas:
        if pl['sobre'] != 'muro del búnker': continue
        x_, y_ = pl['centro'][0] - c['ox'], pl['centro'][1] - c['oy']
        al = (0, 1) if pl['muro_dir'] == 'y' else (1, 0); ac = (al[1], al[0])
        offs = [(t, pl['desfase'] + o) for t in (-ANCLAJE_C['sep'] / 2, ANCLAJE_C['sep'] / 2) for o in (-3.8, 3.8)] if pl['tipo'] == 'PLc' else [(t, pl['desfase'] + o) for t in (-ANCLAJE['sep'] / 2, ANCLAJE['sep'] / 2) for o in (-4.0, 4.0)]
        anc += [(x_ + al[0] * t + ac[0] * o, y_ + al[1] * t + ac[1] * o) for t, o in offs]
    def paso(t, eje, rango, dmin=3.6):
        # corre la posición t de una barra que corre según 'eje' ('y' = barra N-S en x = t) si pasa a menos de dmin de un anclaje dentro de 'rango'
        for (ax, ay) in anc:
            a_t, a_l = (ax, ay) if eje == 'y' else (ay, ax)
            if rango[0] - 1 <= a_l <= rango[1] + 1 and abs(t - a_t) < dmin:
                t = a_t + (dmin if t >= a_t else -dmin)
        return t
    # losa de techo e=25 (revisión 23-10-2026): inferior ø10@15 en los dos sentidos; superior ø12@15 en L sobre los 4 muros y ø10@20 sobre la VHA
    zLN, zLE = z_losa_inf + 2 + 0.5, z_losa_inf + 2 + 1.0 + 0.5     # −22,5 / −21,5
    polisNS = []
    x = bx0 + MURO + 15.0   # alternadas 7,5 con las verticales de los muros N y S, que bajan por las mismas x
    while x < bx1 - MURO:
        xo_ = x; x = paso(x, 'y', (by0, by0 + MURO)); x = paso(x, 'y', (by1 - MURO, by1))
        if ex0 - 5 <= x <= ex1:   # el hueco y su viga de borde poniente: la barra se corta en las vigas de borde norte y sur
            polisNS.append([(x, by0 + MURO / 2, -6), (x, by0 + MURO / 2, zLN), (x, ey0 - 5, zLN)])          # termina dentro de la viga de borde norte
            if not hueco_al_muro: polisNS.append([(x, ey1 + 5, zLN), (x, by1 - MURO / 2, zLN), (x, by1 - MURO / 2, -6)])          # y dentro de la viga de borde del lado B
        else:
            polisNS.append([(x, by0 + MURO / 2, -6), (x, by0 + MURO / 2, zLN), (x, by1 - MURO / 2, zLN), (x, by1 - MURO / 2, -6)])
        x = xo_ + 15
    fam('LN', 'losa del búnker', 10, None, polis=polisNS, d='inferiores ø10@15 en A–B (luz de 6,45 entre ejes de muros), con ganchos en los muros; en el hueco de la escalera terminan en sus vigas de borde')
    polisEO = []
    y = by0 + MURO + 15.0   # alternadas 7,5 con las verticales de los muros O y E
    while y < by1 - MURO:
        yo_ = y; y = paso(y, 'x', (bx0, bx0 + MURO)); y = paso(y, 'x', (bx1 - MURO, bx1))
        xf = ex_h - 5 if ey0 - 25 <= y <= ey1 + 25 else bx1 - 5   # junto al hueco termina dentro de la viga de borde poniente
        xf = bx1 - MURO / 2 if xf > bx1 - 10 else xf
        polisEO.append([(bx0 + MURO / 2, y, -7.2), (bx0 + MURO / 2, y, zLE), (xf, y, zLE)] + ([(xf, y, -7.2)] if xf > bx1 - MURO else []))
        y = yo_ + 15
    fam('LE', 'losa del búnker', 10, None, polis=polisEO, d='inferiores ø10@15 en 1–5, sobre las de A–B, con ganchos en los muros; en el hueco terminan en la viga de borde del lado del eje 4')
    # superiores ø12@15 en L: la pata baja 72 (60ø) por la cara exterior del muro, por dentro de sus verticales, y la barra entra 180 en la losa desde la cara interior
    zTN, zTE = -2.0 - 0.6, -2.0 - 1.2 - 0.6    # N-S arriba, E-O debajo
    pL = L60(12); ent = MURO + 180.0; fL = 4.0 + 1.6 + 1.2 + 0.6   # la pata baja por dentro de las verticales y horizontales exteriores del muro (7,4 de la cara)
    polT, polT16 = [], []
    pL16, fL16 = L60(16), fL + 0.2
    x = bx0 + MURO + 15.0   # alternadas 7,5 con las verticales del muro (sus ganchos superiores no chocan con la pata)
    while x < bx1 - MURO:
        xo_ = x; x = paso(x, 'y', (by0, by0 + MURO)); x = paso(x, 'y', (by1 - MURO, by1))
        polT.append([(x, by0 + fL, zTN - pL), (x, by0 + fL, zTN), (x, by0 + ent, zTN)])
        if hueco_al_muro and ex_h - 120 <= x <= ex_h - 2.5:
            polT16.append([(x, by1 - fL16, zTN - 0.2 - pL16), (x, by1 - fL16, zTN - 0.2), (x, by1 - ent, zTN - 0.2)])   # donde la VHA de borde se empotra en el muro del eje B
        elif hueco_al_muro and ex_h - 2.5 < x < ex1 + 2.5:
            polT.append([(x, by1 - fL, zTN - pL), (x, by1 - fL, zTN), (x, ey1 + 4.5, zTN)])     # frente al hueco: solo la franja sobre el muro, a 4,5 de su cara
        elif not hueco_al_muro and ex0 - 5 <= x <= ex1:
            polT.append([(x, by1 - fL, zTN - pL), (x, by1 - fL, zTN), (x, ey1 + 12.5, zTN)])    # termina en la viga de borde del lado B del hueco
        else:
            polT.append([(x, by1 - fL, zTN - pL), (x, by1 - fL, zTN), (x, by1 - ent, zTN)])
        x = xo_ + 15
    fam('LT-NS', 'losa del búnker', 12, None, polis=polT, d=f'superiores ø12@15 en A–B, en L sobre los muros de los ejes A y B: pata de {pL:.0f} por la cara exterior del muro y {ent - MURO:.0f} dentro de la losa (continuidad losa–muro)')
    if polT16: fam('LT-NS16', 'losa del búnker', 16, None, polis=polT16, d=f'superiores ø16@15 en A–B sobre el muro del eje B, en los 1,20 junto a la VHA de borde de la escalera (ahí se empotra en el muro): pata de {pL16:.0f} y {ent - MURO:.0f} dentro de la losa')
    polT = []
    y = by0 + MURO + 15.0
    while y < by1 - MURO:
        yo_ = y; y = paso(y, 'x', (bx0, bx0 + MURO)); y = paso(y, 'x', (bx1 - MURO, bx1))
        polT.append([(bx0 + fL, y, zTE - pL), (bx0 + fL, y, zTE), (bx0 + ent, y, zTE)])
        if not (ey0 <= y <= ey1):   # solo se cortan frente al hueco; sobre las vigas de borde sí van
            polT.append([(bx1 - fL, y, zTE - pL), (bx1 - fL, y, zTE), (bx1 - ent, y, zTE)])
        y = yo_ + 15
    fam('LT-EO', 'losa del búnker', 12, None, polis=polT, d=f'superiores ø12@15 en 1–5, en L sobre los muros de los ejes 1 y 5: pata de {pL:.0f} por la cara exterior del muro y {ent - MURO:.0f} dentro de la losa')
    fam('LS', 'losa del búnker', 10, [(x3 - 80, by0 + MURO + 10, zTE), (x3 + 80, by0 + MURO + 10, zTE)], n=int((by1 - by0 - 2 * MURO) // 20), paso=(0, 20, 0), d='superiores ø10@20 L=160 sobre la VHA del eje 3 (80 a cada lado)')
    # suples ø10@15 arriba y abajo en 1,50 × 1,50 alrededor de cada esquina del hueco (revisión 23-10-2026: ahí se juntan las vigas de borde y el peso de los muros de la caja)
    polS, polI = [], []
    for (cx_, cy_) in ((ex_h, ey0), (ex1, ey0)) + (() if hueco_al_muro else ((ex_h, ey1), (ex1, ey1))):
        x0_, x1_ = max(cx_ - 75, bx0 + MURO), min(cx_ + 75, bx1 - MURO); y0_, y1_ = max(cy_ - 75, by0 + MURO), min(cy_ + 75, by1 - MURO)
        dentro_hueco = lambda xx, yy: ex_h < xx < ex1 and ey0 < yy < ey1
        xx = bx0 + MURO + 7.5 + 15 * math.ceil((x0_ - bx0 - MURO) / 15)   # a medio camino entre las LT-NS (arriba) y las LN (abajo)
        while xx < x1_:
            tramo = [(xx, y0_), (xx, y1_)] if not (ex_h < xx < ex1) else ([(xx, y0_), (xx, ey0 - 2.5)] if cy_ == ey0 else [(xx, ey1 + 2.5), (xx, y1_)])   # a 2,5 de las caras del hueco
            if tramo[1][1] - tramo[0][1] > 40:   # sin los retazos de la franja de 10 entre el hueco y el muro
                polS.append([(tramo[0][0], tramo[0][1], zTN), (tramo[1][0], tramo[1][1], zTN)]); polI.append([(tramo[0][0], tramo[0][1], zLN), (tramo[1][0], tramo[1][1], zLN)])
            xx += 15
        yy = by0 + MURO + 7.5 + 15 * math.ceil((y0_ - by0 - MURO) / 15)   # a medio camino entre las LT-EO y las LE
        while yy < y1_:
            tramo = [(x0_, yy), (x1_, yy)] if not (ey0 < yy < ey1) else ([(x0_, yy), (ex_h - 2.5, yy)] if cx_ == ex_h else [(ex1 + 2.5, yy), (x1_, yy)])
            if tramo[1][0] - tramo[0][0] > 40:
                polS.append([(tramo[0][0], tramo[0][1], zTE), (tramo[1][0], tramo[1][1], zTE)]); polI.append([(tramo[0][0], tramo[0][1], zLE), (tramo[1][0], tramo[1][1], zLE)])
            yy += 15
    fam('LR-sup', 'losa del búnker', 10, None, polis=polS, d='suples superiores ø10@15 en 1,50 × 1,50 alrededor de cada esquina del hueco de la escalera, intercalados con las superiores (quedan @7,5)')
    fam('LR-inf', 'losa del búnker', 10, None, polis=polI, d='suples inferiores ø10@15 en 1,50 × 1,50 alrededor de cada esquina del hueco de la escalera (quedan ø10@7,5)')
    # VHA 25/45 (eje 3) y vigas de borde del hueco de la escalera (VHA-esc al poniente, VB-N y VB-S): 3ø12 arriba, 2ø10 al medio, 3ø16 abajo, Est ø10@15
    zvs, zvm, zvi = -6.0, z_losa_inf - (VHA[1] - LOSA) / 2 + 2, z_losa_inf - (VHA[1] - LOSA) + 4.8   # −6 (bajo las mallas superiores de la losa) / −33 / −40,2
    for vid, eje, c_, t0, t1, ancho in (('VHA-3', 'y', x3, by0 + 5, by1 - 5, 25.0), ('VHA-esc', 'y', (ex0 + ex_h) / 2, ey0 - 25 + 5, (by1 - 9) if hueco_al_muro else (ey1 + 25 - 5), ex_h - ex0),
                                        ('VB-N', 'x', ey0 - 12.5, ex0 + 5, bx1 - 9, 25.0)) + (() if hueco_al_muro else (('VB-S', 'x', ey1 + 12.5, ex0 + 5, bx1 - 9, 25.0),)):
        o = ancho / 2 - 4.8
        cruza = vid in ('VB-N', 'VB-S')   # las vigas de borde E-O cruzan la VHA-esc: sus barras van una capa más adentro
        dsup = 16 if (hueco_al_muro and vid in ('VHA-esc', 'VB-N')) else 12   # 3ø16 arriba en las vigas de borde desde que la VHA de borde se empotra en el muro del eje B (23-10-2026)
        zvs_, zvi_, zvm_ = (zvs - 1.4, zvi + 1.6, zvm + 1.0) if cruza else (zvs, zvi, zvm)
        if dsup == 16: zvs_ -= 0.4 + (0.2 if cruza else 0)   # bajo las mallas superiores de la losa y, en el cruce, bajo las ø16 de la VHA de borde
        P_ = (lambda k, t, z: (c_ + k, t, z)) if eje == 'y' else (lambda k, t, z: (t, c_ + k, z))
        nv = f'VHA {VHA[0]:.0f}/{VHA[1]:.0f}'
        fam(f'{vid}-sup', nv, dsup, None, polis=[[P_(k, t0, zvs_), P_(k, t1, zvs_)] for k in (-o, 0, o)], d=f'3ø{dsup} superiores de la {vid}')
        fam(f'{vid}-med', nv, 10, None, polis=[[P_(k, t0, zvm_), P_(k, t1, zvm_)] for k in (-o, o)], d=f'2ø10 medios de la {vid}')
        fam(f'{vid}-inf', nv, 16, None, polis=[[P_(k, t0, zvi_), P_(k, t1, zvi_)] for k in (-o, 0, o)], d=f'3ø16 inferiores de la {vid}')
        oe = ancho / 2 - 3.5
        if vid == 'VHA-esc': t0, t1 = ey0 + 5, (ey1 + 2.5) if hueco_al_muro else (ey1 - 5 + 7.5)   # en los cruces con las vigas de borde mandan los estribos de esas vigas; en el muro, su fierro
        if vid == 'VHA-3': t0, t1 = by0 + MURO - 2.5, by1 - MURO   # los estribos van entre las caras de los muros; dentro del muro manda su fierro
        if vid in ('VB-N', 'VB-S'): t1 = bx1 - MURO   # los estribos llegan a la cara del muro
        t = t0 + 7.5
        zq = zvs_ + dsup / 20 + 0.5
        q = [P_(-oe, t, zq), P_(oe, t, zq), P_(oe, t, zvi_ - 1.3), P_(-oe, t, zvi_ - 1.3), P_(-oe, t, zq)]
        fam(f'{vid}-est', nv, 10, estribo(q), n=int((t1 - t0 - 7.5) // 15) + 1, paso=((0, 15, 0) if eje == 'y' else (15, 0, 0)), d=f'estribos ø10@15 de la {vid}, con ganchos de 135°')
    # losa de fundación e=35: ø16@15 N-S (luz corta) y ø12@15 E-O, abajo y arriba; la inferior con ganchos de 20 hacia arriba en los bordes; recubrimiento 5
    zi, zs = z_zap_inf + 5 + 0.8, z_zap_sup - 5 - 0.8
    def posiciones(a0, a1, evitar):
        # barras @15 entre a0 y a1; la que cae a menos de 4,2 de una vertical del muro se corre lo justo (revisión de choques, 23-10-2026)
        out, t = [], a0 + 7.5
        while t < a1 - 5:
            for e in evitar:
                if abs(t - e) < 4.2: t = e + (4.2 if t >= e else -4.2)
            out.append(t); t += 15
        return out
    vx = [bx0 + 4.8, bx0 + MURO - 3.6, bx1 - 4.8, bx1 - MURO + 3.6]; vy = [by0 + 4.8, by0 + MURO - 3.6, by1 - 4.8, by1 - MURO + 3.6]
    XS, YS = posiciones(zx0, zx1, vx), posiciones(zy0, zy1, vy)
    fam('LF-inf-NS', 'losa de fundación', 16, None, polis=[[(xx, zy0 + 5.8, zi + 15), (xx, zy0 + 5.8, zi), (xx, zy1 - 5.8, zi), (xx, zy1 - 5.8, zi + 15)] for xx in XS],
        d='malla inferior ø16@15 en A–B de la losa de fundación (luz corta), con ganchos de 15 hacia arriba en los bordes; bajo los muros se corren lo justo para no topar sus verticales')
    fam('LF-inf-EO', 'losa de fundación', 12, None, polis=[[(zx0 + 5.6, yy, zi + 1.4 + 15), (zx0 + 5.6, yy, zi + 1.4), (zx1 - 5.6, yy, zi + 1.4), (zx1 - 5.6, yy, zi + 1.4 + 15)] for yy in YS],
        d='malla inferior ø12@15 en 1–5 de la losa de fundación, sobre la de A–B, con ganchos de 15 en los bordes')
    fam('LF-sup-NS', 'losa de fundación', 16, None, polis=[[(xx, zy0 + 5.8, zs), (xx, zy1 - 5.8, zs)] for xx in XS], d='malla superior ø16@15 en A–B de la losa de fundación')
    fam('LF-sup-EO', 'losa de fundación', 12, None, polis=[[(zx0 + 5.6, yy, zs - 1.4), (zx1 - 5.6, yy, zs - 1.4)] for yy in YS], d='malla superior ø12@15 en 1–5 de la losa de fundación, bajo la de A–B')
    # sobrecimiento y cimiento corrido fuera del búnker
    yE = yA[6]                                   # eje de la fachada sur; su sobrecimiento va de yE−12,5 a yE+12,5 y su cimiento de yE−40 a yE+40
    def extremos(n, diam, k):
        # extremos de la barra de cada tramo que va a k del eje (barra_L): en las esquinas dobla en L y su pata corre sobre la barra
        # equivalente del otro tramo (exterior con exterior, interior con interior), traslapada 60ø por contacto. Revisión de choques
        # del 23-10-2026: hasta entonces todas doblaban en el recubrimiento lejano, sobre las ramas de los estribos y unas encima de otras
        Lp = L60(diam)
        if n == '1': return (None, (yE - k, Lp, 0))       # de norte a sur: parte tras la junta con el búnker y dobla al oriente en la fachada sur
        if n == '5': return (None, (yE + k, -Lp, 0))      # igual, doblando al poniente
        return ((xA[0] - k, 0, -Lp), (xA[4] + k, 0, -Lp))  # tramo E: en las dos esquinas dobla al norte
    sc_info, cf_info = {}, {}
    for n, x0, y0, x1, y1, d in tramos_sc:
        dx, dy = x1 - x0, y1 - y0; ln = math.hypot(dx, dy); ux, uy = dx / ln, dy / ln; px, py = -uy, ux
        ejeB = 'y' if abs(dx) < 1 else 'x'; cB = x0 if ejeB == 'y' else y0; tA, tB = (y0 + 3.8, y1) if ejeB == 'y' else (x0, x1)   # 1 y 5: parten con recubrimiento (3 + radio) tras la junta
        # las U arrancan 3,5 antes del inicio del tramo (recubrimiento) y llegan al final de la pieza: en las esquinas quedan U en los dos sentidos
        # tramo E: su pieza va de cara exterior a cara exterior (0..1055): las U de 3,5 a 1051,5. Tramos 1 y 5: siguen hasta la cara exterior del tramo E menos 3,5
        xU, yU = x0 + ux * 3.5, y0 + uy * 3.5
        lnU = (ln - 7.0) if n == 'E' else (ln - 27.5)   # en las esquinas solo van los del tramo E; los de 1 y 5 paran antes de sus patas (a 37,5 del eje E), si no se cruzan
        # estribo ø10@20 L=211 de la lámina 01 (corte b-b): cerrado arriba (15), ramas de 68 que bajan al cimiento y patas de 30 hacia afuera
        # (30 + 68 + 15 + 68 + 30 = 211). Hasta la V111 estaba dibujado al revés: U abierta arriba con ganchos de 15 (Gabriel, 22-10-2026: "revisa los detalles de enfierradura")
        # revisión de recubrimientos (23-10-2026): en el cimiento todo va con 5. U ø12 con su base a 5,6 del fondo y ramas hasta 5,6 bajo su cara
        # superior, 4ø12 sobre la base y las patas de los estribos sobre las 4ø12 (hasta la V115 las patas quedaban a 3,5 del fondo y a 2 del borde)
        zCb, zCt = z_ci_inf + 5.6, z_sc_inf - 5.6; zCL = zCb + 1.2; pC = 40.0 - 5.6; pP = pC - 1.4   # 4ø12 sobre la base de las U ø12
        zT, zP = -3.5, zCL + 1.2 + 1.1   # −3,5 (recubrimiento 3) / −66,3: arriba envuelve las 2ø16; las patas, sobre las longitudinales del cimiento (las del tramo E van 1 más arriba)
        rs = hs - 3.5                # ramas a 3,5 de la cara (recubrimiento 3): ±11,5 con el sobrecimiento de 30
        sc_info[n] = dict(o=(xU, yU), u=(ux, uy), p=(px, py), rs=rs, zT=zT, zP=zP, pP=pP, n=int(lnU // 20) + 1)
        fam(f'SU-{n}', 'sobrecimiento', 10, [(xU - px * pP, yU - py * pP, zP), (xU - px * rs, yU - py * rs, zP), (xU - px * rs, yU - py * rs, zT), (xU + px * rs, yU + py * rs, zT), (xU + px * rs, yU + py * rs, zP), (xU + px * pP, yU + py * pP, zP)],
            n=int(lnU // 20) + 1, paso=(ux * 20, uy * 20, 0), d=f'estribos ø10@20 L={2 * (zT - zP) + 2 * rs + 2 * (pP - rs):.0f} del sobrecimiento (eje {n}): cerrados arriba ({2 * rs:.0f}), ramas de {zT - zP:.0f} hasta el cimiento y patas de {pP - rs:.0f} hacia afuera; en las esquinas solo las del tramo E')
        zs16 = -4.8 if n != 'E' else -6.4   # en las esquinas las del tramo E pasan bajo las de 1 y 5
        fam(f'S16-{n}', 'sobrecimiento', 16, None, polis=[barra_L(ejeB, cB, k, tA, tB, zs16, *extremos(n, 16, k)) for k in (-(rs - 1.3), rs - 1.3)],   # dentro del estribo
            d=f'2ø16 superiores del sobrecimiento (eje {n}), con patas de {L60(16):.0f} (60ø) en las esquinas; parten tras la junta con el búnker (revisión 23-10-2026: antes 2ø12 anclados al muro)')
        fam(f'S8-{n}', 'sobrecimiento', 8, None, polis=[barra_L(ejeB, cB, k, tA, tB, zz - (0.8 if n == 'E' else 0.0), *extremos(n, 8, k)) for k in (-(rs - 0.9), rs - 0.9) for zz in (-15, -35)], d=f'ø8@20 horizontales del sobrecimiento (eje {n}), dos caras, con patas de {L60(8):.0f} (60ø) en las esquinas')
        # cimiento: la pieza E va de 40 antes del eje 1 a 40 después del eje 5: U desde 5,6 de sus caras; las de 1 y 5 parten a 5,6 de la junta y paran antes del cimiento E
        xC, yC_ = x0 - ux * (40.0 - hs - 5.6 if n == 'E' else 0.0), y0 + uy * 5.6
        lnC = (ln + 2 * (40.0 - hs - 5.6)) if n == 'E' else (ln + hs - 50.0)
        fam(f'CU-{n}', 'cimiento corrido', 12, [(xC - px * pC, yC_ - py * pC, zCt), (xC - px * pC, yC_ - py * pC, zCb), (xC + px * pC, yC_ + py * pC, zCb), (xC + px * pC, yC_ + py * pC, zCt)],
            n=int(lnC // 20) + 1, paso=(ux * 20, uy * 20, 0), d=f'ø12@20 L={2 * pC + 2 * (zCt - zCb):.0f} en U del cimiento corrido (eje {n}): base de {2 * pC:.0f} y ramas de {zCt - zCb:.0f} (recubrimiento 5); en las esquinas solo las del tramo E')
        fam(f'CL-{n}', 'cimiento corrido', 12, None, polis=[barra_L(ejeB, cB, k, tA + (1.8 if ejeB == 'y' else 0.0), tB, zCL + (1.2 if n == 'E' else 0.0), *extremos(n, 12, k)) for k in (-33, -13, 13, 33)], d=f'4ø12 longitudinales del cimiento corrido (eje {n}), sobre la base de las U, con patas de {L60(12):.0f} (60ø) en las esquinas; parten tras la junta con el búnker')
    # CF 25/50 (de 0 a −50): barras a 5 del borde arriba y abajo, 2ø10 al medio
    for cid, x0, y0, x1, y1 in (('CF-4', xA[3], yJ + 5, xA[3], yA[6] - hs - 2.5), ('CF-C', xA[3] + hcf + 2.5, yC, xA[4] - hs - 2.5, yC), ('CF-C2', xA[3] + hcf + 2.5, yC2, xA[4] - hs - 2.5, yC2)):
        dx, dy = x1 - x0, y1 - y0; ln = math.hypot(dx, dy); ux, uy = dx / ln, dy / ln; px, py = -uy, ux
        # revisión de choques (23-10-2026): las barras terminan con gancho de 90° (12ø) dentro del elemento que las recibe, a 9,4 de su cara
        # lejana (por dentro de sus barras), en vez de patas horizontales de 60ø que corrían unas encima de otras y sobre las ramas de los estribos.
        # ldh (ACI 318-14 25.4.3, con el factor 0,7 por recubrimiento) = 17 cm para ø12: caben 24 en el sobrecimiento y 21 en el CF-4.
        # Capas: el CF-4 pasa bajo las 2ø16 del sobrecimiento sur; los CF E-O pasan sobre el CF-4 (arriba) y por encima de sus inferiores (abajo)
        if cid == 'CF-4':   # N-S: parte tras la junta con el búnker (sin anclarse al muro, revisión 23-10-2026) y entra al sobrecimiento sur
            ejeB, cB, tI, tF, gI = 'y', xA[3], y0 + 0.6, yE + hs - 5.6, False   # y0 = junta + 5: barras a 5 + radio
            zS, zM, zI = -8.0, -25.0, -43.4
        else:               # E-O: entra al CF-4 y al sobrecimiento oriente
            ejeB, cB, tI, tF, gI = 'x', y0, xA[3] - hcf + 8.6, xA[4] + hs - 5.6, True   # y0 = yC o yC2: cada CF con su eje
            zS, zM, zI = -6.8, -24.0, -42.2
        def barra_g(k, z, g):
            pt = (lambda t, zz: (cB + k, t, zz)) if ejeB == 'y' else (lambda t, zz: (t, cB + k, zz))
            return ([pt(tI, z + g)] if (g and gI) else []) + [pt(tI, z), pt(tF, z)] + ([pt(tF, z + g)] if g else [])
        # recubrimiento 5 (lámina 02, fundaciones): estribo ø10 por fuera de las barras; ramas a ±9,5 con el CF de 30
        rc = hcf - 5.5
        if cid == 'CF-4': y0 += 0.5   # primer estribo a 5 + radio de la junta
        cf_info[cid] = dict(o=(x0, y0), u=(ux, uy), p=(px, py), rc=rc, n=int(ln // 25) + 1)
        anc_ = ' en el sobrecimiento del eje E (parten tras la junta con el búnker)' if cid == 'CF-4' else ' en el CF-4 y en el sobrecimiento del eje 5'
        fam(f'{cid}-sup', NCF, 12, None, polis=[barra_g(k, zS, -15.0) for k in (-(rc - 1.1), 0, rc - 1.1)], d=f'3ø12 superiores del {cid}, con gancho de 90° (12ø){anc_}')
        fam(f'{cid}-med', NCF, 10, None, polis=[barra_g(k, zM, 0.0) for k in (-(rc - 1.0), rc - 1.0)], d=f'2ø10 medios (de piel) del {cid}, rectos hasta 9,4 de la cara lejana del elemento que los recibe')
        fam(f'{cid}-inf', NCF, 12, None, polis=[barra_g(k, zI, 15.0) for k in (-(rc - 1.1), 0, rc - 1.1)], d=f'3ø12 inferiores del {cid}, con gancho de 90° (12ø){anc_}')
        fam(f'{cid}-est', NCF, 10, estribo([(x0 - px * rc, y0 - py * rc, zS + 1.1), (x0 + px * rc, y0 + py * rc, zS + 1.1), (x0 + px * rc, y0 + py * rc, zI - 1.1), (x0 - px * rc, y0 - py * rc, zI - 1.1), (x0 - px * rc, y0 - py * rc, zS + 1.1)]),
            n=int(ln // 25) + 1, paso=(ux * 25, uy * 25, 0), d=f'estribos ø10@25 del {cid}, con ganchos de 135° (propuesta)')
    # anclajes de las placas base: 1+1 ø3/4 de 43 + gancho 10, con estribos ø8@20
    polisA, polisP, polisU, polisX = [], [], [], []
    h, g_, L_ = ANCLAJE['sep'] / 2, ANCLAJE['gancho'], ANCLAJE['largo']
    for pl in placas:
        x, y = pl['centro'][0] - c['ox'], pl['centro'][1] - c['oy']
        along = (0, 1) if pl['muro_dir'] == 'y' else (1, 0); across = (along[1], along[0])
        q = lambda t, o, z: (x + along[0] * t + across[0] * o, y + along[1] * t + across[1] * o, z)
        df = pl.get('desfase', 0.0)   # en los muros del búnker las filas se centran en el eje del muro, no en el del pilar
        if pl['sobre'] == 'muro del búnker':
            # en las esquinas las ramas no pueden caer sobre las horizontales del muro perpendicular (a 6,2 y 25,2 de su cara exterior): el grupo se corre lo justo
            lin = [by0 + 6.2, by0 + 25.2, by1 - 25.2, by1 - 6.2] if pl['muro_dir'] == 'y' else [bx0 + 6.2, bx0 + 25.2, bx1 - 25.2, bx1 - 6.2]
            c0 = y if pl['muro_dir'] == 'y' else x
            ts = (-ANCLAJE['sep'] / 2, ANCLAJE['sep'] / 2) if pl['tipo'] == 'PLb' else (-ANCLAJE_C['sep'] / 2, ANCLAJE_C['sep'] / 2)
            for dt in (0, -2, 2, -3, 3, -4, 4):
                if all(abs(c0 + t + dt - l) >= 1.9 for t in ts for l in lin): break
            if dt:
                x, y = (x, y + dt) if pl['muro_dir'] == 'y' else (x + dt, y)
                pl['corrimiento_anclajes'] = dt   # queda en la ficha de la placa
        if pl['tipo'] == 'PLb':
            # dos horquillas en U (1+1) PARALELAS, a lo largo del elemento y a ±4 de su eje: las dos coronas tocan la placa y quedan dentro de su fierro
            # (hasta la V115 iban cruzadas a la misma cota y una no se podía soldar; revisión 23-10-2026). L = 10 + 43 + 14 + 43 + 10 = 120
            zb = -1 - L_
            hh, tc = h, 0.0
            if pl['sobre'] == 'muro del búnker' and pl['muro_dir'] == 'x' and abs(x - x3) < 15:
                hh, tc = 3.85, x3 - x   # sobre la VHA del eje 3: horquilla de 7,7 con las ramas entre sus barras (a 0 y ±7,7 del eje)
            for o in (df - 4.0, df + 4.0):
                polisA.append([q(tc - hh - g_, o, zb), q(tc - hh, o, zb), q(tc - hh, o, -1), q(tc + hh, o, -1), q(tc + hh, o, zb), q(tc + hh + g_, o, zb)])
            continue
        # PLc: 4 pernos ø3/4" (hef 45) en dos filas a lo largo del elemento, a ±3,8 de su eje y ±6 a lo largo; tuerca sobre la placa y golilla 5 × 5 abajo
        hP, LP, gl = ANCLAJE_C['sep'] / 2, ANCLAJE_C['largo'], ANCLAJE_C['golilla'] / 2
        for t in (-hP, hP):
            for o in (df - 3.8, df + 3.8):
                polisP.append([q(t, o, 4.0), q(t, o, -LP)])
                polisP.append([q(t - gl, o, -LP), q(t + gl, o, -LP)])
        # armadura de anclaje (ACI 318 17.5.2.1, dimensionada con Ω0 = 2):
        if pl['sobre'] == 'muro del búnker':
            continue   # las verticales del muro (ø16@15 y ø12@15, continuas a ambos lados del cono) hacen de armadura de anclaje
        if 'dado' in pl['sobre']:
            # 6 verticales ø16 con ganchos de 15 arriba y abajo, a 20 de los pernos, fuera del CF que pasa por el dado
            for (t, o) in ((-20, -20), (20, -20), (-20, 20), (20, 20)):   # en el dado se cruzan dos CF: en (0, ±20) y (±20, 0) chocaban con sus barras
                polisU.append([q(t + 15 * (1 if t > 0 else -1), o, z_da_sup - 5.8), q(t, o, z_da_sup - 5.8), q(t, o, z_da_inf + 8.6), q(t + 15 * (1 if t > 0 else -1), o, z_da_inf + 8.6)])
            continue
        # sobrecimiento: estribos extra (los mismos del sobrecimiento) entre los existentes en ±25 del pilar: quedan @10 bajo la placa
        nS = 'E' if abs(y - yA[6]) < 1 else ('1' if abs(x - xA[0]) < 1 else '5')
        si = sc_info[nS]; tp = (x - si['o'][0]) * si['u'][0] + (y - si['o'][1]) * si['u'][1]
        for k in range(si['n']):
            te = 20 * k + 10
            if abs(te - tp) <= 25:
                X_, Y_ = si['o'][0] + si['u'][0] * te, si['o'][1] + si['u'][1] * te; px_, py_ = si['p']; rs_ = si['rs']
                polisX.append([(X_ - px_ * si['pP'], Y_ - py_ * si['pP'], si['zP']), (X_ - px_ * rs_, Y_ - py_ * rs_, si['zP']), (X_ - px_ * rs_, Y_ - py_ * rs_, si['zT']), (X_ + px_ * rs_, Y_ + py_ * rs_, si['zT']), (X_ + px_ * rs_, Y_ + py_ * rs_, si['zP']), (X_ + px_ * si['pP'], Y_ + py_ * si['pP'], si['zP'])])
    nb = sum(1 for p in placas if p['tipo'] == 'PLb'); ncz = len(placas) - nb
    fam('AN', 'placa base PLb', 19, None, polis=polisA, d=f'anclajes 1+1 ø3/4" en horquilla PARALELAS a ±4 del eje del elemento (L=1200 mm: 140 bajo la placa, ramas de 430 y ganchos de 100), doblez interior ≤ 1ø, en los {nb} pilares sin cruz')
    fam('AP', 'placa base PLc', 19, None, polis=polisP, d=f'4 pernos ø3/4" A36 con tuerca y golilla 50 × 50 × 10 (hef 45), en dos filas a ±3,8 del eje del elemento, en los {ncz} pilares con cruz')
    fam('AU', 'placa base PLc', 16, None, polis=polisU, d='armadura de anclaje de los dados: 4 verticales ø16 en las esquinas de un cuadrado de 40, con ganchos de 15 hacia afuera (Ω0 = 2)')
    fam('AX', 'placa base PLc', 10, None, polis=polisX, d='estribos extra ø10 bajo los pilares con cruz sobre el sobrecimiento (quedan @10 en ±25): armadura de anclaje (Ω0 = 2); en los muros del búnker la dan sus verticales')
    # dados de 4C y 4C2: malla inferior ø12@15 y estribos perimetrales ø10@20
    for p in da_piezas:
        xs_ = [q[0] - c['ox'] for q in p['pts']]; ys_ = [q[1] - c['oy'] for q in p['pts']]
        X0, X1, Y0, Y1 = min(xs_) + 5.5, max(xs_) - 5.5, min(ys_) + 5.5, max(ys_) - 5.5   # estribos a 5 + radio de las caras
        zi_d = z_da_inf + 5.8; mi = 1.6   # la malla y sus ganchos por dentro de los estribos perimetrales
        tramo_e = (z_da_sup - 6) - (zi_d + 1.2 + 15 + 3.7); nE_d = int(tramo_e // 18) + 2; pE_d = round(tramo_e / (nE_d - 1), 1)   # estribos @≤18 hasta sobre los ganchos de la malla
        fam(f'{p["id"]}-inf', 'dado', 12, None, polis=[[(X0 + mi, yy, zi_d + 15), (X0 + mi, yy, zi_d), (X1 - mi, yy, zi_d), (X1 - mi, yy, zi_d + 15)] for yy in [Y0 + 2.5 + 15 * k for k in range(int((Y1 - Y0) // 15) + 1)]]
                                                 + [[(xx, Y0 + mi, zi_d + 1.2 + 15), (xx, Y0 + mi, zi_d + 1.2), (xx, Y1 - mi, zi_d + 1.2), (xx, Y1 - mi, zi_d + 1.2 + 15)] for xx in [X0 + 2.5 + 15 * k for k in range(int((X1 - X0) // 15) + 1)]],
            d=f'malla inferior ø12@15 en los dos sentidos del dado {p["id"]}, con ganchos de 15')
        fam(f'{p["id"]}-est', 'dado', 10, estribo([(X0, Y0, z_da_sup - 6), (X1, Y0, z_da_sup - 6), (X1, Y1, z_da_sup - 6), (X0, Y1, z_da_sup - 6), (X0, Y0, z_da_sup - 6)]),
            n=nE_d, paso=(0, 0, -pE_d), d=f'{nE_d} estribos perimetrales ø10@{pE_d:.1f} del dado {p["id"]}, el último sobre los ganchos de la malla inferior'.replace('.', ','))

    # ---------- estribos que topan con barras de otro elemento (esquinas y cruces): se corren hasta ±4 cm ----------
    _resolver_estribos(fierros)
    # ---------- cubicación de hormigón (m³) y de fierro (kg) ----------
    def area(pts):
        return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))) / 2
    def vol(piezas, alto): return sum(area(p['pts']) for p in piezas) * alto / 1e6
    esc = c['escalera']
    # escalera: losa inclinada de 15 más los peldaños (triángulos huella x contrahuella / 2), no el bloque macizo que dibuja el 3D
    nP = esc['tramo']['peldanos']; dz = (esc['z_arriba'] - esc['z_abajo']) / nP; dy = esc['tramo']['largo'] / nP
    v_esc = (esc['ancho'] * math.hypot(esc['tramo']['largo'], esc['z_arriba'] - esc['z_abajo']) * 15 + esc['ancho'] * dy * dz / 2 * nP) / 1e6
    muro_esc = esc.get('muro'); muro_n = esc.get('muro_norte')
    v_caja = (area(muro_esc['pts']) * (c['h_caja']) + (area(muro_n['pts']) * c['h_caja'] if muro_n else 0)) / 1e6 if muro_esc else 0
    cub_h = [
        dict(elemento=f'Muros del búnker e={MURO:.0f} (DM)', m3=round(vol(muros['piezas'], z_losa_inf - z_zap_sup), 2), hormigon='G30'),
        dict(elemento=f'Losa del búnker e={LOSA:.0f}', m3=round((area(losa['pts']) - area(losa['hueco'])) * LOSA / 1e6, 2), hormigon='G30'),
        dict(elemento=f'VHA {VHA[0]:.0f}/{VHA[1]:.0f} y vigas de borde del hueco (bajo la losa)', m3=round(sum(area(v['pts']) for v in vigas) * (VHA[1] - LOSA) / 1e6, 2), hormigon='G30'),
        dict(elemento=f'Losa de fundación del búnker e={LOSA_FUND:.0f}', m3=round(vol(losa_fundacion['piezas'], LOSA_FUND), 2), hormigon='G30'),
        dict(elemento=NSC, m3=round(vol(sc_piezas, SOBRECIM[1]), 2), hormigon='G25'),
        dict(elemento='Cimiento corrido 80 × 25', m3=round(vol(ci_piezas, CIMIENTO[1]), 2), hormigon='G25'),
        dict(elemento=NCF, m3=round(vol(cf_piezas, CF[1]), 2), hormigon='G25'),
        dict(elemento=f'Dados bajo 4C y 4C2 ({DADO[0]:.0f} × {DADO[1]:.0f} × {DADO[2]:.0f})', m3=round(vol(da_piezas, DADO[2]), 2), hormigon='G25'),
        dict(elemento='Radier del estudio e=10', m3=round(vol(radier_estudio['capas'][0]['piezas'], RADIER_EST), 2), hormigon='G25'),
        dict(elemento='Escalera de hormigón y su caja de muros', m3=round(v_esc + v_caja, 2), hormigon='G25'),
        dict(elemento='Emplantillados (losa de fundación del búnker, cimientos y CF)', m3=round(vol(losa_fundacion['piezas'], EMPLANTILLADO) + vol(cemp_piezas, EMPLANTILLADO) + vol(cf['emplantillado']['piezas'], EMPLANTILLADO), 2), hormigon='G5'),
        dict(elemento='Hormigón pobre hasta el sello de −140 (cimientos, CF y dados)', m3=round(vol(hp_piezas, z_cemp_inf - SELLO_EXT) + vol(cf['hormigon_pobre']['piezas'], z_cfe_inf - SELLO_EXT) + vol(dados['hormigon_pobre']['piezas'], z_da_inf - SELLO_EXT), 2), hormigon='G5'),
    ]
    cub_f = {}
    for f in fierros: cub_f[f['diam']] = cub_f.get(f['diam'], 0) + f['largo']
    cub_fierro = [dict(diam=d, nombre=('ø3/4"' if d == 19 else f'ø{d}'), metros=round(cub_f[d] / 100, 1), kg=round(cub_f[d] / 100 * KGM[d])) for d in sorted(cub_f)]
    cubicacion = dict(hormigon=cub_h, total_m3=round(sum(x['m3'] for x in cub_h), 2), fierro=cub_fierro, total_kg=round(sum(x['kg'] for x in cub_fierro)),
                      nota='volúmenes del modelo (sin pérdidas ni traslapos); fierro por largo de barras del modelo, sin traslapos ni ganchos adicionales')
    return hormigon, fierros, cubicacion

ESTRIBOS = lambda f: f['id'].endswith('-est') or f['id'].split('-')[0] in ('SU', 'CU', 'AX')
REPARTIDAS = ('MV-', 'LN', 'LE', 'LT-', 'LR-')   # barras repartidas @: se pueden correr unos cm, como en obra

def _expandir(f):
    if 'polilineas' in f: return [list(map(tuple, p)) for p in f['polilineas']]
    base, paso = f['polilinea'], f.get('paso', [0, 0, 0])
    return [[(q[0] + k * paso[0], q[1] + k * paso[1], q[2] + k * paso[2]) for q in base] for k in range(f.get('n', 1))]

def _dseg(p, q, r, t):
    # distancia mínima entre los segmentos pq y rt (Eberly), en Python puro
    d1 = (q[0] - p[0], q[1] - p[1], q[2] - p[2]); d2 = (t[0] - r[0], t[1] - r[1], t[2] - r[2]); w = (p[0] - r[0], p[1] - r[1], p[2] - r[2])
    dot = lambda u, v: u[0] * v[0] + u[1] * v[1] + u[2] * v[2]
    a, b, c, d, e = dot(d1, d1), dot(d1, d2), dot(d2, d2), dot(d1, w), dot(d2, w)
    den = a * c - b * b
    sN, sD = (b * e - c * d, den) if den > 1e-9 else (0.0, 1.0)
    tN, tD = (a * e - b * d, den) if den > 1e-9 else (e, c)
    if sN < 0: sN, tN, tD = 0.0, e, c
    elif sN > sD: sN, tN, tD = sD, e + b, c
    if tN < 0:
        tN = 0.0
        sN, sD = (0.0, sD) if -d < 0 else ((sD, sD) if -d > a else (-d, a))
    elif tN > tD:
        tN = tD
        sN, sD = (0.0, sD) if (-d + b) < 0 else ((sD, sD) if (-d + b) > a else (-d + b, a))
    sc = 0.0 if abs(sN) < 1e-12 else sN / sD; tc = 0.0 if abs(tN) < 1e-12 else tN / tD
    dx = [w[i] + sc * d1[i] - tc * d2[i] for i in range(3)]
    return math.sqrt(dot(dx, dx))

def _normal(pl):
    # dirección en que se corre una barra: la normal de su plano (estribos, barras con ganchos o patas) o, si es recta, la horizontal perpendicular
    segs = [tuple(pl[i + 1][j] - pl[i][j] for j in range(3)) for i in range(len(pl) - 1)]
    segs = [v for v in segs if sum(c * c for c in v) > 1e-6]
    for v1 in segs:
        for v2 in segs:
            n = (v1[1] * v2[2] - v1[2] * v2[1], v1[2] * v2[0] - v1[0] * v2[2], v1[0] * v2[1] - v1[1] * v2[0]); ln = math.sqrt(sum(c * c for c in n))
            if ln > 1e-3 * math.sqrt(sum(c * c for c in v1)) * math.sqrt(sum(c * c for c in v2)): return tuple(c / ln for c in n)
    v = segs[0]; ln = math.hypot(v[0], v[1])
    return (-v[1] / ln, v[0] / ln, 0.0) if ln > 1e-6 else (1.0, 0.0, 0.0)

def _resolver_estribos(fierros):
    """Revisión de choques (23-10-2026): cada barra repartida (verticales de los muros, mallas de la losa de techo, suples) y cada estribo que
    atraviesa una barra de otra familia se corre lo justo (hasta ±5 cm, en la normal de su plano), como se hace en obra. Primero las barras, después los estribos."""
    from collections import defaultdict
    C = 25.0
    movibles = [f for f in fierros if f['id'].startswith(REPARTIDAS)] + [f for f in fierros if ESTRIBOS(f)]
    for f in movibles:
        segs, grid = [], defaultdict(list)
        for g in fierros:
            if g is f: continue
            for pl in _expandir(g):
                for a, b in zip(pl[:-1], pl[1:]):
                    i = len(segs); segs.append((a, b, g['diam'] / 20.0))
                    for ix in range(int(min(a[0], b[0]) // C) - 1, int(max(a[0], b[0]) // C) + 2):
                        for iy in range(int(min(a[1], b[1]) // C) - 1, int(max(a[1], b[1]) // C) + 2):
                            grid[(ix, iy)].append(i)
        r = f['diam'] / 20.0
        def choca(pl):
            for a, b in zip(pl[:-1], pl[1:]):
                cand = set()
                for ix in range(int(min(a[0], b[0]) // C), int(max(a[0], b[0]) // C) + 1):
                    for iy in range(int(min(a[1], b[1]) // C), int(max(a[1], b[1]) // C) + 1):
                        cand.update(grid.get((ix, iy), ()))
                for i in cand:
                    p, q, rr = segs[i]
                    if _dseg(a, b, p, q) < r + rr - 0.05: return True
            return False
        nuevas, movio = [], False
        for pl in _expandir(f):
            if choca(pl):
                u = _normal(pl)
                for dlt in (1.5, -1.5, 2.5, -2.5, 3.5, -3.5, 5, -5):
                    pl2 = [(q[0] + u[0] * dlt, q[1] + u[1] * dlt, q[2] + u[2] * dlt) for q in pl]
                    if not choca(pl2): pl = pl2; movio = True; break
            nuevas.append(pl)
        if movio or 'polilineas' not in f:
            f.pop('polilinea', None); f.pop('n', None); f.pop('paso', None)
            f['polilineas'] = [[[round(v, 1) for v in q] for q in pl] for pl in nuevas]
            f['largo'] = round(sum(_largo(pl) for pl in nuevas), 1)

def _largo(pl):
    return sum(math.dist(pl[i], pl[i + 1]) for i in range(len(pl) - 1))
