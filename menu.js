// Menú común a todas las vistas. Cada página lo carga dentro de su <header>:
//   <script src="menu.js" data-vista="plano"></script>
// y el menú se dibuja ahí mismo, antes del primer pintado (el script es síncrono).
// Para agregar una vista nueva basta con sumarla a VISTAS.
// Versión publicada: la escribe fuente/version.py antes de cada commit (V<n> = número de commits del proyecto).
window.PILAUCO_VERSION = { n: 'V128', fecha: '28-10-2026' };
(function () {
  // Tema claro / oscuro (Gabriel, 14-10-2026: "agrega una versión clara de toda la web"). Sin elección guardada se sigue al sistema;
  // el botón del menú guarda 'claro' u 'oscuro' en localStorage ('pilauco-tema') y recarga, para que el 3D (three.js) se arme con sus colores.
  // ?tema=claro|oscuro manda para esa carga (sirve para compartir un link claro). El CSS de cada página reacciona a <html data-theme="light|dark">.
  const raiz = document.documentElement;
  const temaElegido = () => { try { const q = new URLSearchParams(location.search).get('tema'); if (q === 'claro' || q === 'oscuro') return q; return localStorage.getItem('pilauco-tema'); } catch (e) { return null; } };
  const aplicarTema = t => { if (t === 'claro') raiz.dataset.theme = 'light'; else if (t === 'oscuro') raiz.dataset.theme = 'dark'; else delete raiz.dataset.theme; };
  aplicarTema(temaElegido());
  const esOscuro = () => raiz.dataset.theme === 'dark' || (raiz.dataset.theme !== 'light' && window.matchMedia('(prefers-color-scheme: dark)').matches);
  window.PILAUCO_TEMA = { esOscuro, elegido: temaElegido };
  const VISTAS = [
    { id: 'plano', href: 'index.html', t: 'Plano', d: 'Nivel 1 y nivel 2: recintos, medidas, herramienta de medir',
      ico: '<rect x="3" y="3" width="14" height="14" rx="1.5"/><path d="M3 10h6M9 10v7"/>' },
    { id: '3d', href: '3d.html', t: 'Vista 3D', d: 'Los dos niveles a su altura, techo y estructura de acero',
      ico: '<path d="M10 2.5 17 6.5v7L10 17.5 3 13.5v-7z"/><path d="M3 6.5 10 10.5l7-4M10 10.5v7"/>' },
    { id: 'losa', href: 'losa.html', t: 'Losa', d: 'Losa colaborante del entrepiso: marco C, placa, pernos, malla, hormigón, despiece y montaje',
      ico: '<path d="M2.5 12.5h15M2.5 15.5h15"/><path d="M3 12.5l2-3h2l2 3 2-3h2l2 3"/><path d="M5 9.5V7M15 9.5V7"/>' },
    { id: 'alzaprimas', href: 'alzaprimas.html', t: 'Alzaprimas', d: 'Alzaprimas bajo la losa: puntales metálicos arrendados con solera 2x4 doble; planta, alzado, corte, carga por puntal y pedido (borrador para el ingeniero)',
      ico: '<path d="M3 3.5h14"/><path d="M7 3.5v2h6v-2"/><path d="M10 5.5v6"/><path d="M8.5 11.5h3v5h-3z"/><path d="M7 11.5h6"/><path d="M6 16.5h8"/>' },
    { id: 'pernos', href: 'pernos.html', t: 'Pernos', d: 'Pernos Nelson: perforación, soldadura y cada caso de instalación en 2D y 3D, paso a paso',
      ico: '<path d="M8.5 5.5h3M10 5.5v9"/><path d="M6.5 3.5h7"/><path d="M3 16.5h14"/><circle cx="10" cy="15.5" r="2.5"/>' },
    { id: 'estudio', href: 'estudio.html', t: 'Estudio', d: 'Estudio con búnker: la estructura del ingeniero adaptada a la planta nueva, para su revisión',
      ico: '<path d="M3.5 16.5v-9l6.5-4 6.5 4v9"/><path d="M3.5 7.5l13 9M16.5 7.5l-13 9"/><path d="M3 16.5h14"/>' },
    { id: 'tablero', href: 'tablero.html', t: 'Tablero', d: 'Aro de básquetbol: piezas, fundación, armado paso a paso y 3D',
      ico: '<rect x="3" y="2.5" width="14" height="9" rx="1"/><rect x="7.5" y="5.5" width="5" height="4"/><path d="M6.5 13.5h7l-1.2 4h-4.6z"/>' },
    { id: 'escalera', href: 'escalera.html', t: 'Escalera', d: 'Escalera de obra de la bodega: dónde va, planta y corte, medidas y el fierro para comprar',
      ico: '<path d="M3 17h3v-3h3v-3h3V8h3V5h2"/><path d="M3 17h14"/>' },
  ];
  const yo = document.currentScript;
  const actual = yo.dataset.vista;

  const css = `
.menu{display:flex;align-items:center;gap:2px;align-self:center;flex:none;position:relative;margin-right:4px}
.menu .m-tabs{display:flex;gap:2px;border:1px solid var(--chrome-line);border-radius:999px;padding:2px}
.menu .m-tab{font:inherit;font-size:12.5px;font-weight:500;color:var(--chrome-muted);text-decoration:none;padding:4px 12px;border-radius:999px;white-space:nowrap;display:inline-flex;align-items:center;gap:6px;line-height:1.35;border:0;margin:0}
.menu .m-tab:hover{color:var(--chrome-ink)}
.menu .m-tab[aria-current="page"]{background:var(--chrome-ink);color:var(--chrome)}
.menu .m-tab svg{width:14px;height:14px;fill:none;stroke:currentColor;stroke-width:1.6;stroke-linejoin:round;stroke-linecap:round;flex:none}
.m-ver{font-size:10.5px;font-weight:600;letter-spacing:.06em;color:var(--chrome-muted);border:1px solid var(--chrome-line);border-radius:999px;padding:3px 8px;margin-left:6px;white-space:nowrap}
.m-ver:hover{color:var(--chrome-ink)}
.m-tema{display:inline-flex;align-items:center;justify-content:center;width:26px;height:26px;margin-left:6px;border:1px solid var(--chrome-line);border-radius:999px;background:transparent;color:var(--chrome-muted);cursor:pointer;padding:0}
.m-tema:hover{color:var(--chrome-ink);border-color:var(--chrome-muted)}
.m-tema svg{width:14px;height:14px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.menu .m-btn{display:none;font:inherit;font-size:12.5px;font-weight:500;color:var(--chrome-ink);background:transparent;border:1px solid var(--chrome-line);border-radius:999px;padding:4px 11px 4px 9px;cursor:pointer;align-items:center;gap:7px;line-height:1.35}
.menu .m-btn:hover{border-color:var(--chrome-muted)}
.menu .m-btn svg{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round}
.menu .m-btn .car{width:9px;height:9px;stroke-width:1.8;opacity:.7;transition:transform .15s}
.menu .m-btn[aria-expanded="true"] .car{transform:rotate(180deg)}
.menu .m-pop{position:absolute;top:calc(100% + 8px);left:0;z-index:50;min-width:270px;max-width:calc(100vw - 24px);background:var(--chrome);border:1px solid var(--chrome-line);border-radius:12px;padding:6px;box-shadow:0 14px 40px rgba(0,0,0,.35)}
.menu .m-pop[hidden]{display:none}
.menu .m-item{display:flex;gap:11px;align-items:flex-start;padding:9px 10px;border-radius:8px;text-decoration:none;color:var(--chrome-ink)}
.menu .m-item:hover,.menu .m-item:focus-visible{background:var(--chrome-hi);outline:none}
.menu .m-item svg{width:18px;height:18px;flex:none;margin-top:1px;fill:none;stroke:var(--chrome-muted);stroke-width:1.5;stroke-linejoin:round;stroke-linecap:round}
.menu .m-item b{display:block;font-weight:600;font-size:13px}
.menu .m-item span{display:block;color:var(--chrome-muted);font-size:11.5px;line-height:1.35;margin-top:1px}
.menu .m-item[aria-current="page"]{background:var(--chrome-hi)}
.menu .m-item[aria-current="page"] svg{stroke:var(--chrome-ink)}
.menu .m-tab:focus-visible,.menu .m-btn:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
@media (max-width:760px){.menu .m-tabs{display:none}.menu .m-btn{display:inline-flex}}
`;
  const st = document.createElement('style');
  st.textContent = css;
  document.head.appendChild(st);

  const svg = ico => `<svg viewBox="0 0 20 20" aria-hidden="true">${ico}</svg>`;
  const cur = VISTAS.find(v => v.id === actual) || VISTAS[0];
  const html = `<nav class="menu" aria-label="Vistas del proyecto">
  <div class="m-tabs">${VISTAS.map(v =>
    `<a class="m-tab" href="${v.href}"${v.id === actual ? ' aria-current="page"' : ''} title="${v.d}">${svg(v.ico)}${v.t}</a>`).join('')}</div>
  <button class="m-btn" type="button" aria-expanded="false" aria-haspopup="true">
    <svg viewBox="0 0 20 20" aria-hidden="true"><path d="M3.5 6h13M3.5 10h13M3.5 14h13"/></svg>${cur.t}
    <svg class="car" viewBox="0 0 10 10" aria-hidden="true"><path d="M2 3.5 5 6.5 8 3.5"/></svg>
  </button>
  <div class="m-pop" hidden>${VISTAS.map(v =>
    `<a class="m-item" href="${v.href}"${v.id === actual ? ' aria-current="page"' : ''}>${svg(v.ico)}<div><b>${v.t}</b><span>${v.d}</span></div></a>`).join('')}</div>
</nav><span class="m-ver" title="Versión publicada: número de commit y fecha">${window.PILAUCO_VERSION ? window.PILAUCO_VERSION.n : ''}</span><button class="m-tema" type="button" title="Cambiar a modo claro u oscuro" aria-label="Cambiar entre modo claro y oscuro"></button>`;
  yo.insertAdjacentHTML('afterend', html);
  const SOL = '<svg viewBox="0 0 20 20"><circle cx="10" cy="10" r="3.5"/><path d="M10 2.5v2M10 15.5v2M2.5 10h2M15.5 10h2M4.7 4.7l1.4 1.4M13.9 13.9l1.4 1.4M4.7 15.3l1.4-1.4M13.9 6.1l1.4-1.4"/></svg>';
  const LUNA = '<svg viewBox="0 0 20 20"><path d="M16 12.3A6.5 6.5 0 0 1 7.7 4a6.5 6.5 0 1 0 8.3 8.3z"/></svg>';
  const botTema = yo.parentElement.querySelector('.m-tema');
  if (botTema) {
    botTema.innerHTML = esOscuro() ? SOL : LUNA;   // muestra a lo que se cambia
    botTema.addEventListener('click', () => {
      const nuevo = esOscuro() ? 'claro' : 'oscuro';
      try { localStorage.setItem('pilauco-tema', nuevo); } catch (e) {}
      const u = new URL(location.href); u.searchParams.delete('tema'); location.replace(u.href);   // recarga: el 3D arma sus colores al cargar
    });
  }

  const nav = yo.nextElementSibling;
  const btn = nav.querySelector('.m-btn'), pop = nav.querySelector('.m-pop');
  const abrir = si => { pop.hidden = !si; btn.setAttribute('aria-expanded', si ? 'true' : 'false'); };
  btn.addEventListener('click', e => { e.stopPropagation(); abrir(pop.hidden); if (!pop.hidden) pop.querySelector('a').focus(); });
  document.addEventListener('click', e => { if (!nav.contains(e.target)) abrir(false); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !pop.hidden) { abrir(false); btn.focus(); } });
})();
