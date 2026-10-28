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
            K._bot(r, "entrega", f"ENTREGADO → {destino}", f"Recibió: {mov['recibido_por']}", yo)
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
@media (max-width:640px){.cs-esp{height:58px}}
</style>"""


def _tarjeta_simple(r):
    ind = f'<div class="i">📝 {ui.esc(r["entrega_indicaciones"])}</div>' if r.get("entrega_indicaciones") else ""
    st.markdown(f'<div class="ent"><div class="l">N° DE EXPEDIENTE</div><div class="n">{ui.esc(r["identificador"])}</div>'
                f'<div class="l">LLEVAR A</div><div class="d">{ui.esc(r.get("entrega_destino") or "—")}</div>{ind}</div>',
                unsafe_allow_html=True)


def render_simple():
    st.markdown(CSS_SIMPLE, unsafe_allow_html=True)
    st.markdown("<div class='cs-esp'></div>", unsafe_allow_html=True)
    modo = st.segmented_control("¿Qué va a hacer?", ["🚚 Llevar", "📥 Traer a la Dirección", "📋 Mi historial"], default="🚚 Llevar",
                                key="cs_modo", label_visibility="collapsed")
    if modo == "📋 Mi historial":
        st.session_state.pop("com_sel", None)
        return _historial()
    if modo == "📥 Traer a la Dirección":
        st.session_state.pop("com_sel", None)
        return _traer()
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
            recibe = K.campo_persona(st, "¿Quién lo recibió?", f"cs_recibe_{r['id']}")
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
                K._bot(r, "entrega", f"ENTREGADO → {mov['destino']}", f"Recibió: {mov['recibido_por']}", yo)
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
        _avisar_grupo(_msg_comision("ENTREGADO", ult["exp"].get("identificador"), m["destino"], f"Recibió: {m['recibido_por']}",
                                    m["fecha_hora"], m.get("observaciones")), "ent")

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


def _traer():
    """El comisionista retiró expedientes de otra dependencia y los trae: si el sistema ya lo conoce, se registra el reingreso;
    si no, queda para que la mesa de entradas lo registre."""
    yo = K.usuario()
    ult = st.session_state.get("cs_traido")
    if ult:
        (st.success if ult[0] else st.info)(ult[1])
        if len(ult) > 2:
            _avisar_grupo(ult[2], "tra")
        if st.button("Listo", key="cs_traido_ok"):
            st.session_state.pop("cs_traido", None)
            st.rerun()
    st.markdown("## 📥 Traje expedientes a la Dirección")
    deps = [d for d in K.deps() if d != C.DEP_PROPIA]
    with st.form("cs_traer", clear_on_submit=True):
        origen = st.selectbox("¿De dónde lo retiró?", deps, index=None, placeholder="Elija la dependencia")
        numero = st.text_input("N° que figura en la carátula o en la nota", placeholder="Ej.: 584/56/6 · J-1234/26 · 9319/269/26D1",
                               help="Copie el número tal como está escrito, sea de la Dirección o de la dependencia que lo envía.")
        asunto = st.text_input("¿De qué se trata? (opcional)", placeholder="Ej.: pedido de curso de tiro, sumario de un cadete…")
        quien = K.campo_persona(st, "¿Quién se lo entregó allá? (opcional)", "cs_traer_quien")
        c1, c2 = st.columns(2)
        f = c1.date_input("Fecha", db.hoy(), format="DD/MM/YYYY")
        h = c2.time_input("Hora", db.ahora().time().replace(second=0), step=60)
        obs = st.text_input("Observaciones (opcional)")
        ok = st.form_submit_button("✅ TRAÍDO A LA DIRECCIÓN", type="primary", width="stretch")
    if ok:
        if not origen or not numero.strip():
            st.error("Indique de dónde lo retiró y el número.")
            return
        cuando = datetime.combine(f, h if isinstance(h, time) else time(0, 0))
        rec = {"fecha_hora": cuando, "origen": origen, "numero": " ".join(numero.split()).upper(), "asunto": asunto.strip().upper() or None,
               "entrego_en_origen": quien.strip().upper() or None, "traido_por": yo, "observaciones": obs.strip() or None}
        coinc = db.buscar_por_numero(rec["numero"])
        coinc = coinc[coinc["ubicacion_actual"].fillna(C.DEP_PROPIA) != C.DEP_PROPIA] if not coinc.empty else coinc
        try:
            rid = db.registrar_recepcion(rec, yo)
            if len(coinc) == 1:  # lo conocemos y estaba afuera: reingreso automático
                e = coinc.iloc[0]
                det = "Retirado por el comisionista" + (f"; lo entregó {rec['entrego_en_origen']}" if rec["entrego_en_origen"] else "")
                mov = {"fecha_hora": cuando, "tipo": "REINGRESO", "origen": origen, "destino": C.DEP_PROPIA, "entregado_por": yo,
                       "recibido_por": None, "fojas": None, "urgente": False,
                       "observaciones": "; ".join(x for x in [det, rec["observaciones"]] if x)}
                db.registrar_movimiento(int(e["id"]), mov, "EN TRÁMITE", yo)
                db.cerrar_recepcion(rid, int(e["id"]), yo)
                try:
                    import auth
                    import avisos

                    avisos.avisar_expediente(e.to_dict(), "reingreso", yo, auth.rol())
                except Exception:
                    pass
                st.session_state["cs_traido"] = (True, f"✔ {e['identificador']} registrado como REINGRESO desde {origen}. Ya lo ve el oficial.",
                                                 _msg_comision("TRAÍDO A LA DIRECCIÓN", e["identificador"], origen,
                                                               rec["entrego_en_origen"] and f"Lo entregó: {rec['entrego_en_origen']}",
                                                               cuando, rec["observaciones"], desde=True))
            else:
                K._bot({"identificador": rec["numero"], "tipo": "—", "asunto": "Para registrar en el libro (mesa de entradas)"},
                       "entrega", f"TRAÍDO A LA DIRECCIÓN desde {origen}", rec.get("entrego_en_origen") and f"Lo entregó: {rec['entrego_en_origen']}", yo)
                st.session_state["cs_traido"] = (False, f"✔ Anotado: {rec['numero']} desde {origen}. Es la primera vez que llega a la "
                                                        "Dirección: entréguelo en mesa de entradas, allí lo registran en el libro.",
                                                 _msg_comision("TRAÍDO A LA DIRECCIÓN (para registrar)", rec["numero"], origen,
                                                               rec["entrego_en_origen"] and f"Lo entregó: {rec['entrego_en_origen']}",
                                                               cuando, rec["observaciones"], desde=True))
        except Exception as ex:
            st.error(f"No se pudo guardar: {ex}")
            return
        st.rerun()
    rec = db.df_recepciones(False)
    hoy = rec[(rec["fecha_hora"].dt.normalize() == pd.Timestamp(db.hoy())) & (rec["traido_por"].fillna("") == yo)] if not rec.empty else rec
    if not hoy.empty:
        st.markdown(f"#### 📥 Traídos hoy: {len(hoy)}")
        for _, r in hoy.iterrows():
            est = "✅ registrado" if r["estado"] == "REGISTRADO" else "⏳ en mesa de entradas"
            st.markdown(f'<div class="ok-ent"><b>{ui.esc(r["numero"])}</b> ← {ui.esc(r["origen"])} · {r["fecha_hora"]:%H:%M} · {est}</div>',
                        unsafe_allow_html=True)


# ───────────────────────── Aviso al grupo y mi historial ─────────────────────────
def _msg_comision(accion, numero, lugar, quien, cuando, obs=None, desde=False):
    lin = [f"🚚 *Comisión – {accion}*", f"*Exp. N° {numero}*", f"{'Desde' if desde else 'Destino'}: {lugar}"]
    if quien:
        lin.append(quien)
    lin.append(f"Fecha: {pd.Timestamp(cuando):%d/%m/%Y %H:%M}")
    if obs:
        lin.append(f"Obs.: {obs}")
    lin.append(f"Comisionista: {K.usuario()}")
    return "\n".join(lin)


def _avisar_grupo(msg, key):
    """Botón grande: abre SU WhatsApp con el mensaje armado para enviarlo al grupo de trabajo."""
    st.link_button("👥 Enviar al grupo de trabajo (WhatsApp)", R.link_whatsapp(msg), type="primary", width="stretch")
    st.caption("Se abre su WhatsApp: elija el grupo de trabajo y toque Enviar.")
    st.link_button("✈️ Enviar por Telegram", R.link_telegram(msg), width="stretch")


def _historial():
    """Solo lo que hizo el usuario conectado: entregas y retiros, con búsqueda por N°, dependencia o persona."""
    yo = K.usuario()
    st.markdown("## 📋 Mi historial")
    c1, c2 = st.columns(2)
    desde = c1.date_input("Desde", db.hoy() - pd.Timedelta(days=30), format="DD/MM/YYYY", key="hs_desde")
    hasta = c2.date_input("Hasta", db.hoy(), format="DD/MM/YYYY", key="hs_hasta")
    q = st.text_input("Buscar", key="hs_q", placeholder="N° de expediente, dependencia o persona").strip().lower()
    filas = []
    movs = db.df_movimientos()
    if not movs.empty:
        m = movs[(movs["registrado_por"].fillna("") == yo) & movs["tipo"].isin(TIPOS_ENTREGA + ["REINGRESO"])]
        for _, x in m.iterrows():
            entrega = x["tipo"] != "REINGRESO"
            filas.append({"Fecha": x["fecha_hora"], "Qué": "🚚 Entregado" if entrega else "📥 Traído",
                          "Expediente": x["identificador"], "Dependencia": x["destino"] if entrega else x["origen"],
                          "Persona": x.get("recibido_por") if entrega else (x.get("observaciones") or ""),
                          "Obs.": x.get("observaciones") if entrega else ""})
    rec = db.df_recepciones(False)
    if not rec.empty:
        rec = rec[(rec["traido_por"].fillna("") == yo) & (rec["estado"] == "PENDIENTE")]
        for _, x in rec.iterrows():
            filas.append({"Fecha": x["fecha_hora"], "Qué": "📥 Traído (para registrar)", "Expediente": x["numero"],
                          "Dependencia": x["origen"], "Persona": x.get("entrego_en_origen") or "", "Obs.": x.get("observaciones") or ""})
    df = pd.DataFrame(filas, columns=["Fecha", "Qué", "Expediente", "Dependencia", "Persona", "Obs."])
    if not df.empty:
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
        df = df[(df["Fecha"].dt.date >= desde) & (df["Fecha"].dt.date <= hasta)]
        if q:
            df = df[df.astype(str).apply(lambda col: col.str.lower().str.contains(q, regex=False)).any(axis=1)]
        df = df.sort_values("Fecha", ascending=False)
    ent = int(df["Qué"].str.startswith("🚚").sum()) if not df.empty else 0
    st.markdown(f"**{len(df)}** registros · 🚚 {ent} entregados · 📥 {len(df) - ent} traídos")
    if df.empty:
        st.info("No hay actividad suya en ese período.")
        return
    for _, x in df.head(200).iterrows():
        st.markdown(f'<div class="ok-ent">{x["Fecha"]:%d/%m %H:%M} · {x["Qué"]} · <b>{ui.esc(x["Expediente"])}</b> '
                    f'{"→" if x["Qué"].startswith("🚚") else "←"} {ui.esc(x["Dependencia"] or "—")}'
                    f'{" · " + ui.esc(x["Persona"]) if x["Persona"] else ""}</div>', unsafe_allow_html=True)
    st.download_button("📥 Descargar mi historial (Excel)", R.excel({"Mi historial": df.assign(Fecha=df["Fecha"].dt.strftime("%d/%m/%Y %H:%M"))}),
                       file_name=f"historial_comision_{db.hoy():%Y%m%d}.xlsx", width="stretch")
