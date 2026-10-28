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
VHA = (25.0, 50.0)          # VHA 25/50 del eje 3: 25 dentro de la losa + 25 bajo ella (ingeniero, 25/26-10-2026: "se acepta"; antes 25/45 y el detalle VHA 25/40 colgaba 20 de una losa de 20)
VIGA_BOTADA = (40.0, 25.0)  # vigas botadas VBL y VBC en los bordes del hueco de la escalera, dentro de la losa de 25, sin caída (ingeniero, 25/26-10-2026; ancho 40: propuesta,
                            # con 30 también pasa); reemplazan a las vigas de borde 25/45 colgadas (VHA-esc y VB-N)
PILAR_ESC = dict(perfil='CUAD 100x100x4', acero='A270ES', lado=10.0, area=15.36, retiro=12.5, placa=(25.0, 25.0, 1.6), grout=2.5,
                 pernos='4 ø16 A36 hef 12 (nominales: el pilar nunca tracciona)', conectores='4 ø12 L=10')   # pilar en la esquina del hueco (ingeniero, 25/26-10-2026: "perfil cuadrado de 100");
                            # espesor 4, centro a 12,5 de los dos bordes del hueco (placa de cabeza de 25 al ras del hueco), placas, grout y pernos: propuesta
# Placas base = PLACAS EMBEBIDAS CON ANCLAJES SOLDADOS (ingeniero, V121 25-10-2026: "insertos con anclajes soldados a la placa y embebidos en el hormigón ... verificar
# soldadura y revisar largos de anclaje"; "ACEPTADO"): sin pernos con hilo ni tuercas arriba. Propuesta 27-10-2026 (cálculo: calculo/anclajes_insertos.py).
PLACA = dict(borde=10.0, espesor=1.2)          # PLb: inserto 200 x 200 x 12 A36 en los pilares sin cruz (borde a 100 del eje del pilar)
ANCLAJE = dict(diam=19, ac=4.0, al=4.0, hef=45.0, hef_vha=50.0, cabeza=5.0, cab_e=1.0)   # PLb: 4 barras lisas A36 ø3/4" a 80 x 80 (≥ 4·ø, ACI 318-19 17.9.2), soldadas bajo la placa (filete 10), cabeza 50 x 50 x 10 soldada (hef 45;
                            # 50 en 3A y 3B, sobre la VHA-3: con la VHA 25/50 sus 3ø16 inferiores quedan a −45,2 y las cabezas pasan 4 bajo ellas)
PLACA_C = dict(borde=12.5, borde_diag=20.0, espesor=1.6)   # PLc: inserto de 16 A36; borde a 125 del eje del pilar y a 200 del lado de cada diagonal que llega a su pie (cartela)
ANCLAJE_C_EXTRA = {'P-4A': [-22.5, 22.5]}   # pares extra de barras (t a lo largo, cm desde el eje del pilar): 4A lleva 8 barras a ±75 y ±225 (pry-out y desprendimiento lateral con el sismo del modelo unido, 27-10-2026)
# ajustes por placa con las reacciones del modelo unido (sismo con masa de tabiques y torsión accidental + unión UM, 27-10-2026; calculo/anclajes_insertos.py):
# bordes: la placa llega más lejos del eje del pilar de ese lado (cartela más larga: pared del tubo, AISC K1); espesor de la placa (cm); hef (cm); cabeza (largo a lo largo × ancho, cm)
PLACA_C_PILAR = {'P-4A': dict(bordes={'+al': 27.5, '-al': 27.5}, espesor=3.0, hef=120.0, cabeza=(10.0, 4.5)),
                 'P-1E': dict(cabeza=(8.0, 4.5)),   # 80 a lo largo: con 100 la cabeza quedaba a 2,5 de la cara del eje E (recubrimiento 3)
                 'P-5A': dict(bordes={'-ac': 27.5}), 'P-5C': dict(bordes={'+al': 27.5}), 'P-1C2': dict(bordes={'-al': 27.5}), 'P-5C2': dict(bordes={'-al': 27.5})}
AX_EXTRA = {'P-1E': [13.5]}   # estribo extra ø10 adicional (cm a lo largo del sobrecimiento desde el pilar): 1E, armadura de anclaje con el sismo del modelo unido (27-10-2026)
HORQ_DOBLA = {('P-1E', '+ac'): dict(hacia='-al', z=19.0)}   # horquilla cuyas patas topan con la cara del sobrecimiento a menos de 30: doblan a 90° hacia ese sentido, por dentro del elemento perpendicular (esquina);
                            # a 19 bajo la cara: entre las ø8@20 horizontales del sobrecimiento (a 15 y 35) y bajo la otra horquilla
HORQ = dict(diam=16, z=9.5, dz=2.5, dz_par=4.1, ld=83.2)   # horquillas de corte ø16 A630 (ACI 318-19 17.5.2.1 b): horizontales bajo la placa, abrazan los anclajes por delante y sus patas siguen ld = 832 (25.4.2.3, ψt 1,3) hacia atrás;
                            # capas a 25 entre ejes si se cruzan y a 41 (25 libres, ACI 318-19 25.2.2) si sus patas corren paralelas
HORQUILLAS = {'P-1A': ['+al', '+al'], 'P-4A': ['+al', '+al'], 'P-5A': ['+al', '+ac', '+al', '+ac'], 'P-1E': ['+al', '+ac'], 'P-5E': ['+al', '+ac'], 'P-5C': ['+al', '+ac', '+al'], 'P-1D': ['+al'], 'P-5D': ['+al'],
              'P-1C': ['+al'], 'P-1C2': ['+al'], 'P-5C2': ['+al']}   # sentidos en que el arranque del hormigón no alcanza (calculo/anclajes_insertos.py)
ANCLAJE_C = dict(diam=22, ac=4.5, hef=45.0, hef_muro=100.0, cabeza=6.0, cab_ac=4.5, cab_e=1.2)   # PLc: 4 barras lisas A36 ø22 (7/8") bajo las paredes del tubo que cruzan el elemento (±7,5 en CUAD 150, ±5 en RECT 150x100; ±5 en las esquinas del búnker), filas a ±4,5 del eje del pilar (90 ≥ 4·ø, 17.9.2); cabeza 60 x 45 x 12; hef 100 en los muros del búnker (verticales del muro desarrolladas sobre el cono y pry-out) y 45 en el resto
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
KGM = {6: 0.222, 8: 0.395, 10: 0.617, 12: 0.888, 16: 1.578, 19: 2.235, 22: 3.04}   # kg/m por diámetro (ø19 = 3/4")
EJE_MURO = {'N': 'A', 'S': 'B', 'O': '1', 'E': '5'}   # muros del búnker por su eje: los textos no llevan orientación (Gabriel, por consejo del ingeniero, 23-10-2026)

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
                armadura='inferior: ø10@15 en los dos sentidos (ganchos en los muros); superior: ø12@15 en L sobre los 4 muros (pata de 72 por la cara exterior del muro y 180 dentro de la losa), ø10@20 L=160 sobre la VHA '
                         'y ø10@20 en 1–5 en las franjas junto a los muros de los ejes A y B (1,80 desde su cara, bajo las L); hueco de la escalera: vigas botadas 40/25 dentro de la losa en sus lados hacia el eje 4 (VBL, del muro A al muro B) '
                         'y hacia el eje A (VBC, de la VBL al muro del eje 5), con un pilar CUAD 100x100x4 en la esquina libre (el borde del eje B es el muro); suples ø10@15 arriba y abajo en 1,50 × 1,50 en sus 2 esquinas libres, '
                         'suple inferior ø10@15 en A–B de 1,00 × 2,40 junto a la VBL (intercalado: queda ø10@7,5) y ø16@15 en L sobre el muro del eje B en los 1,20 junto a la VBL; fisura máxima 0,30 mm; recubrimiento 2; G30',
                fuente='revisión 23-10-2026: la losa de 20 de la lámina 03 rev H (L001/L002, diseñada para 5,00 m) no pasaba con 6,45 m; ahora e=25 y continua con los muros. Pilar, vigas botadas, ø10@20 en 1–5 y fisura 0,30 mm: ingeniero (25/26-10-2026); medidas y suples: propuesta')
    piso = None; relleno_b = None   # sin radier ni relleno desde el 15-10-2026: el piso es la cara superior de la losa de fundación
    # losa de fundación armada e=30 bajo todo el búnker, unida a los muros y sobresaliendo 37,5 (ingeniero vía Gabriel, 15-10-2026).
    # Las cuatro franjas bajo los muros (37,5 + 25 + 37,5 = 100) se mantienen como contornos para las láminas y las elevaciones.
    zx0, zy0, zx1, zy1 = bx0 - LOSA_FUND_MARGEN, by0 - LOSA_FUND_MARGEN, bx1 + LOSA_FUND_MARGEN, by1 + LOSA_FUND_MARGEN
    emp_lf = dict(espesor=EMPLANTILLADO, z_sup=Z(z_zap_inf - GAP), z_inf=Z(z_emp_inf), hormigon='G5', piezas=[dict(id='EMP-LF', pts=rect(zx0, zy0, zx1, zy1))],
                  nota='Var. / mín. 10 bajo toda la losa de fundación: el sello va 20 cm dentro del estrato indicado en la memoria de cálculo')
    losa_fundacion = dict(espesor=LOSA_FUND, margen=LOSA_FUND_MARGEN, pts=rect(zx0, zy0, zx1, zy1), z_sup=Z(z_zap_sup), z_inf=Z(z_zap_inf),
                          piezas=[pieza('LF', zx0, zy0, zx1, zy1, z_zap_inf, z_zap_sup, 'Losa de fundación del búnker', f'e={LOSA_FUND:.0f} bajo todo el búnker, unida a los muros; sobresale {LOSA_FUND_MARGEN:.1f} de su cara exterior; su cara superior es el piso del búnker'.replace('.', ','))],
                          armadura='doble malla: ø16@15 en A–B (luz corta) y ø12@15 en 1–5, abajo (con ganchos de 15 hacia arriba en los bordes) y arriba; las verticales exteriores de los muros bajan con pata de 60 traslapada sobre la malla inferior; '
                                   'bajo el pilar de la escalera, suple inferior ø12@15 en 1–5 de 1,50 × 1,50 (intercalado: queda ø12@7,5), sin fundación aparte; recubrimiento 5; G30',
                          fuente='ingeniero (vía Gabriel, 15-10-2026): losa armada unida con la zapata de toda la fundación; e=35 y armadura de la revisión del 23-10-2026', emplantillado=emp_lf)
    zap_piezas = [pieza('ZC-N', zx0, zy0, zx1, zy0 + ZAPATA_B[0], z_zap_inf, z_zap_sup, 'Losa de fundación: franja bajo el muro del eje A', 'parte de la losa de fundación'),
                  pieza('ZC-S', zx0, zy1 - ZAPATA_B[0], zx1, zy1, z_zap_inf, z_zap_sup, 'Losa de fundación: franja bajo el muro del eje B', 'parte de la losa de fundación'),
                  pieza('ZC-O', zx0, zy0 + ZAPATA_B[0], zx0 + ZAPATA_B[0], zy1 - ZAPATA_B[0], z_zap_inf, z_zap_sup, 'Losa de fundación: franja bajo el muro del eje 1', 'parte de la losa de fundación'),
                  pieza('ZC-E', zx1 - ZAPATA_B[0], zy0 + ZAPATA_B[0], zx1, zy1 - ZAPATA_B[0], z_zap_inf, z_zap_sup, 'Losa de fundación: franja bajo el muro del eje 5', 'parte de la losa de fundación')]
    zapata_corrida = dict(ancho=ZAPATA_B[0], espesor=LOSA_FUND, z_sup=Z(z_zap_sup), z_inf=Z(z_zap_inf), piezas=zap_piezas, armadura=losa_fundacion['armadura'], emplantillado=emp_lf, fuente=losa_fundacion['fuente'],
                          nota='franjas de 100 (37,5 + 25 + 37,5) de la losa de fundación bajo cada muro, solo para contornos y cotas; el hormigón y la cubicación usan la losa completa (losa_fundacion)')
    # vigas: la VHA del eje 3 bajo la losa y las vigas botadas del hueco de la escalera dentro de ella (ingeniero, 25/26-10-2026: salen las vigas de borde 25/45 colgadas VHA-esc y VB-N)
    NV = f'VHA {VHA[0]:.0f}/{VHA[1]:.0f}'
    arm_v = f'3ø12 arriba, 2ø10 al medio, 3ø16 abajo, Est ø10@15 ({LOSA:.0f} dentro de la losa + {VHA[1] - LOSA:.0f} bajo ella)'
    zv_inf, zv_sup = Z(z_losa_inf - (VHA[1] - LOSA)), Z(z_losa_inf)
    bV = VIGA_BOTADA[0]; NVB = f'Viga botada {VIGA_BOTADA[0]:.0f}/{VIGA_BOTADA[1]:.0f}'
    xv0 = ex_h - bV; yv0 = ey0 - bV   # cara poniente de la VBL y cara de la VBC hacia el eje A
    fte_vb = 'ingeniero (25-10 y 26-10-2026): pilar en la esquina del hueco y vigas botadas dentro de la losa; ancho 40, extensión y armadura: propuesta (ACI 318-08, con torsión)'
    vigas = [dict(id='VHA-3', nombre=NV, pts=rect(x3 - 12.5, by0 + MURO, x3 + 12.5, by1 - MURO), z_inf=zv_inf, z_sup=zv_sup, armadura=arm_v,
                  d=f'viga bajo la losa en el eje 3, de muro a muro ({by1 - by0 - 2 * MURO:.0f})', fuente='lámina 03 rev H, detalle VHA 25/40; estribos @15 de la revisión del 23-10-2026; 25/50 del ingeniero (25/26-10-2026)'),
             dict(id='VBL', nombre=NVB, pts=rect(xv0, by0 + MURO, ex_h, by1 - MURO), z_inf=Z(z_losa_inf), z_sup=Z(0), botada=True,
                  armadura='4ø12 abajo y 5ø12 arriba (en L de 72 en los muros de los ejes A y B), E ø8@10 cerrados con ganchos de 135° en todo el largo; recubrimiento 3 al estribo',
                  d=f'viga botada del hueco de la escalera en su lado hacia el eje 4, dentro de la losa (sin caída), del muro del eje A al del eje B ({(by1 - by0 - 2 * MURO) / 100:.2f}); pasa sobre el pilar de la esquina y recibe el muro de la caja'.replace('.', ','), fuente=fte_vb),
             dict(id='VBC', nombre=NVB, pts=rect(ex_h, yv0, bx1 - MURO, ey0), z_inf=Z(z_losa_inf), z_sup=Z(0), botada=True,
                  armadura='4ø12 abajo y 4ø12 arriba (las de arriba en L en el muro del eje 5; con gancho pasada la VBL), E ø8@10 cerrados; donde cruza la VBL va una capa más adentro',
                  d=f'viga botada del hueco de la escalera en su lado hacia el eje A, dentro de la losa, de la VBL (sobre el pilar) al muro del eje 5 ({(bx1 - MURO - ex_h) / 100:.2f} libres); recibe el muro de la caja de ese lado'.replace('.', ','), fuente=fte_vb)]
    hueco_al_muro = ey1 >= by1 - MURO - 1   # el hueco llega a la cara del muro del eje B: ese muro hace de borde (23-10-2026)
    # pilar de acero en la esquina libre del hueco (ingeniero, 25/26-10-2026): de la losa de fundación a la cara inferior de la losa de techo, rotulado en los dos extremos
    pe = PILAR_ESC; xpe, ype = ex_h - pe['retiro'], ey0 - pe['retiro']   # (907,5; 235,5): bajo una placa de cabeza de 25 con dos bordes al ras del hueco
    lpe, tpe = pe['placa'][0], pe['placa'][2]
    z_pbase = z_piso + pe['grout']                                     # cara inferior de la placa base, sobre el grout (dentro del piso de 5,5)
    l_tubo = z_losa_inf - (z_pbase + tpe)                             # la placa de cabeza va embebida en la losa: el tubo llega a su cara inferior
    kg_pe = l_tubo / 100 * pe['area'] * 1e-4 * 7850 + 2 * (lpe / 100) ** 2 * (tpe / 100) * 7850
    pilar_escalera = dict(id='P-esc', perfil=pe['perfil'], acero=pe['acero'], lado=pe['lado'], centro=[r1(v) for v in ap(xpe, ype, 0)[:2]], centro_local=[r1(xpe), r1(ype)],
                          pts=rect(xpe - pe['lado'] / 2, ype - pe['lado'] / 2, xpe + pe['lado'] / 2, ype + pe['lado'] / 2), z_inf=Z(z_pbase + tpe), z_sup=Z(z_losa_inf),
                          largo_tubo=r1(l_tubo), largo_calculo=r1(z_losa_inf - z_piso), k=1.0, kg=r1(kg_pe),
                          placa_base=dict(pts=rect(xpe - lpe / 2, ype - lpe / 2, xpe + lpe / 2, ype + lpe / 2), z_inf=Z(z_pbase), z_sup=Z(z_pbase + tpe), lado=lpe, espesor=tpe,
                                          detalle=f'PL 250×250×16 A36 sobre grout sin retracción de {pe["grout"] * 10:.0f} mm (queda dentro del piso de 5,5), con {pe["pernos"]}'.replace('.', ',')),
                          placa_cabeza=dict(pts=rect(xpe - lpe / 2, ype - lpe / 2, xpe + lpe / 2, ype + lpe / 2), z_inf=Z(z_losa_inf), z_sup=Z(z_losa_inf + tpe), lado=lpe, espesor=tpe,
                                            detalle=f'PL 250×250×16 A36 embebida al ras de la cara inferior de la losa, con {pe["conectores"]}; dos bordes al ras del hueco'),
                          soldadura='filete de 4 mm en todo el contorno del tubo, arriba y abajo', montaje='se instala y se suelda antes de desalzaprimar la losa de techo',
                          d=f'pilar {pe["perfil"]} {pe["acero"]} en la esquina libre del hueco de la escalera, con su centro a {pe["retiro"]:.1f} de los dos bordes (caras a 7,5); recibe la VBL y la VBC; L = {(z_losa_inf - z_piso) / 100:.2f} m, K = 1'.replace('.', ','),
                          fuente='ingeniero (25-10 y 26-10-2026): pilar de 100 en la esquina del hueco; espesor, posición, placas y pernos: propuesta')

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

    # ---------- placas base (insertos PLc y PLb) en todos los pilares ----------
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
        P_along = (0, 1) if muro_dir == 'y' else (1, 0); P_across = (P_along[1], P_along[0])
        P_es_c = mb['id'] in cruz
        # tubo: medio lado a lo largo del elemento (los RECT 150x100 llevan el 150 en el sentido de 'alma')
        P_pr = mb['p']; P_t_al = 7.5 if P_pr.startswith('CUAD 150') or (P_pr.startswith('RECT 150x100') and mb.get('alma', 'Y').lower() == muro_dir) else 5.0
        # anclajes (t a lo largo, o a través, cm desde el eje del pilar): bajo las paredes del tubo que cruzan el elemento (PLc) o a 76 x 76 (PLb)
        P_hs = P_t_al if P_es_c else ANCLAJE['al']; P_tc = 0.0
        if not P_es_c and sobre == 'muro del búnker' and muro_dir == 'x' and abs(xl - x3) < 15:
            P_tc = x3 - xl   # sobre la VHA del eje 3: centradas en su eje, entre sus barras (a 0 y ±7,7)
        P_dt = 0.0
        # barras que corren a través del elemento bajo la placa y que los anclajes no pueden atravesar: en las esquinas del búnker, las horizontales del muro perpendicular
        # (a 6,2 y 25,2 de su cara exterior); donde llega un CF (4E con el CF-4, 5C y 5C2 con el CF-C y el CF-C2), sus barras a 0 y ±8,4 de su eje
        P_c0 = yl if muro_dir == 'y' else xl
        P_lin = []
        if sobre == 'muro del búnker':
            P_lin += [by0 + 6.2, by0 + 25.2, by1 - 25.2, by1 - 6.2] if muro_dir == 'y' else [bx0 + 6.2, bx0 + 25.2, bx1 - 25.2, bx1 - 6.2]
        else:
            for P_eje, P_dir in ((xA[3], 'y'), (yC, 'x'), (yC2, 'x')):   # CF-4 corre en y por x = eje 4; CF-C y CF-C2 corren en x
                if P_dir != muro_dir and abs(P_c0 - P_eje) < 20: P_lin += [P_eje - 8.4, P_eje, P_eje + 8.4]
        if sobre == 'muro del búnker' and P_es_c and any(abs(P_c0 - l_) < 12 for l_ in P_lin):
            P_hs = min(P_hs, 5.0)   # esquinas del búnker: par a ±50 (las horquillas de corte caben entre las verticales del muro perpendicular)
        if P_lin:
            # se acerca el par al eje del pilar y/o se corre lo justo, lo menos posible
            P_ops = sorted(((abs(P_h_ - P_hs) + abs(P_d_), P_h_, P_d_) for P_h_ in [P_hs - 0.5 * i for i in range(8)] for P_d_ in (0, -1, 1, -2, 2, -3, 3)))
            for _, P_h_, P_d_ in P_ops:
                if all(abs(P_c0 + P_tc + s * P_h_ + P_d_ - l) >= 1.9 for s in (-1, 1) for l in P_lin): P_hs, P_dt = P_h_, P_d_; break
        P_oc = desf if (sobre == 'muro del búnker' and not P_es_c) else 0.0   # PLb: filas centradas en el eje del muro; PLc: en el eje del pilar (2,5 hacia adentro: sin excentricidad en las barras)
        P_anclas = [[r1(P_tc + P_dt + s * P_hs), r1(P_oc + u * (ANCLAJE_C['ac'] if P_es_c else ANCLAJE['ac']))] for s in (-1, 1) for u in (-1, 1)]
        P_aj = PLACA_C_PILAR.get(mb['id'], {}) if P_es_c else {}
        if P_es_c and mb['id'] in ANCLAJE_C_EXTRA:
            P_anclas += [[r1(P_tc + P_dt + t_x), r1(P_oc + u * ANCLAJE_C['ac'])] for t_x in ANCLAJE_C_EXTRA[mb['id']] for u in (-1, 1)]
        P_hef = P_aj.get('hef', (ANCLAJE_C['hef_muro'] if sobre == 'muro del búnker' else ANCLAJE_C['hef']) if P_es_c else (ANCLAJE['hef_vha'] if P_tc else ANCLAJE['hef']))
        P_cab = list(P_aj.get('cabeza', (ANCLAJE_C['cabeza'], ANCLAJE_C['cab_ac']) if P_es_c else (ANCLAJE['cabeza'], ANCLAJE['cabeza'])))
        # placa: bordes a 'borde' del eje del pilar y a 'borde_diag' del lado de cada diagonal que llega al pie (cartela)
        P_dirs = c.get('diag_pie', {}).get(mb['id'], [])
        P_b_ = PLACA_C['borde'] if P_es_c else PLACA['borde']
        P_ext = {k: P_b_ for k in ('+al', '-al', '+ac', '-ac')}
        for (P_ux, P_uy) in P_dirs:
            P_pa, P_pc = P_ux * P_along[0] + P_uy * P_along[1], P_ux * P_across[0] + P_uy * P_across[1]
            P_k = ('+al' if P_pa > 0 else '-al') if abs(P_pa) > abs(P_pc) else ('+ac' if P_pc > 0 else '-ac')
            P_ext[P_k] = PLACA_C['borde_diag']
        for k_, v_ in P_aj.get('bordes', {}).items(): P_ext[k_] = max(P_ext[k_], v_)
        P_lar, P_anc_ = P_ext['+al'] + P_ext['-al'], P_ext['+ac'] + P_ext['-ac']
        P_q_ = lambda t, o: [r1(x + P_along[0] * t + P_across[0] * o), r1(y + P_along[1] * t + P_across[1] * o)]
        P_loc = [(-P_ext['-al'], -P_ext['-ac']), (P_ext['+al'], -P_ext['-ac']), (P_ext['+al'], P_ext['+ac']), (-P_ext['-al'], P_ext['+ac'])]
        P_recorte = None
        if sobre != 'muro del búnker':
            # esquina de sobrecimientos con diagonales en los dos sentidos (1E y 5E): la esquina interior de la placa caería fuera del hormigón (5 × 5): se recorta
            P_st = [1 if k_ == '+al' else -1 for k_ in P_ext if 'al' in k_ and P_ext[k_] > P_b_]; P_so = [1 if k_ == '+ac' else -1 for k_ in P_ext if 'ac' in k_ and P_ext[k_] > P_b_]
            if P_st and P_so:
                P_i = [i_ for i_, (t_, o_) in enumerate(P_loc) if t_ * P_st[0] > 0 and o_ * P_so[0] > 0][0]
                t_, o_ = P_loc[P_i]; h_ = SOBRECIM[0] / 2
                P_nue = [(t_, P_so[0] * h_), (P_st[0] * h_, P_so[0] * h_), (P_st[0] * h_, o_)]
                P_prev = P_loc[P_i - 1]
                if abs(P_prev[0] - t_) > 1e-6: P_nue = P_nue[::-1]   # el lado anterior corre a lo largo de t: se llega por (h, o)
                P_loc = P_loc[:P_i] + P_nue + P_loc[P_i + 1:]
                P_recorte = round((P_ext['+al'] if P_st[0] > 0 else P_ext['-al']) - h_, 1)
        P_pts = [P_q_(t_, o_) for t_, o_ in P_loc]
        P_esp = P_aj.get('espesor', PLACA_C['espesor'] if P_es_c else PLACA['espesor'])
        P_base = dict(desfase=r1(desf), pilar=mb['id'], perfil=mb['p'], centro=[r1(x), r1(y)], z=Z(0), lado=max(P_lar, P_anc_), largo=P_lar, ancho=P_anc_, pts=P_pts, espesor=P_esp, sobre=sobre, muro_dir=muro_dir,
                    anclas=P_anclas, hef=P_hef, cabeza=P_cab, bordes=dict(P_ext), diag_pie=[[round(u, 3) for u in P_d_] for P_d_ in P_dirs], horquillas=HORQUILLAS.get(mb['id'], []) if P_es_c else [])
        if P_dt: P_base['corrimiento_anclajes'] = P_dt
        if P_recorte: P_base['recorte_esquina'] = P_recorte   # cm, esquina interior recortada (cuadrado de este lado)
        if P_es_c:
            placas.append(dict(id='PLc-' + mb['id'][2:], tipo='PLc', **P_base,
                               anclajes=f'inserto: placa de {P_esp * 10:.0f}; {len(P_anclas)} barras lisas A36 ø22 (7/8") soldadas bajo la placa (filete 12 E7018 en todo el contorno) con cabeza {P_cab[0] * 10:.0f} × {P_cab[1] * 10:.0f} × 12 soldada (hef {P_hef * 10:.0f} mm), a {2 * P_hs * 10:.0f} × 90 mm bajo las paredes del tubo'
                                        + (f' y un par más a ±{max(abs(t_x) for t_x in ANCLAJE_C_EXTRA[mb["id"]]) * 10:.0f}' if mb['id'] in ANCLAJE_C_EXTRA else '') + '; '
                                        + 'armadura de anclaje: ' + (f'las verticales del muro, desarrolladas sobre el cono (hef {P_hef * 10:.0f})' if sobre == 'muro del búnker' else ('no la necesita (el dado da el cono); quedan las 4ø16 verticales' if sobre.startswith('dado') else ('estribos extra ø10 (quedan @10 en ±25, y uno más a ' + ', '.join(f'{v_:.1f}'.replace('.', ',') for v_ in AX_EXTRA[mb['id']]) + ' del pilar)' if mb['id'] in AX_EXTRA else 'estribos extra ø10 (quedan @10 en ±25)')))
                                        + (f'; horquillas de corte ø16 hacia {", ".join(HORQUILLAS[mb["id"]])}' if mb['id'] in HORQUILLAS else '')
                                        + '; ' + (f'cartela de la diagonal soldada a la placa y a la cara del tubo (placa de {P_lar * 10:.0f} × {P_anc_ * 10:.0f})' if P_dirs else f'sin cartela (placa de {P_lar * 10:.0f} × {P_anc_ * 10:.0f}): la diagonal llega a la cabeza de este pilar')))
        else:
            placas.append(dict(id='PLb-' + mb['id'][2:], tipo='PLb', **P_base,
                               anclajes=f'inserto: 4 barras lisas A36 ø3/4" a 80 × 80 soldadas bajo la placa (filete 10 E7018) con cabeza 50 × 50 × 10 soldada (hef {P_hef * 10:.0f} mm)'
                                        + (' centradas en la VHA del eje 3, entre sus barras' if P_tc else '')))
    n_c = sum(1 for p in placas if p['tipo'] == 'PLc')
    placas_info = dict(detalle=f'Placas embebidas con anclajes soldados (insertos), a ras con la cara del hormigón: PLc A36 e=16 (250 a 400 × 250 a 325 según las diagonales que llegan a su pie) con 4 barras lisas A36 ø22 (7/8") '
                              f'bajo las paredes del tubo, a 90 a través (cabeza 60 × 45 × 12, filete 12), hef 1000 en los muros del búnker y 450 en el resto, y horquillas de corte ø16 donde el hormigón no alcanza, en los {n_c} pilares con cruz '
                              f'(PLc-4A: 550 × 250 × 30 con 8 barras a ±75 y ±225, cabeza 100 × 45 × 12 y hef 1200; PLc-1E: cabeza 80 × 45 × 12); PLb A36 200 × 200 × 12 con 4 barras ø3/4" a 80 × 80 (cabeza 50 × 50 × 10, filete 10, hef 450; 500 en 3A y 3B, bajo las 3ø16 de la VHA 25/50) en los otros {len(placas) - n_c}. '
                              'Barras soldadas a la placa y a su cabeza con filete en todo el contorno (E7018, sin precalentar sobre 0 °C hasta 20 mm; 10 °C en la placa de 30 de PLc-4A, AWS D1.1); pilar soldado a la placa con filete igual al espesor del tubo en todo el contorno; sin tuercas ni llave de corte',
                       fuente='lámina 01 rev 1, detalle placa base PLb; insertos con anclajes soldados: ingeniero (V121, 25-10-2026: sugerido y aceptado); dimensiones: propuesta 27-10-2026 (calculo/anclajes_insertos.py)', lista=placas)

    hormigon = dict(especificaciones=ESPECIFICACIONES, impermeabilizacion=IMPERMEABILIZACION, muros=muros, losa=losa, piso=piso, relleno=relleno_b, relleno_excavacion=relleno, losa_fundacion=losa_fundacion, zapata_corrida=zapata_corrida, vigas=vigas,
                    pilar_escalera=pilar_escalera, cimiento=cimiento, cf=cf, dados=dados, dren=dren, radier_estudio=radier_estudio, placas=placas_info, escalera=c['escalera'],
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
    # vigas botadas del hueco (dentro de la losa de 25): arriba van bajo las dos capas superiores de la losa (ø12 N-S a −2,6 y E-O a −3,8) y bajo las ø10@20 en 1–5
    # que junto al muro B pasan bajo las ø16 en L (−4,1); abajo, sobre la capa E-O inferior (−21,5) que cruza la VBL. La VBC va una capa más adentro (cruza la VBL)
    zAB_B = -2.0 - 1.2 - 0.6 - 0.3                 # −4,1: ø10@20 en 1–5 junto al muro B (bajo las ø16 en L de −2,8)
    zBLs = zAB_B - 0.5 - 0.6                       # −5,2: 5ø12 superiores de la VBL (d = 19,8)
    zBLi = z_losa_inf + 2 + 1.0 + 0.5 + 0.5 + 0.6  # −20,4: 4ø12 inferiores de la VBL, sobre las LE (−21,5) (d = 20,4)
    zBCs, zBCi = zBLs - 1.2, zBLi + 1.2            # −6,4 / −19,2: VBC (d = 18,6 / 19,2)
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
                if nm in ('N', 'S') and not ext and xv0 <= X_ <= ex_h: zg_ = zBLs - 0.2   # bajo la VBL, igual: bajo la rama superior de sus estribos, entre sus 5ø12
                hx_g, hy_g = hx, hy
                frente_hueco = (nm == 'E' and ey0 - 8 <= Y_ <= ey1 + 8) or (nm == 'S' and ey1 >= by1 - MURO - 1 and ex_h - 8 <= X_ <= ex1 + 8)   # con margen: la vertical puede correrse unos cm al revisar los choques
                if frente_hueco and not ext:
                    hx_g, hy_g, zg_ = -hx, -hy, zg - (2.8 if nm == 'S' else 1.4)   # frente al hueco de la escalera el gancho vuelve hacia el muro, bajo el de la vertical exterior (en el muro B, también bajo las ø16 en L junto a la VBL)
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
        anc += [(x_ + al[0] * t + ac[0] * o, y_ + al[1] * t + ac[1] * o) for t, o in pl['anclas']]
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
        if xv0 - 0.5 <= x <= ex_h + 0.5: pass   # en el ancho de la VBL las reemplazan sus 4ø12 inferiores
        elif ex_h < x <= ex1:   # frente al hueco: terminan dentro de la VBC, a 3 de su cara
            polisNS.append([(x, by0 + MURO / 2, -6), (x, by0 + MURO / 2, zLN), (x, ey0 - 3, zLN)])
        else:
            polisNS.append([(x, by0 + MURO / 2, -6), (x, by0 + MURO / 2, zLN), (x, by1 - MURO / 2, zLN), (x, by1 - MURO / 2, -6)])
        x = xo_ + 15
    fam('LN', 'losa del búnker', 10, None, polis=polisNS, d='inferiores ø10@15 en A–B (luz de 6,45 entre ejes de muros), con ganchos en los muros; frente al hueco de la escalera terminan en la VBC y en el ancho de la VBL las reemplaza la viga')
    polisEO = []
    y = by0 + MURO + 15.0   # alternadas 7,5 con las verticales de los muros O y E
    while y < by1 - MURO:
        yo_ = y; y = paso(y, 'x', (bx0, bx0 + MURO)); y = paso(y, 'x', (bx1 - MURO, bx1))
        xf = ex_h - 3 if yv0 <= y <= ey1 + 25 else bx1 - 5   # frente al hueco y en el ancho de la VBC terminan dentro de la VBL, a 3 de su cara oriente
        xf = bx1 - MURO / 2 if xf > bx1 - 10 else xf
        polisEO.append([(bx0 + MURO / 2, y, -7.2), (bx0 + MURO / 2, y, zLE), (xf, y, zLE)] + ([(xf, y, -7.2)] if xf > bx1 - MURO else []))
        y = yo_ + 15
    fam('LE', 'losa del búnker', 10, None, polis=polisEO, d='inferiores ø10@15 en 1–5, sobre las de A–B, con ganchos en los muros; frente al hueco y en el ancho de la VBC terminan en la VBL')
    # superiores ø12@15 en L: la pata baja 72 (60ø) por la cara exterior del muro, por dentro de sus verticales, y la barra entra 180 en la losa desde la cara interior
    zTN, zTE = -2.0 - 0.6, -2.0 - 1.2 - 0.6    # N-S arriba, E-O debajo
    pL = L60(12); ent = MURO + 180.0; fL = 4.0 + 1.6 + 1.2 + 0.6   # la pata baja por dentro de las verticales y horizontales exteriores del muro (7,4 de la cara)
    polT, polT16 = [], []
    pL16, fL16 = L60(16), fL + 0.2
    # placas sobre los muros A y B más gruesas que el recubrimiento superior (PLc-4A, de 30): las LT-NS que pasan bajo ellas bajan 4 mm bajo la placa
    # y suben a su cota pasado el borde interior con pendiente 1:6 (ACI 25.3, barras con quiebre)
    gruesas = []
    for pl in placas:
        if pl['sobre'] != 'muro del búnker' or pl['muro_dir'] != 'x' or zTN + 0.6 <= -pl['espesor'] - 0.4: continue
        xs_ = [q[0] - c['ox'] for q in pl['pts']]; ys_ = [q[1] - c['oy'] for q in pl['pts']]
        gruesas.append((min(xs_) - 1.0, max(xs_) + 1.0, min(ys_), max(ys_), -pl['espesor'] - 0.4 - 0.6))
    def bajo_placa(x, y_pata, y_fin):
        for (xa, xb, ya, yb, zb) in gruesas:
            if xa <= x <= xb and min(y_pata, y_fin) < yb and max(y_pata, y_fin) > ya:
                s_ = 1 if y_fin > y_pata else -1; y_b = (yb + 1.0) if s_ > 0 else (ya - 1.0)
                return [(x, y_pata, zb - pL), (x, y_pata, zb), (x, y_b, zb), (x, y_b + s_ * 6 * (zTN - zb), zTN), (x, y_fin, zTN)]
        return [(x, y_pata, zTN - pL), (x, y_pata, zTN), (x, y_fin, zTN)]
    x = bx0 + MURO + 15.0   # alternadas 7,5 con las verticales del muro (sus ganchos superiores no chocan con la pata)
    while x < bx1 - MURO:
        xo_ = x; x = paso(x, 'y', (by0, by0 + MURO)); x = paso(x, 'y', (by1 - MURO, by1))
        polT.append(bajo_placa(x, by0 + fL, by0 + ent))
        if hueco_al_muro and ex_h - 120 <= x <= ex_h - 2.5:
            polT16.append([(x, by1 - fL16, zTN - 0.2 - pL16), (x, by1 - fL16, zTN - 0.2), (x, by1 - ent, zTN - 0.2)])   # junto a la VBL, que se empotra en el muro del eje B
        elif hueco_al_muro and ex_h - 2.5 < x < ex1 + 2.5:
            polT.append([(x, by1 - fL, zTN - pL), (x, by1 - fL, zTN), (x, ey1 + 4.5, zTN)])     # frente al hueco: solo la franja sobre el muro, a 4,5 de su cara
        elif not hueco_al_muro and ex0 - 5 <= x <= ex1:
            polT.append([(x, by1 - fL, zTN - pL), (x, by1 - fL, zTN), (x, ey1 + 12.5, zTN)])    # termina en la viga de borde del lado B del hueco
        else:
            polT.append([(x, by1 - fL, zTN - pL), (x, by1 - fL, zTN), (x, by1 - ent, zTN)])
        x = xo_ + 15
    fam('LT-NS', 'losa del búnker', 12, None, polis=polT, d=f'superiores ø12@15 en A–B, en L sobre los muros de los ejes A y B: pata de {pL:.0f} por la cara exterior del muro y {ent - MURO:.0f} dentro de la losa (continuidad losa–muro); bajo la placa de 30 de PLc-4A bajan 1,4 cm y suben con quiebre 1:6 pasado su borde')
    if polT16: fam('LT-NS16', 'losa del búnker', 16, None, polis=polT16, d=f'superiores ø16@15 en A–B sobre el muro del eje B, en los 1,20 junto a la VBL de la escalera (ahí se empotra en el muro): pata de {pL16:.0f} y {ent - MURO:.0f} dentro de la losa')
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
    # VHA 25/50 del eje 3: 3ø12 arriba, 2ø10 al medio, 3ø16 abajo, Est ø10@15 (las vigas de borde 25/45 del hueco salieron el 26-10-2026: ahora van vigas botadas)
    zvs, zvm, zvi = -6.0, z_losa_inf - (VHA[1] - LOSA) / 2 + 2, z_losa_inf - (VHA[1] - LOSA) + 4.8   # −6 (bajo las mallas superiores de la losa) / −35,5 / −45,2
    o, oe = 25.0 / 2 - 4.8, 25.0 / 2 - 3.5
    P_ = lambda k, t, z: (x3 + k, t, z)
    t0, t1 = by0 + 5, by1 - 5
    fam('VHA-3-sup', NV, 12, None, polis=[[P_(k, t0, zvs), P_(k, t1, zvs)] for k in (-o, 0, o)], d='3ø12 superiores de la VHA-3')
    fam('VHA-3-med', NV, 10, None, polis=[[P_(k, t0, zvm), P_(k, t1, zvm)] for k in (-o, o)], d='2ø10 medios de la VHA-3')
    fam('VHA-3-inf', NV, 16, None, polis=[[P_(k, t0, zvi), P_(k, t1, zvi)] for k in (-o, 0, o)], d='3ø16 inferiores de la VHA-3')
    t0, t1 = by0 + MURO - 2.5, by1 - MURO   # los estribos van entre las caras de los muros; dentro del muro manda su fierro
    t = t0 + 7.5; zq = zvs + 12 / 20 + 0.5
    q = [P_(-oe, t, zq), P_(oe, t, zq), P_(oe, t, zvi - 1.3), P_(-oe, t, zvi - 1.3), P_(-oe, t, zq)]
    fam('VHA-3-est', NV, 10, estribo(q), n=int((t1 - t0 - 7.5) // 15) + 1, paso=(0, 15, 0), d='estribos ø10@15 de la VHA-3, con ganchos de 135°')
    # superiores ø10@20 en 1–5 en las franjas junto a los muros de los ejes A y B (ingeniero, 25-10-2026), 1,80 desde su cara como las L: de donde terminan las L del
    # muro del eje 1 hasta la VBL (a 3 de su cara oriente). En la franja A van a la cota de las LT-EO; en la B, 0,3 más abajo, porque pasan bajo las ø16 en L junto a la VBL;
    # ahí la primera va a 22,5 de la cara del muro (más cerca pasan los ganchos de 20 de sus verticales interiores). Quedan a 2,5 o más de las otras barras de su capa
    ocup = [(pl[0][1], min(q_[0] for q_ in pl), max(q_[0] for q_ in pl)) for pl in polT + polS if abs(pl[0][1] - pl[-1][1]) < 0.1 and abs(pl[-1][2] - zTE) < 0.1]
    ocup += [(by0 + MURO + 10 + 20 * k, x3 - 80, x3 + 80) for k in range(int((by1 - by0 - 2 * MURO) // 20))]   # LS sobre la VHA
    xAB0, xAB1 = bx0 + ent - 5, ex_h - 3
    polAB = []
    # en la franja A la primera parte pasado el quiebre de las LT-NS que bajan bajo la placa de 30 de la PLc-4A (si no, se cruzan en la rampa)
    ysA = max([by0 + MURO + 2.5] + [yb + 1.0 + 6 * (zTN - zb) + 1.6 for (xa, xb, ya, yb, zb) in gruesas if yb < by0 + ent])
    for ys0, ys1, paso_, zAB in ((ysA, by0 + ent, 20.0, zTE), (by1 - MURO - 22.5, by1 - ent, -20.0, zAB_B)):
        yy = ys0
        while (yy <= ys1) if paso_ > 0 else (yy >= ys1):
            for dy_ in ((0.0, 2.5, 5.0, 7.5, 10.0) if paso_ > 0 and ysA > by0 + MURO + 2.5 else (0.0, 2.5, -2.5, 5.0, -5.0)):   # pasado el quiebre, solo hacia adentro
                if all(abs(yy + dy_ - yo) >= 2.5 for yo, xo0, xo1 in ocup if xo1 > xAB0 and xo0 < xAB1): break
            polAB.append([(xAB0, yy + dy_, zAB), (xAB1, yy + dy_, zAB)])
            yy += paso_
    fam('LS-AB', 'losa del búnker', 10, None, polis=polAB, d=f'superiores ø10@20 en 1–5 en las franjas junto a los muros de los ejes A y B (1,80 desde su cara, como las L), de las L del muro del eje 1 a la VBL; junto al muro B pasan bajo las ø16 en L (ingeniero, 25-10-2026)')
    # suple inferior ø10@15 en A–B junto a la VBL (la losa vecina daba 1,04): 1,00 al poniente de la viga, de 2,80 a 5,20 desde el eje A, intercalado con las LN (queda ø10@7,5);
    # los que caen sobre los suples de la esquina del hueco se corren 2,5
    yR0, yR1 = by0 + MURO / 2 + 280.0, by0 + MURO / 2 + 520.0
    nsI = [(pl[0][0], min(q_[1] for q_ in pl), max(q_[1] for q_ in pl)) for pl in polI if abs(pl[0][0] - pl[-1][0]) < 0.1]   # suples inferiores N-S de las esquinas
    xsR = [pl[0][0] + 7.5 for pl in polisNS if ex_h - 140 - 7.5 <= pl[0][0] <= xv0 - 8.0]
    xsR = [xr - (2.5 if any(abs(xr - xi) < 2 and yi1 > yR0 and yi0 < yR1 for xi, yi0, yi1 in nsI) else 0.0) for xr in xsR]
    fam('LR-VBL', 'losa del búnker', 10, None, polis=[[(xr, yR0, zLN), (xr, yR1, zLN)] for xr in xsR], d='suple inferior ø10@15 en A–B de 1,00 × 2,40 junto a la VBL, intercalado con las inferiores (queda ø10@7,5)')
    # vigas botadas del hueco de la escalera, 40/25 dentro de la losa (ingeniero, 25/26-10-2026; armadura: propuesta, ACI 318-08 con torsión): recubrimiento 3 al estribo ø8.
    # VBL: 4ø12 abajo y 5ø12 arriba en L de 72 en los muros A y B (las patas, una capa por dentro de las de la losa), E ø8@10 de cara a cara de los muros.
    # VBC: 4ø12 abajo y 4ø12 arriba, una capa más adentro que la VBL; parten con gancho pasada la VBL y las de arriba bajan en L de 72 en el muro del eje 5; E ø8@10
    NVBf = 'viga botada'; rE = 3.0 + 0.4; bI = bV - 2 * rE - 2.0       # eje de las ramas del estribo; ancho entre ejes de las barras de esquina (31,2)
    pLv = L60(12); fLv = fL + 1.2; yLa, yLb = by0 + fLv, by1 - (fL16 + 0.8 + 0.6)   # patas de las L: por dentro de las ø12 (muro A) y de las ø16 (muro B) de la losa
    xsV = lambda n: [xv0 + rE + 1.0 + k * bI / (n - 1) for k in range(n)]
    ysV = lambda n: [yv0 + rE + 1.0 + k * bI / (n - 1) for k in range(n)]
    fam('VBL-sup', NVBf, 12, None, polis=[[(x_, yLa, zBLs - pLv), (x_, yLa, zBLs), (x_, yLb, zBLs), (x_, yLb, zBLs - pLv)] for x_ in xsV(5)],
        d=f'5ø12 superiores de la VBL, en L de {pLv:.0f} (60ø) en los muros de los ejes A y B')
    fam('VBL-inf', NVBf, 12, None, polis=[[(x_, yLa + 1.2, zBLi), (x_, yLb - 1.2, zBLi)] for x_ in xsV(4)], d='4ø12 inferiores de la VBL, de muro a muro')
    t0, t1 = by0 + MURO + 5, by1 - MURO - 5
    q = [(xv0 + rE, t0, zBLs + 1.0), (ex_h - rE, t0, zBLs + 1.0), (ex_h - rE, t0, zBLi - 1.0), (xv0 + rE, t0, zBLi - 1.0), (xv0 + rE, t0, zBLs + 1.0)]
    fam('VBL-est', NVBf, 8, estribo(q), n=int((t1 - t0) // 10) + 1, paso=(0, 10, 0), d='estribos cerrados E ø8@10 de la VBL en todo su largo, con ganchos de 135°')
    xBC1 = bx1 - fLv   # patas de las L de la VBC en el muro del eje 5, por dentro de las de la losa
    fam('VBC-sup', NVBf, 12, None, polis=[[(xv0 + rE + 1.0, y_, zBCi + 1.2), (xv0 + rE + 1.0, y_, zBCs), (xBC1, y_, zBCs), (xBC1, y_, zBCs - pLv)] for y_ in ysV(4)],
        d=f'4ø12 superiores de la VBC: gancho dentro de la VBL, pasada su cara poniente, y L de {pLv:.0f} (60ø) en el muro del eje 5')
    fam('VBC-inf', NVBf, 12, None, polis=[[(xv0 + rE + 2.6, y_, zBCs - 1.2), (xv0 + rE + 2.6, y_, zBCi), (xBC1 - 1.2, y_, zBCi)] for y_ in ysV(4)],
        d='4ø12 inferiores de la VBC: gancho dentro de la VBL, pasada su cara poniente, y rectas hasta el muro del eje 5')
    t0, t1 = ex_h + 5, bx1 - MURO - 5
    q = [(t0, yv0 + rE, zBCs + 1.0), (t0, ey0 - rE, zBCs + 1.0), (t0, ey0 - rE, zBCi - 1.0), (t0, yv0 + rE, zBCi - 1.0), (t0, yv0 + rE, zBCs + 1.0)]
    fam('VBC-est', NVBf, 8, estribo(q), n=int((t1 - t0) // 10) + 1, paso=(10, 0, 0), d='estribos cerrados E ø8@10 de la VBC, de la VBL al muro del eje 5, con ganchos de 135°')
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
    # suple inferior ø12@15 en 1–5 bajo el pilar de la escalera, de 1,50 × 1,50 e intercalado con la malla (queda ø12@7,5): sin él, la flexión local daba 1,01
    fam('LF-suple', 'losa de fundación', 12, None, polis=[[(xpe - 75, yy + 7.5, zi + 1.4), (xpe + 75, yy + 7.5, zi + 1.4)] for yy in YS if abs(yy + 7.5 - ype) <= 75],
        d='suple inferior ø12@15 en 1–5 de la losa de fundación bajo el pilar de la escalera, de 1,50 × 1,50, intercalado con la malla (queda ø12@7,5)')
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
    # anclajes de las placas embebidas (insertos): barras lisas A36 verticales (ø22 en PLc, ø3/4" en PLb), soldadas bajo la placa, con cabeza soldada abajo
    polisA, polisP, polisU, polisX = [], [], [], []
    for pl in placas:
        x, y = pl['centro'][0] - c['ox'], pl['centro'][1] - c['oy']
        along = (0, 1) if pl['muro_dir'] == 'y' else (1, 0); across = (along[1], along[0])
        q = lambda t, o, z: (x + along[0] * t + across[0] * o, y + along[1] * t + across[1] * o, z)
        AN_ = ANCLAJE_C if pl['tipo'] == 'PLc' else ANCLAJE
        gl, ce = pl['cabeza'][0] / 2, AN_['cab_e']
        for t, o in pl['anclas']:
            # fuste: de la cara inferior de la placa a la cara de apoyo de la cabeza (hef bajo el NPOG 0); cabeza dibujada como un trazo de 5 a media altura de su espesor
            (polisP if pl['tipo'] == 'PLc' else polisA).append([q(t, o, -pl['espesor']), q(t, o, -pl['hef'])])
            (polisP if pl['tipo'] == 'PLc' else polisA).append([q(t - gl, o, -pl['hef'] - ce / 2), q(t + gl, o, -pl['hef'] - ce / 2)])
        if pl['tipo'] == 'PLb': continue
        # armadura de anclaje (ACI 318-19 17.5.2.1, con Ω0 = 2):
        if pl['sobre'] == 'muro del búnker':
            continue   # las verticales del muro (ø16@15 y ø12@15), desarrolladas a ambos lados del cono con hef 75, hacen de armadura de anclaje
        if 'dado' in pl['sobre']:
            # 6 verticales ø16 con ganchos de 15 arriba y abajo, a 20 de los pernos, fuera del CF que pasa por el dado
            for (t, o) in ((-20, -20), (20, -20), (-20, 20), (20, 20)):   # en el dado se cruzan dos CF: en (0, ±20) y (±20, 0) chocaban con sus barras
                polisU.append([q(t + 15 * (1 if t > 0 else -1), o, z_da_sup - 5.8), q(t, o, z_da_sup - 5.8), q(t, o, z_da_inf + 8.6), q(t + 15 * (1 if t > 0 else -1), o, z_da_inf + 8.6)])
            continue
        # sobrecimiento: estribos extra (los mismos del sobrecimiento) entre los existentes en ±25 del pilar: quedan @10 bajo la placa
        nS = 'E' if abs(y - yA[6]) < 1 else ('1' if abs(x - xA[0]) < 1 else '5')
        si = sc_info[nS]; tp = (x - si['o'][0]) * si['u'][0] + (y - si['o'][1]) * si['u'][1]
        for te in [20 * k + 10 for k in range(si['n'])] + [tp + v_ for v_ in AX_EXTRA.get(pl['pilar'], [])]:
            if abs(te - tp) <= 25:
                X_, Y_ = si['o'][0] + si['u'][0] * te, si['o'][1] + si['u'][1] * te; px_, py_ = si['p']; rs_ = si['rs']
                polisX.append([(X_ - px_ * si['pP'], Y_ - py_ * si['pP'], si['zP']), (X_ - px_ * rs_, Y_ - py_ * rs_, si['zP']), (X_ - px_ * rs_, Y_ - py_ * rs_, si['zT']), (X_ + px_ * rs_, Y_ + py_ * rs_, si['zT']), (X_ + px_ * rs_, Y_ + py_ * rs_, si['zP']), (X_ + px_ * si['pP'], Y_ + py_ * si['pP'], si['zP'])])
    nb = sum(1 for p in placas if p['tipo'] == 'PLb'); ncz = len(placas) - nb
    fam('AN', 'placa base PLb', 19, None, polis=polisA, d=f'anclajes del inserto PLb: 4 barras lisas A36 ø3/4" a 80 × 80, soldadas bajo la placa de 12 y a su cabeza 50 × 50 × 10 (filete 10 E7018), hef 450 (500 en 3A y 3B, bajo las 3ø16 de la VHA 25/50), en los {nb} pilares sin cruz')
    fam('AP', 'placa base PLc', ANCLAJE_C['diam'], None, polis=polisP, d=f'anclajes del inserto PLc: 4 barras lisas A36 ø22 (7/8") bajo las paredes del tubo, en dos filas a ±4,5 del eje del pilar, soldadas bajo la placa de 16 y a su cabeza 60 × 45 × 12 (filete 12 E7018); hef 1000 en los muros del búnker y 450 en el resto, en los {ncz} pilares con cruz (PLc-4A: 8 barras bajo una placa de 30, cabeza 100 × 45 × 12, hef 1200; PLc-1E: cabeza 80 × 45 × 12)')
    fam('AU', 'placa base PLc', 16, None, polis=polisU, d='armadura de anclaje de los dados: 4 verticales ø16 en las esquinas de un cuadrado de 40, con ganchos de 15 hacia afuera (Ω0 = 2)')
    # horquillas de corte (17.5.2.1 b): U horizontal que abraza los anclajes por el lado hacia donde empuja el corte; sus patas siguen ld hacia atrás
    polisH = []
    for pl in placas:
        if not pl.get('horquillas'): continue
        x, y = pl['centro'][0] - c['ox'], pl['centro'][1] - c['oy']
        along = (0, 1) if pl['muro_dir'] == 'y' else (1, 0); across = (along[1], along[0])
        q = lambda t, o, z: (x + along[0] * t + across[0] * o, y + along[1] * t + across[1] * o, z)
        ts = [a_[0] for a_ in pl['anclas']]; os_ = [a_[1] for a_ in pl['anclas']]
        rr = ANCLAJE_C['diam'] / 20 + HORQ['diam'] / 20 + 0.1; rl = rr + 0.2   # lomo en contacto con los anclajes; patas a 3 mm de ellos
        capas = []   # (sentido de las patas, profundidad bajo la cara)
        for i, dd in enumerate(pl['horquillas']):
            sent = 'al' if (dd in ('+al', '-al') or HORQ_DOBLA.get((pl['pilar'], dd), {}).get('hacia', '').endswith('al')) else 'ac'
            zz = HORQ_DOBLA.get((pl['pilar'], dd), {}).get('z', HORQ['z'] + (7.0 if pl['pilar'] == 'P-5C' else 0.0))   # en 5C sus patas entran al CF-C: van bajo los ganchos de 135° de sus estribos (16,5 bajo la cara)
            for s_, z_p in capas: zz = max(zz, z_p + (HORQ['dz_par'] if s_ == sent else HORQ['dz']))
            capas.append((sent, zz)); z_ = -zz
            if dd in ('+al', '-al'):
                sg = 1 if dd == '+al' else -1
                tb = (max(ts) if sg > 0 else min(ts)) + sg * rr; te = (min(ts) if sg > 0 else max(ts)) - sg * (ANCLAJE_C['diam'] / 20 + HORQ['ld'])
                o1, o2 = min(os_) - rl, max(os_) + rl
                # esquina del búnker: hacia atrás está la cara exterior del muro perpendicular a ~12 cm; las patas llegan hasta 9,5 / 12 de esa cara y doblan a 90° por
                # dentro de ese muro, hacia el centro del búnker, con ld recto después del doblez
                c0_ = (y if pl['muro_dir'] == 'y' else x); cara = None
                if pl['sobre'] == 'muro del búnker':
                    for f_ in ((by0, by1) if pl['muro_dir'] == 'y' else (bx0, bx1)):
                        if 0 < -sg * (f_ - c0_) < 30: cara = f_
                if cara is not None:
                    perp_c = (bx0 + bx1) / 2 - (x if pl['muro_dir'] == 'y' else y)   # hacia el centro del búnker, a lo largo del muro perpendicular (en coordenada 'o')
                    so = 1 if perp_c > 0 else -1
                    t_a = cara - c0_ + sg * 9.5; t_b = cara - c0_ + sg * 12.0          # la pata que dobla hacia adentro va más lejos de la cara
                    (oa, ta), (ob, tb_) = ((o2, t_a), (o1, t_b)) if so < 0 else ((o1, t_a), (o2, t_b))
                    polisH.append([q(ta, oa + so * HORQ['ld'], z_), q(ta, oa, z_), q(tb, oa, z_), q(tb, ob, z_), q(tb_, ob, z_), q(tb_, ob + so * HORQ['ld'], z_)])
                else:
                    polisH.append([q(te, o1, z_), q(tb, o1, z_), q(tb, o2, z_), q(te, o2, z_)])
            else:
                sg = 1 if dd == '+ac' else -1
                ob = (max(os_) if sg > 0 else min(os_)) + sg * rr; oe = (min(os_) if sg > 0 else max(os_)) - sg * (ANCLAJE_C['diam'] / 20 + HORQ['ld'])
                t1, t2 = min(ts) - rl, max(ts) + rl
                dobla = HORQ_DOBLA.get((pl['pilar'], dd), {}).get('hacia')
                if dobla:
                    # esquina de sobrecimientos (1E): hacia atrás la cara exterior queda a ~15 del eje del pilar; las patas llegan hasta 6,5 / 8,5 de esa cara
                    # (entre las ramas de los estribos y las barras del inserto) y doblan a 90° hacia 'dobla', por dentro del sobrecimiento perpendicular, con ld recto
                    so = 1 if dobla == '+al' else -1
                    cara_o = -sg * SOBRECIM[0] / 2
                    (ta, oa), (tb_, ob_) = ((t1, cara_o + sg * 8.5), (t2, cara_o + sg * 6.5)) if so < 0 else ((t2, cara_o + sg * 8.5), (t1, cara_o + sg * 6.5))
                    polisH.append([q(ta + so * HORQ['ld'], oa, z_), q(ta, oa, z_), q(ta, ob, z_), q(tb_, ob, z_), q(tb_, ob_, z_), q(tb_ + so * HORQ['ld'], ob_, z_)])
                else:
                    polisH.append([q(t1, oe, z_), q(t1, ob, z_), q(t2, ob, z_), q(t2, oe, z_)])
    if polisH:
        fam('AH', 'placa base PLc', HORQ['diam'], None, polis=polisH, d=f'horquillas de corte ø16 A630 (ACI 318-19 17.5.2.1 b) bajo las placas {", ".join(p["id"] for p in placas if p.get("horquillas"))}: abrazan las barras del inserto por el lado hacia donde empuja el corte, amarradas (sin soldar), con patas de {HORQ["ld"] * 10:.0f} (ld, ψt 1,3) hacia atrás')
    fam('AX', 'placa base PLc', 10, None, polis=polisX, d='estribos extra ø10 bajo los pilares con cruz sobre el sobrecimiento (quedan @10 en ±25; en 1E uno más a 13,5 del pilar): armadura de anclaje (Ω0 = 2); en los muros del búnker la dan sus verticales')
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
        dict(elemento=f'VHA {VHA[0]:.0f}/{VHA[1]:.0f} del eje 3 (bajo la losa; las vigas botadas del hueco van dentro de ella)', m3=round(sum(area(v['pts']) for v in vigas if not v.get('botada')) * (VHA[1] - LOSA) / 1e6, 2), hormigon='G30'),
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
    cub_fierro = [dict(diam=d, nombre=('ø3/4" A36' if d == 19 else ('ø7/8" A36' if d == 22 else f'ø{d}')), metros=round(cub_f[d] / 100, 1), kg=round(cub_f[d] / 100 * KGM[d])) for d in sorted(cub_f)]
    cub_acero = [dict(elemento=f'Pilar de la escalera {PILAR_ESC["perfil"]} {PILAR_ESC["acero"]} ({l_tubo / 100:.2f} m) y sus 2 placas PL 250×250×16 A36'.replace('.', ','), kg=round(kg_pe))]
    cubicacion = dict(hormigon=cub_h, total_m3=round(sum(x['m3'] for x in cub_h), 2), fierro=cub_fierro, total_kg=round(sum(x['kg'] for x in cub_fierro)),
                      acero=cub_acero, total_acero_kg=round(sum(x['kg'] for x in cub_acero)),
                      nota='volúmenes del modelo (sin pérdidas ni traslapos); fierro por largo de barras del modelo, sin traslapos ni ganchos adicionales; el acero del pilar de la escalera va aparte (acero)')
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
