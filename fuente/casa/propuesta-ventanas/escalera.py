# -*- coding: utf-8 -*-
"""Escalera de obra en la bodega del ala oriente (Gabriel, 16-10-2026): planta y corte con los pilares y vigas del ingeniero."""
import json, re
R='/Users/toledobrintrup/Coding/Pilauco'; S='/private/tmp/claude-501/-Users-toledobrintrup-Coding-Pilauco/336a464c-579a-4405-af69-f1b1813fc385/scratchpad/prop'
E=json.loads(re.search(r'const DATA_ESTRUCTURA = (\{.*\});?\s*$', open(R+'/estructura.js',encoding='utf-8').read(), re.S).group(1))
PIL=[(m['id'],m['a'][0],m['a'][1],m['a'][2],m['b'][2],m['p']) for m in E['miembros'] if m['c']=='pilar' and 1750<m['a'][0]<2220 and 300<m['a'][1]<1000 and m['a'][2]<15]
# geometría (cm, marco de la app): bodega interior 1790..2165 × 349..940; muro de la casa (eje 5) x 1771..1796; nivel 2 termina en x 1793
X0,X1,Y0,Y1 = 1796, 1946, 420, 940      # escalera y plataforma pegadas al muro de la casa, 1,50 de ancho
PL = (X0, 420, X1, 570)                 # plataforma 1,5 × 1,5
NH, HUELLA = 16, 23.125                 # 16 huellas de 23,1 → avance 3,70
NC, CH = 17, 361/17                     # 17 contrahuellas de 21,2 → 3,61 (piso del nivel 2 +3,61 sobre el piso terminado de la bodega)
sc=2.2; ML=300; MT=120
g=[]
W=int((2240-1700)*sc+2*ML); H=int((1020-280)*sc+MT+60)
X=lambda c: ML+(c-1700)*sc; Y=lambda c: MT+(c-280)*sc
g.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#0f1115"/>')
g.append(f'<text x="{ML}" y="40" class="t">Escalera de obra en la bodega · planta</text><text x="{ML}" y="64" class="nota">norte arriba · fierro: zancas, peldaños de plancha estriada, plataforma 1,5 × 1,5, baranda a 1,00 · naranjo = pilares del ingeniero · violeta = vigas de la cubierta baja del ala (+2,78) · azul = borde del nivel 2</text>')
g.append(f'<text x="{ML}" y="86" class="nota">Gabriel: "380 de altura por 370 de avance, ancho 1,5 con baranda, plataforma 1,5 × 1,5 arriba y el quiebre hacia la casa" · dibujada para llegar al piso del nivel 2 (+3,61 sobre el piso terminado; desde el radier serían ≈3,80)</text>')
# muros: casa (eje 5) y ala
def rect(x0,y0,x1,y1,fill,stroke='#2a2a2a',op=1,dash=''):
    da = (' stroke-dasharray="' + dash + '"') if dash else ''
    g.append(f'<rect x="{X(x0):.1f}" y="{Y(y0):.1f}" width="{(x1-x0)*sc:.1f}" height="{(y1-y0)*sc:.1f}" fill="{fill}" stroke="{stroke}" opacity="{op}"{da}/>')
rect(1700,300,1771,1000,'#1a1c21')                          # interior de la casa (lavandería/despensa/baño)
rect(1771,280,1796,1000,'#8a8780')                           # muro de la casa, eje 5
rect(2165,280,2195,1000,'#8a8780'); rect(1796,334,2165,349,'#8a8780'); rect(1796,940,2165,965,'#8a8780')   # muros del ala
rect(1796,349,2165,940,'#2b2720')                            # bodega
rect(1796,280,2165,334,'#2b2720')                            # sala de máquinas (al norte)
g.append(f'<text x="{X(1980):.1f}" y="{Y(700):.1f}" class="rec" text-anchor="middle">BODEGA 3,74 × 5,91</text><text x="{X(1980):.1f}" y="{Y(310):.1f}" class="rec" text-anchor="middle">SALA DE MÁQUINAS</text><text x="{X(1735):.1f}" y="{Y(700):.1f}" class="rec" text-anchor="middle" transform="rotate(-90 {X(1735):.1f} {Y(700):.1f})">DESPENSA · BAÑO</text>')
# borde del nivel 2 (losa termina en x 1793) y puerta P3 de la bodega al oriente (357..447)
g.append(f'<line x1="{X(1793):.1f}" y1="{Y(280):.1f}" x2="{X(1793):.1f}" y2="{Y(1000):.1f}" stroke="#4A90D9" stroke-width="2" stroke-dasharray="8 4"/><text x="{X(1793)-6:.1f}" y="{Y(985):.1f}" class="azul" text-anchor="end">borde del nivel 2 (losa a +3,46 · piso +3,61)</text>')
rect(2165,357.4,2195,447.4,'#8B6A45'); g.append(f'<text x="{X(2200):.1f}" y="{Y(405):.1f}" class="nota">P3 0,90</text>')
# vigas bajas del ala (cubierta a +2,78): ejes G (y 341) y E (y 958) y eje 6
for (ya) in (341.4, 958.5): rect(1791,ya-10,2176,ya+10,'#8e44ad',op=.7)
rect(2183-7.5,334,2183+7.5,951,'#8e44ad',op=.7)
g.append(f'<text x="{X(1985):.1f}" y="{Y(341)-14:.1f}" class="viol" text-anchor="middle">viga RECT 200×150 a +2,78 (cubierta baja del ala)</text>')
# pilares
for pid,px,py,z0,z1,p in PIL:
    h=16 if 'HEB' in p else 15
    rect(px-h/2,py-h/2,px+h/2,py+h/2,'#E8893A',stroke='#1a1a1a')
    g.append(f'<text x="{X(px)+(14 if px<2000 else -14):.1f}" y="{Y(py)+4:.1f}" class="eje" text-anchor="{"start" if px<2000 else "end"}">{pid.split("-")[1]}</text>')
# plataforma y escalera
rect(*PL,'#3b4a5c',stroke='#8ec3ee'); g.append(f'<text x="{X((PL[0]+PL[2])/2):.1f}" y="{Y(495):.1f}" class="win" text-anchor="middle">plataforma</text><text x="{X((PL[0]+PL[2])/2):.1f}" y="{Y(515):.1f}" class="wins" text-anchor="middle">1,50 × 1,50 · +3,61</text>')
rect(X0,570,X1,940,'#33414f',stroke='#8ec3ee')
for k in range(NH+1):
    y=570+k*HUELLA; g.append(f'<line x1="{X(X0):.1f}" y1="{Y(y):.1f}" x2="{X(X1):.1f}" y2="{Y(y):.1f}" stroke="#d8d4cc" stroke-width="1"/>')
g.append(f'<line x1="{X(X0+75):.1f}" y1="{Y(930):.1f}" x2="{X(X0+75):.1f}" y2="{Y(590):.1f}" stroke="#E8E6E1" stroke-width="1.5" marker-end="url(#fl)"/><text x="{X(X1)+8:.1f}" y="{Y(760):.1f}" class="wins">sube: 16 huellas de 23,1 (avance 3,70)</text><text x="{X(X1)+8:.1f}" y="{Y(776):.1f}" class="wins">17 contrahuellas de 21,2 (3,61) · 44°</text>')
# baranda: lado oriente de la escalera + lados norte y oriente de la plataforma; entrada a la casa por el poniente
g.append(f'<polyline points="{X(X1):.1f},{Y(940):.1f} {X(X1):.1f},{Y(420):.1f} {X(X0):.1f},{Y(420):.1f}" fill="none" stroke="#f5c542" stroke-width="3"/><text x="{X(X1)+6:.1f}" y="{Y(520):.1f}" class="amar">baranda 1,00 (pasamanos, barra a 0,50 y rodapié)</text>')
g.append(f'<line x1="{X(X0):.1f}" y1="{Y(430):.1f}" x2="{X(X0-40):.1f}" y2="{Y(430):.1f}" stroke="#4A90D9" stroke-width="2" marker-end="url(#fla)"/><line x1="{X(X0):.1f}" y1="{Y(560):.1f}" x2="{X(X0-40):.1f}" y2="{Y(560):.1f}" stroke="#4A90D9" stroke-width="2" marker-end="url(#fla)"/><text x="{X(1766):.1f}" y="{Y(498):.1f}" class="azul" text-anchor="end">quiebre: entra al nivel 2 entre los pilares F2 y E4 (2,28 libres)</text>')
# cotas
def cota(x0,y0,x1,y1,txt,off=0,vert=False):
    if vert:
        g.append(f'<line x1="{X(x0)+off:.1f}" y1="{Y(y0):.1f}" x2="{X(x0)+off:.1f}" y2="{Y(y1):.1f}" stroke="#B9B5AD"/><text x="{X(x0)+off-5:.1f}" y="{Y((y0+y1)/2):.1f}" class="cota" text-anchor="middle" transform="rotate(-90 {X(x0)+off-5:.1f} {Y((y0+y1)/2):.1f})">{txt}</text>')
    else:
        g.append(f'<line x1="{X(x0):.1f}" y1="{Y(y0)+off:.1f}" x2="{X(x1):.1f}" y2="{Y(y0)+off:.1f}" stroke="#B9B5AD"/><text x="{X((x0+x1)/2):.1f}" y="{Y(y0)+off-5:.1f}" class="cota" text-anchor="middle">{txt}</text>')
cota(X0,975,X1,975,'1,50',off=0); cota(X1,975,2165,975,'2,19 libres para pasar al lado',off=0)
cota(2210,420,2210,570,'1,50',vert=True); cota(2210,570,2210,940,'3,70',vert=True); cota(2210,349,2210,420,'0,71',vert=True)
css='<style>text{font-family:-apple-system,Inter,Helvetica,sans-serif;fill:#E8E6E1}.t{font-size:22px;font-weight:600}.nota{font-size:12px;fill:#B9B5AD}.rec{font-size:12px;fill:#B9B5AD;font-weight:600}.eje{font-size:11px;fill:#E8893A;font-weight:600}.win{font-size:12px;fill:#fff;font-weight:700}.wins{font-size:11px;fill:#f3f3f3}.azul{font-size:11px;fill:#8ec3ee}.amar{font-size:11px;fill:#f5c542}.viol{font-size:11px;fill:#c39bd3}.cota{font-size:11px;fill:#B9B5AD}</style><defs><marker id="fl" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#E8E6E1"/></marker><marker id="fla" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#4A90D9"/></marker></defs>'
planta=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'+'\n'.join(g)+'</svg>'
# ---------- corte por la escalera (mirando al poniente): eje y horizontal (norte a la izquierda), z vertical ----------
g=[]; sc2=2.0; ML2=90; MT2=110; W2=int((1000-300)*sc2+2*ML2+80); H2=int((520+60)*sc2+MT2+80)
Xc=lambda y: ML2+(y-300)*sc2; Zc=lambda z: MT2+(520-z)*sc2
g.append(f'<rect x="0" y="0" width="{W2}" height="{H2}" fill="#0f1115"/><text x="{ML2}" y="40" class="t">Escalera de obra · corte mirando al poniente (norte a la izquierda)</text>')
g.append(f'<text x="{ML2}" y="64" class="nota">a la izquierda la sala de máquinas y el muro del eje G; arriba a la izquierda, el nivel 2 de la casa empieza detrás del plano del corte (la plataforma entra a él por el poniente) · la cubierta baja del ala (+2,88) tiene que quedar abierta sobre la escalera mientras se use</text>')
g.append(f'<rect x="0" y="{Zc(0):.1f}" width="{W2}" height="{Zc(-60)-Zc(0):.1f}" fill="#1e2a1e"/>')   # terreno/radier
# muros: eje G (334..349) y sur (940..965) hasta la cubierta del ala (+2,88); losa cubierta ala +2,78..2,88 (vigas RECT 200x150: 2,68..2,88)
g.append(f'<rect x="{Xc(334):.1f}" y="{Zc(288):.1f}" width="{15*sc2:.1f}" height="{288*sc2:.1f}" fill="#8a8780"/><rect x="{Xc(940):.1f}" y="{Zc(288):.1f}" width="{25*sc2:.1f}" height="{288*sc2:.1f}" fill="#8a8780"/>')
g.append(f'<rect x="{Xc(331):.1f}" y="{Zc(288):.1f}" width="{20*sc2:.1f}" height="{20*sc2:.1f}" fill="#8e44ad"/><rect x="{Xc(948):.1f}" y="{Zc(288):.1f}" width="{20*sc2:.1f}" height="{20*sc2:.1f}" fill="#8e44ad"/>')
g.append(f'<line x1="{Xc(349):.1f}" y1="{Zc(288):.1f}" x2="{Xc(430):.1f}" y2="{Zc(288):.1f}" stroke="#c39bd3" stroke-width="3"/><line x1="{Xc(850):.1f}" y1="{Zc(288):.1f}" x2="{Xc(940):.1f}" y2="{Zc(288):.1f}" stroke="#c39bd3" stroke-width="3"/><line x1="{Xc(430):.1f}" y1="{Zc(288):.1f}" x2="{Xc(850):.1f}" y2="{Zc(288):.1f}" stroke="#c39bd3" stroke-width="2" stroke-dasharray="6 5"/>')
g.append(f'<text x="{Xc(640):.1f}" y="{Zc(288)-8:.1f}" class="viol" text-anchor="middle">cubierta baja del ala a +2,88 (vigas RECT 200×150 del ingeniero a +2,78): hueco de 1,5 × 4,2 sobre la escalera y la plataforma</text>')
# nivel 2 detrás del plano (muro de la casa está en x 1771..1796, la escalera en 1796..1946): losa a 3,46..3,61 desde y 300 hasta 1000 como referencia tenue
g.append(f'<rect x="{Xc(300):.1f}" y="{Zc(361):.1f}" width="{(1000-300)*sc2:.1f}" height="{15*sc2:.1f}" fill="#4a4d53" opacity=".55"/><text x="{Xc(760):.1f}" y="{Zc(361)-6:.1f}" class="azul">losa del nivel 2 detrás del muro de la casa: +3,46 placa · +3,61 hormigón (la plataforma llega a ese nivel)</text>')
# escalera: peldaños
pts=[]
for k in range(NC):
    y0=940-k*HUELLA; y1=y0-HUELLA; z=(k+1)*CH
    g.append(f'<rect x="{Xc(y1):.1f}" y="{Zc(z):.1f}" width="{HUELLA*sc2:.1f}" height="{CH*sc2:.1f}" fill="#33414f" stroke="#d8d4cc" stroke-width="1"/>') if k<NH else None
# plataforma
g.append(f'<rect x="{Xc(420):.1f}" y="{Zc(361):.1f}" width="{150*sc2:.1f}" height="{12*sc2:.1f}" fill="#3b4a5c" stroke="#8ec3ee" stroke-width="1.5"/><text x="{Xc(495):.1f}" y="{Zc(361)+30:.1f}" class="win" text-anchor="middle">plataforma 1,50 · +3,61</text>')
# zancas (línea bajo los peldaños) y postes de la plataforma
g.append(f'<line x1="{Xc(940):.1f}" y1="{Zc(0):.1f}" x2="{Xc(570):.1f}" y2="{Zc(349):.1f}" stroke="#8ec3ee" stroke-width="4" opacity=".8"/><text x="{Xc(800):.1f}" y="{Zc(120):.1f}" class="azul" transform="rotate(-44 {Xc(800):.1f} {Zc(120):.1f})">zancas C 200×50×4 · peldaños plancha estriada 4 mm</text>')
for yy in (428,562): g.append(f'<rect x="{Xc(yy)-5:.1f}" y="{Zc(349):.1f}" width="10" height="{349*sc2:.1f}" fill="#8ec3ee" opacity=".8"/>')
g.append(f'<text x="{Xc(495):.1f}" y="{Zc(170):.1f}" class="azul" text-anchor="middle">2 postes tubo 100×100×3 (el lado poniente va anclado a la viga IPE 270 del eje 5)</text>')
# baranda: a 1,00 sobre peldaños y plataforma
g.append(f'<line x1="{Xc(940):.1f}" y1="{Zc(100):.1f}" x2="{Xc(570):.1f}" y2="{Zc(461):.1f}" stroke="#f5c542" stroke-width="3"/><line x1="{Xc(570):.1f}" y1="{Zc(461):.1f}" x2="{Xc(420):.1f}" y2="{Zc(461):.1f}" stroke="#f5c542" stroke-width="3"/><line x1="{Xc(420):.1f}" y1="{Zc(461):.1f}" x2="{Xc(420):.1f}" y2="{Zc(361):.1f}" stroke="#f5c542" stroke-width="3"/>')
for k in range(0,NH+1,4):
    y=940-k*HUELLA; z=k*CH; g.append(f'<line x1="{Xc(y):.1f}" y1="{Zc(z):.1f}" x2="{Xc(y):.1f}" y2="{Zc(z+100):.1f}" stroke="#f5c542" stroke-width="2"/>')
g.append(f'<text x="{Xc(620):.1f}" y="{Zc(430):.1f}" class="amar">baranda 1,00 · pasamanos tubo 50×2 · barra a 0,50 · postes tubo 50×50×3 cada 1,2 m</text>')
# cotas
g.append(f'<line x1="{Xc(570):.1f}" y1="{Zc(-30):.1f}" x2="{Xc(940):.1f}" y2="{Zc(-30):.1f}" stroke="#B9B5AD"/><text x="{Xc(755):.1f}" y="{Zc(-30)-5:.1f}" class="cota" text-anchor="middle">avance 3,70 = 16 × 23,1</text>')
g.append(f'<line x1="{Xc(420):.1f}" y1="{Zc(-30):.1f}" x2="{Xc(570):.1f}" y2="{Zc(-30):.1f}" stroke="#B9B5AD"/><text x="{Xc(495):.1f}" y="{Zc(-30)-5:.1f}" class="cota" text-anchor="middle">1,50</text>')
g.append(f'<line x1="{Xc(995):.1f}" y1="{Zc(0):.1f}" x2="{Xc(995):.1f}" y2="{Zc(361):.1f}" stroke="#B9B5AD"/><text x="{Xc(995)-6:.1f}" y="{Zc(180):.1f}" class="cota" transform="rotate(-90 {Xc(995)-6:.1f} {Zc(180):.1f})" text-anchor="middle">3,61 = 17 × 21,2 (44°)</text>')
g.append(f'<text x="{Xc(300):.1f}" y="{Zc(0)+16:.1f}" class="nota">±0,00 piso terminado de la bodega (si la escalera parte del radier, ≈20 más abajo, el alto queda en tus 3,80: se agrega un peldaño)</text>')
corte=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W2}" height="{H2}" viewBox="0 0 {W2} {H2}">'+'\n'.join(g)+'</svg>'
html=f'<!doctype html><html><head><meta charset="utf-8">{css}<style>body{{margin:0;background:#0f1115}} svg{{display:block}}</style></head><body>{planta}{corte}</body></html>'
open(S+'/escalera.html','w',encoding='utf-8').write(html); print('dims', W, H+H2)
