# -*- coding: utf-8 -*-
"""Escribe estructura.js (formato que lee 3d.html) a partir de un modelo JSON:
{"miembros": [{"id","clase","perfil","a":[x,y,z],"b":[x,y,z],"alma"?: "X"|"Y","donde"?: str}],
 "techo"?: {"x0","x1","y0","y1","z0","z1"}}
Uso: python3 generar_estructura_js.py modelo.json salida.js
"""
import sys, json, math
import numpy as np

PERFILES = {  # cm (secciones de los detalles de las laminas del ingeniero)
    'HEB 160': dict(forma='I', h=16, b=16, tf=1.3, tw=0.8),
    'IPE 220': dict(forma='I', h=22, b=11, tf=0.92, tw=0.59),
    'IPE 270': dict(forma='I', h=27, b=13.5, tf=1.0, tw=0.7),
    'IPE 300': dict(forma='I', h=30, b=15, tf=1.07, tw=0.71),
    'IPE 360': dict(forma='I', h=36, b=17, tf=1.27, tw=0.8),
    'IPE 400': dict(forma='I', h=40, b=18, tf=1.35, tw=0.86),
    'IPE 450': dict(forma='I', h=45, b=19, tf=1.5, tw=0.9),
    'IPE 500': dict(forma='I', h=50, b=20, tf=1.6, tw=1.02),
    'IPE 600': dict(forma='I', h=60, b=22, tf=1.9, tw=1.2),
    'CUAD 150x150x2': dict(forma='tubo_rect', h=15, b=15, t=0.2),
    'CUAD 150x150x3': dict(forma='tubo_rect', h=15, b=15, t=0.3),
    'CUAD 150x150x4': dict(forma='tubo_rect', h=15, b=15, t=0.4),
    'RECT 200x150x3': dict(forma='tubo_rect', h=20, b=15, t=0.3),
    'CANERIA 310': dict(forma='tubo_circ', d=31, t=0.6),
    'C 150x50x3': dict(forma='C', h=15, b=5, t=0.3),
    'CA 200x50x15x3': dict(forma='CA', h=20, b=5, c=1.5, t=0.3),
    'FE 22': dict(forma='barra', d=2.2),
    'FE 12': dict(forma='barra', d=1.2),
    'desconocido': dict(forma='tubo_rect', h=10, b=10, t=1.0),
}

def techo_desde_cabios(miembros):
    ys, zs, xs = [], [], []
    for m in miembros:
        if m['perfil'] == 'IPE 400':
            for p in (m['a'], m['b']):
                ys.append(p[1]); zs.append(p[2]); xs.append(p[0])
    if len(ys) < 2:
        return dict(x0=-110, x1=1890, y0=-100, y1=2280, z0=700, z1=780)
    a, b = np.polyfit(ys, zs, 1)
    y0, y1 = min(ys), max(ys)
    sobre = 20 + 20  # medio IPE 400 + costanera CA 200
    return dict(x0=round(min(xs) - 110, 1), x1=round(max(xs) + 110, 1), y0=round(y0, 1), y1=round(y1, 1),
                z0=round(a * y0 + b + sobre, 1), z1=round(a * y1 + b + sobre, 1))

def main(entrada, salida):
    mod = json.load(open(entrada))
    ms = []
    for m in mod['miembros']:
        p = m.get('perfil') if m.get('perfil') in PERFILES else 'desconocido'
        r = dict(id=m['id'], c=m.get('clase', 'otro'), p=p, a=[round(v, 1) for v in m['a']], b=[round(v, 1) for v in m['b']])
        if m.get('alma') in ('X', 'Y'): r['alma'] = m['alma']
        if m.get('donde'): r['d'] = m['donde']
        ms.append(r)
    techo = mod.get('techo') or techo_desde_cabios(mod['miembros'])
    if 'contorno' in techo and 'z_en_y' in techo:
        (y0, z0), (y1, z1) = techo['z_en_y'][0], techo['z_en_y'][-1]
        xs = [p[0] for p in techo['contorno']]
        techo = dict(contorno=[[round(x, 1), round(y, 1)] for x, y in techo['contorno']],
                     x0=min(xs), x1=max(xs), y0=y0, y1=y1, z0=z0, z1=z1)
    techo = {k: (round(float(v), 1) if isinstance(v, (int, float)) else v) for k, v in techo.items()}
    usados = sorted(set(r['p'] for r in ms) | {'desconocido'})
    out = dict(fuente=mod.get('fuente', ''), perfiles={k: PERFILES[k] for k in usados}, techo=techo, miembros=ms)
    js = 'const DATA_ESTRUCTURA = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n'
    open(salida, 'w').write(js)
    print(salida, len(js), 'bytes,', len(ms), 'miembros; techo', techo)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
