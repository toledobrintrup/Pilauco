// Cotas del estudio en 3D (capa "Medidas" de 3d.html): líneas de medida con sus marcas, líneas de extensión
// finas y rótulos en metros, agrupadas por familia (vanos, edificio, recintos, alturas, ejes, búnker y
// fundaciones). Los datos vienen de estudio_estructura.js (DATA_ESTUDIO_EST) y sitio.js (DATA_SITIO.estudio),
// en cm y en el marco de la app: X hacia el oriente, Y hacia el sur, Z hacia arriba (Z = 0 = piso del
// nivel 1 de la casa). Mundo de Three.js en metros: (x/100, z/100, y/100), igual que sitio3d.js.
//
//   const cotas = Cotas3D.crear(DATA_ESTUDIO_EST, DATA_SITIO.estudio, { dark, ficha, textoM: 0.42 });
//   scene.add(cotas); cotas.visible = false;          // la capa parte apagada; un botón la prende
//   cotas.userData.sub.vanos.visible = false;         // o se filtra por familia
//   cotas.userData.conteo                             // cuántas cotas tiene cada familia
//
// Cada cota es: la línea de medida, dos marcas oblicuas de 10 cm en los extremos, líneas de extensión desde
// el elemento (con 10 cm de exceso) y un rótulo (Sprite con CanvasTexture: píldora semitransparente y texto
// en negrita, nítido) centrado en la cota y corrido hacia afuera para no pisar la línea. Las líneas de una
// familia van en un solo LineSegments (y otro para las extensiones, más tenue): barato para el iPhone. Los
// rótulos llevan ficha (userData.sitio) para que al tocarlos se vea qué miden; las líneas no, para que no
// atrapen los toques de los objetos de atrás.
(function () {
  'use strict';
  if (window.Cotas3D) return;

  function crear(D, E, o) {
    const T = window.THREE; o = o || {};
    const dark = !!o.dark, textoM = o.textoM > 0 ? o.textoM : 0.42;
    const ficha = typeof o.ficha === 'function' ? o.ficha
      : (mesh, t, s) => { mesh.userData.sitio = '<b>' + t + '</b><br><span class="sub">' + s + '</span>'; return mesh; };
    const m = v => v / 100;
    const fmt = cm => (cm / 100).toFixed(2).replace('.', ',');          // 211.7 → "2,12"
    const mas = cm => (cm < 0 ? '−' : '+') + fmt(Math.abs(cm));         // alturas: "+4,00"
    const FAM = ['vanos', 'edificio', 'recintos', 'alturas', 'ejes', 'bunker'];
    const COLOR = dark
      ? { vanos: 0x5FA8E0, edificio: 0xC9CED6, recintos: 0x7CC27E, alturas: 0xF2A541, ejes: 0xB58CE0, bunker: 0x8FB0C9 }
      : { vanos: 0x2F7CB8, edificio: 0x4A5058, recintos: 0x3F8F42, alturas: 0xC77D14, ejes: 0x7E55B5, bunker: 0x5A7E99 };
    const FONDO = dark ? 'rgba(22,25,31,.84)' : 'rgba(255,255,255,.9)';
    const ALZA = textoM / 2 + 0.05;    // m: cuánto se levanta un rótulo sobre una cota de planta (no toca la línea ni el piso)

    // ---------- vectores en el marco de la app (cm) ----------
    const N = [0, -1, 0], S = [0, 1, 0], EST = [1, 0, 0], OES = [-1, 0, 0], UP = [0, 0, 1], DOWN = [0, 0, -1];
    const suma = (p, v, k) => [p[0] + v[0] * k, p[1] + v[1] * k, p[2] + v[2] * k];
    const resta = (p, q) => [p[0] - q[0], p[1] - q[1], p[2] - q[2]];
    const largo = v => Math.hypot(v[0], v[1], v[2]);
    const unit = v => { const L = largo(v) || 1; return [v[0] / L, v[1] / L, v[2] / L]; };
    const bbox = pts => {
      const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
      return { x0: Math.min(...xs), x1: Math.max(...xs), y0: Math.min(...ys), y1: Math.max(...ys) };
    };

    // ---------- acumuladores por familia ----------
    const sub = {}, lineas = {}, extens = {}, conteo = {};
    FAM.forEach(f => { sub[f] = new T.Group(); sub[f].userData.cota = f; lineas[f] = []; extens[f] = []; conteo[f] = 0; });
    const seg = (arr, p, q) => arr.push(m(p[0]), m(p[2]), m(p[1]), m(q[0]), m(q[2]), m(q[1]));   // app → mundo

    // ---------- rótulo: Sprite con píldora; una textura (y un material) por texto y familia ----------
    function pildora(ctx, x, y, w, h) {
      const r = h / 2;
      ctx.beginPath(); ctx.moveTo(x + r, y); ctx.lineTo(x + w - r, y); ctx.arc(x + w - r, y + r, r, -Math.PI / 2, Math.PI / 2);
      ctx.lineTo(x + r, y + h); ctx.arc(x + r, y + r, r, Math.PI / 2, 3 * Math.PI / 2); ctx.closePath();
    }
    const cache = {};
    function rotulo(f, texto) {
      const k = f + '|' + texto;
      if (!cache[k]) {
        const cv = document.createElement('canvas'), ctx = cv.getContext('2d');
        // canvas grande (72 px de fuente) para que el texto se vea nítido de cerca
        const fs = 72, pad = 28, borde = 4, font = '700 ' + fs + 'px Inter, -apple-system, system-ui, "Helvetica Neue", sans-serif';
        ctx.font = font;
        const tw = Math.ceil(ctx.measureText(texto).width);
        cv.width = tw + pad * 2; cv.height = Math.round(fs * 1.5);
        ctx.font = font; ctx.textBaseline = 'middle'; ctx.textAlign = 'center';
        const col = '#' + COLOR[f].toString(16).padStart(6, '0');
        pildora(ctx, borde / 2, borde / 2, cv.width - borde, cv.height - borde);
        ctx.fillStyle = FONDO; ctx.fill();
        ctx.lineWidth = borde; ctx.strokeStyle = col; ctx.globalAlpha = 0.85; ctx.stroke(); ctx.globalAlpha = 1;
        ctx.fillStyle = col; ctx.fillText(texto, cv.width / 2, cv.height / 2 + fs * 0.04);
        const tex = new T.CanvasTexture(cv);
        tex.minFilter = T.LinearFilter; tex.magFilter = T.LinearFilter; tex.generateMipmaps = false;
        cache[k] = { mat: new T.SpriteMaterial({ map: tex, transparent: true, depthWrite: false }), aspecto: cv.width / cv.height };
      }
      const c = cache[k], sp = new T.Sprite(c.mat);
      sp.scale.set(textoM * c.aspecto, textoM, 1);     // alto fijo en metros (sizeAttenuation: se achica con la distancia)
      sp.renderOrder = 6; sp.userData.cota = f; sp.userData.texto = texto;
      return sp;
    }

    // ---------- una cota ----------
    // a, b: extremos de la línea de medida (app cm, [x, y, z]). n: unitario perpendicular "hacia afuera":
    // da la oblicua de las marcas (45° entre la línea y n) y el exceso de las extensiones.
    // op.ea / op.eb: puntos del elemento medido, de donde salen las líneas de extensión (si faltan, no hay).
    // op.texto: rótulo (por defecto la distancia a-b en m). op.rot: dirección del corrimiento del rótulo
    // (por defecto n), op.sep: cuánto se corre (m), op.alza: cuánto se levanta en Z (m).
    // op.t / op.s: título y subtítulo de la ficha del rótulo.
    function cota(f, a, b, n, op) {
      op = op || {};
      const d = unit(resta(b, a)), L = largo(resta(b, a));
      const tk = unit([d[0] + n[0], d[1] + n[1], d[2] + n[2]]);
      seg(lineas[f], a, b);
      seg(lineas[f], suma(a, tk, -5), suma(a, tk, 5));
      seg(lineas[f], suma(b, tk, -5), suma(b, tk, 5));
      if (op.ea) seg(extens[f], op.ea, suma(a, n, 10));
      if (op.eb) seg(extens[f], op.eb, suma(b, n, 10));
      const c = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2];
      const rot = op.rot || n, sep = op.sep == null ? 0.3 : op.sep, alza = op.alza || 0;
      const p = suma(suma(c, rot, sep * 100), UP, alza * 100);
      const sp = rotulo(f, op.texto || fmt(L));
      sp.position.set(m(p[0]), m(p[2]), m(p[1]));
      if (op.t) ficha(sp, op.t, op.s || fmt(L) + ' m');
      sub[f].add(sp); conteo[f]++;
      return sp;
    }

    // ---------- datos base ----------
    const zP = D.z_piso, M = E.muro || (D.parametros && D.parametros.muro) || 25;
    const ext = bbox(E.exterior), x0 = ext.x0, x1 = ext.x1, y0 = ext.y0, y1 = ext.y1;   // caras exteriores
    const rec = {}; (E.recintos || []).forEach(r => { rec[r.id] = Object.assign({ r }, bbox(r.pts)); });
    const techo = E.techo || D.techo || {};
    const techoZ = y => techo.z0 + (techo.z1 - techo.z0) * (y - techo.y0) / (techo.y1 - techo.y0);   // cara inferior del techo
    const eTecho = techo.espesor || 10;
    const cielo = D.cielo || E.cielo || {};
    const zTerreno = o.zTerreno != null ? o.zTerreno
      : (window.DATA_SITIO && DATA_SITIO.terreno && DATA_SITIO.terreno.z != null ? DATA_SITIO.terreno.z : -70);
    const bunker = E.bunker || {};
    const H = D.hormigon || {};

    // ========== 1. Edificio: los 4 lados por fuera a 0,80 m, al nivel del piso, y el espesor del muro ==========
    {
      const f = 'edificio', s = 80, z = zP, ancho = fmt(x1 - x0), largoE = fmt(y1 - y0);
      const sE = ' m por fuera (muros de ' + fmt(M) + ')';
      cota(f, [x0, y0 - s, z], [x1, y0 - s, z], N, { ea: [x0, y0, z], eb: [x1, y0, z], sep: 0.5, alza: ALZA, t: 'Estudio: ancho, fachada norte', s: ancho + sE });
      cota(f, [x0, y1 + s, z], [x1, y1 + s, z], S, { ea: [x0, y1, z], eb: [x1, y1, z], sep: 0.5, alza: ALZA, t: 'Estudio: ancho, fachada sur', s: ancho + sE });
      cota(f, [x1 + s, y0, z], [x1 + s, y1, z], EST, { ea: [x1, y0, z], eb: [x1, y1, z], sep: 0.5, alza: ALZA, t: 'Estudio: largo, fachada oriente', s: largoE + sE });
      cota(f, [x0 - s, y0, z], [x0 - s, y1, z], OES, { ea: [x0, y0, z], eb: [x0, y1, z], sep: 0.5, alza: ALZA, t: 'Estudio: largo, fachada poniente', s: largoE + sE });
      // espesor del muro oriente, visto desde el sur en la esquina SE (lejos de las ventanas y de las cotas de altura)
      cota(f, [x1 - M, y1 + 30, z], [x1, y1 + 30, z], S, { ea: [x1 - M, y1, z], eb: [x1, y1, z], sep: 0.3, alza: ALZA, t: 'Muro exterior', s: fmt(M) + ' m de espesor (como la casa; supuesto)' });
    }

    // ========== 2. Recintos: ancho (x) y fondo (y) interiores, a 10 cm sobre el piso, a 45 cm de dos muros ==========
    {
      const f = 'recintos', z = zP + 10, s = 45;
      (E.recintos || []).forEach(r => {
        const b = bbox(r.pts), nombre = (r.nombre || r.id).split(' (')[0];
        const esHueco = r.id === 'escalera';
        const sA = fmt(b.x1 - b.x0) + ' × ' + fmt(b.y1 - b.y0) + ' m' + (esHueco ? ' el hueco' : ' interiores') + (r.area_m2 ? ' · ' + String(r.area_m2).replace('.', ',') + ' m²' : '');
        // ancho: pegado al lado norte, rótulo corrido hacia el centro del recinto
        cota(f, [b.x0, b.y0 + s, z], [b.x1, b.y0 + s, z], S, { sep: 0.35, alza: ALZA, t: nombre + ': ancho' + (esHueco ? ' del hueco' : ''), s: sA });
        // fondo: pegado al lado poniente
        cota(f, [b.x0 + s, b.y0, z], [b.x0 + s, b.y1, z], EST, { sep: 0.35, alza: ALZA, t: nombre + ': fondo' + (esHueco ? ' del hueco' : ''), s: sA });
      });
    }

    // ========== 3. Vanos: ancho en la cara exterior (0,30 m afuera, a la altura del alféizar) y alto vertical al costado ==========
    {
      const f = 'vanos';
      const NORMAL = { norte: N, sur: S, oriente: EST, poniente: OES, 'tabique B': N, 'tabique 4': OES };
      const FIN = {
        norte: [x0, x1], sur: [x0, x1], oriente: [y0, y1], poniente: [y0, y1],
        'tabique B': rec.cafeteria ? [rec.cafeteria.x0, rec.cafeteria.x1] : [x0 + M, x1 - M],
        'tabique 4': rec.estudio ? [rec.estudio.y0, rec.estudio.y1] : [y0 + M, y1 - M],
      };
      const lugar = mu => /^tabique/.test(mu) ? mu : 'fachada ' + mu;
      const porMuro = {};
      (D.vanos || []).filter(v => v.tipo !== 'escalera' && NORMAL[v.muro]).forEach(v => { (porMuro[v.muro] = porMuro[v.muro] || []).push(v); });
      Object.keys(porMuro).forEach(muro => {
        const nn = NORMAL[muro], lista = porMuro[muro], fin = FIN[muro];
        const eje = nn[0] !== 0 ? 1 : 0;                 // coordenada a lo largo del muro: y si la normal es ±x, x si es ±y
        const along = eje === 1 ? [0, 1, 0] : [1, 0, 0];
        lista.sort((p, q) => Math.min(p.a[eje], p.b[eje]) - Math.min(q.a[eje], q.b[eje]));
        lista.forEach((v, i) => {
          const lo = Math.min(v.a[eje], v.b[eje]), hi = Math.max(v.a[eje], v.b[eje]);
          const perp = v.a[1 - eje] + nn[1 - eje] * M / 2;   // a/b están en el eje del muro: la cara exterior queda a M/2
          const P = (t, z) => eje === 1 ? [perp, t, z] : [t, perp, z];
          const A = P(lo, v.z0), B = P(hi, v.z0);
          const tipo = v.tipo.charAt(0).toUpperCase() + v.tipo.slice(1);
          const enPiso = Math.abs(v.z0 - zP) < 1;
          const t = tipo + ' ' + v.id;
          const sV = fmt(hi - lo) + ' × ' + fmt(v.z1 - v.z0) + ' m · ' + lugar(muro) + (enPiso ? '' : ' · alféizar a ' + mas(v.z0 - zP));
          // ancho: a 0,30 m de la cara; rótulos alternados (cerca / lejos) para que las ventanas contiguas no se pisen;
          // si el alféizar está sobre el piso, el rótulo va bajo la línea (el del alto queda a media altura)
          cota(f, suma(A, nn, 30), suma(B, nn, 30), nn, { ea: A, eb: B, sep: i % 2 ? 0.75 : 0.3, alza: enPiso ? ALZA : -ALZA, texto: fmt(hi - lo), t: t + ': ancho', s: sV });
          // alto: cota vertical a 15 cm de la jamba (del lado con más muro libre) y 10 cm por fuera de la cara;
          // rótulo a media altura, corrido hacia afuera (tapa la línea detrás, como en un plano)
          const prev = i > 0 ? Math.max(lista[i - 1].a[eje], lista[i - 1].b[eje]) : fin[0];
          const next = i < lista.length - 1 ? Math.min(lista[i + 1].a[eje], lista[i + 1].b[eje]) : fin[1];
          const gapL = lo - prev, gapR = next - hi;
          const der = gapR >= 30 || gapR >= gapL;
          const lado = der ? along : [-along[0], -along[1], 0];
          const base = der ? P(hi, 0) : P(lo, 0);
          const pie = suma(suma(base, lado, 15), nn, 10);
          cota(f, [pie[0], pie[1], v.z0], [pie[0], pie[1], v.z1], lado,
            { ea: suma([base[0], base[1], v.z0], nn, 3), eb: suma([base[0], base[1], v.z1], nn, 3), rot: nn, sep: 0.45, texto: fmt(v.z1 - v.z0), t: t + ': alto', s: sV });
        });
      });
    }

    // ========== 4. Alturas: cielo, techo y piso sobre el terreno, verticales en las esquinas, 0,70 m por fuera ==========
    {
      const f = 'alturas', d = 70, fuera = 5;   // fuera: 5 cm delante de la fachada para no pelear con el muro
      const vertical = (x, y, za, zb, ladoTk, rot, texto, t, s) =>
        cota(f, [x, y, za], [x, y, zb], ladoTk, { ea: [x - ladoTk[0] * d, y - ladoTk[1] * d, za], eb: [x - ladoTk[0] * d, y - ladoTk[1] * d, zb], rot, sep: 0.45, texto, t, s });
      const zCN = cielo.z_norte, zCS = cielo.z_sur;
      if (zCN != null) vertical(x0 - d, y0 - fuera, zP, zCN, OES, N, mas(zCN - zP), 'Cielo interior, lado norte', mas(zCN - zP) + ' m sobre el piso del estudio (4,00 m terminados; sube hacia el sur al 3,5 %)');
      if (zCS != null) vertical(x0 - d, y1 + fuera, zP, zCS, OES, S, mas(zCS - zP), 'Cielo interior, lado sur', mas(zCS - zP) + ' m sobre el piso del estudio (el cielo sigue la pendiente del techo)');
      if (techo.z0 != null) {
        const zTN = techoZ(y0), zTS = techoZ(y1);
        vertical(x1 + d, y0 - fuera, zP, zTN, EST, N, mas(zTN - zP), 'Fachada norte: alto hasta el techo', mas(zTN - zP) + ' m del piso a la cara inferior del techo (la cubierta agrega ' + fmt(eTecho) + ')');
        vertical(x1 + d, y1 + fuera, zP, zTS, EST, S, mas(zTS - zP), 'Fachada sur: alto hasta el techo', mas(zTS - zP) + ' m del piso a la cara inferior del techo (la cubierta agrega ' + fmt(eTecho) + ')');
      }
      // piso del estudio sobre el terreno (misma vertical que el cielo norte, bajo el piso)
      vertical(x0 - d, y0 - fuera, zTerreno, zP, OES, N, mas(zP - zTerreno), 'Piso del estudio sobre el terreno', mas(zP - zTerreno) + ' m: el terreno se toma plano, 0,70 bajo el piso del nivel 1 de la casa');
    }

    // ========== 5. Ejes: 1-2-3-4-5 sobre el alero norte y A-A2-B-C-D-E sobre el alero poniente, 0,60 m sobre el techo ==========
    if (D.ejes && E.origen && techo.z0 != null) {
      const f = 'ejes', cont = techo.contorno ? bbox(techo.contorno) : { x0: x0 - 60, y0: techo.y0 };
      const yAlero = cont.y0, xAlero = cont.x0;
      const ordena = obj => Object.keys(obj).filter(k => typeof obj[k] === 'number').sort((p, q) => obj[p] - obj[q]);
      const sEje = (a, b, L) => fmt(L) + ' m entre los ejes ' + a + ' y ' + b + ' (pilares)';
      // norte: línea horizontal al nivel del alero norte + 0,60; extensiones que suben desde el borde del techo
      const zN = techoZ(yAlero) + eTecho, kx = ordena(D.ejes.x), xs = kx.map(k => E.origen[0] + D.ejes.x[k]);
      for (let i = 0; i + 1 < xs.length; i++) {
        cota(f, [xs[i], yAlero, zN + 60], [xs[i + 1], yAlero, zN + 60], UP,
          { ea: [xs[i], yAlero, zN + 2], eb: [xs[i + 1], yAlero, zN + 2], sep: ALZA, t: 'Ejes ' + kx[i] + '–' + kx[i + 1], s: sEje(kx[i], kx[i + 1], xs[i + 1] - xs[i]) });
      }
      if (xs.length > 2) cota(f, [xs[0], yAlero, zN + 130], [xs[xs.length - 1], yAlero, zN + 130], UP,
        { ea: [xs[0], yAlero, zN + 70], eb: [xs[xs.length - 1], yAlero, zN + 70], sep: ALZA, t: 'Ejes ' + kx[0] + '–' + kx[kx.length - 1], s: fmt(xs[xs.length - 1] - xs[0]) + ' m entre los ejes extremos' });
      // poniente: la línea sigue la pendiente del alero (3,5 %), 0,60 sobre el techo en cada eje
      const ky = ordena(D.ejes.y), ys = ky.map(k => E.origen[1] + D.ejes.y[k]), zA = y => techoZ(y) + eTecho;
      for (let i = 0; i + 1 < ys.length; i++) {
        cota(f, [xAlero, ys[i], zA(ys[i]) + 60], [xAlero, ys[i + 1], zA(ys[i + 1]) + 60], UP,
          { ea: [xAlero, ys[i], zA(ys[i]) + 2], eb: [xAlero, ys[i + 1], zA(ys[i + 1]) + 2], sep: ALZA, texto: fmt(ys[i + 1] - ys[i]), t: 'Ejes ' + ky[i] + '–' + ky[i + 1], s: sEje(ky[i], ky[i + 1], ys[i + 1] - ys[i]) });
      }
      if (ys.length > 2) cota(f, [xAlero, ys[0], zA(ys[0]) + 130], [xAlero, ys[ys.length - 1], zA(ys[ys.length - 1]) + 130], UP,
        { ea: [xAlero, ys[0], zA(ys[0]) + 70], eb: [xAlero, ys[ys.length - 1], zA(ys[ys.length - 1]) + 70], sep: ALZA, texto: fmt(ys[ys.length - 1] - ys[0]), t: 'Ejes ' + ky[0] + '–' + ky[ky.length - 1], s: fmt(ys[ys.length - 1] - ys[0]) + ' m entre los ejes extremos' });
    }

    // ========== 6. Búnker y fundaciones (bajo tierra: se ven cuando el terreno está apagado o la cámara baja) ==========
    {
      const f = 'bunker';
      // búnker: planta interior a 10 cm sobre su piso y alto interior en el muro poniente, 0,40 m por fuera
      const bi = H.interior || {}, pb = bunker.pts ? bbox(bunker.pts) : (H.piso ? bbox(H.piso.pts) : null);
      const zPB = bunker.z_piso != null ? bunker.z_piso : (H.piso ? H.piso.z_sup : null);
      const zCB = bunker.z_cielo != null ? bunker.z_cielo : (H.losa ? H.losa.z_inf : null);
      if (pb && zPB != null) {
        const z = zPB + 10, s = 45, sB = fmt(pb.x1 - pb.x0) + ' × ' + fmt(pb.y1 - pb.y0) + ' m interiores, como la cafetería de arriba';
        cota(f, [pb.x0, pb.y0 + s, z], [pb.x1, pb.y0 + s, z], S, { sep: 0.35, alza: ALZA, t: 'Búnker: ancho interior', s: sB });
        cota(f, [pb.x0 + s, pb.y0, z], [pb.x0 + s, pb.y1, z], EST, { sep: 0.35, alza: ALZA, t: 'Búnker: fondo interior', s: sB });
      }
      if (pb && zPB != null && zCB != null) {
        const xm = (H.muros && H.muros.piezas ? bbox(H.muros.piezas.reduce((a, p) => a.concat(p.pts), [])).x0 : pb.x0 - M) - 40, ym = (pb.y0 + pb.y1) / 2;
        cota(f, [xm, ym, zPB], [xm, ym, zCB], S, { ea: [pb.x0, ym, zPB], eb: [pb.x0, ym, zCB], rot: OES, sep: 0.45, texto: fmt(zCB - zPB), t: 'Búnker: alto interior', s: fmt(bi.alto || zCB - zPB) + ' m terminados (Gabriel)' });
      }
      // losa de fundación del búnker: espesor, vertical en su borde poniente
      if (H.fundacion && H.fundacion.pts) {
        const F = H.fundacion, fb = bbox(F.pts), yF = fb.y0 + (fb.y1 - fb.y0) * 0.8;
        cota(f, [fb.x0 - 20, yF, F.z_inf], [fb.x0 - 20, yF, F.z_sup], S, { ea: [fb.x0, yF, F.z_inf], eb: [fb.x0, yF, F.z_sup], rot: OES, sep: 0.45, texto: fmt(F.z_sup - F.z_inf), t: 'Búnker: losa de fundación', s: fmt(F.z_sup - F.z_inf) + ' m de espesor bajo todo el búnker (dato del ingeniero)' });
      }
      // una zapata: 1,00 × 1,00 × 1,00 (ancho por el borde sur, fondo por el borde poniente, alto en la esquina SO)
      const Z = (D.zapatas || [])[0];
      if (Z && Z.pts) {
        const zb = bbox(Z.pts), zs = Z.z_sup, zi = Z.z_inf, s = 20;
        const sZ = fmt(zb.x1 - zb.x0) + ' × ' + fmt(zb.y1 - zb.y0) + ' × ' + fmt(zs - zi) + ' m · ' + (Z.d || '');
        cota(f, [zb.x0, zb.y1 + s, zs], [zb.x1, zb.y1 + s, zs], S, { ea: [zb.x0, zb.y1, zs], eb: [zb.x1, zb.y1, zs], sep: 0.3, alza: ALZA, t: 'Zapata ' + Z.id + ': ancho', s: sZ });
        cota(f, [zb.x0 - s, zb.y0, zs], [zb.x0 - s, zb.y1, zs], OES, { ea: [zb.x0, zb.y0, zs], eb: [zb.x0, zb.y1, zs], sep: 0.3, alza: ALZA, t: 'Zapata ' + Z.id + ': fondo', s: sZ });
        cota(f, [zb.x0 - s, zb.y1 + s, zi], [zb.x0 - s, zb.y1 + s, zs], S, { ea: [zb.x0, zb.y1 + s, zi], eb: [zb.x0, zb.y1 + s, zs], rot: OES, sep: 0.45, texto: fmt(zs - zi), t: 'Zapata ' + Z.id + ': alto', s: sZ });
      }
      // una viga de fundación: 0,25 × 0,50. El alto va en su cara expuesta, en un tramo libre de zapatas;
      // el ancho (espesor) solo se ve en sección, así que va 10 cm bajo la viga con el rótulo colgando
      const V = (D.vigas_fundacion || [])[0];
      if (V && V.pts) {
        const vb = bbox(V.pts), zs = V.z_sup, zi = V.z_inf;
        const enY = (vb.y1 - vb.y0) >= (vb.x1 - vb.x0);        // corre norte-sur
        const l0 = enY ? vb.y0 : vb.x0, l1 = enY ? vb.y1 : vb.x1;
        // tramo más largo sin zapatas encima
        const ocup = (D.zapatas || []).map(z => bbox(z.pts)).filter(b => enY ? (b.x0 < vb.x1 && b.x1 > vb.x0) : (b.y0 < vb.y1 && b.y1 > vb.y0))
          .map(b => enY ? [b.y0, b.y1] : [b.x0, b.x1]).sort((p, q) => p[0] - q[0]);
        let libre = [l0, l1], t0 = l0;
        ocup.forEach(iv => { if (iv[0] - t0 > libre[1] - libre[0]) libre = [t0, iv[0]]; t0 = Math.max(t0, iv[1]); });
        if (l1 - t0 > libre[1] - libre[0]) libre = [t0, l1];
        const tm = (libre[0] + libre[1]) / 2;
        const sV = fmt(enY ? vb.x1 - vb.x0 : vb.y1 - vb.y0) + ' × ' + fmt(zs - zi) + ' m · ' + (V.d || '');
        if (enY) {
          cota(f, [vb.x0 - 20, tm, zi], [vb.x0 - 20, tm, zs], S, { ea: [vb.x0, tm, zi], eb: [vb.x0, tm, zs], rot: OES, sep: 0.45, texto: fmt(zs - zi), t: 'Viga de fundación ' + V.id + ': alto', s: sV });
          cota(f, [vb.x0, tm, zi - 10], [vb.x1, tm, zi - 10], DOWN, { ea: [vb.x0, tm, zi], eb: [vb.x1, tm, zi], sep: 0.3, texto: fmt(vb.x1 - vb.x0), t: 'Viga de fundación ' + V.id + ': ancho', s: sV });
        } else {
          cota(f, [tm, vb.y1 + 20, zi], [tm, vb.y1 + 20, zs], EST, { ea: [tm, vb.y1, zi], eb: [tm, vb.y1, zs], rot: S, sep: 0.45, texto: fmt(zs - zi), t: 'Viga de fundación ' + V.id + ': alto', s: sV });
          cota(f, [tm, vb.y0, zi - 10], [tm, vb.y1, zi - 10], DOWN, { ea: [tm, vb.y0, zi], eb: [tm, vb.y1, zi], sep: 0.3, texto: fmt(vb.y1 - vb.y0), t: 'Viga de fundación ' + V.id + ': ancho', s: sV });
        }
      }
    }

    // ---------- armado: un LineSegments por familia (y otro, más tenue, para las extensiones) ----------
    const grupo = new T.Group();
    FAM.forEach(f => {
      const mk = (arr, opacidad) => {
        const g = new T.BufferGeometry();
        g.setAttribute('position', new T.BufferAttribute(new Float32Array(arr), 3));
        const l = new T.LineSegments(g, new T.LineBasicMaterial({ color: COLOR[f], transparent: true, opacity: opacidad }));
        l.userData.cota = f; l.renderOrder = 4; return l;
      };
      if (lineas[f].length) sub[f].add(mk(lineas[f], 0.95));
      if (extens[f].length) sub[f].add(mk(extens[f], 0.45));
      grupo.add(sub[f]);
    });
    grupo.userData.sub = sub; grupo.userData.conteo = conteo; grupo.userData.cota = 'medidas';
    return grupo;
  }

  window.Cotas3D = { crear };
})();
