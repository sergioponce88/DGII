"""Ayuda de redacción gratuita, en tres niveles:

1. Diccionario propio: errores frecuentes de los modelos de la Dirección (local, sin enviar datos).
2. LanguageTool (API pública gratuita): ortografía y gramática en español.
3. Google Gemini (nivel gratuito, opcional): mejora de redacción. En el nivel gratuito Google puede
   usar los textos para mejorar sus productos, por eso NUNCA se usa en documentos con datos
   personales (sumarios, actuaciones, notificaciones, sanciones).
"""
import os
import re

import requests

LT_URL = "https://api.languagetool.org/v2/check"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
GEMINI_MODELOS = ["gemini-flash-latest", "gemini-flash-lite-latest", "gemini-3.5-flash-lite"]  # lectura de fotos
GEMINI_RAPIDOS = ["gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-flash-latest"]  # corrección de textos

# (patrón, reemplazo) — se respeta mayúsculas si el original estaba en mayúsculas
DICCIONARIO = [
    (r"\bJefe de Polic[ií]a de la Provincia de la Provincia\b", "Jefe de Policía de la Provincia"),
    (r"\bTergo el agrado\b", "Tengo el agrado"),
    (r"\bAtendo al estado\b", "Atento al estado"),
    (r"\bAse mismo\b", "Asimismo"),
    (r"\bAs[ií] mismo\b", "Asimismo"),
    (r"\bse precede a\b", "se procede a"),
    (r"\bINTERO\b", "INTERNO"),
    (r"\bINTERVINIENE\b", "INTERVIENE"),
    (r"I\.\.E\.S\.P\.", "I.E.S.P."),
    (r"\bcito en\b", "sito en"),
    (r"\bcita en (calle|Av\.|avenida)", r"sita en \1"),
    (r"\bcapacitancia\b", "capacidad"),
    (r"\bRestigo\b", "Testigo"),
    (r"\bConsucido\b", "Conducido"),
    (r"\bAudicencias\b", "Audiencias"),
    (r"\brecepci[oó]no\b", "recepcionó"),
    (r"\bVIENTI", "VEINTI"),
    (r"\bvienti", "veinti"),
    (r"\bde m[aá]s diligencias\b", "demás diligencias"),
    (r"\ben termino\b", "en término"),
    (r"\bjuramente que prest[oó]\b", "juramento que prestó"),
    (r"\bdebera\b", "deberá"),
    (r"\bN[ªa] (?=\d)", "N° "),
    (r"\bCusa:", "Causa:"),
    (r"\bdesfaborables?\b", "desfavorable"),
    (r"\bpermatencia\b", "permanencia"),
    (r"\badministrabas\b", "administrativas"),
    (r"\bconcordancia con con\b", "concordancia con"),
    (r"\bprocedio\b", "procedió"),
    (r"\bse resbalo\b", "se resbaló"),
    (r"\bpiso mal\b", "pisó mal"),
    (r"\bpresenta capacitaci[oó]n\b", "presente capacitación"),
    (r"\bcon la referencia que se lo merece\b", "con la deferencia que se merece"),
    (r"\bcon la deferencia que se lo merece\b", "con la deferencia que se merece"),
    (r"\bSin otro en particular\b", "Sin otro particular"),
    (r"\bdar por reca[ií]do\b", "dar por decaído"),
    (r"\bse le dar[aá] por reca[ií]do\b", "se le dará por decaído"),
    (r"\bRENUNCI[OÓ] AL MISMO\b", "RENUNCIO AL MISMO"),
    (r"\.\.(?!\.)", "."),
    (r"[ \t]{2,}", " "),
    (r" ,", ","),
]

# Siglas y términos institucionales que LanguageTool no conoce
VOCABULARIO = {
    "IESP", "I.E.S.P.", "G.J.F.S.M.", "D.G.I.I.", "DGII", "RRDP", "R.R.D.P.", "RDC", "R.D.C.", "RIEC", "R.I.E.C.", "CITTU", "C.I.T.T.U.",
    "PTP", "URC", "U.R.C.", "Crio", "Subcrio", "Insp", "Ppal", "Grl", "Sgto", "Cdte", "fs", "foja", "fojas", "actuados", "obrados",
    "recaratular", "RECARATULAR", "recepcionado", "educando", "educandos", "Subjefatura", "Vicerrector", "Vicerrectorado", "Rectorado",
    "subsidiariedad", "CONSTE", "CERTIFICA", "Muñecas", "Tucumán",
}


def _igualar_caso(original, nuevo):
    return nuevo.upper() if original.isupper() and len(original) > 2 else nuevo


def revisar_local(texto: str):
    """Devuelve (texto_corregido, [(antes, después)])."""
    cambios = []
    t = texto or ""
    for pat, rep in DICCIONARIO:
        def _r(m, rep=rep):
            nuevo = _igualar_caso(m.group(0), m.expand(rep))
            if nuevo != m.group(0) and pat not in (r"[ \t]{2,}", r" ,"):
                cambios.append((m.group(0), nuevo))
            return nuevo
        t = re.sub(pat, _r, t, flags=re.IGNORECASE if not pat.startswith(r"\bVIENTI") and pat != r"\.\.(?!\.)" else 0)
    return t, cambios


def languagetool(texto: str, idioma="es"):
    """Sugerencias de LanguageTool. Devuelve lista de dicts: offset, length, original, sugerencia, mensaje."""
    if not (texto or "").strip():
        return []
    r = requests.post(LT_URL, data={"text": texto[:19000], "language": idioma, "disabledRules": "WHITESPACE_RULE,UPPERCASE_SENTENCE_START"},
                      timeout=25)
    if r.status_code == 429:
        raise RuntimeError("LanguageTool está recibiendo muchas consultas: espere un minuto y vuelva a intentar.")
    r.raise_for_status()
    out = []
    for m in r.json().get("matches", []):
        ori = texto[m["offset"]: m["offset"] + m["length"]]
        regla = m.get("rule", {})
        es_ortografia = regla.get("issueType") == "misspelling"
        if es_ortografia and (ori in VOCABULARIO or ori.strip(".").isupper() or ori[:1].isupper()):
            continue  # siglas, apellidos y nombres propios
        reps = [x["value"] for x in m.get("replacements", [])[:3]]
        if not reps:
            continue
        out.append({"offset": m["offset"], "length": m["length"], "original": ori, "sugerencia": reps[0],
                    "opciones": reps, "mensaje": m.get("message", ""), "tipo": "Ortografía" if es_ortografia else "Gramática / estilo"})
    return out


def aplicar(texto: str, sugerencias):
    """Aplica las sugerencias elegidas (de atrás hacia adelante para no correr los offsets)."""
    for s in sorted(sugerencias, key=lambda x: x["offset"], reverse=True):
        texto = texto[: s["offset"]] + s["sugerencia"] + texto[s["offset"] + s["length"]:]
    return texto


def _secret(k):
    try:
        import streamlit as st

        v = st.secrets.get(k)
    except Exception:
        v = None
    return (v or os.getenv(k) or "").strip() or None


def gemini_disponible():
    return bool(_secret("GEMINI_API_KEY"))


PROMPT = ("Sos corrector de estilo de notas administrativas de la Policía de Tucumán (Argentina). Corregí ortografía, gramática, "
          "puntuación y mejorá la redacción con un registro formal administrativo-policial, claro y conciso. NO cambies hechos, nombres, "
          "jerarquías, números, fechas, fojas ni artículos citados. No agregues información nueva ni saludos. Devolvé SOLO el texto corregido, "
          "sin comillas ni comentarios.\n\nTexto:\n")


def _gemini(parts, json_out=False, timeout=90, rapido=True):
    """Prueba los modelos en orden; si uno tarda o falla, pasa al siguiente."""
    key = _secret("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Falta GEMINI_API_KEY en Secrets (es gratuita: aistudio.google.com → Get API key).")
    base = GEMINI_RAPIDOS if rapido else GEMINI_MODELOS
    modelos = ([_secret("GEMINI_MODEL")] if _secret("GEMINI_MODEL") else []) + base
    ultimo = ""
    for m in dict.fromkeys(modelos):
        for pensar in (True, False):
            cfg = {"temperature": 0.2}
            if json_out:
                cfg["responseMimeType"] = "application/json"
            if pensar:  # respuesta más rápida: sin "razonamiento" largo
                cfg["thinkingConfig"] = {"thinkingBudget": 0} if "2.5" in m else {"thinkingLevel": "low"}
            try:
                r = requests.post(GEMINI_URL.format(m=m), headers={"x-goog-api-key": key, "Content-Type": "application/json"},
                                  json={"contents": [{"parts": parts}], "generationConfig": cfg}, timeout=timeout)
            except (requests.Timeout, requests.ConnectionError):
                ultimo = f"{m} tardó demasiado en responder"
                break  # siguiente modelo
            if r.status_code == 200:
                try:
                    return "".join(p.get("text", "") for p in r.json()["candidates"][0]["content"]["parts"]).strip()
                except (KeyError, IndexError):
                    ultimo = "Gemini no devolvió texto (puede que las imágenes no se lean bien)."
                    break
            if r.status_code == 429:
                raise RuntimeError("Se alcanzó el límite gratuito de Gemini por ahora. Intente en unos minutos.")
            ultimo = r.json().get("error", {}).get("message", r.text[:200]) if r.headers.get("content-type", "").startswith("application/json") else r.text[:200]
            if r.status_code == 400 and pensar and "think" in ultimo.lower():
                continue  # el modelo no admite esa opción: reintentar sin ella
            break
    raise RuntimeError(f"Gemini no respondió ({ultimo}). Intente nuevamente en unos segundos.")


def gemini_mejorar(texto: str, sensible=False) -> str:
    if sensible:
        raise PermissionError("Este documento contiene datos personales: no se envía a servicios de IA externos.")
    return _gemini([{"text": PROMPT + texto}], timeout=45, rapido=True)


def preparar_archivo(nombre: str, datos: bytes):
    """Fotos → JPEG liviano (máx. 1600 px); PDF tal cual. Devuelve (mime, bytes)."""
    import io

    if nombre.lower().endswith(".pdf"):
        return "application/pdf", datos
    from PIL import Image, ImageOps

    im = ImageOps.exif_transpose(Image.open(io.BytesIO(datos))).convert("RGB")
    im.thumbnail((1600, 1600))
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=80)
    return "image/jpeg", buf.getvalue()


PROMPT_FOTOS = """Sos oficial de la Dirección General de Institutos e Instrucción de la Policía de Tucumán (Argentina) y redactás la
tramitación de un expediente. Te adjunto fotos/escaneos de las fojas del expediente.

Datos del expediente en el sistema: {exp}
Documento a redactar: {modelo} — {desc}

Leé las fojas y redactá el contenido de estos campos (clave: descripción · ejemplo de estilo):
{campos}

Reglas:
- Registro formal administrativo-policial argentino, claro y conciso, como en las notas de la Dirección.
- Usá SOLO datos que figuren en las fojas o en los datos del expediente; NO inventes nombres, fechas, lugares, números ni artículos.
  Si un dato no se lee o no figura, escribí ________ en su lugar.
- No incluyas saludos, encabezados, referencias al expediente ni firma: solo el contenido de cada campo.
- Si un campo no corresponde según lo leído, devolvelo vacío "".
- Agregá además la clave "_resumen" con un resumen de 1 a 3 líneas de lo que pide el expediente.
Respondé SOLO un objeto JSON con esas claves."""


def gemini_desde_fotos(archivos, modelo_nombre, modelo_desc, campos, exp_txt):
    """archivos: [(mime, bytes)] · campos: [(clave, etiqueta, ayuda)] → dict clave → texto propuesto."""
    import base64
    import json

    if not archivos:
        raise ValueError("Agregue al menos una foto o PDF del expediente.")
    total = sum(len(b) for _, b in archivos)
    if total > 18 * 1024 * 1024:
        raise ValueError("Las fotos superan el máximo (18 MB). Suba menos fojas o fotos más livianas.")
    lista = "\n".join(f"- {k}: {lab}" + (f" · {ay}" if ay else "") for k, lab, ay in campos)
    parts = [{"text": PROMPT_FOTOS.format(exp=exp_txt, modelo=modelo_nombre, desc=modelo_desc, campos=lista)}]
    parts += [{"inline_data": {"mime_type": mime, "data": base64.b64encode(b).decode()}} for mime, b in archivos]
    txt = _gemini(parts, json_out=True, timeout=150, rapido=False)
    try:
        d = json.loads(txt.strip().removeprefix("```json").removesuffix("```"))
    except json.JSONDecodeError:
        raise RuntimeError("Gemini no devolvió un resultado válido. Intente de nuevo o con fotos más nítidas.")
    return {k: (str(v).strip() if v is not None else "") for k, v in d.items()}
