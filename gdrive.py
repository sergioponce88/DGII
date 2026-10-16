"""Google Drive (cuenta personal, OAuth de escritorio, permiso mínimo drive.file).

Flujo de conexión (una sola vez, desde ⚙️ Configuración → Google Drive):
  1. El usuario abre el link de autorización y acepta con su cuenta.
  2. Google redirige a http://localhost/?code=... (la página no carga: es normal).
  3. El usuario pega esa dirección en la app; se canjea el código por un refresh_token
     que queda guardado en la tabla config.
"""
import io
import json
import os
import time
import urllib.parse

import requests
import streamlit as st

import db

SCOPE = "https://www.googleapis.com/auth/drive.file"
REDIRECT = "http://localhost"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
API = "https://www.googleapis.com/drive/v3"
UPLOAD = "https://www.googleapis.com/upload/drive/v3/files"
CARPETA_RAIZ = "EXPEDIENTES DGII - SISTEMA"


class DriveError(Exception):
    pass


def _secret(k):
    try:
        v = st.secrets.get(k)
    except Exception:
        v = None
    return v or os.getenv(k)


def credenciales():
    cid, sec = _secret("GDRIVE_CLIENT_ID"), _secret("GDRIVE_CLIENT_SECRET")
    return (cid or "").strip().strip('"') or None, (sec or "").strip().strip('"') or None


def configurado():
    cid, sec = credenciales()
    return bool(cid and sec)


def conectado():
    return configurado() and bool(db.get_config().get("gdrive_refresh_token"))


def url_autorizacion():
    cid, _ = credenciales()
    q = {
        "client_id": cid, "redirect_uri": REDIRECT, "response_type": "code", "scope": SCOPE,
        "access_type": "offline", "prompt": "consent", "include_granted_scopes": "true",
    }
    return f"{AUTH_URL}?{urllib.parse.urlencode(q)}"


def canjear_codigo(texto):
    """Acepta la dirección completa pegada (http://localhost/?code=...) o solo el código."""
    texto = texto.strip()
    if "code=" in texto:
        texto = urllib.parse.parse_qs(urllib.parse.urlparse(texto).query).get("code", [""])[0]
    if not texto:
        raise DriveError("No se encontró el código en la dirección pegada.")
    cid, sec = credenciales()
    r = requests.post(TOKEN_URL, data={"code": texto, "client_id": cid, "client_secret": sec,
                                       "redirect_uri": REDIRECT, "grant_type": "authorization_code"}, timeout=20)
    d = r.json()
    if r.status_code != 200 or "refresh_token" not in d:
        if d.get("error") == "invalid_client":
            raise DriveError("Google rechazó el cliente: el GDRIVE_CLIENT_SECRET (o el ID) cargado en Secrets no coincide "
                             "con el de Google Cloud. Copie el secreto de nuevo (o genere uno nuevo), guárdelo en Secrets "
                             "y vuelva a tocar 'Autorizar con Google'.")
        if d.get("error") == "invalid_grant":
            raise DriveError("El código ya se usó o venció. Toque 'Autorizar con Google' de nuevo y pegue la dirección enseguida.")
        raise DriveError(d.get("error_description") or d.get("error") or "Google no devolvió el permiso.")
    db.set_config({"gdrive_refresh_token": d["refresh_token"]})
    st.session_state["_gd_token"] = (d["access_token"], time.time() + int(d.get("expires_in", 3600)) - 120)
    return True


def desconectar():
    db.set_config({"gdrive_refresh_token": "", "gdrive_raiz_id": ""})
    st.session_state.pop("_gd_token", None)


def _token():
    tok = st.session_state.get("_gd_token")
    if tok and tok[1] > time.time():
        return tok[0]
    cid, sec = credenciales()
    rt = db.get_config().get("gdrive_refresh_token")
    if not (cid and sec and rt):
        raise DriveError("Google Drive no está conectado. Vaya a ⚙️ Configuración → Google Drive.")
    r = requests.post(TOKEN_URL, data={"client_id": cid, "client_secret": sec, "refresh_token": rt,
                                       "grant_type": "refresh_token"}, timeout=20)
    d = r.json()
    if r.status_code != 200:
        if d.get("error") == "invalid_grant":
            raise DriveError("El permiso de Google venció o fue revocado. Vuelva a conectar Drive en ⚙️ Configuración.")
        raise DriveError(d.get("error_description") or d.get("error") or "Error al renovar el acceso a Drive.")
    st.session_state["_gd_token"] = (d["access_token"], time.time() + int(d.get("expires_in", 3600)) - 120)
    return d["access_token"]


def _h():
    return {"Authorization": f"Bearer {_token()}"}


def _crear_carpeta(nombre, padre=None):
    meta = {"name": nombre, "mimeType": "application/vnd.google-apps.folder"}
    if padre:
        meta["parents"] = [padre]
    r = requests.post(f"{API}/files", headers=_h() | {"Content-Type": "application/json"},
                      params={"fields": "id"}, data=json.dumps(meta), timeout=30)
    if r.status_code >= 300:
        raise DriveError(f"No se pudo crear la carpeta '{nombre}': {r.text[:200]}")
    return r.json()["id"]


def _existe(file_id):
    r = requests.get(f"{API}/files/{file_id}", headers=_h(), params={"fields": "id,trashed"}, timeout=20)
    return r.status_code == 200 and not r.json().get("trashed")


def carpeta_raiz():
    """Carpeta propia de la app. Intenta crearla dentro de la carpeta indicada por el usuario;
    con el permiso drive.file eso puede no estar permitido, y entonces la crea en 'Mi unidad'."""
    cfg = db.get_config()
    rid = cfg.get("gdrive_raiz_id")
    if rid and _existe(rid):
        return rid
    padre = cfg.get("gdrive_folder_id") or _secret("GDRIVE_FOLDER_ID")
    try:
        rid = _crear_carpeta(CARPETA_RAIZ, padre) if padre else _crear_carpeta(CARPETA_RAIZ)
        dentro = bool(padre)
    except DriveError:
        rid, dentro = _crear_carpeta(CARPETA_RAIZ), False
    db.set_config({"gdrive_raiz_id": rid, "gdrive_raiz_en_carpeta": "SI" if dentro else "NO"})
    return rid


def carpeta_anio(anio):
    key = f"gdrive_anio_{anio}"
    fid = db.get_config().get(key)
    if fid and _existe(fid):
        return fid
    fid = _crear_carpeta(str(anio), carpeta_raiz())
    db.set_config({key: fid})
    return fid


def subir_pdf(nombre, contenido: bytes, anio, descripcion=""):
    """Subida reanudable (sirve para archivos grandes). Devuelve (id, link)."""
    meta = {"name": nombre, "parents": [carpeta_anio(anio)], "mimeType": "application/pdf", "description": descripcion}
    r = requests.post(UPLOAD, headers=_h() | {"Content-Type": "application/json; charset=UTF-8",
                                              "X-Upload-Content-Type": "application/pdf",
                                              "X-Upload-Content-Length": str(len(contenido))},
                      params={"uploadType": "resumable", "fields": "id,webViewLink"}, data=json.dumps(meta), timeout=30)
    if r.status_code >= 300 or "Location" not in r.headers:
        raise DriveError(f"Drive rechazó la subida: {r.text[:200]}")
    up = requests.put(r.headers["Location"], headers={"Content-Type": "application/pdf"}, data=contenido, timeout=300)
    if up.status_code >= 300:
        raise DriveError(f"Falló el envío del archivo: {up.text[:200]}")
    d = up.json()
    link = d.get("webViewLink") or f"https://drive.google.com/file/d/{d['id']}/view"
    return d["id"], link


def probar():
    rid = carpeta_raiz()
    r = requests.get(f"{API}/files/{rid}", headers=_h(), params={"fields": "name,webViewLink"}, timeout=20)
    return r.json().get("webViewLink", f"https://drive.google.com/drive/folders/{rid}")


def imagenes_a_pdf(archivos) -> bytes:
    """Une fotos (JPG/PNG, p. ej. sacadas con el celular) en un único PDF, en el orden recibido."""
    from PIL import Image, ImageOps

    paginas = []
    for a in archivos:
        im = ImageOps.exif_transpose(Image.open(a)).convert("RGB")
        im.thumbnail((1700, 2400))  # ~200 ppp en A4: legible y liviano
        paginas.append(im)
    if not paginas:
        raise DriveError("No hay imágenes para convertir.")
    buf = io.BytesIO()
    paginas[0].save(buf, format="PDF", save_all=True, append_images=paginas[1:], resolution=200, quality=80)
    return buf.getvalue()


def unir_pdfs(archivos) -> bytes:
    """Si se suben varios PDF juntos, se unen en uno solo (requiere pypdf)."""
    from pypdf import PdfWriter

    w = PdfWriter()
    for a in archivos:
        w.append(a)
    buf = io.BytesIO()
    w.write(buf)
    return buf.getvalue()
