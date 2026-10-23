# -*- coding: utf-8 -*-
"""Escalera de obra de la bodega (Gabriel, 16-10-2026): geometría, planta y corte en SVG, dimensiones, despiece y lista de fierro para
comprar. Escribe escalera_dibujo.js (DATA_ESCALERA), que lee escalera.html. Misma geometría que grupoEscalera en 3d.html.
Uso: python3 fuente/casa/generar_escalera_js.py"""
import json, math, re, pathlib
raiz = pathlib.Path(__file__).resolve().parents[2]
E = json.loads(re.search(r'const DATA_ESTRUCTURA = (\{.*\});?\s*$', open(raiz / 'estructura.js', encoding='utf-8').read(), re.S).group(1))
PIL = [(m['id'].split('-')[1], m['a'][0], m['a'][1], m['p']) for m in E['miembros'] if m['c'] == 'pilar' and 1750 < m['a'][0] < 2220 and 300 < m['a'][1] < 1000 and m['a'][2] < 15]
# ---------- geometría (cm, marco de la app: x al oriente, y al sur; alturas sobre el piso terminado de la bodega) ----------
PISO_N1 = 380.0; HORM = 15.0; Z1 = PISO_N1 + HORM            # viga de entrepiso medida en terreno + hormigón de la losa = piso del nivel 2
X0, X1 = 1796.0, 1946.0                                       # pegada a la cara interior del muro de la casa (eje 5 en 1783,7), 1,50 de ancho
PL0, PL1 = 349.0, 499.0                                       # plataforma 1,5 × 1,5 contra el muro del eje G (334..349)
NH, H = 17, 24.0; YA = PL1 + NH * H                           # 17 huellas de 24: pie en y 907 (muro del eje E de la bodega en 940)
NC = 18; CH = Z1 / NC                                         # 18 contrahuellas de 21,9
ANG = math.degrees(math.atan2(Z1, NH * H)); LZ = math.hypot(NH * H, Z1)
ALA_TOP = 288.0; HUECO = [1790, PL0 - 6, 1952, YA + 6]        # cubierta baja del ala (vigas RECT 200×150 a +2,78) y su hueco provisorio
BAR = 100.0                                                   # baranda
fm = lambda v: f'{v / 100:.2f}'.replace('.', ',')
fm1 = lambda v: f'{v:.1f}'.replace('.', ',')
# ---------- despiece ----------
PERF = {   # kg/m o kg/m² (catálogos chilenos habituales; el proveedor confirma)
    'C 200×50×4': 9.0, 'C 150×50×3': 5.7, 'Tubo cuadrado 100×100×3': 9.0, 'Tubo cuadrado 50×50×3': 4.25, 'Tubo redondo Ø50×2': 2.37,
    'Pletina 100×4': 3.14, 'Plancha estriada 4 mm': 33.0, 'Plancha lisa 8 mm': 62.8, 'Ángulo L 75×75×6': 6.85}
piezas = [
    dict(pieza='Zancas', perfil='C 200×50×4', n=2, largo=LZ, uni='m', donde='las dos vigas inclinadas que cargan los peldaños; placa base abajo, al marco de la plataforma arriba'),
    dict(pieza='Peldaños', perfil='Plancha estriada 4 mm', n=NH, largo=1.50 * 0.30, uni='m²', donde='1,50 × 0,30 cada uno: 0,24 de huella y pestaña de 0,06 doblada hacia abajo; soldados entre las zancas'),
    dict(pieza='Plataforma', perfil='Plancha estriada 4 mm', n=1, largo=1.50 * 1.50, uni='m²', donde='1,50 × 1,50 sobre el marco'),
    dict(pieza='Marco de la plataforma', perfil='C 150×50×3', n=6, largo=150, uni='m', donde='4 lados + 2 travesaños (la plancha de 4 no aguanta 1,5 m sin apoyo)'),
    dict(pieza='Postes de la plataforma', perfil='Tubo cuadrado 100×100×3', n=2, largo=Z1 - 10, uni='m', donde='esquinas del lado del eje 6, del radier al marco'),
    dict(pieza='Postes de la baranda', perfil='Tubo cuadrado 50×50×3', n=9, largo=BAR + 5, uni='m', donde='5 en la escalera (cada 4 peldaños) y 4 en la plataforma'),
    dict(pieza='Pasamanos', perfil='Tubo redondo Ø50×2', n=1, largo=LZ + 300, uni='m', donde='a 1,00: escalera (lado del eje 6) y lados de la plataforma hacia los ejes G y 6'),
    dict(pieza='Barra intermedia', perfil='Tubo redondo Ø50×2', n=1, largo=LZ + 300, uni='m', donde='a 0,50, mismo recorrido'),
    dict(pieza='Rodapié', perfil='Pletina 100×4', n=1, largo=300, uni='m', donde='bordes libres de la plataforma (lados de los ejes G y 6)'),
    dict(pieza='Placas base', perfil='Plancha lisa 8 mm', n=4, largo=0.20 * 0.20, uni='m²', donde='200 × 200 × 8 bajo las 2 zancas y los 2 postes'),
    dict(pieza='Escuadras a la viga', perfil='Ángulo L 75×75×6', n=2, largo=20, uni='m', donde='amarran el marco de la plataforma a la IPE 270 del eje 5, apernadas'),
]
for p in piezas:
    L = p['largo'] / 100 if p['uni'] == 'm' else p['largo']
    p['total'] = round(L * p['n'], 2); p['kg'] = round(PERF[p['perfil']] * p['total'], 1); p['largo_txt'] = (fm(p['largo']) + ' m') if p['uni'] == 'm' else (f'{p["largo"]:.2f}'.replace('.', ',') + ' m²')
compra = [   # unidades comerciales
    dict(item='Perfil C 200×50×4 (barra de 6 m)', n=2, det='2 zancas de 5,70', kg=2 * 6 * PERF['C 200×50×4']),
    dict(item='Perfil C 150×50×3 (barra de 6 m)', n=2, det='6 tramos de 1,50 del marco (9 m)', kg=2 * 6 * PERF['C 150×50×3']),
    dict(item='Tubo cuadrado 100×100×3 (barra de 6 m)', n=2, det='2 postes de 3,85 (uno por barra)', kg=2 * 6 * PERF['Tubo cuadrado 100×100×3']),
    dict(item='Tubo cuadrado 50×50×3 (barra de 6 m)', n=2, det='9 postes de 1,05 (9,45 m)', kg=2 * 6 * PERF['Tubo cuadrado 50×50×3']),
    dict(item='Tubo redondo Ø50×2 (barra de 6 m)', n=3, det='pasamanos + barra intermedia (17,4 m)', kg=3 * 6 * PERF['Tubo redondo Ø50×2']),
    dict(item='Pletina 100×4 (barra de 6 m)', n=1, det='rodapié, 3 m (sobra la mitad)', kg=6 * PERF['Pletina 100×4']),
    dict(item='Plancha estriada 4 mm de 1500 × 3000', n=3, det='17 peldaños (10 por plancha, de 1,50 × 0,30) + la plataforma en media plancha', kg=3 * 4.5 * PERF['Plancha estriada 4 mm']),
    dict(item='Placas 200 × 200 × 8 mm', n=4, det='placas base (retazo de plancha de 8)', kg=4 * 0.04 * PERF['Plancha lisa 8 mm']),
    dict(item='Ángulo L 75×75×6', n=1, det='retazo de 0,50 m para las 2 escuadras', kg=0.5 * PERF['Ángulo L 75×75×6']),
]
fijaciones = [dict(item='Pernos de expansión 1/2" × 4"', n=16, det='4 por placa base, al radier'), dict(item='Pernos M12 × 40 con tuerca y golilla', n=8, det='escuadras a la viga IPE 270 (4) y al marco (4)')]
for c in compra: c['kg'] = round(c['kg'], 0)
total_kg = round(sum(p['kg'] for p in piezas)); total_compra = round(sum(c['kg'] for c in compra))
dims = [
    ('Ancho', '1,50 m', 'entre zancas, libre para subir materiales'),
    ('Huellas', f'{NH} × {fm(H)} = {fm(NH * H)} m', 'avance total; el pie queda a 0,33 del muro del eje E'),
    ('Contrahuellas', f'{NC} × {fm1(CH)} = {fm(Z1)} m', 'del piso de la bodega al piso del nivel 2 (viga a 3,80 medida en terreno + 15 de hormigón)'),
    ('Pendiente', f'{ANG:.0f}°', 'empinada pero normal para obra; largo de zanca ' + fm(LZ) + ' m'),
    ('Plataforma', '1,50 × 1,50 m a +3,95', 'pegada al fierro del eje G; desde ahí se entra al nivel 2 por el lado del eje 5'),
    ('Entrada al nivel 2', '0,55 + 0,79 m', 'el pilar F2 (y 4,12) queda en el borde: 0,55 libres hacia el eje G y 0,79 hacia el eje F1'),
    ('Baranda', '1,00 m', 'pasamanos a 1,00, barra a 0,50, rodapié de 10 en la plataforma; lado del eje 6 de la escalera y lados de la plataforma hacia los ejes G y 6'),
    ('Hueco en la cubierta del ala', f'1,62 × {fm(HUECO[3] - HUECO[1])} m', 'la cubierta baja del ala va a +2,88 y la escalera la atraviesa: ese tramo queda abierto mientras se use'),
]
# ---------- SVG: planta (arriba = eje G, con la flecha de norte en la esquina; José vía Gabriel, 23-10-2026: sin "norte"
# ni "sur" escritos, una flecha de norte y los ejes del ingeniero) ----------
# Letra de 14 en unidades del dibujo: el SVG no se achica bajo su ancho de diseño (min-width), así que en pantalla no baja de 14 px.
FS = 14
EJES_N = [('5', 1783.7), ('6', 2183.3)]                                           # ejes del ingeniero que cruzan la bodega
EJES_L = [('G', 341.4), ('F2', 412.0), ('F1', 518.9), ('E4', 655.6), ('E', 958.5)]   # (estructura.js)
def flecha_norte(cx, cy, R, fs):
    """Flecha de norte de plano de arquitectura: círculo fino, punta con la mitad derecha en tinta y la izquierda en papel, y la N
    sobre la punta. (cx, cy) es el centro del conjunto. Igual que flechaNorte() de losa.html."""
    sw = R * 0.05; capN = 0.72 * fs; gap = 0.18 * R; arriba = 1.35 * R + gap + capN; yc = (R - arriba) / 2
    P = [(0, -1.35 * R), (0.47 * R, 0.7 * R), (0, 0.35 * R), (-0.47 * R, 0.7 * R)]
    pts = lambda idx: ' '.join(f'{P[i][0]:.1f},{P[i][1]:.1f}' for i in idx)
    return (f'<g aria-hidden="true" transform="translate({cx:.1f} {cy - yc:.1f})"><circle cx="0" cy="0" r="{R}" fill="none" stroke="var(--fig-ink)" stroke-width="{sw:.2f}"/>'
            f'<polygon points="{pts([0, 2, 3])}" fill="var(--paper)" stroke="var(--fig-ink)" stroke-width="{sw:.2f}" stroke-linejoin="round"/>'
            f'<polygon points="{pts([0, 1, 2])}" fill="var(--fig-ink)" stroke="var(--fig-ink)" stroke-width="{sw:.2f}" stroke-linejoin="round"/>'
            f'<text x="0" y="{-1.35 * R - gap:.1f}" class="tx" text-anchor="middle" font-size="{fs}" font-weight="700">N</text></g>')
def burbuja(x, y, t):   # círculo con el nombre del eje
    g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="var(--panel)" stroke="var(--fig-soft)" stroke-width="1.2"/>'); tx(x, y + 5, t, 'tx', size=FS)
eje_l = lambda x1, y1, x2, y2: g.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="var(--fig-soft)" stroke-width="1" stroke-dasharray="10 3 2 3"/>')
sc = 1.0; ML = 200; MT = 80; MR = 70; MB = 50
X = lambda c: ML + (c - 1700) * sc; Y = lambda c: MT + (c - 280) * sc
W = int((2240 - 1700) * sc + ML + MR); Hh = int((1010 - 280) * sc + MT + MB)
g = []
rect = lambda x0, y0, x1, y1, fill, extra='': g.append(f'<rect x="{X(x0):.1f}" y="{Y(y0):.1f}" width="{(x1 - x0) * sc:.1f}" height="{(y1 - y0) * sc:.1f}" fill="{fill}" {extra}/>')
tx = lambda x, y, t, cls='tx', anchor='middle', size=FS, extra='': g.append(f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" font-size="{size}" {extra}>{t}</text>')
rect(1700, 300, 1771, 1000, 'var(--fig-fill)'); rect(1771, 280, 1796, 1000, 'var(--fig-horm)'); rect(2165, 280, 2195, 1000, 'var(--fig-horm)'); rect(1796, 334, 2165, 349, 'var(--fig-horm)'); rect(1796, 940, 2165, 965, 'var(--fig-horm)')
rect(1796, 349, 2165, 940, 'var(--fig-fill)'); rect(1796, 280, 2165, 334, 'var(--fig-fill)')
tx(X(1980), Y(314), 'SALA DE MÁQUINAS', 'txs'); tx(X(2060), Y(620), 'BODEGA 3,74 × 5,91', 'txs'); tx(X(1735), Y(800), 'CASA (despensa · baño)', 'txs', extra=f'transform="rotate(-90 {X(1735):.1f} {Y(800):.1f})"')
# ejes: círculos arriba (números) y a la derecha (letras), con un trazo corto hasta el dibujo
for t, c in EJES_N: eje_l(X(c), Y(250) + 15, X(c), Y(280)); burbuja(X(c), Y(250), t)
for t, c in EJES_L: eje_l(X(2195), Y(c), X(2268) - 15, Y(c)); burbuja(X(2268), Y(c), t)
g.append(flecha_norte(70, 62, 24, 16))
g.append(f'<line x1="{X(1793):.1f}" y1="{Y(280):.1f}" x2="{X(1793):.1f}" y2="{Y(1000):.1f}" stroke="var(--fig-viga)" stroke-width="1.5" stroke-dasharray="6 4"/>')
tx(X(1788), Y(990), 'borde del nivel 2', 'txs', 'end'); tx(X(1788), Y(1008), 'placa +3,80 · piso +3,95', 'txs', 'end')
rect(2165, 357.4, 2195, 447.4, 'var(--fig-sold)'); tx(X(2160), Y(428), 'puerta P3', 'txs', 'end')
for ya in (341.4, 958.5): rect(1791, ya - 10, 2176, ya + 10, '#8e44ad', 'opacity=".6"')
rect(2183 - 7.5, 334, 2183 + 7.5, 951, '#8e44ad', 'opacity=".6"'); tx(X(1958), Y(376), 'vigas RECT 200×150 a +2,78', 'txs', 'start'); tx(X(1958), Y(394), 'cubierta del ala a +2,88', 'txs', 'start')
rect(*HUECO[:2], *HUECO[2:], 'none', 'stroke="#8e44ad" stroke-width="1.5" stroke-dasharray="5 4"'); tx(X(1960), Y(880), 'hueco provisorio', 'txs', 'start'); tx(X(1960), Y(898), 'en la cubierta del ala', 'txs', 'start')
for eje, px, py, p in PIL:   # pilares del eje 5 con su nombre al lado de la casa; los del eje 6, hacia adentro de la bodega
    h = 16 if 'HEB' in p else 15; rect(px - h / 2, py - h / 2, px + h / 2, py + h / 2, 'var(--hi)'); tx(X(px) + (-12 if px < 2000 else -13), Y(py) + 5, eje, 'tx', 'end', extra='fill="var(--hi)" font-weight="600"')
rect(X0, PL0, X1, PL1, 'var(--fig-viga)', 'opacity=".35" stroke="var(--fig-viga)"'); tx(X((X0 + X1) / 2), Y(436), 'plataforma', 'tx', size=15, extra='font-weight="600"'); tx(X((X0 + X1) / 2), Y(454), '1,50 × 1,50', 'tx'); tx(X((X0 + X1) / 2), Y(472), '+3,95', 'tx')
rect(X0, PL1, X1, YA, 'var(--fig-placa)', 'opacity=".35" stroke="var(--fig-viga)"')
for k in range(NH + 1): y = PL1 + k * H; g.append(f'<line x1="{X(X0):.1f}" y1="{Y(y):.1f}" x2="{X(X1):.1f}" y2="{Y(y):.1f}" stroke="var(--fig-ink)" stroke-width=".8"/>')
g.append(f'<line x1="{X(X0 + 75):.1f}" y1="{Y(YA - 10):.1f}" x2="{X(X0 + 75):.1f}" y2="{Y(PL1 + 20):.1f}" stroke="var(--fig-ink)" stroke-width="1.2" marker-end="url(#fle)"/>')
for i, t in enumerate([f'sube: {NH} huellas de {fm1(H).replace(",0", "")}', f'(avance {fm(NH * H)})', f'{NC} contrahuellas de {fm1(CH)}', f'({fm(Z1)}) · {ANG:.0f}°']): tx(X(X1) + 12, Y(730 + 18 * i), t, 'tx', 'start')
g.append(f'<polyline points="{X(X1):.1f},{Y(YA):.1f} {X(X1):.1f},{Y(PL0):.1f} {X(X0):.1f},{Y(PL0):.1f}" fill="none" stroke="var(--fig-c)" stroke-width="3"/>')
for i, t in enumerate(['baranda 1,00', 'pasamanos, barra a 0,50', 'y rodapié']): tx(X(X1) + 12, Y(474 + 18 * i), t, 'tx', 'start', extra='fill="var(--fig-c)"' + (' font-weight="600"' if not i else ''))
for yy in (375, 470): g.append(f'<line x1="{X(X0):.1f}" y1="{Y(yy):.1f}" x2="{X(X0 - 40):.1f}" y2="{Y(yy):.1f}" stroke="var(--fig-viga)" stroke-width="1.5" marker-end="url(#fla)"/>')
for i, t in enumerate(['entra al nivel 2 junto al pilar F2', '0,55 libres hacia el eje G', '0,79 hacia el eje F1']): tx(X(1766), Y(500 + 18 * i), t, 'tx', 'end', extra='fill="var(--fig-viga)"')
def cota(x0, y0, x1, y1, t, vert=False, ty=None):
    if vert: g.append(f'<line x1="{X(x0):.1f}" y1="{Y(y0):.1f}" x2="{X(x0):.1f}" y2="{Y(y1):.1f}" stroke="var(--fig-soft)"/>'); tx(X(x0) + 6, Y(ty if ty is not None else (y0 + y1) / 2) + 5, t, 'txs', 'start')
    else: g.append(f'<line x1="{X(x0):.1f}" y1="{Y(y0):.1f}" x2="{X(x1):.1f}" y2="{Y(y0):.1f}" stroke="var(--fig-soft)"/>'); tx(X((x0 + x1) / 2), Y(y0) - 4, t, 'txs')
# cotas verticales con el número al costado, entre los trazos de los ejes F2, F1, E4 y E
cota(X0, 990, X1, 990, '1,50'); cota(X1, 990, 2165, 990, '2,19 libres'); cota(2210, PL0, 2210, PL1, '1,50', True, 462); cota(2210, PL1, 2210, YA, fm(NH * H), True, 720); cota(2210, YA, 2210, 940, '0,33', True, 924)
defs = '<defs><marker id="fle" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="var(--fig-ink)"/></marker><marker id="fla" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="var(--fig-viga)"/></marker></defs>'
planta = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {Hh}" style="min-width:{W}px;max-height:none" role="img" aria-label="Planta de la escalera de obra en la bodega, con la flecha de norte y los ejes del ingeniero">{defs}' + '\n'.join(g) + '</svg>'
# ---------- SVG: corte mirando hacia el eje 5 (el muro de la casa queda al fondo): eje G a la derecha, eje E a la izquierda ----------
# Alturas desde el piso terminado de la bodega (±0,00), una sola referencia. Ejes del ingeniero en círculos bajo el terreno.
g = []; ML2 = 34; MR2 = 46; MT2 = 10; ZTOP = 600; ZBOT = -104
W2 = int(700 + ML2 + MR2); H2 = int(MT2 + ZTOP - ZBOT)
Xc = lambda y: ML2 + (1000 - y); Zc = lambda z: MT2 + (ZTOP - z)
rect2 = lambda y0, z0, y1, z1, fill, extra='': g.append(f'<rect x="{Xc(max(y0, y1)):.1f}" y="{Zc(max(z0, z1)):.1f}" width="{abs(y1 - y0):.1f}" height="{abs(z1 - z0):.1f}" fill="{fill}" {extra}/>')
g.append(f'<rect x="0" y="{Zc(0):.1f}" width="{W2}" height="60" fill="var(--fig-horm)"/>')
rect2(334, 0, 349, ALA_TOP, 'var(--fig-horm)'); rect2(940, 0, 965, ALA_TOP, 'var(--fig-horm)')
rect2(331, ALA_TOP - 20, 351, ALA_TOP, '#8e44ad'); rect2(948, ALA_TOP - 20, 968, ALA_TOP, '#8e44ad')
g.append(f'<line x1="{Xc(HUECO[3]):.1f}" y1="{Zc(ALA_TOP):.1f}" x2="{Xc(940):.1f}" y2="{Zc(ALA_TOP):.1f}" stroke="#8e44ad" stroke-width="3"/><line x1="{Xc(349):.1f}" y1="{Zc(ALA_TOP):.1f}" x2="{Xc(HUECO[3]):.1f}" y2="{Zc(ALA_TOP):.1f}" stroke="#8e44ad" stroke-width="1.5" stroke-dasharray="6 5"/>')
tx(Xc(935), Zc(ALA_TOP) + 16, 'cubierta del ala a +2,88', 'txs', 'start'); tx(Xc(935), Zc(ALA_TOP) + 34, 'abierta mientras se use', 'txs', 'start')
rect2(300, PISO_N1, 1000, Z1, 'var(--fig-horm2)', 'opacity=".5"')
tx(Xc(990), Zc(Z1) - 24, 'losa del nivel 2, tras el muro del eje 5', 'txs', 'start'); tx(Xc(990), Zc(Z1) - 6, 'placa +3,80 · piso terminado +3,95', 'txs', 'start')
for k in range(NH):   # peldaños: plancha de 4 con la pestaña de 6 hacia abajo en el frente (el borde que se encuentra al subir)
    y0 = YA - k * H; rect2(y0 - H, (k + 1) * CH - 4, y0, (k + 1) * CH, 'var(--fig-placa)', 'stroke="var(--fig-ink)" stroke-width=".6"'); rect2(y0 - 4, (k + 1) * CH - 10, y0, (k + 1) * CH - 4, 'var(--fig-placa)')
rect2(PL0, Z1 - 4, PL1, Z1, 'var(--fig-placa)', 'stroke="var(--fig-ink)" stroke-width=".6"'); rect2(PL0, Z1 - 19, PL1, Z1 - 4, 'var(--fig-viga)', 'opacity=".8"')
tx(Xc(424), Zc(Z1 + BAR) - 32, 'plataforma 1,50 · +3,95', 'tx', extra='font-weight="600"'); tx(Xc(424), Zc(Z1 + BAR) - 13, 'marco apernado a la IPE 270 del eje 5', 'txs')
g.append(f'<line x1="{Xc(YA):.1f}" y1="{Zc(0):.1f}" x2="{Xc(PL1):.1f}" y2="{Zc(Z1 - 12):.1f}" stroke="var(--fig-viga)" stroke-width="5" opacity=".85"/>')
# rótulo de las zancas bajo la zanca, paralelo a ella, en dos tramos seguidos (sus cajas no se tocan)
xa, za, xb, zb = Xc(YA), Zc(0), Xc(PL1), Zc(Z1 - 12); LZp = math.hypot(xb - xa, zb - za); ca, sa = (xb - xa) / LZp, (za - zb) / LZp; angz = math.degrees(math.atan2(za - zb, xb - xa))
for s_, t in ((146, 'zancas C 200×50×4'), (362, 'peldaños de plancha estriada 4 mm')):
    px_, py_ = xa + s_ * ca + 22 * sa, za - s_ * sa + 22 * ca
    tx(px_, py_, t, 'tx', extra=f'fill="var(--fig-viga)" transform="rotate(-{angz:.1f} {px_:.1f} {py_:.1f})"')
for yy in (357, 491): rect2(yy - 5, 0, yy + 5, Z1 - 19, 'var(--fig-viga)', 'opacity=".85"')
tx(Xc(424), Zc(240), '2 postes', 'tx', extra='fill="var(--fig-viga)"'); tx(Xc(424), Zc(222), 'tubo 100×100×3', 'tx', extra='fill="var(--fig-viga)"')
g.append(f'<line x1="{Xc(YA):.1f}" y1="{Zc(BAR):.1f}" x2="{Xc(PL1):.1f}" y2="{Zc(Z1 + BAR):.1f}" stroke="var(--fig-c)" stroke-width="3"/><line x1="{Xc(PL1):.1f}" y1="{Zc(Z1 + BAR):.1f}" x2="{Xc(PL0):.1f}" y2="{Zc(Z1 + BAR):.1f}" stroke="var(--fig-c)" stroke-width="3"/><line x1="{Xc(PL0):.1f}" y1="{Zc(Z1 + BAR):.1f}" x2="{Xc(PL0):.1f}" y2="{Zc(Z1):.1f}" stroke="var(--fig-c)" stroke-width="3"/>')
g.append(f'<line x1="{Xc(YA):.1f}" y1="{Zc(BAR / 2):.1f}" x2="{Xc(PL1):.1f}" y2="{Zc(Z1 + BAR / 2):.1f}" stroke="var(--fig-c)" stroke-width="1.5"/>')
for k in range(0, NH + 1, 4): y = YA - k * H; g.append(f'<line x1="{Xc(y):.1f}" y1="{Zc(k * CH):.1f}" x2="{Xc(y):.1f}" y2="{Zc(k * CH + BAR):.1f}" stroke="var(--fig-c)" stroke-width="2"/>')
tx(Xc(990), Zc(578), 'baranda 1,00: postes tubo 50×50×3 cada 4 peldaños,', 'tx', 'start', extra='fill="var(--fig-c)"'); tx(Xc(990), Zc(560), 'pasamanos tubo Ø50×2 y barra a 0,50', 'tx', 'start', extra='fill="var(--fig-c)"')
g.append(f'<line x1="{Xc(PL1):.1f}" y1="{Zc(-45):.1f}" x2="{Xc(YA):.1f}" y2="{Zc(-45):.1f}" stroke="var(--fig-soft)"/>'); tx((Xc(PL1) + Xc(YA)) / 2, Zc(-45) - 5, f'avance {fm(NH * H)} = {NH} × {fm1(H).replace(",0", "")}', 'txs')
g.append(f'<line x1="{Xc(PL0):.1f}" y1="{Zc(-45):.1f}" x2="{Xc(PL1):.1f}" y2="{Zc(-45):.1f}" stroke="var(--fig-soft)"/>'); tx(Xc(424), Zc(-45) - 5, '1,50', 'txs')
g.append(f'<line x1="{Xc(995):.1f}" y1="{Zc(0):.1f}" x2="{Xc(995):.1f}" y2="{Zc(Z1):.1f}" stroke="var(--fig-soft)"/>'); tx(Xc(995) - 6, Zc(Z1 / 2), f'{fm(Z1)} = {NC} × {fm1(CH)} ({ANG:.0f}°)', 'txs', extra=f'transform="rotate(-90 {Xc(995) - 6:.1f} {Zc(Z1 / 2):.1f})"')
tx(Xc(990), Zc(0) + 18, '±0,00 piso terminado de la bodega', 'txs', 'start')
for t, c in EJES_L: eje_l(Xc(c), Zc(-60), Xc(c), Zc(-80) - 15); burbuja(Xc(c), Zc(-80), t)
corte = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W2} {H2}" style="min-width:{W2}px;max-height:none" role="img" aria-label="Corte de la escalera de obra mirando hacia el eje 5, con los ejes del ingeniero">' + '\n'.join(g) + '</svg>'
salida = dict(fuente='Gabriel, 16-10-2026: "380 de altura por 370 de avance, ancho 1,5 con baranda, plataforma 1,5 × 1,5 arriba y el quiebre… toda de fierro, cómoda y segura para subir materiales"; "justo llega hasta el borde, córrela más atrás, pegado al fierro de atrás". Geometría de fuente/casa/generar_escalera_js.py, la misma del 3D.',
              geometria=dict(x0=X0, x1=X1, plataforma=[PL0, PL1], pie=YA, huellas=NH, huella=H, contrahuellas=NC, contrahuella=round(CH, 1), alto=Z1, pendiente=round(ANG, 1), zanca=round(LZ), hueco=HUECO, ala_top=ALA_TOP),
              dimensiones=[dict(k=k, v=v, d=d) for k, v, d in dims], piezas=piezas, compra=compra, fijaciones=fijaciones, total_kg=total_kg, total_compra=total_compra, kgm=PERF, svg=dict(planta=planta, corte=corte))
(raiz / 'escalera_dibujo.js').write_text('const DATA_ESCALERA = ' + json.dumps(salida, ensure_ascii=False) + ';\n', encoding='utf-8')
print(f'escalera_dibujo.js: {NH} huellas de {H:.0f}, {NC} contrahuellas de {CH:.1f}, {ANG:.1f}°, zanca {LZ:.0f} · fierro usado {total_kg} kg, comprado {total_compra} kg')
