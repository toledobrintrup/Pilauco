# -*- coding: utf-8 -*-
"""placa.json: sección y tablas de la placa Instadeck 0,8 (ficha Cintac, agosto 2026).
La polilínea es el EJE de la chapa medido en el dibujo vectorial de la pág. 1 (escala por la cota
de 950 mm de avance útil); aquí se baja 0,4 mm para que sea la cara inferior.
Uso: python3 placa_desde_ficha.py deck_instadeck.json placa.json"""
import sys, json
d = json.load(open(sys.argv[1]))
perfil = [[round(x, 2), round(max(0.0, y - 0.4), 2)] for x, y in d['polilinea_eje_mm']]
placa = {
    'perfil': perfil, 'espesor': 0.8, 'alto': 63.5, 'util': 950, 'total': d['ancho_total_eje_mm'],
    'peso': 8.03, 'nervios': d['nervios'], 'paso': d['paso_mm'], 'x_nervio0': d['x_centros_nervio_mm'][0],
    'ala_superior': d['ala_superior_eje_mm'], 'base_trapecio': d['base_trapecio_eje_mm'], 'valle': d['valle_interior_eje_mm'],
    'angulo_alma': d['alma_angulo_horizontal_deg'], 'desarrollo': d['desarrollo_eje_mm'],
    'cotas_texto': ('Cresta ≈ 110 mm, base del trapecio ≈ 184 mm, valle ≈ 134 mm, almas a 60° sobre la horizontal, '
                    'con un embutido en V de 14 × 5 mm en cada cresta y un rigidizador de 14 × 5 mm en los valles. '
                    'Las planchas se unen con un gancho que monta sobre el labio de la anterior.'),
    # [espesor total cm, hormigón sobre la cresta cm, m3/m2, kg/m2 total] (tabla "Cubicación y cargas de peso propio")
    'tabla_espesores': [[11.35, 5, 0.085, 212], [12.35, 6, 0.095, 236], [14.35, 8, 0.115, 284], [16.35, 10, 0.135, 332], [18.35, 12, 0.155, 380]],
    'vacio_m3m2': 0.0285,     # espesor total - m3/m2 de la tabla, igual en todas las filas
    # "Longitud máxima sin alzaprimado" (cm), filas 1 vano / 2 vanos / 3 o más; columnas hormigón sobre la cresta
    'sin_alzaprima': {'hc': [5, 6, 8, 10, 12], 'filas': [[209, 200, 187, 175, 166], [277, 267, 250, 236, 224], [285, 274, 256, 241, 229]]},
    # "Control de deformaciones": distancia máxima entre apoyos (cm), por espesor total, para 1 / 2 / 3 vanos
    'deformacion': {'et': [11.35, 12.35, 14.35, 16.35, 18.35], 'filas': [[250, 306, 363], [272, 333, 395], [316, 387, 459], [360, 441, 523], [404, 495, 587]]},
    'notas_ficha': [
        'Acero estructural grado 37, galvanizado G-90 según ASTM A653; largos de 1,5 a 15 m.',
        'Hormigón H25 como mínimo; su espesor se mide sobre la cresta y no baja de 5 cm.',
        'Malla de retracción de al menos 1,8 cm²/m en cada dirección (A63-42H), a 2,5 cm de la cara superior.',
        'La placa se fija a la estructura en todos los valles; con apoyos a más de 1,5 m, bordes y uniones se fijan a mitad de luz o cada 90 cm (lo menor).',
        'Los conectores de corte deben resistir 11,2 t de corte último por metro de ancho de placa en todos los apoyos.',
        'Sección efectiva de la placa: I+ 74,60 e I− 69,39 cm⁴/m; S+ 18,62 y S− 19,23 cm³/m.',
        'Inercia de la sección compuesta (para flechas): 18 826 cm⁴/m con 8 cm de hormigón sobre la cresta; 26 619 con 10 cm.',
        'Para que la placa trabaje continua sobre varios apoyos hace falta armadura superior en los apoyos intermedios, según el calculista.',
        'Sobrecarga admisible de la losa compuesta con 8 cm sobre la cresta: 2000 kg/m² hasta 2,0 m entre apoyos, 1554 a 2,4 m, 950 a 3,0 m y 452 a 4,0 m.',
    ],
}
json.dump(placa, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
print('placa.json', len(perfil), 'puntos; ancho', placa['total'])
