// Textos que se salen de la figura que rotulan (Gabriel, 24-10-2026: "arregla ese tipo de cosas", con "muro eje B e=30" más largo que el muro y "losa e=25" pisando el borde de la losa).
// Uso: como lint_textos_svg.js (webshot ... "$(sed 1,2d fuente/estudio/lint_textos_figuras.js)"). Por cada texto mira las figuras rellenas (rect, polygon, path, circle, ellipse) que toca: si una parte del texto queda dentro y otra fuera (una grilla de puntos sobre toda la caja del texto, hasta 1 px de su borde: si queda algo adentro y algo afuera, el texto toca o cruza el borde), el texto cruza el borde de esa figura.
(function(){
  const out = []; document.querySelectorAll("nav,header").forEach(n => n.style.display = "none");
  const relleno = el => { const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') return false; const f = cs.fill; return f && f !== 'none' && !/rgba\(.*,\s*0\)$/.test(f) && parseFloat(cs.fillOpacity || 1) > 0.05 && parseFloat(cs.opacity || 1) > 0.05; };
  let total = 0;
  document.querySelectorAll('svg').forEach((svg, fi) => {
    const R = svg.getBoundingClientRect(); if (R.width < 50 || R.height < 30) return;
    const id = svg.id || (svg.closest('section') || {}).id || ('svg' + fi);
    const visible = e => { for (let n = e; n && n !== svg; n = n.parentNode) if (getComputedStyle(n).display === 'none') return false; return true; };   // WebKit da cajas también a lo que está en una capa apagada
    const formas = [...svg.querySelectorAll('rect,polygon,path,circle,ellipse')].filter(e => e.getClientRects().length && relleno(e) && visible(e)).map(e => ({ e, b: e.getBoundingClientRect() }))
      .filter(f => f.b.width * f.b.height < 0.8 * R.width * R.height);   // sin el fondo del dibujo
    let n = 0;
    [...svg.querySelectorAll('text')].filter(t => t.textContent.trim() && t.getClientRects().length && visible(t)).forEach(t => {
      const b = t.getBoundingClientRect(); if (b.width < 2) return;
      // grilla de puntos sobre toda la caja del texto, hasta 1 px de sus bordes (cada ~6 px, mínimo 5 × 3): un texto que toca o pasa el borde de su figura deja puntos afuera
      const ins = 1, nx = Math.min(25, Math.max(5, Math.round(b.width / 6))), ny = Math.min(25, Math.max(3, Math.round(b.height / 6))), pts = [];
      for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) pts.push([b.left + ins + (b.width - 2 * ins) * i / (nx - 1), b.top + ins + (b.height - 2 * ins) * j / (ny - 1)]);
      // un rótulo con su propia placa de fondo (rect relleno que lo contiene y no es mucho más grande) tapa lo que cruza: se acepta
      // (también la placa de una cota: cubre todo el ancho del número y al menos el 70 % de su alto, que es donde están las cifras)
      if (formas.some(f => f.e.tagName === 'rect' && f.e.parentNode === t.parentNode && f.b.left <= b.left + 0.5 && f.b.right >= b.right - 0.5 && Math.min(f.b.bottom, b.bottom) - Math.max(f.b.top, b.top) >= 0.7 * b.height && f.b.width * f.b.height < 3.5 * b.width * b.height)) return;
      for (const f of formas) {
        if (f.b.right < b.left || f.b.left > b.right || f.b.bottom < b.top || f.b.top > b.bottom) continue;
        if (f.e.closest('text')) continue;
        const M = f.e.getScreenCTM(); if (!M) continue; const inv = M.inverse();
        let dentro = 0;
        for (const [x, y] of pts) { const p = new DOMPoint(x, y).matrixTransform(inv); try { if (f.e.isPointInFill(p)) dentro++; } catch (e) {} }
        const fr = dentro / pts.length;
        if (fr > 0.04 && fr < 0.96) { n++; if (n <= 40) out.push(`${id} SE SALE "${t.textContent.trim().slice(0, 34)}" de ${f.e.tagName}${f.e.id ? '#' + f.e.id : ''} (${Math.round(fr * 100)} % adentro)`); break; }
      }
    });
    total += n; if (n) out.push(`${id}: ${n} textos cruzan el borde de una figura`);
  });
  out.push(`TOTAL: ${total}`);
  return out.join('\n');
})()
