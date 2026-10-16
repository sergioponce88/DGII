import re

import streamlit as st

import catalogos as C
import db
import reportes as R
import ui


def render():
    ui.header("Configuración", "Libro, alertas, dependencias, tipos de expediente y respaldo")
    cfg = db.get_config()
    t1, t2, t3, t4 = st.tabs(["📖 Libro y alertas", "🏢 Dependencias y colores", "🗂️ Tipos de expediente", "💾 Respaldo y auditoría"])

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
