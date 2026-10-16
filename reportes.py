"""Salidas: Excel, PDF institucional, plantilla de carga masiva y enlaces de WhatsApp."""
import io
import re
import urllib.parse
from datetime import datetime
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

import catalogos as C

AZUL = colors.HexColor("#1E3A8A")
GRIS = colors.HexColor("#CBD5E1")


# ───────────────────────── WhatsApp ─────────────────────────
def normalizar_tel(tel):
    d = re.sub(r"\D", "", str(tel or ""))
    if not d:
        return ""
    if d.startswith("00"):
        d = d[2:]
    if d.startswith("549") and len(d) == 13:
        return d
    if d.startswith("54"):
        d = d[2:]
    d = d.lstrip("0")
    if len(d) == 12:  # 0381 15 5123456 -> quita el "15" local
        i = d.find("15", 2, 6)
        if i != -1:
            d = d[:i] + d[i + 2:]
    return "549" + d if len(d) == 10 else d


def link_whatsapp(mensaje, tel=None):
    t = normalizar_tel(tel)
    base = f"https://wa.me/{t}" if t else "https://wa.me/"
    return f"{base}?text={urllib.parse.quote(mensaje)}"


def _f(x, hora=False):
    if x is None or pd.isna(x):
        return "—"
    return pd.Timestamp(x).strftime("%d/%m/%Y %H:%M" if hora else "%d/%m/%Y")


def msg_movimiento(exp, mov):
    urg = "⚡ *URGENTE TRÁMITE*\n" if mov.get("urgente") or exp.get("prioridad") == "URGENTE TRÁMITE" else ""
    lineas = [
        f"📁 *{C.INSTITUCION_CORTA} – Movimiento de Expediente*",
        urg + f"*Exp. N° {exp['identificador']}* (Año {exp['anio']})",
        f"Tipo: {exp['tipo']}",
        f"Asunto: {exp.get('asunto') or '—'}",
        f"Movimiento: {mov['tipo']} · {mov.get('origen') or '—'} ➜ *{mov.get('destino') or '—'}*",
        f"Fecha/hora: {_f(mov['fecha_hora'], True)}",
    ]
    if mov.get("despacho"):
        lineas.append(f"Despacho: *{mov['despacho']}*")
    if mov.get("entregado_por"):
        lineas.append(f"Lo lleva: {mov['entregado_por']}")
    if mov.get("recibido_por"):
        lineas.append(f"Recibe: {mov['recibido_por']}")
    if mov.get("observaciones"):
        lineas.append(f"Obs.: {mov['observaciones']}")
    return "\n".join(lineas)


def msg_alta(exp):
    return "\n".join(
        [
            f"📁 *{C.INSTITUCION_CORTA} – Nuevo expediente registrado*",
            f"*Exp. N° {exp['identificador']}* (Año {exp['anio']})",
            f"Tipo: {exp['tipo']}",
            f"Origen: {exp.get('dependencia_origen') or exp.get('origen')}",
            f"Asunto: {exp.get('asunto') or '—'}",
            f"Ingreso: {_f(exp.get('fecha_ingreso'))}" + (" · ⚡ URGENTE TRÁMITE" if exp.get("prioridad") == "URGENTE TRÁMITE" else ""),
        ]
    )


def msg_alerta(titulo, detalle):
    return f"🔔 *{C.INSTITUCION_CORTA} – Aviso*\n*{titulo}*\n{detalle}"


# ───────────────────────── Excel ─────────────────────────
def excel(hojas: dict) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as xw:
        wb = xw.book
        fh = wb.add_format({"bold": True, "font_color": "#FFFFFF", "bg_color": "#1E3A8A", "border": 1, "text_wrap": True, "valign": "vcenter"})
        for nombre, df in hojas.items():
            df = df.copy()
            for c in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[c]):
                    df[c] = df[c].dt.tz_localize(None) if getattr(df[c].dt, "tz", None) else df[c]
            hoja = re.sub(r"[\[\]\*\?/\\:]", "", str(nombre))[:31] or "Hoja"
            df.to_excel(xw, sheet_name=hoja, index=False)
            ws = xw.sheets[hoja]
            for i, col in enumerate(df.columns):
                ws.write(0, i, str(col), fh)
                ancho = max([len(str(col))] + [len(str(v)) for v in df[col].head(300).tolist()]) + 2
                ws.set_column(i, i, min(max(ancho, 9), 55))
            ws.freeze_panes(1, 0)
            if len(df):
                ws.autofilter(0, 0, len(df), max(0, len(df.columns) - 1))
    return buf.getvalue()


COLUMNAS_PLANTILLA = [
    "NRO_EXP", "FOLIO", "ORDEN", "LIBRO", "AÑO", "FECHA_INGRESO", "TIPO", "ORIGEN", "DEPENDENCIA_ORIGEN",
    "NRO_EXP_ORIGEN", "ASUNTO", "INICIADOR", "PRIORIDAD", "FECHA_TERMINO", "ESTADO", "DESPACHO",
    "UBICACION_ACTUAL", "FOJAS", "OBSERVACIONES",
]


def plantilla_carga(tipos, dependencias) -> bytes:
    ej = pd.DataFrame(
        [
            [545, 120, 1, 1, 2026, "15/10/2026", "AUTORIZACIÓN PARA REALIZAR CURSO", "RECIBIDO DE OTRA DEPENDENCIA",
             "JEFATURA DE POLICÍA", "J-1234/26", "Curso de Tirador Especial", "Crio. Pérez", "NORMAL", "",
             "EN TRÁMITE", "", C.DEP_PROPIA, 5, ""],
            [546, 120, 2, 1, 2026, "15/10/2026", "SUMARIO ADMINISTRATIVO", "INICIADO EN LA DIRECCIÓN", "", "",
             "Sumario a Agte. Gómez", "", "URGENTE TRÁMITE", "20/10/2026", "REMITIDO", "VISTO BUENO",
             "JEFATURA DE POLICÍA", 12, ""],
        ],
        columns=COLUMNAS_PLANTILLA,
    )
    instr = pd.DataFrame(
        {
            "CAMPO": COLUMNAS_PLANTILLA,
            "DESCRIPCIÓN": [
                "N° de expediente correlativo (obligatorio)",
                "Foja izquierda del libro (obligatorio)",
                "N° de orden dentro del folio, inicia en 1 (obligatorio)",
                "N° de libro (si se omite: libro actual)",
                "Año (si se omite: año de la fecha de ingreso)",
                "dd/mm/aaaa (obligatorio)",
                "Ver hoja TIPOS (si no existe se puede crear al importar)",
                " / ".join(C.ORIGENES),
                "Dependencia que lo envía (ver hoja DEPENDENCIAS)",
                "Número que trae de la dependencia de origen",
                "Asunto / carátula",
                "Causante o iniciador",
                " / ".join(C.PRIORIDADES),
                "Fecha de término (urgente) dd/mm/aaaa",
                " / ".join(C.ESTADOS),
                " / ".join([d for d in C.DESPACHOS if d]),
                "Dónde está hoy el expediente",
                "Cantidad de fojas",
                "Texto libre",
            ],
        }
    )
    return excel(
        {
            "CARGA": ej,
            "INSTRUCCIONES": instr,
            "TIPOS": pd.DataFrame({"TIPO": list(tipos)}),
            "DEPENDENCIAS": pd.DataFrame({"DEPENDENCIA": list(dependencias)}),
        }
    )


# ───────────────────────── PDF ─────────────────────────
_ss = getSampleStyleSheet()
ST_T = ParagraphStyle("t", parent=_ss["Heading1"], fontSize=12, alignment=1, textColor=colors.HexColor("#0F172A"), spaceAfter=1)
ST_S = ParagraphStyle("s", parent=_ss["Normal"], fontSize=8.5, alignment=1, textColor=AZUL, spaceAfter=8)
ST_H = ParagraphStyle("h", parent=_ss["Normal"], fontSize=9, fontName="Helvetica-Bold", textColor=AZUL, spaceBefore=8, spaceAfter=4)
ST_B = ParagraphStyle("b", parent=_ss["Normal"], fontSize=7.8, leading=9.6, textColor=colors.HexColor("#1E293B"))
ST_BW = ParagraphStyle("bw", parent=ST_B, textColor=colors.white, fontName="Helvetica-Bold")
ST_K = ParagraphStyle("k", parent=ST_B, leading=16)


def _e(x):
    return "" if x is None or (isinstance(x, float) and pd.isna(x)) else escape(str(x))


def _tabla(df, anchos=None, max_filas=None):
    df = df.head(max_filas) if max_filas else df
    data = [[Paragraph(_e(c), ST_BW) for c in df.columns]]
    for _, r in df.iterrows():
        data.append([Paragraph("" if pd.isna(v) else _e(v), ST_B) for v in r.tolist()])
    t = Table(data, colWidths=anchos, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), AZUL),
                ("GRID", (0, 0), (-1, -1), 0.4, GRIS),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return t


def _encabezado(el, titulo, logo=None):
    if logo:
        try:
            el.append(Image(logo, width=16 * mm, height=18 * mm))
        except Exception:
            pass
    el.append(Paragraph("POLICÍA DE TUCUMÁN", ST_T))
    el.append(Paragraph(C.INSTITUCION, ST_S))
    el.append(Paragraph(titulo, ST_H))


def _pie(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawString(15 * mm, 9 * mm, f"Sistema de Registro de Expedientes · {C.INSTITUCION_CORTA} · emitido {datetime.now():%d/%m/%Y %H:%M}")
    canvas.drawRightString(doc.pagesize[0] - 15 * mm, 9 * mm, f"Pág. {doc.page}")
    canvas.restoreState()


def pdf_hoja_ruta(exp, movs, cursos, personal, logo=None) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=12 * mm, bottomMargin=15 * mm)
    el = []
    _encabezado(el, f"HOJA DE RUTA · EXPEDIENTE N° {exp['identificador']} (AÑO {exp['anio']})", logo)
    datos = [
        ["N° Exp / Folio / Orden", f"{exp['nro_exp']} / {exp['folio']} / {exp['orden']}", "Libro", str(exp.get("libro", ""))],
        ["Tipo", exp.get("tipo") or "", "Fecha ingreso", _f(exp.get("fecha_ingreso"))],
        ["Origen", exp.get("origen") or "", "Dependencia", exp.get("dependencia_origen") or "—"],
        ["N° origen", exp.get("nro_exp_origen") or "—", "Iniciador", exp.get("iniciador") or "—"],
        ["Estado", exp.get("estado") or "", "Prioridad", exp.get("prioridad") or ""],
        ["Despacho", exp.get("despacho") or "—", "Ubicación actual", exp.get("ubicacion_actual") or "—"],
        ["Fecha término", _f(exp.get("fecha_termino")), "Fojas", ("—" if pd.isna(exp.get("fojas")) or not exp.get("fojas") else str(int(exp["fojas"])))],
    ]
    t = Table([[Paragraph(f"<b>{a}</b>", ST_B), Paragraph(_e(b), ST_B), Paragraph(f"<b>{c}</b>", ST_B), Paragraph(_e(d), ST_B)] for a, b, c, d in datos],
              colWidths=[32 * mm, 58 * mm, 30 * mm, 60 * mm])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, GRIS), ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF2FF")),
                           ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#EEF2FF")), ("PADDING", (0, 0), (-1, -1), 3)]))
    el.append(t)
    el.append(Spacer(1, 4))
    el.append(Paragraph(f"<b>Asunto:</b> {_e(exp.get('asunto') or '—')}", ST_B))
    if exp.get("observaciones"):
        el.append(Paragraph(f"<b>Observaciones:</b> {_e(exp['observaciones'])}", ST_B))

    el.append(Paragraph("MOVIMIENTOS", ST_H))
    if movs.empty:
        el.append(Paragraph("Sin movimientos.", ST_B))
    else:
        m = movs.sort_values("fecha_hora").copy()
        tm = pd.DataFrame(
            {
                "Fecha/Hora": m["fecha_hora"].map(lambda x: _f(x, True)),
                "Mov.": m["tipo"],
                "Origen": m["origen"].fillna("—"),
                "Destino": m["destino"].fillna("—"),
                "Despacho": m["despacho"].fillna(""),
                "Lleva": m["entregado_por"].fillna(""),
                "Recibe": m["recibido_por"].fillna(""),
            }
        )
        el.append(_tabla(tm, [24 * mm, 18 * mm, 32 * mm, 32 * mm, 26 * mm, 24 * mm, 24 * mm]))

    if not cursos.empty:
        el.append(Paragraph("DATOS DEL CURSO / ACTIVIDAD", ST_H))
        for _, c in cursos.iterrows():
            el.append(Paragraph(
                f"<b>{_e(c['nombre'])}</b> · {_e(c.get('categoria'))} · Dicta: {_e(c.get('division_dicta') or '—')} · Lugar: {_e(c.get('lugar') or '—')} "
                f"({_e(c.get('ambito'))}) · {_f(c.get('fecha_inicio'))} al {_f(c.get('fecha_fin'))} · Modalidad: {_e(c.get('modalidad') or '—')} "
                f"· Requerimiento: <b>{_e(c.get('requerimiento') or '—')}</b> · Estado: {_e(c.get('estado') or '—')}", ST_B))
        if not personal.empty:
            tp = personal[["apellido", "nombre", "jerarquia", "dni", "division", "provincia", "rol"]].copy()
            tp.columns = ["Apellido", "Nombre", "Jerarquía", "DNI", "División", "Provincia", "Rol"]
            el.append(Spacer(1, 4))
            el.append(_tabla(tp, [30 * mm, 30 * mm, 30 * mm, 20 * mm, 30 * mm, 20 * mm, 20 * mm]))
    doc.build(el, onFirstPage=_pie, onLaterPages=_pie)
    return buf.getvalue()


def pdf_informe(titulo, periodo, kpis, secciones, logo=None, apaisado=True) -> bytes:
    """kpis: lista (etiqueta, valor). secciones: lista (subtítulo, DataFrame)."""
    buf = io.BytesIO()
    ps = landscape(A4) if apaisado else A4
    doc = SimpleDocTemplate(buf, pagesize=ps, leftMargin=12 * mm, rightMargin=12 * mm, topMargin=10 * mm, bottomMargin=15 * mm)
    el = []
    _encabezado(el, titulo, logo)
    el.append(Paragraph(f"Período: <b>{_e(periodo)}</b>", ST_B))
    el.append(Spacer(1, 4))
    if kpis:
        fila = [[Paragraph(f"<font size=7 color='#64748B'>{_e(k).upper()}</font><br/><font size=13><b>{_e(v)}</b></font>", ST_K) for k, v in kpis]]
        tk = Table(fila, colWidths=[(ps[0] - 24 * mm) / len(kpis)] * len(kpis))
        tk.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.5, GRIS), ("INNERGRID", (0, 0), (-1, -1), 0.5, GRIS),
                                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")), ("PADDING", (0, 0), (-1, -1), 6)]))
        el.append(tk)
    for sub, df in secciones:
        el.append(Paragraph(sub.upper(), ST_H))
        if df is None or df.empty:
            el.append(Paragraph("Sin registros para el período.", ST_B))
        else:
            el.append(_tabla(df, max_filas=600))
    doc.build(el, onFirstPage=_pie, onLaterPages=_pie)
    return buf.getvalue()
