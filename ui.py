"""Capa visual: CSS responsive (PC + celular), componentes HTML y tema Plotly."""
import html

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

import catalogos as C
import db

INK = "#F8FAFC"
INK_2 = "#CBD5E1"
MUTED = "#94A3B8"
GRID = "rgba(148,163,184,0.12)"
SURFACE = "#0F172A"

# ───────────────────────── Tema Plotly ─────────────────────────
pio.templates["dgii"] = go.layout.Template(
    layout=dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, -apple-system, Segoe UI, sans-serif", color=INK_2, size=12),
        colorway=C.PALETA,
        title=dict(font=dict(size=15, color=INK), x=0.01, xanchor="left"),
        xaxis=dict(gridcolor=GRID, linecolor="#334155", zerolinecolor="#334155", tickfont=dict(color=MUTED)),
        yaxis=dict(gridcolor=GRID, linecolor="#334155", zerolinecolor="#334155", tickfont=dict(color=MUTED)),
        legend=dict(orientation="h", yanchor="top", y=-0.15, x=0, font=dict(color=INK_2)),
        margin=dict(l=8, r=8, t=48, b=8),
        hoverlabel=dict(bgcolor=SURFACE, bordercolor="#334155", font=dict(color=INK)),
        bargap=0.28,
    )
)
pio.templates.default = "plotly_dark+dgii"
PLOT_CFG = {"displayModeBar": False, "responsive": True}


def plot(fig, h=340):
    fig.update_layout(height=h)
    st.plotly_chart(fig, config=PLOT_CFG, width="stretch")


# ───────────────────────── CSS ─────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root { --azul:#3B82F6; --borde:rgba(51,65,85,.85); --card:rgba(19,27,46,.72); }
.stApp, .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5 {
  color:#F8FAFC; font-family:'Inter', system-ui, -apple-system, sans-serif !important; }
.stApp { background: radial-gradient(circle at 50% 0%, #111C38 0%, #070A14 100%) !important; }
/* Los íconos de Streamlit usan su propia fuente: sin esto se ve el texto "expand_more", "arrow_right", etc. */
.stApp [data-testid="stIconMaterial"], .stApp span[data-testid="stIconMaterial"],
.stApp .material-symbols-rounded, .stApp [class*="material-symbols"], .stApp [class*="material-icons"] {
  font-family: "Material Symbols Rounded" !important; font-weight: normal !important; font-style: normal !important;
  letter-spacing: normal !important; text-transform: none !important; font-feature-settings: "liga" !important;
  -webkit-font-feature-settings: "liga" !important; white-space: nowrap; direction: ltr; }
.block-container { padding-top: 2.2rem; padding-bottom: 4rem; max-width: 1500px; }
footer, [data-testid="stStatusWidget"], .stDeployButton { display:none !important; }

[data-testid="stSidebar"] { background:#04060B; border-right:1px solid #1E293B; }
[data-testid="stSidebar"] [role="radiogroup"] label { padding:7px 10px; border-radius:9px; margin-bottom:2px; width:100%; }
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background:rgba(59,130,246,.12); }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) { background:linear-gradient(135deg,rgba(37,99,235,.35),rgba(29,78,216,.15)); border:1px solid rgba(96,165,250,.45); }

.hdr { display:flex; align-items:center; gap:14px; border-bottom:2px solid rgba(59,130,246,.35); padding-bottom:10px; margin-bottom:6px; }
.hdr h1 { font-size:1.9rem; font-weight:800; letter-spacing:-.5px; margin:0; padding:0; line-height:1.15; }
.hdr .sub { color:#94A3B8; font-size:.8rem; text-transform:uppercase; letter-spacing:1px; font-weight:600; }

.kgrid { display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:12px; margin:10px 0 18px; }
.kpi { background:linear-gradient(135deg, rgba(30,41,59,.75), rgba(15,23,42,.85)); border:1px solid var(--borde);
  border-radius:14px; padding:14px 16px; position:relative; overflow:hidden; }
.kpi::before { content:""; position:absolute; left:0; top:0; bottom:0; width:4px; background:var(--k, #3B82F6); }
.kpi .kl { font-size:.68rem; color:#94A3B8; font-weight:700; text-transform:uppercase; letter-spacing:.8px; }
.kpi .kv { font-size:1.75rem; font-weight:800; color:#FFFFFF; line-height:1.15; margin-top:4px; }
.kpi .kn { font-size:.74rem; color:#CBD5E1; margin-top:2px; }

.card { background:var(--card); border:1px solid var(--borde); border-radius:14px; padding:16px 18px; margin-bottom:12px;
  box-shadow:0 10px 25px rgba(0,0,0,.35); }
.card.acc { border-left:5px solid var(--c, #3B82F6); }
.ident { font-size:1.55rem; font-weight:800; letter-spacing:-.3px; color:#FFFFFF; font-variant-numeric:tabular-nums; }
.ident small { font-size:.72rem; color:#94A3B8; font-weight:600; letter-spacing:.5px; margin-left:6px; }
.meta { color:#CBD5E1; font-size:.86rem; margin-top:6px; line-height:1.55; }
.meta b { color:#F8FAFC; }

.chip { display:inline-flex; align-items:center; gap:6px; padding:3px 10px; border-radius:999px; font-size:.72rem;
  font-weight:700; letter-spacing:.3px; margin:2px 4px 2px 0; white-space:nowrap; border:1px solid; }
.chip i { width:8px; height:8px; border-radius:50%; display:inline-block; }

.sec { display:flex; align-items:center; gap:8px; margin:18px 0 8px; padding:8px 14px; border-radius:10px;
  background:rgba(30,41,59,.45); border-left:4px solid #3B82F6; }
.sec h4 { margin:0; color:#93C5FD; font-size:1rem; font-weight:700; }

.tl { position:relative; margin-left:10px; padding-left:22px; border-left:2px solid #1E293B; }
.tl .it { position:relative; margin-bottom:14px; background:rgba(15,23,42,.6); border:1px solid #1E293B; border-radius:12px; padding:10px 14px; }
.tl .it::before { content:""; position:absolute; left:-30px; top:14px; width:14px; height:14px; border-radius:50%;
  background:var(--c,#3B82F6); border:3px solid #070A14; box-shadow:0 0 0 2px var(--c,#3B82F6); }
.tl .t1 { font-weight:700; color:#F8FAFC; font-size:.92rem; }
.tl .t2 { color:#94A3B8; font-size:.78rem; }
.tl .t3 { color:#CBD5E1; font-size:.84rem; margin-top:4px; }

.alerta { border-radius:12px; padding:12px 14px; margin-bottom:10px; border:1px solid; display:flex; gap:12px; align-items:flex-start; }
.alerta .ic { font-size:1.3rem; line-height:1; }
.alerta .at { font-weight:700; color:#F8FAFC; font-size:.9rem; }
.alerta .ad { color:#CBD5E1; font-size:.8rem; margin-top:2px; }

[data-testid="stForm"] { background:rgba(19,27,46,.75) !important; border:1px solid var(--borde) !important;
  border-radius:14px !important; padding:20px !important; }
.stButton>button, div.stFormSubmitButton>button, .stDownloadButton>button, .stLinkButton>a {
  border-radius:9px !important; font-weight:700 !important; width:100%; min-height:2.6rem; }
div.stFormSubmitButton>button, .stButton>button[kind="primary"] {
  background:linear-gradient(135deg,#3B82F6,#1D4ED8) !important; color:#fff !important; border:1px solid #60A5FA !important;
  box-shadow:0 4px 12px rgba(59,130,246,.35) !important; }
.stLinkButton>a[href*="wa.me"] { background:linear-gradient(135deg,#16A34A,#15803D) !important; color:#fff !important; border:1px solid #4ADE80 !important; }

.stTabs [data-baseweb="tab-list"] { gap:6px; background:rgba(15,23,42,.6); padding:4px; border-radius:12px; border:1px solid #1E293B; overflow-x:auto; }
.stTabs [data-baseweb="tab"] { background:rgba(30,41,59,.5); border-radius:8px; color:#94A3B8 !important; font-weight:600; padding:8px 14px; }
.stTabs [aria-selected="true"] { background:linear-gradient(135deg,#2563EB,#1D4ED8) !important; color:#fff !important; }
[data-testid="stMetric"] { background:rgba(15,23,42,.55); border:1px solid #1E293B; border-radius:12px; padding:10px 14px; }

/* ── Barra superior y botón del menú lateral siempre visibles ── */
header[data-testid="stHeader"] { background: rgba(7,10,20,.92) !important; backdrop-filter: blur(8px); }
header[data-testid="stHeader"] svg, [data-testid="stSidebarCollapsedControl"] svg, [data-testid="stExpandSidebarButton"] svg,
[data-testid="stSidebarCollapseButton"] svg { color:#F8FAFC !important; fill:#F8FAFC !important; }
[data-testid="stSidebarCollapsedControl"] button, [data-testid="stExpandSidebarButton"] {
  background:rgba(59,130,246,.25) !important; border:1px solid rgba(96,165,250,.6) !important; border-radius:8px !important; }

/* ── Menú de navegación para celular ── */
.st-key-nav_movil { display:none; }

/* ── Celular ── */
@media (max-width: 640px) {
  .block-container { padding: 3.2rem .7rem 5rem; }
  .hdr h1 { font-size:1.25rem; }
  .hdr img { width:44px !important; }
  .hdr .sub { font-size:.66rem; }
  .kgrid { grid-template-columns:repeat(2, 1fr); gap:8px; }
  .kpi { padding:10px 12px; }
  .kpi .kv { font-size:1.35rem; }
  .ident { font-size:1.25rem; }
  .card { padding:12px 13px; }
  [data-testid="stForm"] { padding:12px !important; }
  .stTabs [data-baseweb="tab"] { padding:6px 10px; font-size:.78rem; }
  input, textarea, select { font-size:16px !important; } /* evita zoom en iOS */
  .st-key-nav_movil { display:block; position:sticky; top:3.75rem; z-index:990; background:rgba(7,10,20,.97);
    padding:8px 0 10px; margin-bottom:6px; border-bottom:1px solid #1E293B; }
  .st-key-nav_movil [data-baseweb="select"] > div { background:linear-gradient(135deg,#1D4ED8,#1E3A8A) !important;
    border:1px solid #60A5FA !important; border-radius:10px !important; min-height:3rem; font-weight:700; }
}
@media print { [data-testid="stSidebar"], header, .stButton { display:none !important; } }
</style>
"""


def css():
    st.markdown(CSS, unsafe_allow_html=True)
    try:
        from tactico import CAPA  # capa visual «Tactical Next-Gen»
        st.markdown(CAPA, unsafe_allow_html=True)
    except Exception:
        pass


def esc(x):
    if x is None or (isinstance(x, float) and pd.isna(x)) or x is pd.NaT:
        return ""
    return html.escape(str(x))


def rgba(hex_color, a=0.18):
    h = str(hex_color or "#64748B").lstrip("#")
    if len(h) != 6:
        h = "64748B"
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"


# ───────────────────────── Colores por entidad ─────────────────────────
def mapa_dependencias():
    df = db.df_dependencias()
    return {r["nombre"]: (r["color"] or "#64748B") for _, r in df.iterrows()}


def color_dep(nombre, mapa=None):
    mapa = mapa if mapa is not None else mapa_dependencias()
    return mapa.get(nombre, "#64748B")


def sigla_dep(nombre):
    df = db.df_dependencias()
    m = df[df["nombre"] == nombre]
    if not m.empty and m["sigla"].iloc[0]:
        return m["sigla"].iloc[0]
    return nombre or "—"


# ───────────────────────── Componentes ─────────────────────────
def header(titulo, sub=C.SUBTITULO, logo=None):
    img = ""
    if logo:
        import base64

        try:
            with open(logo, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            img = f'<img src="data:image/png;base64,{b64}" width="62">'
        except OSError:
            img = ""
    try:  # cabecera «centro de comando»
        import tactico

        st.markdown(tactico.header_html(img, titulo, sub), unsafe_allow_html=True)
    except Exception:
        st.markdown(
            f'<div class="hdr">{img}<div><h1>{esc(titulo)}</h1><div class="sub">{esc(sub)}</div></div></div>',
            unsafe_allow_html=True,
        )


def kpis(items):
    """items: lista de (etiqueta, valor, nota, color)."""
    try:  # indicadores «Tactical Next-Gen»
        import tactico

        st.markdown(tactico.kpis_html(items), unsafe_allow_html=True)
        return
    except Exception:
        pass
    html_ = "".join(
        f'<div class="kpi" style="--k:{c}"><div class="kl">{esc(l)}</div><div class="kv">{esc(v)}</div>'
        f'<div class="kn">{esc(n)}</div></div>'
        for l, v, n, c in items
    )
    st.markdown(f'<div class="kgrid">{html_}</div>', unsafe_allow_html=True)


def chip(texto, color="#64748B", punto=True):
    p = f'<i style="background:{color}"></i>' if punto else ""
    return (
        f'<span class="chip" style="background:{rgba(color, .16)};border-color:{rgba(color, .55)};color:#F1F5F9">'
        f"{p}{esc(texto)}</span>"
    )


def chip_estado(estado):
    return chip(estado or "—", C.COLOR_ESTADO.get(estado, "#64748B"))


def chip_prioridad(prioridad):
    if prioridad == "URGENTE TRÁMITE":
        return chip("⚡ URGENTE TRÁMITE", C.STATUS["critical"], punto=False)
    return ""


def seccion(titulo):
    st.markdown(f'<div class="sec"><h4>{esc(titulo)}</h4></div>', unsafe_allow_html=True)


def fmt_fecha(x, hora=False):
    if x is None or pd.isna(x):
        return "—"
    try:
        t = pd.Timestamp(x)
        return t.strftime("%d/%m/%Y %H:%M") if hora else t.strftime("%d/%m/%Y")
    except Exception:
        return str(x)


def dias_desde(x):
    if x is None or pd.isna(x):
        return None
    return (pd.Timestamp(db.hoy()) - pd.Timestamp(x).normalize()).days


def chips_expediente(r, mapa=None):
    """(chips de estado, chips de ubicación) del expediente, en HTML. Lo usan la tarjeta simple y la premium."""
    mapa = mapa if mapa is not None else mapa_dependencias()
    ub = r.get("ubicacion_actual") or "—"
    c_ub = color_dep(ub, mapa)
    venc = ""
    if pd.notna(r.get("fecha_termino")) and r.get("estado") not in C.ESTADOS_CERRADOS and not bool(r.get("tramitado")):
        dv = (pd.Timestamp(r["fecha_termino"]) - pd.Timestamp(db.hoy())).days
        col = C.STATUS["critical"] if dv < 0 else (C.STATUS["warning"] if dv <= 2 else C.STATUS["ok"])
        txt = f"VENCIDO hace {-dv} d" if dv < 0 else (f"Vence en {dv} d" if dv else "VENCE HOY")
        venc = chip(f"⏱ {txt}", col, punto=False)
    if isinstance(r.get("pdf_link"), str) and r.get("pdf_link"):
        venc += (f'<a href="{esc(r["pdf_link"])}" target="_blank" style="text-decoration:none">'
                 f'{chip("📄 VER PDF", "#60A5FA", punto=False)}</a>')
    if bool(r.get("entrega_pendiente")):
        venc += chip(f"🚚 PARA ENTREGAR → {r.get('entrega_destino') or ''}", "#C98500", punto=False)
    sec = C.SECRETARIAS[C.sec_de(r.get("secretaria"))]
    venc = chip(f"📖 {sec['sigla']}", sec["color"], punto=False) + venc
    if bool(r.get("tramitado")):
        venc += chip(f"✅ TRAMITADO {fmt_fecha(r.get('fecha_tramite'))}", C.STATUS["ok"], punto=False)
    elif r.get("estado") not in C.ESTADOS_CERRADOS:
        venc += chip("⏳ PENDIENTE DE TRÁMITE", C.STATUS["warning"], punto=False)
    rei = r.get("reingresos")
    if pd.notna(rei) and int(rei) > 0:
        venc += chip(f"↩️ REINGRESÓ {int(rei)}×", "#9085E9", punto=False)
    linea1 = f'{chip(r.get("tipo"), "#60A5FA", False)}{chip_estado(r.get("estado"))}{chip_prioridad(r.get("prioridad"))}{venc}'
    linea2 = (f'📍 {chip(ub, c_ub)}'
              f'{"🎯 " + chip(r.get("destino"), color_dep(r.get("destino"), mapa)) if isinstance(r.get("destino"), str) and r.get("destino") else ""}'
              f'{chip(r.get("despacho"), "#A78BFA", False) if r.get("despacho") else ""}')
    return linea1, linea2


def tarjeta_expediente(r, mapa=None, detalle=True):
    mapa = mapa if mapa is not None else mapa_dependencias()
    ub = r.get("ubicacion_actual") or "—"
    c_ub = color_dep(ub, mapa)
    d = dias_desde(r.get("ult_mov") if pd.notna(r.get("ult_mov")) else r.get("fecha_ingreso"))
    linea1, linea2 = chips_expediente(r, mapa)
    meta = ""
    if detalle:
        org = r.get("dependencia_origen") or "—"
        meta = (
            f'<div class="meta"><b>{esc(r.get("asunto") or "Sin asunto")}</b><br>'
            f'Ingreso: {fmt_fecha(r.get("fecha_ingreso"))} · Origen: {esc(org)}'
            f'{" · Iniciador: " + esc(r.get("iniciador")) if r.get("iniciador") else ""}<br>'
            f'Último movimiento: {fmt_fecha(r.get("ult_mov"), True)}'
            f'{f" · {d} días sin moverse" if d is not None else ""}</div>'
        )
    st.markdown(
        f'<div class="card acc" style="--c:{c_ub}">'
        f'<div class="ident">N° {esc(r.get("nro_exp"))} / F° {esc(r.get("folio"))} / O° {esc(r.get("orden"))}'
        f'<small>AÑO {esc(r.get("anio"))} · LIBRO {esc(r.get("libro"))}</small></div>'
        f'<div style="margin-top:6px">{linea1}</div>'
        f'<div style="margin-top:4px">{linea2}</div>{meta}</div>',
        unsafe_allow_html=True,
    )


def timeline(movs, mapa=None, exp=None):
    """Hoja de ruta. Si se pasa el expediente, muestra arriba la entrega pendiente con el comisionista."""
    mapa = mapa if mapa is not None else mapa_dependencias()
    items = []
    if exp is not None and bool(exp.get("entrega_pendiente")):
        dest = exp.get("entrega_destino") or "—"
        det = [f"Encargó: <b>{esc(exp.get('entrega_solicitada_por') or '—')}</b>"]
        if exp.get("entrega_despacho"):
            det.append(f"Despacho: <b>{esc(exp['entrega_despacho'])}</b>")
        if exp.get("entrega_indicaciones"):
            det.append(esc(exp["entrega_indicaciones"]))
        items.append(
            f'<div class="it" style="--c:#F59E0B"><div class="t1">🚚 PARA ENTREGAR · con el comisionista ➜ {esc(dest)}</div>'
            f'<div class="t2">🕒 {fmt_fecha(exp.get("entrega_solicitada_en"), True)} · pendiente: al entregarlo se asienta la SALIDA '
            f'con quién lo recibe</div><div class="t3">{" · ".join(det)}</div></div>')
    if movs.empty and not items:
        st.info("Sin movimientos registrados.")
        return
    for _, m in movs.iterrows():
        c = color_dep(m.get("destino"), mapa)
        tram = m.get("tipo") == "TRÁMITE"
        extra = []
        if m.get("despacho"):
            extra.append(f"{'Se hizo' if tram else 'Despacho'}: <b>{esc(m['despacho'])}</b>")
        if m.get("entregado_por"):
            extra.append(f"{'Tramitó' if tram else 'Lleva/entrega'}: <b>{esc(m['entregado_por'])}</b>")
        if m.get("recibido_por"):
            extra.append(f"Recibe: <b>{esc(m['recibido_por'])}</b>")
        if pd.notna(m.get("fojas")) and m.get("fojas"):
            extra.append(f"Fojas: {int(m['fojas'])}")
        if m.get("observaciones"):
            extra.append(esc(m["observaciones"]))
        urg = " ⚡" if m.get("urgente") else ""
        org, dst = m.get("origen") or "—", m.get("destino") or "—"
        lugar = f"en {esc(dst)}" if org == dst else f"{esc(org)} ➜ {esc(dst)}"
        titulo = "✅ TRAMITADO" if tram else esc(m["tipo"])
        items.append(
            f'<div class="it" style="--c:{c}"><div class="t1">{titulo}{urg} · {lugar}</div>'
            f'<div class="t2">🕒 {fmt_fecha(m["fecha_hora"], True)} · registró {esc(m.get("registrado_por") or "—")}</div>'
            f'<div class="t3">{" · ".join(extra)}</div></div>'
        )
    st.markdown(f'<div class="tl">{"".join(items)}</div>', unsafe_allow_html=True)


def alerta(icono, titulo, detalle, color):
    st.markdown(
        f'<div class="alerta" style="background:{rgba(color, .12)};border-color:{rgba(color, .5)}">'
        f'<div class="ic">{icono}</div><div><div class="at">{esc(titulo)}</div>'
        f'<div class="ad">{esc(detalle)}</div></div></div>',
        unsafe_allow_html=True,
    )


def estilo_tabla(df, mapa=None, cols_dep=("Ubicación", "Origen", "Destino")):
    """Styler: colorea dependencias, estado y prioridad."""
    mapa = mapa if mapa is not None else mapa_dependencias()

    def _f(col):
        if col.name in cols_dep:
            return [f"background-color:{rgba(color_dep(v, mapa), .28)};color:#F8FAFC" if v else "" for v in col]
        if col.name == "Estado":
            return [f"color:{C.COLOR_ESTADO.get(v, '#CBD5E1')};font-weight:700" for v in col]
        if col.name == "Días sin mover":
            return [f"background-color:{rgba(C.STATUS['critical'], min(1, (v or 0) / 30) * .55)};font-weight:700" for v in col]
        if col.name == "Prioridad":
            return [f"color:{C.STATUS['critical']};font-weight:800" if v == "URGENTE TRÁMITE" else "" for v in col]
        return [""] * len(col)

    return df.style.apply(_f, axis=0)
