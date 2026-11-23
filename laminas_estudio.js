// Láminas del estudio «a la antigua» (Gabriel, 17-11-2026: «un plano a la antigua, como los que envió el ingeniero, así tal cual… el enfierrador
// quiere eso… con toda la formalidad que pondría un ingeniero civil estructural, mismo formato»). Cada lámina es un SVG en milímetros de papel
// (A1 apaisado, 841 × 594), con el marco y la viñeta de las láminas del proyecto del estudio (medidos de la lámina 01 rev 1), la letra de trazo
// único de los planos CAD (fuente_trazos.js), plantas a 1:50 y cortes a 1:20 con el despiece de las barras al lado.
// Nada se retipea: la geometría sale de DATA_ESTUDIO_EST.hormigon, las barras de DATA_ESTUDIO_EST.fierros (cortadas por el mismo plano que los
// cortes de la sección 07, con Armaduras.seccion) y las marcas de la planilla de doblado (Armaduras.planilla).
// La viñeta NO lleva nombre, timbre ni firma de ningún profesional: es un plano de trabajo para que lo vise el ingeniero del proyecto.
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
    T(g, 689.4, 558.6, '(revisado con cálculo propio)', 1.9, { a: 'm' });
    R(g, 664.5, 563.2, 49.8, 11.4, 'lm-m');
    T(g, 689.4, 568.0, 'SIN FIRMA', 2.6, { a: 'm', sw: 0.3 }); T(g, 689.4, 572.3, 'para visar por el ingeniero', 1.7, { a: 'm' });
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
  function marca(g, x, y, n, r) { r = r || 2.3; C(g, x, y, r, 'lm-f'); T(g, x, y + r * 0.42, String(n), r * 0.86, { a: 'm' }); }
  // Barra en planta, como en la «Planta losa» del proyecto: una barra de la familia dibujada entera, con su rótulo (marca, ø, separación y largo)
  // a lo largo, y la línea de reparto con flechas hasta la primera y la última barra. o: { en: coordenada (cm locales) de la barra elegida,
  // rep: coordenada de la línea de reparto, t: posición del rótulo (0–1), texto: sufijo («inf.», «sup.»), lado: 1 | −1 }
  function barraPlanta(g, V, PL, f, o) {
    const ins = instancias(f), eje = Math.abs(ins[0][0][0] - ins[ins.length - 1][0][0]) > Math.abs(ins[0][0][1] - ins[ins.length - 1][0][1]) ? 0 : 1;   // eje en que se reparten
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
    if (hor) { if (fila) marca(g, tx - w / 2 - 3.6, ty - 2.6, fila.marca); T(g, tx, ty - 1.3, rot, 2.3, { a: 'm' }); }
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
    const c0 = co(ins[0]), c1 = co(ins[ins.length - 1]);
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
    const dentro = (u, z) => u > -0.5 && u < W + 0.5 && z > za - 0.5 && z < zb + 0.5, pts = S.puntos.filter(p => dentro(p.u, p.z));
    pts.forEach(p => C(gc, X(p.u), Y(p.z), Math.max(0.42, p.f.diam / 20 * k), 'lm-p'));
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
    llamada(g, V.XL(ex['1'] + 2), V.YL(ey.B + 21), V.XL(150), V.YL(ey.B + 122), ['JUNTA DE 2 cm ENTRE EL BUNKER', 'Y LAS FUNDACIONES DEL ESTUDIO'], { h: 1.9 });
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
        T(g2, x0d + 3.2, y0d + hb + 6.4, `cabeza ${coma(cab[0] * 10)}x${coma(cab[1] * 10)}x12 soldada`, 1.9); T(g2, x0d + 3.2, y0d + hb + 9.8, 'bajo el gancho (por visar)', 1.9); }
      titulo(sv, 664, 186, 'Corte b-b', 20); T(sv, 707, 186, 'EJE 1 POR EL PILAR D (EJES 5 Y E IGUALES)', 2.1);
    }
    // ================= Corte c-c: cadena de fundación CF 30/50 (1:20) =================
    {
      const yC = ey.C2, zse = N.sello_cf, G5 = H.cf.emplantillado, RE = H.cf.relleno, zg5 = N.cf_inf - G5.espesor;   // bajo la cadena: 20 de G5 sobre 30 de estabilizado compactado, sello −100 (el ingeniero, 22 y 23-11-2026)
      const Cc = corte(sv, D, PL, { eje: 'x', c: AX(880), u0: AY(yC) - 45, u1: AY(yC) + 45, zmin: zse - 6, zmax: 12 }, 704, 222, 20), U = y => y - (yC - 45), g2 = Cc.g, a2 = H.cf.ancho / 2;
      Cc.rotulos([['CF-C2-sup', null, null, null], ['CF-C2-est', 'E ' + nomD(F('CF-C2-est').diam) + '@' + espDe(F('CF-C2-est')), -18, null], ['CF-C2-med', null, null, null], ['CF-C2-inf', null, null, null]], Cc.X(Cc.W) + 6, { gap: 6.4 });
      llamada(g2, Cc.X(U(yC + 8)), Cc.Y((N.cf_inf + zg5) / 2), Cc.X(Cc.W) + 6, Cc.Y(-59), [`Hormigón G5 ${cmt(G5.ancho)}x${cmt(G5.espesor)}`], { h: 2.3 });
      llamada(g2, Cc.X(U(yC + 5)), Cc.Y((zg5 + zse) / 2), Cc.X(Cc.W) + 6, Cc.Y(-78), [`Estabilizado compactado ${cmt(RE.ancho)}x${cmt(RE.espesor)}`, '2 capas de 15, Tmáx 2"'], { h: 2.3 });
      llamada(g2, Cc.X(U(yC + 18)), Cc.Y(zse), Cc.X(Cc.W) + 6, Cc.Y(zse) - 1, [`Sello ${cmt(zse).replace('-', '−')}, compactado`], { h: 2.3 });
      llamada(g2, Cc.X(U(yC + 32)), Cc.Y(-5), Cc.X(Cc.W) + 6, Cc.Y(13), ['Radier e=10 y capas: ver corte b-b'], { h: 2.3 });
      Cc.nivel(U(yC - 30), 0, 'NPOG 0,00', { alto: 6.5, lado: 'i' });
      const dxc = -(45 - a2) * Cc.k - 4; Cc.cotaV(U(yC - a2), N.cf_inf, 0, cmt(-N.cf_inf), dxc); Cc.cotaV(U(yC - a2), zg5, N.cf_inf, cmt(N.cf_inf - zg5), dxc); Cc.cotaV(U(yC - a2), zse, zg5, cmt(zg5 - zse), dxc);
      Cc.cotaH(U(yC - G5.ancho / 2), U(yC + G5.ancho / 2), zse, cmt(G5.ancho), 5);
      Cc.despiece('CF-C2-est', { dx: -62, dy: 22 });
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
    // ================= Notas =================
    {
      const ES = H.especificaciones, rc = ES.recubrimientos, x = 618, tr = [8, 10, 12, 16].map(d => `ø${d}: ${coma(60 * d / 10)}`).join(' · ');
      TA(sv, x, 334, 'NOTAS', 6.2); L(sv, x, 336.4, x + 205, 336.4);
      const lin = [
        '1. HORMIGON: ' + ES.hormigon.replace('Hormigón ', '') + '.', '   Emplantillado y hormigón pobre: G5.',
        '2. ACERO DE REFUERZO: ' + ES.acero.replace('Acero ', '') + '. Barras de los insertos: lisas A36 soldables, con gancho de 10 y cabeza soldada.',
        `3. RECUBRIMIENTOS (cm): fundaciones ${rc.fundaciones} · muros del búnker, cara exterior ${rc['muros del búnker, cara exterior']} ·`, `   elementos de hormigón armado ${rc['elementos de hormigón armado']} · losa ${rc.losa}.`, '   Estribos de las cadenas CF y del sobrecimiento: 3 (abajo, dentro del cimiento, 5).',
        `4. TRASLAPOS: ${ES.traslapo} (${tr} cm), alternados.`,
        '5. Estribos cerrados con ganchos de 135°. En las esquinas, las barras longitudinales llevan pata de 60 diámetros.',
        `6. NIVELES en cm desde el NPOG 0,00 (cara superior de la losa del búnker y del radier). Terreno natural: N.T.N ${N.ntn}.`.replace('-', '−'),
        `7. SELLO DE FUNDACION: búnker ${cmt(N.emplantillado_inf)}, 20 cm dentro del estrato indicado en la memoria de cálculo;`.replace('-', '−'), `   fachadas y dados ${cmt(N.sello_fachadas)} (0,90 m bajo el terreno natural), con hormigón pobre G5 hasta el sello;`.replace('-', '−'), `   cadenas CF ${cmt(N.sello_cf)}: bajo ellas, ${cmt(H.cf.emplantillado.espesor)} de G5 sobre ${cmt(H.cf.relleno.espesor)} de estabilizado compactado en 2 capas de 15, de ${cmt(H.cf.relleno.ancho)} de ancho.`.replace('-', '−'),
        '8. Junta de 2 cm entre el búnker y las fundaciones del estudio, sin barras pasantes.',
        '9. Los números en círculo son las marcas de la planilla de doblado (pestaña Fundaciones del sitio).', '   Las barras se miden por fuera, de fuera a fuera de sus dobleces; L es la suma de los tramos.', '   Medidas en cm, salvo las placas (mm).',
        '10. Insertos PLc y PLb: placas embebidas a ras, con sus barras soldadas; se colocan antes de hormigonar.', '   Detalle y cuadro: pestaña Fundaciones del sitio.',
        '11. Impermeabilización del búnker (membranas, water-stop, cristalizante): pestaña Revisión del sitio.',
        '12. Muros del búnker: verticales de una pieza, con patas de 60 y 30 hacia el interior sobre la malla inferior de la', '   losa de fundación y ganchos superiores cruzados. Trabas ø8 L=30 entre las dos mallas, 9 por m² (cada 3 nudos).', '   Separadores de las mallas contra los moldajes.',
        '13. Esta lámina no define completa la losa de techo del búnker (suples, vigas VHA, VBL y VBC, hueco de la escalera)', '   ni la escalera: van en lámina aparte. Mientras tanto, pestañas Planta y Fundaciones del sitio.',
        '14. Losa de fundación del búnker: la malla superior se sostiene en sus patas (25 + 5), sobre separadores de 5 cm', '   (trozos de conduit de PVC de 50 mm); ø10 corrido en los cuatro bordes, constructivo.'];
      lin.forEach((t, i) => T(sv, x, 344 + 5.0 * i, t, 2.3));
    }
    return sv;
  }

  const LISTA = [{ n: '01', id: 'fundaciones', titulo: 'Planta de fundaciones y cortes', plano: 'E-01', contenido: ['PLANTA FUNDACIONES', 'CORTES Y NOTAS'], fn: lamina01 }];
  function dibujar(cont, n, D, E, ver) {
    const l = LISTA.find(x => x.n === n) || LISTA[0];
    const info = { n: l.n, plano: l.plano, contenido: l.contenido, rev: 'B', fecha: '23-11-2026', mandante: 'Gabriel Toledo Brintrup', proyecto: 'Casa Toledo , Sector estudio',
      identificacion: [['1', 'Láminas 01 rev 1 y 02 a 05 del proyecto del estudio (ingeniero)', '04-2026'], ['2', 'Revisión estructural con cálculo propio (modelo 3D)', '23-10-2026'],
        ['3', 'Respuestas del ingeniero: solución mixta, insertos, VBL', '28-10-2026'], ['4', 'Informe V134 revisado por el ingeniero: aceptado', '10-11-2026'],
        ['5', 'Observaciones del ingeniero a la rev. A y sus respuestas', '23-11-2026']],
      revisiones: [['A', 'EMITIDO PARA VISAR POR EL INGENIERO (17-11-2026)'], ['B', 'CON LAS OBSERVACIONES DEL INGENIERO (22 Y 23-11-2026)' + (ver ? ' (modelo ' + ver + ')' : '')]],
      nota: ['Plano de trabajo dibujado desde el modelo 3D del estudio, con el formato de las láminas del proyecto.',
        'Geometría, armaduras y niveles: los del modelo revisado con cálculo propio (23-10-2026) y aceptado por el', 'ingeniero del proyecto (28-10 y 10-11-2026), con sus observaciones a la rev. A (22 y 23-11-2026) ya aplicadas.',
        'NO LLEVA FIRMA: antes de cortar y doblar fierro, debe visarlo el ingeniero civil del proyecto.', 'Las medidas mandan sobre el dibujo. Cualquier diferencia con la obra se consulta antes de hormigonar.'],
      profesionales: ['PROYECTO: ingeniero civil del proyecto', 'CALCULO: revisión con modelo propio', 'REVISO: pendiente (visar esta lámina)', 'APROBO:', 'DIBUJO: modelo 3D del sitio' + (ver ? ' (' + ver + ')' : '')] };
    return l.fn(cont, D, E, info);
  }
  window.LaminasEstudio = { lista: LISTA.map(l => ({ n: l.n, id: l.id, titulo: l.titulo, plano: l.plano })), dibujar };
})();
