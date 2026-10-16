import pandas as pd
import streamlit as st

import catalogos as C
import comun as K
import db
import reportes as R
import ui


def _datos_curso(c, key, exp_id=None, tipo_def=None):
    """Alta/edición de actividad (curso, formación, disertación, congreso, evento…). c = Series o None."""
    g = (lambda k, d=None: c.get(k) if c is not None and pd.notna(c.get(k)) else d)
    with st.form(f"fc_{key}"):
        t1_, t2_, t3_ = st.columns([2, 1, 2])
        tipo_act = t1_.selectbox("Tipo de actividad", C.TIPOS_ACTIVIDAD,
                                 index=K.idx(C.TIPOS_ACTIVIDAD, g("tipo_actividad", tipo_def or "CURSO")))
        hora = t2_.text_input("Hora", g("hora", "") or "", placeholder="08:30")
        organiza = t3_.text_input("Organiza / convoca", g("organiza", "") or "")
        k1, k2 = st.columns(2)
        categoria = k1.radio("Categoría", C.CATEGORIAS_CURSO, index=K.idx(C.CATEGORIAS_CURSO, g("categoria")), horizontal=True)
        requerimiento = k2.radio("¿Qué se solicita?", C.REQUERIMIENTOS, index=K.idx(C.REQUERIMIENTOS, g("requerimiento")), horizontal=True)
        k3, k4 = st.columns(2)
        nombre = k3.text_input("Nombre de la actividad", g("nombre", ""))
        div = k4.text_input("División / institución que dicta", g("division_dicta", ""))
        k5, k6, k7, k8 = st.columns(4)
        lugar = k5.text_input("Lugar", g("lugar", ""))
        ambito = k6.selectbox("Ámbito", C.AMBITOS, index=K.idx(C.AMBITOS, g("ambito")))
        modalidad = k7.selectbox("Modalidad", C.MODALIDADES, index=K.idx(C.MODALIDADES, g("modalidad")))
        estado = k8.selectbox("Estado", C.ESTADOS_CURSO, index=K.idx(C.ESTADOS_CURSO, g("estado"), 1))
        k9, k10, k11 = st.columns(3)
        fi = g("fecha_inicio")
        ff = g("fecha_fin")
        f_ini = k9.date_input("Inicio", value=pd.Timestamp(fi).date() if fi is not None else None, format="DD/MM/YYYY")
        f_fin = k10.date_input("Fin", value=pd.Timestamp(ff).date() if ff is not None else None, format="DD/MM/YYYY")
        plan = k11.checkbox("Planificación anual", value=bool(g("planificacion_anual", False)))
        o1, o2 = st.columns(2)
        responsable = o1.text_input("Responsable por la Dirección", g("responsable", "") or "")
        obs = o2.text_input("Observaciones / resultado", g("observaciones", "") or "")
        st.markdown("**👮 Personal**")
        pers = db.df_personal()
        pers = pers[pers["curso_id"] == c["id"]] if c is not None else pd.DataFrame()
        ed = K.editor_personal(pers, f"pers_{key}")
        ok = st.form_submit_button("💾 Guardar actividad y personal")
    if ok:
        if not nombre.strip():
            st.error("Falta el nombre de la actividad.")
            return
        data = dict(categoria=categoria, requerimiento=requerimiento, nombre=nombre.strip().upper(),
                    division_dicta=div.strip().upper() or None, lugar=lugar.strip().upper() or None, ambito=ambito,
                    modalidad=modalidad, estado=estado, fecha_inicio=f_ini, fecha_fin=f_fin, planificacion_anual=plan,
                    observaciones=obs.strip() or None, tipo_actividad=tipo_act, hora=hora.strip() or None,
                    organiza=organiza.strip().upper() or None, responsable=responsable.strip().upper() or None)
        if exp_id is not None:
            data["expediente_id"] = int(exp_id)
        db.guardar_curso(data, K.limpiar_personal(ed), int(c["id"]) if c is not None else None, K.usuario())
        st.toast("Actividad guardada", icon="✅")
        st.rerun()


def auth_puede(p):
    import auth

    return auth.puede(p)


def render():
    ui.header("Ficha de Expediente", "Hoja de ruta, movimientos, curso y personal")
    exp = db.df_expedientes()
    r = K.selector_expediente("ficha_sel", exp)
    if r is None:
        return
    exp_id = int(r["id"])
    mapa = ui.mapa_dependencias()
    ui.tarjeta_expediente(r, mapa)

    movs_all = db.df_movimientos()
    movs = movs_all[movs_all["expediente_id"] == exp_id]
    cursos = db.df_cursos()
    cursos = cursos[cursos["expediente_id"] == exp_id]
    pers = db.df_personal()
    pers = pers[pers["curso_id"].isin(cursos["id"])]

    dias = ui.dias_desde(r["fecha_ingreso"])
    ui.kpis(
        [
            ("Días desde ingreso", dias if dias is not None else "—", ui.fmt_fecha(r["fecha_ingreso"]), "#3B82F6"),
            ("Movimientos", len(movs), f"último {ui.fmt_fecha(r['ult_mov'], True)}", C.PALETA[6]),
            ("Dependencias recorridas", movs["destino"].nunique(), "destinos distintos", C.PALETA[2]),
            ("Personal afectado", len(pers), f"{len(cursos)} curso(s)", C.PALETA[4]),
        ]
    )

    b1, b2 = st.columns(2)
    b1.download_button("🖨️ Hoja de ruta (PDF)",
                       R.pdf_hoja_ruta(r.to_dict(), movs, cursos, pers, K.LOGO),
                       file_name=f"hoja_ruta_{r['identificador'].replace('/', '-')}_{r['anio']}.pdf", mime="application/pdf")
    resumen = R.msg_alta(r.to_dict()) + f"\n📍 Ubicación actual: {r['ubicacion_actual'] or '—'}\nEstado: {r['estado']}"
    b2.link_button("📲 Compartir por WhatsApp", R.link_whatsapp(resumen))

    t0, tp, t1, t2, t3, t4, t5 = st.tabs(["✅ Trámite", "📎 PDF", "🧭 Hoja de ruta", "🔁 Registrar movimiento", "🎓 Curso y personal", "🔔 Alertas", "✏️ Editar"])

    with tp:
        K.panel_pdf(r, f"ficha_{exp_id}")

    with t0:
        K.form_tramite(r, f"ficha_{exp_id}")

    with t1:
        ui.timeline(movs, mapa)
        if not movs.empty:
            import auth

            if auth.puede("editar"):
                with st.expander("🗑️ Corregir: eliminar un movimiento cargado por error"):
                    opc = {int(m["id"]): f"{ui.fmt_fecha(m['fecha_hora'], True)} · {m['tipo']} ➜ {m['destino']}" for _, m in movs.iterrows()}
                    mid = st.selectbox("Movimiento", list(opc), format_func=opc.get, key="del_mov")
                    if st.button("Eliminar movimiento", key="del_mov_btn"):
                        db.eliminar_movimiento(mid, K.usuario())
                        st.rerun()

    with t2:
        K.form_movimiento(r, f"ficha_{exp_id}")

    with t3:
        if cursos.empty:
            st.caption("Este expediente no tiene curso asociado.")
            if st.toggle("➕ Agregar datos de curso / actividad", key="add_curso"):
                _datos_curso(None, f"nuevo_{exp_id}", exp_id, C.ACTIVIDAD_POR_TIPO.get(r["tipo"]))
        for _, c in cursos.iterrows():
            ui.seccion(f"🎓 {c['nombre']} · {c['fase']}")
            st.markdown(
                f"<div class='meta'>{ui.chip(c['categoria'] or '—', C.PALETA[0])}{ui.chip(c['requerimiento'] or '—', C.PALETA[3])}"
                f"{ui.chip(c['modalidad'] or '—', C.PALETA[6])}{ui.chip(c['ambito'] or '—', C.PALETA[2])}<br>"
                f"Dicta: <b>{ui.esc(c['division_dicta'])}</b> · Lugar: <b>{ui.esc(c['lugar'])}</b> · "
                f"{ui.fmt_fecha(c['fecha_inicio'])} al {ui.fmt_fecha(c['fecha_fin'])}</div>",
                unsafe_allow_html=True,
            )
            _datos_curso(c, f"c{c['id']}", exp_id)
            if auth_puede("editar") and st.button("🗑️ Eliminar curso", key=f"delc_{c['id']}"):
                db.eliminar_curso(int(c["id"]), K.usuario())
                st.rerun()

    with t4:
        ev = db.df_eventos()
        ev = ev[ev["expediente_id"] == exp_id]
        for _, v in ev.iterrows():
            est = "✅" if v["completado"] else "⏳"
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"{est} **{ui.esc(v['titulo'])}** · {ui.fmt_fecha(v['fecha'])} {ui.esc(v['hora'] or '')} · {ui.esc(v['tipo'] or '')}")
            if c2.button("✔" if not v["completado"] else "↺", key=f"evc_{v['id']}"):
                db.completar_evento(int(v["id"]), not v["completado"])
                st.rerun()
        with st.form(f"ev_{exp_id}", clear_on_submit=True):
            st.markdown("**Nueva alerta / evento para este expediente**")
            e1, e2, e3 = st.columns(3)
            tit = e1.text_input("Título")
            tip = e2.selectbox("Tipo", C.TIPOS_EVENTO)
            fec = e3.date_input("Fecha", db.hoy(), format="DD/MM/YYYY")
            e4, e5, e6 = st.columns(3)
            hora = e4.text_input("Hora", placeholder="09:00")
            lug = e5.text_input("Lugar")
            av = e6.number_input("Avisar días antes", 0, 60, 3)
            if st.form_submit_button("➕ Agregar alerta") and tit.strip():
                db.crear_evento(dict(expediente_id=exp_id, titulo=tit.strip(), tipo=tip, fecha=fec, hora=hora or None,
                                     lugar=lug or None, dias_aviso=int(av)), K.usuario())
                st.rerun()

    with t5:
        import auth

        if not auth.puede("editar"):
            auth.aviso_sin_permiso("la edición de expedientes")
        else:
            lista_dep = K.deps(False)
            lista_tipos = K.tipos(False)
            with st.form(f"edit_{exp_id}"):
                st.caption("⚠️ Cambiar N° / folio / orden modifica la identificación del expediente.")
                n1, n2, n3, n4, n5 = st.columns(5)
                nro = n1.number_input("N° Exp", 1, value=int(r["nro_exp"]))
                fol = n2.number_input("Folio", 1, value=int(r["folio"]))
                ord_ = n3.number_input("Orden", 1, value=int(r["orden"]))
                lib = n4.number_input("Libro", 1, value=int(r["libro"]))
                anio = n5.number_input("Año", 2000, 2100, value=int(r["anio"]))
                a1, a2, a3 = st.columns(3)
                tipo = a1.selectbox("Tipo", lista_tipos, index=K.idx(lista_tipos, r["tipo"]))
                origen = a2.selectbox("Origen", C.ORIGENES, index=K.idx(C.ORIGENES, r["origen"]))
                dep_org = a3.selectbox("Dependencia de origen", lista_dep, index=K.idx(lista_dep, r["dependencia_origen"]))
                asunto = st.text_area("Asunto", r["asunto"] or "", height=70)
                b1_, b2_, b3_ = st.columns(3)
                nro_org = b1_.text_input("N° origen", r["nro_exp_origen"] or "")
                inic = b2_.text_input("Iniciador", r["iniciador"] or "")
                f_ing = b3_.date_input("Fecha ingreso", r["fecha_ingreso"].date(), format="DD/MM/YYYY")
                c1, c2, c3, c4 = st.columns(4)
                prio = c1.selectbox("Prioridad", C.PRIORIDADES, index=K.idx(C.PRIORIDADES, r["prioridad"]))
                ft = c2.date_input("Fecha término", r["fecha_termino"].date() if pd.notna(r["fecha_termino"]) else None, format="DD/MM/YYYY")
                est = c3.selectbox("Estado", C.ESTADOS, index=K.idx(C.ESTADOS, r["estado"]))
                desp = c4.selectbox("Despacho", C.DESPACHOS, index=K.idx(C.DESPACHOS, r["despacho"] or ""))
                d1, d2, d3 = st.columns([2, 2, 1])
                ubic = d1.selectbox("Ubicación actual", lista_dep, index=K.idx(lista_dep, r["ubicacion_actual"]))
                dest_ops = [None] + lista_dep
                dest = d2.selectbox("🎯 Destino / instancia", dest_ops, index=K.idx(dest_ops, r.get("destino")),
                                    format_func=lambda d: d or "— A definir —")
                fojas = d3.number_input("Fojas", 0, value=K.num(r["fojas"]))
                obs = st.text_area("Observaciones", r["observaciones"] or "", height=60)
                if st.form_submit_button("💾 Guardar cambios"):
                    choque = db.conflicto_numeracion(nro, fol, ord_, lib, anio, excluir_id=exp_id)
                    if choque:
                        st.error(f"La numeración choca con el expediente {choque}.")
                    else:
                        db.actualizar_expediente(exp_id, dict(
                            nro_exp=int(nro), folio=int(fol), orden=int(ord_), libro=int(lib), anio=int(anio), tipo=tipo,
                            origen=origen, dependencia_origen=dep_org, asunto=asunto.strip() or None,
                            nro_exp_origen=nro_org.strip() or None, iniciador=inic.strip().upper() or None, fecha_ingreso=f_ing,
                            prioridad=prio, fecha_termino=ft, estado=est, despacho=desp or None, ubicacion_actual=ubic, destino=dest,
                            fojas=int(fojas) or None, observaciones=obs.strip() or None), K.usuario())
                        st.toast("Expediente actualizado", icon="✅")
                        st.rerun()
            if auth.puede("eliminar"):
                with st.expander("🗑️ Eliminar expediente"):
                    conf = st.text_input(f"Escriba {r['identificador']} para confirmar", key="del_conf")
                    if st.button("Eliminar definitivamente", disabled=conf.strip() != r["identificador"], key="del_exp"):
                        db.eliminar_expediente(exp_id, K.usuario())
                        st.session_state.pop("exp_sel", None)
                        st.rerun()
