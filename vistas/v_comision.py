"""🚚 Comisión: el comisionista del día lleva los expedientes tramitados y registra quién los recibe.

El oficial deja el encargo (destino y despacho) al tramitar; el comisionista lo ve en «Para entregar»,
completa quién lo recibe y lo asienta. El movimiento queda en la hoja de ruta para el oficial.
"""
from datetime import datetime, time

import pandas as pd
import streamlit as st

import catalogos as C
import comun as K
import db
import reportes as R
import ui

TIPOS_ENTREGA = ["SALIDA", "DEVOLUCIÓN", "PASE INTERNO"]


def _pendientes(exp):
    p = exp[exp["entrega_pendiente"].fillna(False).astype(bool)]
    return p.sort_values("entrega_solicitada_en", ascending=True, na_position="last")


def _tramitados_en_direccion(exp):
    """Tramitados que siguen en la Dirección (para buscarlos aunque no tengan encargo)."""
    t = exp[exp["tramitado"] & (exp["ubicacion_actual"].fillna(C.DEP_PROPIA) == C.DEP_PROPIA)
            & ~exp["estado"].isin(C.ESTADOS_CERRADOS)]
    return t


def render():
    ui.header("Comisión", "Entrega de expedientes tramitados · registre quién los recibe")
    import auth

    if not auth.puede("entregar"):
        auth.aviso_sin_permiso("la entrega de expedientes")
        return
    exp = db.df_expedientes()
    for c in ("entrega_pendiente", "entrega_destino", "entrega_despacho", "entrega_indicaciones", "entrega_solicitada_por",
              "entrega_solicitada_en"):
        if c not in exp.columns:
            exp[c] = None
    exp["entrega_solicitada_en"] = pd.to_datetime(exp["entrega_solicitada_en"], errors="coerce")
    pend = _pendientes(exp)
    movs = db.df_movimientos()
    hoy = pd.Timestamp(db.hoy())
    yo = K.usuario()
    hechas = movs[(movs["fecha_hora"].dt.normalize() == hoy) & (movs["tipo"].isin(TIPOS_ENTREGA))] if not movs.empty else movs
    mias = hechas[hechas["registrado_por"].fillna("") == yo] if not hechas.empty else hechas

    ui.kpis([
        ("Para entregar", len(pend), "encargados por los oficiales", C.STATUS["warning"]),
        ("Entregados hoy", len(mias), "por usted", C.STATUS["ok"]),
        ("Entregas del día", len(hechas), "todos los comisionistas", C.PALETA[6]),
    ])

    sel = st.session_state.get("com_sel")
    if sel is None:
        _lista(pend)
        with st.expander("🔎 Buscar otro expediente tramitado"):
            base = _tramitados_en_direccion(exp)
            if base.empty:
                st.caption("No hay otros expedientes tramitados en la Dirección.")
            else:
                r = K.selector_expediente("com_buscar", base, label="N° o asunto")
                if r is not None and st.button("Entregar este expediente", key="com_buscar_ok", type="primary"):
                    st.session_state["com_sel"] = int(r["id"])
                    st.rerun()
        _hechas(hechas)
        return

    fila = exp[exp["id"] == sel]
    if fila.empty:
        st.session_state.pop("com_sel", None)
        st.rerun()
    _formulario(fila.iloc[0], yo)


def _lista(pend):
    ui.seccion("📦 Para entregar")
    if pend.empty:
        st.markdown('<div class="alerta" style="border-color:rgba(34,197,94,.5);background:rgba(34,197,94,.10)"><div class="ic">✅</div>'
                    '<div><div class="at">No hay entregas pendientes</div><div class="ad">Cuando un oficial tramite un expediente y lo '
                    'encargue, aparecerá aquí.</div></div></div>', unsafe_allow_html=True)
        return
    mapa = ui.mapa_dependencias()
    for _, r in pend.iterrows():
        dest = r.get("entrega_destino") or "—"
        col = ui.color_dep(dest, mapa)
        extra = (f"<br>📝 {ui.esc(r['entrega_indicaciones'])}" if r.get("entrega_indicaciones") else "")
        st.markdown(
            f'<div class="card acc" style="--c:{col}"><div class="ident">{ui.esc(r["identificador"])}'
            f'<small>{C.SECRETARIAS[C.sec_de(r.get("secretaria"))]["sigla"]} · {ui.esc(r["tipo"])}</small></div>'
            f'<div class="meta"><b>➜ {ui.esc(dest)}</b>'
            f'{" · " + ui.esc(r["entrega_despacho"]) if r.get("entrega_despacho") else ""}<br>'
            f'{ui.esc((r.get("asunto") or "")[:110])}<br>'
            f'<span style="color:#94A3B8">Encargó: {ui.esc(r.get("entrega_solicitada_por") or "—")} · '
            f'{ui.fmt_fecha(r.get("entrega_solicitada_en"), True)} · {K.num(r.get("fojas"))} fojas</span>{extra}</div></div>',
            unsafe_allow_html=True)
        if st.button(f"🚚 Entregar {r['identificador']}", key=f"com_ent_{r['id']}", type="primary", width="stretch"):
            st.session_state["com_sel"] = int(r["id"])
            st.rerun()


def _formulario(r, yo):
    if st.button("← Volver a la lista", key="com_volver"):
        st.session_state.pop("com_sel", None)
        st.rerun()
    ui.tarjeta_expediente(r, detalle=True)
    lista_dep = K.deps()
    dest_def = r.get("entrega_destino") or r.get("destino") or (lista_dep[1] if len(lista_dep) > 1 else lista_dep[0])
    if dest_def and dest_def not in lista_dep:
        lista_dep = [dest_def] + lista_dep
    if r.get("entrega_indicaciones"):
        ui.alerta("📝", "Indicaciones del oficial", r["entrega_indicaciones"], C.STATUS["warning"])
    with st.form(f"com_form_{r['id']}"):
        c1, c2 = st.columns(2)
        tipo = c1.selectbox("Tipo de movimiento", TIPOS_ENTREGA)
        destino = c2.selectbox("Destino ➜", lista_dep, index=K.idx(lista_dep, dest_def))
        c3, c4 = st.columns(2)
        c3.text_input("Desde", C.DEP_PROPIA, disabled=True)
        despacho = c4.selectbox("Despacho / Resolución", C.DESPACHOS, index=K.idx(C.DESPACHOS, r.get("entrega_despacho") or r.get("despacho") or ""),
                                format_func=lambda d: d or "— Sin indicar —")
        c5, c6 = st.columns(2)
        f = c5.date_input("Fecha", db.hoy(), format="DD/MM/YYYY")
        h = c6.time_input("Hora", db.ahora().time().replace(second=0), step=60)
        c7, c8 = st.columns(2)
        lleva = c7.text_input("Quién lo lleva / entrega", yo)
        recibe = c8.text_input("Quién lo recibe *", placeholder="Grado, apellido y nombre de quien recibe")
        c9, c10 = st.columns([1, 2])
        fojas = c9.number_input("Fojas", min_value=0, value=K.num(r.get("fojas")), step=1)
        obs = c10.text_input("Observaciones", placeholder="Ej.: se entregó en Mesa de Entradas de la Escuela")
        ok = st.form_submit_button("✅ Registrar entrega", type="primary")
    if ok:
        if not recibe.strip():
            st.error("Indique quién recibe el expediente en la dependencia.")
            return
        mov = {"fecha_hora": datetime.combine(f, h if isinstance(h, time) else time(0, 0)), "tipo": tipo, "origen": C.DEP_PROPIA,
               "destino": destino, "despacho": despacho or None, "entregado_por": lleva.strip().upper() or yo,
               "recibido_por": recibe.strip().upper(), "fojas": int(fojas) or None, "observaciones": obs.strip() or None}
        estado = C.ESTADO_POR_MOVIMIENTO.get(tipo, "REMITIDO")
        try:
            db.registrar_entrega(int(r["id"]), mov, estado, yo)
        except Exception as e:
            st.error(f"No se pudo registrar la entrega: {e}")
            return
        st.session_state["com_ult"] = {"exp": dict(r), "mov": mov}
        st.session_state.pop("com_sel", None)
        st.toast(f"Entrega registrada: {r['identificador']} → {destino}", icon="✅")
        st.rerun()


def _hechas(hechas):
    ult = st.session_state.get("com_ult")
    if ult:
        m = ult["mov"]
        st.success(f"✔ Última entrega: {ult['exp']['identificador']} → {m['destino']} · recibió {m['recibido_por']}")
        st.link_button("📲 Avisar por WhatsApp", R.link_whatsapp(R.msg_movimiento(ult["exp"], m), K.tel_dep(m["destino"])))
    if hechas.empty:
        return
    ui.seccion("✅ Entregados hoy")
    for _, m in hechas.head(30).iterrows():
        st.markdown(f"<small>{ui.fmt_fecha(m['fecha_hora'], True)} · <b>{ui.esc(m['identificador'])}</b> → {ui.esc(m['destino'])} · "
                    f"recibió <b>{ui.esc(m.get('recibido_por') or '—')}</b> · llevó {ui.esc(m.get('entregado_por') or '—')}</small>",
                    unsafe_allow_html=True)
