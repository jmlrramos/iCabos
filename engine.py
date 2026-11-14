# -*- coding: utf-8 -*-
"""
Motor de cálculo: dimensionamento de cabos e linhas para centrais solares e parques eólicos.
Critérios: aquecimento (RTIEBT 523), proteção (RTIEBT 433), queda de tensão, perdas,
curto-circuito e efeito capacitivo. Tabelas Eurocabos (Mai.06), IEC 60364-5-52, IEC 60502-2,
EN 50618 e condutores nus ACSR / AAAC.
Criado por Jorge Ramos (Tecneira) para uso privado.
"""
import math

# ---------------------------------------------------------------- formatação
def nf(x, d=2):
    try:
        if x is None or not math.isfinite(x):
            return "–"
    except TypeError:
        return "–"
    s = f"{x:,.{d}f}"
    return s.replace(",", " ").replace(".", ",")


def interp(t, x):
    k = sorted(t)
    if x <= k[0]:
        return t[k[0]]
    if x >= k[-1]:
        return t[k[-1]]
    for a, b in zip(k, k[1:]):
        if a <= x <= b:
            return t[a] + (t[b] - t[a]) * (x - a) / (b - a)


# ---------------------------------------------------------------- dados base
# Resistência CC a 20 °C (Ω/km), IEC 60228 (Al 280/380/480/600/740 aproximados)
R20 = {
    "Cu": {0.5: 36.0, 0.75: 24.5, 1: 18.1, 1.5: 12.1, 2.5: 7.41, 4: 4.61, 6: 3.08, 10: 1.83, 16: 1.15, 25: 0.727,
           35: 0.524, 50: 0.387, 70: 0.268, 95: 0.193, 120: 0.153, 150: 0.124, 185: 0.0991, 240: 0.0754,
           300: 0.0601, 400: 0.047, 500: 0.0366, 630: 0.0283, 800: 0.0221, 1000: 0.0176, 1200: 0.0151,
           1600: 0.0113, 2000: 0.009, 2500: 0.0072},
    "Al": {10: 3.08, 16: 1.91, 25: 1.2, 35: 0.868, 50: 0.641, 70: 0.443, 95: 0.32, 120: 0.253, 150: 0.206,
           185: 0.164, 240: 0.125, 280: 0.107, 300: 0.1, 380: 0.080, 400: 0.0778, 480: 0.063, 500: 0.0605,
           600: 0.049, 630: 0.0469, 740: 0.040, 800: 0.0367, 1000: 0.0291, 1200: 0.0247, 1600: 0.0186,
           2000: 0.0149, 2500: 0.0127},
}
ALPHA = {"Cu": 0.00393, "Al": 0.00403}

# BT genérico IEC 60364-5-52 (Cu XLPE, 3 carregados). Ref.: ar 30 °C, solo 20 °C, 2,5 K·m/W
LV_S = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 500, 630]
LV_T = {
    "D1": [21, 28, 36, 44, 58, 75, 96, 115, 135, 167, 197, 223, 251, 281, 324, 365, None, None, None],
    "D2": [23, 30, 39, 49, 65, 84, 107, 129, 153, 188, 226, 257, 287, 324, 375, 419, None, None, None],
    "C": [24, 33, 45, 58, 80, 107, 138, 171, 209, 269, 328, 382, 441, 506, 599, 693, None, None, None],
    "E": [23, 32, 42, 54, 75, 100, 127, 158, 192, 246, 298, 346, 399, 456, 538, 621, None, None, None],
    "F": [None] * 6 + [141, 176, 216, 279, 342, 400, 464, 533, 634, 736, 868, 998, 1151],
}
LV_M = {
    "D2": dict(n="D2 · Enterrado diretamente", g=True, duct=False, x=0.08),
    "D1": dict(n="D1 · Enterrado em tubo", g=True, duct=True, x=0.08),
    "C": dict(n="C · Fixado em parede / tabuleiro", g=False, x=0.08),
    "E": dict(n="E · Ao ar, tabuleiro perfurado", g=False, x=0.08),
    "F": dict(n="F · Ao ar, unipolares em trevo", g=False, x=0.09),
}
PV_S = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240]
PV_I = [30, 41, 55, 70, 98, 132, 176, 218, 276, 347, 416, 488, 566, 644, 775]
LXS_S = [16, 25, 35, 50, 70, 95, 120]
LXS_I = [72, 95, 115, 140, 175, 215, 250]
MT_S = [50, 70, 95, 120, 150, 185, 240, 300, 400, 500, 630]
MT_T = {"D": [145, 175, 205, 235, 260, 295, 340, 385, 440, 500, 565],
        "A": [180, 225, 270, 310, 350, 400, 470, 535, 615, 710, 810]}
MT_M = {"D": "Enterrado diretamente, trevo", "T": "Enterrado em tubo, trevo", "A": "Ao ar (caleira / tabuleiro), trevo"}
HV_S = [240, 300, 400, 500, 630, 800, 1000, 1200, 1600, 2000, 2500]
HV_T = {"Al": [420, 465, 515, 575, 650, 730, 810, 870, 970, 1050, 1120],
        "Cu": [530, 590, 650, 730, 820, 920, 1010, 1080, 1210, 1300, 1400]}
HV_M = {"D": "Enterrado diretamente, trevo", "T": "Enterrado em tubo, trevo"}

# Condutores nus: ACSR (tabela fornecida) e AAAC Aster (indicativo)
ACSR = [dict(d="30", al=26.25, i=150), dict(d="50", al=42.21, i=200), dict(d="90", al=75.40, i=280),
        dict(d="125", al=108.02, i=380), dict(d="130", al=80.36, i=325), dict(d="153", al=96.5, i=365),
        dict(d="160", al=135.93, i=435), dict(d="235", al=202.62, i=565), dict(d="325", al=264.42, i=675),
        dict(d="485", al=428.88, i=920), dict(d="595", al=565.36, i=1075)]
AAAC = [dict(d="Aster 34", s=34.4, i=140), dict(d="Aster 55", s=54.6, i=190), dict(d="Aster 75", s=75.5, i=235),
        dict(d="Aster 117", s=117, i=315), dict(d="Aster 148", s=148.1, i=365), dict(d="Aster 182", s=181.6, i=415),
        dict(d="Aster 228", s=228, i=480), dict(d="Aster 288", s=288, i=555), dict(d="Aster 366", s=366, i=645),
        dict(d="Aster 570", s=570, i=860)]

# ---------------------------------------------------------------- Eurocabos (Mai.06)
# (S, uni_sub, uni_ar, uni_du, bi_sub, bi_ar, bi_du, tri_sub, tri_ar, tri_du)   ΔU em V/(A·km), cos φ 0,8
_ = None
EC_LV = {
    "VV": dict(nome="VV / VAV", desc="BT · Cu · PVC", mat="Cu", ins="PVC", tab="Tabela I", rows=[
        (0.5, _, 12, _, _, 10, _, _, 9, _), (0.75, _, 15, _, _, 13.5, _, _, 12, _),
        (1, _, 18, _, _, 14.5, 34.8, _, 13, 30.1), (1.5, 34, 23, 20.2, 30, 19, 23.3, 25, 17, 20.2),
        (2.5, 45, 31, 12.4, 40, 26, 14.3, 35, 24, 12.4), (4, 60, 42, 7.77, 50, 35, 8.94, 45, 31, 7.74),
        (6, 75, 52, 5.22, 65, 44, 6.0, 60, 42, 5.19), (10, 105, 74, 3.14, 90, 61, 3.6, 80, 57, 3.12),
        (16, 135, 96, 2.02, 120, 83, 2.3, 110, 79, 1.99), (25, 180, 127, 1.31, 155, 110, 1.48, 135, 96, 1.28),
        (35, 225, 158, 0.963, 185, 132, 1.08, 165, 114, 0.946), (50, 260, 184, 0.734, 220, 158, 0.822, 190, 132, 0.718),
        (70, 345, 242, 0.533, 280, 198, 0.589, 245, 171, 0.52), (95, 410, 290, 0.406, 335, 237, 0.443, 295, 206, 0.393),
        (120, 485, 343, 0.34, 380, 268, 0.368, 340, 237, 0.326), (150, 550, 387, 0.299, 435, 308, 0.313, 390, 272, 0.279),
        (185, 630, 444, 0.25, 490, 343, 0.265, 445, 312, 0.238), (240, 740, 523, 0.21, 570, 400, 0.218, 515, 360, 0.198),
        (300, 855, 602, 0.183, 640, 448, 0.188, 590, 413, 0.172), (400, 1015, 721, 0.16, 760, 536, 0.164, 700, 492, 0.15),
        (500, 1170, 822, 0.14, _, _, _, _, _, _)]),
    "XV": dict(nome="XV / XAV", desc="BT · Cu · XLPE", mat="Cu", ins="XLPE", tab="Tabela II", rows=[
        (1, _, 24, 32.1, _, 20, 37.0, _, 18, 32.0), (1.5, 48, 32, 21.5, 32, 26, 24.8, 30, 24, 21.4),
        (2.5, 63, 43, 13.2, 43, 35, 15.2, 40, 32, 13.1), (4, 82, 57, 8.27, 55, 45, 9.51, 52, 42, 8.24),
        (6, 103, 72, 5.6, 68, 58, 6.38, 64, 53, 5.53), (10, 137, 99, 3.34, 90, 80, 3.83, 86, 73, 3.31),
        (16, 177, 131, 2.14, 115, 105, 2.44, 111, 96, 2.11), (25, 229, 177, 1.36, 149, 143, 1.57, 143, 130, 1.35),
        (35, 275, 218, 1.02, 178, 176, 1.15, 173, 160, 1.01), (50, 327, 266, 0.776, 211, 215, 0.87, 205, 195, 0.774),
        (70, 402, 338, 0.562, 259, 270, 0.623, 252, 247, 0.559), (95, 482, 416, 0.427, 310, 335, 0.469, 303, 305, 0.425),
        (120, 550, 487, 0.356, 352, 390, 0.387, 346, 355, 0.353), (150, 618, 559, 0.306, 396, 447, 0.329, 390, 407, 0.303),
        (185, 701, 648, 0.261, 449, 514, 0.227, 441, 469, 0.259), (240, 819, 779, 0.218, 521, 610, 0.228, 511, 551, 0.215),
        (300, 931, 902, 0.189, _, _, _, _, _, _), (400, 1073, 1100, 0.165, _, _, _, _, _, _),
        (500, 1223, 1246, 0.144, _, _, _, _, _, _)]),
    "LVV": dict(nome="LVV / LSVV", desc="BT · Al · PVC", mat="Al", ins="PVC", tab="Tabela IV", rows=[
        (16, 110, 80, 3.3, 95, 67, 3.76, 90, 62, 3.28), (25, 145, 102, 2.11, 125, 89, 2.39, 110, 80, 2.09),
        (35, 180, 129, 1.55, 150, 107, 1.75, 130, 93, 1.53), (50, 210, 151, 1.18, 175, 129, 0.31, 150, 107, 1.15),
        (70, 275, 196, 0.834, 225, 160, 0.927, 195, 138, 0.821), (95, 330, 236, 0.626, 270, 191, 0.687, 235, 169, 0.614),
        (120, 390, 276, 0.512, 305, 218, 0.558, 270, 191, 0.502), (150, 440, 311, 0.432, 350, 249, 0.467, 310, 222, 0.424),
        (185, 505, 360, 0.363, 390, 276, 0.387, 355, 254, 0.354), (240, 590, 423, 0.296, 455, 325, 0.312, 410, 294, 0.288),
        (280, 640, 463, 0.273, _, _, _, _, _, _), (300, 685, 490, 0.253, 510, 365, 0.263, 470, 334, 0.245),
        (380, 780, 561, 0.219, _, _, _, _, _, _), (400, 810, 583, 0.215, 610, 436, 0.236, 560, 401, 0.204),
        (480, 910, 650, 0.19, _, _, _, _, _, _), (500, 935, 668, 0.185, _, _, _, _, _, _),
        (600, 1050, 748, 0.169, _, _, _, _, _, _), (630, 1080, 774, 0.161, _, _, _, _, _, _),
        (740, 1190, 854, 0.149, _, _, _, _, _, _)]),
    "LXV": dict(nome="LXV / LSXV (e LXS ao ar)", desc="BT · Al · XLPE", mat="Al", ins="XLPE", tab="Tabela V", rows=[
        (16, _, 105, 3.5, 104, 91, 4.0, 87, 79, 3.49), (25, 180, 135, 2.24, 133, 108, 2.55, 110, 98, 2.23),
        (35, 215, 166, 1.65, 160, 135, 1.86, 134, 122, 1.63), (50, 257, 205, 1.29, 188, 164, 1.39, 160, 149, 1.22),
        (70, 315, 260, 0.883, 233, 211, 0.984, 197, 192, 0.87), (95, 377, 321, 0.662, 275, 257, 0.728, 234, 235, 0.651),
        (120, 430, 375, 0.54, 314, 300, 0.59, 266, 273, 0.53), (150, 482, 432, 0.455, 359, 346, 0.494, 300, 316, 0.447),
        (185, 545, 500, 0.381, 398, 397, 0.371, 337, 363, 0.372), (240, 640, 603, 0.315, 458, 470, 0.328, 388, 430, 0.303),
        (280, 690, 658, 0.285, _, _, _, _, _, _), (300, 725, 697, 0.271, 520, 543, 0.293, 440, 497, 0.248),
        (380, 820, 810, 0.228, _, _, _, _, _, _), (400, 835, 829, 0.224, _, _, _, _, _, _),
        (480, 922, 936, 0.197, _, _, _, _, _, _), (500, 950, 963, 0.191, _, _, _, _, _, _),
        (600, 1005, 1015, 0.174, _, _, _, _, _, _), (630, 1035, 1050, 0.16, _, _, _, _, _, _),
        (740, 1150, 1175, 0.138, _, _, _, _, _, _)]),
}
# MT monopolares XLPE em trevo juntivo (Tabela VI): (S, Al_sub, Cu_sub, Al_ar_catálogo, Cu_ar)
EC_MT_MONO = [(35, 150, 190, 25, 200), (50, 180, 230, 35, 240), (70, 220, 270, 50, 300), (95, 260, 330, 70, 360),
              (120, 300, 380, 95, 430), (150, 330, 430, 120, 490), (185, 380, 480, 150, 570), (240, 440, 560, 185, 670),
              (300, 490, 630, 240, 760), (400, 570, 720, 690, 890), (500, 650, 820, 810, 1020),
              (630, 750, 930, 950, 1180), (800, 840, 1030, 1090, 1340), (1000, 950, 1150, 1250, 1510)]
# A coluna "Al ao ar" do catálogo repete a secção até 300 mm² (gralha). Usa-se 0,78 × Cu ao ar.
def ec_mt_al_air(S, al_cat, cu_air):
    return al_cat if S >= 400 else round(0.78 * cu_air)

# MT tripolares (S, Al_sub, Cu_sub, Al_ar, Cu_ar)   (185 Cu ar = 310 no catálogo, provável gralha)
EC_MT_TRI = [(25, _, 165, _, 160), (35, _, 200, _, 195), (50, 180, 235, 175, 230), (70, 225, 285, 220, 280),
             (95, 270, 345, 265, 345), (120, 305, 390, 305, 395), (150, 340, 435, 345, 450), (185, 385, 490, 395, 310),
             (240, 445, 570, 470, 600)]

LV_FAMS = {"LXV": "LXV / LSXV · Al XLPE (Eurocabos)", "LVV": "LVV / LSVV · Al PVC (Eurocabos)",
           "XV": "XV / XAV · Cu XLPE (Eurocabos)", "VV": "VV / VAV · Cu PVC (Eurocabos)",
           "IEC": "Genérico IEC 60364-5-52 (Cu/Al, XLPE/PVC)", "PV": "Cabo solar H1Z2Z2-K (EN 50618)"}
MT_FAMS = {"LXHIOV": "LXHIOV · Al XLPE monopolar (Eurocabos)", "XHIOV": "XHIOV · Cu XLPE monopolar (Eurocabos)",
           "IEC_Al": "Genérico IEC 60502-2 · Al", "IEC_Cu": "Genérico IEC 60502-2 · Cu"}
EC_INST = {"sub": "Subterrânea (enterrado)", "tubo": "Subterrânea em tubo (×0,85)", "ar": "Ao ar livre"}
EC_CONSTR = {"uni": "Unipolares (ternos juntivos ×0,80)", "multi": "Multipolar (2 / 3-4 condutores)"}

KV = {6: dict(gmd=0.8, t=3.4), 10: dict(gmd=1.0, t=3.4), 15: dict(gmd=1.2, t=4.5), 20: dict(gmd=1.4, t=5.5),
      30: dict(gmd=1.8, t=8), 60: dict(gmd=3.5, t=11), 150: dict(gmd=6.5, t=18), 220: dict(gmd=8, t=22),
      400: dict(gmd=11.5, t=27)}
NB = {6: 1, 10: 1, 15: 1, 20: 1, 30: 1, 60: 1, 150: 1, 220: 2, 400: 3}
SOIL_DIRECT = {0.5: 1.88, 0.7: 1.62, 1: 1.5, 1.5: 1.28, 2: 1.12, 2.5: 1, 3: 0.9}
SOIL_DUCT = {0.5: 1.28, 0.7: 1.2, 1: 1.18, 1.5: 1.1, 2: 1.05, 2.5: 1, 3: 0.96}
G_GROUND = {0: {1: 1, 2: .75, 3: .65, 4: .6, 5: .55, 6: .5}, 0.25: {1: 1, 2: .85, 3: .75, 4: .7, 5: .65, 6: .6},
            0.5: {1: 1, 2: .9, 3: .8, 4: .75, 5: .7, 6: .7}, 1: {1: 1, 2: .95, 3: .85, 4: .8, 5: .8, 6: .8}}
G_AIR = {1: 1, 2: .88, 3: .82, 4: .79, 5: .78, 6: .76, 7: .75, 8: .74, 9: .73}
INS = [2, 4, 6, 10, 13, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000,
       1250, 1600, 2000, 2500, 3200, 4000, 5000, 6300]
KAC = {300: 1.02, 400: 1.03, 500: 1.05, 630: 1.07, 800: 1.10, 1000: 1.06, 1200: 1.07, 1600: 1.09, 2000: 1.11, 2500: 1.13}

TECH = {
    "pv_fix": dict(lbl="Solar fixo", h=1650.0, f=0.65, r=(1300, 2000), n="central solar fixa"),
    "pv_trk": dict(lbl="Solar seguidor", h=2050.0, f=0.68, r=(1700, 2450), n="central solar com seguidor"),
    "wind": dict(lbl="Eólico", h=2600.0, f=0.62, r=(1800, 3600), n="parque eólico"),
    "hyb": dict(lbl="Híbrido", h=3200.0, f=0.60, r=(2400, 4600), n="central híbrida"),
    "other": dict(lbl="Outro", h=2000.0, f=0.60, r=(500, 8760), n="central"),
}
LEVELS = {
    "bt_cc": dict(nome="BT · corrente contínua (FV)", U=[600, 1000, 1500], Ud=1500, u="V", sys="dc", nets=["sub"],
                  d=dict(P=350.0, L=250.0, fd=1.25, lvfam="LXV", constr="uni", inst="sub", du=1.5, icc=0.0, cos=1.0, prot="fus", net="sub")),
    "bt_ca": dict(nome="BT · corrente alternada", U=[230, 400, 690, 800], Ud=800, u="V", sys="ac", nets=["sub", "aer"],
                  d=dict(P=330.0, L=150.0, fd=1.0, lvfam="LXV", constr="uni", inst="sub", du=1.5, icc=0.0, cos=0.95, prot="disj", net="sub")),
    "mt": dict(nome="MT · 6 a 30 kV", U=[6, 10, 15, 20, 30], Ud=30, u="kV", sys="ac", nets=["sub", "aer"],
               d=dict(P=20.0, L=5.0, fd=1.0, mtfam="LXHIOV", m_mt="D", du=2.0, icc=12.5, cos=0.95, net="sub")),
    "at": dict(nome="AT · 60 kV", U=[60], Ud=60, u="kV", sys="ac", nets=["sub", "aer"],
               d=dict(P=50.0, L=10.0, fd=1.0, mat="Al", m_hv="D", du=3.0, icc=20.0, cos=0.95, net="aer")),
    "mat": dict(nome="MAT · 150 / 220 / 400 kV", U=[150, 220, 400], Ud=220, u="kV", sys="ac", nets=["sub", "aer"],
                d=dict(P=200.0, L=30.0, fd=1.0, mat="Cu", m_hv="D", du=3.0, icc=31.5, cos=0.95, net="aer")),
}


# ---------------------------------------------------------------- funções técnicas
def temp_f(tmax, ta, tref):
    return 0.0 if ta >= tmax else math.sqrt((tmax - ta) / (tmax - tref))


def soil_f(rho, duct, ref):
    t = SOIL_DUCT if duct else SOIL_DIRECT
    return interp(t, rho) / interp(t, ref)


def group_f(n, ground, sp):
    if n <= 1:
        return 1.0
    if ground:
        t = G_GROUND.get(sp, G_GROUND[0.5])
        return t[n] if n <= 6 else max(0.35, t[6] - 0.02 * (n - 6))
    return G_AIR[n] if n <= 9 else 0.72


def oh_x(dmm, nb, gmd):
    r = dmm / 2000
    gmr = 0.8 * r
    a = 0.4
    g = gmr
    if nb == 2:
        g = math.sqrt(gmr * a)
    elif nb == 3:
        g = (gmr * a * a) ** (1 / 3)
    elif nb >= 4:
        g = 1.09 * (gmr * a ** 3) ** 0.25
    return 0.0628 * math.log(gmd / g), g


def cable_geo(S, kV):
    t = KV.get(kV, dict(t=8))["t"]
    dc = math.sqrt(4 * S / (math.pi * 0.92))
    ext = 12 if kV >= 60 else 5
    Di = dc + 2 * t + 2
    D = Di + 2 * ext
    gmr = 0.779 * dc / 2
    return dict(X=0.0628 * math.log(D / gmr), dc=dc, Di=Di, D=D)


def medium(st):
    if st["net"] == "aer":
        return "air"
    if st["bt"]:
        f = st["lvfam"]
        if f == "PV":
            return "pv"
        if f == "IEC":
            return "ground" if LV_M[st["m_lv"]]["g"] else "air"
        return "air" if st["inst"] == "ar" else "ground"
    if st["kV"] < 60:
        return "air" if st["m_mt"] == "A" else "ground"
    return "ground"


def _kSC(mat, ins):
    if mat == "Cu":
        return 115 if ins == "PVC" else 143
    return 76 if ins == "PVC" else 94


def build_cands(st):
    out = []
    bt = st["bt"]
    if st["net"] == "aer":
        if bt:
            for S, I in zip(LXS_S, LXS_I):
                out.append(dict(label=f"LXS {S} mm² Al", S=S, Iz0=I, kE=1, kNote="tabela LXS (indicativa)", tmax=90,
                                tref=30, med="air", R20=R20["Al"][S], alpha=ALPHA["Al"], kac=1, X=0.1,
                                xNote="X ≈ 0,10 Ω/km (cabo torçado)", npar=1, kSC=94, mat="Al", src="LXS (indicativa), ar 30 °C"))
            return out
        fams = ["ACSR", "AAAC"] if st["fam"] == "ALL" else [st["fam"]]
        for f in fams:
            for c in (ACSR if f == "ACSR" else AAAC):
                S = c["al"] if f == "ACSR" else c["s"]
                Stot = float(c["d"]) if f == "ACSR" else c["s"]
                dmm = math.sqrt(4 * Stot / math.pi) / 0.866
                X, g = oh_x(dmm, st["nb"], st["gmd"])
                out.append(dict(label=f"{f} {c['d']}", fam=f, S=S, Stot=Stot, dmm=dmm, Iz0=c["i"], kE=1,
                                tmax=85 if st["kV"] >= 60 else 75, med="oh", R20=(28.9 if f == "ACSR" else 33.1) / S,
                                alpha=ALPHA["Al"], kac=1.02 if S >= 300 else 1, X=X, gmrEq=g, xb=True, npar=st["nb"],
                                kSC=87, mat="Al", src="ACSR: tabela fornecida" if f == "ACSR" else "AAAC Aster (indicativa)"))
        out.sort(key=lambda c: (c["Iz0"], c["S"]))
        return out

    if bt:
        f = st["lvfam"]
        dc = st["sys"] == "dc"
        if f == "PV":
            for S, I in zip(PV_S, PV_I):
                out.append(dict(label=f"{nf(S, 1 if S < 2 else 0)} mm² Cu H1Z2Z2-K", S=S, Iz0=I, kE=1,
                                kNote="EN 50618, cabo isolado ao ar", tmax=120, tref=60, med="air", pv=True,
                                R20=R20["Cu"][S], alpha=ALPHA["Cu"], kac=1, X=0, xNote="CC: sem reactância",
                                npar=st["npar"], kSC=143, mat="Cu", src="EN 50618 (ar 60 °C)"))
            return out
        if f in EC_LV:
            fam = EC_LV[f]
            uni = st["constr"] == "uni"
            inst = st["inst"]
            col = (1 if inst != "ar" else 2) if uni else ((4 if inst != "ar" else 5) if st["sys"] != "3f" else (7 if inst != "ar" else 8))
            for row in fam["rows"]:
                S = row[0]
                I0 = row[col]
                if I0 is None or R20[fam["mat"]].get(S) is None:
                    continue
                kE = (0.8 if uni else 1.0) * (0.85 if inst == "tubo" else 1.0)
                notes = []
                if uni:
                    notes.append("ternos juntivos ×0,80")
                if inst == "tubo":
                    notes.append("em tubo ×0,85")
                coln = ("1 condutor" if uni else ("2 condutores" if st["sys"] != "3f" else "3-4 condutores")) + \
                       (" ao ar" if inst == "ar" else " subterrânea")
                out.append(dict(label=f"{nf(S, 1 if S < 2 else 0)} mm² {fam['nome'].split(' ')[0]}", S=S, Iz0=I0, kE=kE,
                                kNote=", ".join(notes) or "valor direto do catálogo", tmax=70 if fam["ins"] == "PVC" else 90,
                                tref=30 if inst == "ar" else 20, med="air" if inst == "ar" else "ground", duct=inst == "tubo",
                                rhoRef=1.0, R20=R20[fam["mat"]][S], alpha=ALPHA[fam["mat"]], kac=1 if dc else KAC.get(S, 1),
                                X=0 if dc else (0.09 if uni else 0.08),
                                xNote="CC: sem reactância" if dc else ("X ≈ 0,09 Ω/km (unipolares)" if uni else "X ≈ 0,08 Ω/km (multipolar)"),
                                npar=st["npar"], kSC=_kSC(fam["mat"], fam["ins"]), mat=fam["mat"],
                                src=f"Eurocabos {fam['tab']} ({fam['nome']}), coluna {coln}; solo 20 °C, ar 30 °C"))
            return out
        # IEC genérico
        m = LV_M[st["m_lv"]]
        mat, ins = st["mat"], st["ins"]
        kM = 0.78 if mat == "Al" else 1
        kI = 0.81 if ins == "PVC" else 1
        kL = 1 if st["sys"] == "3f" else 1.17
        notes = [t for t, k in (("alumínio ×0,78", kM), ("PVC ×0,81", kI), ("2 condutores carregados ×1,17", kL)) if k != 1]
        for S, I0 in zip(LV_S, LV_T[st["m_lv"]]):
            if I0 is None or R20[mat].get(S) is None or (mat == "Al" and S < 16):
                continue
            out.append(dict(label=f"{nf(S, 1 if S < 2 else 0)} mm² {mat} {ins}", S=S, Iz0=I0, kE=kM * kI * kL,
                            kNote=", ".join(notes) or "tabela base Cu XLPE", tmax=70 if ins == "PVC" else 90,
                            tref=20 if m["g"] else 30, med="ground" if m["g"] else "air", duct=m.get("duct", False),
                            rhoRef=2.5, R20=R20[mat][S], alpha=ALPHA[mat], kac=1 if dc else KAC.get(S, 1),
                            X=0 if dc else m["x"], xNote="CC: sem reactância" if dc else f"X ≈ {nf(m['x'])} Ω/km (típico BT)",
                            npar=st["npar"], kSC=_kSC(mat, ins), mat=mat,
                            src="IEC 60364-5-52 / RTIEBT 523 (solo 20 °C 2,5 K·m/W, ar 30 °C)"))
        return out

    kV = st["kV"]
    if kV < 60:
        f = st["mtfam"]
        meth = st["m_mt"]
        air = meth == "A"
        if f in ("LXHIOV", "XHIOV"):
            mat = "Al" if f == "LXHIOV" else "Cu"
            for S, al_s, cu_s, al_a, cu_a in EC_MT_MONO:
                if air:
                    I0 = ec_mt_al_air(S, al_a, cu_a) if mat == "Al" else cu_a
                else:
                    I0 = al_s if mat == "Al" else cu_s
                kE = 0.9 if meth == "T" else 1
                note = "valor do catálogo" + (", em tubo ×0,90" if meth == "T" else "")
                if air and mat == "Al" and S < 400:
                    note = "estimado 0,78 × Cu (gralha no catálogo)"
                g = cable_geo(S, kV)
                out.append(dict(label=f"{S} mm² {f}", S=S, Iz0=I0, kE=kE, kNote=note, tmax=90, tref=30 if air else 20,
                                med="air" if air else "ground", duct=meth == "T", rhoRef=1.0, R20=R20[mat][S],
                                alpha=ALPHA[mat], kac=KAC.get(S, 1), X=g["X"], geo=g,
                                xNote=f"trevo juntivo: DMG = Ø exterior ≈ {nf(g['D'], 0)} mm", npar=st["npar"],
                                kSC=143 if mat == "Cu" else 94, mat=mat, cable=True,
                                src="Eurocabos Tabela VI, monopolares em trevo juntivo (solo 20 °C, ar 30 °C)"))
            return out
        mat = "Al" if f == "IEC_Al" else "Cu"
        for i, S in enumerate(MT_S):
            I0 = (MT_T["A"][i] if air else MT_T["D"][i]) * (1.28 if mat == "Cu" else 1)
            kE = 0.9 if meth == "T" else 1
            g = cable_geo(S, kV)
            out.append(dict(label=f"{S} mm² {mat} XLPE", S=S, Iz0=I0, kE=kE,
                            kNote=("cobre ×1,28" if mat == "Cu" else "tabela base Al") + (", em tubo ×0,90" if meth == "T" else ""),
                            tmax=90, tref=30 if air else 20, med="air" if air else "ground", duct=meth == "T", rhoRef=1.5,
                            R20=R20[mat][S], alpha=ALPHA[mat], kac=KAC.get(S, 1), X=g["X"], geo=g,
                            xNote=f"trevo juntivo: DMG = Ø exterior ≈ {nf(g['D'], 0)} mm", npar=st["npar"],
                            kSC=143 if mat == "Cu" else 94, mat=mat, cable=True,
                            src="IEC 60502-2 / catálogos (solo 20 °C 1,5 K·m/W, 0,8 m; ar 30 °C)"))
        return out
    mat = st["mat"]
    meth = st["m_hv"]
    kd = 0.92 if kV >= 400 else (0.95 if kV >= 220 else 1)
    for i, S in enumerate(HV_S):
        g = cable_geo(S, kV)
        note = ("dieléctrico ×" + nf(kd) if kd != 1 else "tabela base") + (", em tubo ×0,90" if meth == "T" else "")
        out.append(dict(label=f"{S} mm² {mat} XLPE", S=S, Iz0=HV_T[mat][i] * kd, kE=0.9 if meth == "T" else 1,
                        kNote=note, tmax=90, tref=20, med="ground", duct=meth == "T", rhoRef=1.0, R20=R20[mat][S],
                        alpha=ALPHA[mat], kac=KAC.get(S, 1), X=g["X"], geo=g,
                        xNote=f"trevo juntivo: DMG = Ø exterior ≈ {nf(g['D'], 0)} mm", npar=st["npar"],
                        kSC=143 if mat == "Cu" else 94, mat=mat, cable=True,
                        src="XLPE AT/MAT em trevo, solo 20 °C 1,0 K·m/W, cross-bonding (indicativo)"))
    return out


def evaluate(c, st):
    fT = fS = fG = 1.0
    if c["med"] != "oh":
        fT = temp_f(c["tmax"], st["ta"], c["tref"])
        if c.get("pv"):
            fT = min(1.0, fT)
        if c["med"] == "ground":
            fS = soil_f(st["rho"], c.get("duct", False), c["rhoRef"])
            fG = group_f(st["ncirc"] * c["npar"], True, st["sp"])
        else:
            fG = group_f(st["ncirc"] * c["npar"], False, 0)
    ncl = st.get("ncl", 1)
    Iz = c["Iz0"] * c["kE"] * fT * fS * fG * c["npar"] * ncl
    Ib = st["I"]
    Id = Ib * st["fd"]
    load = Id / Iz if Iz > 0 else math.inf
    theta = st["ta"] + (c["tmax"] - st["ta"]) * min(1.0, (Ib / Iz) ** 2 if Iz > 0 else 1.0)
    R = c["R20"] * (1 + c["alpha"] * (theta - 20)) * c["kac"] / c["npar"] / ncl
    X = (c["X"] if c.get("xb") else c["X"] / c["npar"]) / ncl
    sin = math.sqrt(max(0.0, 1 - st["cos"] ** 2))
    L = st["Lkm"]
    if st["sys"] == "3f":
        dU = math.sqrt(3) * Ib * L * (R * st["cos"] + X * sin)
        Pw = 3 * R * L * Ib * Ib
    elif st["sys"] == "1f":
        dU = 2 * Ib * L * (R * st["cos"] + X * sin)
        Pw = 2 * R * L * Ib * Ib
    else:
        dU = 2 * Ib * L * R
        Pw = 2 * R * L * Ib * Ib
    dUp = dU / st["U"] * 100
    PlossKW = Pw / 1000
    lossP = PlossKW / st["Pkw"] * 100 if st["Pkw"] > 0 else 0
    tau = st["heq"] * st["ftau"]
    Eloss = PlossKW * tau / 1000
    Eprod = st["Pkw"] * st["heq"] / 1000
    lossE = Eloss / Eprod * 100 if Eprod > 0 else 0
    eur = Eloss * st["price"]
    r = st["rate"] / 100
    ann = (1 - (1 + r) ** (-st["life"])) / r if r > 0 else st["life"]
    npv = eur * ann
    Smin, okSC = None, True
    Seff = c["S"] * (c["npar"] if c.get("xb") else 1) * ncl
    if st["icc"] > 0:
        Smin = st["icc"] * 1000 * math.sqrt(st["tcc"]) / c["kSC"]
        okSC = Seff >= Smin
    In, okProt = None, True
    if st["bt"] and st["prot"] != "none":
        In = next((v for v in INS if v >= Id / c["npar"]), None)
        lim = Iz / c["npar"] * (1 if st["prot"] == "disj" else 1.45 / 1.6)
        okProt = In is not None and In <= lim
    okTh = Id <= Iz and okProt
    okDU = dUp <= st["du"]
    okLoss = (not st["lossOn"]) or lossP <= st["lossMax"]
    chg = None
    if c.get("cable") and st["sys"] == "3f":
        C = 2 * math.pi * 8.854e-12 * 2.5 / math.log(c["geo"]["Di"] / c["geo"]["dc"]) * 1000
        w = 2 * math.pi * 50
        chg = dict(C=C, Ic=st["U"] / math.sqrt(3) * w * C * L * c["npar"],
                   Q=st["U"] ** 2 * w * C * L * c["npar"] / 1e6)
    mom = (st["U"] / 1000) ** 2 / (100 * (R + X * (sin / st["cos"]))) if st["sys"] == "3f" else None
    return dict(c=c, ncl=ncl, fT=fT, fS=fS, fG=fG, Iz=Iz, Ib=Ib, Id=Id, load=load, theta=theta, R=R, X=X, sin=sin,
                dU=dU, dUp=dUp, PlossKW=PlossKW, lossP=lossP, tau=tau, Eloss=Eloss, Eprod=Eprod, lossE=lossE,
                eur=eur, ann=ann, npv=npv, Smin=Smin, Seff=Seff, okSC=okSC, In=In, okProt=okProt, okTh=okTh,
                okDU=okDU, okLoss=okLoss, okAll=okTh and okDU and okLoss and okSC, chg=chg, mom=mom)


def make_state(**kw):
    """Completa o estado com corrente e sistema."""
    st = dict(kw)
    lv = st["level"]
    L = LEVELS[lv]
    st["bt"] = lv.startswith("bt")
    uin = st["Uin"]
    st["U"] = uin * 1000 if L["u"] == "kV" else uin
    st["kV"] = uin if L["u"] == "kV" else uin / 1000
    st["sys"] = "dc" if L["sys"] == "dc" else ("1f" if st["U"] == 230 else "3f")
    if st["sys"] == "dc":
        st["cos"] = 1.0
    st["cos"] = min(1.0, max(0.5, st["cos"] or 1.0))
    P = st["Pkw"]
    st["I"] = P * 1000 / (math.sqrt(3) * st["U"] * st["cos"]) if st["sys"] == "3f" else P * 1000 / (st["U"] * st["cos"])
    return st


def compute(st):
    cands = build_cands(st)
    ev = [evaluate(c, st) for c in cands]
    sel = next((i for i, e in enumerate(ev) if e["okAll"]), -1)
    th = next((i for i, e in enumerate(ev) if e["okTh"]), -1)
    sug = None
    if sel < 0 and ev:
        if st["net"] == "sub" or st["bt"]:
            for n in range(st["npar"] + 1, 13):
                s2 = dict(st, npar=n)
                e2 = [evaluate(c, s2) for c in build_cands(s2)]
                k = next((i for i, e in enumerate(e2) if e["okAll"]), -1)
                if k >= 0:
                    sug = dict(n=n, label=e2[k]["c"]["label"], kind="par")
                    break
        else:
            for n in range(st["nb"] + 1, 5):
                s2 = dict(st, nb=n)
                e2 = [evaluate(c, s2) for c in build_cands(s2)]
                k = next((i for i, e in enumerate(e2) if e["okAll"]), -1)
                if k >= 0:
                    sug = dict(n=n, label=e2[k]["c"]["label"], kind="feixe")
                    break
    return dict(ev=ev, sel=sel, th=th, sug=sug, crit=crit(ev, sel, th))


def crit(ev, sel, th):
    if sel < 0:
        return None
    if sel == th:
        return "aquecimento (critério térmico)"
    names = []
    for e in ev[max(0, th):sel]:
        if not e["okDU"]:
            names.append("queda de tensão")
        if not e["okLoss"]:
            names.append("perdas")
        if not e["okSC"]:
            names.append("curto-circuito")
    out = []
    for n in names:
        if n not in out:
            out.append(n)
    return " e ".join(out) or "aquecimento"


def alerts_for(st, e, sel, sug):
    A = []
    c = e["c"]
    if sel < 0:
        if sug:
            what = (f"com <b>{sug['n']} cabos em paralelo por fase</b>" if sug["kind"] == "par"
                    else f"com <b>feixe de {sug['n']} condutores</b>")
            A.append(("err", f"<b>Nenhum condutor da tabela cumpre todos os critérios.</b> Solução possível {what}: {sug['label']}."))
        else:
            A.append(("err", "<b>Nenhum condutor da tabela cumpre todos os critérios.</b> Considerar subir o nível de tensão ou dividir a potência por mais circuitos."))
    if 0.9 < e["load"] <= 1:
        A.append(("warn", f"Utilização térmica de {nf(e['load'] * 100, 0)} %. Margem reduzida para harmónicos, sobrecargas sazonais e incerteza na resistividade do solo."))
    if not e["okDU"]:
        A.append(("warn", f"Queda de tensão de {nf(e['dUp'])} % acima do limite de projeto ({nf(st['du'], 1)} %)."))
    if st["level"] == "bt_ca" and e["dUp"] > 8:
        A.append(("err", "Queda de tensão acima de 8 %, limite do RTIEBT 525 para instalações alimentadas por posto de transformação próprio."))
    if st["level"] == "bt_cc" and e["dUp"] > 3:
        A.append(("warn", "Em CC FV a boa prática (IEC 62548) é manter a queda de tensão entre 1 e 3 % para não afastar o inversor do ponto MPPT."))
    if e["lossP"] > 3:
        A.append(("err", f"Perdas de {nf(e['lossP'])} % à potência nominal. Valor elevado para uma ligação de central."))
    elif e["lossP"] > 1.5:
        A.append(("warn", f"Perdas de {nf(e['lossP'])} % à potência nominal. Avaliar a secção seguinte (ver poupança VAL)."))
    if st["icc"] > 0 and not e["okSC"]:
        A.append(("err", f"Curto-circuito: secção mínima de {nf(e['Smin'], 0)} mm² para {nf(st['icc'], 1)} kA durante {nf(st['tcc'])} s."))
    if st["bt"] and st["prot"] != "none" and not e["okProt"]:
        A.append(("err", "Proteção: não existe calibre normalizado com Ib ≤ In ≤ Iz (RTIEBT 433)."))
    if e["chg"]:
        Pmw = st["Pkw"] / 1000
        if e["chg"]["Q"] > 0.1 * Pmw:
            A.append(("warn", f"Potência reativa capacitiva do cabo de {nf(e['chg']['Q'])} Mvar ({nf(e['chg']['Q'] / Pmw * 100, 0)} % de P). Prever compensação e verificar sobretensões em vazio."))
        elif st["kV"] >= 60:
            A.append(("info", f"Potência reativa capacitiva do cabo: {nf(e['chg']['Q'])} Mvar. Considerar no balanço reativo no ponto de ligação."))
    if c["med"] == "oh":
        if st["kV"] >= 400 and st["nb"] < 2:
            A.append(("err", "A 400 kV é obrigatório feixe (habitualmente duplo ou triplo) para limitar o efeito de coroa e o ruído."))
        elif st["kV"] >= 220 and st["nb"] < 2:
            A.append(("warn", "A 220 kV recomenda-se feixe duplo ou condutor de grande diâmetro para limitar o efeito de coroa."))
        if st["kV"] >= 150 and st["nb"] == 1 and c["dmm"] < 20:
            A.append(("warn", f"Diâmetro de {nf(c['dmm'], 1)} mm reduzido para {st['kV']:g} kV. Verificar o gradiente superficial (coroa)."))
        if e["ncl"] > 1:
            n1 = e["load"] * 2
            if n1 > 1:
                A.append(("warn", f"Critério N-1: com um circuito fora de serviço o outro ficaria a {nf(n1 * 100, 0)} %. Prever redução de produção nessa contingência ou condutor maior."))
            else:
                A.append(("ok", f"Critério N-1 cumprido: um só circuito transporta a potência total ({nf(n1 * 100, 0)} %)."))
        A.append(("info", "Linha aérea: confirmar cálculo mecânico, distâncias de segurança (RSLEAT) e capacidade sazonal adotada pelo operador."))
    if st["bt"] and c.get("pv"):
        A.append(("info", "Cabo H1Z2Z2-K (EN 50618) estipulado para 1,5 kV CC. Fator de temperatura limitado a 1,0 abaixo de 60 °C."))
    if st.get("npar", 1) > 4 and c["med"] != "oh":
        A.append(("info", f"{st['npar']} cabos em paralelo por fase. Avaliar subir o nível de tensão ou dividir em circuitos independentes."))
    if st["sys"] != "dc" and st["cos"] < 0.9:
        A.append(("info", "cos φ inferior a 0,9. A componente reativa aumenta a corrente e a queda de tensão."))
    r = TECH[st["tech"]]["r"]
    if not (r[0] <= st["heq"] <= r[1]):
        A.append(("warn", f"Horas equivalentes ({nf(st['heq'], 0)} h) fora da gama típica em Portugal para {TECH[st['tech']]['n']} ({r[0]} a {r[1]} h)."))
    if c["med"] != "oh" and e["theta"] > c["tmax"] - 5 and e["load"] <= 1:
        A.append(("info", f"Temperatura estimada do condutor de {nf(e['theta'], 0)} °C, próxima do máximo ({c['tmax']} °C)."))
    if sel >= 0 and not any(a[0] in ("err", "warn") for a in A):
        A.insert(0, ("ok", "Todos os critérios cumpridos com margem."))
    return A


# ---------------------------------------------------------------- justificação
def _step(t, why, fx):
    w = f"<p>{why}</p>" if why else ""
    return f'<div class="step"><h4>{t}</h4>{w}<div class="fx">{fx}</div></div>'


def _ok(b):
    return '<span class="okc">✓ cumpre</span>' if b else '<span class="errc">✕ não cumpre</span>'


def justification_html(e, st, is_sel):
    c = e["c"]
    S = []
    U = st["U"]
    P = st["Pkw"] * 1000
    L = st["Lkm"]
    if st["sys"] == "3f":
        S.append(_step("Corrente de serviço", "Corrente que a central injeta à potência máxima.",
                       f"I = P / (√3 × U × cos φ)<br>I = {nf(P, 0)} W / (1,732 × {nf(U, 0)} V × {nf(st['cos'])})<br>I = <b>{nf(e['Ib'], 1)} A</b>"))
    elif st["sys"] == "1f":
        S.append(_step("Corrente de serviço", "Circuito monofásico.",
                       f"I = P / (U × cos φ) = {nf(P, 0)} / ({nf(U, 0)} × {nf(st['cos'])}) = <b>{nf(e['Ib'], 1)} A</b>"))
    else:
        S.append(_step("Corrente de serviço", "Corrente contínua: não há cos φ.",
                       f"I = P / U = {nf(P, 0)} W / {nf(U, 0)} V = <b>{nf(e['Ib'], 1)} A</b>"))
    if st["fd"] != 1:
        S.append(_step("Corrente de dimensionamento", "Margem regulamentar para a corrente máxima dos módulos.",
                       f"Id = I × {nf(st['fd'])} = <b>{nf(e['Id'], 1)} A</b>"))
    if c["med"] == "oh":
        dup = " × 2 circuitos" if e["ncl"] > 1 else ""
        S.append(_step("Capacidade do condutor", "Valor nominal tabelado por condutor, multiplicado pelo nº de condutores do feixe e de circuitos.",
                       f"Iz = {nf(c['Iz0'], 0)} A × {st['nb']}{dup} = <b>{nf(e['Iz'], 0)} A</b><br>Id = {nf(e['Id'], 1)} A ≤ Iz → {_ok(e['okTh'])}<br>Utilização = {nf(e['load'] * 100, 0)} %"))
    else:
        parts = [f"I₀ = {nf(c['Iz0'], 0)} A (tabela)"]
        if c["kE"] != 1:
            parts.append(f"k_cabo = {nf(c['kE'], 3)} ({c['kNote']})")
        lim = " (limitado a 1)" if c.get("pv") else ""
        parts.append(f"fθ = √(({c['tmax']} − {nf(st['ta'], 0)}) / ({c['tmax']} − {c['tref']})) = {nf(e['fT'], 3)}{lim}")
        if c["med"] == "ground":
            parts.append(f"f_solo ({nf(st['rho'], 1)} K·m/W, ref. {nf(c['rhoRef'], 1)}) = {nf(e['fS'], 3)}")
        parts.append(f"f_agrup ({st['ncirc'] * c['npar']} cabos/circuitos) = {nf(e['fG'])}")
        if c["npar"] > 1:
            parts.append(f"n paralelos = {c['npar']}")
        S.append(_step("Corrente admissível corrigida",
                       "A tabela vale para condições de referência. Corrige-se para a temperatura real, o solo e o agrupamento, porque cabos juntos aquecem-se uns aos outros.",
                       "<br>".join(parts) + f"<br>Iz = <b>{nf(e['Iz'], 0)} A</b>"))
        th = f"Id = {nf(e['Id'], 1)} A ≤ Iz = {nf(e['Iz'], 0)} A → {_ok(e['Id'] <= e['Iz'])}<br>Utilização = {nf(e['load'] * 100, 0)} %"
        if st["bt"] and st["prot"] != "none":
            th += f"<br>Proteção: Ib ≤ In ≤ Iz{' × 1,45/1,6' if st['prot'] == 'fus' else ''}<br>In = {e['In'] if e['In'] else '–'} A → {_ok(e['okProt'])}"
        S.append(_step("Critério térmico (RTIEBT 433 e 523)", "O cabo tem de transportar a corrente sem ultrapassar a temperatura máxima do isolamento.", th))
    eq = " (equivalente dos 2 circuitos)" if e["ncl"] > 1 else ""
    S.append(_step("Resistência à temperatura de serviço", "A resistência sobe com a temperatura. Estima-se a temperatura do condutor pela carga real.",
                   f"θ ≈ θa + (θmax − θa) × (I/Iz)² = {nf(st['ta'], 0)} + ({c['tmax']} − {nf(st['ta'], 0)}) × ({nf(e['Ib'], 0)}/{nf(e['Iz'], 0)})² = {nf(e['theta'], 0)} °C"
                   f"<br>R = R20 × [1 + α(θ − 20)] × k_ca / n<br>R = {nf(c['R20'], 4)} × [1 + {nf(c['alpha'], 5)}×({nf(e['theta'], 0)} − 20)] × {nf(c['kac'])} / {c['npar'] * e['ncl']} = <b>{nf(e['R'], 4)} Ω/km</b>{eq}"))
    if st["sys"] != "dc":
        if c["med"] == "oh":
            pre = f"{nf(e['X'] * 2, 3)} / 2 circuitos = " if e["ncl"] > 1 else ""
            S.append(_step("Reactância da linha", "Depende da distância entre fases e do raio equivalente do feixe.",
                           f"X = 0,0628 × ln(DMG / RMG) = 0,0628 × ln({nf(st['gmd'])} / {nf(c['gmrEq'], 4)})<br>X = {pre}<b>{nf(e['X'], 3)} Ω/km</b> (Ø {nf(c['dmm'], 1)} mm)"))
        else:
            dv = f" / {c['npar']}" if c["npar"] > 1 else ""
            S.append(_step("Reactância", "Cabos unipolares em trevo." if c.get("cable") else "Valor típico de cabos BT.",
                           f"{c['xNote']}<br>X = {nf(c['X'], 3)}{dv} = <b>{nf(e['X'], 3)} Ω/km</b>"))
    okdu = _ok(e["okDU"])
    if st["sys"] == "3f":
        S.append(_step("Queda de tensão", "Diferença de tensão entre as extremidades da ligação.",
                       f"ΔU = √3 × I × L × (R cos φ + X sen φ)<br>ΔU = 1,732 × {nf(e['Ib'], 1)} × {nf(L, 3)} × ({nf(e['R'], 4)}×{nf(st['cos'])} + {nf(e['X'], 3)}×{nf(e['sin'])})"
                       f"<br>ΔU = {nf(e['dU'], 1)} V → <b>{nf(e['dUp'])} %</b> (limite {nf(st['du'], 1)} %) {okdu}"))
    elif st["sys"] == "1f":
        S.append(_step("Queda de tensão", "Ida e volta do circuito.",
                       f"ΔU = 2 × I × L × (R cos φ + X sen φ) = {nf(e['dU'], 1)} V → <b>{nf(e['dUp'])} %</b> {okdu}"))
    else:
        S.append(_step("Queda de tensão", "Em CC conta o condutor de ida e o de volta.",
                       f"ΔU = 2 × I × L × R = 2 × {nf(e['Ib'], 1)} × {nf(L, 3)} × {nf(e['R'], 4)}<br>ΔU = {nf(e['dU'], 1)} V → <b>{nf(e['dUp'])} %</b> (limite {nf(st['du'], 1)} %) {okdu}"))
    m = 3 if st["sys"] == "3f" else 2
    lim = f" (limite {nf(st['lossMax'], 1)} %) {_ok(e['okLoss'])}" if st["lossOn"] else ""
    S.append(_step("Perdas à potência nominal", "Energia dissipada em calor nos condutores (efeito Joule).",
                   f"Pp = {m} × R × L × I² = {m} × {nf(e['R'], 4)} × {nf(L, 3)} × {nf(e['Ib'], 1)}²<br>Pp = <b>{nf(e['PlossKW'])} kW</b> = {nf(e['lossP'])} % de P{lim}"))
    S.append(_step("Perdas anuais de energia", "Usam-se as horas de perdas τ, porque as perdas variam com o quadrado da potência.",
                   f"τ = h_eq × f = {nf(st['heq'], 0)} × {nf(st['ftau'])} = {nf(e['tau'], 0)} h<br>E_perdas = {nf(e['PlossKW'])} kW × {nf(e['tau'], 0)} h = <b>{nf(e['Eloss'])} MWh/ano</b>"
                   f"<br>E_produzida = {nf(st['Pkw'] / 1000)} MW × {nf(st['heq'], 0)} h = {nf(e['Eprod'], 0)} MWh<br>Perdas = {nf(e['lossE'])} % da energia"
                   f"<br>Valor = {nf(e['Eloss'])} × {nf(st['price'], 0)} €/MWh = {nf(e['eur'], 0)} €/ano<br>VAL ({st['life']} anos, {nf(st['rate'], 1)} %) = {nf(e['eur'], 0)} × {nf(e['ann'])} = <b>{nf(e['npv'], 0)} €</b>"))
    if st["icc"] > 0:
        S.append(_step("Curto-circuito (aquecimento adiabático)", "O condutor tem de suportar o defeito até a proteção atuar.",
                       f"S_min = Icc × √t / k = {nf(st['icc'] * 1000, 0)} × √{nf(st['tcc'])} / {c['kSC']}<br>S_min = {nf(e['Smin'], 0)} mm² ≤ {nf(e['Seff'], 0)} mm² → {_ok(e['okSC'])}"))
    if e["chg"]:
        S.append(_step("Efeito capacitivo do cabo", "Os cabos MT e AT geram potência reativa mesmo sem carga.",
                       f"C ≈ 2π ε₀ εr / ln(Di/dc) = {nf(e['chg']['C'] * 1e6, 3)} µF/km<br>Q = U² × ω × C × L = <b>{nf(e['chg']['Q'])} Mvar</b>; Ic = {nf(e['chg']['Ic'], 1)} A"))
    if e["mom"]:
        S.append(_step("Momento elétrico", "Potência × distância que provoca 1 % de queda de tensão.",
                       f"M = U² / [100 × (R + X tg φ)] = <b>{nf(e['mom'], 1)} MW·km</b>"))
    title = c["label"]
    if c["med"] == "oh":
        title = (f"{st['nb']} × " if st["nb"] > 1 else "") + title + (" · linha dupla" if e["ncl"] > 1 else "")
    hyp = [f"Fonte: {c.get('src', '')}."]
    if c["med"] == "oh":
        hyp.append(f"Condutor a {c['tmax']} °C máx.; R20 ≈ {'28,9' if c.get('fam') == 'ACSR' else '33,1'} / S Ω/km; RMG = 0,8 r; feixe com 0,4 m.")
        if e["ncl"] > 1:
            hyp.append("Linha dupla: impedância equivalente = metade; acoplamento mútuo desprezado.")
    else:
        if c["med"] == "ground":
            hyp.append(f"Resistividade térmica de referência da tabela: {nf(c['rhoRef'], 1)} K·m/W.")
        hyp.append("Valores tabelados a validar com o fabricante e cálculo IEC 60287 para projeto de execução.")
    hyp.append("Harmónicos e efeitos de proximidade detalhados não modelados.")
    sel_txt = " · recomendada" if is_sel else ""
    return (f'<div class="ptitle">{title}{sel_txt}</div><div class="steps">{"".join(S)}</div>'
            f'<div class="hyp"><b>Hipóteses</b><ul>{"".join("<li>" + h + "</li>" for h in hyp)}</ul></div>')
