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

# ---------- lo que dicen las láminas (dato) ----------
LOSA = 20.0                 # losa de techo del búnker (corte a-a)
MURO = 25.0                 # muro DM e=25 (corte a-a, elevación 1.a)
RADIER_BUNKER = 10.0        # radier e=10 (corte a-a / c-c)
RELLENO_BUNKER = 10.0       # relleno granular T.máx 1 1/2", 90 % Proctor modificado, bajo el radier (corte a-a)
ZAPATA_B = (100.0, 30.0)    # zapata corrida bajo los muros del búnker: 37,5 + 25 + 37,5 = 100 de ancho, 30 de alto (corte a-a)
EMPLANTILLADO = 10.0        # emplantillado G5 "Var. / Mn. 10" (sello 20 cm en el estrato indicado en la memoria de cálculo)
SOBRECIM = (25.0, 50.0)     # sobrecimiento de 25 x 50 bajo los pilares fuera del búnker (corte b-b: cadena 50 | 25 | var. mín. 10 = 75 hasta el sello)
CIMIENTO = (80.0, 25.0)     # cimiento corrido 27,5 + 25 + 27,5 = 80 de ancho, 25 de alto, de −50 (NTN) a −75 (corte b-b)
CF = (25.0, 40.0)           # CF 25/40 bajo los ejes interiores con pilares; va de −10 a −50, bajo el radier de 10 (elevación 2.a: cadena 10 + 40, fondo en el NTN −50)
CF_TOPE = -10.0             # cara superior del CF: bajo el radier; el anclaje de 43 de la placa queda dentro con 7 de recubrimiento
RADIER_EST = 10.0           # radier e=10 del estudio (corte b-b)
POLIESTIRENO = 10.0         # poliestireno expandido de alta densidad e=100 mm bajo el radier (corte b-b)
RELLENO_EST = 15.0          # relleno granular 15 bajo el poliestireno, sobre sub base granular compactada (corte b-b)
VHA = (25.0, 40.0)          # VHA 25/40: 20 dentro de la losa + 20 bajo ella (detalle VHA 25/40)
PLACA = (20.0, 20.0, 0.8)   # PLb 200 x 200 x 8 mm (detalle placa base)
ANCLAJE = dict(diam=19, n=2, sep=14.0, largo=43.0, gancho=10.0, estribos='ø8@20')   # 1+1 ø3/4: dos horquillas en U (una por dirección) de L=1200 mm: 140 bajo la placa, ramas de 430 y ganchos de 100 hacia afuera; Est. ø8@20
GAP = 0.5                   # separación entre piezas apiladas, para que las caras no parpadeen en el 3D

ESPECIFICACIONES = dict(
    emplantillado='Hormigón G5', hormigon='Hormigón G25', acero='Acero A630-420H',
    recubrimientos={'fundaciones': 5, 'elementos de hormigón armado': 3, 'losa': 2}, traslapo='60 diámetros',
    fuente='lámina 02 rev G (07-04-2026), especificaciones técnicas generales')
KGM = {8: 0.395, 10: 0.617, 12: 0.888, 16: 1.578, 19: 2.235}   # kg/m por diámetro (ø19 = 3/4")

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
    z_losa_inf = -LOSA; z_piso = z_losa_inf - H                      # −20, −300
    z_rad_inf = z_piso - RADIER_BUNKER; z_rell_inf = z_rad_inf - RELLENO_BUNKER   # −310, −320 (= tope de la zapata = pie del muro)
    z_zap_sup = z_rell_inf; z_zap_inf = z_zap_sup - ZAPATA_B[1]      # −320, −350
    z_emp_inf = z_zap_inf - EMPLANTILLADO                            # −360
    Z = lambda z: r1(z0 + z)
    hb = ZAPATA_B[0] / 2                                             # 50: media zapata

    def pieza(id_, x0, y0, x1, y1, zi, zs, nombre, d, **k):
        return dict(id=id_, pts=rect(x0, y0, x1, y1), z_inf=Z(zi), z_sup=Z(zs), nombre=nombre, d=d, **k)

    # ---------- búnker ----------
    muros = dict(espesor=MURO, z_inf=Z(z_zap_sup + GAP), z_sup=Z(z_losa_inf), alto=r1(z_losa_inf - z_zap_sup),
                 armadura='DM (doble malla): V ø12@15 que bajan hasta el fondo de la zapata (pata de 30 sobre su parrilla) y terminan con gancho de 20 en la losa (L≈3,92 m), H ø10@20, 2ø12 de coronamiento bajo la losa; recubrimiento 3',
                 fuente='lámina 01 rev 1, cortes a-a y c-c; lámina 03 rev H, elevación 1.a; lámina 05 rev H, elevación A1',
                 piezas=[dict(id='M-N', pts=rect(bx0, by0, bx1, by0 + MURO), lado='norte (recibe los 5 pilares del eje A)'),
                         dict(id='M-S', pts=rect(bx0, by1 - MURO, bx1, by1), lado='sur, bajo el tabique cafetería/estudio (recibe los 5 pilares del eje B)'),
                         dict(id='M-O', pts=rect(bx0, by0 + MURO, bx0 + MURO, by1 - MURO), lado='poniente'),
                         dict(id='M-E', pts=rect(bx1 - MURO, by0 + MURO, bx1, by1 - MURO), lado='oriente')])
    losa = dict(espesor=LOSA, pts=rect(bx0, by0, bx1, by1), hueco=rect(ex_h, ey0, ex1 := c['ex1'], ey1), z_inf=Z(z_losa_inf), z_sup=Z(0),
                armadura='inferior: ø10@20 en la luz corta (N-S, 6,00 m entre muros, con ganchos de 13,5 en los muros) y ø8@20 en la larga (E-O); '
                         'superior: ø8@20 sobre la VHA (42 a cada lado); 2ø12 de borde en los muros y 2ø12 L=456 de borde en el hueco de la escalera; recubrimiento 2',
                fuente='lámina 03 rev H, planta losa (L001/L002); el original salva 5,00 m: con 6,00 el ingeniero debe recalcular')
    piso = dict(espesor=RADIER_BUNKER, pts=rect(bx0 + MURO, by0 + MURO, bx1 - MURO, by1 - MURO), z_inf=Z(z_rad_inf), z_sup=Z(z_piso),
                armadura='radier e=10 (sin armadura en el corte)', fuente='lámina 01 rev 1, corte a-a')
    relleno_b = dict(espesor=RELLENO_BUNKER, pts=rect(bx0 + MURO, by0 + MURO, bx1 - MURO, by1 - MURO), z_inf=Z(z_rell_inf + GAP), z_sup=Z(z_rad_inf - GAP),
                     dato='relleno granular T.máx 1 1/2", 90 % Proctor modificado', fuente='lámina 01 rev 1, corte a-a')
    # zapata corrida de 100 x 30 bajo los cuatro muros (anillo: norte y sur completos, poniente y oriente entre ellos)
    zx0, zy0, zx1, zy1 = bx0 - 37.5, by0 - 37.5, bx1 + 37.5, by1 + 37.5
    zap_piezas = [pieza('ZC-N', zx0, zy0, zx1, zy0 + ZAPATA_B[0], z_zap_inf, z_zap_sup, 'Zapata corrida del búnker (norte)', 'bajo el muro norte'),
                  pieza('ZC-S', zx0, zy1 - ZAPATA_B[0], zx1, zy1, z_zap_inf, z_zap_sup, 'Zapata corrida del búnker (sur)', 'bajo el muro sur'),
                  pieza('ZC-O', zx0, zy0 + ZAPATA_B[0], zx0 + ZAPATA_B[0], zy1 - ZAPATA_B[0], z_zap_inf, z_zap_sup, 'Zapata corrida del búnker (poniente)', 'bajo el muro poniente'),
                  pieza('ZC-E', zx1 - ZAPATA_B[0], zy0 + ZAPATA_B[0], zx1, zy1 - ZAPATA_B[0], z_zap_inf, z_zap_sup, 'Zapata corrida del búnker (oriente)', 'bajo el muro oriente')]
    zapata_corrida = dict(ancho=ZAPATA_B[0], espesor=ZAPATA_B[1], z_sup=Z(z_zap_sup), z_inf=Z(z_zap_inf), piezas=zap_piezas,
                          armadura='ø16@20 L=130 (U de 90 con ganchos de 20 hacia arriba) + 4ø10 longitudinales; recubrimiento 5',
                          emplantillado=dict(espesor=EMPLANTILLADO, z_sup=Z(z_zap_inf - GAP), z_inf=Z(z_emp_inf), hormigon='G5',
                                             piezas=[dict(id=p['id'].replace('ZC', 'EMP'), pts=p['pts']) for p in zap_piezas],
                                             nota='Var. / mín. 10: el sello va 20 cm dentro del estrato indicado en la memoria de cálculo'),
                          fuente='lámina 01 rev 1, cortes a-a y c-c (37,5 + 25 + 37,5 = 100; 30 de alto; NPOG −312 a −342 en el original)')
    # vigas bajo la losa
    vigas = [dict(id='VHA-3', nombre='VHA 25/40', pts=rect(x3 - 12.5, by0 + MURO, x3 + 12.5, by1 - MURO), z_inf=Z(z_losa_inf - (VHA[1] - LOSA)), z_sup=Z(z_losa_inf),
                  armadura='3ø12 arriba, 2ø10 al medio, 3ø16 abajo, Est ø10@20 (20 dentro de la losa + 20 bajo ella)',
                  d=f'viga bajo la losa en el eje 3, de muro a muro ({by1 - by0 - 2 * MURO:.0f}): parte la losa en dos paños como la del eje 2.a original', fuente='lámina 03 rev H, detalle VHA 25/40'),
             dict(id='VHA-esc', nombre='VHA 25/40 de borde', pts=rect(ex0, ey0 - 25, ex_h, ey1), z_inf=Z(z_losa_inf - (VHA[1] - LOSA)), z_sup=Z(z_losa_inf),
                  armadura='como VHA 25/40 (propuesta)', d='viga de borde del hueco de la escalera, bajo el muro de la caja (el original llevaba 2ø12 de borde en un hueco de 3,05 x 1,00)', fuente='propuesta')]

    # ---------- fuera del búnker: sobrecimiento + cimiento corrido bajo las fachadas; CF 25/40 bajo los tabiques con pilares ----------
    z_sc_inf = -SOBRECIM[1]; z_ci_inf = z_sc_inf - CIMIENTO[1]; z_cemp_inf = z_ci_inf - EMPLANTILLADO   # −75, −100, −110
    hs, hc = SOBRECIM[0] / 2, CIMIENTO[0] / 2
    tramos_sc = [('1', xA[0], by1, xA[0], yA[6] - hs, 'bajo la fachada poniente, del búnker a la fachada sur'),
                 ('5', xA[4], by1, xA[4], yA[6] - hs, 'bajo la fachada oriente, del búnker a la fachada sur'),
                 ('E', xA[0] - hs, yA[6], xA[4] + hs, yA[6], 'bajo la fachada sur')]
    sc_piezas, ci_piezas, cemp_piezas = [], [], []
    for n, x0, y0, x1, y1, d in tramos_sc:
        vert = abs(x1 - x0) < 1
        if vert:
            sc_piezas.append(pieza(f'SC-{n}', x0 - hs, y0, x0 + hs, y1, z_sc_inf, 0, 'Sobrecimiento 25 × 50', d))
            ci_piezas.append(pieza(f'CC-{n}', x0 - hc, y0, x0 + hc, y1 - (hc - hs), z_ci_inf, z_sc_inf - GAP, 'Cimiento corrido 80 × 25', d))
        else:
            sc_piezas.append(pieza(f'SC-{n}', x0, y0 - hs, x1, y0 + hs, z_sc_inf, 0, 'Sobrecimiento 25 × 50', d))
            ci_piezas.append(pieza(f'CC-{n}', x0 - (hc - hs), y0 - hc, x1 + (hc - hs), y0 + hc, z_ci_inf, z_sc_inf - GAP, 'Cimiento corrido 80 × 25', d))
    for p in ci_piezas: cemp_piezas.append(dict(id=p['id'].replace('CC', 'EMP'), pts=p['pts'], z_inf=Z(z_cemp_inf), z_sup=Z(z_ci_inf - GAP)))
    cimiento = dict(sobrecimiento=dict(ancho=SOBRECIM[0], alto=SOBRECIM[1], z_sup=Z(0), z_inf=Z(z_sc_inf), piezas=sc_piezas,
                                       armadura='2ø12 arriba, ø10@20 L=211 (U que baja hasta el cimiento, ganchos de 15 arriba), ø8@20 horizontales; recubrimiento 3'),
                    zapata=dict(ancho=CIMIENTO[0], espesor=CIMIENTO[1], z_sup=Z(z_sc_inf - GAP), z_inf=Z(z_ci_inf), piezas=ci_piezas,
                                armadura='ø12@20 L=100 (U de 70 con ganchos de 15) + 4ø10 longitudinales; recubrimiento 5'),
                    emplantillado=dict(espesor=EMPLANTILLADO, z_sup=Z(z_ci_inf - GAP), z_inf=Z(z_cemp_inf), hormigon='G5', piezas=cemp_piezas),
                    fuente='lámina 01 rev 1, corte b-b (cadena 50 | 25 | var. mín. 10: sobrecimiento 25 x 50 hasta el NTN −50, zapata 27,5 + 25 + 27,5 = 80 x 25 de −50 a −75, emplantillado)',
                    nota='bajo las fachadas fuera del búnker; el original lo lleva bajo todo su perímetro F1 y sus esquinas, con placas PLb encima de cada pilar')
    hcf = CF[0] / 2; z_cf_sup = CF_TOPE - GAP; z_cf_inf = CF_TOPE - CF[1]; z_cfe_inf = z_cf_inf - EMPLANTILLADO   # −10,5, −50 (= NTN), −60
    cf_piezas = [pieza('CF-4', xA[3] - hcf, by1, xA[3] + hcf, yA[6] - hs, z_cf_inf, z_cf_sup, 'CF 25/40', 'bajo el tabique estudio/baño-bodega (eje 4), del búnker a la fachada sur, bajo el radier'),
                 pieza('CF-C', xA[3] + hcf, yC - hcf, xA[4] - hs, yC + hcf, z_cf_inf, z_cf_sup, 'CF 25/40', 'bajo el tabique baño/cabina (eje C), del eje 4 a la fachada oriente, bajo el radier'),
                 pieza('CF-C2', xA[3] + hcf, yC2 - hcf, xA[4] - hs, yC2 + hcf, z_cf_inf, z_cf_sup, 'CF 25/40', 'bajo el tabique cabina/bodega (eje C2), del eje 4 a la fachada oriente, bajo el radier')]
    cf = dict(ancho=CF[0], alto=CF[1], z_sup=Z(CF_TOPE), z_inf=Z(z_cf_inf), piezas=cf_piezas,
              emplantillado=dict(espesor=EMPLANTILLADO, z_sup=Z(z_cf_inf - GAP), z_inf=Z(z_cfe_inf), hormigon='G5',
                                 piezas=[dict(id=p['id'].replace('CF', 'EMP'), pts=rect(min(q[0] for q in p['pts']) - 7.5 - c['ox'], min(q[1] for q in p['pts']) - 7.5 - c['oy'], max(q[0] for q in p['pts']) + 7.5 - c['ox'], max(q[1] for q in p['pts']) + 7.5 - c['oy'])) for p in cf_piezas]),
              armadura='3ø12 arriba, 2ø10 al medio, 3ø12 abajo, Est ø10@25; emplantillado de 40 x 10',
              fuente='lámina 01 rev 1, detalle CF 25/40 y planta (bajo el eje 2.a del original); lámina 04 rev I, elevación 2.a (cadena 10 + 40: el radier de 10 va encima, el fondo del CF en el NTN −50)',
              nota='el ingeniero lo usa bajo su eje interior 2.a; aquí va bajo los dos tabiques con pilares. Con la placa en NPOG 0, el anclaje de 43 termina a −43, dentro del CF (−10 a −50) con 7 de recubrimiento')
    # radier del estudio (fuera del búnker) en tres paños, dejando las franjas del sobrecimiento y de los CF (caras coplanares parpadean)
    g = GAP
    rad_pts = [('estudio', xA[0] + hs + g, by1 + g, xA[3] - hcf - g, yA[6] - hs - g),
               ('bano', xA[3] + hcf + g, by1 + g, xA[4] - hs - g, yC - hcf - g),
               ('cabina', xA[3] + hcf + g, yC + hcf + g, xA[4] - hs - g, yC2 - hcf - g),
               ('bodega', xA[3] + hcf + g, yC2 + hcf + g, xA[4] - hs - g, yA[6] - hs - g)]
    capas = [('radier', 'Radier e=10', 0, -RADIER_EST), ('poliestireno', 'Poliestireno expandido de alta densidad e=100', -RADIER_EST - g, -RADIER_EST - POLIESTIRENO),
             ('relleno', 'Relleno granular 15 (T.máx 1 1/2", 90 % Proctor modificado) sobre sub base granular compactada', -RADIER_EST - POLIESTIRENO - g, -RADIER_EST - POLIESTIRENO - RELLENO_EST)]
    rad_cont = [('estudio, baño, cabina y bodega', xA[0] + hs + g, by1 + g, xA[4] - hs - g, yA[6] - hs - g)]   # el radier es continuo: pasa sobre los CF
    radier_estudio = dict(capas=[dict(id=k, nombre=nm, z_sup=Z(zs), z_inf=Z(zi), piezas=[dict(id=f'{k}-{r}', pts=rect(x0, y0, x1, y1), recinto=r) for r, x0, y0, x1, y1 in (rad_cont if k == 'radier' else rad_pts)]) for k, nm, zs, zi in capas],
                          fuente='lámina 01 rev 1, corte b-b (radier 10 sobre poliestireno 10, relleno 15 y sub base)')

    # ---------- placas base PLb en todos los pilares ----------
    placas = []
    for mb in c['pilares']:
        x, y = mb['a'][0], mb['a'][1]
        yl = y - c['oy']
        sobre = 'muro del búnker' if yl <= by1 + 1 else ('CF 25/40' if abs(mb['a'][0] - c['ox'] - xA[3]) < 1 or abs(yl - yC) < 1 or abs(yl - yC2) < 1 else 'sobrecimiento')
        xl = mb['a'][0] - c['ox']
        muro_dir = 'y' if (abs(xl - xA[0]) < 1 or abs(xl - xA[4]) < 1 or (abs(xl - xA[3]) < 1 and yl > by1 + 1 and abs(yl - yC) > 1 and abs(yl - yC2) > 1)) else 'x'   # sentido del muro bajo el pilar
        placas.append(dict(id='PLb-' + mb['id'][2:], pilar=mb['id'], perfil=mb['p'], centro=[r1(x), r1(y)], z=Z(0), lado=PLACA[0], espesor=PLACA[2], sobre=sobre, muro_dir=muro_dir,
                           anclajes=f'1+1 ø3/4" en horquilla (L=120: {ANCLAJE["sep"]:.0f} bajo la placa, ramas de {ANCLAJE["largo"]:.0f} y ganchos de {ANCLAJE["gancho"]:.0f}), Est. {ANCLAJE["estribos"]}'))
    placas_info = dict(detalle='PLb 200 x 200 x 8 mm soldada al tubo en todo el contorno, bajo todos los pilares (PM1, PM2 y PM3); anclaje 1+1 ø3/4" en horquilla, L=1200 mm (140 bajo la placa, ramas de 430, ganchos de 100 hacia adentro), con estribos ø8@20, embebido en el muro, sobrecimiento o CF de 25 (sin pedestal)',
                       fuente='lámina 01 rev 1, detalle placa base PLb y planta (PLb en los 23 pilares del original)', lista=placas)

    hormigon = dict(especificaciones=ESPECIFICACIONES, muros=muros, losa=losa, piso=piso, relleno=relleno_b, zapata_corrida=zapata_corrida, vigas=vigas,
                    cimiento=cimiento, cf=cf, radier_estudio=radier_estudio, placas=placas_info, escalera=c['escalera'],
                    interior=dict(ancho=r1(bx1 - bx0 - 2 * MURO), largo=r1(by1 - by0 - 2 * MURO), alto=H,
                                  terminado=dict(ancho=r1(bx1 - bx0 - 2 * MURO - 2 * c.get('T', 0)), largo=r1(by1 - by0 - 2 * MURO - 2 * c.get('T', 0)), tabique=c.get('T', 0), nota='entre los tabiques de 10 que van por dentro de los muros (Gabriel, 14-10-2026)')),
                    niveles=dict(npog_0='NPOG 0,00 = cara superior de la losa del búnker y del radier (obra gruesa); el piso terminado va más arriba (sobrelosa + adhesivo + porcelanato)', losa_inf=z_losa_inf, piso_bunker=z_piso, radier_bunker_inf=z_rad_inf,
                                 zapata_sup=z_zap_sup, zapata_inf=z_zap_inf, emplantillado_inf=z_emp_inf, ntn=-50, sobrecimiento_inf=z_sc_inf, cimiento_inf=z_ci_inf, cf_sup=CF_TOPE, cf_inf=z_cf_inf,
                                 nota='el original tiene el búnker de 2,72 libres (−272 piso, −292 radier, −312 zapata, −342 sello); con los 2,80 de Gabriel todo baja 8 cm'))

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
    # muros del búnker: por muro, eje y normal hacia adentro
    murosL = [('N', (bx0, by0 + 12.5), (bx1, by0 + 12.5), (0, 1)), ('S', (bx0, by1 - 12.5), (bx1, by1 - 12.5), (0, -1)),
              ('O', (bx0 + 12.5, by0 + 25), (bx0 + 12.5, by1 - 25), (1, 0)), ('E', (bx1 - 12.5, by0 + 25), (bx1 - 12.5, by1 - 25), (-1, 0))]   # O/E entre los muros N y S (sus verticales se alargan a las esquinas abajo)
    for nm, a, b, nrm in murosL:
        dx, dy = b[0] - a[0], b[1] - a[1]; ln = math.hypot(dx, dy); ux, uy = dx / ln, dy / ln
        extV = 25.0 if nm in ('O', 'E') else 0.0   # verticales: los muros poniente/oriente también arman la esquina (las mallas se cruzan)
        nV = int((ln + 2 * extV) // 15)
        for cara, s in (('exterior', -1), ('interior', 1)):
            fx, fy = nrm[0] * 9 * s, nrm[1] * 9 * s        # 9 = 12,5 − 3 de recubrimiento − medio ø
            gx, gy = nrm[0] * (-s) * 30, nrm[1] * (-s) * 30  # gancho inferior de 30 hacia la otra cara
            hx, hy = nrm[0] * 20, nrm[1] * 20               # gancho superior de 20 en la losa, hacia adentro
            x0, y0 = a[0] - ux * extV + ux * 7.5 + fx, a[1] - uy * extV + uy * 7.5 + fy
            # la barra baja dentro de la zapata: la pata de 30 va apoyada sobre la parrilla del fondo (corte a-a: 20 + 334 + 30 = 384 en el original)
            fam(f'MV-{nm}-{cara[:3]}', 'muro del búnker', 12, [(x0 + gx, y0 + gy, z_zap_inf + 7), (x0, y0, z_zap_inf + 7), (x0, y0, -3), (x0 + hx, y0 + hy, -3)],
                n=nV, paso=(ux * 15, uy * 15, 0), d=f'verticales ø12@15 del muro {nm}, malla {cara}: bajan dentro de la zapata con la pata de 30 sobre la parrilla del fondo y terminan con gancho de 20 en la losa (L≈{(-3 - (z_zap_inf + 7) + 50)/100:.2f} m)'.replace('.', ','))
            if nm in ('N', 'S'):
                polH = [(a[0] + fx, a[1] + fy, z_zap_sup + 10), (b[0] + fx, b[1] + fy, z_zap_sup + 10)]
                polC = [(a[0] + fx, a[1] + fy, -3), (b[0] + fx, b[1] + fy, -3)]
                dH = f'horizontales ø10@20 del muro {nm}, malla {cara} (corren de esquina a esquina)'
            else:
                # muros poniente y oriente: las barras entran al muro N y al muro S hasta su recubrimiento lejano y doblan 60ø a lo largo de ellos
                sx = 1 if nm == 'O' else -1
                polH = barra_L('y', a[0], fx, a[1], b[1], z_zap_sup + 10, (by0 + 3.5, sx * L60(10), 0), (by1 - 3.5, sx * L60(10), 0))
                polC = barra_L('y', a[0], fx, a[1], b[1], -3, (by0 + 3.5, sx * L60(12), 0), (by1 - 3.5, sx * L60(12), 0))
                dH = f'horizontales ø10@20 del muro {nm}, malla {cara}, con patas de {L60(10):.0f} dentro de los muros norte y sur (60ø)'
            fam(f'MH-{nm}-{cara[:3]}', 'muro del búnker', 10, polH, n=int((z_losa_inf - 5 - (z_zap_sup + 10)) // 20) + 1, paso=(0, 0, 20), d=dH)
            fam(f'MC-{nm}-{cara[:3]}', 'muro del búnker', 12, polC, d=f'2ø12 de coronamiento del muro {nm} (borde de la losa)' + ('' if nm in ('N', 'S') else f', con patas de {L60(12):.0f} en las esquinas'))
    # losa: inferior N-S ø10@20 (luz corta) y E-O ø8@20; superior ø8@20 sobre la VHA; borde del hueco 2ø12
    polisNS = []
    x = bx0 + MURO + 10
    while x < bx1 - MURO:
        if ex_h <= x <= ex1:
            polisNS.append([(x, by0 + 5, -3.5), (x, by0 + 5, -17), (x, ey0 - 5, -17), (x, ey0 - 5, -3.5)])
            polisNS.append([(x, ey1 + 5, -3.5), (x, ey1 + 5, -17), (x, by1 - 5, -17), (x, by1 - 5, -3.5)])
        else:
            polisNS.append([(x, by0 + 5, -3.5), (x, by0 + 5, -17), (x, by1 - 5, -17), (x, by1 - 5, -3.5)])
        x += 20
    fam('LN', 'losa del búnker', 10, None, polis=polisNS, d='inferiores ø10@20 N-S (luz corta, 6,00 entre muros), ganchos de 13,5 en los muros; cortadas en el hueco de la escalera')
    polisEO = []
    y = by0 + MURO + 10
    while y < by1 - MURO:
        xf = ex_h - 5 if ey0 <= y <= ey1 else bx1 - 5
        polisEO.append([(bx0 + 5, y, -3.5), (bx0 + 5, y, -16), (xf, y, -16), (xf, y, -3.5)])
        y += 20
    fam('LE', 'losa del búnker', 8, None, polis=polisEO, d='inferiores ø8@20 E-O, ganchos de 13,5 en los muros; cortadas en el hueco de la escalera')
    fam('LS', 'losa del búnker', 8, [(x3 - 42, by0 + MURO + 10, -3), (x3 + 42, by0 + MURO + 10, -3)], n=int((by1 - by0 - 2 * MURO) // 20), paso=(0, 20, 0), d='superiores ø8@20 sobre la VHA 25/40 (42 a cada lado del eje 3)')
    for zz, tag in ((-3, 'sup'), (-17, 'inf')):
        fam(f'LH-{tag}', 'losa del búnker', 12, None, polis=[[(ex_h - 6, ey0 - 60, zz), (ex_h - 6, ey1 + 60, zz)], [(ex_h - 60, ey0 - 6, zz), (bx1 - 5, ey0 - 6, zz)], [(ex_h - 60, ey1 + 6, zz), (bx1 - 5, ey1 + 6, zz)]],
            d=f'2ø12 de borde del hueco de la escalera, capa {tag}erior (L=456 en el original, 60 más allá del hueco)')
    # VHA 25/40 (eje 3) y de borde de la escalera
    for vid, xc, ya, yb in (('VHA-3', x3, by0 + 5, by1 - 5), ('VHA-esc', (ex0 + ex_h) / 2, ey0 - 25 + 5, ey1 - 5)):
        ancho = 25 if vid == 'VHA-3' else ex_h - ex0
        o = ancho / 2 - 3.5
        fam(f'{vid}-sup', 'VHA 25/40', 12, None, polis=[[(xc + k, ya, -3), (xc + k, yb, -3)] for k in (-o, 0, o)], d=f'3ø12 superiores de la {vid}')
        fam(f'{vid}-med', 'VHA 25/40', 10, None, polis=[[(xc + k, ya, -20), (xc + k, yb, -20)] for k in (-o, o)], d=f'2ø10 medios de la {vid}')
        fam(f'{vid}-inf', 'VHA 25/40', 16, None, polis=[[(xc + k, ya, -37), (xc + k, yb, -37)] for k in (-o, 0, o)], d=f'3ø16 inferiores de la {vid}')
        fam(f'{vid}-est', 'VHA 25/40', 10, [(xc - o, ya + 10, -3), (xc + o, ya + 10, -3), (xc + o, ya + 10, -37), (xc - o, ya + 10, -37), (xc - o, ya + 10, -3)],
            n=int((yb - ya) // 20), paso=(0, 20, 0), d=f'estribos ø10@20 de la {vid}')
    # zapata corrida del búnker: U ø16@20 (90 + ganchos 20) + 4ø10
    for nm, a, b, nrm in murosL:
        dx, dy = b[0] - a[0], b[1] - a[1]; ln = math.hypot(dx, dy); ux, uy = dx / ln, dy / ln
        ext = 37.5   # las U de los cuatro lados cubren las esquinas (ahí la parrilla queda doble, en los dos sentidos)
        extL = 37.5 if nm in ('N', 'S') else -12.5 + L60(10)   # longitudinales O/E: entran 60ø (60 cm) en las zapatas norte y sur
        a2 = (a[0] - ux * ext, a[1] - uy * ext); ln2 = ln + 2 * ext
        px, py = nrm[0], nrm[1]
        fam(f'ZU-{nm}', 'zapata corrida del búnker', 16, [(a2[0] - px * 45, a2[1] - py * 45, z_zap_inf + 25), (a2[0] - px * 45, a2[1] - py * 45, z_zap_inf + 5), (a2[0] + px * 45, a2[1] + py * 45, z_zap_inf + 5), (a2[0] + px * 45, a2[1] + py * 45, z_zap_inf + 25)],
            n=int(ln2 // 20) + 1, paso=(ux * 20, uy * 20, 0), d=f'ø16@20 L=130 en U de la zapata corrida ({nm}), ganchos de 20 hacia arriba')
        a3 = (a[0] - ux * extL, a[1] - uy * extL); ln3 = ln + 2 * extL
        fam(f'ZL-{nm}', 'zapata corrida del búnker', 10, None, polis=[[(a3[0] + px * k, a3[1] + py * k, z_zap_inf + 6), (a3[0] + ux * ln3 + px * k, a3[1] + uy * ln3 + py * k, z_zap_inf + 6)] for k in (-42, -14, 14, 42)],
            d=f'4ø10 longitudinales de la zapata corrida ({nm})' + ('' if nm in ('N', 'S') else ', traslapados 60 cm (60ø) dentro de las zapatas norte y sur'))
    # sobrecimiento y cimiento corrido fuera del búnker
    yE = yA[6]                                   # eje de la fachada sur; su sobrecimiento va de yE−12,5 a yE+12,5 y su cimiento de yE−40 a yE+40
    def extremos(n, diam, prof):
        # extremos de las barras longitudinales de cada tramo (ini, fin) para barra_L; prof = 'sc' (sobrecimiento, 25 de ancho) o 'ci' (cimiento, 80)
        Lp = L60(diam); b = 3.5 if prof == 'sc' else 5.0   # recubrimiento lejano
        if n == '1':   # de norte a sur: arranca en el muro sur del búnker (entra al muro y dobla hacia el oriente) y termina en la fachada sur (entra al tramo E y dobla hacia el oriente)
            return ((by1 - MURO + b, Lp, 0), ((yE + 12.5 - b) if prof == 'sc' else (yE + 40 - b), Lp, 0))
        if n == '5':   # igual, doblando hacia el poniente
            return ((by1 - MURO + b, -Lp, 0), ((yE + 12.5 - b) if prof == 'sc' else (yE + 40 - b), -Lp, 0))
        # tramo E (de poniente a oriente): en las dos esquinas entra al tramo 1 / 5 hasta su recubrimiento lejano y dobla hacia el norte
        xo = (xA[0] - 12.5 + b) if prof == 'sc' else (xA[0] - 40 + b); xe = (xA[4] + 12.5 - b) if prof == 'sc' else (xA[4] + 40 - b)
        return ((xo, 0, -Lp), (xe, 0, -Lp))
    for n, x0, y0, x1, y1, d in tramos_sc:
        dx, dy = x1 - x0, y1 - y0; ln = math.hypot(dx, dy); ux, uy = dx / ln, dy / ln; px, py = -uy, ux
        ejeB = 'y' if abs(dx) < 1 else 'x'; cB = x0 if ejeB == 'y' else y0; tA, tB = (y0, y1) if ejeB == 'y' else (x0, x1)
        # las U arrancan 3,5 antes del inicio del tramo (recubrimiento) y llegan al final de la pieza: en las esquinas quedan U en los dos sentidos
        # tramo E: su pieza va de cara exterior a cara exterior (0..1055): las U de 3,5 a 1051,5. Tramos 1 y 5: siguen hasta la cara exterior del tramo E menos 3,5
        xU, yU = x0 + ux * (3.5 if n == 'E' else 0.0), y0 + uy * 0.0
        lnU = (ln - 7.0) if n == 'E' else (ln + 25.0 - 3.5)
        fam(f'SU-{n}', 'sobrecimiento', 10, [(xU + px * 6, yU + py * 6, -5), (xU - px * 9, yU - py * 9, -5), (xU - px * 9, yU - py * 9, z_ci_inf + 7), (xU + px * 9, yU + py * 9, z_ci_inf + 7), (xU + px * 9, yU + py * 9, -5), (xU - px * 6, yU - py * 6, -5)],
            n=int(lnU // 20) + 1, paso=(ux * 20, uy * 20, 0), d=f'ø10@20 L=211 en U del sobrecimiento (eje {n}), con ganchos de 15 arriba; en las esquinas las U van en los dos sentidos')
        i12, f12 = extremos(n, 12, 'sc'); i8, f8 = extremos(n, 8, 'sc'); i10, f10 = extremos(n, 10, 'ci')
        fam(f'S12-{n}', 'sobrecimiento', 12, None, polis=[barra_L(ejeB, cB, k, tA, tB, -5, i12, f12) for k in (-9, 9)], d=f'2ø12 superiores del sobrecimiento (eje {n}), con patas de {L60(12):.0f} (60ø) en las esquinas y ancladas en el muro del búnker')
        fam(f'S8-{n}', 'sobrecimiento', 8, None, polis=[barra_L(ejeB, cB, k, tA, tB, zz, i8, f8) for k in (-9, 9) for zz in (-15, -35)], d=f'ø8@20 horizontales del sobrecimiento (eje {n}), dos caras, con patas de {L60(8):.0f} (60ø) en las esquinas')
        # cimiento: la pieza E va de −27,5 a 1082,5 (80 de ancho en los extremos): U de −22,5 a 1077,5; las de 1 y 5 siguen hasta 1597,5 (cara exterior del cimiento E menos 5)
        xC, yC_ = x0 - ux * (27.5 - 5.0 if n == 'E' else 0.0), y0 + uy * 0.0
        lnC = (ln + 2 * (27.5 - 5.0)) if n == 'E' else (ln + 12.5 + 40.0 - 5.0)
        fam(f'CU-{n}', 'cimiento corrido', 12, [(xC - px * 35, yC_ - py * 35, z_ci_inf + 20), (xC - px * 35, yC_ - py * 35, z_ci_inf + 5), (xC + px * 35, yC_ + py * 35, z_ci_inf + 5), (xC + px * 35, yC_ + py * 35, z_ci_inf + 20)],
            n=int(lnC // 20) + 1, paso=(ux * 20, uy * 20, 0), d=f'ø12@20 L=100 en U del cimiento corrido (eje {n}), ganchos de 15; en las esquinas las U van en los dos sentidos')
        fam(f'CL-{n}', 'cimiento corrido', 10, None, polis=[barra_L(ejeB, cB, k, tA, tB, z_ci_inf + 6, i10, f10) for k in (-33, -11, 11, 33)], d=f'4ø10 longitudinales del cimiento corrido (eje {n}), con patas de {L60(10):.0f} (60ø) en las esquinas y ancladas en el muro del búnker')
    # CF 25/40
    for cid, x0, y0, x1, y1 in (('CF-4', xA[3], by1 + 5, xA[3], yA[6] - 15), ('CF-C', xA[3] + 15, yC, xA[4] - 15, yC), ('CF-C2', xA[3] + 15, yC2, xA[4] - 15, yC2)):
        dx, dy = x1 - x0, y1 - y0; ln = math.hypot(dx, dy); ux, uy = dx / ln, dy / ln; px, py = -uy, ux
        if cid == 'CF-4':   # N-S: entra al muro sur del búnker (dobla al oriente) y al sobrecimiento sur (dobla al oriente)
            ejeB, cB, tA, tB = 'y', xA[3], y0, y1
            ext = lambda dm: ((by1 - MURO + 3.5, L60(dm), 0), (yE + 12.5 - 3.5, L60(dm), 0))
        else:               # E-O: entra al CF-4 (dobla al norte) y al sobrecimiento oriente (dobla al norte)
            ejeB, cB, tA, tB = 'x', yC, x0, x1
            ext = lambda dm: ((xA[3] - 12.5 + 3.5, 0, -L60(dm)), (xA[4] + 12.5 - 3.5, 0, -L60(dm)))
        fam(f'{cid}-sup', 'CF 25/40', 12, None, polis=[barra_L(ejeB, cB, k, tA, tB, -15, *ext(12)) for k in (-9, 0, 9)], d=f'3ø12 superiores del {cid}, anclados 60ø en los dos extremos')
        fam(f'{cid}-med', 'CF 25/40', 10, None, polis=[barra_L(ejeB, cB, k, tA, tB, -30, *ext(10)) for k in (-9, 9)], d=f'2ø10 medios del {cid}, anclados 60ø')
        fam(f'{cid}-inf', 'CF 25/40', 12, None, polis=[barra_L(ejeB, cB, k, tA, tB, -45, *ext(12)) for k in (-9, 0, 9)], d=f'3ø12 inferiores del {cid}, anclados 60ø')
        fam(f'{cid}-est', 'CF 25/40', 10, [(x0 - px * 9, y0 - py * 9, -15), (x0 + px * 9, y0 + py * 9, -15), (x0 + px * 9, y0 + py * 9, -45), (x0 - px * 9, y0 - py * 9, -45), (x0 - px * 9, y0 - py * 9, -15)],
            n=int(ln // 25) + 1, paso=(ux * 25, uy * 25, 0), d=f'estribos ø10@25 del {cid}')
    # anclajes de las placas base: 1+1 ø3/4 de 43 + gancho 10, con estribos ø8@20
    polisA, polisE = [], []
    h, g_, L_ = ANCLAJE['sep'] / 2, ANCLAJE['gancho'], ANCLAJE['largo']
    for pl in placas:
        x, y = pl['centro'][0] - c['ox'], pl['centro'][1] - c['oy']
        # dos horquillas en U (1+1), una por sentido, colgadas de la placa; los ganchos de 100 doblan hacia adentro, uno frente al otro
        # (así lo dibuja el detalle: el ancho total es 140 y cabe en el muro de 25)
        polisA.append([(x - h + g_, y, -L_), (x - h, y, -L_), (x - h, y, -1), (x + h, y, -1), (x + h, y, -L_), (x + h - g_, y, -L_)])
        polisA.append([(x, y - h + g_, -L_), (x, y - h, -L_), (x, y - h, -1), (x, y + h, -1), (x, y + h, -L_), (x, y + h - g_, -L_)])
        for zz in (-12, -32):
            polisE.append([(x - 7, y - 7, zz), (x + 7, y - 7, zz), (x + 7, y + 7, zz), (x - 7, y + 7, zz), (x - 7, y - 7, zz)])
    fam('AN', 'placa base PLb', 19, None, polis=polisA, d='anclajes 1+1 ø3/4" en horquilla (L=1200 mm: 140 bajo la placa, ramas de 430 y ganchos de 100 hacia adentro) de las placas base, en los 22 pilares')
    fam('AE', 'placa base PLb', 8, None, polis=polisE, d='estribos ø8@20 de los anclajes')

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
        dict(elemento='Muros del búnker e=25 (DM)', m3=round(vol(muros['piezas'], z_losa_inf - z_zap_sup), 2), hormigon='G25'),
        dict(elemento='Losa del búnker e=20', m3=round((area(losa['pts']) - area(losa['hueco'])) * LOSA / 1e6, 2), hormigon='G25'),
        dict(elemento='VHA 25/40 (bajo la losa)', m3=round(sum(area(v['pts']) for v in vigas) * (VHA[1] - LOSA) / 1e6, 2), hormigon='G25'),
        dict(elemento='Zapata corrida del búnker 100 × 30', m3=round(vol(zap_piezas, ZAPATA_B[1]), 2), hormigon='G25'),
        dict(elemento='Radier del búnker e=10', m3=round(vol([piso], RADIER_BUNKER), 2), hormigon='G25'),
        dict(elemento='Sobrecimiento 25 × 50', m3=round(vol(sc_piezas, SOBRECIM[1]), 2), hormigon='G25'),
        dict(elemento='Cimiento corrido 80 × 25', m3=round(vol(ci_piezas, CIMIENTO[1]), 2), hormigon='G25'),
        dict(elemento='CF 25/40', m3=round(vol(cf_piezas, CF[1]), 2), hormigon='G25'),
        dict(elemento='Radier del estudio e=10', m3=round(vol(radier_estudio['capas'][0]['piezas'], RADIER_EST), 2), hormigon='G25'),
        dict(elemento='Escalera de hormigón y su caja de muros', m3=round(v_esc + v_caja, 2), hormigon='G25'),
        dict(elemento='Emplantillados (zapata del búnker, cimientos y CF)', m3=round(vol(zap_piezas, EMPLANTILLADO) + vol(cemp_piezas, EMPLANTILLADO) + vol(cf['emplantillado']['piezas'], EMPLANTILLADO), 2), hormigon='G5'),
    ]
    cub_f = {}
    for f in fierros: cub_f[f['diam']] = cub_f.get(f['diam'], 0) + f['largo']
    cub_fierro = [dict(diam=d, nombre=('ø3/4"' if d == 19 else f'ø{d}'), metros=round(cub_f[d] / 100, 1), kg=round(cub_f[d] / 100 * KGM[d])) for d in sorted(cub_f)]
    cubicacion = dict(hormigon=cub_h, total_m3=round(sum(x['m3'] for x in cub_h), 2), fierro=cub_fierro, total_kg=round(sum(x['kg'] for x in cub_fierro)),
                      nota='volúmenes del modelo (sin pérdidas ni traslapos); fierro por largo de barras del modelo, sin traslapos ni ganchos adicionales')
    return hormigon, fierros, cubicacion

def _largo(pl):
    return sum(math.dist(pl[i], pl[i + 1]) for i in range(len(pl) - 1))
