import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import catalogos as C
import comun as K
import db
import ui

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
GAP = dict(color="#0B1224", width=2)  # separación de 2px entre segmentos


def render():
    ui.header("Panel de Control", logo=K.LOGO)
    exp = db.df_expedientes()
    if exp.empty:
        st.info("Aún no hay expedientes. Comience en **➕ Nuevo Expediente** o importe el libro en **📥 Carga Masiva**.")
        return
    mapa = ui.mapa_dependencias()
    anios = sorted(exp["anio"].dropna().astype(int).unique().tolist(), reverse=True)
    c1, c2 = st.columns([1, 3])
    anio = c1.selectbox("Año", anios, index=0, key="pan_anio")
    e = exp[exp["anio"] == anio]
    h = pd.Timestamp(db.hoy())
    abiertos = e[~e["estado"].isin(C.ESTADOS_CERRADOS)]
    vencidos = abiertos[abiertos["fecha_termino"].notna() & (abiertos["fecha_termino"] < h)]
    urg = abiertos[abiertos["prioridad"] == "URGENTE TRÁMITE"]
    movs = db.df_movimientos()
    mov_hoy = movs[movs["fecha_hora"].dt.normalize() == h] if not movs.empty else movs
    cur = db.df_cursos()
    cur_act = cur[cur["fase"] == "EN CURSO"] if not cur.empty else cur
    fuera = e[e["ubicacion_actual"].fillna("") != C.DEP_PROPIA]

    ui.kpis(
        [
            ("Expedientes " + str(anio), len(e), f"{(e['origen'] == C.ORIGENES[0]).sum()} iniciados · {(e['origen'] == C.ORIGENES[1]).sum()} recibidos", "#3B82F6"),
            ("En trámite", len(abiertos), f"{len(e) - len(abiertos)} resueltos / archivados", C.PALETA[2]),
            ("Pendientes de trámite", int((~abiertos["tramitado"]).sum()), f"{int(e['tramitado'].sum())} tramitados", C.STATUS["warning"]),
            ("Urgentes activos", len(urg), "Urgente trámite", C.STATUS["serious"]),
            ("Vencidos", len(vencidos), "Fecha de término superada", C.STATUS["critical"]),
            ("Fuera de la Dirección", len(fuera[~fuera["estado"].isin(C.ESTADOS_CERRADOS)]), "Abiertos en otras dependencias", C.PALETA[3]),
            ("Movimientos hoy", len(mov_hoy), ui.fmt_fecha(h), C.PALETA[6]),
            ("Actividades en desarrollo", len(cur_act), f"{len(cur)} actividades registradas", C.PALETA[4]),
        ]
    )

    # Comisión: lo que está encargado y lo que ya entregaron hoy los comisionistas
    pend = e[e["entrega_pendiente"].fillna(False).astype(bool)] if "entrega_pendiente" in e.columns else e.iloc[0:0]
    ent = mov_hoy[mov_hoy["tipo"].isin(["SALIDA", "DEVOLUCIÓN", "PASE INTERNO"]) & mov_hoy["recibido_por"].notna()] if not mov_hoy.empty else mov_hoy
    if len(pend) or len(ent):
        with st.expander(f"🚚 Comisión · {len(pend)} para entregar · {len(ent)} entregados hoy", expanded=bool(len(ent))):
            for _, m in ent.head(15).iterrows():
                st.markdown(f"<small>✅ {ui.fmt_fecha(m['fecha_hora'], True)} · <b>{ui.esc(m['identificador'])}</b> → {ui.esc(m['destino'])} · "
                            f"recibió <b>{ui.esc(m.get('recibido_por') or '—')}</b> · llevó {ui.esc(m.get('entregado_por') or '—')}</small>",
                            unsafe_allow_html=True)
            for _, r in pend.head(15).iterrows():
                st.markdown(f"<small>📦 <b>{ui.esc(r['identificador'])}</b> → {ui.esc(r.get('entrega_destino') or '—')} · "
                            f"encargado por {ui.esc(r.get('entrega_solicitada_por') or '—')}</small>", unsafe_allow_html=True)

    alertas = K.calcular_alertas()
    top = [a for a in alertas if a["nivel"] in ("critical", "serious")][:3]
    if top:
        for a in top:
            ic, col, _ = K.NIVELES[a["nivel"]]
            ui.alerta(ic, a["titulo"], a["detalle"], col)

    # ── Qué está pasando esta semana (más allá de los expedientes) ──
    if not cur.empty:
        fin = cur["fecha_fin"].fillna(cur["fecha_inicio"])
        vigentes = cur[cur["fecha_inicio"].notna() & ~cur["estado"].isin(["NO AUTORIZADO", "SUSPENDIDO"])
                       & (cur["fecha_inicio"] <= h + pd.Timedelta(days=7)) & (fin >= h)].sort_values("fecha_inicio")
        if not vigentes.empty:
            ui.seccion(f"📅 Esta semana en la Dirección ({len(vigentes)} actividades)")
            filas = []
            for _, c in vigentes.head(8).iterrows():
                en_curso = c["fecha_inicio"] <= h
                col = C.PALETA[2] if en_curso else C.STATUS["warning"]
                tipo = c["tipo_actividad"] if isinstance(c["tipo_actividad"], str) else "CURSO"
                cuando = "EN DESARROLLO" if en_curso else f"Inicia {ui.fmt_fecha(c['fecha_inicio'])}"
                filas.append(f"<div class='card acc' style='--c:{col};padding:9px 14px;margin-bottom:8px'>{ui.chip(tipo, C.PALETA[0], False)}"
                             f"{ui.chip(cuando, col)} <b>{ui.esc(c['nombre'])}</b>"
                             f"<span class='meta'> · {ui.esc(c['lugar'] or '')} · {int(c['cant_personal'] or 0)} efectivos</span></div>")
            st.markdown("".join(filas), unsafe_allow_html=True)

    g1, g2 = st.columns([3, 2])
    with g1:
        e2 = e.dropna(subset=["fecha_ingreso"]).copy()
        e2["mes"] = e2["fecha_ingreso"].dt.month
        piv = e2.pivot_table(index="mes", columns="origen", values="id", aggfunc="count").reindex(range(1, 13)).fillna(0)
        fig = go.Figure()
        for i, o in enumerate(C.ORIGENES):
            if o in piv.columns:
                fig.add_bar(x=MESES, y=piv[o], name="Iniciados en la Dirección" if i == 0 else "Recibidos de otras dependencias",
                            marker=dict(color=C.PALETA[i], line=GAP, cornerradius=4),
                            hovertemplate="%{x}: %{y:.0f}<extra>%{fullData.name}</extra>")
        fig.update_layout(barmode="stack", title=f"Ingresos por mes · {anio}", yaxis_title=None)
        ui.plot(fig, 330)
    with g2:
        st_cnt = e["estado"].value_counts().reindex(C.ESTADOS).dropna()
        fig = go.Figure(go.Bar(
            x=st_cnt.values, y=st_cnt.index, orientation="h",
            marker=dict(color=[C.COLOR_ESTADO[s] for s in st_cnt.index], cornerradius=4),
            text=st_cnt.values.astype(int), textposition="outside", textfont=dict(color=ui.INK_2),
            hovertemplate="%{y}: %{x:.0f}<extra></extra>"))
        fig.update_layout(title="Estado de los expedientes", yaxis=dict(autorange="reversed"), xaxis=dict(showgrid=False, visible=False))
        ui.plot(fig, 330)

    g3, g4 = st.columns(2)
    with g3:
        ub = abiertos["ubicacion_actual"].fillna("SIN DATO").value_counts().head(12)
        fig = go.Figure(go.Bar(
            x=ub.values, y=[ui.sigla_dep(n) for n in ub.index], orientation="h",
            marker=dict(color=[ui.color_dep(n, mapa) for n in ub.index], cornerradius=4),
            customdata=ub.index, text=ub.values, textposition="outside", textfont=dict(color=ui.INK_2),
            hovertemplate="%{customdata}: %{x:.0f} expedientes<extra></extra>"))
        fig.update_layout(title="¿Dónde están hoy los expedientes abiertos?", yaxis=dict(autorange="reversed"), xaxis=dict(visible=False))
        ui.plot(fig, 360)
    with g4:
        grupos = [g for g in C.GRUPOS]
        col_g = {g: C.PALETA[i % len(C.PALETA)] for i, g in enumerate(grupos)}
        tp = e.groupby(["tipo", "grupo"]).size().reset_index(name="n").sort_values("n", ascending=False).head(12)
        fig = go.Figure(go.Bar(
            x=tp["n"], y=tp["tipo"], orientation="h",
            marker=dict(color=[col_g.get(g, "#64748B") for g in tp["grupo"]], cornerradius=4),
            customdata=tp["grupo"], text=tp["n"], textposition="outside", textfont=dict(color=ui.INK_2),
            hovertemplate="%{y}<br>%{customdata}: %{x:.0f}<extra></extra>"))
        fig.update_layout(title="Tipos de expediente más frecuentes", yaxis=dict(autorange="reversed", tickfont=dict(size=10)), xaxis=dict(visible=False))
        ui.plot(fig, 360)
        st.markdown(" ".join(ui.chip(g, col_g[g]) for g in grupos if g in set(tp["grupo"])), unsafe_allow_html=True)

    m_anio = movs[movs["anio"] == anio] if not movs.empty else movs
    flujo = m_anio[m_anio["tipo"] != "ARCHIVO"].groupby(["origen", "destino"]).size().reset_index(name="n") if not m_anio.empty else pd.DataFrame()
    flujo = flujo[(flujo["origen"].notna()) & (flujo["destino"].notna()) & (flujo["origen"] != flujo["destino"])] if not flujo.empty else flujo
    if not flujo.empty:
        izq = sorted(flujo["origen"].unique())
        der = sorted(flujo["destino"].unique())
        nodos = [f"{ui.sigla_dep(n)} ▸" for n in izq] + [f"▸ {ui.sigla_dep(n)}" for n in der]
        colores = [ui.color_dep(n, mapa) for n in izq] + [ui.color_dep(n, mapa) for n in der]
        src = [izq.index(o) for o in flujo["origen"]]
        tgt = [len(izq) + der.index(d) for d in flujo["destino"]]
        fig = go.Figure(go.Sankey(
            arrangement="snap",
            node=dict(label=nodos, color=colores, pad=14, thickness=14, line=dict(color="#0B1224", width=1)),
            link=dict(source=src, target=tgt, value=flujo["n"], color=[ui.rgba(colores[s], .35) for s in src],
                      hovertemplate="%{source.label} %{target.label}: %{value} movimientos<extra></extra>"),
        ))
        fig.update_layout(title=f"Flujo de expedientes entre dependencias · {anio}", font=dict(size=11, color=ui.INK))
        ui.plot(fig, 420)

    ui.seccion("🕒 Últimos movimientos")
    ult = movs.head(8) if not movs.empty else movs
    if ult.empty:
        st.caption("Sin movimientos.")
    for _, m in ult.iterrows():
        c = ui.color_dep(m["destino"], mapa)
        st.markdown(
            f"<div class='card acc' style='--c:{c};padding:10px 14px'>"
            f"<b>Exp. {ui.esc(m['identificador'])}</b> · {ui.esc(m['tipo'])} "
            f"{ui.chip(m['origen'] or '—', ui.color_dep(m['origen'], mapa))}➜ {ui.chip(m['destino'] or '—', c)}"
            f"<div class='meta'>🕒 {ui.fmt_fecha(m['fecha_hora'], True)} · {ui.esc(m['tipo_exp'])}"
            f"{' · Despacho: <b>' + ui.esc(m['despacho']) + '</b>' if m['despacho'] else ''}"
            f"{' · Lleva: ' + ui.esc(m['entregado_por']) if m['entregado_por'] else ''}</div></div>",
            unsafe_allow_html=True,
        )
