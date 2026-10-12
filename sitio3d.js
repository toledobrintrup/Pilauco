// Terreno de Casa Pilauco en 3D: lote, cierros, gimnasio, estudio con búnker, estacionamiento futuro y
// urbanismo (senderos, grava, radier, piscina, laguna). Los datos vienen de sitio.js (DATA_SITIO), en cm y
// en el marco de la app: X hacia el oriente, Y hacia el sur, Z hacia arriba (Z = 0 = piso del nivel 1).
// Mundo de Three.js: (x/100, z/100, y/100), igual que el resto de 3d.html.
//
//   const sitio = Sitio3D.crear({ T: THREE, D: DATA_SITIO, dark, tipoColor: KIND_COLOR });
//   scene.add(sitio.grupo);  sitio.sub.gimnasio.visible = false;  sitio.etiquetas.visible = ...
//
(function () {
  'use strict';
  if (window.Sitio3D) return;

  function crear(o) {
    const T = o.T, D = o.D, dark = !!o.dark, m = v => v / 100;
    const C = dark ? {
      pasto: 0x27392B, pastoLinea: 0x5C7A5E, lote: 0xB9C2CC, cierro: 0x9AA3AE, porton: 0xD3B26A,
      gimMuro: 0x7A5A3E, gimTecho: 0x2A2D33, estudioTecho: 0x6B5440, muro: 0x4A5058, bunker: 0x3C3F46, bunkerBorde: 0xC0C6CF,
      estac: 0x8FB4D4, grava: 0x5E5A52, hormigon: 0x7E8187, radier: 0x6E7177, agua: 0x2C6E8A, laguna: 0x3E6F5A, galpon: 0x3A3D44, galponTecho: 0xB7BCC4,
      etiqueta: '#E7E9EE', etiquetaFondo: 'rgba(26,29,35,.88)',
    } : {
      pasto: 0xA9C79B, pastoLinea: 0x7FA072, lote: 0x3A4250, cierro: 0x6B7380, porton: 0xB8862B,
      gimMuro: 0xB68B62, gimTecho: 0x3A3D44, estudioTecho: 0xC9A06C, muro: 0x8F97A2, bunker: 0x6E7480, bunkerBorde: 0x3A4250,
      estac: 0x3D5A73, grava: 0xC9C2B3, hormigon: 0xD7D9DC, radier: 0xC5C8CD, agua: 0x6FB8D6, laguna: 0x7FA78F, galpon: 0x8A8F98, galponTecho: 0xF0F1F3,
      etiqueta: '#1F2328', etiquetaFondo: 'rgba(255,255,255,.9)',
    };
    const lambert = (color, extra) => new T.MeshLambertMaterial(Object.assign({ color, side: T.DoubleSide }, extra || {}));

    // ---------- geometrías básicas en el marco de la app ----------
    // prisma con base plana en z0 y tapa en z1 (número) o z1(y) (función: tapa inclinada, por ejemplo un cielo de un agua)
    function prisma(pts, z0, z1, material, conFondo, sinTapa) {
      const zt = typeof z1 === 'function' ? z1 : () => z1;
      const v = [], n = pts.length;
      const push = (x, y, z) => v.push(m(x), m(z), m(y));
      for (let i = 0; i < n; i++) {
        const a = pts[i], b = pts[(i + 1) % n];
        push(a[0], a[1], z0); push(b[0], b[1], z0); push(b[0], b[1], zt(b[1]));
        push(a[0], a[1], z0); push(b[0], b[1], zt(b[1])); push(a[0], a[1], zt(a[1]));
      }
      const tris = T.ShapeUtils.triangulateShape(pts.map(p => new T.Vector2(p[0], p[1])), []);
      if (!sinTapa) tris.forEach(t => t.forEach(i => push(pts[i][0], pts[i][1], zt(pts[i][1]))));
      if (conFondo) tris.forEach(t => t.forEach(i => push(pts[i][0], pts[i][1], z0)));
      const g = new T.BufferGeometry();
      g.setAttribute('position', new T.BufferAttribute(new Float32Array(v), 3));
      g.computeVertexNormals();
      return new T.Mesh(g, material);
    }
    // placa plana (polígono) a la altura z, con huecos opcionales
    function placa(pts, z, material, huecos) {
      const cont = pts.map(p => new T.Vector2(p[0], p[1])), hs = (huecos || []).map(h => h.map(p => new T.Vector2(p[0], p[1])));
      const tris = T.ShapeUtils.triangulateShape(cont, hs);
      const todos = cont.concat(...hs), v = [];
      tris.forEach(t => t.forEach(i => v.push(m(todos[i].x), m(z), m(todos[i].y))));
      const g = new T.BufferGeometry();
      g.setAttribute('position', new T.BufferAttribute(new Float32Array(v), 3));
      g.computeVertexNormals();
      return new T.Mesh(g, material);
    }
    // losa inclinada: contorno + espesor, con la cara inferior en zInf(y)
    function losaInclinada(pts, zInf, espesor, material) {
      {
        const v = [], n = pts.length, push = (x, y, z) => v.push(m(x), m(z), m(y));
        for (let i = 0; i < n; i++) {
          const a = pts[i], b = pts[(i + 1) % n];
          const za = zInf(a[1]), zb = zInf(b[1]);
          push(a[0], a[1], za); push(b[0], b[1], zb); push(b[0], b[1], zb + espesor);
          push(a[0], a[1], za); push(b[0], b[1], zb + espesor); push(a[0], a[1], za + espesor);
        }
        const tris = T.ShapeUtils.triangulateShape(pts.map(p => new T.Vector2(p[0], p[1])), []);
        tris.forEach(t => t.forEach(i => push(pts[i][0], pts[i][1], zInf(pts[i][1]) + espesor)));
        tris.forEach(t => t.forEach(i => push(pts[i][0], pts[i][1], zInf(pts[i][1]))));
        const g = new T.BufferGeometry();
        g.setAttribute('position', new T.BufferAttribute(new Float32Array(v), 3));
        g.computeVertexNormals();
        return new T.Mesh(g, material);
      }
    }
    function linea(pts, z, color, cerrada, opacidad) {
      const v = [];
      const arr = cerrada ? pts.concat([pts[0]]) : pts;
      arr.forEach(p => v.push(m(p[0]), m(typeof z === 'function' ? z(p[1]) : z), m(p[1])));
      const g = new T.BufferGeometry(); g.setAttribute('position', new T.BufferAttribute(new Float32Array(v), 3));
      return new T.Line(g, new T.LineBasicMaterial({ color, transparent: opacidad != null, opacity: opacidad == null ? 1 : opacidad }));
    }
    function bordes(mesh, color, opacidad) {
      const eg = new T.EdgesGeometry(mesh.geometry, 20);
      const l = new T.LineSegments(eg, new T.LineBasicMaterial({ color, transparent: true, opacity: opacidad == null ? .35 : opacidad }));
      l.position.copy(mesh.position); return l;
    }
    // franja de ancho w (cm) a lo largo de una polilínea → polígono
    function franja(pts, w) {
      const izq = [], der = [], h = w / 2;
      for (let i = 0; i < pts.length; i++) {
        const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
        let dx = b[0] - a[0], dy = b[1] - a[1]; const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l;
        izq.push([pts[i][0] - dy * h, pts[i][1] + dx * h]); der.push([pts[i][0] + dy * h, pts[i][1] - dx * h]);
      }
      return izq.concat(der.reverse());
    }
    function etiqueta(texto, x, y, z, ancho) {
      const cv = document.createElement('canvas'), ctx = cv.getContext('2d');
      const esc = 4, fs = 15 * esc; ctx.font = `500 ${fs}px Inter, system-ui, sans-serif`;
      const tw = ctx.measureText(texto).width, pad = 10 * esc;
      cv.width = Math.ceil(tw + pad * 2); cv.height = Math.ceil(fs * 1.6);
      ctx.font = `500 ${fs}px Inter, system-ui, sans-serif`; ctx.textBaseline = 'middle';
      const r = cv.height / 2; ctx.fillStyle = C.etiquetaFondo;
      ctx.beginPath(); ctx.moveTo(r, 0); ctx.lineTo(cv.width - r, 0); ctx.arc(cv.width - r, r, r, -Math.PI / 2, Math.PI / 2); ctx.lineTo(r, cv.height); ctx.arc(r, r, r, Math.PI / 2, 3 * Math.PI / 2); ctx.fill();
      ctx.fillStyle = C.etiqueta; ctx.fillText(texto, pad, r);
      const tex = new T.CanvasTexture(cv); tex.minFilter = T.LinearFilter;
      // tamaño fijo en pantalla (sin atenuación): 0,05 ≈ un 6 % del alto del visor con el FOV de 42°
      const sp = new T.Sprite(new T.SpriteMaterial({ map: tex, transparent: true, depthTest: false, sizeAttenuation: false }));
      const alto = 0.024;
      sp.scale.set(alto * cv.width / cv.height, alto, 1); sp.position.set(m(x), m(z), m(y)); sp.renderOrder = 5;
      return sp;
    }
    const centro = pts => { const n = pts.length; return [pts.reduce((s, p) => s + p[0], 0) / n, pts.reduce((s, p) => s + p[1], 0) / n]; };
    const ficha = (mesh, titulo, sub) => { mesh.userData.sitio = `<b>${titulo}</b><br><span class="sub">${sub}</span>`; return mesh; };
    const fmt = v => (v / 100).toFixed(2).replace('.', ',');

    const grupo = new T.Group(), sub = {}, etiquetas = new T.Group();
    // etiquetas flotantes: apagadas por defecto (Gabriel, 2026-10-12: "todos sabemos lo que es"); se crean solo si se piden
    const etq = (...args) => { if (o.etiquetas) etiquetas.add(etiqueta(...args)); };
    ['terreno', 'cierros', 'gimnasio', 'estudio', 'estacionamiento', 'urbanismo'].forEach(k => { sub[k] = new T.Group(); grupo.add(sub[k]); });
    grupo.add(etiquetas);
    const zT = D.terreno.z;

    // ---------- lote: superficie de pasto y deslinde ----------
    const L = D.lote;
    const R0 = D.real || {}, huecosPasto = [R0.excavacion, R0.piscina, R0.piscina_chica].filter(p => p && p.pts).map(p => p.borde || p.pts);
    const pasto = placa(L.poligono, zT, lambert(C.pasto, { transparent: true, opacity: 1 }), huecosPasto);
    ficha(pasto, `Lote 6 "a11" · ${L.superficie_m2.toLocaleString('es-CL')} m²`, `Deslindes: norte ${fmt(L.deslindes.norte)} m · oriente ${fmt(L.deslindes.este)} m · sur ${fmt(L.deslindes.sur)} m · poniente ${fmt(L.deslindes.oeste)} m · ${D.terreno.dato}`);
    sub.terreno.add(pasto, linea(L.poligono, zT + 2, C.lote, true));
    // ---------- cierros ----------
    // sur (del emplazamiento): cierro de pilares de 50 x 70 cada 2,5 m con tablas, a 5 m del deslinde, curvado hacia el acceso
    const matPilar = lambert(C.cierro), matTabla = lambert(C.cierro, { transparent: true, opacity: .8 }), matPorton = lambert(C.porton);
    const caja = (w, h, d, mat, x, y, z, ang) => { const b = new T.Mesh(new T.BoxGeometry(m(w), m(h), m(d)), mat); b.position.set(m(x), m(z), m(y)); if (ang) b.rotation.y = ang; return b; };
    (D.cierros || []).forEach(c => {
      const w = c.ancho || 7, muro = prisma(franja(c.pts, Math.min(w, 10)), zT, zT + 150, matTabla);
      ficha(muro, 'Cierro sur', `${fmt(c.pts.reduce((s, p, i) => i ? s + Math.hypot(p[0] - c.pts[i - 1][0], p[1] - c.pts[i - 1][1]) : 0, 0))} m · ${c.dato || ''}`);
      sub.cierros.add(muro);
    });
    (D.pilares_cierro || []).forEach(p => {
      const [a, b] = p.lado || [50, 70], ang = ((p.ang || 90) - 90) * Math.PI / 180;
      sub.cierros.add(caja(a, 190, b, matPilar, p.c[0], p.c[1], zT + 95, -ang));
    });
    const AC = D.acceso;
    if (AC) {
      const rect = (r, h, mat, nombre, sub2) => {
        const [[x0, y0], [x1, y1]] = r, bx = caja(x1 - x0, h, y1 - y0, mat, (x0 + x1) / 2, (y0 + y1) / 2, zT + h / 2);
        if (nombre) ficha(bx, nombre, sub2 || AC.dato); sub.cierros.add(bx);
      };
      rect(AC.pilar_oeste, 200, matPilar, 'Pilar del acceso (poniente)'); rect(AC.pilar_este, 200, matPilar, 'Pilar del acceso (oriente)'); rect(AC.poste, 180, matPilar);
      const pv = AC.porton.vano, px0 = Math.min(pv[0][0], pv[1][0]), px1 = Math.max(pv[0][0], pv[1][0]);
      const hoja = caja(px1 - px0, 170, 10, lambert(C.porton, { transparent: true, opacity: .6 }), (px0 + px1) / 2, AC.linea_y + 9, zT + 90);
      ficha(hoja, 'Portón corredera', `${fmt(AC.porton.ancho)} m de ancho · ${AC.porton.tipo} · ${AC.dato}`); sub.cierros.add(hoja);
      const dv = AC.puerta.vano, dx0 = Math.min(dv[0][0], dv[1][0]), dx1 = Math.max(dv[0][0], dv[1][0]);
      const puerta = caja(dx1 - dx0, 170, 8, matPorton, (dx0 + dx1) / 2, AC.linea_y + 9, zT + 90);
      ficha(puerta, 'Puerta peatonal', `${fmt(AC.puerta.ancho)} m de ancho`); sub.cierros.add(puerta);
      etq('Acceso', (px0 + px1) / 2, AC.linea_y, zT + 280, 5);
    }
    // norte, oriente y poniente: el cierro real (pilares de hormigón con reja), sobre el deslinde, cada 3 m
    {
      const pts = L.poligono, n = pts.length, sur = D.servidumbre ? D.servidumbre.eje : null;
      const esSur = (a, b) => sur && Math.min(a[1], b[1]) > 4500;   // el lado sur es la servidumbre: ahí va el cierro interior
      const matReja = lambert(C.cierro, { transparent: true, opacity: .45 });
      for (let i = 0; i < n; i++) {
        const a = pts[i], b = pts[(i + 1) % n];
        if (esSur(a, b)) continue;
        const l = Math.hypot(b[0] - a[0], b[1] - a[1]), k = Math.max(1, Math.round(l / 300)), ang = -Math.atan2(b[1] - a[1], b[0] - a[0]);
        for (let j = 0; j <= k; j++) { const t = j / k; sub.cierros.add(caja(22, 185, 22, matPilar, a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, zT + 92, ang)); }
        const reja = caja(l, 140, 3, matReja, (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, zT + 95, ang);
        ficha(reja, 'Cierro perimetral', `${fmt(l)} m · pilares de hormigón con reja (foto de dron); sobre el deslinde del emplazamiento`);
        sub.cierros.add(reja);
      }
      if (sur) sub.terreno.add(linea(sur, zT + 3, C.lote, false, .5));
    }

    // ---------- gimnasio (construido): muros con cielo inclinado y cubierta gruesa con aleros ----------
    const G = D.gimnasio;
    if (G && G.planta) {
      const A = G.alturas, cub = G.cubierta;
      const zc = y => G.z_piso + A.cielo_norte + (A.cielo_sur - A.cielo_norte) * (y - G.planta_y0) / (G.planta_y1 - G.planta_y0);
      const muros = prisma(G.planta, G.z_piso - 10, zc, lambert(C.gimMuro, { transparent: true, opacity: .92 }));
      ficha(muros, 'Gimnasio', `${fmt(G.ancho)} × ${fmt(G.largo)} m en planta (L) · cielo de ${fmt(A.cielo_norte)} a ${fmt(A.cielo_sur)} m · lámina L11 del arquitecto · ${G.dato || ''}`);
      sub.gimnasio.add(muros, bordes(muros, C.muro, .5));
      const zInf = y => G.z_piso + cub.z_inf_norte + (cub.z_inf_sur - cub.z_inf_norte) * (y - cub.y0) / (cub.y1 - cub.y0);
      const techo = losaInclinada(cub.contorno, zInf, cub.espesor, lambert(C.gimTecho));
      ficha(techo, 'Cubierta del gimnasio', `Un agua, baja hacia el norte (2,2°) · ${fmt(cub.espesor)} m de espesor · aleros según L11`);
      sub.gimnasio.add(techo);
      const cg = centro(G.planta); etq('Gimnasio', cg[0], cg[1], G.z_piso + A.cubierta_sur + 120, 6);
    }

    // ---------- estudio con búnker (volúmenes según la planta de Gabriel; estructura pendiente) ----------
    const E = D.estudio, tipoColor = o.tipoColor || {};
    if (E) {
      const zc = y => E.cielo.z_norte + (E.cielo.z_sur - E.cielo.z_norte) * (y - E.cielo.y_norte) / (E.cielo.y_sur - E.cielo.y_norte);
      E.recintos.forEach(rc => {
        const color = tipoColor[rc.tipo] !== undefined ? tipoColor[rc.tipo] : C.muro;
        const mesh = prisma(rc.pts, E.z_piso, zc, lambert(color, { transparent: true, opacity: .88 }));
        ficha(mesh, rc.nombre, `${rc.area_m2.toLocaleString('es-CL')} m² · ${rc.dato} · ${D.estudio_anclaje ? D.estudio_anclaje.metodo : ''}`);
        const bd = bordes(mesh, C.muro); mesh.userData.recintoEstudio = bd.userData.recintoEstudio = true;   // se esconden cuando se dibujan los muros y ventanas propuestos
        sub.estudio.add(mesh, bd);
      });
      // losa de piso y zócalo hasta el terreno (la losa va 50 cm sobre el NPT de la casa; fundación pendiente del ingeniero)
      const losa = prisma(E.exterior, zT, E.z_piso, lambert(C.muro, { transparent: true, opacity: .95 }), true);
      losa.userData.losaEstudio = true;
      ficha(losa, 'Estudio: losa de piso y zócalo', `${fmt(E.ancho)} × ${fmt(E.largo)} m exteriores · losa terminada ${fmt(E.z_piso - zT)} m sobre el terreno natural, ${fmt(-E.z_piso)} m bajo el piso de la casa (Gabriel) · fundación según el ingeniero`);
      sub.estudio.add(losa);
      const zInf = y => E.techo.z0 + (E.techo.z1 - E.techo.z0) * (y - E.techo.y0) / (E.techo.y1 - E.techo.y0);
      const techo = losaInclinada(E.techo.contorno, zInf, E.techo.espesor, lambert(C.estudioTecho, { transparent: true, opacity: .9 }));
      ficha(techo, 'Techo del estudio', `Un agua al ${(E.techo.pendiente * 100).toLocaleString('es-CL')} % como la casa, sube hacia el ${E.techo.sube_hacia} · aleros de ${fmt(E.techo.alero_ns || E.techo.alero)} (N-S) y ${fmt(E.techo.alero_eo || E.techo.alero)} m (E-O) · ${E.datos.techo}`);
      techo.userData.techoEstudio = true;   // se apaga con la capa Techo del estudio
      sub.estudio.add(techo);
      const B = E.bunker;
      const bk = prisma(B.pts, B.z_piso, B.z_cielo, lambert(C.bunker, { transparent: true, opacity: .6 }), true);
      ficha(bk, 'Búnker', `${B.area_m2.toLocaleString('es-CL')} m² · ${fmt(B.interior_cm)} m interiores · piso en ${fmt(B.z_piso)} m · ${B.dato}`);
      bk.userData.bunker = true;
      sub.estudio.add(bk, bordes(bk, C.bunkerBorde, .7));
      const ce = centro(E.exterior); etq('Estudio', ce[0], ce[1], E.cielo.z_sur + E.techo.espesor + 120, 6);
      const cb = centro(B.pts); etq('Búnker', cb[0], cb[1], B.z_piso + 60, 5);
    }

    // ---------- estacionamiento futuro: solo el contorno y una sombra ----------
    const P = D.estacionamiento;
    if (P && P.planta) {
      const sombra = placa(P.planta, zT + 3, lambert(C.estac, { transparent: true, opacity: .18 }));
      ficha(sombra, 'Estacionamiento (futuro)', `${(Math.abs(areaDe(P.planta)) / 1e4).toFixed(1).replace('.', ',')} m² · ${P.dato || ''}`);
      sub.estacionamiento.add(sombra, linea(P.planta, zT + 4, C.estac, true, .9));
      const cp = centro(P.planta); etq('Estacionamiento (futuro)', cp[0], cp[1], zT + 250, 8);
    }
    function areaDe(pts) { return pts.reduce((s, p, i) => { const q = pts[(i + 1) % pts.length]; return s + p[0] * q[1] - q[0] * p[1]; }, 0) / 2; }

    // ---------- urbanismo: senderos, grava, radier, soleras (del emplazamiento) y lo real de la foto ----------
    const U = D.urbanismo || {}, R = D.real || {};
    (U.grava || []).forEach(g => { const mh = placa(g.pts, zT + 1, lambert(C.grava)); ficha(mh, g.nombre || 'Grava', g.dato || 'emplazamiento'); sub.urbanismo.add(mh); });
    (U.radier || []).forEach(g => { const mh = placa(g.pts, zT + 2, lambert(C.radier)); ficha(mh, g.nombre || 'Radier', g.dato || 'emplazamiento'); sub.urbanismo.add(mh); });
    (U.senderos || []).forEach(s => {
      const pts = s.poligono || franja(s.pts, s.ancho || 120);
      const mh = placa(pts, zT + 2, lambert(C.hormigon)); ficha(mh, s.nombre || 'Sendero', s.dato || 'emplazamiento'); sub.urbanismo.add(mh);
    });
    (U.soleras || []).forEach(s => sub.urbanismo.add(linea(s.pts, zT + 6, C.lote, false, .6)));
    (U.contornos || []).forEach(c => sub.urbanismo.add(linea(c.pts, zT + 6, C.lote, true, .45)));   // lo que dibujó el arquitecto, solo el contorno
    if (D.radier_arq && D.radier_arq.contorno) sub.urbanismo.add(linea(D.radier_arq.contorno, zT + 6, C.lote, false, .45));
    // el edificio B del arquitecto: solo su contorno, para comparar con el estudio centrado en la excavación
    if (D.estudio_arq && D.estudio_arq.pts) {
      const ln = linea(D.estudio_arq.pts, zT + 8, C.estac, true, .8); sub.estudio.add(ln);
      const sombra = placa(D.estudio_arq.pts, zT + 2, lambert(C.estac, { transparent: true, opacity: .08 }));
      ficha(sombra, 'Estudio según el emplazamiento del arquitecto', `${fmt(D.estudio_arq.ancho)} × ${fmt(D.estudio_arq.largo)} m · ${D.estudio_arq.dato}`); sub.estudio.add(sombra);
    }
    const agua = (p, nombre, color, prof) => {
      if (!p || !p.pts) return;
      const vaso = prisma(p.pts, zT - (prof || 150), zT + 1, lambert(C.radier, { transparent: true, opacity: .9 }), true, true);
      const esp = placa(p.pts, zT - 12, lambert(color, { transparent: true, opacity: .85 }));
      ficha(esp, nombre, `${(Math.abs(areaDe(p.pts)) / 1e4).toFixed(1).replace('.', ',')} m² · ${p.dato || 'foto de dron'}`);
      sub.urbanismo.add(vaso, esp);
      const c = centro(p.pts); etq(nombre, c[0], c[1], zT + 150, 5);
    };
    agua(R.piscina, 'Piscina', C.agua, 150); agua(R.piscina_chica, 'Jacuzzi', C.agua, 100);
    const EX = R.excavacion || R.excavacion_bunker || R.laguna;
    if (EX && EX.pts) {
      const fondo = (D.estudio && D.estudio.bunker) ? D.estudio.bunker.z_piso - 10 : zT - 200;   // hasta 10 cm bajo el piso del búnker
      const pozo = prisma(EX.pts, fondo, zT, lambert(dark ? 0x4A3B2E : 0x8C7355, { transparent: true, opacity: .85 }), true, true);
      ficha(pozo, 'Excavación del búnker (actual)', `${(Math.abs(areaDe(EX.pts)) / 1e4).toFixed(1).replace('.', ',')} m² en la foto de dron · ${EX.dato || 'con agua en la foto; el búnker se centra aquí (Gabriel)'}`);
      sub.urbanismo.add(pozo, linea(EX.pts, zT + 2, C.lote, true, .6));
    }
    const huecosAgua = [R.piscina, R.piscina_chica].filter(p => p && p.pts).map(p => p.borde || p.pts);
    (R.senderos || []).forEach(s => { const mh = placa(s.pts, zT + 2, lambert(C.hormigon), huecosAgua); ficha(mh, s.nombre || 'Sendero', s.dato || 'foto de dron'); sub.urbanismo.add(mh); });
    (R.radieres || []).forEach(s => { const mh = placa(s.pts, zT + 2, lambert(C.radier)); ficha(mh, s.nombre || 'Radier', s.dato || 'foto de dron'); sub.urbanismo.add(mh); });
    if (R.galpon && R.galpon.pts) {
      const gp = prisma(R.galpon.pts, zT, zT + (R.galpon.alto || 300), lambert(C.galpon, { transparent: true, opacity: .85 }));
      const tp = placa(R.galpon.pts, zT + (R.galpon.alto || 300) + 1, lambert(C.galponTecho));
      ficha(gp, R.galpon.nombre || 'Galpón de obra', R.galpon.dato || 'foto de dron'); sub.urbanismo.add(gp, tp);
      const c = centro(R.galpon.pts); etq(R.galpon.nombre || 'Galpón de obra', c[0], c[1], zT + 450, 6);
    }
    (R.otros || []).forEach(x => { if (!x.pts) return; const mh = x.alto ? prisma(x.pts, zT, zT + x.alto, lambert(C.galpon)) : placa(x.pts, zT + 2, lambert(C.radier)); ficha(mh, x.nombre || 'Elemento', x.dato || 'foto de dron'); sub.urbanismo.add(mh); });

    const bb = D.terreno.bbox;
    // "bajo tierra": el pasto se vuelve translúcido para ver el búnker y la excavación
    const bajoTierra = on => { pasto.material.opacity = on ? 0.28 : 1; pasto.material.depthWrite = !on; pasto.material.needsUpdate = true; };
    return { grupo, sub, etiquetas, bajoTierra, bbox: bb, centro: [(bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2], radio: Math.max(bb[2] - bb[0], bb[3] - bb[1]) / 2 };
  }

  window.Sitio3D = { crear };
})();
