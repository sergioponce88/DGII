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
    tu, t1, t2, t3, t5, t4 = st.tabs(["👥 Usuarios", "📖 Libro y alertas", "🏢 Dependencias y colores", "🗂️ Tipos de expediente", "☁️ Google Drive", "💾 Respaldo y auditoría"])

    with tu:
        _usuarios()

    with t5:
        _drive(cfg)

    with t1:
        with st.form("cfg_libro"):
            st.markdown("**Numeración del libro**")
            c1, c2, c3 = st.columns(3)
            nro_ini = c1.number_input("N° de expediente inicial", 1, value=int(cfg["nro_inicial"]), help="Se usa solo cuando todavía no hay expedientes cargados.")
            fol_ini = c2.number_input("Folio inicial", 1, value=int(cfg["folio_inicial"]))
            libro = c3.number_input("Libro actual", 1, value=int(cfg["libro_actual"]))
            c4, c5, c6 = st.columns(3)
            ren = c4.number_input("Renglones (asientos) por folio", 1, 100, int(cfg["renglones_por_folio"]),
                                  help="Cuando el orden llega a este número, el próximo expediente pasa al siguiente folio con orden 1.")
            paso = c5.selectbox("Avance de folio", [2, 1], index=0 if cfg["paso_folio"] == "2" else 1,
                                help="2 = cada asiento ocupa la doble página (se numera la foja izquierda: 1, 3, 5…). 1 = folio correlativo.")
            rei = c6.selectbox("¿El N° de expediente reinicia cada año?", ["NO", "SI"], index=0 if cfg["reinicio_anual"] == "NO" else 1)
            st.markdown("**Alertas y avisos**")
            a1, a2, a3 = st.columns(3)
            dav = a1.number_input("Avisar inicio de curso (días antes)", 0, 60, int(cfg["dias_aviso_cursos"]))
            dest = a2.number_input("Marcar expediente detenido después de (días)", 1, 365, int(cfg["dias_estancado"]))
            wp = a3.text_input("WhatsApp por defecto (Mesa de Entradas)", cfg.get("wp_por_defecto", ""), placeholder="381 5123456")
            if st.form_submit_button("💾 Guardar configuración"):
                db.set_config(dict(nro_inicial=nro_ini, folio_inicial=fol_ini, libro_actual=libro, renglones_por_folio=ren,
                                   paso_folio=paso, reinicio_anual=rei, dias_aviso_cursos=dav, dias_estancado=dest, wp_por_defecto=wp.strip()))
                st.toast("Configuración guardada", icon="✅")
                st.rerun()
        s = db.sugerir_numeracion()
        st.info(f"Próximo asiento sugerido: **{s['nro_exp']}/{s['folio']}/{s['orden']}** (libro {s['libro']}).")

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
