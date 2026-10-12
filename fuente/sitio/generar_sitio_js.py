# -*- coding: utf-8 -*-
"""Genera sitio.js (DATA_SITIO) a partir de sitio.json (terreno extraído del emplazamiento, la lámina del
gimnasio y la foto de dron) y estudio.json (la planta del estudio con búnker, de Gabriel).

    python3 generar_sitio_js.py sitio.json estudio.json ../../sitio.js

Todo en cm, en el marco de la app: X hacia el oriente (eje 6 de la casa), Y hacia el sur (eje A), Z hacia
arriba, con Z = 0 en el piso terminado del nivel 1 de la casa (NPT +0,70 del emplazamiento).
"""
import json, sys, math

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
    ext = [[0, 0], [ancho, 0], [ancho, largo_], [0, largo_]]
    A = E['alturas']
    z0 = E['nivel_piso']['z_cm']
    # cielo interior: 4,00 m en el lado bajo (norte) y sube con la pendiente de la casa hacia el sur
    y_bajo = 0 if sube_hacia == 'sur' else largo_
    def z_cielo(y_local): return z0 + A['interior_cm'] + pendiente * abs(y_local - y_bajo)
    alero = A['alero_cm']
    techo = [[-alero, -alero], [ancho + alero, -alero], [ancho + alero, largo_ + alero], [-alero, largo_ + alero]]
    recintos = []
    for rc in E['recintos']:
        recintos.append(dict(id=rc['id'], nombre=rc['nombre'], tipo=rc['tipo'], pts=desplazar(rc['pts'], ox, oy),
                             area_m2=round(area(rc['pts']) / 1e4, 2), dato=rc.get('dato', '')))
    B = E['bunker']
    z_losa = z0 - A['losa_piso_cm']           # cara inferior de la losa de piso del estudio = cielo del búnker
    bunker = dict(nombre=B['nombre'], pts=desplazar(B['pts'], ox, oy), z_cielo=r1(z_losa), z_piso=r1(z_losa - B['interior_cm']),
                  interior_cm=B['interior_cm'], area_m2=round(area(B['pts']) / 1e4, 2), dato=B['dato'])
    return dict(
        origen=[r1(ox), r1(oy)], exterior=desplazar(ext, ox, oy), ancho=ancho, largo=largo_, muro=muro,
        z_piso=r1(z0), recintos=recintos, bunker=bunker,
        cielo=dict(z_norte=r1(z_cielo(0)), z_sur=r1(z_cielo(largo_)), y_norte=r1(oy), y_sur=r1(oy + largo_),
                   dato='4,00 m interiores en el lado bajo; sube con la pendiente de la casa (supuesto el lado)'),
        techo=dict(contorno=desplazar(techo, ox, oy), espesor=A['techo_espesor_cm'], alero=alero, pendiente=pendiente, sube_hacia=sube_hacia,
                   y0=r1(oy - alero), y1=r1(oy + largo_ + alero),
                   z0=r1(z_cielo(-alero)), z1=r1(z_cielo(largo_ + alero))),
        datos=dict(exterior=E['exterior']['dato'], muro=E['muro']['dato'], interior=A['dato_interior'], losa=A['dato_losa'],
                   techo=E['techo']['dato'], alero=A['dato_alero'], emplazamiento=E['emplazamiento']['dato'], nivel=E['nivel_piso']['dato']),
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
