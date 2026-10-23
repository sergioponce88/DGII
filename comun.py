"""Piezas compartidas entre vistas: navegación, selectores, formulario de movimiento y motor de alertas."""
from datetime import datetime, time

import pandas as pd
import streamlit as st

import catalogos as C
import db
import reportes as R
import ui

LOGO = "assets/logo_policia.png"
LOGO_IESP = "assets/logo_iesp.png"

PAG_PANEL = "📊 Panel de Control"
PAG_NUEVO = "➕ Nuevo Expediente"
PAG_MOV = "🔁 Movimiento Rápido"
PAG_TRAMITAR = "📝 Tramitar"
PAG_LIBRO = "📚 Libro de Registro"
PAG_FICHA = "🔎 Ficha de Expediente"
PAG_CURSOS = "🎓 Actividades y Personal"
PAG_ALERTAS = "🔔 Alertas y Agenda"
PAG_CARGA = "📥 Carga Masiva"
PAG_INFORMES = "📈 Informes"
PAG_CONFIG = "⚙️ Configuración"
PAGINAS = [PAG_PANEL, PAG_NUEVO, PAG_MOV, PAG_TRAMITAR, PAG_LIBRO, PAG_FICHA, PAG_CURSOS, PAG_ALERTAS, PAG_CARGA, PAG_INFORMES, PAG_CONFIG]


def usuario():
    import auth

    u = auth.actual()
    return auth.nombre_completo(u) if u else "SIN IDENTIFICAR"


def ir_a(pagina, exp_id=None):
    st.session_state["_goto"] = pagina
    if exp_id is not None:
        st.session_state["exp_sel"] = int(exp_id)
    st.rerun()


def deps(solo_activas=True):
    return db.df_dependencias(solo_activas)["nombre"].tolist()


def tipos(solo_activos=True):
    return db.df_tipos(solo_activos)["nombre"].tolist()


def tipo_es_curso(nombre):
    t = db.df_tipos()
    m = t[t["nombre"] == nombre]
    return bool(m["es_curso"].iloc[0]) if not m.empty else False


def tel_dep(nombre):
    d = db.df_dependencias()
    m = d[d["nombre"] == nombre]
    tel = m["telefono_wp"].iloc[0] if not m.empty else None
    return tel or db.get_config().get("wp_por_defecto") or None


def num(x, defecto=0):
    try:
        return defecto if x is None or pd.isna(x) else int(x)
    except (TypeError, ValueError):
        return defecto


def idx(lista, valor, defecto=0):
    try:
        return lista.index(valor)
    except ValueError:
        return defecto


def etiqueta_exp(r):
    a = r.get("asunto")
    asunto = a[:45] if isinstance(a, str) else ""
    return f"{r['identificador']} · {r['anio']} · {r['tipo']}" + (f" · {asunto}" if asunto else "")


def selector_expediente(key, df=None, label="Buscar expediente (N°, tipo o asunto):"):
    df = db.df_expedientes() if df is None else df
    if df.empty:
        st.info("Todavía no hay expedientes registrados.")
        return None
    ids = df["id"].tolist()
    etiquetas = {r["id"]: etiqueta_exp(r) for _, r in df.iterrows()}
    pre = st.session_state.get("exp_sel")
    i = ids.index(pre) if pre in ids else None
    sel = st.selectbox(label, ids, index=i, format_func=lambda x: etiquetas.get(x, str(x)), key=key, placeholder="Escriba para buscar…")
    if sel is None:
        return None
    st.session_state["exp_sel"] = sel
    return df[df["id"] == sel].iloc[0]


# ───────────────────────── Alta rápida de dependencia (➕) ─────────────────────────
def boton_nueva_dependencia(key, seleccionar_en=None):
    """Popover ➕ para agregar una dependencia sin salir de la pantalla.
    seleccionar_en: key del selectbox donde queda seleccionada la nueva dependencia."""
    with st.popover("➕", help="Agregar una dependencia que no está en la lista"):
        with st.form(f"nd_{key}", clear_on_submit=True):
            st.markdown("**Nueva dependencia**")
            nombre = st.text_input("Nombre", placeholder="Ej: COMISARÍA SECCIONAL 5°")
            c1, c2 = st.columns(2)
            sigla = c1.text_input("Sigla (opcional)")
            tel = c2.text_input("WhatsApp (opcional)")
            if st.form_submit_button("➕ Agregar"):
                if not nombre.strip():
                    st.error("Ingrese el nombre.")
                else:
                    n, existia = db.agregar_dependencia(nombre, sigla, None, tel)
                    if seleccionar_en:
                        st.session_state[f"_sel_{seleccionar_en}"] = n
                    st.toast(f"{'Ya existía' if existia else 'Agregada'}: {n}", icon="🏢")
                    st.rerun()


def preselect(key):
    """Aplica la selección pendiente de una dependencia recién agregada (antes de crear el widget)."""
    v = st.session_state.pop(f"_sel_{key}", None)
    if v is not None:
        st.session_state[key] = v


# ───────────────────────── Movimiento ─────────────────────────
def form_movimiento(exp, key):
    """Formulario de registro de movimiento (salida / ingreso / pase / archivo)."""
    lista_dep = deps()
    ub = exp.get("ubicacion_actual") or C.DEP_PROPIA
    c_a, c_b = st.columns([6, 1], vertical_alignment="bottom")
    c_a.caption("¿El destino no está en la lista? Agréguelo con ➕")
    with c_b:
        boton_nueva_dependencia(f"mov_{key}")
    with st.form(f"fmov_{key}", clear_on_submit=True):
        c1, c2 = st.columns(2)
        import auth

        tipos_ok = C.TIPOS_MOVIMIENTO if auth.puede("tramitar") else [t for t in C.TIPOS_MOVIMIENTO if t != "TRÁMITE"]
        estados_ok = C.ESTADOS if auth.puede("tramitar") else [e for e in C.ESTADOS if e != "TRAMITADO"]
        tipo_mov = c1.selectbox("Tipo de movimiento", tipos_ok, key=f"tm_{key}")
        defecto_dest = exp.get("destino") if isinstance(exp.get("destino"), str) and exp.get("destino") != ub else (
            C.DEP_PROPIA if ub != C.DEP_PROPIA else (lista_dep[1] if len(lista_dep) > 1 else lista_dep[0]))
        destino = c2.selectbox("Destino ➜", lista_dep, index=idx(lista_dep, defecto_dest), key=f"de_{key}")
        c3, c4 = st.columns(2)
        origen = c3.selectbox("Desde", lista_dep, index=idx(lista_dep, ub), key=f"or_{key}")
        despacho = c4.selectbox("Despacho / Resolución", C.DESPACHOS, index=idx(C.DESPACHOS, exp.get("despacho") or ""), key=f"dp_{key}")
        c5, c6 = st.columns(2)
        f = c5.date_input("Fecha", db.hoy(), format="DD/MM/YYYY", key=f"fe_{key}")
        h = c6.time_input("Hora", db.ahora().time().replace(second=0), step=300, key=f"ho_{key}")
        c7, c8 = st.columns(2)
        entrega = c7.text_input("Quién lo lleva / entrega", key=f"en_{key}")
        recibe = c8.text_input("Quién lo recibe", key=f"re_{key}")
        c9, c10, c11 = st.columns([1, 1, 2])
        fojas = c9.number_input("Fojas", min_value=0, value=num(exp.get("fojas")), step=1, key=f"fo_{key}")
        urgente = c10.checkbox("⚡ Urgente trámite", value=exp.get("prioridad") == "URGENTE TRÁMITE", key=f"ur_{key}")
        estado_sug = C.ESTADO_POR_MOVIMIENTO.get(tipo_mov, exp.get("estado"))
        nuevo_estado = c11.selectbox("Estado resultante", ["(automático)"] + estados_ok, key=f"es_{key}",
                                     help="Automático: SALIDA→REMITIDO, INGRESO→EN TRÁMITE, PASE→EN DESPACHO, ARCHIVO→ARCHIVADO")
        obs = st.text_area("Observaciones", height=70, key=f"ob_{key}")
        ok = st.form_submit_button("💾 Registrar movimiento")
    if ok:
        mov = {
            "fecha_hora": datetime.combine(f, h if isinstance(h, time) else time(0, 0)),
            "tipo": tipo_mov,
            "origen": origen,
            "destino": destino,
            "despacho": despacho or None,
            "entregado_por": entrega.strip().upper() or None,
            "recibido_por": recibe.strip().upper() or None,
            "fojas": int(fojas) or None,
            "urgente": bool(urgente),
            "observaciones": obs.strip() or None,
        }
        estado_final = estado_sug if nuevo_estado == "(automático)" else nuevo_estado
        try:
            db.registrar_movimiento(int(exp["id"]), mov, estado_final, usuario())
            st.session_state[f"ultimo_mov_{key}"] = {"exp": dict(exp), "mov": mov}
            st.toast(f"Movimiento registrado: {exp['identificador']} ➜ {destino}", icon="✅")
            st.rerun()
        except Exception as e:
            st.error(f"No se pudo registrar el movimiento: {e}")

    ult = st.session_state.get(f"ultimo_mov_{key}")
    if ult and ult["exp"]["id"] == exp["id"]:
        m = ult["mov"]
        st.success(f"✔ Último movimiento: {m['tipo']} ➜ {m['destino']} ({ui.fmt_fecha(m['fecha_hora'], True)})")
        msg = R.msg_movimiento(ult["exp"], m)
        st.link_button("📲 Informar por WhatsApp", R.link_whatsapp(msg, tel_dep(m["destino"])))


# ───────────────────────── Reingreso ─────────────────────────
def form_reingreso(exp, key):
    """Vuelve a la Dirección un expediente ya registrado (tramitado o remitido): se actualiza el MISMO expediente."""
    ub = exp.get("ubicacion_actual") or "—"
    if bool(exp.get("tramitado")):
        ui.alerta("↩️", f"Vuelve un expediente TRAMITADO el {ui.fmt_fecha(exp.get('fecha_tramite'), True)} por {exp.get('tramitado_por') or '—'}",
                  f"{exp.get('accion_tramite') or ''} · {exp.get('detalle_tramite') or ''} — El trámite anterior queda en la hoja de ruta.",
                  C.STATUS["warning"])
    else:
        ui.alerta("↩️", f"Último lugar registrado: {ub}", "Se asienta el reingreso sobre el mismo N° / folio / orden.", C.STATUS["warning"])
    if int(num(exp.get("reingresos"))):
        st.caption(f"Este expediente ya reingresó {int(num(exp.get('reingresos')))} vez/veces.")
    lista_dep = deps()
    c_a, c_b = st.columns([6, 1], vertical_alignment="bottom")
    c_a.caption("¿De dónde vuelve? Si no está en la lista, agréguela con ➕")
    with c_b:
        boton_nueva_dependencia(f"rei_{key}")
    with st.form(f"frei_{key}", clear_on_submit=True):
        c1, c2 = st.columns(2)
        desde = c1.selectbox("Vuelve desde", lista_dep, index=idx(lista_dep, ub if ub != C.DEP_PROPIA else exp.get("destino")), key=f"rd_{key}")
        despacho = c2.selectbox("Vuelve con (despacho / resolución)", C.DESPACHOS, format_func=lambda d: d or "— Sin indicar —", key=f"rp_{key}")
        c3, c4 = st.columns(2)
        f = c3.date_input("Fecha de reingreso", db.hoy(), format="DD/MM/YYYY", key=f"rf_{key}")
        h = c4.time_input("Hora", db.ahora().time().replace(second=0), step=300, key=f"rh_{key}")
        c5, c6 = st.columns(2)
        trae = c5.text_input("Quién lo trae", key=f"rt_{key}")
        recibe = c6.text_input("Quién lo recibe", value=usuario(), key=f"rr_{key}")
        c7, c8, c9 = st.columns([1, 1, 2])
        fojas = c7.number_input("Fojas actuales", min_value=0, value=num(exp.get("fojas")), step=1, key=f"rfo_{key}")
        urgente = c8.checkbox("⚡ Urgente", key=f"ru_{key}")
        f_term = c9.date_input("Nueva fecha de término (si es urgente)", None, format="DD/MM/YYYY", key=f"rft_{key}")
        motivo = st.text_area("Motivo / qué se solicita ahora", height=70, key=f"rm_{key}",
                              placeholder="Ej.: vuelve con informe de la División, para nueva providencia…")
        ok = st.form_submit_button("📥 Registrar reingreso", type="primary")
    if ok:
        mov = {
            "fecha_hora": datetime.combine(f, h if isinstance(h, time) else time(0, 0)),
            "tipo": "REINGRESO", "origen": desde, "destino": C.DEP_PROPIA, "despacho": despacho or None,
            "entregado_por": trae.strip().upper() or None, "recibido_por": recibe.strip().upper() or None,
            "fojas": int(fojas) or None, "urgente": bool(urgente), "observaciones": motivo.strip() or None,
        }
        try:
            db.registrar_movimiento(int(exp["id"]), mov, "EN TRÁMITE", usuario(), fecha_termino=f_term if urgente else None)
            st.session_state[f"ultimo_mov_{key}"] = {"exp": dict(exp), "mov": mov}
            st.toast(f"Reingreso registrado: {exp['identificador']} · queda PENDIENTE DE TRÁMITE", icon="📥")
            st.rerun()
        except Exception as e:
            st.error(f"No se pudo registrar el reingreso: {e}")
    ult = st.session_state.get(f"ultimo_mov_{key}")
    if ult and ult["exp"]["id"] == exp["id"] and ult["mov"]["tipo"] == "REINGRESO":
        st.success(f"✔ Reingreso desde {ult['mov']['origen']} ({ui.fmt_fecha(ult['mov']['fecha_hora'], True)}). Ya puede tramitarse nuevamente.")


# ───────────────────────── Trámite ─────────────────────────
def form_tramite(exp, key):
    """Marca el expediente como TRAMITADO: qué se hizo, quién y cuándo. Permite anular la marca."""
    if bool(exp.get("tramitado")):
        ui.alerta("✅", f"TRAMITADO el {ui.fmt_fecha(exp.get('fecha_tramite'), True)} por {exp.get('tramitado_por') or '—'}",
                  f"{exp.get('accion_tramite') or ''} · {exp.get('detalle_tramite') or ''}", C.STATUS["ok"])
        import auth

        if not auth.puede("tramitar"):
            return
        with st.expander("↺ Anular la marca de tramitado"):
            motivo = st.text_input("Motivo", key=f"anu_m_{key}")
            if st.button("Anular", key=f"anu_b_{key}"):
                db.marcar_tramitado([int(exp["id"])], None, motivo, db.ahora(), usuario(), usuario(), revertir=True)
                st.rerun()
        return
    import auth

    ui.alerta("⏳", "PENDIENTE DE TRÁMITE", "Registre lo realizado para dejarlo asentado en la hoja de ruta.", C.STATUS["warning"])
    if not auth.puede("tramitar"):
        auth.aviso_sin_permiso("la marca de tramitado")
        return
    if st.button("📝 Tramitar con modelos (nota en Word)", key=f"ir_tram_{key}", type="primary", width="stretch"):
        st.session_state["tram_sel"] = int(exp["id"])
        ir_a(PAG_TRAMITAR, exp["id"])
    st.caption("…o registre manualmente lo realizado:")
    with st.form(f"ftr_{key}", clear_on_submit=True):
        c1, c2 = st.columns(2)
        accion = c1.selectbox("¿Qué se hizo?", C.ACCIONES_TRAMITE, key=f"tr_ac_{key}")
        quien = c2.text_input("Tramitado por", value=usuario(), key=f"tr_q_{key}")
        c3, c4 = st.columns(2)
        f = c3.date_input("Fecha", db.hoy(), format="DD/MM/YYYY", key=f"tr_f_{key}")
        h = c4.time_input("Hora", db.ahora().time().replace(second=0), step=300, key=f"tr_h_{key}")
        det = st.text_area("Detalle (N° de nota, providencia, a quién se respondió…)", height=70, key=f"tr_d_{key}")
        if st.form_submit_button("✅ Marcar como TRAMITADO"):
            db.marcar_tramitado([int(exp["id"])], accion, det.strip() or None, datetime.combine(f, h),
                                quien.strip().upper() or usuario(), usuario())
            st.toast(f"Exp. {exp['identificador']} tramitado", icon="✅")
            st.rerun()


# ───────────────────────── PDF del expediente (Google Drive) ─────────────────────────
def panel_pdf(exp, key):
    import gdrive

    exp_id = int(exp["id"])
    adj = db.df_adjuntos(exp_id)
    if not adj.empty:
        ult = adj.iloc[0]
        st.link_button(f"📄 Ver PDF del expediente (v{int(ult['version'])})", ult["link"])
        with st.expander(f"🗂️ Versiones ({len(adj)})"):
            for _, a in adj.iterrows():
                st.markdown(f"**v{int(a['version'])}** · {ui.fmt_fecha(a['subido_en'], True)} · {ui.esc(a['subido_por'])} · "
                            f"{num(a['paginas']) or '?'} fojas · {(num(a['bytes']) or 0) / 1e6:.1f} MB · "
                            f"[abrir]({a['link']}) {('· ' + ui.esc(a['descripcion'])) if a['descripcion'] else ''}")
    else:
        st.caption("Este expediente todavía no tiene PDF digitalizado.")

    if not gdrive.conectado():
        st.info("Para subir el PDF, primero conecte Google Drive en ⚙️ Configuración → ☁️ Google Drive.")
        return
    ui.seccion("📎 Subir expediente digitalizado")
    modo = st.segmented_control("Origen", ["📄 Archivo PDF", "📷 Fotos de las fojas"], default="📄 Archivo PDF", key=f"pdfm_{key}")
    if modo == "📷 Fotos de las fojas":
        arch = st.file_uploader("Fotos en orden (en el celular podés usar la cámara)", type=["jpg", "jpeg", "png", "webp"],
                                accept_multiple_files=True, key=f"pdfi_{key}")
    else:
        arch = st.file_uploader("PDF del expediente (si elegís varios, se unen en uno)", type=["pdf"],
                                accept_multiple_files=True, key=f"pdff_{key}")
    desc = st.text_input("Descripción (opcional)", placeholder="Ej: con informe de la División y providencia", key=f"pdfd_{key}")
    if arch and st.button(f"☁️ Subir a Google Drive ({len(arch)} archivo/s)", type="primary", key=f"pdfb_{key}"):
        try:
            with st.spinner("Preparando PDF…"):
                if modo == "📷 Fotos de las fojas":
                    contenido, paginas = gdrive.imagenes_a_pdf(arch), len(arch)
                else:
                    contenido = arch[0].getvalue() if len(arch) == 1 else gdrive.unir_pdfs(arch)
                    try:
                        from pypdf import PdfReader
                        import io as _io
                        paginas = len(PdfReader(_io.BytesIO(contenido)).pages)
                    except Exception:
                        paginas = None
            ver = (0 if adj.empty else int(adj["version"].max())) + 1
            nombre = f"{exp['nro_exp']}-{exp['folio']}-{exp['orden']}_{exp['anio']}_v{ver}.pdf"
            with st.spinner(f"Subiendo {len(contenido) / 1e6:.1f} MB a Google Drive…"):
                fid, link = gdrive.subir_pdf(nombre, contenido, int(exp["anio"]), f"{exp['tipo']} · {exp.get('asunto') or ''} {desc}".strip())
            db.registrar_adjunto(exp_id, nombre, fid, link, len(contenido), paginas, desc.strip() or None, usuario())
            st.toast(f"PDF subido: {nombre}", icon="☁️")
            st.rerun()
        except gdrive.DriveError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"No se pudo subir el archivo: {e}")


# ───────────────────────── Personal (editor) ─────────────────────────
COLS_PERSONAL = ["apellido", "nombre", "jerarquia", "dni", "division", "provincia", "rol"]


def editor_personal(df_ini, key):
    if df_ini is None or df_ini.empty:
        df_ini = pd.DataFrame(columns=COLS_PERSONAL)
    df_ini = df_ini[COLS_PERSONAL].copy()
    return st.data_editor(
        df_ini,
        key=key,
        num_rows="dynamic",
        width="stretch",
        hide_index=True,
        column_config={
            "apellido": st.column_config.TextColumn("Apellido", required=True),
            "nombre": st.column_config.TextColumn("Nombre"),
            "jerarquia": st.column_config.SelectboxColumn("Jerarquía / Grado", options=list(C.JERARQUIAS)),
            "dni": st.column_config.TextColumn("DNI"),
            "division": st.column_config.TextColumn("División a la que pertenece"),
            "provincia": st.column_config.SelectboxColumn("Provincia / Fuerza", options=C.PROVINCIAS, default="TUCUMÁN"),
            "rol": st.column_config.SelectboxColumn("Rol", options=C.ROLES_PERSONAL, default="CURSANTE"),
        },
    )


def limpiar_personal(df):
    out = []
    for _, r in df.iterrows():
        ape = str(r.get("apellido") or "").strip()
        if not ape or ape.lower() == "nan":
            continue
        jer = r.get("jerarquia") if isinstance(r.get("jerarquia"), str) else "OTRO"
        out.append(
            {
                "apellido": ape.upper(),
                "nombre": str(r.get("nombre") or "").strip().title(),
                "jerarquia": jer,
                "escalafon": C.escalafon(jer),
                "dni": "".join(ch for ch in str(r.get("dni") or "") if ch.isdigit()) or None,
                "division": str(r.get("division") or "").strip().upper() or None,
                "provincia": r.get("provincia") if isinstance(r.get("provincia"), str) else "TUCUMÁN",
                "rol": r.get("rol") if isinstance(r.get("rol"), str) else "CURSANTE",
            }
        )
    return out


# ───────────────────────── Motor de alertas ─────────────────────────
NIVELES = {
    "critical": ("🔴", C.STATUS["critical"], 0),
    "serious": ("🟠", C.STATUS["serious"], 1),
    "warning": ("🟡", C.STATUS["warning"], 2),
    "info": ("🔵", "#3B82F6", 3),
}


def calcular_alertas():
    cfg = db.get_config()
    n_aviso = int(cfg["dias_aviso_cursos"])
    n_est = int(cfg["dias_estancado"])
    h = pd.Timestamp(db.hoy())
    al = []

    def add(nivel, titulo, detalle, fecha, exp_id=None, dep=None, cat=""):
        al.append({"nivel": nivel, "titulo": titulo, "detalle": detalle, "fecha": fecha, "exp_id": exp_id, "dep": dep, "cat": cat})

    cur = db.df_cursos()
    for _, c in cur.iterrows():
        if c["estado"] in ("NO AUTORIZADO", "SUSPENDIDO"):
            continue
        ini, fin = c["fecha_inicio"], c["fecha_fin"]
        tipo_a = c["tipo_actividad"] if isinstance(c.get("tipo_actividad"), str) else "CURSO"
        ref = f"Exp. {c['identificador']}" if pd.notna(c.get("identificador")) else "Sin expediente"
        lugar = f"{c.get('lugar') or 's/lugar'} · {c.get('modalidad') or ''} · {int(c.get('cant_personal') or 0)} efectivos"
        if pd.notna(ini):
            d = (ini - h).days
            if d == 0:
                add("critical", f"HOY inicia · {tipo_a}: {c['nombre']}", f"{ref} · {lugar}", ini, c.get("expediente_id"), cat="Actividades")
            elif 0 < d <= n_aviso:
                sin_aut = c["estado"] == "SOLICITADO" and "SIN REQUERIMIENTO" not in str(c.get("requerimiento") or "")
                add("serious" if sin_aut else "warning",
                    f"En {d} día{'s' if d > 1 else ''} inicia · {tipo_a}: {c['nombre']}" + (" · SIN AUTORIZACIÓN" if sin_aut else ""),
                    f"{ref} · {ui.fmt_fecha(ini)} · {lugar}", ini, c.get("expediente_id"), cat="Actividades")
        if pd.notna(fin) and (fin - h).days == 0 and not (pd.notna(ini) and ini == fin):
            add("info", f"HOY finaliza · {tipo_a}: {c['nombre']}", f"{ref} · {lugar}", fin, c.get("expediente_id"), cat="Actividades")

    exp = db.df_expedientes()
    abiertos = exp[~exp["estado"].isin(C.ESTADOS_CERRADOS)] if not exp.empty else exp
    for _, e in abiertos.iterrows():
        txt = f"{e['tipo']} · {e.get('asunto') or ''} · 📍 {e.get('ubicacion_actual') or '—'}"
        if pd.notna(e["fecha_termino"]):
            d = (e["fecha_termino"] - h).days
            if d < 0:
                add("critical", f"VENCIDO hace {-d} d · Exp. {e['identificador']}", txt, e["fecha_termino"], e["id"], e.get("ubicacion_actual"), "Vencimientos")
            elif d <= 2:
                add("serious", f"Vence {'HOY' if d == 0 else f'en {d} d'} · Exp. {e['identificador']}", txt, e["fecha_termino"], e["id"], e.get("ubicacion_actual"), "Vencimientos")
        ref = e["ult_mov"] if pd.notna(e["ult_mov"]) else e["fecha_ingreso"]
        if pd.notna(ref):
            ds = (h - ref.normalize()).days
            lim = 2 if e["prioridad"] == "URGENTE TRÁMITE" else n_est
            if ds > lim:
                add("serious" if e["prioridad"] == "URGENTE TRÁMITE" else "info",
                    f"{ds} días sin movimiento · Exp. {e['identificador']}" + (" ⚡" if e["prioridad"] == "URGENTE TRÁMITE" else ""),
                    txt, ref, e["id"], e.get("ubicacion_actual"), "Estancados")

    ev = db.df_eventos()
    for _, v in ev[~ev["completado"].astype(bool)].iterrows() if not ev.empty else []:
        d = (v["fecha"] - h).days
        det = f"{v.get('tipo') or ''} · {v.get('hora') or ''} · {v.get('lugar') or ''}" + (f" · Exp. {v['identificador']}" if pd.notna(v.get("identificador")) else "")
        if d == 0:
            add("critical", f"HOY: {v['titulo']}", det, v["fecha"], v.get("expediente_id"), cat="Agenda")
        elif 0 < d <= int(v.get("dias_aviso") or 3):
            add("warning", f"En {d} día{'s' if d > 1 else ''}: {v['titulo']}", det, v["fecha"], v.get("expediente_id"), cat="Agenda")
        elif d < 0:
            add("info", f"Pendiente de cerrar: {v['titulo']}", det, v["fecha"], v.get("expediente_id"), cat="Agenda")

    al.sort(key=lambda a: (NIVELES[a["nivel"]][2], a["fecha"] if pd.notna(a["fecha"]) else h))
    return al
