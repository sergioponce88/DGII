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
AUTOR = "Crio. Abog. Rodríguez Julio, Crio. Abog. Aira Celestina y Of. Aux. Ponce Sergio"
HOY = date.today()
FECHA = f"{MESES[HOY.month - 1].capitalize()} de {HOY.year}"

st["carta"] = ParagraphStyle("carta", parent=st["p"], fontSize=9.0, leading=11.8, firstLineIndent=28, alignment=4, spaceAfter=1)
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
    c.drawCentredString(W / 2, 76 * mm, "Elevada a consideración del Comando Superior por")
    c.setFont("SB", 13)
    c.drawCentredString(W / 2, 68 * mm, "Comisario Abogado RODRÍGUEZ Julio")
    c.drawCentredString(W / 2, 61 * mm, "Comisario Abogada AIRA Celestina")
    c.drawCentredString(W / 2, 54 * mm, "Oficial Auxiliar PONCE Sergio")
    c.setFont("S", 10)
    c.drawCentredString(W / 2, 47.5 * mm, "Derecho y marco legal · Gestión administrativa y sumarial · Desarrollo de sistemas")
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
    c.setFont("S", 7.5)
    c.drawString(M, 8.5 * mm, f"Elaborado por Crio. Abog. Rodríguez J., Crio. Abog. Aira C. y Of. Aux. Ponce S. · {FECHA}")
    c.setFont("S", 8)
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
    t = Table([[Paragraph("_______________________<br/><b>Oficial Auxiliar PONCE Sergio</b><br/>Auxiliar de Secretaría Académica<br/>"
                          "I.E.S.P. “G.J.F.S.M.”", est),
                Paragraph("_______________________<br/><b>Comisario Abogada AIRA Celestina</b><br/>Policía de Tucumán", est),
                Paragraph("_______________________<br/><b>Comisario Abogado RODRÍGUEZ Julio</b><br/>Policía de Tucumán", est)]],
              colWidths=[ANCHO / 3] * 3)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return KeepTogether([Spacer(1, 8), t])


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
          Paragraph("La propuesta surge del trabajo conjunto de <b>dos abogados</b> y de un <b>oficial con formación en desarrollo de sistemas</b>, "
                    "con experiencia en lo <b>sumarial y lo administrativo</b>. Los abogados velan por que todo lo que se desarrolle se encuadre "
                    "en la <b>normativa vigente</b> y en lo dispuesto por la <b>justicia ordinaria</b>, de modo que las herramientas sean, a la "
                    "vez, prácticas para el personal y jurídicamente sólidas.", st["carta"]),
          Paragraph("Esta iniciativa busca <b>complementar y potenciar la tarea de excelencia</b> que viene demostrando la Policía de Tucumán, "
                    "reconocida públicamente y reflejada en las estadísticas. En 2026, cuando la Justicia provincial ya trabaja con expedientes digitales, "
                    "<b>digitalizar los datos</b> que produce la Institución permitirá ver su trabajo con precisión, decidir con evidencia y hacer visibles "
                    "aspectos de la gestión que hoy no se aprecian.", st["carta"]),
          Paragraph("Los sistemas desarrollados con personal propio demuestran que es posible ordenar la gestión administrativa, contar con "
                    "trazabilidad completa de los expedientes, producir documentación normalizada y obtener estadísticas para la toma de "
                    "decisiones, <b>sin costo de licencias</b> y utilizando el equipamiento existente. A ellos se suma un <b>piloto para el oficial de "
                    "turno</b>, que guía el procedimiento desde el celular y genera las actas y notas sin volver a transcribir los datos.", st["carta"]),
          Paragraph("En ese marco, se propone <b>comenzar a trabajar</b> junto a las distintas divisiones y Unidades Regionales: designar "
                    "referentes, relevar sus procesos y necesidades, y avanzar con pruebas piloto graduales, de modo que la Superioridad "
                    "cuente con información concreta para decidir los pasos siguientes.", st["carta"]),
          Paragraph("La presente no pretende ser una propuesta cerrada: quedamos <b>abiertos a las ideas, observaciones y propuestas</b> que formule "
                    "la Superioridad o que surjan de las distintas áreas, ya que de eso se trata: de evaluar en conjunto qué puede mejorarse y "
                    "de optimizar el trabajo de la Institución.", st["carta"]),
          Paragraph("Quedamos a disposición para una demostración práctica. Sin otro particular, saludamos a Usted con atenta y distinguida consideración y respeto.-", st["carta"]),
          firma()]

    s += [PageBreak(), Paragraph("Índice", st["h1"]), Spacer(1, 2)]
    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle("t0", fontName="SB", fontSize=9.0, leading=10.6, textColor=NAVY),
                       ParagraphStyle("t1", fontName="S", fontSize=7.8, leading=8.7, leftIndent=14, textColor=TINTA)]
    s += [toc]

    # Resumen ejecutivo
    s += h1("Resumen ejecutivo")
    s += [Paragraph("<b>Qué se propone:</b> informatizar progresivamente la gestión administrativa de oficinas, áreas y divisiones de la Policía "
                    "de Tucumán —divisiones, departamentos y Unidades Regionales— mediante sistemas web propios, <b>comenzando por un relevamiento "
                    "con referentes de cada área</b> y pruebas piloto graduales, para que el trabajo <b>administrativo y operativo</b> quede registrado "
                    "como datos útiles para el análisis y la toma de decisiones.", st["lead"]), Spacer(1, 4),
          kpis([("6 + 2", "sistemas propios y<br/>propuestas individuales"), ("$0", "en licencias<br/>de software"), ("App", "en el celular y la PC,<br/>instalable"),
                ("Propio", "personal para desarrollo<br/>y capacitación")]),
          Spacer(1, 8),
          tabla(["Punto", "Síntesis"], [
              ["<b>Fundamento</b>", "La información que produce la Policía es un <b>recurso estratégico</b>: digitalizada, permite medir, comparar "
                                  "y decidir con evidencia, y hace visibles cargas de trabajo y problemas que hoy no se ven."],
              ["<b>Firma digital</b>", "Certificados del personal registrados en DIMAC, para que lo que se genera en los sistemas se firme y circule con plena "
                                       "validez jurídica, sin imprimir (sección 12)."],
              ["<b>Resultado</b>", "Una plataforma policial unificada: registro único, mapa del delito en tiempo real, cruce de información, "
                                   "historial de casos y tablero de gestión, con envío automático al SNIC (sección 8)."],
              ["<b>Problema</b>", "Gestión en papel y planillas dispersas: demoras para ubicar expedientes, notas con formatos distintos, errores repetidos, "
                                  "vencimientos que se pasan y ausencia de estadísticas confiables."],
              ["<b>Solución</b>", "Sistemas web con usuario y clave, roles por jerarquía, registro de cada acción, documentos normalizados en Word/PDF, "
                                  "alertas, informes, validaciones que impiden cargar datos contradictorios y app instalable en el celular."],
              ["<b>Método</b>", "Cada sistema nace del <b>análisis del flujo de trabajo</b> del área, con entrevistas a su personal. El sistema de "
                                "expedientes es un ejemplo: no se impone un modelo único, se diseña a medida de cada lugar."],
              ["<b>Evidencia</b>", "Sistemas en funcionamiento en la D.G.I.I. y el I.E.S.P. (expedientes, legajos académicos, legajo de compañía, gabinete "
                                   "interdisciplinario), un <b>piloto para oficiales de turno</b> que ya genera actas y notas, y Medicina Legal en desarrollo. Se suman dos propuestas individuales: la <b>Plataforma de Capacitación Virtual</b> y el <b>Repositorio de Protocolos y Normativa</b>."],
              ["<b>Costo</b>", "Sin licencias. Infraestructura en la nube en planes gratuitos, equipamiento existente y personal propio. Para la escala "
                               "institucional se recomienda alojarlos en servidores de la Policía."],
              ["<b>Capacitación</b>", "Corta y por perfil (de 2 a 6 horas), dictada por personal propio, con manual y material digital."],
              ["<b>Se solicita</b>", "Aval de la Superioridad para comenzar: referentes por división y Unidad Regional, relevamiento de procesos y pruebas piloto."]],
              [30 * mm, ANCHO - 30 * mm])]

    # 1. Fundamentación
    s += h1("1. Fundamentación: el dato como recurso de gestión")
    s += [pj("La Policía de Tucumán viene mostrando un rendimiento creciente, reconocido por la comunidad, los medios, el Gobierno de la Provincia "
             "y los Ministerios de Seguridad provincial y nacional. Esta propuesta parte de ese reconocimiento: <b>no viene a corregir lo que se hace "
             "bien</b>, sino a dotar a la Institución de herramientas para que ese esfuerzo quede registrado, se mida y se multiplique."),
          pj("A diario la Institución produce un volumen enorme de información: expedientes, notas, pases, oficios judiciales, sumarios, actas, "
             "partes, servicios, legajos, licencias, inventarios y estadísticas. Gran parte se registra todavía en libros de papel, planillas sueltas "
             "o archivos de Word que se copian de una vez para la otra. Esa información existe, pero <b>no está disponible</b> para ser consultada, "
             "sumada, comparada ni analizada.")]
    s += h2("De la información al dato")
    s += [pj("La diferencia es concreta. Un libro de guardia <b>registra</b>; una base de datos, además, <b>responde</b>: cuántos procedimientos hubo "
             "en una franja horaria, cuánto tardó cada trámite, qué dependencia tiene mayor carga en relación con su personal o qué oficios están "
             "por vencer. Digitalizar no es pasar el papel a la pantalla: es registrar cada hecho de manera <b>estructurada, uniforme y en el "
             "momento</b>, para que el mismo dato sirva a la vez para el documento, el parte, la estadística y la decisión."),
          tabla(["Información en papel", "Dato digitalizado"], [
              ["Se lee de a un registro por vez.", "Se cuenta, se suma y se compara en segundos."],
              ["Está en un solo lugar físico.", "Está disponible para cada nivel de conducción, según su rol."],
              ["Se reescribe en cada pieza, con errores.", "Se carga una vez y se reutiliza sin cambios."],
              ["Se pierde con el traslado o el retiro del personal.", "Queda en la Institución, con historial y respaldo."],
              ["Muestra el pasado, cuando alguien lo revisa.", "Muestra el presente y permite anticipar."]],
              [ANCHO / 2, ANCHO / 2])]
    s += h2("Lo que hoy no se ve")
    s += [pj("Con la forma actual de registro, muchas preguntas de gestión no tienen respuesta precisa, aunque el personal conozca la realidad por "
             "experiencia. La digitalización permite responderlas con números y, con ello, <b>clarificar áreas y cuestiones</b> que hoy quedan fuera "
             "de la vista de la conducción:"),
          tabla(["Pregunta de gestión", "Hoy", "Con datos digitalizados"], [
              ["¿Cuántas horas del personal operativo se destinan a tareas administrativas?", "Se estima por experiencia.", "Se mide por trámite, dependencia y período."],
              ["¿En qué zonas y franjas horarias se concentra la demanda?", "Partes y libros dispersos.", "Mapa y horarios consolidados, al día."],
              ["¿Cuánto tarda la respuesta a un oficio judicial?", "Se controla de memoria.", "Plazos, alertas y tiempos promedio."],
              ["¿Qué carga tiene cada comisaría u oficina respecto de su personal?", "No es comparable.", "Indicadores por dependencia."],
              ["¿Qué actuaciones vuelven con requerimientos de la Fiscalía, y por qué?", "No se registra.", "Se registra y se corrige en el origen."],
              ["¿Qué domicilios, vehículos o lugares se repiten en distintas intervenciones?", "Queda en la memoria de cada uno.", "Cruces sistemáticos, con resguardo legal."],
              ["¿Cómo evolucionan licencias, aptitudes y formación del personal?", "Expedientes en papel.", "Tablero de personal y legajo digital."],
              ["¿Qué estado tienen móviles, armamento y bienes?", "Inventarios manuales.", "Inventario trazable y actualizado."]],
              [ANCHO * 0.42, ANCHO * 0.22, ANCHO * 0.36]),
          caja("Lo que no se mide difícilmente pueda gestionarse. Registrar el trabajo como datos también hace visible el <b>mérito del personal</b>: "
               "el volumen real de tareas, los resultados obtenidos y el esfuerzo que hoy no figura en ningún informe.", "ok")]
    s += h2("Gestión de la seguridad basada en evidencia")
    s += [pj("Las experiencias policiales de referencia coinciden en que los datos son la base de la gestión moderna. El caso más citado es el "
             "del Departamento de Policía de Nueva York, donde un sistema informatizado para registrar y mapear el delito por barrio (CompStat) "
             "permitió desplegar los recursos con mayor eficacia [1]."),
          pj("El Banco Interamericano de Desarrollo sostiene que las políticas de prevención del delito requieren <b>indicadores de gestión</b> "
             "(procesos, actividades y recursos) y <b>estratégicos</b> (impactos) [2], y en 2025 publicó una encuesta para evaluar a las policías "
             "de la región que dedica módulos específicos a los <b>datos administrativos</b> y a la <b>información, el análisis de datos y la "
             "tecnología</b> [3]. Es decir: la capacidad de registrar y analizar datos ya es un parámetro con el que se mide a las instituciones policiales."),
          pj("En el plano nacional, la Ley N.º 25.266 obliga a las policías provinciales a remitir datos estadísticos a la Dirección Nacional de "
             "Política Criminal [4]. Cuanto mejor sea el registro de origen, más precisa será la información que la Provincia aporta y la que "
             "recibe para planificar.")]
    s += h2("El contexto de Tucumán en 2026")
    s += [pj("La transformación digital ya está en marcha en la Provincia. El Poder Judicial de Tucumán completó en abril de 2026 la "
             "digitalización de los expedientes penales en papel de su fuero conclusional, un proceso iniciado en 2020 [5]; la Corte Suprema "
             "había creado en 2017 una Oficina de Digitalización como complemento del expediente digital [6]. La Provincia adhirió al régimen "
             "nacional de firma digital mediante la Ley N.º 7.291 [7], y en el orden nacional la Ley N.º 27.446 reconoció los documentos y "
             "expedientes electrónicos [8]."),
          caja("La Policía produce la <b>primera pieza</b> de cada proceso penal y una gran parte de la información de seguridad de la Provincia. "
               "Si la Justicia ya trabaja en digital y la Policía continúa en papel, la brecha se traduce en transcripciones, demoras y pérdida de "
               "información. Digitalizar el origen del dato es el paso que completa el circuito.", "ojo")]
    s += h2("Situación observada")
    s += lista(["<b>Partes por WhatsApp:</b> el informe de cada hecho a los jefes se envía por mensajería, en forma informal, sin registro "
                "institucional ni resguardo de la información; si el hecho no es de relevancia, el parte queda en la nada.",
                "Registros en <b>libros físicos</b> que solo puede consultar quien está en la oficina.",
                "Notas redactadas a partir de <b>modelos viejos</b>, con membretes distintos, autoridades desactualizadas y errores que se arrastran.",
                "<b>Seguimiento manual</b> de dónde está cada expediente y quién lo tiene.",
                "<b>Vencimientos</b> y plazos judiciales controlados de memoria.",
                "Estadísticas que se arman a mano, tarde y con criterios distintos según la dependencia.",
                "Dependencia de personas: cuando alguien se traslada, se pierde parte del conocimiento de la oficina."])
    s += [Spacer(1, 4), pj("<b>Por qué ahora.</b> Hoy existen herramientas tecnológicas de uso libre que permiten desarrollar sistemas a medida con recursos propios, accesibles desde "
             "el celular y sin grandes inversiones, como lo demuestran los sistemas que ya funcionan en la Institución. La Policía cuenta además "
             "con personal joven formado en informática y con capacidad de adaptación, lo que hace viable una transformación progresiva y sostenida.")]
    s += h2("Impacto esperado")
    s += [pj("La experiencia de los sistemas en funcionamiento permite fijar <b>metas de mejora significativas</b>, que se verificarán con datos en "
             "cada prueba piloto, comparando contra una línea de base tomada antes de implementar:"),
          tabla(["Aspecto", "Situación actual", "Meta con la informatización"], [
              ["Confección de un sumario o actuación", "Horas de redacción y transcripción.", "Reducir el tiempo a la mitad o menos."],
              ["Ubicar un expediente o trámite", "Minutos u horas de búsqueda.", "Segundos, desde cualquier puesto autorizado."],
              ["Completitud de la documentación de procedimientos", "Depende de la memoria del oficial.", "Mejorar entre un 200 % y un 300 %."],
              ["Plazos y vencimientos", "Control de memoria.", "Alertas previas; tender a cero vencidos."],
              ["Estadística para la conducción", "Planillas mensuales armadas a mano.", "Disponible al día, por nivel."]],
              [ANCHO * 0.34, ANCHO * 0.30, ANCHO * 0.36]),
          caja("Las metas son <b>objetivos de trabajo</b>, no resultados garantizados: cada piloto medirá la situación de partida y el resultado "
               "alcanzado, para que la Superioridad decida con evidencia.", "tip")]

    # 2. Antecedentes
    s += h1("2. Antecedentes: lo que ya funciona")
    s += h2("Quiénes impulsan la propuesta")
    s += [tabla(["Integrante", "Aporte"], [
        ["<b>Comisario Abogado RODRÍGUEZ Julio</b>", "Formación jurídica y experiencia en lo sumarial y administrativo. Control del <b>marco legal</b>: "
                                                     "validez de las actuaciones, normativa procesal y reglamentaria, protección de datos y relación con el Ministerio Público Fiscal."],
        ["<b>Comisario Abogada AIRA Celestina</b>", "Formación jurídica. Control del <b>marco legal</b>: que cada sistema, documento y procedimiento se "
                                                    "encuadre en la normativa vigente y en lo dispuesto por la justicia ordinaria."],
        ["<b>Oficial Auxiliar PONCE Sergio</b><br/>Auxiliar de Secretaría Académica, I.E.S.P.", "Experiencia en lo sumarial y administrativo como "
                                                     "instructor y en la tramitación de expedientes; análisis de procesos y desarrollo de los sistemas en funcionamiento."]],
        [60 * mm, ANCHO - 60 * mm]),
        Spacer(1, 4),
        caja("La <b>combinación de profesiones</b> es la fortaleza del proyecto: los Comisarios Abogados Rodríguez y Aira aseguran que cada "
             "documento y cada registro respeten la normativa vigente y lo dispuesto por la justicia ordinaria, y tengan validez; el conocimiento técnico y la experiencia en la tarea diaria aseguran que el sistema "
             "sea simple, rápido y realmente útil para el personal. Ambos comparten la experiencia en lo sumarial y lo administrativo, que es "
             "donde más tiempo se pierde hoy y donde más se puede ganar.", "ok")]
    s += h2("Sistemas en funcionamiento")
    s += [pj("La propuesta no parte de cero. Con personal propio y sin costo se desarrollaron los siguientes sistemas, que hoy constituyen "
             "la experiencia piloto de esta iniciativa:"),
          tabla(["Sistema", "Área", "Qué resuelve", "Estado"], [
              ["<b>Registro, Control y Tramitación de Expedientes</b>", "Dirección General de Institutos e Instrucción",
               "Libro de mesa de entradas, seguimiento, reingresos, digitalización en Drive, 26 modelos de notas en Word, actuaciones y sumarios, "
               "oficios judiciales, actividades, alertas e informes.", "En funcionamiento"],
              ["<b>Legajos Académicos</b>", "I.E.S.P.", "Notas, promedios, orden de mérito, mesas y calendario de finales, actas volantes con el modelo "
               "del Ministerio, Portal del Cadete y Portal Docente, aviso diario por WhatsApp y legajo digital tipo libro con código QR de verificación.",
               "En funcionamiento"],
              ["<b>Legajo de Compañía de Cadetes</b>", "I.E.S.P.", "Disciplina (sanciones con planilla Word), sanidad y A.R.T., servicio y guardias, "
               "documentación del cadete, carga rápida de legajos anteriores y centro de análisis.", "En funcionamiento"],
              ["<b>Gabinete Interdisciplinario</b>", "I.E.S.P.", "Certificados médicos, prórrogas y altas con sus PDF, y seguimiento de cada cadete.", "En funcionamiento"],
              ["<b>Actuaciones para Oficiales de Turno</b>", "Comisarías (piloto)", "Ruta guiada del procedimiento desde el celular, acta para "
               "NOTeWEB, notas por delito, denuncias desde el PDF de NOTeWEB, croquis, oficios y mapa del delito.", "Piloto en curso"],
              ["<b>Medicina Legal</b>", "División Medicina Legal", "Registro de intervenciones y exámenes e informes técnicos para las Unidades Fiscales.", "En desarrollo"]],
              [42 * mm, 34 * mm, ANCHO - 106 * mm, 30 * mm]),
          Spacer(1, 6),
          ]
    s += h2("Propuestas individuales que integran esta política")
    s += [pj("Además de los sistemas en funcionamiento, se elevan por separado dos propuestas que concretan la misma política en áreas con "
             "responsable definido y beneficio inmediato para toda la fuerza. Cada sistema de esta propuesta tendrá, del mismo modo, su "
             "<b>propuesta individual</b>: la general fija la política; las individuales la llevan a cada área."),
          tabla(["Propuesta", "Qué resuelve", "Datos que genera"], [
              ["<b>Plataforma de Capacitación Virtual</b><br/>D.G.I.I.", "Convocatoria igual para toda la Provincia, disertaciones en vivo y grabadas, "
               "inscripción y asistencia en línea, legajo de formación de cada agente.", "Alcance de cada convocatoria, inscriptos, asistencia, "
               "horas de formación por agente, dependencia y región."],
              ["<b>Repositorio de Protocolos y Normativa Vigente</b>", "Un solo lugar oficial, con vigencia revisada jurídicamente, donde consultar "
               "desde el celular los protocolos propios y de otros organismos, y la normativa vigente, con aviso de novedades.",
               "Qué se consulta, desde dónde y cuándo; novedades leídas; temas que generan dudas y conviene capacitar."]],
              [46 * mm, (ANCHO - 46 * mm) * 0.55, (ANCHO - 46 * mm) * 0.45]),
          caja("Ambas se complementan: el repositorio muestra qué normas consulta el personal y dónde tiene dudas; la plataforma convoca a "
               "la disertación que lo explica. Y ambas producen datos que hoy no existen.", "tip")]
    s += h2("Capacidades comunes ya probadas")
    s += [pj("Con el desarrollo de estos sistemas se fue armando un conjunto de soluciones que ya funcionan y que pueden aplicarse en "
             "cualquier área que se incorpore:"),
          tabla(["Capacidad", "Qué aporta", "Dónde funciona"], [
              ["<b>App en el celular</b>", "Se instala como una aplicación (Android, iPhone y PC), sin tiendas ni costo.", "Legajos, Oficiales"],
              ["<b>Usuarios y permisos</b>", "Clave cifrada, cambio obligatorio en el primer ingreso, bloqueo por intentos fallidos y permisos por pantalla.",
               "Todos"],
              ["<b>Base de datos propia</b>", "Cada sistema tiene su base independiente: un problema en uno no afecta a los demás.", "Todos"],
              ["<b>Documentos normalizados</b>", "Notas, actas y planillas en Word y PDF con membrete y formato institucional.", "Todos"],
              ["<b>Validación de datos</b>", "Opciones con botones y controles que no dejan guardar datos contradictorios (fechas u horas imposibles).",
               "Oficiales, Legajos"],
              ["<b>Legajo digital verificable</b>", "Legajo tipo libro y PDF con código QR que permite verificar que es auténtico.", "Legajos, Compañía"],
              ["<b>Avisos y portales</b>", "Avisos diarios por WhatsApp y portales para cadetes y docentes.", "Legajos"],
              ["<b>Análisis de datos</b>", "Tableros, estadísticas, mapa del delito e informes para decidir.", "Expedientes, Compañía, Oficiales"]],
              [38 * mm, ANCHO - 38 * mm - 40 * mm, 40 * mm]),
          Spacer(1, 6),
          imagen(I("mB.png"), pie="Figura 1. Sistema de Expedientes D.G.I.I.: tramitación asistida con vista previa de la nota.", alto_max=95 * mm)]

    # 3. Objetivos
    s += h1("3. Objetivos")
    s += [pj("<b>Objetivo general.</b> Impulsar la informatización progresiva de la gestión administrativa de la Policía de Tucumán, mediante sistemas propios, "
             "seguros y accesibles, comenzando por el trabajo conjunto con cada división y Unidad Regional.")]
    s += [Spacer(1, 2), pj("<b>Objetivos específicos:</b>")]
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
        caja("Los beneficios concretos (tiempos, cantidades, vencimientos evitados) se medirán con los indicadores propuestos en el punto 17, "
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
    s += [Spacer(1, 4),
          pj("<b>Cómo se hace hoy.</b> Desde hace años, las comisarías, las jefaturas de zona y las Unidades Regionales elaboran su estadística "
             "y su mapa del delito con <b>planillas de Excel y archivos comunes</b> que cada dependencia completa a mano, al final del turno o "
             "del mes, con los datos que recuerda o que vuelve a copiar de los libros o de los partes enviados por WhatsApp. Esas planillas viajan por correo o mensajería, se "
             "consolidan a mano en cada nivel y llegan a la conducción con días de demora. La información resultante es, con frecuencia, "
             "<b>errónea o incompleta</b>: criterios distintos entre dependencias, hechos duplicados o faltantes, direcciones mal escritas que no "
             "se pueden ubicar en el mapa, y cifras que no coinciden entre la planilla de la comisaría, la de la zona y la de la regional."),
          tabla(["Planillas de Excel (hoy)", "Datos del sistema"], [
              ["Se cargan después, de memoria o copiando del libro.", "Se generan en el momento, desde el mismo procedimiento que ya se documentó."],
              ["Cada dependencia usa su propio criterio y formato.", "Un solo formato, con opciones cerradas y validaciones."],
              ["Se consolidan a mano en cada nivel.", "Se consolidan solos: comisaría, zona, regional y provincia ven el mismo dato."],
              ["Direcciones libres, difíciles de ubicar.", "Ubicación por GPS o por calle y altura, lista para el mapa."],
              ["Errores que nadie detecta hasta que se comparan.", "Incoherencias detectadas al cargar; sin duplicados."],
              ["Llegan con días de demora.", "Disponibles al instante, con el detalle que cada nivel necesite."]],
              [ANCHO / 2, ANCHO / 2], colors.HexColor("#C2410C")),
          caja("El <b>mapa del delito</b> y la <b>estadística</b> no son un módulo aparte que alguien deba alimentar: son el <b>resultado automático</b> "
               "de documentar el procedimiento. Un buen análisis depende de un buen registro; por eso es fundamental que tanto el trabajo "
               "<b>administrativo</b> como el <b>operativo</b> queden registrados de manera completa y uniforme desde el inicio.", "ok")]

    # 6. Caso testigo
    s += h1("8. Lo que deja la informatización: resultados esperados")
    s += [pj("Las secciones anteriores describen el punto de partida y el método. Esta muestra <b>hacia dónde lleva</b>: lo que la Institución "
             "obtiene cuando todo lo que hace queda registrado como dato, de manera digital, uniforme y completa. Es una visión, pero no una "
             "abstracción: cada capacidad se apoya en el registro de origen que el piloto para oficiales de turno ya produce, y cada una se "
             "construirá a partir del análisis de las áreas y se validará en un piloto medido."),
          caja("En una frase: pasar de <b>registrar lo que pasó</b> a <b>anticipar lo que puede pasar</b>, con una visión precisa, al día y "
               "comparable de toda la Provincia.", "ok"),
          Spacer(1, 4),
          Paragraph("<b>Una Plataforma Digital Policial Unificada: cinco capacidades que hoy no existen</b>", st["p"]),
          tabla(["Capacidad", "Qué hace", "Resultado para la Institución"], [
              ["<b>1. Registro digital unificado</b>", "Captura el hecho una sola vez: lugar exacto con GPS y tipo de lugar; fecha, día, hora del hecho y "
               "del aviso; datos de víctimas e involucrados; modus operandi, medios empleados, bienes y vía de escape.",
               "Fin de las planillas manuscritas y de Excel. Datos exactos y consistentes en toda la Provincia. <i>Ya existe en el piloto.</i>"],
              ["<b>2. Mapa del delito y alertas</b>", "Une la base con un sistema de información geográfica: mapas interactivos, zonas calientes "
               "y franjas horarias de mayor riesgo, en tiempo real.", "Patrullaje orientado por la demanda real; análisis táctico para cada "
               "comisaría, zona y regional."],
              ["<b>3. Cruce de información</b>", "Relaciona personas, apodos, vehículos, domicilios y hechos que en papel quedaban en "
               "expedientes inconexos de distintas dependencias.", "Detección temprana de reiteraciones, bandas y redes; apoyo a las áreas "
               "de investigación."],
              ["<b>4. Historial de casos</b>", "Sistematiza modus operandi y evidencias de los delitos graves.", "Conexión de hechos seriales y "
               "priorización de líneas de investigación, en apoyo de la Fiscalía."],
              ["<b>5. Tablero de gestión</b>", "Mide tiempos de respuesta, patrullaje por cuadrante, uso de móviles y carga de trabajo por "
               "comisaría.", "Distribución de personal y recursos según datos; rendición de cuentas con evidencia."]],
              [36 * mm, (ANCHO - 36 * mm) * 0.5, (ANCHO - 36 * mm) * 0.5]),
          Paragraph("Las capacidades 3 y 4 se diseñan con los Comisarios Abogados del proyecto: acceso solo para las áreas habilitadas, registro "
                    "de cada consulta y el encuadre legal y judicial que corresponda en cada caso.", st["pc"]),
          Spacer(1, 6),
          Paragraph("<b>El salto de calidad institucional</b>", st["p"]),
          tabla(["Dimensión", "Hoy: papel y planillas", "Con el sistema informatizado"], [
              ["Disponibilidad del dato", "Planillas que tardan semanas en llegar.", "En tiempo real, en cada nivel de conducción."],
              ["Calidad del dato", "Inconsistencias, extravíos, ilegibilidad y errores manuales.", "Estandarizado, validado y auditable."],
              ["Despliegue del patrullaje", "Rutina o intuición individual.", "Dinámico, hacia zonas y horarios de mayor riesgo."],
              ["Cruce de información", "Imposible entre comisarías o brigadas.", "Patrones, series y vínculos detectados."],
              ["Estadística y rendición de cuentas", "Carga manual mensual.", "Reportes automáticos y envío al SNIC."],
              ["Calidad de las actuaciones", "Depende de la memoria del oficial.", "Lista de control completa antes de elevar."],
              ["Parte a la superioridad", "WhatsApp: informal, sin registro ni resguardo.", "Registrado, seguro, con conteos y acuse de lectura."]],
              [40 * mm, (ANCHO - 40 * mm) / 2, (ANCHO - 40 * mm) / 2], colors.HexColor("#C2410C")),
          Spacer(1, 6),
          Paragraph("<b>Impacto esperado</b>", st["p"]),
          tabla(["Para", "Resultado esperado"], [
              ["<b>La conducción</b>", "Personal y móviles asignados según la demanda real; dependencias comparables con el mismo criterio; "
                                       "decisiones con evidencia."],
              ["<b>La Justicia</b>", "Actuaciones completas desde el origen, menos requerimientos y causas en condiciones de investigarse y elevarse a juicio."],
              ["<b>La Provincia y la Nación</b>", "Datos estandarizados para el Sistema Nacional de Información Criminal (SNIC), con menos tiempo de "
                                                  "reporte y mayor precisión en lo que Tucumán aporta y recibe para planificar."],
              ["<b>La comunidad</b>", "Una recepción más ágil en las dependencias reduce las barreras para denunciar y ayuda a visibilizar la "
                                      "<b>cifra negra</b>: el delito que hoy no llega a registrarse."],
              ["<b>El personal</b>", "Menos tiempo de escritorio, más tiempo de servicio, y su trabajo registrado y reconocido."]],
              [40 * mm, ANCHO - 40 * mm]),
          caja("Estos resultados son el <b>efecto esperado de registrar bien</b>, no promesas: cada piloto medirá su línea de base y su resultado, "
               "para que la Superioridad decida su extensión con evidencia.", "tip")]

    s += h1("9. Caso testigo: Sistema de Expedientes de la D.G.I.I.")
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
    s += h1("10. Modelo tecnológico y costos")
    s += [imagen(I("arquitectura.png"), pie="Figura 5. Componentes de los sistemas.", alto_max=85 * mm),
          Spacer(1, 4),
          tabla(["Componente", "Herramienta", "Costo actual"], [
              ["Programación", "Python y Streamlit (software libre)", "Sin costo"],
              ["Código y versiones", "GitHub", "Sin costo"],
              ["Publicación web", "Streamlit Community Cloud", "Sin costo (plan gratuito)"],
              ["Base de datos", "PostgreSQL en Supabase", "Sin costo (plan gratuito)"],
              ["Archivos (PDF)", "Google Drive", "Sin costo (cuenta existente)"],
              ["App en el celular", "Aplicación instalable (PWA) publicada en GitHub Pages", "Sin costo"],
              ["Corrección de textos", "LanguageTool y diccionario propio", "Sin costo"],
              ["Inteligencia artificial", "Google Gemini (solo ayuda de redacción en Expedientes)", "Sin costo (nivel gratuito, opcional)"],
              ["Equipamiento", "PC y celulares que ya usa el personal", "Sin costo adicional"],
              ["Desarrollo y capacitación", "Personal policial propio", "Dentro de sus funciones"]],
              [40 * mm, 72 * mm, ANCHO - 112 * mm]),
          Spacer(1, 6),
          caja("<b>No genera costos de licencias ni de compra de software.</b> Los planes gratuitos tienen límites de capacidad y de uso, "
               "adecuados para pruebas piloto y oficinas. Para el despliegue a escala institucional se recomienda alojar los sistemas en "
               "<b>servidores propios de la Policía</b> y utilizar cuentas institucionales: como todo el software es libre, el único requerimiento "
               "sería la infraestructura, sin pago de licencias.", "ok")]

    # 8. Seguridad
    s += h1("11. Seguridad y protección de datos")
    s += lista(["<b>Acceso personal</b> con legajo y clave; las claves se guardan cifradas y nadie puede verlas; cambio obligatorio "
                "de la clave inicial y <b>bloqueo temporal</b> ante intentos fallidos.",
                "Cada sistema con su <b>propia base de datos</b>, separada de las demás.",
                "<b>Roles y permisos</b> según jerarquía y función: cada usuario ve y hace solo lo que le corresponde.",
                "<b>Auditoría</b> de todas las acciones (usuario, fecha, hora y detalle).",
                "<b>Respaldos</b> descargables que nunca incluyen claves ni credenciales.",
                "Conexiones cifradas (https) desde cualquier dispositivo.",
                "Usuarios que dejan el área se <b>deshabilitan</b>, conservando el historial.",
                "Política de inteligencia artificial: por defecto, los documentos con datos personales <b>no se envían</b> a servicios externos. "
                "Las actas de los oficiales se arman <b>sin inteligencia artificial</b>, con modelos fijos.",
                "Estadísticas y exportaciones <b>anonimizadas</b>: el DNI se reemplaza por un código.",
                "Tratamiento de datos personales conforme a la <b>Ley N° 25.326 de Protección de los Datos Personales</b> y a las disposiciones "
                "internas que dicte la Superioridad."])
    s += [caja("<b>Encuadre legal permanente:</b> los Comisarios Abogados Rodríguez Julio y Aira Celestina revisan que cada sistema, cada "
               "modelo de documento y cada procedimiento se ajusten a la normativa vigente y a lo dispuesto por la justicia ordinaria, antes "
               "de su implementación y durante su uso.", "ok"),
          caja("Se propone elaborar, para aprobación de la Superioridad, un <b>reglamento interno de uso</b> de los "
               "sistemas: responsables de cada base de datos, alta y baja de usuarios, respaldos periódicos y confidencialidad.", "tip")]

    # 10. Cómo empezar
    s += h1("12. Firma digital: que lo digital tenga plena validez")
    s += [pj("Informatizar sin firma digital deja el circuito a mitad de camino: el documento se genera en el sistema, pero hay que "
             "imprimirlo, firmarlo, sellarlo y volver a escanearlo o entregarlo en papel. La <b>firma digital</b> cierra ese círculo. La Ley "
             "Nacional N.º 25.506 la define como el resultado de aplicar a un documento digital un procedimiento matemático que requiere "
             "información de exclusivo conocimiento del firmante [9]. Su uso en la administración pública protege la <b>autenticidad, "
             "integridad y no repudio</b> de los documentos electrónicos."),
          pj("La ley establece además que, si la verificación de una firma digital es verdadera, se presume —salvo prueba en contrario— que el "
             "documento <b>no fue modificado</b> desde el momento de su firma [9]. Para una institución que produce piezas que llegan a la Justicia, "
             "esa garantía es tan importante como la firma misma."),
          tabla(["Hoy: papel, firma ológrafa y sello", "Con firma digital"], [
              ["Imprimir, firmar, sellar, escanear o entregar en mano.", "El documento se firma y se envía desde el sistema, sin imprimir."],
              ["La autenticidad depende del sello y de la firma visible.", "La firma identifica al firmante y detecta cualquier alteración posterior."],
              ["El original en papel se traslada, se extravía o se deteriora.", "El original digital se conserva íntegro y se verifica en cualquier momento."],
              ["Cada pase entre oficinas suma horas o días.", "Las notas, informes y elevaciones circulan al instante, con constancia."],
              ["Un parte por mensajería no tiene autor verificable.", "El parte firmado identifica sin duda a quien informa."]],
              [ANCHO / 2, ANCHO / 2], colors.HexColor("#C2410C")),
          Spacer(1, 6),
          Paragraph("<b>Qué se propone</b>", st["p"]),
          *lista(["Gestionar el <b>certificado de firma digital</b> del personal que firma documentos —jefes de dependencia, oficiales de turno, "
                 "instructores sumariales, personal de las Direcciones— con su <b>registro en DIMAC</b>, y llevar un padrón de firmantes habilitados.",
                 "Incorporar la firma digital en los sistemas propios, empezando por las notas y elevaciones de la D.G.I.I., los certificados del "
                 "I.E.S.P. y los partes a la superioridad.",
                 "Avanzar, en coordinación con el Ministerio Público Fiscal y el Poder Judicial, hacia el envío de piezas firmadas digitalmente, "
                 "según los mecanismos que esos organismos admitan.",
                 "Mientras tanto, los documentos impresos con firma ológrafa y sello siguen siendo válidos: la firma digital se incorpora de "
                 "forma progresiva, sin interrumpir el trabajo."]),
          caja("El certificado de firma digital emitido bajo la Política Única de Certificación es gratuito [10]: incorporarlo no requiere "
               "inversión, sino <b>organización</b>.", "ok"),
          pj("<b>Qué significa para todo este proyecto.</b> Con la firma digital, la informatización deja de ser una ayuda para redactar y pasa a "
             "ser un <b>circuito digital completo</b>: el dato se registra una vez, el documento se genera solo, se firma con plena validez "
             "jurídica, se envía sin papel y queda verificable. Menos impresiones y traslados, menos tiempo entre el hecho y la pieza en manos de "
             "la Justicia, y una trazabilidad que el papel nunca puede ofrecer.")]

    s += h1("13. Cómo empezar: trabajo conjunto con las divisiones")
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
    s += h2("Un análisis profundo, área por área")
    s += [pj("Cada área de la Policía tiene su propio circuito, sus plazos, sus documentos y su lenguaje. Por eso el análisis del flujo de trabajo "
             "no es un trámite previo sino el <b>corazón de la propuesta</b>: es lo que permite que el sistema resuelva problemas reales y que la "
             "información que produzca sea útil para decidir. Se propone una metodología en siete etapas:"),
          tabla(["Etapa", "Qué se hace", "Resultado"], [
              ["1. Relevamiento", "Entrevistas, observación del circuito real y recolección de libros, planillas y modelos.", "Mapa del proceso actual."],
              ["2. Medición", "Volúmenes mensuales, tiempos de cada paso, demoras y tareas que se repiten.", "Línea de base para comparar."],
              ["3. Inventario de datos", "Qué datos se generan, dónde, quién los usa y cuáles se copian varias veces.", "Diccionario de datos del área."],
              ["4. Diagnóstico", "Cuellos de botella, controles que dependen de la memoria y riesgos legales o de seguridad.", "Informe de diagnóstico."],
              ["5. Diseño", "Circuito propuesto, validado con el personal y revisado jurídicamente.", "Proceso mejorado y requisitos."],
              ["6. Priorización", "Matriz de volumen, impacto y factibilidad.", "Orden de implementación."],
              ["7. Piloto y medición", "Uso real acotado y comparación con la línea de base.", "Resultados para decidir la extensión."]],
              [32 * mm, ANCHO * 0.52, ANCHO - 32 * mm - ANCHO * 0.52]),
          Spacer(1, 6),
          pj("A modo orientativo, y sujeto a lo que surja del relevamiento, estos son ejemplos de la información que distintas áreas podrían "
             "aportar y de las decisiones que permitiría tomar:"),
          tabla(["Área", "Información que se digitaliza", "Decisiones que permite"], [
              ["Comisarías y jefaturas de zona", "Procedimientos, actas, denuncias recibidas, servicios y móviles.", "Distribución de personal y móviles por zona y horario."],
              ["Unidades Regionales", "Consolidado de sus dependencias.", "Comparar dependencias y planificar refuerzos."],
              ["Personal y recursos humanos", "Legajos, licencias, aptitudes, destinos y formación.", "Cobertura de servicios y planificación de carrera."],
              ["Logística", "Móviles, combustible, armamento, equipamiento y bienes.", "Mantenimiento preventivo y compras basadas en uso real."],
              ["Áreas judiciales y sumariales", "Oficios, sumarios, plazos y respuestas.", "Cumplimiento ante la Justicia y control de vencimientos."],
              ["Áreas técnicas (Criminalística, Medicina Legal)", "Pedidos, intervenciones, tiempos y resultados.", "Demanda real y tiempos de respuesta."],
              ["Institutos de formación", "Legajos académicos, calificaciones y asistencia.", "Calidad de la formación y seguimiento de cada cadete."]],
              [40 * mm, (ANCHO - 40 * mm) / 2, (ANCHO - 40 * mm) / 2]),
          caja("El análisis también revela lo que funciona bien y conviene preservar: la informatización se adapta al saber hacer de cada área, "
               "no lo reemplaza.", "ok")]
    s += h2("Del análisis surgen las propuestas")
    s += [pj("El análisis no es un trámite previo a un sistema ya decidido: es el <b>origen de cada propuesta</b>. Al relevar una comisaría, una "
             "zona, una oficina o una dirección, aparecen cosas que nadie había puesto por escrito: un trámite que pasa por cuatro manos cuando "
             "podría pasar por una, una planilla que se completa dos veces, un plazo que se controla de memoria, un dato que se pide y nunca "
             "se usa. Y aparecen también las prácticas que ese lugar hace mejor que los demás y que conviene extender."),
          tabla(["El análisis de información permite…", "…y el resultado es"], [
              ["Identificar fallas del sistema de trabajo que hoy se repiten sin que nadie las vea.", "Una propuesta concreta de mejora para esa área, con su línea de base."],
              ["Detectar lo que se hace bien, dónde y por qué.", "Buenas prácticas documentadas y extendidas a otras dependencias."],
              ["Dimensionar volúmenes, tiempos y cargas reales.", "Prioridades fundadas en datos, no en la urgencia del momento."],
              ["Descubrir datos que se generan y se pierden.", "Nuevos indicadores para la conducción, sin trabajo adicional."],
              ["Comparar circuitos entre dependencias que hacen lo mismo.", "Un circuito único, más simple, validado con quienes lo ejecutan."]],
              [ANCHO / 2, ANCHO / 2]),
          Spacer(1, 4),
          pj("El fin de ese recorrido es la <b>informatización del flujo de trabajo</b> tal como quedó rediseñado: la falencia descubierta se "
             "corrige en el circuito nuevo, lo que se hacía bien se optimiza, y el sistema que lo soporta produce, desde el primer día, los datos "
             "que permiten seguir mejorando. Así, cada área analizada se convierte en una propuesta, cada propuesta en un sistema, y cada "
             "sistema en información para la próxima decisión."),
          caja("Es un <b>ciclo de mejora continua</b> para toda la Policía provincial: analizar, descubrir, proponer, informatizar, medir y volver "
               "a analizar. Las propuestas individuales que acompañan a esta (capacitación y protocolos) nacieron exactamente así, y las que "
               "sigan nacerán del relevamiento que hoy se solicita autorizar.", "ok")]
    s += h2("Mesa de trabajo de informatización")
    s += [pj("Se sugiere convocar una <b>mesa de trabajo</b> integrada por un referente de cada división y Unidad Regional que se incorpore, "
             "junto con el personal que desarrolló los sistemas existentes. Sus integrantes mantienen sus funciones habituales y se reúnen "
             "periódicamente para:")]
    s += lista(["Relevar los procesos, libros, planillas y modelos de notas de cada área.",
                "Priorizar qué informatizar primero según volumen de trabajo y beneficio esperado.",
                "Acompañar las pruebas piloto y la capacitación en su área.",
                "Recoger las opiniones de los usuarios y proponer mejoras.",
                "Informar periódicamente a la Superioridad los avances y resultados."])
    s += [Spacer(1, 4), pj("<b>Guía de relevamiento por área.</b> Como complemento de las entrevistas, se propone completar para cada área una guía breve con la siguiente información:"),
          tabla(["Qué se releva", "Para qué"], [
              ["Trámites y documentos que se producen (y cuántos por mes)", "Dimensionar el trabajo y priorizar."],
              ["Libros, planillas y registros que se llevan", "Definir qué se digitaliza y con qué formato."],
              ["Modelos de notas, actas y formularios", "Incorporarlos como modelos automáticos."],
              ["Plazos y vencimientos que se controlan", "Configurar alertas."],
              ["Personal y equipamiento disponible (PC, celulares, conectividad)", "Planificar la implementación y la capacitación."],
              ["Principales dificultades actuales", "Orientar el sistema a resolver problemas reales."]],
              [ANCHO / 2, ANCHO / 2])]
    s += [Spacer(1, 4), pj("<b>Continuidad.</b> A medida que aumente la cantidad de áreas y usuarios, la propia experiencia indicará qué organización conviene darle a este "
             "trabajo para asegurar su continuidad, su seguridad y su crecimiento ordenado. Esa evaluación quedará a criterio de la Superioridad, "
             "con la información que surja de los pilotos.")]

    # 10. Capacitación
    s += h1("14. Capacitación del personal")
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
                "<b>Simulacros guionados</b>: un hecho simulado con roles (conductor, víctima, testigo, primer interventor, fiscalía) para "
                "practicar el abordaje de la escena y el uso del sistema, con planillas de evaluación.",
                "Acompañamiento durante las primeras semanas y consultas por mensajería.",
                "Requisito previo: manejo básico de celular o computadora."])
    s += [caja("<b>La capacitación no genera costos:</b> la dicta personal propio dentro de su horario de servicio, con material digital, "
               "sin traslados ni contrataciones externas.", "ok")]

    # 11. Implementación
    s += h1("15. Plan de implementación por etapas")
    s += [tabla(["Etapa", "Acciones", "Plazo orientativo"], [
        ["<b>1. Piloto</b> (en curso)", "Sistemas en funcionamiento en la D.G.I.I. y el I.E.S.P.; piloto del sistema para oficiales de turno; Medicina Legal en desarrollo.", "En marcha"],
        ["<b>2. Evaluación</b>", "Medición de indicadores, encuesta a usuarios, demostración a la Superioridad.", "60 a 90 días"],
        ["<b>3. Mesa de trabajo y análisis</b>", "Referentes por división y Unidad Regional; entrevistas y análisis del flujo de trabajo de cada área; priorización.", "Según disponga la Superioridad"],
        ["<b>4. Pilotos</b>", "Una o dos divisiones priorizadas (por ejemplo D-1, D-5 o Asuntos Internos) y una comisaría piloto por Unidad Regional.", "6 a 12 meses"],
        ["<b>5. Extensión</b>", "Extensión a otras oficinas y comisarías; servidor propio y cuentas institucionales; capacitación permanente.", "Mediano plazo"],
        ["<b>6. Oficial de turno</b>", "Extender el piloto a otros delitos y a una comisaría por Unidad Regional; sumar imágenes, videos y audios del procedimiento, en coordinación con el M.P.F.", "Según resultados del piloto"]],
        [42 * mm, ANCHO - 82 * mm, 40 * mm]),
        Spacer(1, 4),
        caja("Los plazos son orientativos y dependen de las prioridades y recursos que disponga la Superioridad. Cada etapa se evalúa antes de iniciar la siguiente.", "tip")]

    # 12. Riesgos e indicadores
    # Visión a futuro
    s += h1("16. La tarea del oficial de turno: de la idea al piloto")
    s += [Paragraph("La <b>sistematización de la tarea del oficial de turno</b> —oficial y auxiliar de turno de las comisarías— dejó de ser "
                    "solo una idea: ya existe un <b>sistema piloto</b> que se usa desde el celular, como <b>complemento de la plataforma de "
                    "denuncias digitales</b> del Ministerio Público Fiscal y no en reemplazo de ella. Es donde la informatización más "
                    "facilita el trabajo policial.", st["lead"])]
    s += h2("Lo que ya hace el piloto")
    s += [tabla(["Función", "Cómo ayuda al oficial"], [
        ["<b>Ruta guiada del procedimiento</b>", "Nueve pasos, de a dos preguntas por pantalla: toma de conocimiento, salida, arribo, primer "
                                                  "interventor, involucrados, inspección ocular, fiscalía, cumplimiento y llegada de equipos "
                                                  "(Criminalística, Policía Vial, grúa), y croquis. Comienza por lesiones culposas en siniestros viales."],
        ["<b>Pensado para la calle</b>", "Botones grandes, barra fija abajo, modo de alto contraste para el sol, ubicación por GPS, fotos que "
                                         "quedan como adjuntos, lectura del DNI desde una foto y dictado con el teclado del celular."],
        ["<b>Datos coherentes</b>", "No deja guardar datos contradictorios (fechas imposibles, horas incoherentes, croquis distinto de los "
                                    "vehículos cargados) y cada aviso de lo que falta lleva directo al dato a completar."],
        ["<b>Acta sin transcribir</b>", "El acta se arma sola, con modelos fijos y sin inteligencia artificial, lista para copiar en NOTeWEB "
                                        "y en Word con el croquis."],
        ["<b>Notas por delito</b>", "Propone las notas que corresponden al delito y las genera en A4, original y duplicado, listas para el sello."],
        ["<b>Denuncias ya tomadas</b>", "Con solo subir el PDF de la denuncia de NOTeWEB, propone las notas y actas de diligencias "
                                        "(constatación de domicilio, averiguaciones, notificación, secuestro, entrega)."],
        ["<b>Croquis dinámico</b>", "Editor en pantalla para dibujar el lugar (intersecciones, rotondas, rutas), con vehículos, personas, "
                                    "punto de impacto y orientación."],
        ["<b>Partes a la superioridad</b>", "Reemplazan el parte por WhatsApp: el oficial envía un parte preliminar con lo que sabe en el "
                                            "momento, marcando lo que está «a confirmar», y después el ampliatorio con los datos del caso. Los "
                                            "jefes lo reciben en una bandeja segura, con conteos por tipo de hecho y dependencia y acuse de lectura."],
        ["<b>Oficios y análisis</b>", "Oficios judiciales con plazos y semáforo de vencimiento; mapa del delito e informe para el análisis criminal."],
        ["<b>Respeto de competencias</b>", "El oficial registra lo que observa; las mediciones y la determinación técnica quedan a cargo de Criminalística."]],
        [42 * mm, ANCHO - 42 * mm]),
        Spacer(1, 4),
        caja("El piloto se está probando en uso real y en <b>simulacros con cadetes del I.E.S.P.</b>, midiendo el tiempo de cada paso y "
             "recogiendo sus observaciones para ajustarlo antes de extenderlo.", "ok")]
    s += h2("Situación actual: la Policía como auxiliar de la Justicia")
    s += [pj("El Ministerio Público Fiscal de Tucumán dio un paso importante con la denuncia digital y su plataforma de actuaciones: ordenó la "
             "recepción, unificó formatos y aceleró la llegada de la información a las Unidades Fiscales. Pero esa plataforma fue diseñada "
             "desde la necesidad de la Fiscalía, para optimizar <b>su</b> trabajo. La Policía, que es quien produce la información como auxiliar "
             "de la Justicia, <b>no fue contemplada</b>: en ella se carga, de forma manual, lo que antes hubo que escribir en otro lado, y la "
             "Institución sigue trabajando de manera precaria en cuanto a sistematización, sin un <b>registro propio y estructurado</b> de lo "
             "actuado en cada procedimiento."),
          caja("La brecha no está en la Fiscalía ni en la Policía, sino <b>entre ambas</b>: en el tramo que va desde el lugar del hecho hasta la "
               "actuación cargada, que nadie informatizó. Mejorar ese tramo mejora también la investigación y la elevación a juicio. La propuesta "
               "no modifica la plataforma del M.P.F.: informatiza el tramo policial y abre una instancia de coordinación con la Fiscalía.", "ojo"),
          pj("Además, en un mismo procedimiento el oficial transcribe una y otra vez los mismos datos —personas, documentos, domicilios, lugar, "
             "fecha y hora, elementos secuestrados, intervinientes, fiscalía— en actas, constancias, notas, partes y en la causa que se eleva a "
             "la Justicia provincial. Cada transcripción insume tiempo y abre la posibilidad de errores u omisiones."),
          pj("A esto se suma el <b>parte a la superioridad</b>. Hoy toda la Policía informa los hechos a sus jefes por <b>WhatsApp</b>: un "
             "mensaje informal, redactado a las apuradas mientras se procede, muchas veces como adelanto con datos que el oficial todavía no "
             "tiene confirmados. Ese parte no queda registrado en ningún sistema institucional, la información circula por una aplicación "
             "personal sin resguardo, y si el hecho no es de relevancia queda en la nada: nadie puede contar después cuántos hechos hubo, de "
             "qué tipo ni dónde. La plataforma lo reemplaza por un parte <b>registrado, seguro y ordenado</b>: preliminar con los datos «a "
             "confirmar» marcados, ampliatorio generado del caso, y una bandeja para los jefes con conteos y acuse de lectura."),
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
          caja("Es el mismo método que ya funciona en la Dirección General de Institutos e Instrucción y que el piloto aplica a las "
               "comisarías. El conjunto de notas de cada tipo de delito se completa con el <b>análisis junto a las comisarías</b> y los "
               "modelos que hoy utilizan, validados por quienes realizan la tarea.", "tip")]
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
    s += h2("Qué se logra y qué falta")
    s += lista(["<b>Ya en el piloto:</b> registro guiado y único de los datos del procedimiento, en el lugar del hecho, desde el celular.",
                "<b>A desarrollar:</b> registro de imágenes, videos y audios del hecho, con fecha, hora y ubicación, asociados al procedimiento, "
                "para documentar con precisión lo ocurrido.",
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
               "de cadena de custodia. Su extensión a otros delitos y comisarías se evaluará a partir de los resultados del piloto.", "ojo")]

    s += h1("17. Riesgos, mitigaciones e indicadores")
    s += [tabla(["Riesgo", "Mitigación"], [
        ["Dependencia de una sola persona", "Mesa de trabajo y referentes por área, código documentado y guardado en repositorios, manuales."],
        ["Resistencia al cambio", "Capacitación práctica, convivencia inicial con el libro físico y mejoras según la opinión de los usuarios."],
        ["Conectividad", "Funciona con datos móviles y bajo consumo; la documentación impresa sigue siendo válida."],
        ["Seguridad de la información", "Claves cifradas, roles, auditoría, respaldos y reglamento interno de uso."],
        ["Desajuste normativo", "Revisión jurídica permanente a cargo de los Comisarios Abogados del proyecto, según la normativa vigente y lo dispuesto por la justicia ordinaria."],
        ["Límites de los planes gratuitos", "Plan de migración a servidores institucionales, sin cambiar los sistemas."]],
        [52 * mm, ANCHO - 52 * mm], colors.HexColor("#C2410C"))]
    s += h2("Indicadores de seguimiento")
    s += lista(["Tiempo de confección de un sumario procesal completo (antes y después).",
                "Tiempo de documentación de un procedimiento con el sistema para oficiales, paso por paso.",
                "Tiempo promedio para ubicar un expediente.",
                "Tiempo desde el ingreso hasta la tramitación.",
                "Cantidad de expedientes vencidos o fuera de término.",
                "Cantidad de documentos generados con los modelos normalizados.",
                "Usuarios capacitados y activos por área.",
                "Grado de satisfacción de los usuarios (encuesta breve)."])

    # 13. Petitorio
    s += h1("18. Lo que se solicita a la Superioridad")
    s += [pj("Para avanzar con la presente propuesta —que queda abierta a las modificaciones e ideas que la Superioridad estime "
             "convenientes—, se solicita respetuosamente:")]
    s += [P.pasos([(1, "<b>Aval institucional</b> para adoptar la gestión basada en datos como política de la Institución y continuar los sistemas desarrollados."),
                   (2, "<b>Designación de referentes</b> en comisarías, jefaturas de zona, Unidades Regionales, departamentos, direcciones y oficinas, para conformar una mesa de trabajo."),
                   (3, "<b>Autorización para realizar entrevistas y analizar el flujo de trabajo</b> de esas áreas (procesos, libros y modelos de documentos)."),
                   (4, "<b>Autorización de pruebas piloto</b> en las áreas que se prioricen (incluida una comisaría por Unidad Regional) y de los espacios de capacitación."),
                   (5, "Uso de <b>cuentas institucionales</b> y, a mediano plazo, de un <b>servidor propio</b> para alojar los sistemas."),
                   (6, "Una <b>demostración práctica</b> ante la Superioridad de los sistemas en funcionamiento."),
                   (7, "<b>Autorización para extender el piloto del sistema para oficiales de turno</b> a una comisaría por Unidad Regional, en coordinación con el Ministerio Público Fiscal."),
                   (8, "<b>Aval para las propuestas individuales</b> de la Plataforma de Capacitación Virtual y del Repositorio de Protocolos y Normativa Vigente, que se elevan por separado."),
                   (9, "<b>Gestión de la firma digital</b> del personal que firma documentos, con el registro de los certificados en DIMAC, para incorporarla progresivamente a los sistemas.")])]
    s += h2("Conclusión")
    s += [pj("La informatización de la gestión administrativa no es un objetivo a futuro: ya está ocurriendo en la Institución, con resultados "
             "concretos, personal propio y sin costo de licencias, y viene a complementar la tarea de excelencia que la Policía de Tucumán "
             "demuestra y que es destacada públicamente. Comenzar a trabajar junto a las divisiones y las Unidades Regionales, "
             "<b>analizando en cada caso su flujo de trabajo</b>, "
             "hará surgir, área por área, las propuestas de mejora, las fallas a corregir y las buenas prácticas a extender; permitirá multiplicar esos resultados en todas las oficinas y comisarías, registrar el trabajo administrativo y operativo como datos "
             "útiles para decidir y facilitar la tarea del oficial de turno —que ya cuenta con un piloto y a futuro sumará imágenes, videos y "
             "audios del procedimiento— para cumplir con mayor agilidad lo que exige la Justicia, con orden, seguridad y continuidad, en "
             "beneficio de la Policía de Tucumán y de la comunidad a la que sirve."),
          caja("Esta propuesta está <b>abierta a las ideas y propuestas de la Superioridad</b> y de cada área. Su espíritu es evaluar en conjunto "
               "qué puede mejorarse y optimizar el trabajo de la Institución: los sistemas y este documento <b>se irán ajustando</b> con cada "
               "aporte que se reciba.", "ok"),
          firma()]
    s += [PageBreak(), Paragraph("Anexo: referencias", st["h1"]), Spacer(1, 4)]
    refs = [
        "[1] Banco Interamericano de Desarrollo, blog «Enfoque Educación», referencia al sistema CompStat del Departamento de Policía de Nueva York. blogs.iadb.org/educacion/es/?p=4640",
        "[2] BID (2017). <i>Información para la prevención del delito y la violencia</i>. Washington D. C.: Banco Interamericano de Desarrollo.",
        "[3] Sutton, H., Alvarado, N. y Keefer, P. (2025). <i>Encuesta sobre la gestión y administración de la policía en América Latina y el Caribe (EGAP-ALC): cuestionario y metodología</i>. BID. publications.iadb.org",
        "[4] Ley N.º 25.266, modificatoria de la Ley N.º 22.117 (Registro Nacional de Reincidencia), art. 13. argentina.gob.ar/normativa",
        "[5] Diario Judicial (18/05/2026). «Adiós para siempre al papel»: finaliza la digitalización de expedientes penales en Tucumán. diariojudicial.com",
        "[6] Diario Judicial. «Los números de la digitalización»: primer año del expediente digital en la Corte Suprema de Justicia de Tucumán. diariojudicial.com",
        "[7] Decreto N.º 165/2016 (Tucumán), reglamentario de la Ley N.º 7.291 de adhesión a la Ley N.º 25.506 de Firma Digital.",
        "[8] Ley N.º 27.446 de Simplificación y Desburocratización de la Administración Pública Nacional (B.O. 18/06/2018).",
        "[9] Ley N.º 25.506 de Firma Digital, arts. 2 y 8.",
        "[10] iProfesional (2026). «Diferencias entre firma electrónica y firma digital»: gratuidad del certificado bajo la Política Única de Certificación.",
        "Normativa provincial considerada: Ley N.º 8933 (Código Procesal Penal de Tucumán), Ley N.º 3656 (Orgánica de la Policía) y Ley N.º 25.326 de Protección de Datos Personales."]
    s += [Paragraph(r, st["li"]) for r in refs]
    return s


if __name__ == "__main__":
    doc = Doc(SALIDA)
    doc.multiBuild(armar())
    print(SALIDA)
