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
NH, H = 17, 24.0; YA = PL1 + NH * H                           # 17 huellas de 24: pie en y 907 (muro sur de la bodega en 940)
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
    dict(pieza='Postes de la plataforma', perfil='Tubo cuadrado 100×100×3', n=2, largo=Z1 - 10, uni='m', donde='esquinas oriente, del radier al marco'),
    dict(pieza='Postes de la baranda', perfil='Tubo cuadrado 50×50×3', n=9, largo=BAR + 5, uni='m', donde='5 en la escalera (cada 4 peldaños) y 4 en la plataforma'),
    dict(pieza='Pasamanos', perfil='Tubo redondo Ø50×2', n=1, largo=LZ + 300, uni='m', donde='a 1,00: escalera (lado oriente) y lados norte y oriente de la plataforma'),
    dict(pieza='Barra intermedia', perfil='Tubo redondo Ø50×2', n=1, largo=LZ + 300, uni='m', donde='a 0,50, mismo recorrido'),
    dict(pieza='Rodapié', perfil='Pletina 100×4', n=1, largo=300, uni='m', donde='bordes libres de la plataforma (norte y oriente)'),
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
    ('Huellas', f'{NH} × {fm(H)} = {fm(NH * H)} m', 'avance total; el pie queda a 0,33 del muro sur de la bodega'),
    ('Contrahuellas', f'{NC} × {fm1(CH)} = {fm(Z1)} m', 'del piso de la bodega al piso del nivel 2 (viga a 3,80 medida en terreno + 15 de hormigón)'),
    ('Pendiente', f'{ANG:.0f}°', 'empinada pero normal para obra; largo de zanca ' + fm(LZ) + ' m'),
    ('Plataforma', '1,50 × 1,50 m a +3,95', 'pegada al fierro del eje G; desde ahí se entra al nivel 2 por el poniente'),
    ('Entrada al nivel 2', '0,55 + 0,79 m', 'el pilar F2 (y 4,12) queda en el borde: 0,55 libres al norte y 0,79 al sur'),
    ('Baranda', '1,00 m', 'pasamanos a 1,00, barra a 0,50, rodapié de 10 en la plataforma; lado oriente de la escalera y lados norte y oriente de la plataforma'),
    ('Hueco en la cubierta del ala', f'1,62 × {fm(HUECO[3] - HUECO[1])} m', 'la cubierta baja del ala va a +2,88 y la escalera la atraviesa: ese tramo queda abierto mientras se use'),
]
# ---------- SVG: planta (norte arriba) ----------
sc = 1.0; ML = 150; MT = 40
X = lambda c: ML + (c - 1700) * sc; Y = lambda c: MT + (c - 280) * sc
W = int((2240 - 1700) * sc + ML + 60); Hh = int((1010 - 280) * sc + MT + 60)
g = []
rect = lambda x0, y0, x1, y1, fill, extra='': g.append(f'<rect x="{X(x0):.1f}" y="{Y(y0):.1f}" width="{(x1 - x0) * sc:.1f}" height="{(y1 - y0) * sc:.1f}" fill="{fill}" {extra}/>')
tx = lambda x, y, t, cls='tx', anchor='middle', size=11, extra='': g.append(f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" font-size="{size}" {extra}>{t}</text>')
rect(1700, 300, 1771, 1000, 'var(--fig-fill)'); rect(1771, 280, 1796, 1000, 'var(--fig-horm)'); rect(2165, 280, 2195, 1000, 'var(--fig-horm)'); rect(1796, 334, 2165, 349, 'var(--fig-horm)'); rect(1796, 940, 2165, 965, 'var(--fig-horm)')
rect(1796, 349, 2165, 940, 'var(--fig-fill)'); rect(1796, 280, 2165, 334, 'var(--fig-fill)')
tx(X(1980), Y(312), 'SALA DE MÁQUINAS', 'txs', size=10); tx(X(2060), Y(700), 'BODEGA 3,74 × 5,91', 'txs', size=10); tx(X(1735), Y(650), 'CASA (despensa · baño)', 'txs', size=10, extra=f'transform="rotate(-90 {X(1735):.1f} {Y(650):.1f})"')
g.append(f'<line x1="{X(1793):.1f}" y1="{Y(280):.1f}" x2="{X(1793):.1f}" y2="{Y(1000):.1f}" stroke="var(--fig-viga)" stroke-width="1.5" stroke-dasharray="6 4"/>'); tx(X(1788), Y(990), 'borde del nivel 2 (placa +3,80 · piso +3,95)', 'txs', 'end', 9)
rect(2165, 357.4, 2195, 447.4, 'var(--fig-sold)'); tx(X(2200), Y(405), 'P3', 'txs', 'start', 9)
for ya in (341.4, 958.5): rect(1791, ya - 10, 2176, ya + 10, '#8e44ad', 'opacity=".6"')
rect(2183 - 7.5, 334, 2183 + 7.5, 951, '#8e44ad', 'opacity=".6"'); tx(X(1985), Y(341) - 13, 'viga RECT 200×150 a +2,78: cubierta baja del ala (+2,88)', 'txs', size=9)
rect(*HUECO[:2], *HUECO[2:], 'none', 'stroke="#8e44ad" stroke-width="1.5" stroke-dasharray="5 4"'); tx(X(1960), Y(HUECO[3] + 14), 'hueco provisorio en la cubierta del ala', 'txs', 'start', 9)
for eje, px, py, p in PIL:
    h = 16 if 'HEB' in p else 15; rect(px - h / 2, py - h / 2, px + h / 2, py + h / 2, 'var(--hi)'); tx(X(px) + (13 if px < 2000 else -13), Y(py) + 4, eje, 'tx', 'start' if px < 2000 else 'end', 9, 'fill="var(--hi)" font-weight="600"')
rect(X0, PL0, X1, PL1, 'var(--fig-viga)', 'opacity=".35" stroke="var(--fig-viga)"'); tx(X((X0 + X1) / 2), Y(418), 'plataforma', 'tx', size=11, extra='font-weight="600"'); tx(X((X0 + X1) / 2), Y(434), '1,50 × 1,50 · +3,95', 'tx', size=10)
rect(X0, PL1, X1, YA, 'var(--fig-placa)', 'opacity=".35" stroke="var(--fig-viga)"')
for k in range(NH + 1): y = PL1 + k * H; g.append(f'<line x1="{X(X0):.1f}" y1="{Y(y):.1f}" x2="{X(X1):.1f}" y2="{Y(y):.1f}" stroke="var(--fig-ink)" stroke-width=".8"/>')
g.append(f'<line x1="{X(X0 + 75):.1f}" y1="{Y(YA - 10):.1f}" x2="{X(X0 + 75):.1f}" y2="{Y(PL1 + 20):.1f}" stroke="var(--fig-ink)" stroke-width="1.2" marker-end="url(#fle)"/>')
tx(X(X1) + 8, Y(760), f'sube: {NH} huellas de {fm1(H).replace(",0", "")} (avance {fm(NH * H)})', 'tx', 'start', 10); tx(X(X1) + 8, Y(776), f'{NC} contrahuellas de {fm1(CH)} ({fm(Z1)}) · {ANG:.0f}°', 'tx', 'start', 10)
g.append(f'<polyline points="{X(X1):.1f},{Y(YA):.1f} {X(X1):.1f},{Y(PL0):.1f} {X(X0):.1f},{Y(PL0):.1f}" fill="none" stroke="var(--fig-c)" stroke-width="3"/>'); tx(X(X1) + 8, Y(470), 'baranda 1,00 (pasamanos, barra a 0,50, rodapié)', 'tx', 'start', 10, 'fill="var(--fig-c)"')
for yy in (375, 470): g.append(f'<line x1="{X(X0):.1f}" y1="{Y(yy):.1f}" x2="{X(X0 - 40):.1f}" y2="{Y(yy):.1f}" stroke="var(--fig-viga)" stroke-width="1.5" marker-end="url(#fla)"/>')
tx(X(1766), Y(492), 'entra al nivel 2 junto al pilar F2', 'tx', 'end', 9, 'fill="var(--fig-viga)"'); tx(X(1766), Y(506), '(0,55 libres al norte, 0,79 al sur)', 'tx', 'end', 9, 'fill="var(--fig-viga)"')
def cota(x0, y0, x1, y1, t, vert=False, off=0):
    if vert: g.append(f'<line x1="{X(x0) + off:.1f}" y1="{Y(y0):.1f}" x2="{X(x0) + off:.1f}" y2="{Y(y1):.1f}" stroke="var(--fig-soft)"/>'); tx(X(x0) + off - 5, Y((y0 + y1) / 2), t, 'txs', size=9, extra=f'transform="rotate(-90 {X(x0) + off - 5:.1f} {Y((y0 + y1) / 2):.1f})"')
    else: g.append(f'<line x1="{X(x0):.1f}" y1="{Y(y0) + off:.1f}" x2="{X(x1):.1f}" y2="{Y(y0) + off:.1f}" stroke="var(--fig-soft)"/>'); tx(X((x0 + x1) / 2), Y(y0) + off - 4, t, 'txs', size=9)
cota(X0, 985, X1, 985, '1,50'); cota(X1, 985, 2165, 985, '2,19 libres'); cota(2210, PL0, 2210, PL1, '1,50', True); cota(2210, PL1, 2210, YA, fm(NH * H), True); cota(2210, YA, 2210, 940, '0,33', True)
defs = '<defs><marker id="fle" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="var(--fig-ink)"/></marker><marker id="fla" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="var(--fig-viga)"/></marker></defs>'
planta = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {Hh}" role="img" aria-label="Planta de la escalera de obra en la bodega">{defs}' + '\n'.join(g) + '</svg>'
# ---------- SVG: corte mirando al poniente (norte a la izquierda) ----------
g = []; sc2 = 1.0; ML2 = 70; MT2 = 30; W2 = int((1000 - 300) * sc2 + ML2 + 80); H2 = int(520 * sc2 + MT2 + 80)
Xc = lambda y: ML2 + (y - 300) * sc2; Zc = lambda z: MT2 + (520 - z) * sc2
rect2 = lambda y0, z0, y1, z1, fill, extra='': g.append(f'<rect x="{Xc(y0):.1f}" y="{Zc(z1):.1f}" width="{(y1 - y0) * sc2:.1f}" height="{(z1 - z0) * sc2:.1f}" fill="{fill}" {extra}/>')
g.append(f'<rect x="0" y="{Zc(0):.1f}" width="{W2}" height="{60 * sc2}" fill="var(--fig-horm)"/>')
rect2(334, 0, 349, ALA_TOP, 'var(--fig-horm)'); rect2(940, 0, 965, ALA_TOP, 'var(--fig-horm)')
rect2(331, ALA_TOP - 20, 351, ALA_TOP, '#8e44ad'); rect2(948, ALA_TOP - 20, 968, ALA_TOP, '#8e44ad')
g.append(f'<line x1="{Xc(HUECO[3]):.1f}" y1="{Zc(ALA_TOP):.1f}" x2="{Xc(940):.1f}" y2="{Zc(ALA_TOP):.1f}" stroke="#8e44ad" stroke-width="3"/><line x1="{Xc(349):.1f}" y1="{Zc(ALA_TOP):.1f}" x2="{Xc(HUECO[3]):.1f}" y2="{Zc(ALA_TOP):.1f}" stroke="#8e44ad" stroke-width="1.5" stroke-dasharray="6 5"/>')
tx(Xc(640), Zc(ALA_TOP) - 7, 'cubierta baja del ala a +2,88: hueco sobre la escalera y la plataforma mientras se use', 'txs', size=9, extra='fill="#8e44ad"')
rect2(300, PISO_N1, 1000, Z1, 'var(--fig-horm2)', 'opacity=".5"'); tx(Xc(760), Zc(Z1) - 6, 'losa del nivel 2 detrás del muro de la casa: placa +3,80 · hormigón +3,95', 'txs', size=9)
for k in range(NH):
    y0 = YA - k * H; rect2(y0 - H, (k + 1) * CH - 4, y0, (k + 1) * CH, 'var(--fig-placa)', 'stroke="var(--fig-ink)" stroke-width=".6"'); rect2(y0 - H, (k + 1) * CH - 10, y0 - H + 4, (k + 1) * CH - 4, 'var(--fig-placa)')
rect2(PL0, Z1 - 4, PL1, Z1, 'var(--fig-placa)', 'stroke="var(--fig-ink)" stroke-width=".6"'); rect2(PL0, Z1 - 19, PL1, Z1 - 4, 'var(--fig-viga)', 'opacity=".8"'); tx(Xc(424), Zc(Z1) + 30, 'plataforma 1,50 · +3,95', 'tx', size=10, extra='font-weight="600"')
g.append(f'<line x1="{Xc(YA):.1f}" y1="{Zc(0):.1f}" x2="{Xc(PL1):.1f}" y2="{Zc(Z1 - 12):.1f}" stroke="var(--fig-viga)" stroke-width="5" opacity=".85"/>'); tx(Xc(760), Zc(118), 'zancas C 200×50×4 · peldaños de plancha estriada 4 mm', 'tx', size=9, extra=f'fill="var(--fig-viga)" transform="rotate(-{ANG:.0f} {Xc(760):.1f} {Zc(118):.1f})"')
for yy in (357, 491): rect2(yy - 5, 0, yy + 5, Z1 - 19, 'var(--fig-viga)', 'opacity=".85"')
tx(Xc(424), Zc(170), '2 postes tubo 100×100×3', 'tx', size=9, extra='fill="var(--fig-viga)"'); tx(Xc(424), Zc(156), '(el lado poniente va apernado a la IPE 270 del eje 5)', 'txs', size=8)
g.append(f'<line x1="{Xc(YA):.1f}" y1="{Zc(BAR):.1f}" x2="{Xc(PL1):.1f}" y2="{Zc(Z1 + BAR):.1f}" stroke="var(--fig-c)" stroke-width="3"/><line x1="{Xc(PL1):.1f}" y1="{Zc(Z1 + BAR):.1f}" x2="{Xc(PL0):.1f}" y2="{Zc(Z1 + BAR):.1f}" stroke="var(--fig-c)" stroke-width="3"/><line x1="{Xc(PL0):.1f}" y1="{Zc(Z1 + BAR):.1f}" x2="{Xc(PL0):.1f}" y2="{Zc(Z1):.1f}" stroke="var(--fig-c)" stroke-width="3"/>')
g.append(f'<line x1="{Xc(YA):.1f}" y1="{Zc(BAR / 2):.1f}" x2="{Xc(PL1):.1f}" y2="{Zc(Z1 + BAR / 2):.1f}" stroke="var(--fig-c)" stroke-width="1.5"/>')
for k in range(0, NH + 1, 4): y = YA - k * H; g.append(f'<line x1="{Xc(y):.1f}" y1="{Zc(k * CH):.1f}" x2="{Xc(y):.1f}" y2="{Zc(k * CH + BAR):.1f}" stroke="var(--fig-c)" stroke-width="2"/>')
tx(Xc(640), Zc(Z1 + BAR + 30), 'baranda 1,00: postes tubo 50×50×3 cada 4 peldaños, pasamanos tubo Ø50×2, barra a 0,50', 'tx', size=9, extra='fill="var(--fig-c)"')
g.append(f'<line x1="{Xc(PL1):.1f}" y1="{Zc(-30):.1f}" x2="{Xc(YA):.1f}" y2="{Zc(-30):.1f}" stroke="var(--fig-soft)"/>'); tx(Xc((PL1 + YA) / 2), Zc(-30) - 4, f'avance {fm(NH * H)} = {NH} × {fm1(H).replace(",0", "")}', 'txs', size=9)
g.append(f'<line x1="{Xc(PL0):.1f}" y1="{Zc(-30):.1f}" x2="{Xc(PL1):.1f}" y2="{Zc(-30):.1f}" stroke="var(--fig-soft)"/>'); tx(Xc(424), Zc(-30) - 4, '1,50', 'txs', size=9)
g.append(f'<line x1="{Xc(995):.1f}" y1="{Zc(0):.1f}" x2="{Xc(995):.1f}" y2="{Zc(Z1):.1f}" stroke="var(--fig-soft)"/>'); tx(Xc(995) - 6, Zc(Z1 / 2), f'{fm(Z1)} = {NC} × {fm1(CH)} ({ANG:.0f}°)', 'txs', size=9, extra=f'transform="rotate(-90 {Xc(995) - 6:.1f} {Zc(Z1 / 2):.1f})"')
tx(Xc(300), Zc(0) + 16, '±0,00 piso terminado de la bodega · norte a la izquierda', 'txs', 'start', 9)
corte = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W2} {H2}" role="img" aria-label="Corte de la escalera de obra mirando al poniente">' + '\n'.join(g) + '</svg>'
salida = dict(fuente='Gabriel, 16-10-2026: "380 de altura por 370 de avance, ancho 1,5 con baranda, plataforma 1,5 × 1,5 arriba y el quiebre… toda de fierro, cómoda y segura para subir materiales"; "justo llega hasta el borde, córrela más atrás, pegado al fierro de atrás". Geometría de fuente/casa/generar_escalera_js.py, la misma del 3D.',
              geometria=dict(x0=X0, x1=X1, plataforma=[PL0, PL1], pie=YA, huellas=NH, huella=H, contrahuellas=NC, contrahuella=round(CH, 1), alto=Z1, pendiente=round(ANG, 1), zanca=round(LZ), hueco=HUECO, ala_top=ALA_TOP),
              dimensiones=[dict(k=k, v=v, d=d) for k, v, d in dims], piezas=piezas, compra=compra, fijaciones=fijaciones, total_kg=total_kg, total_compra=total_compra, kgm=PERF, svg=dict(planta=planta, corte=corte))
(raiz / 'escalera_dibujo.js').write_text('const DATA_ESCALERA = ' + json.dumps(salida, ensure_ascii=False) + ';\n', encoding='utf-8')
print(f'escalera_dibujo.js: {NH} huellas de {H:.0f}, {NC} contrahuellas de {CH:.1f}, {ANG:.1f}°, zanca {LZ:.0f} · fierro usado {total_kg} kg, comprado {total_compra} kg')
