// Capa "Terreno" del plano 2D (index.html): lote con sus deslindes, cierros, acceso, gimnasio, estudio con búnker y lo que se ve
// en la foto de dron (piscina, jacuzzi, explanadas, radier, pozo, estanque), dibujado en el mismo marco y escala que la casa
// (cm; x hacia el oriente, y hacia el sur, norte arriba) con los datos de sitio.js (DATA_SITIO, los mismos que usa el 3D).
// Gabriel, 21-10-2026: "en el plano 2D agreguemos también el terreno, el estudio, el cerco, todo" → opción 1: capa dentro del Plano.
//
//   const T = Terreno2D.crear(g, DATA_SITIO, { el, fmt, casa: [[x, y], ...] });   // g: <g> del svg donde dibujar; casa: contorno del nivel 1
//   T.vertices   → puntos a los que se ajusta la regla de medir (deslindes, pilares, edificios, piscina)
//   T.aplicar(k) → al cambiar el zoom: esconde los nombres chicos cuando el plano está muy alejado
//   T.lote       → [x0, y0, x1, y1] del lote, para encuadrar
(function () {
  const NS = 'http://www.w3.org/2000/svg';

  function crear(g, D, o) {
    const el = o.el, fmt = o.fmt;
    const P = pts => pts.map(p => p[0].toFixed(1) + ',' + p[1].toFixed(1)).join(' ');
    const txt = (parent, x, y, t, cls, extra) => { const e = el('text', Object.assign({ x, y, class: cls }, extra || {}), parent); e.textContent = t; return e; };
    // texto girado r° en (x, y) y corrido 'off' píxeles de pantalla hacia (nx, ny): el corrimiento se recalcula en aplicar(k) para que no lo tache su línea
    const txtR = (parent, x, y, t, cls, r, nx, ny, off, extra) => txt(parent, x, y, t, cls, Object.assign({ 'data-r': r, 'data-cx': x, 'data-cy': y, 'data-nx': nx, 'data-ny': ny, 'data-off': off }, extra || {}));
    // texto corrido 'dy' píxeles de pantalla hacia abajo (rótulos apilados): se recalcula en aplicar(k), así los renglones no se juntan al alejar
    const txtD = (parent, x, y, t, cls, dy, extra) => txt(parent, x, y, t, cls, Object.assign({ 'data-dy': dy }, extra || {}));
    const titulo = (n, t) => { const e = document.createElementNS(NS, 'title'); e.textContent = t; n.appendChild(e); return n; };
    const verts = [];
    const V = pts => pts.forEach(p => verts.push([p[0], p[1]]));
    const bbox = pts => [Math.min(...pts.map(p => p[0])), Math.min(...pts.map(p => p[1])), Math.max(...pts.map(p => p[0])), Math.max(...pts.map(p => p[1]))];
    // cortes de una recta horizontal (y = cte) o vertical (x = cte) con un polígono: para medir distancias reales entre caras
    const cortesY = (poly, y) => { const xs = []; for (let i = 0; i < poly.length; i++) { const a = poly[i], b = poly[(i + 1) % poly.length]; if ((a[1] <= y && b[1] > y) || (b[1] <= y && a[1] > y)) xs.push(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])); } return xs.sort((p, q) => p - q); };
    const cortesX = (poly, x) => { const ys = []; for (let i = 0; i < poly.length; i++) { const a = poly[i], b = poly[(i + 1) % poly.length]; if ((a[0] <= x && b[0] > x) || (b[0] <= x && a[0] > x)) ys.push(a[1] + (x - a[0]) * (b[1] - a[1]) / (b[0] - a[0])); } return ys.sort((p, q) => p - q); };

    // ---- subcapas, de abajo hacia arriba ----
    const gL = el('g', { class: 'tr-g-lote' }, g), gR = el('g', { class: 'tr-g-real' }, g), gC = el('g', { class: 'tr-g-cierros' }, g),
      gB = el('g', { class: 'tr-g-edif' }, g), gK = el('g', { class: 'tr-g-cotas' }, g), gT = el('g', { class: 'tr-g-textos' }, g);

    // ---- lote: pasto, deslinde y sus largos ----
    const lot = D.lote.poligono; V(lot);
    const loteBox = bbox(lot);
    titulo(el('polygon', { points: P(lot), class: 'tr-pasto' }, gL), `Lote: ${D.lote.superficie_m2.toLocaleString('es-CL', { maximumFractionDigits: 1 })} m² según el polígono del emplazamiento (la lámina rotula 5.135 m²) · rol ${D.lote.rol} · fuente: ${D.fuente}`);
    const des = D.lote.deslindes, m = v => fmt(v) + ' m';
    const rot = (a, b) => Math.atan2(b[1] - a[1], b[0] - a[0]) * 180 / Math.PI;
    const mid = (a, b) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
    const lblDes = (a, b, t, lado, f) => {   // rótulo del deslinde paralelo al lado (lado 1: hacia adentro del lote); f: dónde a lo largo del lado (0,5 = al medio)
      f = f === undefined ? 0.5 : f; const c = [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f]; let r = rot(a, b); if (r > 90 || r < -90) r += 180;
      const nx = -(b[1] - a[1]), ny = (b[0] - a[0]), L = Math.hypot(nx, ny) || 1;
      txtR(gT, c[0], c[1], t, 'tr-des', r, nx / L * lado, ny / L * lado, 11);
    };
    // los largos de los deslindes van por fuera del lote, como en un plano de loteo: con letra de 14 px adentro topaban con las cotas y los rótulos
    lblDes(lot[0], lot[1], `deslinde del fondo ${m(des.norte)}`, -1);
    lblDes(lot[1], lot[2], `deslinde lateral ${m(des.este)}`, -1, 0.28);   // corrido hacia el fondo: al medio chocaba con la cota del estudio al deslinde
    lblDes(lot[13], lot[0], `deslinde lateral ${m(des.oeste)}`, -1);
    // sur: el deslinde es el eje de la servidumbre (camino); el cierro de verdad va 5 m adentro
    const sv = D.servidumbre;
    titulo(el('polyline', { points: P(sv.eje), class: 'tr-serv' }, gL), sv.dato);
    titulo(el('polyline', { points: P(sv.cierro_exterior), class: 'tr-serv-ext' }, gL), 'Cierro del frente, al otro lado del camino (supuesto: trazo del emplazamiento)');
    txt(gT, 1300, (sv.cierro_exterior[0][1] + sv.cierro_exterior[1][1]) / 2 + 150, 'cierro al otro lado del camino (supuesto)', 'tr-sub');   // textos cortos: con 14 px los largos no cabían en el ancho del teléfono
    lblDes(sv.eje[1], sv.eje[0], `deslinde ${m(des.sur)} · eje del camino`, 1);   // hacia afuera: sobre el camino, entre el eje y el cierro exterior
    // (la flecha del norte ya no va aquí: la pone la página, fija en una esquina del plano, para la casa y el terreno; Gabriel y el ingeniero, 23-10-2026)

    // ---- cierro perimetral (norte, oriente y poniente, sobre el deslinde): pilares de hormigón con reja cada 3 m (foto de dron) ----
    for (let i = 0; i < lot.length; i++) {
      const a = lot[i], b = lot[(i + 1) % lot.length];
      if (Math.min(a[1], b[1]) > 4500) continue;   // el lado sur es la servidumbre: ahí va el cierro interior
      const L = Math.hypot(b[0] - a[0], b[1] - a[1]), n = Math.floor(L / 300);
      for (let j = 0; j <= n; j++) { const t = j * 300 / L, y = a[1] + (b[1] - a[1]) * t; if (y > 4150) continue; el('rect', { x: a[0] + (b[0] - a[0]) * t - 12, y: y - 12, width: 24, height: 24, class: 'tr-reja' }, gC); }   // termina en el cierro sur
    }
    // ---- cierro sur interior: franja de 70 con pilares de 50 × 70 cada 2,5 m, curvado hacia el acceso ----
    D.cierros.forEach(c => titulo(el('polyline', { points: P(c.pts), class: 'tr-cierro', 'stroke-width': c.ancho }, gC), c.dato));
    D.pilares_cierro.forEach(p => { const [a, b] = p.lado, ang = (p.ang || 90) - 90; el('rect', { x: p.c[0] - a / 2, y: p.c[1] - b / 2, width: a, height: b, class: 'tr-pilar', transform: `rotate(${ang} ${p.c[0]} ${p.c[1]})` }, gC); verts.push([p.c[0], p.c[1]]); });
    // ---- acceso: pilares, puerta peatonal, poste y portón corredera (hoja abierta hacia el oriente) ----
    const ac = D.acceso;
    [['pilar_oeste', 'Pilar del acceso junto a la puerta peatonal (132 cm)'], ['pilar_este', 'Pilar del acceso junto al portón (100 cm)'], ['poste', 'Poste entre la puerta y el portón (20 cm)']].forEach(([k, t]) => {
      const [[x1, y1], [x2, y2]] = ac[k]; titulo(el('rect', { x: x1, y: y1, width: x2 - x1, height: y2 - y1, class: 'tr-pilar' }, gC), t); V([[x1, y1], [x2, y1], [x1, y2], [x2, y2]]);
    });
    const yA = ac.linea_y + 35;
    titulo(el('line', { x1: ac.puerta.vano[0][0], y1: yA, x2: ac.puerta.vano[1][0], y2: yA, class: 'tr-acceso' }, gC), `Puerta peatonal ${fmt(ac.puerta.ancho)} m`);
    titulo(el('line', { x1: ac.porton.vano[0][0], y1: yA, x2: ac.porton.vano[1][0], y2: yA, class: 'tr-acceso tr-porton' }, gC), `Portón ${fmt(ac.porton.ancho)} m · ${ac.porton.tipo}`);
    titulo(el('line', { x1: ac.porton.hoja_abierta[0][0], y1: ac.porton.hoja_abierta[0][1] + 20, x2: ac.porton.hoja_abierta[1][0], y2: ac.porton.hoja_abierta[1][1] + 20, class: 'tr-hoja' }, gC), 'Hoja del portón abierta, corrida detrás del pilar del portón');
    txt(gT, ac.porton.hoja_abierta[1][0] + 90, ac.porton.hoja_abierta[1][1] + 22, '→', 'tr-sub');
    txtD(gT, (ac.pilar_oeste[0][0] + ac.pilar_este[1][0]) / 2, ac.linea_y, `acceso · puerta ${fmt(ac.puerta.ancho)} + portón corredera ${fmt(ac.porton.ancho)}`, 'tr-sub tr-cota-t', -17);   // sobre la flecha de la hoja, a distancia fija en pantalla
    // cierro de la servidumbre: el nombre entre el cierro y el deslinde; el detalle aparece al acercar (con el lote entero no cabe en un renglón de 14 px)
    txt(gT, 2200, 4390, 'cierro de servidumbre', 'tr-sub');   // a la derecha de la cota de 5,01 y lejos de los botones de zoom del teléfono
    txtD(gT, 2200, 4390, 'pilares 50 × 70 cada 2,5 m, a 5 m del deslinde', 'tr-sub tr-chico', 17);

    // ---- lo que se ve en la foto de dron (rectificada con las esquinas del lote, ±30 cm): explanadas, radieres, piscinas, pozo, estanque ----
    const R = D.real, nota = ' (foto de dron, ±30 cm)';
    R.senderos.concat(R.radieres).forEach(it => { titulo(el('polygon', { points: P(it.pts), class: 'tr-horm' }, gR), it.nombre + nota + ' · ' + it.dato); V(it.pts); });
    [['piscina', 'Piscina'], ['piscina_chica', 'Jacuzzi (piscina chica)']].forEach(([k, nm]) => {
      const it = R[k]; if (!it) return;
      if (it.borde) el('polygon', { points: P(it.borde), class: 'tr-borde' }, gR);
      titulo(el('polygon', { points: P(it.pts), class: 'tr-agua' }, gR), nm + nota + ' · ' + it.dato); V(it.pts);
    });
    R.otros.forEach(it => { titulo(el('polygon', { points: P(it.pts), class: 'tr-horm' }, gR), it.nombre + nota + ' · ' + it.dato); });
    const lblReal = (pts, t, cls, dy) => { const b = bbox(pts); txt(gT, (b[0] + b[2]) / 2, (b[1] + b[3]) / 2 + (dy || 0), t, cls || 'tr-sub'); };
    lblReal(R.piscina.pts, 'piscina');
    { const b = bbox(R.piscina_chica.pts); txtD(gT, (b[0] + b[2]) / 2, b[1], 'jacuzzi', 'tr-sub tr-chico', -10); }   // sobre el jacuzzi: al centro lo tapaba el rótulo del eje 4 de la casa
    R.radieres.forEach(it => { const b = bbox(it.pts), w = b[2] - b[0]; if (w > 1500) txtD(gT, (b[0] + b[2]) / 2, b[3], `radier ${fmt(w)} × ${fmt(b[3] - b[1])} m`, 'tr-sub', 14); else lblReal(it.pts, 'explanada', 'tr-sub tr-chico'); });   // el radier grande se rotula bajo su borde, lejos del rótulo del gimnasio
    R.otros.forEach(it => { const b = bbox(it.pts); txt(gT, (b[0] + b[2]) / 2, b[1] - 60, it.nombre.split(' (')[0].toLowerCase(), 'tr-sub tr-chico'); });
    txt(gT, 1460, -1800, 'explanada de hormigón', 'tr-sub');   // un poco más abajo: con 14 px tocaba el rótulo del radier

    // ---- gimnasio (construido): planta en L y su cubierta con aleros ----
    const gi = D.gimnasio;
    titulo(el('polygon', { points: P(gi.cubierta.contorno), class: 'tr-cub' }, gB), 'Cubierta del gimnasio con sus aleros (4,44 m hacia la casa)');
    titulo(el('polygon', { points: P(gi.planta), class: 'tr-edif' }, gB), `Gimnasio (construido): ${fmt(gi.ancho)} × ${fmt(gi.largo)} m en L, muros de ${gi.muro} · ${gi.dato}`); V(gi.planta);
    { const b = bbox(gi.planta), cx = (b[0] + b[2]) / 2, cy = (b[1] + b[3]) / 2;   // apilado sobre el gimnasio y su alero; el renglón de arriba queda bajo la cota al deslinde del fondo
      txtD(gT, cx, cy, 'GIMNASIO', 'tr-lbl', -6); txtD(gT, cx, cy, 'construido', 'tr-sub', 11); txtD(gT, cx, cy, `${fmt(gi.ancho)} × ${fmt(gi.largo)}`, 'tr-sub', 28); }
    txt(gT, 1971, -2720, 'cubierta (alero de 4,44 hacia la casa)', 'tr-sub tr-chico');

    // ---- estudio con búnker (por construir): contorno, recintos y el búnker punteado bajo la cafetería ----
    const es = D.estudio, eb = bbox(es.exterior);
    titulo(el('polygon', { points: P(es.exterior), class: 'tr-edif' }, gB), `Estudio (por construir): ${fmt(es.ancho)} × ${fmt(es.largo)} m por fuera, muros de ${es.muro}; a 3,50 m del deslinde lateral`); V(es.exterior);
    es.recintos.forEach(r => { titulo(el('polygon', { points: P(r.pts), class: 'tr-recinto' }, gB), r.nombre); V(r.pts); const b = bbox(r.pts); const nm = r.nombre.split(' (')[0]; if (b[2] - b[0] > 200) txt(gT, (b[0] + b[2]) / 2, (b[1] + b[3]) / 2, nm.length > 22 ? nm.slice(0, 20) + '…' : nm, 'tr-sub tr-rec'); });
    titulo(el('polygon', { points: P(es.bunker.pts), class: 'tr-bunker' }, gB), `Búnker bajo la cafetería: ${es.bunker.dato || 'losa, muros de 25 y losa de fundación de 30'}`);
    txtD(gT, (eb[0] + eb[2]) / 2, 480, 'búnker abajo', 'tr-sub', 17);   // bajo las cotas que cruzan a la altura y = 4,80, a distancia fija en pantalla
    txtD(gT, (eb[0] + eb[2]) / 2, eb[1], 'ESTUDIO', 'tr-lbl', -48); txtD(gT, (eb[0] + eb[2]) / 2, eb[1], 'por construir', 'tr-sub', -31); txtD(gT, (eb[0] + eb[2]) / 2, eb[1], `${fmt(es.ancho)} × ${fmt(es.largo)}`, 'tr-sub', -14);   // apilado sobre el estudio

    // ---- la casa: su huella tapa el pasto (el plano de la casa se dibuja encima, en sus propias capas) ----
    if (o.casa && o.casa.length) { el('polygon', { points: P(o.casa), class: 'tr-casa' }, gB); }

    // ---- cotas entre edificios y a los deslindes: distancias reales entre caras, calculadas de los mismos polígonos ----
    const cota = (x1, y1, x2, y2, t, lado, horiz) => {   // horiz: texto sin girar, al lado de la línea (para cotas verticales cortas)
      const gg = el('g', { class: 'tr-cota' }, gK), dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy) || 1, nx = -dy / L, ny = dx / L, tk = 40;
      el('line', { x1, y1, x2, y2 }, gg); [[x1, y1], [x2, y2]].forEach(([x, y]) => el('line', { x1: x + nx * tk, y1: y + ny * tk, x2: x - nx * tk, y2: y - ny * tk }, gg));
      let r = Math.atan2(dy, dx) * 180 / Math.PI; if (r > 90 || r < -90) r += 180;
      const cx = (x1 + x2) / 2, cy = (y1 + y2) / 2;
      let ux = nx, uy = ny; if (Math.abs(uy) > Math.abs(ux) ? uy > 0 : ux > 0) { ux = -ux; uy = -uy; }   // el texto va arriba (o a la izquierda) de su línea
      // horiz: a la derecha de la línea (o a la izquierda con lado < 0); text-anchor en style, porque el de la clase le ganaba al atributo y el texto quedaba encima de su línea
      if (horiz) { if (lado < 0) txt(gg, Math.min(x1, x2) - 60, cy, t, 'tr-cota-t', { style: 'text-anchor:end' }); else txt(gg, Math.max(x1, x2) + 60, cy, t, 'tr-cota-t', { style: 'text-anchor:start' }); } else txtR(gg, cx, cy, t, 'tr-cota-t', r, ux * (lado === undefined ? 1 : lado), uy * (lado === undefined ? 1 : lado), 8);
    };
    const casa = o.casa || [];
    const xs = (poly, y) => cortesY(poly, y), ys = (poly, x) => cortesX(poly, x);
    // casa → estudio (a la altura de la cocina, y = 900) y estudio → deslinde oriente
    if (casa.length) { const cE = xs(casa, 480); const xc = cE[cE.length - 1], xe = eb[0]; cota(xc, 480, xe, 480, m(xe - xc)); }
    { const lE = xs(lot, 480); const xl = lE[lE.length - 1]; cota(eb[2], 480, xl, 480, m(xl - eb[2]), 1); }   // texto sobre la línea: al lado se salía de la pantalla del teléfono
    // gimnasio → deslinde norte y poniente
    { const gb = bbox(gi.planta), xm = (gb[0] + gb[2]) / 2, ln = ys(lot, xm)[0]; cota(xm, ln, xm, gb[1], m(gb[1] - ln), 1, true);   // texto horizontal: girado, con 14 px, tocaba el rótulo del deslinde del fondo
      const ym = (gb[1] + gb[3]) / 2, lw = xs(lot, ym)[0]; cota(lw, ym, gb[0], ym, m(gb[0] - lw), -1); }
    // casa → deslinde poniente (y = 1500) y casa → cierro sur (x = 1000)
    if (casa.length) {
      const cw = xs(casa, 1660)[0], lw = xs(lot, 1660)[0]; cota(lw, 1660, cw, 1660, m(cw - lw));   // en y = 16,60 la cara poniente es la de verdad (x = −0,3), no un retranqueo
      // cara más al sur de la casa (la caja de la escalera): se busca el x donde la casa llega más abajo
      let xsur = 1000, ysur = -1e9; for (let x = 880; x <= 1120; x += 10) { const cs = ys(casa, x); if (cs.length && cs[cs.length - 1] > ysur) { ysur = cs[cs.length - 1]; xsur = x; } }
      const yCierro = x => { const cie = D.cierros[0].pts.concat(D.cierros[1].pts); let yc = null; for (let i = 0; i + 1 < cie.length; i++) { const a = cie[i], b = cie[i + 1]; if ((a[0] <= x && b[0] > x) || (b[0] <= x && a[0] > x)) yc = a[1] + (x - a[0]) * (b[1] - a[1]) / (b[0] - a[0]); } return yc; };
      const yc = yCierro(xsur); if (yc !== null) cota(xsur, ysur, xsur, yc - 35, m(yc - 35 - ysur), 0, true);   // texto horizontal: girado chocaba con el rótulo del acceso
      const xe2 = (eb[0] + eb[2]) / 2, yce = yCierro(xe2); if (yce !== null) cota(xe2, eb[3], xe2, yce - 35, m(yce - 35 - eb[3]), -1, true);   // estudio → cierro sur (amarre norte-sur para replantear)
    }
    // cierro sur → deslinde sur (servidumbre), en x = 300
    { const cie = D.cierros[0].pts; let yc = null; for (let i = 0; i + 1 < cie.length; i++) { const a = cie[i], b = cie[i + 1]; if ((a[0] <= 300 && b[0] > 300) || (b[0] <= 300 && a[0] > 300)) yc = a[1] + (300 - a[0]) * (b[1] - a[1]) / (b[0] - a[0]); }
      const ls = ys(lot, 300); const yl = ls[ls.length - 1]; if (yc !== null) cota(300, yc + 35, 300, yl, m(yl - yc - 35), -1, true); }   // texto horizontal: girado chocaba con el rótulo del deslinde sur

    const subs = gT.querySelectorAll('.tr-sub'), chicos = gT.querySelectorAll('.tr-chico'), recs = gT.querySelectorAll('.tr-rec'), girados = g.querySelectorAll('text[data-r]'), corridos = g.querySelectorAll('text[data-dy]');
    return {
      vertices: verts, lote: loteBox,
      aplicar(k) {
        // con letra de 14 px (antes 10) los rótulos aparecen un poco más cerca que antes, para que no se monten con el lote entero en pantallas chicas
        subs.forEach(t => { t.style.display = k >= 0.048 ? '' : 'none'; }); chicos.forEach(t => { t.style.display = k >= 0.14 ? '' : 'none'; }); recs.forEach(t => { t.style.display = k >= 0.3 ? '' : 'none'; });
        corridos.forEach(t => t.setAttribute('transform', `translate(0 ${(+t.dataset.dy) / k})`));
        girados.forEach(t => { const d = t.dataset, off = (+d.off) / k; t.setAttribute('transform', `translate(${(+d.nx) * off} ${(+d.ny) * off}) rotate(${d.r} ${d.cx} ${d.cy})`); });
      },
    };
  }
  window.Terreno2D = { crear };
})();
