"""Avisos automáticos por WhatsApp a los oficiales (sin que nadie toque «Enviar»).

Proveedores (se elige en Configuración → 📲 Avisos automáticos):
  META      → WhatsApp Business Cloud API. El mensaje llega desde el número propio del sistema, con el nombre
              «Sistema de Expedientes DGII». Secrets: WA_TOKEN, WA_PHONE_ID. Plantilla aprobada en Meta (config wa_plantilla).
  CALLMEBOT → gratuito. Cada oficial activa el servicio una vez y recibe su «apikey». Llega desde el número de CallMeBot,
              con el texto encabezado «Sistema de Expedientes DGII». Secret: CALLMEBOT_KEYS = "5493811234567:123456,…".
Las claves NUNCA se guardan en la base ni salen en el respaldo: solo en los Secrets de Streamlit.
"""
import re
import threading
import urllib.parse

import requests
import streamlit as st

import db

PROVEEDORES = ["DESACTIVADO", "TELEGRAM", "TEXTMEBOT", "CALLMEBOT", "META"]
NOMBRE = "Sistema de Expedientes DGII"
EVENTOS = {"alta_sub": "Expediente nuevo cargado por un suboficial", "alta_todos": "Expediente nuevo (cualquier usuario)",
           "reingreso": "Reingreso de un expediente", "tramite": "Un oficial tramitó o despachó",
           "entrega": "El comisionista entregó o trajo un expediente", "urgente": "Solo si es URGENTE"}
ETQ_REGISTRO = {"origen": "Origen", "quien": "Cargó", "pie": "👉 Revíselo en Mi trabajo → Para tramitar."}


def _secret(k):
    import os

    try:
        v = st.secrets.get(k)
    except Exception:
        v = None
    return v if v is not None else os.getenv(k)


def _num(t):
    d = re.sub(r"\D", "", str(t or ""))
    from reportes import normalizar_tel

    return normalizar_tel(d)


def destinatarios(cfg=None):
    """[(nombre, número)] desde config «wa_destinos» (una línea por oficial: Nombre | número)."""
    cfg = cfg or db.get_config()
    out = []
    if (cfg.get("wa_proveedor") or "") == "TELEGRAM":  # Telegram: «Nombre | chat_id»
        for linea in str(cfg.get("tg_destinos") or "").splitlines():
            n, t = linea.split("|", 1) if "|" in linea else ("", linea)
            t = re.sub(r"[^\d-]", "", t)
            if t:
                out.append((n.strip(), t))
        return out
    for linea in str(cfg.get("wa_destinos") or "").splitlines():
        if "|" in linea:
            n, t = linea.split("|", 1)
        else:
            n, t = "", linea
        t = _num(t)
        if t:
            out.append((n.strip(), t))
    return out


def eventos_activos(cfg=None):
    cfg = cfg or db.get_config()
    ev = {e for e in str(cfg.get("wa_eventos") or "alta_sub").split(",") if e}
    if cfg.get("wa_ev_v2") != "1":  # configuraciones anteriores: trámites y entregas avisan por defecto
        ev |= {"tramite", "entrega"}
    return ev


def estado(cfg=None):
    """(listo: bool, explicación)."""
    cfg = cfg or db.get_config()
    prov = cfg.get("wa_proveedor") or "DESACTIVADO"
    if prov == "DESACTIVADO":
        return False, "Avisos automáticos desactivados."
    if prov == "TELEGRAM" and not _secret("TELEGRAM_BOT_TOKEN"):
        return False, "Falta TELEGRAM_BOT_TOKEN en los Secrets de Streamlit."
    if not destinatarios(cfg):
        return False, ("Ningún oficial vinculado: cada uno escribe /start al bot y luego use «Buscar oficiales»."
                       if prov == "TELEGRAM" else "Falta cargar los números de los oficiales.")
    if prov == "META" and not (_secret("WA_TOKEN") and _secret("WA_PHONE_ID")):
        return False, "Faltan WA_TOKEN y WA_PHONE_ID en los Secrets de Streamlit."
    if prov == "TEXTMEBOT" and not _secret("TEXTMEBOT_KEY"):
        return False, "Falta TEXTMEBOT_KEY en los Secrets de Streamlit."
    if prov == "CALLMEBOT":
        claves = _claves_callmebot()
        faltan = [n or t for n, t in destinatarios(cfg) if t not in claves]
        if faltan:
            return False, "Falta la apikey de CallMeBot (Secrets: CALLMEBOT_KEYS) de: " + ", ".join(faltan)
    return True, f"Activo · {prov} · {len(destinatarios(cfg))} destinatario(s)."


def _claves_callmebot():
    out = {}
    for par in str(_secret("CALLMEBOT_KEYS") or "").split(","):
        if ":" in par:
            t, k = par.split(":", 1)
            out[_num(t)] = k.strip()
    return out


def _plano(s, n=180):
    """Los parámetros de plantilla de Meta no admiten saltos de línea ni muchos espacios."""
    return re.sub(r"\s+", " ", str(s or "—")).strip()[:n] or "—"


def _enviar_meta(tel, campos, cfg, sec):
    url = f"https://graph.facebook.com/v21.0/{sec['phone_id']}/messages"
    cuerpo = {"messaging_product": "whatsapp", "to": tel, "type": "template",
              "template": {"name": cfg.get("wa_plantilla") or "aviso_expediente", "language": {"code": cfg.get("wa_idioma") or "es_AR"},
                           "components": [{"type": "body", "parameters": [{"type": "text", "text": _plano(c)} for c in campos]}]}}
    r = requests.post(url, json=cuerpo, headers={"Authorization": f"Bearer {sec['token']}"}, timeout=20)
    if r.status_code >= 300:
        raise RuntimeError(f"Meta {r.status_code}: {r.text[:200]}")


def _tg(metodo, token, **datos):
    r = requests.post(f"https://api.telegram.org/bot{token}/{metodo}", json=datos, timeout=20)
    j = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    if not j.get("ok"):
        raise RuntimeError(f"Telegram: {j.get('description') or r.text[:160]}")
    return j.get("result")


def _html(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _enviar_telegram(chat, campos, sec, etq=None):
    etq = etq or ETQ_REGISTRO
    acc, nro, tipo, asunto, origen, quien = [_html(_plano(c, 300)) for c in campos]
    texto = (f"📁 <b>{NOMBRE}</b>\n🔔 {acc}\n<b>Exp. N° {nro}</b>\nTipo: {tipo}\nAsunto: {asunto}\n{etq['origen']}: {origen}\n"
             f"{etq['quien']}: {quien}\n{_html(etq['pie'])}")
    datos = {"chat_id": chat, "text": texto, "parse_mode": "HTML", "disable_web_page_preview": True}
    if sec.get("url"):
        datos["reply_markup"] = {"inline_keyboard": [[{"text": "📂 Abrir el sistema", "url": sec["url"]}]]}
    _tg("sendMessage", sec["tg"], **datos)


def buscar_chats():
    """Personas que escribieron al bot (/start): [(nombre, chat_id)]."""
    token = _secret("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Falta TELEGRAM_BOT_TOKEN en los Secrets.")
    vistos = {}
    for u in _tg("getUpdates", token, limit=100) or []:
        m = u.get("message") or u.get("edited_message") or {}
        c = m.get("chat") or {}
        if c.get("id") is not None:
            nom = " ".join(x for x in [c.get("first_name"), c.get("last_name")] if x) or c.get("title") or c.get("username") or ""
            vistos[str(c["id"])] = nom
    return [(n, i) for i, n in vistos.items()]


def nombre_bot():
    try:
        r = _tg("getMe", _secret("TELEGRAM_BOT_TOKEN"))
        return r.get("username")
    except Exception:
        return None


def _enviar_textmebot(tel, texto, sec):
    url = (f"https://api.textmebot.com/send.php?recipient=%2B{tel}&apikey={urllib.parse.quote(sec['tmb'] or '')}"
           f"&text={urllib.parse.quote(texto)}")
    r = requests.get(url, timeout=30)
    if r.status_code >= 300 or "error" in r.text.lower()[:300]:
        raise RuntimeError(f"TextMeBot {r.status_code}: {r.text[:160]}")


def _enviar_callmebot(tel, texto, sec):
    k = sec["claves"].get(tel)
    if not k:
        raise RuntimeError("sin apikey")
    url = f"https://api.callmebot.com/whatsapp.php?phone=%2B{tel}&apikey={urllib.parse.quote(k)}&text={urllib.parse.quote(texto)}"
    r = requests.get(url, timeout=25)
    if r.status_code >= 300 or "error" in r.text.lower()[:300]:
        raise RuntimeError(f"CallMeBot {r.status_code}: {r.text[:160]}")


def campos_expediente(exp, accion, quien):
    """Parámetros de la plantilla (en este orden): {{1}} acción · {{2}} N° · {{3}} tipo · {{4}} asunto · {{5}} origen · {{6}} quién."""
    urg = " ⚡ URGENTE" if exp.get("prioridad") == "URGENTE TRÁMITE" else ""
    return [accion + urg, f"{exp.get('identificador')} ({exp.get('anio') or ''})", exp.get("tipo"), exp.get("asunto"),
            exp.get("dependencia_origen") or exp.get("origen"), quien]


def texto_expediente(campos, etq=None):
    etq = etq or ETQ_REGISTRO
    acc, nro, tipo, asunto, origen, quien = [_plano(c, 300) for c in campos]
    return (f"📁 *{NOMBRE}*\n🔔 {acc}\n*Exp. N° {nro}*\nTipo: {tipo}\nAsunto: {asunto}\n{etq['origen']}: {origen}\n"
            f"{etq['quien']}: {quien}\n{etq['pie']}")


def enviar(campos, cfg=None, esperar=False, etq=None):
    """Envía el aviso a todos los destinatarios. En segundo plano salvo esperar=True (prueba). Devuelve [(destino, ok, detalle)]."""
    cfg = cfg or db.get_config()
    listo, _ = estado(cfg)
    if not listo:
        return []
    prov = cfg.get("wa_proveedor")
    dest = destinatarios(cfg)
    res = []
    sec = {"token": _secret("WA_TOKEN"), "phone_id": _secret("WA_PHONE_ID"), "claves": _claves_callmebot(), "tmb": _secret("TEXTMEBOT_KEY"),
           "tg": _secret("TELEGRAM_BOT_TOKEN"), "url": cfg.get("app_url") or "https://expedientesdgii.streamlit.app/"}  # se leen antes del hilo

    def _run():
        for n, t in dest:
            try:
                if prov == "META":
                    _enviar_meta(t, campos, cfg, sec)
                elif prov == "TELEGRAM":
                    _enviar_telegram(t, campos, sec, etq)
                elif prov == "TEXTMEBOT":
                    _enviar_textmebot(t, texto_expediente(campos, etq), sec)
                else:
                    _enviar_callmebot(t, texto_expediente(campos, etq), sec)
                res.append((n or t, True, "enviado"))
            except Exception as e:  # nunca interrumpe el trabajo del usuario
                res.append((n or t, False, str(e)))
        db.log(NOMBRE, "AVISO WHATSAPP", f"{campos[1]} · " + "; ".join(f"{d}: {'ok' if ok else det}" for d, ok, det in res))

    if esperar:
        _run()
    else:
        threading.Thread(target=_run, daemon=True).start()
    return res


def avisar_expediente(exp, evento, quien, rol):
    """Llamar después de registrar. evento: 'alta' o 'reingreso'."""
    try:
        cfg = db.get_config()
        ev = eventos_activos(cfg)
        if evento == "alta" and not ("alta_todos" in ev or ("alta_sub" in ev and rol == "SUBOFICIAL")):
            return False
        if evento == "reingreso" and "reingreso" not in ev:
            return False
        if "urgente" in ev and exp.get("prioridad") != "URGENTE TRÁMITE":
            return False
        if not estado(cfg)[0]:
            return False
        accion = "Nuevo expediente registrado" if evento == "alta" else "Reingresó un expediente"
        enviar(campos_expediente(exp, accion, quien), cfg)
        return True
    except Exception:
        return False


def avisar_movimiento(exp, evento, titulo, detalle, quien):
    """Aviso de trámite / despacho (evento 'tramite') o de entrega / retiro del comisionista (evento 'entrega')."""
    try:
        cfg = db.get_config()
        ev = eventos_activos(cfg)
        if evento not in ev or not estado(cfg)[0]:
            return False
        if "urgente" in ev and exp.get("prioridad") != "URGENTE TRÁMITE":
            return False
        etq = {"origen": "Detalle", "quien": "Entregó" if evento == "entrega" else "Tramitó",
               "pie": "👉 Ver la hoja de ruta en el sistema."}
        campos = [titulo, f"{exp.get('identificador')} ({exp.get('anio') or ''})", exp.get("tipo"), exp.get("asunto"), detalle or "—", quien]
        enviar(campos, cfg, etq=etq)
        return True
    except Exception:
        return False
