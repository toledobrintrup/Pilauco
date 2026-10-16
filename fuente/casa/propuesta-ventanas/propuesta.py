# -*- coding: utf-8 -*-
"""Propuesta de ventanas de la casa (Gabriel, 15-10-2026): datos + luz + elevaciones por fachada.
Coordenadas en cm, marco de la app (x al oriente, y al sur). Alturas desde el piso de cada nivel."""
import json, re, math
R='/Users/toledobrintrup/Coding/Pilauco'; S='/private/tmp/claude-501/-Users-toledobrintrup-Coding-Pilauco/336a464c-579a-4405-af69-f1b1813fc385/scratchpad/prop'
s=open(R+'/data.js',encoding='utf-8').read()
def datos(name):
    m=re.search(r'const '+name+r' = (\{.*?\});?\n', s, re.S); return json.loads(m.group(1))
N1=datos('DATA_N1')['variants']['v1']['rooms']; N2=datos('DATA_N2')['variants']['v2']['rooms']
E=json.loads(re.search(r'const DATA_ESTRUCTURA = (\{.*\});?\s*$', open(R+'/estructura.js',encoding='utf-8').read(), re.S).group(1))
T=E['techo']; techo=lambda y: T['z0']+(T['z1']-T['z0'])*(max(T['y0'],min(T['y1'],y))-T['y0'])/(T['y1']-T['y0'])
PC=(0,280); AL=(200,260); ALB=(150,260); ALC=(160,260)   # piso a cielo · franja alta de closet (0,6) · ventana alta de baño (1,1) · baño chico (1,0)
# ---------- ACTUAL (plano del arquitecto): fachada, nivel, recinto, lo, hi, (z0,z1), tipo, plano (coordenada perpendicular de la cara) ----------
ACT=[
 ('norte',1,'Oficina',41.6,425.1,PC,'ventana',25,'V8'), ('norte',1,'Galería',425.1,625.1,PC,'puerta vidriada',25,'P-N'),
 ('norte',1,'Cocina',687.8,858.9,PC,'ventana',245,'P4a'), ('norte',1,'Cocina',858.9,1050.9,PC,'corredera',245,'P4'), ('norte',1,'Cocina',1050.9,1222.8,PC,'ventana',245,'P4b'),
 ('norte',1,'Lavandería',1386.9,1602.9,PC,'ventana',25,'V7'),
 ('norte',2,'Dorm. matrimonial',112,258,PC,'ventana',25,'V24'), ('norte',2,'Dorm. matrimonial',270,360,PC,'puerta vidriada',25,'P6'), ('norte',2,'Dorm. matrimonial',383.9,572.9,PC,'ventana',25,'V22'),
 ('norte',2,'WKC Maggie',1066.1,1413.1,PC,'ventana',25,'V21'),
 ('oriente',1,'Sala de máquinas',235.5,325.5,(0,210),'puerta',2165,'P3'), ('oriente',1,'Bodega',357.4,447.4,(0,210),'puerta',2165,'P3'),
 ('oriente',1,'Chiflonera',991.8,1081.8,(0,210),'puerta',1765,'P2'), ('oriente',1,'Comedor',1182.3,1429.3,PC,'ventana',1765,'V6'),
 ('oriente',1,'Hall',1553,1673,(0,210),'puerta',989,'P1'), ('oriente',1,'Hall',2049.8,2158.8,(0,730),'doble altura',989,'V4'),
 ('oriente',2,'WKC Maggie',91,438,PC,'ventana',1765,'V20'), ('oriente',2,'Dorm. hijo 1',535.4,682.4,PC,'ventana',1765,'V19'), ('oriente',2,'Dorm. hijo 1',941.2,1088.2,PC,'ventana',1765,'V18'),
 ('oriente',2,'Baño hijos',1205.6,1352.6,PC,'ventana',1765,'V17'), ('oriente',2,'Dorm. hijo 2',1470.3,1617.3,PC,'ventana',1765,'V16'),
 ('sur',1,'Living',144.6,541.6,PC,'ventana',1676,'V1'), ('sur',1,'Hall',671.3,989.1,(0,730),'doble altura',2159,'V3'), ('sur',1,'Comedor',1253.2,1550.2,PC,'ventana',1493,'V5'),
 ('sur',1,'Bodega',1897.4,2057.4,(0,210),'puerta',940,'P'),
 ('sur',2,'Dorm. visitas',145,242,PC,'puerta vidriada',1825,'V12'), ('sur',2,'Family room',364.7,541.7,PC,'ventana',1825,'V13'),
 ('sur',2,'WKC hijo 2',1100.1,1197.1,PC,'ventana',2037,'V14'), ('sur',2,'Dorm. hijo 2',1361.1,1657.1,PC,'ventana',2037,'V15'),
 ('poniente',1,'Oficina',20.2,617.2,PC,'ventana',30,'V9'), ('poniente',1,'Living',745.4,982.4,PC,'ventana',25,'V10'), ('poniente',1,'Living',1112.4,1626.4,PC,'ventana',25,'V11'),
 ('poniente',1,'Hall',1979.7,2158.7,(0,730),'doble altura',671,'V2'),
 ('poniente',2,'Dorm. matrimonial',247,394,PC,'ventana',25,'V25'), ('poniente',2,'Baño matrimonial',572.8,870.8,PC,'ventana',25,'V26'),
 ('poniente',2,'Baño visitas',1113.1,1259.1,PC,'ventana',25,'V27'), ('poniente',2,'Dorm. visitas',1479.1,1626.1,PC,'ventana',25,'V28'),
]
# ---------- PROPUESTA v2 (15-10-2026, tarde): todo piso a cielo. Nivel 1 hasta 3,10 (bajo la viga IPE 300); nivel 2 hasta el cielo bajo los cabios (techo−4,35 → 2,65 al norte, 3,35 al sur) ----------
N1H=310
def d2(y): return 280          # nivel 2 todas iguales de 2,80 (Gabriel: todas iguales; 3,00 libres bajo los cabios en el norte con el techo subido 20 cm); el cielo real es int((techo(y)-435)//5*5)
def dd(y): return int((techo(y)-74)//5*5)           # doble altura: cielo del nivel 2 bajo las vigas (techo − 74, como cielo_n2 y CIELO_HALL)
PROP=[
 # norte N1 (la sala de máquinas la indica Gabriel)
 ('norte',1,'Oficina',40,370,(0,N1H),'ventana',25,'N1 · 3,3 piso a cielo: toda la pared norte a la piscina (Gabriel: "la vista más linda de la casa")'),
 ('norte',1,'Galería',425,625,(0,N1H),'puerta vidriada',25,'N2 · puerta vidriada de 2 hojas 2,0 al porche cubierto (como el plano)'),
 ('norte',1,'Cocina',687.8,858.9,(0,N1H),'ventana',245,'N3 · P4 se mantiene: fijo 1,7'), ('norte',1,'Cocina',858.9,1050.9,(0,N1H),'corredera',245,'N3 · P4 se mantiene: corredera de 2 hojas 1,9'), ('norte',1,'Cocina',1050.9,1222.8,(0,N1H),'ventana',245,'N3 · P4 se mantiene: fijo 1,7'),
 ('norte',1,'Lavandería',1290,1530,(0,N1H),'ventana',25,'N4 · ventana 2,4 piso a cielo, alineada con N8 (antes no tenía); una hoja proyectante'),
 ('norte',1,'Lavandería',1620,1710,(0,280),'puerta',25,'N4b · puerta de servicio 0,9 al patio cubierto del norte (tendedero bajo el pasillo-balcón)'),
 # norte N2
 ('norte',2,'Dorm. matrimonial',130,370,(0,d2(10)),'corredera',25,'N6 · corredera elevable 2 hojas 2,4 a la terraza'), ('norte',2,'Dorm. matrimonial',380,570,(0,d2(10)),'ventana',25,'N6 · fijo 1,9 (4,4 de vidrio en total)'),
 ('norte',2,'WKC Gabriel',710,950,(0,d2(10)),'ventana',25,'N7 · ventana 2,4 piso a cielo centrada en el paño 2–3 (antes 1,9)'),
 ('norte',2,'WKC Maggie',1290,1530,(0,d2(10)),'corredera',25,'N8 · corredera 2 hojas 2,4 al pasillo-balcón (de ahí a la terraza grande), alineada con la lavandería (antes 3,5)'),
 # oriente N1
 ('oriente',1,'Sala de máquinas',235.5,325.5,(0,280),'puerta',2165,'E1 · puerta 0,9, se mantiene (puertas de 2,80)'), ('oriente',1,'Bodega',357.4,447.4,(0,280),'puerta',2165,'E2 · puerta 0,9, se mantiene (puertas de 2,80)'),
 ('oriente',1,'Chiflonera',991.8,1081.8,(0,N1H),'puerta vidriada',1765,'E4 · puerta vidriada 0,9 piso a cielo (laminado + multipunto)'),
 ('oriente',1,'Comedor',1120,1165,(0,N1H),'ventana',1765,'E5 · 3 paños: 0,45'), ('oriente',1,'Comedor',1181,1430,(0,N1H),'ventana',1765,'E5 · 2,5 (V6)'), ('oriente',1,'Comedor',1446,1490,(0,N1H),'ventana',1765,'E5 · 0,44 hasta la esquina: los dos pilares quedan a la vista como parantes'),
 ('oriente',1,'Hall',1532.8,1553,(0,N1H),'ventana',989,'E6 · fijo 0,2'), ('oriente',1,'Hall',1553,1673,(0,N1H),'puerta vidriada',989,'E6 · puerta de entrada vidriada 1,2 (P1 del plano), piso a cielo'), ('oriente',1,'Hall',2049.8,2158.8,(0,dd(2104)),'doble altura',989,'E7 · V4 doble altura hasta el cielo del nivel 2'),
 # oriente N2
 ('oriente',2,'WKC Maggie',120,360,(0,d2(240)),'ventana',1765,'E8 · 2,4 piso a cielo sobre la cubierta del ala (antes 3,5); la salida al balcón va por el norte'),
 ('oriente',2,'Dorm. hijo 1',540,680,(0,d2(610)),'ventana',1765,'E9 · 1,4 entre el closet y el pilar E3'), ('oriente',2,'Dorm. hijo 1',975,1125,(0,d2(1050)),'ventana',1765,'E9 · 1,5 entre el pilar E y el hall (el paño 690–958 lleva la cruz del ingeniero)'),
 ('oriente',2,'Baño hijos',1180,1330,(0,d2(1255)),'ventana',1765,'E10 · 1,5 piso a cielo, satinado hasta 1,8 (tina frente al vidrio)'),
 ('oriente',2,'Dorm. hijo 2',1480,1720,(0,d2(1600)),'ventana',1765,'E11 · 2,4 piso a cielo (antes 1,47)'),
 # sur N1
 ('sur',1,'Living',144.6,541.6,(0,N1H),'ventana',1676,'S1 · V1 4,0 se mantiene (entre los pilares 110 y 575)'),
 ('sur',1,'Hall',671.3,989.1,(0,dd(2182.8)),'doble altura',2159,'S2 · ventanal principal hasta el cielo del nivel 2, bajo las vigas (no entre costaneras), marco solo de fierro'),
 ('sur',1,'Comedor',1253.2,1550.2,(0,N1H),'ventana',1493,'S3 · V5 3,0 se mantiene'),
 ('sur',1,'Bodega',1897.4,2057.4,(0,280),'puerta',940,'S4 · portón de la bodega 1,6, se mantiene (puertas de 2,80)'),
 # sur N2
 ('sur',2,'Dorm. visitas',90,330,(0,d2(1842.8)),'ventana',1812,'S5 · 2,4 piso a cielo, laminado como baranda (el plano tenía una puerta a una terraza que no existe)'),
 ('sur',2,'Family room',390,630,(0,d2(1842.8)),'ventana',1812,'S6 · 2,4 piso a cielo (antes 1,77)'),
 ('sur',2,'WKC hijo 2',1090,1210,(0,d2(2057.7)),'ventana',2024,'S7 · 1,2 piso a cielo (antes 0,95)'),
 ('sur',2,'Dorm. hijo 2',1361,1657,(0,d2(2057.7)),'ventana',2024,'S8 · V15 3,0 se mantiene'),
 # poniente N1
 ('poniente',1,'Oficina',250,600,(0,N1H),'ventana',25,'O1 · 3,5 piso a cielo (antes 6,0, toda la pared); misma jamba que O5: torre de vidrio en la esquina; quedan 2,2 de muro para estantes'),
 ('poniente',1,'Living',745,982,(0,N1H),'ventana',25,'O2 · V10 2,4 se mantiene'), ('poniente',1,'Living',1112,1626,(0,N1H),'ventana',25,'O3 · V11 5,1 se mantiene (en 2 paños)'),
 ('poniente',1,'Hall',1979.7,2158.7,(0,dd(2069)),'doble altura',671,'O4 · V2 doble altura hasta el cielo del nivel 2'),
 # poniente N2
 ('poniente',2,'Dorm. matrimonial',250,535,(0,d2(392)),'ventana',25,'O5 · 2,85 piso a cielo (antes 1,47), alineada con O1'),
 ('poniente',2,'Baño matrimonial',580,860,(0,d2(720)),'ventana',25,'O6 · 2,8 piso a cielo, satinado hasta 1,8 (tina bajo el vidrio)'),
 ('poniente',2,'Baño visitas',1115,1255,(0,d2(1185)),'ventana',25,'O7 · 1,4 piso a cielo, satinado hasta 1,8'),
 ('poniente',2,'Dorm. visitas',1386,1625.8,(0,d2(1506)),'ventana',25,'O8 · 2,4 piso a cielo (antes 1,47), jamba en la cara del pilar B1'),
]
# paños ciegos por estructura (cruces y celosías del ingeniero en fachada): fachada, nivel, lo, hi, tipo
CIEGOS=[('poniente',1,10,107,'celosía'),('poniente',1,625,736,'celosía'),('poniente',1,991,1104,'celosía'),('poniente',1,1634,1695,'celosía'),
        ('poniente',2,10,238,'cruz'),('poniente',2,991,1104,'celosía'),('poniente',2,1634,1695,'celosía'),
        ('oriente',2,10,82,'celosía'),('oriente',2,690,958,'cruz')]
json.dump(dict(actual=ACT, propuesta=PROP, ciegos=CIEGOS), open(S+'/propuesta.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
# ---------- luz: factor de luz diurna por recinto (Lynes), con θ por obstrucción ----------
def theta(fach, nivel, plano, lo, hi):
    if nivel==1 and fach=='norte' and plano<100 and hi<660: return 15   # bajo la terraza norte (7,85 m de losa a 3,46)
    if nivel==1 and fach=='norte' and plano==245: return 30             # cocina: 4,15 m bajo el nivel 2 y la cubierta del patio
    if nivel==1 and fach=='norte' and plano<100: return 50              # lavandería: cubierta de 1,8 m del eje I
    if nivel==2: return 65   # aleros de 1 m
    if fach=='sur' and plano==1493: return 20   # comedor sur: 6,6 m bajo el nivel 2 (acceso cubierto)
    if fach=='oriente' and plano==1765 and nivel==1: return 30   # comedor/chiflonera: 4 m bajo el techo del estacionamiento cubierto
    if fach=='oriente' and plano==989: return 60
    return 85
rooms={('Oficina',1):(21.34,19.05),('Galería',1):(14.3,16.7),('Cocina',1):(50.14,28.81),('Lavandería',1):(17.36,17.01),('Living',1):(129,70),('Comedor',1):(29.6,23.1),('Hall',1):(21.2,19.7),('Bodega',1):(22.13,19.31),('Chiflonera',1):(6.52,12.61),('Sala de máquinas',1):(18.19,17.21),
       ('Dorm. matrimonial',2):(32.54,22.9),('WKC Gabriel',2):(12.88,14.38),('WKC Maggie',2):(36.51,24.74),('Dorm. hijo 1',2):(32.54,27.17),('Baño hijos',2):(15.66,17.28),('Dorm. hijo 2',2):(32.19,27.02),('Dorm. visitas',2):(18.04,17.38),('Family room',2):(68.67,38.31),('Baño matrimonial',2):(18.99,18.53),('Baño visitas',2):(6.93,11.3),('WKC hijo 2',2):(11.71,14.11)}
def df(lista):
    out={}; area={}
    for fach,niv,rec,lo,hi,(z0,z1),tipo,plano,*_ in lista:
        if tipo in ('puerta','celosía'): continue
        Aw=(hi-lo)*(z1-z0)/1e4; area[(rec,niv)]=area.get((rec,niv),0)+Aw
        A,per=rooms.get((rec,niv),(None,None))
        if A is None: continue
        h=3.2 if niv==1 else 3.1
        th=theta(fach,niv,plano,lo,hi)
        out[(rec,niv)]=out.get((rec,niv),0)+0.63*Aw*th/((2*A+per*h)*0.75)
    return out, area
(dA,aA),(dP,aP)=df(ACT),df(PROP)
rows=[(k[1],k[0],dA.get(k,0),dP.get(k,0),aA.get(k,0),aP.get(k,0)) for k in rooms]
txt='\n'.join(f'{n} {r:18} actual {aa:5.1f} m² DF {a:5.1f}% → {a*150:5.0f} lux | propuesta {ap:5.1f} m² DF {p:5.1f}% → {p*150:5.0f} lux' for n,r,a,p,aa,ap in sorted(rows))
txt+=f"\n\nVIDRIO TOTAL (sin puertas opacas): actual {sum(aA.values()):.0f} m² · propuesta {sum(aP.values()):.0f} m²"
open(S+'/luz.txt','w').write(txt); print(txt)
