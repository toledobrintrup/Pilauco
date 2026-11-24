// Láminas del estudio «a la antigua» (Gabriel, 17-11-2026: «un plano a la antigua, como los que envió el ingeniero, así tal cual… el enfierrador
// quiere eso… con toda la formalidad que pondría un ingeniero civil estructural, mismo formato»). Cada lámina es un SVG en milímetros de papel
// (A1 apaisado, 841 × 594), con el marco y la viñeta de las láminas del proyecto del estudio (medidos de la lámina 01 rev 1), la letra de trazo
// único de los planos CAD (fuente_trazos.js), plantas a 1:50 y cortes a 1:20 con el despiece de las barras al lado.
// Nada se retipea: la geometría sale de DATA_ESTUDIO_EST.hormigon, las barras de DATA_ESTUDIO_EST.fierros (cortadas por el mismo plano que los
// cortes de la sección 07, con Armaduras.seccion) y las marcas de la planilla de doblado (Armaduras.planilla).
// La viñeta NO lleva nombre, timbre ni firma de ningún profesional: es un plano de trabajo para que lo vise el ingeniero del proyecto.
// Láminas: 01 fundaciones (visada el 24-11-2026), 02 losa de techo del búnker con sus vigas y el hueco, 03 escalera del búnker.
//   LaminasEstudio.lista                         → [{ n, id, titulo }]
//   LaminasEstudio.dibujar(contenedor, n, D, E)  → <svg> de la lámina n (D = DATA_ESTUDIO_EST, E = DATA_SITIO.estudio)
(function () {
  'use strict';
  const NS = 'http://www.w3.org/2000/svg';
  const el = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) if (attrs[k] != null) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
  const f2 = v => String(Math.round(v * 100) / 100);
  const coma = (v, d) => (+v).toLocaleString('es-CL', { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0, useGrouping: false });   // sin punto de miles, como en los planos: L=1179
  const cmt = v => coma(v, Math.abs(v - Math.round(v)) > 0.04 ? 1 : 0);   // 37,5 · 25 (medidas en cm, con un decimal solo si lo tiene)
  const nomD = d => d === 19 ? 'ø3/4"' : d === 22 ? 'ø22' : 'ø' + d;

  // ---------- hoja: A1 apaisado, marco y viñeta medidos de la lámina 01 rev 1 del proyecto (mm) ----------
  const HOJA = { w: 841, h: 594, mx0: 30.5, my0: 12.06, mx1: 830.5, my1: 582.1, vy: 512.1 };
  const CSS = `
    .lm-t{fill:none;stroke:#000;stroke-linecap:round;stroke-linejoin:round}
    .lm-f{fill:none;stroke:#000;stroke-width:.25}
    .lm-m{fill:none;stroke:#000;stroke-width:.35}
    .lm-g{fill:none;stroke:#000;stroke-width:.5}
    .lm-u2{fill:none;stroke:#000;stroke-width:.7}
    .lm-u1{fill:none;stroke:#000;stroke-width:.5}
    .lm-uc{fill:none;stroke:#000;stroke-width:.6}
    .lm-w{fill:#fff;stroke:none}
    .lm-tr{fill:none;stroke:#000;stroke-width:.13}
    .lm-pt{fill:none;stroke:#000;stroke-width:.24;stroke-linecap:round}
    .lm-e{fill:none;stroke:#000;stroke-width:.18;stroke-dasharray:5 1.6}
    .lm-o{fill:none;stroke:#000;stroke-width:.2;stroke-dasharray:1.6 1}
    .lm-b{fill:none;stroke:#000;stroke-linecap:round;stroke-linejoin:round}
    .lm-p{fill:#000;stroke:none}
    .lm-n{fill:#000;stroke:none}
    .lm-a{font-family:Arial,Helvetica,sans-serif;fill:#000}
    .lm-s{font-family:'Book Antiqua',Palatino,'Palatino Linotype',Georgia,serif;fill:#000}`;

  // ---------- letra de trazo único (romans) ----------
  function trazos(str, h) {
    const k = h / 21; let x = 0, d = '';
    for (const ch of String(str)) {
      let g = FUENTE_TRAZOS[ch];
      if (!g) { console.error('lámina: falta el glifo «' + ch + '» en fuente_trazos.js'); g = FUENTE_TRAZOS['?']; }
      for (const t of g.s) d += 'M' + t.map(p => f2(x + (p[0] - g.l) * k) + ' ' + f2((p[1] - 9) * k)).join('L');
      x += (g.r - g.l) * k;
    }
    return { d, w: x };
  }
  const anchoT = (str, h) => { const k = h / 21; let x = 0; for (const ch of String(str)) { const g = FUENTE_TRAZOS[ch] || FUENTE_TRAZOS['?']; x += (g.r - g.l) * k; } return x; };
  // T: texto de trazos con la línea base en (x, y). o: { a: 'm' centrado | 'e' a la derecha, rot: grados, obl: true (oblicua, como los rótulos de la viñeta) }
  function T(g, x, y, str, h, o) {
    o = o || {}; const t = trazos(str, h), dx = o.a === 'm' ? -t.w / 2 : o.a === 'e' ? -t.w : 0, dy = o.cv ? h / 2 : 0;   // cv: centrado también en altura
    const p = el('path', { d: t.d, class: 'lm-t', 'data-t': String(str), 'stroke-width': f2(o.sw || Math.max(0.13, h * 0.085)),   // data-t: el texto, para el revisor de textos que se pisan
      transform: `translate(${f2(x)} ${f2(y)})${o.rot ? ` rotate(${f2(o.rot)})` : ''}${dx || dy ? ` translate(${f2(dx)} ${f2(dy)})` : ''}${o.obl ? ' skewX(-15)' : ''}` }, g);
    p.w = t.w; return p;
  }
  // TA: texto en Arial (títulos, burbujas de ejes, nombres de la viñeta), como en las láminas del proyecto
  function TA(g, x, y, str, size, o) {
    o = o || {}; const t = el('text', { x: f2(x), y: f2(y), class: o.serif ? 'lm-s' : 'lm-a', 'font-size': f2(size), 'text-anchor': o.a === 'm' ? 'middle' : o.a === 'e' ? 'end' : 'start',
      'font-style': o.it ? 'italic' : null, 'font-weight': o.b ? 'bold' : null, transform: o.rot ? `rotate(${o.rot} ${f2(x)} ${f2(y)})` : null }, g);
    t.textContent = str; return t;
  }
  const L = (g, x1, y1, x2, y2, cls) => el('line', { x1: f2(x1), y1: f2(y1), x2: f2(x2), y2: f2(y2), class: cls || 'lm-f' }, g);
  const P = (g, pts, cls, cerrar) => el(cerrar ? 'polygon' : 'polyline', { points: pts.map(p => f2(p[0]) + ',' + f2(p[1])).join(' '), class: cls || 'lm-f' }, g);
  const R = (g, x, y, w, h, cls) => el('rect', { x: f2(x), y: f2(y), width: f2(w), height: f2(h), class: cls || 'lm-f' }, g);
  const C = (g, x, y, r, cls) => el('circle', { cx: f2(x), cy: f2(y), r: f2(r), class: cls || 'lm-f' }, g);
  // punta de flecha llena en (x, y), apuntando en la dirección (ux, uy)
  function punta(g, x, y, ux, uy, largo, medio) {
    const h = Math.hypot(ux, uy) || 1; ux /= h; uy /= h; const l = largo || 1.9, m = medio || 0.33, bx = x - ux * l, by = y - uy * l;
    return el('polygon', { points: `${f2(x)},${f2(y)} ${f2(bx - uy * m)},${f2(by + ux * m)} ${f2(bx + uy * m)},${f2(by - ux * m)}`, class: 'lm-n' }, g);
  }

  // ---------- tramas (achurados) de los cortes: dibujadas con líneas (los <pattern> se ven mal al reducir la lámina) ----------
  function trama(g, x, y, w, h, tipo) {
    if (w <= 0 || h <= 0) return; let d = '', pt = '';
    const raya = (x0, y0, hh, c, inv) => { let xa = x0 + c, ya = y0 + hh, xb = x0 + c + hh, yb = y0; if (xb <= x0 || xa >= x0 + w) return; if (xa < x0) { ya -= x0 - xa; xa = x0; } if (xb > x0 + w) { yb += xb - (x0 + w); xb = x0 + w; } if (inv) { ya = 2 * y0 + hh - ya; yb = 2 * y0 + hh - yb; } d += `M${f2(xa)} ${f2(ya)}L${f2(xb)} ${f2(yb)}`; };
    const rayas = (s, inv) => { for (let c = -h + s / 2; c < w; c += s) raya(x, y, h, c, inv); };
    const puntos = (dens, semilla) => { let a = semilla; const rnd = () => (a = (a * 16807) % 2147483647) / 2147483647, n = Math.round(w * h * dens); for (let i = 0; i < n; i++) pt += `M${f2(x + 0.25 + rnd() * (w - 0.5))} ${f2(y + 0.25 + rnd() * (h - 0.5))}h0.01`; };
    if (tipo === 'emp') rayas(0.62);                                      // emplantillado: rayado denso
    else if (tipo === 'pobre') { rayas(1.9); puntos(0.1, 11); }           // hormigón pobre: rayado abierto con áridos
    else if (tipo === 'rad') puntos(1.0, 5);                              // radier: hormigón
    else if (tipo === 'pol') { rayas(1.5); rayas(1.5, true); }            // poliestireno: rombos
    else if (tipo === 'sub') rayas(1.0, true);                            // sub base compactada
    else { const hb = 1.7; for (let yy = 0, i = 0; yy < h - 0.01; yy += hb, i++) { const hh = Math.min(hb, h - yy); for (let c = -hh + 0.5; c < w; c += 1.05) raya(x, y + yy, hh, c, i % 2 === 1); } }   // relleno granular: espiga
    if (d) el('path', { d, class: 'lm-tr' }, g); if (pt) el('path', { d: pt, class: 'lm-pt' }, g);
  }

  function hoja(cont, info) {
    const sv = el('svg', { xmlns: NS, viewBox: `0 0 ${HOJA.w} ${HOJA.h}`, class: 'lamina', role: 'img', 'aria-label': `Lámina ${info.n}: ${info.contenido.join(', ')}` });
    el('style', {}, sv).textContent = CSS;
    R(sv, 0, 0, HOJA.w, HOJA.h, 'lm-w');
    R(sv, 0.5, 2.1, 840, 589.9, 'lm-f');                                                         // línea de corte del papel
    R(sv, HOJA.mx0, HOJA.my0, HOJA.mx1 - HOJA.mx0, HOJA.my1 - HOJA.my0, 'lm-f');                 // marco
    vineta(sv, info);
    if (cont) cont.appendChild(sv);
    return sv;
  }

  // Viñeta: la misma franja de 70 mm de las láminas del proyecto (identificación, revisiones, nota, profesionales, mandante y número de lámina),
  // sin el nombre, el timbre ni los datos del proyectista: aquí va lo que es este plano y queda el espacio para la firma.
  function vineta(sv, info) {
    const g = el('g', { class: 'lm-vin' }, sv), y0 = HOJA.vy, y1 = HOJA.my1;
    L(g, HOJA.mx0, y0, HOJA.mx1, y0);
    [41.3, 67.0, 175.3, 197.6, 208.4, 220.7, 339.4, 560.8, 623.4, 655.5, 723.3].forEach(x => L(g, x, y0, x, y1));
    for (let i = 1; i <= 8; i++) { const y = y0 + 7.5 * i; L(g, 41.3, y, 197.6, y); L(g, 208.4, y, 339.4, y); }
    for (let i = 1; i <= 6; i++) L(g, 560.8, y0 + 10 * i, 655.5, y0 + 10 * i);
    R(g, 658.5, 515.1, 61.8, 64);
    L(g, 723.3, 572.1, HOJA.mx1, 572.1); L(g, 754.0, 572.1, 754.0, y1); L(g, 784.8, 572.1, 784.8, y1); L(g, 815.5, 552.1, 815.5, y1); L(g, 815.5, 552.1, HOJA.mx1, 552.1);
    // encabezados
    T(g, 37.0, 547.1, 'IDENTIFICACION', 2.3, { a: 'm', rot: -90 }); T(g, 204.1, 547.1, 'REVISIONES', 2.3, { a: 'm', rot: -90 });
    T(g, 54.15, 578.7, 'N°', 3, { a: 'm' }); T(g, 121.15, 578.7, 'DESCRIPCION', 3, { a: 'm' }); T(g, 186.45, 578.7, 'FECHA', 3, { a: 'm' });
    T(g, 214.55, 578.7, 'N°', 3, { a: 'm' }); T(g, 280.05, 578.7, 'OBSERVACIONES', 3, { a: 'm' });
    T(g, 592.1, 578.7, 'PROFESIONAL', 3, { a: 'm' }); T(g, 639.45, 578.7, 'FIRMA', 3, { a: 'm' });
    // identificación: de dónde sale el plano (de abajo hacia arriba, como las revisiones)
    (info.identificacion || []).forEach((f, i) => { const y = 572.1 - 7.5 * i - 2.6; T(g, 54.15, y, f[0], 1.9, { a: 'm' }); T(g, 69.2, y, f[1], 1.9); T(g, 186.45, y, f[2], 1.9, { a: 'm' }); });
    (info.revisiones || []).forEach((f, i) => { const y = 572.1 - 7.5 * i - 2.6; T(g, 214.55, y, f[0], 1.9, { a: 'm' }); T(g, 223.2, y, f[1], 1.9); });
    // nota
    T(g, 341.6, 516.6, 'NOTA:', 1.9);
    (info.nota || []).forEach((t, i) => T(g, 341.6, 522.6 + 4.6 * i, t, 2.1));
    // profesionales (sin nombres: el plano no está firmado)
    (info.profesionales || []).forEach((t, i) => T(g, 563.2, 528.1 + 10 * i, t, 1.75));
    // caja central: qué es este plano (en las láminas del proyecto va aquí el timbre del proyectista)
    TA(g, 689.4, 527.5, 'ESTUDIO PILAUCO', 5.4, { a: 'm', b: true });
    T(g, 689.4, 534.6, 'Estudio de grabación con búnker', 2.1, { a: 'm' });
    L(g, 664.5, 539.2, 714.3, 539.2);
    TA(g, 689.4, 547.6, 'PLANO DE TRABAJO', 4.6, { a: 'm' });
    T(g, 689.4, 554.2, 'dibujado desde el modelo del sitio', 1.9, { a: 'm' });
    R(g, 664.5, 563.2, 49.8, 11.4, 'lm-m');
    T(g, 689.4, 568.0, 'SIN FIRMA', 2.6, { a: 'm', sw: 0.3 }); if (info.pie) T(g, 689.4, 572.3, info.pie, 1.7, { a: 'm' });
    // bloque derecho
    T(g, 727.4, 521.6, 'MANDANTE:', 1.9, { obl: true }); TA(g, 752.3, 522.4, info.mandante, 4.5);
    T(g, 727.4, 532.6, 'PROYECTO:', 1.9, { obl: true }); TA(g, 751.5, 533.4, info.proyecto, 4.5);
    info.contenido.forEach((t, i) => T(g, 777, 544.6 + 3.5 * i, (i ? '' : 'CONTENIDO : ') + t, 1.9, { a: 'm', obl: true }));
    L(g, 727.2, 556.2, 756.9, 556.2); T(g, 727.4, 559.5, 'FIRMA REPRESENTANTE', 1.9, { obl: true });
    T(g, 727.4, 563.4, 'Fecha : ' + info.fecha, 1.9, { obl: true }); T(g, 727.4, 566.9, 'Ubicacion : Pilauco', 1.9, { obl: true });
    T(g, 725.2, 578.3, 'ESCALAS: INDICADAS', 1.6, { obl: true }); T(g, 756.0, 578.3, 'N° PLANO: ' + info.plano, 1.6, { obl: true });
    T(g, 786.4, 578.3, 'SUP. LÁMINA: 0,50 m²', 1.6, { obl: true }); T(g, 817.0, 578.3, 'REV:', 1.6, { obl: true }); TA(g, 824.4, 580.4, info.rev, 5.7, { serif: true });
    T(g, 816.7, 555.0, 'Lámina N°', 1.5, { obl: true }); TA(g, 823.0, 569.6, info.n, 10, { a: 'm' });
  }

  // ---------- ayudantes de dibujo en papel (mm) ----------
  // título de vista, como en las láminas: nombre en Arial, escala y unidad en letra de trazos
  function titulo(g, x, y, nombre, esc, unidad) {
    TA(g, x, y, nombre, 8.36); T(g, x + 0.6, y + 4.6, 'ESC. 1:' + esc, 2.5); T(g, x + 0.9, y + 8.7, 'Medidas en ' + (unidad || 'cm') + '.', 2.2);
  }
  // cota: línea con puntas de flecha y trazos de referencia; el número va sobre la línea (o a su izquierda si es vertical)
  function cotaH(g, x1, x2, y, t, o) {
    o = o || {}; const h = o.h || 2.5;
    L(g, x1, y, x2, y); [x1, x2].forEach(x => L(g, x, y - 1.1, x, y + 1.1));
    if (Math.abs(x2 - x1) > 5.5) { punta(g, x1, y, -1, 0); punta(g, x2, y, 1, 0); } else { L(g, x1 - 0.8, y + 0.8, x1 + 0.8, y - 0.8); L(g, x2 - 0.8, y + 0.8, x2 + 0.8, y - 0.8); }
    if (o.ref) o.ref.forEach(([x, ya]) => L(g, x, ya, x, y + (ya < y ? 1.1 : -1.1)));
    const w = anchoT(t, h), xm = o.tx != null ? o.tx : (x1 + x2) / 2;
    if (w > Math.abs(x2 - x1) - 1 && !o.dentro) { if (o.fuera === 'izq2') T(g, Math.min(x1, x2) - 1.6, y + h + 1.1, t, h, { a: 'e' }); else T(g, o.fuera === 'izq' ? Math.min(x1, x2) - w - 1.6 : Math.max(x1, x2) + 1.6, y - 0.9, t, h); }   // no cabe: al lado
    else T(g, xm, y - 0.9, t, h, { a: 'm' });
  }
  function cotaV(g, x, y1, y2, t, o) {
    o = o || {}; const h = o.h || 2.5;
    L(g, x, y1, x, y2); [y1, y2].forEach(y => L(g, x - 1.1, y, x + 1.1, y));
    if (Math.abs(y2 - y1) > 5.5) { punta(g, x, Math.min(y1, y2), 0, -1); punta(g, x, Math.max(y1, y2), 0, 1); } else { [y1, y2].forEach(y => L(g, x - 0.8, y + 0.8, x + 0.8, y - 0.8)); }
    if (o.ref) o.ref.forEach(([xa, y]) => L(g, xa, y, x + (xa < x ? 1.1 : -1.1), y));
    const w = anchoT(t, h), ym = o.ty != null ? o.ty : (y1 + y2) / 2;
    if (w > Math.abs(y2 - y1) - 1 && !o.dentro) { if (o.lado === 'izq') T(g, x - 1.8, ym + h / 2, t, h, { a: 'e' }); else if (o.abajo) T(g, x - 0.9, Math.max(y1, y2) + 1.6, t, h, { rot: -90, a: 'e' }); else T(g, x - 0.9, Math.min(y1, y2) - 1.6, t, h, { rot: -90 }); }   // no cabe: al lado, antes o después de la cota
    else T(g, x - 0.9, ym, t, h, { a: 'm', rot: -90 });
  }
  // burbuja de eje (círculo con el nombre en Arial)
  function burbuja(g, x, y, t) { C(g, x, y, 4.8, 'lm-f'); TA(g, x, y + (t.length > 1 ? 1.85 : 2.2), t, t.length > 1 ? 5.2 : 6.2, { a: 'm' }); }
  // marca de corte: dos escuadras con trazos entre ellas y la letra en cada punta (a ⌐ — — ¬ a); (x1,y1)-(x2,y2) es la línea de corte y (nx,ny) hacia dónde se mira
  function marcaCorte(g, x1, y1, x2, y2, nx, ny, letra) {
    const dx = x2 - x1, dy = y2 - y1, h = Math.hypot(dx, dy), ux = dx / h, uy = dy / h, e = 3.2, c = 'lm-u1';
    P(g, [[x1 + nx * e, y1 + ny * e], [x1, y1], [x1 + ux * 4, y1 + uy * 4]], c); P(g, [[x2 + nx * e, y2 + ny * e], [x2, y2], [x2 - ux * 4, y2 - uy * 4]], c);
    const n = Math.max(1, Math.round((h - 8) / 9)), paso = (h - 8) / n;
    for (let i = 0; i < n; i++) { const a = 4 + paso * i + paso * 0.2, b = 4 + paso * i + paso * 0.8; L(g, x1 + ux * a, y1 + uy * a, x1 + ux * b, y1 + uy * b, c); }
    const rot = Math.abs(ux) > Math.abs(uy) ? 0 : -90;
    [[x1 - ux * 4.2, y1 - uy * 4.2], [x2 + ux * 4.2, y2 + uy * 4.2]].forEach(([x, y]) => TA(g, x, y, letra, 7.3, { a: 'm', rot, }).setAttribute('dominant-baseline', 'central'));
  }
  // llamada: texto subrayado y línea hasta el punto (px, py); lado 'd' = texto a la derecha del quiebre, 'i' = a la izquierda
  function llamada(g, px, py, tx, ty, textos, o) {
    o = o || {}; const h = o.h || 2.5, w = Math.max(...textos.map(t => anchoT(t, h))), izq = o.lado === 'i';
    const xa = tx, xb = izq ? tx - w - 1 : tx + w + 1;
    L(g, xa, ty, xb, ty); L(g, xa, ty, px, py);
    if (o.punta !== false) { if (o.circ) C(g, px, py, o.circ, 'lm-f'); else punta(g, px, py, px - xa, py - ty, 1.7, 0.3); }
    textos.forEach((t, i) => T(g, izq ? xb + 0.5 : xa + 0.5, ty - 0.9 + (i ? (h + 1.3) * i + 0.6 : 0), t, h));
  }
  // nivel: rótulo subrayado y flecha vertical hasta la cota (px, py)
  function nivel(g, px, py, t, o) {
    o = o || {}; const h = o.h || 2.5, w = anchoT(t, h), alto = o.alto || 7, izq = o.lado === 'i', y = py - alto, xa = izq ? px - w - 1.5 : px - 1.5, xb = izq ? px + 1.5 : px + w + 1.5;
    L(g, xa, y, xb, y); L(g, px, y, px, py); punta(g, px, py, 0, 1, 1.9, 0.33); T(g, izq ? xa + 0.6 : px + 0.9, y - 0.9, t, h);
  }
  // unión de rectángulos: se dibuja el contorno de todos y después se tapa con sus rellenos, así desaparecen las líneas interiores
  function union(g, rects, cls) { rects.forEach(r => R(g, r[0], r[1], r[2] - r[0], r[3] - r[1], cls)); rects.forEach(r => R(g, r[0], r[1], r[2] - r[0], r[3] - r[1], 'lm-w')); }
  const caja = pts => { const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]); return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)]; };

  // ---------- planta de fundaciones (1:50) ----------
  function plantaFundaciones(sv, D, H, E, X0, Y0) {
    const k = 10 / 50, ox = E.origen[0], oy = E.origen[1], X = x => X0 + (x - ox) * k, Y = y => Y0 + (y - oy) * k, XL = x => X0 + x * k, YL = y => Y0 + y * k;
    const g = el('g', { class: 'lm-planta' }, sv), rc = r => [X(r[0]), Y(r[1]), X(r[2]), Y(r[3])];
    const LF = caja(H.losa_fundacion.pts), mu = H.muros.piezas.map(p => caja(p.pts)), ext = [Math.min(...mu.map(m => m[0])), Math.min(...mu.map(m => m[1])), Math.max(...mu.map(m => m[2])), Math.max(...mu.map(m => m[3]))];
    const int = [ext[0] + H.muros.espesor, ext[1] + H.muros.espesor, ext[2] - H.muros.espesor, ext[3] - H.muros.espesor];
    const CC = H.cimiento.zapata.piezas.map(p => caja(p.pts)), SC = H.cimiento.sobrecimiento.piezas.map(p => caja(p.pts)), CF = H.cf.piezas.map(p => caja(p.pts)), DA = H.dados.piezas.map(p => caja(p.pts));
    // 1) lo de más abajo: losa de fundación del búnker, cimientos corridos y dados (línea fina)
    union(g, [rc(LF)].concat(CC.map(rc)), 'lm-u1');
    DA.forEach(d => R(g, X(d[0]), Y(d[1]), (d[2] - d[0]) * k, (d[3] - d[1]) * k, 'lm-f'));
    // 2) lo que sube: muros del búnker, sobrecimientos y cadenas de fundación (línea media); el interior del búnker queda a la vista
    union(g, mu.map(rc), 'lm-u2');
    union(g, SC.map(rc).concat(CF.map(rc)), 'lm-u2');
    // los dados siguen bajo los CF: su contorno, de trazos donde lo tapa la cadena
    DA.forEach((d, i) => { const c = H.dados.piezas[i]; P(g, [[X(d[0]), Y(d[1])], [X(d[2]), Y(d[1])], [X(d[2]), Y(d[3])], [X(d[0]), Y(d[3])]], 'lm-o', true); });
    // 3) insertos (placas embebidas) bajo cada pilar: contorno con cruz
    H.placas.lista.forEach(q => {
      const b = caja(q.pts); P(g, q.pts.map(p => [X(p[0]), Y(p[1])]), 'lm-m', true);
      L(g, X(b[0]), Y(b[1]), X(b[2]), Y(b[3]), 'lm-f'); L(g, X(b[2]), Y(b[1]), X(b[0]), Y(b[3]), 'lm-f');
    });
    return { g, k, X, Y, XL, YL, LF, ext, int, CC, SC, CF, DA };
  }

  // ---------- barras del modelo ----------
  const instancias = f => f.polilineas ? f.polilineas : Array.from({ length: f.n }, (_, i) => f.polilinea.map(p => [p[0] + f.paso[0] * i, p[1] + f.paso[1] * i, p[2] + f.paso[2] * i]));
  const d3 = (a, b) => Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]);
  const espDe = f => { if (f.paso && f.n > 1) { const p = Math.hypot(f.paso[0], f.paso[1], f.paso[2]); if (p > 0.1) return Math.round(p); } const m = /ø[\d\/"]+@(\d+)/.exec(f.d || ''); return m ? +m[1] : null; };
  // círculo con la marca de la planilla de doblado
  function marca(g, x, y, n, r) { r = r || 2.3; const h = r * (String(n).length > 2 ? 0.64 : 0.86); C(g, x, y, r, 'lm-f'); T(g, x, y + h * 0.49, String(n), h, { a: 'm' }); }   // tres cifras (desde la marca 100): letra más chica, para que quepa en el mismo círculo
  // Barra en planta, como en la «Planta losa» del proyecto: una barra de la familia dibujada entera, con su rótulo (marca, ø, separación y largo)
  // a lo largo, y la línea de reparto con flechas hasta la primera y la última barra. o: { en: coordenada (cm locales) de la barra elegida,
  // rep: coordenada de la línea de reparto, t: posición del rótulo (0–1), texto: sufijo («inf.», «sup.»), lado: 1 | −1 }
  function barraPlanta(g, V, PL, f, o) {
    const ins = o.filtro ? instancias(f).filter(o.filtro) : instancias(f);   // o.filtro: solo algunas barras de la familia (las de un muro, las de una forma)
    if (!ins.length) { console.error('lámina: sin barras de', f.id, 'para la planta'); return null; }
    const eje = o.eje != null ? o.eje : Math.abs(ins[0][0][0] - ins[ins.length - 1][0][0]) > Math.abs(ins[0][0][1] - ins[ins.length - 1][0][1]) ? 0 : 1;   // eje en que se reparten (o.eje lo fuerza)
    const co = pl => pl[0][eje] - (eje ? V.oy : V.ox), pl = ins.reduce((m, q) => Math.abs(co(q) - o.en) < Math.abs(co(m) - o.en) ? q : m), fila = PL.filaDe(f, pl);
    // «Destacado» (el ingeniero, 22-11-2026: «el dibujo de la barra con todos sus dobleces y largos respectivos, además de su largo total»): la barra va
    // en su lugar y sus dobleces, que en planta no se ven, se abaten sobre el dibujo a escala (los que suben, a un lado; los que bajan, al otro), cada tramo con su medida por fuera
    const p3 = pl.filter((q, i) => i === 0 || d3(q, pl[i - 1]) > 0.05), sL = p3.slice(1).map((q, i) => d3(p3[i], q)); let iM = 0; sL.forEach((v, i) => { if (v > sL[iM]) iM = i; });
    const A3 = p3[iM], B3 = p3[iM + 1], a = [V.X(A3[0]), V.Y(A3[1])], b = [V.X(B3[0]), V.Y(B3[1])], lm = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1, mx = (b[0] - a[0]) / lm, my = (b[1] - a[1]) / lm;
    const hor = Math.abs(b[0] - a[0]) > Math.abs(b[1] - a[1]), lado = o.lado || 1, L3 = d3(A3, B3), u3 = [(B3[0] - A3[0]) / L3, (B3[1] - A3[1]) / L3];
    let nx = -my, ny = mx; if (hor ? ny > 0 : nx < 0) { nx = -nx; ny = -ny; }   // los dobleces que suben se abaten hacia arriba del papel (barra horizontal) o hacia la derecha (vertical)
    const des = p3.map(q => { const t = (q[0] - A3[0]) * u3[0] + (q[1] - A3[1]) * u3[1], z = (q[2] - A3[2]) * lado; return [a[0] + (mx * t + nx * z) * V.k, a[1] + (my * t + ny * z) * V.k]; });
    P(g, des, 'lm-b').setAttribute('stroke-width', '0.6');
    const t = o.t == null ? 0.5 : o.t, tx = a[0] + (b[0] - a[0]) * t, ty = a[1] + (b[1] - a[1]) * t, esp = espDe(f);
    const rot = `${nomD(f.diam)}${esp ? '@' + esp : ''}, L=${coma(Math.round(fila ? fila.L : 0))}${o.texto ? ' ' + o.texto : ''}`, w = anchoT(rot, 2.3);
    if (o.rotulo) { const wx = V.XL(o.rotulo[0]), wy = V.YL(o.rotulo[1]), izq = o.rotulo[2] === 'i', w2 = anchoT(rot, 2.1);   // rótulo aparte, con su línea hasta la barra
      llamada(g, tx, ty, wx, wy, [rot], { h: 2.1, lado: izq ? 'i' : 'd', circ: 0.7 }); if (fila) marca(g, izq ? wx - w2 - 4 : wx + w2 + 4, wy - 1.1, fila.marca, 2.1); }
    else if (hor) { if (fila) marca(g, tx - w / 2 - 3.6, ty - 2.6, fila.marca); T(g, tx, ty - 1.3, rot, 2.3, { a: 'm' }); }
    else { if (fila) marca(g, tx - 2.6, ty + w / 2 + 3.6, fila.marca); T(g, tx - 1.3, ty, rot, 2.3, { a: 'm', rot: -90 }); }
    if (fila && fila.ext && fila.ext.length === sL.length && sL.length > 1) {
      const hh = 1.9, cx = des.reduce((q, v) => q + v[0], 0) / des.length, cy = des.reduce((q, v) => q + v[1], 0) / des.length;
      sL.forEach((v, i) => {
        const txt = cmt(fila.ext[i]), q0 = des[i], q1 = des[i + 1], Mx = (q0[0] + q1[0]) / 2, My = (q0[1] + q1[1]) / 2, len = Math.hypot(q1[0] - q0[0], q1[1] - q0[1]) || 1;
        if (i === iM) { if (hor) T(g, tx, ty + 1.3 + hh, txt, hh, { a: 'm' }); else T(g, tx + 1.3 + hh, ty, txt, hh, { a: 'm', rot: -90 }); return; }   // tramo principal: al otro lado del rótulo
        let ox = -(q1[1] - q0[1]) / len, oy = (q1[0] - q0[0]) / len; if ((Mx - cx) * ox + (My - cy) * oy < 0) { ox = -ox; oy = -oy; }   // hacia afuera de la figura
        if (Math.abs(ox) > Math.abs(oy)) T(g, Mx + ox * 0.9, My + hh / 2, txt, hh, ox > 0 ? {} : { a: 'e' });
        else { if (!hor) oy = -oy; T(g, Mx, oy < 0 ? My - 0.9 : My + 0.9 + hh, txt, hh, { a: 'm' }); }   // barra vertical: la medida del gancho va hacia adentro, lejos del borde de la losa y de sus cotas
      });
    }
    // línea de reparto
    const c0 = o.filtro ? Math.min(...ins.map(co)) : co(ins[0]), c1 = o.filtro ? Math.max(...ins.map(co)) : co(ins[ins.length - 1]);
    if (o.rep != null) {
      if (hor) { const x = V.XL(o.rep), y0 = V.YL(Math.min(c0, c1)), y1 = V.YL(Math.max(c0, c1)); if (!o.sinLinea) { L(g, x, y0, x, y1); punta(g, x, y0, 0, -1); punta(g, x, y1, 0, 1); L(g, x - 1.2, y0, x + 1.2, y0); L(g, x - 1.2, y1, x + 1.2, y1); } C(g, x, a[1], 0.8, 'lm-f'); }
      else { const y = V.YL(o.rep), x0 = V.XL(Math.min(c0, c1)), x1 = V.XL(Math.max(c0, c1)); if (!o.sinLinea) { L(g, x0, y, x1, y); punta(g, x0, y, -1, 0); punta(g, x1, y, 1, 0); L(g, x0, y - 1.2, x0, y + 1.2); L(g, x1, y - 1.2, x1, y + 1.2); } C(g, a[0], y, 0.8, 'lm-f'); }
    }
    return fila;
  }
  // ---------- cortes del modelo ----------
  let nClip = 0;
  const medio = v => Math.round(v * 2) / 2;
  const tramaDe = c => c.nombre === 'emplantillado G5' ? 'emp' : c.nombre === 'hormigón pobre G5' ? 'pobre' : c.cls === 'ad-rad' ? 'rad' : /oliestireno/.test(c.nombre || '') ? 'pol' : /estabilizado/.test(c.nombre || '') ? 'sub' : 'rel';
  function quiebre(g, x1, y1, x2, y2) {   // línea de quiebre: recta con un zigzag al medio, pasada 1,5 de cada punta
    const dx = x2 - x1, dy = y2 - y1, h = Math.hypot(dx, dy) || 1, ux = dx / h, uy = dy / h, nx = -uy, ny = ux, mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
    P(g, [[x1 - ux * 1.5, y1 - uy * 1.5], [mx - ux * 1.3, my - uy * 1.3], [mx - ux * 0.45 + nx * 1.1, my - uy * 0.45 + ny * 1.1], [mx + ux * 0.45 - nx * 1.1, my + uy * 0.45 - ny * 1.1], [mx + ux * 1.3, my + uy * 1.3], [x2 + ux * 1.5, y2 + uy * 1.5]], 'lm-f');
  }
  function terreno(g, x1, x2, y, rotulo) { if (rotulo) T(g, Math.min(x1, x2) + 0.8, y - 1.1, rotulo, 2.1); L(g, x1, y, x2, y, 'lm-m'); for (let x = Math.min(x1, x2) + 2; x < Math.max(x1, x2) - 2.5; x += 6.5) for (let i = 0; i < 3; i++) L(g, x + i * 0.9, y + 0.25, x + i * 0.9 - 1.3, y + 1.8, 'lm-f'); }
  // Corta el modelo por un plano vertical (el mismo motor de la sección 07: Armaduras.seccion) y lo dibuja a escala con el grafismo de las láminas:
  // hormigón en contorno, emplantillado y capas con trama, barras del plano en línea gruesa y barras que lo cruzan en punto.
  // cfg: el de Armaduras.seccion ({ eje, c, u0, u1, zmin, zmax, girar, ntn }); (X0, Y0): dónde cae en el papel el punto u = 0, z = 0 (mm); esc: 20 → 1:20
  function corte(sv, D, PL, cfg, X0, Y0, esc) {
    const H = D.hormigon, k = 10 / esc, S = window.Armaduras.seccion(document.createElementNS(NS, 'svg'), D, H, PL, cfg);
    const X = u => X0 + u * k, Y = z => Y0 - z * k, W = S.W, za = cfg.zmin, zb = cfg.zmax;
    const g = el('g', { class: 'lm-corte' }, sv), id = 'lm-clip' + (++nClip);
    el('rect', { x: f2(X(0)), y: f2(Y(zb)), width: f2(W * k), height: f2((zb - za) * k) }, el('clipPath', { id }, g));
    const gc = el('g', { 'clip-path': `url(#${id})` }, g);
    // piezas cortadas; se cierran los 0,5 cm que el modelo deja entre piezas (son para el 3D)
    const piezas = S.cortes.map(c => Object.assign({}, c));
    piezas.forEach(c => piezas.forEach(o => { if (o !== c && o.zs < c.zi + 0.01 && o.zs > c.zi - 0.75 && o.x0 < c.x1 - 0.01 && o.x1 > c.x0 + 0.01) c.zi = Math.min(c.zi, o.zs); }));
    const hs = piezas.filter(c => c.cls === 'ad-h'), ot = piezas.filter(c => c.cls !== 'ad-h');
    ot.forEach(c => { R(gc, X(c.x0), Y(c.zs), (c.x1 - c.x0) * k, (c.zs - c.zi) * k, 'lm-f'); const xa = Math.max(c.x0, 0), xb = Math.min(c.x1, W), zt = Math.min(c.zs, zb), zi = Math.max(c.zi, za); trama(gc, X(xa), Y(zt), (xb - xa) * k, (zt - zi) * k, tramaDe(c)); });
    union(gc, hs.map(c => [X(c.x0), Y(c.zs), X(c.x1), Y(c.zi)]), 'lm-uc');
    // quiebres donde las piezas siguen fuera de la ventana: uno por cada tramo continuo de cada borde
    const bordes = { izq: [], der: [], arr: [], aba: [] };
    piezas.forEach(c => {
      if (c.zs <= za || c.zi >= zb || c.x1 <= 0 || c.x0 >= W) return;
      const ya = Y(Math.min(c.zs, zb)), yb = Y(Math.max(c.zi, za)), xa = X(Math.max(c.x0, 0)), xb = X(Math.min(c.x1, W));
      if (c.x0 < -0.5) bordes.izq.push([ya, yb]); if (c.x1 > W + 0.5) bordes.der.push([ya, yb]); if (c.zs > zb + 0.5) bordes.arr.push([xa, xb]); if (c.zi < za - 0.5) bordes.aba.push([xa, xb]);
    });
    const junta = iv => { iv.sort((p, q) => p[0] - q[0]); const o = []; iv.forEach(v => { const u = o[o.length - 1]; if (u && v[0] <= u[1] + 0.6) u[1] = Math.max(u[1], v[1]); else o.push(v.slice()); }); return o; };
    junta(bordes.izq).forEach(v => quiebre(g, X(0), v[0], X(0), v[1])); junta(bordes.der).forEach(v => quiebre(g, X(W), v[0], X(W), v[1]));
    junta(bordes.arr).forEach(v => quiebre(g, v[0], Y(zb), v[1], Y(zb))); junta(bordes.aba).forEach(v => quiebre(g, v[0], Y(za), v[1], Y(za)));
    if (cfg.ntn) terreno(g, X(cfg.ntn[0]), X(cfg.ntn[1]), Y(-50), cfg.ntnRotulo);
    // barras. Armaduras.seccion deja una sola barra del plano por familia (la más cercana); si hay otras a la misma distancia (las dos patas de un
    // par simétrico, como las verticales de anclaje del dado), aquí se suman para que el corte las muestre todas
    const kp = cfg.eje === 'x' ? 0 : 1, kq = 1 - kp, lejos = pl => Math.max(...pl.map(p => Math.abs(p[kp] - cfg.c))), igual = (a, b) => a.length === b.length && a.every((p, i) => d3(p, b[i]) < 0.01);
    S.lineas.slice().forEach(l => { const d0 = lejos(l.pl); instancias(l.f).forEach(pl => { if (Math.abs(lejos(pl) - d0) < 0.3 && !S.lineas.some(q => q.f === l.f && igual(q.pl, pl))) S.lineas.push({ f: l.f, pl, pts: pl.map(p => [S.U(p[kq]), p[2] - D.z_piso]) }); }); });
    const ancho = f => Math.max(0.5, f.diam / 10 * k);
    S.lineas.forEach(l => P(gc, l.pts.map(p => [X(p[0]), Y(p[1])]), 'lm-b').setAttribute('stroke-width', f2(ancho(l.f))));
    const noPt = cfg.sinPuntos || [], dentro = (u, z) => u > -0.5 && u < W + 0.5 && z > za - 0.5 && z < zb + 0.5, pts = S.puntos.filter(p => dentro(p.u, p.z) && !noPt.includes(p.f.id));
    pts.forEach(p => C(gc, X(p.u), Y(p.z), Math.max(0.42, p.f.diam / 20 * k), 'lm-p'));
    // familias proyectadas al plano del corte (los estribos en la elevación de una viga): una línea fina por barra; quedan en S.lineas para poder rotularlas
    (cfg.proyectar || []).forEach(idf => { const f = D.fierros.find(q => q.id === idf); if (!f) return; instancias(f).forEach(pl => { const q = pl.map(p => [S.U(p[kq]), p[2] - D.z_piso]);
      P(gc, q.map(p => [X(p[0]), Y(p[1])]), 'lm-b').setAttribute('stroke-width', '0.28'); S.lineas.push({ f, pl, pts: q, proy: true }); }); });
    // punto de la familia idf más cercano a (u, z), dentro de la ventana
    function cerca(idf, u, z) {
      let best = null; const ku = z != null && u != null ? 0.25 : 1, dist = (qu, qz) => Math.hypot((qu - (u == null ? qu : u)) * ku, qz - (z == null ? qz : z));
      S.lineas.filter(l => l.f.id === idf).forEach(l => { for (let i = 0; i + 1 < l.pts.length; i++) { const a = l.pts[i], b = l.pts[i + 1]; for (let n = 0; n <= 60; n++) { const q = [a[0] + (b[0] - a[0]) * n / 60, a[1] + (b[1] - a[1]) * n / 60]; if (!dentro(q[0], q[1])) continue; const d = dist(q[0], q[1]); if (!best || d < best.d) best = { d, u: q[0], z: q[1], f: l.f, pl: l.pl, linea: true }; } } });
      pts.filter(p => p.f.id === idf).forEach(p => { const d = dist(p.u, p.z); if (!best || d < best.d) best = { d, u: p.u, z: p.z, f: p.f, pl: p.pl, linea: false }; });
      return best;
    }
    const textoDe = b => { const n = pts.filter(p => p.f.id === b.f.id).length, esp = espDe(b.f); return b.linea || esp ? `${nomD(b.f.diam)}${esp ? '@' + esp : ''}` : `${n}${nomD(b.f.diam)}`; };
    // rótulos apilados en una columna al lado del corte, en el orden vertical de sus barras: items = [[id, texto | null, z | null, u | null]]
    function rotulos(items, xCol, o) {
      o = o || {}; const h = o.h || 2.5, gap = o.gap || 6.4, izq = !!o.izq;
      const fs = items.map(it => { const b = cerca(it[0], it[3] != null ? it[3] : (izq ? 0 : W), it[2]); if (!b) { console.error('lámina: sin barra para el rótulo', it[0]); return null; } return { b, t: it[1] || textoDe(b) }; }).filter(Boolean).sort((p, q) => q.b.z - p.b.z);
      let yp = -1e9; fs.forEach(f => { f.y = Math.max(Y(f.b.z), yp + gap); yp = f.y; });
      if (o.yMax != null) { let lim = o.yMax; for (let i = fs.length - 1; i >= 0; i--) { if (fs[i].y > lim) fs[i].y = lim; lim = fs[i].y - gap; } }
      fs.forEach(f => {
        const w = anchoT(f.t, h); llamada(g, X(f.b.u), Y(f.b.z), xCol, f.y, [f.t], { lado: izq ? 'i' : 'd', h, circ: f.b.linea ? null : 1 });
        const ms = f.b.linea ? [PL.filaDe(f.b.f, f.b.pl)] : pts.filter(p => p.f.id === f.b.f.id).map(p => PL.filaDe(p.f, p.pl));
        const ns = [...new Set(ms.filter(Boolean).map(m => m.marca))].sort((a, b) => a - b);   // barras en punta: todas las marcas de la familia que se ven en el corte
        if (o.marcas !== false) ns.forEach((n, i) => marca(g, (izq ? xCol - w - 1 - 2.9 : xCol + w + 1 + 2.9) + (izq ? -1 : 1) * 4.7 * i, f.y - 1.1, n, 2.1));
      });
      return fs;
    }
    // despiece: la barra de la familia que está en el plano, dibujada aparte (corrida dx, dy mm desde su lugar), con el largo de cada tramo
    // y su rótulo (marca, ø, separación y largo total). o.max: largo máximo dibujado de un tramo (mm); los más largos van con quiebre
    function despiece(idf, o) {
      o = o || {}; const l = S.lineas.find(q => q.f.id === idf); if (!l) { console.error('lámina: sin barra en el plano para el despiece de', idf); return null; }
      const fila = PL.filaDe(l.f, l.pl), h = o.h || 2.3, esp = espDe(l.f), sw = ancho(l.f);
      const ku = cfg.eje === 'x' ? 1 : 0, nom = l.pl.length === 7 ? window.Armaduras.nominal(l.pl) : l.pl;   // estribos: con la esquina y los lados enteros, como en la planilla
      const ok = nom.map((p, i) => i === 0 || d3(p, nom[i - 1]) > 0.05), p3 = nom.filter((p, i) => ok[i]), q = p3.map(p => [X(S.U(p[ku])), Y(p[2] - D.z_piso)]);
      const real = p3.slice(1).map((p, i) => d3(p3[i], p)), r = [q[0].slice()], rotos = [];
      if (fila && fila.segs.join('|') !== real.map(medio).join('|')) console.error(`lámina: el despiece de ${idf} (${real.map(medio).join(' + ')}) no calza con la marca ${fila.marca} de la planilla (${fila.segs.join(' + ')})`);   // la lámina y la planilla tienen que decir lo mismo
      for (let i = 1; i < q.length; i++) { const a = q[i - 1], b = q[i], len = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1e-6, m = o.max && len > o.max ? o.max : len; if (m < len) rotos.push(i - 1); r.push([r[i - 1][0] + (b[0] - a[0]) / len * m, r[i - 1][1] + (b[1] - a[1]) / len * m]); }
      const an = o.ancla || 0, ox = q[an][0] - r[an][0] + (o.dx || 0), oy = q[an][1] - r[an][1] + (o.dy || 0); r.forEach(p => { p[0] += ox; p[1] += oy; });
      // la barra, con el quiebre en los tramos acortados
      let tramo = [r[0]]; const dib = () => { if (tramo.length > 1) P(g, tramo, 'lm-b').setAttribute('stroke-width', f2(sw)); };
      for (let i = 0; i + 1 < r.length; i++) {
        const a = r[i], b = r[i + 1];
        if (rotos.includes(i)) { const len = Math.hypot(b[0] - a[0], b[1] - a[1]), ux = (b[0] - a[0]) / len, uy = (b[1] - a[1]) / len, mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, e1 = [mx - ux * 0.9, my - uy * 0.9], e2 = [mx + ux * 0.9, my + uy * 0.9];
          tramo.push(e1); dib(); [e1, e2].forEach(e => L(g, e[0] + uy * 1.4 - ux * 0.5, e[1] - ux * 1.4 - uy * 0.5, e[0] - uy * 1.4 + ux * 0.5, e[1] + ux * 1.4 + uy * 0.5, 'lm-f')); tramo = [e2]; }
        tramo.push(b);
      }
      dib();
      // medidas de los tramos (por fuera) y rótulo (por dentro, o sobre la barra si es recta)
      const cx = r.reduce((s, p) => s + p[0], 0) / r.length, cy = r.reduce((s, p) => s + p[1], 0) / r.length, cerrada = r.length > 4 && Math.hypot(r[0][0] - r[r.length - 1][0], r[0][1] - r[r.length - 1][1]) < 6 * k + 1;
      const vistos = []; let iL = 0; real.forEach((v, i) => { if (v > real[iL]) iL = i; });
      const lado = (i, fuera) => { const a = r[i], b = r[i + 1], len = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1, ux = (b[0] - a[0]) / len, uy = (b[1] - a[1]) / len, mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
        let nx = -uy, ny = ux; const s = (mx - cx) * nx + (my - cy) * ny; if (Math.abs(s) < 0.3) { if (ny > 0 || (Math.abs(ny) < 1e-6 && nx > 0)) { nx = -nx; ny = -ny; } } else if (s < 0) { nx = -nx; ny = -ny; }   // (nx, ny): hacia afuera (recta: hacia arriba o a la izquierda)
        if (!fuera) { nx = -nx; ny = -ny; }
        let ang = Math.atan2(uy, ux) * 180 / Math.PI; if (ang >= 89.9) ang -= 180; if (ang < -90.1) ang += 180;
        const ar = ang * Math.PI / 180, upx = Math.sin(ar), upy = -Math.cos(ar), arriba = nx * upx + ny * upy > 0;   // ¿el texto queda sobre su línea base?
        return { mx, my, nx, ny, ang, arriba, ux, uy, len };
      };
      const pon = (i, t, fuera, hh, sep, alo) => { const q2 = lado(i, fuera), off = (sep == null ? 1.1 : sep) + sw / 2 + (q2.arriba ? 0 : hh), al = alo || 0, x = q2.mx + q2.nx * off + q2.ux * al, y = q2.my + q2.ny * off + q2.uy * al; T(g, x, y, t, hh, { a: 'm', rot: q2.ang }); return { x, y, q2 }; };
      // cada tramo con su largo (en los estribos, cada medida una sola vez); en un tramo con quiebre el número se corre para no pisarlo
      if (real.length > 1) real.forEach((v, i) => { const q2 = lado(i, true), key = Math.round((q2.ang + 180) % 180 / 15) + '|' + medio(v); if (cerrada && (i === 0 || i === real.length - 1)) return; if (cerrada && vistos.includes(key)) return; vistos.push(key); pon(i, cmt(fila && fila.ext && fila.ext.length === real.length ? fila.ext[i] : medio(v)), true, 2.1, 0.9, rotos.includes(i) ? q2.len * 0.25 : 0); });   // la medida que se lee va por fuera (planilla)
      const rot = o.texto != null ? o.texto : `${cerrada ? 'E ' : ''}${nomD(l.f.diam)}${esp ? '@' + esp : ''}, L=${coma(Math.round(fila ? fila.L : real.reduce((a, b) => a + b, 0)))}`;
      if (rot) {
        const w = anchoT(rot, h), qL = lado(iL, true), cabe = real.length === 1 || qL.len > w + 10;
        if (cerrada || !cabe || o.abajo) {   // estribos y formas chicas: el rótulo va bajo la forma (y bajo las medidas de sus tramos)
          const xs = r.map(p => p[0]), xc = (Math.min(...xs) + Math.max(...xs)) / 2 + 2.7 + (o.alo || 0), yb = Math.max(...r.map(p => p[1])) + (cerrada ? 2.4 : 5.6) + h;
          T(g, xc, yb, rot, h, { a: 'm' }); if (fila && o.marca !== false) marca(g, xc - w / 2 - 3.2, yb - h / 2, fila.marca, 2.1);
          if (cerrada) T(g, xc, yb + h + 1.6, `ganchos de 135° de ${cmt(medio(real[0]))}`, 2.0, { a: 'm' });
        } else {
          const dentroT = real.length > 1 && !o.rotFuera, al = o.alo != null ? o.alo : (rotos.includes(iL) ? -qL.len * 0.25 : 0), t = pon(iL, rot, !dentroT, h, 1.3, al), ar = t.q2.ang * Math.PI / 180;
          if (fila && o.marca !== false) marca(g, t.x - Math.cos(ar) * (w / 2 + 3.2) + Math.sin(ar) * h / 2, t.y - Math.sin(ar) * (w / 2 + 3.2) - Math.cos(ar) * h / 2, fila.marca, 2.1);   // la marca, antes del texto y a su altura
        }
      }
      return { r, fila };
    }
    const api = { S, g, gc, k, X, Y, W, za, zb, cerca, rotulos, despiece,
      cotaH: (u1, u2, z, t, dy, o) => cotaH(g, X(u1), X(u2), Y(z) + (dy || 0), t, Object.assign({ ref: dy ? [[X(u1), Y(z)], [X(u2), Y(z)]] : null }, o || {})),
      cotaV: (u, z1, z2, t, dx, o) => cotaV(g, X(u) + (dx || 0), Y(z1), Y(z2), t, Object.assign({ ref: dx ? [[X(u), Y(z1)], [X(u), Y(z2)]] : null }, o || {})),
      nivel: (u, z, t, o) => nivel(g, X(u), Y(z), t, o) };
    return api;
  }

  // ---------- lámina 01: planta de fundaciones (enfierradura) y cortes ----------
  function lamina01(cont, D, E, info) {
    const H = D.hormigon, sv = hoja(cont, info), N = H.niveles, PL = window.Armaduras.planilla(D), F = id => D.fierros.find(f => f.id === id);
    const V = plantaFundaciones(sv, D, H, E, 96, 66), g = V.g, ex = D.ejes.x, ey = D.ejes.y; V.ox = E.origen[0]; V.oy = E.origen[1];
    const AX = v => v + V.ox, AY = v => v + V.oy;
    // ejes: líneas de trazos y burbujas (números arriba y abajo, letras a la izquierda), como en la lámina del proyecto
    const yT = V.YL(-175), yB = V.YL(1745 + 225), xI = V.XL(-200), xD = V.XL(1075 + 150);
    Object.entries(ex).forEach(([n, x]) => { L(g, V.XL(x), yT + 4.8, V.XL(x), yB - 4.8, 'lm-e'); burbuja(g, V.XL(x), yT, n); burbuja(g, V.XL(x), yB, n); });
    Object.entries(ey).forEach(([n, y]) => { L(g, xI + 4.8, V.YL(y), xD, V.YL(y), 'lm-e'); burbuja(g, xI, V.YL(y), n); });
    // cotas entre ejes: arriba y abajo los números; a la derecha las letras
    const xs = Object.values(ex), ys = Object.values(ey), yc1 = V.YL(-118), yc2 = V.YL(1745 + 120), yc3 = V.YL(1745 + 160);
    for (let i = 0; i + 1 < xs.length; i++) { cotaH(g, V.XL(xs[i]), V.XL(xs[i + 1]), yc1, cmt(xs[i + 1] - xs[i])); cotaH(g, V.XL(xs[i]), V.XL(xs[i + 1]), yc2, cmt(xs[i + 1] - xs[i])); }
    cotaH(g, V.XL(xs[0]), V.XL(xs[xs.length - 1]), yc3, cmt(xs[xs.length - 1] - xs[0]), { tx: V.XL((xs[1] + xs[2]) / 2) });
    const xc1 = V.XL(1075 + 80), xc2 = V.XL(1075 + 125);
    for (let i = 0; i + 1 < ys.length; i++) cotaV(g, xc1, V.YL(ys[i]), V.YL(ys[i + 1]), cmt(ys[i + 1] - ys[i]));
    cotaV(g, xc2, V.YL(ys[0]), V.YL(ys[ys.length - 1]), cmt(ys[ys.length - 1] - ys[0]), { ty: V.YL((ys[2] + ys[3]) / 2) });
    // ---- insertos: rótulo de cada placa (nombre sobre la raya, medidas en mm debajo), hacia donde hay lugar ----
    H.placas.lista.forEach(q => {
      const cx = q.centro[0] - V.ox, cy = q.centro[1] - V.oy, x = V.XL(cx), y = V.YL(cy), b = caja(q.pts);
      const enA = Math.abs(cy - ey.A) < 20, enE = Math.abs(cy - ey.E) < 20, en5 = Math.abs(cx - ex['5']) < 20, en4 = Math.abs(cx - ex['4']) < 20 && !enA && !enE && Math.abs(cy - ey.B) > 20;
      const enB = Math.abs(cy - ey.B) < 20, en1 = Math.abs(cx - ex['1']) < 20, izq = (en5 && !enA && !enE) || en4, dy = enA ? -7.6 : enE ? 11.6 : en4 ? 9 : enB ? (en5 ? 15.2 : 7.0) : 6.2;   // las esquinas del eje 5 rotulan hacia afuera; 5B, en segunda fila
      const dx = (izq ? -1 : 1) * ((en1 || en5) && !enA && !enE ? 9.2 : 4.6);   // en los ejes 1 y 5 el texto parte pasado el borde del cimiento
      const t1 = q.id, t2 = `PL ${coma(q.largo * 10)}x${coma(q.ancho * 10)}x${coma(q.espesor * 10)}`, h = 1.8, w = Math.max(anchoT(t1, h), anchoT(t2, h)) + 1;
      const xa = x + dx, ya = y + dy, xb = izq ? xa - w : xa + w;
      L(g, x, y, xa, ya); L(g, xa, ya, xb, ya); T(g, izq ? xb + 0.4 : xa + 0.6, ya - 0.8, t1, h); T(g, izq ? xb + 0.4 : xa + 0.6, ya + h + 0.9, t2, h);
    });
    // ---- enfierradura de la losa de fundación del búnker (las 4 mallas), como la «Planta losa» del proyecto ----
    barraPlanta(g, V, PL, F('LF-inf-NS'), { en: 417, rep: 150, t: 0.72, texto: 'inf.' });
    barraPlanta(g, V, PL, F('LF-sup-NS'), { en: 507, rep: 150, t: 0.72, texto: 'sup.', sinLinea: true });
    barraPlanta(g, V, PL, F('LF-inf-EO'), { en: 290, rep: 740, t: 0.80, texto: 'inf.' });
    barraPlanta(g, V, PL, F('LF-sup-EO'), { en: 350, rep: 740, t: 0.80, texto: 'sup.', sinLinea: true });
    // ---- rótulos de los elementos ----
    const h2 = 2.1;
    TA(g, V.XL(885), V.YL(470), 'LOSA DE FUNDACION e=35', 3.4, { a: 'm' }); T(g, V.XL(885), V.YL(470) + 3.6, `cara superior ${N.zapata_sup} · sello ${N.emplantillado_inf}`.replace(/-/g, '−'), 1.9, { a: 'm' }); T(g, V.XL(885), V.YL(470) + 6.9, 'hormigón G30 con cristalizante', 1.9, { a: 'm' });
    llamada(g, V.XL(585), V.YL(21), V.XL(615), V.YL(88), ['MUROS H.A. e=30 (los cuatro)', 'ver corte a-a'], { h: 1.9 });
    T(g, V.XL(66), V.YL(1245), 'SOBRECIMIENTO 30x50', h2, { a: 'm', rot: -90 }); T(g, V.XL(84), V.YL(1245), 'CIMIENTO CORRIDO 80x25 (corte b-b)', h2, { a: 'm', rot: -90 });
    T(g, V.XL(1016), V.YL(1245), 'SOBRECIMIENTO 30x50', h2, { a: 'm', rot: -90 }); T(g, V.XL(998), V.YL(1245), 'CIMIENTO CORRIDO 80x25 (corte b-b)', h2, { a: 'm', rot: -90 });
    T(g, V.XL(400), V.YL(1672), 'SOBRECIMIENTO 30x50 · CIMIENTO CORRIDO 80x25 (corte b-b)', h2, { a: 'm' });
    T(g, V.XL(ex['4']) - 4.2, V.YL(850), 'CF 30/50 (corte c-c)', h2, { a: 'm', rot: -90 }); T(g, V.XL(ex['4']) - 4.2, V.YL(1245), 'CF 30/50', h2, { a: 'm', rot: -90 }); T(g, V.XL(985), V.YL(ey.C) - 4.4, 'CF 30/50', h2, { a: 'm' }); T(g, V.XL(985), V.YL(ey.C2) - 4.4, 'CF 30/50', h2, { a: 'm' });
    llamada(g, V.XL(ex['4'] - 62), V.YL(ey.C2 - 50), V.XL(ex['4'] - 95), V.YL(ey.C2 - 96), ['DADO 140x140x120', '(corte d-d)'], { lado: 'i', h: h2, punta: true });
    // unión del búnker con las fundaciones del estudio: sin junta, con las esperas que entran 60 al búnker (el ingeniero, 24-11-2026), tal como están en el modelo
    D.fierros.filter(f => /^UB-/.test(f.id)).forEach(f => f.polilineas.forEach(pl => P(g, pl.map(q => [V.XL(q[0] - V.ox), V.YL(q[1] - V.oy)]), 'lm-b').setAttribute('stroke-width', '0.3')));
    llamada(g, V.XL(ex['1'] + 9), V.YL(ey.B + 48), V.XL(150), V.YL(ey.B + 122), ['SIN JUNTA: ESPERAS QUE ENTRAN', '60 AL BUNKER (NOTA 8 Y DETALLE)'], { h: 1.9 });
    TA(g, V.XL(400), V.YL(1120), 'RADIER e=10', 3.4, { a: 'm' }); T(g, V.XL(400), V.YL(1120) + 3.6, 'malla C139 · poliestireno 10 · relleno granular 15', 1.9, { a: 'm' });
    // ---- cotas del búnker y de las fundaciones ----
    const e = H.muros.espesor, m = H.losa_fundacion.margen, bx0 = V.ext[0] - V.ox, bx1 = V.ext[2] - V.ox, by0 = V.ext[1] - V.oy, by1 = V.ext[3] - V.oy;
    const ycb = V.YL(200); cotaH(g, V.XL(bx0 + e), V.XL(bx1 - e), ycb, cmt(bx1 - bx0 - 2 * e), { tx: V.XL(690) });
    const xcb = V.XL(170); cotaV(g, xcb, V.YL(by0 + e), V.YL(by1 - e), cmt(by1 - by0 - 2 * e), { ty: V.YL(480) });
    cotaH(g, V.XL(bx0 - m), V.XL(bx0), V.YL(96), cmt(m), { fuera: 'izq' });
    // medidas totales de la losa de fundación (trazado y emplantillado)
    const lx0 = V.LF[0] - V.ox, lx1 = V.LF[2] - V.ox, ly0 = V.LF[1] - V.oy, ly1 = V.LF[3] - V.oy;
    cotaH(g, V.XL(lx0), V.XL(lx1), V.YL(-62), cmt(lx1 - lx0) + ' losa de fundación', { tx: V.XL(650), ref: [[V.XL(lx0), V.YL(ly0)], [V.XL(lx1), V.YL(ly0)]] });
    cotaV(g, V.XL(-138), V.YL(ly0), V.YL(ly1), cmt(ly1 - ly0) + ' losa de fundación', { ty: V.YL(420), ref: [[V.XL(lx0), V.YL(ly0)], [V.XL(lx0), V.YL(ly1)]] });
    // ---- marcas de corte ----
    marcaCorte(g, V.XL(230), V.YL(-66), V.XL(230), V.YL(120), 1, 0, 'a');
    marcaCorte(g, V.XL(-78), V.YL(ey.D + 1), V.XL(118), V.YL(ey.D + 1), 0, -1, 'b');
    marcaCorte(g, V.XL(880), V.YL(ey.C2 - 52), V.XL(880), V.YL(ey.C2 + 52), 1, 0, 'c');
    marcaCorte(g, V.XL(ex['4'] - 100), V.YL(ey.C - 23.5), V.XL(ex['4'] + 100), V.YL(ey.C - 23.5), 0, -1, 'd');
    titulo(sv, 120, 480, 'PLANTA FUNDACIONES', 50);
    T(sv, 222, 480, 'ENFIERRADURA DE LA LOSA DE FUNDACION DEL BUNKER; EL RESTO, EN LOS CORTES', 2.1);
    // ================= Corte a-a: muro, losa de techo y losa de fundación del búnker (1:20) =================
    {
      const u0 = -56, Ca = corte(sv, D, PL, { eje: 'x', c: AX(230), u0: AY(u0), u1: AY(180), zmin: -397, zmax: 10, ntn: [0, 50.5] }, 452, 80, 20), U = y => y - u0, g2 = Ca.g;   // U: y local → u del corte
      const e = H.muros.espesor, m = H.losa_fundacion.margen, y0m = V.ext[1] - V.oy, zLi = N.losa_inf, zFs = N.zapata_sup, zFi = N.zapata_inf, zSe = N.emplantillado_inf;   // muro del eje A: de y0m a y0m + e
      // barras de las losas, a la derecha; barras del muro, a la izquierda (por fuera, como en la lámina del proyecto)
      Ca.rotulos([['LT-NS', null, -2.6, U(165)], ['LS-AB', null, null, U(150)], ['LN', null, -22.5, U(165)], ['LE', null, null, U(150)]], Ca.X(Ca.W) + 7, { gap: 6.4 });
      Ca.rotulos([['LF-sup-NS', null, null, U(165)], ['LF-sup-EO', null, null, U(150)], ['LF-inf-EO', null, null, U(150)], ['LF-inf-NS', null, -375, U(165)]], Ca.X(Ca.W) + 7, { gap: 6.4 });
      Ca.rotulos([['MC-N-ext', '2ø12 (1 por cara), en los dobleces', null, null], ['MV-N-ext', null, -128, null], ['MH-N-ext', null, -158, null], ['MV-N-int', null, -205, null], ['MH-N-int', null, -233, null], ['MT-N', 'Trabas ø8', -262, null]], Ca.X(0) - 3, { izq: true, gap: 6.4 });
      Ca.rotulos([['LF-borde', 'ø10 de borde', null, null]], Ca.X(0) - 3, { izq: true });
      // pie de la malla superior sobre su separador (el ingeniero, 22-11-2026)
      const fS = F('LF-sup-NS'), zPie = Math.min(...fS.polilineas[0].map(q => q[2])) - D.z_piso, yPie = fS.polilineas[0][0][1] - V.oy;
      llamada(g2, Ca.X(U(yPie)) - 0.4, Ca.Y(zPie) + 0.6, Ca.X(0) - 3, Ca.Y(zPie) + 5.6, ['Pie sobre separador de 5 cm', '(conduit de PVC de 50 mm)'], { lado: 'i', h: 2.1 });
      // despiece: verticales del muro a la izquierda, en el orden del corte (la exterior, a la izquierda), barras de la losa de techo arriba y de la losa de fundación abajo
      Ca.despiece('MV-N-ext', { dx: -124, max: 150 }); Ca.despiece('MV-N-int', { dx: -84, max: 150 });
      Ca.despiece('LT-NS', { dx: -3, dy: -52 }); Ca.despiece('LN', { dy: -22, max: 84, dx: 22 });
      Ca.despiece('LF-sup-NS', { dy: 34, max: 96, dx: 4 }); Ca.despiece('LF-inf-NS', { dy: 55, max: 96, dx: 4 });
      // detalle de la traba (sin escala): 5 – 20 – 5, medida por fuera, con su marca de la planilla
      { const fT = F('MT-N'), fl = PL.filaDe(fT, fT.polilineas[0]), xa = Ca.X(0) - 31, ya = Ca.Y(-262) + 21, e = fl ? fl.ext : [5, 20, 5];
        T(g2, xa - 2, ya - 6.2, 'DETALLE TRABA (SIN ESCALA)', 2.1);
        P(g2, [[xa, ya + 5], [xa, ya], [xa + 20, ya], [xa + 20, ya + 5]], 'lm-b').setAttribute('stroke-width', '0.5');
        T(g2, xa + 10, ya - 1.0, cmt(e[1]), 2.1, { a: 'm' }); T(g2, xa - 1.1, ya + 3.6, cmt(e[0]), 2.1, { a: 'e' }); T(g2, xa + 21.1, ya + 3.6, cmt(e[2]), 2.1);
        if (fl) marca(g2, xa + 1.2, ya + 10.6, fl.marca); T(g2, xa + 4.6, ya + 11.4, `${nomD(fT.diam)}, L=${coma(Math.round(fl ? fl.L : 30))}`, 2.3);
        T(g2, xa - 2, ya + 16.2, 'cada 3 nudos en los dos sentidos', 1.9); T(g2, xa - 2, ya + 19.6, 'ganchos a lo largo del muro', 1.9); }
      // niveles
      Ca.nivel(U(y0m) - 8, 0, 'NPOG 0,00', { alto: 6.5, lado: 'i' }); nivel(g2, Ca.X(9), Ca.Y(-50), 'N.T.N −50', { alto: 4.2, lado: 'i' });
      Ca.nivel(U(100), zFs, cmt(zFs).replace('-', '−'), { alto: 6.5, lado: 'i' });
      // cotas: espesores y altura libre (por dentro), vuelo y muro (abajo)
      Ca.cotaV(U(125), zLi, 0, cmt(-zLi), 0); Ca.cotaV(U(125), zFs, zLi, cmt(zLi - zFs) + ' libres (obra gruesa)', 0);
      Ca.cotaV(U(y0m - m), zFi, zFs, cmt(zFs - zFi), -6); Ca.cotaV(U(y0m - m), zSe, zFi, cmt(zFi - zSe), -6, { abajo: true });
      Ca.cotaH(U(y0m - m), U(y0m), zSe, cmt(m), 6); Ca.cotaH(U(y0m), U(y0m + e), zSe, cmt(e), 6);
      // materiales
      llamada(g2, Ca.X(U(172)), Ca.Y(0), Ca.X(Ca.W) + 7, Ca.Y(0) - 5.2, ['Losa H.A. e=' + cmt(H.losa.espesor)], { h: 2.5 });
      llamada(g2, Ca.X(U(y0m + e / 2)), Ca.Y(-285), Ca.X(U(y0m + e)) + 9, Ca.Y(-285) - 5, ['Muro H.A. e=' + cmt(e)], { h: 2.5 });
      llamada(g2, Ca.X(U(172)), Ca.Y(zFs), Ca.X(Ca.W) + 7, Ca.Y(zFs) - 5.2, ['Losa de fundación e=' + cmt(zFs - zFi)], { h: 2.5 });
      llamada(g2, Ca.X(U(135)), Ca.Y((zFi + zSe) / 2), Ca.X(Ca.W) + 7, Ca.Y(zSe) + 8.5, ['Emplantillado G5 e=' + cmt(zFi - zSe)], { h: 2.5 });
      llamada(g2, Ca.X(U(y0m - m) + 6), Ca.Y(zSe), Ca.X(0) - 3, Ca.Y(zSe) + 10, ['Sello ' + cmt(zSe).replace('-', '−') + ': 20 cm en el estrato', 'indicado en la memoria de cálculo'], { lado: 'i', h: 2.1 });
      titulo(sv, 470, 339, 'Corte a-a', 20); T(sv, 513, 339, 'MURO DEL EJE A, ENTRE LOS EJES 1 Y 2', 2.1); T(sv, 513, 343.4, '(LOS CUATRO MUROS IGUALES)', 2.1);
    }
    // ================= Corte b-b: sobrecimiento, cimiento corrido e inserto (fachadas), por el pilar 1-D (1:20) =================
    {
      const x0 = -75, Cb = corte(sv, D, PL, { eje: 'y', c: AY(ey.D) + 1, u0: AX(x0), u1: AX(100), zmin: -146, zmax: 40, ntn: [0, 72.5], ntnRotulo: 'N.T.N −50' }, 668, 42, 20), U = x => x - x0, g2 = Cb.g, xe = ex['1'];
      const hs = H.cimiento.sobrecimiento.ancho / 2, hc = H.cimiento.zapata.ancho / 2, zc = N.cimiento_inf, zs = N.sobrecimiento_inf, zse = N.sello_fachadas, cap = H.radier_estudio.capas, zrel = cap[cap.length - 1].z_inf - D.z_piso;
      // sub base bajo el relleno (la lámina 01 la dibuja; el modelo no la lleva como pieza)
      trama(Cb.gc, Cb.X(U(xe + hs)), Cb.Y(zrel), Cb.X(Cb.W) - Cb.X(U(xe + hs)), (zrel - zs) * Cb.k, 'sub');
      // pilar e inserto (acero: no salen del corte del hormigón)
      const PD = H.placas.lista.find(q => q.id === 'PLc-1D'), tD = PD.espesor;
      R(g2, Cb.X(U(xe)) - 7.5 * Cb.k, Cb.Y(40), 15 * Cb.k, 40 * Cb.k, 'lm-o'); quiebre(g2, Cb.X(U(xe)) - 7.5 * Cb.k, Cb.Y(40), Cb.X(U(xe)) + 7.5 * Cb.k, Cb.Y(40));
      R(g2, Cb.X(U(xe)) - PD.ancho / 2 * Cb.k, Cb.Y(0), PD.ancho * Cb.k, tD * Cb.k, 'lm-n');
      const xl = Cb.X(0) - 3;
      llamada(g2, Cb.X(U(xe)) - 5 * Cb.k, Cb.Y(27), xl, Cb.Y(31), [`Pilar ${PD.perfil.replace('RECT ', '').replace('CUAD ', '')}`], { lado: 'i', h: 2.3, punta: true });
      llamada(g2, Cb.X(U(xe)) - PD.ancho / 2 * Cb.k + 0.6, Cb.Y(-tD / 2), xl, Cb.Y(15), [`Inserto ${PD.id} a ras`, `PL ${coma(PD.largo * 10)}x${coma(PD.ancho * 10)}x${coma(tD * 10)}, barras soldadas`], { lado: 'i', h: 2.3 });
      Cb.rotulos([['S16-1', null, null, null], ['S8-1', null, -15, null], ['SU-1', 'E ' + nomD(F('SU-1').diam) + '@' + espDe(F('SU-1')), -26, null], ['AP', `4ø22 A36 (hef ${cmt(PD.hef)}), gancho 10`, -38, null]], xl, { izq: true, gap: 5.6 });
      if (Cb.cerca('AX', 0, -58)) Cb.rotulos([['AX', 'E ø10 extra bajo el pilar', -58, null]], xl, { izq: true });
      Cb.rotulos([['CL-1', null, null, null], ['CU-1', null, -69.4, U(xe + 30)]], Cb.X(Cb.W) + 6, { gap: 6.2 });
      // capas del radier y materiales (a la derecha, como en la lámina del proyecto)
      const xr = Cb.X(Cb.W) + 6, um = U(xe + hs + 26);
      llamada(g2, Cb.X(um), Cb.Y(-5), xr, Cb.Y(8), ['Radier e=10 Cm.'], { h: 2.3 });
      llamada(g2, Cb.X(um + 8), Cb.Y(-15), xr, Cb.Y(-4), ['Poliestireno expandido', 'alta densidad e=100'], { h: 2.3 });
      llamada(g2, Cb.X(um + 16), Cb.Y(-27), xr, Cb.Y(-24), ['Relleno granular e=15', 'T.Max. 1 1/2", 90% proctor modif.'], { h: 2.3 });
      llamada(g2, Cb.X(um + 24), Cb.Y(-43), xr, Cb.Y(-44), ['Sub base granular compactada'], { h: 2.3 });
      llamada(g2, Cb.X(U(xe + 22)), Cb.Y(zc - 5), xr, Cb.Y(zc - 19), ['Emplantillado G5 e=10'], { h: 2.3 });
      llamada(g2, Cb.X(U(xe + 16)), Cb.Y(zc - 40), xr, Cb.Y(zc - 36), ['Hormigón pobre G5', `hasta el sello (${cmt(zse).replace('-', '−')})`], { h: 2.3 });
      Cb.nivel(U(xe + hs + 9), 0, 'NPOG 0,00', { alto: 6 });
      Cb.cotaV(U(xe - hc), zs, 0, cmt(-zs), -6); Cb.cotaV(U(xe - hc), zc, zs, cmt(zs - zc), -6); Cb.cotaV(U(xe - hc), zc - 10, zc, '10', -6, { lado: 'izq' }); Cb.cotaV(U(xe - hc), zse, zc - 10, cmt(zc - 10 - zse), -6);
      Cb.cotaH(U(xe - hc), U(xe - hs), zse, cmt(hc - hs), 5); Cb.cotaH(U(xe - hs), U(xe + hs), zse, cmt(2 * hs), 5); Cb.cotaH(U(xe + hs), U(xe + hc), zse, cmt(hc - hs), 5); Cb.cotaH(U(xe - hc), U(xe + hc), zse, cmt(2 * hc), 11);
      Cb.despiece('SU-1', { dx: -24, dy: 88 }); Cb.despiece('CU-1', { dx: 32, dy: 92 });
      // detalle de la barra del inserto (sin escala): fuste soldado bajo la placa, gancho de 10 y cabeza soldada bajo el gancho (el ingeniero, 22 y 23-11-2026)
      { const fA = F('AP'), cxp = PD.centro[0], cyp = PD.centro[1], bp = fA.polilineas.find(q => q.length === 3 && Math.hypot(q[0][0] - cxp, q[0][1] - cyp) < 15), fl = bp ? PL.filaDe(fA, bp) : null;
        const x0d = 778, y0d = 118, hb = 30, cab = PD.cabeza || [6, 4.5];
        T(g2, x0d - 6, y0d - 8.6, 'DETALLE BARRA DEL INSERTO', 2.1); T(g2, x0d - 6, y0d - 5.2, '(SIN ESCALA)', 1.9);
        R(g2, x0d - 6, y0d - 1.6, 16, 1.6, 'lm-n');                                                       // placa
        P(g2, [[x0d, y0d], [x0d, y0d + hb], [x0d + 9, y0d + hb]], 'lm-b').setAttribute('stroke-width', '0.9');   // fuste y gancho
        R(g2, x0d + 0.9, y0d + hb + 0.6, 7, 1.3, 'lm-n');                                                 // cabeza
        if (fl) { T(g2, x0d - 1.3, y0d + hb / 2, cmt(fl.ext[0]), 2.1, { a: 'm', rot: -90 }); T(g2, x0d + 4.8, y0d + hb - 1.3, cmt(fl.ext[1]), 2.1, { a: 'm' }); marca(g2, x0d + 5.2, y0d + 9.4, fl.marca); }
        T(g2, x0d + 8.6, y0d + 10.2, `${nomD(fA.diam)} lisa A36, L=${coma(Math.round(fl ? fl.L : 0))}`, 2.1); T(g2, x0d + 3.2, y0d + 14.4, 'soldada bajo la placa', 1.9);
        T(g2, x0d + 3.2, y0d + hb + 6.4, `cabeza ${coma(cab[0] * 10)}x${coma(cab[1] * 10)}x12 soldada`, 1.9); T(g2, x0d + 3.2, y0d + hb + 9.8, 'bajo el gancho', 1.9); }
      titulo(sv, 664, 186, 'Corte b-b', 20); T(sv, 707, 186, 'EJE 1 POR EL PILAR D (EJES 5 Y E IGUALES)', 2.1);
    }
    // ================= Corte c-c: cadena de fundación CF 30/50 (1:20) =================
    {
      const yC = ey.C2, zse = N.sello_cf, G5 = H.cf.emplantillado, RE = H.cf.relleno, zg5 = N.cf_inf - G5.espesor;   // bajo la cadena: 20 de G5 sobre 30 de estabilizado compactado, sello −100 (el ingeniero, 22 y 23-11-2026)
      const Cc = corte(sv, D, PL, { eje: 'x', c: AX(880), u0: AY(yC) - 45, u1: AY(yC) + 45, zmin: zse - 6, zmax: 12 }, 704, 222, 20), U = y => y - (yC - 45), g2 = Cc.g, a2 = H.cf.ancho / 2;
      Cc.rotulos([['CF-C2-sup', null, null, null], ['CF-C2-est', 'E ' + nomD(F('CF-C2-est').diam) + '@' + espDe(F('CF-C2-est')), -14, null], ['CF-C2-traba', 'Traba ' + nomD(F('CF-C2-traba').diam) + '@' + espDe(F('CF-C2-traba')) + ', en toda la cadena', null, null], ['CF-C2-med', null, null, null], ['CF-C2-inf', null, null, null]], Cc.X(Cc.W) + 6, { gap: 6.4 });
      llamada(g2, Cc.X(U(yC + 8)), Cc.Y((N.cf_inf + zg5) / 2), Cc.X(Cc.W) + 6, Cc.Y(-72), [`Hormigón G5 ${cmt(G5.ancho)}x${cmt(G5.espesor)}`], { h: 2.3 });
      llamada(g2, Cc.X(U(yC + 5)), Cc.Y((zg5 + zse) / 2), Cc.X(Cc.W) + 6, Cc.Y(-82.6), [`Estabilizado compactado ${cmt(RE.ancho)}x${cmt(RE.espesor)}`, '2 capas de 15, Tmáx 2"'], { h: 2.3 });
      llamada(g2, Cc.X(U(yC + 18)), Cc.Y(zse), Cc.X(Cc.W) + 6, Cc.Y(zse) - 1, [`Sello ${cmt(zse).replace('-', '−')}, compactado`], { h: 2.3 });
      llamada(g2, Cc.X(U(yC + 32)), Cc.Y(-5), Cc.X(Cc.W) + 6, Cc.Y(13), ['Radier e=10 y capas: ver corte b-b'], { h: 2.3 });
      Cc.nivel(U(yC - 30), 0, 'NPOG 0,00', { alto: 6.5, lado: 'i' });
      const dxc = -(45 - a2) * Cc.k - 4; Cc.cotaV(U(yC - a2), N.cf_inf, 0, cmt(-N.cf_inf), dxc); Cc.cotaV(U(yC - a2), zg5, N.cf_inf, cmt(N.cf_inf - zg5), dxc); Cc.cotaV(U(yC - a2), zse, zg5, cmt(zg5 - zse), dxc);
      Cc.cotaH(U(yC - G5.ancho / 2), U(yC + G5.ancho / 2), zse, cmt(G5.ancho), 5);
      Cc.despiece('CF-C2-est', { dx: -62, dy: 22 }); Cc.despiece('CF-C2-traba', { dx: -62, dy: 50 });
      titulo(sv, 664, 310, 'Corte c-c', 20); T(sv, 707, 310, `CADENA DE FUNDACION CF ${cmt(H.cf.ancho)}/${cmt(H.cf.alto)} (EJES 4, C Y C2)`, 2.1);
    }
    // ================= Corte d-d: dado bajo los pilares 4C y 4C2, con el CF-4 encima (1:20) =================
    {
      const x4 = ex['4'], Cd = corte(sv, D, PL, { eje: 'y', c: AY(ey.C - 23.5), u0: AX(x4 - 110), u1: AX(x4 + 110), zmin: -146, zmax: 12, tol: { AU: 14, 'AU-est': 36 } }, 374, 372, 20), U = x => x - (x4 - 110), g2 = Cd.g, hd = H.dados.lado / 2, zds = N.dado_sup, zdi = N.dado_inf, zse = N.sello_fachadas;
      Cd.rotulos([['CF-4-sup', null, null, null], ['CF-4-est', 'E ' + nomD(F('CF-4-est').diam) + '@' + espDe(F('CF-4-est')) + ' de 24x50 sobre el dado', -14, null], ['CF-4-traba', 'Traba ø10@20', null, null], ['CF-4-med', null, null, null], ['CF-4-inf', null, null, null],
        ['AU', 'Canastillo: 4ø16 verticales', -68, null], ['AU-est', 'E ø8@20 de 24x24', -78, null], ['DA-4C-inf', 'malla ø12@15 en los dos sentidos', -124.2, U(x4 + 40)]], Cd.X(Cd.W) + 6, { gap: 6.4 });
      llamada(g2, Cd.X(U(x4 - 40)), Cd.Y((zdi + zse) / 2), Cd.X(0) - 3, Cd.Y(zse) + 9, ['Hormigón pobre G5', `hasta el sello (${cmt(zse).replace('-', '−')})`], { lado: 'i', h: 2.3 });
      llamada(g2, Cd.X(U(x4 - 85)), Cd.Y(-5), Cd.X(0) - 3, Cd.Y(8), ['Radier e=10 y capas:', 'ver corte b-b'], { lado: 'i', h: 2.3 });
      llamada(g2, Cd.X(U(x4 + 12)), Cd.Y(0), Cd.X(Cd.W) + 6, Cd.Y(0) - 7.5, [`CF ${cmt(H.cf.ancho)}/${cmt(H.cf.alto)} (corte c-c)`], { h: 2.3 });
      Cd.nivel(U(x4 - 66), 0, 'NPOG 0,00', { alto: 12.5, lado: 'i' });
      Cd.cotaV(U(x4 - hd), zdi, zds, cmt(zds - zdi), -7); Cd.cotaV(U(x4 - hd), zse, zdi, cmt(zdi - zse), -7, { abajo: true }); Cd.cotaV(U(x4 - hd), zds, 0, cmt(-zds), -7);
      Cd.cotaH(U(x4 - hd), U(x4 + hd), zse, cmt(2 * hd), 5);
      Cd.despiece('DA-4C-inf', { dy: 27 }); Cd.despiece('AU', { dx: 172 });
      // a la izquierda: estribo de la cadena sobre el dado (24 × 50) y su traba; a la derecha, bajo el despiece de las verticales, el estribo del canastillo (24 × 24, en planta)
      { const fE = F('CF-4-est'), lE = Cd.S.lineas.find(q => q.f.id === 'CF-4-est'), flE = lE ? PL.filaDe(fE, lE.pl) : null, dxE = -82, xE = Cd.X(U(x4) - 11.5) + dxE, yE = Cd.Y(-53);
        Cd.despiece('CF-4-est', { dx: dxE, texto: '' });
        if (flE) marca(g2, xE - 5.4, yE + 7.6, flE.marca); T(g2, xE - 2.2, yE + 8.4, `E ${nomD(fE.diam)}@${espDe(fE)}, L=${coma(Math.round(flE ? flE.L : 0))}`, 2.3); T(g2, xE - 2.2, yE + 12.0, 'ganchos de 135° de 10', 1.9);
        Cd.despiece('CF-4-traba', { dx: dxE, dy: 40 }); }
      { const fE = F('AU-est'), fl = PL.filaDe(fE, fE.polilineas[0]), lq = 12, xq = 584, yq = 441;
        R(g2, xq, yq, lq, lq, 'lm-b').setAttribute('stroke-width', '0.45'); P(g2, [[xq + 0.9, yq + 2.6], [xq + 2.6, yq + 0.9]], 'lm-b').setAttribute('stroke-width', '0.45');
        if (fl) { T(g2, xq + lq / 2, yq - 0.9, cmt(fl.ext[1]), 2.1, { a: 'm' }); T(g2, xq - 1.0, yq + lq / 2, cmt(fl.ext[2]), 2.1, { a: 'm', rot: -90 }); marca(g2, xq - 3.4, yq + lq + 4.2, fl.marca); }
        T(g2, xq - 0.2, yq + lq + 5.0, `E ${nomD(fE.diam)}@20, L=${coma(Math.round(fl ? fl.L : 0))}`, 2.3); T(g2, xq - 5.8, yq + lq + 8.6, 'canastillo, en planta', 1.9); }
      titulo(sv, 374, 492, 'Corte d-d', 20); T(sv, 417, 492, 'DADO 140x140 BAJO LOS PILARES 4C Y 4C2 (SIN ESTRIBOS PERIMETRALES; CANASTILLO BAJO EL INSERTO)', 2.1);
    }
    // ================= Detalle de la unión búnker – fundaciones del estudio (sin escala): esperas que entran 60 al búnker (el ingeniero, 24-11-2026) =================
    {
      const UN = H.union_bunker, UBs = D.fierros.filter(f => /^UB-/.test(f.id));
      if (UN && UBs.length) {
        const g2 = el('g', { class: 'lm-union' }, sv), k = 0.36, xu = 373, y0 = 27, PX = c => xu + c * k, PY = z => y0 - z * k, pen = UN.penetra;
        const filas = []; UBs.forEach(f => f.polilineas.forEach(pl => { const fl = PL.filaDe(f, pl); if (fl) filas.push({ f, pl, fl }); }));
        const conPata = filas.find(q => q.pl.length === 3), pata = conPata ? conPata.fl.ext[0] : 0, dIn = pen - pata, zA = -6, zB = -37, lap = 72;
        const porD = {}; filas.forEach(q => { (porD[q.f.diam] = porD[q.f.diam] || new Set()).add(Math.round(q.fl.L)); });
        const porL = {}; Object.keys(porD).map(Number).sort((a, b) => a - b).forEach(d => [...porD[d]].forEach(l => (porL[l] = porL[l] || []).push(nomD(d))));
        const largos = Object.keys(porL).map(Number).sort((a, b) => a - b).map(l => `${porL[l].join(' y ')}, ${coma(l)}`);
        // hormigón: losa y muro del búnker a la izquierda de la línea de unión; sobrecimiento o cadena a la derecha
        P(g2, [[PX(-78), PY(0)], [PX(0), PY(0)]], 'lm-g'); P(g2, [[PX(-78), PY(-25)], [PX(-30), PY(-25)], [PX(-30), PY(-86)]], 'lm-g'); P(g2, [[PX(0), PY(-50)], [PX(0), PY(-86)]], 'lm-g');
        P(g2, [[PX(0), PY(0)], [PX(88), PY(0)]], 'lm-g'); P(g2, [[PX(0), PY(-50)], [PX(88), PY(-50)]], 'lm-g'); L(g2, PX(0), PY(0), PX(0), PY(-50), 'lm-o');
        quiebre(g2, PX(-78), PY(0), PX(-78), PY(-25)); quiebre(g2, PX(-30), PY(-86), PX(0), PY(-86)); quiebre(g2, PX(88), PY(0), PX(88), PY(-50));
        // las barras del estudio (finas) y sus esperas (gruesas): recta arriba, con pata abajo
        [zA - 2.6, zB - 2.6].forEach(z => P(g2, [[PX(4), PY(z)], [PX(88), PY(z)]], 'lm-b').setAttribute('stroke-width', '0.3'));
        P(g2, [[PX(-pen), PY(zA)], [PX(lap), PY(zA)]], 'lm-b').setAttribute('stroke-width', '0.7');
        P(g2, [[PX(-dIn), PY(zB - pata)], [PX(-dIn), PY(zB)], [PX(lap), PY(zB)]], 'lm-b').setAttribute('stroke-width', '0.7');
        cotaH(g2, PX(-pen), PX(0), PY(0) - 3.2, cmt(pen), { h: 2.1 }); cotaH(g2, PX(0), PX(lap), PY(0) - 3.2, 'traslapo', { h: 1.9 });
        cotaH(g2, PX(-dIn), PX(0), PY(zB) + 3.6, cmt(dIn), { h: 2.1, dentro: true }); cotaV(g2, PX(-dIn) - 3.4, PY(zB), PY(zB - pata), cmt(pata), { h: 2.1 });
        T(g2, PX(-64), PY(-18), 'LOSA', 1.7); T(g2, PX(-24), PY(-83), 'MURO', 1.7); T(g2, PX(22), PY(-24), 'SOBRECIMIENTO', 1.7); T(g2, PX(22), PY(-24) + 3.0, 'O CADENA', 1.7);
        llamada(g2, PX(0), PY(-46), PX(14), PY(-62), ['línea de unión', '(sin junta)'], { h: 1.7 });
        T(g2, PX(-78), y0 - 9.6, 'DETALLE UNION BUNKER - FUNDACIONES DEL ESTUDIO (SIN ESCALA)', 2.1);
        const tx = PX(88) + 7, n = UN.esperas || {};
        ['Una espera por cada barra horizontal,', 'del mismo diámetro que su barra:', `${cmt(pen)} dentro del búnker y, hacia afuera,`, `el traslapo (${UN.traslapo.replace('60 diámetros', '60ø').replace(', 60 como mínimo', ', mín. 60')}).`,
          'L: ' + largos.join(' · '), 'Recta donde tiene losa por delante;', 'si no, entra al muro y dobla en pata,', `a lo largo de él o hacia abajo (${cmt(dIn)} + ${cmt(pata)}).`,
          'Se dejan puestas antes de hormigonar.', 'Ejes ' + Object.keys(n).map(e => `${e}: ${n[e]}`).join(' · ') + ' (planilla).'].forEach((t, i) => T(g2, tx, y0 - 3.6 + 3.3 * i, t, 1.9));
      }
    }
    // ================= Notas =================
    {
      const ES = H.especificaciones, rc = ES.recubrimientos, x = 618, tr = [8, 10, 12, 16].map(d => `ø${d}: ${coma(60 * d / 10)}`).join(' · ');
      TA(sv, x, 334, 'NOTAS', 6.2); L(sv, x, 336.4, x + 205, 336.4);
      const lin = [
        '1. HORMIGON: ' + ES.hormigon.replace('Hormigón ', '') + '.', '   Emplantillado y hormigón pobre: G5.',
        '2. ACERO DE REFUERZO: ' + ES.acero.replace('Acero ', '') + '. Barras de los insertos: lisas A36 soldables, con gancho de 10 y cabeza soldada.',
        `3. RECUBRIMIENTOS (cm): fundaciones ${rc.fundaciones} · muros del búnker, cara exterior ${rc['muros del búnker, cara exterior']} ·`, `   elementos de hormigón armado ${rc['elementos de hormigón armado']} · losa ${rc.losa}.`, '   Estribos de las cadenas CF y del sobrecimiento: 3 (abajo, dentro del cimiento, 5).',
        `4. TRASLAPOS: ${ES.traslapo} (${tr} cm), alternados.`,
        '5. Estribos cerrados con ganchos de 135°. En las esquinas, las barras longitudinales llevan pata de 60 diámetros.', '   Cadenas CF: traba ø10 L=34 para las barras del medio en toda la cadena, una junto a cada estribo.',
        `6. NIVELES en cm desde el NPOG 0,00 (cara superior de la losa del búnker y del radier). Terreno natural: N.T.N ${N.ntn}.`.replace('-', '−'),
        `7. SELLO DE FUNDACION: búnker ${cmt(N.emplantillado_inf)}, 20 cm dentro del estrato indicado en la memoria de cálculo;`.replace('-', '−'), `   fachadas y dados ${cmt(N.sello_fachadas)} (0,90 m bajo el terreno natural), con hormigón pobre G5 hasta el sello;`.replace('-', '−'), `   cadenas CF ${cmt(N.sello_cf)}: bajo ellas, ${cmt(H.cf.emplantillado.espesor)} de G5 sobre ${cmt(H.cf.relleno.espesor)} de estabilizado compactado en 2 capas de 15, de ${cmt(H.cf.relleno.ancho)} de ancho.`.replace('-', '−'),
        '   Zanjas de las cadenas excavadas más abajo: se rellenan con el mismo estabilizado, compactado en capas de 15.',
        '8. Búnker y fundaciones del estudio van unidos, sin junta de dilatación: las armaduras horizontales de uno y otro',
        '   penetran 60 cm en el elemento contrario desde la línea de unión. Cada barra horizontal que llega al muro del',
        '   eje B lleva una espera de su mismo diámetro: 60 dentro del búnker y traslapo con su barra (ver detalle).',
        '9. Los números en círculo son las marcas de la planilla de doblado (pestaña Fundaciones del sitio).', '   Las barras se miden por fuera, de fuera a fuera de sus dobleces; L es la suma de los tramos.', '   Medidas en cm, salvo las placas (mm).',
        '10. Insertos PLc y PLb: placas embebidas a ras, con sus barras soldadas; se colocan antes de hormigonar.', '   Detalle y cuadro: pestaña Fundaciones del sitio.',
        '11. Impermeabilización del búnker (membranas, water-stop, cristalizante): pestaña Humedad del sitio.',
        '12. Muros del búnker: verticales de una pieza, con patas de 60 y 30 hacia el interior sobre la malla inferior de la', '   losa de fundación y ganchos superiores cruzados. Trabas ø8 L=30 entre las dos mallas, 9 por m² (cada 3 nudos).', '   Separadores de las mallas contra los moldajes.',
        '13. Esta lámina no define completa la losa de techo del búnker (suples, vigas VHA, VBL y VBC, hueco de la escalera)', '   ni la escalera: van en las láminas 02 y 03.',
        '14. Losa de fundación del búnker: la malla superior se sostiene en sus patas (25 + 5), sobre separadores de 5 cm', '   (trozos de conduit de PVC de 50 mm); ø10 corrido en los cuatro bordes, constructivo.'];
      lin.forEach((t, i) => T(sv, x, 344 + 5.0 * i, t, 2.3));
    }
    return sv;
  }

  // ---------- lámina 02: losa de techo del búnker, vigas (VHA, VBL, VBC) y hueco de la escalera ----------
  // Planta de la losa (1:50): contorno en línea gruesa; de trazos, lo que va debajo o dentro (cara interior de los muros y vigas); el hueco, con sus diagonales
  function plantaLosa(sv, D, H, E, X0, Y0) {
    const k = 10 / 50, ox = E.origen[0], oy = E.origen[1], X = x => X0 + (x - ox) * k, Y = y => Y0 + (y - oy) * k, XL = x => X0 + x * k, YL = y => Y0 + y * k;
    const g = el('g', { class: 'lm-planta' }, sv), LO = caja(H.losa.pts), HU = caja(H.losa.hueco), e = H.muros.espesor, rr = (c, cls) => R(g, X(c[0]), Y(c[1]), (c[2] - c[0]) * k, (c[3] - c[1]) * k, cls);
    rr(LO, 'lm-u2'); rr([LO[0] + e, LO[1] + e, LO[2] - e, LO[3] - e], 'lm-o');
    H.vigas.forEach(v => rr(caja(v.pts), 'lm-o'));
    rr(HU, 'lm-m'); L(g, X(HU[0]), Y(HU[1]), X(HU[2]), Y(HU[3])); L(g, X(HU[2]), Y(HU[1]), X(HU[0]), Y(HU[3]));
    return { g, k, X, Y, XL, YL, ox, oy };
  }
  // ejes 1 a 5 (arriba) y A, A2 y B (a la izquierda), con las cotas entre ejes
  function ejesLosa(g, V, D) {
    const ex = D.ejes.x, ey = { A: D.ejes.y.A, A2: D.ejes.y.A2, B: D.ejes.y.B }, yT = V.YL(-118), xI = V.XL(-128);
    Object.entries(ex).forEach(([n, x]) => { L(g, V.XL(x), yT + 4.8, V.XL(x), V.YL(688), 'lm-e'); burbuja(g, V.XL(x), yT, n); });
    Object.entries(ey).forEach(([n, y]) => { L(g, xI + 4.8, V.YL(y), V.XL(1092), V.YL(y), 'lm-e'); burbuja(g, xI, V.YL(y), n); });
    const xs = Object.values(ex), ys = Object.values(ey), yc = V.YL(-62), xc = V.XL(1122);
    for (let i = 0; i + 1 < xs.length; i++) cotaH(g, V.XL(xs[i]), V.XL(xs[i + 1]), yc, cmt(xs[i + 1] - xs[i]));
    for (let i = 0; i + 1 < ys.length; i++) cotaV(g, xc, V.YL(ys[i]), V.YL(ys[i + 1]), cmt(ys[i + 1] - ys[i]));
  }
  // cuadro de barras de una lámina: las filas de la planilla de doblado de sus elementos (marca, ø, tramos por fuera, largo, cantidad y kilos)
  function cuadroBarras(sv, PL, x, y, filtro, tituloT) {
    const g = el('g', { class: 'lm-cuadro' }, sv), filas = PL.filas.filter(filtro), hf = 3.8, W = 205, cols = [0, 12, 26, 108, 124, 140, 156, W], cab = ['MARCA', 'ø', 'TRAMOS, MEDIDOS POR FUERA (cm)', 'L (cm)', 'CANT.', 'kg', 'ELEMENTO'];
    TA(sv, x, y, tituloT, 4.6); const y0 = y + 3, yF = i => y0 + 5 + hf * i;
    R(g, x, y0, W, 5 + hf * (filas.length + 1), 'lm-f'); L(g, x, y0 + 5, x + W, y0 + 5, 'lm-f');
    cols.slice(1, -1).forEach(c => L(g, x + c, y0, x + c, yF(filas.length), 'lm-f'));
    cab.forEach((t, i) => T(g, x + (cols[i] + cols[i + 1]) / 2, y0 + 3.5, t, 1.7, { a: 'm' }));
    let kg = 0;
    filas.forEach((f, i) => { const yb = yF(i) + hf - 1.0; if (i) L(g, x, yF(i), x + W, yF(i), 'lm-tr');
      marca(g, x + 6, yF(i) + hf / 2, f.marca, 1.55);
      T(g, x + 19, yb, nomD(f.diam), 1.9, { a: 'm' }); T(g, x + 28, yb, f.ext.map(cmt).join(' + '), 1.9); T(g, x + 122.5, yb, coma(Math.round(f.L)), 1.9, { a: 'e' }); T(g, x + 138.5, yb, coma(f.n), 1.9, { a: 'e' });
      T(g, x + 154.5, yb, coma(f.kg), 1.9, { a: 'e' }); T(g, x + 158, yb, f.elemento, 1.9); kg += f.kg; });
    const yt = yF(filas.length); L(g, x, yt, x + W, yt, 'lm-f'); T(g, x + 28, yt + hf - 1.0, 'TOTAL DE ESTA LAMINA', 1.9); T(g, x + 154.5, yt + hf - 1.0, coma(kg), 1.9, { a: 'e' });
    return yt + hf;
  }
  function lamina02(cont, D, E, info) {
    const H = D.hormigon, sv = hoja(cont, info), N = H.niveles, PL = window.Armaduras.planilla(D), F = id => D.fierros.find(f => f.id === id);
    const ox = E.origen[0], oy = E.origen[1], AX = v => v + ox, AY = v => v + oy, ex = D.ejes.x, ey = D.ejes.y, e = H.muros.espesor, zL = N.losa_inf;
    const loc = c => [c[0] - ox, c[1] - oy, c[2] - ox, c[3] - oy], LO = loc(caja(H.losa.pts)), HU = loc(caja(H.losa.hueco));
    const viga = id => H.vigas.find(v => v.id === id), cH = loc(caja(viga('VHA-3').pts)), cL = loc(caja(viga('VBL').pts)), cC = loc(caja(viga('VBC').pts)), zV = v => v.z_inf - D.z_piso;
    const lx = pl => pl[0][0] - ox, ly = pl => pl[0][1] - oy, lp = pl => Math.hypot(pl[pl.length - 1][0] - pl[0][0], pl[pl.length - 1][1] - pl[0][1]);   // dónde parte la barra y cuánto avanza en planta
    const filaDe = (id, fn) => { const f = F(id), pl = instancias(f).find(fn || (() => true)); return pl ? PL.filaDe(f, pl) : null; };
    const rotL = (id, fn, pre) => { const f = F(id), r = filaDe(id, fn), esp = espDe(f); return `${pre || ''}${nomD(f.diam)}${esp && !pre ? '@' + esp : ''}, L=${coma(Math.round(r ? r.L : 0))}`; };   // «ø12@15, L=276» o «3ø16, L=659»
    // llamada con la marca de la planilla delante del texto
    const llamadaM = (g, px, py, tx, ty, textos, m, o) => { o = o || {}; const izq = o.lado === 'i', h = o.h || 2.1, w = Math.max(...textos.map(t => anchoT(t, h)));
      llamada(g, px, py, tx, ty, textos, Object.assign({ h }, o)); if (m != null) marca(g, izq ? tx - w - 1 - 3.0 : tx + w + 1 + 3.0, ty - 1.1, m, 2.1); };

    const XG = 1012;   // plano del corte g-g (local): por un estribo de la VBC y una barra inferior de la losa
    // ================= plantas 1:50: armadura inferior (izquierda) y superior (derecha) =================
    const VI = plantaLosa(sv, D, H, E, 82, 56), VS = plantaLosa(sv, D, H, E, 376, 56);
    [VI, VS].forEach((V, iV) => {
      const g = V.g; ejesLosa(g, V, D);
      cotaH(g, V.XL(LO[0]), V.XL(LO[2]), V.YL(LO[3]) + 8.5, cmt(LO[2] - LO[0]) + ' losa', { ref: [[V.XL(LO[0]), V.YL(LO[3])], [V.XL(LO[2]), V.YL(LO[3])]] });
      cotaV(g, V.XL(LO[0]) - 9, V.YL(LO[1]), V.YL(LO[3]), cmt(LO[3] - LO[1]) + ' losa', { ref: [[V.XL(LO[0]), V.YL(LO[1])], [V.XL(LO[0]), V.YL(LO[3])]], ty: V.YL(440) });
      T(g, V.XL((HU[0] + HU[2]) / 2) + 0.9, V.YL(545), `HUECO ${cmt(HU[2] - HU[0])}x${cmt(HU[3] - HU[1])}`, 1.9, { a: 'm', rot: -90 });
      T(g, V.XL((cH[0] + cH[2]) / 2) + 0.8, V.YL(iV ? 440 : 270), 'VHA 25/50', 1.8, { a: 'm', rot: -90 });
      T(g, V.XL((cL[0] + cL[2]) / 2) + 0.8, V.YL(545), 'VBL 25/50', 1.8, { a: 'm', rot: -90 });
      const sup = [F('LR-sup')].flatMap(instancias), bx = sup.flatMap(pl => pl.map(q => q[0] - ox)), by = sup.flatMap(pl => pl.map(q => q[1] - oy)), sx0 = Math.min(...bx), sx1 = Math.max(...bx), sy0 = Math.min(...by), sy1 = Math.max(...by);
      R(g, V.XL(sx0), V.YL(sy0), (sx1 - sx0) * V.k, (sy1 - sy0) * V.k, 'lm-o');
      T(g, V.XL(sx0) - 1.6, V.YL(sy1) - 3.2, 'SUPLES ø10@15', 1.8, { a: 'e' }); T(g, V.XL(sx0) - 1.6, V.YL(sy1) - 0.4, '(VER DETALLE)', 1.8, { a: 'e' });
    });
    // inferior: ø10@15 en los dos sentidos; frente al hueco, las barras llegan hasta la VBC y la VBL
    barraPlanta(VI.g, VI, PL, F('LN'), { eje: 0, en: 175, rep: 430, t: 0.4, filtro: pl => lp(pl) > 400 && lx(pl) < HU[0] });
    barraPlanta(VI.g, VI, PL, F('LN'), { eje: 0, en: 955, rep: 40, t: 0.6, filtro: pl => lp(pl) < 400 });
    barraPlanta(VI.g, VI, PL, F('LE'), { eje: 1, en: 70, rep: 640, t: 0.37, filtro: pl => lp(pl) > 1000 });
    barraPlanta(VI.g, VI, PL, F('LE'), { eje: 1, en: 500, rep: 640, t: 0.43, filtro: pl => lp(pl) < 1000 });
    T(VI.g, VI.XL(714), VI.YL(575), 'LOSA H.A. e=' + cmt(H.losa.espesor), 2.3, { a: 'm' }); T(VI.g, VI.XL(714), VI.YL(575) + 3.4, 'hormigón G30', 1.9, { a: 'm' });
    T(VI.g, VI.XL(cC[2]) + 7.5, VI.YL((cC[1] + cC[3]) / 2) + 6.2, 'VBC 40/25', 1.8); L(VI.g, VI.XL(cC[2] - 12), VI.YL((cC[1] + cC[3]) / 2), VI.XL(cC[2]) + 7, VI.YL((cC[1] + cC[3]) / 2) + 4.2);
    // marcas de corte (en la planta de la armadura inferior)
    marcaCorte(VI.g, VI.XL(cH[0] - 45), VI.YL(350), VI.XL(cH[2] + 45), VI.YL(350), 0, -1, 'e');
    marcaCorte(VI.g, VI.XL(cL[0] - 42), VI.YL(410), VI.XL(cL[2] + 34), VI.YL(410), 0, -1, 'f');
    marcaCorte(VI.g, VI.XL(XG), VI.YL(cC[1] - 46), VI.XL(XG), VI.YL(cC[3] + 30), 1, 0, 'g');
    // superior: L ø12@15 sobre los cuatro muros, ø10@20 sobre la VHA y junto a los muros A y B, ø16@15 en L junto a la VBL
    const enA = pl => ly(pl) < 300, en1 = pl => lx(pl) < 500;
    barraPlanta(VS.g, VS, PL, F('LT-NS'), { eje: 0, en: 175, rep: 197, t: 0.42, filtro: pl => enA(pl) && pl.length === 3 });
    barraPlanta(VS.g, VS, PL, F('LT-NS'), { eje: 0, en: 175, rep: 478, t: 0.56, filtro: pl => !enA(pl) && lp(pl) > 100 && lx(pl) < 800 });
    barraPlanta(VS.g, VS, PL, F('LT-NS16'), { eje: 0, en: 850, rep: 474, t: 0.56 });
    barraPlanta(VS.g, VS, PL, F('LT-EO'), { eje: 1, en: 330, rep: 198, t: 0.6, filtro: en1 });
    barraPlanta(VS.g, VS, PL, F('LT-EO'), { eje: 1, en: 110, rep: 890, t: 0.42, filtro: pl => !en1(pl) });
    barraPlanta(VS.g, VS, PL, F('LS'), { eje: 1, en: 330, rep: 575, t: 0.2, rotulo: [430, 300, 'i'] });
    barraPlanta(VS.g, VS, PL, F('LS-AB'), { eje: 1, en: 84, rep: 700, t: 0.3, filtro: enA });
    barraPlanta(VS.g, VS, PL, F('LS-AB'), { eje: 1, en: 560, rep: 700, t: 0.3, filtro: pl => !enA(pl) });
    { const f = F('LT-NS'), c25 = instancias(f).find(pl => !enA(pl) && lp(pl) < 100), c24 = instancias(f).find(pl => pl.length > 3);
      if (c25) llamadaM(VS.g, VS.XL(lx(c25) + 45), VS.YL(LO[3]) - 1.2, VS.XL(760), VS.YL(LO[3]) + 17.5, [rotL('LT-NS', pl => pl === c25), 'en L, frente al hueco'], (PL.filaDe(f, c25) || {}).marca, { lado: 'i', h: 1.9 });
      if (c24) llamadaM(VS.g, VS.XL(lx(c24) + 22), VS.YL(60), VS.XL(835), VS.YL(262), ['4 ' + rotL('LT-NS', pl => pl === c24).replace('@15', '') + ': bajan 1,4', 'bajo la placa del inserto PLc-4A'], (PL.filaDe(f, c24) || {}).marca, { h: 1.9, lado: 'i' }); }
    T(VS.g, VS.XL(cC[2]) + 7.5, VS.YL((cC[1] + cC[3]) / 2) + 6.2, 'VBC 40/25', 1.8); L(VS.g, VS.XL(cC[2] - 12), VS.YL((cC[1] + cC[3]) / 2), VS.XL(cC[2]) + 7, VS.YL((cC[1] + cC[3]) / 2) + 4.2);
    titulo(sv, 98, 222, 'PLANTA LOSA DE TECHO: ARMADURA INFERIOR', 50); titulo(sv, 392, 222, 'PLANTA LOSA DE TECHO: ARMADURA SUPERIOR', 50);

    // ================= detalle de la esquina del hueco (planta, 1:20): suples arriba y abajo =================
    {
      const k = 0.5, wx0 = 825, wx1 = 1085, wy0 = 152, wy1 = 345, X0 = 652, Y0 = 34, X = x => X0 + (x - wx0) * k, Y = y => Y0 + (y - wy0) * k, g = el('g', { class: 'lm-det' }, sv), id = 'lm-clip' + (++nClip);
      el('rect', { x: f2(X(wx0)), y: f2(Y(wy0)), width: f2((wx1 - wx0) * k), height: f2((wy1 - wy0) * k) }, el('clipPath', { id }, g));
      const gc = el('g', { 'clip-path': `url(#${id})` }, g), rr = (c, cls) => R(gc, X(c[0]), Y(c[1]), (c[2] - c[0]) * k, (c[3] - c[1]) * k, cls);
      rr([LO[0], LO[1], LO[2], LO[3]], 'lm-u2'); rr([LO[0] + e, LO[1] + e, LO[2] - e, LO[3] - e], 'lm-o'); rr(cL, 'lm-o'); rr(cC, 'lm-o');
      rr(HU, 'lm-m'); L(gc, X(HU[0]), Y(HU[1]), X(HU[2]), Y(HU[1] + (HU[2] - HU[0])), 'lm-f'); L(gc, X(HU[2]), Y(HU[1]), X(HU[0]), Y(HU[1] + (HU[2] - HU[0])), 'lm-f');
      const fS = F('LR-sup'), ins = instancias(fS);
      ins.forEach(pl => P(gc, pl.map(q => [X(q[0] - ox), Y(q[1] - oy)]), 'lm-b').setAttribute('stroke-width', '0.5'));
      quiebre(g, X(wx0), Y(wy0), X(wx0), Y(wy1)); quiebre(g, X(wx0), Y(wy0), X(wx1), Y(wy0)); quiebre(g, X(wx0), Y(wy1), X(wx1), Y(wy1));
      // una llamada por forma y sentido: marca, ø, separación y largo
      const horiz = pl => Math.abs(pl[1][0] - pl[0][0]) > Math.abs(pl[1][1] - pl[0][1]), grupos = {};
      ins.forEach(pl => { const r = PL.filaDe(fS, pl); if (!r) return; const kk = r.marca + (horiz(pl) ? 'h' : 'v'); (grupos[kk] = grupos[kk] || { r, h: horiz(pl), pls: [] }).pls.push(pl); });
      // de cada grupo se rotula la barra de más a la derecha (o la de más abajo), en su punta; los rótulos, a la derecha, en el orden de esas puntas
      const gs = Object.values(grupos).map(G => { const pl = G.pls.reduce((m, q) => (G.h ? Math.max(q[0][0], q[1][0]) > Math.max(m[0][0], m[1][0]) || (Math.max(q[0][0], q[1][0]) === Math.max(m[0][0], m[1][0]) && q[0][1] < m[0][1]) : q[0][0] > m[0][0]) ? q : m);
        return Object.assign(G, { px: (G.h ? Math.max(pl[0][0], pl[1][0]) - 5 : pl[0][0]) - ox, py: (G.h ? pl[0][1] : Math.min(pl[0][1], pl[1][1]) + 8) - oy }); }).sort((a, b) => a.py - b.py);
      gs.forEach((G, i) => llamadaM(g, X(G.px), Y(G.py), X(wx1) + 5, Y(wy0) + 10 + i * 14, [`${G.pls.length}ø10@15, L=${coma(Math.round(G.r.L))}`, G.h ? 'a lo largo de 1–5' : 'a lo largo de A–B'], G.r.marca, { h: 2.1, circ: 0.7 }));
      T(g, X((cL[0] + cL[2]) / 2) + 0.8, Y(wy1) - 9, 'VBL', 1.9, { a: 'm', rot: -90 }); T(g, X((HU[0] + HU[2]) / 2), Y(wy1) - 5, 'HUECO', 1.9, { a: 'm' });
      llamada(g, X(cC[2] - 6), Y(cC[3] - 4), X(wx1) + 5, Y(wy1) - 6, ['VBC 40/25 (de trazos)'], { h: 1.9 });
      T(g, X(LO[2] - e / 2) + 0.8, Y(300), 'MURO EJE 5', 1.8, { a: 'm', rot: -90 });
      titulo(sv, 652, 146, 'Detalle esquina del hueco', 20); T(sv, 652, 158.6, 'SUPLES ø10@15 EN LAS DOS ESQUINAS LIBRES DEL HUECO: IGUALES ARRIBA Y ABAJO', 2.1); T(sv, 652, 162.4, 'Las de 150, centradas en la esquina; las de 73 y 85 llegan hasta el borde del hueco o la cara del muro.', 1.9);
    }

    // ================= elevación de la VHA 25/50 del eje 3 (corte a lo largo, 1:20) =================
    const u0 = -22, U = y => y - u0, zb = 12, za = -95;
    const muroCaja = (C, ua, ub, t) => { const g = C.g, yt = C.Y(C.zb - 2); L(g, C.X(ua), C.Y(0), C.X(ua), yt, 'lm-uc'); L(g, C.X(ub), C.Y(0), C.X(ub), yt, 'lm-uc'); quiebre(g, C.X(ua), yt, C.X(ub), yt); if (t) T(g, C.X((ua + ub) / 2), yt - 1.6, t, 1.9, { a: 'm' }); };
    const tapaHueco = (C, uH, zE) => { R(C.g, C.X(uH) + 0.02, C.Y(1.4), C.X(C.W) - C.X(uH) + 2.6, (1.4 - zE + 1.4) * C.k, 'lm-w'); L(C.g, C.X(uH), C.Y(0), C.X(uH), C.Y(zE), 'lm-uc'); };
    {
      const Ch = corte(sv, D, PL, { eje: 'x', c: AX(ex['3']), u0: AY(u0), u1: AY(692), zmin: za, zmax: zb, ntn: [0, U(LO[1]) + 0.5], tol: { 'VHA-3-med': 9 }, sinPuntos: ['VHA-3-est'], proyectar: ['VHA-3-est'] }, 72, 262, 20), g2 = Ch.g, zv = zV(viga('VHA-3'));
      Ch.rotulos([['VHA-3-sup', rotL('VHA-3-sup', null, '3'), null, null], ['VHA-3-est', 'E ' + nomD(F('VHA-3-est').diam) + '@' + espDe(F('VHA-3-est')), -22, U(640)], ['VHA-3-med', rotL('VHA-3-med', null, '2'), null, null], ['VHA-3-inf', rotL('VHA-3-inf', null, '3'), null, null]], Ch.X(Ch.W) + 6, { gap: 6.2 });
      Ch.rotulos([['LT-NS', null, -2.6, U(120)], ['LS', null, null, U(60)], ['LE', null, null, U(60)], ['LN', null, -22.5, U(120)]], Ch.X(0) - 3, { izq: true, gap: 6.2 });
      Ch.cotaH(U(LO[1] + e), U(LO[3] - e), zv, cmt(LO[3] - LO[1] - 2 * e) + ' libres', 7);
      Ch.cotaV(U(340), zL, 0, cmt(-zL), 0); Ch.cotaV(U(340), zv, zL, cmt(zL - zv), 0);
      Ch.nivel(U(60), 0, 'NPOG 0,00', { alto: 5.5 });
      T(g2, Ch.X(U(LO[1] + e / 2)), Ch.Y(za) + 4.6, 'MURO EJE A', 1.9, { a: 'm' }); T(g2, Ch.X(U(LO[3] - e / 2)), Ch.Y(za) + 4.6, 'MURO EJE B', 1.9, { a: 'm' });
      Ch.despiece('LT-NS', { dx: 404, dy: 2 }); Ch.despiece('LN', { dx: 404, dy: 36, max: 112 });
      titulo(sv, 72, 323, 'Elevación VHA 25/50', 20); T(sv, 154, 323, 'VIGA BAJO LA LOSA EN EL EJE 3, DE MURO A MURO (CORTE POR SU EJE)', 2.1); T(sv, 154, 326.8, 'cuelga 25 bajo la losa; estribos cerrados en todo el largo, el primero a 5 de la cara del muro', 1.9);
    }
    // ================= elevación de la VBL 25/50 colgada (corte a lo largo, 1:20) =================
    {
      const Cl = corte(sv, D, PL, { eje: 'x', c: AX((cL[0] + cL[2]) / 2), u0: AY(u0), u1: AY(692), zmin: za, zmax: zb, ntn: [0, U(LO[1]) + 0.5], tol: { 'VBL-lat': 9.5 }, sinPuntos: ['VBL-est'], proyectar: ['VBL-est'] }, 72, 362, 20), g2 = Cl.g, zv = zV(viga('VBL'));
      const Es = H.escalera, mc = Es.muro ? loc(caja(Es.muro.pts)) : null, mn = Es.muro_norte ? loc(caja(Es.muro_norte.pts)) : null;
      if (mc) muroCaja(Cl, U(mn ? mn[1] : mc[1]), U(mc[3]), null);
      Cl.rotulos([['VBL-sup', rotL('VBL-sup', null, '5'), null, null], ['VBL-est', 'E ' + nomD(F('VBL-est').diam) + '@' + espDe(F('VBL-est')), -22, U(640)], ['VBL-lat', rotL('VBL-lat', null, '2') + ' (laterales)', null, null], ['VBL-inf', rotL('VBL-inf', null, '3'), null, null]], Cl.X(Cl.W) + 6, { gap: 6.2 });
      Cl.rotulos([['LT-NS', null, -2.6, U(120)], ['LS-AB', null, null, U(50)], ['LE', null, null, U(240)]], Cl.X(0) - 3, { izq: true, gap: 6.2 });
      // la VBC llega a la VBL: sus barras, en punta, con su rótulo debajo
      const bc = Cl.cerca('VBC-inf', U((cC[1] + cC[3]) / 2), -19);
      if (bc) llamada(g2, Cl.X(bc.u), Cl.Y(bc.z), Cl.X(U(cC[3]) + 26), Cl.Y(zv) + 9.5, ['VBC 40/25: 4ø12 arriba y 4ø12 abajo,', 'con gancho dentro de la VBL (corte g-g)'], { h: 1.9, circ: 0.9 });
      const b16 = Cl.cerca('LT-NS16', U(560), -2.8);
      if (b16) llamadaM(g2, Cl.X(b16.u), Cl.Y(b16.z), Cl.X(U(585)), Cl.Y(zb) - 6.4, [rotL('LT-NS16') + ' en L'], (PL.filaDe(b16.f, b16.pl) || {}).marca, { h: 1.9, lado: 'i' });
      if (mc) T(g2, Cl.X(U(400)), Cl.Y(zb) - 0.6, `MURO DE LA CAJA DE LA ESCALERA e=${cmt(mc[2] - mc[0])} (SOBRE LA LOSA)`, 1.8, { a: 'm' });
      Cl.cotaH(U(LO[1] + e), U(LO[3] - e), zv, cmt(LO[3] - LO[1] - 2 * e) + ' libres', 7);
      Cl.cotaV(U(140), zL, 0, cmt(-zL), 0); Cl.cotaV(U(140), zv, zL, cmt(zL - zv), 0);
      T(g2, Cl.X(U(LO[1] + e / 2)), Cl.Y(za) + 4.6, 'MURO EJE A', 1.9, { a: 'm' }); T(g2, Cl.X(U(LO[3] - e / 2)), Cl.Y(za) + 4.6, 'MURO EJE B', 1.9, { a: 'm' });
      Cl.despiece('VBL-sup', { dx: 404, dy: 2, max: 112, texto: rotL('VBL-sup', null, '5') });
      titulo(sv, 72, 423, 'Elevación VBL 25/50', 20); T(sv, 154, 423, 'VIGA COLGADA AL COSTADO DEL HUECO (LADO DEL EJE 4), DEL MURO A AL MURO B (CORTE POR SU EJE)', 2.1); T(sv, 154, 426.8, 'las 3ø16 de abajo entran 19 rectas en cada muro; las 5ø12 de arriba, en L de 72 por la cara exterior de los muros', 1.9);
    }
    // ================= cortes transversales (1:20) =================
    {   // e-e: VHA
      const xa = ex['3'] - 62, Ce = corte(sv, D, PL, { eje: 'y', c: AY(350), u0: AX(xa), u1: AX(ex['3'] + 62), zmin: -62, zmax: 10 }, 78, 452, 20), UU = x => x - xa, zv = zV(viga('VHA-3'));
      Ce.rotulos([['LS', null, null, null], ['VHA-3-sup', '3' + nomD(F('VHA-3-sup').diam), null, null], ['VHA-3-est', 'E ' + nomD(F('VHA-3-est').diam) + '@' + espDe(F('VHA-3-est')), -30, null], ['VHA-3-med', '2' + nomD(F('VHA-3-med').diam), null, null], ['VHA-3-inf', '3' + nomD(F('VHA-3-inf').diam), null, null]], Ce.X(Ce.W) + 6, { gap: 6.0 });
      Ce.rotulos([['LN', null, null, null], ['LE', null, null, null]], Ce.X(0) - 3, { izq: true, gap: 6.0, yMax: Ce.Y(zL) + 2 });
      Ce.cotaH(UU(cH[0]), UU(cH[2]), zv, cmt(cH[2] - cH[0]), 5.5); Ce.cotaV(UU(cH[0]), zv, zL, cmt(zL - zv), -6); Ce.cotaV(UU(cH[0]), zL, 0, cmt(-zL), -6, { ref: [[Ce.X(0), Ce.Y(0)]] });
      Ce.despiece('VHA-3-est', { dx: 96, dy: 2 });
      titulo(sv, 70, 498, 'Corte e-e', 20); T(sv, 112, 498, 'VHA 25/50 (EJE 3)', 2.1);
    }
    {   // f-f: VBL, con el borde del hueco y el muro de la caja
      const xa = cL[0] - 46, Cf = corte(sv, D, PL, { eje: 'y', c: AY(410), u0: AX(xa), u1: AX(HU[0] + 32), zmin: -62, zmax: 22 }, 262, 452, 20), UU = x => x - xa, zv = zV(viga('VBL')), mc = H.escalera.muro ? loc(caja(H.escalera.muro.pts)) : null;
      tapaHueco(Cf, UU(HU[0]), zv); if (mc) muroCaja(Cf, UU(mc[0]), UU(mc[2]), null);
      Cf.rotulos([['VBL-sup', '5' + nomD(F('VBL-sup').diam), null, null], ['VBL-est', 'E ' + nomD(F('VBL-est').diam) + '@' + espDe(F('VBL-est')), -30, null], ['VBL-lat', '2' + nomD(F('VBL-lat').diam) + ' laterales', null, null], ['VBL-inf', '3' + nomD(F('VBL-inf').diam), null, null]], Cf.X(Cf.W) + 6, { gap: 6.0 });
      Cf.rotulos([['LN', null, null, null], ['LE', null, null, null]], Cf.X(0) - 3, { izq: true, gap: 6.0, yMax: Cf.Y(zL) + 2 });
      Cf.cotaH(UU(cL[0]), UU(cL[2]), zv, cmt(cL[2] - cL[0]), 5.5); Cf.cotaV(UU(cL[0]), zv, zL, cmt(zL - zv), -6); Cf.cotaV(UU(cL[0]), zL, 0, cmt(-zL), -6, { ref: [[Cf.X(0), Cf.Y(0)]] });
      T(Cf.g, Cf.X(UU(HU[0]) + 4), Cf.Y(-14), 'HUECO', 1.9); if (mc) T(Cf.g, Cf.X(UU(mc[0])) - 1.2, Cf.Y(14), 'muro de la caja', 1.8, { a: 'e' });
      Cf.despiece('VBL-est', { dx: 92, dy: 2 });
      titulo(sv, 250, 498, 'Corte f-f', 20); T(sv, 292, 498, 'VBL 25/50 COLGADA, EN EL BORDE DEL HUECO', 2.1);
    }
    {   // g-g: VBC, botada dentro de la losa
      const ya = cC[1] - 64, Cg = corte(sv, D, PL, { eje: 'x', c: AX(XG), u0: AY(ya), u1: AY(HU[1] + 28), zmin: -48, zmax: 22 }, 438, 452, 20), UU = y => y - ya, mn = H.escalera.muro_norte ? loc(caja(H.escalera.muro_norte.pts)) : null;
      tapaHueco(Cg, UU(HU[1]), zL); if (mn) muroCaja(Cg, UU(mn[1]), UU(mn[3]), null);
      Cg.rotulos([['VBC-sup', '4' + nomD(F('VBC-sup').diam), null, null], ['VBC-est', 'E ' + nomD(F('VBC-est').diam) + '@' + espDe(F('VBC-est')), -12.5, null], ['VBC-inf', '4' + nomD(F('VBC-inf').diam), null, null]], Cg.X(Cg.W) + 6, { gap: 6.0 });
      Cg.rotulos([['LT-NS', null, -2.6, null], ['LN', null, -22.5, null]], Cg.X(0) - 3, { izq: true, gap: 6.0 });
      Cg.cotaH(UU(cC[1]), UU(cC[3]), zL, cmt(cC[3] - cC[1]), 5.5); Cg.cotaV(UU(cC[1]) - 12, zL, 0, cmt(-zL), 0);
      T(Cg.g, Cg.X(UU(HU[1]) + 4), Cg.Y(-14), 'HUECO', 1.9); if (mn) T(Cg.g, Cg.X(UU(mn[1])) - 1.2, Cg.Y(14), 'muro de la caja', 1.8, { a: 'e' });
      Cg.despiece('VBC-est', { dx: 104, dy: 4 });
      titulo(sv, 428, 498, 'Corte g-g', 20); T(sv, 470, 498, 'VBC 40/25 BOTADA (DENTRO DE LA LOSA)', 2.1);
    }
    {   // elevación de la VBC: de la VBL al muro del eje 5
      const xa = cL[0] - 26, yc = (cC[1] + cC[3]) / 2, Cv = corte(sv, D, PL, { eje: 'y', c: AY(yc), u0: AX(xa), u1: AX(LO[2] + 12), zmin: -72, zmax: 12, tol: { 'VBC-sup': 8, 'VBC-inf': 8 }, sinPuntos: ['VBC-est'], proyectar: ['VBC-est'] }, 632, 390, 20), UU = x => x - xa;
      Cv.rotulos([['VBC-sup', rotL('VBC-sup', null, '4'), null, null], ['VBC-est', 'E ' + nomD(F('VBC-est').diam) + '@' + espDe(F('VBC-est')), -12, UU(1030)], ['VBC-inf', rotL('VBC-inf', null, '4'), null, null]], Cv.X(Cv.W) + 6, { gap: 6.2 });
      Cv.rotulos([['VBL-sup', '5' + nomD(F('VBL-sup').diam) + ' VBL', null, null], ['VBL-inf', '3' + nomD(F('VBL-inf').diam) + ' VBL', null, null]], Cv.X(0) - 3, { izq: true, gap: 6.2 });
      Cv.cotaH(UU(cL[2]), UU(LO[2] - e), zL, cmt(LO[2] - e - cL[2]) + ' libres', 6);
      T(Cv.g, Cv.X(UU(LO[2] - e / 2)) + 9, Cv.Y(-72) + 4.4, 'MURO EJE 5', 1.9, { a: 'm' }); T(Cv.g, Cv.X(UU((cL[0] + cL[2]) / 2)), Cv.Y(zV(viga('VBL'))) + 3.4, 'VBL', 1.9, { a: 'm' });
      Cv.despiece('VBC-sup', { dy: 47, texto: rotL('VBC-sup', null, '4') }); Cv.despiece('VBC-inf', { dy: 70, dx: -7, texto: rotL('VBC-inf', null, '4') });
      titulo(sv, 620, 498, 'Elevación VBC 40/25', 20); T(sv, 702, 498, 'DE LA VBL AL MURO DEL EJE 5', 2.1);
    }
    // ================= notas =================
    {
      const ES = H.especificaciones, rc = ES.recubrimientos, x = 618, y0 = 176, tr = [8, 10, 12, 16].map(d => `ø${d}: ${coma(60 * d / 10)}`).join(' · ');
      TA(sv, x, y0, 'NOTAS', 6.2); L(sv, x, y0 + 2.4, x + 205, y0 + 2.4);
      const lin = [
        '1. HORMIGON: G30 (losa y vigas, con el resto del búnker). ACERO: ' + ES.acero.replace('Acero ', '') + '.',
        `2. RECUBRIMIENTOS (cm): losa ${rc.losa} · vigas ${rc['elementos de hormigón armado']}, al estribo.`, `   TRASLAPOS: ${ES.traslapo} (${tr} cm), alternados.`,
        `3. LOSA e=${cmt(H.losa.espesor)}. Abajo: ø10@15 en los dos sentidos, con gancho hacia arriba en los muros; primero las barras A–B`, '   y sobre ellas las 1–5. Frente al hueco llegan hasta la VBC y la VBL.',
        '4. Arriba: L ø12@15 sobre los cuatro muros (pata de 72 hacia abajo por la cara exterior del muro, por dentro de sus', '   verticales, y 203 dentro de la losa); ø10@20 de 160 sobre la VHA; ø10@20 en 1–5 junto a los muros A y B, bajo las L;', '   ø16@15 en L sobre el muro B en los 1,20 m junto a la VBL.',
        '5. VHA 25/50 (eje 3) y VBL 25/50: cuelgan 25 bajo la losa y van de muro a muro. VBC 40/25: dentro de la losa,', '   de la VBL al muro del eje 5. Estribos cerrados con ganchos de 135°.',
        `6. HUECO DE LA ESCALERA ${cmt(HU[2] - HU[0])} x ${cmt(HU[3] - HU[1])}: suples ø10@15 arriba y abajo en sus dos esquinas libres (detalle).`,
        '7. Los números en círculo son las marcas de la planilla de doblado (pestaña Fundaciones del sitio).', '   Las barras se miden por fuera, de fuera a fuera de sus dobleces; L es la suma de los tramos. Medidas en cm.',
        '8. Muros, losa de fundación e insertos PLc y PLb: lámina 01. Los insertos se colocan antes de hormigonar.',
        '9. Escalera: lámina 03. Las barras de su viga central entran al muro del eje B: se dejan puestas antes de hormigonarlo.'];
      lin.forEach((t, i) => T(sv, x, y0 + 10 + 4.7 * i, t, 2.2));
      cuadroBarras(sv, PL, x, y0 + 10 + 4.7 * lin.length + 6, g => /^(losa del búnker|VHA|viga colgada|viga botada)/.test(g.elemento), 'CUADRO DE BARRAS');
    }
    return sv;
  }

  // llamada con la marca de la planilla al final del texto; cota entre dos puntos cualesquiera (para las medidas perpendiculares a la pendiente de la escalera)
  function llamadaMarca(g, px, py, tx, ty, textos, m, o) { o = o || {}; const izq = o.lado === 'i', h = o.h || 2.1, w = Math.max(...textos.map(t => anchoT(t, h)));
    llamada(g, px, py, tx, ty, textos, Object.assign({ h }, o)); if (m != null) marca(g, izq ? tx - w - 4 : tx + w + 4, ty - 1.1, m, 2.1); }
  function cotaL(g, x1, y1, x2, y2, t, o) { o = o || {}; const h = o.h || 2.1, dx = x2 - x1, dy = y2 - y1, len = Math.hypot(dx, dy) || 1, nx = -dy / len, ny = dx / len;
    L(g, x1, y1, x2, y2); [[x1, y1], [x2, y2]].forEach(([x, y]) => L(g, x - nx * 1.1, y - ny * 1.1, x + nx * 1.1, y + ny * 1.1));
    let ang = Math.atan2(dy, dx) * 180 / Math.PI; if (ang > 90) ang -= 180; if (ang <= -90) ang += 180;
    const ar = ang * Math.PI / 180; T(g, (x1 + x2) / 2 + Math.sin(ar) * 0.9 + (o.dx || 0), (y1 + y2) / 2 - Math.cos(ar) * 0.9 + (o.dy || 0), t, h, { a: 'm', rot: ang }); }

  // ---------- lámina 03: escalera del búnker (viga central VE 25/40 bajo una losa de 10, 19 peldaños) ----------
  function lamina03(cont, D, E, info) {
    const H = D.hormigon, sv = hoja(cont, info), N = H.niveles, PL = window.Armaduras.planilla(D), F = id => D.fierros.find(f => f.id === id);
    const ox = E.origen[0], oy = E.origen[1], AX = v => v + ox, AY = v => v + oy, z0 = D.z_piso, zL = N.losa_inf, zP = N.piso_bunker;
    const Es = H.escalera, ES = Es.estructura, tr = Es.tramo, nP = tr.peldanos, hu = tr.largo / nP, ch = (Es.z_arriba - Es.z_abajo) / nP, yT = tr.y_arriba - oy, yP = tr.y_abajo - oy, kE = ch / hu, aE = Math.atan(kE), cE = Math.cos(aE), sE = Math.sin(aE);
    const VE = ES.viga, hL = ES.losa.espesor, hV = VE.alto, bV = VE.ancho, xc = VE.x - ox, vL = hL / cE, vV = hV / cE, yUL = yT - (-zP - vL) / kE, yUV = yT - (-zP - vV) / kE;   // dónde tocan el piso la cara inferior de la losa de 10 y la de la viga
    const loc = c => [c[0] - ox, c[1] - oy, c[2] - ox, c[3] - oy], HU = loc(caja(H.losa.hueco)), x0E = HU[0], x1E = HU[2], muro = id => loc(caja(H.muros.piezas.find(m => m.id === id).pts)), mS = muro('M-S'), mE = muro('M-E');
    const cC = loc(caja(H.vigas.find(v => v.id === 'VBC').pts)), cL = loc(caja(H.vigas.find(v => v.id === 'VBL').pts)), mn = Es.muro_norte ? loc(caja(Es.muro_norte.pts)) : null;
    const perfil = [[yT, 0]]; for (let i = 0; i < nP; i++) { const y = yT - (i + 1) * hu; perfil.push([y, -i * ch], [y, -(i + 1) * ch]); }   // (y, z): arista del muro B, huellas y contrahuellas
    const filaDe = id => { const f = F(id); return PL.filaDe(f, instancias(f)[0]); }, mk = id => (filaDe(id) || {}).marca, Lde = id => coma(Math.round((filaDe(id) || {}).L || 0));
    const cP = xc + 7.7;   // plano de los cortes a lo largo: por la ø16 de afuera y la ø12 de arriba de ese lado de la viga
    // corte a lo largo por la viga: el modelo cortado por el plano cP más el hormigón de la escalera (que no es un prisma del modelo) y el hueco de la losa
    function corteLong(cfg, X0, Y0, esc) {
      const C = corte(sv, D, PL, Object.assign({ eje: 'x', c: AX(cP), sinPuntos: ['VE-est'], proyectar: ['VE-est'] }, cfg), X0, Y0, esc), ua = cfg.u0 - oy, U = y => y - ua, gc = C.gc;
      const prim = gc.querySelector('polyline.lm-b, circle.lm-p'), antes = n => gc.insertBefore(n, prim), pt = (y, z) => f2(C.X(U(y))) + ',' + f2(C.Y(z));
      if (cfg.zmax > zL) { antes(el('rect', { x: f2(C.X(U(HU[1])) + 0.02), y: f2(C.Y(1.5)), width: f2((HU[3] - HU[1]) * C.k - 0.04), height: f2((3 - zL) * C.k), class: 'lm-w' }));
        antes(el('line', { x1: f2(C.X(U(HU[1]))), y1: f2(C.Y(0)), x2: f2(C.X(U(HU[1]))), y2: f2(C.Y(zL)), class: 'lm-uc' })); }
      const pol = perfil.concat([[yUV, zP], [yT, -vV]]).map(([y, z]) => pt(y, z)).join(' ');
      antes(el('polygon', { points: pol, class: 'lm-w' })); antes(el('polygon', { points: pol, class: 'lm-uc' }));
      antes(el('line', { x1: f2(C.X(U(yUL))), y1: f2(C.Y(zP)), x2: f2(C.X(U(yT))), y2: f2(C.Y(-vL)), class: 'lm-o' }));   // cara inferior de la losa de 10 (los vuelos, más allá)
      return { C, U };
    }
    // ================= A) corte a lo largo por la viga central (1:20) =================
    const uA0 = 107.5, XA0 = 62, YA0 = 50;
    {
      const { C, U } = corteLong({ u0: AY(uA0), u1: AY(717.5), zmin: -400, zmax: 34 }, XA0, YA0, 20), g = C.g, X = y => C.X(U(y)), Y = C.Y;
      if (mn) { const yt = Y(28); L(g, X(mn[1]), Y(0), X(mn[1]), yt, 'lm-uc'); L(g, X(mn[3]), Y(0), X(mn[3]), yt, 'lm-uc'); quiebre(g, X(mn[1]), yt, X(mn[3]), yt); T(g, X(mn[3]) + 1.4, Y(15), 'muro de la caja', 1.8); }
      const b = (id, u, z) => C.cerca(id, u == null ? null : U(u), z);
      // arriba a la izquierda: lo que va en los peldaños y sobre la viga
      const pN = b('ES-N', 470, null), pP = b('ES-P', 452, null), pT = b('ES-LT', 430, null), pS = b('VE-sup', 405, null), xi = X(432);
      if (pN) llamadaMarca(g, C.X(pN.u), Y(pN.z), xi, Y(-32), ['1ø8 corrida en cada nariz'], mk('ES-N'), { lado: 'i', circ: 0.8 });
      if (pP) llamadaMarca(g, C.X(pP.u), Y(pP.z), xi, Y(-46), ['Escuadra ø8@19 bajo cada huella (7 por peldaño)'], (PL.filaDe(pP.f, pP.pl) || {}).marca, { lado: 'i' });
      if (pT) llamadaMarca(g, C.X(pT.u), Y(pT.z), xi, Y(-60), ['ø8@16 transversal, arriba de la losa de 10'], mk('ES-LT'), { lado: 'i', circ: 0.8 });
      if (pS) llamadaMarca(g, C.X(pS.u), Y(pS.z), xi, Y(-74), [`2ø12 arriba de la viga, L=${Lde('VE-sup')}`], mk('VE-sup'), { lado: 'i' });
      // abajo a la derecha: la viga
      const pE = b('VE-est', 520, null), pI = b('VE-inf', 492, null), xd = X(498);
      if (pE) llamadaMarca(g, C.X(pE.u), Y(pE.z - 14), xd, Y(-196), ['E ø8@16 de la viga, 2 por peldaño'], mk('VE-est'), {});
      if (pI) llamadaMarca(g, C.X(pI.u), Y(pI.z), xd, Y(-212), [`3ø16 abajo de la viga, L=${Lde('VE-inf')}`], mk('VE-inf'), {});
      llamada(g, X(455), Y(-(yT - 455) * kE - vL), xd, Y(-228), [`Losa de ${cmt(hL)}, cara inferior (de trazos)`], { h: 2.1 });
      llamada(g, X(478), Y(-(yT - 478) * kE - vV), xd, Y(-244), [`Viga central ${VE.nombre}`], { h: 2.1 });
      llamada(g, X((yP + yUV) / 2), Y(zP + 12), X(110), Y(zP + 88), ['Pie macizo sobre la losa de fundación'], { h: 2.1 });
      // cotas y niveles
      C.cotaH(U(yP), U(yT), -400, `${cmt(tr.largo)} = ${nP} huellas de ${coma(hu, 1)}`, 7);
      C.cotaV(U(mS[3]) + 16, zP, 0, `${cmt(-zP)} = ${nP} contrahuellas de ${coma(ch, 1)}`, 0);
      C.cotaH(U(yUV), U(yT), zP, `${coma(Math.round(yT - yUV))}: la viga llega al piso`, -9, { tx: X(520) });
      C.nivel(U(150), 0, 'NPOG 0,00', { alto: 6, lado: 'i' }); nivel(g, X(300), Y(zP), cmt(zP).replace('-', '−') + ' piso del búnker', { alto: 5 });
      T(g, X((mS[1] + mS[3]) / 2), Y(-400) + 4.4, 'MURO EJE B', 1.9, { a: 'm' }); T(g, X(cC[1] - 30), Y(zL) + 4, 'LOSA DE TECHO', 1.9, { a: 'm' }); T(g, X((cC[1] + cC[3]) / 2), Y(zL) + 4, 'VBC', 1.9, { a: 'm' });
      T(g, X(430), Y(zP - 17), 'LOSA DE FUNDACION e=' + cmt(H.losa_fundacion ? H.losa_fundacion.espesor : 35), 1.9, { a: 'm' });
      // despiece de las barras de la viga (abajo a la derecha de la hoja)
      C.despiece('VE-inf', { dx: 322, dy: 250, max: 112, texto: `3ø16, L=${Lde('VE-inf')}` }); C.despiece('VE-sup', { dx: 492, dy: 250, max: 112, texto: `2ø12, L=${Lde('VE-sup')}` });
      T(sv, 446, 398, 'BARRAS DE LA VIGA CENTRAL (ESC. 1:20, CON QUIEBRE)', 2.1); T(sv, 446, 402, 'el pie va dentro de la losa de fundación; arriba, la L entra al muro del eje B', 1.9);
      titulo(sv, 62, 270, 'Corte a-a', 20); T(sv, 104, 270, 'A LO LARGO DE LA ESCALERA, POR LA VIGA CENTRAL (MIRANDO HACIA EL EJE 5)', 2.1); T(sv, 104, 273.8, 'baja del muro del eje B hacia el eje A', 1.9);
    }
    // ================= planta de la escalera (1:20), bajo el corte y alineada con él =================
    {
      const k = 0.5, g = el('g', { class: 'lm-planta' }, sv), X = y => XA0 + (y - uA0) * k, Yp0 = 296, xN = mE[2] + 8, Y = x => Yp0 + (xN - x) * k, rr = (ya, yb, xa, xb, cls) => R(g, X(ya), Y(xb), (yb - ya) * k, (xb - xa) * k, cls);
      const ya = uA0 - 30, yb = mS[3];
      rr(ya, yb, mE[0], mE[2], 'lm-uc'); trama(g, X(ya), Y(mE[2]), (yb - ya) * k, (mE[2] - mE[0]) * k, 'rad');                     // muro del eje 5
      rr(mS[1], mS[3], cL[0] - 22, mE[0], 'lm-uc'); trama(g, X(mS[1]), Y(mE[0]), (mS[3] - mS[1]) * k, (mE[0] - cL[0] + 22) * k, 'rad');   // muro del eje B
      quiebre(g, X(ya), Y(mE[2]), X(ya), Y(cL[0] - 22)); quiebre(g, X(mS[1]), Y(cL[0] - 22), X(mS[3]), Y(cL[0] - 22));
      rr(yP, yT, x0E, x1E, 'lm-m');                                                                                                // escalera
      for (let i = 1; i < nP; i++) L(g, X(yT - i * hu), Y(x0E), X(yT - i * hu), Y(x1E), 'lm-f');
      rr(yUV, yT, xc - bV / 2, xc + bV / 2, 'lm-o');                                                                               // viga VE, debajo
      rr(ya, mS[1], cL[0], cL[2], 'lm-o'); rr(cC[1], cC[3], cC[0], cC[2], 'lm-o');                                                 // VBL y VBC, arriba
      L(g, X(yT - 30), Y(xc + 30), X(yP + 40), Y(xc + 30), 'lm-f'); punta(g, X(yP + 40), Y(xc + 30), -1, 0, 2.6, 0.5); T(g, X(yT - 34), Y(xc + 30) - 1.1, 'BAJA', 2.1, { a: 'e' });
      T(g, X(yT - 6), Y(xc - 34), '1', 1.9, { a: 'e' }); T(g, X(yP + hu - 6), Y(xc - 34), String(nP), 1.9, { a: 'e' });
      T(g, X((yUV + yT) / 2 + 60), Y(xc) + 0.7, `VIGA ${VE.nombre} (debajo)`, 1.8, { a: 'm' }); T(g, X(ya + 70), Y((cL[0] + cL[2]) / 2) + 0.7, 'VBL (arriba)', 1.8); T(g, X((cC[1] + cC[3]) / 2) + 0.7, Y(xc - 36), 'VBC (arriba)', 1.8, { a: 'm', rot: -90 });
      T(g, X(ya + 70), Y((mE[0] + mE[2]) / 2) + 0.7, 'MURO EJE 5', 1.9); T(g, X((mS[1] + mS[3]) / 2) + 0.7, Y(xc), 'MURO EJE B', 1.9, { a: 'm', rot: -90 });
      const xcv = X(yP) - 7; cotaV(g, xcv, Y(mE[0]), Y(x1E), cmt(mE[0] - x1E), { lado: 'izq' }); cotaV(g, xcv, Y(x1E), Y(xc + bV / 2), cmt(x1E - xc - bV / 2)); cotaV(g, xcv, Y(xc + bV / 2), Y(xc - bV / 2), cmt(bV)); cotaV(g, xcv, Y(xc - bV / 2), Y(x0E), cmt(xc - bV / 2 - x0E));
      cotaV(g, X(yP) - 15, Y(x1E), Y(x0E), cmt(x1E - x0E), { ref: [[X(yP), Y(x1E)], [X(yP), Y(x0E)]] });
      cotaH(g, X(yP), X(yT), Y(cL[0]) + 6, `${cmt(tr.largo)} = ${nP} huellas de ${coma(hu, 1)}`, { ref: [[X(yP), Y(x0E)], [X(yT), Y(x0E)]] });
      titulo(sv, 62, 408, 'Planta escalera', 20); T(sv, 128, 408, `ANCHO ${cmt(x1E - x0E)}, A ${cmt(mE[0] - x1E)} DEL MURO DEL EJE 5 · VIGA CENTRAL DE ${cmt(bV)}, CON VUELOS DE ${cmt((x1E - x0E - bV) / 2)} A CADA LADO`, 2.1);
    }
    // ================= B) tres peldaños ampliados (1:10) =================
    {
      const uB0 = 319.5, { C, U } = corteLong({ u0: AY(uB0), u1: AY(uB0 + 110), zmin: -280, zmax: -138 }, 452, 38 - 138, 10), g = C.g, X = y => C.X(U(y)), Y = C.Y, xr = C.X(C.W) + 6;
      const b = (id, u, z) => C.cerca(id, u == null ? null : U(u), z), eP = b('ES-P', 398, null), its = [];
      if (eP) { const fl = PL.filaDe(eP.f, eP.pl); its.push([eP, `Escuadra ø8@19, L=${fl ? coma(Math.round(fl.L)) : ''}: ${fl ? fl.ext.map(cmt).join(' + ') : ''}`, fl && fl.marca]); }
      [['ES-N', 387, '1ø8 en la nariz'], ['VE-sup', 417, '2ø12'], ['ES-LT', 373, 'ø8@16 transversal'], ['VE-est', 404, 'E ø8@16'], ['VE-inf', 423, '3ø16']].forEach(([id, u, t]) => { const q = b(id, u, null); if (q) its.push([q, t, (PL.filaDe(q.f, q.pl) || {}).marca]); });
      its.forEach(([q, t, m], i) => llamadaMarca(g, C.X(q.u), Y(q.z), xr, Y(-146) + i * 8.2, [t], m, { circ: q.linea ? null : 0.9 }));
      const i10 = 10, yR = yT - (i10 + 1) * hu; C.cotaH(U(yR), U(yR + hu), -i10 * ch, coma(hu, 1), -6); C.cotaV(U(yR), -(i10 + 1) * ch, -i10 * ch, coma(ch, 1), -5);
      const perp = (y, h1, t) => { const zr = -(yT - y) * kE; cotaL(g, X(y), Y(zr), X(y + h1 * sE), Y(zr - h1 * cE), t); };
      perp(yR + hu * 0.5, hV, cmt(hV)); perp(yR + hu * 1.62, hL, cmt(hL));
      titulo(sv, 452, 196, 'Detalle peldaños', 10); T(sv, 452, 208.6, 'POR LA VIGA CENTRAL: LA VIGA MIDE 40 Y LA LOSA 10, PERPENDICULARES A LA PENDIENTE', 2.1);
    }
    // ================= C) corte perpendicular a la pendiente, por un estribo (1:10), mirando hacia el muro B =================
    {
      const zl = p => p[2] - z0, sDe = p => (yT - (p[1] - oy)) * cE - zl(p) * sE, ests = instancias(F('VE-est')), est0 = ests.reduce((m, pl) => Math.abs(pl[2][1] - oy - 409.5) < Math.abs(m[2][1] - oy - 409.5) ? pl : m), s0 = sDe(est0[2]);
      const fS = p => { const dy = yT - (p[1] - oy), z_ = zl(p); return [p[0], dy * cE - z_ * sE, dy * sE + z_ * cE]; };   // al marco de la losa: x, s a lo largo de la pendiente y h perpendicular (0 en la línea de los rincones)
      const D2 = { z_piso: 0, hormigon: { muros: { piezas: [] }, losa: {}, vigas: [], niveles: N }, fierros: D.fierros.filter(f => f.elemento === 'escalera del búnker').map(f => ({ id: f.id, elemento: f.elemento, diam: f.diam, d: f.d, polilineas: instancias(f).map(pl => pl.map(fS)) })) };
      const xa = cL[0] - 8, xb = mE[2] + 4, C = corte(sv, D2, PL, { eje: 'y', c: s0, u0: AX(xa), u1: AX(xb), zmin: -56, zmax: 24, girar: true, tol: { 'ES-LL': 3 } }, 446, 268, 10), g = C.g, gc = C.gc, X = x => C.X(xb - x), Y = C.Y;
      let t0 = 0; for (let h = 0; h >= -30; h -= 0.1) { const y = yT - s0 * cE + h * sE, z = -s0 * sE - h * cE, i = Math.floor((yT - y) / hu); if (y < yT && y > yP && z <= -i * ch + 1e-6) t0 = -h; else break; }   // alto del peldaño sobre la línea de los rincones, en este corte
      const prim = gc.querySelector('polyline.lm-b, circle.lm-p'), xv0 = xc - bV / 2, xv1 = xc + bV / 2, pol = [[x0E, t0], [x1E, t0], [x1E, -hL], [xv1, -hL], [xv1, -hV], [xv0, -hV], [xv0, -hL], [x0E, -hL]].map(([x, z]) => f2(X(x)) + ',' + f2(Y(z))).join(' ');
      gc.insertBefore(el('polygon', { points: pol, class: 'lm-uc' }), prim);
      R(g, X(mE[2]), Y(22), (mE[2] - mE[0]) * C.k, 76 * C.k, 'lm-uc'); quiebre(g, X(mE[2]), Y(22), X(mE[0]), Y(22)); quiebre(g, X(mE[2]), Y(-54), X(mE[0]), Y(-54)); T(g, X((mE[0] + mE[2]) / 2) + 0.7, Y(-16), 'MURO EJE 5', 1.9, { a: 'm', rot: -90 });
      C.rotulos([['ES-LT', 'ø8@16 de borde a borde', null, null], ['ES-P', 'Escuadras ø8@19, 7 en el ancho', null, null], ['ES-LL', '2ø8 a lo largo, en cada vuelo', null, null], ['VE-sup', '2ø12', null, null], ['VE-est', 'E ø8@16', -22, null], ['VE-inf', '3ø16', null, null]], C.X(C.W) + 6, { gap: 6.4 });
      cotaH(g, X(x1E), X(x0E), Y(t0) - 6, `${cmt(x1E - x0E)} (ancho de la escalera)`, { ref: [[X(x1E), Y(t0)], [X(x0E), Y(t0)]] });
      const yc = Y(-hV) + 7; cotaH(g, X(mE[0]), X(x1E), yc, cmt(mE[0] - x1E), { fuera: 'izq' }); cotaH(g, X(x1E), X(xv1), yc, cmt(x1E - xv1)); cotaH(g, X(xv1), X(xv0), yc, cmt(bV)); cotaH(g, X(xv0), X(x0E), yc, cmt(xv0 - x0E));
      cotaV(g, X(x0E) + 6, Y(0), Y(-hL), cmt(hL)); cotaV(g, X(x0E) + 13, Y(0), Y(-hV), cmt(hV), { ref: [[X(xv0), Y(-hV)]] });
      C.despiece('VE-est', { dx: 150, dy: 46 });
      titulo(sv, 446, 352, 'Corte b-b', 10); T(sv, 488, 352, 'PERPENDICULAR A LA PENDIENTE, POR UN ESTRIBO (MIRANDO HACIA EL MURO B)', 2.1);
    }
    // ================= notas y cuadro de barras =================
    {
      const ES2 = H.especificaciones, x = 640, y0 = 28, anc = ES.anclajes || [], aI = anc.find(a => a.familia === 'VE-inf') || {}, aS = anc.find(a => a.familia === 'VE-sup') || {};
      TA(sv, x, y0, 'NOTAS', 6.2); L(sv, x, y0 + 2.4, x + 186, y0 + 2.4);
      const lin = [
        '1. HORMIGON: G25 (G30 si se hormigona con el búnker). ACERO: ' + ES2.acero.replace('Acero ', '') + '.',
        '2. RECUBRIMIENTO: 3 cm (5 en la losa de fundación; 4 por fuera del muro del eje B).',
        `3. ESCALERA: ${nP} peldaños de ${coma(hu, 1)} x ${coma(ch, 1)}, ancho ${cmt(x1E - x0E)}. Baja ${cmt(-zP)} del NPOG 0,00 al`, '   piso del búnker, desde el muro del eje B hacia el eje A.',
        `4. VIGA CENTRAL ${VE.nombre} bajo una losa de ${cmt(hL)}, medidas perpendiculares a la pendiente.`, '   Al pie, la escalera va maciza sobre la losa de fundación.',
        '5. VIGA: 3ø16 abajo y 2ø12 arriba, con gancho de 90° en la losa de fundación y L en el', '   muro del eje B. Estribos ø8 cerrados, 2 por peldaño, con ganchos de 135°.',
        '6. LOSA DE 10: ø8@16 transversal arriba, de borde a borde, y 2ø8 a lo largo en cada vuelo.',
        '7. PELDAÑOS: escuadras ø8@19 (7 por peldaño) y 1ø8 corrida en cada nariz.',
        '8. MONTAJE: las 3ø16 y las 2ø12 de la viga se dejan puestas ANTES de hormigonar la', '   losa de fundación (pie con gancho) y el muro del eje B (L). También pueden dejarse', '   esperas del mismo diámetro y con el mismo gancho, traslapadas 60 diámetros', '   (ø16: 96 · ø12: 72 cm) fuera de la losa y del muro.',
        '9. Altura libre desde las narices: 2,33 m a la losa y 2,27 m al cielo.',
        '10. Los números en círculo son las marcas de la planilla de doblado. Las barras se miden', '   por fuera; L es la suma de los tramos. Medidas en cm.',
        '11. Losa de techo, VBL y VBC: lámina 02. Muros y losa de fundación: lámina 01.'];
      lin.forEach((t, i) => T(sv, x, y0 + 10 + 4.6 * i, t, 2.1));
      cuadroBarras(sv, PL, x - 22, y0 + 10 + 4.6 * lin.length + 8, g => g.elemento === 'escalera del búnker', 'CUADRO DE BARRAS');
    }
    return sv;
  }

  // La lámina 01 está visada por el ingeniero (24-11-2026) y su viñeta lo dice. Las láminas 02 y 03 se dibujan desde el mismo modelo, con la enfierradura del informe
  // que el ingeniero revisó y aceptó (10-11-2026); él no las vio como lámina, así que no llevan fecha de visado. El dueño cerró los vistos buenos (24-11-2026:
  // «se acabaron los vistos buenos»): tampoco llevan «para visar»; la viñeta dice solo de dónde sale la enfierradura
  const LISTA = [{ n: '01', id: 'fundaciones', titulo: 'Planta de fundaciones y cortes', plano: 'E-01', contenido: ['PLANTA FUNDACIONES', 'CORTES Y NOTAS'], fn: lamina01, visada: '24-11-2026', ident: 'Planta de fundaciones y cortes: versión final' },
    { n: '02', id: 'losa-techo', titulo: 'Losa de techo del búnker, vigas y hueco', plano: 'E-02', contenido: ['PLANTA LOSA DE TECHO DEL BUNKER', 'VIGAS, HUECO Y NOTAS'], fn: lamina02, ident: 'Losa de techo del búnker, vigas y hueco de la escalera' },
    { n: '03', id: 'escalera', titulo: 'Escalera del búnker', plano: 'E-03', contenido: ['ESCALERA DEL BUNKER', 'CORTES, PLANTA Y NOTAS'], fn: lamina03, ident: 'Escalera del búnker: cortes, planta y detalle de peldaños' }];
  function dibujar(cont, n, D, E, ver) {
    const l = LISTA.find(x => x.n === n) || LISTA[0];
    const info = { n: l.n, plano: l.plano, contenido: l.contenido, rev: '', fecha: '24-11-2026', mandante: 'Gabriel Toledo Brintrup', proyecto: 'Casa Toledo , Sector estudio', pie: l.visada ? 'visado el ' + l.visada : '',
      identificacion: [['1', l.ident, '24-11-2026']],
      revisiones: [],
      nota: ['Plano dibujado desde el modelo 3D del estudio, con el formato de las láminas del proyecto.'].concat(l.visada
        ? [`Visado por el ingeniero civil del proyecto para cortar y doblar fierro (${l.visada}), con sus últimas indicaciones`, 'incorporadas. No lleva firma ni timbre.']
        : ['La enfierradura es la del informe revisado y aceptado por el ingeniero civil del proyecto (10-11-2026).', 'No lleva firma ni timbre.'],
        ['Las medidas mandan sobre el dibujo; cualquier diferencia con la obra se consulta antes de hormigonar.']),
      profesionales: ['PROYECTO: ingeniero civil del proyecto', 'CALCULO: verificado con modelo 3D', l.visada ? `REVISO: ingeniero civil (${l.visada})` : 'REVISO:', 'APROBO:', 'DIBUJO: modelo 3D del sitio' + (ver ? ' (' + ver + ')' : '')] };
    return l.fn(cont, D, E, info);
  }
  window.LaminasEstudio = { lista: LISTA.map(l => ({ n: l.n, id: l.id, titulo: l.titulo, plano: l.plano })), dibujar };
})();
