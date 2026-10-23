"""📝 Tramitar: el oficial elige el modelo, completa el formulario, revisa la redacción,
descarga el Word para imprimir y deja el expediente asentado como TRAMITADO."""
import json
from datetime import date, datetime, time

import pandas as pd
import streamlit as st

import catalogos as C
import comun as K
import db
import modelos as M
import redaccion as RD
import ui

OTRA = "_OTRA"
ORIGENES_ACT = ["INICIADA EN LA DIRECCIÓN", "RECIBIDA DE OTRA DEPENDENCIA"]


# ───────────────────────── Contexto ─────────────────────────
def _ctx(r):
    aut = db.df_autoridades()
    cfg = dict(db.get_config())
    cfg["dep_propia"] = C.DEP_PROPIA
    exp = {k: (None if (not isinstance(v, (list, dict)) and pd.isna(v)) else v) for k, v in dict(r).items()}
    return {"exp": exp, "act": db.get_actuacion(int(r["id"])), "cfg": cfg, "hoy": db.hoy(),
            "aut": {a["clave"]: a for a in aut.to_dict("records")}}


def _p(m, exp_id):
    return f"tr_{exp_id}_{m.id}_"


# ───────────────────────── Vista ─────────────────────────
def render():
    ui.header("Tramitar", "Modelos de notas, pases, notificaciones y actuaciones · Word listo para imprimir")
    import auth

    if not auth.puede("tramitar"):
        auth.aviso_sin_permiso("la tramitación")
        return
    exp = db.df_expedientes()
    if exp.empty:
        st.info("No hay expedientes registrados.")
        return
    r = K.selector_expediente("tram_sel", exp)
    if r is None:
        st.caption("Elija el expediente a tramitar. También puede llegar desde la ficha → pestaña Trámite.")
        return
    ui.tarjeta_expediente(r, detalle=False)
    ctx = _ctx(r)
    exp_id = int(r["id"])
    docs = db.df_documentos(exp_id)
    hechos = set(docs["modelo"]) if not docs.empty else set()

    if M.es_actuacion(r["tipo"]):
        pasos = _actuacion(r, ctx, hechos)
        if not ctx["act"]:
            return
        otros = [k for k, m in M.MODELOS.items() if m.grupo == "Actuaciones / Sumario" and k not in pasos] + ["notificacion"]
        sugeridos = pasos
    else:
        sugeridos = M.sugeridos(r["tipo"])
        otros = [k for k in M.MODELOS if k not in sugeridos and M.MODELOS[k].grupo != "Actuaciones / Sumario"]

    ui.seccion("① ¿Qué va a hacer?")
    fmt = lambda k: f"{'✓ ' if k in hechos else ''}{M.MODELOS[k].icono} {M.MODELOS[k].nombre}"
    sel = st.pills("Sugeridos para este expediente", sugeridos, format_func=fmt, key=f"tr_mod_{exp_id}")
    with st.expander("Más modelos"):
        sel2 = st.pills("Otros", otros, format_func=fmt, key=f"tr_mod2_{exp_id}", label_visibility="collapsed")
    sel = sel or sel2
    if not sel:
        _historial(docs)
        return
    m = M.MODELOS[sel]
    st.caption(m.descripcion)
    _formulario(m, r, ctx)
    _historial(docs)


# ───────────────────────── Actuaciones / sumario ─────────────────────────
def _actuacion(r, ctx, hechos):
    a = ctx["act"]
    exp_id = int(r["id"])
    with st.expander("📋 Datos de la actuación" + ("" if a else " · complételos primero"), expanded=not a):
        with st.form(f"act_{exp_id}"):
            c1, c2 = st.columns(2)
            clases = M.CLASES
            tipo = (r["tipo"] or "").upper()
            def_clase = a.get("clase") or next((c for c in clases if c in tipo), clases[0])
            clase = c1.selectbox("Clase", clases, index=clases.index(def_clase) if def_clase in clases else 0)
            origen = c2.radio("Origen", ORIGENES_ACT, horizontal=True,
                              index=ORIGENES_ACT.index(a["origen"]) if a.get("origen") in ORIGENES_ACT else (0 if r.get("origen") != C.ORIGENES[1] else 1))
            c3, c4 = st.columns(2)
            numero = c3.text_input("N° de actuación", a.get("numero") or r["identificador"])
            ocurrido = c4.text_input("Ocurrido (fecha y hora)", a.get("ocurrido") or "")
            causa = st.text_input("Causa", a.get("causa") or (r.get("asunto") or ""))
            c5, c6 = st.columns([3, 1])
            causante = c5.text_input("Causante (grado / cadete de … año, APELLIDO Nombre)", a.get("causante") or "")
            lp = c6.text_input("L.P. causante", a.get("causante_lp") or "")
            c7, c8 = st.columns(2)
            victima = c7.text_input("Víctima (si hay)", a.get("victima") or "")
            interviene = c8.text_input("Interviene", a.get("interviene") or "")
            hecho = st.text_area("Hecho (resumen: «el día … a horas …»)", a.get("hecho") or "", height=90)
            st.markdown("**Instrucción**")
            d1, d2, d3 = st.columns([3, 1, 2])
            instr = d1.text_input("Instructor (grado y nombre)", a.get("instructor") or "")
            instr_lp = d2.text_input("L.P. instructor", a.get("instructor_lp") or "")
            instr_f = d3.text_input("Función", a.get("instructor_funcion") or "Vicerrector")
            e1, e2 = st.columns([3, 1])
            secr = e1.text_input("Secretario de actuaciones (grado y nombre)", a.get("secretario") or "")
            secr_lp = e2.text_input("L.P. secretario", a.get("secretario_lp") or "")
            if st.form_submit_button("💾 Guardar datos de la actuación", type="primary"):
                db.guardar_actuacion(exp_id, dict(clase=clase, numero=numero, origen=origen, causa=causa, causante=causante, causante_lp=lp,
                                                  victima=victima, ocurrido=ocurrido, interviene=interviene, hecho=hecho, instructor=instr,
                                                  instructor_lp=instr_lp, instructor_funcion=instr_f, secretario=secr, secretario_lp=secr_lp), K.usuario())
                st.toast("Datos guardados: se usan en todos los documentos", icon="✅")
                st.rerun()
    if not a:
        st.info("Cargue una sola vez los datos de la actuación: carátula, actas, cédulas y conclusiones se completan solos.")
        return []
    if "SUMARIO" in (a.get("clase") or "") or "SUMARIA" in (a.get("clase") or ""):
        pasos = M.PASOS_SUMARIO if a.get("origen") == ORIGENES_ACT[1] else M.PASOS_INTERNA
    else:
        pasos = M.PASOS_INTERNA if a.get("origen") != ORIGENES_ACT[1] else M.PASOS_EXTERNA
    hechos_n = sum(1 for p in pasos if p in hechos)
    st.progress(hechos_n / len(pasos), text=f"Pasos realizados: {hechos_n} de {len(pasos)} · {a.get('origen', '').lower()}")
    return pasos


# ───────────────────────── Formulario genérico ─────────────────────────
def _init(m, ctx, p):
    if st.session_state.get(p + "_init"):
        return
    for k, v in M.valores_por_defecto(m, ctx).items():
        if k == "destino" and v is None:
            v = OTRA
        if isinstance(v, datetime):
            v = v.date()
        st.session_state[p + k] = v
    st.session_state[p + "_init"] = True


def _widget(c, p, ctx, cont):
    k = p + c.key
    if c.tipo == "area":
        cont.text_area(c.label + (" *" if c.requerido else ""), key=k, height=140 if c.ia else 90, help=c.ayuda or None)
    elif c.tipo == "int":
        cont.number_input(c.label, key=k, min_value=0, step=1, help=c.ayuda or None)
    elif c.tipo == "date":
        cont.date_input(c.label, key=k, format="DD/MM/YYYY")
    elif c.tipo == "time":
        cont.time_input(c.label, key=k, step=300)
    elif c.tipo == "select":
        cont.selectbox(c.label, c.opciones, key=k, help=c.ayuda or None)
    elif c.tipo == "check":
        cont.checkbox(c.label, key=k)
    elif c.tipo == "autoridad":
        claves = list(ctx["aut"]) + [OTRA]
        if st.session_state.get(k) not in claves:
            st.session_state[k] = claves[0]

        def _f(x):
            if x == OTRA:
                return "✏️ Otra dependencia (escribir)"
            a = ctx["aut"][x]
            return a["cargo"] + (f" — {a['titular']}" if a.get("titular") else "")

        cont.selectbox(c.label, claves, key=k, format_func=_f)
    else:
        cont.text_input(c.label + (" *" if c.requerido else ""), key=k, help=c.ayuda or None)


def _valores(m, p):
    return {c.key: st.session_state.get(p + c.key) for c in m.campos}


def _formulario(m, r, ctx):
    exp_id = int(r["id"])
    p = _p(m, exp_id)
    # correcciones aceptadas en el paso anterior (antes de dibujar los widgets)
    for k, v in st.session_state.pop(p + "_aplicar", {}).items():
        st.session_state[p + k] = v
    _init(m, ctx, p)

    ui.seccion(f"② {m.icono} {m.nombre}")
    if not m.campos:
        st.caption("Este documento se arma completo con los datos de la actuación.")
    cortos = []

    def _vaciar():
        if cortos:
            cols = st.columns(2)
            for i, c in enumerate(cortos):
                _widget(c, p, ctx, cols[i % 2])
            cortos.clear()

    for c in m.campos:
        if c.tipo in ("area", "check", "autoridad"):
            _vaciar()
            _widget(c, p, ctx, st)
            if c.tipo == "autoridad" and st.session_state.get(p + c.key) == OTRA:
                o1, o2, o3 = st.columns([1, 2, 2])
                o1.selectbox("Tratamiento", ["Señor", "Señora", "Al Señor", "A la Señora"], key=p + "o_trat")
                o2.text_input("Cargo / dependencia", key=p + "o_cargo")
                o3.text_input("Grado y nombre", key=p + "o_tit")
        else:
            cortos.append(c)
    _vaciar()

    v = _valores(m, p)
    if v.get("destino") == OTRA:
        ctx["aut"][OTRA] = {"clave": OTRA, "tratamiento": st.session_state.get(p + "o_trat") or "Señor",
                            "cargo": st.session_state.get(p + "o_cargo") or "", "titular": st.session_state.get(p + "o_tit") or "",
                            "saludo": "Oficina", "relacion": "PAR"}

    ia = [c for c in m.campos if c.ia and (st.session_state.get(p + c.key) or "").strip()]
    ui.seccion("③ Revisar y generar")
    b1, b2 = st.columns(2)
    if b1.button("✨ Revisar redacción", key=p + "rev_b", width="stretch", disabled=not ia,
                 help="Diccionario propio + LanguageTool (gratis)" + ("" if m.sensible else " · Gemini opcional")):
        _revisar(m, p, ia)
    generar = b2.button("📄 Generar Word", key=p + "gen_b", type="primary", width="stretch")
    _panel_revision(m, p)

    if generar:
        faltan = [c.label for c in m.campos if c.requerido and not str(v.get(c.key) or "").strip()]
        if v.get("destino") == OTRA and not ctx["aut"][OTRA]["cargo"].strip():
            faltan.append("Cargo / dependencia del destinatario")
        if faltan:
            st.error("Complete: " + ", ".join(faltan))
        else:
            try:
                datos = m.render(v, ctx).bytes()
            except Exception as e:
                st.error(f"No se pudo armar el documento: {e}")
                return
            dest = ctx["aut"].get(v.get("destino") or "", {}) if v.get("destino") else {}
            nombre = f"{m.id}_{str(r['identificador']).replace('/', '-')}_{db.hoy():%Y%m%d}.docx"
            db.registrar_documento(exp_id, m.id, m.nombre, dest.get("cargo"), json.dumps(v, default=str, ensure_ascii=False), K.usuario())
            st.session_state[p + "_doc"] = {"bytes": datos, "nombre": nombre, "destino": dest.get("cargo"), "v": v}
    _resultado(m, r, p, ctx)


def _revisar(m, p, campos):
    rev = {}
    for c in campos:
        txt = st.session_state.get(p + c.key) or ""
        local, cambios = RD.revisar_local(txt)
        try:
            lt, err = RD.languagetool(txt), None
        except Exception as e:
            lt, err = [], f"LanguageTool no disponible ahora: {e}"
        rev[c.key] = {"label": c.label, "orig": txt, "local": cambios, "lt": lt, "err": err}
    st.session_state[p + "_rev"] = rev


def _panel_revision(m, p):
    rev = st.session_state.get(p + "_rev")
    if not rev:
        return
    with st.container(border=True):
        st.markdown("**✨ Sugerencias de redacción**")
        aplicar = {}
        for k, d in rev.items():
            n = len(d["local"]) + len(d["lt"])
            st.markdown(f"**{d['label']}** · {n or 'sin'} sugerencia{'s' if n != 1 else ''}")
            for a, b in d["local"]:
                st.markdown(f"<small>📘 <s>{ui.esc(a)}</s> → <b>{ui.esc(b)}</b> · diccionario D.G.I.I.</small>", unsafe_allow_html=True)
            elegidas = []
            for i, s in enumerate(d["lt"]):
                ok = st.checkbox(f"«{s['original']}» → «{s['sugerencia']}» · {s['mensaje'][:90]}", value=s["tipo"] == "Ortografía",
                                 key=f"{p}lt_{k}_{i}")
                if ok:
                    elegidas.append(s)
            if d["err"]:
                st.caption(d["err"])
            aplicar[k] = RD.revisar_local(RD.aplicar(d["orig"], elegidas))[0]
            if not m.sensible and RD.gemini_disponible():
                if st.button("🤖 Mejorar con Gemini", key=f"{p}gem_{k}"):
                    try:
                        with st.spinner("Gemini está revisando…"):
                            st.session_state[f"{p}gemtxt_{k}"] = RD.gemini_mejorar(aplicar[k], m.sensible)
                    except Exception as e:
                        st.error(str(e))
                g = st.session_state.get(f"{p}gemtxt_{k}")
                if g:
                    st.text_area("Propuesta de Gemini (puede editarla)", key=f"{p}gemtxt_{k}", height=140)
                    aplicar[k] = st.session_state.get(f"{p}gemtxt_{k}") or aplicar[k]
            elif m.sensible:
                st.caption("🔒 Documento con datos personales: no se envía a IA externa.")
        c1, c2 = st.columns(2)
        if c1.button("✔️ Aplicar correcciones", key=p + "apl", type="primary", width="stretch"):
            st.session_state[p + "_aplicar"] = aplicar
            for k in rev:
                st.session_state.pop(f"{p}gemtxt_{k}", None)
            st.session_state.pop(p + "_rev", None)
            st.rerun()
        if c2.button("Descartar", key=p + "desc", width="stretch"):
            st.session_state.pop(p + "_rev", None)
            st.rerun()


# ───────────────────────── Resultado y registro del trámite ─────────────────────────
def _resultado(m, r, p, ctx):
    doc = st.session_state.get(p + "_doc")
    if not doc:
        return
    ui.seccion("④ Imprimir y asentar")
    st.download_button("⬇️ Descargar Word", doc["bytes"], file_name=doc["nombre"], type="primary", width="stretch",
                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=p + "dl")
    st.caption(f"Hoja {'media oficio' if m.hoja == 'media' else 'oficio'} · revise el documento antes de imprimir. Quedó registrado en el historial del expediente.")
    if bool(r.get("tramitado")):
        ui.alerta("✅", "El expediente ya figura como TRAMITADO", "Puede seguir generando documentos.", C.STATUS["ok"])
        return
    with st.container(border=True):
        st.markdown("**Asentar el trámite**")
        c1, c2 = st.columns(2)
        acc = c1.selectbox("¿Qué se hizo?", C.ACCIONES_TRAMITE, index=C.ACCIONES_TRAMITE.index(m.accion) if m.accion in C.ACCIONES_TRAMITE else 0, key=p + "acc")
        det = c2.text_input("Detalle", f"{m.nombre}" + (f" → {doc['destino']}" if doc.get("destino") else ""), key=p + "det")
        salida = bool(m.destino and doc.get("destino"))
        reg_sal = st.checkbox(f"Registrar también la SALIDA hacia {doc.get('destino')}", value=salida, disabled=not salida, key=p + "sal")
        if st.button("✅ Marcar como TRAMITADO", key=p + "ok", type="primary", width="stretch"):
            ahora = db.ahora()
            u = K.usuario()
            db.marcar_tramitado([int(r["id"])], acc, det, ahora, u, u)
            if reg_sal:
                desp = m.despacho(doc["v"]) if m.despacho else None
                db.registrar_movimiento(int(r["id"]), {"fecha_hora": ahora, "tipo": "SALIDA", "origen": C.DEP_PROPIA, "destino": doc["destino"],
                                                       "despacho": desp, "entregado_por": u, "observaciones": det}, "REMITIDO", u)
            st.session_state.pop(p + "_doc", None)
            st.toast(f"Expediente {r['identificador']} TRAMITADO", icon="✅")
            st.rerun()


def _historial(docs):
    if docs.empty:
        return
    with st.expander(f"🗂️ Documentos generados ({len(docs)})"):
        for _, d in docs.head(20).iterrows():
            st.markdown(f"<small>{ui.fmt_fecha(d['generado_en'], True)} · <b>{ui.esc(d['titulo'])}</b>"
                        f"{' → ' + ui.esc(d['destino']) if d['destino'] else ''} · {ui.esc(d['generado_por'] or '')}</small>",
                        unsafe_allow_html=True)
