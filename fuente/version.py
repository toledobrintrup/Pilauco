# -*- coding: utf-8 -*-
"""Marca la versión del sitio en todas las páginas antes de cada commit.

    python3 fuente/version.py            # usa el número del commit que viene (commits históricos + 1)
    python3 fuente/version.py 60         # o un número a mano

La versión es "V<n>", con n = cantidad de commits del proyecto (cada commit se publica con el push de Gabriel), y
la fecha de hoy. Se escribe en menu.js (window.PILAUCO_VERSION, que el menú muestra en todas las páginas y el 3D
muestra en su ⓘ) y en los "?v=" de los scripts de cada página, para que Safari no sirva archivos viejos del caché.
"""
import re, subprocess, sys, datetime, pathlib

raiz = pathlib.Path(__file__).resolve().parent.parent
if len(sys.argv) > 1:
    n = int(sys.argv[1])
else:
    n = int(subprocess.check_output(['git', 'rev-list', '--count', 'HEAD'], cwd=raiz).decode().strip()) + 1
ver = f'V{n}'
fecha = datetime.date.today().strftime('%d-%m-%Y')

p = raiz / 'menu.js'; s = p.read_text()
s2 = re.sub(r"window\.PILAUCO_VERSION = \{ n: '[^']*', fecha: '[^']*' \};", f"window.PILAUCO_VERSION = {{ n: '{ver}', fecha: '{fecha}' }};", s)
assert s2 != s or ver in s, 'menu.js sin la constante PILAUCO_VERSION'
p.write_text(s2)

paginas = ['index.html', '3d.html', 'losa.html', 'pernos.html', 'estudio.html', 'tablero.html']
total = 0
for nombre in paginas:
    p = raiz / nombre
    if not p.exists(): continue
    s = p.read_text()
    s2, k = re.subn(r'(\?v=|&amp;v=|&v=)[A-Za-z0-9]+', lambda m: m.group(1) + ver, s)   # ?v= de los scripts y &v= de los iframes
    p.write_text(s2); total += k
print(f'{ver} · {fecha} · {total} scripts marcados en {len(paginas)} páginas')
