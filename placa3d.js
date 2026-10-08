// Placa colaborante en 3D, con las perforaciones de los pernos. Común a losa.html y pernos.html.
// Necesita THREE (r128) global; si está THREE.BufferGeometryUtils, cada pieza queda en una sola malla.
//
//   const m = Placa3D.crear({ perfil, espesor, ancho, d0, largo, agujeros, radio, material, cache });
//
// Marco local: x a lo ancho de la plancha (desde el borde de la pieza, en m), y hacia arriba, z a lo largo (desde el
// extremo de la pieza, en m). La pieza va del ancho d0 al d0 + ancho (mm) de la plancha entera, así que sus nervios
// calzan con los de la plancha de la que sale.
//
// Cada agujero { c, s } (c en mm a lo ancho desde el borde de la pieza, s en m a lo largo) saca el fondo del valle en
// una franja chica alrededor del centro (±MEDIO_VALLE a lo ancho, el diámetro más 2·MARGEN a lo largo), donde el
// rigidizador del valle (o, en la unión de dos planchas, el gancho del traslapo) queda cortado, y en esa franja pone
// una chapa plana con el agujero redondo (radio en mm). Es una simplificación del dibujo: la broca solo saca el círculo.
// La chapa la pone la pieza donde cae el centro; { piso: true } la fuerza (último valle de unión, sin plancha vecina).
(function () {
  'use strict';
  if (window.Placa3D) return;
  const MEDIO_VALLE = 25;   // mm a cada lado del centro del valle (el fondo es plano desde ahí: rigidizador y gancho quedan adentro)
  const MARGEN = 5;         // mm de chapa plana antes y después del agujero, a lo largo

  // tramo del perfil (mm) entre x = d0 y x = d0 + w, corrido para que parta en 0
  function tramo(perfil, w, d0) {
    d0 = d0 || 0; const out = [], d1 = d0 + w;
    const en = (q, p, x) => [x - d0, q[1] + (p[1] - q[1]) * (x - q[0]) / (p[0] - q[0])];
    for (let i = 0; i < perfil.length; i++) {
      const p = perfil[i], q = perfil[i - 1];
      if (q && q[0] < d0 && p[0] > d0) out.push(en(q, p, d0));
      if (p[0] >= d0 && p[0] <= d1) out.push([p[0] - d0, p[1]]);
      if (q && q[0] < d1 && p[0] > d1) { out.push(en(q, p, d1)); break; }
    }
    return out;
  }
  // polilínea sin los intervalos de x en 'huecos': se unen los intervalos y cada tramo se recorta por partes,
  // quedándose con lo que cae afuera (también si un vértice cae justo en el borde de un hueco)
  function sinHuecos(pts, huecos) {
    if (!huecos.length) return [pts];
    const iv = huecos.map(h => h.slice()).sort((a, b) => a[0] - b[0]).reduce((o, h) => {
      if (o.length && h[0] <= o[o.length - 1][1]) o[o.length - 1][1] = Math.max(o[o.length - 1][1], h[1]); else o.push(h); return o; }, []);
    const fuera = x => !iv.some(([a, b]) => x > a && x < b);
    const out = []; let cur = [];
    const cierra = () => { if (cur.length > 1) out.push(cur); cur = []; };
    const agrega = p => { const u = cur[cur.length - 1]; if (!u || Math.abs(u[0] - p[0]) > 1e-9 || Math.abs(u[1] - p[1]) > 1e-9) cur.push(p); };
    for (let i = 1; i < pts.length; i++) {
      const p = pts[i - 1], q = pts[i];
      const xs = [p[0], q[0]]; iv.forEach(([a, b]) => [a, b].forEach(x => { if ((x - p[0]) * (x - q[0]) < 0) xs.push(x); }));
      const asc = q[0] >= p[0]; xs.sort((u, v) => asc ? u - v : v - u);
      for (let j = 0; j < xs.length - 1; j++) {
        const x0 = xs[j], x1 = xs[j + 1], xm = (x0 + x1) / 2;
        const en = x => q[0] === p[0] ? null : [x, p[1] + (q[1] - p[1]) * (x - p[0]) / (q[0] - p[0])];
        if (q[0] === p[0]) { if (fuera(p[0])) { agrega(p); agrega(q); } else cierra(); continue; }
        if (fuera(xm)) { agrega(en(x0)); agrega(en(x1)); } else cierra();
      }
    }
    cierra();
    return out;
  }
  // polilínea abierta → contorno cerrado de espesor e (mm), hacia arriba
  function forma(pts, e) {
    const T = window.THREE, n = pts.length, nor = [];
    for (let i = 0; i < n; i++) {
      const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)];
      let dx = b[0] - a[0], dy = b[1] - a[1]; const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l;
      nor.push([-dy, dx]);
    }
    const s = new T.Shape(), m = v => v / 1000;
    pts.forEach((p, i) => i ? s.lineTo(m(p[0]), m(p[1])) : s.moveTo(m(p[0]), m(p[1])));
    for (let i = n - 1; i >= 0; i--) s.lineTo(m(pts[i][0] + nor[i][0] * e), m(pts[i][1] + nor[i][1] * e));
    s.closePath(); return s;
  }

  function crear(o) {
    const T = window.THREE, cache = o.cache || {}, e = o.espesor, R = o.radio || 17.5;
    const largo = o.largo, ancho = o.ancho, d0 = o.d0 || 0;
    const base = tramo(o.perfil, ancho, d0);
    const L2 = (R + MARGEN) / 1000;
    const ag = (o.agujeros || []).filter(h => h.c > -MEDIO_VALLE && h.c < ancho + MEDIO_VALLE && h.s > -L2 && h.s < largo + L2)
      .map(h => ({ c: h.c, s0: Math.max(0, h.s - L2), s1: Math.min(largo, h.s + L2), s: h.s, piso: h.piso }));
    const cortes = [0, largo]; ag.forEach(h => cortes.push(h.s0, h.s1));
    const zs = [...new Set(cortes.map(v => Math.round(v * 1e5) / 1e5))].sort((a, b) => a - b);
    const geoDe = huecos => {
      const k = Math.round(ancho) + '_' + Math.round(d0) + '_' + huecos.map(h => h.map(Math.round).join(':')).join('|');
      if (cache[k] !== undefined) return cache[k];
      const formas = sinHuecos(base, huecos).filter(t => t.length > 1).map(t => forma(t, e));
      return (cache[k] = formas.length ? new T.ExtrudeGeometry(formas, { depth: 1, bevelEnabled: false }) : null);
    };
    const partes = [];   // [geometría, matriz]
    for (let i = 0; i < zs.length - 1; i++) {
      const a = zs[i], b = zs[i + 1]; if (b - a < 1e-5) continue;
      const mz = (a + b) / 2;
      const huecos = ag.filter(h => h.s0 <= mz && h.s1 >= mz).map(h => [h.c - MEDIO_VALLE, h.c + MEDIO_VALLE]);
      const geo = geoDe(huecos); if (!geo) continue;
      partes.push([geo, new T.Matrix4().makeTranslation(0, 0, a).multiply(new T.Matrix4().makeScale(1, 1, b - a))]);
    }
    // chapa plana con el agujero redondo, en el fondo de cada valle perforado (la pone la pieza donde cae el centro)
    ag.filter(h => h.piso || (h.c >= 0 && h.c < ancho)).forEach(h => {
      const k = 'piso_' + R + '_' + Math.round((h.s0 - h.s) * 1e4) + '_' + Math.round((h.s1 - h.s) * 1e4);
      let geo = cache[k];
      if (!geo) {
        const x0 = -MEDIO_VALLE / 1000, x1 = MEDIO_VALLE / 1000;
        const sh = new T.Shape(); sh.moveTo(x0, h.s0 - h.s); sh.lineTo(x1, h.s0 - h.s); sh.lineTo(x1, h.s1 - h.s); sh.lineTo(x0, h.s1 - h.s); sh.closePath();
        const hole = new T.Path(); hole.absarc(0, 0, R / 1000, 0, Math.PI * 2, true); sh.holes.push(hole);
        geo = cache[k] = new T.ExtrudeGeometry(sh, { depth: e / 1000, bevelEnabled: false, curveSegments: 24 });
        geo.rotateX(Math.PI / 2); geo.translate(0, e / 1000, 0);
      }
      partes.push([geo, new T.Matrix4().makeTranslation(h.c / 1000, 0, h.s)]);
    });
    // una sola malla por pieza si se puede (menos llamadas de dibujo); si no, un grupo
    const U = T.BufferGeometryUtils;
    if (U && U.mergeBufferGeometries && partes.length) {
      const gs = partes.map(([g, mt]) => { const c = g.clone(); c.applyMatrix4(mt); return c.index ? c.toNonIndexed() : c; });
      gs.forEach(g => { g.clearGroups(); ['uv2'].forEach(n => g.deleteAttribute && g.getAttribute(n) && g.deleteAttribute(n)); });
      const unida = U.mergeBufferGeometries(gs, false);
      gs.forEach(g => g.dispose());
      if (unida) return new T.Mesh(unida, o.material);
    }
    const grupo = new T.Group();
    partes.forEach(([g, mt]) => { const me = new T.Mesh(g, o.material); me.applyMatrix4(mt); grupo.add(me); });
    return grupo;
  }

  window.Placa3D = { crear, tramo, forma, sinHuecos, MEDIO_VALLE };
})();
