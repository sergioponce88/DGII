from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import catalogos as C
import comun as K
import db
import reportes as R
import ui
from vistas.v_cursos import estadisticas_cursos

DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
SEQ = [[0, "#111C38"], [0.35, "#1C5CAB"], [0.7, "#3987E5"], [1, "#B7D3F6"]]


def _periodo():
    h = db.hoy()
    c1, c2, c3 = st.columns([2, 1, 1])
    pre = c1.segmented_control("Período", ["Este mes", "Trimestre", "Este año", "Año anterior", "Personalizado"], default="Este año", key="inf_per")
    if pre == "Este mes":
        d, a = h.replace(day=1), h
    elif pre == "Trimestre":
        d, a = h - timedelta(days=90), h
    elif pre == "Año anterior":
        d, a = date(h.year - 1, 1, 1), date(h.year - 1, 12, 31)
    elif pre == "Personalizado":
        d = c2.date_input("Desde", h.replace(day=1), format="DD/MM/YYYY", key="inf_d")
        a = c3.date_input("Hasta", h, format="DD/MM/YYYY", key="inf_h")
    else:
        d, a = date(h.year, 1, 1), h
    return d, a


def _cuenta(df, col, nombre):
    if df.empty:
        return pd.DataFrame(columns=[nombre, "Cantidad", "%"])
    s = df[col].fillna("SIN DATO").value_counts()
    return pd.DataFrame({nombre: s.index, "Cantidad": s.values, "%": (s.values / s.sum() * 100).round(1)})


def render():
    ui.header("Informes", "Estadística, control de pendientes y libro de movimientos")
    d, a = _periodo()
    periodo = f"{d:%d/%m/%Y} al {a:%d/%m/%Y}"
    exp = db.df_expedientes()
    movs = db.df_movimientos()
    e = exp[(exp["fecha_ingreso"] >= pd.Timestamp(d)) & (exp["fecha_ingreso"] <= pd.Timestamp(a))] if not exp.empty else exp
    m = movs[(movs["fecha_hora"] >= pd.Timestamp(d)) & (movs["fecha_hora"] < pd.Timestamp(a) + pd.Timedelta(days=1))] if not movs.empty else movs
    h = pd.Timestamp(db.hoy())

    cerrados = e[e["estado"].isin(C.ESTADOS_CERRADOS)]
    dur = (cerrados["ult_mov"].fillna(cerrados["actualizado_en"]) - cerrados["fecha_ingreso"]).dt.days.clip(lower=0) if not cerrados.empty else pd.Series(dtype=float)
    kp = [
        ("Ingresados", len(e), periodo, "#3B82F6"),
        ("Iniciados en la Dirección", int((e["origen"] == C.ORIGENES[0]).sum()), "", C.PALETA[0]),
        ("Recibidos", int((e["origen"] == C.ORIGENES[1]).sum()), "de otras dependencias", C.PALETA[1]),
        ("Resueltos / archivados", len(cerrados), f"{(len(cerrados) / len(e) * 100 if len(e) else 0):.0f}% del período", C.STATUS["ok"]),
        ("Tiempo medio de trámite", f"{dur.median():.0f} d" if len(dur) else "—", "mediana, expedientes cerrados", C.PALETA[6]),
        ("Movimientos", len(m), "salidas, ingresos y pases", C.PALETA[3]),
    ]
    ui.kpis(kp)

    t1, t2, t3, t4 = st.tabs(["📊 Gestión", "⏳ Control de pendientes", "🔁 Libro de movimientos", "🎓 Actividades"])

    with t1:
        if e.empty:
            st.info("Sin expedientes en el período.")
        else:
            g1, g2 = st.columns(2)
            with g1:
                tm = e.groupby(["grupo", "tipo"]).size().reset_index(name="n")
                col_g = {g: C.PALETA[i % len(C.PALETA)] for i, g in enumerate(C.GRUPOS)}
                fig = px.treemap(tm, path=[px.Constant("Expedientes"), "grupo", "tipo"], values="n", color="grupo", color_discrete_map=col_g | {"(?)": "#1E293B"})
                fig.update_traces(marker=dict(cornerradius=4, line=dict(color="#0B1224", width=2)), root_color="#0F172A",
                                  hovertemplate="%{label}: %{value}<extra></extra>", textinfo="label+value")
                fig.update_layout(title="Composición por grupo y tipo", margin=dict(t=48, l=4, r=4, b=4))
                ui.plot(fig, 420)
            with g2:
                if not m.empty:
                    hm = m.assign(d=m["fecha_hora"].dt.dayofweek, hr=m["fecha_hora"].dt.hour).pivot_table(index="d", columns="hr", values="id", aggfunc="count").reindex(range(7)).fillna(0)
                    hm = hm.reindex(columns=range(6, 23), fill_value=0)
                    fig = go.Figure(go.Heatmap(z=hm.values, x=[f"{c}h" for c in hm.columns], y=DIAS, colorscale=SEQ, xgap=2, ygap=2,
                                               hovertemplate="%{y} %{x}: %{z:.0f} movimientos<extra></extra>", colorbar=dict(thickness=10)))
                    fig.update_layout(title="Actividad de mesa de entradas (día × hora)", yaxis=dict(autorange="reversed"))
                    ui.plot(fig, 420)
            ac = e.sort_values("fecha_ingreso").groupby(e["fecha_ingreso"].dt.to_period("W").dt.start_time).size().cumsum()
            fig = go.Figure(go.Scatter(x=ac.index, y=ac.values, mode="lines", line=dict(width=2, color=C.PALETA[0]),
                                       fill="tozeroy", fillcolor=ui.rgba(C.PALETA[0], .12), hovertemplate="%{x|%d/%m/%Y}: %{y} acumulados<extra></extra>"))
            fig.update_layout(title="Expedientes acumulados en el período", hovermode="x unified")
            ui.plot(fig, 280)

        t_tipo, t_grupo = _cuenta(e, "tipo", "Tipo"), _cuenta(e, "grupo", "Grupo")
        t_est, t_org = _cuenta(e, "estado", "Estado"), _cuenta(e, "dependencia_origen", "Dependencia de origen")
        c1, c2 = st.columns(2)
        c1.dataframe(t_tipo, hide_index=True, width="stretch")
        c2.dataframe(t_org, hide_index=True, width="stretch")
        listado = pd.DataFrame({
            "Exp.": e["identificador"], "Año": e["anio"], "Ingreso": e["fecha_ingreso"].dt.strftime("%d/%m/%Y"), "Tipo": e["tipo"],
            "Asunto": e["asunto"], "Origen": e["dependencia_origen"], "Destino": e["destino"], "Estado": e["estado"], "Ubicación": e["ubicacion_actual"],
        })
        secc = [("Por tipo de expediente", t_tipo), ("Por grupo", t_grupo), ("Por estado", t_est), ("Por dependencia de origen", t_org), ("Listado", listado)]
        b1, b2 = st.columns(2)
        b1.download_button("🖨️ Informe de gestión (PDF)", R.pdf_informe("INFORME DE GESTIÓN DE EXPEDIENTES", periodo, [(k, v) for k, v, *_ in kp], secc, K.LOGO),
                           file_name=f"informe_gestion_{d:%Y%m%d}_{a:%Y%m%d}.pdf", mime="application/pdf")
        b2.download_button("📥 Informe de gestión (Excel)", R.excel({n: t for n, t in secc}), file_name=f"informe_gestion_{d:%Y%m%d}_{a:%Y%m%d}.xlsx")

    with t2:
        ab = exp[~exp["estado"].isin(C.ESTADOS_CERRADOS)].copy()
        if ab.empty:
            st.success("No hay expedientes abiertos.")
        else:
            ab["dias_quieto"] = (h - ab["ult_mov"].fillna(ab["fecha_ingreso"]).dt.normalize()).dt.days
            ab["dias_total"] = (h - ab["fecha_ingreso"]).dt.days
            deps = st.multiselect("Ubicación", sorted(ab["ubicacion_actual"].dropna().unique()), key="pend_ub")
            if deps:
                ab = ab[ab["ubicacion_actual"].isin(deps)]
            ab = ab.sort_values(["prioridad", "dias_quieto"], ascending=[False, False])
            pend = pd.DataFrame({
                "Exp.": ab["identificador"], "Año": ab["anio"], "Tipo": ab["tipo"], "Asunto": ab["asunto"], "Prioridad": ab["prioridad"],
                "Estado": ab["estado"], "Ubicación": ab["ubicacion_actual"], "Destino": ab["destino"], "Días sin mover": ab["dias_quieto"], "Días totales": ab["dias_total"],
                "Vence": ab["fecha_termino"].dt.strftime("%d/%m/%Y"),
            })
            mapa = ui.mapa_dependencias()
            rng = ab.groupby("ubicacion_actual")["dias_quieto"].agg(["count", "median"]).sort_values("count", ascending=False).head(10)
            fig = go.Figure(go.Bar(x=[ui.sigla_dep(i) for i in rng.index], y=rng["count"], customdata=rng["median"],
                                   marker=dict(color=[ui.color_dep(i, mapa) for i in rng.index], cornerradius=4),
                                   text=rng["count"], textposition="outside", textfont=dict(color=ui.INK_2),
                                   hovertemplate="%{x}: %{y} abiertos · mediana %{customdata:.0f} días sin mover<extra></extra>"))
            fig.update_layout(title="Expedientes abiertos por ubicación", yaxis=dict(visible=False))
            ui.plot(fig, 300)
            st.dataframe(ui.estilo_tabla(pend, mapa),
                         hide_index=True, width="stretch")
            b1, b2 = st.columns(2)
            b1.download_button("🖨️ Control de pendientes (PDF)",
                               R.pdf_informe("CONTROL DE EXPEDIENTES PENDIENTES", f"al {db.hoy():%d/%m/%Y}",
                                             [("Abiertos", len(pend)), ("Urgentes", int((pend["Prioridad"] == "URGENTE TRÁMITE").sum())),
                                              ("Fuera de la Dirección", int((pend["Ubicación"] != C.DEP_PROPIA).sum()))],
                                             [("Pendientes por antigüedad", pend)], K.LOGO),
                               file_name=f"pendientes_{db.hoy():%Y%m%d}.pdf", mime="application/pdf")
            b2.download_button("📥 Control de pendientes (Excel)", R.excel({"Pendientes": pend}), file_name=f"pendientes_{db.hoy():%Y%m%d}.xlsx")

    with t3:
        if m.empty:
            st.info("Sin movimientos en el período.")
        else:
            lm = pd.DataFrame({
                "Fecha/Hora": m["fecha_hora"].dt.strftime("%d/%m/%Y %H:%M"), "Exp.": m["identificador"], "Tipo exp.": m["tipo_exp"],
                "Movimiento": m["tipo"], "Origen": m["origen"], "Destino": m["destino"], "Despacho": m["despacho"],
                "Lleva": m["entregado_por"], "Recibe": m["recibido_por"], "Registró": m["registrado_por"],
            })
            st.dataframe(ui.estilo_tabla(lm), hide_index=True, width="stretch", height=min(600, 38 + 35 * len(lm)))
            b1, b2 = st.columns(2)
            b1.download_button("🖨️ Libro de movimientos (PDF)", R.pdf_informe("LIBRO DE MOVIMIENTOS", periodo, [("Movimientos", len(lm))], [("Detalle", lm)], K.LOGO),
                               file_name=f"movimientos_{d:%Y%m%d}_{a:%Y%m%d}.pdf", mime="application/pdf")
            b2.download_button("📥 Libro de movimientos (Excel)", R.excel({"Movimientos": lm}), file_name=f"movimientos_{d:%Y%m%d}_{a:%Y%m%d}.xlsx")

    with t4:
        cur = db.df_cursos()
        pers = db.df_personal()
        cur = cur[(cur["fecha_inicio"] >= pd.Timestamp(d)) & (cur["fecha_inicio"] <= pd.Timestamp(a))]
        pers = pers[pers["curso_id"].isin(cur["id"])]
        if cur.empty:
            st.info("Sin actividades con inicio en el período.")
        else:
            kc, tablas = estadisticas_cursos(cur, pers)
            ui.kpis(kc)
            for n, t in tablas.items():
                with st.expander(f"{n} ({len(t)})"):
                    st.dataframe(t, hide_index=True, width="stretch")
            st.download_button("🖨️ Estadística de cursos (PDF)",
                               R.pdf_informe("ESTADÍSTICA DE ACTIVIDADES", periodo, [(k, v) for k, v, *_ in kc], list(tablas.items()), K.LOGO),
                               file_name=f"cursos_{d:%Y%m%d}_{a:%Y%m%d}.pdf", mime="application/pdf")
