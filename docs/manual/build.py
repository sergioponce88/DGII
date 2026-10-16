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
LOGO2 = "assets/logo_iesp.png"

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
    c.roundRect(W / 2 - 52 * mm, H - 180 * mm, 104 * mm, 11 * mm, 5.5 * mm, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("SB", 11)
    c.drawCentredString(W / 2, H - 176.2 * mm, "Mesa de Entradas · PC y celular")
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
    c.drawCentredString(W / 2, 33 * mm, f"Versión 1.1 · {date.today():%m/%Y}")
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

    # Introducción
    s += h1("Antes de empezar")
    s += [p("Este sistema reemplaza y complementa el <b>libro de registro</b> de la Mesa de Entradas. Permite saber en todo momento "
            "<b>qué expedientes hay, dónde está cada uno, quién lo tiene, si ya fue tramitado</b>, qué vencimientos se aproximan y <b>qué actividades se desarrollan</b> (cursos, formaciones, congresos, disertaciones, eventos). "
            "Funciona en la computadora y en el celular, desde el navegador, sin instalar nada."),
          imagen("00_flujo.png", pie="Figura 1. Recorrido de un expediente y quién realiza cada paso.")]
    s += h2("¿Qué puede hacer cada usuario?")
    s += [tabla(["Rol", "Quiénes", "Puede hacer"],
                [["<b>SUBOFICIAL</b>", "Suboficial Mayor a Agente", "Registrar expedientes, cargar el libro, registrar salidas / ingresos / pases, subir el PDF, consultar todo."],
                 ["<b>OFICIAL</b>", "Comisario General a Oficial Subayudante", "Todo lo anterior + <b>tramitar</b> (marcar TRAMITADO) y <b>corregir</b> datos de expedientes."],
                 ["<b>ADMINISTRADOR</b>", "Responsable del sistema", "Todo + usuarios, dependencias, tipos de expediente, Google Drive y respaldos."]],
                [35 * mm, 46 * mm, ANCHO - 81 * mm]),
          Spacer(1, 6),
          caja("El <b>PTP</b>, los <b>cadetes</b> y los <b>aspirantes</b> no son usuarios del sistema: se registran como <b>personal afectado</b> "
               "a una actividad o expediente. La escala completa está en el anexo <i>Jerarquías</i>.", "tip"),
          Spacer(1, 4),
          caja("Todo lo que usted haga queda registrado con su <b>grado, apellido y nombre</b>, la fecha y la hora. Por eso cada persona "
               "debe ingresar con <b>su propio legajo</b> y nunca compartir la clave.", "ojo")]

    # 1 Ingreso
    s += h1("1. Ingresar al sistema")
    s += [p("Abra en el navegador <b>expedientesdgii.streamlit.app</b>. En el celular puede agregarlo a la pantalla de inicio desde "
            "el menú del navegador (<i>Agregar a pantalla principal</i>) para abrirlo como una aplicación."),
          imagen("01_login.png", pie="Figura 2. Pantalla de ingreso."),
          pasos([(1, "Escriba su <b>número de legajo</b>. Es su nombre de usuario."),
                 (2, "Escriba su <b>clave</b>. El administrador le entrega una clave inicial."),
                 (3, "Toque <b>Ingresar</b>. La primera vez el sistema le pide crear una <b>clave personal</b> de al menos 6 caracteres.")]),
          caja("Para cambiar su clave cuando quiera: menú lateral → <b>Cambiar mi clave</b>. Al terminar la jornada use <b>Salir</b>, "
               "sobre todo en computadoras compartidas.")]

    # 2 Pantalla
    s += h1("2. Conocer la pantalla")
    s += [imagen("02_panel.png", pie="Figura 3. Panel de Control en la computadora."),
          pasos([(1, "<b>Menú</b>: desde aquí se va a cada sección del sistema."),
                 (2, "<b>Su usuario</b>: grado, apellido, legajo, función y rol. Debajo están <b>Actualizar</b>, <b>Cambiar mi clave</b> y <b>Salir</b>."),
                 (3, "<b>Indicadores</b>: expedientes del año, pendientes de trámite, urgentes, vencidos y los que están fuera de la Dirección."),
                 (4, "<b>Alertas prioritarias</b>: vencimientos y actividades que inician hoy. El detalle está en <i>Alertas y Agenda</i>."),
                 (5, "<b>Esta semana en la Dirección</b>: actividades en desarrollo y las que comienzan en los próximos días, con su tipo y lugar.")])]
    tel = Image(os.path.join(IMG, "03_movil.png"), width=58 * mm, height=58 * mm * 1160 / 580)
    txt = [pasos([(1, "Arriba aparece una <b>barra azul</b> con la página actual. Tóquela para elegir otra sección."),
                  (2, "El botón <b>›</b> abre el menú lateral completo (usuario, clave, salir)."),
                  (3, "En <b>Movimiento Rápido</b> elija <b>Trámite</b> o <b>Movimiento</b>: es la pantalla pensada para usar con una sola mano.")],
                 ancho=ANCHO - 66 * mm),
           Spacer(1, 6),
           caja("Los campos de fecha muestran el calendario del teléfono y los de búsqueda permiten escribir parte del número o del asunto.",
                ancho=ANCHO - 66 * mm, suelta=True)]
    t = Table([[tel, txt]], colWidths=[64 * mm, ANCHO - 64 * mm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    s += [KeepTogether([Titulo("En el celular", 1), t])]

    # 3 Numeración
    s += h1("3. Cómo se numera un expediente")
    s += [p("Cada expediente se identifica como en el libro: <b>N° de expediente / Folio / N° de orden</b>."),
          imagen("06_libro_fisico.png", pie="Figura 4. El libro: los datos ocupan las dos páginas y se numera la foja izquierda."),
          tabla(["Dato", "Qué es", "Ejemplo"],
                [["<b>N° de expediente</b>", "Número correlativo que se asigna al expediente.", "545"],
                 ["<b>Folio</b>", "Número de la foja <b>izquierda</b> del libro donde queda asentado.", "120"],
                 ["<b>N° de orden</b>", "Posición del renglón dentro de ese folio. Empieza en 1 en cada folio nuevo.", "3"]],
                [36 * mm, ANCHO - 60 * mm, 24 * mm]),
          Spacer(1, 6),
          caja("El sistema <b>propone solo</b> el próximo número, folio y orden. Si el folio se completa, pasa al siguiente con orden 1. "
               "Si en el libro físico empezó una hoja nueva antes de tiempo, marque <b>Iniciar nuevo folio</b>.", "ok")]

    # 4 Nuevo
    s += h1("4. Registrar un expediente nuevo")
    s += [p("Menú → <b>Nuevo Expediente</b>. Lo pueden hacer suboficiales y oficiales."),
          imagen("04_nuevo_1.png", pie="Figura 5. Parte superior: origen, tipo, de dónde viene, a dónde va y numeración."),
          pasos([(1, "Indique si fue <b>iniciado en la Dirección</b> o <b>recibido de otra dependencia</b>."),
                 (2, "Elija el <b>tipo de expediente</b>. Si genera una actividad (curso, formación, congreso, disertación, taller, beca, evento…), más abajo aparecen sus datos y el personal."),
                 (3, "<b>Dependencia de origen</b>: de dónde viene."),
                 (4, "<b>Instancia a la que va</b>: a qué dependencia se eleva o remite. Sirve después para filtrar y controlar."),
                 (5, "Si una dependencia <b>no está en la lista</b>, toque <b>+</b>, escriba el nombre y <b>Agregar</b>: queda seleccionada."),
                 (6, "Verifique la <b>identificación</b> (ej. 545/120/3). Debe coincidir con lo escrito en el libro."),
                 (7, "Corrija N°, folio u orden si hace falta. Si el número ya existe, el sistema avisa en rojo y no deja guardar.")]),
          imagen("05_nuevo_2.png", pie="Figura 6. Datos del expediente."),
          pasos([(1, "Fecha y hora de ingreso, y con qué <b>sale</b> (Visto Bueno, A consideración del Comando Superior, etc.). Si aún no se sabe, deje “A definir”."),
                 (2, "N° de la nota o expediente de origen e <b>iniciador / causante</b>."),
                 (3, "Asunto, prioridad (<b>Urgente trámite</b> con fecha de término), fojas y dónde está ahora."),
                 (4, "Quién lo trajo y quién lo recibió."),
                 (5, "Toque <b>Registrar expediente</b>. Aparece un aviso verde con la identificación y los botones <b>Avisar por WhatsApp</b> y <b>Abrir ficha</b>.")]),
          caja("Si el expediente es <b>urgente</b>, cargue siempre la <b>fecha de término</b>: así el sistema avisa antes de que venza.", "ojo")]
    s += h2("Expedientes que generan actividades")
    s += [p("Cuando el expediente se refiere a una actividad se completan: <b>tipo de actividad</b>, categoría (<b>realizar / cursar</b>, "
            "<b>dictar / disertar</b>, <b>organizar</b> o <b>asistir / participar</b>), qué se solicita (<b>solo autorización</b>, "
            "<b>autorización + viático + movilidad</b> o <b>sin requerimiento – informativo</b>), nombre, quién la <b>organiza</b>, lugar, "
            "ámbito, fechas, <b>hora</b>, modalidad, responsable y la <b>grilla del personal afectado</b>. La actividad queda vinculada al "
            "expediente y aparece en <i>Actividades y Personal</i> (capítulo 10).")]

    # 5 PDF
    s += h1("5. Subir el expediente en PDF")
    s += [p("Menú → <b>Ficha de Expediente</b> → busque el expediente → pestaña <b>PDF</b>."),
          imagen("09_pdf.png", pie="Figura 7. Digitalización del expediente."),
          pasos([(1, "Si ya tiene PDF, <b>Ver PDF</b> lo abre en Google Drive. Las versiones anteriores quedan guardadas."),
                 (2, "Elija <b>Archivo PDF</b> (escaneado) o <b>Fotos de las fojas</b> (sacadas con el celular)."),
                 (3, "Seleccione los archivos. Varios PDF se unen en uno; las fotos se convierten en un PDF <b>en el orden en que las elige</b>."),
                 (4, "Agregue una descripción si quiere y toque <b>Subir a Google Drive</b>. En la hoja de ruta queda el registro DIGITALIZACIÓN.")]),
          caja("Para fotos: buena luz, hoja completa y derecha, una foja por foto, de la primera a la última.")]

    # 6 Trámite
    s += h1("6. Tramitar un expediente (solo oficiales)")
    s += [p("Marcar un expediente como <b>TRAMITADO</b> deja asentado <b>qué se hizo, quién lo hizo y cuándo</b>. "
            "Se hace desde la <b>Ficha</b> (pestaña Trámite) o desde <b>Movimiento Rápido</b>."),
          imagen("07_tramite.png", pie="Figura 8. Registro del trámite."),
          pasos([(1, "Pestaña <b>Trámite</b>. Si dice <b>PENDIENTE DE TRÁMITE</b>, todavía no fue tramitado."),
                 (2, "Elija <b>qué se hizo</b>: nota elevada, providencia firmada, informe, autorización, notificación, respuesta, pase a división u otro."),
                 (3, "Complete fecha, hora y el <b>detalle</b> (N° de nota, providencia, a quién se respondió)."),
                 (4, "Toque <b>Marcar como TRAMITADO</b>. El expediente cambia de estado y queda en la hoja de ruta.")]),
          caja("¿Se marcó por error? En la misma pestaña: <b>Anular la marca de tramitado</b> e indique el motivo. "
               "Los suboficiales ven el estado pero no pueden marcarlo.", "tip")]

    # 7 Movimiento
    s += h1("7. Registrar una salida, ingreso o pase")
    s += [p("Cada vez que el expediente <b>sale, vuelve o pasa</b> de una oficina a otra se registra un movimiento. "
            "Menú → <b>Movimiento Rápido</b> (o pestaña <i>Registrar movimiento</i> de la ficha)."),
          imagen("08_movimiento.png", pie="Figura 9. Movimiento con aviso por WhatsApp."),
          pasos([(1, "<b>Tipo</b>: SALIDA, INGRESO, PASE INTERNO, DEVOLUCIÓN o ARCHIVO."),
                 (2, "<b>Destino</b>: aparece propuesta la instancia cargada al registrar. Si no está, use <b>+</b>."),
                 (3, "<b>Despacho</b> con el que sale (Visto Bueno, A consideración del Comando Superior…)."),
                 (4, "Fecha, hora, <b>quién lo lleva</b> y <b>quién lo recibe</b>. Marque <b>Urgente trámite</b> si corresponde."),
                 (5, "Después de registrar, <b>Informar por WhatsApp</b> abre el mensaje armado para enviarlo a la dependencia.")]),
          tabla(["Movimiento", "Estado que toma el expediente"],
                [["SALIDA / DEVOLUCIÓN", "REMITIDO"], ["INGRESO", "EN TRÁMITE"], ["PASE INTERNO", "EN DESPACHO"], ["ARCHIVO", "ARCHIVADO"]],
                [60 * mm, ANCHO - 60 * mm], AZUL),
          Spacer(1, 6),
          caja("Un despacho <b>VISTO BUENO</b> sobre un expediente de actividad la marca como <b>AUTORIZADO</b> automáticamente.", "ok")]

    # 8 Libro
    s += h1("8. Consultar el Libro de Registro")
    s += [imagen("10_libro.png", pie="Figura 10. Libro de Registro con filtros y marcado por lote."),
          pasos([(1, "<b>Filtros</b>: texto libre, año, tipo, estado, origen, ubicación, <b>instancia de destino</b>, fechas y <b>trámite</b> (pendientes / tramitados)."),
                 (2, "Toque una fila para ver el detalle y abrir la ficha. Los colores indican la dependencia; la columna <b>PDF</b> abre el archivo."),
                 (3, "<b>Oficiales</b>: seleccione varias filas y márquelas como tramitadas juntas. <b>Exportar Excel</b> descarga lo filtrado.")]),
          caja("Vistas disponibles: <b>Tabla</b> (computadora), <b>Tarjetas</b> (celular) y <b>Por folio</b> (igual que el libro físico).")]

    # 9 Ficha
    s += h1("9. La ficha y la hoja de ruta")
    s += [imagen("11_hoja_ruta.png", pie="Figura 11. Hoja de ruta: todo lo que pasó con el expediente."),
          pasos([(1, "Cada tarjeta es un paso: ingreso, trámite, digitalización, salidas, con fecha, hora y quién lo hizo. El color es el de la dependencia de destino."),
                 (2, "<b>Hoja de ruta (PDF)</b> genera el documento para imprimir o adjuntar.")]),
          tabla(["Pestaña", "Para qué sirve"],
                [["Trámite", "Marcar o ver el trámite."], ["PDF", "Subir o ver el expediente digitalizado."],
                 ["Hoja de ruta", "Historial completo de movimientos."], ["Registrar movimiento", "Salida, ingreso, pase o archivo."],
                 ["Actividad y personal", "Datos de la actividad y efectivos afectados."], ["Alertas", "Recordatorios propios del expediente."],
                 ["Editar", "Corregir datos (oficiales). Eliminar: solo administrador."]],
                [45 * mm, ANCHO - 45 * mm], AZUL)]

    # 10 Actividades
    s += h1("10. Actividades: todo lo que acontece")
    s += [p("Menú → <b>Actividades y Personal</b>. La Dirección no solo lleva expedientes: aquí se controla <b>todo lo que se desarrolla</b> "
            "— cursos, formaciones, capacitaciones, disertaciones, congresos, seminarios, talleres, jornadas, prácticas de tiro, eventos, "
            "actos, colaboraciones de efectivos, intervenciones del gabinete, reuniones y visitas —, <b>tenga o no expediente</b>."),
          imagen("15_actividades.png", pie="Figura 12. Qué está pasando: actividades de hoy y de los próximos días."),
          pasos([(1, "<b>Pestañas</b>: Qué está pasando, Nueva actividad, Estadística, Actividades (listado), Personal y Planificación."),
                 (2, "<b>Indicadores</b>: actividades en desarrollo, próximas, sin autorización y efectivos afectados."),
                 (3, "<b>En desarrollo hoy</b>: cada tarjeta muestra tipo, nombre, lugar, horario y cantidad de personal."),
                 (4, "<b>Próximos 7 días</b>: lo que comienza esta semana, para prever personal y autorizaciones.")]),
          imagen("16_actividad_form.png", pie="Figura 13. Carga de una actividad sin expediente."),
          pasos([(1, "Elija el <b>tipo</b>, la <b>hora</b> y quién la <b>organiza</b>."),
                 (2, "Indique la <b>categoría</b> (realizar, dictar, organizar o asistir) y qué se solicita. Si solo se informa, elija <b>Sin requerimiento (informativo)</b>."),
                 (3, "Cargue el <b>personal afectado</b>: puede incluir oficiales, suboficiales, <b>PTP</b>, <b>cadetes</b> y <b>aspirantes</b>, con su rol (alumno, instructor, disertante, participante, organizador, colaborador…)."),
                 (4, "Toque <b>Guardar actividad</b>. Ya cuenta para las alertas, la estadística y el historial de cada efectivo.")]),
          caja("En la pestaña <b>Personal</b> se busca un efectivo por apellido o DNI y se ve <b>todo lo que realizó</b>: cursos, disertaciones, eventos.", "ok")]

    # 11 Alertas
    s += h1("11. Alertas y agenda")
    s += [imagen("12_alertas.png", pie="Figura 14. Alertas ordenadas por prioridad."),
          pasos([(1, "Resumen por prioridad: <b>críticas</b> (hoy o vencidas), <b>importantes</b>, <b>próximas</b> e <b>informativas</b>."),
                 (2, "Cada alerta indica qué pasa y con qué expediente: actividades que inician (con su tipo: <i>HOY inicia · CURSO…</i>), las que no tienen autorización, términos vencidos, expedientes detenidos y eventos."),
                 (3, "<b>Ficha</b> abre el expediente; <b>Avisar</b> envía el aviso por WhatsApp.")]),
          caja("En <b>Nuevo evento</b> puede agendar reuniones, actos o recordatorios, asociados o no a un expediente.")]

    # 12 Carga masiva
    s += h1("12. Pasar el libro existente al sistema")
    s += [p("Menú → <b>Carga Masiva</b>. Sirve para incorporar los asientos que ya están escritos en el libro."),
          imagen("13_carga.png", pie="Figura 15. Transcripción rápida del libro."),
          pasos([(1, "Elija <b>Desde Excel / CSV</b> (descargue la plantilla) o <b>Transcripción rápida</b> para tipear renglón por renglón."),
                 (2, "En la grilla la numeración viene propuesta: complete fecha, tipo, origen, asunto y destino. Los renglones sin tipo se ignoran."),
                 (3, "Revise la validación: <b>listas para cargar</b>, <b>ya existen</b> y <b>con error</b>."),
                 (4, "Toque <b>Importar</b>. Cada asiento queda con su ingreso en la hoja de ruta.")])]

    # 13 Usuarios
    s += h1("13. Usuarios (administrador)")
    s += [imagen("14_usuarios.png", pie="Figura 16. Alta y control de usuarios."),
          pasos([(1, "Listado de usuarios con grado, apellido, nombre, legajo, función, rol y último acceso. Se puede descargar en Excel."),
                 (2, "<b>Nuevo usuario</b>: el rol se asigna <b>según el grado</b> de la escala de Tucumán (oficial / suboficial). PTP, cadetes y aspirantes no figuran: se cargan como personal de actividades."),
                 (3, "Al crear el usuario se entrega una clave inicial; la persona debe cambiarla en su primer ingreso.")]),
          caja("Cuando alguien deja la oficina, <b>deshabilítelo</b> (no lo borre): su nombre debe seguir figurando en el historial. "
               "Desde la misma pantalla se blanquea la clave de quien la olvidó.", "ojo")]

    # Guía rápida
    s += h1("Guía rápida por rol")
    def col(titulo, color, items):
        filas = [[Paragraph(f"<b>{titulo}</b>", ParagraphStyle("x", parent=st["celb"], fontSize=11, leading=14))]]
        filas += [[Paragraph(f"<font color='#15803D'><b>✓</b></font>  {i}", st["cel"])] for i in items]
        t = Table(filas, colWidths=[(ANCHO - 6 * mm) / 2])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), color), ("BOX", (0, 0), (-1, -1), 0.8, color),
                               ("LINEBELOW", (0, 1), (-1, -2), 0.3, colors.HexColor("#E2E8F0")),
                               ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        return t
    sub = col("SUBOFICIAL – Carga y movimientos", colors.HexColor("#B45309"), [
        "Al llegar un expediente: <b>Nuevo Expediente</b>, verificar N°/folio/orden con el libro.",
        "Cargar de dónde viene y <b>a qué instancia va</b>.",
        "Si es urgente: fecha de término.",
        "Subir el <b>PDF</b> o las fotos de las fojas.",
        "Cuando sale: <b>Movimiento Rápido → SALIDA</b>, quién lo lleva y quién lo recibe.",
        "Avisar por <b>WhatsApp</b> a la dependencia.",
        "Cargar las <b>actividades</b> (con o sin expediente) y su personal.",
        "Revisar <b>Alertas</b> al empezar la jornada."])
    of = col("OFICIAL – Trámite y control", colors.HexColor("#15803D"), [
        "Revisar en el Libro el filtro <b>Pendientes de trámite</b>.",
        "Tramitar: qué se hizo, N° de nota o providencia.",
        "Definir con qué <b>sale</b> (Visto Bueno / A consideración…).",
        "Corregir datos mal cargados desde <b>Editar</b>.",
        "Controlar <b>vencidos</b> y expedientes <b>detenidos</b>.",
        "Emitir <b>Informes</b> de gestión y de cursos.",
        "Verificar actividades <b>sin autorización</b> próximas a iniciar.",
        "Seguir <b>Qué está pasando</b> en Actividades y Personal."])
    t = Table([[sub, of]], colWidths=[(ANCHO) / 2, ANCHO / 2])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    s += [t, Spacer(1, 10)]

    s += [CondPageBreak(90 * mm), Titulo("Preguntas frecuentes", 0), Spacer(1, 2)]
    faq = [("El número propuesto no coincide con el libro.", "Corrija N°, folio u orden antes de registrar. Si ya lo registró, un oficial lo corrige en <b>Ficha → Editar</b>."),
           ("No encuentro la dependencia en la lista.", "Use el botón <b>+</b> junto a la lista y agréguela. El administrador puede asignarle color y WhatsApp."),
           ("No me deja marcar TRAMITADO.", "Esa acción es solo para oficiales. Avise a un oficial o al administrador."),
           ("Registré un movimiento por error.", "Un oficial puede eliminarlo en <b>Ficha → Hoja de ruta → Corregir</b>."),
           ("Olvidé mi clave.", "El administrador se la blanquea en <b>Configuración → Usuarios</b>; al ingresar deberá crear una nueva."),
           ("La página se ve vieja o no carga.", "Toque <b>Actualizar</b> en el menú o recargue el navegador (Ctrl + F5 en la PC).")]
    for q, a in faq:
        s += [KeepTogether([Paragraph(f"<b>{q}</b>", st["p"]), Paragraph(a, ParagraphStyle("a", parent=st["p"], leftIndent=10, textColor=GRIS))])]
    s += [Spacer(1, 8), caja("Ante cualquier duda o error, tome una captura de pantalla y envíela al administrador del sistema.", "tip")]
    # Anexo jerarquías
    s += h1("Anexo: Jerarquías")
    s += [p("Escala de la Policía de Tucumán usada en el sistema. Solo <b>oficiales</b> y <b>suboficiales</b> (y personal civil) pueden ser usuarios; "
            "el resto se registra como personal afectado."),
          tabla(["Escalafón", "Grados", "¿Usuario?"],
                [["<b>OFICIALES</b>", "Comisario General · Comisario Mayor · Comisario Inspector · Comisario · Subcomisario · Oficial Principal · "
                  "Oficial Auxiliar · Oficial Ayudante · Oficial Subayudante", "Sí (rol OFICIAL)"],
                 ["<b>SUBOFICIALES</b>", "Suboficial Mayor · Suboficial Principal · Sargento Ayudante · Sargento Primero · Sargento · Cabo Primero · Cabo · Agente",
                  "Sí (rol SUBOFICIAL)"],
                 ["<b>PTP</b>", "Personal Transitorio Policial", "No"],
                 ["<b>CADETES</b>", "Cadete de 1°, 2° y 3° año (Escuela de Oficiales) · Agente Cadete · Cabo Cadete · Sargento Cadete · "
                  "Sargento Primero Cadete (Abanderado, ascendido ad honorem en el I.E.S.P.)", "No"],
                 ["<b>ASPIRANTES</b>", "Aspirante (Escuela de Suboficiales)", "No"],
                 ["<b>OTROS</b>", "Personal civil · Otro", "Civil: sí"]],
                [35 * mm, ANCHO - 63 * mm, 28 * mm]),
          Spacer(1, 10),
          Paragraph("Manual elaborado por el <b>Oficial Auxiliar Ponce Sergio</b> – I.E.S.P., para la Dirección General de Institutos e Instrucción.",
                    ParagraphStyle("firma", parent=st["p"], alignment=1, textColor=GRIS))]
    return s


if __name__ == "__main__":
    doc = Doc(SALIDA)
    doc.multiBuild(armar())
    print(SALIDA)
