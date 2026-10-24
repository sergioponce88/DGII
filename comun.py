"""Piezas compartidas entre vistas: navegación, selectores, formulario de movimiento y motor de alertas."""
from datetime import datetime, time, timedelta

import pandas as pd
import streamlit as st

import catalogos as C
import db
import reportes as R
import ui

LOGO = "assets/logo_policia.png"
LOGO_IESP = "assets/logo_iesp.png"

URL_APP = "https://sergioponce88.github.io/DGII/app/"  # app instalable (Android / iPhone)
PAG_TRABAJO = "🧭 Mi trabajo"
PAG_PANEL = "📊 Panel de Control"
PAG_NUEVO = "➕ Nuevo Expediente"
PAG_MOV = "🔁 Movimiento Rápido"
PAG_TRAMITAR = "📝 Tramitar"
PAG_COMISION = "🚚 Comisión (entregas)"
PAG_LIBRO = "📚 Libro de Registro"
PAG_FICHA = "🔎 Ficha de Expediente"
PAG_CURSOS = "🎓 Actividades y Personal"
PAG_ALERTAS = "🔔 Alertas y Agenda"
PAG_CARGA = "📥 Carga Masiva"
PAG_INFORMES = "📈 Informes"
PAG_CONFIG = "⚙️ Configuración"
PAGINAS = [PAG_TRABAJO, PAG_PANEL, PAG_NUEVO, PAG_MOV, PAG_TRAMITAR, PAG_COMISION, PAG_LIBRO, PAG_FICHA, PAG_CURSOS, PAG_ALERTAS, PAG_CARGA, PAG_INFORMES, PAG_CONFIG]


def usuario():
    import auth

    u = auth.actual()
    return auth.nombre_completo(u) if u else "SIN IDENTIFICAR"


def personas():
    """Personal conocido para autocompletar: usuarios activos + nombres ya usados en la hoja de ruta (más usados primero)."""
    import auth

    try:
        u = auth.df_usuarios()
        u = u[u["activo"].fillna(True).astype(bool)]
        base = [auth.nombre_completo(r) for r in u.to_dict("records")]
    except Exception:
        base = []
    try:
        h = db.leer("SELECT x, COUNT(*) AS n FROM (SELECT entregado_por AS x FROM movimientos UNION ALL "
                    "SELECT recibido_por FROM movimientos UNION ALL SELECT tramitado_por FROM expedientes) t "
                    "WHERE x IS NOT NULL AND TRIM(x) <> '' GROUP BY x ORDER BY n DESC LIMIT 400")
        hist = [str(x).strip().upper() for x in h["x"]]
    except Exception:
        hist = []
    vistos, out = set(), []
    for n in base + hist:
        if n and n not in vistos and n != "SIN IDENTIFICAR":
            vistos.add(n)
            out.append(n)
    return out


def campo_persona(col, label, key, defecto=None, ayuda=None):
    """Selector con búsqueda: elija del personal cargado o escriba uno nuevo (queda para la próxima)."""
    ops = personas()
    defecto = (defecto or "").strip().upper() or None
    if defecto and defecto not in ops:
        ops = [defecto] + ops
    v = col.selectbox(label, ops, index=ops.index(defecto) if defecto else None, key=key, accept_new_options=True,
                      placeholder="Escriba para buscar o cargue grado, apellido y nombre", help=ayuda)
    return (v or "").strip().upper()


def ir_a(pagina, exp_id=None):
    st.session_state["_goto"] = pagina
    if exp_id is not None:
        st.session_state["exp_sel"] = int(exp_id)
    st.rerun()


def deps(solo_activas=True):
    return db.df_dependencias(solo_activas)["nombre"].tolist()


def tipos(solo_activos=True):
    return db.df_tipos(solo_activos)["nombre"].tolist()


def tipo_es_curso(nombre):
    t = db.df_tipos()
    m = t[t["nombre"] == nombre]
    return bool(m["es_curso"].iloc[0]) if not m.empty else False


def tel_dep(nombre):
    d = db.df_dependencias()
    m = d[d["nombre"] == nombre]
    tel = m["telefono_wp"].iloc[0] if not m.empty else None
    return tel or db.get_config().get("wp_por_defecto") or None


def compartir_wp(mensaje, key, etiqueta="📲 Informar por WhatsApp", dep=None, ancho=False):
    """Botón que abre un panel: elegir a quién (dependencia con WhatsApp o contacto libre), revisar el texto y enviar."""
    import hashlib

    with st.popover(etiqueta, width="stretch" if ancho else "content"):
        d = db.df_dependencias()
        con_tel = d[d["telefono_wp"].fillna("").astype(str).str.strip() != ""]["nombre"].tolist() if not d.empty else []
        ops = ["📇 Elegir contacto en WhatsApp"] + con_tel
        a = st.selectbox("Enviar a", ops, index=ops.index(dep) if dep in ops else 0, key=f"wpd_{key}")
        h = hashlib.md5(mensaje.encode()).hexdigest()[:8]
        txt = st.text_area("Mensaje (puede editarlo)", mensaje, height=260, key=f"wpt_{key}_{h}")
        tel = None if a == ops[0] else tel_dep(a)
        st.link_button("📲 Abrir WhatsApp", R.link_whatsapp(txt, tel), type="primary", width="stretch")


def num(x, defecto=0):
    try:
        return defecto if x is None or pd.isna(x) else int(x)
    except (TypeError, ValueError):
        return defecto


def idx(lista, valor, defecto=0):
    try:
        return lista.index(valor)
    except ValueError:
        return defecto


def etiqueta_exp(r):
    a = r.get("asunto")
    asunto = a[:45] if isinstance(a, str) else ""
    sig = C.SECRETARIAS[C.sec_de(r.get("secretaria"))]["sigla"]
    return f"[{sig}] {r['identificador']} · {r['anio']} · {r['tipo']}" + (f" · {asunto}" if asunto else "")


def elegir_secretaria(key, label="¿A qué libro corresponde?", obligatorio=True):
    """Pregunta explícita: Dirección (D.G.I.I.) o Instituto (I.E.S.P.). Sin valor por defecto si es obligatorio."""
    ops = list(C.SECRETARIAS)
    return st.radio(label, ops, index=None if obligatorio else 0, horizontal=True, key=key,
                    format_func=lambda k: f"{C.SECRETARIAS[k]['sigla']} — {C.SECRETARIAS[k]['nombre']}")


def selector_expediente(key, df=None, label="Buscar expediente (N°, tipo o asunto):"):
    df = db.df_expedientes() if df is None else df
    if df.empty:
        st.info("Todavía no hay expedientes registrados.")
        return None
    ids = df["id"].tolist()
    etiquetas = {r["id"]: etiqueta_exp(r) for _, r in df.iterrows()}
    pre = st.session_state.get("exp_sel")
    i = ids.index(pre) if pre in ids else None
    sel = st.selectbox(label, ids, index=i, format_func=lambda x: etiquetas.get(x, str(x)), key=key, placeholder="Escriba para buscar…")
    if sel is None:
        return None
    st.session_state["exp_sel"] = sel
    return df[df["id"] == sel].iloc[0]


# ───────────────────────── Alta rápida de dependencia (➕) ─────────────────────────
def boton_nueva_dependencia(key, seleccionar_en=None):
    """Popover ➕ para agregar una dependencia sin salir de la pantalla.
    seleccionar_en: key del selectbox donde queda seleccionada la nueva dependencia."""
    with st.popover("➕", help="Agregar una dependencia que no está en la lista"):
        with st.form(f"nd_{key}", clear_on_submit=True):
            st.markdown("**Nueva dependencia**")
            nombre = st.text_input("Nombre", placeholder="Ej: COMISARÍA SECCIONAL 5°")
            c1, c2 = st.columns(2)
            sigla = c1.text_input("Sigla (opcional)")
            tel = c2.text_input("WhatsApp (opcional)")
            if st.form_submit_button("➕ Agregar"):
                if not nombre.strip():
                    st.error("Ingrese el nombre.")
                else:
                    n, existia = db.agregar_dependencia(nombre, sigla, None, tel)
                    if seleccionar_en:
                        st.session_state[f"_sel_{seleccionar_en}"] = n
                    st.toast(f"{'Ya existía' if existia else 'Agregada'}: {n}", icon="🏢")
                    st.rerun()


def despachos():
    """Despachos / resoluciones: los fijos + los agregados con ➕ (Configuración: despachos_extra)."""
    extra = [x.strip().upper() for x in str(db.get_config().get("despachos_extra") or "").split("|") if x.strip()]
    return C.DESPACHOS + [x for x in extra if x not in C.DESPACHOS]


def agregar_despacho(nombre):
    n = " ".join(str(nombre or "").split()).upper()
    if not n or n in despachos():
        return n
    extra = [x for x in str(db.get_config().get("despachos_extra") or "").split("|") if x.strip()]
    db.set_config({"despachos_extra": "|".join(extra + [n])})
    return n


def campo_despacho(col, label, key, defecto="", vacio="— Sin indicar —"):
    """Selector de despacho: elija de la lista o escriba uno nuevo (queda guardado para la próxima)."""
    nuevo = st.session_state.pop(f"_sel_{key}", None)
    ops = despachos()
    defecto = (defecto or "").strip().upper()
    if defecto and defecto not in ops:
        ops = ops + [defecto]
    if nuevo is not None and nuevo in ops:
        st.session_state[key] = nuevo
        extra = {}
    else:
        extra = {"index": idx(ops, defecto)}
    v = col.selectbox(label, ops, key=key, accept_new_options=True, **extra,
                      format_func=lambda d: d or vacio, help="Si no está, escríbalo y presione Enter, o agréguelo con ➕")
    v = " ".join(str(v or "").split()).upper()
    if v and v not in ops:
        agregar_despacho(v)
    return v


def boton_nuevo_despacho(key, seleccionar_en=None):
    """Popover ➕ para agregar un despacho / resolución que falta en la lista."""
    with st.popover("➕ Despacho", help="Agregar un despacho o resolución que no está en la lista"):
        with st.form(f"ndp_{key}", clear_on_submit=True):
            nombre = st.text_input("Nuevo despacho / resolución", placeholder="Ej: PARA SU CONOCIMIENTO Y EFECTOS")
            if st.form_submit_button("➕ Agregar"):
                if not nombre.strip():
                    st.error("Escriba el despacho.")
                else:
                    n = agregar_despacho(nombre)
                    if seleccionar_en:
                        st.session_state[f"_sel_{seleccionar_en}"] = n
                    st.toast(f"Despacho agregado: {n}", icon="➕")
                    st.rerun()


def preselect(key):
    """Aplica la selección pendiente de una dependencia recién agregada (antes de crear el widget)."""
    v = st.session_state.pop(f"_sel_{key}", None)
    if v is not None:
        st.session_state[key] = v


# ───────────────────────── Movimiento ─────────────────────────
def form_movimiento(exp, key):
    """Formulario de registro de movimiento (salida / ingreso / pase / archivo)."""
    lista_dep = deps()
    ub = exp.get("ubicacion_actual") or C.DEP_PROPIA
    c_a, c_b, c_c = st.columns([5, 1, 2], vertical_alignment="bottom")
    c_a.caption("¿Falta la dependencia o el despacho? Agréguelos con ➕")
    with c_b:
        boton_nueva_dependencia(f"mov_{key}")
    with c_c:
        boton_nuevo_despacho(f"mov_{key}", seleccionar_en=f"dp_{key}")
    with st.form(f"fmov_{key}", clear_on_submit=True):
        c1, c2 = st.columns(2)
        import auth

        tipos_ok = C.TIPOS_MOVIMIENTO if auth.puede("tramitar") else [t for t in C.TIPOS_MOVIMIENTO if t != "TRÁMITE"]
        estados_ok = C.ESTADOS if auth.puede("tramitar") else [e for e in C.ESTADOS if e != "TRAMITADO"]
        tipo_mov = c1.selectbox("Tipo de movimiento", tipos_ok, key=f"tm_{key}")
        defecto_dest = exp.get("destino") if isinstance(exp.get("destino"), str) and exp.get("destino") != ub else (
            C.DEP_PROPIA if ub != C.DEP_PROPIA else (lista_dep[1] if len(lista_dep) > 1 else lista_dep[0]))
        destino = c2.selectbox("Destino ➜", lista_dep, index=idx(lista_dep, defecto_dest), key=f"de_{key}")
        c3, c4 = st.columns(2)
        origen = c3.selectbox("Desde", lista_dep, index=idx(lista_dep, ub), key=f"or_{key}")
        despacho = campo_despacho(c4, "Despacho / Resolución", f"dp_{key}", exp.get("despacho"))
        c5, c6 = st.columns(2)
        f = c5.date_input("Fecha", db.hoy(), format="DD/MM/YYYY", key=f"fe_{key}")
        h = c6.time_input("Hora", db.ahora().time().replace(second=0), step=300, key=f"ho_{key}")
        c7, c8 = st.columns(2)
        entrega = campo_persona(c7, "Quién lo lleva / entrega", f"en_{key}", defecto=usuario())
        recibe = campo_persona(c8, "Quién lo recibe", f"re_{key}")
        c9, c10, c11 = st.columns([1, 1, 2])
        fojas = c9.number_input("Fojas", min_value=0, value=num(exp.get("fojas")), step=1, key=f"fo_{key}")
        urgente = c10.checkbox("⚡ Urgente trámite", value=exp.get("prioridad") == "URGENTE TRÁMITE", key=f"ur_{key}")
        estado_sug = C.ESTADO_POR_MOVIMIENTO.get(tipo_mov, exp.get("estado"))
        nuevo_estado = c11.selectbox("Estado resultante", ["(automático)"] + estados_ok, key=f"es_{key}",
                                     help="Automático: SALIDA→REMITIDO, INGRESO→EN TRÁMITE, PASE→EN DESPACHO, ARCHIVO→ARCHIVADO")
        obs = st.text_area("Observaciones", height=70, key=f"ob_{key}")
        ok = st.form_submit_button("💾 Registrar movimiento")
    if ok:
        mov = {
            "fecha_hora": datetime.combine(f, h if isinstance(h, time) else time(0, 0)),
            "tipo": tipo_mov,
            "origen": origen,
            "destino": destino,
            "despacho": despacho or None,
            "entregado_por": entrega.strip().upper() or None,
            "recibido_por": recibe.strip().upper() or None,
            "fojas": int(fojas) or None,
            "urgente": bool(urgente),
            "observaciones": obs.strip() or None,
        }
        estado_final = estado_sug if nuevo_estado == "(automático)" else nuevo_estado
        try:
            db.registrar_movimiento(int(exp["id"]), mov, estado_final, usuario())
            st.session_state[f"ultimo_mov_{key}"] = {"exp": dict(exp), "mov": mov}
            st.toast(f"Movimiento registrado: {exp['identificador']} ➜ {destino}", icon="✅")
            st.rerun()
        except Exception as e:
            st.error(f"No se pudo registrar el movimiento: {e}")

    ult = st.session_state.get(f"ultimo_mov_{key}")
    if ult and ult["exp"]["id"] == exp["id"]:
        m = ult["mov"]
        st.success(f"✔ Último movimiento: {m['tipo']} ➜ {m['destino']} ({ui.fmt_fecha(m['fecha_hora'], True)})")
        msg = R.msg_movimiento(ult["exp"], m)
        st.link_button("📲 Informar por WhatsApp", R.link_whatsapp(msg, tel_dep(m["destino"])))


# ───────────────────────── Reingreso ─────────────────────────
def form_reingreso(exp, key):
    """Vuelve a la Dirección un expediente ya registrado (tramitado o remitido): se actualiza el MISMO expediente."""
    ub = exp.get("ubicacion_actual") or "—"
    if bool(exp.get("tramitado")):
        ui.alerta("↩️", f"Vuelve un expediente TRAMITADO el {ui.fmt_fecha(exp.get('fecha_tramite'), True)} por {exp.get('tramitado_por') or '—'}",
                  f"{exp.get('accion_tramite') or ''} · {exp.get('detalle_tramite') or ''} — El trámite anterior queda en la hoja de ruta.",
                  C.STATUS["warning"])
    else:
        ui.alerta("↩️", f"Último lugar registrado: {ub}", "Se asienta el reingreso sobre el mismo N° / folio / orden.", C.STATUS["warning"])
    if int(num(exp.get("reingresos"))):
        st.caption(f"Este expediente ya reingresó {int(num(exp.get('reingresos')))} vez/veces.")
    lista_dep = deps()
    c_a, c_b, c_c = st.columns([5, 1, 2], vertical_alignment="bottom")
    c_a.caption("¿Falta la dependencia o el despacho? Agréguelos con ➕")
    with c_b:
        boton_nueva_dependencia(f"rei_{key}")
    with c_c:
        boton_nuevo_despacho(f"rei_{key}", seleccionar_en=f"rp_{key}")
    with st.form(f"frei_{key}", clear_on_submit=True):
        c1, c2 = st.columns(2)
        desde = c1.selectbox("Vuelve desde", lista_dep, index=idx(lista_dep, ub if ub != C.DEP_PROPIA else exp.get("destino")), key=f"rd_{key}")
        despacho = campo_despacho(c2, "Vuelve con (despacho / resolución)", f"rp_{key}")
        c3, c4 = st.columns(2)
        f = c3.date_input("Fecha de reingreso", db.hoy(), format="DD/MM/YYYY", key=f"rf_{key}")
        h = c4.time_input("Hora", db.ahora().time().replace(second=0), step=300, key=f"rh_{key}")
        c5, c6 = st.columns(2)
        trae = campo_persona(c5, "Quién lo trae", f"rt_{key}")
        recibe = campo_persona(c6, "Quién lo recibe", f"rr_{key}", defecto=usuario())
        c7, c8, c9 = st.columns([1, 1, 2])
        fojas = c7.number_input("Fojas actuales", min_value=0, value=num(exp.get("fojas")), step=1, key=f"rfo_{key}")
        urgente = c8.checkbox("⚡ Urgente", key=f"ru_{key}")
        f_term = c9.date_input("Nueva fecha de término (si es urgente)", None, format="DD/MM/YYYY", key=f"rft_{key}")
        motivo = st.text_area("Motivo / qué se solicita ahora", height=70, key=f"rm_{key}",
                              placeholder="Ej.: vuelve con informe de la División, para nueva providencia…")
        ok = st.form_submit_button("📥 Registrar reingreso", type="primary")
    if ok:
        mov = {
            "fecha_hora": datetime.combine(f, h if isinstance(h, time) else time(0, 0)),
            "tipo": "REINGRESO", "origen": desde, "destino": C.DEP_PROPIA, "despacho": despacho or None,
            "entregado_por": trae.strip().upper() or None, "recibido_por": recibe.strip().upper() or None,
            "fojas": int(fojas) or None, "urgente": bool(urgente), "observaciones": motivo.strip() or None,
        }
        try:
            db.registrar_movimiento(int(exp["id"]), mov, "EN TRÁMITE", usuario(), fecha_termino=f_term if urgente else None)
            st.session_state[f"ultimo_mov_{key}"] = {"exp": dict(exp), "mov": mov}
            st.toast(f"Reingreso registrado: {exp['identificador']} · queda PENDIENTE DE TRÁMITE", icon="📥")
            st.rerun()
        except Exception as e:
            st.error(f"No se pudo registrar el reingreso: {e}")
    ult = st.session_state.get(f"ultimo_mov_{key}")
    if ult and ult["exp"]["id"] == exp["id"] and ult["mov"]["tipo"] == "REINGRESO":
        st.success(f"✔ Reingreso desde {ult['mov']['origen']} ({ui.fmt_fecha(ult['mov']['fecha_hora'], True)}). Ya puede tramitarse nuevamente.")


# ───────────────────────── Trámite ─────────────────────────
MODOS_SALIDA = ["🚚 Lo lleva el comisionista", "📤 Sale ahora (lo entrego yo)", "🏠 Queda en la Dirección"]


def ui_salida(exp, key, modo_def=0, dest_texto=None):
    """Qué pasa con el expediente después del trámite, en el mismo lugar. Devuelve un dict con lo elegido."""
    modo = st.segmented_control("¿Y después?", MODOS_SALIDA, default=MODOS_SALIDA[modo_def], key=f"sal_m_{key}") or MODOS_SALIDA[2]
    if modo == MODOS_SALIDA[2]:
        return {"modo": "queda"}
    lista = [d for d in deps() if d != C.DEP_PROPIA]
    defecto = dep_parecida(dest_texto, lista) or exp.get("entrega_destino") or exp.get("destino")
    c1, c2 = st.columns(2)
    dest = c1.selectbox("Destino ➜", lista, index=idx(lista, defecto), key=f"sal_d_{key}")
    desp = campo_despacho(c2, "Despacho con el que sale", f"sal_p_{key}", exp.get("despacho"))
    if modo == MODOS_SALIDA[0]:
        ind = st.text_input("Indicaciones para el comisionista (opcional)", key=f"sal_i_{key}",
                            placeholder="Ej.: entregar en mano al Secretario")
        return {"modo": "comision", "destino": dest, "despacho": desp, "ind": ind}
    c3, c4 = st.columns([3, 1])
    recibe = campo_persona(c3, "Quién lo recibe", f"sal_r_{key}")
    fojas = c4.number_input("Fojas", min_value=0, value=num(exp.get("fojas")), step=1, key=f"sal_f_{key}")
    return {"modo": "sale", "destino": dest, "despacho": desp, "recibe": recibe, "fojas": int(fojas)}


def despachar(exp, sal, quien=None, cuando=None):
    """Ejecuta lo elegido en ui_salida: encargo al comisionista o salida inmediata (queda en la hoja de ruta)."""
    u = usuario()
    if sal.get("modo") == "comision":
        db.solicitar_entrega(int(exp["id"]), sal["destino"], sal.get("despacho") or None, sal.get("ind"), u)
        return f"encargado al comisionista → {sal['destino']}"
    if sal.get("modo") == "sale":
        if bool(exp.get("entrega_pendiente")):
            db.cancelar_entrega(int(exp["id"]), u)
        mov = {"fecha_hora": cuando or db.ahora(), "tipo": "SALIDA", "origen": C.DEP_PROPIA, "destino": sal["destino"],
               "despacho": sal.get("despacho") or None, "entregado_por": quien or u, "recibido_por": sal.get("recibe") or None,
               "fojas": sal.get("fojas") or None, "urgente": exp.get("prioridad") == "URGENTE TRÁMITE", "observaciones": None}
        db.registrar_movimiento(int(exp["id"]), mov, "REMITIDO", u)
        st.session_state["_ult_salida"] = {"exp": dict(exp), "mov": mov}
        return f"salió → {sal['destino']}"
    return "queda en la Dirección"


def _aviso_salida(exp):
    ult = st.session_state.get("_ult_salida")
    if ult and ult["exp"]["id"] == exp["id"]:
        m = ult["mov"]
        st.success(f"✔ Salió ➜ {m['destino']} ({ui.fmt_fecha(m['fecha_hora'], True)})" + (f" · recibió {m['recibido_por']}" if m.get("recibido_por") else ""))
        st.link_button("📲 Avisar por WhatsApp", R.link_whatsapp(R.msg_movimiento(ult["exp"], m), tel_dep(m["destino"])))


def form_tramite(exp, key):
    """Trámite + salida en un solo paso: qué se hizo y a dónde va (comisionista, sale ahora o queda)."""
    import auth

    en_casa = (exp.get("ubicacion_actual") or C.DEP_PROPIA) == C.DEP_PROPIA
    if bool(exp.get("tramitado")):
        ui.alerta("✅", f"TRAMITADO el {ui.fmt_fecha(exp.get('fecha_tramite'), True)} por {exp.get('tramitado_por') or '—'}",
                  f"{exp.get('accion_tramite') or ''} · {exp.get('detalle_tramite') or ''}", C.STATUS["ok"])
        _aviso_salida(exp)
        if not auth.puede("tramitar"):
            return
        if bool(exp.get("entrega_pendiente")):
            ui.alerta("🚚", f"Encargado al comisionista → {exp.get('entrega_destino') or '—'}",
                      f"Pedido por {exp.get('entrega_solicitada_por') or '—'} · {ui.fmt_fecha(exp.get('entrega_solicitada_en'), True)}",
                      C.STATUS["warning"])
        if en_casa:
            with st.container(border=True):
                st.markdown("**📦 Despachar el expediente**" + (" (cambia el encargo)" if exp.get("entrega_pendiente") else ""))
                sal = ui_salida(exp, f"ya_{key}", 1 if exp.get("entrega_pendiente") else 0)
                b1, b2 = st.columns(2)
                if sal["modo"] != "queda" and b1.button("✅ Despachar", key=f"ya_ok_{key}", type="primary", width="stretch"):
                    st.toast(f"Exp. {exp['identificador']}: {despachar(exp, sal)}", icon="✅")
                    st.rerun()
                if exp.get("entrega_pendiente") and b2.button("Cancelar el encargo", key=f"enc_cancel_{key}", width="stretch"):
                    db.cancelar_entrega(int(exp["id"]), usuario())
                    st.rerun()
        with st.expander("↺ Anular la marca de tramitado"):
            motivo = st.text_input("Motivo", key=f"anu_m_{key}")
            if st.button("Anular", key=f"anu_b_{key}"):
                db.marcar_tramitado([int(exp["id"])], None, motivo, db.ahora(), usuario(), usuario(), revertir=True)
                st.rerun()
        return

    ui.alerta("⏳", "PENDIENTE DE TRÁMITE", "Asiente lo realizado y a dónde va, todo en un solo paso.", C.STATUS["warning"])
    if not auth.puede("tramitar"):
        auth.aviso_sin_permiso("la marca de tramitado")
        return
    if st.button("📝 Tramitar con modelos (nota en Word)", key=f"ir_tram_{key}", width="stretch"):
        st.session_state["tram_sel"] = int(exp["id"])
        ir_a(PAG_TRAMITAR, exp["id"])
    with st.container(border=True):
        st.markdown("**✅ Tramitar y despachar**")
        c1, c2 = st.columns(2)
        accion = c1.selectbox("¿Qué se hizo?", C.ACCIONES_TRAMITE, key=f"tr_ac_{key}")
        quien = campo_persona(c2, "Tramitado por", f"tr_q_{key}", defecto=usuario())
        det = st.text_input("Detalle (N° de nota, providencia, a quién se respondió…)", key=f"tr_d_{key}")
        with st.expander("🕒 Otra fecha u hora (si no fue ahora)"):
            c3, c4 = st.columns(2)
            f = c3.date_input("Fecha", db.hoy(), format="DD/MM/YYYY", key=f"tr_f_{key}")
            h = c4.time_input("Hora", db.ahora().time().replace(second=0), step=300, key=f"tr_h_{key}")
        sal = ui_salida(exp, f"tr_{key}", 0 if en_casa else 2) if en_casa else {"modo": "queda"}
        if st.button("✅ Tramitar" + ("" if sal["modo"] == "queda" else " y despachar"), key=f"tr_ok_{key}", type="primary", width="stretch"):
            cuando = datetime.combine(f, h if isinstance(h, time) else time(0, 0))
            q = quien or usuario()
            db.marcar_tramitado([int(exp["id"])], accion, det.strip() or None, cuando, q, usuario())
            res = despachar(exp, sal, q, cuando + timedelta(minutes=1))
            for k in list(st.session_state):
                if k.endswith(f"_{key}") and k.startswith(("tr_", "sal_")):
                    st.session_state.pop(k, None)
            st.toast(f"Exp. {exp['identificador']} tramitado · {res}", icon="✅")
            st.rerun()


# ───────────────────────── PDF del expediente (Google Drive) ─────────────────────────
def panel_pdf(exp, key):
    import gdrive

    exp_id = int(exp["id"])
    adj = db.df_adjuntos(exp_id)
    if not adj.empty:
        ult = adj.iloc[0]
        st.link_button(f"📄 Ver PDF del expediente (v{int(ult['version'])})", ult["link"])
        with st.expander(f"🗂️ Versiones ({len(adj)})"):
            for _, a in adj.iterrows():
                st.markdown(f"**v{int(a['version'])}** · {ui.fmt_fecha(a['subido_en'], True)} · {ui.esc(a['subido_por'])} · "
                            f"{num(a['paginas']) or '?'} fojas · {(num(a['bytes']) or 0) / 1e6:.1f} MB · "
                            f"[abrir]({a['link']}) {('· ' + ui.esc(a['descripcion'])) if a['descripcion'] else ''}")
    else:
        st.caption("Este expediente todavía no tiene PDF digitalizado.")

    if not gdrive.conectado():
        st.info("Para subir el PDF, primero conecte Google Drive en ⚙️ Configuración → ☁️ Google Drive.")
        return
    ui.seccion("📎 Subir expediente digitalizado")
    modo = st.segmented_control("Origen", ["📄 Archivo PDF", "📷 Fotos de las fojas"], default="📄 Archivo PDF", key=f"pdfm_{key}")
    if modo == "📷 Fotos de las fojas":
        arch = st.file_uploader("Fotos en orden (en el celular podés usar la cámara)", type=["jpg", "jpeg", "png", "webp"],
                                accept_multiple_files=True, key=f"pdfi_{key}")
    else:
        arch = st.file_uploader("PDF del expediente (si elegís varios, se unen en uno)", type=["pdf"],
                                accept_multiple_files=True, key=f"pdff_{key}")
    desc = st.text_input("Descripción (opcional)", placeholder="Ej: con informe de la División y providencia", key=f"pdfd_{key}")
    if arch and st.button(f"☁️ Subir a Google Drive ({len(arch)} archivo/s)", type="primary", key=f"pdfb_{key}"):
        try:
            with st.spinner("Preparando PDF…"):
                if modo == "📷 Fotos de las fojas":
                    contenido, paginas = gdrive.imagenes_a_pdf(arch), len(arch)
                else:
                    contenido = arch[0].getvalue() if len(arch) == 1 else gdrive.unir_pdfs(arch)
                    try:
                        from pypdf import PdfReader
                        import io as _io
                        paginas = len(PdfReader(_io.BytesIO(contenido)).pages)
                    except Exception:
                        paginas = None
            ver = (0 if adj.empty else int(adj["version"].max())) + 1
            nombre = f"{exp['nro_exp']}-{exp['folio']}-{exp['orden']}_{exp['anio']}_v{ver}.pdf"
            with st.spinner(f"Subiendo {len(contenido) / 1e6:.1f} MB a Google Drive…"):
                fid, link = gdrive.subir_pdf(nombre, contenido, int(exp["anio"]), f"{exp['tipo']} · {exp.get('asunto') or ''} {desc}".strip())
            db.registrar_adjunto(exp_id, nombre, fid, link, len(contenido), paginas, desc.strip() or None, usuario())
            st.toast(f"PDF subido: {nombre}", icon="☁️")
            st.rerun()
        except gdrive.DriveError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"No se pudo subir el archivo: {e}")


# ───────────────────────── Personal (editor) ─────────────────────────
COLS_PERSONAL = ["apellido", "nombre", "jerarquia", "dni", "division", "provincia", "rol"]


def editor_personal(df_ini, key):
    if df_ini is None or df_ini.empty:
        df_ini = pd.DataFrame(columns=COLS_PERSONAL)
    df_ini = df_ini[COLS_PERSONAL].copy()
    return st.data_editor(
        df_ini,
        key=key,
        num_rows="dynamic",
        width="stretch",
        hide_index=True,
        column_config={
            "apellido": st.column_config.TextColumn("Apellido", required=True),
            "nombre": st.column_config.TextColumn("Nombre"),
            "jerarquia": st.column_config.SelectboxColumn("Jerarquía / Grado", options=list(C.JERARQUIAS)),
            "dni": st.column_config.TextColumn("DNI"),
            "division": st.column_config.TextColumn("División a la que pertenece"),
            "provincia": st.column_config.SelectboxColumn("Provincia / Fuerza", options=C.PROVINCIAS, default="TUCUMÁN"),
            "rol": st.column_config.SelectboxColumn("Rol", options=C.ROLES_PERSONAL, default="CURSANTE"),
        },
    )


def limpiar_personal(df):
    out = []
    for _, r in df.iterrows():
        ape = str(r.get("apellido") or "").strip()
        if not ape or ape.lower() == "nan":
            continue
        jer = r.get("jerarquia") if isinstance(r.get("jerarquia"), str) else "OTRO"
        out.append(
            {
                "apellido": ape.upper(),
                "nombre": str(r.get("nombre") or "").strip().title(),
                "jerarquia": jer,
                "escalafon": C.escalafon(jer),
                "dni": "".join(ch for ch in str(r.get("dni") or "") if ch.isdigit()) or None,
                "division": str(r.get("division") or "").strip().upper() or None,
                "provincia": r.get("provincia") if isinstance(r.get("provincia"), str) else "TUCUMÁN",
                "rol": r.get("rol") if isinstance(r.get("rol"), str) else "CURSANTE",
            }
        )
    return out


# ───────────────────────── Motor de alertas ─────────────────────────
NIVELES = {
    "critical": ("🔴", C.STATUS["critical"], 0),
    "serious": ("🟠", C.STATUS["serious"], 1),
    "warning": ("🟡", C.STATUS["warning"], 2),
    "info": ("🔵", "#3B82F6", 3),
}


def calcular_alertas():
    cfg = db.get_config()
    n_aviso = int(cfg["dias_aviso_cursos"])
    n_est = int(cfg["dias_estancado"])
    h = pd.Timestamp(db.hoy())
    al = []

    def add(nivel, titulo, detalle, fecha, exp_id=None, dep=None, cat=""):
        al.append({"nivel": nivel, "titulo": titulo, "detalle": detalle, "fecha": fecha, "exp_id": exp_id, "dep": dep, "cat": cat})

    cur = db.df_cursos()
    for _, c in cur.iterrows():
        if c["estado"] in ("NO AUTORIZADO", "SUSPENDIDO"):
            continue
        ini, fin = c["fecha_inicio"], c["fecha_fin"]
        tipo_a = c["tipo_actividad"] if isinstance(c.get("tipo_actividad"), str) else "CURSO"
        ref = f"Exp. {c['identificador']}" if pd.notna(c.get("identificador")) else "Sin expediente"
        lugar = f"{c.get('lugar') or 's/lugar'} · {c.get('modalidad') or ''} · {int(c.get('cant_personal') or 0)} efectivos"
        if pd.notna(ini):
            d = (ini - h).days
            if d == 0:
                add("critical", f"HOY inicia · {tipo_a}: {c['nombre']}", f"{ref} · {lugar}", ini, c.get("expediente_id"), cat="Actividades")
            elif 0 < d <= n_aviso:
                sin_aut = c["estado"] == "SOLICITADO" and "SIN REQUERIMIENTO" not in str(c.get("requerimiento") or "")
                add("serious" if sin_aut else "warning",
                    f"En {d} día{'s' if d > 1 else ''} inicia · {tipo_a}: {c['nombre']}" + (" · SIN AUTORIZACIÓN" if sin_aut else ""),
                    f"{ref} · {ui.fmt_fecha(ini)} · {lugar}", ini, c.get("expediente_id"), cat="Actividades")
        if pd.notna(fin) and (fin - h).days == 0 and not (pd.notna(ini) and ini == fin):
            add("info", f"HOY finaliza · {tipo_a}: {c['nombre']}", f"{ref} · {lugar}", fin, c.get("expediente_id"), cat="Actividades")

    exp = db.df_expedientes()
    abiertos = exp[~exp["estado"].isin(C.ESTADOS_CERRADOS)] if not exp.empty else exp
    for _, e in abiertos.iterrows():
        txt = f"{e['tipo']} · {e.get('asunto') or ''} · 📍 {e.get('ubicacion_actual') or '—'}"
        if pd.notna(e["fecha_termino"]) and not bool(e.get("tramitado")):  # tramitado = el plazo ya se cumplió
            d = (e["fecha_termino"] - h).days
            if d < 0:
                add("critical", f"VENCIDO hace {-d} d · Exp. {e['identificador']}", txt, e["fecha_termino"], e["id"], e.get("ubicacion_actual"), "Vencimientos")
            elif d <= 2:
                add("serious", f"Vence {'HOY' if d == 0 else f'en {d} d'} · Exp. {e['identificador']}", txt, e["fecha_termino"], e["id"], e.get("ubicacion_actual"), "Vencimientos")
        ref = e["ult_mov"] if pd.notna(e["ult_mov"]) else e["fecha_ingreso"]
        if pd.notna(ref):
            ds = (h - ref.normalize()).days
            urg = e["prioridad"] == "URGENTE TRÁMITE"
            en_casa = (e.get("ubicacion_actual") or C.DEP_PROPIA) == C.DEP_PROPIA
            tram = bool(e.get("tramitado"))
            if en_casa and not tram:
                # Lo único que depende de la Dirección: está acá y todavía no se tramitó
                if ds > (2 if urg else n_est):
                    add("serious" if urg else "info", f"{ds} días sin tramitar · Exp. {e['identificador']}" + (" ⚡" if urg else ""),
                        txt, ref, e["id"], e.get("ubicacion_actual"), "Estancados")
            elif en_casa and tram and ds > 3:
                pend = " · encargado al comisionista" if bool(e.get("entrega_pendiente")) else " · falta encargar la entrega"
                add("info", f"Tramitado hace {ds} días y sigue en la Dirección · Exp. {e['identificador']}", txt + pend, ref, e["id"],
                    e.get("ubicacion_actual"), "Para entregar")
            elif not en_casa and ds > 2 * n_est:
                # Ya salió: solo un recordatorio informativo si pasa mucho tiempo sin que vuelva ni se mueva
                add("info", f"{ds} días en {e.get('ubicacion_actual')} sin novedades · Exp. {e['identificador']}", txt, ref, e["id"],
                    e.get("ubicacion_actual"), "Fuera de la Dirección")

    ev = db.df_eventos()
    for _, v in ev[~ev["completado"].astype(bool)].iterrows() if not ev.empty else []:
        d = (v["fecha"] - h).days
        det = f"{v.get('tipo') or ''} · {v.get('hora') or ''} · {v.get('lugar') or ''}" + (f" · Exp. {v['identificador']}" if pd.notna(v.get("identificador")) else "")
        if d == 0:
            add("critical", f"HOY: {v['titulo']}", det, v["fecha"], v.get("expediente_id"), cat="Agenda")
        elif 0 < d <= int(v.get("dias_aviso") or 3):
            add("warning", f"En {d} día{'s' if d > 1 else ''}: {v['titulo']}", det, v["fecha"], v.get("expediente_id"), cat="Agenda")
        elif d < 0:
            add("info", f"Pendiente de cerrar: {v['titulo']}", det, v["fecha"], v.get("expediente_id"), cat="Agenda")

    al.sort(key=lambda a: (NIVELES[a["nivel"]][2], a["fecha"] if pd.notna(a["fecha"]) else h))
    return al


# ───────────────────────── Encargo de entrega al comisionista ─────────────────────────
def dep_parecida(texto, lista):
    """Dependencia de la lista que comparte palabras distintivas con el texto (p. ej. el cargo del destinatario).
    Las palabras genéricas (Dirección, Escuela, General…) no cuentan, para no encargar a un lugar equivocado."""
    import re as _re

    genericas = {"DEL", "LOS", "LAS", "POLICIA", "POLICÍA", "PROVINCIA", "DIRECCIÓN", "DIRECCION", "DIRECTOR", "DIRECTORA", "GENERAL",
                 "ESCUELA", "DEPARTAMENTO", "DIVISIÓN", "DIVISION", "CENTRO", "JEFE", "SEÑOR", "SEÑORA", "UNIDAD", "OFICINA", "SECCIÓN"}
    pal = lambda t: {w for w in _re.findall(r"[A-ZÁÉÍÓÚÑ0-9]{3,}", str(t or "").upper()) if w not in genericas}  # noqa: E731
    t = str(texto or "").upper()
    p = pal(t)
    if _re.search(r"\bSUBJEFE DE POLIC", t):
        p.add("SUBJEFATURA")
    elif _re.search(r"\bJEFE DE POLIC", t):
        p.add("JEFATURA")
    mejor = max(lista, key=lambda d: len(p & pal(d)), default=None) if p else None
    return mejor if mejor and p & pal(mejor) else None


def ui_encargo(exp, key, destino_texto=None, activo=True):
    """Casilla «Encargar la entrega al comisionista» + destino. Devuelve (destino o None, indicaciones)."""
    if bool(exp.get("entrega_pendiente")):
        st.caption(f"🚚 Ya está encargado al comisionista → {exp.get('entrega_destino') or '—'}")
        return None, None
    lista = [d for d in deps() if d != C.DEP_PROPIA]
    if not lista:
        return None, None
    enc = st.checkbox("🚚 Encargar la entrega al comisionista (él registra quién lo recibe)", value=activo, key=f"{key}_enc_chk")
    if not enc:
        return None, None
    defecto = dep_parecida(destino_texto, lista) or exp.get("destino")
    c1, c2 = st.columns([1, 1])
    dest = c1.selectbox("Llevar a", lista, index=idx(lista, defecto), key=f"{key}_enc_dest")
    ind = c2.text_input("Indicaciones para el comisionista (opcional)", key=f"{key}_enc_ind", placeholder="Ej.: entregar en mano al Secretario")
    return dest, ind
