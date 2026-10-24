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
    import auth

    if auth.rol() == "COMISIONISTA":
        return render_simple()
    ui.header("Comisión", "Entrega de expedientes tramitados · registre quién los recibe")

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
        lin = [f"• *{r['identificador']}* ➜ {r.get('entrega_destino') or '—'}" + (f" · {r['entrega_despacho']}" if r.get("entrega_despacho") else "")
               for r in pend.to_dict("records")] or ["Sin entregas pendientes."]
        if not hechas.empty:
            lin += ["", "*✅ Entregados hoy*"] + [f"• {ui.fmt_fecha(m['fecha_hora'], True)} · *{m['identificador']}* ➜ {m['destino']} · recibió {m.get('recibido_por') or '—'}"
                                                 for m in hechas.to_dict("records")]
        K.compartir_wp(R.msg_lista("Comisión del día", lin, sub=f"{len(pend)} para entregar · {len(hechas)} entregados"),
                       "comision", "📲 Informar la comisión por WhatsApp")
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
    import auth

    solo = auth.rol() == "COMISIONISTA"  # el comisionista solo carga fecha, hora, quién recibe y observaciones
    desp_def = r.get("entrega_despacho") or r.get("despacho") or ""
    with st.form(f"com_form_{r['id']}"):
        c1, c2 = st.columns(2)
        tipo = c1.selectbox("Tipo de movimiento", TIPOS_ENTREGA, disabled=solo)
        destino = c2.selectbox("Destino ➜", lista_dep, index=K.idx(lista_dep, dest_def), disabled=solo)
        c3, c4 = st.columns(2)
        c3.text_input("Desde", C.DEP_PROPIA, disabled=True)
        if solo:
            c4.text_input("Despacho / Resolución", desp_def or "— Sin indicar —", disabled=True)
            despacho = desp_def
        else:
            despacho = K.campo_despacho(c4, "Despacho / Resolución", f"com_desp_{r['id']}", desp_def)
        c5, c6 = st.columns(2)
        f = c5.date_input("Fecha", db.hoy(), format="DD/MM/YYYY")
        h = c6.time_input("Hora", db.ahora().time().replace(second=0), step=60)
        c7, c8 = st.columns(2)
        if solo:
            lleva = c7.text_input("Quién lo lleva / entrega", yo, disabled=True)
            recibe = c8.text_input("Quién lo recibe *", key=f"com_recibe_t_{r['id']}", placeholder="Grado, apellido y nombre de quien lo recibe")
        else:
            lleva = K.campo_persona(c7, "Quién lo lleva / entrega", f"com_lleva_{r['id']}", defecto=yo)
            recibe = K.campo_persona(c8, "Quién lo recibe *", f"com_recibe_{r['id']}")
        c9, c10 = st.columns([1, 2])
        fojas = c9.number_input("Fojas", min_value=0, value=K.num(r.get("fojas")), step=1, disabled=solo)
        obs = c10.text_input("Observaciones", placeholder="Ej.: se entregó en Mesa de Entradas de la Escuela")
        ok = st.form_submit_button("✅ Registrar entrega", type="primary")
    if ok:
        if not recibe.strip():
            st.error("Indique quién recibe el expediente en la dependencia.")
            return
        mov = {"fecha_hora": datetime.combine(f, h if isinstance(h, time) else time(0, 0)), "tipo": tipo, "origen": C.DEP_PROPIA,
               "destino": destino, "despacho": despacho or None, "entregado_por": yo if solo else (lleva.strip().upper() or yo),
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


# ───────────────────────── Pantalla simple del comisionista ─────────────────────────
CSS_SIMPLE = """<style>
.ent{border-radius:18px;padding:18px 20px;margin:6px 0 8px;background:rgba(245,158,11,.10);border:2px solid rgba(245,158,11,.55)}
.ent .n{font-size:2.1rem;font-weight:900;letter-spacing:.5px;line-height:1.1}
.ent .l{font-size:.78rem;font-weight:800;color:#94A3B8;letter-spacing:1px;margin-top:10px}
.ent .d{font-size:1.35rem;font-weight:800;color:#FDE68A;line-height:1.25}
.ent .i{font-size:.95rem;color:#E2E8F0;margin-top:8px}
.ok-ent{font-size:.95rem;color:#CBD5E1;padding:6px 0;border-bottom:1px solid #1E293B}
</style>"""


def _tarjeta_simple(r):
    ind = f'<div class="i">📝 {ui.esc(r["entrega_indicaciones"])}</div>' if r.get("entrega_indicaciones") else ""
    st.markdown(f'<div class="ent"><div class="l">N° DE EXPEDIENTE</div><div class="n">{ui.esc(r["identificador"])}</div>'
                f'<div class="l">LLEVAR A</div><div class="d">{ui.esc(r.get("entrega_destino") or "—")}</div>{ind}</div>',
                unsafe_allow_html=True)


def render_simple():
    st.markdown(CSS_SIMPLE, unsafe_allow_html=True)
    yo = K.usuario()
    exp = db.df_expedientes()
    if "entrega_pendiente" not in exp.columns:
        exp["entrega_pendiente"] = False
    exp["entrega_solicitada_en"] = pd.to_datetime(exp.get("entrega_solicitada_en"), errors="coerce")
    pend = _pendientes(exp)
    sel = st.session_state.get("com_sel")
    fila = exp[exp["id"] == sel] if sel is not None else exp.iloc[0:0]

    if sel is not None and not fila.empty:
        r = fila.iloc[0]
        if st.button("← Volver", key="cs_volver"):
            st.session_state.pop("com_sel", None)
            st.rerun()
        _tarjeta_simple(r)
        with st.form(f"cs_form_{r['id']}"):
            c1, c2 = st.columns(2)
            f = c1.date_input("Fecha", db.hoy(), format="DD/MM/YYYY")
            h = c2.time_input("Hora", db.ahora().time().replace(second=0), step=60)
            recibe = st.text_input("¿Quién lo recibió?", placeholder="Grado, apellido y nombre")
            obs = st.text_input("Observaciones (opcional)")
            ok = st.form_submit_button("✅ ENTREGADO", type="primary", width="stretch")
        if ok:
            if not recibe.strip():
                st.error("Escriba quién recibió el expediente.")
                return
            mov = {"fecha_hora": datetime.combine(f, h if isinstance(h, time) else time(0, 0)), "tipo": "SALIDA", "origen": C.DEP_PROPIA,
                   "destino": r.get("entrega_destino"), "despacho": r.get("entrega_despacho") or None, "entregado_por": yo,
                   "recibido_por": recibe.strip().upper(), "fojas": K.num(r.get("fojas")) or None, "observaciones": obs.strip() or None}
            try:
                db.registrar_entrega(int(r["id"]), mov, "REMITIDO", yo)
            except Exception as e:
                st.error(f"No se pudo guardar: {e}")
                return
            st.session_state["com_ult"] = {"exp": dict(r), "mov": mov}
            st.session_state.pop("com_sel", None)
            st.rerun()
        return
    st.session_state.pop("com_sel", None)

    ult = st.session_state.get("com_ult")
    if ult:
        m = ult["mov"]
        st.success(f"✔ Entregado: {ult['exp']['identificador']} → {m['destino']} · recibió {m['recibido_por']}")
        st.link_button("📲 Avisar por WhatsApp", R.link_whatsapp(R.msg_movimiento(ult["exp"], m), K.tel_dep(m["destino"])), width="stretch")

    st.markdown(f"## 🚚 Para entregar: {len(pend)}")
    if pend.empty:
        st.info("No tiene expedientes para entregar. Cuando un oficial le encargue uno, aparecerá aquí.")
    for _, r in pend.iterrows():
        _tarjeta_simple(r)
        if st.button(f"Entregar {r['identificador']}", key=f"cs_ent_{r['id']}", type="primary", width="stretch"):
            st.session_state["com_sel"] = int(r["id"])
            st.session_state.pop("com_ult", None)
            st.rerun()

    movs = db.df_movimientos()
    if not movs.empty:
        hoy = movs[(movs["fecha_hora"].dt.normalize() == pd.Timestamp(db.hoy())) & (movs["registrado_por"].fillna("") == yo)
                   & movs["tipo"].isin(TIPOS_ENTREGA)]
        if not hoy.empty:
            st.markdown(f"#### ✅ Entregados hoy: {len(hoy)}")
            for _, m in hoy.iterrows():
                st.markdown(f'<div class="ok-ent"><b>{ui.esc(m["identificador"])}</b> → {ui.esc(m["destino"])} · '
                            f'recibió {ui.esc(m.get("recibido_por") or "—")} · {m["fecha_hora"]:%H:%M}</div>', unsafe_allow_html=True)
