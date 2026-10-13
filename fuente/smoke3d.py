#!/usr/bin/env python3
"""Prueba de humo de 3d.html sin WebGL: genera una copia de la página con un THREE.WebGLRenderer falso para que corra
todo el código (datos, hormigón, fierros, mobiliario, cotas, nav, Gokú, el loop) en un visor sin WebGL y se vean los
errores de ejecución en la consola (una revisión de sintaxis no pilla, por ejemplo, usar una variable antes de declararla).

Uso:  python3 fuente/smoke3d.py <carpeta_salida> [base_url]
      python3 -m http.server 8799 --bind 127.0.0.1 --directory .        (sirve el repo: scripts y datos)
      python3 -m http.server 8800 --bind 127.0.0.1 --directory <carpeta_salida>
      abrir http://127.0.0.1:8800/3d_stub.html?vista=estudio&goku=1  y leer la consola; window.VISTA3D queda disponible.
"""
import re, sys, pathlib
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
base = sys.argv[2] if len(sys.argv) > 2 else 'http://127.0.0.1:8799/'
src = pathlib.Path(__file__).resolve().parents[1] / '3d.html'
s = src.read_text(encoding='utf-8')
STUB = """<script>
THREE.WebGLRenderer = function(){ const c = document.createElement('canvas'); this.domElement = c;
  this.setSize = (w, h) => { c.width = w; c.height = h; c.style.width = w + 'px'; c.style.height = h + 'px'; };
  this.setPixelRatio = () => {}; this.render = () => { window.__cuadros = (window.__cuadros || 0) + 1; }; this.setClearColor = () => {};
  this.shadowMap = {enabled: false}; this.capabilities = {}; this.dispose = () => {}; this.getSize = v => (v || new THREE.Vector2()).set(c.width, c.height); };
window.__stub = true;
</script>"""
tag = '<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>'
assert tag in s, 'no encuentro el script de three'
s = s.replace(tag, tag + '\n' + STUB)
s = re.sub(r'(src|href)="(?!https?://|#|data:)([^"]+)"', lambda m: f'{m.group(1)}="{base}{m.group(2)}"', s)
(out / '3d_stub.html').write_text(s, encoding='utf-8')
print('listo:', out / '3d_stub.html')
