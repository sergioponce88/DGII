import streamlit as st

import catalogos as C
import comun as K
import db
import ui


def render():
    ui.header("Movimiento Rápido", "Trámite, salidas, ingresos y pases · pensado para el celular")
    exp = db.df_expedientes()
    if exp.empty:
        st.info("No hay expedientes registrados.")
        return
    solo_abiertos = st.toggle("Solo expedientes abiertos", value=True)
    base = exp[~exp["estado"].isin(C.ESTADOS_CERRADOS)] if solo_abiertos else exp
    r = K.selector_expediente("mov_sel", base)
    if r is None:
        return
    ui.tarjeta_expediente(r, detalle=False)
    accion = st.segmented_control("Acción", ["✅ Trámite", "🔁 Movimiento"], default="✅ Trámite", key="mr_accion")
    if accion == "🔁 Movimiento":
        K.form_movimiento(r, "rapido")
    else:
        K.form_tramite(r, "rapido")
    with st.expander("🧭 Hoja de ruta"):
        movs = db.df_movimientos()
        ui.timeline(movs[movs["expediente_id"] == r["id"]].head(10))
