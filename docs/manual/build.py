"""Arma el Manual de Usuario en PDF (A4) a partir de las maquetas generadas por screens.py."""
import os
from datetime import date

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Flowable, Frame, Image, KeepTogether, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

IMG = os.environ.get("IMG", "img")
SALIDA = os.environ.get("PDF", "Manual_Usuario_Expedientes_DGII.pdf")
LOGO = "assets/logo_policia.png"
LOGO2 = "assets/logo_dgii.png"

D = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("S", D + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("SB", D + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("SI", D + "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFontFamily("S", normal="S", bold="SB", italic="SI", boldItalic="SB")

NAVY = colors.HexColor("#0F1E46")
AZUL = colors.HexColor("#1D4ED8")
CELESTE = colors.HexColor("#DBEAFE")
TINTA = colors.HexColor("#1E293B")
GRIS = colors.HexColor("#64748B")
AMARILLO = colors.HexColor("#FACC15")
VERDE = colors.HexColor("#15803D")
NARANJA = colors.HexColor("#C2410C")

W, H = A4
M = 18 * mm
ANCHO = W - 2 * M

st = {
    "h1": ParagraphStyle("h1", fontName="SB", fontSize=19, leading=24, textColor=NAVY, spaceAfter=4),
    "h2": ParagraphStyle("h2", fontName="SB", fontSize=12.5, leading=16, textColor=AZUL, spaceBefore=8, spaceAfter=4),
    "p": ParagraphStyle("p", fontName="S", fontSize=10, leading=14.5, textColor=TINTA, spaceAfter=5),
    "pc": ParagraphStyle("pc", fontName="S", fontSize=8.5, leading=11, textColor=GRIS, alignment=TA_CENTER, spaceAfter=8),
    "paso": ParagraphStyle("paso", fontName="S", fontSize=10, leading=14, textColor=TINTA),
    "tip": ParagraphStyle("tip", fontName="S", fontSize=9.5, leading=13.5, textColor=TINTA),
    "cel": ParagraphStyle("cel", fontName="S", fontSize=9, leading=12, textColor=TINTA),
    "celb": ParagraphStyle("celb", fontName="SB", fontSize=9, leading=12, textColor=colors.white),
    "toc0": ParagraphStyle("toc0", fontName="SB", fontSize=11, leading=20, textColor=NAVY),
}


class Badge(Flowable):
    def __init__(self, n, color=AMARILLO, d=7.2 * mm):
        super().__init__()
        self.n, self.color, self.d = str(n), color, d
        self.width = self.height = d

    def draw(self):
        c = self.canv
        c.setFillColor(self.color)
        c.setStrokeColor(TINTA)
        c.setLineWidth(1.2)
        c.circle(self.d / 2, self.d / 2, self.d / 2 - 0.6, fill=1, stroke=1)
        c.setFillColor(TINTA)
        c.setFont("SB", 10.5)
        c.drawCentredString(self.d / 2, self.d / 2 - 3.7, self.n)


class Titulo(Paragraph):
    """Título de capítulo que se registra en el índice."""

    def __init__(self, texto, nivel=0):
        super().__init__(texto, st["h1"] if nivel == 0 else st["h2"])
        self.nivel = nivel
        self.texto = texto


def pasos(items, ancho=ANCHO):
    filas = [[Badge(n), Paragraph(t, st["paso"])] for n, t in items]
    t = Table(filas, colWidths=[10 * mm, ancho - 10 * mm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                           ("TOPPADDING", (0, 0), (-1, -1), 1), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    return t


def caja(texto, tipo="tip", ancho=ANCHO, suelta=False):
    fondo, borde, icono = {"tip": (CELESTE, AZUL, "Consejo"), "ojo": (colors.HexColor("#FEF3C7"), colors.HexColor("#D97706"), "Importante"),
                           "ok": (colors.HexColor("#DCFCE7"), VERDE, "Recuerde")}[tipo]
    t = Table([[Paragraph(f"<b>{icono}:</b> {texto}", st["tip"])]], colWidths=[ancho])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), fondo), ("LINEBEFORE", (0, 0), (0, -1), 4, borde),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                           ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return t if suelta else KeepTogether([Spacer(1, 3), t, Spacer(1, 6)])


def imagen(nombre, ancho=ANCHO, pie=None):
    ruta = os.path.join(IMG, nombre)
    from PIL import Image as PI

    w, h = PI.open(ruta).size
    im = Image(ruta, width=ancho, height=ancho * h / w)
    marco = Table([[im]], colWidths=[ancho])
    marco.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    out = [marco]
    if pie:
        out += [Spacer(1, 3), Paragraph(pie, st["pc"])]
    return KeepTogether(out)


def tabla(cab, filas, anchos, color=NAVY):
    data = [[Paragraph(c, st["celb"]) for c in cab]] + [[Paragraph(str(v), st["cel"]) for v in f] for f in filas]
    t = Table(data, colWidths=anchos, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), color), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                           ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return t


# ───────────────────────── Páginas ─────────────────────────
def portada(c, doc):
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#1D4ED8"))
    c.rect(0, H * 0.36, W, 4, fill=1, stroke=0)
    try:
        c.drawImage(LOGO, W / 2 - 62 * mm / 2 - 20 * mm, H - 95 * mm, width=36 * mm, height=42 * mm, mask="auto", preserveAspectRatio=True)
        c.drawImage(LOGO2, W / 2 + 6 * mm, H - 95 * mm, width=36 * mm, height=42 * mm, mask="auto", preserveAspectRatio=True)
    except Exception:
        pass
    c.setFillColor(colors.HexColor("#93C5FD"))
    c.setFont("SB", 11)
    c.drawCentredString(W / 2, H - 112 * mm, "POLICÍA DE TUCUMÁN")
    c.setFont("S", 11)
    c.drawCentredString(W / 2, H - 119 * mm, "DIRECCIÓN GENERAL DE INSTITUTOS E INSTRUCCIÓN")
    c.setFillColor(colors.white)
    c.setFont("SB", 34)
    c.drawCentredString(W / 2, H - 148 * mm, "MANUAL DE USUARIO")
    c.setFont("S", 15)
    c.drawCentredString(W / 2, H - 160 * mm, "Sistema de Registro y Control de Expedientes")
    c.setFillColor(AMARILLO)
    c.roundRect(W / 2 - 68 * mm, H - 180 * mm, 136 * mm, 11 * mm, 5.5 * mm, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("SB", 11)
    c.drawCentredString(W / 2, H - 176.2 * mm, "Oficial · Suboficial · Comisionista · PC y celular")
    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.setFont("S", 10)
    c.drawCentredString(W / 2, 40 * mm, "expedientesdgii.streamlit.app")
    c.setFillColor(colors.white)
    c.setFont("S", 10)
    c.drawCentredString(W / 2, 62 * mm, "Elaborado por")
    c.setFont("SB", 12.5)
    c.drawCentredString(W / 2, 55 * mm, "Oficial Auxiliar PONCE Sergio")
    c.setFont("S", 10)
    c.drawCentredString(W / 2, 49.5 * mm, "I.E.S.P. – Policía de Tucumán")
    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.drawCentredString(W / 2, 33 * mm, f"Versión 2.0 · {date.today():%m/%Y}")
    c.restoreState()


def normal(c, doc):
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, H - 12 * mm, W, 12 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("SB", 8.5)
    c.drawString(M, H - 7.6 * mm, "MANUAL DE USUARIO · REGISTRO DE EXPEDIENTES")
    c.setFont("S", 8.5)
    c.drawRightString(W - M, H - 7.6 * mm, "D.G.I.I. · POLICÍA DE TUCUMÁN")
    c.setStrokeColor(colors.HexColor("#CBD5E1"))
    c.line(M, 13 * mm, W - M, 13 * mm)
    c.setFillColor(GRIS)
    c.setFont("S", 8)
    c.drawString(M, 8.5 * mm, "Uso interno – D.G.I.I. · Elaborado por Of. Aux. Ponce Sergio (I.E.S.P.)")
    c.drawRightString(W - M, 8.5 * mm, f"Página {doc.page}")
    c.restoreState()


class Doc(BaseDocTemplate):
    def __init__(self, ruta):
        super().__init__(ruta, pagesize=A4, leftMargin=M, rightMargin=M, topMargin=20 * mm, bottomMargin=18 * mm,
                         title="Manual de Usuario – Registro de Expedientes D.G.I.I.", author="Oficial Auxiliar Ponce Sergio – I.E.S.P.")
        fr = Frame(M, 18 * mm, ANCHO, H - 38 * mm, id="f")
        self.addPageTemplates([PageTemplate("portada", [Frame(0, 0, W, H)], onPage=portada),
                               PageTemplate("normal", [fr], onPage=normal)])

    def afterFlowable(self, f):
        if isinstance(f, Titulo):
            self.notify("TOCEntry", (f.nivel, f.texto, self.page))


def h1(t):
    return [PageBreak(), Titulo(t, 0), Spacer(1, 2)]


def h2(t):
    return [CondPageBreak(30 * mm), Titulo(t, 1)]


def p(t):
    return Paragraph(t, st["p"])


def armar():
    s = [NextPageTemplate("normal"), PageBreak()]

    # Índice
    s += [Paragraph("Índice", st["h1"]), Spacer(1, 6)]
    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle("t0", fontName="SB", fontSize=11, leading=19, textColor=NAVY),
                       ParagraphStyle("t1", fontName="S", fontSize=9.5, leading=15, leftIndent=14, textColor=TINTA)]
    s += [toc]

    # ── Antes de empezar ──
    s += h1("Antes de empezar")
    s += [p("El sistema lleva el <b>libro de registro</b> de la Dirección y del I.E.S.P. en la computadora y en el celular. "
            "Permite saber en todo momento <b>qué expedientes hay, dónde está cada uno, quién lo tiene, si ya fue tramitado</b>, "
            "qué vence y qué actividades se desarrollan. Además <b>redacta las notas en Word</b>, lee las fojas con IA y avisa por WhatsApp."),
          p("La idea central es simple: <b>cada uno tiene su propia ruta de trabajo</b> y el expediente pasa de una bandeja a la "
            "otra <b>sin volver a cargar datos</b>."),
          imagen("19_roles.png", pie="Figura 1. Las tres rutas de trabajo: suboficial, oficial y comisionista.")]
    s += h2("¿Qué puede hacer cada usuario?")
    s += [tabla(["Rol", "Quiénes", "Qué hace"],
                [["<b>SUBOFICIAL</b>", "Suboficial Mayor a Agente", "Recibe y registra expedientes (nuevos y reingresos), registra movimientos, sube el PDF, carga actividades. Puede hacer entregas."],
                 ["<b>OFICIAL</b>", "Comisario General a Oficial Subayudante", "Todo lo anterior + <b>tramita</b> (notas en Word, elevaciones, pases, oficios, actuaciones), despacha y corrige. Puede borrar los expedientes que cargó él."],
                 ["<b>COMISIONISTA</b>", "Personal designado para llevar expedientes", "Solo ve <b>Comisión</b>: lleva los expedientes encargados y registra <b>quién los recibe</b>."],
                 ["<b>ADMINISTRADOR</b>", "Responsable del sistema", "Todo + usuarios, autoridades, dependencias, despachos, numeración, IA, carga masiva y respaldos."]],
                [32 * mm, 44 * mm, ANCHO - 76 * mm]),
          Spacer(1, 6),
          caja("Todo queda registrado con su <b>grado, apellido y nombre</b>, la fecha y la hora. Cada persona ingresa con <b>su propio legajo</b> "
               "y nunca comparte la clave.", "ojo"),
          caja("<b>Dos libros, mismo personal:</b> la Dirección (D.G.I.I.) y el I.E.S.P. llevan cada uno su libro con <b>numeración propia</b>. "
               "Al cargar un expediente el sistema siempre pregunta a cuál corresponde.", "tip")]

    # ── 1 Ingreso ──
    s += h1("1. Ingresar al sistema")
    s += [p("Abra <b>expedientesdgii.streamlit.app</b> en el navegador. En el celular conviene agregarlo a la pantalla de inicio "
            "(menú del navegador → <i>Agregar a pantalla principal</i>) para abrirlo como una aplicación."),
          imagen("01_login.png", pie="Figura 2. Pantalla de ingreso."),
          pasos([(1, "Escriba su <b>número de legajo</b>."),
                 (2, "Escriba su <b>clave</b>. La primera vez usa la clave inicial que le dio el administrador."),
                 (3, "Toque <b>Ingresar</b>. En el primer ingreso el sistema le pide crear su <b>clave personal</b> (mínimo 6 caracteres).")]),
          caja("Al ingresar, el sistema lo lleva directo a <b>Mi trabajo</b>, con lo que le toca hacer según su rol. "
               "Al terminar la jornada use <b>Salir</b>, sobre todo en computadoras compartidas.", "ok")]

    # ── 2 Pantalla ──
    s += h1("2. Conocer la pantalla")
    s += [imagen("20_mi_trabajo.png", pie="Figura 3. Mi trabajo: la pantalla de inicio del oficial."),
          pasos([(1, "<b>Su ruta</b>: los pasos de su trabajo, de izquierda a derecha."),
                 (2, "<b>Llegó un expediente</b>: buscador de la mesa de entradas (también lo tienen los oficiales)."),
                 (3, "<b>Bandejas</b>: <i>Para tramitar</i>, <i>Para despachar</i> y <i>Con el comisionista</i>, con la cantidad de cada una."),
                 (4, "<b>Nota en Word</b>: abre Tramitar con ese expediente ya elegido."),
                 (5, "<b>Tramitar y despachar</b>: registra el trámite y a dónde va, en la misma tarjeta.")]),
          tabla(["Menú", "Para qué sirve"],
                [["Mi trabajo", "Su bandeja: lo que tiene que hacer hoy. <b>Empiece siempre aquí.</b>"],
                 ["Panel de Control", "Resumen general: cantidades, urgentes, vencidos, actividades de la semana, parte del día."],
                 ["Nuevo Expediente", "Alta de un expediente en el libro."],
                 ["Movimiento Rápido", "Trámite, reingreso o movimiento de un expediente desde el celular."],
                 ["Tramitar", "Redacta notas, pases, elevaciones, oficios y actuaciones en Word (oficiales)."],
                 ["Comisión (entregas)", "Entregas del comisionista y quién recibió cada expediente."],
                 ["Libro de Registro", "Todos los expedientes con filtros, por folio y exportación."],
                 ["Ficha de Expediente", "Todo sobre un expediente: trámite, PDF, hoja de ruta, edición."],
                 ["Actividades y Personal", "Cursos, eventos, disertaciones y el personal afectado."],
                 ["Alertas y Agenda", "Vencimientos, expedientes detenidos, inicios de actividades."],
                 ["Informes", "Estadística, pendientes, libro de movimientos (PDF / Excel / WhatsApp)."],
                 ["Configuración", "Solo administrador."]],
                [42 * mm, ANCHO - 42 * mm], AZUL)]
    tel = Image(os.path.join(IMG, "03_movil.png"), width=55 * mm, height=55 * mm * 1160 / 580)
    txt = [pasos([(1, "La <b>barra azul</b> de arriba es el menú: tóquela para cambiar de sección."),
                  (2, "El botón <b>›</b> abre su usuario, el cambio de clave y Salir."),
                  (3, "Todas las pantallas están pensadas para usarse con una mano; los botones grandes ocupan todo el ancho.")],
                 ancho=ANCHO - 63 * mm),
           Spacer(1, 6),
           caja("En las listas desplegables puede <b>escribir</b> para buscar: dos o tres letras del apellido o del número alcanzan.",
                ancho=ANCHO - 63 * mm, suelta=True)]
    t = Table([[tel, txt]], colWidths=[61 * mm, ANCHO - 61 * mm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    s += [KeepTogether([Titulo("En el celular", 1), t])]

    # ── 3 Suboficial ──
    s += h1("3. Ruta del suboficial: recibir y registrar")
    s += [p("Cuando llega un expediente a la Dirección, <b>primero se busca</b>: puede ser uno que <b>vuelve</b> (reingreso) o uno <b>nuevo</b>. "
            "Así nunca se duplica un número."),
          imagen("21_mesa.png", pie="Figura 4. Mi trabajo → Llegó un expediente."),
          pasos([(1, "Escriba el <b>N° de la Dirección</b>, el <b>N° de origen</b> (ej. J-1234/26) o parte del <b>asunto</b>."),
                 (2, "Si aparece, toque <b>Volvió: registrar reingreso</b>. Se asienta sobre el <b>mismo</b> N°/folio/orden."),
                 (3, "Indique de dónde vuelve y <b>con qué despacho o resolución</b>. Si falta uno, agréguelo con <b>+ Despacho</b> o escríbalo."),
                 (4, "Quién lo trae y quién lo recibe se eligen de una <b>lista con buscador</b> (ya trae su nombre)."),
                 (5, "Si no aparece, toque <b>cargar como nuevo</b>.")]),
          caja("Tras el reingreso el expediente vuelve a <b>PENDIENTE DE TRÁMITE</b> y aparece en la bandeja del oficial. "
               "El trámite anterior queda en la hoja de ruta.", "ok")]
    s += h2("Registrar un expediente nuevo")
    s += [imagen("22_libro_elegir.png", pie="Figura 5. Primero se elige el libro."),
          pasos([(1, "<b>D.G.I.I.</b>: asuntos de la Dirección."),
                 (2, "<b>I.E.S.P.</b>: asuntos del Instituto. Cada libro propone su propio N°, folio y orden.")]),
          imagen("06_libro_fisico.png", pie="Figura 6. Cómo se numera: N° de expediente / Folio (foja izquierda) / N° de orden."),
          imagen("05_nuevo_2.png", pie="Figura 7. Datos del expediente."),
          pasos([(1, "Fecha y hora de ingreso y con qué <b>sale</b> (si no se sabe, “A definir”)."),
                 (2, "N° de origen e <b>iniciador / causante</b>."),
                 (3, "Asunto, prioridad (<b>Urgente</b> con fecha de término), fojas y ubicación."),
                 (4, "Quién lo trajo y quién lo recibió (listas con buscador)."),
                 (5, "Toque <b>Registrar expediente</b>. Si ya estaba tramitado, ahí mismo puede <b>tramitarlo y despacharlo</b>.")]),
          caja("Verifique que la identificación (ej. 584/56/6) coincida con lo escrito en el libro físico. Si el número ya existe, "
               "el sistema avisa en rojo y no deja guardar.", "ojo")]
    s += h2("Subir el expediente en PDF o fotos")
    s += [imagen("09_pdf.png", pie="Figura 8. Ficha → pestaña PDF."),
          p("Elija <b>Archivo PDF</b> o <b>Fotos de las fojas</b> (se unen en un PDF en el orden elegido) y toque <b>Subir a Google Drive</b>. "
            "Las versiones anteriores quedan guardadas.")]

    # ── 4 Oficial ──
    s += h1("4. Ruta del oficial: tramitar y despachar")
    s += [p("El oficial trabaja desde <b>Mi trabajo → Para tramitar</b>. Los expedientes vienen ordenados: <b>vencidos</b>, "
            "<b>urgentes</b> y los que <b>más días esperan</b>, primero. Para cada uno elige uno de dos caminos:"),
          tabla(["Camino", "Cuándo usarlo", "Qué hace el sistema"],
                [["<b>Nota en Word</b>", "Hay que redactar una nota, pase, elevación, oficio o pieza de actuación.",
                  "Arma el Word y, si la nota sale de la Dirección, lo deja <b>TRAMITADO</b> y <b>encargado al comisionista</b>."],
                 ["<b>Tramitar y despachar</b>", "La nota ya está hecha o es un trámite simple.",
                  "Registra qué se hizo y a dónde va, en <b>un solo paso</b>."]],
                [36 * mm, 60 * mm, ANCHO - 96 * mm], VERDE)]
    s += h2("Tramitar y despachar en un paso")
    s += [imagen("23_tramitar_despachar.png", pie="Figura 9. Trámite y salida en el mismo formulario."),
          pasos([(1, "<b>Qué se hizo</b> y <b>quién</b> (ya viene su nombre). Fecha y hora son las de ese momento; si fue otra, ábrala en «Otra fecha u hora»."),
                 (2, "<b>¿Y después?</b> — <i>Lo lleva el comisionista</i>, <i>Sale ahora (lo entrego yo)</i> o <i>Queda en la Dirección</i>."),
                 (3, "Destino, despacho e indicaciones para el comisionista. Si sale ahora: quién lo recibe y fojas."),
                 (4, "Un solo botón: <b>Tramitar y despachar</b>. Queda todo en la hoja de ruta.")])]
    s += h2("Redactar la nota en Word (Tramitar)")
    s += [imagen("24_tramitar_word.png", pie="Figura 10. Tramitar: modelo, datos, vista previa y Word."),
          pasos([(1, "El <b>expediente</b> ya viene elegido si llegó desde Mi trabajo."),
                 (2, "Elija <b>qué va a hacer</b>: notas y pases, notificación, proyecto, oficios judiciales o actuaciones / sumario, y luego el modelo."),
                 (3, "<b>Completar con IA</b> (opcional): lee las fotos de las fojas y propone el texto (ver más abajo)."),
                 (4, "Complete los datos: destinatario, opinión, cuerpo. Los campos vienen agrupados y con ejemplos."),
                 (5, "La <b>vista previa</b> muestra cómo queda la nota con el membrete, en hoja oficio."),
                 (6, "<b>Revisar redacción</b>: diccionario propio + corrector gratuito (ortografía y estilo)."),
                 (7, "<b>Generar Word</b>.")]),
          tabla(["Grupo", "Modelos"],
                [["Notas y pases", "Elevación con opinión, pase a la Superioridad, a CITTU, a Relaciones, a Compañía, al Gabinete, sanción con visto bueno, devolver al origen."],
                 ["Notificación / Proyecto", "Notificación al causante; proyecto de resolución o nota."],
                 ["Oficios judiciales", "Respuesta, pase para informe, comparendo, rueda de reconocimiento, notificación."],
                 ["Actuaciones / Sumario", "Carátula, acta de apertura, providencia, valoración, testigo, causante, visu, defensa, análisis, conclusiones, elevación."]],
                [40 * mm, ANCHO - 40 * mm], AZUL),
          Spacer(1, 6),
          imagen("26_resultado.png", pie="Figura 11. Después de generar el Word."),
          pasos([(1, "<b>Descargar Word</b> para imprimir y firmar."),
                 (2, "El expediente ya quedó <b>TRAMITADO</b> y <b>encargado al comisionista</b> con el destino de la nota."),
                 (3, "<b>Cambiar</b>: otro destino, “lo entrego yo ahora” (registra la salida) o “queda aquí”."),
                 (4, "<b>Deshacer</b> si en realidad no estaba terminado."),
                 (5, "<b>Volver a Mi trabajo</b> y seguir con el próximo expediente.")]),
          caja("Si el sistema no reconoce a qué dependencia va la nota, la elige una vez y <b>queda aprendida</b> para las próximas notas a esa autoridad. "
               "Las piezas internas de una actuación (actas, declaraciones, providencias) <b>no</b> marcan el expediente como tramitado.", "tip")]
    s += h2("Completar con IA: fotos e instrucciones")
    s += [imagen("25_ia.png", pie="Figura 12. La IA lee las fojas y redacta siguiendo sus instrucciones."),
          pasos([(1, "Saque <b>fotos</b> de las fojas con el celular o suba el PDF."),
                 (2, "Toque <b>indicaciones rápidas</b>: opinión favorable / desfavorable, breve, detallado, mencionar fojas, notificar al causante…"),
                 (3, "Escriba <b>instrucciones libres</b>: qué destacar, qué pedir, qué no mencionar."),
                 (4, "Toque <b>Leer fojas y proponer el texto</b>. Sin fotos, el botón dice <i>Proponer el texto con mis instrucciones</i>."),
                 (5, "Si le sirve: <b>Usar estos textos</b>. Si no, cambie las instrucciones y vuelva a pedir.")]),
          caja("La IA <b>no inventa datos</b>: si falta un nombre, fecha o número deja <b>________</b> para que usted lo complete. "
               "Los documentos con datos personales (sanciones, actuaciones, oficios judiciales) no se envían a la IA salvo que el administrador lo habilite.", "ojo")]
    s += h2("Para despachar y Con el comisionista")
    s += [p("<b>Para despachar</b> muestra lo que ya está tramitado pero sigue en la Dirección: tóquelo y elija comisionista, "
            "sale ahora o queda. <b>Con el comisionista</b> muestra lo encargado que todavía no se entregó.")]

    # ── 5 Comisionista ──
    s += h1("5. Ruta del comisionista: entregar")
    tel = Image(os.path.join(IMG, "27_comision.png"), width=62 * mm, height=62 * mm * 1220 / 580)
    txt = [p("El comisionista ve <b>una sola pantalla</b>: <b>Comisión</b>."),
           pasos([(1, "<b>Para entregar</b>: lo que encargaron los oficiales, con destino, despacho e indicaciones. <b>Entregados hoy</b>: lo que ya llevó."),
                  (2, "Toque <b>Entregar</b> en el expediente que va a llevar."),
                  (3, "Cargue <b>quién lo recibe</b> (obligatorio). Destino y despacho ya vienen."),
                  (4, "<b>Registrar entrega</b>: la SALIDA queda asentada con quién lo recibió y el oficial ya la ve."),
                  (5, "<b>Avisar por WhatsApp</b> a la dependencia.")], ancho=ANCHO - 70 * mm),
           Spacer(1, 6),
           caja("Si lleva un expediente tramitado que no estaba encargado, use <b>Buscar otro expediente tramitado</b>.",
                ancho=ANCHO - 70 * mm, suelta=True)]
    t = Table([[tel, txt]], colWidths=[68 * mm, ANCHO - 68 * mm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    s += [t]

    # ── 6 Ficha y hoja de ruta ──
    s += h1("6. La ficha y la hoja de ruta")
    s += [imagen("29_hoja_ruta.png", pie="Figura 13. Hoja de ruta: todo lo que pasó con el expediente."),
          pasos([(1, "<b>Para entregar</b> (arriba, en naranja): está con el comisionista; al entregarlo se asienta la salida."),
                 (2, "<b>TRAMITADO en …</b>: qué se hizo y quién lo tramitó. No es un traslado: el expediente sigue en la Dirección."),
                 (3, "<b>INGRESO / SALIDA / REINGRESO</b>: de dónde a dónde, quién lo llevó y quién lo recibió."),
                 (4, "<b>Corregir</b>: un oficial puede eliminar movimientos o trámites cargados por error; el sistema recalcula dónde está.")]),
          tabla(["Pestaña", "Para qué sirve"],
                [["Trámite", "Tramitar y despachar, o despachar lo ya tramitado. Anular la marca."], ["PDF", "Subir o ver el expediente digitalizado."],
                 ["Hoja de ruta", "Historial completo y corrección de errores."], ["Registrar movimiento", "Salida, ingreso, pase, devolución o archivo."],
                 ["Curso y personal", "Actividad vinculada y efectivos afectados."], ["Alertas", "Recordatorios propios del expediente."],
                 ["Editar", "Corregir datos y libro. <b>Eliminar</b>: el administrador, o el oficial que lo cargó."]],
                [42 * mm, ANCHO - 42 * mm], AZUL),
          Spacer(1, 6),
          caja("Arriba de la ficha: <b>Hoja de ruta (PDF)</b> para imprimir y <b>Compartir por WhatsApp</b> con el estado del expediente.", "tip")]

    # ── 7 WhatsApp ──
    s += h1("7. Informar por WhatsApp")
    s += [p("En casi todas las pantallas hay un botón verde de WhatsApp que arma el mensaje con lo que se ve en ese momento."),
          imagen("28_whatsapp.png", pie="Figura 14. El mensaje se revisa y se envía a una dependencia o a un grupo."),
          pasos([(1, "Toque el botón verde."),
                 (2, "<b>Enviar a</b>: una dependencia con WhatsApp cargado, o <i>Elegir contacto</i> (abre sus contactos y grupos)."),
                 (3, "Revise o corrija el texto."),
                 (4, "<b>Abrir WhatsApp</b> y enviar.")]),
          tabla(["Pantalla", "Qué informa"],
                [["Panel de Control", "Parte del día: cantidades, urgentes, vencidos, actividades en curso."],
                 ["Actividades → Qué está pasando", "En desarrollo hoy, próximos 7 días, próximo mes, terminadas."],
                 ["Actividades → Actividades / Personal", "Una actividad con su personal, o el personal filtrado."],
                 ["Alertas", "Las alertas del filtro elegido."], ["Libro de Registro", "Los expedientes filtrados."],
                 ["Informes", "Resumen del período, pendientes, movimientos, actividades."],
                 ["Comisión", "Lo que falta entregar y lo entregado hoy."], ["Ficha", "Estado del expediente y último movimiento."]],
                [60 * mm, ANCHO - 60 * mm], VERDE)]

    # ── 8 Libro ──
    s += h1("8. Libro de Registro")
    s += [imagen("10_libro.png", pie="Figura 15. Libro de Registro con filtros."),
          pasos([(1, "<b>Filtros</b>: texto, libro (D.G.I.I. / I.E.S.P.), año, tipo, estado, ubicación, destino, fechas y trámite."),
                 (2, "Toque una fila para ver el detalle y abrir la ficha."),
                 (3, "Vistas: <b>Tabla</b>, <b>Tarjetas</b> (celular) y <b>Por folio</b> (como el libro físico). <b>Exportar a Excel</b>.")])]

    # ── 9 Actividades ──
    s += h1("9. Actividades y personal")
    s += [p("Todo lo que acontece — cursos, formaciones, disertaciones, congresos, tiro, eventos, actos, colaboraciones — <b>tenga o no expediente</b>."),
          imagen("15_actividades.png", pie="Figura 16. Qué está pasando."),
          imagen("16_actividad_form.png", pie="Figura 17. Nueva actividad con su personal."),
          pasos([(1, "Tipo, hora y quién organiza."),
                 (2, "Categoría (realizar, dictar, organizar, asistir) y qué se solicita."),
                 (3, "Personal afectado: oficiales, suboficiales, PTP, cadetes y aspirantes, con su rol."),
                 (4, "<b>Guardar</b>: cuenta para alertas, estadística e historial de cada efectivo.")])]

    # ── 10 Alertas e informes ──
    s += h1("10. Alertas, agenda e informes")
    s += [imagen("12_alertas.png", pie="Figura 18. Alertas por prioridad."),
          tabla(["Alerta", "Cuándo aparece"],
                [["Días sin tramitar", "Expediente <b>en la Dirección y sin tramitar</b> (urgentes a los 2 días)."],
                 ["Tramitado y sigue en la Dirección", "Recordatorio para entregarlo."],
                 ["Fuera de la Dirección", "Aviso informativo si pasa mucho tiempo sin novedades en otra dependencia."],
                 ["Vencido / vence", "Fecha de término de un expediente <b>no tramitado</b>."],
                 ["Actividades", "Inicio hoy o próximo, sin autorización, pendientes de cerrar."]],
                [55 * mm, ANCHO - 55 * mm], AZUL),
          Spacer(1, 6),
          p("<b>Informes</b>: gestión del período, control de pendientes, libro de movimientos y estadística de actividades, en PDF, Excel o WhatsApp.")]

    # ── 11 Administrador ──
    s += h1("11. Configuración (administrador)")
    s += [imagen("14_usuarios.png", pie="Figura 19. Usuarios."),
          tabla(["Pestaña", "Qué se configura"],
                [["Usuarios", "Alta con grado, apellido, nombre y rol (OFICIAL, SUBOFICIAL, COMISIONISTA, ADMINISTRADOR). Blanquear clave. Deshabilitar (no borrar)."],
                 ["Notas y autoridades", "Libreta de autoridades (tratamiento, cargo, titular, relación) y la columna <b>«El comisionista lo lleva a»</b>. Elevar a Jefatura o Subjefatura. IA de redacción."],
                 ["Libro y alertas", "Numeración de cada libro (D.G.I.I. e I.E.S.P.): N° inicial, folio, renglones por folio, reinicio anual. Plazos de alerta."],
                 ["Dependencias y colores", "Dependencias, siglas, colores y <b>WhatsApp</b> de cada una."],
                 ["Tipos", "Tipos de expediente y cuáles generan actividades."],
                 ["Google Drive / Respaldo", "Carpeta de los PDF; respaldo completo en Excel."]],
                [45 * mm, ANCHO - 45 * mm], NAVY),
          Spacer(1, 6),
          caja("Los <b>despachos</b> nuevos (ej. RESOLUCIÓN, PARA SU CONOCIMIENTO Y EFECTOS) los agrega cualquiera con <b>+ Despacho</b> y quedan para todos.", "tip"),
          caja("<b>Carga Masiva</b> (solo administrador): pasa al sistema los asientos ya escritos en el libro, desde Excel o tipeando renglón por renglón.", "tip")]

    # ── Guía rápida ──
    s += h1("Guía rápida por rol")

    def col(titulo, color, items):
        filas = [[Paragraph(f"<b>{titulo}</b>", ParagraphStyle("x", parent=st["celb"], fontSize=10.5, leading=13))]]
        filas += [[Paragraph(f"<font color='#15803D'><b>{i + 1}.</b></font>  {t}", st["cel"])] for i, t in enumerate(items)]
        t = Table(filas, colWidths=[(ANCHO - 8 * mm) / 3])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), color), ("BOX", (0, 0), (-1, -1), 0.8, color),
                               ("LINEBELOW", (0, 1), (-1, -2), 0.3, colors.HexColor("#E2E8F0")),
                               ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        return t
    sub = col("SUBOFICIAL", colors.HexColor("#B45309"), [
        "Abrir <b>Mi trabajo</b>.", "Llegó un expediente: <b>buscar el N°</b>.", "Si existe: <b>reingreso</b> con despacho.",
        "Si no: <b>nuevo</b>, eligiendo el libro.", "Verificar N°/folio/orden con el libro.", "Subir el <b>PDF</b> o fotos.",
        "Cargar <b>actividades</b> y personal.", "Revisar <b>Alertas</b>."])
    of = col("OFICIAL", colors.HexColor("#15803D"), [
        "Abrir <b>Mi trabajo → Para tramitar</b>.", "Empezar por vencidos y urgentes.", "<b>Nota en Word</b> (con IA si sirve) o <b>Tramitar y despachar</b>.",
        "Imprimir y firmar.", "Revisar <b>Para despachar</b>.", "Controlar <b>Con el comisionista</b>.",
        "Corregir errores desde la ficha.", "Parte del día por <b>WhatsApp</b>."])
    com = col("COMISIONISTA", colors.HexColor("#6D28D9"), [
        "Abrir <b>Comisión</b>.", "Ver <b>Para entregar</b> y las indicaciones.", "Llevar el expediente.",
        "<b>Entregar</b>: cargar quién lo recibe.", "<b>Registrar entrega</b>.", "<b>Avisar por WhatsApp</b>.",
        "Revisar <b>Entregados hoy</b>.", "Ante dudas, consultar al oficial."])
    t = Table([[sub, of, com]], colWidths=[ANCHO / 3] * 3)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]))
    s += [t]

    # ── Preguntas frecuentes ──
    s += h1("Preguntas frecuentes")
    grupos = [
        ("Ingreso y uso general", [
            ("Olvidé mi clave.", "El administrador la blanquea en <b>Configuración → Usuarios</b>. Al ingresar deberá crear una nueva."),
            ("La página se ve vieja, no carga o aparece un error.", "Toque <b>Actualizar</b> en el menú o recargue el navegador (Ctrl + F5 en la PC; deslizar hacia abajo en el celular). Si sigue, envíe una captura al administrador."),
            ("¿Puedo usarlo en el celular?", "Sí. Todas las pantallas funcionan en el celular; conviene agregarlo a la pantalla de inicio."),
            ("No veo algunas opciones del menú.", "Cada rol ve lo que necesita. Tramitar es solo para oficiales; Configuración y Carga Masiva, para el administrador; el comisionista solo ve Comisión.")]),
        ("Cargar expedientes", [
            ("¿D.G.I.I. o I.E.S.P.?", "Elija el libro al que corresponde el asunto. Cada uno tiene su numeración; el mismo personal trabaja en ambos."),
            ("El número propuesto no coincide con el libro.", "Corrija N°, folio u orden antes de registrar. Si ya lo registró, un oficial lo corrige en <b>Ficha → Editar</b>."),
            ("Llegó un expediente que ya habíamos tramitado.", "No lo cargue de nuevo: búsquelo en <b>Mi trabajo → Llegó un expediente</b> y registre el <b>reingreso</b>."),
            ("No encuentro la dependencia o el despacho en la lista.", "Use <b>+</b> (dependencia) o <b>+ Despacho</b>. En las listas también puede escribirlo y presionar Enter."),
            ("Tengo que escribir siempre los nombres.", "No: <b>quién lo lleva, recibe o tramita</b> se elige de una lista con buscador. Un nombre nuevo se escribe una vez y queda para la próxima."),
            ("Cargué un expediente de prueba.", "El oficial que lo cargó puede borrarlo en <b>Ficha → Editar → Eliminar expediente</b> (escribiendo el número para confirmar).")]),
        ("Tramitar y despachar", [
            ("Ya tramité: ¿tengo que registrar el movimiento?", "No. <b>Tramitar y despachar</b> hace las dos cosas; y al generar una nota en Word el expediente queda tramitado y encargado al comisionista."),
            ("En la hoja de ruta dice «TRAMITADO en Dirección».", "Es correcto: el trámite se hace en la Dirección. La salida aparece cuando el comisionista lo entrega (o cuando usted elige <i>Sale ahora</i>)."),
            ("Lo llevé yo, no el comisionista.", "Ficha → Trámite → <b>Despachar el expediente</b> → <i>Sale ahora (lo entrego yo)</i> y cargue quién lo recibió."),
            ("Me equivoqué de destino del encargo.", "En Tramitar → <b>Cambiar</b>, o en Ficha → Trámite → Despachar, elija otro destino."),
            ("Marqué TRAMITADO por error.", "Ficha → Trámite → <b>Anular la marca de tramitado</b>; o en Tramitar, <b>Deshacer</b>."),
            ("Registré un movimiento por error.", "Ficha → Hoja de ruta → <b>Corregir</b>: seleccione y elimine. El sistema recalcula dónde está el expediente."),
            ("La IA tarda o da error.", "Pruebe con menos fotos o más nítidas. Si dice que no está activada, el administrador debe cargar la clave de Gemini (gratuita).")]),
        ("Comisionista", [
            ("No me aparece un expediente para entregar.", "El oficial todavía no lo encargó. Si está tramitado, búsquelo en <b>Buscar otro expediente tramitado</b>."),
            ("¿Es obligatorio cargar quién lo recibe?", "Sí: es la constancia de la entrega y queda en la hoja de ruta.")]),
        ("Alertas", [
            ("Un expediente tramitado aparece con días sin movimiento.", "Ya no: «días sin tramitar» solo se calcula para expedientes <b>en la Dirección y sin tramitar</b>. Recargue la página."),
            ("¿Por qué no me avisa un vencimiento?", "Cargue la <b>fecha de término</b> en los urgentes. Si ya está tramitado, no se marca como vencido.")]),
    ]
    for g, qs in grupos:
        s += [CondPageBreak(40 * mm), Titulo(g, 1)]
        for q, a in qs:
            s += [KeepTogether([Paragraph(f"<b>¿{q}</b>" if q.endswith("?") and "¿" not in q else f"<b>{q}</b>", st["p"]),
                                Paragraph(a, ParagraphStyle("a", parent=st["p"], leftIndent=10, textColor=GRIS))])]
    s += [Spacer(1, 8), caja("Ante cualquier duda o error, tome una captura de pantalla y envíela al administrador del sistema. "
                             "El sistema se sigue optimizando con las sugerencias de quienes lo usan.", "tip")]

    # ── Anexo jerarquías ──
    s += h1("Anexo: Jerarquías")
    s += [p("Escala de la Policía de Tucumán usada en el sistema. Solo <b>oficiales</b>, <b>suboficiales</b> y personal civil pueden ser usuarios; "
            "el resto se registra como personal afectado a actividades."),
          tabla(["Escalafón", "Grados", "¿Usuario?"],
                [["<b>OFICIALES</b>", "Comisario General · Comisario Mayor · Comisario Inspector · Comisario · Subcomisario · Oficial Principal · "
                  "Oficial Auxiliar · Oficial Ayudante · Oficial Subayudante", "Sí"],
                 ["<b>SUBOFICIALES</b>", "Suboficial Mayor · Suboficial Principal · Sargento Ayudante · Sargento Primero · Sargento · Cabo Primero · Cabo · Agente", "Sí"],
                 ["<b>PTP</b>", "Personal Transitorio Policial", "No"],
                 ["<b>CADETES</b>", "Cadete de 1°, 2° y 3° año · Agente / Cabo / Sargento / Sargento Primero Cadete", "No"],
                 ["<b>ASPIRANTES</b>", "Aspirante (Escuela de Suboficiales)", "No"],
                 ["<b>OTROS</b>", "Personal civil · Otro", "Civil: sí"]],
                [35 * mm, ANCHO - 58 * mm, 23 * mm]),
          Spacer(1, 10),
          Paragraph("Manual elaborado por el <b>Oficial Auxiliar Ponce Sergio</b> – I.E.S.P., para la Dirección General de Institutos e Instrucción.",
                    ParagraphStyle("firma", parent=st["p"], alignment=1, textColor=GRIS))]
    return s


if __name__ == "__main__":
    doc = Doc(SALIDA)
    doc.multiBuild(armar())
    print(SALIDA)
