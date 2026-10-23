"""Propuesta institucional de informatización y creación de un Área de Sistemas (PDF A4).

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
AUTOR = "Oficial Auxiliar Ponce Sergio – I.E.S.P."
HOY = date.today()
FECHA = f"{MESES[HOY.month - 1].capitalize()} de {HOY.year}"

st["carta"] = ParagraphStyle("carta", parent=st["p"], fontSize=10.5, leading=16, firstLineIndent=28, alignment=4)
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
    for x, logo in ((W / 2 - 46 * mm, P.LOGO_POL), (W / 2 + 8 * mm, P.LOGO_DGII)):
        try:
            c.drawImage(logo, x, H - 85 * mm, width=38 * mm, height=44 * mm, mask="auto", preserveAspectRatio=True)
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
    c.drawCentredString(W / 2, H - 154 * mm, "de oficinas, áreas y divisiones de la Policía de Tucumán")
    c.drawCentredString(W / 2, H - 161 * mm, "y creación de un Área de Sistemas y Transformación Digital")
    c.setFillColor(AMARILLO)
    c.roundRect(W / 2 - 58 * mm, H - 182 * mm, 116 * mm, 11 * mm, 5.5 * mm, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("SB", 10.5)
    c.drawCentredString(W / 2, H - 178.3 * mm, "Sin costo de licencias · con personal propio")
    c.setFillColor(colors.white)
    c.setFont("S", 10)
    c.drawCentredString(W / 2, 64 * mm, "Elevada a consideración del Comando Superior por")
    c.setFont("SB", 13)
    c.drawCentredString(W / 2, 57 * mm, "Oficial Auxiliar PONCE Sergio")
    c.setFont("S", 10)
    c.drawCentredString(W / 2, 51.5 * mm, "Instituto de Enseñanza Superior de Policía “Grl. José Francisco de San Martín”")
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
    return KeepTogether([Spacer(1, 24), Table([[Paragraph(
        "______________________________<br/><b>Oficial Auxiliar PONCE Sergio</b><br/>Auxiliar de Secretaría Académica<br/>"
        "Instituto de Enseñanza Superior de Policía “G.J.F.S.M.”", ParagraphStyle("f", parent=st["p"], alignment=1, leading=14))]],
        colWidths=[80 * mm], hAlign="RIGHT")])


# ───────────────────────── Contenido ─────────────────────────
def armar():
    s = [NextPageTemplate("normal"), PageBreak()]

    # Nota de elevación
    s += [Paragraph(f"San Miguel de Tucumán, {HOY.day:02d} de {MESES[HOY.month - 1].capitalize()} de {HOY.year}.-",
                    ParagraphStyle("fr", parent=st["p"], alignment=2)), Spacer(1, 8),
          Paragraph("Al Señor<br/>Jefe de Policía de la Provincia<br/><u>Su Despacho:</u>", st["p"]), Spacer(1, 6),
          Paragraph("<b>Ref.:</b> Propuesta de informatización de oficinas, áreas y divisiones de la Policía de Tucumán y creación de un "
                    "Área de Sistemas y Transformación Digital.-", st["p"]), Spacer(1, 6),
          Paragraph("De mi mayor consideración:", st["p"]),
          Paragraph("Tengo el agrado de dirigirme a Usted, por la vía jerárquica correspondiente, a fin de elevar a su consideración la presente "
                    "propuesta, cuyo objeto es extender a las distintas oficinas, áreas y divisiones de la Institución la experiencia de "
                    "informatización que ya se encuentra en funcionamiento en la Dirección General de Institutos e Instrucción y en el "
                    "Instituto de Enseñanza Superior de Policía “Grl. José Francisco de San Martín”.", st["carta"]),
          Paragraph("Los sistemas desarrollados con personal propio demuestran que es posible ordenar la gestión administrativa, contar con "
                    "trazabilidad completa de los expedientes, producir documentación normalizada y obtener estadísticas para la toma de "
                    "decisiones, <b>sin costo de licencias</b> y utilizando el equipamiento existente.", st["carta"]),
          Paragraph("En ese marco, se propone asimismo la <b>creación de un área específica</b> dedicada al desarrollo, la capacitación y el "
                    "soporte de estos sistemas, que asegure su continuidad institucional, su seguridad y su crecimiento ordenado.", st["carta"]),
          Paragraph("Quedo a disposición para ampliar la información, realizar una demostración práctica de los sistemas en funcionamiento y "
                    "colaborar en la etapa que la Superioridad estime pertinente.", st["carta"]),
          Paragraph("Sin otro particular, saludo a Usted con atenta y distinguida consideración y respeto.-", st["carta"]),
          firma()]

    s += [PageBreak(), Paragraph("Índice", st["h1"]), Spacer(1, 6)]
    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle("t0", fontName="SB", fontSize=10.5, leading=17, textColor=NAVY),
                       ParagraphStyle("t1", fontName="S", fontSize=9, leading=13, leftIndent=14, textColor=TINTA)]
    s += [toc]

    # Resumen ejecutivo
    s += h1("Resumen ejecutivo")
    s += [Paragraph("<b>Qué se propone:</b> informatizar progresivamente la gestión administrativa de oficinas, áreas y divisiones de la Policía "
                    "de Tucumán mediante sistemas web propios, y crear un <b>Área de Sistemas y Transformación Digital</b> que los desarrolle, "
                    "capacite al personal y les dé soporte.", st["lead"]), Spacer(1, 4),
          kpis([("4", "sistemas propios<br/>en uso o desarrollo"), ("$0", "en licencias<br/>de software"), ("Web", "PC y celular,<br/>sin instalar nada"),
                ("Propio", "personal para desarrollo<br/>y capacitación")]),
          Spacer(1, 8),
          tabla(["Punto", "Síntesis"], [
              ["<b>Problema</b>", "Gestión en papel y planillas dispersas: demoras para ubicar expedientes, notas con formatos distintos, errores repetidos, "
                                  "vencimientos que se pasan y ausencia de estadísticas confiables."],
              ["<b>Solución</b>", "Sistemas web con usuario y clave, roles por jerarquía, registro de cada acción, documentos normalizados en Word/PDF, "
                                  "alertas, informes y ayuda de redacción con inteligencia artificial gratuita."],
              ["<b>Evidencia</b>", "Sistemas ya en funcionamiento en la D.G.I.I. y el I.E.S.P. (expedientes, legajos académicos, gabinete interdisciplinario) "
                                   "y un piloto en desarrollo para Medicina Legal."],
              ["<b>Costo</b>", "Sin licencias. Infraestructura en la nube en planes gratuitos, equipamiento existente y personal propio. Para la escala "
                               "institucional se recomienda alojarlos en servidores de la Policía."],
              ["<b>Capacitación</b>", "Corta y por perfil (de 2 a 6 horas), dictada por personal propio, con manual y material digital."],
              ["<b>Se solicita</b>", "Aval de la Superioridad, creación o designación del Área de Sistemas, referentes por área y autorización de pruebas piloto."]],
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
    s += [pj("Los procesos de modernización del Estado avanzan hacia la gestión digital, la trazabilidad y la transparencia. Hoy existen "
             "herramientas tecnológicas de uso libre y gratuito que permiten desarrollar sistemas a medida con recursos propios, accesibles "
             "desde el celular, sin necesidad de grandes inversiones. La Institución cuenta además con personal joven formado en informática "
             "y con capacidad de adaptación, lo que hace viable una transformación progresiva y sostenida.")]

    # 2. Antecedentes
    s += h1("2. Antecedentes: lo que ya funciona")
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
             "seguros y accesibles, y dotar a la Institución de un área específica que garantice su desarrollo, capacitación, soporte y continuidad.")]
    s += h2("Objetivos específicos")
    s += lista([
        "Reemplazar progresivamente libros y planillas por registros digitales con respaldo, sin perder la validez de la documentación en papel.",
        "Asegurar la <b>trazabilidad</b>: quién hizo qué, cuándo y con qué resultado.",
        "Normalizar la documentación con <b>membretes y modelos institucionales</b> únicos.",
        "Reducir tiempos de búsqueda, redacción y respuesta, en especial ante requerimientos judiciales.",
        "Generar <b>estadísticas e indicadores</b> para la planificación y el control de gestión.",
        "Capacitar al personal en el uso de herramientas digitales, con formación breve y práctica.",
        "Crear el <b>Área de Sistemas y Transformación Digital</b> como responsable técnico y metodológico.",
        "Resguardar los datos personales conforme a la normativa vigente."])

    # 4. Ventajas
    s += h1("4. Ventajas para la Institución")
    s += [tabla(["Dimensión", "Ventajas"], [
        ["<b>Operativa</b>", "Ubicación inmediata de cada expediente; menos tiempo de búsqueda y de redacción; consulta desde el celular."],
        ["<b>De gestión</b>", "Indicadores, informes y gráficos al día para la toma de decisiones del Comando."],
        ["<b>De control</b>", "Registro de cada acción con usuario, fecha y hora; alertas de vencimientos; responsables identificados."],
        ["<b>Documental</b>", "Notas, pases, cédulas y actas con formato único, sin errores repetidos y con autoridades actualizadas."],
        ["<b>Económica</b>", "Sin licencias; uso del equipamiento existente; ahorro de papel, impresiones y horas de trabajo."],
        ["<b>Para el personal</b>", "Trabajo más simple y guiado; menos tareas repetitivas; aprendizaje de herramientas útiles."],
        ["<b>Ante la Justicia</b>", "Respuestas en término a oficios, comparendos y requerimientos, con constancia de lo actuado."],
        ["<b>Institucional</b>", "Imagen de una Policía moderna, ordenada y transparente; continuidad aunque cambie el personal."]],
        [32 * mm, ANCHO - 32 * mm], VERDE),
        Spacer(1, 6),
        caja("Los beneficios concretos (tiempos, cantidades, vencimientos evitados) se medirán con los indicadores propuestos en el punto 12, "
             "para que la Superioridad pueda evaluar resultados con datos.", "tip")]

    # 5. Alcance
    s += h1("5. Alcance de la propuesta")
    s += [pj("Se propone una plataforma común —con los mismos criterios de acceso, seguridad, diseño y respaldo— sobre la cual cada área "
             "cuente con el sistema que necesita. La implementación es <b>gradual</b> y comienza por las áreas con mayor volumen administrativo."),
          imagen(PI("mapa.png"), pie="Figura 2. Áreas en funcionamiento, en desarrollo y propuestas, alrededor del Área de Sistemas.")]
    s += [PageBreak(), Titulo("Áreas y procesos susceptibles de informatizar", 1),
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
              ["Comisarías", "Novedades internas, oficios y requerimientos administrativos.", "Comunicación ordenada con la Superioridad."]],
              [36 * mm, 76 * mm, ANCHO - 112 * mm]),
          Spacer(1, 4),
          caja("La informatización <b>complementa</b> y no reemplaza la documentación exigida por la normativa vigente (libros rubricados, "
               "actas, firmas ológrafas): los sistemas registran, ordenan y producen esa documentación, que se sigue imprimiendo y firmando.", "ojo")]

    # 6. Caso testigo
    s += h1("6. Caso testigo: Sistema de Expedientes de la D.G.I.I.")
    s += [pj("El Sistema de Registro, Control y Tramitación de Expedientes muestra en la práctica lo que se propone extender:"),
          *lista(["Libro de mesa de entradas digital con la misma numeración del libro físico (N° / folio / orden).",
                  "Seguimiento de salidas, ingresos, pases y reingresos, con aviso por WhatsApp.",
                  "Tramitación asistida: el oficial elige el modelo, completa un formulario breve y obtiene la nota en Word con membrete institucional "
                  "y firma del Director, lista para imprimir.",
                  "Actuaciones administrativas y sumarios guiados paso a paso; oficios judiciales con sus cédulas y respuestas.",
                  "Ayuda de redacción con inteligencia artificial gratuita, con resguardo de los datos personales.",
                  "Actividades, alertas, informes, usuarios por jerarquía, auditoría y respaldos."]),
          imagen(MI("02_panel.png"), pie="Figura 3. Panel de control con indicadores del año.", alto_max=72 * mm),
          Spacer(1, 4),
          P.galeria([(I("doc_elevacion.png"), "Elevación generada por el sistema"), (I("doc_caratula.png"), "Carátula de sumario"),
                     (I("doc_oj_respuesta.png"), "Respuesta a oficio judicial")], cols=3, alto=58 * mm)]

    # 7. Modelo tecnológico y costos
    s += h1("7. Modelo tecnológico y costos")
    s += [imagen(I("arquitectura.png"), pie="Figura 4. Componentes de los sistemas.", alto_max=85 * mm),
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
    s += h1("8. Seguridad y protección de datos")
    s += lista(["<b>Acceso personal</b> con legajo y clave; las claves se guardan cifradas y nadie puede verlas.",
                "<b>Roles y permisos</b> según jerarquía y función: cada usuario ve y hace solo lo que le corresponde.",
                "<b>Auditoría</b> de todas las acciones (usuario, fecha, hora y detalle).",
                "<b>Respaldos</b> descargables que nunca incluyen claves ni credenciales.",
                "Conexiones cifradas (https) desde cualquier dispositivo.",
                "Usuarios que dejan el área se <b>deshabilitan</b>, conservando el historial.",
                "Política de inteligencia artificial: por defecto, los documentos con datos personales <b>no se envían</b> a servicios externos.",
                "Tratamiento de datos personales conforme a la <b>Ley N° 25.326 de Protección de los Datos Personales</b> y a las disposiciones "
                "internas que dicte la Superioridad."])
    s += [caja("Se propone que el Área de Sistemas elabore, para aprobación de la Superioridad, un <b>reglamento interno de uso</b> de los "
               "sistemas: responsables de cada base de datos, alta y baja de usuarios, respaldos periódicos y confidencialidad.", "tip")]

    # 9. Área de Sistemas
    s += h1("9. Creación del Área de Sistemas y Transformación Digital")
    s += [Paragraph("La experiencia demuestra que los sistemas funcionan y que el personal los adopta. Para que esta transformación "
                    "<b>no dependa de esfuerzos individuales</b> y pueda crecer de manera ordenada, segura y sostenida en el tiempo, se propone "
                    "crear un área específica dedicada a ella.", st["lead"])]
    s += h2("Misión")
    s += [pj("Diseñar, desarrollar, implementar y mantener los sistemas de gestión de la Policía de Tucumán; capacitar y asistir al personal "
             "en su uso; y resguardar la información institucional, promoviendo la modernización administrativa de todas las áreas.")]
    s += h2("Funciones")
    s += lista(["Relevar los procesos de cada área y proponer su informatización.",
                "Desarrollar, mantener y mejorar los sistemas con criterios comunes de diseño y seguridad.",
                "Elaborar los modelos de documentos institucionales y mantener actualizadas las autoridades y normativas.",
                "Capacitar al personal por perfil y formar referentes (multiplicadores) en cada área.",
                "Brindar soporte y mesa de ayuda a los usuarios.",
                "Administrar usuarios, permisos, respaldos y la protección de los datos.",
                "Producir estadísticas e informes de gestión para el Comando Superior.",
                "Coordinar con las áreas técnicas existentes (comunicaciones, informática) y con otros organismos del Estado."])
    s += [imagen(PI("organigrama.png"), pie="Figura 5. Estructura sugerida (a adecuar por la Superioridad).", alto_max=72 * mm)]
    s += h2("Conformación inicial sugerida")
    s += [tabla(["Aspecto", "Propuesta"], [
        ["Dependencia orgánica", "A definir por la Superioridad (Jefatura, Subjefatura o la órbita de la D.G.I.I. por su perfil formativo)."],
        ["Dotación inicial", "Un núcleo reducido de personal policial con conocimientos de informática, por <b>reasignación de funciones</b>, sin creación de cargos."],
        ["Perfil", "Oficiales y suboficiales con formación o experiencia en sistemas, programación, redes o gestión administrativa."],
        ["Referentes", "Un referente por área usuaria, que mantiene sus funciones y actúa como enlace."],
        ["Equipamiento", "El existente; a futuro, un servidor institucional para alojar los sistemas."],
        ["Costo", "Sin costo adicional en la etapa inicial."]], [40 * mm, ANCHO - 40 * mm])]

    # 10. Capacitación
    s += h1("10. Capacitación del personal")
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
    s += h1("11. Plan de implementación por etapas")
    s += [tabla(["Etapa", "Acciones", "Plazo orientativo"], [
        ["<b>1. Piloto</b> (en curso)", "Sistemas en funcionamiento en la D.G.I.I. y el I.E.S.P.; piloto de Medicina Legal.", "En marcha"],
        ["<b>2. Evaluación</b>", "Medición de indicadores, encuesta a usuarios, demostración a la Superioridad.", "60 a 90 días"],
        ["<b>3. Creación del Área</b>", "Designación del personal, reglamento interno de uso, referentes por área.", "Según disponga la Superioridad"],
        ["<b>4. Extensión</b>", "Informatización de 2 o 3 áreas priorizadas por la Superioridad (por ejemplo D-1, D-5, Asuntos Internos).", "6 a 12 meses"],
        ["<b>5. Institucionalización</b>", "Servidor propio, cuentas institucionales, integración de sistemas, capacitación permanente.", "Mediano plazo"]],
        [42 * mm, ANCHO - 82 * mm, 40 * mm]),
        Spacer(1, 4),
        caja("Los plazos son orientativos y dependen de las prioridades y recursos que disponga la Superioridad. Cada etapa se evalúa antes de iniciar la siguiente.", "tip")]

    # 12. Riesgos e indicadores
    s += h1("12. Riesgos, mitigaciones e indicadores")
    s += [tabla(["Riesgo", "Mitigación"], [
        ["Dependencia de una sola persona", "Creación del Área, código documentado y guardado en repositorios, manuales y referentes por área."],
        ["Resistencia al cambio", "Capacitación práctica, convivencia inicial con el libro físico y mejoras según la opinión de los usuarios."],
        ["Conectividad", "Funciona con datos móviles y bajo consumo; la documentación impresa sigue siendo válida."],
        ["Seguridad de la información", "Claves cifradas, roles, auditoría, respaldos y reglamento interno de uso."],
        ["Límites de los planes gratuitos", "Plan de migración a servidores institucionales, sin cambiar los sistemas."]],
        [52 * mm, ANCHO - 52 * mm], colors.HexColor("#C2410C"))]
    s += h2("Indicadores de seguimiento")
    s += lista(["Tiempo promedio para ubicar un expediente.",
                "Tiempo desde el ingreso hasta la tramitación.",
                "Cantidad de expedientes vencidos o fuera de término.",
                "Cantidad de documentos generados con los modelos normalizados.",
                "Usuarios capacitados y activos por área.",
                "Grado de satisfacción de los usuarios (encuesta breve)."])

    # 13. Petitorio
    s += h1("13. Lo que se solicita a la Superioridad")
    s += [pj("Para avanzar con la presente propuesta, se solicita respetuosamente:")]
    s += [P.pasos([(1, "<b>Aval institucional</b> para la continuidad y extensión de los sistemas desarrollados."),
                   (2, "<b>Creación o designación del Área de Sistemas y Transformación Digital</b>, con el personal que la Superioridad determine."),
                   (3, "<b>Designación de referentes</b> en las áreas que se prioricen para la próxima etapa."),
                   (4, "<b>Autorización de pruebas piloto</b> en dichas áreas y de los espacios de capacitación correspondientes."),
                   (5, "Uso de <b>cuentas institucionales</b> y, a mediano plazo, de un <b>servidor propio</b> para alojar los sistemas."),
                   (6, "Una <b>demostración práctica</b> ante la Superioridad de los sistemas en funcionamiento.")])]
    s += h2("Conclusión")
    s += [pj("La informatización de la gestión administrativa no es un objetivo a futuro: ya está ocurriendo en la Institución, con resultados "
             "concretos, personal propio y sin costo de licencias. Darle un marco institucional, mediante la creación de un área específica, "
             "permitirá multiplicar esos resultados en todas las oficinas, áreas y divisiones, con orden, seguridad y continuidad, en "
             "beneficio de la Policía de Tucumán y de la comunidad a la que sirve."),
          caja("Los sistemas y esta propuesta <b>se irán optimizando en forma continua</b>, incorporando las necesidades y sugerencias de cada área.", "ok"),
          firma()]
    return s


if __name__ == "__main__":
    doc = Doc(SALIDA)
    doc.multiBuild(armar())
    print(SALIDA)
