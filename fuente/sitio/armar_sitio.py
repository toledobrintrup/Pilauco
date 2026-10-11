# -*- coding: utf-8 -*-
"""Arma sitio.json a partir de las extracciones de datos/ (lote, gimnasio, estudio_arq, urbanismo_L1, dron,
topografia) y de estudio.json. Decide el anclaje del estudio: el búnker centrado en la excavación actual
(foto de dron); si no hay foto, la esquina NO del edificio B del arquitecto.

    python3 armar_sitio.py datos/ estudio.json sitio.json
"""
import json, os, sys, math

def carga(d, nombre):
    p = os.path.join(d, nombre)
    return json.load(open(p)) if os.path.exists(p) else None

def centroide(pts):
    a = cx = cy = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % len(pts)]
        f = x0 * y1 - x1 * y0; a += f; cx += (x0 + x1) * f; cy += (y0 + y1) * f
    if abs(a) < 1e-9: return [sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)]
    return [cx / (3 * a), cy / (3 * a)]

def r1(v): return round(float(v), 1)
def poli(pts): return [[r1(x), r1(y)] for x, y in pts]

def main(d, estudio_json, salida):
    E = json.load(open(estudio_json))
    L = carga(d, 'lote.json'); G = carga(d, 'gimnasio.json'); A = carga(d, 'estudio_arq.json')
    U = carga(d, 'urbanismo_L1.json'); DR = carga(d, 'dron.json'); TP = carga(d, 'topografia.json')
    notas = []
    S = dict(fuente='L1 EMPLAZAMIENTO 29-12-2025 (lote, cierros, acceso, edificio B, estacionamiento H, senderos), L11.GIM (gimnasio), '
                    'planta del estudio de Gabriel (2026-10-11), foto de dron de octubre 2026 (piscina, excavación, senderos reales); '
                    'topografía (26 puntos, enero 2026)')
    # ---------- terreno ----------
    S['terreno'] = dict(z=-70.0, dato='L1 rotula NPT +0,70 en la casa y ±0,00 en el acceso y junto al gimnasio: el terreno se toma plano en Z = -70 cm. '
                        'La topografía (26 puntos) confirma que es casi plano: 0,9 m de diferencia en 90 m, con la casa en lo más alto.')
    if TP and TP.get('terreno'):
        t = TP['terreno']; S['terreno']['topografia'] = dict(rango_m=t.get('rango_m'), media_m=t.get('media_m'), plano=t.get('plano_ajustado'), conclusion=t.get('conclusion'))
    # ---------- lote, cierros, acceso ----------
    lo = L['lote']
    S['lote'] = dict(poligono=poli(lo['poligono']), rol='12225-303',
                     deslindes={k: v['rotulado_cm'] for k, v in lo['deslindes'].items()},
                     deslindes_medidos={k: v['medido_cm'] for k, v in lo['deslindes'].items()},
                     area_rotulada_m2=lo['area_rotulada_m2'],
                     dato='Polígono del emplazamiento (trazo del lote): los 4 deslindes calzan con lo rotulado a 1 cm (el sur a 10 cm). ' + lo['nota_area'])
    notas.append('Lote: ' + lo['nota_area'])
    sv = L['servidumbre']; ci = sv['cierro_interior']; ac = sv['acceso']
    cierros = []
    for k in ('tramo_oeste', 'tramo_este'):
        tr = ci[k]
        cierros.append(dict(id='cierro_' + k.split('_')[1], tipo='cierro', pts=poli(tr['eje']), ancho=ci['ancho_cm'], desde=tr['desde'], hasta=tr['hasta'],
                            dato='LINEA CIERRO SERVIDUMBRE del emplazamiento: cierro a 5 m del deslinde sur, pilares de 50 x 70 cada 2,5 m; los extremos se curvan hacia el acceso'))
    S['cierros'] = cierros
    S['pilares_cierro'] = [dict(c=poli([p['c']])[0], ang=p['ang'], lado=p['lado_cm']) for p in ci['pilares']]
    S['deslinde_cierro'] = dict(dato='Los otros tres deslindes se dibujan con el cierro real de la foto: pilares de hormigón con reja. En el plano solo está el del sur.')
    S['acceso'] = dict(linea_y=ac['linea_acceso_y_cm'],
                       pilar_oeste=ac['pilar_oeste']['rect'], pilar_este=ac['pilar_este']['rect'], poste=ac['poste_intermedio']['rect'],
                       puerta=dict(vano=ac['puerta_peatonal']['vano'], ancho=ac['puerta_peatonal']['ancho_cm']),
                       porton=dict(vano=ac['porton']['vano'], ancho=ac['porton']['ancho_cm'], tipo=ac['porton']['tipo'], hoja_abierta=ac['porton']['hoja_abierta']),
                       dato='Acceso del emplazamiento: pilar 132 | puerta peatonal 98 | poste 20 | portón corredera 500 | pilar 100 (cotas de la lámina, medidas a 1 cm)')
    S['servidumbre'] = dict(eje=[sv['eje']['desde'], sv['eje']['hasta']], cierro_exterior=[sv['cierro_exterior']['desde'], sv['cierro_exterior']['hasta']],
                            dato='El eje de la servidumbre coincide con el deslinde sur; el cierro exterior dibujado queda unos 5 m al sur (otro borde de la servidumbre, supuesto)')
    # ---------- gimnasio ----------
    if G:
        al = G['alturas_cm_sobre_NPT']; cu = G['cubierta']; z_piso = -60.0
        pend = cu['pendiente']['tangente']; yN = G['caras_cm']['norte']
        cont_cub = cu['contorno_cm']; ys = [p[1] for p in cont_cub]
        y0, y1 = min(ys), max(ys)
        S['gimnasio'] = dict(
            z_piso=z_piso, planta=poli(G['contorno_planta_cm']), planta_y0=G['caras_cm']['norte'], planta_y1=G['caras_cm']['sur'],
            ancho=r1(G['caras_cm']['este'] - G['caras_cm']['oeste']), largo=r1(G['caras_cm']['sur'] - G['caras_cm']['norte']), muro=G['caras_cm']['espesor_muros'],
            ejes=G['ejes_cm'],
            alturas=dict(cielo_norte=al['cielo_NCT1']['cara_norte_C2'], cielo_sur=al['cielo_NCT1']['cara_sur_A2'],
                         cubierta_norte=al['cubierta_superior']['punta_alero_norte'], cubierta_sur=al['cubierta_superior']['punta_alero_sur'], ntn=al['NTN']),
            cubierta=dict(contorno=poli(cont_cub), espesor=cu['espesor_banda_cm'], y0=r1(y0), y1=r1(y1),
                          z_inf_norte=r1(al['cielo_NCT1']['cara_norte_C2'] + pend * (y0 - yN) ),
                          z_inf_sur=r1(al['cielo_NCT1']['cara_norte_C2'] + pend * (y1 - yN)),
                          pendiente=pend, aleros=cu['aleros_cm']),
            deslindes=dict(norte=G['deslindes']['norte']['rotulado_L11_cm'], oeste=G['deslindes']['oeste']['rotulado_L11_cm'], este=G['deslindes']['este']['rotulado_L11_cm']),
            dato='Forma y alturas de la lámina L11 (902 x 700 en L, cielo +297 a +324, cubierta 981 x 1.185 con 4,44 m de alero al sur); posición de L1 (calza con L11 a 1-8 cm en los deslindes norte y oeste; en el este L11 dice 23,77 y el plano da 23,97). '
                 'Piso 60 cm bajo el de la casa: L1 rotula NPT +0,10 en el gimnasio y +0,70 en la casa (supuesto que comparten datum).')
        for dd in G.get('dudas', []): notas.append('Gimnasio: ' + dd)
    # ---------- estudio del arquitecto, estacionamiento, accesos ----------
    if A:
        B = A['edificio_B']; H = A['estacionamiento_H']
        S['estudio_arq'] = dict(pts=poli(B['contorno_exterior']), ancho=B['ancho_cm'], largo=B['largo_cm'], area_m2=B['area_m2'],
                                dato='Edificio B del emplazamiento (29-12-2025): estudio, acceso estudio, 2 habitaciones y escalera; 167,32 m² según su cuadro. Se reemplaza por la planta de Gabriel, centrada en la excavación')
        S['estacionamiento'] = dict(planta=poli(H['cubierta_dibujada']['pts']), cuadro=poli(H['cuadro']['pts']), bahias=H['cubierta_dibujada'].get('bahias'),
                                    dato='Estacionamiento H del emplazamiento: cobertizo de 3 bahías de 2,50 m (cotas 250|10|250|10|250) entre la casa y el estudio, 49,27 m² al 50 % en el cuadro; futuro')
        S['accesos_arq'] = dict(G=poli(A['acceso_G']['pts']), D=poli(A['acceso_cubierto_D']['pts']))
        rs = A['radier_y_sendero']
        S['radier_arq'] = dict(linea=poli(rs['linea_radier']['pts']), contorno=poli(rs['contorno_radier']['pts']), dato='Linea Radier del emplazamiento')
    # ---------- urbanismo del plano del arquitecto ----------
    urb = dict(grava=[], radier=[], senderos=[], soleras=[], contornos=[])
    if U:
        el = {e['id']: e for e in U['elementos']}
        def pl(e): return e.get('poligono') or e.get('polilinea') or e.get('pts')
        if 'calzada_grava' in el: urb['grava'].append(dict(nombre='Calzada de grava', pts=poli(el['calzada_grava']['poligono']), dato='GRAVA entre las soleras divisorias, del acceso a la Linea Radier (contorno supuesto por el agente: el plano solo rotula)'))
        for k, nombre in (('explanada_U', 'Explanada en U (plano)'), ('patio_norte_U', 'Patio norte (plano)'), ('acceso_sur_explanada', 'Explanada de acceso sur (plano)')):
            if k in el and pl(el[k]): urb['contornos'].append(dict(nombre=nombre, pts=poli(pl(el[k])), dato=el[k].get('nota', '')[:200]))
        for k in ('solera_oeste', 'solera_este'):
            if k in el and el[k].get('eje'): urb['soleras'].append(dict(nombre='Solera divisoria', pts=poli(el[k]['eje']), dato='SOLERAS DIVISORIAS del emplazamiento'))
        if 'linea_radier' in el: urb['soleras'].append(dict(nombre='Línea radier', pts=poli(el['linea_radier']['polilinea']), dato='Linea Radier del emplazamiento'))
    S['urbanismo'] = urb
    # ---------- lo real (foto de dron), remapeado con la homografía correcta ----------
    # El agente del dron tomó el cierro sur (5 m adentro del lote) como deslinde sur: su homografía estira la foto.
    # Se deshace con la inversa de su matriz y se vuelve a proyectar con las 4 esquinas del cierro real.
    real = {}
    if DR:
        import numpy as np
        Hw = np.array(DR['homografia_px_a_cm']); Hwi = np.linalg.inv(Hw)
        px = DR['esquinas_lote_px']; ci = L['servidumbre']['cierro_interior']
        ok = {'NO': L['lote']['esquinas']['NO'], 'NE': L['lote']['esquinas']['NE'], 'SO': ci['tramo_oeste']['eje'][0], 'SE': ci['tramo_este']['eje'][-1]}
        def dlt(src, dst):
            M = []
            for (x, y), (u, v) in zip(src, dst):
                M.append([-x, -y, -1, 0, 0, 0, u * x, u * y, u]); M.append([0, 0, 0, -x, -y, -1, v * x, v * y, v])
            _, _, Vt = np.linalg.svd(np.array(M, float)); h = Vt[-1]; return (h / h[-1]).reshape(3, 3)
        ks = ['NO', 'NE', 'SE', 'SO']; Hr = dlt([px[k] for k in ks], [ok[k] for k in ks]); Hfix = Hr @ Hwi
        def re(p):
            v = Hfix @ np.array([p[0], p[1], 1.0]); return [r1(v[0] / v[2]), r1(v[1] / v[2])]
        def re_pts(pts): return [re(p) for p in pts]
        E_ = DR['elementos']
        def rect_pts(e): return re_pts(e.get('interior') or e.get('pts'))
        real['piscina'] = dict(pts=rect_pts(E_['piscina']), borde=re_pts(E_['piscina']['borde_exterior']), dato='Piscina de hormigón, interior 7,8 × 5,2 m (foto de dron, ±25 cm); con agua en el video de agosto')
        real['piscina_chica'] = dict(pts=rect_pts(E_['cuadrado_chico']), borde=re_pts(E_['cuadrado_chico']['borde_exterior']), dato='Cuadrado de 3,1 × 3,2 m junto a la piscina (jacuzzi, según el video)')
        real['excavacion'] = dict(pts=re_pts(E_['laguna']['pts']), area_m2=E_['laguna']['area_m2'], dato='Excavación del búnker, con agua en la foto de octubre (Gabriel: "la laguna verde es la excavación donde va el búnker")')
        real['senderos'] = [dict(nombre='Explanada de hormigón', pts=re_pts(E_['explanada_hormigon']['pts']), dato='Sendero en U + patio + terraza de la piscina, hormigón visible en la foto (±50 cm; el tramo bajo la lona es supuesto)')]
        real['radieres'] = [dict(nombre='Radier junto al gimnasio', pts=re_pts(E_['radier_grande']['pts']), dato='Radier de hormigón de 17,3 × 12,0 m al oriente del gimnasio (foto, ±30 cm)'),
                            dict(nombre='Explanada del gimnasio', pts=re_pts(E_['apron_gimnasio']['pts']), dato='Hormigón al sur del techo del gimnasio (foto)')]
        g = E_['galpon_obra']
        real['galpon'] = dict(nombre='Galpón de obra', pts=re_pts(g['techo_blanco']), alto=320, dato='Instalación de faena (provisoria), techo blanco; medido en la foto ±60 cm')
        real['otros'] = [dict(nombre='Galpón de obra (ala oeste)', pts=re_pts(g['techo_oscuro_oeste']), alto=280, dato='techo oscuro, provisorio'),
                         dict(nombre='Galpón de obra (ala este)', pts=re_pts(g['techo_oscuro_este']), alto=280, dato='techo oscuro, provisorio')]
        pz = E_['pozo_anillo']; c = re(pz['centro']); rr = pz['r_exterior']
        real['otros'].append(dict(nombre='Pozo (anillo de hormigón)', pts=[[r1(c[0] + rr * math.cos(t)), r1(c[1] + rr * math.sin(t))] for t in [i * 2 * math.pi / 24 for i in range(24)]], alto=40, dato='Anillo de hormigón de Ø4 m con hueco al centro (foto); uso supuesto'))
        real['otros'].append(dict(nombre='Estanque / cámara', pts=rect_pts(E_['estanque_cuadrado']), alto=20, dato='Cuadrado oscuro con marco de 1,8 m cerca del cierro oriente (foto); uso supuesto'))
        real['otros'].append(dict(nombre='Caseta de bombas', pts=re_pts(E_['caja_blanca_oeste']['pts']), alto=150, dato='Caja blanca de 2,5 × 2,25 m junto al cierro poniente (foto y video)'))
        real['nota_homografia'] = 'Foto rectificada con las 4 esquinas del cierro real (norte y laterales sobre el deslinde; sur sobre el cierro de servidumbre, 5 m adentro). Precisión ±30-50 cm.'
    S['real'] = real
    # ---------- anclaje del estudio: búnker centrado en la excavación ----------
    exc = None
    if isinstance(real, dict):
        for k in ('excavacion', 'excavacion_bunker', 'laguna', 'estanque'):
            if real.get(k) and real[k].get('pts'): exc = real[k]; break
    bk = E['bunker']['pts']; cb = centroide(bk)
    if exc:
        ce = centroide(exc['pts'])
        S['estudio_origen'] = [r1(ce[0] - cb[0]), r1(ce[1] - cb[1])]
        S['estudio_anclaje'] = dict(metodo='búnker centrado en la excavación actual (foto de dron de octubre 2026)', excavacion_centro=poli([ce])[0],
                                   dato='Gabriel (2026-10-11): "centremos el búnker donde está la excavación actual"; la excavación se digitalizó de la foto rectificada con las esquinas del lote (±30 cm)')
    else:
        S['estudio_origen'] = [3278.0, 84.0]
        S['estudio_anclaje'] = dict(metodo='esquina NO del edificio B del arquitecto (provisorio, hasta tener la excavación de la foto)')
    S['estudio_pendiente'] = 0.035
    notas.insert(0, 'Casa en el emplazamiento: el bloque de la vivienda está dibujado 3,28 m al sur de donde está construida (dx 0). '
                    'Se comprobó con los muros de L2 (correlación: dy = -328 cm), con las fundaciones de la ortofoto de topografía (ejes reales) y con la losa en la foto de dron. '
                    'El lote, los cierros, el acceso y el gimnasio del emplazamiento sí calzan con la realidad (cierro sur sobre sus postes a ±20 cm), así que el modelo usa esos; '
                    'el estacionamiento H, el acceso G y el edificio B del arquitecto se dibujan donde él los puso respecto del lote, y quedan 3,3 m más al sur de lo que él pensó respecto de la casa. Preguntar al arquitecto.')
    S['notas'] = notas
    json.dump(S, open(salida, 'w'), ensure_ascii=False, indent=1)
    print(f"{salida}: lote {len(S['lote']['poligono'])} vértices · cierros {len(S['cierros'])} · pilares {len(S['pilares_cierro'])} · gimnasio {'sí' if G else 'no'} · "
          f"estudio_arq {'sí' if A else 'no'} · urbanismo {'sí' if U else 'no'} · real {len(real) if isinstance(real, dict) else 0} · estudio en {S['estudio_origen']} ({S['estudio_anclaje']['metodo']})")

if __name__ == '__main__':
    main(*sys.argv[1:4])
