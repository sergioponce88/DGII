import re

import pandas as pd

import streamlit as st

import catalogos as C
import comun as K
import db
import reportes as R
import ui


def render():
    ui.header("Configuración", "Libro, alertas, dependencias, tipos de expediente y respaldo")
    import auth

    if not auth.puede("configurar"):
        auth.aviso_sin_permiso("la configuración")
        return
    cfg = db.get_config()
    tu, tn, tw, t1, t2, t3, t5, t4 = st.tabs(["👥 Usuarios", "📝 Notas y autoridades", "📲 Avisos WhatsApp", "📖 Libro y alertas",
                                              "🏢 Dependencias y colores", "🗂️ Tipos de expediente", "☁️ Google Drive", "💾 Respaldo y auditoría"])

    with tw:
        _avisos(cfg)

    with tu:
        _usuarios()

    with tn:
        _tramitacion(cfg)

    with t5:
        _drive(cfg)

    with t1:
        sec_cfg = st.segmented_control("📖 Libro a configurar", list(C.SECRETARIAS), default=C.SEC_DEFAULT, key="cfg_sec",
                                       format_func=lambda k: f"{C.SECRETARIAS[k]['sigla']} — {C.SECRETARIAS[k]['nombre']}") or C.SEC_DEFAULT
        pre = "iesp_" if sec_cfg == "IESP" else ""
        L = lambda k: C.cfg_libro(cfg, sec_cfg, k)  # noqa: E731
        with st.form(f"cfg_libro_{sec_cfg}"):
            st.markdown(f"**Numeración del libro del {C.SECRETARIAS[sec_cfg]['sigla']}**")
            c1, c2, c3 = st.columns(3)
            nro_ini = c1.number_input("N° de expediente inicial", 1, value=int(L("nro_inicial")), help="Se usa solo cuando todavía no hay expedientes cargados en este libro.")
            fol_ini = c2.number_input("Folio inicial", 1, value=int(L("folio_inicial")))
            libro = c3.number_input("Libro actual", 1, value=int(L("libro_actual")))
            c4, c5, c6 = st.columns(3)
            ren = c4.number_input("Renglones (asientos) por folio", 1, 100, int(L("renglones_por_folio")),
                                  help="Cuando el orden llega a este número, el próximo expediente pasa al siguiente folio con orden 1.")
            paso = c5.selectbox("Avance de folio", [2, 1], index=0 if str(L("paso_folio")) == "2" else 1,
                                help="2 = cada asiento ocupa la doble página (se numera la foja izquierda: 1, 3, 5…). 1 = folio correlativo.")
            rei = c6.selectbox("¿El N° de expediente reinicia cada año?", ["NO", "SI"], index=0 if L("reinicio_anual") == "NO" else 1)
            sref = st.text_input("Secretaría que figura en la referencia de las notas", L("sec_ref"))
            st.markdown("**Alertas y avisos** (comunes a ambos libros)")
            a1, a2, a3 = st.columns(3)
            dav = a1.number_input("Avisar inicio de curso (días antes)", 0, 60, int(cfg["dias_aviso_cursos"]))
            dest = a2.number_input("Marcar expediente detenido después de (días)", 1, 365, int(cfg["dias_estancado"]))
            wp = a3.text_input("WhatsApp por defecto (Mesa de Entradas)", cfg.get("wp_por_defecto", ""), placeholder="381 5123456")
            if st.form_submit_button("💾 Guardar configuración"):
                vals = {"nro_inicial": nro_ini, "folio_inicial": fol_ini, "libro_actual": libro, "renglones_por_folio": ren,
                        "paso_folio": paso, "reinicio_anual": rei, "sec_ref": sref.strip()}
                db.set_config({pre + k: v for k, v in vals.items()} | dict(dias_aviso_cursos=dav, dias_estancado=dest, wp_por_defecto=wp.strip()))
                st.toast("Configuración guardada", icon="✅")
                st.rerun()
        s = db.sugerir_numeracion(sec=sec_cfg)
        st.info(f"Próximo asiento sugerido en el libro del {C.SECRETARIAS[sec_cfg]['sigla']}: **{s['nro_exp']}/{s['folio']}/{s['orden']}** (libro {s['libro']}).")

    with t2:
        df = db.df_dependencias()[["id", "nombre", "sigla", "color", "telefono_wp", "activa"]]
        st.caption("El color identifica a la dependencia en tablas, tarjetas, hoja de ruta y gráficos. Use formato #RRGGBB.")
        st.markdown(" ".join(ui.chip(f"{r['sigla'] or ''} · {r['nombre']}", r["color"]) for _, r in df.iterrows()), unsafe_allow_html=True)
        st.markdown("<span style='color:#94A3B8;font-size:.8rem'>Paleta sugerida (apta daltonismo):</span> " + " ".join(ui.chip(c, c) for c in C.PALETA), unsafe_allow_html=True)
        ed = st.data_editor(
            df, key="ed_deps", num_rows="dynamic", hide_index=True, width="stretch",
            column_config={
                "id": None,
                "nombre": st.column_config.TextColumn("Dependencia", required=True, width="large"),
                "sigla": st.column_config.TextColumn("Sigla"),
                "color": st.column_config.TextColumn("Color (#hex)", validate=r"^#[0-9A-Fa-f]{6}$", default="#64748B"),
                "telefono_wp": st.column_config.TextColumn("WhatsApp de contacto"),
                "activa": st.column_config.CheckboxColumn("Activa", default=True),
            },
        )
        if st.button("💾 Guardar dependencias", type="primary"):
            bad = [c for c in ed["color"].fillna("") if c and not re.match(r"^#[0-9A-Fa-f]{6}$", str(c))]
            if bad:
                st.error(f"Colores inválidos: {', '.join(bad)}")
            else:
                db.guardar_catalogo("dependencias", ed, ["nombre", "sigla", "color", "telefono_wp", "activa"])
                st.toast("Dependencias guardadas", icon="✅")
                st.rerun()

    with t3:
        df = db.df_tipos()[["id", "nombre", "grupo", "origen", "es_curso", "activo"]]
        ed = st.data_editor(
            df, key="ed_tipos", num_rows="dynamic", hide_index=True, width="stretch",
            column_config={
                "id": None,
                "nombre": st.column_config.TextColumn("Tipo de expediente", required=True, width="large"),
                "grupo": st.column_config.SelectboxColumn("Grupo", options=C.GRUPOS, default="Otros"),
                "origen": st.column_config.SelectboxColumn("Origen habitual", options=["DIR", "EXT", "AMBOS"], default="AMBOS"),
                "es_curso": st.column_config.CheckboxColumn("Pide datos de curso y personal", default=False),
                "activo": st.column_config.CheckboxColumn("Activo", default=True),
            },
        )
        st.caption("Desactive en lugar de borrar los tipos que ya tienen expedientes cargados.")
        if st.button("💾 Guardar tipos", type="primary"):
            db.guardar_catalogo("tipos_expediente", ed, ["nombre", "grupo", "origen", "es_curso", "activo"])
            st.toast("Tipos guardados", icon="✅")
            st.rerun()

    with t4:
        st.markdown("Descargue periódicamente un respaldo completo de la base (todas las tablas en un Excel).")
        if st.button("📦 Generar respaldo completo"):
            with st.spinner("Generando…"):
                st.session_state["respaldo"] = R.excel(db.respaldo_completo())
        if st.session_state.get("respaldo"):
            st.download_button("📥 Descargar respaldo", st.session_state["respaldo"], file_name=f"respaldo_expedientes_{db.hoy():%Y%m%d}.xlsx")
        ui.seccion("🕵️ Auditoría (últimas 200 acciones)")
        st.dataframe(db.leer("SELECT fecha, usuario, accion, detalle FROM auditoria ORDER BY id DESC LIMIT 200"), hide_index=True, width="stretch")


def _drive(cfg):
    import gdrive

    if not gdrive.configurado():
        st.warning("Faltan las credenciales de Google en los Secrets de Streamlit.")
        st.markdown(
            "En Streamlit Cloud: **Manage app → ⋮ → Settings → Secrets**, agregue estas dos líneas debajo de las existentes "
            "(con los datos del cliente OAuth *App de escritorio* de Google Cloud) y guarde:"
        )
        st.code('GDRIVE_CLIENT_ID = "xxxxxxxx.apps.googleusercontent.com"\nGDRIVE_CLIENT_SECRET = "GOCSPX-xxxxxxxx"', language="toml")
        return

    with st.form("gd_carpeta"):
        fid = st.text_input("ID de la carpeta de Drive donde guardar los expedientes", cfg.get("gdrive_folder_id", ""),
                            help="Es lo que aparece en el link de la carpeta después de /folders/")
        if st.form_submit_button("💾 Guardar carpeta"):
            db.set_config({"gdrive_folder_id": fid.strip(), "gdrive_raiz_id": ""})
            st.toast("Carpeta guardada", icon="📁")
            st.rerun()

    if gdrive.conectado():
        ui.alerta("✅", "Google Drive conectado", "Los PDF se guardan en la carpeta 'EXPEDIENTES DGII - SISTEMA', con subcarpetas por año.", C.STATUS["ok"])
        c1, c2 = st.columns(2)
        if c1.button("🔎 Probar conexión"):
            try:
                link = gdrive.probar()
                st.success("Conexión correcta.")
                st.link_button("📁 Abrir carpeta en Drive", link)
                if db.get_config().get("gdrive_raiz_en_carpeta") == "NO":
                    st.info("Por el permiso mínimo de Google, la app creó su carpeta en 'Mi unidad'. "
                            "Si querés, arrastrala dentro de tu carpeta: la app la sigue encontrando igual.")
            except gdrive.DriveError as e:
                st.error(str(e))
        if c2.button("⛔ Desconectar Drive"):
            gdrive.desconectar()
            st.rerun()
        return

    st.markdown("**Conectar con Google Drive (una sola vez)**")
    st.markdown("1. Tocá el botón y aceptá con tu cuenta de Google. Si aparece *Google no verificó esta app*, "
                "tocá **Configuración avanzada → Ir a … (no seguro)** y luego **Continuar**.")
    st.link_button("🔐 Autorizar con Google", gdrive.url_autorizacion())
    st.markdown("2. Al terminar, el navegador va a una página que **no carga** (`localhost`). Es normal: "
                "**copiá la dirección completa** de esa pestaña y pegala acá:")
    with st.form("gd_codigo", clear_on_submit=True):
        url = st.text_input("Dirección completa (empieza con http://localhost/?...code=...)")
        if st.form_submit_button("✅ Conectar"):
            try:
                gdrive.canjear_codigo(url)
                gdrive.carpeta_raiz()
                st.toast("Google Drive conectado", icon="☁️")
                st.rerun()
            except gdrive.DriveError as e:
                st.error(str(e))


def _usuarios():
    import auth

    df = auth.df_usuarios()
    yo = auth.actual()
    act = df[df["activo"]]
    ui.kpis([
        ("Usuarios habilitados", len(act), f"{len(df) - len(act)} deshabilitados", "#3B82F6"),
        ("Oficiales", int((act["rol"] == "OFICIAL").sum()), "cargan y tramitan", C.PALETA[2]),
        ("Suboficiales", int((act["rol"] == "SUBOFICIAL").sum()), "cargan expedientes", C.PALETA[3]),
        ("Administradores", int((act["rol"] == "ADMINISTRADOR").sum()), "configuración", C.PALETA[0]),
    ])
    st.markdown(" · ".join(f"**{r}**: {d}" for r, d in auth.DESCRIPCION_ROL.items()))
    tabla = pd.DataFrame({
        "Legajo": df["legajo"], "Grado": df["grado"], "Apellido": df["apellido"], "Nombre": df["nombre"],
        "Función": df["funcion"], "Rol": df["rol"], "Habilitado": df["activo"].map({True: "✅ SÍ", False: "⛔ NO"}),
        "Último acceso": df["ultimo_acceso"].dt.strftime("%d/%m/%Y %H:%M"),
    })
    st.dataframe(tabla, hide_index=True, width="stretch")
    st.download_button("📥 Listado de usuarios (Excel)", R.excel({"Usuarios habilitados": tabla}), file_name="usuarios_expedientes.xlsx")

    c1, c2 = st.columns(2)
    with c1:
        ui.seccion("➕ Nuevo usuario")
        with st.form("nuevo_usuario", clear_on_submit=True):
            a, b = st.columns(2)
            grado = a.selectbox("Grado", C.GRADOS_USUARIO)
            legajo = b.text_input("Legajo (usuario para ingresar)")
            apellido = a.text_input("Apellido")
            nombre = b.text_input("Nombre")
            funcion = st.text_input("Función", placeholder="Ej: AUXILIAR DE MESA DE ENTRADAS")
            rol = st.selectbox("Rol", ["(según grado)"] + auth.ROLES,
                               help="Según grado: oficiales → OFICIAL (tramitan); suboficiales → SUBOFICIAL (cargan)")
            clave = st.text_input("Clave inicial (mín. 6)", type="password",
                                  help="El usuario deberá cambiarla en su primer ingreso")
            if st.form_submit_button("➕ Crear usuario"):
                try:
                    r_final = auth.rol_por_grado(grado) if rol == "(según grado)" else rol
                    auth.crear_usuario(legajo, grado, apellido, nombre, funcion, r_final, clave, K.usuario())
                    st.success(f"Usuario creado como {r_final}.")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
    with c2:
        ui.seccion("✏️ Modificar usuario")
        if df.empty:
            return
        opc = {int(r["id"]): f"{r['legajo']} · {r['grado'] or ''} {r['apellido']} {r['nombre'] or ''}" for _, r in df.iterrows()}
        uid = st.selectbox("Usuario", list(opc), format_func=opc.get, key="usr_sel")
        u = df[df["id"] == uid].iloc[0]
        with st.form(f"edit_usr_{uid}"):
            a, b = st.columns(2)
            grados = C.GRADOS_USUARIO + ([u["grado"]] if u["grado"] and u["grado"] not in C.GRADOS_USUARIO else [])
            grado = a.selectbox("Grado", grados, index=K.idx(grados, u["grado"]))
            rol = b.selectbox("Rol", auth.ROLES, index=K.idx(auth.ROLES, u["rol"]))
            apellido = a.text_input("Apellido", u["apellido"] or "")
            nombre = b.text_input("Nombre", u["nombre"] or "")
            funcion = st.text_input("Función", u["funcion"] or "")
            activo = st.checkbox("Habilitado", bool(u["activo"]))
            nueva = st.text_input("Nueva clave (dejar vacío para no cambiarla)", type="password")
            if st.form_submit_button("💾 Guardar"):
                es_yo = yo and int(yo["id"]) == int(uid)
                admins = int(((df["rol"] == "ADMINISTRADOR") & df["activo"]).sum())
                if es_yo and (rol != "ADMINISTRADOR" or not activo) and admins <= 1:
                    st.error("No puede quitarse el rol de administrador ni deshabilitarse: es el único administrador.")
                else:
                    try:
                        auth.actualizar_usuario(int(uid), {"grado": grado, "rol": rol, "apellido": apellido.strip().upper(),
                                                           "nombre": nombre.strip().title(), "funcion": funcion.strip().upper() or None,
                                                           "activo": activo}, K.usuario())
                        if nueva:
                            auth.cambiar_clave(int(uid), nueva, K.usuario(), forzar_cambio=not es_yo)
                        st.success("Usuario actualizado.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))


def _tramitacion(cfg):
    """Firmante, destino de las elevaciones, libreta de autoridades e IA de redacción."""
    import redaccion

    aut = db.df_autoridades(False)
    sup = aut[aut["relacion"] == "SUPERIOR"]
    ui.seccion("✍️ Firma y elevaciones")
    with st.form("cfg_tram"):
        c1, c2 = st.columns(2)
        claves = sup["clave"].tolist() or ["SUBJEFE"]
        etiqueta = dict(zip(aut["clave"], aut["cargo"]))
        elevar = c1.selectbox("Las elevaciones van a", claves, index=claves.index(cfg.get("elevar_a")) if cfg.get("elevar_a") in claves else 0,
                              format_func=lambda k: etiqueta.get(k, k), help="Depende de la gestión: Jefatura o Subjefatura de Policía")
        c2.caption("La secretaría de la referencia se configura por libro en «📖 Libro y alertas».")
        c3, c4 = st.columns(2)
        fn = c3.text_input("Firmante (grado y nombre)", cfg.get("firmante_nombre") or "", placeholder="Crio. Insp. APELLIDO NOMBRE")
        fc = c4.text_input("Cargo del firmante", cfg.get("firmante_cargo") or "")
        car = st.text_area("Fórmula «en mi carácter de…»", cfg.get("firmante_caracter") or "", height=70)
        lema = st.text_input("Pie de página de los documentos", cfg.get("doc_lema") or "")
        ia_pers = st.toggle("Permitir IA (Gemini) en documentos con datos personales (sumarios, oficios, notificaciones)",
                            value=cfg.get("ia_datos_personales") == "SI",
                            help="En el nivel gratuito, Google puede usar lo enviado para mejorar sus productos. Recomendado: desactivado.")
        if st.form_submit_button("💾 Guardar"):
            db.set_config({"elevar_a": elevar, "firmante_nombre": fn.strip(), "firmante_cargo": fc.strip(),
                           "firmante_caracter": car.strip(), "doc_lema": lema.strip(),
                           "ia_datos_personales": "SI" if ia_pers else "NO"})
            st.toast("Configuración de notas guardada", icon="✅")
            st.rerun()

    ui.seccion("📇 Libreta de autoridades")
    st.caption("Destinatarios de las notas. **Relación** define el verbo: SUPERIOR → *elevo*, PAR → *remito*, INTERNO → *pase*. "
               "Actualice los titulares cuando cambia la gestión.")
    if "dependencia" not in aut.columns:
        aut["dependencia"] = None
    ed = st.data_editor(
        aut[["clave", "tratamiento", "cargo", "titular", "saludo", "relacion", "dependencia", "activa"]], num_rows="dynamic", width="stretch", hide_index=True,
        key="ed_aut",
        column_config={
            "clave": st.column_config.TextColumn("Clave", help="Identificador corto, sin espacios (ej. ESC_SUPERIOR)"),
            "tratamiento": st.column_config.SelectboxColumn("Tratamiento", options=["Al Señor", "Señor", "Señora", "A la Señora"]),
            "cargo": st.column_config.TextColumn("Cargo", width="large"),
            "titular": st.column_config.TextColumn("Grado y nombre del titular", width="medium"),
            "saludo": st.column_config.SelectboxColumn("Su …", options=["Despacho", "Oficina"]),
            "relacion": st.column_config.SelectboxColumn("Relación", options=C.RELACIONES_AUT),
            "dependencia": st.column_config.SelectboxColumn("El comisionista lo lleva a", options=[d for d in K.deps() if d != C.DEP_PROPIA],
                                                            help="Se completa solo la primera vez que encarga una entrega a esa autoridad"),
            "activa": st.column_config.CheckboxColumn("Activa"),
        })
    if st.button("💾 Guardar autoridades"):
        db.guardar_autoridades(ed, K.usuario())
        st.toast("Autoridades actualizadas", icon="✅")
        st.rerun()

    ui.seccion("✨ Ayuda de redacción (gratuita)")
    st.markdown(
        "- **Diccionario propio** de errores frecuentes: siempre activo, no envía datos.\n"
        "- **LanguageTool**: ortografía y gramática, gratis (hasta ~20 revisiones por minuto).\n"
        f"- **Google Gemini**: mejora de redacción · {'✅ configurado' if redaccion.gemini_disponible() else '⚪ sin configurar'}. "
        "Mejora la redacción y **lee las fotos de las fojas** para proponer el fundamento y demás textos. "
        "Por defecto solo en notas sin datos personales.")
    if not redaccion.gemini_disponible():
        with st.expander("Cómo activar Gemini (gratis)"):
            st.markdown("1. Entre a **aistudio.google.com** con una cuenta de Google y toque **Get API key → Create API key**.\n"
                        "2. En Streamlit: **Manage app → Settings → Secrets**, agregue una línea:\n\n"
                        "```toml\nGEMINI_API_KEY = \"su-clave\"\n```\n"
                        "3. Guarde: la app se reinicia sola. No pegue la clave en ningún chat.")


def _avisos(cfg):
    """Avisos automáticos (Telegram o WhatsApp) a los oficiales cuando se carga o reingresa un expediente."""
    import avisos as AV

    listo, expl = AV.estado(cfg)
    ui.alerta("✅" if listo else "⚙️", "Avisos automáticos " + ("ACTIVOS" if listo else "sin activar"), expl,
              C.STATUS["ok"] if listo else C.STATUS["warning"])
    nombres = {"DESACTIVADO": "Desactivado", "TELEGRAM": "Telegram (gratis)", "TEXTMEBOT": "WhatsApp común (TextMeBot)",
               "CALLMEBOT": "WhatsApp (CallMeBot)", "META": "WhatsApp Business (Meta)"}
    prov = st.radio("¿Por dónde se envían?", AV.PROVEEDORES, index=AV.PROVEEDORES.index(cfg.get("wa_proveedor") or "DESACTIVADO"),
                    horizontal=True, format_func=nombres.get, key="av_prov")
    if prov == "TELEGRAM":
        bot = AV.nombre_bot()
        if bot:
            st.markdown(f"🤖 Bot conectado: **@{bot}** · Cada oficial abre **t.me/{bot}** y toca **Iniciar** (o escribe /start).")
        if st.button("🔎 Buscar oficiales que escribieron al bot", key="av_buscar"):
            try:
                st.session_state["av_chats"] = AV.buscar_chats()
            except Exception as e:
                st.error(str(e))
        chats = st.session_state.get("av_chats")
        if chats is not None:
            if not chats:
                st.info("Todavía nadie escribió al bot. Pida a cada oficial que lo abra y toque «Iniciar», y vuelva a buscar.")
            actuales = str(cfg.get("tg_destinos") or "")
            for n, i in chats:
                c1, c2 = st.columns([3, 1], vertical_alignment="center")
                c1.markdown(f"**{n or 'Sin nombre'}** · id `{i}`" + (" · ✅ ya agregado" if i in actuales else ""))
                if i not in actuales and c2.button("➕ Agregar", key=f"av_add_{i}"):
                    db.set_config({"tg_destinos": (actuales.strip() + f"\n{n.upper()} | {i}").strip()})
                    st.session_state.pop("av_chats", None)
                    st.rerun()
    with st.form("cfg_avisos"):
        if prov == "TELEGRAM":
            dest = st.text_area("Oficiales que reciben el aviso (Nombre | id de Telegram)", cfg.get("tg_destinos") or "", height=90,
                                help="Se completa solo con «Buscar oficiales». Para quitar a alguien, borre su línea.")
        elif prov != "DESACTIVADO":
            dest = st.text_area("Oficiales que reciben el aviso (uno por línea: Nombre | número)", cfg.get("wa_destinos") or "", height=90,
                                placeholder="OF. AUX. ALVAREZ | 381 512-3456")
        else:
            dest = None
        ev = st.multiselect("¿Cuándo avisar?", list(AV.EVENTOS), default=[e for e in AV.eventos_activos(cfg) if e in AV.EVENTOS],
                            format_func=AV.EVENTOS.get)
        plant, idioma = cfg.get("wa_plantilla") or "aviso_expediente", cfg.get("wa_idioma") or "es_AR"
        if prov == "META":
            c1, c2 = st.columns(2)
            plant = c1.text_input("Plantilla aprobada en Meta", plant)
            idioma = c2.text_input("Idioma de la plantilla", idioma)
        if st.form_submit_button("💾 Guardar avisos", type="primary"):
            val = {"wa_proveedor": prov, "wa_eventos": ",".join(ev), "wa_plantilla": plant.strip(), "wa_idioma": idioma.strip()}
            if dest is not None:
                val["tg_destinos" if prov == "TELEGRAM" else "wa_destinos"] = dest.strip()
            db.set_config(val)
            st.toast("Avisos guardados", icon="📲")
            st.rerun()
    if listo and st.button("📤 Enviar un aviso de prueba ahora"):
        r = AV.enviar(["Aviso de PRUEBA", "000/0/0 (2026)", "PRUEBA", "Mensaje de prueba del sistema", "DIRECCIÓN", K.usuario()], esperar=True)
        for d, ok, det in r:
            (st.success if ok else st.error)(f"{d}: {det}")

    with st.expander("📘 Cómo activar Telegram (gratis, 5 minutos)", expanded=prov == "TELEGRAM" and not listo):
        st.markdown(f"""
1. En Telegram abra **@BotFather** → escriba `/newbot`.
2. Nombre: **{AV.NOMBRE}** · usuario: por ejemplo `ExpedientesDGII_bot` (debe terminar en *bot*).
3. BotFather le da un **token**. En Streamlit Cloud → *Settings → Secrets* agregue `TELEGRAM_BOT_TOKEN = "…"` (no lo pegue en el chat ni en otro lado).
4. Opcional: `/setuserpic` para ponerle el logo de la Dirección.
5. Cada oficial instala Telegram, abre el bot y toca **Iniciar**.
6. Aquí: elija **Telegram**, toque **Buscar oficiales**, **➕ Agregar** a cada uno, **Guardar** y **Enviar un aviso de prueba**.
""")
    with st.expander("📘 Otras opciones por WhatsApp"):
        st.markdown(f"""
- **WhatsApp común (TextMeBot):** un WhatsApp del sistema vinculado por QR en textmebot.com; secret `TEXTMEBOT_KEY`. Pago mensual bajo; el teléfono debe quedar encendido.
- **CallMeBot:** gratis, uso personal; cada oficial obtiene su apikey; secret `CALLMEBOT_KEYS = "549381…:clave,…"`.
- **WhatsApp Business (Meta):** número propio con nombre «{AV.NOMBRE}», plantilla aprobada; secrets `WA_TOKEN` y `WA_PHONE_ID`. Costo por mensaje.
""")
