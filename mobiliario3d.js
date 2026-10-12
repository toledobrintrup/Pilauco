// Mobiliario del estudio en 3D (Three.js r128 como script global, sin módulos).
// Una pieza por elemento de DATA_ESTUDIO_EST.interior, construida según su 'tipo' y encajada en su
// rectángulo 'pts' (planta, en cm del marco de la app: X al oriente, Y al sur, Z arriba; Z = 0 es el
// piso del nivel 1 de la casa). Mundo de Three.js en metros: (x/100, z/100, y/100).
//
//   const mobiliario = Mobiliario3D.crear(DATA_ESTUDIO_EST, DATA_SITIO.estudio, { dark, ficha });
//   scene.add(mobiliario);
//
// Cómo se arma cada pieza: en un marco local centrado en su rectángulo, con el piso en y = 0, el ancho
// a lo largo de x y el FRENTE hacia +z (= sur). Después el grupo de la pieza se gira según 'mira':
// S → 0, N → π, E → π/2, O → −π/2 (mirar al este = el frente local +z cae en +X mundo). Cuando mira
// es E u O, el ancho local es la extensión en y del rectángulo y el fondo la extensión en x, así la
// pieza siempre cabe dentro de lo que dibuja la planta. 'alto' es el tope de la pieza sobre el piso.
// Lo que sobresale por diseño del 'alto' (monitores sobre la consola, la cafetera sobre la barra, el
// espejo del lavamanos) se anota en el constructor correspondiente.
//
// Toda malla lleva ficha (userData.sitio, igual que el resto de 3d.html) y userData.mueble = id, así el
// clic identifica la pieza. Pensado para correr en un iPhone: cilindros de 8–16 segmentos, geometrías
// y materiales compartidos, sin texturas externas (la cabina usa una CanvasTexture generada).
(function () {
  'use strict';
  if (window.Mobiliario3D) return;

  const ROT = { S: 0, N: Math.PI, E: Math.PI / 2, O: -Math.PI / 2 };
  const cm = v => v / 100;
  const fmt = v => (v / 100).toFixed(2).replace('.', ',');

  // ---------- paleta sobria, con variante clara y oscura ----------
  function paleta(dark) {
    return {
      acero: 0x1B1E24, nogal: dark ? 0x6B4A2E : 0x8B6A45, canto: dark ? 0x4A3220 : 0x5E4430,
      tela: dark ? 0x3A3D43 : 0x6E7279, cojin: dark ? 0x474B52 : 0x7E838B, telaPanel: dark ? 0x4F5560 : 0x7A8190,
      telaCabina: dark ? 0x50545C : 0x8A8F97, cunas: dark ? 0x44474E : 0x5A5E66,
      laminado: dark ? 0xD9D7D2 : 0xE8E6E1, metal: 0x9AA0A8, cromo: dark ? 0xC9CED4 : 0xD8DCE1,
      vidrio: 0x7FB4D8, pantalla: 0x0E1014, ceramica: dark ? 0xDCDBD6 : 0xF2F1EC, piedra: dark ? 0x2F3238 : 0x3A3D44,
      vino: dark ? 0x4F2531 : 0x6A3341, vinoBorde: dark ? 0x36191F : 0x4A2330,
      carton: dark ? 0xA88B64 : 0xC2A77F, plastico: dark ? 0x3B5F86 : 0x4A74A3,
      led: 0x58D68D, ampolleta: 0xFFE2A8, calido: 0xE8B978, espejo: dark ? 0xAFC3D1 : 0xC4D6E2,
    };
  }

  // textura de cuñas acústicas (interior de la cabina): pirámides insinuadas con cuatro tonos
  function texturaCunas(T, dark) {
    try {
      const cv = document.createElement('canvas'); cv.width = cv.height = 256;
      const ctx = cv.getContext('2d'), n = 8, s = 256 / n;
      const base = dark ? [58, 61, 68] : [86, 90, 98];
      const tono = k => `rgb(${base[0] + k},${base[1] + k},${base[2] + k})`;
      ctx.fillStyle = tono(0); ctx.fillRect(0, 0, 256, 256);
      for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
        const x = i * s, y = j * s, c = [x + s / 2, y + s / 2];
        // cuatro caras de cada pirámide: arriba clara, izquierda media, derecha oscura, abajo más oscura
        [[[x, y], [x + s, y], 18], [[x, y], [x, y + s], 6], [[x + s, y], [x + s, y + s], -10], [[x, y + s], [x + s, y + s], -20]].forEach(([a, b, k]) => {
          ctx.fillStyle = tono(k); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.lineTo(c[0], c[1]); ctx.closePath(); ctx.fill();
        });
      }
      const tex = new T.CanvasTexture(cv);
      tex.wrapS = tex.wrapT = T.RepeatWrapping; tex.repeat.set(4, 4);
      return tex;
    } catch (e) { return null; }
  }

  function crear(D, E, o) {
    const T = window.THREE; o = o || {};
    const dark = !!o.dark, P = paleta(dark);
    const ficha = typeof o.ficha === 'function' ? o.ficha
      : (mesh, titulo, sub) => { mesh.userData.sitio = '<b>' + titulo + '</b><br><span class="sub">' + sub + '</span>'; return mesh; };

    // ---------- materiales compartidos ----------
    const lam = (color, extra) => new T.MeshLambertMaterial(Object.assign({ color }, extra || {}));
    const phong = (color, brillo, extra) => new T.MeshPhongMaterial(Object.assign({ color, shininess: brillo, specular: 0x666666 }, extra || {}));
    const M = {
      acero: lam(P.acero), nogal: lam(P.nogal), canto: lam(P.canto), tela: lam(P.tela), cojin: lam(P.cojin),
      telaPanel: lam(P.telaPanel), telaCabina: lam(P.telaCabina), cunas: lam(P.cunas), laminado: lam(P.laminado),
      metal: phong(P.metal, 60), cromo: phong(P.cromo, 120, { specular: 0xffffff }), pantalla: phong(P.pantalla, 100),
      ceramica: phong(P.ceramica, 40), piedra: phong(P.piedra, 50), vino: lam(P.vino), vinoBorde: lam(P.vinoBorde),
      carton: lam(P.carton), plastico: lam(P.plastico),
      vidrio: phong(P.vidrio, 90, { transparent: true, opacity: 0.3, side: T.DoubleSide }),
      espejo: phong(P.espejo, 140, { specular: 0xffffff }),
      led: new T.MeshBasicMaterial({ color: P.led }), ampolleta: new T.MeshBasicMaterial({ color: P.ampolleta }),
      calido: new T.MeshBasicMaterial({ color: P.calido, side: T.BackSide }),
      antipop: lam(P.acero, { transparent: true, opacity: 0.7, side: T.DoubleSide }),
      bowl: lam(P.laminado, { side: T.BackSide }),
    };
    const tex = texturaCunas(T, dark);
    M.cunasTex = tex ? new T.MeshLambertMaterial({ color: 0xffffff, map: tex }) : M.cunas;

    // ---------- geometrías compartidas (caché por medidas en cm) ----------
    const cacheGeo = new Map();
    function cache(tipo, nums, mk) {
      const k = tipo + nums.map(n => Math.round(n * 10) / 10).join(',');
      let g = cacheGeo.get(k); if (!g) { g = mk(); cacheGeo.set(k, g); } return g;
    }
    const geo = {
      caja: (w, h, d) => cache('b', [w, h, d], () => new T.BoxGeometry(cm(w), cm(h), cm(d))),
      cil: (rt, rb, h, seg, abierto) => cache('c', [rt, rb, h, seg, abierto ? 1 : 0], () => new T.CylinderGeometry(cm(rt), cm(rb), cm(h), seg, 1, !!abierto)),
      esfera: (r, seg) => cache('s', [r, seg], () => new T.SphereGeometry(cm(r), seg, Math.max(6, Math.round(seg * 0.75)))),
      toro: (r, t, seg) => cache('t', [r, t, seg], () => new T.TorusGeometry(cm(r), cm(t), 6, seg)),
    };

    // ---------- primitivas en cm (y0 = base de la pieza) ----------
    const add = (g, m) => { g.add(m); return m; };
    // caja w × h × d con la base en y0 y el centro en (x, z)
    function caja(g, mat, w, h, d, x, y0, z) {
      const m = new T.Mesh(geo.caja(w, h, d), mat); m.position.set(cm(x), cm(y0 + h / 2), cm(z)); return add(g, m);
    }
    // cilindro vertical (o cono si rb ≠ r) con la base en y0
    function cil(g, mat, r, h, x, y0, z, seg, rb, abierto) {
      const m = new T.Mesh(geo.cil(r, rb == null ? r : rb, h, seg || 12, abierto), mat); m.position.set(cm(x), cm(y0 + h / 2), cm(z)); return add(g, m);
    }
    // disco o cilindro con el eje en z: la cara trasera en zCara, crece hacia +z
    function disco(g, mat, r, h, x, y, zCara, seg) {
      const m = new T.Mesh(geo.cil(r, r, h, seg || 12), mat); m.rotation.x = Math.PI / 2; m.position.set(cm(x), cm(y), cm(zCara + h / 2)); return add(g, m);
    }
    // cilindro con el eje en x: desde x0, largo L
    function barraX(g, mat, r, L, x0, y, z, seg) {
      const m = new T.Mesh(geo.cil(r, r, L, seg || 10), mat); m.rotation.z = Math.PI / 2; m.position.set(cm(x0 + L / 2), cm(y), cm(z)); return add(g, m);
    }
    // caja de sección grosor × grosor (o cilindro si r) entre dos puntos [x, y, z]
    function entre(g, mat, a, b, grosor, r) {
      const L = Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]); if (L < 0.1) return null;
      const m = new T.Mesh(r ? geo.cil(r, r, L, 8) : geo.caja(grosor, grosor, L), mat);
      const dir = new T.Vector3(b[0] - a[0], b[1] - a[1], b[2] - a[2]).normalize();
      m.quaternion.setFromUnitVectors(new T.Vector3(0, r ? 1 : 0, r ? 0 : 1), dir);
      m.position.set(cm((a[0] + b[0]) / 2), cm((a[1] + b[1]) / 2), cm((a[2] + b[2]) / 2)); return add(g, m);
    }
    function esfera(g, mat, r, x, y, z, seg) {
      const m = new T.Mesh(geo.esfera(r, seg || 8), mat); m.position.set(cm(x), cm(y), cm(z)); return add(g, m);
    }
    // aro horizontal (toro acostado) a la altura y
    function aro(g, mat, r, t, x, y, z, seg) {
      const m = new T.Mesh(geo.toro(r, t, seg || 16), mat); m.rotation.x = Math.PI / 2; m.position.set(cm(x), cm(y), cm(z)); return add(g, m);
    }
    // subgrupo con su propio marco (para girar un conjunto: brazos de la silla, monitores, taburete de la cabina)
    function sub(g, x, y, z, rotY) {
      const s = new T.Group(); s.position.set(cm(x), cm(y), cm(z)); if (rotY) s.rotation.y = rotY; g.add(s); return s;
    }

    // ---------- constructores por tipo: (g, p) con p = {w, d, alto, it, hCielo} en cm ----------
    // w = ancho local (a lo largo de x), d = fondo (z), frente en +z; el piso es y = 0.
    const C = {};

    // Parlante: pedestal (placa + columna) y caja de monitor con woofer y tweeter en el frente; tope de la caja en 'alto'.
    C.parlante = (g, p) => {
      const hc = Math.min(50, p.alto - 60), wc = Math.min(50, p.w - 10), dc = Math.min(45, p.d - 6), y0 = p.alto - hc;
      caja(g, M.acero, 40, 2, 40, 0, 0, 0);                           // placa base
      caja(g, M.acero, 8, y0 - 2, 8, 0, 2, 0);                         // columna
      caja(g, M.acero, 22, 1.5, 22, 0, y0 - 1.5, 0);                   // platina bajo la caja
      caja(g, M.acero, wc, hc, dc, 0, y0, 0);                          // caja del monitor
      const zf = dc / 2;
      caja(g, M.tela, wc - 4, hc - 4, 1, 0, y0 + 2, zf);               // frente (bafle) algo más claro
      disco(g, M.metal, 13.5, 1, 0, y0 + hc * 0.36, zf + 1, 16);       // aro del woofer
      disco(g, M.pantalla, 11.5, 1.4, 0, y0 + hc * 0.36, zf + 1.4, 16); // cono del woofer
      disco(g, M.metal, 5.5, 1, 0, y0 + hc * 0.8, zf + 1, 12);          // aro del tweeter
      disco(g, M.pantalla, 4, 1.4, 0, y0 + hc * 0.8, zf + 1.4, 12);     // domo
    };

    // Consola: cubierta de 4 sobre dos costados; el productor se sienta por -z (norte) y mira hacia +z ('mira'),
    // así que los dos monitores van en el borde lejano mirando hacia -z, el controlador MIDI en el borde cercano
    // y la interfaz de audio a la derecha. Los monitores suben hasta unos 0,50 sobre la cubierta (sobre 'alto').
    C.consola = (g, p) => {
      const h = p.alto, w = p.w, d = p.d;
      caja(g, M.nogal, w, 4, d, 0, h - 4, 0);                           // cubierta
      caja(g, M.acero, 3, h - 4, d - 6, -(w / 2 - 4), 0, 0);            // costado izquierdo
      caja(g, M.acero, 3, h - 4, d - 6, (w / 2 - 4), 0, 0);             // costado derecho
      caja(g, M.acero, w - 14, 28, 2, 0, h - 44, -(d / 2 - 10));        // travesaño trasero (rigidiza)
      // monitores de 27": 62 × 36 con pie, mirando al productor (-z) y angulados 11° hacia el centro:
      // el de la izquierda (s = −1) gira −0,19 rad, así su normal (−z local) se inclina hacia +x, al productor
      [-1, 1].forEach(s => {
        const m = sub(g, s * 34, h, d / 2 - 22, s * 0.19);
        caja(m, M.acero, 22, 1, 18, 0, 0, 0);                           // placa del pie
        caja(m, M.acero, 5, 14, 2, 0, 1, 3);                            // cuello
        caja(m, M.acero, 62, 36, 1.5, 0, 13, 0);                        // marco
        caja(m, M.pantalla, 59.5, 33.5, 0.4, 0, 14.25, -0.95);          // pantalla (cara hacia -z)
      });
      caja(g, M.acero, 50, 3, 20, 0, h, -(d / 2 - 14));                 // controlador MIDI: cuerpo
      caja(g, M.laminado, 46, 1, 11, 0, h + 3, -(d / 2 - 14) + 3);      // teclas
      caja(g, M.metal, 18, 5, 14, w / 2 - 30, h, d / 2 - 30);           // interfaz de audio
      caja(g, M.pantalla, 16, 2.5, 0.6, w / 2 - 30, h + 1.2, d / 2 - 30 - 7.3); // su frente (perillas)
    };

    // Silla de oficina: base de 5 brazos con ruedas, columna, asiento, respaldo alto hasta 'alto' y apoyabrazos.
    C.silla_oficina = (g, p) => {
      for (let k = 0; k < 5; k++) {
        const b = sub(g, 0, 0, 0, k * Math.PI * 2 / 5);
        caja(b, M.acero, 4, 3, 24, 0, 4, 12);                           // brazo (de 0 a 24 cm del centro)
        const r = new T.Mesh(geo.cil(2.5, 2.5, 2.5, 8), M.acero); r.rotation.z = Math.PI / 2; r.position.set(0, cm(2.5), cm(24)); b.add(r); // rueda
      }
      cil(g, M.acero, 3, 10, 0, 5, 0, 10);                              // base de la columna
      cil(g, M.metal, 2, 32, 0, 15, 0, 10);                             // columna (gas)
      caja(g, M.tela, 48, 7, 48, 0, 45, 0);                             // asiento
      const resp = caja(g, M.tela, 46, p.alto - 50, 6, 0, 50, -(p.d / 2 - 8));   // nace dentro del asiento (45–52)
      resp.rotation.x = -0.08;                                          // leve inclinación hacia atrás
      [-1, 1].forEach(s => { caja(g, M.acero, 2.5, 16, 4, s * 25, 52, -2); caja(g, M.acero, 5, 2.5, 25, s * 25, 68, -2); }); // apoyabrazos
    };

    // Rack de 19": gabinete de 60 × 60 × 'alto' (centrado en el rectángulo), sin puerta, con rieles y 6 equipos de 1U–2U.
    C.rack = (g, p) => {
      const w = Math.min(60, p.w), d = Math.min(60, p.d), h = p.alto;
      caja(g, M.acero, w, 4, d - 2, 0, 0, 0);                           // zócalo
      caja(g, M.acero, 2, h - 6, d - 2, -(w / 2 - 1), 4, 0);            // lateral
      caja(g, M.acero, 2, h - 6, d - 2, (w / 2 - 1), 4, 0);
      caja(g, M.acero, w, 2, d - 2, 0, h - 2, 0);                       // tapa
      caja(g, M.acero, w - 4, h - 6, 2, 0, 4, -(d / 2 - 2));            // fondo
      const zf = d / 2 - 8;                                             // plano de los frentes
      caja(g, M.metal, 2, h - 10, 2, -24.5, 6, zf - 1);                 // rieles
      caja(g, M.metal, 2, h - 10, 2, 24.5, 6, zf - 1);
      const U = 4.445, unidades = [2, 1, 1, 2, 1, 2]; let y = 8;
      unidades.forEach((u, i) => {
        const hu = u * U - 0.6, frente = i % 2 ? M.acero : M.metal;
        caja(g, M.acero, 44, hu, 30, 0, y, zf - 16);                    // cuerpo del equipo
        caja(g, frente, 48, hu, 0.8, 0, y, zf);                          // frente
        caja(g, M.led, 6, 0.5, 0.4, -17, y + hu / 2, zf + 1);             // línea de LEDs, por delante del frente (que llega a zf + 0,8)
        y += u * U + (i === 2 ? U : 0);                                 // una U libre a mitad del rack
      });
    };

    // Sofá: patas, base, apoyabrazos, respaldo hasta 'alto' y cojines (3 de asiento, 3 de respaldo); tela gris carbón.
    C.sofa = (g, p) => {
      const w = p.w, d = p.d, h = p.alto, ba = 15, n = 3;
      [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([sx, sz]) => cil(g, M.acero, 2.5, 8, sx * (w / 2 - 12), 0, sz * (d / 2 - 10), 8));
      caja(g, M.tela, w, 12, d, 0, 8, 0);                               // base
      caja(g, M.tela, ba, 50, d, -(w / 2 - ba / 2), 8, 0);              // apoyabrazos
      caja(g, M.tela, ba, 50, d, (w / 2 - ba / 2), 8, 0);
      caja(g, M.tela, w - 2 * ba, h - 20, 22, 0, 20, -(d / 2 - 11));    // respaldo
      const wc = (w - 2 * ba) / n - 3, dz = d - 26;
      for (let i = 0; i < n; i++) {
        const x = -(w - 2 * ba) / 2 + (i + 0.5) * (w - 2 * ba) / n;
        caja(g, M.cojin, wc, 14, dz, x, 20, -(d / 2) + 22 + dz / 2 + 1);  // cojín de asiento
        caja(g, M.cojin, wc, h - 20 - 14, 9, x, 34, -(d / 2 - 22 - 4.5)); // cojín de respaldo
      }
    };

    // Panel acústico: 1,20 de alto cuya cara superior queda en 'alto'; marco fino negro y tela al frente.
    C.panel_acustico = (g, p) => {
      const h = 120, y0 = p.alto - h, d = p.d;
      caja(g, M.acero, p.w, h, 2, 0, y0, -(d / 2 - 1.5));               // marco (fondo), 0,5 separado del muro para no parpadear con él
      caja(g, M.telaPanel, p.w - 4, h - 4, d - 2, 0, y0 + 2, 1);        // tela
    };

    // Alfombra: lámina de 1 cm en vino oscuro, con borde.
    C.alfombra = (g, p) => {
      caja(g, M.vinoBorde, p.w, 1, p.d, 0, 0, 0);
      caja(g, M.vino, p.w - 24, 1.2, p.d - 24, 0, 0, 0);
    };

    // Cabina (sala de grabación): tres muros acústicos de 10 (tela por fuera, cuñas por dentro), techo de 10,
    // frente vidriado con marco negro y puerta de vidrio de 0,80 al lado (+x); adentro un pie de micrófono
    // con micrófono de condensador y antipop, y un taburete. Tope del techo en 'alto'.
    C.cabina = (g, p) => {
      const w = p.w, d = p.d, e = 10, hm = p.alto - e;
      const mats = idx => { const a = [M.telaCabina, M.telaCabina, M.telaCabina, M.telaCabina, M.telaCabina, M.telaCabina]; a[idx] = M.cunasTex; return a; };
      // caras del BoxGeometry: 0 +x, 1 -x, 2 +y, 3 -y, 4 +z, 5 -z → la cara interior lleva las cuñas
      caja(g, mats(0), e, hm, d, -(w / 2 - e / 2), 0, 0);               // muro izquierdo (−x), de fondo a frente
      caja(g, mats(1), e, hm, d, (w / 2 - e / 2), 0, 0);                // muro derecho (+x)
      caja(g, mats(4), w - 2 * e, hm, e, 0, 0, -(d / 2 - e / 2));       // muro del fondo (−z)
      caja(g, mats(3), w, e, d, 0, hm, 0);                              // techo
      // frente vidriado en la banda z ∈ [d/2 − 10, d/2]: puerta 0,80 | montante | vidrio fijo | montante.
      // La puerta va en el lado −x local: mirando al norte eso es el extremo ORIENTE, lejos de la puerta de
      // entrada del estudio (que está en el muro poniente, justo al norte de la cabina).
      const zf = d / 2 - e / 2, xL = -w / 2 + e, xR = w / 2 - e, puerta = 80, hv = hm - 5;
      caja(g, M.acero, 5, hv, e, xL + puerta + 2.5, 0, zf);             // montante junto a la puerta
      caja(g, M.acero, 5, hv, e, xR - 2.5, 0, zf);                      // montante derecho
      caja(g, M.acero, xR - xL, 5, e, (xL + xR) / 2, hv, zf);           // dintel
      const xv0 = xL + puerta + 5, wv = (xR - 5) - xv0;
      caja(g, M.acero, wv, 5, e, xv0 + wv / 2, 0, zf);                  // zócalo bajo el vidrio fijo
      caja(g, M.vidrio, wv, hv - 5, 1, xv0 + wv / 2, 5, zf);             // vidrio fijo
      // puerta de vidrio 0,80: hoja de 2,05 con marco de 4 (bisagra en el muro) y manilla; sobre ella un paño fijo
      const xp = xL + puerta / 2, hp = 205;
      caja(g, M.acero, 4, hp, 4, xL + 2, 0, zf); caja(g, M.acero, 4, hp, 4, xL + puerta - 2, 0, zf);
      caja(g, M.acero, puerta - 8, 4, 4, xp, hp - 4, zf); caja(g, M.acero, puerta - 8, 4, 4, xp, 0, zf);
      caja(g, M.vidrio, puerta - 8, hp - 8, 1, xp, 4, zf);
      caja(g, M.vidrio, puerta, hv - hp, 1, xp, hp, zf);                // paño fijo sobre la puerta
      cil(g, M.metal, 1, 30, xL + puerta - 9, 95, d / 2 - 1.5, 8);      // manilla por fuera (dentro del rectángulo)
      // interior: pie de micrófono (base, poste, brazo, micrófono y antipop) y taburete mirando al micrófono
      const xm = -w / 6, zm = -d / 2 + e + 30;
      cil(g, M.acero, 14, 2, xm, 0, zm, 16);                            // base
      cil(g, M.metal, 1.3, 100, xm, 2, zm, 8);                          // poste
      entre(g, M.acero, [xm, 102, zm], [xm, 128, zm + 28], 2.2);        // brazo (jirafa)
      const mic = new T.Mesh(geo.cil(2.4, 2.4, 16, 12), M.metal); mic.rotation.x = Math.PI / 2 + 0.25;
      mic.position.set(cm(xm), cm(124), cm(zm + 34)); add(g, mic);     // micrófono de condensador, ligeramente inclinado
      const rej = new T.Mesh(geo.cil(2.7, 2.7, 6, 12), M.acero); rej.rotation.copy(mic.rotation);
      rej.position.set(cm(xm), cm(124 - 2.5), cm(zm + 34 + 9.7)); add(g, rej); // rejilla de la cápsula
      const pop = new T.Mesh(geo.cil(7.5, 7.5, 0.6, 16), M.antipop); pop.rotation.x = Math.PI / 2;
      pop.position.set(cm(xm), cm(120), cm(zm + 50)); add(g, pop);     // antipop
      C.taburete(sub(g, xm, 0, zm + 78, Math.PI), { w: 35, d: 35, alto: 75 });
    };

    // Barra: mostrador con frente de madera (abierto por detrás, con dos repisas y tazas para el barman),
    // zócalo retranqueado, cubierta de piedra oscura que sobresale 15 hacia el cliente (+z) y una máquina de
    // espresso (cuerpo + cilindro cromado) en un extremo, mirando al barman. Cubierta en 'alto'.
    C.barra = (g, p) => {
      const w = p.w, d = p.d, h = p.alto, vuelo = 15, dc = d - vuelo, zc = -vuelo / 2;   // cuerpo de fondo dc, centrado en zc
      caja(g, M.acero, w - 10, 8, dc - 10, 0, 0, zc);                   // zócalo retranqueado
      caja(g, M.nogal, w, h - 12, 3, 0, 8, zc + dc / 2 - 1.5);          // frente de madera
      caja(g, M.nogal, 3, h - 12, dc, -(w / 2 - 1.5), 8, zc);           // costados
      caja(g, M.nogal, 3, h - 12, dc, (w / 2 - 1.5), 8, zc);
      caja(g, M.nogal, 3, h - 12, dc - 3, 0, 8, zc - 1.5);              // división central
      caja(g, M.nogal, w - 6, 2, dc - 3, 0, 8, zc - 1.5);               // piso del mueble
      caja(g, M.nogal, w - 6, 2, dc - 3, 0, 8 + (h - 12) * 0.5, zc - 1.5); // repisa baja (lado del barman)
      caja(g, M.piedra, w, 4, d, 0, h - 4, 0);                          // cubierta con vuelo hacia el cliente
      for (let i = 0; i < 4; i++) cil(g, M.ceramica, 4, 8, -(w / 2) + 20 + i * 12, 8 + (h - 12) * 0.5 + 2, zc - 12, 8); // tazas en la repisa
      // máquina de espresso en el extremo +x, con el frente (grupos y vaporizador) hacia el barman (−z)
      const xe = w / 2 - 35, ze = zc - 2;
      caja(g, M.metal, 42, 36, 38, xe, h, ze);                          // cuerpo
      barraX(g, M.cromo, 7, 40, xe - 20, h + 36 + 6, ze, 14);           // cilindro cromado (caldera) sobre el cuerpo
      disco(g, M.cromo, 3.5, 7, xe - 10, h + 14, ze - 19 - 7, 10);      // grupos de café (salen hacia −z)
      disco(g, M.cromo, 3.5, 7, xe + 10, h + 14, ze - 19 - 7, 10);
      caja(g, M.acero, 12, 2, 2, xe - 10, h + 9, ze - 19 - 9);          // mangos de los portafiltros
      caja(g, M.acero, 12, 2, 2, xe + 10, h + 9, ze - 19 - 9);
      entre(g, M.cromo, [xe + 19, h + 30, ze - 16], [xe + 25, h + 8, ze - 28], 0, 0.8); // vaporizador
    };

    // Taburete: asiento redondo tapizado (tope en 'alto'), columna, base y aro reposapiés.
    C.taburete = (g, p) => {
      const r = Math.min(17, p.w / 2 - 0.5), h = p.alto;
      cil(g, M.acero, r, 2, 0, 0, 0, 16);                               // base
      cil(g, M.metal, 2.5, h - 10, 0, 2, 0, 10);                        // columna
      aro(g, M.acero, r - 3, 0.9, 0, 25, 0, 16);                        // aro reposapiés
      caja(g, M.acero, 2 * (r - 3), 1.2, 1.2, 0, 24.4, 0);              // cruceta que une el aro con la columna
      caja(g, M.acero, 1.2, 1.2, 2 * (r - 3), 0, 24.4, 0);
      cil(g, M.acero, 7, 1.5, 0, h - 9.5, 0, 12);                       // platina bajo el asiento
      cil(g, M.tela, r, 8, 0, h - 8, 0, 16);                            // asiento tapizado
    };

    // Mesa: cubierta de madera de 4 (con canto más oscuro) y 4 patas de acero negro.
    C.mesa = (g, p) => {
      const w = p.w, d = p.d, h = p.alto;
      caja(g, M.nogal, w - 1, 3, d - 1, 0, h - 3, 0);                   // cubierta
      caja(g, M.canto, w, 1.2, d, 0, h - 4, 0);                         // canto
      [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([sx, sz]) => caja(g, M.acero, 4, h - 4, 4, sx * (w / 2 - 8), 0, sz * (d / 2 - 8)));
    };

    // Silla: asiento de madera con bisel y respaldo levemente inclinado (tope en 'alto'); 4 patas finas de acero negro.
    C.silla = (g, p) => {
      const w = Math.min(42, p.w - 3), d = Math.min(42, p.d - 3), h = p.alto, ha = 44;
      caja(g, M.nogal, w, 3, d, 0, ha, 0);                              // asiento
      caja(g, M.canto, w - 3, 1, d - 3, 0, ha - 1, 0);                  // bisel
      const resp = caja(g, M.nogal, w, 22, 2, 0, h - 22, -(d / 2 - 1.5)); resp.rotation.x = -0.1;
      [-1, 1].forEach(s => { caja(g, M.acero, 2, h - 22 - ha - 1, 2, s * (w / 2 - 3), ha + 1, -(d / 2 - 2)); caja(g, M.acero, 2, ha, 2, s * (w / 2 - 3), 0, -(d / 2 - 3)); caja(g, M.acero, 2, ha, 2, s * (w / 2 - 3), 0, (d / 2 - 3)); });
    };

    // Lámpara colgante: roseta y cable fino desde el cielo (p.hCielo sobre el piso) hasta una pantalla cónica
    // negra con interior cálido y ampolleta; tope de la pantalla en 'alto'.
    C.lampara = (g, p) => {
      const h = p.alto, hc = p.hCielo, rp = Math.min(16, p.w / 2 - 0.5), hp = 22;
      cil(g, M.acero, 5, 2, 0, hc - 2, 0, 12);                          // roseta en el cielo
      cil(g, M.acero, 0.4, Math.max(1, hc - 2 - h), 0, h, 0, 6);        // cable
      cil(g, M.acero, 5, 1, 0, h - 1, 0, 12);                           // tapa de la pantalla
      cil(g, M.acero, 5, hp, 0, h - hp, 0, 16, rp, true);               // pantalla (cono abierto) por fuera
      cil(g, M.calido, 5, hp, 0, h - hp, 0, 16, rp, true);              // su interior cálido
      esfera(g, M.ampolleta, 3, 0, h - 13, 0, 8);                       // ampolleta
    };

    // Inodoro: taza ovalada (cilindro achatado), tapa y estanque contra el muro de atrás (−z); tope del estanque en 'alto'.
    C.wc = (g, p) => {
      const h = p.alto, d = p.d;
      const zt = d / 2 - 24, escala = 1.35;
      cil(g, M.ceramica, 10, 2, 0, 0, zt, 12);                           // pie
      const taza = cil(g, M.ceramica, 17, 36, 0, 2, zt, 16, 13); taza.scale.z = escala;
      const tapa = cil(g, M.laminado, 17.5, 3, 0, 38, zt, 16); tapa.scale.z = escala;
      caja(g, M.ceramica, 20, 10, 12, 0, 32, -(d / 2) + 20);            // unión taza-estanque
      caja(g, M.ceramica, 38, h - 41, 18, 0, 41, -(d / 2 - 9));         // estanque (tope en 'alto')
      cil(g, M.metal, 2.5, 0.8, 0, h - 0.8, -(d / 2 - 9), 10);          // botón, embutido en la tapa
    };

    // Lavamanos: mueble bajo de madera, cubierta clara con lavatorio sobrepuesto (sube 11 sobre 'alto'),
    // grifería y espejo en el muro de atrás (−z, el muro oriente cuando mira 'O'), de 1,05 a 1,75.
    C.lavamanos = (g, p) => {
      const w = p.w, d = p.d, h = p.alto, dm = d - 4;
      caja(g, M.acero, w - 8, 10, dm - 8, 0, 0, 0);                     // zócalo
      caja(g, M.nogal, w, h - 13, dm, 0, 10, 0);                        // mueble
      caja(g, M.canto, 0.6, h - 17, 0.6, 0, 12, dm / 2 + 0.2);          // junta de las dos puertas
      caja(g, M.metal, 8, 1, 1.5, -6, h - 20, dm / 2 + 0.75);           // tiradores
      caja(g, M.metal, 8, 1, 1.5, 6, h - 20, dm / 2 + 0.75);
      caja(g, M.laminado, w, 3, d, 0, h - 3, 0);                        // cubierta
      cil(g, M.ceramica, 16, 11, 0, h, 2, 16, 14.5, true);              // lavatorio sobrepuesto (abierto arriba, para ver el cuenco)
      aro(g, M.ceramica, 15, 1.1, 0, h + 11, 2, 16);                    // borde redondeado del lavatorio
      cil(g, M.bowl, 14, 9.5, 0, h + 1.5, 2, 16, 8, true);              // cuenco (se ve por dentro: BackSide)
      cil(g, M.laminado, 8, 1, 0, h + 1, 2, 12);                        // fondo del cuenco
      cil(g, M.metal, 2.2, 0.5, 0, h + 2, 2, 10);                       // desagüe
      cil(g, M.cromo, 1.3, 22, 0, h, -(d / 2 - 11), 8);                 // grifería: monomando
      const pico = new T.Mesh(geo.cil(1.1, 1.1, 14, 8), M.cromo); pico.rotation.x = Math.PI / 2;
      pico.position.set(0, cm(h + 20), cm(-(d / 2 - 11) + 7)); add(g, pico);
      caja(g, M.acero, w - 2, 72, 0.8, 0, 104, -(d / 2 - 0.9));         // marco del espejo (0,5 separado del muro: sin parpadeo)
      caja(g, M.espejo, w - 4, 70, 1, 0, 105, -(d / 2 - 1.8));          // espejo
    };

    // Cocina chica: mueble bajo con puertas, cubierta, lavaplatos de acero inoxidable con monomando y una repisa en el muro.
    C.cocina = (g, p) => {
      const w = p.w, d = p.d, h = p.alto, dm = d - 4;
      caja(g, M.acero, w - 8, 10, dm - 8, 0, 0, 0);                     // zócalo retranqueado
      caja(g, M.nogal, w, h - 13, dm, 0, 10, 0);                        // mueble con puertas
      const nP = Math.max(2, Math.round(w / 45));
      for (let k = 1; k < nP; k++) caja(g, M.canto, 0.6, h - 17, 0.6, -w / 2 + k * w / nP, 12, dm / 2 + 0.2);   // juntas de las puertas
      for (let k = 0; k < nP; k++) caja(g, M.metal, 8, 1, 1.5, -w / 2 + (k + 0.5) * w / nP, h - 20, dm / 2 + 0.75);   // tiradores
      caja(g, M.laminado, w, 3, d, 0, h - 3, 0);                        // cubierta
      const cw = Math.min(42, w - 16), cd = Math.min(36, d - 14);
      caja(g, M.metal, cw + 2, 1.2, cd + 2, 0, h - 0.6, 1);             // marco del lavaplatos (acero inoxidable)
      caja(g, M.acero, cw, 1, cd, 0, h - 0.4, 1);                       // cuba (se ve oscura por dentro)
      cil(g, M.metal, 2, 0.4, 0, h + 0.6, 1, 10);                       // desagüe
      cil(g, M.cromo, 1.3, 24, 0, h, -(d / 2 - 7), 8);                  // monomando
      const pico = new T.Mesh(geo.cil(1.1, 1.1, 16, 8), M.cromo); pico.rotation.x = Math.PI / 2;
      pico.position.set(0, cm(h + 22), cm(-(d / 2 - 7) + 8)); add(g, pico);
      caja(g, M.nogal, w - 6, 3, 22, 0, 150, -(d / 2 - 11.5));          // repisa en el muro, a 1,50
      caja(g, M.acero, w - 6, 2, 1, 0, 148, -(d / 2 - 1));              // soporte de la repisa
      [-w / 4, 0, w / 4].forEach(x => cil(g, M.ceramica, 4, 8, x, 153, -(d / 2 - 11.5), 10));   // tazas
    };

    // Refrigerador pequeño (bajo mesón): cuerpo blanco con puerta, manilla vertical y zócalo.
    C.refrigerador = (g, p) => {
      const w = p.w, d = p.d, h = p.alto;
      caja(g, M.acero, w - 8, 5, d - 10, 0, 0, 0);                      // zócalo
      caja(g, M.laminado, w - 2, h - 5, d - 4, 0, 5, 0);                // cuerpo
      caja(g, M.plastico, w - 6, h - 9, 1.5, 0, 7, d / 2 - 1.3);        // puerta
      caja(g, M.metal, 1.6, (h - 9) * 0.55, 2.2, w / 2 - 7, 7 + (h - 9) * 0.25, d / 2 + 0.4);   // manilla vertical
      caja(g, M.laminado, w, 2, d, 0, h - 2, 0);                        // tapa
    };

    // Minibar (frigobar): cuerpo negro con puerta de vidrio enmarcada, dos repisas que se ven por dentro y manilla.
    C.minibar = (g, p) => {
      const w = p.w, d = p.d, h = p.alto;
      caja(g, M.acero, w - 8, 4, d - 10, 0, 0, 0);                      // zócalo
      caja(g, M.acero, w - 2, h - 4, d - 4, 0, 4, 0);                   // cuerpo
      caja(g, M.laminado, w - 8, h - 12, d - 10, 0, 7, -1.5);           // interior iluminado (claro)
      [0.33, 0.66].forEach(f => caja(g, M.metal, w - 10, 0.8, d - 12, 0, 7 + (h - 12) * f, -1.5));   // repisas
      caja(g, M.vidrio, w - 8, h - 12, 0.6, 0, 7, d / 2 - 1.2);         // puerta de vidrio
      caja(g, M.acero, w - 4, 2, 1.2, 0, 5, d / 2 - 1);                 // marco de la puerta
      caja(g, M.acero, w - 4, 2, 1.2, 0, h - 5, d / 2 - 1);
      caja(g, M.acero, 2, h - 8, 1.2, -(w / 2 - 2.5), 5, d / 2 - 1);
      caja(g, M.acero, 2, h - 8, 1.2, (w / 2 - 2.5), 5, d / 2 - 1);
      caja(g, M.metal, 1.4, (h - 12) * 0.5, 2, w / 2 - 6, 7 + (h - 12) * 0.25, d / 2 + 0.4);   // manilla
    };

    // Estantería metálica: módulos de hasta 1,00 (4 parantes cada uno), 5 repisas y algunas cajas; tope en 'alto'.
    C.estante = (g, p) => {
      const w = p.w, d = p.d, h = p.alto, n = Math.max(1, Math.ceil(w / 100)), mod = w / n;
      const repisas = [4, (h - 4) * 0.25, (h - 4) * 0.5, (h - 4) * 0.75, h - 4].map(v => Math.round(v));
      for (let k = 0; k <= n; k++) { const x = -w / 2 + k * mod; caja(g, M.metal, 3, h, 3, x + (k === 0 ? 1.5 : k === n ? -1.5 : 0), 0, -(d / 2 - 1.5)); caja(g, M.metal, 3, h, 3, x + (k === 0 ? 1.5 : k === n ? -1.5 : 0), 0, (d / 2 - 1.5)); }
      for (let k = 0; k < n; k++) {
        const xc = -w / 2 + (k + 0.5) * mod;
        repisas.forEach(y => caja(g, M.metal, mod - 3.5, 2.5, d - 1, xc, y - 2.5, 0));
        // cajas: patrón fijo (sin azar) para que se vea igual en cada carga
        for (let s = 0; s < 4; s++) {
          const sel = (k * 3 + s * 5) % 7; if (sel >= 4) continue;
          const alta = sel % 2 === 0, wb = mod * 0.42, hb = alta ? 28 : 22, mat = sel === 3 ? M.plastico : M.carton;
          caja(g, mat, wb, hb, d - 10, xc + (sel % 2 ? 1 : -1) * mod * 0.2, repisas[s], 0);
        }
      }
    };

    // ---------- subtítulo de la ficha: medidas en metros con coma; por tipo cuando el rectángulo no describe la pieza ----------
    const SUB = {
      panel_acustico: p => `${fmt(p.w)} × 1,20 m · de ${fmt(p.alto - 120)} a ${fmt(p.alto)} m sobre el piso`,
      lampara: p => `pantalla ø ${fmt(2 * Math.min(16, p.w / 2 - 0.5))} m · cuelga del cielo (${fmt(p.hCielo)} m) hasta ${fmt(p.alto)} m sobre el piso`,
      alfombra: p => `${fmt(p.w)} × ${fmt(p.d)} m`,
      cocina: p => `${fmt(p.w)} × ${fmt(p.d)} m · cubierta a ${fmt(p.alto)} m · lavaplatos de 0,42 × 0,36 · repisa a 1,50`,
      refrigerador: p => `${fmt(p.w)} × ${fmt(p.d)} m · alto ${fmt(p.alto)} m · bajo mesón`,
      minibar: p => `frigobar de ${fmt(p.w)} × ${fmt(p.d)} m · alto ${fmt(p.alto)} m · puerta de vidrio`,
      rack: p => `gabinete de 19" de ${fmt(Math.min(60, p.w))} × ${fmt(Math.min(60, p.d))} m en un espacio de ${fmt(p.w)} × ${fmt(p.d)} m · alto ${fmt(p.alto)} m`,
    };
    const subGenerico = p => `${fmt(p.w)} × ${fmt(p.d)} m · alto ${fmt(p.alto)} m`;

    // ---------- armado: una pieza por elemento de D.interior ----------
    const cielo = E && E.cielo ? E.cielo : (D.cielo || { z_norte: 380, z_sur: 435.1, y_norte: 10.5, y_sur: 1585.5 });
    const zCielo = y => cielo.z_norte + (cielo.z_sur - cielo.z_norte) * (y - cielo.y_norte) / ((cielo.y_sur - cielo.y_norte) || 1);
    const zPiso = D.z_piso != null ? D.z_piso : (E && E.z_piso != null ? E.z_piso : 0);
    const grupo = new T.Group(); grupo.name = 'mobiliario';
    const omitidos = [];
    (D.interior || []).forEach(it => {
      const build = C[it.tipo];
      if (!build || !it.pts || it.pts.length < 3) { omitidos.push(it.id); return; }
      const xs = it.pts.map(q => q[0]), ys = it.pts.map(q => q[1]);
      const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
      const ex = x1 - x0, ey = y1 - y0, lateral = it.mira === 'E' || it.mira === 'O';
      const p = { w: lateral ? ey : ex, d: lateral ? ex : ey, alto: it.alto || 75, it, hCielo: zCielo((y0 + y1) / 2) - zPiso };
      const g = new T.Group(); g.name = it.id; g.userData.mueble = it.id;
      build(g, p);
      const sub2 = `${(SUB[it.tipo] || subGenerico)(p)}${it.nota ? ' · ' + it.nota : ''} · idea para conversar`;
      g.traverse(ob => { if (ob.isMesh) { ficha(ob, it.nombre || it.id, sub2); ob.userData.mueble = it.id; } });
      g.position.set(cm((x0 + x1) / 2), cm(zPiso), cm((y0 + y1) / 2));
      g.rotation.y = ROT[it.mira] || 0;
      grupo.add(g);
    });
    grupo.userData.omitidos = omitidos;   // ids sin constructor (para que la página lo pueda avisar)
    return grupo;
  }

  window.Mobiliario3D = {
    crear,
    TIPOS: ['parlante', 'consola', 'silla_oficina', 'rack', 'sofa', 'panel_acustico', 'alfombra', 'cabina', 'barra', 'taburete', 'mesa', 'silla', 'lampara', 'wc', 'lavamanos', 'estante', 'cocina', 'refrigerador', 'minibar'],
  };
})();
