"""Geometría chica compartida por los generadores (sitio y estudio)."""


def offset_rect_poly(pts, t):
    """Desplaza hacia adentro en t un polígono rectilíneo (lados paralelos a los ejes), sin vértices repetidos.
    Sirve para pasar de las caras de obra gruesa a las caras terminadas (tabique de t por dentro)."""
    n = len(pts)
    if n < 4 or not t:
        return [list(p) for p in pts]
    area2 = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    sgn = 1.0 if area2 > 0 else -1.0          # con área positiva el interior queda a la izquierda de cada lado
    lineas = []                                 # por lado: ('h', y') o ('v', x') ya desplazado hacia adentro
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        dx, dy = x1 - x0, y1 - y0
        if abs(dy) < 1e-9:                      # lado horizontal: normal interior = (0, sgn*dx/|dx|)
            lineas.append(('h', y0 + sgn * (1 if dx > 0 else -1) * t))
        else:                                   # lado vertical: normal interior = (-sgn*dy/|dy|, 0)
            lineas.append(('v', x0 - sgn * (1 if dy > 0 else -1) * t))
    out = []
    for i in range(n):                          # vértice i = intersección del lado i-1 con el lado i
        a, b = lineas[i - 1], lineas[i]
        if a[0] == b[0]:
            raise ValueError('polígono no rectilíneo o con lados colineales seguidos')
        x = a[1] if a[0] == 'v' else b[1]
        y = a[1] if a[0] == 'h' else b[1]
        out.append([round(x, 1), round(y, 1)])
    return out


if __name__ == '__main__':
    print(offset_rect_poly([[25, 25], [1070, 25], [1070, 235], [906.7, 235], [906.7, 532], [1070, 532], [1070, 645], [25, 645]], 10))
    print(offset_rect_poly([[25, 670], [775, 670], [775, 1610], [25, 1610]], 10))
