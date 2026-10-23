import re
import unicodedata
from datetime import date, datetime

import pandas as pd
import streamlit as st

import catalogos as C
import comun as K
import db
import reportes as R
import ui

ALIAS = {
    "nro_exp": ["NROEXP", "NEXP", "NUMEXP", "NUMERO", "NRO", "N", "NROEXPEDIENTE", "NEXPEDIENTE", "EXPEDIENTE", "NUMERODEEXPEDIENTE"],
    "folio": ["FOLIO", "FOJA", "NFOLIO", "NFOJA", "NROFOLIO", "FOLIOLIBRO"],
    "orden": ["ORDEN", "NORDEN", "NROORDEN", "ORD"],
    "ident": ["IDENTIFICACION", "IDENTIFICADOR", "NEXPFOLIOORDEN", "EXPFOLIOORDEN", "NROEXPFOLIOORDEN"],
    "libro": ["LIBRO", "NLIBRO", "NROLIBRO"],
    "anio": ["ANO", "ANIO", "YEAR"],
    "fecha_ingreso": ["FECHAINGRESO", "FECHA", "FECHADEINGRESO", "INGRESO", "FECHAENTRADA"],
    "tipo": ["TIPO", "TIPOEXPEDIENTE", "TIPODEEXPEDIENTE", "CLASE"],
    "origen": ["ORIGEN", "INICIADOEN"],
    "dependencia_origen": ["DEPENDENCIAORIGEN", "DEPENDENCIA", "PROCEDENCIA", "REMITENTE", "DEPENDENCIADEORIGEN", "VIENEDE"],
    "nro_exp_origen": ["NROEXPORIGEN", "NORIGEN", "NROORIGEN", "NUMEROORIGEN", "REFERENCIA"],
    "asunto": ["ASUNTO", "CARATULA", "EXTRACTO", "MOTIVO", "DETALLE"],
    "iniciador": ["INICIADOR", "CAUSANTE", "SOLICITANTE"],
    "prioridad": ["PRIORIDAD", "URGENCIA"],
    "fecha_termino": ["FECHATERMINO", "TERMINO", "VENCIMIENTO", "PLAZO"],
    "estado": ["ESTADO", "SITUACION"],
    "despacho": ["DESPACHO", "RESOLUCION", "SALIDACON"],
    "ubicacion_actual": ["UBICACIONACTUAL", "UBICACION", "ENPODERDE"],
    "destino": ["DESTINO", "INSTANCIA", "INSTANCIADESTINO", "SALIOA", "VAA", "SEELEVAA", "ELEVADOA"],
    "fojas": ["FOJAS", "CANTFOJAS", "CANTIDADDEFOJAS"],
    "observaciones": ["OBSERVACIONES", "OBS", "OBSERVACION", "NOTAS"],
}


def _norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z0-9]", "", s)


def mapear_columnas(df):
    inv = {a: k for k, v in ALIAS.items() for a in v}
    ren = {}
    for c in df.columns:
        k = inv.get(_norm(c))
        if k and k not in ren.values():
            ren[c] = k
    return df.rename(columns=ren)[list(ren.values())]


def _fecha(x):
    if x is None or (isinstance(x, float) and pd.isna(x)) or str(x).strip() in ("", "NaT", "nan"):
        return None
    if isinstance(x, (pd.Timestamp, datetime)):
        return x.date()
    if isinstance(x, date):
        return x
    s = str(x).strip()
    try:
        if re.match(r"^\d{4}-\d{1,2}-\d{1,2}", s):
            return pd.to_datetime(s[:10], format="%Y-%m-%d").date()
        return pd.to_datetime(s, dayfirst=True).date()
    except Exception:
        return "ERR"


def _int(x):
    try:
        if x is None or pd.isna(x) or str(x).strip() == "":
            return None
        return int(float(str(x).strip().replace(",", ".")))
    except Exception:
        return "ERR"


def _txt(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    s = str(x).strip()
    return s or None


def _match(valor, opciones, defecto):
    v = _norm(valor or "")
    if not v:
        return defecto
    for o in opciones:
        if o and (_norm(o) == v or _norm(o).startswith(v) or v in _norm(o)):
            return o
    return None


def validar(df_std, sec=None):
    """df_std con columnas estándar → (filas_para_importar, preview, tipos_nuevos, deps_nuevas)."""
    cfg = db.get_config()
    sec = C.sec_de(sec)
    exist = db.df_expedientes()
    exist = exist[exist["secretaria"].fillna(C.SEC_DEFAULT) == sec][["libro", "folio", "orden", "nro_exp", "anio", "identificador"]]
    clave_db = {(int(a), int(b), int(c)) for a, b, c in exist[["libro", "folio", "orden"]].itertuples(index=False)}
    tipos_cat = set(K.tipos(False))
    deps_cat = set(K.deps(False))
    filas, prev, vistos = [], [], set()
    tipos_nuevos, deps_nuevas = set(), set()
    for i, r in df_std.reset_index(drop=True).iterrows():
        g = r.get
        err, avisos = [], []
        nro, fol, ord_ = _int(g("nro_exp")), _int(g("folio")), _int(g("orden"))
        if g("ident") is not None and _txt(g("ident")) and None in (nro, fol, ord_):
            p = re.findall(r"\d+", str(g("ident")))
            if len(p) >= 3:
                nro, fol, ord_ = int(p[0]), int(p[1]), int(p[2])
        for nombre, v in (("N° Exp", nro), ("Folio", fol), ("Orden", ord_)):
            if v in (None, "ERR"):
                err.append(f"{nombre} inválido")
        libro = _int(g("libro"))
        libro = int(C.cfg_libro(cfg, sec, "libro_actual")) if libro in (None, "ERR") else libro
        fing = _fecha(g("fecha_ingreso"))
        if fing in (None, "ERR"):
            err.append("Fecha de ingreso inválida")
        anio = _int(g("anio"))
        if anio in (None, "ERR"):
            anio = fing.year if fing not in (None, "ERR") else db.hoy().year
        tipo = (_txt(g("tipo")) or "").upper()
        if not tipo:
            err.append("Falta tipo")
        elif tipo not in tipos_cat:
            tipos_nuevos.add(tipo)
            avisos.append("tipo nuevo")
        dep = (_txt(g("dependencia_origen")) or "").upper() or None
        if dep and dep not in deps_cat:
            deps_nuevas.add(dep)
            avisos.append("dependencia nueva")
        org_txt = _norm(_txt(g("origen")) or "")
        if org_txt:
            origen = C.ORIGENES[0] if ("INICI" in org_txt or "DIREC" in org_txt) else C.ORIGENES[1]
        else:
            origen = C.ORIGENES[0] if (not dep or dep == C.DEP_PROPIA) else C.ORIGENES[1]
        if origen == C.ORIGENES[0] and not dep:
            dep = C.DEP_PROPIA
        estado = _match(_txt(g("estado")), C.ESTADOS, "EN TRÁMITE")
        if estado is None:
            avisos.append(f"estado '{g('estado')}' → EN TRÁMITE")
            estado = "EN TRÁMITE"
        desp_raw = _txt(g("despacho"))
        desp = _match(desp_raw, [d for d in K.despachos() if d], None) if desp_raw else None
        if desp_raw and not desp:
            desp = desp_raw.upper()
        prio = "URGENTE TRÁMITE" if "URG" in _norm(_txt(g("prioridad")) or "") else "NORMAL"
        ft = _fecha(g("fecha_termino"))
        if ft == "ERR":
            avisos.append("fecha de término ignorada")
            ft = None
        ub = (_txt(g("ubicacion_actual")) or C.DEP_PROPIA).upper()
        if ub not in deps_cat:
            deps_nuevas.add(ub)
        dest = (_txt(g("destino")) or "").upper() or None
        if dest and dest not in deps_cat:
            deps_nuevas.add(dest)
        fojas = _int(g("fojas"))
        fojas = None if fojas == "ERR" else fojas

        estado_val = "OK"
        if not err:
            k = (libro, fol, ord_)
            if k in vistos:
                err.append("duplicado en el archivo")
            vistos.add(k)
            if k in clave_db:
                estado_val = "YA EXISTE"
        if err:
            estado_val = "ERROR"
        prev.append({
            "Validación": estado_val, "Detalle": "; ".join(err + avisos),
            "N° Exp/Folio/Orden": f"{nro}/{fol}/{ord_}", "Libro": libro, "Año": anio,
            "Ingreso": fing if fing != "ERR" else None, "Tipo": tipo, "Origen": dep, "Asunto": _txt(g("asunto")),
            "Estado": estado, "Ubicación": ub, "Destino": dest,
        })
        if not err:
            filas.append(dict(
                secretaria=sec, nro_exp=nro, folio=fol, orden=ord_, libro=libro, anio=anio, fecha_ingreso=fing, origen=origen,
                dependencia_origen=dep, nro_exp_origen=_txt(g("nro_exp_origen")), tipo=tipo, asunto=_txt(g("asunto")),
                iniciador=(_txt(g("iniciador")) or "").upper() or None, prioridad=prio, fecha_termino=ft, estado=estado,
                despacho=desp, destino=dest, ubicacion_actual=ub, fojas=fojas, observaciones=_txt(g("observaciones")),
            ))
    return filas, pd.DataFrame(prev), tipos_nuevos, deps_nuevas


def _vista_previa_e_importar(df_std, key):
    filas, prev, tn, dn = validar(df_std, st.session_state.get("cm_sec"))
    ok = int((prev["Validación"] == "OK").sum())
    ex = int((prev["Validación"] == "YA EXISTE").sum())
    er = int((prev["Validación"] == "ERROR").sum())
    ui.kpis([
        ("Filas leídas", len(prev), "", "#3B82F6"),
        ("Listas para cargar", ok, "nuevas", C.STATUS["ok"]),
        ("Ya existen", ex, "mismo libro/folio/orden", C.STATUS["warning"]),
        ("Con error", er, "no se importan", C.STATUS["critical"]),
    ])
    col_v = {"OK": C.STATUS["ok"], "YA EXISTE": C.STATUS["warning"], "ERROR": C.STATUS["critical"]}
    st.dataframe(
        prev.style.apply(lambda c: [f"color:{col_v.get(v, '')};font-weight:800" for v in c] if c.name == "Validación" else [""] * len(c), axis=0),
        hide_index=True, width="stretch", height=min(520, 38 + 35 * len(prev)),
    )
    if tn:
        st.warning("Tipos nuevos detectados: " + ", ".join(sorted(tn)))
    if dn:
        st.info("Dependencias nuevas detectadas: " + ", ".join(sorted(dn)))
    c1, c2 = st.columns(2)
    modo = c1.radio("Si el asiento ya existe", ["omitir", "actualizar"], horizontal=True, key=f"{key}_modo",
                    format_func=lambda x: "Omitir" if x == "omitir" else "Actualizar datos")
    agregar = c2.checkbox("Agregar tipos y dependencias nuevos al catálogo", value=True, key=f"{key}_cat")
    if st.button(f"🚀 Importar {ok + (ex if modo == 'actualizar' else 0)} asientos", type="primary", key=f"{key}_go", disabled=not filas):
        if agregar and (tn or dn):
            db.asegurar_catalogos(tn, dn)
        with st.spinner("Importando…"):
            n, a, o, errs = db.importar_expedientes(filas, modo, K.usuario())
        st.success(f"✔ {n} nuevos · {a} actualizados · {o} omitidos")
        for e in errs[:30]:
            st.error(e)
        return True
    return False


def render():
    ui.header("Carga Masiva", "Importación del libro de registro · Excel / CSV o transcripción directa")
    sec = K.elegir_secretaria("cm_sec", "📖 ¿De qué libro son los asientos que va a cargar?")
    if not sec:
        st.info("Elija primero el libro: la **Dirección (D.G.I.I.)** y el **I.E.S.P.** tienen numeración independiente.")
        return
    t1, t2 = st.tabs(["📄 Desde Excel / CSV", "⌨️ Transcripción rápida del libro"])

    with t1:
        st.download_button("📥 Descargar plantilla Excel", R.plantilla_carga(K.tipos(), K.deps()),
                           file_name="plantilla_carga_expedientes.xlsx")
        st.caption("Acepta encabezados flexibles (N° EXP, FOLIO, ORDEN, FECHA, TIPO, ASUNTO…) o una sola columna **IDENTIFICACIÓN** con el formato 545/120/3.")
        arch = st.file_uploader("Archivo del libro", type=["xlsx", "xls", "csv"], key="up_libro")
        if arch:
            try:
                if arch.name.lower().endswith(".csv"):
                    raw = pd.read_csv(arch, dtype=str, sep=None, engine="python")
                else:
                    xl = pd.ExcelFile(arch)
                    hoja = st.selectbox("Hoja", xl.sheet_names, key="up_hoja")
                    raw = xl.parse(hoja, dtype=object)
            except Exception as e:
                st.error(f"No se pudo leer el archivo: {e}")
                return
            raw = raw.dropna(how="all")
            std = mapear_columnas(raw)
            faltan = [c for c in ("tipo", "fecha_ingreso") if c not in std.columns]
            if not ({"nro_exp", "folio", "orden"} <= set(std.columns) or "ident" in std.columns):
                faltan.append("N° EXP / FOLIO / ORDEN (o IDENTIFICACIÓN)")
            st.caption("Columnas reconocidas: " + ", ".join(f"`{c}`" for c in std.columns))
            if faltan:
                st.error("Faltan columnas obligatorias: " + ", ".join(faltan))
            else:
                _vista_previa_e_importar(std, "xl")

    with t2:
        st.caption("Copie el libro tal como está: complete renglón por renglón. La numeración se propone sola según los renglones por folio configurados.")
        c1, c2, c3 = st.columns(3)
        n = c1.number_input("Renglones a transcribir", 1, 200, 10, key="tr_n")
        base = db.sugerir_numeracion(sec=sec)
        fecha_def = c2.date_input("Fecha por defecto", db.hoy(), format="DD/MM/YYYY", key="tr_f")
        if c3.button("🔄 Regenerar grilla", key="tr_reset") or "tr_df" not in st.session_state or st.session_state.get("tr_n_prev") != (n, sec):
            filas, num = [], base
            for _ in range(int(n)):
                filas.append(dict(nro_exp=num["nro_exp"], folio=num["folio"], orden=num["orden"], fecha_ingreso=fecha_def,
                                  tipo=None, dependencia_origen=None, asunto=None, iniciador=None, nro_exp_origen=None,
                                  prioridad="NORMAL", estado="EN TRÁMITE", despacho=None, destino=None, ubicacion_actual=C.DEP_PROPIA))
                num = db.avanzar(num)
            st.session_state["tr_df"] = pd.DataFrame(filas)
            st.session_state["tr_n_prev"] = (n, sec)
            st.session_state.pop("tr_editor", None)
        lista_dep = K.deps()
        ed = st.data_editor(
            st.session_state["tr_df"], key="tr_editor", num_rows="dynamic", hide_index=True, width="stretch",
            column_config={
                "nro_exp": st.column_config.NumberColumn("N° Exp", step=1, format="%d"),
                "folio": st.column_config.NumberColumn("Folio", step=1, format="%d"),
                "orden": st.column_config.NumberColumn("Orden", step=1, format="%d"),
                "fecha_ingreso": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY"),
                "tipo": st.column_config.SelectboxColumn("Tipo", options=K.tipos(), width="large"),
                "dependencia_origen": st.column_config.SelectboxColumn("Origen", options=lista_dep, width="medium"),
                "asunto": st.column_config.TextColumn("Asunto", width="large"),
                "iniciador": st.column_config.TextColumn("Iniciador"),
                "nro_exp_origen": st.column_config.TextColumn("N° origen"),
                "prioridad": st.column_config.SelectboxColumn("Prioridad", options=C.PRIORIDADES),
                "estado": st.column_config.SelectboxColumn("Estado", options=C.ESTADOS),
                "despacho": st.column_config.SelectboxColumn("Despacho", options=[d for d in K.despachos() if d]),
                "destino": st.column_config.SelectboxColumn("🎯 Destino", options=lista_dep, width="medium"),
                "ubicacion_actual": st.column_config.SelectboxColumn("Ubicación", options=lista_dep, width="medium"),
            },
        )
        completas = ed[ed["tipo"].notna() & (ed["tipo"].astype(str).str.strip() != "")]
        st.caption(f"{len(completas)} renglones con tipo cargado (los renglones sin tipo se ignoran).")
        if not completas.empty and _vista_previa_e_importar(completas, "tr"):
            st.session_state.pop("tr_df", None)
