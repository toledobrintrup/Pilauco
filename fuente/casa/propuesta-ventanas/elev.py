# -*- coding: utf-8 -*-
"""Elevaciones de la propuesta de ventanas (vistas verdaderas, desde afuera), con el plano actual en gris punteado."""
import json, re
R='/Users/toledobrintrup/Coding/Pilauco'; S='/private/tmp/claude-501/-Users-toledobrintrup-Coding-Pilauco/336a464c-579a-4405-af69-f1b1813fc385/scratchpad/prop'
D=json.load(open(S+'/propuesta.json',encoding='utf-8')); ACT=D['actual']; PROP=D['propuesta']; CIEGOS=D.get('ciegos',[])
E=json.loads(re.search(r'const DATA_ESTRUCTURA = (\{.*\});?\s*$', open(R+'/estructura.js',encoding='utf-8').read(), re.S).group(1))
T=E['techo']; techo=lambda y: T['z0']+(T['z1']-T['z0'])*(max(T['y0'],min(T['y1'],y))-T['y0'])/(T['y1']-T['y0'])
PIL=[(m['id'],m['a'][0],m['a'][1],m['a'][2]) for m in E['miembros'] if m['c']=='pilar']
N1T,LOSA0,N2F=368,368,395; BANDA=50; ALA_TOP=300   # nivel 1 de 3,80 a la viga (medido en terreno): losa de 12 bajo 3,80, piso del nivel 2 a 3,95; cubierta baja del ala a +3,00 (vigas RECT 200×150 a +2,78)
sc=0.56; ML=160; MT=130; MB=150
def planos(f):
    # (coordenada perpendicular de la cara exterior, nivel, rango a lo largo, nota, recintos [(lo,hi,nombre)])
    if f=='norte': return [
        (245,'N1',(660,1249),'cocina retranqueada 2,35 m bajo el nivel 2',[(660,1249,'Cocina')]),
        (-2.6,'N1',(0,660),'bajo la terraza del nivel 2: porche cubierto de 7,85 m',[(30,390,'Oficina'),(405,645,'Galería')]),
        (-2.6,'N1',(1249,1790),'',[(1264,1775,'Lavandería')]),
        (-2.6,'N2',(0,1796),'pasillo-balcón de ≈1,75 m corrido por toda la fachada (baranda de vidrio), que lleva a la terraza grande',[(25,646,'Dorm. matrimonial'),(661,1000,'WKC Gabriel'),(1015,1765,'WKC Maggie')]),
        (-182.5,'ALA',(1771,2196),'sala de máquinas (sale 1,8 m)',[(1790,2165,'Sala de máquinas')])]
    if f=='sur': return [
        (965,'ALA',(1771,2196),'bodega (ala oriente)',[(1790,2165,'Bodega')]),
        (1521.9,'N1',(994.7,1796),'comedor, 5,4 m atrás, bajo el acceso cubierto',[(989,1765,'Comedor')]),
        (1704.7,'N1',(-5.8,665.7),'living',[(25,671,'Living')]),
        (1842.8,'N2',(-5.8,665.7),'nivel 2 vuela 1,4 m sobre el living',[(25,367,'Dorm. visitas'),(382,646,'Family room')]),
        (2057.7,'N2',(994.7,1796),'nivel 2 sobre el acceso cubierto',[(1015,1282,'WKC hijo 2'),(1282,1765,'Dorm. hijo 2')]),
        (2182.8,'HALL',(640.7,1019.7),'hall de acceso (doble altura)',[(671,989,'Hall')])]
    if f=='oriente': return [
        (2195.8,'ALA',(-182.5,965),'ala oriente de un piso: sala de máquinas y bodega',[(-152,334,'Sala de máquinas'),(349,940,'Bodega')]),
        (1796.2,'N1',(946,1521.9),'',[(966,1097,'Chiflonera'),(1112,1493,'Comedor')]),
        (1796.2,'N2',(-2.6,2057.7),'',[(25,512,'WKC Maggie'),(527,1135,'Dorm. hijo 1'),(1150,1409,'Baño hijos'),(1424,2024,'Dorm. hijo 2')]),
        (1019.7,'HALL',(1521.9,2182.8),'hall de acceso, 7,8 m atrás (acceso cubierto al frente)',[(1493,2159,'Hall · entrada')])]
    if f=='poniente': return [
        (-5.8,'N1',(-2.6,1704.7),'',[(25,618,'Oficina'),(633,1676,'Living')]),
        (-5.8,'N2',(-2.6,1842.8),'',[(25,550,'Dorm. matrimonial'),(564,871,'Baño matrimonial'),(886,1271,'Baño visitas'),(1286,1812,'Dorm. visitas')]),
        (640.7,'HALL',(1704.7,2182.8),'hall de acceso, 6,5 m atrás',[(1676,2159,'Hall')])]
def depth(f,pc):  # distancia al observador (mayor = más lejos)
    return {'norte':pc,'sur':-pc,'oriente':-pc,'poniente':pc}[f]
TONOS=['#a6a299','#8f8b83','#78756e','#605e58','#4c4a45']
def dibujar(f):
    g=[]; W={'norte':(0,2196),'sur':(-6,2196),'oriente':(-183,2183),'poniente':(-790,2183)}[f]
    rev = f in ('norte','poniente')
    L=W[1]-W[0]; wpx=L*sc+2*ML
    X=lambda c: ML+((W[1]-c) if rev else (c-W[0]))*sc
    ztop=830; Y=lambda z: MT+(ztop-z)*sc; hpx=Y(-80)+MB
    g.append(f'<rect x="0" y="0" width="{wpx:.0f}" height="{hpx:.0f}" fill="#0f1115"/>')
    g.append(f'<rect x="0" y="{Y(0)}" width="{wpx:.0f}" height="{80*sc}" fill="#1e2a1e"/>')
    pls=planos(f)
    ds=sorted(set(depth(f,p[0]) for p in pls)); tono={d:TONOS[min(len(TONOS)-1, int(round(i*(len(TONOS)-1)/max(1,len(ds)-1))))] for i,d in enumerate(ds)}
    # lejanos primero
    for (pc,niv,(a,b),nota,recs) in sorted(pls,key=lambda p:-depth(f,p[0])):
        tn=tono[depth(f,pc)]; x0=min(X(a),X(b)); w=abs(X(b)-X(a))
        if niv=='ALA':
            g.append(f'<rect x="{x0:.1f}" y="{Y(ALA_TOP)}" width="{w:.1f}" height="{ALA_TOP*sc:.1f}" fill="{tn}" stroke="#1a1a1a" stroke-width="1"/>')
            g.append(f'<rect x="{x0:.1f}" y="{Y(ALA_TOP)}" width="{w:.1f}" height="{15*sc:.1f}" fill="#4a4d53"/>')
        elif niv=='N1':
            g.append(f'<rect x="{x0:.1f}" y="{Y(N1T)}" width="{w:.1f}" height="{N1T*sc:.1f}" fill="{tn}" stroke="#1a1a1a" stroke-width="1"/>')
        else:
            z0=0 if niv=='HALL' else N2F
            if f in ('norte','sur'):
                zt=techo(pc); pts=[(a,z0),(b,z0),(b,zt),(a,zt)]
            else:
                pts=[(a,z0),(b,z0),(b,techo(b)),(a,techo(a))]
            g.append('<polygon points="'+' '.join(f'{X(x):.1f},{Y(z):.1f}' for x,z in pts)+f'" fill="{tn}" stroke="#1a1a1a" stroke-width="1"/>')
            tz=lambda c: techo(pc) if f in ('norte','sur') else techo(c)
            pts=[(a,tz(a)-BANDA),(b,tz(b)-BANDA),(b,tz(b)),(a,tz(a))]
            g.append('<polygon points="'+' '.join(f'{X(x):.1f},{Y(z):.1f}' for x,z in pts)+'" fill="url(#viga)" opacity=".9"/>')
            if niv=='N2': g.append(f'<rect x="{x0:.1f}" y="{Y(N2F)}" width="{w:.1f}" height="{(N2F-LOSA0+15)*sc:.1f}" fill="#4a4d53"/>')  # losa + hormigón
        for lo,hi,nm in recs:
            if niv=='N2':
                zt=techo(pc) if f in ('norte','sur') else techo((lo+hi)/2)
                g.append(f'<text x="{(X(lo)+X(hi))/2:.1f}" y="{Y(zt)-8:.1f}" class="rec" text-anchor="middle">{nm}</text>')
            else:
                g.append(f'<text x="{(X(lo)+X(hi))/2:.1f}" y="{Y(-22):.1f}" class="rec" text-anchor="middle">{nm}</text>')
        if nota:
            yy = (Y(techo(pc) if f in ('norte','sur') else techo((a+b)/2))-24) if niv=='N2' else Y(-48)
            g.append(f'<text x="{(X(a)+X(b))/2:.1f}" y="{yy:.1f}" class="nota" text-anchor="middle">{nota}</text>')
    # terraza norte (nivel 2) a +3,80 (placa) / +3,95 (piso): losa, baranda y sus 2 pilares (columns de DATA_N2.terrace)
    if f=='norte':
        g.append(f'<rect x="{min(X(590),X(660)):.1f}" y="{Y(ALA_TOP)}" width="{abs(X(660)-X(590)):.1f}" height="{ALA_TOP*sc:.1f}" fill="#7a5248"/>')
        g.append(f'<rect x="{min(X(40),X(660)):.1f}" y="{Y(395)}" width="{abs(X(660)-X(40)):.1f}" height="{15*sc:.1f}" fill="#5c6168" stroke="#1a1a1a"/><line x1="{X(46)}" y1="{Y(500)}" x2="{X(653)}" y2="{Y(500)}" stroke="#d8d4cc" stroke-width="1.4"/>')
        for xx in (46,653): g.append(f'<line x1="{X(xx)}" y1="{Y(500)}" x2="{X(xx)}" y2="{Y(395)}" stroke="#d8d4cc" stroke-width="1.2"/>')
        g.append(f'<rect x="{min(X(652),X(1783)):.1f}" y="{Y(500)}" width="{abs(X(1783)-X(652)):.1f}" height="{105*sc:.1f}" fill="#8ec3ee" opacity=".25" stroke="#d8d4cc" stroke-width="1"/><rect x="{min(X(652),X(1783)):.1f}" y="{Y(395)}" width="{abs(X(1783)-X(652)):.1f}" height="{15*sc:.1f}" fill="#5c6168" stroke="#1a1a1a"/>')
    if f=='poniente':
        for ya,yb in ((-785,-715),(-205,-135)): g.append(f'<rect x="{min(X(ya),X(yb)):.1f}" y="{Y(ALA_TOP)}" width="{abs(X(yb)-X(ya)):.1f}" height="{ALA_TOP*sc:.1f}" fill="#7a5248"/>')
        g.append(f'<rect x="{min(X(-785),X(0)):.1f}" y="{Y(395)}" width="{abs(X(0)-X(-785)):.1f}" height="{15*sc:.1f}" fill="#5c6168" stroke="#1a1a1a"/><line x1="{X(-748)}" y1="{Y(500)}" x2="{X(-203)}" y2="{Y(500)}" stroke="#d8d4cc" stroke-width="1.4"/><line x1="{X(-748)}" y1="{Y(500)}" x2="{X(-748)}" y2="{Y(395)}" stroke="#d8d4cc" stroke-width="1.2"/>')
        g.append(f'<text x="{(X(-785)+X(0))/2:.1f}" y="{Y(300):.1f}" class="nota" text-anchor="middle">terraza norte del nivel 2 · porche de 7,85 m abajo</text>')
    # pilares del ingeniero en la fachada
    for pid,px,py,pz in PIL:
        c=None
        if f=='norte' and abs(py-9.9)<3: c=px
        if f=='norte' and abs(py+170)<3 and px>1700: c=px
        if f=='sur' and (abs(py-2170.3)<3 or abs(py-2045.2)<3): c=px
        if f=='oriente' and (abs(px-1783.7)<3 or abs(px-2183.3)<3): c=py
        if f=='poniente' and abs(px-6.7)<3 and py>-20: c=py
        if c is None: continue
        n1=pz<15; z0=0 if n1 else N2F
        yt = techo(py) if f in ('oriente','poniente') else techo(9.9 if f=='norte' else (2182.8 if abs(py-2170.3)<3 else 2057.7))
        z1=N1T if n1 else yt-BANDA
        g.append(f'<line x1="{X(c):.1f}" y1="{Y(z0):.1f}" x2="{X(c):.1f}" y2="{Y(z1):.1f}" stroke="#E8893A" stroke-width="1.6" stroke-dasharray="7 4" opacity=".9"/>')
        if n1:
            ej=pid.split('-')[1]; ej = ej.split('x')[0] if f in ('norte','sur') else ej.split('x')[1]
            g.append(f'<text x="{X(c):.1f}" y="{Y(N1T)+11:.1f}" class="eje" text-anchor="middle">{ej}</text>')
    # paños ciegos por cruces y celosías del ingeniero
    for fach,niv,lo,hi,tipo in CIEGOS:
        if fach!=f: continue
        z0=0 if niv==1 else N2F
        if f in ('norte','sur'): z1=N1T if niv==1 else techo(10)-BANDA
        else: z1=N1T if niv==1 else techo((lo+hi)/2)-BANDA
        x0=min(X(lo),X(hi)); w=abs(X(hi)-X(lo))
        g.append(f'<rect x="{x0:.1f}" y="{Y(z1):.1f}" width="{w:.1f}" height="{(z1-z0)*sc:.1f}" fill="#2b2e35" opacity=".85"/>')
        g.append(f'<line x1="{x0:.1f}" y1="{Y(z1):.1f}" x2="{x0+w:.1f}" y2="{Y(z0):.1f}" stroke="#E8893A" stroke-width="1.4" opacity=".9"/><line x1="{x0:.1f}" y1="{Y(z0):.1f}" x2="{x0+w:.1f}" y2="{Y(z1):.1f}" stroke="#E8893A" stroke-width="1.4" opacity=".9"/>')
        g.append(f'<text x="{x0+w/2:.1f}" y="{Y((z0+z1)/2)+4:.1f}" class="eje" text-anchor="middle">{tipo}</text>')
    # ventanas: actual (gris punteado) y propuesta (rellena)
    col={'ventana':'#4A90D9','corredera':'#4A90D9','doble altura':'#5aa4e6','puerta vidriada':'#5aa4e6','franja alta':'#8ec3ee','ventana alta':'#8ec3ee','puerta':'#8B6A45','celosía':'#7a7a7a'}
    for fach,niv,rec,lo,hi,(z0,z1),tipo,plano,*rest in ACT:
        if fach!=f: continue
        base=N2F if niv==2 else 0
        g.append(f'<rect x="{min(X(lo),X(hi)):.1f}" y="{Y(base+z1):.1f}" width="{abs(X(hi)-X(lo)):.1f}" height="{(z1-z0)*sc:.1f}" fill="none" stroke="#e8e6e1" stroke-width="1.3" stroke-dasharray="4 3" opacity=".85"/>')
    for fach,niv,rec,lo,hi,(z0,z1),tipo,plano,nota in PROP:
        if fach!=f: continue
        base=N2F if niv==2 else 0; x0=min(X(lo),X(hi)); w=abs(X(hi)-X(lo))
        g.append(f'<rect x="{x0:.1f}" y="{Y(base+z1):.1f}" width="{w:.1f}" height="{(z1-z0)*sc:.1f}" fill="{col[tipo]}" opacity="{0.6 if tipo=="celosía" else 0.9}" stroke="#15171b" stroke-width="2"/>')
        if 'satinado' in nota: g.append(f'<rect x="{x0:.1f}" y="{Y(base+180):.1f}" width="{w:.1f}" height="{180*sc:.1f}" fill="#8ec3ee" opacity=".9"/>')
        if tipo=='corredera': g.append(f'<line x1="{x0+w/2:.1f}" y1="{Y(base+z1):.1f}" x2="{x0+w/2:.1f}" y2="{Y(base+z0):.1f}" stroke="#15171b" stroke-width="2"/>')
        if tipo in ('puerta','puerta vidriada'): g.append(f'<circle cx="{x0+w*0.8:.1f}" cy="{Y(base+100):.1f}" r="2.2" fill="#eee"/>')
        code=nota.split(' · ')[0]; medidas=f'{(hi-lo)/100:.2f} × {(z1-z0)/100:.2f}'.replace('.',',')
        if (z1-z0)*sc>40 and w>26:
            g.append(f'<text x="{x0+w/2:.1f}" y="{Y(base+(z0+z1)/2)-2:.1f}" class="win" text-anchor="middle">{code}</text><text x="{x0+w/2:.1f}" y="{Y(base+(z0+z1)/2)+12:.1f}" class="wins" text-anchor="middle">{medidas}</text>')
        else:
            g.append(f'<text x="{x0+w/2:.1f}" y="{Y(base+z1)-4:.1f}" class="wins" text-anchor="middle">{code} {medidas}</text>')
    for z,t in ((0,'±0,00 piso nivel 1'),(N2F,'+3,95 piso nivel 2')):
        g.append(f'<line x1="{ML-40}" y1="{Y(z):.1f}" x2="{ML-8}" y2="{Y(z):.1f}" stroke="#b9b5ad"/><text x="{ML-44}" y="{Y(z)+4:.1f}" class="nota" text-anchor="end">{t}</text>')
    izq={'norte':'izquierda = oriente · derecha = poniente','sur':'izquierda = poniente · derecha = oriente','oriente':'izquierda = norte · derecha = sur','poniente':'izquierda = sur · derecha = norte'}[f]
    tit={'norte':'Fachada norte (patio, sol)','sur':'Fachada sur (acceso y camino)','oriente':'Fachada oriente (sol de la mañana)','poniente':'Fachada poniente (sol de la tarde)'}[f]
    g.append(f'<text x="{ML}" y="34" class="t">{tit} · propuesta de ventanas</text>')
    g.append(f'<text x="{ML}" y="58" class="nota">vista desde afuera ({izq}) · planos más lejanos en gris más oscuro · gris punteado = ventanas del plano de hoy · azul = propuesta · celeste = vidrio satinado (baños) · café = puertas</text>')
    g.append(f'<text x="{ML}" y="76" class="nota">naranjo punteado = pilares del ingeniero (eje) · X naranja = paño ciego por cruz o celosía del ingeniero · achurado = vigas y costaneras bajo el techo</text>')
    g.append(f'<text x="{ML}" y="94" class="nota">todas iguales por nivel: nivel 1 de 3,40, lo máximo bajo la viga (el nivel 1 mide 3,80 a la viga, medido en terreno) · nivel 2 de 2,80 (el nivel 2 queda con 3,00 libres en el norte: techo 20 cm más alto, misma pendiente) · punto blanco = hoja que abre</text>')
    legy=hpx-40
    for i,(c,t) in enumerate((('#4A90D9','ventana / ventanal piso a cielo'),('#8ec3ee','vidrio satinado hasta 1,8 (baños)'),('#5aa4e6','puerta vidriada / doble altura'),('#8B6A45','puerta'))):
        g.append(f'<rect x="{ML+i*300}" y="{legy-11}" width="16" height="12" fill="{c}"/><text x="{ML+i*300+22}" y="{legy}" class="nota">{t}</text>')
    css='<style>text{font-family:-apple-system,Inter,Helvetica,sans-serif;fill:#E8E6E1}.t{font-size:22px;font-weight:600}.nota{font-size:12px;fill:#B9B5AD}.rec{font-size:12px;fill:#E8E6E1;font-weight:600}.eje{font-size:10px;fill:#E8893A;font-weight:600}.win{font-size:11px;fill:#fff;font-weight:700}.wins{font-size:10px;fill:#f3f3f3}</style><defs><pattern id="viga" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="8" height="8" fill="#5a564f"/><line x1="0" y1="0" x2="0" y2="8" stroke="#8e44ad" stroke-width="2"/></pattern></defs>'
    html=f'<!doctype html><html><head><meta charset="utf-8">{css}<style>body{{margin:0;background:#0f1115}}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" width="{wpx:.0f}" height="{hpx:.0f}" viewBox="0 0 {wpx:.0f} {hpx:.0f}">'+'\n'.join(g)+'</svg></body></html>'
    open(f'{S}/elev_{f}.html','w',encoding='utf-8').write(html); return int(wpx),int(hpx)
dims={f:dibujar(f) for f in ('norte','sur','oriente','poniente')}
json.dump(dims,open(S+'/dims.json','w')); print(dims)
