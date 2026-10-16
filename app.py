"""Sistema de Registro y Control de Expedientes — Dirección General de Institutos e Instrucción (Policía de Tucumán)."""
import os

import streamlit as st

st.set_page_config(
    page_title="Expedientes · D.G.I.I.",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="auto",
)

import catalogos as C  # noqa: E402
import comun as K  # noqa: E402
import db  # noqa: E402
import ui  # noqa: E402
from vistas import (  # noqa: E402
    v_alertas,
    v_carga,
    v_config,
    v_cursos,
    v_ficha,
    v_informes,
    v_libro,
    v_movimiento,
    v_nuevo,
    v_panel,
)

ui.css()

# ── Base de datos ──
try:
    db.init_db()
except Exception as e:
    st.error(f"❌ No se pudo conectar a la base de datos: {e}")
    st.info("Configure `SUPABASE_URL` en *Settings → Secrets* de Streamlit Cloud (cadena de conexión PostgreSQL de Supabase, preferentemente el *Session pooler*).")
    st.stop()


# ── Acceso ──
def _secret(k):
    try:
        return st.secrets.get(k)
    except Exception:
        return os.getenv(k)


if not st.session_state.get("operador"):
    ui.header("Registro de Expedientes", logo=K.LOGO if os.path.exists(K.LOGO) else None)
    clave_req = _secret("APP_PASSWORD")
    _, mid, _ = st.columns([1, 2, 1])
    with mid, st.form("login"):
        st.markdown("#### 🔐 Ingreso de operador")
        op = st.text_input("Jerarquía y apellido del operador", placeholder="Ej: OF. PPAL. GÓMEZ")
        clave = st.text_input("Clave de acceso", type="password") if clave_req else ""
        if st.form_submit_button("Ingresar"):
            if not op.strip():
                st.error("Ingrese el operador.")
            elif clave_req and clave != clave_req:
                st.error("Clave incorrecta.")
            else:
                st.session_state["operador"] = op.strip().upper()
                st.rerun()
    st.stop()

# ── Navegación ──
if "_goto" in st.session_state:
    st.session_state["nav"] = st.session_state.pop("_goto")

alertas = K.calcular_alertas()
n_crit = sum(1 for a in alertas if a["nivel"] in ("critical", "serious"))


def _fmt(p):
    return f"{p}  ·  {n_crit}" if p == K.PAG_ALERTAS and n_crit else p


# ── Menú superior para celular (el CSS lo muestra solo en pantallas angostas) ──
def _desde_movil():
    st.session_state["nav"] = st.session_state["nav_m"]


st.session_state.setdefault("nav", K.PAGINAS[0])
st.session_state["nav_m"] = st.session_state["nav"]
with st.container(key="nav_movil"):
    st.selectbox("☰ Menú", K.PAGINAS, key="nav_m", format_func=_fmt, on_change=_desde_movil, label_visibility="collapsed")

with st.sidebar:
    if os.path.exists(K.LOGO):
        c1, c2, c3 = st.columns([1, 2, 1])
        c2.image(K.LOGO, width=90)
    st.markdown(
        f"<div style='text-align:center;font-weight:800;font-size:1rem;letter-spacing:.3px'>MESA DE ENTRADAS</div>"
        f"<div style='text-align:center;color:#60A5FA;font-size:.74rem;font-weight:600;margin-bottom:10px'>{C.INSTITUCION}</div>",
        unsafe_allow_html=True,
    )

    pagina = st.radio("Navegación", K.PAGINAS, key="nav", format_func=_fmt, label_visibility="collapsed")
    st.markdown("---")
    st.caption(f"👤 {K.usuario()}")
    cs1, cs2 = st.columns(2)
    if cs1.button("🔄 Actualizar"):
        db.invalidar()
        st.rerun()
    if cs2.button("🚪 Salir"):
        st.session_state.clear()
        st.rerun()

if n_crit and not st.session_state.get("_avisado"):
    st.toast(f"Hay {n_crit} alertas prioritarias. Revise 🔔 Alertas y Agenda.", icon="🔔")
    st.session_state["_avisado"] = True

VISTAS = {
    K.PAG_PANEL: v_panel.render,
    K.PAG_NUEVO: v_nuevo.render,
    K.PAG_MOV: v_movimiento.render,
    K.PAG_LIBRO: v_libro.render,
    K.PAG_FICHA: v_ficha.render,
    K.PAG_CURSOS: v_cursos.render,
    K.PAG_ALERTAS: lambda: v_alertas.render(alertas),
    K.PAG_CARGA: v_carga.render,
    K.PAG_INFORMES: v_informes.render,
    K.PAG_CONFIG: v_config.render,
}
VISTAS[pagina]()
