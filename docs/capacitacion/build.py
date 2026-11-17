"""Propuesta: Plataforma de Capacitación Virtual de la Policía de Tucumán (D.G.I.I.). PDF A4.

Uso (desde la raíz del repo):
    PDF=docs/Propuesta_Plataforma_Capacitacion_Virtual.pdf python3 docs/capacitacion/build.py
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

DIR = os.path.join(os.path.dirname(__file__), "img")
SALIDA = os.environ.get("PDF", "Propuesta_Plataforma_Capacitacion_Virtual.pdf")
B = P.B
NAVY, AZUL, TINTA, GRIS, AMARILLO, VERDE = B.NAVY, B.AZUL, B.TINTA, B.GRIS, B.AMARILLO, B.VERDE
W, H, M, ANCHO = B.W, B.H, B.M, B.ANCHO
st = P.st
Titulo, caja, tabla, imagen, lista, kpis, h1, h2 = P.Titulo, P.caja, P.tabla, P.imagen, P.lista, P.kpis, P.h1, P.h2
AUTOR = "Crio. Abog. Rodríguez Julio, Crio. Abog. Aira Celestina y Of. Aux. Ponce Sergio"
HOY = date.today()
FECHA = f"{MESES[HOY.month - 1].capitalize()} de {HOY.year}"
ROJO = colors.HexColor("#C2410C")
st["carta"] = ParagraphStyle("carta", parent=st["p"], fontSize=9.2, leading=12.2, firstLineIndent=28, alignment=4, spaceAfter=2)
st["just"] = ParagraphStyle("just", parent=st["p"], alignment=4)


def I(n):
    return os.path.join(DIR, n)


def pj(t):
    return Paragraph(t, st["just"])


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
    c.drawCentredString(W / 2, H - 100 * mm, "POLICÍA DE TUCUMÁN · DIRECCIÓN GENERAL DE INSTITUTOS E INSTRUCCIÓN")
    c.setFillColor(colors.white)
    c.setFont("SB", 13)
    c.drawCentredString(W / 2, H - 116 * mm, "PROPUESTA INSTITUCIONAL")
    c.setFont("SB", 24)
    c.drawCentredString(W / 2, H - 131 * mm, "PLATAFORMA DE")
    c.drawCentredString(W / 2, H - 142 * mm, "CAPACITACIÓN VIRTUAL")
    c.setFont("S", 12.5)
    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.drawCentredString(W / 2, H - 154 * mm, "Disertaciones, cursos, inscripción y asistencia para todo el personal policial,")
    c.drawCentredString(W / 2, H - 161 * mm, "con registro de datos para la gestión de la formación")
    c.setFillColor(AMARILLO)
    c.roundRect(W / 2 - 62 * mm, H - 182 * mm, 124 * mm, 11 * mm, 5.5 * mm, fill=1, stroke=0)
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
    c.drawString(M, H - 7.6 * mm, "PLATAFORMA DE CAPACITACIÓN VIRTUAL · PROPUESTA")
    c.setFont("S", 8.5)
    c.drawRightString(W - M, H - 7.6 * mm, "POLICÍA DE TUCUMÁN · D.G.I.I.")
    c.setStrokeColor(colors.HexColor("#CBD5E1"))
    c.line(M, 13 * mm, W - M, 13 * mm)
    c.setFillColor(GRIS)
    c.setFont("S", 7.5)
    c.drawString(M, 8.5 * mm, f"Elaborado por Crio. Abog. Rodríguez J., Crio. Abog. Aira C. y Of. Aux. Ponce S. · {FECHA}")
    c.setFont("S", 8)
    c.drawRightString(W - M, 8.5 * mm, f"Página {doc.page}")
    c.restoreState()


class Doc(BaseDocTemplate):
    def __init__(self, ruta):
        super().__init__(ruta, pagesize=B.A4, leftMargin=M, rightMargin=M, topMargin=20 * mm, bottomMargin=18 * mm,
                         title="Plataforma de Capacitación Virtual – Propuesta", author=AUTOR)
        fr = Frame(M, 18 * mm, ANCHO, H - 38 * mm, id="f")
        self.addPageTemplates([PageTemplate("portada", [Frame(0, 0, W, H)], onPage=portada), PageTemplate("normal", [fr], onPage=normal)])

    def afterFlowable(self, f):
        if isinstance(f, Titulo):
            self.notify("TOCEntry", (f.nivel, f.texto, self.page))


def firma():
    est = ParagraphStyle("f", parent=st["p"], alignment=1, leading=13, fontSize=9.5)
    t = Table([[Paragraph("_______________________<br/><b>Oficial Auxiliar PONCE Sergio</b><br/>Auxiliar de Secretaría Académica<br/>"
                          "I.E.S.P. “G.J.F.S.M.”", est),
                Paragraph("_______________________<br/><b>Comisario Abogada AIRA Celestina</b><br/>Policía de Tucumán", est),
                Paragraph("_______________________<br/><b>Comisario Abogado RODRÍGUEZ Julio</b><br/>Policía de Tucumán", est)]],
              colWidths=[ANCHO / 3] * 3)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return KeepTogether([Spacer(1, 10), t])


# ───────────────────────── Contenido ─────────────────────────
def armar():
    s = [NextPageTemplate("normal"), PageBreak()]

    # Nota de elevación
    s += [Paragraph(f"San Miguel de Tucumán, {HOY.day:02d} de {MESES[HOY.month - 1].capitalize()} de {HOY.year}.-",
                    ParagraphStyle("fr", parent=st["p"], alignment=2)), Spacer(1, 8),
          Paragraph("Al Señor<br/>Jefe de Policía de la Provincia<br/><u>Su Despacho:</u>", st["p"]), Spacer(1, 6),
          Paragraph("<b>Ref.:</b> Propuesta de creación de una Plataforma de Capacitación Virtual para el personal policial, a cargo de la "
                    "Dirección General de Institutos e Instrucción.-", st["p"]), Spacer(1, 6),
          Paragraph("De mi mayor consideración:", st["p"]),
          Paragraph("Tenemos el agrado de dirigirnos a Usted, por la vía jerárquica correspondiente, a fin de elevar a su consideración la "
                    "propuesta de creación de una <b>Plataforma de Capacitación Virtual</b> de la Policía de Tucumán: un espacio digital en el que "
                    "todo el personal en actividad, identificándose con su número de legajo o su DNI, pueda ser convocado a disertaciones de "
                    "profesionales, inscribirse a los cursos del plan anual de capacitación, cursarlos a distancia o en forma presencial, y contar "
                    "con su historial de formación.", st["carta"]),
          Paragraph("La propuesta responde a una necesidad señalada desde hace tiempo: la difusión de las capacitaciones <b>no llega por igual</b> "
                    "a todas las dependencias, y no todo el personal tiene la posibilidad real de acceder a un curso. La era digital permite "
                    "resolverlo: una misma convocatoria, al mismo tiempo, para toda la Provincia, y la posibilidad de <b>replicar y reforzar</b> "
                    "el conocimiento de cada disertación sin límite de cupo ni de distancia.", st["carta"]),
          Paragraph("Esta iniciativa forma parte de la propuesta general de informatización ya elevada, pero se presenta <b>en forma individual</b> "
                    "porque tiene un área responsable definida, una base de personal ya disponible y un beneficio inmediato para toda la "
                    "Institución. Como en los demás sistemas, cada acción que el personal realice en la plataforma queda registrada como dato, "
                    "lo que permitirá por primera vez conocer con precisión cuánto, en qué y dónde se capacita la Policía de Tucumán.", st["carta"]),
          Paragraph("Los Comisarios Abogados que suscriben velan por que el tratamiento de los datos del personal y el funcionamiento de la "
                    "plataforma se encuadren en la normativa vigente. Quedamos a disposición para una demostración práctica.", st["carta"]),
          Paragraph("Sin otro particular, saludamos a Usted con atenta y distinguida consideración y respeto.-", st["carta"]),
          firma()]

    s += [PageBreak(), Paragraph("Índice", st["h1"]), Spacer(1, 4)]
    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle("t0", fontName="SB", fontSize=10, leading=13, textColor=NAVY),
                       ParagraphStyle("t1", fontName="S", fontSize=8.6, leading=10.4, leftIndent=14, textColor=TINTA)]
    s += [toc]

    # Resumen
    s += h1("Resumen ejecutivo")
    s += [Paragraph("<b>Qué se propone:</b> una plataforma web propia, administrada por la D.G.I.I., donde el personal policial en actividad "
                    "ingresa con su legajo o DNI, recibe las convocatorias, se inscribe, cursa (en vivo, grabado o presencial), registra su "
                    "asistencia y acumula su legajo de formación; y donde la conducción obtiene datos para planificar la capacitación.", st["lead"]),
          Spacer(1, 4),
          kpis([("1", "convocatoria igual<br/>para toda la Provincia"), ("Legajo/DNI", "acceso validado contra<br/>la base del personal"),
                ("$0", "en licencias<br/>de software"), ("Datos", "de oferta, inscripción,<br/>asistencia y resultados")]),
          Spacer(1, 8),
          tabla(["Punto", "Síntesis"], [
              ["<b>Problema</b>", "Difusión despareja de las capacitaciones; inscripciones por nota o por contacto personal; sin registro unificado de "
                                  "quién se capacitó en qué; disertaciones valiosas que se pierden al terminar."],
              ["<b>Solución</b>", "Plataforma con acceso restringido al personal, calendario del plan anual, disertaciones virtuales obligatorias o "
                                  "voluntarias, inscripción y asistencia en línea, certificados y legajo de formación de cada agente."],
              ["<b>Beneficio</b>", "Igualdad de acceso en toda la Provincia; el conocimiento se replica y se refuerza; menos papel y menos trámites; "
                                   "datos para decidir qué, dónde y a quién capacitar."],
              ["<b>Base disponible</b>", "La D.G.I.I. cuenta con la base del personal policial en actividad, que valida el ingreso y evita cargar datos."],
              ["<b>Costo</b>", "Sin licencias. Herramientas de uso libre, equipamiento existente y personal propio; videoconferencia con servicios gratuitos "
                               "o los que la Institución ya utiliza."],
              ["<b>Se solicita</b>", "Aval para desarrollar la plataforma, autorización de uso de la base de personal con resguardo legal, y una prueba piloto "
                                     "con el plan anual de capacitación."]],
              [30 * mm, ANCHO - 30 * mm])]

    # 1. Fundamentación
    s += h1("1. Fundamentación")
    s += [pj("La capacitación continua es una obligación del personal y una responsabilidad de la Institución. La Policía de Tucumán cuenta con un "
             "plan anual de capacitación y con profesionales dispuestos a disertar, dentro y fuera de la fuerza. El problema no es la falta de "
             "oferta sino el <b>circuito</b>: la convocatoria se difunde por notas y por contacto personal, llega antes a unas dependencias que a "
             "otras, los cupos se cubren sin que muchos se hayan enterado, y el personal del interior tiene menos posibilidades de asistir."),
          pj("A eso se suma que lo que se enseña en cada disertación <b>se pierde cuando termina</b>: no queda grabado, no se puede volver a "
             "ver, y quien no pudo asistir no tiene forma de reponerlo. Y, por último, la Institución no sabe con precisión cuánto se capacita: "
             "los certificados quedan en legajos de papel, sin un registro consolidado por agente, dependencia o tema."),
          imagen(I("cobertura.png"), pie="Figura 1. La difusión actual depende de la dependencia y del contacto; la plataforma convoca a todos por igual.",
                 alto_max=62 * mm)]
    s += h2("Aprovechar el momento digital")
    s += [pj("Hoy todo el personal tiene un teléfono con conexión. Una disertación dictada una vez en la capital puede verse en vivo desde "
             "cualquier Unidad Regional y quedar grabada para quien esté de servicio. La inscripción deja de ser una nota y pasa a ser un toque "
             "en la pantalla. La asistencia deja de ser una planilla y pasa a ser un registro automático. El certificado deja de ser un papel "
             "que se extravía y pasa a ser un dato en el legajo del agente."),
          caja("Cada una de esas acciones, al hacerse en la plataforma, <b>se convierte en un dato</b>. Y cuando se tienen datos de todo lo que se "
               "hace, el análisis posible es inmenso: qué temas tienen más demanda, qué dependencias se capacitan menos, cuántas horas de "
               "formación acumula cada agente, qué disertaciones conviene repetir y dónde.", "ok")]
    s += h2("Por qué una propuesta individual")
    s += [pj("Esta plataforma forma parte de la propuesta general de informatización, pero se eleva por separado porque reúne tres condiciones "
             "que permiten avanzar de inmediato: un <b>área responsable</b> definida (la D.G.I.I.), una <b>base de datos</b> del personal ya "
             "disponible, y un <b>beneficio directo</b> para cada agente de la Provincia desde el primer día. El mismo criterio se aplicará a cada "
             "sistema: una propuesta general que fija la política, y propuestas individuales que la concretan área por área.")]

    # 2. Qué es
    s += h1("2. Qué es la plataforma")
    s += [imagen(I("circuito.png"), pie="Figura 2. Circuito completo de la capacitación y los datos que genera cada paso.", alto_max=78 * mm),
          Spacer(1, 4),
          tabla(["Módulo", "Qué hace"], [
              ["<b>Acceso del personal</b>", "Ingreso con número de legajo o DNI, validado contra la base del personal en actividad de la D.G.I.I. Solo "
                                             "personal policial; cada agente ve su propia información."],
              ["<b>Plan anual de capacitación</b>", "Calendario con todos los cursos y disertaciones del año: tema, disertante, modalidad, fecha, sede o "
                                                    "enlace, cupo, destinatarios y carácter obligatorio o voluntario."],
              ["<b>Convocatoria</b>", "Aviso a todo el personal al mismo tiempo, o al perfil que corresponda (jerarquía, dependencia, función), por "
                                      "la plataforma, correo o WhatsApp."],
              ["<b>Disertaciones virtuales</b>", "En vivo por videoconferencia, con grabación disponible después para replicar y reforzar el contenido. "
                                                 "Material de apoyo descargable."],
              ["<b>Inscripción</b>", "En línea, con control de cupo, lista de espera y confirmación. Para cursos en la Provincia o fuera de ella, "
                                     "con la autorización que corresponda."],
              ["<b>Asistencia</b>", "Registro automático en lo virtual; en lo presencial, por código QR o lista digital. Constancia para la dependencia."],
              ["<b>Evaluación y certificados</b>", "Cuestionarios breves cuando el curso lo exige; certificado digital verificable con código QR."],
              ["<b>Legajo de formación</b>", "Historial de cada agente: cursos, horas, resultados y certificados, consultable por él y por la D.G.I.I."],
              ["<b>Tablero de gestión</b>", "Indicadores por tema, dependencia, Unidad Regional, jerarquía y período, para planificar el año siguiente."]],
              [42 * mm, ANCHO - 42 * mm])]
    s += h2("Obligatorias y voluntarias")
    s += [pj("Cada capacitación se carga como <b>obligatoria</b> (para un universo definido: toda la fuerza, una jerarquía, una función) o "
             "<b>voluntaria</b>. En las obligatorias, la plataforma muestra a la conducción quién la completó y quién no, y recuerda a los "
             "pendientes; en las voluntarias, registra la demanda, que es un dato valioso para planificar.")]

    # 3. Datos
    s += h1("3. Del registro al análisis: lo que permiten los datos")
    s += [pj("Hoy la pregunta «¿cuánto se capacitó la Policía este año?» se responde sumando planillas. Con la plataforma, cada acción queda "
             "registrada en el momento y la respuesta está disponible al instante, con el detalle que la conducción necesite."),
          tabla(["Pregunta de gestión", "Hoy", "Con la plataforma"], [
              ["¿A cuántos agentes llegó la convocatoria y cuántos se inscribieron?", "No se sabe.", "Se mide por dependencia y región."],
              ["¿Qué dependencias o regiones se capacitan menos?", "Se intuye.", "Indicador comparable, al día."],
              ["¿Cuántas horas de formación acumula cada agente?", "Certificados en papel.", "Legajo de formación consolidado."],
              ["¿Qué temas tienen más demanda y cuáles faltan?", "No se registra.", "Inscriptos, lista de espera y encuestas."],
              ["¿Quién completó una capacitación obligatoria?", "Listas manuales.", "Cumplimiento por agente y dependencia."],
              ["¿Qué disertaciones conviene repetir y dónde?", "Criterio del momento.", "Asistencia, visualizaciones y evaluación."],
              ["¿Cómo evolucionó la formación de una promoción o una jerarquía?", "Imposible de consolidar.", "Series por año y cohorte."]],
              [ANCHO * 0.44, ANCHO * 0.2, ANCHO * 0.36]),
          caja("La <b>automatización</b> no solo ahorra trámites: produce, como efecto, los datos. Lo que antes era una planilla que alguien debía "
               "armar al final del año, ahora es un tablero que se actualiza con cada inscripción y cada asistencia. Ese análisis es la base para "
               "que la D.G.I.I. planifique el plan anual con evidencia y lo informe a la Superioridad.", "tip")]
    s += h2("Antes y después")
    s += [tabla(["Tarea", "Hoy", "Con la plataforma"], [
        ["Difundir un curso", "Nota, cadena de mensajes, llega a algunos.", "Una publicación: llega a todos los destinatarios."],
        ["Inscribirse", "Nota por vía jerárquica o contacto personal.", "Un toque en el celular, con confirmación."],
        ["Controlar el cupo", "Lista manual.", "Automático, con lista de espera."],
        ["Tomar asistencia", "Planilla en papel.", "Registro automático o QR."],
        ["Emitir certificados", "Uno por uno, impresos y firmados.", "Digitales, verificables, en el legajo."],
        ["Informar la capacitación anual", "Semanas de recopilación.", "Tablero al día."],
        ["Reponer una disertación perdida", "No es posible.", "Grabación disponible."]],
        [40 * mm, (ANCHO - 40 * mm) / 2, (ANCHO - 40 * mm) / 2], ROJO)]

    # 4. Marco legal y seguridad
    s += h1("4. Marco legal, seguridad y protección de datos")
    s += [pj("La plataforma utiliza datos del personal policial. Por eso su diseño parte del resguardo legal:"),
          tabla(["Aspecto", "Cómo se resuelve"], [
              ["Base del personal", "Se usa solo para validar el ingreso (legajo o DNI) y mostrar nombre, jerarquía y dependencia. No se exportan ni "
                                    "se comparten los datos personales; cada agente ve únicamente los propios."],
              ["Protección de datos (Ley N.º 25.326)", "Finalidad definida (capacitación), acceso por roles, registro de cada acceso, contraseñas "
                                                        "cifradas y resguardo en base de datos propia."],
              ["Reglamentación interna", "La D.G.I.I. dicta las pautas de uso: quién publica, quién convoca, qué capacitaciones son obligatorias y "
                                         "cómo se certifican, en el marco de la Ley N.º 3656 y del régimen de personal."],
              ["Validez de los certificados", "Certificado digital con código de verificación y firma de la autoridad de la D.G.I.I.; a futuro, firma "
                                              "digital según la Ley N.º 7.291 de adhesión a la Ley N.º 25.506."],
              ["Revisión jurídica", "Los Comisarios Abogados del proyecto revisan el reglamento, los textos y el tratamiento de los datos."]],
              [46 * mm, ANCHO - 46 * mm]),
          caja("<b>Encuadre legal permanente:</b> toda publicación, convocatoria y certificación se emite por la autoridad competente de la D.G.I.I.; "
               "la plataforma es el medio, no la fuente de la obligación.", "ok")]

    # 5. Tecnología
    s += h1("5. Modelo tecnológico y costos")
    s += [tabla(["Componente", "Solución", "Costo"], [
        ["Plataforma web", "Desarrollo propio con herramientas de uso libre, como los sistemas ya en funcionamiento en la D.G.I.I. y el I.E.S.P.", "Sin licencias"],
        ["Base de datos", "Base propia del personal y de capacitaciones, con respaldo; a escala, en servidores de la Policía.", "Sin licencias"],
        ["Videoconferencia", "Servicios gratuitos o los que la Institución ya utiliza; grabación alojada en cuentas institucionales.", "Sin costo adicional"],
        ["Acceso del personal", "Desde el celular o la PC, instalable como aplicación en la pantalla de inicio.", "Equipamiento existente"],
        ["Avisos", "Correo institucional y WhatsApp, con el mismo texto para todos.", "Sin costo"]],
        [34 * mm, ANCHO - 34 * mm - 28 * mm, 28 * mm]),
          Spacer(1, 6),
          pj("La plataforma se integra con los sistemas existentes: el legajo de formación puede alimentar el legajo del personal y los legajos "
             "académicos del I.E.S.P., sin cargar dos veces el mismo dato.")]

    # 6. Implementación
    s += h1("6. Implementación por etapas e indicadores")
    s += [P.pasos([(1, "<b>Relevamiento (1 mes):</b> circuito actual de capacitación, plan anual, modelos de certificados y requisitos de la D.G.I.I."),
                   (2, "<b>Desarrollo (2 meses):</b> acceso con legajo o DNI, calendario, convocatoria, inscripción y asistencia."),
                   (3, "<b>Piloto (3 meses):</b> una disertación virtual abierta a toda la Provincia y dos cursos del plan anual con inscripción en línea."),
                   (4, "<b>Evaluación:</b> comparación con la línea de base y ajustes según la opinión del personal."),
                   (5, "<b>Extensión:</b> todo el plan anual, certificados digitales, legajo de formación y tablero para la Superioridad.")]),
          Spacer(1, 6),
          tabla(["Indicador", "Cómo se mide"], [
              ["Alcance de la convocatoria", "Agentes que recibieron y abrieron cada convocatoria, por dependencia y región."],
              ["Igualdad de acceso", "Inscriptos del interior respecto del total, antes y después."],
              ["Participación", "Inscriptos, asistentes y aprobados por capacitación."],
              ["Cumplimiento de obligatorias", "Porcentaje del universo convocado que completó la capacitación."],
              ["Tiempo administrativo", "Horas dedicadas a difusión, inscripción, asistencia y certificados, antes y después."],
              ["Satisfacción", "Encuesta breve al cierre de cada capacitación."]],
              [48 * mm, ANCHO - 48 * mm])]

    # 7. Pedido
    s += h1("7. Lo que se solicita a la Superioridad")
    s += [P.pasos([(1, "<b>Aval institucional</b> para desarrollar la Plataforma de Capacitación Virtual a cargo de la D.G.I.I."),
                   (2, "<b>Autorización</b> para utilizar la base del personal en actividad con la finalidad exclusiva de validar el acceso, bajo las "
                       "condiciones de resguardo descriptas."),
                   (3, "<b>Prueba piloto</b> con una disertación virtual para toda la Provincia y dos cursos del plan anual."),
                   (4, "<b>Cuentas institucionales</b> para videoconferencia y almacenamiento de grabaciones."),
                   (5, "<b>Difusión</b> de la plataforma a todas las dependencias mediante la orden del día, para que la primera convocatoria llegue a todos.")])]
    s += h2("Conclusión")
    s += [pj("La Policía de Tucumán ya capacita a su personal y cuenta con profesionales dispuestos a compartir su conocimiento. Lo que falta es "
             "el medio para que ese esfuerzo llegue a todos por igual, se pueda replicar y reforzar, y quede registrado. La era digital lo hace "
             "posible sin costo de licencias y con personal propio. Y, como en cada sistema que la Institución incorpore, la automatización del "
             "trámite traerá consigo lo más valioso: <b>datos de todo lo que se hace</b>, para planificar la formación del personal con evidencia "
             "y optimizar un rendimiento institucional que hoy ya es reconocido."),
          caja("La propuesta queda <b>abierta a las observaciones de la Superioridad y de la D.G.I.I.</b>: el relevamiento inicial y el piloto "
               "definirán sus ajustes.", "ok"),
          firma()]
    return s


if __name__ == "__main__":
    doc = Doc(SALIDA)
    doc.multiBuild(armar())
    print(SALIDA)
