import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import catalogos as C
import comun as K
import db
import reportes as R
import ui
from vistas.v_ficha import _datos_curso

FASE_COLOR = {
    "SOLICITADO": C.PALETA[3],
    "PREVISTO": C.PALETA[6],
    "AUTORIZADO": C.PALETA[0],
    "EN CURSO": C.PALETA[2],
    "REALIZADO": C.STATUS["ok"],
    "NO AUTORIZADO": C.STATUS["critical"],
    "SUSPENDIDO": "#64748B",
    "VENCIDO SIN AUTORIZAR": C.STATUS["serious"],
}


def _tabla_cursos(cur):
    return pd.DataFrame(
        {
            "Exp.": cur["identificador"].fillna("Planificación"),
            "Curso / actividad": cur["nombre"],
            "Categoría": cur["categoria"],
            "Dicta": cur["division_dicta"],
            "Lugar": cur["lugar"],
            "Ámbito": cur["ambito"],
            "Modalidad": cur["modalidad"],
            "Inicio": cur["fecha_inicio"].dt.strftime("%d/%m/%Y"),
            "Fin": cur["fecha_fin"].dt.strftime("%d/%m/%Y"),
            "Requerimiento": cur["requerimiento"],
            "Estado": cur["estado"],
            "Fase": cur["fase"],
            "Efectivos": cur["cant_personal"],
        }
    )


def _tabla_personal(p):
    return pd.DataFrame(
        {
            "Apellido": p["apellido"], "Nombre": p["nombre"], "Jerarquía": p["jerarquia"], "Escalafón": p["escalafon"],
            "DNI": p["dni"], "División": p["division"], "Provincia": p["provincia"], "Rol": p["rol"],
            "Curso": p["curso"], "Ámbito": p["ambito"], "Inicio": p["fecha_inicio"].dt.strftime("%d/%m/%Y"),
            "Fin": p["fecha_fin"].dt.strftime("%d/%m/%Y"), "Requerimiento": p["requerimiento"], "Exp.": p["identificador"],
        }
    )


def estadisticas_cursos(cur, pers):
    """Indicadores pedidos por la Dirección. Devuelve (kpis, tablas)."""
    realizados = cur[cur["fase"] == "REALIZADO"]
    autorizados = cur[cur["estado"] == "AUTORIZADO"]
    cursantes = pers[pers["rol"] == "CURSANTE"]
    fuera = cursantes[(cursantes["ambito"] == "FUERA DE LA PROVINCIA") & (cursantes["provincia"] == "TUCUMÁN")]
    otra_prov = cursantes[(cursantes["ambito"] == "EN LA PROVINCIA") & (cursantes["provincia"] != "TUCUMÁN")]
    of = int((cursantes["escalafon"] == "OFICIAL").sum())
    sub = int((cursantes["escalafon"] == "SUBOFICIAL").sum())
    viat = cur[cur["requerimiento"].fillna("").str.contains("VIÁTICO")]
    mov = cur[cur["requerimiento"].fillna("").str.contains("MOVILIDAD")]
    kp = [
        ("Cursos autorizados", len(autorizados), f"{len(realizados)} ya realizados", C.PALETA[0]),
        ("Personal fuera de la provincia", len(fuera), "efectivos de Tucumán cursando afuera", C.PALETA[1]),
        ("Oficiales en cursos", of, "cursantes", C.PALETA[2]),
        ("Suboficiales en cursos", sub, "cursantes", C.PALETA[3]),
        ("De otras provincias", len(otra_prov), "cursando en Tucumán", C.PALETA[4]),
        ("Con viático / movilidad", f"{len(viat)} / {len(mov)}", "cursos que lo requieren", C.PALETA[6]),
    ]
    tablas = {
        "Cursos autorizados realizados": _tabla_cursos(realizados),
        "Personal fuera de la provincia": _tabla_personal(fuera),
        "Personal de otras provincias": _tabla_personal(otra_prov),
        "Oficiales y suboficiales": cursantes.groupby(["escalafon", "jerarquia"]).size().reset_index(name="Cantidad")
        .rename(columns={"escalafon": "Escalafón", "jerarquia": "Jerarquía"}),
    }
    return kp, tablas


def render():
    ui.header("Cursos y Personal", "Autorizaciones, disertaciones, planificación anual y estadística")
    cur = db.df_cursos()
    pers = db.df_personal()
    anios = sorted({d.year for d in cur["fecha_inicio"].dropna()} | {db.hoy().year}, reverse=True)
    c1, c2 = st.columns([1, 3])
    anio = c1.selectbox("Año", ["Todos"] + anios, index=1, key="cur_anio")
    if anio != "Todos":
        cur = cur[(cur["fecha_inicio"].dt.year == anio) | cur["fecha_inicio"].isna()]
        pers = pers[(pers["fecha_inicio"].dt.year == anio) | pers["fecha_inicio"].isna()]

    t1, t2, t3, t4 = st.tabs(["📊 Estadística", "🎓 Cursos", "👮 Personal", "🗓️ Planificación anual"])

    with t1:
        if cur.empty:
            st.info("Sin cursos registrados para el período.")
        else:
            kp, tablas = estadisticas_cursos(cur, pers)
            ui.kpis(kp)
            g1, g2 = st.columns(2)
            with g1:
                fz = cur["fase"].value_counts()
                fig = go.Figure(go.Bar(x=fz.values, y=fz.index, orientation="h",
                                       marker=dict(color=[FASE_COLOR.get(f, "#64748B") for f in fz.index], cornerradius=4),
                                       text=fz.values, textposition="outside", textfont=dict(color=ui.INK_2),
                                       hovertemplate="%{y}: %{x}<extra></extra>"))
                fig.update_layout(title="Cursos por fase", yaxis=dict(autorange="reversed"), xaxis=dict(visible=False))
                ui.plot(fig, 300)
            with g2:
                cs = pers[pers["rol"] == "CURSANTE"]
                if not cs.empty:
                    pv = cs.groupby(["ambito", "escalafon"]).size().reset_index(name="n")
                    fig = px.bar(pv, x="ambito", y="n", color="escalafon", barmode="group",
                                 color_discrete_map={"OFICIAL": C.PALETA[0], "SUBOFICIAL": C.PALETA[1], "OTRO": "#64748B"},
                                 labels={"ambito": "", "n": "Efectivos", "escalafon": "Escalafón"})
                    fig.update_traces(marker_cornerradius=4, hovertemplate="%{x}<br>%{y} efectivos<extra>%{fullData.name}</extra>")
                    fig.update_layout(title="Oficiales y suboficiales por ámbito")
                    ui.plot(fig, 300)
            g3, g4 = st.columns(2)
            with g3:
                rq = cur["requerimiento"].fillna("SIN DATO").value_counts()
                fig = go.Figure(go.Bar(x=rq.values, y=rq.index, orientation="h", marker=dict(color=C.PALETA[3], cornerradius=4),
                                       text=rq.values, textposition="outside", textfont=dict(color=ui.INK_2),
                                       hovertemplate="%{y}: %{x}<extra></extra>"))
                fig.update_layout(title="Qué se solicitó", yaxis=dict(autorange="reversed"), xaxis=dict(visible=False))
                ui.plot(fig, 280)
            with g4:
                pr = pers[pers["provincia"] != "TUCUMÁN"]["provincia"].value_counts()
                if pr.empty:
                    st.caption("Sin personal de otras provincias.")
                else:
                    fig = go.Figure(go.Bar(x=pr.values, y=pr.index, orientation="h", marker=dict(color=C.PALETA[4], cornerradius=4),
                                           text=pr.values, textposition="outside", textfont=dict(color=ui.INK_2)))
                    fig.update_layout(title="Personal de otras provincias / fuerzas", yaxis=dict(autorange="reversed"), xaxis=dict(visible=False))
                    ui.plot(fig, 280)
            for nom, df in tablas.items():
                with st.expander(f"{nom} ({len(df)})"):
                    st.dataframe(df, hide_index=True, width="stretch")
            st.download_button("📥 Estadística de cursos (Excel)",
                               R.excel({"Cursos": _tabla_cursos(cur), "Personal": _tabla_personal(pers), **tablas}),
                               file_name=f"estadistica_cursos_{anio}.xlsx")
            st.download_button("🖨️ Estadística de cursos (PDF)",
                               R.pdf_informe(f"ESTADÍSTICA DE CURSOS · {anio}", str(anio), [(k, v) for k, v, *_ in kp],
                                             [(n, d) for n, d in tablas.items()], K.LOGO),
                               file_name=f"estadistica_cursos_{anio}.pdf", mime="application/pdf")

    with t2:
        if cur.empty:
            st.info("Sin cursos.")
        else:
            f1, f2, f3 = st.columns(3)
            cat = f1.multiselect("Categoría", C.CATEGORIAS_CURSO)
            amb = f2.multiselect("Ámbito", C.AMBITOS)
            fas = f3.multiselect("Fase", list(FASE_COLOR))
            cf = cur
            if cat:
                cf = cf[cf["categoria"].isin(cat)]
            if amb:
                cf = cf[cf["ambito"].isin(amb)]
            if fas:
                cf = cf[cf["fase"].isin(fas)]
            tb = _tabla_cursos(cf)
            st.dataframe(tb.style.apply(lambda col: [f"color:{FASE_COLOR.get(v, '#CBD5E1')};font-weight:700" for v in col]
                                        if col.name == "Fase" else [""] * len(col), axis=0),
                         hide_index=True, width="stretch")
            st.download_button("📥 Exportar cursos", R.excel({"Cursos": tb}), file_name="cursos.xlsx")

    with t3:
        q = st.text_input("Buscar por apellido o DNI", key="pers_q")
        pf = pers
        if q:
            ql = q.strip().lower()
            pf = pf[(pf["apellido"].fillna("").str.lower().str.contains(ql, regex=False)) | (pf["dni"].fillna("").str.contains(ql, regex=False))]
        e1, e2 = st.columns(2)
        esc = e1.multiselect("Escalafón", ["OFICIAL", "SUBOFICIAL", "OTRO"])
        rol = e2.multiselect("Rol", C.ROLES_PERSONAL)
        if esc:
            pf = pf[pf["escalafon"].isin(esc)]
        if rol:
            pf = pf[pf["rol"].isin(rol)]
        st.caption(f"{len(pf)} registros · {pf['dni'].nunique()} personas distintas")
        st.dataframe(_tabla_personal(pf), hide_index=True, width="stretch")
        st.download_button("📥 Exportar personal", R.excel({"Personal en cursos": _tabla_personal(pf)}), file_name="personal_cursos.xlsx")

    with t4:
        gc = cur.dropna(subset=["fecha_inicio"]).copy()
        if gc.empty:
            st.info("No hay cursos con fecha de inicio para graficar.")
        else:
            gc["fin_g"] = gc["fecha_fin"].fillna(gc["fecha_inicio"]) + pd.Timedelta(days=1)
            solo_plan = st.toggle("Solo cursos de la planificación anual", value=False)
            if solo_plan:
                gc = gc[gc["planificacion_anual"].astype(bool)]
            gc = gc.sort_values("fecha_inicio")
            fig = px.timeline(gc, x_start="fecha_inicio", x_end="fin_g", y="nombre", color="fase",
                              color_discrete_map=FASE_COLOR, hover_data={"lugar": True, "modalidad": True, "cant_personal": True, "fin_g": False})
            fig.update_yaxes(autorange="reversed", title=None, tickfont=dict(size=10))
            fig.add_vline(x=str(db.hoy()), line_width=2, line_dash="dot", line_color=C.STATUS["warning"])
            fig.update_layout(title=f"Planificación de cursos · {anio}", legend_title_text="")
            ui.plot(fig, max(320, 30 * len(gc) + 120))
        ui.seccion("➕ Agregar curso a la planificación (sin expediente)")
        _datos_curso(None, "plan_nuevo", None)
