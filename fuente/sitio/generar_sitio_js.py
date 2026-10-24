# -*- coding: utf-8 -*-
"""Genera sitio.js (DATA_SITIO) a partir de sitio.json (terreno extraído del emplazamiento, la lámina del
gimnasio y la foto de dron) y estudio.json (la planta del estudio con búnker, de Gabriel).

    python3 generar_sitio_js.py sitio.json estudio.json ../../sitio.js

Todo en cm, en el marco de la app: X hacia el oriente (eje 6 de la casa), Y hacia el sur (eje A), Z hacia
arriba, con Z = 0 en el piso terminado del nivel 1 de la casa (NPT +0,70 del emplazamiento).
"""
import json, sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geom import offset_rect_poly

def r1(v): return round(float(v), 1)
def poli(pts): return [[r1(x), r1(y)] for x, y in pts]
def area(pts):
    return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))) / 2
def largo(pts, cerrado=False):
    idx = range(len(pts)) if cerrado else range(len(pts) - 1)
    return sum(math.hypot(pts[(i + 1) % len(pts)][0] - pts[i][0], pts[(i + 1) % len(pts)][1] - pts[i][1]) for i in idx)
def desplazar(pts, dx, dy): return [[r1(x + dx), r1(y + dy)] for x, y in pts]

def armar_estudio(E, origen, pendiente, sube_hacia):
    """Estudio en coordenadas absolutas: recintos, búnker, techo y alturas, a partir de la planta local."""
    ox, oy = origen
    ancho, largo_ = E['exterior']['ancho'], E['exterior']['largo']
    muro = E['muro']['espesor']
    T = float(E.get('tabique', {}).get('espesor', 0))   # tabique por dentro de los 4 muros del búnker: el búnker se mide entre tabiques
    ext = [[0, 0], [ancho, 0], [ancho, largo_], [0, largo_]]
    A = E['alturas']
    z0 = E['nivel_piso']['z_cm']
    # techo: 4,00 m de cielo en el lado bajo (norte) y sube con la pendiente de la casa hacia el sur (el cielo interior va plano, ver abajo)
    y_bajo = 0 if sube_hacia == 'sur' else largo_
    t_piso, t_cielo = A.get('terminacion_piso_cm', 0), A.get('terminacion_cielo_cm', 0)   # terminaciones (porcelanato / yeso cartón): la estructura va encima de los 4,00 libres
    z_est = z0 + A['interior_cm'] + t_piso + t_cielo                                    # cara inferior de la estructura (vigas E-O): 4,00 + 1,5 + 5,5 = +4,07
    def z_cielo(y_local): return z_est + pendiente * ((y_local - y_bajo) if sube_hacia == 'sur' else (y_bajo - y_local))
    # aleros medidos desde la cara exterior del muro (estudio.json); el contorno del volumen también parte de la cara exterior
    an, ae = A['alero_ns_cm'], A['alero_eo_cm']
    est = A.get('estructura_techo_cm', 0)   # vigas y costaneras entre el cielo y la plancha del techo
    techo = [[-ae, -an], [ancho + ae, -an], [ancho + ae, largo_ + an], [-ae, largo_ + an]]
    recintos = []
    for rc in E['recintos']:
        # arriba muros y tabiques de 25 terminado, sin tabique extra (Gabriel, 14-10-2026, opción 1): los recintos se miden entre caras de muro
        recintos.append(dict(id=rc['id'], nombre=rc['nombre'], tipo=rc['tipo'], pts=desplazar(rc['pts'], ox, oy),
                             area_m2=round(area(rc['pts']) / 1e4, 2), dato=rc.get('dato', ''),
                             **({'cielo_cm': rc['cielo_cm'], 'cielo_z': r1(z0 + t_piso + rc['cielo_cm'])} if rc.get('cielo_cm') else {})))   # cielo propio (la cabina baja a 3,35)
    B = E['bunker']
    z_losa = z0 - A['losa_piso_cm']           # cara inferior de la losa de piso del estudio = cielo del búnker
    h_bk = B['interior_cm'] + t_piso + t_cielo   # obra gruesa del búnker: 2,80 libres terminados + piso + cielo = 2,87
    bterm = offset_rect_poly(B['pts'], T) if T else B['pts']
    bunker = dict(nombre=B['nombre'], pts=desplazar(B['pts'], ox, oy), terminado=desplazar(bterm, ox, oy), z_cielo=r1(z_losa), z_piso=r1(z_losa - h_bk), npt=r1(z_losa - h_bk + t_piso), cielo_terminado=r1(z_losa - t_cielo),
                  interior_cm=B['interior_cm'], obra_gruesa_cm=r1(h_bk), area_m2=round(area(bterm) / 1e4, 2), area_og_m2=round(area(B['pts']) / 1e4, 2),
                  terminado_cm=dict(ancho=r1(bterm[1][0] - bterm[0][0]), largo=r1(bterm[2][1] - bterm[0][1])), dato=B['dato'])
    return dict(
        origen=[r1(ox), r1(oy)], exterior=desplazar(ext, ox, oy), ancho=ancho, largo=largo_, muro=muro,
        z_piso=r1(z0), recintos=recintos, bunker=bunker, tabique=dict(espesor=T, dato=E.get('tabique', {}).get('dato', '')),
        # cielo interior plano a 4,00 en todo el estudio (Gabriel, 13-10-2026: "el cielo completo terminado a 4 m, esa fue siempre la idea");
        # el techo sigue inclinado por encima, con la estructura en el entretecho
        cielo=dict(z_norte=r1(z0 + t_piso + A['interior_cm']), z_sur=r1(z0 + t_piso + A['interior_cm']), y_norte=r1(oy), y_sur=r1(oy + largo_),
                   dato='cielo terminado plano a 4,00 sobre el piso terminado, en todo el estudio (Gabriel, 13-10-2026); la estructura y el techo van encima'),
        npt=r1(z0 + t_piso), z_estructura=r1(z_est), terminaciones=dict(piso=t_piso, cielo=t_cielo, libre=A['interior_cm'], capas=A.get('capas', {}), dato=A.get('dato_terminaciones', '')),
        techo=dict(contorno=desplazar(techo, ox, oy), espesor=A['techo_espesor_cm'], alero=A['alero_ns_cm'], alero_ns=A['alero_ns_cm'], alero_eo=A['alero_eo_cm'], pendiente=pendiente, sube_hacia=sube_hacia,
                   y0=r1(oy - an), y1=r1(oy + largo_ + an),
                   z0=r1(z_cielo(-an) + est), z1=r1(z_cielo(largo_ + an) + est), estructura=est),
        datos=dict(exterior=E['exterior']['dato'], muro=E['muro']['dato'], interior=A['dato_interior'], losa=A['dato_losa'],
                   techo=E['techo']['dato'], estructura=A.get('dato_estructura_techo', ''), alero=A['dato_alero'], emplazamiento=E['emplazamiento']['dato'], nivel=E['nivel_piso']['dato']),
    )

# Qué NO va al 3D por ahora (Gabriel, 2026-10-12): el galpón de obra y el baño provisorio (caseta del lado
# poniente), el camino de grava y las líneas del plano en el piso (soleras, contornos, radier y el edificio B del
# arquitecto). Los datos siguen en sitio.json por si se vuelven a usar.
OCULTAR_REAL = {'galpon', 'excavacion'}   # la excavación del búnker tampoco se dibuja (Gabriel, 2026-10-12); sigue anclando el estudio
OCULTAR_OTROS = {'Galpón de obra (ala oeste)', 'Galpón de obra (ala este)', 'Caseta de bombas'}
OCULTAR_URBANISMO = {'grava', 'soleras', 'contornos', 'senderos', 'radier'}
OCULTAR_CLAVES = {'estudio_arq', 'radier_arq', 'accesos_arq', 'estacionamiento'}   # el estacionamiento futuro también fuera (2026-10-12)

def filtrar(S):
    real = {k: v for k, v in S.get('real', {}).items() if k not in OCULTAR_REAL}
    if 'otros' in real: real['otros'] = [x for x in real['otros'] if x.get('nombre') not in OCULTAR_OTROS]
    urb = {k: ([] if k in OCULTAR_URBANISMO else v) for k, v in S.get('urbanismo', {}).items()}
    return real, urb

def main(sitio_json, estudio_json, salida):
    S = json.load(open(sitio_json)); E = json.load(open(estudio_json))
    real_vis, urb_vis = filtrar(S)
    lote = S['lote']
    xs = [p[0] for p in lote['poligono']]; ys = [p[1] for p in lote['poligono']]
    out = dict(
        fuente=S.get('fuente', ''),
        terreno=dict(z=S['terreno']['z'], dato=S['terreno']['dato'], bbox=[r1(min(xs)), r1(min(ys)), r1(max(xs)), r1(max(ys))]),
        lote=dict(poligono=poli(lote['poligono']), superficie_m2=round(area(lote['poligono']) / 1e4, 1), perimetro_m=round(largo(lote['poligono'], True) / 100, 2),
                  deslindes=lote.get('deslindes', {}), rol=lote.get('rol', ''), dato=lote.get('dato', '')),
        cierros=[dict(id=c['id'], pts=poli(c['pts']), tipo=c.get('tipo', 'cierro'), ancho=c.get('ancho'), dato=c.get('dato', '')) for c in S.get('cierros', [])],
        pilares_cierro=S.get('pilares_cierro', []),
        acceso=S.get('acceso'),
        servidumbre=S.get('servidumbre'),
        gimnasio=S.get('gimnasio'),
        estudio=armar_estudio(E, S['estudio_origen'], S['estudio_pendiente'], E['techo']['sube_hacia']),
        estudio_anclaje=S.get('estudio_anclaje'),
        estacionamiento=None if 'estacionamiento' in OCULTAR_CLAVES else S.get('estacionamiento'),
        urbanismo=urb_vis,
        real=real_vis,
        notas=S.get('notas', []),
    )
    js = 'const DATA_SITIO = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n'
    open(salida, 'w').write(js)
    e = out['estudio']
    print(f"{salida} {len(js)} bytes · lote {out['lote']['superficie_m2']} m2 · estudio {e['ancho']/100:.2f} x {e['largo']/100:.2f} m en {e['origen']} · búnker {e['bunker']['area_m2']} m2 "
          f"· gimnasio {'sí' if out['gimnasio'] else 'no'} · cierros {len(out['cierros'])} · urbanismo {sum(len(v) for v in out['urbanismo'].values() if isinstance(v, list))} · real {len(out['real'])}")

if __name__ == '__main__':
    main(*sys.argv[1:4])
