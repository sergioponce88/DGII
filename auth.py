"""Usuarios, claves y permisos por rol.

Roles:
  ADMINISTRADOR -> todo, incluida la configuración y la gestión de usuarios
  OFICIAL       -> carga, movimientos, TRAMITA y edita expedientes
  SUBOFICIAL    -> carga expedientes, registra movimientos y sube PDF (no tramita ni edita)
"""
import hashlib
import hmac
import secrets

import pandas as pd
import streamlit as st

import catalogos as C
import db

ROLES = ["ADMINISTRADOR", "OFICIAL", "SUBOFICIAL"]
PERMISOS = {
    "ADMINISTRADOR": {"cargar", "mover", "tramitar", "editar", "eliminar", "configurar"},
    "OFICIAL": {"cargar", "mover", "tramitar", "editar"},
    "SUBOFICIAL": {"cargar", "mover"},
}
DESCRIPCION_ROL = {
    "ADMINISTRADOR": "Todo el sistema + configuración y usuarios",
    "OFICIAL": "Carga, movimientos, trámite y edición de expedientes",
    "SUBOFICIAL": "Carga de expedientes, movimientos y PDF",
}
ITER = 200_000


# ───────────────────────── Claves ─────────────────────────
def hash_clave(clave: str) -> str:
    sal = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", clave.encode(), bytes.fromhex(sal), ITER).hex()
    return f"pbkdf2${ITER}${sal}${h}"


def verificar(clave: str, guardado: str) -> bool:
    try:
        _, it, sal, h = guardado.split("$")
        calc = hashlib.pbkdf2_hmac("sha256", clave.encode(), bytes.fromhex(sal), int(it)).hex()
        return hmac.compare_digest(calc, h)
    except Exception:
        return False


def rol_por_grado(grado):
    esc = C.escalafon(grado)
    return "OFICIAL" if esc == "OFICIAL" else "SUBOFICIAL"


# ───────────────────────── Datos ─────────────────────────
def df_usuarios():
    df = db.leer("SELECT id, legajo, grado, apellido, nombre, funcion, rol, activo, debe_cambiar, "
                 "ultimo_acceso, creado_en FROM usuarios ORDER BY activo DESC, rol, apellido")
    for c in ("ultimo_acceso", "creado_en"):
        df[c] = pd.to_datetime(df[c], errors="coerce")
    return df


def hay_usuarios():
    return int(db.leer("SELECT COUNT(*) AS n FROM usuarios")["n"].iloc[0]) > 0


def crear_usuario(legajo, grado, apellido, nombre, funcion, rol, clave, creado_por=""):
    legajo = "".join(str(legajo).split()).upper()
    if not legajo or not apellido.strip() or len(clave) < 6:
        raise ValueError("Legajo, apellido y una clave de al menos 6 caracteres son obligatorios.")
    if not db.leer("SELECT 1 FROM usuarios WHERE legajo = %s", (legajo,)).empty:
        raise ValueError(f"Ya existe un usuario con el legajo {legajo}.")
    db.ejecutar(
        "INSERT INTO usuarios (legajo, grado, apellido, nombre, funcion, rol, clave_hash, debe_cambiar) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (legajo, grado, apellido.strip().upper(), nombre.strip().title(), (funcion or "").strip().upper() or None,
         rol, hash_clave(clave), bool(creado_por)),
    )
    db.log(creado_por or legajo, "ALTA USUARIO", f"{legajo} {rol}")


def actualizar_usuario(uid, datos, por=""):
    sets = ", ".join(f"{k} = %s" for k in datos)
    db.ejecutar(f"UPDATE usuarios SET {sets} WHERE id = %s", list(datos.values()) + [uid])
    db.log(por, "EDICIÓN USUARIO", f"{uid} {list(datos)}")


def cambiar_clave(uid, nueva, por="", forzar_cambio=False):
    if len(nueva) < 6:
        raise ValueError("La clave debe tener al menos 6 caracteres.")
    db.ejecutar("UPDATE usuarios SET clave_hash = %s, debe_cambiar = %s WHERE id = %s", (hash_clave(nueva), forzar_cambio, uid))
    db.log(por, "CLAVE USUARIO", str(uid))


def login(legajo, clave):
    legajo = "".join(str(legajo).split()).upper()
    df = db.leer("SELECT * FROM usuarios WHERE legajo = %s", (legajo,))
    if df.empty or not verificar(clave, df["clave_hash"].iloc[0]):
        return None, "Legajo o clave incorrectos."
    u = df.iloc[0].to_dict()
    if not u.get("activo"):
        return None, "El usuario está deshabilitado. Consulte al administrador."
    db.ejecutar("UPDATE usuarios SET ultimo_acceso = %s WHERE id = %s", (db.ahora(), int(u["id"])))
    u.pop("clave_hash", None)
    u["id"] = int(u["id"])
    db.log(nombre_completo(u), "INGRESO", legajo)
    return u, None


# ───────────────────────── Sesión ─────────────────────────
def nombre_completo(u):
    return " ".join(x for x in [u.get("grado"), u.get("apellido"), u.get("nombre")] if x).upper()


def actual():
    return st.session_state.get("usuario")


def rol():
    u = actual()
    return u["rol"] if u else None


def puede(permiso):
    return permiso in PERMISOS.get(rol() or "", set())


def aviso_sin_permiso(accion="esta acción"):
    st.info(f"🔒 {accion.capitalize()} está reservada a {('oficiales' if accion != 'la configuración' else 'administradores')}. "
            f"Su rol: **{rol() or '—'}**.")
