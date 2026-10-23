import pandas as pd
import streamlit as st

import catalogos as C
import comun as K
import db
import reportes as R
import ui


def filtrar(exp, key):
    with st.expander("🔍 Filtros", expanded=True):
        secs = st.segmented_control("📖 Libro", ["Ambos"] + list(C.SECRETARIAS), default="Ambos", key=f"{key}_sec",
                                    format_func=lambda k: k if k == "Ambos" else C.SECRETARIAS[k]["sigla"])
        c1, c2, c3 = st.columns([2, 1, 1])
        texto = c1.text_input("Buscar (N°, asunto, iniciador, N° origen)", key=f"{key}_txt")
        anios = sorted(exp["anio"].dropna().astype(int).unique().tolist(), reverse=True)
        anio = c2.selectbox("Año", ["Todos"] + anios, key=f"{key}_anio")
        prio = c3.selectbox("Prioridad", ["Todas"] + C.PRIORIDADES, key=f"{key}_prio")
        c4, c5, c6, c7 = st.columns(4)
        tipos = c4.multiselect("Tipo", sorted(exp["tipo"].dropna().unique()), key=f"{key}_tipo")
        estados = c5.multiselect("Estado", C.ESTADOS, key=f"{key}_est")
        origen = c6.multiselect("Dependencia de origen", sorted(exp["dependencia_origen"].dropna().unique()), key=f"{key}_org")
        ubic = c7.multiselect("Ubicación actual", sorted(exp["ubicacion_actual"].dropna().unique()), key=f"{key}_ub")
        dest = st.multiselect("🎯 Instancia de destino", sorted(exp["destino"].dropna().unique()), key=f"{key}_dest")
        c8, c9, c10 = st.columns(3)
        desde = c8.date_input("Ingreso desde", value=None, format="DD/MM/YYYY", key=f"{key}_d")
        hasta = c9.date_input("Ingreso hasta", value=None, format="DD/MM/YYYY", key=f"{key}_h")
        tram = c10.selectbox("Trámite", ["Todos", "⏳ Pendientes de trámite", "✅ Tramitados"], key=f"{key}_tram")
    df = exp
    if secs and secs != "Ambos":
        df = df[df["secretaria"].fillna(C.SEC_DEFAULT) == secs]
    if texto:
        t = texto.strip().lower()
        blob = (df["identificador"].astype(str) + " " + df["asunto"].fillna("") + " " + df["iniciador"].fillna("") + " "
                + df["nro_exp_origen"].fillna("") + " " + df["tipo"].fillna("")).str.lower()
        df = df[blob.str.contains(t, regex=False)]
    if anio != "Todos":
        df = df[df["anio"] == anio]
    if prio != "Todas":
        df = df[df["prioridad"] == prio]
    if tipos:
        df = df[df["tipo"].isin(tipos)]
    if estados:
        df = df[df["estado"].isin(estados)]
    if origen:
        df = df[df["dependencia_origen"].isin(origen)]
    if ubic:
        df = df[df["ubicacion_actual"].isin(ubic)]
    if dest:
        df = df[df["destino"].isin(dest)]
    if tram.startswith("⏳"):
        df = df[~df["tramitado"] & ~df["estado"].isin(C.ESTADOS_CERRADOS)]
    elif tram.startswith("✅"):
        df = df[df["tramitado"]]
    if desde:
        df = df[df["fecha_ingreso"] >= pd.Timestamp(desde)]
    if hasta:
        df = df[df["fecha_ingreso"] <= pd.Timestamp(hasta)]
    return df


def tabla_libro(df):
    return pd.DataFrame(
        {
            "Libro de": df["secretaria"].fillna(C.SEC_DEFAULT).map(lambda s: C.SECRETARIAS[C.sec_de(s)]["sigla"]),
            "N° Exp/Folio/Orden": df["identificador"],
            "Año": df["anio"],
            "Libro": df["libro"],
            "Ingreso": df["fecha_ingreso"].dt.strftime("%d/%m/%Y"),
            "Tipo": df["tipo"],
            "Asunto": df["asunto"],
            "Origen": df["dependencia_origen"],
            "Iniciador": df["iniciador"],
            "Prioridad": df["prioridad"],
            "Estado": df["estado"],
            "Tramitado": df["tramitado"].map({True: "✅ SÍ", False: "⏳ NO"}),
            "Fecha trámite": df["fecha_tramite"].dt.strftime("%d/%m/%Y %H:%M"),
            "Despacho": df["despacho"],
            "Ubicación": df["ubicacion_actual"],
            "Destino": df["destino"],
            "Últ. movimiento": df["ult_mov"].dt.strftime("%d/%m/%Y %H:%M"),
            "Movs.": df["cant_mov"],
            "PDF": df["pdf_link"],
        }
    )


COLCFG = {"PDF": st.column_config.LinkColumn("PDF", display_text="📄 Ver")}


def render():
    ui.header("Libro de Registro", "Control integral de expedientes")
    exp = db.df_expedientes()
    if exp.empty:
        st.info("El libro está vacío.")
        return
    df = filtrar(exp, "lib")
    mapa = ui.mapa_dependencias()
    abiertos = df[~df["estado"].isin(C.ESTADOS_CERRADOS)]
    ui.kpis(
        [
            ("Resultado", len(df), "expedientes filtrados", "#3B82F6"),
            ("Abiertos", len(abiertos), "en trámite", C.PALETA[2]),
            ("Urgentes", int((abiertos["prioridad"] == "URGENTE TRÁMITE").sum()), "abiertos", C.STATUS["serious"]),
            ("Pendientes de trámite", int((~abiertos["tramitado"]).sum()), f"{int(df['tramitado'].sum())} tramitados", C.STATUS["warning"]),
            ("Folios", df["folio"].nunique(), "del libro", C.PALETA[6]),
        ]
    )
    vista = st.segmented_control("Vista", ["📋 Tabla", "🗂️ Tarjetas", "📖 Por folio"], default="📋 Tabla", key="lib_vista")
    t = tabla_libro(df)

    if vista == "🗂️ Tarjetas":
        n = st.slider("Mostrar", 5, 100, 20, 5) if len(df) > 5 else len(df)
        for _, r in df.head(n).iterrows():
            ui.tarjeta_expediente(r, mapa)
            if st.button("Abrir ficha", key=f"lib_open_{r['id']}"):
                K.ir_a(K.PAG_FICHA, r["id"])
    elif vista == "📖 Por folio":
        d = df.assign(_sec=df["secretaria"].fillna(C.SEC_DEFAULT))
        for (sec, lib, fol), g in d.sort_values(["_sec", "libro", "folio", "orden"], ascending=[True, False, False, True]).groupby(["_sec", "libro", "folio"], sort=False):
            ui.seccion(f"{C.SECRETARIAS[C.sec_de(sec)]['sigla']} · Libro {lib} · Folio {fol}–{fol + 1}  ({len(g)} asientos)")
            st.dataframe(ui.estilo_tabla(tabla_libro(g).drop(columns=["Libro", "Libro de"]), mapa), hide_index=True, width="stretch", column_config=COLCFG)
    else:
        ev = st.dataframe(
            ui.estilo_tabla(t, mapa),
            column_config=COLCFG,
            hide_index=True,
            width="stretch",
            height=min(700, 38 + 35 * max(1, len(t))),
            on_select="rerun",
            selection_mode="multi-row",
            key="lib_tabla",
        )
        sel = ev.selection.rows if ev and hasattr(ev, "selection") else []
        if len(sel) == 1:
            r = df.iloc[sel[0]]
            st.caption("Expediente seleccionado:")
            ui.tarjeta_expediente(r, mapa)
            if st.button("🔎 Abrir ficha completa", key="lib_abrir"):
                K.ir_a(K.PAG_FICHA, r["id"])
        elif not sel:
            st.caption("💡 Toque una fila para ver el detalle. Seleccione varias para marcarlas como tramitadas juntas.")
        pend = df.iloc[sel] if sel else df.iloc[0:0]
        pend = pend[~pend["tramitado"]]
        import auth

        if len(pend) and auth.puede("tramitar"):
            with st.form("lib_tram_lote", clear_on_submit=True):
                st.markdown(f"**✅ Marcar {len(pend)} expediente(s) como TRAMITADO:** " + ", ".join(pend["identificador"]))
                c1, c2 = st.columns(2)
                acc = c1.selectbox("¿Qué se hizo?", C.ACCIONES_TRAMITE)
                det = c2.text_input("Detalle")
                if st.form_submit_button("✅ Marcar como tramitados"):
                    db.marcar_tramitado([int(i) for i in pend["id"]], acc, det.strip() or None, db.ahora(), K.usuario(), K.usuario())
                    st.toast(f"{len(pend)} expedientes tramitados", icon="✅")
                    st.rerun()

    st.download_button("📥 Exportar a Excel", R.excel({"Libro de expedientes": t}),
                       file_name=f"libro_expedientes_{db.hoy():%Y%m%d}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
