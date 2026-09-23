def etiquetas_con_linea(labels, lines, tol=22):
    """Deja sólo los rótulos que tienen línea de eje de verdad (las marcas de
    elevación del plano no la tienen), ajusta el rótulo a la posición real de la
    línea y guarda su extensión, para poder unir rótulo y línea en el dibujo."""
    hor, ver = {}, {}
    for x0, y0, x1, y1 in lines:
        if abs(y0 - y1) < 1: hor.setdefault(round(y0, 1), []).extend([x0, x1])
        elif abs(x0 - x1) < 1: ver.setdefault(round(x0, 1), []).extend([y0, y1])
    out = []
    for a in labels:
        num = a['t'].isdigit()
        tabla, ref = (ver, a['x']) if num else (hor, a['y'])
        ks = [k for k in tabla if abs(k - ref) < tol]
        if not ks: continue
        vs = [v for k in ks for v in tabla[k]]
        b = dict(a); b['ext'] = [round(min(vs), 1), round(max(vs), 1)]
        if num: b['x'] = round(sum(ks) / len(ks), 1)
        else:   b['y'] = round(sum(ks) / len(ks), 1)
        out.append(b)
    return out
