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
            "Exp.": cur["identificador"].fillna("Sin expediente"),
            "Tipo": cur["tipo_actividad"].fillna("CURSO"),
            "Actividad": cur["nombre"],
            "Hora": cur["hora"],
            "Organiza": cur["organiza"],
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
            "Tipo": p["tipo_actividad"].fillna("CURSO"), "Actividad": p["curso"], "Ámbito": p["ambito"], "Inicio": p["fecha_inicio"].dt.strftime("%d/%m/%Y"),
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
        ("Actividades autorizadas", len(autorizados), f"{len(realizados)} ya realizadas", C.PALETA[0]),
        ("Personal fuera de la provincia", len(fuera), "efectivos de Tucumán cursando afuera", C.PALETA[1]),
        ("Oficiales capacitándose", of, "cursantes", C.PALETA[2]),
        ("Suboficiales capacitándose", sub, "cursantes", C.PALETA[3]),
        ("PTP / Cadetes / Aspirantes", f"{int((pers['escalafon'] == 'PTP').sum())} / {int((pers['escalafon'] == 'CADETE').sum())} / "
         f"{int((pers['escalafon'] == 'ASPIRANTE').sum())}", "personal en formación afectado", C.PALETA[5]),
        ("De otras provincias", len(otra_prov), "cursando en Tucumán", C.PALETA[4]),
        ("Con viático / movilidad", f"{len(viat)} / {len(mov)}", "actividades que lo requieren", C.PALETA[6]),
    ]
    por_tipo = (cur.assign(t=cur["tipo_actividad"].fillna("CURSO"))
                .groupby("t").agg(Actividades=("id", "count"), Efectivos=("cant_personal", "sum")).reset_index()
                .rename(columns={"t": "Tipo de actividad"}).sort_values("Actividades", ascending=False))
    tablas = {
        "Actividades por tipo": por_tipo,
        "Actividades autorizadas realizadas": _tabla_cursos(realizados),
        "Personal fuera de la provincia": _tabla_personal(fuera),
        "Personal de otras provincias": _tabla_personal(otra_prov),
        "Oficiales y suboficiales": cursantes.groupby(["escalafon", "jerarquia"]).size().reset_index(name="Cantidad")
        .rename(columns={"escalafon": "Escalafón", "jerarquia": "Jerarquía"}),
    }
    return kp, tablas


def _tarjeta_act(c):
    col = FASE_COLOR.get(c["fase"], "#64748B")
    tipo = c["tipo_actividad"] if isinstance(c["tipo_actividad"], str) else "CURSO"
    fechas = ui.fmt_fecha(c["fecha_inicio"]) + (f" al {ui.fmt_fecha(c['fecha_fin'])}" if pd.notna(c["fecha_fin"]) and c["fecha_fin"] != c["fecha_inicio"] else "")
    extra = " · ".join(x for x in [c["hora"] if isinstance(c["hora"], str) else "", c["lugar"] if isinstance(c["lugar"], str) else "",
                                   c["modalidad"] if isinstance(c["modalidad"], str) else ""] if x)
    org = c["organiza"] if isinstance(c["organiza"], str) else (c["division_dicta"] if isinstance(c["division_dicta"], str) else "")
    exp = f"Exp. {c['identificador']}" if isinstance(c["identificador"], str) else "Sin expediente"
    st.markdown(
        f"<div class='card acc' style='--c:{col};padding:12px 16px'>"
        f"{ui.chip(tipo, C.PALETA[0], False)}{ui.chip(c['fase'], col)}"
        f"<div style='font-weight:800;font-size:1.05rem;margin-top:6px'>{ui.esc(c['nombre'])}</div>"
        f"<div class='meta'>🗓️ {fechas}{' · ' + ui.esc(extra) if extra else ''}<br>"
        f"{('Organiza: <b>' + ui.esc(org) + '</b> · ') if org else ''}👮 {int(c['cant_personal'] or 0)} efectivos · {ui.esc(exp)}</div></div>",
        unsafe_allow_html=True,
    )


def _que_pasa(cur):
    """Tablero de todo lo que acontece: hoy, esta semana, próximo mes y lo recién terminado."""
    cur = cur.dropna(subset=["fecha_inicio"]).copy()
    cur = cur[~cur["estado"].isin(["NO AUTORIZADO", "SUSPENDIDO"])]
    h = pd.Timestamp(db.hoy())
    fin = cur["fecha_fin"].fillna(cur["fecha_inicio"])
    hoy = cur[(cur["fecha_inicio"] <= h) & (fin >= h)]
    semana = cur[(cur["fecha_inicio"] > h) & (cur["fecha_inicio"] <= h + pd.Timedelta(days=7))]
    mes = cur[(cur["fecha_inicio"] > h + pd.Timedelta(days=7)) & (cur["fecha_inicio"] <= h + pd.Timedelta(days=31))]
    recien = cur[(fin < h) & (fin >= h - pd.Timedelta(days=7))]
    ui.kpis([
        ("En desarrollo hoy", len(hoy), f"{int(hoy['cant_personal'].sum() or 0)} efectivos afectados", C.PALETA[2]),
        ("Próximos 7 días", len(semana), "por iniciar", C.STATUS["warning"]),
        ("Próximo mes", len(mes), "programadas", C.PALETA[0]),
        ("Terminaron esta semana", len(recien), "para cerrar / informar", C.PALETA[6]),
    ])
    for titulo, df, orden in [("🟢 En desarrollo hoy", hoy, "fecha_inicio"), ("🟡 Próximos 7 días", semana, "fecha_inicio"),
                              ("🔵 Próximo mes", mes, "fecha_inicio"), ("⚪ Terminaron en los últimos 7 días", recien, "fecha_fin")]:
        ui.seccion(f"{titulo} ({len(df)})")
        if df.empty:
            st.caption("Nada para mostrar.")
            continue
        cols = st.columns(2)
        for i, (_, c) in enumerate(df.sort_values(orden).iterrows()):
            with cols[i % 2]:
                _tarjeta_act(c)


def render():
    ui.header("Actividades y Personal", "Cursos, formaciones, disertaciones, congresos, eventos y todo lo que acontece")
    cur = db.df_cursos()
    pers = db.df_personal()
    anios = sorted({d.year for d in cur["fecha_inicio"].dropna()} | {db.hoy().year}, reverse=True)
    c1, c2 = st.columns([1, 3])
    anio = c1.selectbox("Año", ["Todos"] + anios, index=1, key="cur_anio")
    tipos_f = c2.multiselect("Tipo de actividad", C.TIPOS_ACTIVIDAD, key="cur_tipos", placeholder="Todas")
    if tipos_f:
        cur = cur[cur["tipo_actividad"].fillna("CURSO").isin(tipos_f)]
        pers = pers[pers["tipo_actividad"].fillna("CURSO").isin(tipos_f)]
    if anio != "Todos":
        cur = cur[(cur["fecha_inicio"].dt.year == anio) | cur["fecha_inicio"].isna()]
        pers = pers[(pers["fecha_inicio"].dt.year == anio) | pers["fecha_inicio"].isna()]

    t0, t5, t1, t2, t3, t4 = st.tabs(["📅 Qué está pasando", "➕ Nueva actividad", "📊 Estadística", "🎓 Actividades",
                                      "👮 Personal", "🗓️ Planificación anual"])

    with t0:
        _que_pasa(db.df_cursos() if not tipos_f else db.df_cursos()[db.df_cursos()["tipo_actividad"].fillna("CURSO").isin(tipos_f)])

    with t5:
        st.caption("Registre cualquier actividad aunque no tenga expediente: formaciones, disertaciones, congresos, actos, "
                   "eventos deportivos, colaboraciones de efectivos, reuniones, visitas…")
        _datos_curso(None, "act_nueva", None)

    with t1:
        if cur.empty:
            st.info("Sin actividades registradas para el período.")
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
                fig.update_layout(title="Actividades por fase", yaxis=dict(autorange="reversed"), xaxis=dict(visible=False))
                ui.plot(fig, 300)
            with g2:
                cs = pers[pers["rol"] == "CURSANTE"]
                if not cs.empty:
                    pv = cs.groupby(["ambito", "escalafon"]).size().reset_index(name="n")
                    fig = px.bar(pv, x="ambito", y="n", color="escalafon", barmode="group",
                                 color_discrete_map={"OFICIAL": C.PALETA[0], "SUBOFICIAL": C.PALETA[1], "PTP": C.PALETA[2],
                                                     "CADETE": C.PALETA[3], "ASPIRANTE": C.PALETA[4], "OTRO": "#64748B"},
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
            pt = tablas["Actividades por tipo"]
            fig = go.Figure(go.Bar(x=pt["Actividades"], y=pt["Tipo de actividad"], orientation="h",
                                   marker=dict(color=C.PALETA[0], cornerradius=4), customdata=pt["Efectivos"],
                                   text=pt["Actividades"], textposition="outside", textfont=dict(color=ui.INK_2),
                                   hovertemplate="%{y}: %{x} actividades · %{customdata} efectivos<extra></extra>"))
            fig.update_layout(title="Actividades por tipo", yaxis=dict(autorange="reversed"), xaxis=dict(visible=False))
            ui.plot(fig, max(260, 34 * len(pt) + 90))
            for nom, df in tablas.items():
                with st.expander(f"{nom} ({len(df)})"):
                    st.dataframe(df, hide_index=True, width="stretch")
            st.download_button("📥 Estadística de cursos (Excel)",
                               R.excel({"Cursos": _tabla_cursos(cur), "Personal": _tabla_personal(pers), **tablas}),
                               file_name=f"estadistica_actividades_{anio}.xlsx")
            st.download_button("🖨️ Estadística de cursos (PDF)",
                               R.pdf_informe(f"ESTADÍSTICA DE ACTIVIDADES · {anio}", str(anio), [(k, v) for k, v, *_ in kp],
                                             [(n, d) for n, d in tablas.items()], K.LOGO),
                               file_name=f"estadistica_actividades_{anio}.pdf", mime="application/pdf")

    with t2:
        if cur.empty:
            st.info("Sin actividades.")
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
            st.download_button("📥 Exportar actividades", R.excel({"Actividades": tb}), file_name="actividades.xlsx")

    with t3:
        q = st.text_input("Buscar por apellido o DNI", key="pers_q")
        pf = pers
        if q:
            ql = q.strip().lower()
            pf = pf[(pf["apellido"].fillna("").str.lower().str.contains(ql, regex=False)) | (pf["dni"].fillna("").str.contains(ql, regex=False))]
        e1, e2 = st.columns(2)
        esc = e1.multiselect("Escalafón", C.ESCALAFONES)
        rol = e2.multiselect("Rol", C.ROLES_PERSONAL)
        if esc:
            pf = pf[pf["escalafon"].isin(esc)]
        if rol:
            pf = pf[pf["rol"].isin(rol)]
        st.caption(f"{len(pf)} registros · {pf['dni'].nunique()} personas distintas")
        st.dataframe(_tabla_personal(pf), hide_index=True, width="stretch")
        st.download_button("📥 Exportar personal", R.excel({"Personal en actividades": _tabla_personal(pf)}), file_name="personal_actividades.xlsx")

    with t4:
        gc = cur.dropna(subset=["fecha_inicio"]).copy()
        if gc.empty:
            st.info("No hay actividades con fecha de inicio para graficar.")
        else:
            gc["fin_g"] = gc["fecha_fin"].fillna(gc["fecha_inicio"]) + pd.Timedelta(days=1)
            solo_plan = st.toggle("Solo actividades de la planificación anual", value=False)
            if solo_plan:
                gc = gc[gc["planificacion_anual"].astype(bool)]
            gc = gc.sort_values("fecha_inicio")
            gc["etiqueta"] = gc["tipo_actividad"].fillna("CURSO") + " · " + gc["nombre"]
            fig = px.timeline(gc, x_start="fecha_inicio", x_end="fin_g", y="etiqueta", color="fase",
                              color_discrete_map=FASE_COLOR, hover_data={"lugar": True, "modalidad": True, "cant_personal": True, "fin_g": False})
            fig.update_yaxes(autorange="reversed", title=None, tickfont=dict(size=10))
            fig.add_vline(x=str(db.hoy()), line_width=2, line_dash="dot", line_color=C.STATUS["warning"])
            fig.update_layout(title=f"Planificación de actividades · {anio}", legend_title_text="")
            ui.plot(fig, max(320, 30 * len(gc) + 120))
        st.caption("Para agregar una actividad a la planificación use la pestaña ➕ Nueva actividad y marque 'Planificación anual'.")
