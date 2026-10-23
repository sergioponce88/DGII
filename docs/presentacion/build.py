"""Presentación institucional del Sistema de Expedientes D.G.I.I. (PDF A4).

Uso (desde la raíz del repo):
    IMG=<carpeta de imágenes> MIMG=<imágenes del manual> PDF=docs/Presentacion_Sistema_Expedientes_DGII.pdf \
        python3 docs/presentacion/build.py
"""
import importlib.util
import os
import sys
from datetime import date

sys.path.insert(0, os.getcwd())
_spec = importlib.util.spec_from_file_location("manual", os.path.join(os.path.dirname(__file__), "..", "manual", "build.py"))
B = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B)

from reportlab.lib import colors  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Frame, Image, KeepTogether, NextPageTemplate,  # noqa: E402
                                PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents  # noqa: E402

import modelos as MOD  # noqa: E402
from docword import MESES  # noqa: E402

IMG = os.environ.get("IMG", "img")
MIMG = os.environ.get("MIMG", IMG)
SALIDA = os.environ.get("PDF", "Presentacion_Sistema_Expedientes_DGII.pdf")
LOGO_POL = "assets/logo_policia.png"
LOGO_DGII = "assets/logo_dgii.png"
NAVY, AZUL, TINTA, GRIS, AMARILLO, VERDE = B.NAVY, B.AZUL, B.TINTA, B.GRIS, B.AMARILLO, B.VERDE
W, H, M, ANCHO = B.W, B.H, B.M, B.ANCHO
st = B.st
Titulo, caja, tabla, pasos = B.Titulo, B.caja, B.tabla, B.pasos
AUTOR = "Oficial Auxiliar Ponce Sergio – I.E.S.P."
VERSION = "2.0"

st["lead"] = ParagraphStyle("lead", parent=st["p"], fontSize=11.5, leading=17, textColor=NAVY)
st["kn"] = ParagraphStyle("kn", fontName="SB", fontSize=22, leading=24, textColor=AZUL, alignment=1)
st["kl"] = ParagraphStyle("kl", fontName="S", fontSize=8.5, leading=11, textColor=GRIS, alignment=1)
st["li"] = ParagraphStyle("li", parent=st["p"], leftIndent=12, bulletIndent=2, spaceAfter=3)


def p(t):
    return Paragraph(t, st["p"])


def lista(items):
    return [Paragraph(t, st["li"], bulletText="•") for t in items]


def h1(t):
    return [PageBreak(), Titulo(t, 0), Spacer(1, 2)]


def h2(t):
    return [CondPageBreak(35 * mm), Titulo(t, 1)]


def imagen(ruta, ancho=ANCHO, pie=None, alto_max=None):
    from PIL import Image as PI

    w, h = PI.open(ruta).size
    alto = ancho * h / w
    if alto_max and alto > alto_max:
        ancho, alto = alto_max * w / h, alto_max
    im = Image(ruta, width=ancho, height=alto)
    marco = Table([[im]], colWidths=[ancho])
    marco.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    out = [marco]
    if pie:
        out += [Spacer(1, 3), Paragraph(pie, st["pc"])]
    return KeepTogether(out)


def I(nombre):
    return os.path.join(IMG, nombre)


def MI(nombre):
    return os.path.join(MIMG, nombre)


def kpis(items):
    celdas = [[Paragraph(n, st["kn"]), Paragraph(l, st["kl"])] for n, l in items]
    t = Table([[Table([[a], [b]], colWidths=[ANCHO / len(items) - 4 * mm]) for a, b in celdas]], colWidths=[ANCHO / len(items)] * len(items))
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")), ("INNERGRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")),
                           ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")), ("TOPPADDING", (0, 0), (-1, -1), 8),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 8), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return t


def galeria(rutas_pies, cols=2, alto=None):
    ancho = (ANCHO - (cols - 1) * 5 * mm) / cols
    filas, fila = [], []
    from PIL import Image as PI

    for ruta, pie in rutas_pies:
        w, h = PI.open(ruta).size
        al = ancho * h / w
        if alto and al > alto:
            al = alto
        cel = [Image(ruta, width=al * w / h, height=al), Spacer(1, 2), Paragraph(pie, st["pc"])]
        fila.append(cel)
        if len(fila) == cols:
            filas.append(fila)
            fila = []
    if fila:
        filas.append(fila + [""] * (cols - len(fila)))
    t = Table(filas, colWidths=[ancho + 5 * mm] * cols)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    return KeepTogether([t])


# ───────────────────────── Plantillas de página ─────────────────────────
def portada(c, doc):
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#1D4ED8"))
    c.rect(0, H * 0.33, W, 4, fill=1, stroke=0)
    c.setFillColor(AMARILLO)
    c.rect(0, H - 8 * mm, W, 8 * mm, fill=1, stroke=0)
    for x, logo in ((W / 2 - 46 * mm, LOGO_POL), (W / 2 + 8 * mm, LOGO_DGII)):
        try:
            c.drawImage(logo, x, H - 85 * mm, width=38 * mm, height=44 * mm, mask="auto", preserveAspectRatio=True)
        except Exception:
            pass
    c.setFillColor(colors.HexColor("#93C5FD"))
    c.setFont("SB", 11)
    c.drawCentredString(W / 2, H - 100 * mm, "POLICÍA DE TUCUMÁN")
    c.setFont("S", 10.5)
    c.drawCentredString(W / 2, H - 106 * mm, "DIRECCIÓN GENERAL DE INSTITUTOS E INSTRUCCIÓN")
    c.setFillColor(colors.white)
    c.setFont("SB", 25)
    c.drawCentredString(W / 2, H - 130 * mm, "SISTEMA DE REGISTRO, CONTROL")
    c.drawCentredString(W / 2, H - 141 * mm, "Y TRAMITACIÓN DE EXPEDIENTES")
    c.setFont("S", 13)
    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.drawCentredString(W / 2, H - 153 * mm, "Presentación institucional del alcance del sistema")
    c.setFillColor(AMARILLO)
    c.roundRect(W / 2 - 62 * mm, H - 175 * mm, 124 * mm, 11 * mm, 5.5 * mm, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("SB", 10.5)
    c.drawCentredString(W / 2, H - 171.3 * mm, "Mesa de Entradas · Tramitación · Actividades · IA")
    c.setFillColor(colors.white)
    c.setFont("S", 10)
    c.drawCentredString(W / 2, 64 * mm, "Elaborado por")
    c.setFont("SB", 13)
    c.drawCentredString(W / 2, 57 * mm, "Oficial Auxiliar PONCE Sergio")
    c.setFont("S", 10)
    c.drawCentredString(W / 2, 51.5 * mm, "I.E.S.P. – Policía de Tucumán")
    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.drawCentredString(W / 2, 36 * mm, "expedientesdgii.streamlit.app")
    c.drawCentredString(W / 2, 30 * mm, f"Versión {VERSION} · {date.today():%m/%Y} · Documento en mejora continua")
    c.restoreState()


def normal(c, doc):
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, H - 12 * mm, W, 12 * mm, fill=1, stroke=0)
    c.setFillColor(AMARILLO)
    c.rect(0, H - 12.8 * mm, W, 0.8 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("SB", 8.5)
    c.drawString(M, H - 7.6 * mm, "SISTEMA DE EXPEDIENTES · PRESENTACIÓN INSTITUCIONAL")
    c.setFont("S", 8.5)
    c.drawRightString(W - M, H - 7.6 * mm, "D.G.I.I. · POLICÍA DE TUCUMÁN")
    c.setStrokeColor(colors.HexColor("#CBD5E1"))
    c.line(M, 13 * mm, W - M, 13 * mm)
    c.setFillColor(GRIS)
    c.setFont("S", 8)
    c.drawString(M, 8.5 * mm, f"Elaborado por {AUTOR} · Versión {VERSION} · el sistema se optimiza en forma continua")
    c.drawRightString(W - M, 8.5 * mm, f"Página {doc.page}")
    c.restoreState()


class Doc(BaseDocTemplate):
    def __init__(self, ruta):
        super().__init__(ruta, pagesize=B.A4, leftMargin=M, rightMargin=M, topMargin=20 * mm, bottomMargin=18 * mm,
                         title="Sistema de Expedientes D.G.I.I. – Presentación institucional", author=AUTOR)
        fr = Frame(M, 18 * mm, ANCHO, H - 38 * mm, id="f")
        self.addPageTemplates([PageTemplate("portada", [Frame(0, 0, W, H)], onPage=portada), PageTemplate("normal", [fr], onPage=normal)])

    def afterFlowable(self, f):
        if isinstance(f, Titulo):
            self.notify("TOCEntry", (f.nivel, f.texto, self.page))


# ───────────────────────── Contenido ─────────────────────────
def armar():
    s = [NextPageTemplate("normal"), PageBreak()]
    s += [Paragraph("Índice", st["h1"]), Spacer(1, 6)]
    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle("t0", fontName="SB", fontSize=10.5, leading=17, textColor=NAVY),
                       ParagraphStyle("t1", fontName="S", fontSize=9, leading=13, leftIndent=14, textColor=TINTA)]
    s += [toc]

    n_mod = len(MOD.MODELOS)
    n_oj = sum(1 for m in MOD.MODELOS.values() if m.grupo == "Oficios judiciales")
    n_act = sum(1 for m in MOD.MODELOS.values() if m.grupo == "Actuaciones / Sumario")

    # 1. Presentación
    s += h1("1. Presentación")
    s += [Paragraph("El <b>Sistema de Registro, Control y Tramitación de Expedientes</b> es una herramienta digital desarrollada para la "
                    "<b>Dirección General de Institutos e Instrucción</b> de la Policía de Tucumán. Reúne en un solo lugar el libro de la "
                    "Mesa de Entradas, el seguimiento de cada expediente, su digitalización, la <b>redacción asistida de las notas y "
                    "tramitaciones</b> y el control de todas las actividades que se desarrollan en la Dirección.", st["lead"]),
          Spacer(1, 4),
          kpis([("100 %", "web: PC y celular<br/>sin instalar nada"), (str(n_mod), "modelos de notas<br/>y tramitaciones"),
                ("3", "niveles de ayuda<br/>de redacción (IA)"), ("24/7", "consulta del estado<br/>de cada expediente")]),
          Spacer(1, 8),
          p("Hasta ahora, el registro se llevaba en un libro de papel y las notas se redactaban copiando modelos anteriores en Word. "
            "Eso generaba demoras para saber dónde estaba un expediente, errores repetidos de redacción, membretes distintos, nombres de "
            "autoridades desactualizados y ninguna estadística de lo trabajado. El sistema ordena ese circuito sin cambiar la forma de "
            "trabajo: respeta la numeración del libro (N° de expediente / folio / orden) y los textos institucionales de siempre, pero "
            "los completa, los corrige y los deja registrados."),
          imagen(MI("00_flujo.png"), pie="Figura 1. Recorrido de un expediente dentro del sistema."),
          caja("El sistema está en funcionamiento y <b>se irá optimizando en forma continua</b>, incorporando las mejoras que surjan del "
               "uso diario por parte del personal de la Dirección.", "ok")]

    # 2. Objetivos
    s += h1("2. Objetivos")
    s += h2("Objetivo general")
    s += [p("Modernizar la gestión administrativa de la Dirección General de Institutos e Instrucción mediante un sistema único, "
            "seguro y accesible desde cualquier dispositivo, que permita registrar, seguir, tramitar y documentar los expedientes y "
            "las actividades institucionales con trazabilidad completa.")]
    s += h2("Objetivos específicos")
    s += lista([
        "Reemplazar y complementar el libro de registro, manteniendo su numeración y su lógica de folios.",
        "Saber en todo momento <b>dónde está cada expediente, quién lo tiene, desde cuándo y si fue tramitado</b>.",
        "Unificar el formato de las notas con un <b>membrete institucional</b> y textos normalizados.",
        "Reducir el tiempo de redacción con <b>modelos que se completan solos</b> con los datos del expediente.",
        "Disminuir los errores de ortografía y redacción con <b>herramientas gratuitas de inteligencia artificial</b>.",
        "Guiar la instrucción de <b>actuaciones administrativas y sumarios</b> paso a paso.",
        "Responder en término los <b>oficios judiciales</b>.",
        "Controlar <b>cursos, formaciones, congresos, disertaciones y eventos</b>, con o sin expediente, y el personal afectado.",
        "Anticipar vencimientos mediante <b>alertas</b> y avisos por WhatsApp.",
        "Contar con <b>estadísticas e informes</b> para la toma de decisiones del Comando.",
        "Resguardar la información con usuarios, permisos, auditoría y respaldos."])

    # 3. Alcance
    s += h1("3. Alcance general del sistema")
    s += [p("El sistema se organiza en módulos. Cada usuario ve solamente los que corresponden a su rol.")]
    s += [tabla(["Módulo", "Qué permite"], [
        ["<b>Panel de Control</b>", "Indicadores del año, pendientes de trámite, urgentes, vencidos, expedientes fuera de la Dirección y actividades de la semana."],
        ["<b>Nuevo Expediente</b>", "Registro con numeración del libro (N° / folio / orden), origen, destino, tipo, urgencia y datos de la actividad."],
        ["<b>Movimiento Rápido</b>", "Salidas, ingresos, pases, devoluciones, archivo y <b>reingreso</b> de expedientes ya tramitados, con aviso por WhatsApp."],
        ["<b>Tramitar</b>", f"{n_mod} modelos de notas, pases, notificaciones, proyectos, oficios judiciales y piezas de instrucción en Word, con IA."],
        ["<b>Libro de Registro</b>", "Consulta con filtros, vista de tabla, tarjetas o por folio, marcado múltiple y exportación a Excel."],
        ["<b>Ficha de Expediente</b>", "Hoja de ruta completa, trámite, PDF, movimientos, actividad, alertas y corrección de datos."],
        ["<b>Actividades y Personal</b>", "Cursos, formaciones, disertaciones, congresos, eventos y personal afectado (incluye PTP, cadetes y aspirantes)."],
        ["<b>Alertas y Agenda</b>", "Vencimientos, actividades que inician, expedientes detenidos y eventos, por prioridad."],
        ["<b>Carga Masiva</b>", "Incorporación del libro existente desde Excel o por transcripción rápida."],
        ["<b>Informes</b>", "Estadísticas de gestión y de actividades, gráficos y exportación."],
        ["<b>Configuración</b>", "Usuarios, autoridades y firmante, dependencias, tipos de expediente, Google Drive, IA y respaldos."],
    ], [42 * mm, ANCHO - 42 * mm])]

    # 4. Arquitectura y seguridad
    s += h1("4. Funcionamiento, acceso y seguridad")
    s += [imagen(I("arquitectura.png"), pie="Figura 2. Componentes del sistema."), Spacer(1, 4)]
    s += lista([
        "<b>Acceso web</b> desde la computadora o el celular, con dirección propia, sin instalar programas.",
        "<b>Base de datos</b> en la nube (PostgreSQL) con creación automática de la estructura y migraciones seguras.",
        "<b>Google Drive</b> institucional para guardar el PDF de cada expediente, ordenado por año, con versiones.",
        "<b>Ingreso por legajo y clave personal</b>; las claves se guardan cifradas (PBKDF2) y nadie puede verlas.",
        "<b>Roles y permisos</b>: lo que cada usuario puede hacer depende de su jerarquía y función.",
        "<b>Auditoría</b>: cada acción queda registrada con grado, apellido, nombre, fecha y hora.",
        "<b>Respaldo completo</b> descargable en Excel, que nunca incluye claves ni credenciales.",
        "<b>Privacidad en la IA</b>: por defecto, los documentos con datos personales no se envían a servicios externos."])
    s += [caja("Cada persona debe ingresar con <b>su propio legajo</b>. Los usuarios que dejan la oficina se deshabilitan (no se borran) para "
               "que su nombre siga figurando en el historial.", "ojo")]

    # 5. Usuarios y roles
    s += h1("5. Usuarios, roles y jerarquías")
    s += [tabla(["Rol", "Quiénes", "Puede hacer"], [
        ["<b>SUBOFICIAL</b>", "Suboficial Mayor a Agente", "Registrar expedientes, cargar el libro, movimientos, reingresos, subir PDF, cargar actividades y consultar."],
        ["<b>OFICIAL</b>", "Comisario General a Oficial Subayudante", "Todo lo anterior + <b>tramitar</b> con los modelos, marcar TRAMITADO y corregir datos."],
        ["<b>ADMINISTRADOR</b>", "Responsable del sistema", "Todo + usuarios, autoridades y firmante, dependencias, tipos, Drive, IA y respaldos."]],
        [37 * mm, 44 * mm, ANCHO - 81 * mm]),
        Spacer(1, 6),
        p("Las jerarquías corresponden a la escala de la Policía de Tucumán. El <b>Personal Transitorio Policial (PTP)</b>, los "
          "<b>cadetes</b> (de 1°, 2° y 3° año, Agente, Cabo, Sargento y Sargento Primero Cadete Abanderado) y los <b>aspirantes</b> de la "
          "Escuela de Suboficiales no son usuarios: se registran como <b>personal afectado</b> a actividades y expedientes."),
        imagen(MI("14_usuarios.png"), pie="Figura 3. Administración de usuarios.", alto_max=95 * mm)]

    # 6. Registro
    s += h1("6. Registro de expedientes")
    s += [p("El registro respeta el libro físico: el sistema propone automáticamente el próximo <b>N° de expediente, folio (foja izquierda) "
            "y orden</b>, avisa si la numeración choca con otra ya registrada y permite iniciar un folio nuevo."),
          imagen(MI("04_nuevo_1.png"), pie="Figura 4. Alta: origen, tipo, de dónde viene, a dónde va y numeración.", alto_max=110 * mm)]
    s += lista(["Expedientes <b>iniciados</b> en la Dirección o <b>recibidos</b> de otras dependencias, con colores por dependencia.",
                "Nuevas dependencias de origen o destino se agregan con el botón <b>+</b> sin salir de la pantalla.",
                "<b>Urgente trámite</b> con fecha de término y alerta de vencimiento.",
                "Si el expediente genera una <b>actividad</b> (curso, congreso, evento…), se cargan sus datos y el personal en el mismo paso.",
                "Al guardar, se ofrece el aviso por <b>WhatsApp</b> a la dependencia."])

    # 7. Seguimiento
    s += h1("7. Seguimiento: movimientos, reingresos y hoja de ruta")
    s += [p("Cada salida, ingreso, pase, devolución o archivo se registra con fecha, hora, <b>quién lo lleva y quién lo recibe</b> y el "
            "despacho con el que sale (Visto Bueno, A consideración del Comando Superior, etc.). El estado del expediente se actualiza solo."),
          imagen(MI("08_movimiento.png"), pie="Figura 5. Movimiento Rápido, pensado para el celular.", alto_max=95 * mm),
          Spacer(1, 4),
          caja("<b>Reingreso:</b> cuando vuelve a la Dirección un expediente ya tramitado, se busca por su número y se actualiza "
               "<b>el mismo expediente</b>: queda nuevamente pendiente de trámite, el trámite anterior se conserva en la hoja de ruta "
               "y se lleva la cuenta de reingresos.", "tip"),
          imagen(MI("11_hoja_ruta.png"), pie="Figura 6. Hoja de ruta: todo lo que pasó con el expediente, exportable a PDF.", alto_max=80 * mm)]

    # 8. Libro, ficha y digitalización
    s += h1("8. Libro de registro, ficha y digitalización")
    s += [imagen(MI("10_libro.png"), pie="Figura 7. Libro de Registro con filtros, colores por dependencia y marcado por lote.", alto_max=85 * mm)]
    s += lista(["Filtros por texto, año, tipo, estado, origen, ubicación, instancia de destino, fechas y trámite.",
                "Vistas: <b>tabla</b> (PC), <b>tarjetas</b> (celular) y <b>por folio</b> (igual que el libro físico).",
                "<b>Exportación a Excel</b> de lo filtrado."])
    s += [Spacer(1, 4), imagen(MI("09_pdf.png"), pie="Figura 8. Digitalización: PDF escaneado o fotos de las fojas, guardados en Google Drive.", alto_max=80 * mm)]

    # 9. Tramitación asistida
    s += h1("9. Tramitación asistida (módulo Tramitar)")
    s += [Paragraph("Es el módulo central para los oficiales. Convierte la tramitación en <b>cinco pasos claros</b>: elegir el expediente, "
                    "elegir qué se va a hacer, completar un formulario breve viendo la nota en vivo, revisar la redacción y generar el Word, "
                    "y finalmente asentar el trámite.", st["lead"]),
          imagen(I("mA.png"), pie="Figura 9. Paso 1 y 2: el sistema sugiere los modelos que corresponden al tipo de expediente."),
          ]
    s += [PageBreak(), imagen(I("mB.png"), pie="Figura 10. Paso 3 y 4: formulario agrupado y vista previa en vivo con el membrete.", alto_max=165 * mm)]
    s += h2("Qué resuelve")
    s += lista([
        "La <b>referencia</b> (Expte. N° / Sec. D.G.I.I. / Asunto / Iniciado por) y el <b>cómputo de fojas</b> salen del expediente.",
        "El <b>destinatario</b> sale de una libreta de autoridades actualizable; el verbo se adapta: <i>elevo</i> a superiores, <i>remito</i> a pares, <i>pase</i> a dependencias internas.",
        "Las <b>elevaciones</b> van a Jefatura o Subjefatura de Policía según lo que disponga la gestión, configurable en un solo lugar.",
        "Todas las notas de la Dirección salen con la <b>firma del Director General</b> (Crio. Grl. Claudio Néstor Dadín).",
        "La opinión de la Dirección (<b>favorable, desfavorable, no reúne las condiciones, a consideración</b>) arma su párrafo y actualiza el despacho del expediente.",
        "Al terminar se descarga el <b>Word en hoja oficio</b>, queda en el historial del expediente y con un toque se marca <b>TRAMITADO</b> y se registra la salida."])
    s += h2("Catálogo de modelos")
    filas = []
    for g in MOD.GRUPOS:
        ms = [m for m in MOD.MODELOS.values() if m.grupo == g]
        for i, m in enumerate(ms):
            filas.append([f"<b>{g}</b>" if i == 0 else "", f"<b>{m.nombre}</b>", m.descripcion])
    s += [tabla(["Grupo", "Modelo", "Para qué"], filas, [32 * mm, 52 * mm, ANCHO - 84 * mm])]

    s += h2("Membrete y documentos")
    s += [p("Todos los documentos comparten un <b>membrete unificado</b> con el escudo de la Policía de Tucumán y el de la Dirección "
            "General de Institutos e Instrucción, pie institucional y tipografía uniforme. Las fechas, horas y legajos se escriben en "
            "letras automáticamente («a los VEINTIDÓS días del mes de OCTUBRE del año DOS MIL VEINTISÉIS…»)."),
          galeria([(I("doc_elevacion.png"), "Elevación con opinión favorable"), (I("doc_relaciones.png"), "Solicitud de formación → Relaciones"),
                   (I("doc_notificacion.png"), "Cédula de notificación"), (I("doc_caratula.png"), "Carátula de sumario")], cols=4, alto=70 * mm)]

    # 10. Actuaciones y sumarios
    s += h1("10. Actuaciones administrativas y sumarios")
    s += [p("Para la instrucción, los datos de la actuación se cargan <b>una sola vez</b>: clase, número, causa, causante y legajo, víctima, "
            "fecha del hecho, quién interviene, instructor y secretario de actuaciones. Con eso se completan todas las piezas."),
          imagen(I("mC.png"), pie="Figura 11. Hoja de pasos de la instrucción con el siguiente paso destacado.", alto_max=78 * mm)]
    s += [tabla(["Origen", "Pasos que guía el sistema"], [
        ["<b>Iniciada por la Dirección</b>", "Carátula · Acta cabeza · Providencia (hoja chica) · Valoración objetiva · Designación de instructor y "
                                             "secretario · Declaración de testigo · Cédula de notificación · Inspección de visu · Defensa · Análisis · Conclusiones definitivas"],
        ["<b>Recibida de otra dependencia</b>", "Notificación · Declaración del causante y/o testigo · Análisis · Elevación"],
        ["<b>Información sumaria / Sumario</b>", "Se puede recaratular y dictar providencias; el resto sigue el mismo circuito de las actuaciones."]],
        [45 * mm, ANCHO - 45 * mm]),
        Spacer(1, 4),
        galeria([(I("doc_valoracion.png"), "Valoración objetiva (Visto · Considerando · Resuelve)"),
                 (I("doc_providencia.png"), "Providencia en media hoja oficio")], cols=2, alto=62 * mm)]

    # 11. Oficios judiciales
    s += h1("11. Oficios judiciales")
    s += [p(f"Nuevo tipo de expediente con {n_oj} modelos para responder en término a fiscalías y juzgados. Los datos del oficio "
            "(organismo, N°, fecha, autos caratulados y legajo) se cargan una vez y se repiten en todas las piezas."),
          tabla(["Situación", "Qué genera el sistema"], [
              ["Solicitud de informe", "Pase interno al área que debe informar, con plazo, y luego la <b>respuesta al oficio</b> con el informe."],
              ["Notificación de comparendo", "<b>Cédula</b> con día, hora, lugar, calidad (testigo, imputado…) y apercibimiento del Art. 176 del C.P.P."],
              ["Rueda de reconocimiento", "Pedido a Compañía o a la Escuela del personal con las características requeridas y nómina para la Justicia."],
              ["Notificaciones varias", "Cédula para cualquier otra disposición judicial."]], [45 * mm, ANCHO - 45 * mm]),
          Spacer(1, 6),
          galeria([(I("doc_oj_respuesta.png"), "Respuesta al oficio judicial"), (I("doc_oj_rueda.png"), "Rueda de reconocimiento")], cols=2, alto=100 * mm)]

    # 12. IA
    s += h1("12. Inteligencia artificial para la redacción")
    s += [p("El sistema incorpora <b>tres niveles de ayuda gratuitos</b>, que el oficial usa con un botón y siempre revisa antes de aceptar:"),
          tabla(["Nivel", "Qué hace", "Datos"], [
              ["<b>Diccionario propio D.G.I.I.</b>", "Corrige los errores frecuentes detectados en los modelos de la Dirección (por ejemplo «de la Provincia de la Provincia», «INTERO», «Ase mismo», «cito en»).", "No salen del sistema"],
              ["<b>LanguageTool</b>", "Ortografía y gramática en español, con sugerencias que se aceptan una por una.", "Servicio gratuito"],
              ["<b>Google Gemini</b>", "Mejora la redacción y <b>lee las fotos de las fojas</b> para proponer el fundamento, el motivo y demás textos.", "Opcional; bloqueado en documentos con datos personales"]],
              [40 * mm, ANCHO - 80 * mm, 40 * mm]),
          Spacer(1, 6),
          imagen(I("mD.png"), pie="Figura 12. Completar con fotos del expediente: la IA lee las fojas y propone el texto.", alto_max=95 * mm),
          caja("La IA <b>propone</b>; el oficial <b>decide</b>. Tiene instrucciones de no inventar nombres, fechas ni números: si un dato no se lee, "
               "deja una línea en blanco para completar. En el plan gratuito de Google, lo enviado puede usarse para mejorar sus productos; por eso, "
               "por defecto, no se usa con sumarios, oficios judiciales, notificaciones ni sanciones.", "ojo")]

    # 13. Actividades
    s += h1("13. Actividades y personal")
    s += [p("La Dirección no solo gestiona expedientes: el sistema registra <b>todo lo que acontece</b> —cursos, formaciones, capacitaciones, "
            "disertaciones, congresos, seminarios, talleres, jornadas, diplomaturas, becas, prácticas de tiro, eventos deportivos, actos, "
            "colaboraciones de efectivos, intervenciones del gabinete, reuniones y visitas—, con o sin expediente."),
          imagen(MI("15_actividades.png"), pie="Figura 13. Qué está pasando: actividades en desarrollo y próximas.", alto_max=95 * mm)]
    s += lista(["Categoría (realizar, dictar, organizar o asistir), requerimiento (autorización, viático, movilidad o informativo), organizador, lugar, fechas y hora.",
                "Grilla del <b>personal afectado</b> con jerarquía, DNI, división y rol; incluye PTP, cadetes y aspirantes.",
                "<b>Historial por efectivo</b>: qué cursos, disertaciones o eventos realizó.",
                "Planificación anual y estadísticas por tipo, categoría y ámbito."])

    # 14. Alertas, informes, carga
    s += h1("14. Alertas, informes y carga del libro existente")
    s += [imagen(MI("12_alertas.png"), pie="Figura 14. Alertas ordenadas por prioridad.", alto_max=90 * mm)]
    s += lista(["<b>Alertas</b>: términos vencidos o por vencer, actividades que inician (y si no tienen autorización), expedientes detenidos y eventos de agenda.",
                "<b>Informes</b>: gestión por período, tipos, dependencias, tiempos de trámite y actividades, con gráficos accesibles y exportación.",
                "<b>Carga masiva</b>: el libro existente se incorpora desde Excel o por transcripción rápida con validación de duplicados."])
    s += [imagen(MI("02_panel.png"), pie="Figura 15. Panel de Control con indicadores y la semana de la Dirección.", alto_max=85 * mm)]

    # 15. Beneficios
    s += h1("15. Beneficios para la Dirección")
    s += [tabla(["Antes", "Con el sistema"], [
        ["Libro de papel; para saber dónde estaba un expediente había que preguntar.", "Ubicación, responsable y estado en tiempo real, desde la PC o el celular."],
        ["Notas copiadas de modelos viejos, con membretes distintos y autoridades desactualizadas.", "Modelos normalizados, membrete unificado y libreta de autoridades actualizable."],
        ["Errores de redacción repetidos.", "Diccionario propio, corrector ortográfico e IA opcional."],
        ["Cómputo de fojas y referencias escritas a mano.", "Referencia, fojas, fechas y legajos en letras completados automáticamente."],
        ["Sumarios sin guía de pasos.", "Hoja de pasos de la instrucción con el siguiente paso destacado."],
        ["Vencimientos que se pasaban.", "Alertas por prioridad y aviso por WhatsApp."],
        ["Sin estadísticas.", "Informes y gráficos para el Comando Superior."],
        ["Expedientes que volvían y se registraban de nuevo.", "Reingreso sobre el mismo número, con historial completo."]],
        [ANCHO / 2, ANCHO / 2], VERDE)]

    # 16. Mejora continua
    s += h1("16. Mejora continua: próximas etapas")
    s += [Paragraph("El sistema <b>se irá optimizando</b> de manera permanente a partir del uso diario y de las sugerencias del personal. "
                    "Las siguientes líneas de trabajo se encuentran <b>proyectadas</b> y se incorporarán en forma gradual:", st["lead"])]
    s += lista([
        "Ajuste fino de los textos de cada modelo junto a los oficiales que tramitan.",
        "Numeración y registro de las <b>notas salientes</b>, con su propio libro.",
        "Edición de plantillas por el administrador, sin necesidad de programar.",
        "Guardado automático del Word generado en la carpeta de Drive del expediente.",
        "Estadísticas de tramitación: tiempos por tipo de expediente y por oficial.",
        "Avisos automáticos de vencimiento por correo o mensajería.",
        "Ampliación del diccionario institucional con los errores que se detecten.",
        "Actualización del Manual de Usuario y capacitación del personal en cada nueva versión."])
    s += [Spacer(1, 6),
          caja("Cada mejora se publica sin interrumpir el servicio y sin pérdida de datos. Las sugerencias pueden enviarse al administrador "
               "del sistema con una captura de pantalla de lo que se desea mejorar.", "tip")]

    # Cierre
    s += [Spacer(1, 16), Table([[Paragraph(
        "<b>Sistema de Registro, Control y Tramitación de Expedientes</b><br/>Dirección General de Institutos e Instrucción · Policía de Tucumán<br/><br/>"
        f"Elaborado por el <b>Oficial Auxiliar Ponce Sergio</b> – Instituto de Enseñanza Superior de Policía “Grl. José Francisco de San Martín”.<br/>"
        f"Versión {VERSION} · {MESES[date.today().month - 1].lower()} de {date.today().year}", ParagraphStyle("cierre", parent=st["p"], alignment=1, textColor=NAVY))]],
        colWidths=[ANCHO], style=TableStyle([("BOX", (0, 0), (-1, -1), 1, NAVY), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF2F8")),
                                             ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 12)]))]
    return s


if __name__ == "__main__":
    doc = Doc(SALIDA)
    doc.multiBuild(armar())
    print(SALIDA)
