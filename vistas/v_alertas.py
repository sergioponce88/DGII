import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import catalogos as C
import comun as K
import db
import reportes as R
import ui


def _agenda():
    h = pd.Timestamp(db.hoy())
    filas = []
    cur = db.df_cursos()
    for _, c in cur.dropna(subset=["fecha_inicio"]).iterrows():
        if c["estado"] in ("NO AUTORIZADO", "SUSPENDIDO"):
            continue
        fin = c["fecha_fin"] if pd.notna(c["fecha_fin"]) else c["fecha_inicio"]
        filas.append(dict(item=f"🎓 {c['nombre']}", ini=c["fecha_inicio"], fin=fin + pd.Timedelta(days=1), cat="Curso", det=c.get("lugar") or ""))
    ev = db.df_eventos()
    for _, v in ev[~ev["completado"].astype(bool)].iterrows() if not ev.empty else []:
        filas.append(dict(item=f"📌 {v['titulo']}", ini=v["fecha"], fin=v["fecha"] + pd.Timedelta(days=1), cat="Evento", det=v.get("lugar") or ""))
    exp = db.df_expedientes()
    vto = exp[exp["fecha_termino"].notna() & ~exp["estado"].isin(C.ESTADOS_CERRADOS) & ~exp["tramitado"]] if not exp.empty else exp
    for _, e in vto.iterrows():
        filas.append(dict(item=f"⏱ Exp. {e['identificador']}", ini=e["fecha_termino"], fin=e["fecha_termino"] + pd.Timedelta(days=1), cat="Vencimiento", det=e["tipo"]))
    df = pd.DataFrame(filas)
    if df.empty:
        return df
    return df[(df["fin"] >= h - pd.Timedelta(days=7)) & (df["ini"] <= h + pd.Timedelta(days=60))].sort_values("ini")


def render(alertas):
    ui.header("Alertas y Agenda", "Inicios de curso, vencimientos, expedientes detenidos y eventos")
    cnt = {n: sum(1 for a in alertas if a["nivel"] == n) for n in K.NIVELES}
    ui.kpis(
        [
            ("Críticas", cnt["critical"], "hoy / vencidas", C.STATUS["critical"]),
            ("Importantes", cnt["serious"], "requieren acción", C.STATUS["serious"]),
            ("Próximas", cnt["warning"], "en los próximos días", C.STATUS["warning"]),
            ("Informativas", cnt["info"], "seguimiento", "#3B82F6"),
        ]
    )
    t1, t2, t3 = st.tabs(["🔔 Alertas", "🗓️ Agenda 60 días", "➕ Nuevo evento"])

    with t1:
        cats = sorted({a["cat"] for a in alertas})
        sel = st.pills("Filtrar", cats, selection_mode="multi", key="al_cat") if cats else []
        lista = [a for a in alertas if not sel or a["cat"] in sel]
        if lista:
            K.compartir_wp(R.msg_alertas(lista), "alertas", f"📲 Enviar estas {len(lista)} alertas por WhatsApp")
        if not lista:
            st.success("✔ Sin alertas pendientes.")
        for i, a in enumerate(lista[:80]):
            ic, col, _ = K.NIVELES[a["nivel"]]
            ui.alerta(ic, a["titulo"], f"{a['detalle']} · {ui.fmt_fecha(a['fecha'])}", col)
            b1, b2, _ = st.columns([1, 1, 2])
            if a["exp_id"] is not None and pd.notna(a["exp_id"]):
                if b1.button("🔎 Ficha", key=f"al_f_{i}"):
                    K.ir_a(K.PAG_FICHA, a["exp_id"])
            b2.link_button("📲 Avisar", R.link_whatsapp(R.msg_alerta(a["titulo"], a["detalle"]), K.tel_dep(a["dep"]) if a["dep"] else None))

    with t2:
        ag = _agenda()
        if ag.empty:
            st.info("Nada agendado en los próximos 60 días.")
        else:
            colores = {"Curso": C.PALETA[2], "Evento": C.PALETA[6], "Vencimiento": C.STATUS["critical"]}
            fig = go.Figure()
            for cat, g in ag.groupby("cat"):
                fig.add_bar(
                    base=g["ini"], x=(g["fin"] - g["ini"]).dt.total_seconds() * 1000, y=g["item"], orientation="h", name=cat,
                    marker=dict(color=colores.get(cat, "#64748B"), cornerradius=4),
                    customdata=g[["det"]].assign(i=g["ini"].dt.strftime("%d/%m/%Y")),
                    hovertemplate="%{y}<br>%{customdata[1]} · %{customdata[0]}<extra></extra>",
                )
            fig.update_xaxes(type="date")
            fig.update_yaxes(autorange="reversed", title=None, tickfont=dict(size=10))
            fig.add_vline(x=str(db.hoy()), line_width=2, line_dash="dot", line_color=C.STATUS["warning"])
            fig.update_layout(title="Agenda (−7 / +60 días)", barmode="overlay")
            ui.plot(fig, max(320, 28 * len(ag) + 120))
            st.dataframe(pd.DataFrame({"Fecha": ag["ini"].dt.strftime("%d/%m/%Y"), "Tipo": ag["cat"], "Detalle": ag["item"], "Info": ag["det"]}),
                         hide_index=True, width="stretch")
        ev = db.df_eventos()
        pend = ev[~ev["completado"].astype(bool)] if not ev.empty else ev
        if not pend.empty:
            ui.seccion("📌 Eventos pendientes")
            for _, v in pend.iterrows():
                c1, c2, c3 = st.columns([5, 1, 1])
                c1.markdown(f"**{ui.esc(v['titulo'])}** · {ui.fmt_fecha(v['fecha'])} {ui.esc(v['hora'] or '')} · {ui.esc(v['lugar'] or '')}"
                            + (f" · Exp. {ui.esc(v['identificador'])}" if pd.notna(v["identificador"]) else ""))
                if c2.button("✔", key=f"ag_ok_{v['id']}", help="Marcar cumplido"):
                    db.completar_evento(int(v["id"]))
                    st.rerun()
                if c3.button("🗑", key=f"ag_del_{v['id']}", help="Eliminar"):
                    db.eliminar_evento(int(v["id"]))
                    st.rerun()

    with t3:
        exp = db.df_expedientes()
        with st.form("nuevo_evento", clear_on_submit=True):
            e1, e2 = st.columns(2)
            tit = e1.text_input("Título del evento")
            tip = e2.selectbox("Tipo", C.TIPOS_EVENTO)
            e3, e4, e5, e6 = st.columns(4)
            fec = e3.date_input("Fecha", db.hoy(), format="DD/MM/YYYY")
            hora = e4.text_input("Hora", placeholder="09:00")
            lug = e5.text_input("Lugar")
            av = e6.number_input("Avisar días antes", 0, 90, 3)
            opciones = [None] + exp["id"].tolist()
            etq = {r["id"]: K.etiqueta_exp(r) for _, r in exp.iterrows()}
            eid = st.selectbox("Expediente asociado (opcional)", opciones, format_func=lambda x: "— Ninguno —" if x is None else etq.get(x, x))
            desc = st.text_area("Descripción", height=60)
            if st.form_submit_button("➕ Agendar"):
                if not tit.strip():
                    st.error("Ingrese un título.")
                else:
                    db.crear_evento(dict(titulo=tit.strip(), tipo=tip, fecha=fec, hora=hora or None, lugar=lug or None,
                                         dias_aviso=int(av), descripcion=desc or None, expediente_id=int(eid) if eid else None), K.usuario())
                    st.toast("Evento agendado", icon="🗓️")
                    st.rerun()
