"""Sistema de Registro y Control de Expedientes — Dirección General de Institutos e Instrucción (Policía de Tucumán)."""
import os

import streamlit as st

st.set_page_config(
    page_title="Expedientes · D.G.I.I.",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="auto",
)

# Al publicar cambios, Streamlit Cloud a veces conserva módulos viejos en memoria (AttributeError en K.PAG_…):
# si el archivo de un módulo propio cambió desde que se cargó, se recarga en orden de dependencias.
import importlib  # noqa: E402
import sys  # noqa: E402

_PROPIOS = ["catalogos", "docword", "redaccion", "db", "auth", "gdrive", "reportes", "ui", "comun", "modelos", "avisos"]
_VISTAS = ["v_alertas", "v_carga", "v_config", "v_cursos", "v_ficha", "v_informes", "v_libro", "v_movimiento",
           "v_tramitar", "v_comision", "v_nuevo", "v_panel", "v_trabajo"]
_cambio = False
for _n in _PROPIOS + [f"vistas.{v}" for v in _VISTAS]:
    _m = sys.modules.get(_n)
    if _m is None or not getattr(_m, "__file__", None):
        continue
    try:
        _t = os.path.getmtime(_m.__file__)
    except OSError:
        continue
    if _cambio or getattr(_m, "_mtime_carga", None) != _t:  # sin marca = cargado por una versión anterior
        _cambio = True
        _m = importlib.reload(_m)
    _m._mtime_carga = _t

import auth  # noqa: E402
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
    v_tramitar,
    v_comision,
    v_trabajo,
    v_nuevo,
    v_panel,
)

for _n in _PROPIOS + [f"vistas.{v}" for v in _VISTAS]:  # marca de carga de esta versión
    _m = sys.modules.get(_n)
    if _m is not None and getattr(_m, "__file__", None):
        try:
            _m._mtime_carga = os.path.getmtime(_m.__file__)
        except OSError:
            pass

ui.css()

# ── Base de datos ──
try:
    db.init_db(db.VERSION_ESQUEMA)
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


def _pantalla_acceso():
    ui.header("Registro de Expedientes", logo=K.LOGO if os.path.exists(K.LOGO) else None)
    _, mid, _ = st.columns([1, 2, 1])
    if not auth.hay_usuarios():
        # Primer uso: se crea el administrador. Si hay APP_PASSWORD, se exige para evitar altas ajenas.
        with mid, st.form("primer_admin"):
            st.markdown("#### 🛡️ Primer ingreso: crear el usuario administrador")
            clave_app = st.text_input("Clave de la app (APP_PASSWORD)", type="password") if _secret("APP_PASSWORD") else ""
            c1, c2 = st.columns(2)
            grado = c1.selectbox("Grado", C.GRADOS_USUARIO)
            legajo = c2.text_input("Legajo (será su usuario)")
            apellido = c1.text_input("Apellido")
            nombre = c2.text_input("Nombre")
            funcion = st.text_input("Función", placeholder="Ej: JEFE DE MESA DE ENTRADAS")
            p1 = c1.text_input("Clave", type="password")
            p2 = c2.text_input("Repetir clave", type="password")
            if st.form_submit_button("Crear administrador"):
                if _secret("APP_PASSWORD") and clave_app != _secret("APP_PASSWORD"):
                    st.error("Clave de la app incorrecta.")
                elif p1 != p2:
                    st.error("Las claves no coinciden.")
                else:
                    try:
                        auth.crear_usuario(legajo, grado, apellido, nombre, funcion, "ADMINISTRADOR", p1)
                        st.success("Administrador creado. Ingrese con su legajo y clave.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
        st.stop()
    with mid, st.form("login"):
        st.markdown("#### 🔐 Ingreso")
        legajo = st.text_input("Legajo")
        clave = st.text_input("Clave", type="password")
        if st.form_submit_button("Ingresar"):
            u, err = auth.login(legajo, clave)
            if err:
                st.error(err)
            else:
                st.session_state["usuario"] = u
                st.rerun()
    mid.caption(f"📲 ¿Usa el celular? [Instale la aplicación]({K.URL_APP}) (Android y iPhone).")
    st.stop()


def _cambio_obligatorio():
    ui.header("Cambio de clave", "Por seguridad, defina una clave personal antes de continuar")
    _, mid, _ = st.columns([1, 2, 1])
    with mid, st.form("cambio_obl"):
        p1 = st.text_input("Nueva clave (mínimo 6 caracteres)", type="password")
        p2 = st.text_input("Repetir nueva clave", type="password")
        if st.form_submit_button("Guardar clave"):
            if p1 != p2:
                st.error("Las claves no coinciden.")
            else:
                try:
                    auth.cambiar_clave(auth.actual()["id"], p1, K.usuario())
                    st.session_state["usuario"]["debe_cambiar"] = False
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
    st.stop()


if not auth.actual():
    _pantalla_acceso()
if auth.actual().get("debe_cambiar"):
    _cambio_obligatorio()

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


if auth.rol() == "COMISIONISTA":  # el comisionista solo ve sus entregas
    PAGINAS_OK = [K.PAG_COMISION]
else:
    PAGINAS_OK = [p for p in K.PAGINAS if (p not in (K.PAG_CONFIG, K.PAG_CARGA) or auth.puede("configurar"))
                  and (p != K.PAG_TRAMITAR or auth.puede("tramitar"))
                  and (p != K.PAG_COMISION or auth.puede("entregar"))]
if st.session_state.get("nav") not in PAGINAS_OK:
    st.session_state["nav"] = PAGINAS_OK[0]
st.session_state.setdefault("nav", PAGINAS_OK[0])
st.session_state["nav_m"] = st.session_state["nav"]
with st.container(key="nav_movil"):
    st.selectbox("☰ Menú", PAGINAS_OK, key="nav_m", format_func=_fmt, on_change=_desde_movil, label_visibility="collapsed")

with st.sidebar:
    if os.path.exists(K.LOGO):
        c1, c2, c3 = st.columns([1, 2, 1])
        c2.image(K.LOGO, width=90)
    st.markdown(
        f"<div style='text-align:center;font-weight:800;font-size:1rem;letter-spacing:.3px'>MESA DE ENTRADAS</div>"
        f"<div style='text-align:center;color:#60A5FA;font-size:.74rem;font-weight:600;margin-bottom:10px'>{C.INSTITUCION}</div>",
        unsafe_allow_html=True,
    )

    pagina = st.radio("Navegación", PAGINAS_OK, key="nav", format_func=_fmt, label_visibility="collapsed")
    st.markdown("---")
    _u = auth.actual()
    st.markdown(f"<div style='font-size:.82rem;line-height:1.35'>👤 <b>{ui.esc(K.usuario())}</b><br>"
                f"<span style='color:#94A3B8'>Legajo {ui.esc(_u['legajo'])} · {ui.esc(_u.get('funcion') or '')}</span><br>"
                f"{ui.chip(_u['rol'], C.PALETA[0] if _u['rol'] == 'ADMINISTRADOR' else (C.PALETA[2] if _u['rol'] == 'OFICIAL' else (C.PALETA[6] if _u['rol'] == 'COMISIONISTA' else C.PALETA[3])), False)}</div>",
                unsafe_allow_html=True)
    with st.expander("🔑 Cambiar mi clave"):
        with st.form("mi_clave", clear_on_submit=True):
            actual_c = st.text_input("Clave actual", type="password")
            n1 = st.text_input("Nueva clave", type="password")
            n2 = st.text_input("Repetir", type="password")
            if st.form_submit_button("Cambiar"):
                ok_u, _err = auth.login(_u["legajo"], actual_c)
                if not ok_u:
                    st.error("Clave actual incorrecta.")
                elif n1 != n2:
                    st.error("No coinciden.")
                else:
                    try:
                        auth.cambiar_clave(_u["id"], n1, K.usuario())
                        st.success("Clave actualizada.")
                    except ValueError as e:
                        st.error(str(e))
    st.caption(f"📲 [Instalar la app en el celular]({K.URL_APP})")
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

# Lo que trajo el comisionista y falta asentar en el libro: aviso visible para quien carga (suboficiales y oficiales)
if auth.puede("cargar") and auth.rol() != "COMISIONISTA":
    try:
        _rec = db.df_recepciones()
    except Exception:
        _rec = None
    if _rec is not None and not _rec.empty:
        _n = len(_rec)
        _lst = ", ".join(f"{r['numero']} ({r['origen'] or '—'})" for _, r in _rec.head(4).iterrows()) + (" …" if _n > 4 else "")
        if pagina != K.PAG_TRABAJO:
            _a, _b = st.columns([4, 1], vertical_alignment="center")
            with _a:
                ui.alerta("📦", f"El comisionista trajo {_n} expediente(s) para registrar en el libro", _lst, C.STATUS["warning"])
            if _b.button("📥 Registrar ahora", key="rec_ir", type="primary", width="stretch"):
                K.ir_a(K.PAG_TRABAJO)
        if st.session_state.get("_rec_avisado") != _n:
            st.toast(f"📦 {_n} expediente(s) traído(s) por el comisionista para registrar en el libro.", icon="📦")
            st.session_state["_rec_avisado"] = _n

VISTAS = {
    K.PAG_TRABAJO: v_trabajo.render,
    K.PAG_PANEL: v_panel.render,
    K.PAG_NUEVO: v_nuevo.render,
    K.PAG_MOV: v_movimiento.render,
    K.PAG_TRAMITAR: v_tramitar.render,
    K.PAG_COMISION: v_comision.render,
    K.PAG_LIBRO: v_libro.render,
    K.PAG_FICHA: v_ficha.render,
    K.PAG_CURSOS: v_cursos.render,
    K.PAG_ALERTAS: lambda: v_alertas.render(alertas),
    K.PAG_CARGA: v_carga.render,
    K.PAG_INFORMES: v_informes.render,
    K.PAG_CONFIG: v_config.render,
}
VISTAS[pagina]()
