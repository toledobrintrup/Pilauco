# -*- coding: utf-8 -*-
"""Helpers compartidos para reprocesar la estructura de Casa Pilauco desde los PDF.

TODAS las coordenadas que devuelven estas funciones estan en el sistema "rotado" (el
que se ve en pantalla): punto_rotado = punto_pdf * page.rotation_matrix. Las laminas de
estructura vienen con rotation=270; si no se aplica la matriz, todo sale girado.
render() recorta usando esas mismas coordenadas rotadas: pixel = (pt - clip.x0/y0) * escala.
"""
import fitz, json, os, math
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
ING = '/Users/gabrieltoledobrintrup/Library/Mobile Documents/com~apple~CloudDocs/04_Negocios/N03_Inversión Inmobiliaria/06_Casa Pilauco/02_Ingeniería/'
ARQ = '/Users/gabrieltoledobrintrup/Library/Mobile Documents/com~apple~CloudDocs/04_Negocios/N03_Inversión Inmobiliaria/06_Casa Pilauco/01_Arquitectura/01_Planos/'

LAMINAS = {
    'eje2':       ING + '04_Estructura/Elevación Eje 2.pdf',        # ELEVACION EJE 1, EJE 2
    'eje5':       ING + '04_Estructura/Elevación Eje 5.pdf',        # EJE 3, 5, 6, 1a', K
    'ejeA':       ING + '04_Estructura/Elevación Eje A.pdf',        # EJE A, A1, D, H, I, 1a', G3, J
    'otras':      ING + '04_Estructura/Otras Elevaciones.pdf',      # EJE A3, B, C, F, E, E4, F1, F2, G, G2
    'techumbre':  ING + '04_Estructura/Estructura Techumbre.pdf',   # PLANTA ESTRUCTURA TECHUMBRE
    'nivel1':     ING + '01_Fundaciones Casa Pilauco/Planta Estructura Nivel 1.pdf',  # rev. 08-04-2026, cotas y perfiles como TEXTO
    'nivel2':     ING + '01_Fundaciones Casa Pilauco/Plata Estructura Nivel 2.pdf',
    'fundaciones':ING + '01_Fundaciones Casa Pilauco/Planta Fundaciones.pdf',
    'det_fund1':  ING + '01_Fundaciones Casa Pilauco/Detalle Fundaciones 1.pdf',
    'det_fund2':  ING + '01_Fundaciones Casa Pilauco/Detalle Fundaciones 2.pdf',
}
ARQUITECTURA = {
    # sistema de coordenadas DE LA APP (data.js): cm = (pt - origen) / S, mismo S en x e y.
    'arq_n2': dict(pdf=ARQ + 'L3.PLARQ2.29.12.2025.pdf', X0=302.23, Y0=717.19, S=(1317.24 - 302.23) / 1790.0),
    'arq_n1': dict(pdf=ARQ + 'L2.PLARQ.29.12.2025.pdf',  X0=326.70, Y0=733.46, S=(1317.24 - 302.23) / 1790.0),
}

_cache = {}
def abrir(clave):
    if clave not in _cache:
        ruta = LAMINAS[clave] if clave in LAMINAS else ARQUITECTURA[clave]['pdf']
        d = fitz.open(ruta); pg = d[0]
        _cache[clave] = (d, pg, pg.rotation_matrix)
    return _cache[clave]

def palabras(clave):
    """[(x0,y0,x1,y1,texto)] en coordenadas rotadas (rect normalizado)."""
    _, pg, M = abrir(clave)
    out = []
    for w in pg.get_text('words'):
        r = fitz.Rect(w[:4]) * M
        r.normalize()
        out.append((r.x0, r.y0, r.x1, r.y1, w[4]))
    return out

def trazos(clave, clip=None):
    """Segmentos rectos de TODOS los dibujos, en coordenadas rotadas:
    dict(x0,y0,x1,y1,ancho,color,relleno,tipo,grupo). Las curvas 'c' se aproximan por su cuerda;
    los 're'/'qu' se devuelven como sus 4 lados con tipo='re'/'qu'."""
    _, pg, M = abrir(clave)
    out = []
    for gi, g in enumerate(pg.get_drawings()):
        w = g.get('width') or 0.0
        col = tuple(round(c, 3) for c in (g.get('color') or ()))
        fill = tuple(round(c, 3) for c in (g.get('fill') or ())) if g.get('fill') else None
        for it in g['items']:
            t = it[0]
            if t == 'l':
                segs = [(it[1], it[2])]
            elif t == 'c':
                segs = [(it[1], it[4])]
            elif t == 're':
                r = it[1]; segs = [(r.tl, r.tr), (r.tr, r.br), (r.br, r.bl), (r.bl, r.tl)]
            elif t == 'qu':
                q = it[1]; segs = [(q.ul, q.ur), (q.ur, q.lr), (q.lr, q.ll), (q.ll, q.ul)]
            else:
                continue
            for a, b in segs:
                p0 = fitz.Point(a) * M; p1 = fitz.Point(b) * M
                if clip is not None:
                    x0c, y0c, x1c, y1c = clip
                    if not (x0c <= p0.x <= x1c and y0c <= p0.y <= y1c and x0c <= p1.x <= x1c and y0c <= p1.y <= y1c):
                        continue
                out.append(dict(x0=p0.x, y0=p0.y, x1=p1.x, y1=p1.y, ancho=round(w, 3), color=col,
                                relleno=fill, tipo=t, grupo=gi))
    return out

def render(clave, ruta_png, clip=None, escala=2.0):
    """Renderiza (zona de) la lamina tal como se ve. clip=(x0,y0,x1,y1) en coords rotadas.
    Devuelve f(pt_x, pt_y) -> (px, py) para dibujar encima."""
    _, pg, _ = abrir(clave)
    if clip is None:
        clip = (0, 0, pg.rect.width, pg.rect.height)
    pix = pg.get_pixmap(matrix=fitz.Matrix(escala, escala), clip=fitz.Rect(*clip))
    pix.save(ruta_png)
    cx, cy = clip[0], clip[1]
    return lambda x, y: ((x - cx) * escala, (y - cy) * escala)

def theil_sen(xs, ys):
    """Ajuste robusto y = a*x + b (mediana de pendientes por pares). Devuelve a, b, residuales."""
    xs = np.asarray(xs, float); ys = np.asarray(ys, float)
    pend = [(ys[j]-ys[i])/(xs[j]-xs[i]) for i in range(len(xs)) for j in range(i+1, len(xs)) if xs[j] != xs[i]]
    a = float(np.median(pend)); b = float(np.median(ys - a*xs))
    return a, b, (a*xs + b - ys)

def guardar_json(nombre, obj):
    with open(os.path.join(AQUI, nombre), 'w') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)

def leer_json(nombre):
    ruta = os.path.join(AQUI, nombre)
    if not os.path.exists(ruta):
        ruta = os.path.join(AQUI, '..', 'datos', nombre)
    with open(ruta) as f:
        return json.load(f)

# Estimaciones PREVIAS (de una sesion anterior), NO verificadas a fondo: sirven de punto de
# partida y de chequeo cruzado, nunca de verdad. Sistema de la app (cm).
ESTIMACION_PREVIA_LETRAS = {'A': 2170.0, 'B': 1694.7, 'C': 1511.8, 'D': 1104.1, 'E': 958.5, 'F': 625.3,
                            'G': 341.4, 'H': 7.2, 'I': -169.8, 'J': -470.7, 'K': -764.7}
ESTIMACION_PREVIA_NUMEROS = {'1': 6.8, '2': 652.8, '3': 1007.4, '4': 1257.3, '5': 1783.6, '6': 2183.0}

# Lista de materiales del ingeniero ("Cubicacion casa sin anclajes"): largo TOTAL por perfil, en m.
CUBICACION_M = {
    'C 150x50x3': 56.20, 'CANERIA 310 e=6': 17.00, 'CUAD 150x150x2': 63.39, 'CUAD 150x150x3': 138.70,
    'CUAD 150x150x4': 208.38, 'FE 22': 159.97, 'HEB 160': 3.77 + 95.20, 'IPE 220': 67.75, 'IPE 270': 29.98,
    'IPE 300': 94.28, 'IPE 360': 23.31, 'IPE 400': 81.79, 'IPE 450': 35.57, 'IPE 500': 18.12,
    'IPE 600': 20.70, 'RECT 200x150x3': 112.90, 'CA 200x50x15x3 (costanera)': 760.00, 'FE 12 (colgador)': 177.00,
}
