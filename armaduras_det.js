// Detalle de armaduras del estudio (sección 07 de estudio.html), para el ingeniero (Gabriel, 22-10-2026: "revisa que los detalles de
// enfierradura tengan todas las medidas de los fierros, distanciamientos, etc. … parece más un plano de arquitectura que de ingeniería").
// Todo sale de las barras del modelo (DATA_ESTUDIO_EST.fierros, en cm, marco de la app: x oriente, y sur, z hacia arriba), así que los
// cortes, la planilla de doblado y la cubicación dicen lo mismo:
//   const A = Armaduras.planilla(D)            → { filas, totales, marcasDe(id), filaDe(f, pl) }   (una marca por forma de barra)
//   Armaduras.tablaHTML(A)                      → planilla de doblado: marca, dónde, ø, forma acotada, L, cantidad, @, m, kg, fuente
//   Armaduras.seccion(svg, D, H, A, cfg)        → corte vertical del modelo (hormigón + barras) con marcas, recubrimientos y cotas
(function () {
  const NS = 'http://www.w3.org/2000/svg';
  const KGM = { 8: 0.395, 10: 0.617, 12: 0.888, 16: 1.578, 19: 2.235 };   // kg/m (los mismos del generador)
  const ORDEN = ['losa de fundación', 'muro del búnker', 'losa del búnker', 'VHA 25/40', 'sobrecimiento', 'cimiento corrido', 'CF 25/50', 'placa base PLb'];
  const coma = (v, d) => (+v).toLocaleString('es-CL', { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 });
  const cm = v => coma(v, Math.abs(v - Math.round(v)) > 0.01 ? 1 : 0);
  const nomD = d => d === 19 ? 'ø3/4"' : 'ø' + d;
  const dist3 = (a, b) => Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]);
  const segsDe = pl => pl.slice(1).map((p, i) => dist3(pl[i], p)).filter(v => v > 0.05);
  const medio = v => Math.round(v * 2) / 2;
  const instancias = f => f.polilineas ? f.polilineas : Array.from({ length: f.n }, (_, k) => f.polilinea.map(p => [p[0] + f.paso[0] * k, p[1] + f.paso[1] * k, p[2] + f.paso[2] * k]));
  const espaciado = f => { if (f.paso && f.n > 1) { const p = Math.hypot(f.paso[0], f.paso[1], f.paso[2]); if (p > 0.1) return Math.round(p); } const m = /ø\d+@(\d+)/.exec(f.d || ''); return m ? +m[1] : null; };
  const clave = (f, pl) => [f.elemento, f.diam, segsDe(pl).map(medio).join(',')].join('|');

  // ---------- dónde va y de dónde sale cada barra ----------
  const PARTE = { sup: 'superiores', med: 'medias', inf: 'inferiores', est: 'estribos' };
  const lista = a => a.length <= 1 ? (a[0] || '') : a.slice(0, -1).join(', ') + ' y ' + a[a.length - 1];
  function donde(ids) {
    const uniq = a => [...new Set(a)];
    const m = ids.map(id => /^M([VHC])-([NSOE])-(ext|int)$/.exec(id)).filter(Boolean);
    if (m.length) { const t = { V: 'verticales', H: 'horizontales', C: 'coronamiento (2ø12)' }[m[0][1]]; return `${t} de los muros ${lista(uniq(m.map(x => x[2])))}${uniq(m.map(x => x[3])).length > 1 ? ', 2 mallas' : ''}`; }
    const lf = { 'LF-inf-NS': 'malla inferior N-S', 'LF-inf-EO': 'malla inferior E-O', 'LF-sup-NS': 'malla superior N-S', 'LF-sup-EO': 'malla superior E-O', LN: 'inferiores N-S (luz corta)', LE: 'inferiores E-O', LS: 'superiores sobre la VHA', AN: 'horquillas 1+1 de las placas base', AE: 'estribos de los anclajes' };
    if (ids.every(id => lf[id])) return lista(uniq(ids.map(id => lf[id])));
    if (ids.every(id => /^LH-/.test(id))) return 'borde del hueco de la escalera, arriba y abajo';
    const v = ids.map(id => /^VHA-(3|esc)-(sup|med|inf|est)$/.exec(id)).filter(Boolean);
    if (v.length) return `${v[0][1] === '3' ? 'VHA del eje 3' : 'VHA del borde de la escalera'}: ${lista(uniq(v.map(x => PARTE[x[2]])))}`;
    const s = ids.map(id => /^(SU|S12|S8|CU|CL)-(1|5|E)$/.exec(id)).filter(Boolean);
    if (s.length) { const t = { SU: 'estribos', S12: '2ø12 superiores', S8: 'horizontales (2 caras)', CU: 'U transversales', CL: '4ø10 longitudinales' }[s[0][1]]; const e = uniq(s.map(x => x[2])); return `${t} · eje${e.length > 1 ? 's' : ''} ${lista(e)}`; }
    const c = ids.map(id => /^CF-(4|C|C2)-(sup|med|inf|est)$/.exec(id)).filter(Boolean);
    if (c.length) { const e = uniq(c.map(x => x[1])); return `${lista(uniq(c.map(x => PARTE[x[2]])))} · eje${e.length > 1 ? 's' : ''} ${lista(e)}`; }
    return ids.join(', ');
  }
  function fuente(id) {   // [tipo, corto, detalle]
    if (/^M[VHC]-/.test(id)) return ['dato', 'L01 a-a', 'lámina 01, corte a-a; lámina 03'];
    if (/^L[NESH]/.test(id)) return ['dato', 'L03', 'lámina 03, planta losa (adaptada a 6,20 de luz)'];
    if (/^(VHA|CF)-.*-est$/.test(id) || id === 'AE') return ['propuesta', 'ganchos 135°', 'diámetro y paso de la lámina; ganchos de 135° propuestos'];
    if (/^VHA-/.test(id)) return ['dato', 'L03', 'lámina 03, VHA 25/40'];
    if (/^LF-/.test(id)) return ['propuesta', 'losa fund.', 'losa e=30 del ingeniero (15-10-2026); armadura propuesta'];
    if (/^(SU|CU)-/.test(id)) return ['dato', 'L01 b-b', 'lámina 01, corte b-b'];
    if (/^(S12|S8|CL)-/.test(id)) return ['dato', 'L01 b-b', 'lámina 01, corte b-b; patas 60ø propuestas'];
    if (/^CF-/.test(id)) return ['dato', 'L01 CF', 'lámina 01, CF 25/40; sección 25/50 de Gabriel; patas 60ø propuestas'];
    if (id === 'AN') return ['dato', 'L01 PLb', 'lámina 01, detalle PLb'];
    return ['propuesta', '', ''];
  }

  // ---------- planilla: una marca por (elemento, diámetro, forma) ----------
  function planilla(D) {
    const grupos = new Map();
    D.fierros.forEach(f => {
      const pls = f.polilineas ? f.polilineas.map(pl => [pl, 1]) : [[f.polilinea, f.n]];
      pls.forEach(([pl, n]) => {
        const k = clave(f, pl); let g = grupos.get(k);
        if (!g) { g = { elemento: f.elemento, diam: f.diam, segs: segsDe(pl).map(medio), Lx: segsDe(pl).reduce((a, b) => a + b, 0), pl, n: 0, ids: [], esp: null, fams: [] }; grupos.set(k, g); }
        g.n += n; if (!g.ids.includes(f.id)) { g.ids.push(f.id); g.fams.push(f); }
        const e = espaciado(f); if (e && !g.esp) g.esp = e;
      });
    });
    const filas = [...grupos.values()].sort((a, b) => ORDEN.indexOf(a.elemento) - ORDEN.indexOf(b.elemento));
    filas.forEach((g, i) => {
      g.marca = i + 1; g.L = Math.round(g.Lx * 10) / 10; g.m = g.Lx * g.n / 100; g.kg = g.m * KGM[g.diam];
      g.donde = donde(g.ids); const fs = g.ids.map(fuente); g.fuente = fs.find(x => x[0] === 'propuesta') || fs[0];
    });
    const totales = {}; filas.forEach(g => { const t = totales[g.diam] = totales[g.diam] || { m: 0, kg: 0 }; t.m += g.m; t.kg += g.kg; });
    const porClave = new Map(filas.map(g => [[g.elemento, g.diam, g.segs.join(',')].join('|'), g]));
    return {
      filas, totales,
      filaDe: (f, pl) => porClave.get(clave(f, pl)),
      marcasDe: id => filas.filter(g => g.ids.includes(id)).map(g => g.marca),
    };
  }

  // ---------- forma acotada de una barra (esquema sin escala, medidas reales en cm) ----------
  function plano2D(pl) {
    const P = pl.filter((p, i) => i === 0 || dist3(p, pl[i - 1]) > 0.05);
    const conZ = P.some(p => Math.abs(p[2] - P[0][2]) > 0.5);
    if (!conZ) {   // barra horizontal: en planta, girada para que su tramo más largo quede horizontal
      let lx = 0, ly = 0; for (let i = 1; i < P.length; i++) { lx += Math.abs(P[i][0] - P[i - 1][0]); ly += Math.abs(P[i][1] - P[i - 1][1]); }
      return P.map(p => ly > lx ? [p[1] - P[0][1], -(p[0] - P[0][0])] : [p[0] - P[0][0], p[1] - P[0][1]]);
    }
    let d = null;
    for (let i = 1; i < P.length; i++) { const dx = P[i][0] - P[i - 1][0], dy = P[i][1] - P[i - 1][1], h = Math.hypot(dx, dy); if (h > 0.5) { d = [dx / h, dy / h]; break; } }
    return P.map(p => [d ? (p[0] - P[0][0]) * d[0] + (p[1] - P[0][1]) * d[1] : 0, -(p[2] - P[0][2])]);   // plano vertical: z hacia arriba
  }
  function formaSVG(g) {
    const P = plano2D(g.pl); if (P.length < 2) return '';
    const Ls = P.slice(1).map((p, i) => Math.hypot(p[0] - P[i][0], p[1] - P[i][1])), Lmax = Math.max(...Ls);
    // largo dibujado comprimido (raíz) para que una barra de 11 m con patas de 72 se lea; las direcciones se respetan
    const Q = [[0, 0]]; Ls.forEach((L, i) => { const a = P[i], b = P[i + 1], s = (16 + 64 * Math.sqrt(L / Lmax)) / (L || 1); Q.push([Q[i][0] + (b[0] - a[0]) * s, Q[i][1] + (b[1] - a[1]) * s]); });
    const cerrada = Q.some((q, i) => Q.some((r, j) => j > i + 1 && Math.hypot(q[0] - r[0], q[1] - r[1]) < 1));
    if (cerrada) { const n = Q.length - 1, a = Q[n - 1], b = Q[n], dx = b[0] - a[0], dy = b[1] - a[1], h = Math.hypot(dx, dy) || 1; Q[n] = [b[0] - dy / h * 3, b[1] + dx / h * 3]; }   // el segundo gancho, un poco al lado del primero
    const xs = Q.map(q => q[0]), ys = Q.map(q => q[1]), cx = (Math.min(...xs) + Math.max(...xs)) / 2, cy = (Math.min(...ys) + Math.max(...ys)) / 2;
    const tx = [], vistos = [], cajas = [];
    Ls.forEach((L, i) => {
      const a = Q[i], b = Q[i + 1], mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, dx = b[0] - a[0], dy = b[1] - a[1], h = Math.hypot(dx, dy) || 1;
      let nx = -dy / h, ny = dx / h; if ((mx - cx) * nx + (my - cy) * ny < 0) { nx = -nx; ny = -ny; }
      const ang = Math.round(((Math.atan2(dy, dx) * 180 / Math.PI) + 180) % 180 / 20), k = ang + '|' + medio(L);
      if (vistos.includes(k) && (cerrada || L < 25)) return; vistos.push(k);   // estribos y ganchos: cada medida una vez
      const t = cm(medio(L)), wt = t.length * 6.6, off = 7 + Math.abs(nx) * wt / 2, x = mx + nx * off, y = my + ny * (off - Math.abs(nx) * wt / 2 + 3) + 4;
      tx.push(`<text x="${x.toFixed(1)}" y="${y.toFixed(1)}" text-anchor="middle" class="pl-t">${t}</text>`); cajas.push([x - wt / 2, y - 11, x + wt / 2, y + 3]);
    });
    const bx = xs.concat(cajas.flatMap(c => [c[0], c[2]])), by = ys.concat(cajas.flatMap(c => [c[1], c[3]])), pad = 6;
    const x0 = Math.min(...bx) - pad, y0 = Math.min(...by) - pad, w = Math.max(...bx) - Math.min(...bx) + 2 * pad, h = Math.max(...by) - Math.min(...by) + 2 * pad;
    const d = 'M' + Q.map(q => q[0].toFixed(1) + ' ' + q[1].toFixed(1)).join(' L');
    return `<svg class="pl-forma" viewBox="${x0.toFixed(1)} ${y0.toFixed(1)} ${w.toFixed(1)} ${h.toFixed(1)}" width="${w.toFixed(1)}" height="${h.toFixed(1)}" role="img" aria-label="forma de la marca ${g.marca}"><path d="${d}" class="pl-b"/>${tx.join('')}</svg>`;
  }

  function tablaHTML(A, cub) {
    const filas = A.filas.map(g => {
      const esp = g.esp ? '@' + g.esp : '—', [tipo, corto, nota] = g.fuente;
      return `<tr><td class="c"><span class="pl-m">${g.marca}</span></td><td><b>${g.elemento}</b><br><span class="small">${g.donde}</span></td><td class="c"><b>${nomD(g.diam)}</b></td>
        <td class="pl-c">${formaSVG(g)}</td><td class="r"><b>${coma(Math.round(g.L))}</b></td><td class="r">${coma(g.n)}</td><td class="c">${esp}</td><td class="r">${coma(g.m, 1)}</td><td class="r">${coma(g.kg, 0)}</td>
        <td class="small" title="${nota}" style="white-space:nowrap"><span class="fuente ${tipo === 'dato' ? 'man' : 'med'}">${tipo}</span> ${corto}</td></tr>`;
    }).join('');
    const ds = Object.keys(A.totales).map(Number).sort((a, b) => a - b);
    const tot = ds.map(d => `<tr class="pl-tot"><td></td><td colspan="2">Total ${nomD(d)}</td><td></td><td></td><td></td><td></td><td class="r">${coma(A.totales[d].m, 1)}</td><td class="r">${coma(A.totales[d].kg, 0)}</td><td class="small">${cub && cub[d] != null ? 'cubicación: ' + coma(cub[d], 0) + ' kg' : ''}</td></tr>`).join('');
    const T = ds.reduce((a, d) => a + A.totales[d].kg, 0), M = ds.reduce((a, d) => a + A.totales[d].m, 0);
    return `<thead><tr><th class="c">Marca</th><th>Elemento · dónde</th><th class="c">ø</th><th>Forma y medidas (cm, sin escala)</th><th class="r">L (cm)</th><th class="r">Cant.</th><th class="c">Esp.</th><th class="r">m</th><th class="r">kg</th><th>Fuente</th></tr></thead>
      <tbody>${filas}${tot}<tr class="pl-tot pl-tt"><td></td><td colspan="2"><b>Total acero A630-420H</b></td><td></td><td></td><td></td><td></td><td class="r"><b>${coma(M, 1)}</b></td><td class="r"><b>${coma(T, 0)}</b></td><td class="small">sin pérdidas ni despuntes</td></tr></tbody>`;
  }

  // ---------- corte vertical del modelo: hormigón y barras, con marcas, recubrimientos y cotas ----------
  const el = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) if (attrs[k] !== undefined) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
  const txt = (p, x, y, t, a) => { const e = el('text', Object.assign({ x, y }, a || {}), p); e.textContent = t; return e; };
  function prismas(D, H) {
    const z0 = D.z_piso, L = z => z - z0, out = [];
    const add = (pts, zi, zs, cls, nombre) => { if (pts) out.push({ pts, zi: L(zi), zs: L(zs), cls, nombre }); };
    (H.losa_fundacion ? H.losa_fundacion.emplantillado.piezas : []).forEach(p => add(p.pts, H.losa_fundacion.emplantillado.z_inf, H.losa_fundacion.emplantillado.z_sup, 'ad-emp', 'emplantillado G5'));
    if (H.cimiento) { H.cimiento.emplantillado.piezas.forEach(p => add(p.pts, p.z_inf, p.z_sup, 'ad-emp', 'emplantillado G5')); }
    if (H.cf) H.cf.emplantillado.piezas.forEach(p => add(p.pts, H.cf.emplantillado.z_inf, H.cf.emplantillado.z_sup, 'ad-emp', 'emplantillado G5'));
    if (H.radier_estudio) H.radier_estudio.capas.forEach(c => c.piezas.forEach(p => add(p.pts, c.z_inf, c.z_sup, c.id === 'radier' ? 'ad-rad' : 'ad-capa', c.nombre)));
    (H.losa_fundacion ? H.losa_fundacion.piezas : []).forEach(p => add(p.pts, p.z_inf, p.z_sup, 'ad-h', 'losa de fundación'));
    H.muros.piezas.forEach(p => add(p.pts, H.muros.z_inf, H.muros.z_sup, 'ad-h', 'muro'));
    add(H.losa.pts, H.losa.z_inf, H.losa.z_sup, 'ad-h', 'losa');
    H.vigas.forEach(v => add(v.pts, v.z_inf, v.z_sup, 'ad-h', v.nombre));
    if (H.cimiento) { H.cimiento.zapata.piezas.forEach(p => add(p.pts, p.z_inf, p.z_sup, 'ad-h', 'cimiento corrido')); H.cimiento.sobrecimiento.piezas.forEach(p => add(p.pts, p.z_inf, p.z_sup, 'ad-h', 'sobrecimiento')); }
    if (H.cf) H.cf.piezas.forEach(p => add(p.pts, p.z_inf, p.z_sup, 'ad-h', 'CF'));
    return out;
  }
  function seccion(sv, D, H, A, cfg) {
    // cfg: { eje: 'x' | 'y' (plano x = c o y = c), c, u0, u1 (ventana en la otra coordenada), zmin, zmax (NPOG local), girar (true: u crece a la izquierda),
    //        llamadas: [[id, lx, lz, texto?]] (lx, lz en coordenadas del corte: u relativo a u0 y z local), rec: [[id, cara, valor, lado]], fs }
    const z0 = D.z_piso, k = cfg.eje === 'x' ? 0 : 1, ku = cfg.eje === 'x' ? 1 : 0, c = cfg.c, fs = cfg.fs || 9;
    const U = u => cfg.girar ? (cfg.u1 - u) : (u - cfg.u0), Y = z => -z, W = cfg.u1 - cfg.u0;
    const id = 'ad-clip-' + Math.random().toString(36).slice(2, 8);
    const cp = el('clipPath', { id }, el('defs', {}, sv)); el('rect', { x: 0, y: Y(cfg.zmax), width: W, height: cfg.zmax - cfg.zmin }, cp);
    const g = el('g', { 'clip-path': `url(#${id})` }, sv);
    // hormigón y capas cortados por el plano
    const cortes = [];
    prismas(D, H).forEach(p => {
      const vs = p.pts.map(q => q[k]), us = p.pts.map(q => q[ku]);
      if (c <= Math.min(...vs) + 0.01 || c >= Math.max(...vs) - 0.01) return;
      const a = U(Math.min(...us)), b = U(Math.max(...us)), x = Math.min(a, b), w = Math.abs(b - a);
      el('rect', { x, y: Y(p.zs), width: w, height: p.zs - p.zi, class: p.cls }, g); cortes.push({ x0: x, x1: x + w, zi: p.zi, zs: p.zs, cls: p.cls });
    });
    // terreno natural (−50) y quiebres donde el hormigón sigue fuera de la ventana
    if (cfg.ntn !== false) { const [a, b] = Array.isArray(cfg.ntn) ? cfg.ntn : [0, W]; el('line', { x1: a, y1: Y(-50), x2: b, y2: Y(-50), class: 'ad-ntn' }, g); }
    // barras: las que están en el plano (la más cercana de cada familia) como líneas; las que lo cruzan como puntos
    const lineas = [], puntos = [];
    D.fierros.forEach(f => {
      const sp = espaciado(f), tol = sp ? sp / 2 : 6; let mejor = null;
      instancias(f).forEach(pl => {
        const dk = pl.map(p => Math.abs(p[k] - c)), dmax = Math.max(...dk);
        if (dmax < tol) { if (!mejor || dmax < mejor.d) mejor = { d: dmax, pl }; return; }
        for (let i = 0; i + 1 < pl.length; i++) { const a = pl[i], b = pl[i + 1]; if ((a[k] - c) * (b[k] - c) < 0) { const t = (c - a[k]) / (b[k] - a[k]); puntos.push({ f, pl, u: U(a[ku] + t * (b[ku] - a[ku])), z: a[2] + t * (b[2] - a[2]) - z0 }); } }
      });
      if (mejor) lineas.push({ f, pl: mejor.pl, pts: mejor.pl.map(p => [U(p[ku]), p[2] - z0]) });
    });
    const dentro = (u, z) => u > -2 && u < W + 2 && z > cfg.zmin - 2 && z < cfg.zmax + 2;
    lineas.forEach(l => el('polyline', { points: l.pts.map(p => `${p[0].toFixed(2)},${Y(p[1]).toFixed(2)}`).join(' '), class: 'ad-b', 'stroke-width': Math.max(0.9, l.f.diam / 10) }, g));
    puntos.filter(p => dentro(p.u, p.z)).forEach(p => el('circle', { cx: p.u, cy: Y(p.z), r: 0.7 + p.f.diam / 20, class: 'ad-p' }, g));
    // marco de la ventana
    el('rect', { x: 0, y: Y(cfg.zmax), width: W, height: cfg.zmax - cfg.zmin, class: 'ad-marco' }, sv);
    // ---- ayudantes para rotular ----
    const enVentana = (a, b) => {   // tramo a→b (u, z) recortado a la ventana: [t0, t1] o null (Liang–Barsky)
      let t0 = 0, t1 = 1; const d = [b[0] - a[0], b[1] - a[1]];
      for (const [p, q] of [[-d[0], a[0]], [d[0], W - a[0]], [-d[1], a[1] - cfg.zmin], [d[1], cfg.zmax - a[1]]]) {
        if (Math.abs(p) < 1e-9) { if (q < 0) return null; continue; }
        const r = q / p; if (p < 0) { if (r > t1) return null; if (r > t0) t0 = r; } else { if (r < t0) return null; if (r < t1) t1 = r; }
      }
      return [t0, t1];
    };
    const geomDe = idf => {
      const ls = lineas.filter(l => l.f.id === idf), ps = puntos.filter(p => p.f.id === idf && dentro(p.u, p.z)), segs = [];
      ls.forEach(l => { for (let i = 0; i + 1 < l.pts.length; i++) { const a = l.pts[i], b = l.pts[i + 1], r = enVentana(a, b); if (r) segs.push({ a, b, t0: r[0], t1: r[1], obj: l }); } });
      return { ls, ps, segs, vacio: !segs.length && !ps.length, f: (ls[0] || ps[0] || {}).f };
    };
    const masCerca = (G, X, Z) => {   // punto de la barra más cercano a (X, Z), dentro de la ventana
      let best = null;
      G.segs.forEach(s => { const dx = s.b[0] - s.a[0], dz = s.b[1] - s.a[1], L2 = dx * dx + dz * dz; let t = L2 ? ((X - s.a[0]) * dx + (Z - s.a[1]) * dz) / L2 : 0; t = Math.max(s.t0, Math.min(s.t1, t)); const p = [s.a[0] + t * dx, s.a[1] + t * dz]; const d = Math.hypot(p[0] - X, (p[1] - Z) * 1); if (!best || d < best.d) best = { d, p, obj: s.obj }; });
      G.ps.forEach(q => { const d = Math.hypot(q.u - X, q.z - Z); if (!best || d < best.d) best = { d, p: [q.u, q.z], obj: q }; });
      return best;
    };
    const circMarca = (x, y, n) => { el('circle', { cx: x, cy: y, r: fs * 0.82, class: 'ad-mc' }, sv); txt(sv, x, y + fs * 0.34, n, { 'text-anchor': 'middle', 'font-size': fs * 0.92, class: 'ad-mt' }); };
    function llamada(idf, lx, lz, texto, opc) {
      const G = geomDe(idf); if (G.vacio) return;
      const X = lx, YY = Y(lz);
      const best = masCerca(G, X, lz); best.p[2] = best.obj;
      const obj = best.obj, f = obj.f, fila = A.filaDe(f, obj.pl);
      const marcas = fila ? [fila.marca] : A.marcasDe(idf);
      const izq = X < best.p[0];
      el('polyline', { points: `${best.p[0].toFixed(2)},${Y(best.p[1]).toFixed(2)} ${X + (izq ? fs * 0.9 : -fs * 0.9)},${YY} ${X},${YY}`, class: 'ad-ll' }, sv);
      el('circle', { cx: best.p[0], cy: Y(best.p[1]), r: 0.8, class: 'ad-lp' }, sv);
      let x = X + (izq ? -fs * 0.82 : fs * 0.82);
      marcas.forEach(n => { circMarca(x, YY, n); x += (izq ? -1 : 1) * fs * 1.8; });
      const n = G.ps.length, esp = espaciado(f);
      const t = texto || (G.ls.includes(obj) ? `${nomD(f.diam)}${esp ? '@' + esp : ''} L=${coma(Math.round(fila ? fila.L : segsDe(obj.pl).reduce((a, b) => a + b, 0)))}` : (esp ? `${nomD(f.diam)}@${esp}` : `${n > 1 ? n : ''}${nomD(f.diam)}`));
      txt(sv, x - (izq ? -fs * 0.8 : fs * 0.8) + (izq ? -fs * 0.15 : fs * 0.15), YY + fs * 0.34, t, { 'text-anchor': izq ? 'end' : 'start', 'font-size': fs, class: 'tx ad-lt' });
    }
    // recubrimiento: de la cara (z o u del corte) a la cara de la barra más cercana de esa familia
    function recubrimiento(idf, cara, valor, pos) {
      // cara 'z': cara horizontal a la altura valor; se mide sobre la vertical u = pos. Cara 'u': cara vertical en u = valor; se mide a la altura z = pos.
      const G = geomDe(idf); if (G.vacio) return null;
      const r = G.f.diam / 20, cand = [];
      G.segs.forEach(s => { const i = cara === 'z' ? 0 : 1, a = s.a[i], b = s.b[i]; if ((a - pos) * (b - pos) <= 0 && Math.abs(b - a) > 1e-6) { const t = (pos - a) / (b - a); if (t >= s.t0 - 1e-6 && t <= s.t1 + 1e-6) cand.push(cara === 'z' ? s.a[1] + t * (s.b[1] - s.a[1]) : s.a[0] + t * (s.b[0] - s.a[0])); } });
      G.ps.forEach(q => { if (cara === 'z' ? Math.abs(q.u - pos) < 4 : Math.abs(q.z - pos) < 4) cand.push(cara === 'z' ? q.z : q.u); });
      if (!cand.length) return null;
      const v = cand.reduce((m, x) => Math.abs(x - valor) < Math.abs(m - valor) ? x : m), sg = Math.sign(v - valor), rec = Math.abs(v - valor) - r, e = valor + sg * rec, t = 'r=' + cm(Math.round(rec * 2) / 2);
      if (cara === 'z') {
        el('line', { x1: pos, y1: Y(valor), x2: pos, y2: Y(e), class: 'ad-rc' }, sv); [valor, e].forEach(z => el('line', { x1: pos - 2, y1: Y(z), x2: pos + 2, y2: Y(z), class: 'ad-rc' }, sv));
        txt(sv, pos, Y(valor) + (sg > 0 ? fs * 1.05 : -fs * 0.4), t, { 'text-anchor': 'middle', 'font-size': fs * 0.85, class: 'ad-rt' });   // por fuera de la cara
      } else {
        const y = Y(pos); el('line', { x1: valor, y1: y, x2: e, y2: y, class: 'ad-rc' }, sv); [valor, e].forEach(u => el('line', { x1: u, y1: y - 2, x2: u, y2: y + 2, class: 'ad-rc' }, sv));
        txt(sv, valor - sg * 2, y + fs * 0.3, t, { 'text-anchor': sg > 0 ? 'end' : 'start', 'font-size': fs * 0.85, class: 'ad-rt' });
      }
      return rec;
    }
    // cota simple con marcas oblicuas
    function cotaH(xa, xb, z, t, dz) { const y = Y(z) + (dz || 0); el('line', { x1: xa, y1: y, x2: xb, y2: y, class: 'ad-ct' }, sv); [xa, xb].forEach(x => { el('line', { x1: x - 1.6, y1: y + 1.6, x2: x + 1.6, y2: y - 1.6, class: 'ad-ct2' }, sv); el('line', { x1: x, y1: Y(z), x2: x, y2: y + (dz > 0 ? 2 : -2), class: 'ad-ce' }, sv); }); txt(sv, (xa + xb) / 2, y - fs * 0.35, t, { 'text-anchor': 'middle', 'font-size': fs, class: 'ad-cn' }); }
    function cotaV(x, za, zb, t, dx) { const xx = x + (dx || 0); el('line', { x1: xx, y1: Y(za), x2: xx, y2: Y(zb), class: 'ad-ct' }, sv); [za, zb].forEach(z => { el('line', { x1: xx - 1.6, y1: Y(z) + 1.6, x2: xx + 1.6, y2: Y(z) - 1.6, class: 'ad-ct2' }, sv); el('line', { x1: x, y1: Y(z), x2: xx + ((dx || 0) > 0 ? 2 : -2), y2: Y(z), class: 'ad-ce' }, sv); }); const ym = (Y(za) + Y(zb)) / 2; txt(sv, xx - fs * 0.45, ym, t, { 'text-anchor': 'middle', 'font-size': fs, class: 'ad-cn', transform: `rotate(-90 ${xx - fs * 0.45} ${ym})` }); }
    function nivel(x, z, t, der) { el('line', { x1: x - 8, y1: Y(z), x2: x + 8, y2: Y(z), class: 'ad-ct' }, sv); el('polygon', { points: `${x},${Y(z)} ${x - 3},${Y(z) - 4.5} ${x + 3},${Y(z) - 4.5}`, class: 'ad-nv' }, sv); txt(sv, der ? x + 11 : x - 11, Y(z) - 1.5, t, { 'text-anchor': der ? 'start' : 'end', 'font-size': fs * 0.92, class: 'ad-lt' }); }
    return { U, Y, W, zmin: cfg.zmin, zmax: cfg.zmax, lineas, puntos, cortes, llamada, recubrimiento, cotaH, cotaV, nivel, fs };
  }

  window.Armaduras = { planilla, tablaHTML, formaSVG, seccion, KGM, nomD };
})();
