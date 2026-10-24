"""🧭 Mi trabajo: una sola ruta según quién trabaja.

SUBOFICIAL (mesa de entradas): llega un expediente → lo busca → reingreso o alta → queda para el oficial.
OFICIAL: bandeja «Para tramitar» → nota en Word o «Tramitar y despachar» → «Para despachar» → comisionista.
COMISIONISTA: su propia pantalla de entregas (Comisión).
"""
import pandas as pd
import streamlit as st

import catalogos as C
import comun as K
import db
import ui

RUTAS = {
    "SUBOFICIAL": ["📥 Llega", "🔎 Lo busco", "✍️ Reingreso o alta", "👮 Queda para el oficial"],
    "OFICIAL": ["📋 Para tramitar", "📝 Nota o ✅ trámite", "📦 Despacho", "🚚 Comisionista"],
    "ADMINISTRADOR": ["📥 Mesa de entradas", "📋 Para tramitar", "📦 Despacho", "🚚 Comisionista"],
}


def _ruta(rol):
    pasos = RUTAS.get(rol, RUTAS["OFICIAL"])
    html = " <span style='color:#64748B'>➜</span> ".join(
        f"<span style='background:rgba(59,130,246,.14);border:1px solid rgba(96,165,250,.35);border-radius:999px;"
        f"padding:3px 10px;font-size:.8rem;font-weight:700;white-space:nowrap'>{p}</span>" for p in pasos)
    st.markdown(f"<div style='margin:-4px 0 12px;line-height:2.1'>{html}</div>", unsafe_allow_html=True)


def _orden(df):
    h = pd.Timestamp(db.hoy())
    d = df.copy()
    d["_venc"] = d["fecha_termino"].notna() & (d["fecha_termino"] < h)
    d["_urg"] = d["prioridad"] == "URGENTE TRÁMITE"
    d["_dias"] = (h - d["ult_mov"].fillna(d["fecha_ingreso"]).dt.normalize()).dt.days.fillna(0)
    return d.sort_values(["_venc", "_urg", "_dias"], ascending=[False, False, False])


def _en_casa(exp):
    return exp[(exp["ubicacion_actual"].fillna(C.DEP_PROPIA) == C.DEP_PROPIA) & ~exp["estado"].isin(C.ESTADOS_CERRADOS)]


# ───────────────────────── Mesa de entradas (suboficial / todos) ─────────────────────────
def mesa_entradas(exp):
    ui.seccion("📥 Llegó un expediente")
    q = st.text_input("Busque por N° (de la Dirección o de origen) o por asunto", key="tb_q",
                      placeholder="Ej.: 546  ·  J-1234/26  ·  curso de tiro").strip()
    if not q:
        st.caption("Escriba el número: si ya está registrado se asienta el **reingreso**; si no, se carga como **nuevo**.")
        return
    ql = q.lower()
    campos = ["identificador", "nro_exp_origen", "asunto", "iniciador"]
    m = pd.Series(False, index=exp.index)
    for c in campos:
        if c in exp.columns:
            m |= exp[c].fillna("").astype(str).str.lower().str.contains(ql, regex=False)
    res = exp[m].sort_values("fecha_ingreso", ascending=False).head(6)
    if res.empty:
        st.warning(f"No hay ningún expediente registrado con «{q}».")
        if st.button("➕ Registrarlo como expediente nuevo", key="tb_nuevo", type="primary", width="stretch"):
            K.ir_a(K.PAG_NUEVO)
        return
    sel = st.session_state.get("tb_rei")
    for _, r in res.iterrows():
        ui.tarjeta_expediente(r, detalle=False)
        if sel == int(r["id"]):
            K.form_reingreso(r, "tb")
            if st.button("✖ Cerrar", key=f"tb_rei_x_{r['id']}"):
                st.session_state.pop("tb_rei", None)
                st.rerun()
        elif st.button(f"↩️ Volvió: registrar reingreso de {r['identificador']}", key=f"tb_rei_{r['id']}", width="stretch"):
            st.session_state["tb_rei"] = int(r["id"])
            st.rerun()
    if st.button("➕ No es ninguno: cargar como nuevo", key="tb_nuevo2"):
        K.ir_a(K.PAG_NUEVO)


def _recibidos_hoy(movs):
    if movs.empty:
        return
    h = pd.Timestamp(db.hoy())
    hoy = movs[(movs["fecha_hora"].dt.normalize() == h) & movs["tipo"].isin(["INGRESO", "REINGRESO"])]
    if hoy.empty:
        return
    with st.expander(f"🗂️ Recibidos hoy ({len(hoy)})"):
        for _, m in hoy.iterrows():
            st.markdown(f"<small>{ui.fmt_fecha(m['fecha_hora'], True)} · <b>{ui.esc(m['identificador'])}</b> · {m['tipo']} desde "
                        f"{ui.esc(m['origen'] or '—')} · trajo {ui.esc(m.get('entregado_por') or '—')}</small>", unsafe_allow_html=True)


# ───────────────────────── Bandeja del oficial ─────────────────────────
def _acciones(r, key, despachar=False):
    abierto = st.session_state.get("tb_open") == (key, int(r["id"]))
    b1, b2 = st.columns(2)
    if not despachar and b1.button("📝 Nota en Word", key=f"tb_w_{key}_{r['id']}", width="stretch"):
        st.session_state["tram_sel"] = int(r["id"])
        K.ir_a(K.PAG_TRAMITAR, r["id"])
    txt = ("📦 Despachar" if despachar else "✅ Tramitar y despachar") if not abierto else "✖ Cerrar"
    col = b1 if despachar else b2
    if col.button(txt, key=f"tb_t_{key}_{r['id']}", type="secondary" if abierto else "primary", width="stretch"):
        st.session_state["tb_open"] = None if abierto else (key, int(r["id"]))
        st.rerun()
    if abierto:
        K.form_tramite(r, f"tb{key}{int(r['id'])}")


def _lista(df, key, vacio, despachar=False, max_n=25):
    if df.empty:
        st.markdown(f'<div class="tr-listo">✅ {vacio}</div>', unsafe_allow_html=True)
        return
    mapa = ui.mapa_dependencias()
    for _, r in df.head(max_n).iterrows():
        ui.tarjeta_expediente(r, mapa, detalle=False)
        _acciones(r, key, despachar)
    if len(df) > max_n:
        st.caption(f"… y {len(df) - max_n} más. Use 📚 Libro de Registro para verlos todos.")


def bandeja_oficial(exp):
    casa = _en_casa(exp)
    para_tramitar = _orden(casa[~casa["tramitado"]])
    para_despachar = _orden(casa[casa["tramitado"] & ~casa["entrega_pendiente"].fillna(False).astype(bool)])
    encargados = exp[exp["entrega_pendiente"].fillna(False).astype(bool)]
    venc = int(para_tramitar["_venc"].sum()) if not para_tramitar.empty else 0
    ui.kpis([
        ("Para tramitar", len(para_tramitar), f"{venc} vencidos · {int(para_tramitar['_urg'].sum()) if len(para_tramitar) else 0} urgentes",
         C.STATUS["warning"]),
        ("Para despachar", len(para_despachar), "tramitados que siguen aquí", C.PALETA[3]),
        ("Con el comisionista", len(encargados), "esperando entrega", C.PALETA[6]),
    ])
    t1, t2, t3 = st.tabs([f"📋 Para tramitar ({len(para_tramitar)})", f"📦 Para despachar ({len(para_despachar)})",
                          f"🚚 Con el comisionista ({len(encargados)})"])
    with t1:
        st.caption("Ordenados: vencidos, urgentes y más días esperando primero. Toque **Tramitar y despachar** y se hace todo en un paso.")
        _lista(para_tramitar, "pt", "No hay expedientes pendientes de trámite en la Dirección.")
    with t2:
        st.caption("Ya tramitados que siguen en la Dirección: encárguelos al comisionista o regístrelos como entregados.")
        _lista(para_despachar, "pd", "Nada para despachar.", despachar=True)
    with t3:
        if encargados.empty:
            st.caption("No hay entregas pendientes.")
        for _, r in encargados.iterrows():
            st.markdown(f"<small>🚚 <b>{ui.esc(r['identificador'])}</b> → {ui.esc(r.get('entrega_destino') or '—')} · "
                        f"encargó {ui.esc(r.get('entrega_solicitada_por') or '—')} · {ui.fmt_fecha(r.get('entrega_solicitada_en'), True)}</small>",
                        unsafe_allow_html=True)


def render():
    import auth

    rol = auth.rol() or "OFICIAL"
    ui.header("Mi trabajo", {"SUBOFICIAL": "Mesa de entradas: recibir y registrar",
                             "OFICIAL": "Bandeja del oficial: tramitar y despachar",
                             "ADMINISTRADOR": "Mesa de entradas y bandeja de trámite"}.get(rol, ""))
    _ruta(rol)
    exp = db.df_expedientes()
    for c in ("entrega_pendiente", "entrega_destino", "entrega_solicitada_por", "entrega_solicitada_en"):
        if c not in exp.columns:
            exp[c] = None
    movs = db.df_movimientos()
    if auth.puede("tramitar"):
        with st.expander("📥 Llegó un expediente (buscar · reingreso · nuevo)", expanded=bool(st.session_state.get("tb_q"))):
            mesa_entradas(exp)
        if exp.empty:
            return
        bandeja_oficial(exp)
    else:
        mesa_entradas(exp)
        if not exp.empty:
            casa = _en_casa(exp)
            n = int((~casa["tramitado"]).sum())
            st.caption(f"👮 En la Dirección esperando trámite del oficial: **{n}** expediente(s).")
    _recibidos_hoy(movs)
