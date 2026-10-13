// Huevo de Pascua: un saiyajin sentado en una viga del perímetro, con el ki moviéndose. Se prende con 3d.html?goku=1.
// Figura armada con geometría (no es un modelo escaneado): cuerpo, gi naranjo, pelo en punta y un aura animada con
// capas aditivas y partículas que suben. window.Goku3D.crear(THREE, {pos: [x, y, z] (m, mundo), mira: 'S'|'N'|'E'|'O', dorado: bool})
// devuelve un THREE.Group con .animar(t) para llamarlo en cada cuadro.
(function () {
  if (window.Goku3D) return;
  const ROT = { S: 0, N: Math.PI, E: Math.PI / 2, O: -Math.PI / 2 };

  function texturaRadial(T, color, alfa) {
    const c = document.createElement('canvas'); c.width = c.height = 256;
    const x = c.getContext('2d');
    if (x && x.createRadialGradient) {
      const g = x.createRadialGradient(128, 128, 0, 128, 128, 128);
      g.addColorStop(0, `rgba(${color},${alfa})`); g.addColorStop(0.45, `rgba(${color},${alfa * 0.45})`); g.addColorStop(1, `rgba(${color},0)`);
      x.fillStyle = g; x.fillRect(0, 0, 256, 256);
    }
    const t = new T.CanvasTexture(c); return t;
  }

  function crear(T, o) {
    o = o || {};
    const g = new T.Group(); g.name = 'goku';
    const dorado = o.dorado !== false;
    const piel = new T.MeshLambertMaterial({ color: 0xF1C9A5 }), gi = new T.MeshLambertMaterial({ color: 0xF07A1C }), azul = new T.MeshLambertMaterial({ color: 0x1E3A8A });
    const pelo = new T.MeshLambertMaterial({ color: dorado ? 0xF5D033 : 0x15161A, emissive: dorado ? 0x8A6A00 : 0x000000 });
    const bota = new T.MeshLambertMaterial({ color: 0x1B2A6B }), blanco = new T.MeshLambertMaterial({ color: 0xF4F4F0 }), negro = new T.MeshLambertMaterial({ color: 0x111111 });
    const add = (geo, mat, x, y, z, rx, ry, rz) => { const m = new T.Mesh(geo, mat); m.position.set(x, y, z); if (rx) m.rotation.x = rx; if (ry) m.rotation.y = ry; if (rz) m.rotation.z = rz; g.add(m); return m; };
    // sentado en el borde: el origen del grupo es el punto de apoyo (el trasero sobre la viga); +z local = hacia adelante (las piernas cuelgan)
    const S = 1.0;   // escala (1,75 m de pie)
    // tronco (gi) con cuello azul y cinturón
    add(new T.BoxGeometry(0.46 * S, 0.60 * S, 0.30 * S), gi, 0, 0.30 * S, 0.02 * S);
    add(new T.BoxGeometry(0.24 * S, 0.16 * S, 0.31 * S), azul, 0, 0.56 * S, 0.02 * S);                 // camiseta azul asomando en el cuello
    add(new T.BoxGeometry(0.48 * S, 0.08 * S, 0.32 * S), azul, 0, 0.06 * S, 0.02 * S);                 // cinturón
    // cuello y cabeza
    add(new T.CylinderGeometry(0.07 * S, 0.08 * S, 0.10 * S, 12), piel, 0, 0.65 * S, 0.02 * S);
    const cab = add(new T.SphereGeometry(0.15 * S, 18, 14), piel, 0, 0.80 * S, 0.03 * S);
    add(new T.BoxGeometry(0.05 * S, 0.012 * S, 0.02 * S), negro, -0.055 * S, 0.84 * S, 0.17 * S, 0, 0, 0.35);   // cejas en V (ceño saiyajin)
    add(new T.BoxGeometry(0.05 * S, 0.012 * S, 0.02 * S), negro, 0.055 * S, 0.84 * S, 0.17 * S, 0, 0, -0.35);
    add(new T.SphereGeometry(0.018 * S, 8, 6), negro, -0.05 * S, 0.81 * S, 0.16 * S);                   // ojos
    add(new T.SphereGeometry(0.018 * S, 8, 6), negro, 0.05 * S, 0.81 * S, 0.16 * S);
    // pelo en punta: conos en abanico hacia arriba y atrás
    const puntas = [[0, 0.98, -0.02, 0.3, 0, 0], [-0.08, 0.96, -0.04, 0.5, 0, 0.45], [0.08, 0.96, -0.04, 0.5, 0, -0.45], [-0.13, 0.90, -0.06, 0.45, 0, 0.9], [0.13, 0.90, -0.06, 0.45, 0, -0.9],
                    [-0.05, 0.98, -0.10, 0.4, -0.55, 0.2], [0.05, 0.98, -0.10, 0.4, -0.55, -0.2], [0, 0.93, -0.14, 0.42, -1.0, 0], [-0.1, 0.9, -0.12, 0.36, -0.9, 0.5], [0.1, 0.9, -0.12, 0.36, -0.9, -0.5],
                    [-0.07, 0.86, -0.16, 0.3, -1.3, 0.3], [0.07, 0.86, -0.16, 0.3, -1.3, -0.3]];
    puntas.forEach(p => add(new T.ConeGeometry(0.055 * S, p[3] * S, 7), pelo, p[0] * S, p[1] * S, p[2] * S, p[4], 0, p[5]));
    add(new T.SphereGeometry(0.155 * S, 14, 10, 0, Math.PI * 2, 0, Math.PI * 0.55), pelo, 0, 0.81 * S, 0.02 * S);   // casquete de pelo
    // brazos: hombros, antebrazos apoyados en los muslos, muñequeras azules
    [-1, 1].forEach(s => {
      add(new T.SphereGeometry(0.09 * S, 10, 8), gi, s * 0.27 * S, 0.52 * S, 0.02 * S);
      add(new T.CylinderGeometry(0.06 * S, 0.055 * S, 0.30 * S, 10), gi, s * 0.30 * S, 0.37 * S, 0.06 * S, 0.25, 0, s * -0.15);
      add(new T.CylinderGeometry(0.05 * S, 0.045 * S, 0.28 * S, 10), piel, s * 0.27 * S, 0.17 * S, 0.22 * S, 1.2, 0, 0);
      add(new T.CylinderGeometry(0.056 * S, 0.056 * S, 0.08 * S, 10), azul, s * 0.27 * S, 0.11 * S, 0.33 * S, 1.2, 0, 0);
      add(new T.SphereGeometry(0.05 * S, 8, 6), piel, s * 0.27 * S, 0.08 * S, 0.40 * S);
      // muslos horizontales y piernas colgando, botas
      add(new T.BoxGeometry(0.18 * S, 0.17 * S, 0.44 * S), gi, s * 0.13 * S, 0.0, 0.22 * S);
      add(new T.CylinderGeometry(0.075 * S, 0.07 * S, 0.44 * S, 10), gi, s * 0.13 * S, -0.26 * S, 0.40 * S, 0.12, 0, 0);
      add(new T.BoxGeometry(0.13 * S, 0.12 * S, 0.22 * S), bota, s * 0.13 * S, -0.52 * S, 0.44 * S);
      add(new T.BoxGeometry(0.14 * S, 0.03 * S, 0.23 * S), blanco, s * 0.13 * S, -0.455 * S, 0.44 * S);
    });
    g.traverse(m => { if (m.isMesh) m.userData.sitio = '<b>Un saiyajin de visita</b><br><span class="sub">huevo de Pascua: se sienta en la viga a mirar la obra; su ki no cuenta en la cubicación</span>'; });

    // ---------- ki: tres capas de aura aditivas que laten y giran, y partículas que suben ----------
    const colAura = dorado ? '255,215,60' : '120,190,255';
    const tex = texturaRadial(T, colAura, 0.9);
    const capas = [];
    [[1.5, 2.1, 0.55], [1.15, 1.6, 0.8], [0.8, 1.1, 1.0]].forEach(([w, h, op], i) => {
      const sp = new T.Sprite(new T.SpriteMaterial({ map: tex, color: 0xffffff, transparent: true, opacity: op, blending: T.AdditiveBlending, depthWrite: false }));
      sp.scale.set(w * S, h * S, 1); sp.position.set(0, 0.35 * S, 0); sp.userData.base = [w * S, h * S, op, i]; g.add(sp); capas.push(sp);
    });
    const N = 160, pos = new Float32Array(N * 3), vel = new Float32Array(N), fase = new Float32Array(N);
    for (let i = 0; i < N; i++) { const a = Math.random() * Math.PI * 2, r = (0.25 + Math.random() * 0.45) * S; pos[i * 3] = Math.cos(a) * r; pos[i * 3 + 1] = (-0.5 + Math.random() * 1.6) * S; pos[i * 3 + 2] = Math.sin(a) * r * 0.7; vel[i] = (0.4 + Math.random() * 0.9) * S; fase[i] = Math.random() * 6.28; }
    const geoP = new T.BufferGeometry(); geoP.setAttribute('position', new T.BufferAttribute(pos, 3));
    const puntos = new T.Points(geoP, new T.PointsMaterial({ map: tex, color: dorado ? 0xFFE066 : 0x9ED2FF, size: 0.09 * S, transparent: true, opacity: 0.95, blending: T.AdditiveBlending, depthWrite: false, sizeAttenuation: true }));
    g.add(puntos);
    const luz = new T.PointLight(dorado ? 0xFFD040 : 0x7FB4FF, 1.2, 6 * S); luz.position.set(0, 0.6 * S, 0.1 * S); g.add(luz);
    let tAnt = 0;
    g.animar = function (t) {
      const s = t / 1000, dt = tAnt ? Math.min(0.05, s - tAnt) : 0.016; tAnt = s;
      capas.forEach(sp => { const [w, h, op, i] = sp.userData.base; const lat = 1 + 0.12 * Math.sin(s * (6 + i * 1.7) + i) + 0.05 * Math.sin(s * 13 + i * 2); sp.scale.set(w * lat, h * (1 + 0.18 * Math.sin(s * 4.5 + i)), 1); sp.material.rotation = s * (0.6 + i * 0.3) * (i % 2 ? -1 : 1); sp.material.opacity = op * (0.8 + 0.2 * Math.sin(s * 9 + i)); });
      const a = puntos.geometry.attributes.position.array;
      for (let i = 0; i < N; i++) { a[i * 3 + 1] += vel[i] * dt; a[i * 3] += Math.sin(s * 5 + fase[i]) * 0.004 * S; if (a[i * 3 + 1] > 1.25 * S) { a[i * 3 + 1] = -0.55 * S; const an = Math.random() * Math.PI * 2, r = (0.2 + Math.random() * 0.45) * S; a[i * 3] = Math.cos(an) * r; a[i * 3 + 2] = Math.sin(an) * r * 0.7; } }
      puntos.geometry.attributes.position.needsUpdate = true;
      luz.intensity = 1.0 + 0.5 * Math.sin(s * 11) + 0.25 * Math.sin(s * 23);
      cab.rotation.y = 0.15 * Math.sin(s * 0.7);   // mira de a poco para los lados
    };
    if (o.pos) g.position.set(o.pos[0], o.pos[1], o.pos[2]);
    g.rotation.y = ROT[o.mira || 'S'] || 0;
    return g;
  }
  window.Goku3D = { crear };
})();
