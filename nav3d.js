// Navegación 3D común a las vistas del sitio (Three.js r128 y OrbitControls de examples/js, globales).
//
//   <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
//   <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
//   <script src="nav3d.js"></script>
//
//   const nav = Nav3D.conectar({ camera, controls, dom: renderer.domElement,
//     objetivos: () => [grupoVisible, ...], planoY: 0, inicio: () => [pos, target],
//     contenedor: visor, pedir: () => { sucio = true; }, distMin: 0.2, distMax: 60 });
//
//   y en el bucle de la página, ANTES de controls.update():
//     if (nav.actualizar(t)) sucio = true;      // o simplemente nav.actualizar(t) si renderiza siempre
//
// Qué cambia respecto de OrbitControls solo:
//   - la rueda, el pellizco del trackpad y el de dos dedos acercan HACIA LO QUE ESTÁ BAJO EL CURSOR;
//   - doble clic / doble toque sobre el modelo vuela hasta ese punto; en el vacío, a la vista de inicio;
//   - al girar o desplazar, el centro de giro pasa a ser lo que está bajo el puntero (sin saltos);
//   - teclado (+ − 0 P con el puntero encima; flechas solo con el foco en el modelo) y una barra de
//     botones: acercar, alejar, inicio, planta, 3D.
//   Tras un doble clic / doble toque, el lienzo emite 'nav3d-doble' (detail.punto o null).
(function () {
  'use strict';
  if (window.Nav3D) return;

  const AYUDA = 'Arrastrar: girar · Rueda o pellizco: acercar donde apuntas · Doble clic: acercarse ahí · Clic derecho o dos dedos: desplazar';

  const ZPASO = Math.log(1.5);      // + y −: 1,5 veces más cerca o más lejos
  const TAU_ZOOM = 75;              // ms: inercia corta de la rueda y de los botones
  const TAU_PAN = 70;               // ms: inercia de las flechas
  const EPS_PLANTA = 1e-3;          // rad: la planta queda casi vertical para que el norte (-Z) quede arriba
  const UMBRAL_PLANTA = 0.035;      // rad (2°): se considera planta
  const DOBLE_MS = 350, DOBLE_PX = 30, TOQUE_PX = 10;

  const ICONOS = {
    mas: '<path d="M10 4.5v11M4.5 10h11"/>',
    menos: '<path d="M4.5 10h11"/>',
    inicio: '<path d="M3.5 9.6 10 4l6.5 5.6"/><path d="M5.5 8.2V16h9V8.2"/><path d="M8.6 16v-4.2h2.8V16"/>',
    planta: '<rect x="3" y="3" width="14" height="14" rx="1.5"/><path d="M3 10h6M9 10v7"/>',
    tresd: '<path d="M10 2.5 17 6.5v7L10 17.5 3 13.5v-7z"/><path d="M3 6.5 10 10.5l7-4M10 10.5v7"/>',
  };

  const CSS = `
.nav3d-barra{position:absolute;z-index:4;display:flex;align-items:center;gap:2px;padding:3px;background:var(--paper,#fff);color:var(--ink,#16181D);border:1px solid var(--line,#E3E6EB);border-radius:12px;box-shadow:var(--shadow,0 1px 2px rgba(16,18,22,.06),0 8px 22px rgba(16,18,22,.10));font:500 12px/1 var(--ui,system-ui,-apple-system,"Segoe UI",sans-serif);user-select:none;-webkit-user-select:none;touch-action:manipulation;pointer-events:auto}
.nav3d-barra.abajo{bottom:12px}.nav3d-barra.arriba{top:12px}.nav3d-barra.derecha{right:12px}.nav3d-barra.izquierda{left:12px}
.nav3d-barra.flujo{position:relative;top:auto;right:auto;bottom:auto;left:auto;align-self:flex-end}
.nav3d-barra.vertical{flex-direction:column}
.nav3d-b{flex:none;box-sizing:border-box;min-width:32px;height:32px;margin:0;padding:0 9px;display:inline-flex;align-items:center;justify-content:center;border:0;border-radius:9px;background:transparent;color:inherit;font:inherit;line-height:1;cursor:pointer;-webkit-tap-highlight-color:transparent}
.nav3d-b.ico{width:32px;padding:0}
.nav3d-b:hover{background:rgba(127,127,127,.14);background:color-mix(in srgb,var(--ink,#16181D) 8%,transparent)}
.nav3d-b:active{background:rgba(127,127,127,.24);background:color-mix(in srgb,var(--ink,#16181D) 15%,transparent)}
.nav3d-b[aria-pressed="true"]{background:var(--ink,#16181D);color:var(--paper,#fff)}
.nav3d-b:focus-visible{outline:2px solid var(--accent,#3D5A73);outline-offset:1px}
.nav3d-b svg{width:17px;height:17px;flex:none;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.nav3d-b.txt svg{display:none}
.nav3d-barra.vertical .nav3d-b.txt{width:32px;padding:0}
.nav3d-barra.vertical .nav3d-b.txt svg{display:block}
.nav3d-barra.vertical .nav3d-b.txt span{display:none}
.nav3d-sep{flex:none;width:1px;height:18px;margin:0 2px;background:var(--line,#E3E6EB)}
.nav3d-barra.vertical .nav3d-sep{width:18px;height:1px;margin:2px 0}
.nav3d-lienzo:focus{outline:none}
.nav3d-lienzo:focus-visible{outline:2px solid var(--accent,#3D5A73);outline-offset:-2px}
@media (max-width:639px){.nav3d-barra{gap:0;padding:2px;border-radius:11px}.nav3d-b.txt{padding:0 7px}.nav3d-sep{margin:0 1px}.nav3d-barra.vertical .nav3d-sep{margin:1px 0}}
@media (prefers-reduced-motion:no-preference){.nav3d-b{transition:background-color .12s,color .12s}}
`;

  function ponerEstilo() {
    if (document.getElementById('nav3d-estilo')) return;
    const st = document.createElement('style');
    st.id = 'nav3d-estilo';
    st.textContent = CSS;
    document.head.appendChild(st);
  }

  const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
  const suave = u => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2);   // ease in-out

  function conectar(o) {
    const T = window.THREE;
    o = o || {};
    const camera = o.camera, controls = o.controls, dom = o.dom || (controls && controls.domElement);
    if (!T || !camera || !controls || !dom) throw new Error('Nav3D: faltan THREE, camera, controls o dom');

    const pedir = typeof o.pedir === 'function' ? o.pedir : () => {};
    const objetivos = typeof o.objetivos === 'function' ? o.objetivos : () => [];
    const inicioFn = typeof o.inicio === 'function' ? o.inicio : null;
    const planoY = Number.isFinite(o.planoY) ? o.planoY : 0;
    const distMin = o.distMin > 0 ? o.distMin : (controls.minDistance > 0 ? controls.minDistance : 0.1);
    const distMax = o.distMax > distMin ? o.distMax
      : (Number.isFinite(controls.maxDistance) && controls.maxDistance > distMin ? controls.maxDistance : distMin * 2000);

    // ---------- OrbitControls: sin su zoom (lo hace este módulo), botón del medio = desplazar ----------
    const previo = {
      enableZoom: controls.enableZoom, minDistance: controls.minDistance, maxDistance: controls.maxDistance,
      middle: controls.mouseButtons ? controls.mouseButtons.MIDDLE : undefined,
    };
    controls.enableZoom = false;
    controls.minDistance = distMin;
    controls.maxDistance = distMax;
    if (controls.mouseButtons && T.MOUSE) controls.mouseButtons.MIDDLE = T.MOUSE.PAN;

    // el lienzo recibe foco (teclado); OrbitControls le hace focus() al hacer clic: sin desplazar la página
    const puso = { tab: !dom.hasAttribute('tabindex'), aria: !dom.hasAttribute('aria-label'), focus: false };
    if (puso.tab) dom.tabIndex = 0;
    if (puso.aria) dom.setAttribute('aria-label', 'Modelo 3D. Teclas: más y menos acercan, flechas desplazan, 0 vuelve a la vista de inicio, P muestra la planta.');
    dom.classList.add('nav3d-lienzo');
    if (typeof HTMLElement !== 'undefined' && !Object.prototype.hasOwnProperty.call(dom, 'focus')) {
      dom.focus = function (op) { HTMLElement.prototype.focus.call(this, Object.assign({ preventScroll: true }, op || {})); };
      puso.focus = true;
    }

    // ---------- objetos reutilizados (nada se crea por cuadro) ----------
    const ray = new T.Raycaster(), ndc = new T.Vector2();
    const plano = new T.Plane(new T.Vector3(0, 1, 0), -planoY);
    const vA = new T.Vector3(), vB = new T.Vector3(), vC = new T.Vector3(), dirV = new T.Vector3();
    const punto = new T.Vector3();     // resultado del último rayo
    const ancla = new T.Vector3();     // hacia dónde va el zoom en curso
    const panPend = new T.Vector3();
    const esfT = new T.Spherical();
    const mallas = [], pila = [];
    const vuelo = { activo: false, ini: 0, dur: 0, t0: new T.Vector3(), t1: new T.Vector3(), s0: new T.Spherical(), s1: new T.Spherical(), dTheta: 0 };
    let zPend = 0, tPrev = 0, encima = false, enGesto = false, gEsc = 1, tipoPuntero = 'mouse';
    const rueda = { x: -1e9, y: -1e9, t: 0 };
    const toques = { n: 0, d: 0, prof: 0, multi: false };
    const tap = { id: -1, x: 0, y: 0, t: 0, ultT: 0, ultX: 0, ultY: 0 };

    const mqMov = window.matchMedia ? matchMedia('(prefers-reduced-motion: reduce)') : null;
    const sinMov = () => !!(mqMov && mqMov.matches);
    const conTamano = () => dom.clientWidth > 1 && dom.clientHeight > 1;
    const aV3 = (v, dest) => (Array.isArray(v) ? dest.fromArray(v) : dest.copy(v));

    // ---------- rayos ----------
    function aNdc(x, y) {
      const r = dom.getBoundingClientRect();
      if (r.width < 2 || r.height < 2) return false;
      ndc.set((x - r.left) / r.width * 2 - 1, -((y - r.top) / r.height) * 2 + 1);
      return true;
    }
    function lanzar() { camera.updateMatrixWorld(); ray.setFromCamera(ndc, camera); }
    function visibleArriba(ob) { for (let p = ob; p; p = p.parent) if (!p.visible) return false; return true; }
    function materialVisible(m) {
      if (!m) return false;
      if (Array.isArray(m)) return m.some(materialVisible);
      return m.visible !== false && !(m.transparent && m.opacity < 0.05);
    }
    // solo mallas visibles (las líneas de borde y lo oculto no cuentan); sirve también para InstancedMesh
    function juntarMallas() {
      mallas.length = 0; pila.length = 0;
      const raices = objetivos() || [];
      for (let i = 0; i < raices.length; i++) if (raices[i] && visibleArriba(raices[i])) pila.push(raices[i]);
      while (pila.length) {
        const ob = pila.pop();
        if (!ob.visible) continue;
        if (ob.isMesh && materialVisible(ob.material)) mallas.push(ob);
        const ch = ob.children;
        for (let i = 0; i < ch.length; i++) pila.push(ch[i]);
      }
      return mallas;
    }
    // ¿el rayo actual toca el modelo? el punto queda en `punto`
    function tocarModelo() {
      const hits = ray.intersectObjects(juntarMallas(), false);
      mallas.length = 0;
      for (let i = 0; i < hits.length; i++) {
        if (hits[i].distance > camera.near) { punto.copy(hits[i].point); return true; }
      }
      return false;
    }
    // punto de respaldo sobre el rayo actual: el plano y = planoY si queda a una distancia razonable;
    // si no, el punto del rayo a la misma profundidad que el centro de giro (así el cursor igual queda fijo)
    function respaldo(dest) {
      const d = camera.position.distanceTo(controls.target);
      if (ray.ray.intersectPlane(plano, dest)) {
        const t = dest.distanceTo(ray.ray.origin);
        if (t > camera.near && t <= Math.min(distMax, Math.max(d * 3, distMin * 4))) return 'plano';
      }
      dirV.subVectors(controls.target, camera.position).normalize();
      const c = ray.ray.direction.dot(dirV);
      if (d > 0 && c > 0.05) { ray.ray.at(d / c, dest); return 'profundidad'; }
      dest.copy(controls.target);
      return 'centro';
    }
    // mueve el centro de giro sobre su propio rayo hasta la profundidad de p: la imagen no cambia
    function profundizar(p) {
      dirV.subVectors(controls.target, camera.position);
      const d = dirV.length();
      if (!(d > 1e-9)) return;
      dirV.divideScalar(d);
      const z = vA.subVectors(p, camera.position).dot(dirV);
      if (!(z > 0)) return;
      controls.target.copy(camera.position).addScaledVector(dirV, clamp(z, distMin, distMax));
    }

    // ---------- zoom hacia un punto: cámara y centro de giro se acercan juntos a p ----------
    function zoomHacia(p, k) {
      const d = camera.position.distanceTo(controls.target);
      if (!(d > 0) || !(k > 0)) return 1;
      if (k < 1) k = Math.max(k, Math.min(1, distMin / d));
      else k = Math.min(k, Math.max(1, distMax / d));
      if (Math.abs(k - 1) < 1e-7) return 1;
      camera.position.sub(p).multiplyScalar(k).add(p);
      controls.target.sub(p).multiplyScalar(k).add(p);
      return k;
    }
    function aplicarZoom(frac) {
      let paso = zPend * frac;
      zPend -= paso;
      if (Math.abs(zPend) < 1e-4) { paso += zPend; zPend = 0; }
      const pedido = Math.exp(paso), hecho = zoomHacia(ancla, pedido);
      if (Math.abs(hecho - pedido) > 1e-9) zPend = 0;      // tope de distancia: no acumular
      return hecho !== 1;
    }
    function aplicarPan(frac) {
      vB.copy(panPend).multiplyScalar(frac);
      panPend.sub(vB);
      if (panPend.lengthSq() < 1e-12) { vB.add(panPend); panPend.set(0, 0, 0); }
      camera.position.add(vB); controls.target.add(vB);
      return true;
    }
    function sumarZoom(z) {
      zPend = clamp(zPend + z, -3, 3);
      if (sinMov()) aplicarZoom(1);
      pedir();
    }
    // + / −: hacia lo que está al centro de la vista (el rayo que pasa por el centro de giro)
    function zoomCentro(z) {
      if (!conTamano()) return;
      vuelo.activo = false;
      camera.updateMatrixWorld();
      vA.copy(controls.target).project(camera);
      if (Math.abs(vA.x) <= 1 && Math.abs(vA.y) <= 1 && vA.z < 1) ndc.set(vA.x, vA.y); else ndc.set(0, 0);
      lanzar();
      if (tocarModelo()) profundizar(punto);
      ancla.copy(controls.target);
      sumarZoom(z);
    }
    function desplazar(dx, dy, grande) {
      if (!conTamano()) return;
      vuelo.activo = false;
      const d = camera.position.distanceTo(controls.target);
      const paso = 2 * d * Math.tan((camera.fov || 50) * Math.PI / 360) * (grande ? 0.3 : 0.1);
      camera.updateMatrixWorld();
      vA.setFromMatrixColumn(camera.matrixWorld, 0).multiplyScalar(dx * paso);
      vB.setFromMatrixColumn(camera.matrixWorld, 1).multiplyScalar(dy * paso);
      panPend.add(vA).add(vB);
      if (sinMov()) aplicarPan(1);
      pedir();
    }

    // ---------- vuelos: el centro de giro va en línea recta y la cámara gira a su alrededor ----------
    function irA(pos, target, ms) {
      if (!pos || !target) return;
      zPend = 0; panPend.set(0, 0, 0); rueda.t = 0;
      const dur = ms == null ? 650 : +ms;
      aV3(target, vuelo.t1);
      aV3(pos, vC);
      if (!(dur > 0) || sinMov()) {
        vuelo.activo = false;
        camera.position.copy(vC); controls.target.copy(vuelo.t1);
        pedir();
        return;
      }
      vuelo.t0.copy(controls.target);
      vuelo.s0.setFromVector3(vA.subVectors(camera.position, controls.target));
      vuelo.s1.setFromVector3(vA.subVectors(vC, vuelo.t1));
      let dt = vuelo.s1.theta - vuelo.s0.theta;
      dt = ((dt + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI;   // por el lado corto
      vuelo.dTheta = dt;
      vuelo.ini = performance.now(); vuelo.dur = dur; vuelo.activo = true;
      pedir();
    }
    function avanzarVuelo(ahora) {
      const u = clamp((ahora - vuelo.ini) / vuelo.dur, 0, 1), s = suave(u);
      const r0 = vuelo.s0.radius, r1 = vuelo.s1.radius;
      controls.target.lerpVectors(vuelo.t0, vuelo.t1, s);
      esfT.radius = r0 > 1e-6 && r1 > 1e-6 ? r0 * Math.pow(r1 / r0, s) : r0 + (r1 - r0) * s;
      esfT.phi = vuelo.s0.phi + (vuelo.s1.phi - vuelo.s0.phi) * s;
      esfT.theta = vuelo.s0.theta + vuelo.dTheta * s;
      camera.position.setFromSpherical(esfT).add(controls.target);
      if (u >= 1) vuelo.activo = false;
    }
    function saltar() {
      if (vuelo.activo) { vuelo.ini = -Infinity; avanzarVuelo(0); }
      if (zPend) aplicarZoom(1);
      if (panPend.lengthSq()) aplicarPan(1);
      pedir();
    }
    function cancelar() { vuelo.activo = false; zPend = 0; panPend.set(0, 0, 0); rueda.t = 0; }

    // acercarse a un punto: queda como centro de giro, misma dirección de vista, a 40 % de la distancia
    function enfocar(p) {
      if (!p) return;
      aV3(p, vC);
      dirV.subVectors(controls.target, camera.position);
      if (dirV.lengthSq() < 1e-12) return;
      dirV.normalize();
      const dp = camera.position.distanceTo(vC);
      const dist = clamp(Math.max(dp * 0.4, Math.min(dp, distMin * 2)), distMin, distMax);
      vB.copy(vC).addScaledVector(dirV, -dist);
      irA(vB, vC.clone(), 700);
    }
    function vistaInicio() {
      const v = inicioFn && inicioFn();
      if (v && v[0] && v[1]) irA(v[0], v[1], 750);
    }
    function esPlanta() {
      vA.subVectors(camera.position, controls.target);
      const r = vA.length();
      return r > 0 && vA.y / r > Math.cos(UMBRAL_PLANTA);
    }
    const guardada = { hay: false, phi: 0, theta: 0 };
    function vistaPlanta() {
      vA.subVectors(camera.position, controls.target);
      const r = vA.length() || distMin * 4;
      if (!esPlanta()) { esfT.setFromVector3(vA); guardada.hay = true; guardada.phi = esfT.phi; guardada.theta = esfT.theta; }
      vB.set(0, Math.cos(EPS_PLANTA) * r, Math.sin(EPS_PLANTA) * r).add(controls.target);   // norte (-Z) arriba
      irA(vB, controls.target.clone(), 650);
    }
    function vista3D() {
      vA.subVectors(camera.position, controls.target);
      const r = vA.length() || distMin * 4;
      let phi = 0.95, theta = Math.PI / 4;
      if (esPlanta() && guardada.hay && guardada.phi > 0.2) { phi = guardada.phi; theta = guardada.theta; }
      else {
        const v = inicioFn && inicioFn();
        if (v && v[0] && v[1]) {
          aV3(v[0], vB); aV3(v[1], vC);
          esfT.setFromVector3(vB.sub(vC));
          if (esfT.phi > 0.2) { phi = esfT.phi; theta = esfT.theta; }
        }
      }
      esfT.set(r, phi, theta);
      vB.setFromSpherical(esfT).add(controls.target);
      irA(vB, controls.target.clone(), 650);
    }

    // ---------- doble clic / doble toque ----------
    function dobleEn(x, y) {
      if (!conTamano() || !aNdc(x, y)) return;
      lanzar();
      const toco = tocarModelo();
      if (toco) enfocar(punto); else vistaInicio();
      // aviso a la página (p. ej. para cerrar una ficha que queda fuera de lugar al volar la cámara)
      try { dom.dispatchEvent(new CustomEvent('nav3d-doble', { detail: { punto: toco ? punto.clone() : null } })); } catch (err) { /* navegador sin CustomEvent */ }
    }

    // ---------- eventos ----------
    function onWheel(e) {
      e.preventDefault();
      if (!conTamano()) return;
      if (enGesto && e.ctrlKey) return;                  // Safari ya lo maneja con gesture*
      let dy = e.deltaY;
      if (e.deltaMode === 1) dy *= 33; else if (e.deltaMode === 2) dy *= Math.max(400, dom.clientHeight);
      if (!dy) return;
      dy = clamp(dy, -300, 300);
      vuelo.activo = false;
      const ahora = performance.now();
      // el punto bajo el cursor se recalcula si el cursor se movió o pasó un rato (si no, sigue bajo el cursor)
      if (Math.abs(e.clientX - rueda.x) > 2 || Math.abs(e.clientY - rueda.y) > 2 || ahora - rueda.t > 160) {
        if (!aNdc(e.clientX, e.clientY)) return;
        lanzar();
        if (tocarModelo()) { ancla.copy(punto); profundizar(ancla); } else respaldo(ancla);
        rueda.x = e.clientX; rueda.y = e.clientY;
      }
      rueda.t = ahora;
      // pellizco del trackpad (llega como rueda con ctrl y deltas chicos): directo, más sensible.
      // Ctrl + rueda de un mouse trae deltas de ~100: va por el camino suave, sin saltos de 1,6x
      if (e.ctrlKey && Math.abs(dy) < 50) {
        zPend = 0;
        if (zoomHacia(ancla, Math.exp(clamp(dy * 0.01, -0.5, 0.5))) !== 1) pedir();
        return;
      }
      sumarZoom(dy * 0.0015);
    }

    function onPointerDown(e) {
      tipoPuntero = e.pointerType || 'mouse';
      encima = true;
      cancelar();
      if (!conTamano()) return;
      if (tipoPuntero === 'touch') {
        if (e.isPrimary) { tap.id = e.pointerId; tap.x = e.clientX; tap.y = e.clientY; tap.t = performance.now(); toques.multi = false; }
        else { toques.multi = true; return; }
      }
      if (tipoPuntero === 'mouse' && e.button > 2) return;
      // girar (o desplazar) en torno a lo que está bajo el puntero
      if (aNdc(e.clientX, e.clientY)) { lanzar(); if (tocarModelo()) profundizar(punto); }
    }
    function onPointerUp(e) {
      if (e.pointerType !== 'touch' || e.pointerId !== tap.id) return;
      tap.id = -1;
      const ahora = performance.now();
      if (toques.multi || ahora - tap.t > DOBLE_MS || Math.hypot(e.clientX - tap.x, e.clientY - tap.y) > TOQUE_PX) { tap.ultT = 0; return; }
      if (tap.ultT && ahora - tap.ultT < DOBLE_MS && Math.hypot(e.clientX - tap.ultX, e.clientY - tap.ultY) < DOBLE_PX) {
        tap.ultT = 0;
        dobleEn(e.clientX, e.clientY);
        return;
      }
      tap.ultT = ahora; tap.ultX = e.clientX; tap.ultY = e.clientY;
    }
    function onDblClick(e) {
      if (tipoPuntero === 'touch') return;                // el doble toque se detecta aparte
      e.preventDefault();
      dobleEn(e.clientX, e.clientY);
    }
    const onEnter = () => { encima = true; };
    const onLeave = () => { encima = false; };

    // pellizco de dos dedos: hacia el punto medio (el desplazamiento con dos dedos lo sigue haciendo OrbitControls)
    function distToques(t) { return Math.hypot(t[0].clientX - t[1].clientX, t[0].clientY - t[1].clientY); }
    function empezarPinza(t) {
      toques.d = distToques(t); toques.prof = 0;
      if (!aNdc((t[0].clientX + t[1].clientX) / 2, (t[0].clientY + t[1].clientY) / 2)) return;
      lanzar();
      if (tocarModelo()) { toques.prof = punto.distanceTo(ray.ray.origin); profundizar(punto); }
      else if (respaldo(vA) !== 'centro') toques.prof = vA.distanceTo(ray.ray.origin);
      else toques.prof = camera.position.distanceTo(controls.target);
    }
    function onTouchStart(e) {
      toques.n = e.touches.length;
      if (toques.n >= 2) { toques.multi = true; cancelar(); if (conTamano()) empezarPinza(e.touches); }
    }
    function onTouchMove(e) {
      if (e.touches.length < 2 || !toques.d || !toques.prof) return;
      const d = distToques(e.touches);
      if (d < 1) return;
      const k = toques.d / d;
      toques.d = d;
      if (!aNdc((e.touches[0].clientX + e.touches[1].clientX) / 2, (e.touches[0].clientY + e.touches[1].clientY) / 2)) return;
      lanzar();
      ray.ray.at(toques.prof, ancla);
      const hecho = zoomHacia(ancla, k);
      if (hecho !== 1) { toques.prof *= hecho; pedir(); }
    }
    function onTouchEnd(e) {
      toques.n = e.touches.length;
      if (toques.n >= 2) empezarPinza(e.touches); else toques.d = 0;
    }

    // Safari (macOS) entrega el pellizco del trackpad como gesture*, no como rueda con ctrl
    function onGestureStart(e) {
      e.preventDefault();
      if (toques.n > 0 || !conTamano()) return;
      enGesto = true; gEsc = 1; cancelar();
      if (aNdc(e.clientX, e.clientY)) { lanzar(); if (tocarModelo()) { ancla.copy(punto); profundizar(ancla); } else respaldo(ancla); }
      else ancla.copy(controls.target);
    }
    function onGestureChange(e) {
      e.preventDefault();
      if (toques.n > 0 || !enGesto || !(e.scale > 0)) return;
      const k = gEsc / e.scale;
      gEsc = e.scale;
      if (zoomHacia(ancla, k) !== 1) pedir();
    }
    function onGestureEnd(e) { e.preventDefault(); enGesto = false; }

    function onKey(e) {
      if (e.defaultPrevented || e.ctrlKey || e.metaKey || e.altKey || e.isComposing) return;
      const act = document.activeElement;
      const conFoco = act === dom || !!(barra && barra.contains(act));
      if (!(encima || conFoco)) return;
      const el = e.target;
      if (el && el !== dom && (el.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName))) return;
      if (act && act !== dom && (act.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(act.tagName))) return;
      // flechas e Inicio también desplazan la página (o el texto de al lado): solo con el foco en el
      // modelo o en su barra, no por tener el puntero encima
      if (!conFoco && (e.key === 'Home' || /^Arrow/.test(e.key))) return;
      if (!conTamano()) return;
      switch (e.key) {
        case '+': case '=': case 'Add': zoomCentro(-ZPASO); break;
        case '-': case '_': case 'Subtract': zoomCentro(ZPASO); break;
        case 'ArrowLeft': desplazar(-1, 0, e.shiftKey); break;
        case 'ArrowRight': desplazar(1, 0, e.shiftKey); break;
        case 'ArrowUp': desplazar(0, 1, e.shiftKey); break;
        case 'ArrowDown': desplazar(0, -1, e.shiftKey); break;
        case '0': case 'Home': vistaInicio(); break;
        case 'p': case 'P': vistaPlanta(); break;
        default: return;
      }
      e.preventDefault();
    }

    const pasivo = { passive: true };
    dom.addEventListener('wheel', onWheel, { passive: false });
    dom.addEventListener('pointerdown', onPointerDown);
    dom.addEventListener('pointerup', onPointerUp);
    dom.addEventListener('pointerenter', onEnter);
    dom.addEventListener('pointerleave', onLeave);
    dom.addEventListener('dblclick', onDblClick);
    dom.addEventListener('touchstart', onTouchStart, pasivo);
    dom.addEventListener('touchmove', onTouchMove, pasivo);
    dom.addEventListener('touchend', onTouchEnd, pasivo);
    dom.addEventListener('touchcancel', onTouchEnd, pasivo);
    dom.addEventListener('gesturestart', onGestureStart, { passive: false });
    dom.addEventListener('gesturechange', onGestureChange, { passive: false });
    dom.addEventListener('gestureend', onGestureEnd, { passive: false });
    window.addEventListener('keydown', onKey);

    // ---------- barra de botones ----------
    let barra = null, bPlanta = null, b3d = null, modoPlanta = null, mqV = null, aplicarV = null;
    if (o.contenedor) {
      ponerEstilo();
      barra = document.createElement('div');
      const pos = o.enFlujo ? ['flujo'] : [o.arriba ? 'arriba' : 'abajo', o.lado === 'izquierda' ? 'izquierda' : 'derecha'];
      barra.className = 'nav3d-barra ' + pos.join(' ');
      barra.setAttribute('role', 'toolbar');
      barra.setAttribute('aria-label', 'Navegación del modelo 3D');
      const svg = d => `<svg viewBox="0 0 20 20" aria-hidden="true" focusable="false">${d}</svg>`;
      const boton = (accion, nombre, ico, fn, texto) => {
        const b = document.createElement('button');
        b.type = 'button';
        b.className = 'nav3d-b ' + (texto ? 'txt' : 'ico');
        b.dataset.accion = accion;
        b.setAttribute('aria-label', nombre);
        b.title = nombre;
        b.innerHTML = svg(ico) + (texto ? `<span>${texto}</span>` : '');
        b.addEventListener('click', e => { e.preventDefault(); fn(); });
        barra.appendChild(b);
        return b;
      };
      const sep = () => { const s = document.createElement('span'); s.className = 'nav3d-sep'; s.setAttribute('aria-hidden', 'true'); barra.appendChild(s); };
      boton('acercar', 'Acercar', ICONOS.mas, () => zoomCentro(-ZPASO));
      boton('alejar', 'Alejar', ICONOS.menos, () => zoomCentro(ZPASO));
      sep();
      boton('inicio', 'Vista de inicio', ICONOS.inicio, vistaInicio);
      sep();
      bPlanta = boton('planta', 'Vista en planta', ICONOS.planta, vistaPlanta, 'Planta');
      b3d = boton('3d', 'Vista 3D', ICONOS.tresd, vista3D, '3D');
      if (o.vertical === true) barra.classList.add('vertical');
      else if (typeof o.vertical === 'string' && window.matchMedia) {
        mqV = matchMedia(o.vertical);
        aplicarV = () => barra.classList.toggle('vertical', mqV.matches);
        aplicarV();
        if (mqV.addEventListener) mqV.addEventListener('change', aplicarV); else mqV.addListener(aplicarV);
      }
      o.contenedor.appendChild(barra);
    }
    function marcarModo() {
      if (!barra) return;
      const p = esPlanta();
      if (p === modoPlanta) return;
      modoPlanta = p;
      bPlanta.setAttribute('aria-pressed', p ? 'true' : 'false');
      b3d.setAttribute('aria-pressed', p ? 'false' : 'true');
    }
    marcarModo();

    // ---------- por cuadro ----------
    function actualizar(ahora) {
      if (!Number.isFinite(ahora)) ahora = performance.now();
      const dt = tPrev ? clamp(ahora - tPrev, 0, 100) : 16;
      tPrev = ahora;
      let movio = false;
      if (vuelo.activo) { avanzarVuelo(ahora); movio = true; }
      if (zPend) movio = aplicarZoom(sinMov() ? 1 : 1 - Math.exp(-dt / TAU_ZOOM)) || movio;
      if (panPend.x || panPend.y || panPend.z) movio = aplicarPan(sinMov() ? 1 : 1 - Math.exp(-dt / TAU_PAN)) || movio;
      marcarModo();
      return movio;
    }
    function ocupado() { return vuelo.activo || zPend !== 0 || panPend.lengthSq() > 0; }

    function destruir() {
      dom.removeEventListener('wheel', onWheel, { passive: false });
      dom.removeEventListener('pointerdown', onPointerDown);
      dom.removeEventListener('pointerup', onPointerUp);
      dom.removeEventListener('pointerenter', onEnter);
      dom.removeEventListener('pointerleave', onLeave);
      dom.removeEventListener('dblclick', onDblClick);
      dom.removeEventListener('touchstart', onTouchStart, pasivo);
      dom.removeEventListener('touchmove', onTouchMove, pasivo);
      dom.removeEventListener('touchend', onTouchEnd, pasivo);
      dom.removeEventListener('touchcancel', onTouchEnd, pasivo);
      dom.removeEventListener('gesturestart', onGestureStart, { passive: false });
      dom.removeEventListener('gesturechange', onGestureChange, { passive: false });
      dom.removeEventListener('gestureend', onGestureEnd, { passive: false });
      window.removeEventListener('keydown', onKey);
      if (mqV && aplicarV) { if (mqV.removeEventListener) mqV.removeEventListener('change', aplicarV); else mqV.removeListener(aplicarV); }
      if (barra && barra.parentNode) barra.parentNode.removeChild(barra);
      barra = null;
      cancelar();
      controls.enableZoom = previo.enableZoom;
      controls.minDistance = previo.minDistance;
      controls.maxDistance = previo.maxDistance;
      if (controls.mouseButtons && previo.middle !== undefined) controls.mouseButtons.MIDDLE = previo.middle;
      if (puso.tab) dom.removeAttribute('tabindex');
      if (puso.aria) dom.removeAttribute('aria-label');
      if (puso.focus) delete dom.focus;
      dom.classList.remove('nav3d-lienzo');
    }

    return {
      actualizar, irA, enfocar, vistaInicio, vistaPlanta, vista3D, ocupado, destruir,
      saltar, cancelar,
      get barra() { return barra; },
    };
  }

  window.Nav3D = { conectar, ayuda: AYUDA, ayudaLineas: AYUDA.split(' · ') };
})();
