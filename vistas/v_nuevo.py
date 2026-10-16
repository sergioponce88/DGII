from datetime import datetime

import streamlit as st

import catalogos as C
import comun as K
import db
import reportes as R
import ui


def _resultado():
    r = st.session_state.get("ultimo_alta")
    if not r:
        return
    ui.alerta("✅", f"Expediente registrado: N° {r['identificador']} (Año {r['anio']})",
              f"{r['tipo']} · Asiento en libro {r['libro']}, folio {r['folio']}, orden {r['orden']}", C.STATUS["ok"])
    c1, c2, c3 = st.columns(3)
    c1.link_button("📲 Avisar por WhatsApp", R.link_whatsapp(R.msg_alta(r), K.tel_dep(r.get("ubicacion_actual"))))
    if c2.button("🔎 Abrir ficha", key="alta_ficha"):
        st.session_state.pop("ultimo_alta", None)
        K.ir_a(K.PAG_FICHA, r["id"])
    if c3.button("➕ Cargar otro", key="alta_otro"):
        st.session_state.pop("ultimo_alta", None)
        st.rerun()


def render():
    ui.header("Nuevo Expediente", "Registro en el libro · N° EXP / FOLIO / ORDEN")
    _resultado()
    if st.session_state.get("ultimo_alta"):
        return

    lista_dep = K.deps()
    lista_tipos = K.tipos()

    # ── Paso 1 (reactivo): origen, tipo y numeración ──
    c1, c2 = st.columns(2)
    origen = c1.radio("Origen del expediente", C.ORIGENES, horizontal=True, key="n_origen")
    tipo = c2.selectbox("Tipo de expediente", lista_tipos, index=None, placeholder="Seleccione el tipo…", key="n_tipo")

    d1, d1b, d2, d2b = st.columns([5, 1, 5, 1], vertical_alignment="bottom")
    if origen == C.ORIGENES[1]:
        K.preselect("n_dep_org")
        dep_org = d1.selectbox("🏢 Dependencia de origen (de dónde viene)", lista_dep, index=None,
                               placeholder="¿De dónde llega?", key="n_dep_org")
        with d1b:
            K.boton_nueva_dependencia("org", "n_dep_org")
    else:
        dep_org = C.DEP_PROPIA
        d1.text_input("🏢 Dependencia de origen", C.DEP_PROPIA, disabled=True)
    K.preselect("n_destino")
    destino = d2.selectbox("🎯 Instancia a la que va", lista_dep, index=None,
                           placeholder="¿A qué instancia se eleva o remite?", key="n_destino")
    with d2b:
        K.boton_nueva_dependencia("dest", "n_destino")

    sug = db.sugerir_numeracion()
    with st.container(border=True):
        st.markdown("**📖 Asiento en el libro**")
        n1, n2, n3, n4, n5 = st.columns(5)
        nro = n1.number_input("N° Expediente", min_value=1, value=sug["nro_exp"], step=1, key="n_nro")
        nuevo_folio = n5.checkbox("Iniciar nuevo folio", key="n_nf", help=f"Pasa al folio {sug['folio'] + sug['paso'] if sug['orden'] > 1 else sug['folio']} con orden 1")
        f_def, o_def = (sug["folio"] + sug["paso"], 1) if nuevo_folio and sug["orden"] > 1 else (sug["folio"], sug["orden"])
        folio = n2.number_input("Folio (foja izq.)", min_value=1, value=f_def, step=1, key=f"n_fol_{f_def}")
        orden = n3.number_input("N° Orden", min_value=1, value=o_def, step=1, key=f"n_ord_{f_def}_{o_def}")
        libro = n4.number_input("Libro", min_value=1, value=sug["libro"], step=1, key="n_lib")
        conflicto = db.conflicto_numeracion(nro, folio, orden, libro, db.hoy().year)
        ident = f"{nro}/{folio}/{orden}"
        if conflicto:
            st.error(f"⚠️ La numeración choca con el expediente ya registrado **{conflicto}**. Corrija N°, folio u orden.")
        else:
            st.markdown(f"<div class='ident'>{ui.esc(ident)}<small>IDENTIFICACIÓN · {sug['cap']} renglones por folio</small></div>", unsafe_allow_html=True)

    es_curso = bool(tipo) and K.tipo_es_curso(tipo)

    # ── Paso 2: datos ──
    with st.form("form_nuevo", clear_on_submit=False):
        ui.seccion("📝 Datos del expediente")
        a1, a2, a3 = st.columns(3)
        f_ing = a1.date_input("Fecha de ingreso / inicio", db.hoy(), format="DD/MM/YYYY")
        h_ing = a2.time_input("Hora", db.ahora().time().replace(second=0), step=300)
        despacho = a3.selectbox("Sale con", C.DESPACHOS, format_func=lambda d: d or "— A definir —")
        b1, b2 = st.columns(2)
        nro_org = b1.text_input("N° de expediente / nota de origen", placeholder="Ej: J-1234/26")
        iniciador = b2.text_input("Iniciador / causante", placeholder="Jerarquía, apellido y nombre o dependencia")
        asunto = st.text_area("Asunto / carátula", height=80)
        d1, d2, d3, d4 = st.columns(4)
        prioridad = d1.radio("Prioridad", C.PRIORIDADES, horizontal=True)
        f_term = d2.date_input("Fecha de término (si es urgente)", value=None, format="DD/MM/YYYY")
        fojas = d3.number_input("Fojas", min_value=0, value=0, step=1)
        ubic = d4.selectbox("Ubicación actual", lista_dep, index=K.idx(lista_dep, C.DEP_PROPIA))
        e1, e2, e3 = st.columns(3)
        entrega = e1.text_input("Entregado por (quien lo trae)")
        recibe = e2.text_input("Recibido por", value=K.usuario())
        import auth

        estado = e3.selectbox("Estado", C.ESTADOS if auth.puede("tramitar") else [x for x in C.ESTADOS if x != "TRAMITADO"])
        obs = st.text_area("Observaciones", height=60)

        curso, personal_df = None, None
        if es_curso:
            ui.seccion("🎓 Datos de la actividad (curso, formación, disertación, congreso, evento…)")
            cat_def = 1 if any(k in tipo for k in ("DICTAR", "DISERTACIÓN")) else 0
            a_1, a_2, a_3 = st.columns([2, 1, 2])
            tipo_act = a_1.selectbox("Tipo de actividad", C.TIPOS_ACTIVIDAD,
                                     index=K.idx(C.TIPOS_ACTIVIDAD, C.ACTIVIDAD_POR_TIPO.get(tipo, "CURSO")))
            hora_act = a_2.text_input("Hora", placeholder="08:30")
            organiza = a_3.text_input("Organiza / convoca")
            k1, k2 = st.columns(2)
            categoria = k1.radio("Categoría", C.CATEGORIAS_CURSO, index=cat_def, horizontal=True)
            requerimiento = k2.radio("¿Qué se solicita?", C.REQUERIMIENTOS, horizontal=True)
            k3, k4 = st.columns(2)
            nombre_curso = k3.text_input("Nombre de la actividad")
            div_dicta = k4.text_input("División / institución que dicta")
            k5, k6, k7 = st.columns(3)
            lugar = k5.text_input("Lugar")
            ambito = k6.selectbox("Ámbito", C.AMBITOS)
            modalidad = k7.selectbox("Modalidad", C.MODALIDADES)
            k8, k9, k10 = st.columns(3)
            f_ini = k8.date_input("Fecha de inicio", value=None, format="DD/MM/YYYY")
            f_fin = k9.date_input("Fecha de finalización", value=None, format="DD/MM/YYYY")
            plan = k10.checkbox("Integra la planificación anual")
            st.markdown("**👮 Personal afectado (cursantes, disertantes, participantes, colaboradores)**")
            personal_df = K.editor_personal(None, "n_personal")
            curso = dict(categoria=categoria, requerimiento=requerimiento, nombre=nombre_curso, division_dicta=div_dicta,
                         lugar=lugar, ambito=ambito, modalidad=modalidad, fecha_inicio=f_ini, fecha_fin=f_fin,
                         planificacion_anual=plan, tipo_actividad=tipo_act, hora=hora_act.strip() or None,
                         organiza=organiza.strip().upper() or None)

        enviar = st.form_submit_button("💾 Registrar expediente", disabled=bool(conflicto))

    if not enviar:
        return
    errores = []
    if not tipo:
        errores.append("Seleccione el tipo de expediente.")
    if origen == C.ORIGENES[1] and not dep_org:
        errores.append("Indique la dependencia de origen.")
    if prioridad == "URGENTE TRÁMITE" and not f_term:
        st.warning("Expediente urgente sin fecha de término: se registrará igual, pero no tendrá alerta de vencimiento.")
    if curso and not curso["nombre"].strip():
        errores.append("Indique el nombre de la actividad.")
    if curso and curso["fecha_inicio"] and curso["fecha_fin"] and curso["fecha_fin"] < curso["fecha_inicio"]:
        errores.append("La fecha de finalización es anterior a la de inicio.")
    if errores:
        for e in errores:
            st.error(e)
        return

    exp = dict(
        nro_exp=int(nro), folio=int(folio), orden=int(orden), libro=int(libro), anio=f_ing.year,
        fecha_ingreso=f_ing, origen=origen, dependencia_origen=dep_org, nro_exp_origen=nro_org.strip() or None,
        tipo=tipo, asunto=asunto.strip() or None, iniciador=iniciador.strip().upper() or None, prioridad=prioridad,
        fecha_termino=f_term, estado=estado, ubicacion_actual=ubic, destino=destino, despacho=despacho or None, fojas=int(fojas) or None, observaciones=obs.strip() or None,
    )
    mov = dict(
        fecha_hora=datetime.combine(f_ing, h_ing), tipo="INGRESO" if origen == C.ORIGENES[1] else "PASE INTERNO",
        origen=dep_org, destino=C.DEP_PROPIA, entregado_por=entrega.strip().upper() or None,
        recibido_por=recibe.strip().upper() or None, fojas=int(fojas) or None, urgente=prioridad == "URGENTE TRÁMITE",
        observaciones="Registro inicial en libro",
    )
    eventos = []
    personal = []
    if curso:
        personal = K.limpiar_personal(personal_df)
        curso["nombre"] = curso["nombre"].strip().upper()
        curso["division_dicta"] = curso["division_dicta"].strip().upper() or None
        curso["lugar"] = curso["lugar"].strip().upper() or None
        curso["estado"] = "SOLICITADO"
    try:
        exp_id, ident_db = db.crear_expediente(exp, mov, curso, personal, eventos, K.usuario())
    except Exception as e:
        st.error(f"No se pudo registrar: {e}")
        return
    st.session_state["ultimo_alta"] = {**exp, "id": exp_id, "identificador": ident_db}
    for k in ["n_tipo", "n_nf", "n_nro", "n_lib", "n_dep_org", "n_destino"]:
        st.session_state.pop(k, None)
    st.rerun()
