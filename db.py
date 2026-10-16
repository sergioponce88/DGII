"""Capa de datos: Supabase (PostgreSQL) vía psycopg2. Esquema, lecturas cacheadas, escrituras y numeración del libro."""
import contextlib
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import psycopg2
import streamlit as st

import catalogos as C

TZ = ZoneInfo("America/Argentina/Buenos_Aires")


def ahora():
    return datetime.now(TZ).replace(tzinfo=None, microsecond=0)


def hoy():
    return ahora().date()


# ───────────────────────── Conexión ─────────────────────────
def _dsn():
    try:
        v = st.secrets.get("SUPABASE_URL")
    except Exception:
        v = None
    return v or os.getenv("SUPABASE_URL")


@contextlib.contextmanager
def conexion():
    dsn = _dsn()
    if not dsn:
        raise RuntimeError("Falta SUPABASE_URL en los secrets de Streamlit.")
    conn = psycopg2.connect(dsn, connect_timeout=10)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def leer(sql, params=None):
    with conexion() as c, c.cursor() as cur:
        cur.execute(sql, [_py(p) for p in params] if params else params)
        cols = [d[0] for d in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=cols)


def ejecutar(sql, params=None):
    with conexion() as c, c.cursor() as cur:
        cur.execute(sql, [_py(p) for p in params] if params else params)
        return cur.fetchone() if cur.description else None


def _py(v):
    """psycopg2 no adapta tipos numpy ni NaT/NaN: los convierte a nativos de Python."""
    if v is None or v is pd.NaT:
        return None
    if isinstance(v, float) and pd.isna(v):
        return None
    if hasattr(v, "item") and not isinstance(v, (str, bytes)):
        try:
            v = v.item()
        except (ValueError, AttributeError):
            pass
        if isinstance(v, float) and pd.isna(v):
            return None
    return v


def _insert(cur, tabla, data, returning="id"):
    cols = list(data.keys())
    sql = f"INSERT INTO {tabla} ({', '.join(cols)}) VALUES ({', '.join(['%s'] * len(cols))})"
    if returning:
        sql += f" RETURNING {returning}"
    cur.execute(sql, [_py(data[k]) for k in cols])
    return cur.fetchone() if returning else None


def _update(cur, tabla, data, id_):
    cols = list(data.keys())
    sets = ", ".join(f"{k} = %s" for k in cols)
    cur.execute(f"UPDATE {tabla} SET {sets} WHERE id = %s", [_py(data[k]) for k in cols] + [_py(id_)])


def invalidar():
    st.cache_data.clear()


# ───────────────────────── Esquema ─────────────────────────
ESQUEMA = """
CREATE TABLE IF NOT EXISTS config (clave TEXT PRIMARY KEY, valor TEXT);

CREATE TABLE IF NOT EXISTS dependencias (
    id SERIAL PRIMARY KEY,
    nombre TEXT UNIQUE NOT NULL,
    sigla TEXT,
    color TEXT DEFAULT '#64748B',
    telefono_wp TEXT,
    activa BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS tipos_expediente (
    id SERIAL PRIMARY KEY,
    nombre TEXT UNIQUE NOT NULL,
    grupo TEXT DEFAULT 'Otros',
    origen TEXT DEFAULT 'AMBOS',
    es_curso BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS expedientes (
    id SERIAL PRIMARY KEY,
    nro_exp INTEGER NOT NULL,
    folio INTEGER NOT NULL,
    orden INTEGER NOT NULL,
    libro INTEGER NOT NULL DEFAULT 1,
    anio INTEGER NOT NULL,
    identificador TEXT GENERATED ALWAYS AS (nro_exp::text || '/' || folio::text || '/' || orden::text) STORED,
    fecha_ingreso DATE NOT NULL,
    origen TEXT NOT NULL,
    dependencia_origen TEXT,
    nro_exp_origen TEXT,
    tipo TEXT NOT NULL,
    asunto TEXT,
    iniciador TEXT,
    prioridad TEXT DEFAULT 'NORMAL',
    fecha_termino DATE,
    estado TEXT DEFAULT 'EN TRÁMITE',
    despacho TEXT,
    ubicacion_actual TEXT,
    fojas INTEGER,
    observaciones TEXT,
    creado_por TEXT,
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW(),
    CONSTRAINT ux_libro_folio_orden UNIQUE (libro, folio, orden)
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_exp_nro_anio ON expedientes (nro_exp, anio);
CREATE INDEX IF NOT EXISTS ix_exp_tipo ON expedientes (tipo);
CREATE INDEX IF NOT EXISTS ix_exp_estado ON expedientes (estado);

ALTER TABLE expedientes ADD COLUMN IF NOT EXISTS tramitado BOOLEAN DEFAULT FALSE;
ALTER TABLE expedientes ADD COLUMN IF NOT EXISTS fecha_tramite TIMESTAMP;
ALTER TABLE expedientes ADD COLUMN IF NOT EXISTS tramitado_por TEXT;
ALTER TABLE expedientes ADD COLUMN IF NOT EXISTS accion_tramite TEXT;
ALTER TABLE expedientes ADD COLUMN IF NOT EXISTS detalle_tramite TEXT;
ALTER TABLE expedientes ADD COLUMN IF NOT EXISTS destino TEXT;

CREATE TABLE IF NOT EXISTS movimientos (
    id SERIAL PRIMARY KEY,
    expediente_id INTEGER NOT NULL REFERENCES expedientes (id) ON DELETE CASCADE,
    fecha_hora TIMESTAMP NOT NULL,
    tipo TEXT NOT NULL,
    origen TEXT,
    destino TEXT,
    despacho TEXT,
    entregado_por TEXT,
    recibido_por TEXT,
    fojas INTEGER,
    urgente BOOLEAN DEFAULT FALSE,
    observaciones TEXT,
    registrado_por TEXT,
    creado_en TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_mov_exp ON movimientos (expediente_id);

CREATE TABLE IF NOT EXISTS cursos (
    id SERIAL PRIMARY KEY,
    expediente_id INTEGER REFERENCES expedientes (id) ON DELETE CASCADE,
    categoria TEXT,
    nombre TEXT NOT NULL,
    division_dicta TEXT,
    lugar TEXT,
    ambito TEXT DEFAULT 'EN LA PROVINCIA',
    fecha_inicio DATE,
    fecha_fin DATE,
    modalidad TEXT,
    requerimiento TEXT,
    planificacion_anual BOOLEAN DEFAULT FALSE,
    estado TEXT DEFAULT 'SOLICITADO',
    observaciones TEXT,
    creado_en TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS personal_curso (
    id SERIAL PRIMARY KEY,
    curso_id INTEGER NOT NULL REFERENCES cursos (id) ON DELETE CASCADE,
    apellido TEXT,
    nombre TEXT,
    jerarquia TEXT,
    escalafon TEXT,
    dni TEXT,
    division TEXT,
    provincia TEXT DEFAULT 'TUCUMÁN',
    rol TEXT DEFAULT 'CURSANTE'
);
CREATE INDEX IF NOT EXISTS ix_pers_dni ON personal_curso (dni);

CREATE TABLE IF NOT EXISTS eventos (
    id SERIAL PRIMARY KEY,
    expediente_id INTEGER REFERENCES expedientes (id) ON DELETE CASCADE,
    curso_id INTEGER REFERENCES cursos (id) ON DELETE CASCADE,
    titulo TEXT NOT NULL,
    tipo TEXT,
    fecha DATE NOT NULL,
    hora TEXT,
    lugar TEXT,
    descripcion TEXT,
    dias_aviso INTEGER DEFAULT 3,
    completado BOOLEAN DEFAULT FALSE,
    creado_en TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS auditoria (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP DEFAULT NOW(),
    usuario TEXT,
    accion TEXT,
    detalle TEXT
);
"""


VERSION_ESQUEMA = __import__("hashlib").md5(ESQUEMA.encode()).hexdigest()[:10]


@st.cache_resource(show_spinner="Actualizando la estructura de la base…")
def init_db(version=VERSION_ESQUEMA):
    """La versión forma parte de la clave de caché: cada cambio en ESQUEMA vuelve a ejecutar las migraciones."""
    with conexion() as c, c.cursor() as cur:
        cur.execute(ESQUEMA)
        for k, v in C.CONFIG_DEFAULT.items():
            cur.execute("INSERT INTO config (clave, valor) VALUES (%s, %s) ON CONFLICT (clave) DO NOTHING", (k, v))
        cur.execute("SELECT COUNT(*) FROM dependencias")
        if cur.fetchone()[0] == 0:
            for n, s, col in C.DEPENDENCIAS_SEED:
                cur.execute(
                    "INSERT INTO dependencias (nombre, sigla, color) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                    (n, s, col),
                )
        cur.execute("SELECT COUNT(*) FROM tipos_expediente")
        if cur.fetchone()[0] == 0:
            for n, g, o, ec in C.TIPOS_SEED:
                cur.execute(
                    "INSERT INTO tipos_expediente (nombre, grupo, origen, es_curso) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                    (n, g, o, ec),
                )
    return True


def log(usuario, accion, detalle=""):
    try:
        ejecutar("INSERT INTO auditoria (usuario, accion, detalle) VALUES (%s, %s, %s)", (usuario, accion, detalle))
    except Exception:
        pass


# ───────────────────────── Lecturas cacheadas ─────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def get_config():
    cfg = dict(C.CONFIG_DEFAULT)
    df = leer("SELECT clave, valor FROM config")
    cfg.update(dict(zip(df["clave"], df["valor"])))
    return cfg


def set_config(valores: dict):
    with conexion() as c, c.cursor() as cur:
        for k, v in valores.items():
            cur.execute(
                "INSERT INTO config (clave, valor) VALUES (%s, %s) ON CONFLICT (clave) DO UPDATE SET valor = EXCLUDED.valor",
                (k, str(v)),
            )
    invalidar()


@st.cache_data(ttl=300, show_spinner=False)
def df_dependencias(solo_activas=False):
    sql = "SELECT * FROM dependencias"
    if solo_activas:
        sql += " WHERE activa"
    return leer(sql + " ORDER BY id")


@st.cache_data(ttl=300, show_spinner=False)
def df_tipos(solo_activos=False):
    sql = "SELECT * FROM tipos_expediente"
    if solo_activos:
        sql += " WHERE activo"
    return leer(sql + " ORDER BY grupo, nombre")


@st.cache_data(ttl=60, show_spinner=False)
def df_expedientes():
    df = leer(
        """
        SELECT e.*, m.ult_mov, m.cant_mov, COALESCE(t.grupo, 'Otros') AS grupo
        FROM expedientes e
        LEFT JOIN (SELECT expediente_id, MAX(fecha_hora) AS ult_mov, COUNT(*) AS cant_mov
                   FROM movimientos GROUP BY expediente_id) m ON m.expediente_id = e.id
        LEFT JOIN tipos_expediente t ON t.nombre = e.tipo
        ORDER BY e.libro DESC, e.folio DESC, e.orden DESC
        """
    )
    for col in ["fecha_ingreso", "fecha_termino"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in ["ult_mov", "creado_en", "actualizado_en", "fecha_tramite"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df["cant_mov"] = df["cant_mov"].fillna(0).astype(int)
    df["tramitado"] = df["tramitado"].fillna(False).astype(bool)
    return df


@st.cache_data(ttl=60, show_spinner=False)
def df_movimientos():
    df = leer(
        """
        SELECT m.*, e.identificador, e.tipo AS tipo_exp, e.nro_exp, e.anio, e.asunto
        FROM movimientos m JOIN expedientes e ON e.id = m.expediente_id
        ORDER BY m.fecha_hora DESC, m.id DESC
        """
    )
    df["fecha_hora"] = pd.to_datetime(df["fecha_hora"], errors="coerce")
    return df


@st.cache_data(ttl=60, show_spinner=False)
def df_cursos():
    df = leer(
        """
        SELECT c.*, e.identificador, e.tipo AS tipo_exp, e.despacho AS despacho_exp,
               (SELECT COUNT(*) FROM personal_curso p WHERE p.curso_id = c.id) AS cant_personal
        FROM cursos c LEFT JOIN expedientes e ON e.id = c.expediente_id
        ORDER BY c.fecha_inicio DESC NULLS LAST, c.id DESC
        """
    )
    for col in ["fecha_inicio", "fecha_fin"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df["fase"] = df.apply(fase_curso, axis=1) if not df.empty else pd.Series(dtype=str)
    return df


@st.cache_data(ttl=60, show_spinner=False)
def df_personal():
    df = leer(
        """
        SELECT p.*, c.nombre AS curso, c.categoria, c.ambito, c.modalidad, c.requerimiento,
               c.fecha_inicio, c.fecha_fin, c.estado AS estado_curso, c.division_dicta, c.lugar,
               e.identificador
        FROM personal_curso p
        JOIN cursos c ON c.id = p.curso_id
        LEFT JOIN expedientes e ON e.id = c.expediente_id
        ORDER BY c.fecha_inicio DESC NULLS LAST, p.apellido
        """
    )
    for col in ["fecha_inicio", "fecha_fin"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


@st.cache_data(ttl=60, show_spinner=False)
def df_eventos():
    df = leer(
        """
        SELECT ev.*, e.identificador FROM eventos ev
        LEFT JOIN expedientes e ON e.id = ev.expediente_id
        ORDER BY ev.fecha
        """
    )
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    return df


def fase_curso(row):
    """Fase efectiva del curso combinando el estado administrativo con las fechas."""
    est = row.get("estado") if isinstance(row.get("estado"), str) else "SOLICITADO"
    if est in ("NO AUTORIZADO", "SUSPENDIDO"):
        return est
    ini, fin = row.get("fecha_inicio"), row.get("fecha_fin")
    h = pd.Timestamp(hoy())
    if pd.notna(fin) and h > fin:
        return "REALIZADO" if est == "AUTORIZADO" else "VENCIDO SIN AUTORIZAR"
    if pd.notna(ini) and ini <= h and (pd.isna(fin) or h <= fin):
        return "EN CURSO"
    return est


# ───────────────────────── Numeración del libro ─────────────────────────
def sugerir_numeracion(anio=None):
    """Próximo N°EXP/FOLIO/ORDEN según el último asiento del libro actual."""
    cfg = get_config()
    anio = anio or hoy().year
    libro = int(cfg["libro_actual"])
    cap = max(1, int(cfg["renglones_por_folio"]))
    paso = max(1, int(cfg["paso_folio"]))
    if cfg["reinicio_anual"] == "SI":
        r = leer("SELECT MAX(nro_exp) AS m FROM expedientes WHERE anio = %s", (anio,))
    else:
        r = leer("SELECT MAX(nro_exp) AS m FROM expedientes")
    max_nro = r["m"].iloc[0]
    nro = int(max_nro) + 1 if pd.notna(max_nro) else int(cfg["nro_inicial"])
    ult = leer(
        "SELECT folio, orden FROM expedientes WHERE libro = %s ORDER BY folio DESC, orden DESC LIMIT 1", (libro,)
    )
    if ult.empty:
        folio, orden = int(cfg["folio_inicial"]), 1
    else:
        f, o = int(ult["folio"].iloc[0]), int(ult["orden"].iloc[0])
        folio, orden = (f + paso, 1) if o >= cap else (f, o + 1)
    return {"nro_exp": nro, "folio": folio, "orden": orden, "libro": libro, "anio": anio, "cap": cap, "paso": paso}


def avanzar(num: dict, nuevo_folio=False):
    """Siguiente posición a partir de una dada (para la grilla de transcripción)."""
    n = dict(num)
    n["nro_exp"] += 1
    if nuevo_folio or n["orden"] >= n["cap"]:
        n["folio"] += n["paso"]
        n["orden"] = 1
    else:
        n["orden"] += 1
    return n


def conflicto_numeracion(nro, folio, orden, libro, anio, excluir_id=None):
    cfg = get_config()
    params = [libro, folio, orden]
    sql = "SELECT identificador FROM expedientes WHERE ((libro = %s AND folio = %s AND orden = %s)"
    if cfg["reinicio_anual"] == "SI":
        sql += " OR (nro_exp = %s AND anio = %s))"
        params += [nro, anio]
    else:
        sql += " OR nro_exp = %s)"
        params += [nro]
    if excluir_id:
        sql += " AND id <> %s"
        params.append(excluir_id)
    r = leer(sql, params)
    return None if r.empty else r["identificador"].iloc[0]


# ───────────────────────── Escrituras ─────────────────────────
def crear_expediente(exp, mov=None, curso=None, personal=None, eventos=None, usuario=""):
    with conexion() as c, c.cursor() as cur:
        exp = {**exp, "creado_por": usuario, "creado_en": ahora(), "actualizado_en": ahora()}
        exp_id, ident = _insert(cur, "expedientes", exp, "id, identificador")
        if mov:
            _insert(cur, "movimientos", {**mov, "expediente_id": exp_id, "registrado_por": usuario}, None)
        curso_id = None
        if curso:
            (curso_id,) = _insert(cur, "cursos", {**curso, "expediente_id": exp_id})
            for p in personal or []:
                _insert(cur, "personal_curso", {**p, "curso_id": curso_id}, None)
        for ev in eventos or []:
            _insert(cur, "eventos", {**ev, "expediente_id": exp_id, "curso_id": curso_id}, None)
    log(usuario, "ALTA EXPEDIENTE", ident)
    invalidar()
    return exp_id, ident


def actualizar_expediente(exp_id, data, usuario=""):
    with conexion() as c, c.cursor() as cur:
        _update(cur, "expedientes", {**data, "actualizado_en": ahora()}, exp_id)
    log(usuario, "EDICIÓN EXPEDIENTE", str(exp_id))
    invalidar()


def eliminar_expediente(exp_id, usuario=""):
    ejecutar("DELETE FROM expedientes WHERE id = %s", (exp_id,))
    log(usuario, "BAJA EXPEDIENTE", str(exp_id))
    invalidar()


def registrar_movimiento(exp_id, mov, nuevo_estado=None, usuario=""):
    with conexion() as c, c.cursor() as cur:
        _insert(cur, "movimientos", {**mov, "expediente_id": exp_id, "registrado_por": usuario}, None)
        upd = {"ubicacion_actual": mov.get("destino"), "actualizado_en": ahora()}
        if nuevo_estado:
            upd["estado"] = nuevo_estado
        if mov.get("despacho"):
            upd["despacho"] = mov["despacho"]
        if mov.get("urgente"):
            upd["prioridad"] = "URGENTE TRÁMITE"
        if mov.get("fojas"):
            upd["fojas"] = mov["fojas"]
        _update(cur, "expedientes", upd, exp_id)
        # Visto bueno sobre un expediente de curso -> curso autorizado
        if mov.get("despacho") == "VISTO BUENO":
            cur.execute(
                "UPDATE cursos SET estado = 'AUTORIZADO' WHERE expediente_id = %s AND estado IN ('PREVISTO','SOLICITADO')",
                (exp_id,),
            )
        elif mov.get("despacho") == "NO AUTORIZADO":
            cur.execute("UPDATE cursos SET estado = 'NO AUTORIZADO' WHERE expediente_id = %s", (exp_id,))
    log(usuario, "MOVIMIENTO", f"{exp_id} → {mov.get('destino')}")
    invalidar()


def marcar_tramitado(ids, accion, detalle, fecha_hora, tramito, usuario="", revertir=False):
    """Deja asentado que el expediente fue tramitado (o revierte la marca). Queda en la hoja de ruta."""
    with conexion() as c, c.cursor() as cur:
        for i in ids:
            cur.execute("SELECT ubicacion_actual, estado FROM expedientes WHERE id = %s", (_py(i),))
            fila = cur.fetchone()
            if not fila:
                continue
            ub, est = fila
            if revertir:
                _update(cur, "expedientes", {"tramitado": False, "fecha_tramite": None, "tramitado_por": None,
                                             "accion_tramite": None, "detalle_tramite": None,
                                             "estado": "EN TRÁMITE" if est == "TRAMITADO" else est, "actualizado_en": ahora()}, i)
                obs = f"Se anula la marca de tramitado. {detalle or ''}".strip()
            else:
                _update(cur, "expedientes", {"tramitado": True, "fecha_tramite": fecha_hora, "tramitado_por": tramito,
                                             "accion_tramite": accion, "detalle_tramite": detalle,
                                             "estado": "TRAMITADO" if est not in ("REMITIDO", "RESUELTO", "ARCHIVADO") else est,
                                             "actualizado_en": ahora()}, i)
                obs = detalle
            _insert(cur, "movimientos", {"expediente_id": i, "fecha_hora": fecha_hora, "tipo": "TRÁMITE", "origen": ub,
                                         "destino": ub, "despacho": None if revertir else accion,
                                         "entregado_por": tramito, "observaciones": obs, "registrado_por": usuario}, None)
    log(usuario, "TRÁMITE" if not revertir else "ANULA TRÁMITE", ",".join(str(i) for i in ids))
    invalidar()


def eliminar_movimiento(mov_id, usuario=""):
    ejecutar("DELETE FROM movimientos WHERE id = %s", (mov_id,))
    log(usuario, "BAJA MOVIMIENTO", str(mov_id))
    invalidar()


def guardar_curso(curso, personal=None, curso_id=None, usuario=""):
    with conexion() as c, c.cursor() as cur:
        if curso_id:
            _update(cur, "cursos", curso, curso_id)
        else:
            (curso_id,) = _insert(cur, "cursos", curso)
        if personal is not None:
            cur.execute("DELETE FROM personal_curso WHERE curso_id = %s", (curso_id,))
            for p in personal:
                _insert(cur, "personal_curso", {**p, "curso_id": curso_id}, None)
    log(usuario, "CURSO", f"{curso_id} {curso.get('nombre', '')}")
    invalidar()
    return curso_id


def eliminar_curso(curso_id, usuario=""):
    ejecutar("DELETE FROM cursos WHERE id = %s", (curso_id,))
    log(usuario, "BAJA CURSO", str(curso_id))
    invalidar()


def crear_evento(ev, usuario=""):
    with conexion() as c, c.cursor() as cur:
        _insert(cur, "eventos", ev, None)
    log(usuario, "EVENTO", ev.get("titulo", ""))
    invalidar()


def completar_evento(ev_id, valor=True):
    ejecutar("UPDATE eventos SET completado = %s WHERE id = %s", (valor, ev_id))
    invalidar()


def eliminar_evento(ev_id):
    ejecutar("DELETE FROM eventos WHERE id = %s", (ev_id,))
    invalidar()


def guardar_catalogo(tabla, df_nuevo, columnas):
    """Sincroniza un data_editor (dependencias / tipos) con su tabla."""
    with conexion() as c, c.cursor() as cur:
        cur.execute(f"SELECT id FROM {tabla}")
        ids_db = {r[0] for r in cur.fetchall()}
        ids_ui = set()
        for _, r in df_nuevo.iterrows():
            if not str(r.get("nombre") or "").strip():
                continue
            data = {k: (None if pd.isna(r.get(k)) else r.get(k)) for k in columnas}
            data["nombre"] = str(data["nombre"]).strip().upper()
            rid = r.get("id")
            if pd.notna(rid) and int(rid) in ids_db:
                ids_ui.add(int(rid))
                _update(cur, tabla, data, int(rid))
            else:
                cur.execute(
                    f"INSERT INTO {tabla} ({', '.join(data)}) VALUES ({', '.join(['%s'] * len(data))}) "
                    f"ON CONFLICT (nombre) DO NOTHING",
                    [_py(v) for v in data.values()],
                )
        for rid in ids_db - ids_ui:
            cur.execute(f"DELETE FROM {tabla} WHERE id = %s", (rid,))
    invalidar()


def agregar_dependencia(nombre, sigla=None, color=None, telefono=None):
    """Alta rápida desde el botón ➕. Devuelve el nombre normalizado y si ya existía."""
    nombre = " ".join(str(nombre).split()).upper()
    with conexion() as c, c.cursor() as cur:
        cur.execute("SELECT 1 FROM dependencias WHERE nombre = %s", (nombre,))
        if cur.fetchone():
            cur.execute("UPDATE dependencias SET activa = TRUE WHERE nombre = %s", (nombre,))
            existia = True
        else:
            if not color:
                cur.execute("SELECT color FROM dependencias")
                usados = {(r[0] or "").upper() for r in cur.fetchall()}
                color = next((p for p in C.PALETA if p.upper() not in usados), "#64748B")
            cur.execute("INSERT INTO dependencias (nombre, sigla, color, telefono_wp) VALUES (%s, %s, %s, %s)",
                        (nombre, (sigla or "").strip().upper() or None, color, (telefono or "").strip() or None))
            existia = False
    invalidar()
    return nombre, existia


def asegurar_catalogos(tipos=(), dependencias=()):
    """Agrega al catálogo tipos/dependencias nuevos detectados en una importación."""
    with conexion() as c, c.cursor() as cur:
        for t in {str(x).strip().upper() for x in tipos if str(x).strip()}:
            cur.execute("INSERT INTO tipos_expediente (nombre) VALUES (%s) ON CONFLICT DO NOTHING", (t,))
        for d in {str(x).strip().upper() for x in dependencias if str(x).strip()}:
            cur.execute("INSERT INTO dependencias (nombre) VALUES (%s) ON CONFLICT DO NOTHING", (d,))
    invalidar()


def importar_expedientes(filas, modo="omitir", usuario=""):
    """Inserta en bloque. Cada fila es independiente (SAVEPOINT): un error no frena el lote."""
    ok, act, omit, errores = 0, 0, 0, []
    campos_upd = [
        "fecha_ingreso", "origen", "dependencia_origen", "nro_exp_origen", "tipo", "asunto", "iniciador",
        "prioridad", "estado", "despacho", "destino", "ubicacion_actual", "fojas", "observaciones", "fecha_termino",
    ]
    with conexion() as c, c.cursor() as cur:
        for f in filas:
            cur.execute("SAVEPOINT sp")
            try:
                cur.execute(
                    "SELECT id FROM expedientes WHERE libro = %s AND folio = %s AND orden = %s",
                    (f["libro"], f["folio"], f["orden"]),
                )
                existe = cur.fetchone()
                if existe:
                    if modo == "actualizar":
                        _update(cur, "expedientes", {k: f.get(k) for k in campos_upd} | {"actualizado_en": ahora()}, existe[0])
                        act += 1
                    else:
                        omit += 1
                else:
                    data = dict(f) | {"creado_por": usuario, "creado_en": ahora(), "actualizado_en": ahora()}
                    (eid,) = _insert(cur, "expedientes", data)
                    _insert(
                        cur,
                        "movimientos",
                        {
                            "expediente_id": eid,
                            "fecha_hora": pd.Timestamp(f["fecha_ingreso"]).to_pydatetime(),
                            "tipo": "INGRESO",
                            "origen": f.get("dependencia_origen"),
                            "destino": C.DEP_PROPIA,
                            "observaciones": "Asiento incorporado por carga masiva del libro",
                            "registrado_por": usuario,
                        },
                        None,
                    )
                    ok += 1
                cur.execute("RELEASE SAVEPOINT sp")
            except Exception as e:
                cur.execute("ROLLBACK TO SAVEPOINT sp")
                errores.append(f"{f.get('nro_exp')}/{f.get('folio')}/{f.get('orden')}: {str(e).splitlines()[0]}")
    log(usuario, "CARGA MASIVA", f"nuevos={ok} actualizados={act} omitidos={omit} errores={len(errores)}")
    invalidar()
    return ok, act, omit, errores


def respaldo_completo():
    tablas = ["expedientes", "movimientos", "cursos", "personal_curso", "eventos", "dependencias", "tipos_expediente", "config", "auditoria"]
    return {t: leer(f"SELECT * FROM {t} ORDER BY 1") for t in tablas}
