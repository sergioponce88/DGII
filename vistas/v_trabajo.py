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
def _prellenar_nuevo():
    """Si viene de algo que trajo el comisionista: el alta abre con origen, N° de origen, asunto y quién lo trajo ya cargados."""
    rid = st.session_state.get("tb_rec")
    if not rid:
        return
    rec = db.df_recepciones(False)
    rec = rec[rec["id"] == rid]
    if rec.empty:
        return
    r = rec.iloc[0]
    st.session_state["n_origen"] = C.ORIGENES[1]
    if r.get("origen"):
        st.session_state["_sel_n_dep_org"] = r["origen"]
    st.session_state["n_nro_org"] = r.get("numero") or ""
    if r.get("asunto"):
        st.session_state["n_asunto"] = r["asunto"]
    st.session_state["_pref_entrega"] = r.get("traido_por") or ""
    st.session_state["n_rec"] = int(rid)


def traidos_comision():
    """Lo que trajo el comisionista y el sistema no pudo asociar: la mesa de entradas lo registra."""
    rid, ult = st.session_state.get("tb_rec"), st.session_state.get("ultimo_mov_tb")
    if rid and ult and ult["mov"].get("tipo") == "REINGRESO":  # se registró el reingreso de lo que trajo el comisionista
        db.cerrar_recepcion(rid, int(ult["exp"]["id"]), K.usuario())
        st.session_state.pop("tb_rec", None)
    try:
        rec = db.df_recepciones()
    except Exception:
        return
    if rec.empty:
        return
    ui.seccion(f"📦 Traídos por el comisionista para registrar ({len(rec)})")
    for _, r in rec.iterrows():
        st.markdown(f"<div class='card acc' style='--c:#F59E0B;padding:10px 14px'><b>{ui.esc(r['numero'])}</b> ← {ui.esc(r['origen'] or '—')}"
                    f"{('<br>' + ui.esc(r['asunto'])) if r.get('asunto') else ''}"
                    f"<div class='meta'>Trajo {ui.esc(r['traido_por'] or '—')} · {ui.fmt_fecha(r['fecha_hora'], True)}"
                    f"{' · lo entregó ' + ui.esc(r['entrego_en_origen']) if r.get('entrego_en_origen') else ''}"
                    f"{' · ' + ui.esc(r['observaciones']) if r.get('observaciones') else ''}</div></div>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        if b1.button("🔎 Buscarlo y registrarlo", key=f"rc_b_{r['id']}", width="stretch"):
            st.session_state["tb_q"] = r["numero"]
            st.session_state["tb_rec"] = int(r["id"])
            st.rerun()
        if b2.button("✔ Ya está registrado", key=f"rc_ok_{r['id']}", width="stretch"):
            db.cerrar_recepcion(int(r["id"]), None, K.usuario())
            st.rerun()


def mesa_entradas(exp):
    msg = st.session_state.get("ult_registro")
    if msg:
        st.success("✔ Registrado. Avise a los oficiales:")
        K.avisar_oficiales_wp(msg, "ult_reg")
        if st.button("Listo", key="ult_reg_ok"):
            st.session_state.pop("ult_registro", None)
            st.rerun()
    traidos_comision()
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
        b1, b2 = st.columns(2)
        if b1.button("➕ Es nuevo: registrarlo", key="tb_nuevo", type="primary", width="stretch"):
            _prellenar_nuevo()
            K.ir_a(K.PAG_NUEVO)
        if b2.button("📜 Es viejo: ya figura en el libro físico", key="tb_viejo", width="stretch"):
            st.session_state["tb_viejo_on"] = True
        if st.session_state.get("tb_viejo_on"):
            form_anterior(q)
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
    c1, c2 = st.columns(2)
    if c1.button("➕ No es ninguno: cargar como nuevo", key="tb_nuevo2", width="stretch"):
        _prellenar_nuevo()
        K.ir_a(K.PAG_NUEVO)
    if c2.button("📜 No es ninguno: es viejo (libro físico)", key="tb_viejo2", width="stretch"):
        st.session_state["tb_viejo_on"] = True
    if st.session_state.get("tb_viejo_on"):
        form_anterior(q)


def form_anterior(q=""):
    """Expediente viejo, asentado en el libro físico antes del sistema, que vuelve: se carga con su N°/folio/orden ORIGINAL
    y en el mismo paso se registra el reingreso de hoy."""
    from datetime import datetime, time

    with st.container(border=True):
        st.markdown("**📜 Expediente anterior al sistema que vuelve**")
        st.caption("Copie los datos tal como figuran en el libro físico. Se respeta su numeración original y queda registrado el reingreso de hoy.")
        sec = K.elegir_secretaria("tv_sec", "¿En qué libro está asentado?")
        if not sec:
            return
        n = "".join(ch for ch in q if ch.isdigit())
        lista_dep, lista_tipos = K.deps(), K.tipos()
        with st.form("tv_form"):
            st.markdown("**Asiento original (del libro físico)**")
            a1, a2, a3, a4, a5 = st.columns(5)
            nro = a1.number_input("N° exp.", min_value=1, value=int(n) if n and len(n) <= 6 else 1, step=1)
            folio = a2.number_input("Folio", min_value=1, value=1, step=1)
            orden = a3.number_input("Orden", min_value=1, value=1, step=1)
            libro = a4.number_input("Libro", min_value=1, value=1, step=1)
            f_ing = a5.date_input("Fecha de ingreso original", None, format="DD/MM/YYYY")
            b1, b2 = st.columns(2)
            tipo = b1.selectbox("Tipo de expediente", lista_tipos, index=None, placeholder="Elija…")
            dep_org = b2.selectbox("Dependencia de origen", lista_dep, index=None, placeholder="De dónde vino la primera vez")
            asunto = st.text_input("Asunto / carátula")
            c1, c2 = st.columns(2)
            nro_org = c1.text_input("N° de origen (opcional)")
            iniciador = c2.text_input("Iniciador / causante (opcional)")
            st.markdown("**Reingreso de hoy**")
            d1, d2 = st.columns(2)
            desde = d1.selectbox("Vuelve desde", lista_dep, index=None, placeholder="¿De dónde vuelve?")
            despacho = K.campo_despacho(d2, "Vuelve con (despacho / resolución)", "tv_desp")
            e1, e2, e3 = st.columns([2, 2, 1])
            trae = K.campo_persona(e1, "Quién lo trae", "tv_trae")
            recibe = K.campo_persona(e2, "Quién lo recibe", "tv_recibe", defecto=K.usuario())
            fojas = e3.number_input("Fojas", min_value=0, value=0, step=1)
            motivo = st.text_input("Motivo / qué se solicita ahora", placeholder="Ej.: vuelve con informe para nueva providencia")
            ok = st.form_submit_button("📥 Cargar del libro y registrar el reingreso", type="primary", width="stretch")
        if not ok:
            return
        faltan = [x for x, v in [("fecha de ingreso original", f_ing), ("tipo", tipo), ("de dónde vuelve", desde)] if not v]
        if faltan:
            st.error("Falta: " + ", ".join(faltan) + ".")
            return
        choque = db.conflicto_numeracion(int(nro), int(folio), int(orden), int(libro), f_ing.year, sec=sec)
        if choque:
            st.error(f"Ese N° / folio / orden ya está registrado ({choque}). Búsquelo y registre el reingreso sobre ese expediente.")
            return
        exp = dict(secretaria=sec, nro_exp=int(nro), folio=int(folio), orden=int(orden), libro=int(libro), anio=f_ing.year,
                   fecha_ingreso=f_ing, origen=(C.ORIGENES[2] if dep_org == K.dep_iesp() else C.ORIGENES[1] if dep_org and dep_org != C.DEP_PROPIA else C.ORIGENES[0]),
                   dependencia_origen=dep_org, nro_exp_origen=nro_org.strip() or None, tipo=tipo, asunto=asunto.strip().upper() or None,
                   iniciador=iniciador.strip().upper() or None, prioridad=C.PRIORIDADES[0], estado="EN TRÁMITE", ubicacion_actual=desde,
                   fojas=int(fojas) or None, observaciones="Asiento anterior al sistema, cargado desde el libro físico")
        mov0 = dict(fecha_hora=datetime.combine(f_ing, time(8, 0)), tipo="INGRESO", origen=dep_org, destino=C.DEP_PROPIA,
                    observaciones="Asiento original del libro físico (anterior al sistema)")
        try:
            exp_id, ident = db.crear_expediente(exp, mov0, usuario=K.usuario())
            mov = {"fecha_hora": db.ahora(), "tipo": "REINGRESO", "origen": desde, "destino": C.DEP_PROPIA, "despacho": despacho or None,
                   "entregado_por": trae or None, "recibido_por": recibe or None, "fojas": int(fojas) or None, "urgente": False,
                   "observaciones": motivo.strip() or None}
            db.registrar_movimiento(exp_id, mov, "EN TRÁMITE", K.usuario())
        except Exception as e:
            st.error(f"No se pudo cargar: {e}")
            return
        import auth
        import avisos

        avisos.avisar_expediente({**exp, "identificador": ident}, "reingreso", K.usuario(), auth.rol())
        if st.session_state.get("tb_rec"):
            db.cerrar_recepcion(st.session_state.pop("tb_rec"), exp_id, K.usuario())
        st.session_state["ult_registro"] = K.msg_registro({**exp, "identificador": ident}, "Reingreso (expediente del libro físico)", mov)
        for k in ("tb_viejo_on", "tv_sec", "tb_q"):
            st.session_state.pop(k, None)
        st.toast(f"Exp. {ident} cargado del libro y reingresado: queda PARA TRAMITAR", icon="📥")
        st.rerun()


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
        try:
            n_rec = len(db.df_recepciones())
        except Exception:
            n_rec = 0
        titulo = "📥 Llegó un expediente (buscar · reingreso · nuevo)" + (f" · 📦 {n_rec} traído(s) por el comisionista" if n_rec else "")
        with st.expander(titulo, expanded=bool(st.session_state.get("tb_q")) or bool(n_rec)):
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
