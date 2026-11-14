# -*- coding: utf-8 -*-
"""
Tecneira · Dimensionamento de Cabos e Linhas para centrais solares e parques eólicos.
Criado por Jorge Ramos para uso privado.
Executar localmente:  streamlit run app.py
"""
import base64
import math
import pathlib
from datetime import date

import pandas as pd
import streamlit as st

import engine as E
from engine import nf

ROOT = pathlib.Path(__file__).parent
LOGO = ROOT / "assets" / "logo_tecneira.png"
ICON = ROOT / "assets" / "icon.png"

st.set_page_config(
    page_title="Tecneira · Dimensionamento de Cabos e Linhas",
    page_icon=str(ICON) if ICON.exists() else "⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


def b64(p):
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else ""


LOGO_B64 = b64(LOGO)

# ------------------------------------------------------------------ estilo (vidro, tipografia Apple)
CSS = """
<style>
:root{--tb:#1E56A0;--tb2:#163F78;--tg:#8DC63F;--ink:#1d1d1f;--muted:#6e6e73;
 --ok:#1d8a3a;--ok-s:rgba(52,199,89,.15);--warn:#a95a00;--warn-s:rgba(255,159,10,.17);
 --err:#d70015;--err-s:rgba(255,59,48,.12);--info:#3f3dbd;--info-s:rgba(94,92,230,.11);
 --glass:rgba(255,255,255,.62);--edge:rgba(255,255,255,.75);--field:rgba(118,118,128,.10);
 --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace}
html,body,[class*="css"],.stApp{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Roboto,"Helvetica Neue",sans-serif}
.stApp{background:
  radial-gradient(1100px 620px at 8% -12%,rgba(30,86,160,.16),transparent 60%),
  radial-gradient(900px 520px at 100% -6%,rgba(141,198,63,.20),transparent 62%),
  radial-gradient(700px 500px at 60% 110%,rgba(30,86,160,.08),transparent 60%),#f4f6f9}
[data-testid="stHeader"]{background:rgba(244,246,249,.55);-webkit-backdrop-filter:blur(20px) saturate(180%);backdrop-filter:blur(20px) saturate(180%)}
[data-testid="stSidebar"]>div:first-child{background:rgba(255,255,255,.58);-webkit-backdrop-filter:blur(26px) saturate(180%);backdrop-filter:blur(26px) saturate(180%);border-right:1px solid var(--edge)}
[data-testid="stSidebar"] h3{font-size:.72rem;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);margin:1.1rem 0 .2rem;font-weight:650}
.block-container{padding-top:1.4rem;max-width:1500px}
.glass{background:var(--glass);-webkit-backdrop-filter:blur(22px) saturate(180%);backdrop-filter:blur(22px) saturate(180%);
 border:1px solid var(--edge);border-radius:22px;box-shadow:inset 0 1px 0 rgba(255,255,255,.9),0 12px 34px rgba(17,38,77,.08);padding:18px 22px;margin-bottom:14px}
.hdr{display:flex;align-items:center;gap:26px;flex-wrap:wrap;padding:16px 26px}
.hdr img{height:70px;width:auto}
.hdr .t{flex:1;min-width:260px}
.hdr h1{font-size:clamp(1.5rem,2.6vw,2.15rem);line-height:1.08;letter-spacing:-.025em;margin:0;color:var(--ink);font-weight:700;padding:0}
.hdr p{margin:.25rem 0 0;color:var(--muted);font-size:.92rem}
.badge{display:inline-flex;align-items:center;gap:8px;padding:7px 14px;border-radius:980px;font-size:.78rem;font-weight:600;
 background:linear-gradient(135deg,rgba(30,86,160,.12),rgba(141,198,63,.18));color:var(--tb2);border:1px solid rgba(255,255,255,.8)}
.badge i{width:8px;height:8px;border-radius:50%;background:var(--tg);display:inline-block;box-shadow:0 0 0 3px rgba(141,198,63,.25)}
.stButton>button,.stDownloadButton>button{border-radius:980px!important;font-weight:550;border:1px solid rgba(30,86,160,.18)!important;
 background:rgba(255,255,255,.7)!important;-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);transition:transform .1s ease-out,box-shadow .2s}
.stButton>button:active,.stDownloadButton>button:active{transform:scale(.97)}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#1E56A0,#2C6CC4)!important;color:#fff!important;border:0!important;box-shadow:0 6px 18px rgba(30,86,160,.28)}
.lbl{font-size:.72rem;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);font-weight:650;margin:0 0 6px}
.big{font-size:clamp(1.55rem,2.6vw,2.2rem);font-weight:750;letter-spacing:-.025em;line-height:1.1;color:var(--ink)}
.sub{color:var(--muted);font-size:.88rem;margin-top:4px}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0 2px}
.chip{font-size:.74rem;font-weight:650;padding:4px 11px;border-radius:980px}
.chip.ok{background:var(--ok-s);color:var(--ok)}.chip.err{background:var(--err-s);color:var(--err)}.chip.na{background:var(--field);color:var(--muted)}
.metrics{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin-top:14px}
.m{background:rgba(255,255,255,.55);border:1px solid var(--edge);border-radius:14px;padding:10px 12px}
.m .k{font-size:.7rem;color:var(--muted)}.m .v{font-size:1.1rem;font-weight:650;letter-spacing:-.01em;font-variant-numeric:tabular-nums;color:var(--ink)}
.m .v small{font-size:.74rem;font-weight:400;color:var(--muted)}
.alerts{list-style:none;padding:0;margin:14px 0 0;display:flex;flex-direction:column;gap:8px}
.alerts li{padding:10px 13px;border-radius:13px;font-size:.86rem;line-height:1.42;color:var(--ink)}
.alerts li.err{background:var(--err-s)}.alerts li.warn{background:var(--warn-s)}.alerts li.ok{background:var(--ok-s)}.alerts li.info{background:var(--info-s)}
.reco{margin-top:12px;font-size:.87rem;background:rgba(30,86,160,.09);padding:12px 14px;border-radius:13px;color:var(--ink)}
.st-key-panel{position:sticky;top:3.8rem}
.ptitle{font-size:1.2rem;font-weight:720;letter-spacing:-.02em;margin:0 0 12px;color:var(--ink)}
.steps{counter-reset:s}
.step{position:relative;padding:0 0 13px 30px}
.step:before{counter-increment:s;content:counter(s);position:absolute;left:0;top:1px;width:20px;height:20px;border-radius:50%;
 background:linear-gradient(135deg,#1E56A0,#2C6CC4);color:#fff;font-size:.68rem;font-weight:700;display:grid;place-items:center}
.step h4{margin:0 0 2px;font-size:.9rem;font-weight:650;color:var(--ink);padding:0}
.step p{margin:0 0 6px;font-size:.79rem;color:var(--muted)}
.fx{font-family:var(--mono);font-size:.75rem;background:rgba(255,255,255,.6);border:1px solid var(--edge);border-radius:10px;padding:8px 10px;line-height:1.62;overflow-x:auto;color:var(--ink)}
.fx b{color:var(--tb)}.okc{color:var(--ok);font-weight:700}.errc{color:var(--err);font-weight:700}
.hyp{font-size:.75rem;color:var(--muted);border-top:1px solid rgba(0,0,0,.07);padding-top:10px;margin-top:4px}
.hyp ul{padding-left:18px;margin:6px 0}
.foot{color:var(--muted);font-size:.76rem;line-height:1.5;padding:6px 4px 30px}
.foot b{color:var(--ink)}
.side-sign{font-size:.74rem;color:var(--muted);margin-top:18px;padding-top:12px;border-top:1px solid rgba(0,0,0,.07)}
@media (prefers-reduced-transparency:reduce){.glass,[data-testid="stSidebar"]>div:first-child{background:#fff;backdrop-filter:none;-webkit-backdrop-filter:none}}
@media (prefers-reduced-motion:reduce){.stButton>button{transition:none}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

ss = st.session_state


# ------------------------------------------------------------------ estado e valores por defeito
def lv_def():
    return E.LEVELS[ss.level]["d"]


def apply_medium():
    probe = dict(net=ss.net or "sub", bt=ss.level.startswith("bt"), lvfam=ss.lvfam, m_lv=ss.m_lv, inst=ss.inst,
                 kV=float(ss.U) if E.LEVELS[ss.level]["u"] == "kV" else ss.U / 1000, m_mt=ss.m_mt)
    md = E.medium(probe)
    ss.ta = 20.0 if md == "ground" else (50.0 if md == "pv" else 30.0)


def apply_net():
    if (ss.net or "sub") == "aer" and not ss.level.startswith("bt"):
        kV = int(ss.U)
        ss.gmd = float(E.KV[kV]["gmd"])
        ss.nb = E.NB[kV]
    ss.ncl = "Simples"
    apply_medium()


def apply_level():
    L = E.LEVELS[ss.level]
    d = L["d"]
    ss.U = L["Ud"]
    for k in ("P", "L", "fd", "du", "icc", "cos"):
        ss[k] = float(d[k])
    if "prot" in d:
        ss.prot = d["prot"]
    for k in ("lvfam", "constr", "inst", "mtfam", "m_mt", "mat", "m_hv"):
        if k in d:
            ss[k] = d[k]
    if ss.level == "bt_cc" and ss.lvfam not in E.LV_FAMS:
        ss.lvfam = "LXV"
    if ss.level == "bt_ca" and ss.lvfam == "PV":
        ss.lvfam = "LXV"
    ss.net = d["net"]
    ss.npar = 1
    ss.rho = 1.0 if ss.level in ("bt_cc", "bt_ca", "at", "mat") or ss.mtfam in ("LXHIOV", "XHIOV") else 1.5
    apply_net()


def on_tech():
    if not ss.tech:
        ss.tech = "pv_fix"
    t = E.TECH[ss.tech]
    ss.heq, ss.ftau = t["h"], t["f"]


def on_U():
    if (ss.net or "sub") == "aer" and not ss.level.startswith("bt"):
        kV = int(ss.U)
        ss.gmd = float(E.KV[kV]["gmd"])
        ss.nb = E.NB[kV]


def on_net():
    if not ss.net:
        ss.net = "sub"
    apply_net()


DEFAULTS = dict(
    tech="pv_fix", heq=1650.0, ftau=0.65, price=55.0, life=30, rate=7.0, level="mt", U=30, P=20.0, L=5.0, cos=0.95,
    fd=1.0, net="sub", lvfam="LXV", constr="uni", inst="sub", m_lv="D2", mat="Al", ins="XLPE", mtfam="LXHIOV",
    m_mt="D", m_hv="D", ncirc=1, sp=0.5, npar=1, rho=1.0, ta=20.0, fam="ACSR", nb=1, gmd=1.8, ncl="Simples",
    du=2.0, lossOn=True, lossMax=1.0, icc=12.5, tcc=0.5, prot="disj",
    q_kV=30, q_fam="ALL", q_ncl="Simples", q_nb=1, q_gmd=1.8, q_P=20.0, q_cos=0.95, q_L=8.0, q_ta=30.0,
    q_du=5.0, q_loss=2.0, q_heq=1650.0, q_tau=0.65, t_sel="LXHIOV",
)
_first = not ss.get("_init")
# Mantém os valores de widgets que não são desenhados nesta execução (Streamlit apaga-os por defeito).
for _k, _v in DEFAULTS.items():
    ss[_k] = ss[_k] if _k in ss else _v
if _first:
    apply_level()
    ss._init = True


# ------------------------------------------------------------------ barra lateral: dados de entrada
with st.sidebar:
    st.markdown("### 1 · Central e perdas")
    st.segmented_control("Tecnologia", list(E.TECH), format_func=lambda k: E.TECH[k]["lbl"], key="tech", on_change=on_tech)
    c1, c2 = st.columns(2)
    c1.number_input("Horas equivalentes (h)", 100.0, 8760.0, step=10.0, format="%.0f", key="heq", help="Produção anual ÷ potência nominal")
    c2.number_input("Fator τ / h eq", 0.2, 1.0, step=0.01, key="ftau", help="Horas de perdas ÷ horas equivalentes")
    c1, c2, c3 = st.columns(3)
    c1.number_input("€/MWh", 0.0, 1000.0, step=1.0, format="%.0f", key="price")
    c2.number_input("Vida (anos)", 1, 60, step=1, key="life")
    c3.number_input("Taxa (%)", 0.0, 30.0, step=0.1, key="rate")

    st.markdown("### 2 · Ligação")
    st.selectbox("Nível de tensão", list(E.LEVELS), format_func=lambda k: E.LEVELS[k]["nome"], key="level", on_change=apply_level)
    Ldef = E.LEVELS[ss.level]
    bt = ss.level.startswith("bt")
    c1, c2 = st.columns(2)
    c1.selectbox("Tensão nominal", Ldef["U"], format_func=lambda u: f"{u} {Ldef['u']}", key="U", on_change=on_U)
    c2.number_input("Potência (kW)" if bt else "Potência (MW)", 0.0, 1e6, step=1.0 if bt else 0.5, key="P")
    c1, c2 = st.columns(2)
    c1.number_input("Comprimento (m)" if bt else "Comprimento (km)", 0.0, 1e5, step=10.0 if bt else 0.5, key="L")
    if Ldef["sys"] != "dc":
        c2.number_input("cos φ", 0.5, 1.0, step=0.01, key="cos", help="0,95 cobre a capacidade reativa exigida")
    st.number_input("Fator de dimensionamento", 1.0, 2.0, step=0.05, key="fd",
                    help="1,25 × Isc em CC FV (RTIEBT 712 / IEC 62548); 1,0 em CA")
    if len(Ldef["nets"]) > 1:
        st.segmented_control("Tipo de rede", Ldef["nets"], format_func=lambda k: "Subterrânea · cabo" if k == "sub" else "Aérea",
                             key="net", on_change=on_net)
    net = ss.net or "sub"

    st.markdown("### 3 · Condutor e instalação")
    if net == "aer":
        if bt:
            st.caption("Rede aérea BT em cabo torçado LXS.")
        else:
            st.selectbox("Família de condutor", ["ACSR", "AAAC", "ALL"],
                         format_func=lambda k: {"ACSR": "ACSR · alumínio-aço", "AAAC": "AAAC · Aster", "ALL": "ACSR + AAAC"}[k], key="fam")
            c1, c2 = st.columns(2)
            c1.selectbox("Linha", ["Simples", "Dupla"], key="ncl", help="Dupla: 2 circuitos (ternos) em paralelo")
            c2.selectbox("Condutores por fase", [1, 2, 3, 4], key="nb")
            st.number_input("Distância média geométrica entre fases (m)", 0.3, 30.0, step=0.1, key="gmd")
    else:
        if bt:
            fams = list(E.LV_FAMS) if ss.level == "bt_cc" else [k for k in E.LV_FAMS if k != "PV"]
            st.selectbox("Tipo de cabo", fams, format_func=lambda k: E.LV_FAMS[k], key="lvfam", on_change=apply_medium)
            if ss.lvfam in E.EC_LV:
                st.selectbox("Constituição", list(E.EC_CONSTR), format_func=lambda k: E.EC_CONSTR[k], key="constr")
                st.selectbox("Instalação", list(E.EC_INST), format_func=lambda k: E.EC_INST[k], key="inst", on_change=apply_medium)
            elif ss.lvfam == "IEC":
                st.selectbox("Modo de instalação", list(E.LV_M), format_func=lambda k: E.LV_M[k]["n"], key="m_lv", on_change=apply_medium)
                c1, c2 = st.columns(2)
                c1.segmented_control("Material", ["Al", "Cu"], key="mat")
                c2.segmented_control("Isolamento", ["XLPE", "PVC"], key="ins")
        elif ss.level == "mt":
            st.selectbox("Tipo de cabo", list(E.MT_FAMS), format_func=lambda k: E.MT_FAMS[k], key="mtfam")
            st.selectbox("Modo de instalação", list(E.MT_M), format_func=lambda k: E.MT_M[k], key="m_mt", on_change=apply_medium)
        else:
            st.segmented_control("Material", ["Al", "Cu"], key="mat")
            st.selectbox("Modo de instalação", list(E.HV_M), format_func=lambda k: E.HV_M[k], key="m_hv")
        probe = dict(net=net, bt=bt, lvfam=ss.lvfam, m_lv=ss.m_lv, inst=ss.inst, kV=float(ss.U) if not bt else 0, m_mt=ss.m_mt)
        md = E.medium(probe)
        c1, c2 = st.columns(2)
        c1.number_input("Circuitos na vala / tabuleiro", 1, 30, step=1, key="ncirc")
        c2.number_input("Cabos em paralelo por fase", 1, 12, step=1, key="npar")
        if md == "ground":
            c1, c2 = st.columns(2)
            c1.number_input("Resistividade do solo (K·m/W)", 0.5, 3.0, step=0.1, key="rho")
            c2.selectbox("Afastamento", [0.0, 0.25, 0.5, 1.0], format_func=lambda v: "Justapostos" if v == 0 else f"{nf(v)} m", key="sp")
    probe = dict(net=net, bt=bt, lvfam=ss.lvfam, m_lv=ss.m_lv, inst=ss.inst, kV=float(ss.U) if not bt else 0, m_mt=ss.m_mt)
    st.number_input("Temperatura do solo (°C)" if E.medium(probe) == "ground" else "Temperatura do ar (°C)", -10.0, 70.0, step=1.0, key="ta")

    st.markdown("### 4 · Critérios")
    c1, c2 = st.columns(2)
    c1.number_input("ΔU máx. (%)", 0.1, 20.0, step=0.1, key="du")
    c2.number_input("Perdas máx. (%)", 0.1, 20.0, step=0.1, key="lossMax")
    st.toggle("Aplicar critério de perdas", key="lossOn")
    c1, c2 = st.columns(2)
    c1.number_input("Icc (kA)", 0.0, 100.0, step=0.5, key="icc", help="0 desativa a verificação")
    c2.number_input("Duração (s)", 0.01, 5.0, step=0.05, key="tcc")
    if bt:
        st.selectbox("Proteção", ["disj", "fus", "none"],
                     format_func=lambda k: {"disj": "Disjuntor (I2 = 1,45 In)", "fus": "Fusível gG / gPV (I2 = 1,6 In)", "none": "Sem verificação"}[k], key="prot")
    st.markdown('<div class="side-sign">Criado por <b>Jorge Ramos</b> · uso privado<br>Tecneira – Tecnologias Energéticas, S.A.</div>', unsafe_allow_html=True)


def read_state():
    bt = ss.level.startswith("bt")
    return E.make_state(
        level=ss.level, Uin=float(ss.U), Pkw=ss.P if bt else ss.P * 1000, Lkm=ss.L / 1000 if bt else ss.L,
        cos=ss.cos, fd=max(1.0, ss.fd), net=ss.net or "sub", lvfam=ss.lvfam, constr=ss.constr, inst=ss.inst,
        m_lv=ss.m_lv, mat=ss.mat or "Al", ins=ss.ins or "XLPE", mtfam=ss.mtfam, m_mt=ss.m_mt, m_hv=ss.m_hv,
        ta=ss.ta, rho=ss.rho, ncirc=int(ss.ncirc), sp=float(ss.sp), npar=int(ss.npar), fam=ss.fam, nb=int(ss.nb),
        gmd=ss.gmd, ncl=2 if ((ss.net or "sub") == "aer" and not bt and ss.ncl == "Dupla") else 1,
        du=ss.du, lossOn=ss.lossOn, lossMax=ss.lossMax, icc=ss.icc, tcc=ss.tcc, prot=ss.prot if bt else "none",
        heq=ss.heq, ftau=ss.ftau, price=ss.price, life=int(ss.life), rate=ss.rate, tech=ss.tech or "pv_fix")


# ------------------------------------------------------------------ componentes visuais
def chip(ok, t, na=False):
    cls = "na" if na else ("ok" if ok else "err")
    sym = "–" if na else ("✓" if ok else "✕")
    return f'<span class="chip {cls}">{sym} {t}</span>'


def alerts_html(A):
    return '<ul class="alerts">' + "".join(f'<li class="{t}">{m}</li>' for t, m in A) + "</ul>"


def status_icon(e):
    return "🟢" if e["okAll"] else ("🟠" if e["okTh"] else "🔴")


def cmp_frame(ev, sel, ref, oh=False, ncl=1):
    order = sorted(range(len(ev)), key=lambda i: ev[i]["load"])
    rows = []
    for i in order:
        e = ev[i]
        row = {
            "": status_icon(e),
            "Condutor": ("★ " if i == sel else "") + e["c"]["label"],
            "Iz (A)": round(e["Iz"]),
            "Utilização (%)": round(e["load"] * 100, 1),
        }
        if ncl > 1:
            row["Carga N-1 (%)"] = round(e["load"] * 200, 1)
        row.update({
            "ΔU (%)": round(e["dUp"], 2),
            "Perdas Pn (%)": round(e["lossP"], 2),
            "Perdas (kW)": round(e["PlossKW"], 1),
            "MWh/ano": round(e["Eloss"], 1),
            "€/ano": round(e["eur"]),
            "VAL perdas (k€)": round(e["npv"] / 1000, 1),
            "Poupança VAL (k€)": round((ref["npv"] - e["npv"]) / 1000, 1) if ref else None,
        })
        if oh:
            row["MW·km / 1 %"] = round(e["mom"]) if e["mom"] else None
        rows.append(row)
    return pd.DataFrame(rows), order


COLCFG = {
    "": st.column_config.TextColumn("", width=30),
    "Utilização (%)": st.column_config.ProgressColumn("Utilização", format="%.0f %%", min_value=0, max_value=150),
}


# ------------------------------------------------------------------ diálogo: cálculo rápido de linhas aéreas
def q_defaults():
    kV = int(ss.q_kV)
    ss.q_gmd = float(E.KV[kV]["gmd"])
    ss.q_nb = E.NB[kV]
    ss.q_P = float({10: 5, 15: 8, 20: 10, 30: 20, 60: 50, 150: 150, 220: 300, 400: 800}[kV])
    ss.q_L = float({10: 4, 15: 6, 20: 8, 30: 8, 60: 25, 150: 50, 220: 60, 400: 100}[kV])
    ss.q_du = 5.0 if kV >= 150 or kV < 60 else 3.0


@st.dialog("Cálculo rápido · perdas e queda de tensão em linhas aéreas", width="large")
def quick_dialog():
    c = st.columns(4)
    c[0].selectbox("Tensão (kV)", [10, 15, 20, 30, 60, 150, 220, 400], key="q_kV", on_change=q_defaults)
    c[1].selectbox("Linha", ["Simples", "Dupla"], key="q_ncl")
    c[2].selectbox("Família", ["ALL", "ACSR", "AAAC"], format_func=lambda k: {"ALL": "ACSR + AAAC", "ACSR": "ACSR (tabela)", "AAAC": "AAAC Aster"}[k], key="q_fam")
    c[3].selectbox("Condutores por fase", [1, 2, 3, 4], key="q_nb")
    c = st.columns(4)
    c[0].number_input("Potência (MW)", 0.1, 5000.0, step=1.0, key="q_P")
    c[1].number_input("cos φ", 0.5, 1.0, step=0.01, key="q_cos")
    c[2].number_input("Comprimento (km)", 0.1, 500.0, step=1.0, key="q_L")
    c[3].number_input("DMG entre fases (m)", 0.3, 30.0, step=0.1, key="q_gmd")
    c = st.columns(5)
    c[0].number_input("Temp. ar (°C)", -10.0, 50.0, step=1.0, key="q_ta")
    c[1].number_input("Horas equiv. (h)", 100.0, 8760.0, step=10.0, format="%.0f", key="q_heq")
    c[2].number_input("Fator τ / h eq", 0.2, 1.0, step=0.01, key="q_tau")
    c[3].number_input("ΔU máx. (%)", 0.1, 20.0, step=0.1, key="q_du")
    c[4].number_input("Perdas máx. (%)", 0.1, 20.0, step=0.1, key="q_loss")
    kV = int(ss.q_kV)
    stq = E.make_state(level="mat" if kV >= 150 else ("at" if kV >= 60 else "mt"), Uin=float(kV), Pkw=ss.q_P * 1000,
                       Lkm=ss.q_L, cos=ss.q_cos, fd=1.0, net="aer", fam=ss.q_fam, nb=int(ss.q_nb), gmd=ss.q_gmd,
                       ncl=2 if ss.q_ncl == "Dupla" else 1, ta=ss.q_ta, du=ss.q_du, lossOn=True, lossMax=ss.q_loss,
                       icc=0.0, tcc=0.5, prot="none", heq=ss.q_heq, ftau=ss.q_tau, price=ss.price, life=int(ss.life),
                       rate=ss.rate, ncirc=1, npar=1, rho=1.0, sp=0.5, tech=ss.tech or "pv_fix",
                       lvfam="LXV", constr="uni", inst="sub", m_lv="D2", mat="Al", ins="XLPE", mtfam="LXHIOV", m_mt="D", m_hv="D")
    r = E.compute(stq)
    ev, sel = r["ev"], r["sel"]
    ref = ev[sel] if sel >= 0 else None
    df, order = cmp_frame(ev, sel, ref, oh=True, ncl=stq["ncl"])
    df["Condutor"] = [("★ " if v.startswith("★ ") else "") + ("Dupla · " if stq["ncl"] > 1 else "") + (f"{stq['nb']} × " if stq["nb"] > 1 else "") + v.replace("★ ", "") for v in df["Condutor"]]
    st.caption("Ordenado da menor para a maior utilização (melhores soluções primeiro). ★ e 🟢 marcam o menor condutor que cumpre carga, queda de tensão e perdas. Clique numa linha para ver a justificação.")
    sig = abs(hash((kV, ss.q_ncl, ss.q_fam, ss.q_nb)))
    evt = st.dataframe(df, hide_index=True, use_container_width=True, on_select="rerun", selection_mode="single-row",
                       column_config=COLCFG, key=f"qsel_{sig}", height=min(560, 38 + 35 * len(df)))
    rows = evt.selection.rows if evt and evt.selection else []
    vi = order[rows[0]] if rows else (sel if sel >= 0 else (order[0] if order else -1))
    if vi >= 0:
        e = ev[vi]
        A = E.alerts_for(stq, e, sel, r["sug"])
        st.markdown(f'<div class="glass">{alerts_html(A)}<div style="height:10px"></div>{E.justification_html(e, stq, vi == sel)}</div>',
                    unsafe_allow_html=True)


# ------------------------------------------------------------------ diálogo: tabelas de correntes admissíveis
TABLES = {
    "LXHIOV": "LXHIOV · MT monopolar Al XLPE (Eurocabos Tab. VI)",
    "XHIOV": "XHIOV · MT monopolar Cu XLPE (Eurocabos Tab. VI)",
    "MT_TRI": "MT tripolares Cu / Al XLPE (Eurocabos Tab. VI)",
    "VV": "VV / VAV · BT Cu PVC (Eurocabos Tab. I)",
    "XV": "XV / XAV · BT Cu XLPE (Eurocabos Tab. II)",
    "LVV": "LVV / LSVV · BT Al PVC (Eurocabos Tab. IV)",
    "LXV": "LXV / LSXV / LXS · BT Al XLPE (Eurocabos Tab. V)",
    "ACSR": "ACSR · alumínio-aço (linhas aéreas)",
    "AAAC": "AAAC Aster · liga de alumínio (linhas aéreas, indicativo)",
    "PV": "H1Z2Z2-K · cabo solar CC (EN 50618)",
}


def table_data(key):
    """Devolve DataFrame, metadados das colunas de corrente {col: (meio, θmax)} e notas."""
    meta, notes = {}, []
    if key in ("LXHIOV", "XHIOV"):
        al = key == "LXHIOV"
        rows = []
        for S, a_s, c_s, a_a, c_a in E.EC_MT_MONO:
            air = E.ec_mt_al_air(S, a_a, c_a) if al else c_a
            rows.append({"Secção (mm²)": S, "Subterrânea (A)": a_s if al else c_s, "Ao ar livre (A)": air,
                         "R20 (Ω/km)": E.R20["Al" if al else "Cu"][S]})
        meta = {"Subterrânea (A)": ("ground", 90), "Ao ar livre (A)": ("air", 90)}
        notes = ["Três cabos monopolares em trevo juntivo, canalização trifásica. Solo 20 °C, ar 30 °C. Isolamento PEX (XLPE), 90 °C.",
                 "Tensões estipuladas habituais: 6/10, 8,7/15, 12/20 e 18/30 kV."]
        if al:
            notes.append("No catálogo, a coluna Al ao ar livre até 300 mm² repete a secção (gralha). Os valores mostrados até 300 mm² são estimados como 0,78 × Cu ao ar.")
        return pd.DataFrame(rows), meta, notes
    if key == "MT_TRI":
        rows = [{"Secção (mm²)": S, "Al subterrânea (A)": a, "Cu subterrânea (A)": b, "Al ao ar (A)": c, "Cu ao ar (A)": d}
                for S, a, b, c, d in E.EC_MT_TRI]
        meta = {k: ("ground" if "subt" in k else "air", 90) for k in rows[0] if "(A)" in k}
        notes = ["Cabos tripolares MT, isolamento PEX. Solo 20 °C, ar 30 °C.",
                 "185 mm² Cu ao ar: o catálogo indica 310 A, provável gralha (valor coerente ≈ 510 A)."]
        return pd.DataFrame(rows), meta, notes
    if key in E.EC_LV:
        f = E.EC_LV[key]
        tmax = 70 if f["ins"] == "PVC" else 90
        rows = []
        for r in f["rows"]:
            rows.append({"Secção (mm²)": r[0],
                         "1 cond. subterrânea (A)": r[1], "1 cond. ao ar (A)": r[2], "1 cond. ΔU (V/A·km)": r[3],
                         "2 cond. subterrânea (A)": r[4], "2 cond. ao ar (A)": r[5], "2 cond. ΔU (V/A·km)": r[6],
                         "3-4 cond. subterrânea (A)": r[7], "3-4 cond. ao ar (A)": r[8], "3-4 cond. ΔU (V/A·km)": r[9]})
        meta = {k: ("ground" if "subt" in k else "air", tmax) for k in rows[0] if "(A)" in k}
        notes = [f"{f['nome']} · {f['desc']} · {f['tab']} Eurocabos (Mai.06). Solo 20 °C, ar 30 °C.",
                 "1 condutor: cabo monopolar isolado. Em ternos juntivos multiplicar por 0,80.",
                 "2 condutores: canalização monofásica. 3-4 condutores: canalização trifásica. ΔU com cos φ = 0,8."]
        if key == "LXV":
            notes.append("Para cabos torçados LXS, as intensidades ao ar livre são as desta tabela (nota do catálogo).")
        return pd.DataFrame(rows), meta, notes
    if key == "ACSR":
        rows = []
        for c in E.ACSR:
            d = math.sqrt(4 * float(c["d"]) / math.pi) / 0.866
            rows.append({"Tipo": f"ACSR {c['d']}", "Secção Al (mm²)": c["al"], "Capacidade nominal (A)": c["i"],
                         "R20 aprox. (Ω/km)": round(28.9 / c["al"], 4), "Ø aprox. (mm)": round(d, 1)})
        notes = ["Tabela de referência fornecida (capacidade nominal*). O valor do ACSR 595 foi lido como 1075 A.",
                 "A capacidade depende das condições do operador (verão / inverno, vento, temperatura do condutor 75 a 85 °C)."]
        return pd.DataFrame(rows), {"Capacidade nominal (A)": ("oh", 0)}, notes
    if key == "AAAC":
        rows = [{"Tipo": f"AAAC {c['d']}", "Secção (mm²)": c["s"], "Capacidade (A)": c["i"],
                 "R20 aprox. (Ω/km)": round(33.1 / c["s"], 4)} for c in E.AAAC]
        return pd.DataFrame(rows), {"Capacidade (A)": ("oh", 0)}, ["Valores indicativos (liga AL3 / Almelec). Confirmar com o fabricante."]
    rows = [{"Secção (mm²)": S, "Ao ar, isolado (A)": I, "R20 (Ω/km)": E.R20["Cu"][S]} for S, I in zip(E.PV_S, E.PV_I)]
    return pd.DataFrame(rows), {"Ao ar, isolado (A)": ("pv", 120)}, ["EN 50618, ambiente 60 °C, condutor 120 °C, 1,5 kV CC."]


@st.dialog("Tabelas de correntes admissíveis", width="large")
def tables_dialog():
    st.selectbox("Tabela a consultar", list(TABLES), format_func=lambda k: TABLES[k], key="t_sel")
    df, meta, notes = table_data(ss.t_sel)
    corr_cols = [k for k, (m, _) in meta.items() if m in ("ground", "air", "pv")]
    with st.expander("Aplicar fatores de correção e procurar secção", expanded=False):
        c = st.columns(4)
        tg = c[0].number_input("Temp. do solo (°C)", 0.0, 50.0, 20.0, 1.0, key="t_tg")
        ta = c[1].number_input("Temp. do ar (°C)", -10.0, 70.0, 30.0, 1.0, key="t_ta")
        fg = c[2].number_input("Fator de agrupamento", 0.3, 1.0, 1.0, 0.05, key="t_fg")
        Ireq = c[3].number_input("Corrente pretendida (A)", 0.0, 10000.0, 0.0, 10.0, key="t_I")
        apply = st.toggle("Mostrar valores corrigidos", key="t_apply")
    if apply and corr_cols:
        df = df.copy()
        for k in corr_cols:
            m, tmax = meta[k]
            f = E.temp_f(tmax, tg, 20) if m == "ground" else (min(1, E.temp_f(tmax, ta, 60)) if m == "pv" else E.temp_f(tmax, ta, 30))
            df[k] = (df[k] * f * fg).round(0)
        st.caption("Valores corrigidos: I = I₀ × fθ × f_agrup, com fθ = √((θmax − θ) / (θmax − θref)).")
    fmt = lambda v: "–" if pd.isna(v) else (f"{v:g}".replace(".", ",") if isinstance(v, (int, float)) else v)
    st.dataframe(df.style.format(fmt), hide_index=True, use_container_width=True, height=min(620, 38 + 35 * len(df)))
    if Ireq > 0:
        scol = df.columns[0]
        out = []
        for k in meta:
            ok = df[pd.to_numeric(df[k], errors="coerce") >= Ireq]
            out.append(f"<b>{k.replace(' (A)', '')}</b>: {fmt(ok.iloc[0][scol]) if len(ok) else '–'}")
        st.markdown('<div class="reco">Menor secção que suporta ' + nf(Ireq, 0) + " A · " + " · ".join(out) + "</div>", unsafe_allow_html=True)
    for n in notes:
        st.caption(n)
    st.download_button("Descarregar tabela (CSV)", df.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
                       file_name=f"tabela_{ss.t_sel}.csv", mime="text/csv")


# ------------------------------------------------------------------ cabeçalho e ações
logo_tag = f'<img src="data:image/png;base64,{LOGO_B64}" alt="Tecneira">' if LOGO_B64 else "<b>TECNEIRA</b>"
st.markdown(f"""
<div class="glass hdr">{logo_tag}
 <div class="t"><h1>Dimensionamento de Cabos e Linhas</h1>
 <p>Centrais solares e parques eólicos · BT, MT, AT e MAT · RTIEBT, RSLEAT e RSRDEEBT</p></div>
 <span class="badge"><i></i>Criado por Jorge Ramos · uso privado</span>
</div>""", unsafe_allow_html=True)

state = read_state()
res = E.compute(state)
ev, sel, th = res["ev"], res["sel"], res["th"]

b1, b2, b3, _ = st.columns([1.35, 1.35, 1.1, 2.2])
if b1.button("⚡ Cálculo rápido · linhas aéreas", type="primary", use_container_width=True):
    ss.q_heq, ss.q_tau = ss.heq, ss.ftau
    quick_dialog()
if b2.button("📋 Tabelas de correntes admissíveis", type="primary", use_container_width=True):
    tables_dialog()

left, right = st.columns([1.55, 1], gap="medium")

if not ev:
    left.warning("Sem condutores disponíveis para esta combinação.")
    st.stop()

base = sel if sel >= 0 else (th if th >= 0 else len(ev) - 1)
e0 = ev[base]
c0 = e0["c"]
np_ = state["nb"] if c0["med"] == "oh" else state["npar"]
if c0["med"] == "oh":
    name = (f"{np_} × " if np_ > 1 else "") + c0["label"] + (" por fase" if np_ > 1 else "") + (" · linha dupla" if state["ncl"] > 1 else "")
elif state["sys"] == "3f":
    name = f"3 × {np_} × (1 × {c0['label']})" if np_ > 1 else f"3 × {c0['label']}"
else:
    name = f"2 × {np_} × {c0['label']}" if np_ > 1 else f"2 × {c0['label']}"
if c0["med"] == "oh":
    desc = f"Linha aérea {state['kV']:g} kV"
elif state["net"] == "aer":
    desc = "Rede aérea BT"
elif state["bt"]:
    desc = E.EC_INST[state["inst"]] if state["lvfam"] in E.EC_LV else (E.LV_M[state["m_lv"]]["n"] if state["lvfam"] == "IEC" else "Cabo solar ao ar")
else:
    desc = E.MT_M[state["m_mt"]] if state["kV"] < 60 else E.HV_M[state["m_hv"]]
crit_txt = f" · Critério determinante: <b>{res['crit']}</b>" if sel >= 0 else ""

with left:
    ener = nf(e0["Eloss"], 2 if e0["Eloss"] < 10 else 1)
    extra = ""
    if e0["chg"]:
        extra += f'<div class="m"><div class="k">Reativa capacitiva</div><div class="v">{nf(e0["chg"]["Q"])} <small>Mvar</small></div></div>'
    if e0["mom"]:
        extra += f'<div class="m"><div class="k">Momento p/ 1 % ΔU</div><div class="v">{nf(e0["mom"], 1)} <small>MW·km</small></div></div>'
    prot_chip = chip(e0["okProt"], f"Proteção In {e0['In'] or '–'} A") if state["bt"] and state["prot"] != "none" else ""
    st.markdown(f"""
<div class="glass">
 <div class="lbl">{'Secção recomendada' if sel >= 0 else 'Melhor aproximação (não cumpre)'}</div>
 <div class="big">{name}</div>
 <div class="sub">{desc}{crit_txt}</div>
 <div class="chips">{chip(e0['okTh'], 'Térmico')}{chip(e0['okDU'], 'Queda de tensão')}{chip(e0['okLoss'], 'Perdas', not state['lossOn'])}{chip(e0['okSC'], 'Curto-circuito', not state['icc'] > 0)}{prot_chip}</div>
 <div class="metrics">
  <div class="m"><div class="k">Corrente de serviço</div><div class="v">{nf(e0['Ib'], 1)} <small>A</small></div></div>
  <div class="m"><div class="k">Corrente de dimensionamento</div><div class="v">{nf(e0['Id'], 1)} <small>A</small></div></div>
  <div class="m"><div class="k">Iz corrigida</div><div class="v">{nf(e0['Iz'], 0)} <small>A</small></div></div>
  <div class="m"><div class="k">Utilização</div><div class="v">{nf(e0['load'] * 100, 0)} <small>%</small></div></div>
  <div class="m"><div class="k">Queda de tensão</div><div class="v">{nf(e0['dUp'])} <small>% · {nf(e0['dU'], 1 if e0['dU'] < 100 else 0)} V</small></div></div>
  <div class="m"><div class="k">Perdas à Pnom</div><div class="v">{nf(e0['PlossKW'], 2 if e0['PlossKW'] < 100 else 0)} <small>kW · {nf(e0['lossP'])} %</small></div></div>
  <div class="m"><div class="k">Perdas anuais</div><div class="v">{ener} <small>MWh/ano</small></div></div>
  <div class="m"><div class="k">% da energia produzida</div><div class="v">{nf(e0['lossE'])} <small>%</small></div></div>
  <div class="m"><div class="k">Valor das perdas</div><div class="v">{nf(e0['eur'], 0)} <small>€/ano</small></div></div>
  <div class="m"><div class="k">VAL perdas ({state['life']} anos)</div><div class="v">{nf(e0['npv'] / 1000, 1)} <small>k€</small></div></div>
  <div class="m"><div class="k">Temp. condutor estimada</div><div class="v">{nf(e0['theta'], 0)} <small>°C</small></div></div>
  {extra}
 </div>
 {alerts_html(E.alerts_for(state, e0, sel, res['sug']))}
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="lbl" style="margin-top:8px">Comparação · da menor para a maior utilização (melhores primeiro) · clique numa linha para ver a justificação</div>', unsafe_allow_html=True)
    df, order = cmp_frame(ev, sel, e0, oh=c0["med"] == "oh", ncl=state["ncl"])
    sig = abs(hash(tuple(sorted((k, str(v)) for k, v in state.items()))))
    evt = st.dataframe(df, hide_index=True, use_container_width=True, on_select="rerun", selection_mode="single-row",
                       column_config=COLCFG, key=f"cmp_{sig}", height=min(520, 38 + 35 * len(df)))
    rows = evt.selection.rows if evt and evt.selection else []
    vi = order[rows[0]] if rows else base

    if sel >= 0 and sel + 1 < len(ev):
        n, s = ev[sel + 1], ev[sel]
        dv, dE = s["npv"] - n["npv"], s["Eloss"] - n["Eloss"]
        ncond = (3 if state["sys"] == "3f" else 2) * (state["nb"] if c0["med"] == "oh" else state["npar"]) * state["ncl"]
        Lm = state["Lkm"] * 1000
        perm = dv / (Lm * ncond) if Lm > 0 else 0
        st.markdown(f"""<div class="reco"><b>Recomendação económica.</b> Passar de {s['c']['label']} para {n['c']['label']} reduz as perdas
 em {nf(dE, 1)} MWh/ano ({nf(dE * state['price'], 0)} €/ano). Em {state['life']} anos a {nf(state['rate'], 1)} % esta poupança vale
 <b>{nf(dv, 0)} €</b>. Compensa se o sobrecusto total da obra for inferior a este valor, cerca de <b>{nf(perm)} € por metro de condutor</b>
 ({ncond} condutores × {nf(Lm, 0)} m).</div>""", unsafe_allow_html=True)

with right:
    ev_v = ev[vi]
    just = E.justification_html(ev_v, state, vi == sel)
    with st.container(key="panel"):
        st.markdown(f'<div class="glass"><div class="lbl">Cálculos justificativos</div>{just}</div>', unsafe_allow_html=True)
        memo = f"""<!DOCTYPE html><html lang="pt-PT"><head><meta charset="utf-8"><title>Memória de cálculo</title>{CSS}</head>
<body style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:860px;margin:30px auto;padding:0 20px">
{('<img src="data:image/png;base64,' + LOGO_B64 + '" style="height:60px">') if LOGO_B64 else ''}
<h2>Memória de cálculo · {name}</h2>
<p style="color:#6e6e73">{E.LEVELS[state['level']]['nome']} · {nf(state['U'] / 1000 if state['U'] >= 1000 else state['U'], 1 if state['U'] < 1000 else 0)} {'kV' if state['U'] >= 1000 else 'V'} ·
P = {nf(state['Pkw'] / 1000 if state['Pkw'] >= 1000 else state['Pkw'], 2)} {'MW' if state['Pkw'] >= 1000 else 'kW'} · L = {nf(state['Lkm'], 3)} km · {date.today():%d/%m/%Y}</p>
{alerts_html(E.alerts_for(state, ev_v, sel, res['sug']))}<br>{just}
<p style="color:#6e6e73;font-size:12px;margin-top:30px">Criado por Jorge Ramos · Tecneira – Tecnologias Energéticas, S.A. · uso privado</p></body></html>"""
        st.download_button("⬇︎ Descarregar memória de cálculo (HTML)", memo.encode("utf-8"), file_name="memoria_calculo.html",
                           mime="text/html", use_container_width=True)

st.markdown("""<div class="foot"><b>Referências:</b> RTIEBT (Portaria 949-A/2006), secções 433, 434, 523, 525 e 712. RSLEAT (Decreto Regulamentar 1/92).
RSRDEEBT (Decreto Regulamentar 90/84). IEC 60364-5-52, IEC 60502-2, IEC 60287, EN 50618, IEC 62548. Tabelas técnicas Eurocabos (Mai.06).<br>
<b>Limitações:</b> intensidades tabeladas a validar com o fabricante e cálculo IEC 60287 para projeto de execução. Linhas aéreas exigem cálculo mecânico
e verificação de distâncias (RSLEAT). Ferramenta criada por Jorge Ramos para uso privado da Tecneira.</div>""", unsafe_allow_html=True)
