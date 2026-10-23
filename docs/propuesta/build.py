"""Propuesta institucional para iniciar la informatización de divisiones y Unidades Regionales (PDF A4).

Uso (desde la raíz del repo):
    IMG=docs/presentacion/img PIMG=docs/propuesta/img MIMG=<imágenes del manual> \
        PDF=docs/Propuesta_Informatizacion_Policia_Tucuman.pdf python3 docs/presentacion/../propuesta/build.py
"""
import importlib.util
import os
import sys
from datetime import date

sys.path.insert(0, os.getcwd())
_spec = importlib.util.spec_from_file_location("pres", os.path.join(os.path.dirname(__file__), "..", "presentacion", "build.py"))
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)

from reportlab.lib import colors  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, NextPageTemplate, PageBreak,  # noqa: E402
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents  # noqa: E402

from docword import MESES  # noqa: E402

IMG = os.environ.get("IMG", "docs/presentacion/img")
PIMG = os.environ.get("PIMG", "docs/propuesta/img")
MIMG = os.environ.get("MIMG", IMG)
SALIDA = os.environ.get("PDF", "Propuesta_Informatizacion_Policia_Tucuman.pdf")
B = P.B
NAVY, AZUL, TINTA, GRIS, AMARILLO, VERDE = B.NAVY, B.AZUL, B.TINTA, B.GRIS, B.AMARILLO, B.VERDE
W, H, M, ANCHO = B.W, B.H, B.M, B.ANCHO
st = P.st
Titulo, caja, tabla, imagen, lista, kpis, h1, h2, p = P.Titulo, P.caja, P.tabla, P.imagen, P.lista, P.kpis, P.h1, P.h2, P.p
AUTOR = "Crio. Abog. Rodríguez Julio y Of. Aux. Ponce Sergio"
HOY = date.today()
FECHA = f"{MESES[HOY.month - 1].capitalize()} de {HOY.year}"

st["carta"] = ParagraphStyle("carta", parent=st["p"], fontSize=9.8, leading=13.6, firstLineIndent=28, alignment=4, spaceAfter=3)
st["just"] = ParagraphStyle("just", parent=st["p"], alignment=4)


def I(n):
    return os.path.join(IMG, n)


def PI(n):
    return os.path.join(PIMG, n)


def MI(n):
    return os.path.join(MIMG, n)


def pj(t):
    return Paragraph(t, st["just"])


# ───────────────────────── Páginas ─────────────────────────
def portada(c, doc):
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(AMARILLO)
    c.rect(0, H - 8 * mm, W, 8 * mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#1D4ED8"))
    c.rect(0, H * 0.30, W, 4, fill=1, stroke=0)
    try:
        c.drawImage(P.LOGO_POL, W / 2 - 22 * mm, H - 88 * mm, width=44 * mm, height=50 * mm, mask="auto", preserveAspectRatio=True)
    except Exception:
        pass
    c.setFillColor(colors.HexColor("#93C5FD"))
    c.setFont("SB", 11)
    c.drawCentredString(W / 2, H - 100 * mm, "POLICÍA DE TUCUMÁN")
    c.setFillColor(colors.white)
    c.setFont("SB", 13)
    c.drawCentredString(W / 2, H - 116 * mm, "PROPUESTA INSTITUCIONAL")
    c.setFont("SB", 24)
    c.drawCentredString(W / 2, H - 131 * mm, "INFORMATIZACIÓN Y")
    c.drawCentredString(W / 2, H - 142 * mm, "TRANSFORMACIÓN DIGITAL")
    c.setFont("S", 12.5)
    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.drawCentredString(W / 2, H - 154 * mm, "de oficinas, áreas, divisiones y Unidades Regionales")
    c.drawCentredString(W / 2, H - 161 * mm, "de la Policía de Tucumán")
    c.setFillColor(AMARILLO)
    c.roundRect(W / 2 - 58 * mm, H - 182 * mm, 116 * mm, 11 * mm, 5.5 * mm, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("SB", 10.5)
    c.drawCentredString(W / 2, H - 178.3 * mm, "Sin costo de licencias · con personal propio")
    c.setFillColor(colors.white)
    c.setFont("S", 10)
    c.drawCentredString(W / 2, 70 * mm, "Elevada a consideración del Comando Superior por")
    c.setFont("SB", 13)
    c.drawCentredString(W / 2, 62 * mm, "Comisario Abogado RODRÍGUEZ Julio")
    c.drawCentredString(W / 2, 55 * mm, "Oficial Auxiliar PONCE Sergio")
    c.setFont("S", 10)
    c.drawCentredString(W / 2, 48.5 * mm, "Derecho · Gestión administrativa y sumarial · Desarrollo de sistemas")
    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.drawCentredString(W / 2, 32 * mm, f"San Miguel de Tucumán · {FECHA}")
    c.restoreState()


def normal(c, doc):
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, H - 12 * mm, W, 12 * mm, fill=1, stroke=0)
    c.setFillColor(AMARILLO)
    c.rect(0, H - 12.8 * mm, W, 0.8 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("SB", 8.5)
    c.drawString(M, H - 7.6 * mm, "PROPUESTA DE INFORMATIZACIÓN Y TRANSFORMACIÓN DIGITAL")
    c.setFont("S", 8.5)
    c.drawRightString(W - M, H - 7.6 * mm, "POLICÍA DE TUCUMÁN")
    c.setStrokeColor(colors.HexColor("#CBD5E1"))
    c.line(M, 13 * mm, W - M, 13 * mm)
    c.setFillColor(GRIS)
    c.setFont("S", 8)
    c.drawString(M, 8.5 * mm, f"Elaborado por {AUTOR} · {FECHA}")
    c.drawRightString(W - M, 8.5 * mm, f"Página {doc.page}")
    c.restoreState()


class Doc(BaseDocTemplate):
    def __init__(self, ruta):
        super().__init__(ruta, pagesize=B.A4, leftMargin=M, rightMargin=M, topMargin=20 * mm, bottomMargin=18 * mm,
                         title="Propuesta de Informatización y Transformación Digital – Policía de Tucumán", author=AUTOR)
        fr = Frame(M, 18 * mm, ANCHO, H - 38 * mm, id="f")
        self.addPageTemplates([PageTemplate("portada", [Frame(0, 0, W, H)], onPage=portada), PageTemplate("normal", [fr], onPage=normal)])

    def afterFlowable(self, f):
        if isinstance(f, Titulo):
            self.notify("TOCEntry", (f.nivel, f.texto, self.page))


def firma():
    est = ParagraphStyle("f", parent=st["p"], alignment=1, leading=13, fontSize=9.5)
    # El de mayor antigüedad / jerarquía firma a la derecha
    t = Table([[Paragraph("______________________________<br/><b>Oficial Auxiliar PONCE Sergio</b><br/>Auxiliar de Secretaría Académica<br/>"
                          "I.E.S.P. “G.J.F.S.M.”", est),
                Paragraph("______________________________<br/><b>Comisario Abogado RODRÍGUEZ Julio</b><br/>Policía de Tucumán", est)]],
              colWidths=[ANCHO / 2, ANCHO / 2])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return KeepTogether([Spacer(1, 14), t])


# ───────────────────────── Contenido ─────────────────────────
def armar():
    s = [NextPageTemplate("normal"), PageBreak()]

    # Nota de elevación
    s += [Paragraph(f"San Miguel de Tucumán, {HOY.day:02d} de {MESES[HOY.month - 1].capitalize()} de {HOY.year}.-",
                    ParagraphStyle("fr", parent=st["p"], alignment=2)), Spacer(1, 8),
          Paragraph("Al Señor<br/>Jefe de Policía de la Provincia<br/><u>Su Despacho:</u>", st["p"]), Spacer(1, 6),
          Paragraph("<b>Ref.:</b> Propuesta para iniciar la informatización de oficinas, áreas, divisiones y Unidades Regionales "
                    "de la Policía de Tucumán.-", st["p"]), Spacer(1, 6),
          Paragraph("De mi mayor consideración:", st["p"]),
          Paragraph("Tenemos el agrado de dirigirnos a Usted, por la vía jerárquica correspondiente, a fin de elevar a su consideración la presente "
                    "propuesta, cuyo objeto es comenzar a extender a las distintas oficinas, áreas, divisiones y Unidades Regionales de la Institución la experiencia de "
                    "informatización que ya se encuentra en funcionamiento en la Dirección General de Institutos e Instrucción y en el "
                    "Instituto de Enseñanza Superior de Policía “Grl. José Francisco de San Martín”.", st["carta"]),
          Paragraph("La propuesta surge del trabajo conjunto de un <b>abogado</b> y de un <b>oficial con formación en desarrollo de sistemas</b>, "
                    "ambos con experiencia en lo <b>sumarial y lo administrativo</b>: una combinación que permite que las herramientas sean, a la "
                    "vez, prácticas para el personal y jurídicamente sólidas.", st["carta"]),
          Paragraph("Esta iniciativa busca <b>complementar la tarea de excelencia</b> que viene demostrando la Policía de Tucumán, reconocida "
                    "por los medios de comunicación, reflejada en las estadísticas y destacada por el Gobierno de la Provincia y por los "
                    "Ministerios de Seguridad provincial y nacional, aportando herramientas que acompañen ese trabajo y lo potencien.", st["carta"]),
          Paragraph("Los sistemas desarrollados con personal propio demuestran que es posible ordenar la gestión administrativa, contar con "
                    "trazabilidad completa de los expedientes, producir documentación normalizada y obtener estadísticas para la toma de "
                    "decisiones, <b>sin costo de licencias</b> y utilizando el equipamiento existente.", st["carta"]),
          Paragraph("En ese marco, se propone <b>comenzar a trabajar</b> junto a las distintas divisiones y Unidades Regionales: designar "
                    "referentes, relevar sus procesos y necesidades, y avanzar con pruebas piloto graduales, de modo que la Superioridad "
                    "cuente con información concreta para decidir los pasos siguientes.", st["carta"]),
          Paragraph("Si bien se toma como ejemplo el manejo de expedientes, cada oficina tiene su propio circuito de trabajo. Por ello, el "
                    "<b>análisis previo</b> de cada área —mediante entrevistas con su personal y el estudio de su flujo de trabajo— es el paso "
                    "fundamental para determinar qué informatizar y cómo, y para que el sistema que se implemente responda a sus necesidades reales.", st["carta"]),
          Paragraph("La presente no pretende ser una propuesta cerrada: quedamos <b>abiertos a las ideas, observaciones y propuestas</b> que formule "
                    "la Superioridad o que surjan de las distintas áreas, ya que de eso se trata: de evaluar en conjunto qué puede mejorarse y "
                    "de optimizar el trabajo de la Institución.", st["carta"]),
          Paragraph("Quedamos a disposición para ampliar la información, realizar una demostración práctica de los sistemas en funcionamiento y "
                    "colaborar en la etapa que la Superioridad estime pertinente.", st["carta"]),
          Paragraph("Sin otro particular, saludamos a Usted con atenta y distinguida consideración y respeto.-", st["carta"]),
          firma()]

    s += [PageBreak(), Paragraph("Índice", st["h1"]), Spacer(1, 6)]
    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle("t0", fontName="SB", fontSize=10.5, leading=17, textColor=NAVY),
                       ParagraphStyle("t1", fontName="S", fontSize=9, leading=13, leftIndent=14, textColor=TINTA)]
    s += [toc]

    # Resumen ejecutivo
    s += h1("Resumen ejecutivo")
    s += [Paragraph("<b>Qué se propone:</b> informatizar progresivamente la gestión administrativa de oficinas, áreas y divisiones de la Policía "
                    "de Tucumán —divisiones, departamentos y Unidades Regionales— mediante sistemas web propios, <b>comenzando por un relevamiento "
                    "con referentes de cada área</b> y pruebas piloto graduales, para que el trabajo <b>administrativo y operativo</b> quede registrado "
                    "como datos útiles para el análisis y la toma de decisiones.", st["lead"]), Spacer(1, 4),
          kpis([("4", "sistemas propios<br/>en uso o desarrollo"), ("$0", "en licencias<br/>de software"), ("Web", "PC y celular,<br/>sin instalar nada"),
                ("Propio", "personal para desarrollo<br/>y capacitación")]),
          Spacer(1, 8),
          tabla(["Punto", "Síntesis"], [
              ["<b>Problema</b>", "Gestión en papel y planillas dispersas: demoras para ubicar expedientes, notas con formatos distintos, errores repetidos, "
                                  "vencimientos que se pasan y ausencia de estadísticas confiables."],
              ["<b>Solución</b>", "Sistemas web con usuario y clave, roles por jerarquía, registro de cada acción, documentos normalizados en Word/PDF, "
                                  "alertas, informes y ayuda de redacción con inteligencia artificial gratuita."],
              ["<b>Método</b>", "Cada sistema nace del <b>análisis del flujo de trabajo</b> del área, con entrevistas a su personal. El sistema de "
                                "expedientes es un ejemplo: no se impone un modelo único, se diseña a medida de cada lugar."],
              ["<b>Evidencia</b>", "Sistemas ya en funcionamiento en la D.G.I.I. y el I.E.S.P. (expedientes, legajos académicos, gabinete interdisciplinario) "
                                   "y un piloto en desarrollo para Medicina Legal."],
              ["<b>Costo</b>", "Sin licencias. Infraestructura en la nube en planes gratuitos, equipamiento existente y personal propio. Para la escala "
                               "institucional se recomienda alojarlos en servidores de la Policía."],
              ["<b>Capacitación</b>", "Corta y por perfil (de 2 a 6 horas), dictada por personal propio, con manual y material digital."],
              ["<b>Se solicita</b>", "Aval de la Superioridad para comenzar: referentes por división y Unidad Regional, relevamiento de procesos y pruebas piloto."]],
              [30 * mm, ANCHO - 30 * mm])]

    # 1. Fundamentación
    s += h1("1. Fundamentación")
    s += [pj("La Policía de Tucumán genera a diario un volumen muy importante de actuaciones administrativas: expedientes, notas, pases, "
             "oficios judiciales, sumarios, legajos, licencias, inventarios, partes y estadísticas. Buena parte de esa información se registra "
             "todavía en libros de papel, planillas sueltas o archivos de Word que se copian de una vez para la otra."),
          pj("Esta modalidad tiene costos ocultos que no figuran en ningún presupuesto pero que se pagan todos los días: horas de trabajo "
             "dedicadas a buscar un expediente o a reescribir una nota; demoras en responder a la Justicia y al Comando; errores que se "
             "repiten; información que se pierde cuando cambia el personal; y la imposibilidad de saber con datos cuánto se trabaja, en qué "
             "y con qué resultados.")]
    s += h2("Situación observada")
    s += lista(["Registros en <b>libros físicos</b> que solo puede consultar quien está en la oficina.",
                "Notas redactadas a partir de <b>modelos viejos</b>, con membretes distintos, autoridades desactualizadas y errores que se arrastran.",
                "<b>Seguimiento manual</b> de dónde está cada expediente y quién lo tiene.",
                "<b>Vencimientos</b> y plazos judiciales controlados de memoria.",
                "Ausencia de <b>estadísticas</b> para planificar y para informar a la Superioridad.",
                "Dependencia de personas: cuando alguien se traslada, se pierde parte del conocimiento de la oficina."])
    s += h2("Por qué ahora")
    s += [pj("La Policía de Tucumán atraviesa un momento de reconocimiento por su labor: los medios, las estadísticas, el Gobierno de la "
             "Provincia y los Ministerios de Seguridad provincial y nacional destacan su trabajo. La informatización propuesta busca "
             "<b>complementar y sostener esa excelencia</b>, liberando tiempo del personal y ordenando la información que respalda cada resultado."),
          pj("Los procesos de modernización del Estado avanzan hacia la gestión digital, la trazabilidad y la transparencia. Hoy existen "
             "herramientas tecnológicas de uso libre y gratuito que permiten desarrollar sistemas a medida con recursos propios, accesibles "
             "desde el celular, sin necesidad de grandes inversiones. La Institución cuenta además con personal joven formado en informática "
             "y con capacidad de adaptación, lo que hace viable una transformación progresiva y sostenida.")]

    # 2. Antecedentes
    s += h1("2. Antecedentes: lo que ya funciona")
    s += h2("Quiénes impulsan la propuesta")
    s += [tabla(["Integrante", "Aporte"], [
        ["<b>Comisario Abogado RODRÍGUEZ Julio</b>", "Formación jurídica y experiencia en lo sumarial y administrativo: validez legal de las actuaciones, "
                                                     "normativa procesal y reglamentaria, protección de datos y relación con el Ministerio Público Fiscal."],
        ["<b>Oficial Auxiliar PONCE Sergio</b><br/>Auxiliar de Secretaría Académica, I.E.S.P.", "Experiencia en lo sumarial y administrativo como "
                                                     "instructor y en la tramitación de expedientes; análisis de procesos y desarrollo de los sistemas en funcionamiento."]],
        [60 * mm, ANCHO - 60 * mm]),
        Spacer(1, 4),
        caja("La <b>combinación de profesiones</b> es la fortaleza del proyecto: el conocimiento jurídico asegura que cada documento y cada "
             "registro respeten la normativa y tengan validez; el conocimiento técnico y la experiencia en la tarea diaria aseguran que el sistema "
             "sea simple, rápido y realmente útil para el personal. Ambos comparten la experiencia en lo sumarial y lo administrativo, que es "
             "donde más tiempo se pierde hoy y donde más se puede ganar.", "ok")]
    s += h2("Sistemas en funcionamiento")
    s += [pj("La propuesta no parte de cero. Con personal propio y sin costo se desarrollaron los siguientes sistemas, que hoy constituyen "
             "la experiencia piloto de esta iniciativa:"),
          tabla(["Sistema", "Área", "Qué resuelve", "Estado"], [
              ["<b>Registro, Control y Tramitación de Expedientes</b>", "Dirección General de Institutos e Instrucción",
               "Libro de mesa de entradas, seguimiento, reingresos, digitalización en Drive, 26 modelos de notas en Word, actuaciones y sumarios, "
               "oficios judiciales, actividades, alertas e informes.", "En funcionamiento"],
              ["<b>Legajos Académicos</b>", "I.E.S.P.", "Legajo académico de cadetes, notas, promedios, orden de mérito y reportes.", "En funcionamiento"],
              ["<b>Gabinete Interdisciplinario</b>", "I.E.S.P.", "Certificados médicos, prórrogas, altas y seguimiento de cada cadete.", "En funcionamiento"],
              ["<b>Medicina Legal</b>", "División Medicina Legal", "Registro de intervenciones y exámenes e informes técnicos para las Unidades Fiscales.", "En desarrollo (piloto)"]],
              [42 * mm, 34 * mm, ANCHO - 106 * mm, 30 * mm]),
          Spacer(1, 6),
          imagen(I("mB.png"), pie="Figura 1. Sistema de Expedientes D.G.I.I.: tramitación asistida con vista previa de la nota.", alto_max=120 * mm)]

    # 3. Objetivos
    s += h1("3. Objetivos")
    s += h2("Objetivo general")
    s += [pj("Impulsar la informatización progresiva de la gestión administrativa de la Policía de Tucumán, mediante sistemas propios, "
             "seguros y accesibles, comenzando por el trabajo conjunto con cada división y Unidad Regional.")]
    s += h2("Objetivos específicos")
    s += lista([
        "Reemplazar progresivamente libros y planillas por registros digitales con respaldo, sin perder la validez de la documentación en papel.",
        "Asegurar la <b>trazabilidad</b>: quién hizo qué, cuándo y con qué resultado.",
        "Normalizar la documentación con <b>membretes y modelos institucionales</b> únicos.",
        "Reducir tiempos de búsqueda, redacción y respuesta, en especial ante requerimientos judiciales.",
        "Registrar el trabajo <b>administrativo y operativo</b> de forma estructurada, para contar con <b>datos confiables</b> y analizarlos.",
        "Generar <b>estadísticas e indicadores</b> para la planificación y el control de gestión.",
        "Evitar la <b>transcripción repetida</b> de los mismos datos en las distintas piezas de un procedimiento.",
        "Capacitar al personal en el uso de herramientas digitales, con formación breve y práctica.",
        "Conformar una <b>mesa de trabajo</b> con referentes de las divisiones y Unidades Regionales para relevar, priorizar y acompañar la implementación.",
        "Resguardar los datos personales conforme a la normativa vigente."])

    # 4. Ventajas
    s += h1("4. Ventajas para la Institución")
    s += [tabla(["Dimensión", "Ventajas"], [
        ["<b>Operativa</b>", "Ubicación inmediata de cada expediente; menos tiempo de búsqueda y de redacción; consulta desde el celular."],
        ["<b>De gestión</b>", "Indicadores, informes y gráficos al día para la toma de decisiones del Comando."],
        ["<b>Análisis de datos</b>", "La actividad administrativa y operativa queda registrada de manera uniforme y puede analizarse por área, zona, período o tipo."],
        ["<b>De control</b>", "Registro de cada acción con usuario, fecha y hora; alertas de vencimientos; responsables identificados."],
        ["<b>Documental</b>", "Notas, pases, cédulas y actas con formato único, sin errores repetidos y con autoridades actualizadas."],
        ["<b>Económica</b>", "Sin licencias; uso del equipamiento existente; ahorro de papel, impresiones y horas de trabajo."],
        ["<b>Para el personal</b>", "Trabajo más simple y guiado; menos tareas repetitivas; aprendizaje de herramientas útiles."],
        ["<b>Ante la Justicia</b>", "Respuestas en término a oficios, comparendos y requerimientos, con constancia de lo actuado."],
        ["<b>Institucional</b>", "Imagen de una Policía moderna, ordenada y transparente; continuidad aunque cambie el personal."]],
        [32 * mm, ANCHO - 32 * mm], VERDE),
        Spacer(1, 6),
        caja("Los beneficios concretos (tiempos, cantidades, vencimientos evitados) se medirán con los indicadores propuestos en el punto 15, "
             "para que la Superioridad pueda evaluar resultados con datos.", "tip")]

    # 5. Alcance
    s += h1("5. Alcance de la propuesta")
    s += [pj("Se propone una plataforma común —con los mismos criterios de acceso, seguridad, diseño y respaldo— sobre la cual cada área "
             "cuente con el sistema que necesita. La implementación es <b>gradual</b> y comienza por las áreas con mayor volumen administrativo."),
          imagen(PI("mapa.png"), pie="Figura 2. Áreas en funcionamiento, en desarrollo y a relevar, sobre una plataforma común.")]
    s += [PageBreak(), Titulo("Áreas y procesos susceptibles de informatizar", 1),
          pj("La tabla siguiente es <b>orientativa</b>: los procesos concretos de cada área y la forma de informatizarlos surgirán del análisis "
             "y las entrevistas que se realicen en cada una."),
          tabla(["Área", "Procesos a informatizar", "Resultado esperado"], [
              ["Mesas de Entradas", "Libro de registro, pases, reingresos, digitalización, notas normalizadas.", "Ubicación inmediata y trámites en término."],
              ["Dpto. Personal (D-1)", "Legajos, licencias, francos, sanciones, destinos, vencimientos de documentación.", "Información del personal al día y consultable."],
              ["Dpto. Logística (D-4)", "Inventario de bienes, parque automotor, combustible, mantenimiento.", "Control patrimonial y de consumo."],
              ["Dpto. Judicial (D-5)", "Oficios judiciales, comparendos, sumarios, plazos.", "Respuestas en término con constancia."],
              ["Asuntos Internos", "Actuaciones administrativas, sumarios, providencias, notificaciones.", "Instrucción guiada y registro completo."],
              ["Medicina Legal", "Intervenciones, exámenes, informes técnicos a las Unidades Fiscales.", "Informes completos y estadísticas (piloto en desarrollo)."],
              ["Institutos y Escuelas", "Legajos académicos, notas, mesas de examen, actividades.", "Gestión académica ordenada (en funcionamiento en el I.E.S.P.)."],
              ["Gabinete Interdisciplinario", "Certificados, prórrogas, altas, seguimiento.", "Historial completo de cada caso (en funcionamiento)."],
              ["Relaciones Policiales", "Agenda de eventos, solicitudes de personal, ceremonial.", "Planificación y respuesta coordinada."],
              ["Armería y Tiro", "Asignación de armamento, munición, prácticas de tiro.", "Trazabilidad del material y de la instrucción."],
              ["Unidades Regionales y comisarías", "Novedades, oficios y requerimientos, personal y servicios, móviles, control de plazos.", "Información consolidada por zona y en toda la provincia."]],
              [36 * mm, 76 * mm, ANCHO - 112 * mm]),
          Spacer(1, 4),
          caja("La informatización <b>complementa</b> y no reemplaza la documentación exigida por la normativa vigente (libros rubricados, "
               "actas, firmas ológrafas): los sistemas registran, ordenan y producen esa documentación, que se sigue imprimiendo y firmando.", "ojo")]

    # Unidades Regionales
    s += h1("6. Unidades Regionales, jefaturas de zona y comisarías")
    s += [pj("Las <b>Unidades Regionales</b> —Capital, Norte, Sur, Este y Oeste— tienen a su cargo, a través de las jefaturas de zona, a las "
             "comisarías de toda la provincia. Son el lugar donde más información se produce y donde más valor tendría un sistema común: "
             "cada comisaría registra, la jefatura de zona controla, la Unidad Regional consolida y la Superioridad ve el conjunto."),
          imagen(PI("regionales.png"), pie="Figura 3. Un mismo sistema para las cinco Unidades Regionales, sus jefaturas de zona y comisarías."),
          tabla(["Nivel", "Qué podría registrar y consultar"], [
              ["<b>Comisaría</b>", "Mesa de entradas y salidas, oficios y requerimientos judiciales con sus plazos, notas internas con modelos, novedades del servicio, personal y móviles."],
              ["<b>Jefatura de zona</b>", "Estado de las comisarías a su cargo, pendientes y vencimientos, control de respuestas a la Justicia."],
              ["<b>Unidad Regional</b>", "Tablero de su jurisdicción, estadísticas de gestión por comisaría y zona, informes a la Superioridad."],
              ["<b>Jefatura / Subjefatura</b>", "Visión consolidada de las cinco Unidades Regionales para la toma de decisiones."]],
              [38 * mm, ANCHO - 38 * mm]),
          Spacer(1, 4),
          caja("Se sugiere comenzar con <b>una comisaría piloto por Unidad Regional</b> y su jefatura de zona, relevando primero qué libros, "
               "planillas y notas utilizan, para adaptar el sistema a su forma de trabajo.", "tip")]

    # Datos
    s += h1("7. Del registro al análisis de datos: lo administrativo y lo operativo")
    s += [pj("Cada nota, expediente, oficio, servicio, procedimiento o intervención contiene información valiosa. Mientras se registre en papel "
             "o en archivos sueltos, esa información se pierde para el análisis. Si se registra de manera <b>estructurada y uniforme</b>, "
             "se transforma en <b>datos</b> que permiten conocer la realidad de la Institución con precisión."),
          tabla(["Tipo de trabajo", "Qué conviene registrar", "Qué permite analizar"], [
              ["<b>Administrativo</b>", "Expedientes, notas, oficios, plazos, respuestas, personal, licencias, bienes.",
               "Tiempos de trámite, cargas de trabajo, vencimientos, cumplimiento ante la Justicia."],
              ["<b>Operativo</b>", "Servicios, procedimientos, intervenciones, móviles, recursos empleados, resultados, zonas y horarios.",
               "Distribución de recursos, demanda por zona y franja horaria, resultados y necesidades de refuerzo."]],
              [36 * mm, (ANCHO - 36 * mm) / 2, (ANCHO - 36 * mm) / 2]),
          Spacer(1, 6)]
    s += lista(["<b>Calidad del dato</b>: formularios con opciones y validaciones evitan errores, abreviaturas distintas y campos vacíos.",
                "<b>Registro en el momento</b>: se carga cuando ocurre, desde el celular, y no al final de la jornada.",
                "<b>Un solo origen</b>: el mismo dato alimenta los documentos, los partes y las estadísticas, sin volver a copiarlo.",
                "<b>Tableros</b> por oficina, comisaría, zona, Unidad Regional y provincia, para que cada nivel vea lo que necesita."])
    s += [caja("Un buen análisis depende de un buen registro: por eso es fundamental que tanto el trabajo <b>administrativo</b> como el "
               "<b>operativo</b> queden registrados de manera completa y uniforme desde el inicio.", "ok")]

    # 6. Caso testigo
    s += h1("8. Caso testigo: Sistema de Expedientes de la D.G.I.I.")
    s += [caja("El manejo de expedientes se presenta <b>a modo de ejemplo</b>. No se trata de replicar este sistema en todas las áreas, sino de "
               "aplicar el mismo método: <b>analizar el flujo de trabajo de cada lugar</b> y desarrollar la herramienta que esa área necesita.", "ojo"),
          pj("El Sistema de Registro, Control y Tramitación de Expedientes muestra en la práctica lo que se puede lograr con ese método:"),
          *lista(["Libro de mesa de entradas digital con la misma numeración del libro físico (N° / folio / orden).",
                  "Seguimiento de salidas, ingresos, pases y reingresos, con aviso por WhatsApp.",
                  "Tramitación asistida: el oficial elige el modelo, completa un formulario breve y obtiene la nota en Word con membrete institucional "
                  "y firma del Director, lista para imprimir.",
                  "Actuaciones administrativas y sumarios guiados paso a paso; oficios judiciales con sus cédulas y respuestas.",
                  "Ayuda de redacción con inteligencia artificial gratuita, con resguardo de los datos personales.",
                  "Actividades, alertas, informes, usuarios por jerarquía, auditoría y respaldos."]),
          imagen(MI("02_panel.png"), pie="Figura 4. Panel de control con indicadores del año.", alto_max=72 * mm),
          Spacer(1, 4),
          P.galeria([(I("doc_elevacion.png"), "Elevación generada por el sistema"), (I("doc_caratula.png"), "Carátula de sumario"),
                     (I("doc_oj_respuesta.png"), "Respuesta a oficio judicial")], cols=3, alto=58 * mm)]

    # 7. Modelo tecnológico y costos
    s += h1("9. Modelo tecnológico y costos")
    s += [imagen(I("arquitectura.png"), pie="Figura 5. Componentes de los sistemas.", alto_max=85 * mm),
          Spacer(1, 4),
          tabla(["Componente", "Herramienta", "Costo actual"], [
              ["Programación", "Python y Streamlit (software libre)", "Sin costo"],
              ["Código y versiones", "GitHub", "Sin costo"],
              ["Publicación web", "Streamlit Community Cloud", "Sin costo (plan gratuito)"],
              ["Base de datos", "PostgreSQL en Supabase", "Sin costo (plan gratuito)"],
              ["Archivos (PDF)", "Google Drive", "Sin costo (cuenta existente)"],
              ["Corrección de textos", "LanguageTool y diccionario propio", "Sin costo"],
              ["Inteligencia artificial", "Google Gemini", "Sin costo (nivel gratuito, opcional)"],
              ["Equipamiento", "PC y celulares que ya usa el personal", "Sin costo adicional"],
              ["Desarrollo y capacitación", "Personal policial propio", "Dentro de sus funciones"]],
              [40 * mm, 72 * mm, ANCHO - 112 * mm]),
          Spacer(1, 6),
          caja("<b>No genera costos de licencias ni de compra de software.</b> Los planes gratuitos tienen límites de capacidad y de uso, "
               "adecuados para pruebas piloto y oficinas. Para el despliegue a escala institucional se recomienda alojar los sistemas en "
               "<b>servidores propios de la Policía</b> y utilizar cuentas institucionales: como todo el software es libre, el único requerimiento "
               "sería la infraestructura, sin pago de licencias.", "ok")]

    # 8. Seguridad
    s += h1("10. Seguridad y protección de datos")
    s += lista(["<b>Acceso personal</b> con legajo y clave; las claves se guardan cifradas y nadie puede verlas.",
                "<b>Roles y permisos</b> según jerarquía y función: cada usuario ve y hace solo lo que le corresponde.",
                "<b>Auditoría</b> de todas las acciones (usuario, fecha, hora y detalle).",
                "<b>Respaldos</b> descargables que nunca incluyen claves ni credenciales.",
                "Conexiones cifradas (https) desde cualquier dispositivo.",
                "Usuarios que dejan el área se <b>deshabilitan</b>, conservando el historial.",
                "Política de inteligencia artificial: por defecto, los documentos con datos personales <b>no se envían</b> a servicios externos.",
                "Tratamiento de datos personales conforme a la <b>Ley N° 25.326 de Protección de los Datos Personales</b> y a las disposiciones "
                "internas que dicte la Superioridad."])
    s += [caja("Se propone elaborar, para aprobación de la Superioridad, un <b>reglamento interno de uso</b> de los "
               "sistemas: responsables de cada base de datos, alta y baja de usuarios, respaldos periódicos y confidencialidad.", "tip")]

    # 10. Cómo empezar
    s += h1("11. Cómo empezar: trabajo conjunto con las divisiones")
    s += [Paragraph("No se propone por ahora crear estructuras nuevas, sino <b>comenzar a trabajar</b>: conocer cómo funciona cada división "
                    "y cada Unidad Regional, identificar qué conviene informatizar primero y probarlo en pequeño, con resultados medibles.", st["lead"]),
          imagen(PI("ruta.png"), pie="Figura 6. Ruta de trabajo propuesta: el análisis es el paso clave.", alto_max=48 * mm)]
    s += h2("El análisis: punto de partida de todo sistema")
    s += [pj("Ningún sistema se implementa sin antes <b>comprender cómo trabaja el área</b>. El análisis del flujo de trabajo es la etapa "
             "fundamental: evita desarrollar herramientas que no se usan, detecta los verdaderos problemas y asegura que el personal reconozca "
             "en el sistema su propia forma de trabajar. Se realiza en el lugar, con el personal que hace la tarea todos los días."),
          imagen(PI("analisis.png"), pie="Figura 7. Preguntas que guían el análisis del flujo de trabajo de cada área.", alto_max=60 * mm)]
    s += lista(["<b>Entrevistas</b> con el jefe del área y con el personal que realiza cada tarea (carga, redacción, control, firma).",
                "<b>Observación del circuito real</b>: cómo llega cada trámite, qué se hace, quién interviene, a dónde va y en qué plazo.",
                "<b>Recolección de documentos</b>: libros, planillas, modelos de notas, actas y formularios que se usan.",
                "<b>Identificación de problemas</b>: demoras, errores repetidos, información que se pierde, controles que dependen de la memoria.",
                "<b>Propuesta a medida</b>, validada con el área antes de desarrollar, y ajustada durante el piloto según la opinión de los usuarios."])
    s += [caja("Así se construyó el sistema de expedientes de la D.G.I.I.: a partir de los modelos reales que utilizan los oficiales y de la "
               "explicación de cada tramitación por parte de quienes la realizan. Ese mismo método se aplicaría en cada división y Unidad Regional.", "tip")]
    s += h2("Mesa de trabajo de informatización")
    s += [pj("Se sugiere convocar una <b>mesa de trabajo</b> integrada por un referente de cada división y Unidad Regional que se incorpore, "
             "junto con el personal que desarrolló los sistemas existentes. Sus integrantes mantienen sus funciones habituales y se reúnen "
             "periódicamente para:")]
    s += lista(["Relevar los procesos, libros, planillas y modelos de notas de cada área.",
                "Priorizar qué informatizar primero según volumen de trabajo y beneficio esperado.",
                "Acompañar las pruebas piloto y la capacitación en su área.",
                "Recoger las opiniones de los usuarios y proponer mejoras.",
                "Informar periódicamente a la Superioridad los avances y resultados."])
    s += h2("Guía de relevamiento por área")
    s += [pj("Como complemento de las entrevistas, se propone completar para cada área una guía breve con la siguiente información:"),
          tabla(["Qué se releva", "Para qué"], [
              ["Trámites y documentos que se producen (y cuántos por mes)", "Dimensionar el trabajo y priorizar."],
              ["Libros, planillas y registros que se llevan", "Definir qué se digitaliza y con qué formato."],
              ["Modelos de notas, actas y formularios", "Incorporarlos como modelos automáticos."],
              ["Plazos y vencimientos que se controlan", "Configurar alertas."],
              ["Personal y equipamiento disponible (PC, celulares, conectividad)", "Planificar la implementación y la capacitación."],
              ["Principales dificultades actuales", "Orientar el sistema a resolver problemas reales."]],
              [ANCHO / 2, ANCHO / 2])]
    s += h2("Continuidad")
    s += [pj("A medida que aumente la cantidad de áreas y usuarios, la propia experiencia indicará qué organización conviene darle a este "
             "trabajo para asegurar su continuidad, su seguridad y su crecimiento ordenado. Esa evaluación quedará a criterio de la Superioridad, "
             "con la información que surja de los pilotos.")]

    # 10. Capacitación
    s += h1("12. Capacitación del personal")
    s += [pj("Los sistemas están diseñados para que su uso sea intuitivo: funcionan como cualquier aplicación del celular. Aun así, la "
             "capacitación es clave para la adopción. Se propone una formación <b>breve, práctica y por perfil</b>, dictada por personal propio "
             "en el lugar de trabajo."),
          tabla(["Perfil", "Contenidos", "Duración"], [
              ["<b>Usuario de carga</b> (suboficiales, administrativos)", "Ingreso y clave; registro; movimientos; búsqueda; subida de PDF; alertas.", "2 horas"],
              ["<b>Usuario de tramitación</b> (oficiales)", "Lo anterior + tramitación con modelos; revisión de redacción; Word; actuaciones y oficios.", "3 horas"],
              ["<b>Jefes de área</b>", "Panel, indicadores, informes y control de gestión.", "1 hora"],
              ["<b>Administradores</b>", "Usuarios y permisos, autoridades, configuración, respaldos, seguridad.", "4 horas"],
              ["<b>Referentes / multiplicadores</b>", "Uso completo, resolución de consultas frecuentes y cómo capacitar a sus compañeros.", "6 horas"]],
              [52 * mm, ANCHO - 76 * mm, 24 * mm]),
          Spacer(1, 6)]
    s += h2("Modalidad y materiales")
    s += lista(["Encuentros presenciales en la propia oficina, con los datos reales del área (aprender haciendo).",
                "<b>Manual de usuario</b> en PDF con imágenes (ya elaborado para el Sistema de Expedientes).",
                "Guías rápidas de una página y videos cortos para el celular.",
                "Acompañamiento durante las primeras semanas y consultas por mensajería.",
                "Requisito previo: manejo básico de celular o computadora."])
    s += [caja("<b>La capacitación no genera costos:</b> la dicta personal propio dentro de su horario de servicio, con material digital, "
               "sin traslados ni contrataciones externas.", "ok")]

    # 11. Implementación
    s += h1("13. Plan de implementación por etapas")
    s += [tabla(["Etapa", "Acciones", "Plazo orientativo"], [
        ["<b>1. Piloto</b> (en curso)", "Sistemas en funcionamiento en la D.G.I.I. y el I.E.S.P.; piloto de Medicina Legal.", "En marcha"],
        ["<b>2. Evaluación</b>", "Medición de indicadores, encuesta a usuarios, demostración a la Superioridad.", "60 a 90 días"],
        ["<b>3. Mesa de trabajo y análisis</b>", "Referentes por división y Unidad Regional; entrevistas y análisis del flujo de trabajo de cada área; priorización.", "Según disponga la Superioridad"],
        ["<b>4. Pilotos</b>", "Una o dos divisiones priorizadas (por ejemplo D-1, D-5 o Asuntos Internos) y una comisaría piloto por Unidad Regional.", "6 a 12 meses"],
        ["<b>5. Extensión</b>", "Extensión a otras oficinas y comisarías; servidor propio y cuentas institucionales; capacitación permanente.", "Mediano plazo"],
        ["<b>6. Visión a futuro</b>", "Análisis de la tarea del oficial de turno: registro único del procedimiento con imágenes, videos y audios, como complemento de la plataforma de denuncias digitales.", "A evaluar"]],
        [42 * mm, ANCHO - 82 * mm, 40 * mm]),
        Spacer(1, 4),
        caja("Los plazos son orientativos y dependen de las prioridades y recursos que disponga la Superioridad. Cada etapa se evalúa antes de iniciar la siguiente.", "tip")]

    # 12. Riesgos e indicadores
    # Visión a futuro
    s += h1("14. Visión a futuro: la tarea del oficial de turno")
    s += [Paragraph("Como línea de trabajo futura, se propone estudiar la <b>sistematización de la tarea del oficial de turno</b> en las "
                    "comisarías —oficial y auxiliar de turno—, como <b>complemento de la plataforma de denuncias digitales</b> del Ministerio Público Fiscal y no en reemplazo de ella. "
                    "Es, probablemente, donde la informatización más facilitaría el trabajo policial.", st["lead"])]
    s += h2("Situación actual")
    s += [pj("La plataforma de denuncias digitales del Ministerio Público Fiscal de Tucumán responde a las necesidades de la investigación "
             "fiscal: en ella se carga, de forma manual, la información que la Fiscalía requiere. La Policía, en cambio, no cuenta con un "
             "<b>registro propio y estructurado</b> de todo lo actuado en cada procedimiento, que le permita documentar con precisión los "
             "hechos a su cargo, reutilizar esa información y analizarla."),
          pj("Además, en un mismo procedimiento el oficial transcribe una y otra vez los mismos datos —personas, documentos, domicilios, lugar, "
             "fecha y hora, elementos secuestrados, intervinientes, fiscalía— en actas, constancias, notas, partes y en la causa que se eleva a "
             "la Justicia provincial. Cada transcripción insume tiempo y abre la posibilidad de errores u omisiones."),
          imagen(PI("dato_unico.png"), pie="Figura 8. Dato único: la información del procedimiento, incluido el material audiovisual, se registra una vez y se reutiliza.")]
    s += h2("Las notas según el tipo de delito")
    s += [pj("Cada tipo de delito exige un conjunto propio de notas, actas y comunicaciones. Hoy el oficial o auxiliar de turno las confecciona "
             "a partir de <b>archivos de Word</b>: abre un modelo anterior, borra, vuelve a tipear los mismos datos en cada pieza y adapta el "
             "texto. Es una tarea que <b>lleva mucho tiempo</b> y en la que el error puede ocurrir en cualquier momento: un DNI mal copiado, "
             "un nombre distinto entre una nota y otra, una fecha o una carátula que quedó del caso anterior."),
          tabla(["Hoy (archivos de Word)", "Con un sistema de modelos por delito"], [
              ["Se busca el modelo de un caso anterior.", "Se elige el <b>tipo de delito</b> y el sistema propone el conjunto de notas que corresponde."],
              ["Se reescriben los mismos datos en cada nota.", "Los datos se cargan <b>una sola vez</b> y completan todas las piezas."],
              ["Quedan datos del caso anterior por descuido.", "Cada documento se arma desde cero con los datos del procedimiento actual."],
              ["Cada oficial usa su propia versión del modelo.", "Modelos <b>únicos y actualizados</b> para toda la Institución."],
              ["Errores de tipeo y de redacción.", "Validaciones, corrector y redacción asistida."],
              ["No queda registro de lo producido.", "Cada nota queda asociada al procedimiento, con fecha y responsable."]],
              [ANCHO / 2, ANCHO / 2]),
          Spacer(1, 6),
          caja("Es el mismo método que ya funciona en la Dirección General de Institutos e Instrucción, donde el oficial elige el tipo de "
               "tramitación y obtiene la nota lista para imprimir. El conjunto de notas de cada tipo de delito surgiría del <b>análisis con las "
               "comisarías</b> y de los modelos que hoy utilizan, validados por quienes realizan la tarea.", "tip")]
    s += h2("De la información a las actuaciones procesales")
    s += [pj("El valor central de esta línea está en <b>obtener bien la información desde el inicio</b> y convertirla, de manera directa, en las "
             "<b>actuaciones procesales</b> que el oficial firma y eleva al Ministerio Público Fiscal: actas, declaraciones, constancias, notas, "
             "informes y la elevación del sumario. Cuando el dato se registra una vez, correctamente, todas las piezas salen completas, "
             "coherentes entre sí y <b>sin errores</b>."),
          Table([[Paragraph("<b>1. Obtener</b><br/>datos, imágenes, videos y audios en el lugar del hecho", st["cel"]),
                  Paragraph("<b>2. Registrar</b><br/>una sola vez, con validaciones", st["cel"]),
                  Paragraph("<b>3. Generar</b><br/>las actuaciones procesales automáticamente", st["cel"]),
                  Paragraph("<b>4. Firmar y elevar</b><br/>al Ministerio Público Fiscal", st["cel"])]],
                colWidths=[ANCHO / 4] * 4,
                style=TableStyle([("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#DBEAFE")), ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#DCFCE7")),
                                  ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#FEF3C7")), ("BACKGROUND", (3, 0), (3, 0), colors.HexColor("#EDE9FE")),
                                  ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")), ("INNERGRID", (0, 0), (-1, -1), 0.6, colors.white),
                                  ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)])),
          Spacer(1, 6),
          pj("Hoy, confeccionar un <b>sumario procesal completo</b> —sea por un delito grave o de cualquier índole— demanda al oficial muchas horas "
             "de redacción y transcripción. Con la carga única y la generación automática de las piezas, el objetivo es que ese mismo sumario "
             "pueda confeccionarse <b>en la mitad del tiempo o menos</b>, y llegar al Ministerio Público Fiscal completo y sin errores."),
          caja("La reducción de tiempos se <b>medirá en las pruebas piloto</b>, comparando el tiempo actual de confección de un sumario con el "
               "tiempo utilizando el sistema, para presentar a la Superioridad resultados concretos.", "ok")]
    s += h2("Qué se lograría")
    s += lista(["<b>Registro guiado y único</b> de los datos del procedimiento, en el lugar del hecho, desde el celular.",
                "<b>Registro de imágenes, videos y audios</b> del hecho, con fecha, hora y ubicación, asociados al procedimiento, para documentar "
                "con precisión lo ocurrido.",
                "<b>Generación automática</b> de actas, constancias, notas y elevaciones con esos mismos datos, en los formatos vigentes.",
                "<b>Modelos de notas por tipo de delito</b>: al elegir el delito, el sistema propone las piezas que corresponden, sin retipear.",
                "<b>Documentación rápida, efectiva y sin errores</b>: los datos son idénticos en todas las piezas de la causa.",
                "<b>Reducción del tiempo</b> que el oficial dedica a transcribir, que puede destinarse a la tarea policial.",
                "<b>Información propia de la Policía</b>, disponible para la jefatura de zona, la Unidad Regional y la Superioridad, y para el análisis operativo.",
                "<b>Mejor respuesta a lo que exige la Justicia</b>: causas más completas, mejor documentadas y elevadas en menos tiempo."])
    s += h2("Requisitos para el material audiovisual")
    s += lista(["Resguardo de la <b>integridad</b> de cada archivo (registro de fecha, hora, ubicación y huella digital que permita verificar que no fue alterado).",
                "Constancia de <b>quién lo registró</b> y de cada acceso posterior.",
                "Almacenamiento seguro en servidores institucionales y acceso restringido por roles.",
                "Procedimientos acordes a la <b>normativa procesal</b> y a la protección de datos personales."])
    s += [caja("Esta línea requiere un análisis específico del trabajo en comisarías y debe coordinarse con el Ministerio Público Fiscal y "
               "los organismos responsables de la plataforma de denuncias digitales, respetando la normativa procesal vigente y los criterios "
               "de cadena de custodia. Se plantea como <b>visión a futuro</b>, a evaluar a partir de los resultados de las primeras etapas.", "ojo")]

    s += h1("15. Riesgos, mitigaciones e indicadores")
    s += [tabla(["Riesgo", "Mitigación"], [
        ["Dependencia de una sola persona", "Mesa de trabajo y referentes por área, código documentado y guardado en repositorios, manuales."],
        ["Resistencia al cambio", "Capacitación práctica, convivencia inicial con el libro físico y mejoras según la opinión de los usuarios."],
        ["Conectividad", "Funciona con datos móviles y bajo consumo; la documentación impresa sigue siendo válida."],
        ["Seguridad de la información", "Claves cifradas, roles, auditoría, respaldos y reglamento interno de uso."],
        ["Límites de los planes gratuitos", "Plan de migración a servidores institucionales, sin cambiar los sistemas."]],
        [52 * mm, ANCHO - 52 * mm], colors.HexColor("#C2410C"))]
    s += h2("Indicadores de seguimiento")
    s += lista(["Tiempo de confección de un sumario procesal completo (antes y después).",
                "Tiempo promedio para ubicar un expediente.",
                "Tiempo desde el ingreso hasta la tramitación.",
                "Cantidad de expedientes vencidos o fuera de término.",
                "Cantidad de documentos generados con los modelos normalizados.",
                "Usuarios capacitados y activos por área.",
                "Grado de satisfacción de los usuarios (encuesta breve)."])

    # 13. Petitorio
    s += h1("16. Lo que se solicita a la Superioridad")
    s += [pj("Para avanzar con la presente propuesta —que queda abierta a las modificaciones e ideas que la Superioridad estime "
             "convenientes—, se solicita respetuosamente:")]
    s += [P.pasos([(1, "<b>Aval institucional</b> para la continuidad y extensión de los sistemas desarrollados."),
                   (2, "<b>Designación de referentes</b> en las divisiones y en las cinco Unidades Regionales, para conformar una mesa de trabajo."),
                   (3, "<b>Autorización para realizar entrevistas y analizar el flujo de trabajo</b> de esas áreas (procesos, libros y modelos de documentos)."),
                   (4, "<b>Autorización de pruebas piloto</b> en las áreas que se prioricen (incluida una comisaría por Unidad Regional) y de los espacios de capacitación."),
                   (5, "Uso de <b>cuentas institucionales</b> y, a mediano plazo, de un <b>servidor propio</b> para alojar los sistemas."),
                   (6, "Una <b>demostración práctica</b> ante la Superioridad de los sistemas en funcionamiento."),
                   (7, "Tener presente, como <b>línea futura</b>, el análisis de la tarea del oficial de turno en coordinación con los organismos responsables.")])]
    s += h2("Conclusión")
    s += [pj("La informatización de la gestión administrativa no es un objetivo a futuro: ya está ocurriendo en la Institución, con resultados "
             "concretos, personal propio y sin costo de licencias, y viene a complementar la tarea de excelencia que la Policía de Tucumán "
             "demuestra y que es destacada públicamente. Comenzar a trabajar junto a las divisiones y las Unidades Regionales, "
             "<b>analizando en cada caso su flujo de trabajo</b>, "
             "permitirá multiplicar esos resultados en todas las oficinas y comisarías, registrar el trabajo administrativo y operativo como datos "
             "útiles para decidir y, a futuro, facilitar la tarea del oficial de turno —con registro de datos, imágenes, videos y audios del "
             "procedimiento— para cumplir con mayor agilidad lo que exige la Justicia, con orden, seguridad y continuidad, en "
             "beneficio de la Policía de Tucumán y de la comunidad a la que sirve."),
          caja("Esta propuesta está <b>abierta a las ideas y propuestas de la Superioridad</b> y de cada área. Su espíritu es evaluar en conjunto "
               "qué puede mejorarse y optimizar el trabajo de la Institución: los sistemas y este documento <b>se irán ajustando</b> con cada "
               "aporte que se reciba.", "ok"),
          firma()]
    return s


if __name__ == "__main__":
    doc = Doc(SALIDA)
    doc.multiBuild(armar())
    print(SALIDA)
