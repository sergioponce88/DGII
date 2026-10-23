"""📝 Tramitar: el oficial elige el modelo, completa el formulario viendo la nota en vivo, revisa la
redacción, descarga el Word para imprimir y deja el expediente asentado como TRAMITADO."""
import json
from datetime import datetime

import pandas as pd
import streamlit as st

import catalogos as C
import comun as K
import db
import docword as W
import modelos as M
import redaccion as RD
import ui

OTRA = "_OTRA"
ORIGENES_ACT = ["INICIADA EN LA DIRECCIÓN", "RECIBIDA DE OTRA DEPENDENCIA"]
PASOS_UI = ["Expediente", "Qué hacer", "Completar", "Revisar y Word", "Asentar"]
AVANZADOS = {"verbo", "firma", "cumplido_txt", "plazo", "horario", "generales", "nacionalidad", "estado_civil", "padres",
             "telefono", "fundamento_instructor", "dirigido"}
PERSONA = {c.key for c in M.CAMPOS_PERSONA} - {"nombre", "condicion"}

CSS = """
<style>
.tr-steps{display:flex;gap:6px;margin:4px 0 14px;overflow-x:auto;padding-bottom:2px}
.tr-steps .s{flex:1;min-width:92px;display:flex;align-items:center;gap:8px;padding:8px 10px;border-radius:10px;
  background:rgba(30,41,59,.45);border:1px solid #1E293B;color:#94A3B8;font-size:.78rem;font-weight:700;white-space:nowrap}
.tr-steps .s b{display:inline-grid;place-items:center;width:24px;height:24px;border-radius:50%;background:#1E293B;color:#94A3B8;font-size:.78rem}
.tr-steps .s.on{background:linear-gradient(135deg,rgba(37,99,235,.35),rgba(29,78,216,.18));border-color:#60A5FA;color:#F8FAFC}
.tr-steps .s.on b{background:#3B82F6;color:#fff}
.tr-steps .s.ok{border-color:rgba(34,197,94,.45);color:#BBF7D0}
.tr-steps .s.ok b{background:#16A34A;color:#fff}
.tr-h{display:flex;align-items:center;gap:10px;margin:18px 0 8px}
.tr-h b{display:inline-grid;place-items:center;width:28px;height:28px;border-radius:50%;background:#3B82F6;color:#fff;font-size:.9rem}
.tr-h span{font-size:1.05rem;font-weight:800;color:#F8FAFC}
.tr-h small{color:#94A3B8;font-weight:500;margin-left:4px}
.tr-g{font-size:.74rem;font-weight:800;letter-spacing:.8px;text-transform:uppercase;color:#93C5FD;margin:2px 0 6px}
.tr-sel{display:flex;align-items:center;gap:12px;padding:12px 16px;border-radius:12px;border:1px solid #60A5FA;
  background:linear-gradient(135deg,rgba(37,99,235,.28),rgba(15,23,42,.6))}
.tr-sel .ic{font-size:1.6rem}.tr-sel .n{font-weight:800;font-size:1.02rem;color:#fff}.tr-sel .d{color:#CBD5E1;font-size:.8rem}
[class*="st-key-mc_"] button{min-height:3.6rem !important;text-align:left !important;justify-content:flex-start !important;
  background:rgba(19,27,46,.85) !important;border:1px solid #334155 !important;white-space:normal !important;padding:10px 14px !important}
[class*="st-key-mc_"] button:hover{border-color:#60A5FA !important;background:rgba(37,99,235,.18) !important}
[class*="st-key-mc_"] button p{font-size:.92rem !important;line-height:1.3}
[class*="st-key-mc_s_"] button{border-color:rgba(96,165,250,.75) !important;background:linear-gradient(135deg,rgba(37,99,235,.22),rgba(19,27,46,.9)) !important}
.tr-falta{border:1px solid rgba(245,158,11,.55);background:rgba(245,158,11,.10);border-radius:10px;padding:8px 12px;
  color:#FDE68A;font-size:.84rem;margin:6px 0}
.tr-listo{border:1px solid rgba(34,197,94,.55);background:rgba(34,197,94,.10);border-radius:10px;padding:8px 12px;color:#BBF7D0;font-size:.84rem;margin:6px 0}
.tr-paso{display:flex;align-items:center;gap:10px;padding:7px 10px;border-radius:9px;margin-bottom:5px;border:1px solid #1E293B;
  background:rgba(15,23,42,.55);font-size:.86rem;color:#CBD5E1}
.tr-paso.ok{border-color:rgba(34,197,94,.4);color:#BBF7D0}.tr-paso.sig{border-color:#F59E0B;background:rgba(245,158,11,.12);color:#FDE68A;font-weight:700}
.st-key-tr_prev{position:sticky;top:4.2rem}
.paper{background:#fff;border-radius:6px;padding:22px 26px;box-shadow:0 12px 30px rgba(0,0,0,.45);max-height:78vh;overflow:auto;
  font-family:Arial,Helvetica,sans-serif;font-size:12.5px;line-height:1.55}
.paper *{color:#111 !important;font-family:Arial,Helvetica,sans-serif !important}
.paper p{margin:0 0 6px}
.paper .mh{display:grid;grid-template-columns:52px 1fr 52px;align-items:center;gap:8px;border-bottom:2px solid #1F3A6E;padding-bottom:6px;margin-bottom:10px;text-align:center}
.paper .mh img{width:48px}.paper .mh small{display:block;font-size:8px;color:#555 !important;font-weight:700}
.paper .mh b{display:block;font-size:11.5px;color:#0F1E3C !important}.paper .mh i{display:block;font-size:8.5px;font-style:normal}
.paper .bx{border:1px solid #CBD5E1;border-radius:4px;padding:6px 8px;margin:6px 0}
.paper .bx.ref{background:#EEF2F8;border:0;border-left:4px solid #1F3A6E;font-size:11px}
.paper .bx.dk{background:#1F3A6E;border:0}.paper .bx.dk *{color:#fff !important;text-align:center}
.paper .bx2{display:grid;grid-template-columns:1fr 1fr;gap:10px;font-size:10.5px;text-align:center;margin-top:14px}
.paper .pb{text-align:center;color:#94A3B8 !important;font-size:10px;border-top:1px dashed #CBD5E1;margin:12px 0;padding-top:4px}
.paper.media{max-height:46vh}
@media (max-width:640px){.st-key-tr_prev{position:static}.paper{padding:14px 14px;font-size:11.5px}.tr-steps .s span{display:none}.tr-steps .s{min-width:auto;flex:0}}
</style>
"""


# ───────────────────────── Utilidades de presentación ─────────────────────────
def _pasos(actual, hechos):
    html = ""
    for i, n in enumerate(PASOS_UI, 1):
        cls = "ok" if i in hechos else ("on" if i == actual else "")
        html += f'<div class="s {cls}"><b>{"✓" if i in hechos else i}</b><span>{n}</span></div>'
    st.markdown(f'<div class="tr-steps">{html}</div>', unsafe_allow_html=True)


def _h(n, titulo, sub=""):
    st.markdown(f'<div class="tr-h"><b>{n}</b><span>{ui.esc(titulo)}<small>{ui.esc(sub)}</small></span></div>', unsafe_allow_html=True)


def _ctx(r):
    aut = db.df_autoridades()
    cfg = dict(db.get_config())
    cfg["dep_propia"] = C.DEP_PROPIA
    exp = {k: (None if (not isinstance(v, (list, dict)) and pd.isna(v)) else v) for k, v in dict(r).items()}
    return {"exp": exp, "act": db.get_actuacion(int(r["id"])), "cfg": cfg, "hoy": db.hoy(),
            "aut": {a["clave"]: a for a in aut.to_dict("records")}}


def _p(m, exp_id):
    return f"tr_{exp_id}_{m.id}_"


def _elegir(exp_id, mid):
    st.session_state[f"tr_sel_{exp_id}"] = mid


# ───────────────────────── Vista ─────────────────────────
def render():
    st.markdown(CSS, unsafe_allow_html=True)
    ui.header("Tramitar", "Elegí qué hacer · completá · descargá el Word · asentá el trámite")
    import auth

    if not auth.puede("tramitar"):
        auth.aviso_sin_permiso("la tramitación")
        return
    exp = db.df_expedientes()
    if exp.empty:
        st.info("No hay expedientes registrados.")
        return
    paso_ph = st.empty()

    _h(1, "Expediente", " · escriba el N° o el asunto")
    r = K.selector_expediente("tram_sel", exp, label="Expediente a tramitar")
    if r is None:
        with paso_ph.container():
            _pasos(1, set())
        return
    ui.tarjeta_expediente(r, detalle=False)
    ctx = _ctx(r)
    exp_id = int(r["id"])
    docs = db.df_documentos(exp_id)
    hechos = set(docs["modelo"]) if not docs.empty else set()

    if M.es_actuacion(r["tipo"]):
        pasos = _actuacion(r, ctx, hechos)
        if not ctx["act"]:
            with paso_ph.container():
                _pasos(2, {1})
            return
        sugeridos = pasos
        otros = [k for k, m in M.MODELOS.items() if m.grupo == "Actuaciones / Sumario" and k not in pasos] + \
                (["notificacion"] if "notificacion" not in pasos else [])
    else:
        sugeridos = M.sugeridos(r["tipo"])
        otros = [k for k in M.MODELOS if k not in sugeridos and M.MODELOS[k].grupo != "Actuaciones / Sumario"]

    sel = st.session_state.get(f"tr_sel_{exp_id}")
    if sel not in M.MODELOS:
        sel = None
    _h(2, "¿Qué va a hacer?", f" · sugeridos para {r['tipo'].lower()}" if not sel else "")
    if not sel:
        _tarjetas(exp_id, sugeridos, hechos, destacar=True)
        if otros:
            with st.expander(f"Ver todos los modelos ({len(otros)})"):
                _tarjetas(exp_id, otros, hechos)
        with paso_ph.container():
            _pasos(2, {1})
        _historial(docs)
        return
    m = M.MODELOS[sel]
    a, b = st.columns([4, 1], vertical_alignment="center")
    a.markdown(f'<div class="tr-sel"><div class="ic">{m.icono}</div><div><div class="n">{ui.esc(m.nombre)}</div>'
               f'<div class="d">{ui.esc(m.descripcion)}</div></div></div>', unsafe_allow_html=True)
    b.button("↺ Cambiar", key=f"tr_camb_{exp_id}", on_click=_elegir, args=(exp_id, None), width="stretch")

    estado = _formulario(m, r, ctx)
    hechos_ui = {1, 2} | ({3} if estado["completo"] else set()) | ({4} if estado["doc"] else set()) | ({5} if bool(r.get("tramitado")) else set())
    actual = 5 if estado["doc"] else (4 if estado["completo"] else 3)
    with paso_ph.container():
        _pasos(actual, hechos_ui)
    _historial(docs)


def _tarjetas(exp_id, ids, hechos, destacar=False):
    cols = st.columns(3)
    for i, mid in enumerate(ids):
        m = M.MODELOS[mid]
        with cols[i % 3], st.container(key=f"mc_{'s' if destacar else 'n'}_{exp_id}_{mid}"):
            st.button(f"{m.icono}  {m.nombre}{'  ✓' if mid in hechos else ''}", key=f"tr_b_{exp_id}_{mid}", help=m.descripcion,
                      on_click=_elegir, args=(exp_id, mid), width="stretch")


# ───────────────────────── Actuaciones / sumario ─────────────────────────
def _actuacion(r, ctx, hechos):
    a = ctx["act"]
    exp_id = int(r["id"])
    if a:
        resumen = f"{a.get('clase') or ''} N° {a.get('numero') or ''} · Causante: {a.get('causante') or '—'} · Instructor: {a.get('instructor') or '—'}"
        st.markdown(f'<div class="tr-listo">📋 {ui.esc(resumen)}</div>', unsafe_allow_html=True)
    with st.expander("📋 Datos de la actuación" + (" · editar" if a else " · complételos primero (una sola vez)"), expanded=not a):
        with st.form(f"act_{exp_id}"):
            st.markdown('<div class="tr-g">Carátula</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            clases = M.CLASES
            tipo = (r["tipo"] or "").upper()
            def_clase = a.get("clase") or next((c for c in clases if c in tipo), clases[0])
            clase = c1.selectbox("Clase", clases, index=clases.index(def_clase) if def_clase in clases else 0)
            origen = c2.radio("Origen", ORIGENES_ACT, horizontal=True,
                              index=ORIGENES_ACT.index(a["origen"]) if a.get("origen") in ORIGENES_ACT else (0 if r.get("origen") != C.ORIGENES[1] else 1))
            c3, c4 = st.columns(2)
            numero = c3.text_input("N° de actuación", a.get("numero") or r["identificador"])
            ocurrido = c4.text_input("Ocurrido", a.get("ocurrido") or "", placeholder="22/09/2025 a horas 06:50")
            causa = st.text_input("Causa", a.get("causa") or (r.get("asunto") or ""))
            c5, c6 = st.columns([3, 1])
            causante = c5.text_input("Causante", a.get("causante") or "", placeholder="Cadete de II° Año FRÍAS ARIEL ARMANDO")
            lp = c6.text_input("L.P.", a.get("causante_lp") or "")
            c7, c8 = st.columns(2)
            victima = c7.text_input("Víctima (si hay)", a.get("victima") or "")
            interviene = c8.text_input("Interviene", a.get("interviene") or "", placeholder="Rector del I.E.S.P. “G.J.F.S.M.”")
            hecho = st.text_area("Hecho", a.get("hecho") or "", height=90, placeholder="el día … a horas … (se usa en el acta, la valoración y la declaración)")
            st.markdown('<div class="tr-g">Instrucción</div>', unsafe_allow_html=True)
            d1, d2, d3 = st.columns([3, 1, 2])
            instr = d1.text_input("Instructor", a.get("instructor") or "", placeholder="Comisario Inspector APELLIDO NOMBRE")
            instr_lp = d2.text_input("L.P. instructor", a.get("instructor_lp") or "")
            instr_f = d3.text_input("Función", a.get("instructor_funcion") or "Vicerrector")
            e1, e2 = st.columns([3, 1])
            secr = e1.text_input("Secretario de actuaciones", a.get("secretario") or "", placeholder="Oficial Auxiliar APELLIDO NOMBRE")
            secr_lp = e2.text_input("L.P. secretario", a.get("secretario_lp") or "")
            if st.form_submit_button("💾 Guardar datos de la actuación", type="primary"):
                db.guardar_actuacion(exp_id, dict(clase=clase, numero=numero, origen=origen, causa=causa, causante=causante, causante_lp=lp,
                                                  victima=victima, ocurrido=ocurrido, interviene=interviene, hecho=hecho, instructor=instr,
                                                  instructor_lp=instr_lp, instructor_funcion=instr_f, secretario=secr, secretario_lp=secr_lp), K.usuario())
                st.toast("Datos guardados: se usan en todos los documentos", icon="✅")
                st.rerun()
    if not a:
        return []
    if "SUMARIO" in (a.get("clase") or "") or "SUMARIA" in (a.get("clase") or ""):
        pasos = M.PASOS_SUMARIO if a.get("origen") == ORIGENES_ACT[1] else M.PASOS_INTERNA
    else:
        pasos = M.PASOS_INTERNA if a.get("origen") != ORIGENES_ACT[1] else M.PASOS_EXTERNA
    hechos_n = sum(1 for p in pasos if p in hechos)
    siguiente = next((p for p in pasos if p not in hechos), None)
    with st.expander(f"🧭 Hoja de pasos de la instrucción · {hechos_n} de {len(pasos)} hechos"
                     + (f" · sigue: {M.MODELOS[siguiente].nombre}" if siguiente else " · completa"), expanded=False):
        st.progress(hechos_n / len(pasos))
        html = ""
        for i, pid in enumerate(pasos, 1):
            mm = M.MODELOS[pid]
            cls = "ok" if pid in hechos else ("sig" if pid == siguiente else "")
            marca = "✓" if pid in hechos else ("➜" if pid == siguiente else str(i))
            html += f'<div class="tr-paso {cls}"><b>{marca}</b> {mm.icono} {ui.esc(mm.nombre)}</div>'
        st.markdown(html, unsafe_allow_html=True)
        if siguiente and st.session_state.get(f"tr_sel_{exp_id}") != siguiente:
            st.button(f"Continuar con: {M.MODELOS[siguiente].nombre}", key=f"tr_sig_{exp_id}", type="primary",
                      on_click=_elegir, args=(exp_id, siguiente))
    return pasos


# ───────────────────────── Formulario ─────────────────────────
def _init(m, ctx, p):
    if st.session_state.get(p + "_init"):
        return
    for k, v in M.valores_por_defecto(m, ctx).items():
        if k == "destino" and v is None:
            v = OTRA
        if isinstance(v, datetime):
            v = v.date()
        st.session_state[p + k] = v
    st.session_state[p + "_init"] = True


def _widget(c, p, ctx, cont):
    k = p + c.key
    lab = c.label + (" *" if c.requerido else "")
    if c.tipo == "area":
        cont.text_area(lab, key=k, height=150 if c.ia else 90, placeholder=c.ayuda or None)
    elif c.tipo == "int":
        cont.number_input(lab, key=k, min_value=0, step=1, help=c.ayuda or None)
    elif c.tipo == "date":
        cont.date_input(lab, key=k, format="DD/MM/YYYY")
    elif c.tipo == "time":
        cont.time_input(lab, key=k, step=300)
    elif c.tipo == "select":
        cont.selectbox(lab, c.opciones, key=k, help=c.ayuda or None)
    elif c.tipo == "check":
        cont.checkbox(lab, key=k)
    elif c.tipo == "autoridad":
        claves = list(ctx["aut"]) + [OTRA]
        if st.session_state.get(k) not in claves:
            st.session_state[k] = claves[0]

        def _f(x):
            if x == OTRA:
                return "✏️ Otra dependencia (escribir)"
            a = ctx["aut"][x]
            return a["cargo"] + (f" — {a['titular']}" if a.get("titular") else "")

        cont.selectbox(lab, claves, key=k, format_func=_f)
    else:
        cont.text_input(lab, key=k, placeholder=c.ayuda or None)


def _grupos(m):
    g = {"dest": [], "datos": [], "persona": [], "cont": [], "adv": []}
    for c in m.campos:
        if c.key in AVANZADOS:
            g["adv"].append(c)
        elif c.tipo == "autoridad":
            g["dest"].append(c)
        elif c.tipo in ("date", "time", "int") or c.key in ("fojas_concl",):
            g["datos"].append(c)
        elif c.key in PERSONA or c.key in ("nombre", "condicion"):
            g["persona"].append(c)
        else:
            g["cont"].append(c)
    return g


def _bloque(titulo, campos, p, ctx, dos_col=True):
    if not campos:
        return
    with st.container(border=True):
        st.markdown(f'<div class="tr-g">{titulo}</div>', unsafe_allow_html=True)
        cortos = []

        def _vaciar():
            if not cortos:
                return
            cols = st.columns(2) if dos_col and len(cortos) > 1 else [st]
            for i, c in enumerate(cortos):
                _widget(c, p, ctx, cols[i % len(cols)])
            cortos.clear()

        for c in campos:
            if c.tipo in ("area", "check", "autoridad"):
                _vaciar()
                _widget(c, p, ctx, st)
                if c.tipo == "autoridad" and st.session_state.get(p + c.key) == OTRA:
                    o1, o2 = st.columns([1, 2])
                    o1.selectbox("Tratamiento", ["Señor", "Señora", "Al Señor", "A la Señora"], key=p + "o_trat")
                    o2.text_input("Cargo / dependencia", key=p + "o_cargo")
                    st.text_input("Grado y nombre del titular", key=p + "o_tit")
            else:
                cortos.append(c)
        _vaciar()


def _formulario(m, r, ctx):
    exp_id = int(r["id"])
    p = _p(m, exp_id)
    for k, v in st.session_state.pop(p + "_aplicar", {}).items():
        st.session_state[p + k] = v
    _init(m, ctx, p)

    _h(3, "Complete los datos", " · a la derecha ve cómo queda la nota")
    izq, der = st.columns([1.1, 1], gap="large")
    with izq:
        if not m.campos:
            st.markdown('<div class="tr-listo">Este documento se arma completo con los datos de la actuación. Solo genere el Word.</div>',
                        unsafe_allow_html=True)
        g = _grupos(m)
        _bloque("📬 Destinatario", g["dest"], p, ctx)
        _bloque("🗓️ Datos", g["datos"], p, ctx)
        _bloque("👤 Persona", g["persona"], p, ctx)
        _bloque("✍️ Contenido", g["cont"], p, ctx)
        if g["adv"]:
            with st.expander("⚙️ Opciones avanzadas"):
                _bloque("Opcional", g["adv"], p, ctx)

    v = {c.key: st.session_state.get(p + c.key) for c in m.campos}
    if v.get("destino") == OTRA:
        ctx["aut"][OTRA] = {"clave": OTRA, "tratamiento": st.session_state.get(p + "o_trat") or "Señor",
                            "cargo": st.session_state.get(p + "o_cargo") or "", "titular": st.session_state.get(p + "o_tit") or "",
                            "saludo": "Oficina", "relacion": "PAR"}
    faltan = [c.label for c in m.campos if c.requerido and not str(v.get(c.key) or "").strip()]
    if v.get("destino") == OTRA and not ctx["aut"][OTRA]["cargo"].strip():
        faltan.append("Cargo / dependencia del destinatario")

    doc = None
    with der:
        with st.container(key="tr_prev"):
            st.markdown('<div class="tr-g">👁️ Vista previa</div>', unsafe_allow_html=True)
            try:
                doc = m.render(v, ctx)
                st.markdown(W.preview_html(doc), unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"La vista previa no se pudo armar: {e}")

    _h(4, "Revisar y generar el Word")
    if faltan:
        st.markdown(f'<div class="tr-falta">⚠️ Falta completar: <b>{ui.esc(", ".join(faltan))}</b></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="tr-listo">✔ Todo listo. Puede revisar la redacción o generar el Word.</div>', unsafe_allow_html=True)
    ia = [c for c in m.campos if c.ia and (st.session_state.get(p + c.key) or "").strip()]
    b1, b2 = st.columns(2)
    if b1.button("✨ Revisar redacción", key=p + "rev_b", width="stretch", disabled=not ia,
                 help="Diccionario propio + LanguageTool (gratis)" + ("" if m.sensible else " · Gemini opcional")):
        _revisar(m, p, ia)
    if b2.button("📄 Generar Word", key=p + "gen_b", type="primary", width="stretch", disabled=bool(faltan) or doc is None):
        clave = v.get("destino") or (m.destino(v) if m.destino else None)
        dest = ctx["aut"].get(clave or "", {}) if clave else {}
        nombre = f"{m.id}_{str(r['identificador']).replace('/', '-')}_{db.hoy():%Y%m%d}.docx"
        db.registrar_documento(exp_id, m.id, m.nombre, dest.get("cargo"), json.dumps(v, default=str, ensure_ascii=False), K.usuario())
        st.session_state[p + "_doc"] = {"bytes": doc.bytes(), "nombre": nombre, "destino": dest.get("cargo"), "v": v}
    _panel_revision(m, p)
    _resultado(m, r, p)
    return {"completo": not faltan, "doc": bool(st.session_state.get(p + "_doc"))}


# ───────────────────────── Redacción ─────────────────────────
def _revisar(m, p, campos):
    rev = {}
    for c in campos:
        txt = st.session_state.get(p + c.key) or ""
        _, cambios = RD.revisar_local(txt)
        try:
            lt, err = RD.languagetool(txt), None
        except Exception as e:
            lt, err = [], f"LanguageTool no disponible ahora ({e}). Se aplicó solo el diccionario propio."
        rev[c.key] = {"label": c.label, "orig": txt, "local": cambios, "lt": lt, "err": err}
    st.session_state[p + "_rev"] = rev


def _panel_revision(m, p):
    rev = st.session_state.get(p + "_rev")
    if not rev:
        return
    with st.container(border=True):
        st.markdown('<div class="tr-g">✨ Sugerencias de redacción</div>', unsafe_allow_html=True)
        aplicar = {}
        for k, d in rev.items():
            n = len(d["local"]) + len(d["lt"])
            st.markdown(f"**{d['label']}** · {n or 'sin'} sugerencia{'s' if n != 1 else ''}")
            for a, b in d["local"]:
                st.markdown(f"<small>📘 <s>{ui.esc(a)}</s> → <b>{ui.esc(b)}</b> · diccionario D.G.I.I.</small>", unsafe_allow_html=True)
            elegidas = []
            for i, s in enumerate(d["lt"]):
                if st.checkbox(f"«{s['original']}» → «{s['sugerencia']}» · {s['mensaje'][:90]}", value=s["tipo"] == "Ortografía",
                               key=f"{p}lt_{k}_{i}"):
                    elegidas.append(s)
            if d["err"]:
                st.caption(d["err"])
            aplicar[k] = RD.revisar_local(RD.aplicar(d["orig"], elegidas))[0]
            if not m.sensible and RD.gemini_disponible():
                if st.button("🤖 Mejorar con Gemini", key=f"{p}gem_{k}"):
                    try:
                        with st.spinner("Gemini está revisando…"):
                            st.session_state[f"{p}gemtxt_{k}"] = RD.gemini_mejorar(aplicar[k], m.sensible)
                    except Exception as e:
                        st.error(str(e))
                if st.session_state.get(f"{p}gemtxt_{k}"):
                    st.text_area("Propuesta de Gemini (puede editarla)", key=f"{p}gemtxt_{k}", height=140)
                    aplicar[k] = st.session_state.get(f"{p}gemtxt_{k}") or aplicar[k]
            elif m.sensible:
                st.caption("🔒 Documento con datos personales: no se envía a IA externa.")
        c1, c2 = st.columns(2)
        if c1.button("✔️ Aplicar correcciones", key=p + "apl", type="primary", width="stretch"):
            st.session_state[p + "_aplicar"] = aplicar
            for k in rev:
                st.session_state.pop(f"{p}gemtxt_{k}", None)
            st.session_state.pop(p + "_rev", None)
            st.rerun()
        if c2.button("Descartar", key=p + "desc", width="stretch"):
            st.session_state.pop(p + "_rev", None)
            st.rerun()


# ───────────────────────── Resultado y registro del trámite ─────────────────────────
def _resultado(m, r, p):
    doc = st.session_state.get(p + "_doc")
    if not doc:
        return
    _h(5, "Imprimir y asentar")
    with st.container(border=True):
        st.download_button("⬇️ Descargar Word para imprimir", doc["bytes"], file_name=doc["nombre"], type="primary", width="stretch",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=p + "dl")
        st.caption(f"Hoja {'media oficio' if m.hoja == 'media' else 'oficio'} · quedó registrado en el historial del expediente.")
        if bool(r.get("tramitado")):
            st.markdown('<div class="tr-listo">✅ El expediente ya figura como TRAMITADO. Puede seguir generando documentos.</div>',
                        unsafe_allow_html=True)
            return
        c1, c2 = st.columns(2)
        acc = c1.selectbox("¿Qué se hizo?", C.ACCIONES_TRAMITE,
                           index=C.ACCIONES_TRAMITE.index(m.accion) if m.accion in C.ACCIONES_TRAMITE else 0, key=p + "acc")
        det = c2.text_input("Detalle", f"{m.nombre}" + (f" → {doc['destino']}" if doc.get("destino") else ""), key=p + "det")
        salida = bool(m.destino and doc.get("destino"))
        reg_sal = st.checkbox(f"Registrar también la SALIDA hacia {doc.get('destino')}", value=salida, disabled=not salida, key=p + "sal")
        if st.button("✅ Marcar como TRAMITADO", key=p + "ok", type="primary", width="stretch"):
            ahora = db.ahora()
            u = K.usuario()
            db.marcar_tramitado([int(r["id"])], acc, det, ahora, u, u)
            if reg_sal:
                desp = m.despacho(doc["v"]) if m.despacho else None
                db.registrar_movimiento(int(r["id"]), {"fecha_hora": ahora, "tipo": "SALIDA", "origen": C.DEP_PROPIA, "destino": doc["destino"],
                                                       "despacho": desp, "entregado_por": u, "observaciones": det}, "REMITIDO", u)
            st.session_state.pop(p + "_doc", None)
            st.toast(f"Expediente {r['identificador']} TRAMITADO", icon="✅")
            st.rerun()


def _historial(docs):
    if docs.empty:
        return
    with st.expander(f"🗂️ Documentos generados para este expediente ({len(docs)})"):
        for _, d in docs.head(20).iterrows():
            st.markdown(f"<small>{ui.fmt_fecha(d['generado_en'], True)} · <b>{ui.esc(d['titulo'])}</b>"
                        f"{' → ' + ui.esc(d['destino']) if d['destino'] else ''} · {ui.esc(d['generado_por'] or '')}</small>",
                        unsafe_allow_html=True)
