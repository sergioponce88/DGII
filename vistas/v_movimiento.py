import streamlit as st

import catalogos as C
import comun as K
import db
import ui


def render():
    ui.header("Movimiento Rápido", "Trámite, reingresos, salidas y pases · pensado para el celular")
    exp = db.df_expedientes()
    if exp.empty:
        st.info("No hay expedientes registrados.")
        return
    st.session_state.setdefault("mr_abiertos", True)
    if st.session_state.pop("mr_reingreso", False):
        st.session_state["mr_abiertos"] = False
    solo_abiertos = st.toggle("Solo expedientes abiertos", key="mr_abiertos",
                              help="Desactívelo para encontrar expedientes resueltos o archivados que vuelven.")
    base = exp[~exp["estado"].isin(C.ESTADOS_CERRADOS)] if solo_abiertos else exp
    r = K.selector_expediente("mov_sel", base)
    if r is None:
        return
    ui.tarjeta_expediente(r, detalle=False)
    afuera = bool(r.get("tramitado")) or (r.get("ubicacion_actual") or C.DEP_PROPIA) != C.DEP_PROPIA or r["estado"] in C.ESTADOS_CERRADOS
    opciones = ["✅ Trámite", "📥 Reingreso", "🔁 Movimiento"]
    accion = st.segmented_control("Acción", opciones, default="📥 Reingreso" if afuera else "✅ Trámite", key=f"mr_accion_{r['id']}")
    if accion == "📥 Reingreso":
        K.form_reingreso(r, "rapido")
    elif accion == "🔁 Movimiento":
        K.form_movimiento(r, "rapido")
    else:
        K.form_tramite(r, "rapido")
    with st.expander("🧭 Hoja de ruta"):
        movs = db.df_movimientos()
        ui.timeline(movs[movs["expediente_id"] == r["id"]].head(10))
