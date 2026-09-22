# -*- coding: utf-8 -*-
"""Nivel 1 -> bloque de datos de la pagina (mismo esquema que el nivel 2)."""
import json, math, bisect
import numpy as np, cv2
from shapely.geometry import Polygon, Point, LineString

g=json.load(open('n1_geom.json')); L=json.load(open('n1_layers_cm.json'))
WORDS=json.load(open('n1_words.json')); VANOS=json.load(open('n1_vanos.json'))
segs=g['segs']; PX,OFF,W,H=4,40,2200,2190
SH=(H*PX+2*PX*OFF, W*PX+2*PX*OFF); px=lambda v:int(round((v+OFF)*PX))
VX=sorted(set(round(s[0],2) for s in segs if abs(s[0]-s[2])<0.05))
HY=sorted(set(round(s[1],2) for s in segs if abs(s[1]-s[3])<0.05))
def snap(v,arr,tol=2.0):
    i=bisect.bisect_left(arr,v); best=None
    for j in (i-1,i):
        if 0<=j<len(arr) and abs(arr[j]-v)<=tol:
            if best is None or abs(arr[j]-v)<abs(best-v): best=arr[j]
    return best if best is not None else v
def quita_colineales(out):
    ch=True
    while ch:
        ch=False; res=[]; n=len(out)
        for k in range(n):
            p0,p1,p2=out[k-1],out[k],out[(k+1)%n]
            if (abs(p1[0]-p0[0])<0.6 and abs(p1[0]-p2[0])<0.6) or (abs(p1[1]-p0[1])<0.6 and abs(p1[1]-p2[1])<0.6):
                ch=True; continue
            res.append(p1)
        out=res
    return out
def quita_espigas(out):
    """Las hojas de puerta rasterizadas dejan espigas: el contorno sale de la linea de
    muro, rodea la hoja y vuelve al mismo punto. Se reemplazan por el tramo recto."""
    from shapely.geometry import Polygon as _P
    cambio=True
    while cambio and len(out)>6:
        cambio=False; n=len(out)
        for i in range(n):
            for salto in range(min(30,n-2), 2, -1):
                j=(i+salto)%n
                a,b=out[i],out[j]
                if not (abs(a[0]-b[0])<1.2 or abs(a[1]-b[1])<1.2): continue
                inter=[out[(i+t)%n] for t in range(1,salto)]
                recto=math.hypot(b[0]-a[0], b[1]-a[1])
                if recto<8: continue
                camino=sum(math.hypot(p2[0]-p1[0],p2[1]-p1[1])
                           for p1,p2 in zip([a]+inter, inter+[b]))
                if camino < 1.5*recto: continue
                # Firma del barrido de puerta: la muesca incluye un tramo en diagonal.
                # Un nicho real del plano es ortogonal y no se toca.
                if not any(abs(p1[0]-p2[0])>0.01 and abs(p1[1]-p2[1])>0.01
                           for p1,p2 in zip([a]+inter, inter+[b])): continue
                try: area=_P([a]+inter+[b]).buffer(0).area
                except Exception: continue
                if area > 25000: continue            # 2,5 m2
                out=[out[(j+t)%n] for t in range(n-salto+1)]
                cambio=True; break
            if cambio: break
    return out
def clean_poly(pts):
    pts=[(round(snap(a,VX),1),round(snap(b,HY),1)) for a,b in pts]
    out=[]
    for p in pts:
        if out and abs(out[-1][0]-p[0])<0.6 and abs(out[-1][1]-p[1])<0.6: continue
        out.append(p)
    out=quita_colineales(out)
    # Las hojas de puerta rasterizadas dejan dientes de pocos cm: se eliminan los
    # tramos < 6 cm y se vuelve a colapsar lo colineal.
    ch=True
    while ch and len(out)>4:
        ch=False
        for k in range(len(out)):
            a,b=out[k],out[(k+1)%len(out)]
            if math.hypot(b[0]-a[0],b[1]-a[1])<6:
                del out[(k+1)%len(out)]; out=quita_colineales(out); ch=True; break
    out=quita_colineales(quita_espigas(out))
    ch=True
    while ch:
        ch=False; res=[]; n=len(out)
        for k in range(n):
            p0,p1,p2=out[k-1],out[k],out[(k+1)%n]
            if (abs(p1[0]-p0[0])<0.6 and abs(p1[0]-p2[0])<0.6) or (abs(p1[1]-p0[1])<0.6 and abs(p1[1]-p2[1])<0.6):
                ch=True; continue
            res.append(p1)
        out=res
    return out

def cierres_puerta(items, muros):
    """Cierra cada vano de puerta con la recta entre jambas.

    El barrido es un cuarto de circunferencia con centro en la bisagra H y radio R:
    va de la punta de la hoja T (dentro del recinto) a la otra jamba J (sobre el muro).
    Con los extremos del arco, H es una de las dos esquinas del cuadrado que forman;
    la buena es la que cae sobre el muro. El vano es el tramo H-J.

    No sirve emparejar el arco con la hoja: las hojas van dibujadas como rectangulos y
    el extremo mas cercano suele ser un lado corto de 8 cm, no la bisagra.
    """
    from shapely.geometry import LineString as _LS
    segs=[]
    for cu in [it for it in items if it[0]=='c']:
        P0,P3=cu[1],cu[4]
        cands=[((P3[0],P0[1]),P3), ((P0[0],P3[1]),P3), ((P0[0],P3[1]),P0), ((P3[0],P0[1]),P0)]
        mejor=None
        for H,J in cands:
            if abs(H[0]-J[0])>0.01 and abs(H[1]-J[1])>0.01: continue   # H-J debe ir sobre el muro
            if math.hypot(H[0]-J[0],H[1]-J[1])<20: continue
            # Las dos jambas tocan muro; el centro del vano no, porque es el hueco.
            d=max(muros.distance(Point(*H)), muros.distance(Point(*J)))
            if mejor is None or d<mejor[0]: mejor=(d,H,J)
        if mejor and mejor[0]<4: segs.append((mejor[1],mejor[2]))
    return segs

from shapely.ops import unary_union as _uu
_MUROS=_uu([Polygon(w['pts']).buffer(0) for w in g['walls'] if len(w['pts'])>=4])
PUERTAS=cierres_puerta(L.get('(0.23, 0.53)',[]), _MUROS)
print('  puertas cerradas con recta entre jambas:', len(PUERTAS))

img=np.zeros(SH,np.uint8)
for w in g['walls']: cv2.fillPoly(img,[np.array([(px(x),px(y)) for x,y in w['pts']],np.int32)],255)
for o in VANOS: cv2.fillPoly(img,[np.array([(px(x),px(y)) for x,y in o['quad']],np.int32)],255)
for k in ['(0.43, 0.5)','(0.28, 0.53)','(0.23, 0.53)','(0.43, 0.0)']:
    for it in L.get(k,[]):
        if it[0]=='l': cv2.line(img,(px(it[1][0]),px(it[1][1])),(px(it[2][0]),px(it[2][1])),255,2)
        elif it[0]=='re': cv2.rectangle(img,(px(it[1][0]),px(it[1][1])),(px(it[2][0]),px(it[2][1])),255,2)
        elif it[0]=='c': cv2.line(img,(px(it[1][0]),px(it[1][1])),(px(it[4][0]),px(it[4][1])),255,2)
img=cv2.morphologyEx(img,cv2.MORPH_CLOSE,np.ones((13,13),np.uint8))
n,lab,stats,cent=cv2.connectedComponentsWithStats((img==0).astype(np.uint8),connectivity=4)
fuera=lab[2,2]

# El PDF trae cada nombre en un solo span ('SALA DE MAQUINAS', 'BAÑO 1', ...).
TOK={'TERRAZA':'TERRAZA INTERIOR','COCINA':'COCINA','LAVANDERIA':'LAVANDERÍA','DESPENSA':'DESPENSA',
     'BODEGA':'BODEGA','SALA DE MAQUINAS':'SALA DE MÁQUINAS','BAÑO 1':'BAÑO 1','CHIFLONERA':'CHIFLONERA',
     'ESTAR 1':'ESTAR 1','COMEDOR':'COMEDOR','HALL DE ACCESO':'HALL DE ACCESO'}
ORDEN=['ESTAR 1','COMEDOR','HALL DE ACCESO']
pal=[w for w in WORDS if 7<w['size']<9 and w['t'] in TOK]
KIND={'TERRAZA INTERIOR':'terraza','COCINA':'cocina','LAVANDERÍA':'serv','DESPENSA':'serv','BODEGA':'serv',
      'SALA DE MÁQUINAS':'serv','BAÑO 1':'bano','CHIFLONERA':'serv'}
rooms=[]
for i in range(1,n):
    if i==fuera: continue
    x,y,w,h,area=stats[i]; a=area/PX/PX/1e4
    if a<2.0: continue
    m=(lab==i)
    cnts,_=cv2.findContours(m.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    pts=clean_poly([(p[0][0]/PX-OFF,p[0][1]/PX-OFF) for p in cv2.approxPolyDP(max(cnts,key=cv2.contourArea),1.5,True)])
    dentro=[(e['x'],TOK[e['t']]) for e in pal if 0<=px(e['y'])<SH[0] and 0<=px(e['x'])<SH[1] and m[px(e['y']),px(e['x'])]]
    vistos=[]; [vistos.append(t) for _,t in sorted(dentro) if t not in vistos]
    if len(vistos)>1: vistos=sorted(vistos, key=lambda t: ORDEN.index(t) if t in ORDEN else 99)
    lb=[dict(x=round(e['x'],1), y=round(e['y'],1), t=TOK[e['t']]) for e in pal
        if TOK[e['t']] in vistos and 0<=px(e['y'])<SH[0] and 0<=px(e['x'])<SH[1] and m[px(e['y']),px(e['x'])]]
    rooms.append(dict(pts=pts, nombres=vistos, labels=lb))
rooms.sort(key=lambda r:-Polygon(r['pts']).area)

# ---- espesores normalizados: perimetrales 25, interiores 15 ----
from n1_engrosar import engrosar
antes={(' · '.join(r['nombres']) or '?'): round(Polygon(r['pts']).area/1e4,2) for r in rooms}
rooms, MUROS, VENT_NUEVAS = engrosar(rooms, g['walls'])
# ---------- como construido (difiere del plano de permiso) ----------
# En obra la lavanderia se adelanto hasta el eje H (la linea de la fachada norte
# principal) y la sala de maquinas hasta el eje I1 (la linea de pilares de la
# terraza: se cerro esa crujia). La cara interior queda a 17,9 cm del eje, que es
# la relacion que el propio plano usa en toda la fachada.
from shapely.geometry import box as _box
from shapely.ops import unary_union as _uu2
EJE_H, EJE_I1 = 7.1, -169.8
CARA = 17.9
OBRA = [dict(nom='LAVANDERÍA',       viejo=125.5, nuevo=round(EJE_H+CARA,1),  x=(1264.5,1775.2)),
        dict(nom='SALA DE MÁQUINAS', viejo=125.5, nuevo=round(EJE_I1+CARA,1), x=(1790.2,2164.6))]
def como_construido(rooms, anillos):
    M=_uu2([Polygon(a).buffer(0) for a in anillos if len(a)>=3])
    dentro=[]
    for o in OBRA:
        r=[x for x in rooms if o['nom'] in (x['nombres'] or [])]
        if not r: sys.exit('no encontre '+o['nom'])
        r=r[0]
        sur=max(p[1] for p in r['pts'])
        r['pts']=[[p[0], o['nuevo'] if abs(p[1]-o['viejo'])<2 else p[1]] for p in r['pts']]
        dentro.append(_box(o['x'][0], o['nuevo'], o['x'][1], sur))
        o['dy']=o['nuevo']-o['viejo']
    M=M.difference(_uu2(dentro))
    M=_uu2([M,
        _box(1249.4,   0.0, 1790.2,   25.0),   # fachada norte de la lavanderia (eje H)
        _box(1239.5,   0.0, 1264.5,  245.4),   # muro poniente de la lavanderia, ahora exterior
        _box(1775.2,  25.0, 1790.2,  125.5),   # tabique lavanderia / sala de maquinas
        _box(1765.2,-176.9, 2189.6, -151.9),   # fachada norte de la sala de maquinas (eje I1)
        _box(1765.2,-176.9, 1790.2,   25.0),   # muro poniente del volumen que sobresale
        _box(2164.6,-176.9, 2189.6,  125.5)])  # fachada oriente prolongada
    out=[]
    for gm in ([M] if M.geom_type=='Polygon' else list(M.geoms)):
        if gm.geom_type!='Polygon': continue
        q=gm.simplify(0.05)
        out.append([[round(x,1),round(y,1)] for x,y in list(q.exterior.coords)[:-1]])
        for h in q.interiors: out.append([[round(x,1),round(y,1)] for x,y in list(h.coords)[:-1]])
    return rooms, out
def corre_simbolos(items):
    # La ventana y los rotulos que iban en el muro antiguo se corren con el muro.
    out=[]
    for it in items:
        ps=[p for p in it[1:] if isinstance(p,list)]
        mov=None
        for o in OBRA:
            if ps and all(o['x'][0]-20<=p[0]<=o['x'][1]+20 and 90<=p[1]<=132 for p in ps): mov=o['dy']
        out.append([it[0]]+[[p[0],p[1]+mov] if mov is not None and isinstance(p,list) else p for p in it[1:]])
    return out
rooms, MUROS = como_construido(rooms, MUROS)

print('  superficies antes -> despues del engrosado:')
for r in rooms:
    k=' · '.join(r['nombres']) or '?'
    print(f"    {k[:44]:44s} {antes[k]:7.2f} -> {Polygon(r['pts']).area/1e4:7.2f} m2")

# Recorte: fuera de la casa, varias capas comparten grosor con las cadenas de cota.
# Sin la terraza cubierta exterior (al norte de y=0) ni sus pilares.
CASA=(-30,-30,2220,2195); EJES=(-260,-260,2450,2400)
def clip(items, box):
    out=[]
    for it in items:
        ps=[p for p in it[1:] if isinstance(p,list)]
        if ps and all(box[0]<=p[0]<=box[2] and box[1]<=p[1]<=box[3] for p in ps): out.append(it)
    return out
f=lambda v:f"{v:.1f}".rstrip('0').rstrip('.')
poly_path=lambda p:'M'+' L'.join(f"{f(x)} {f(y)}" for x,y in p)+' Z'
def items_path(items):
    out=[]
    for it in items:
        if it[0]=='l': out.append(f"M{f(it[1][0])} {f(it[1][1])} L{f(it[2][0])} {f(it[2][1])}")
        elif it[0]=='c': out.append(f"M{f(it[1][0])} {f(it[1][1])} C{f(it[2][0])} {f(it[2][1])} {f(it[3][0])} {f(it[3][1])} {f(it[4][0])} {f(it[4][1])}")
        elif it[0]=='re': out.append(f"M{f(it[1][0])} {f(it[1][1])} H{f(it[2][0])} V{f(it[2][1])} H{f(it[1][0])} Z")
        elif it[0]=='qu': out.append('M'+' L'.join(f"{f(p[0])} {f(p[1])}" for p in it[1:])+' Z')
    return ' '.join(out)

def vent_items(ws):
    # El vano de fachada se redibuja ocupando el nuevo espesor de 25, para que la
    # ventana no quede flotando dentro del muro engrosado.
    it=[]
    for w in ws:
        if w['vert']: x0,x1,y0,y1=w['a'],w['b'],w['s0'],w['s1']
        else: x0,x1,y0,y1=w['s0'],w['s1'],w['a'],w['b']
        it += [['l',[x0,y0],[x1,y0]],['l',[x1,y0],[x1,y1]],['l',[x1,y1],[x0,y1]],['l',[x0,y1],[x0,y0]]]
        if w['vert']: cx=(x0+x1)/2; it.append(['l',[cx,y0],[cx,y1]])
        else: cy=(y0+y1)/2; it.append(['l',[x0,cy],[x1,cy]])
    return it

# Muros exentos dentro de un recinto (el arrimo del estar, la esquina del comedor):
# el contorno exterior del relleno se los traga, asi que se restan como huecos.
_MUR=_uu2([Polygon(a).buffer(0) for a in MUROS if len(a)>=3])
out=[]
for idx,r in enumerate(rooms):
    P=Polygon(r['pts']); b=P.bounds
    huecos=[]
    _i=P.intersection(_MUR)
    for _g in ([_i] if _i.geom_type=='Polygon' else list(getattr(_i,'geoms',[]))):
        if _g.geom_type=='Polygon' and _g.area>200 and P.buffer(-0.5).contains(_g):
            huecos.append([[round(x,1),round(y,1)] for x,y in list(_g.simplify(0.3).exterior.coords)[:-1]])
    area_neta=P.area-sum(Polygon(h).area for h in huecos)
    nom=' · '.join(r['nombres']) if r['nombres'] else 'RECINTO SIN NOMBRE'
    abierto=len(r['nombres'])>1
    kind=KIND.get(nom,'estar' if abierto else 'otro')
    edges=[]
    pp=r['pts']
    for k in range(len(pp)):
        a,c=pp[k],pp[(k+1)%len(pp)]
        ln=math.hypot(c[0]-a[0],c[1]-a[1])
        mx,my=(a[0]+c[0])/2,(a[1]+c[1])/2; vert=abs(a[0]-c[0])<0.01
        lx,ly=mx,my
        for off in (16,-16):
            q=(mx+off,my) if vert else (mx,my+off)
            if P.contains(Point(*q)): lx,ly=q; break
        edges.append(dict(a=list(a),b=list(c),len=round(ln,1),lx=round(lx,1),ly=round(ly,1),rot=-90 if vert else 0))
    c=P.centroid; rp=P.representative_point()
    cx,cy=(c.x,c.y) if P.contains(c) else (rp.x,rp.y)
    out.append(dict(id='n1r'+str(idx), name=nom, kind=kind, labels=(r['labels'] if abierto else None), pts=[list(p) for p in pp],
                    path=poly_path(pp)+''.join(' '+poly_path(h) for h in huecos), holes=(huecos or None),
                    area=round(area_neta/1e4,2), w=round(b[2]-b[0],1), h=round(b[3]-b[1],1),
                    perim=round(P.length/100,2), cx=round(cx,1), cy=round(cy,1),
                    bbox=[round(v,1) for v in b], edges=edges, abierto=abierto))

# vanos: puerta / paso / ventana
def tipo(o):
    seg=LineString([o['a'],o['b']]).buffer(6); win=0
    for k in ['(0.28, 0.53)','(0.43, 0.5)']:
        for it in L.get(k,[]):
            if it[0]=='l' and seg.contains(LineString([it[1],it[2]]).representative_point()): win+=1
    if win>=2: return 'window'
    return 'door' if o['gap']<=130 else 'passage'
ops=[dict(a=o['a'],b=o['b'],gap=o['gap'],type=tipo(o)) for o in VANOS if o['gap']>=30]
def _corre_rot(x,y):
    for o in OBRA:
        if o['x'][0]-30<=x<=o['x'][1]+30 and 60<=y<=150: return y+o['dy']
    return y
wins=[dict(t=w['t'],x=w['x'],y=_corre_rot(w['x'],w['y'])) for w in WORDS
      if ((w['t'].startswith('V') or w['t'].startswith('P')) and w['t'][1:].isdigit() and w['size']>10)]
# ejes: lineas + etiquetas
ejes=[]
for it in clip(L.get('(0.99, 0.0)',[]), EJES):
    if it[0]=='l': ejes.append([round(it[1][0],1),round(it[1][1],1),round(it[2][0],1),round(it[2][1],1)])
EX=[6.9,653.0,1007.5,1257.6,1784.1,2183.5]; EY=[-764.7,-169.8,7.1,107.4,341.4,625.3,958.5,1104.0,1511.8,1694.7,2170.0]
alab=[]
for w in WORDS:
    if not (12<w['size']<16 and len(w['t'])<=2): continue
    if w['t'].isdigit():
        x=min(EX,key=lambda v:abs(v-w['x']))
        if abs(x-w['x'])<40: alab.append(dict(t=w['t'],x=round(x,1),y=round(w['y'],1)))
    else:
        y=min(EY,key=lambda v:abs(v-w['y']))
        if abs(y-w['y'])<40: alab.append(dict(t=w['t'],x=round(w['x'],1),y=round(y,1)))
vistos=set(); al=[]
for a in alab:
    k=(a['t'],round(a['x']/50),round(a['y']/50))
    if k in vistos: continue
    vistos.add(k); al.append(a)
# etiquetas de recinto del arquitecto (para la planta libre y los espacios exteriores)
# espacios exteriores cubiertos: no son recintos medibles, pero se rotulan igual
ext=[]
for w in WORDS:
    if 7<w['size']<9 and w['t']=='ACCESO CUBIERTO':
        ext.append(dict(x=round(w['x'],1), y=round(w['y'],1), t='ACCESO CUBIERTO'))
notas=[]
data=dict(W=2200,H=2190,
  variants=dict(v1=dict(rooms=out,
    wallsPath=' '.join(poly_path(w) for w in MUROS),
    windowsPath=items_path(corre_simbolos(clip(L.get('(0.43, 0.5)',[])+L.get('(0.28, 0.53)',[]), CASA))+vent_items(VENT_NUEVAS)),
    doorsPath=items_path(corre_simbolos(clip(L.get('(0.23, 0.53)',[]), CASA))),
    furniturePath=items_path(clip(L.get('(0.57, 0.38)',[])+L.get('(0.57, 0.41)',[]), CASA)),
    windows=wins, openings=[o for o in ops if o['type'] in ('door','passage')], setbacks=[], notes=notas)),
  extLabels=ext,
  stairsPath=items_path(clip(L.get('(0.01, 0.3)',[]), CASA)),
  axesPath=' '.join(f"M{f(a)} {f(b)} L{f(c)} {f(d)}" for a,b,c,d in ejes),
  axisLabels=al, terrace=None)
data['view']=[-190,-340,2380,2370]
print('encuadre:', data['view'])
json.dump(data,open('n1_data.json','w'),ensure_ascii=False,separators=(',',':'))
import os
print('recintos:',len(out),' sup total:',round(sum(r['area'] for r in out),2),'m2')
for r in out: print(f"   {r['name'][:44]:44s} {r['w']:7.1f} x {r['h']:7.1f}  {r['area']:7.2f} m2  {len(r['edges']):3d} tramos")
print('vanos:',len(ops),' ventanas/puertas id:',len(wins),' ejes:',len(ejes),' etiquetas eje:',len(al))
print('bytes:',os.path.getsize('n1_data.json'))
