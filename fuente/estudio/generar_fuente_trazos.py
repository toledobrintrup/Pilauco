#!/usr/bin/env python3
# Genera fuente_trazos.js: la letra de trazo único de las láminas del estudio (pestaña Planos de estudio.html),
# igual a la «romans» de los planos de ingeniería en CAD. Sale de la fuente Hershey «Roman Simplex» (futural).
#
#   The Hershey Fonts were originally created by Dr. A. V. Hershey while working at the U. S. National Bureau of Standards.
#   The format of the Font data in this distribution was originally created by James Hurt, Cognition, Inc.,
#   900 Technology Park Drive, Billerica, MA 01821 (mit-eddie!ci-dandelion!hurt).
#
# Cada glifo: límites izquierdo y derecho y polilíneas; las coordenadas son letra − 'R' (y hacia abajo; la línea base
# queda en y = 9 y la mayúscula mide 21). A esos 95 glifos ASCII se suman los que usa el castellano y la notación de
# fierros (á é í ó ú ñ ü, ø, °, ², ×, ·, ≥, ≤, ±, flechas), compuestos aquí mismo.
#
# uso: python3 generar_fuente_trazos.py ../../fuente_trazos.js
import json, sys

FUTURAL = r'''
JZ
MWRFRT RRYQZR[SZRY
JZNFNM RVFVM
H]SBLb RYBRb RLOZO RKUYU
H\PBP_ RTBT_ RYIWGTFPFMGKIKKLMMNOOUQWRXSYUYXWZT[P[MZKX
F^[FI[ RNFPHPJOLMMKMIKIIJGLFNFPGSHVHYG[F RWTUUTWTYV[X[ZZ[X[VYTWT
E_\O\N[MZMYNXPVUTXRZP[L[JZIYHWHUISJRQNRMSKSIRGPFNGMIMKNNPQUXWZY[[[\Z\Y
MWRHQGRFSGSIRKQL
KYVBTDRGPKOPOTPYR]T`Vb
KYNBPDRGTKUPUTTYR]P`Nb
JZRLRX RMOWU RWOMU
E_RIR[ RIR[R
MWSZR[QZRYSZS\R^Q_
E_IR[R
MWRYQZR[SZRY
G][BIb
H\QFNGLJKOKRLWNZQ[S[VZXWYRYOXJVGSFQF
H\NJPISFS[
H\LKLJMHNGPFTFVGWHXJXLWNUQK[Y[
H\MFXFRNUNWOXPYSYUXXVZS[P[MZLYKW
H\UFKTZT RUFU[
H\WFMFLOMNPMSMVNXPYSYUXXVZS[P[MZLYKW
H\XIWGTFRFOGMJLOLTMXOZR[S[VZXXYUYTXQVOSNRNOOMQLT
H\YFO[ RKFYF
H\PFMGLILKMMONSOVPXRYTYWXYWZT[P[MZLYKWKTLRNPQOUNWMXKXIWGTFPF
H\XMWPURRSQSNRLPKMKLLINGQFRFUGWIXMXRWWUZR[P[MZLX
MWRMQNROSNRM RRYQZR[SZRY
MWRMQNROSNRM RSZR[QZRYSZS\R^Q_
F^ZIJRZ[
E_IO[O RIU[U
F^JIZRJ[
I[LKLJMHNGPFTFVGWHXJXLWNVORQRT RRYQZR[SZRY
E`WNVLTKQKOLNMMPMSNUPVSVUUVS RQKOMNPNSOUPV RWKVSVUXVZV\T]Q]O\L[JYHWGTFQFNGLHJJILHOHRIUJWLYNZQ[T[WZYYZX RXKWSWUXV
I[RFJ[ RRFZ[ RMTWT
G\KFK[ RKFTFWGXHYJYLXNWOTP RKPTPWQXRYTYWXYWZT[K[
H]ZKYIWGUFQFOGMILKKNKSLVMXOZQ[U[WZYXZV
G\KFK[ RKFRFUGWIXKYNYSXVWXUZR[K[
H[LFL[ RLFYF RLPTP RL[Y[
HZLFL[ RLFYF RLPTP
H]ZKYIWGUFQFOGMILKKNKSLVMXOZQ[U[WZYXZVZS RUSZS
G]KFK[ RYFY[ RKPYP
NVRFR[
JZVFVVUYTZR[P[NZMYLVLT
G\KFK[ RYFKT RPOY[
HYLFL[ RL[X[
F^JFJ[ RJFR[ RZFR[ RZFZ[
G]KFK[ RKFY[ RYFY[
G]PFNGLIKKJNJSKVLXNZP[T[VZXXYVZSZNYKXIVGTFPF
G\KFK[ RKFTFWGXHYJYMXOWPTQKQ
G]PFNGLIKKJNJSKVLXNZP[T[VZXXYVZSZNYKXIVGTFPF RSWY]
G\KFK[ RKFTFWGXHYJYLXNWOTPKP RRPY[
H\YIWGTFPFMGKIKKLMMNOOUQWRXSYUYXWZT[P[MZKX
JZRFR[ RKFYF
G]KFKULXNZQ[S[VZXXYUYF
I[JFR[ RZFR[
F^HFM[ RRFM[ RRFW[ R\FW[
H\KFY[ RYFK[
I[JFRPR[ RZFRP
H\YFK[ RKFYF RK[Y[
KYOBOb RPBPb ROBVB RObVb
KYKFY^
KYTBTb RUBUb RNBUB RNbUb
JZRDJR RRDZR
I[Ib[b
NVSKQMQORPSORNQO
I\XMX[ RXPVNTMQMONMPLSLUMXOZQ[T[VZXX
H[LFL[ RLPNNPMSMUNWPXSXUWXUZS[P[NZLX
I[XPVNTMQMONMPLSLUMXOZQ[T[VZXX
I\XFX[ RXPVNTMQMONMPLSLUMXOZQ[T[VZXX
I[LSXSXQWOVNTMQMONMPLSLUMXOZQ[T[VZXX
MYWFUFSGRJR[ ROMVM
I\XMX]W`VaTbQbOa RXPVNTMQMONMPLSLUMXOZQ[T[VZXX
I\MFM[ RMQPNRMUMWNXQX[
NVQFRGSFREQF RRMR[
MWRFSGTFSERF RSMS^RaPbNb
IZMFM[ RWMMW RQSX[
NVRFR[
CaGMG[ RGQJNLMOMQNRQR[ RRQUNWMZM\N]Q][
I\MMM[ RMQPNRMUMWNXQX[
I\QMONMPLSLUMXOZQ[T[VZXXYUYSXPVNTMQM
H[LMLb RLPNNPMSMUNWPXSXUWXUZS[P[NZLX
I\XMXb RXPVNTMQMONMPLSLUMXOZQ[T[VZXX
KXOMO[ ROSPPRNTMWM
J[XPWNTMQMNNMPNRPSUTWUXWXXWZT[Q[NZMX
MYRFRWSZU[W[ ROMVM
I\MMMWNZP[S[UZXW RXMX[
JZLMR[ RXMR[
G]JMN[ RRMN[ RRMV[ RZMV[
J[MMX[ RXMM[
JZLMR[ RXMR[P_NaLbKb
J[XMM[ RMMXM RM[X[
KYTBRCQDPFPHQJRKSMSOQQ RRCQEQGRISJTLTNSPORSTTVTXSZR[Q]Q_Ra RQSSUSWRYQZP\P^Q`RaTb
NVRBRb
KYPBRCSDTFTHSJRKQMQOSQ RRCSESGRIQJPLPNQPURQTPVPXQZR[S]S_Ra RSSQUQWRYSZT\T^S`RaPb
F^IUISJPLONOPPTSVTXTZS[Q RISJQLPNPPQTTVUXUZT[Q[O
'''.strip('\n').split('\n')

assert len(FUTURAL) == 95, len(FUTURAL)


def glifo(s):
    l, r = ord(s[0]) - 82, ord(s[1]) - 82
    tr, cur = [], []
    for i in range(2, len(s), 2):
        par = s[i:i + 2]
        if par == ' R':
            if cur: tr.append(cur)
            cur = []
        else:
            cur.append([ord(par[0]) - 82, ord(par[1]) - 82])
    if cur: tr.append(cur)
    return {'l': l, 'r': r, 's': tr}


G = {chr(32 + i): glifo(s) for i, s in enumerate(FUTURAL)}
cp = lambda g: {'l': g['l'], 'r': g['r'], 's': [[p[:] for p in t] for t in g['s']]}


def mas(base, *trazos, l=None, r=None):
    g = cp(G[base]); g['s'] += [list(map(list, t)) for t in trazos]
    if l is not None: g['l'] = l
    if r is not None: g['r'] = r
    return g


AGUDO = [(-1, -8), (3, -12)]
AGUDO_M = [(-1, -15), (3, -19)]
TILDE = [(-5, -8), (-4, -10), (-2, -10), (1, -8), (3, -8), (4, -10)]
TILDE_M = [(-5, -15), (-4, -17), (-2, -17), (1, -15), (3, -15), (4, -17)]
for c, b in zip('áéóú', 'aeou'): G[c] = mas(b, AGUDO)
gi = cp(G['i']); gi['s'] = gi['s'][1:] + [[[-1, -8], [3, -12]]]; G['í'] = gi          # sin el punto
for c, b in zip('ÁÉÍÓÚ', 'AEIOU'): G[c] = mas(b, AGUDO_M)
G['ñ'] = mas('n', TILDE); G['Ñ'] = mas('N', TILDE_M)
G['ü'] = mas('u', [(-3, -9), (-3, -8)], [(2, -9), (2, -8)])
G['ø'] = mas('o', [(-6, 10), (7, -6)])                                                  # diámetro (ø12@15)
G['Ø'] = mas('O', [(-7, 10), (8, -13)])
circ = lambda cx, cy, r, n=10: [[round(cx + r * __import__('math').cos(2 * 3.14159265 * k / n), 2), round(cy + r * __import__('math').sin(2 * 3.14159265 * k / n), 2)] for k in range(n + 1)]
G['°'] = {'l': -5, 'r': 5, 's': [circ(0, -9, 3)]}
G['º'] = G['°']
esc = lambda g, k, dy: {'l': round(g['l'] * k), 'r': round(g['r'] * k), 's': [[[round(p[0] * k, 2), round(-12 + (p[1] + 12) * k + dy, 2)] for p in t] for t in g['s']]}
G['²'] = esc(G['2'], 0.55, -2); G['³'] = esc(G['3'], 0.55, -2)
G['×'] = {'l': -8, 'r': 8, 's': [[[-5, -4], [5, 6]], [[5, -4], [-5, 6]]]}
G['·'] = {'l': -5, 'r': 5, 's': [[[0, 0], [-1, 1], [0, 2], [1, 1], [0, 0]]]}
G['–'] = G['-']; G['—'] = G['-']; G['−'] = G['-']
G['≥'] = {'l': -11, 'r': 11, 's': [[[-8, -7], [8, -1], [-8, 5]], [[-8, 9], [8, 9]]]}
G['≤'] = {'l': -11, 'r': 11, 's': [[[8, -7], [-8, -1], [8, 5]], [[-8, 9], [8, 9]]]}
G['±'] = {'l': -11, 'r': 11, 's': [[[0, -8], [0, 5]], [[-8, -1.5], [8, -1.5]], [[-8, 9], [8, 9]]]}
G['→'] = {'l': -12, 'r': 12, 's': [[[-9, 0], [9, 0]], [[4, -5], [9, 0], [4, 5]]]}
G['←'] = {'l': -12, 'r': 12, 's': [[[9, 0], [-9, 0]], [[-4, -5], [-9, 0], [-4, 5]]]}
G['↑'] = {'l': -8, 'r': 8, 's': [[[0, 9], [0, -12]], [[-5, -7], [0, -12], [5, -7]]]}
G['↓'] = {'l': -8, 'r': 8, 's': [[[0, -12], [0, 9]], [[-5, 4], [0, 9], [5, 4]]]}
G['“'] = G['"']; G['”'] = G['"']; G['«'] = G['"']; G['»'] = G['"']; G['‘'] = G["'"]; G['’'] = G["'"]; G['′'] = G["'"]; G['″'] = G['"']
inv = lambda g: {'l': g['l'], 'r': g['r'], 's': [[[p[0], -3 - p[1]] for p in t] for t in g['s']]}
G['¿'] = inv(G['?']); G['¡'] = inv(G['!'])
G['…'] = {'l': -12, 'r': 12, 's': [[[x, 7], [x - 1, 8], [x, 9], [x + 1, 8], [x, 7]] for x in (-7, 0, 7)]}
G['≈'] = {'l': -12, 'r': 12, 's': [[[-9, d + 2], [-9, d], [-8, d - 2], [-6, d - 3], [-4, d - 3], [-2, d - 2], [2, d + 1], [4, d + 2], [6, d + 2], [8, d + 1], [9, d - 1], [9, d - 3]] for d in (-3, 4)]}
G['½'] = {'l': -12, 'r': 12, 's': esc(G['1'], 0.5, 0)['s'] and [[[p[0] - 7, p[1]] for p in t] for t in esc(G['1'], 0.5, 0)['s']] + [[[7, -12], [-7, 9]]] + [[[p[0] + 7, p[1] + 10.5] for p in t] for t in esc(G['2'], 0.5, 0)['s']]}
G['¼'] = {'l': -12, 'r': 12, 's': [[[p[0] - 7, p[1]] for p in t] for t in esc(G['1'], 0.5, 0)['s']] + [[[7, -12], [-7, 9]]] + [[[p[0] + 7, p[1] + 10.5] for p in t] for t in esc(G['4'], 0.5, 0)['s']]}
G['¾'] = {'l': -12, 'r': 12, 's': [[[p[0] - 7, p[1]] for p in t] for t in esc(G['3'], 0.5, 0)['s']] + [[[7, -12], [-7, 9]]] + [[[p[0] + 7, p[1] + 10.5] for p in t] for t in esc(G['4'], 0.5, 0)['s']]}
G['⌀'] = G['ø']

salida = sys.argv[1] if len(sys.argv) > 1 else 'fuente_trazos.js'
with open(salida, 'w') as f:
    f.write('// Letra de trazo único de las láminas del estudio (Hershey «Roman Simplex», la «romans» de los planos en CAD). Generado por\n'
            '// fuente/estudio/generar_fuente_trazos.py: no editar a mano.\n'
            '// The Hershey Fonts were originally created by Dr. A. V. Hershey while working at the U. S. National Bureau of Standards.\n'
            '// The format of the Font data in this distribution was originally created by James Hurt, Cognition, Inc.\n'
            '// l, r: límites del glifo; s: polilíneas [x, y] (y hacia abajo; línea base en y = 9; la mayúscula mide 21).\n')
    f.write('const FUENTE_TRAZOS = ' + json.dumps(G, ensure_ascii=False, separators=(',', ':')) + ';\n')
print(len(G), 'glifos →', salida)
