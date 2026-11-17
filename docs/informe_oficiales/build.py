"""Informe técnico-jurídico: Plataforma para Oficiales de Turno (prueba piloto). PDF A4.

Uso (desde la raíz del repo):
    PDF=docs/Informe_Plataforma_Oficiales_de_Turno.pdf python3 docs/informe_oficiales/build.py
Las capturas (img/) se generan con el sistema real y un caso ficticio; no contienen datos de causas reales.
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
SALIDA = os.environ.get("PDF", "Informe_Plataforma_Oficiales_de_Turno.pdf")
B = P.B
NAVY, AZUL, TINTA, GRIS, AMARILLO, VERDE = B.NAVY, B.AZUL, B.TINTA, B.GRIS, B.AMARILLO, B.VERDE
W, H, M, ANCHO = B.W, B.H, B.M, B.ANCHO
st = P.st
Titulo, caja, tabla, imagen, lista, kpis, h1, h2 = P.Titulo, P.caja, P.tabla, P.imagen, P.lista, P.kpis, P.h1, P.h2
AUTOR = "Crio. Abog. Rodríguez Julio, Crio. Abog. Aira Celestina y Of. Aux. Ponce Sergio"
HOY = date.today()
FECHA = f"{MESES[HOY.month - 1].capitalize()} de {HOY.year}"
ROJO = colors.HexColor("#C2410C")

st["carta"] = ParagraphStyle("carta", parent=st["p"], fontSize=9.4, leading=12.6, firstLineIndent=28, alignment=4, spaceAfter=2)
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
    c.drawCentredString(W / 2, H - 100 * mm, "POLICÍA DE TUCUMÁN")
    c.setFillColor(colors.white)
    c.setFont("SB", 13)
    c.drawCentredString(W / 2, H - 116 * mm, "INFORME TÉCNICO Y JURÍDICO")
    c.setFont("SB", 24)
    c.drawCentredString(W / 2, H - 131 * mm, "PLATAFORMA PARA")
    c.drawCentredString(W / 2, H - 142 * mm, "OFICIALES DE TURNO")
    c.setFont("S", 12.5)
    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.drawCentredString(W / 2, H - 154 * mm, "Herramienta de apoyo para documentar el procedimiento policial")
    c.drawCentredString(W / 2, H - 161 * mm, "desde el lugar del hecho")
    c.setFillColor(AMARILLO)
    c.roundRect(W / 2 - 62 * mm, H - 182 * mm, 124 * mm, 11 * mm, 5.5 * mm, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("SB", 10.5)
    c.drawCentredString(W / 2, H - 178.3 * mm, "Prueba piloto · sujeta a ajustes según la práctica")
    c.setFillColor(colors.white)
    c.setFont("S", 10)
    c.drawCentredString(W / 2, 76 * mm, "Elevado a consideración del Comando Superior por")
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
    c.drawString(M, H - 7.6 * mm, "PLATAFORMA PARA OFICIALES DE TURNO · INFORME TÉCNICO Y JURÍDICO")
    c.setFont("S", 8.5)
    c.drawRightString(W - M, H - 7.6 * mm, "POLICÍA DE TUCUMÁN")
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
                         title="Plataforma para Oficiales de Turno – Informe técnico y jurídico", author=AUTOR)
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


def _ejemplo(html):
    t = Table([[Paragraph(html, ParagraphStyle("ej", parent=st["p"], fontSize=8.6, leading=11))]], colWidths=[ANCHO])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")), ("LINEBEFORE", (0, 0), (0, -1), 4, NAVY),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                           ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return KeepTogether([Spacer(1, 3), t, Spacer(1, 6)])


def dos(img1, pie1, img2, pie2, alto=118 * mm):
    """Dos capturas lado a lado."""
    from reportlab.platypus import Image
    from PIL import Image as PI
    an = (ANCHO - 6 * mm) / 2
    celdas = []
    for ruta, pie in ((img1, pie1), (img2, pie2)):
        w, h = PI.open(ruta).size
        al = min(alto, an * h / w)
        im = Image(ruta, width=al * w / h, height=al)
        marco = Table([[im]])
        marco.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                   ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
        celdas.append([marco, Spacer(1, 3), Paragraph(pie, st["pc"])])
    t = Table([celdas], colWidths=[an + 3 * mm] * 2)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    return KeepTogether([t])


# ───────────────────────── Contenido ─────────────────────────
def armar():
    s = [NextPageTemplate("normal"), PageBreak()]

    # Nota de elevación
    s += [Paragraph(f"San Miguel de Tucumán, {HOY.day:02d} de {MESES[HOY.month - 1].capitalize()} de {HOY.year}.-",
                    ParagraphStyle("fr", parent=st["p"], alignment=2)), Spacer(1, 8),
          Paragraph("Al Señor<br/>Jefe de Policía de la Provincia<br/><u>Su Despacho:</u>", st["p"]), Spacer(1, 6),
          Paragraph("<b>Ref.:</b> Informe técnico y jurídico sobre la «Plataforma para Oficiales de Turno» y solicitud de autorización "
                    "de su prueba piloto.-", st["p"]), Spacer(1, 6),
          Paragraph("De mi mayor consideración:", st["p"]),
          Paragraph("Tenemos el agrado de dirigirnos a Usted, por la vía jerárquica correspondiente, a fin de elevar el presente informe sobre "
                    "la <b>Plataforma para Oficiales de Turno</b>, una herramienta desarrollada con personal propio que asiste al auxiliar de turno "
                    "en la documentación del procedimiento policial, desde el lugar del hecho y a través del teléfono celular.", st["carta"]),
          Paragraph("El Ministerio Público Fiscal ha digitalizado la recepción de denuncias y actuaciones mediante sus propias plataformas. "
                    "Esas herramientas, sin embargo, están pensadas desde la necesidad de la Justicia y <b>no contemplan el trabajo concreto del "
                    "oficial</b>: tomar nota en la calle, transcribir a modelos de Word, volver a cargar los mismos datos y redactar notas y actas "
                    "una por una. La plataforma viene a cubrir ese espacio, <b>sin reemplazar ni modificar</b> los sistemas oficiales del Ministerio "
                    "Público Fiscal, sino preparando la información para volcarla en ellos.", st["carta"]),
          Paragraph("Se trata de una <b>ayuda</b> para el personal, no de un procedimiento nuevo ni de un formato obligatorio: no altera las "
                    "formalidades que exige la ley procesal, no toma decisiones por el funcionario y no utiliza inteligencia artificial. "
                    "El oficial sigue siendo el autor y el responsable de cada acta, que revisa, firma y sella como hasta hoy.", st["carta"]),
          Paragraph("Su principal aporte es la <b>calidad de la documentación</b>: la ruta guiada recuerda, paso a paso, cada aspecto del "
                    "procedimiento que suele omitirse —la inspección ocular, el primer interventor, la hora de arribo de los equipos, el "
                    "destino de los vehículos, entre otros— e impide generar el acta mientras falte un dato esencial o haya datos que no "
                    "coincidan. Con ello, las actuaciones llegan al Ministerio Público Fiscal más completas y en condiciones de ser judicializadas.", st["carta"]),
          Paragraph("Los Comisarios Abogados que suscriben revisan que cada texto, cada plantilla y cada paso se encuadren en la normativa "
                    "vigente y en lo dispuesto por la justicia ordinaria. Por su carácter de piloto, la herramienta <b>se irá ajustando</b> a las "
                    "necesidades que planteen los auxiliares de turno durante la prueba.", st["carta"]),
          Paragraph("Por lo expuesto, se solicita autorización para llevar adelante la prueba piloto en los términos del presente informe, "
                    "quedando a disposición para realizar una demostración práctica.", st["carta"]),
          Paragraph("Sin otro particular, saludamos a Usted con atenta y distinguida consideración y respeto.-", st["carta"]),
          firma()]

    s += [PageBreak(), Paragraph("Índice", st["h1"]), Spacer(1, 6)]
    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle("t0", fontName="SB", fontSize=10, leading=13.5, textColor=NAVY),
                       ParagraphStyle("t1", fontName="S", fontSize=8.6, leading=10.6, leftIndent=14, textColor=TINTA)]
    s += [toc]

    # Resumen
    s += h1("Resumen ejecutivo")
    s += [Paragraph("<b>Qué es:</b> una herramienta web, de uso en el celular, que guía al auxiliar de turno durante el procedimiento y, con "
                    "los datos cargados una sola vez, prepara el acta para NOTeWEB, las notas, las actas de diligencia y la estadística.", st["lead"]),
          Spacer(1, 4),
          kpis([("1 vez", "se cargan los datos;<br/>se usan en todo"), ("9", "pasos guiados<br/>del procedimiento"),
                ("24", "puntos de control en un<br/>siniestro vial con lesionado"), ("0", "inteligencia artificial:<br/>plantillas fijas")]),
          Spacer(1, 8),
          tabla(["Punto", "Síntesis"], [
              ["<b>Naturaleza</b>", "Herramienta de <b>apoyo</b>. No es un sistema oficial del Ministerio Público Fiscal, no lo reemplaza ni se conecta "
                                    "con él: prepara el texto que el oficial revisa y vuelca en NOTeWEB."],
              ["<b>Problema</b>", "La plataforma del M.P.F. optimizó el trabajo de la Fiscalía, pero no contempló el de la Policía: triple carga (libreta, Word y NOTeWEB), partes informales por WhatsApp, horas de escritorio y actas incompletas que generan requerimientos."],
              ["<b>Aporte central</b>", "Calidad documental: el sistema recuerda cada aspecto del procedimiento, detecta datos que no coinciden y no "
                                        "genera el acta mientras falte lo esencial."],
              ["<b>Encuadre legal</b>", "El oficial es autor y responsable del acta; las plantillas son revisadas por los Comisarios Abogados del proyecto; "
                                        "se respetan las competencias de cada área (p. ej., las mediciones quedan para Criminalística)."],
              ["<b>Carácter</b>", "Prueba piloto, no estandarizada, <b>sujeta a modificaciones</b> según las necesidades de los auxiliares de turno."],
              ["<b>Meta</b>", "Mejorar entre un <b>200 % y un 300 %</b> la completitud de la documentación de los procedimientos, medida con la "
                              "misma lista de control antes y durante el piloto."],
              ["<b>Se solicita</b>", "Autorización para la prueba piloto en una comisaría, capacitación del personal y medición de resultados."]],
              [30 * mm, ANCHO - 30 * mm])]

    # 1. Naturaleza jurídica
    s += h1("1. Naturaleza y encuadre jurídico de la herramienta")
    s += [pj("La plataforma es un <b>instrumento de trabajo</b> del funcionario policial, equiparable a un modelo de acta o a una guía de "
             "procedimiento, pero dinámico: ordena la información, la redacta según plantillas revisadas y controla que no falte lo "
             "esencial. No crea actos procesales nuevos, no sustituye ninguna formalidad y no interviene en las decisiones que la ley "
             "reserva al Ministerio Público Fiscal o a los jueces."),
          pj("Trabaja de la misma manera en que hoy lo hace la Justicia con sus plataformas digitales —carga estructurada de datos y generación "
             "de documentos— pero desde la necesidad policial: el lugar del hecho, el celular, el tiempo escaso y la cantidad de piezas que "
             "debe producir el auxiliar de turno.")]
    s += h2("Marco normativo considerado")
    s += [tabla(["Norma", "Cómo se respeta"], [
        ["Código Procesal Penal de Tucumán (Ley N.º 8933)", "La Policía actúa como preventora y ejecuta las órdenes de fiscales y jueces. El sistema "
                                                            "registra lo dispuesto por la Unidad Fiscal y su cumplimiento; no decide medidas."],
        ["Ley Orgánica de la Policía de Tucumán (Ley N.º 3656)", "El oficial actúa dentro de sus funciones; el sistema no modifica atribuciones ni la "
                                                                 "cadena de mando."],
        ["Ley Nacional de Tránsito (Ley N.º 24.449)", "La terminología vial y la descripción del siniestro siguen sus definiciones; las pericias "
                                                     "quedan a cargo del área técnica."],
        ["Protección de Datos Personales (Ley N.º 25.326)", "Acceso con clave, base de datos propia, exportaciones anónimas y uso exclusivo para la "
                                                            "función policial."],
        ["Disposiciones del Ministerio Público Fiscal y de la justicia ordinaria", "Los textos se adecuan a los requerimientos de la Fiscalía; ante un "
                                                                                    "cambio de criterio, se ajusta la plantilla."]],
        [62 * mm, ANCHO - 62 * mm])]
    s += h2("Lo que la herramienta hace y lo que no hace")
    s += [tabla(["Hace", "No hace"], [
        ["Guía el procedimiento y recuerda cada paso.", "No reemplaza a NOTeWEB ni a ningún sistema del Ministerio Público Fiscal."],
        ["Redacta borradores con plantillas fijas y revisadas.", "No usa inteligencia artificial ni «inventa» texto."],
        ["Controla datos faltantes y contradicciones.", "No decide medidas ni califica jurídicamente el hecho."],
        ["Genera notas y actas en el formato de la dependencia.", "No firma: el oficial revisa, firma y sella cada pieza."],
        ["Deja constancia de lo dispuesto por la Fiscalía y de su cumplimiento.", "No realiza mediciones ni pericias: eso es de Criminalística."]],
        [ANCHO / 2, ANCHO / 2], VERDE),
          caja("<b>Encuadre legal permanente:</b> los Comisarios Abogados RODRÍGUEZ Julio y AIRA Celestina revisan cada plantilla, cada texto y "
               "cada paso, para que todo lo que produce el sistema se ajuste a la normativa vigente y a lo dispuesto por la justicia ordinaria.", "ok")]

    # 2. Problema
    s += h1("2. Análisis: cómo trabaja hoy el Ministerio Público Fiscal con la Policía")
    s += [pj("El Ministerio Público Fiscal dio un paso importante al implementar la denuncia digital y su plataforma de actuaciones (NOTeWEB). "
             "Ese avance ordenó la recepción de denuncias, unificó formatos y aceleró la llegada de la información a las Unidades Fiscales. "
             "Corresponde reconocerlo, y esta propuesta no lo discute: lo toma como punto de partida."),
          pj("Pero la plataforma fue diseñada desde la necesidad del Ministerio Público Fiscal, para optimizar <b>su</b> trabajo: recibir, registrar "
             "y dirigir la investigación. La Policía, como auxiliar de la Justicia, quedó del otro lado del mostrador: es quien produce la "
             "información, pero la herramienta <b>no contempla cómo la produce</b>. El resultado es que la Fiscalía trabaja informatizada y la "
             "Policía sigue trabajando de manera <b>precaria</b> en cuanto a sistematización: libreta, Word y transcripción."),
          tabla(["Lo que la plataforma del M.P.F. resuelve", "Lo que necesita la Policía y no está contemplado"], [
              ["Recepción y registro digital de la denuncia.", "Guía del procedimiento en el lugar del hecho, desde el celular."],
              ["Formato único para la Fiscalía.", "Captura de datos una sola vez, sin transcribir desde la libreta."],
              ["Comunicación de disposiciones del fiscal.", "Registro del cumplimiento de cada disposición, con horas y responsables."],
              ["Expediente digital para la investigación.", "Generación de las notas, actas de diligencia y croquis que la Policía debe producir."],
              ["Seguimiento desde la Unidad Fiscal.", "Control de completitud antes de elevar: qué falta, qué no coincide."],
              ["Información para la Justicia.", "Información para la Policía: estadística propia, carga por dependencia, mapa del delito."]],
              [ANCHO / 2, ANCHO / 2]),
          Spacer(1, 6),
          pj("Así, el oficial carga en la plataforma del M.P.F. un texto que antes tuvo que escribir en otro lado, con los mismos datos que "
             "después vuelve a tipear en cada nota. La brecha no está en la Fiscalía ni en la Policía, sino <b>entre ambas</b>: en el tramo que va "
             "desde el lugar del hecho hasta que la actuación queda cargada, que nadie informatizó."),
          caja("La consecuencia es doble. Para la Policía, horas de transcripción y actuaciones que vuelven con requerimientos. Para la Justicia, "
               "causas que llegan incompletas y demoran su investigación y su elevación a juicio. <b>Mejorar el tramo policial mejora también el "
               "resultado judicial.</b>", "ojo")]
    s += h2("Lo que se propone a partir de ese análisis")
    s += [pj("No se propone modificar la plataforma del Ministerio Público Fiscal ni reemplazarla, lo que excede a la Policía. Se propone "
             "informatizar <b>el tramo que le corresponde a la Policía</b>: desde la toma de conocimiento hasta la actuación lista para cargar en "
             "NOTeWEB y las piezas que la Fiscalía necesita para investigar y elevar a juicio."),
          tabla(["Hoy", "Con la plataforma para oficiales"], [
              ["Libreta, Word y NOTeWEB: triple carga.", "Una sola carga en el lugar del hecho; el texto para NOTeWEB sale listo."],
              ["Modelos de Word sueltos y desactualizados.", "Plantillas únicas, revisadas jurídicamente."],
              ["Lo que no se recuerda, no se documenta.", "La ruta pregunta cada aspecto del procedimiento."],
              ["Errores que aparecen cuando la Fiscalía los observa.", "Los errores se detectan y corrigen antes de generar el acta."],
              ["Notas redactadas una por una.", "Las notas salen con los datos ya cargados, original y duplicado."],
              ["La Policía no tiene datos propios de lo que produce.", "Estadística, mapa del delito y carga por dependencia, de la Policía."]],
              [ANCHO / 2, ANCHO / 2], ROJO),
          Spacer(1, 4),
          pj("La propuesta es, además, una <b>oportunidad de coordinación</b>: con el piloto en marcha, la Policía puede acercar al Ministerio "
             "Público Fiscal actuaciones más completas y uniformes, y acordar con él los formatos y los datos que facilitan la investigación y "
             "la elevación a juicio. Esa coordinación se plantea como parte del pedido a la Superioridad.")]

    s += h1("3. Cómo funciona")
    s += [imagen(I("dato_unico.png"), pie="Figura 1. Dato único: el oficial registra una vez y el sistema reutiliza los datos en cada pieza.")]
    s += h2("Ruta guiada del procedimiento")
    s += [pj("El procedimiento se recorre en nueve pasos, en el mismo orden en que ocurre en la realidad. Cada pantalla muestra pocas "
             "preguntas, con <b>botones grandes</b> para elegir, y guarda automáticamente lo cargado."),
          imagen(I("ruta9.png"), pie="Figura 2. Los nueve pasos de la ruta guiada y lo que se registra en cada uno.")]
    s += h2("Herramientas pensadas para la calle")
    s += [tabla(["Herramienta", "Para qué sirve"], [
        ["Lectura del DNI por foto", "Completa apellido, nombre, número y fecha de nacimiento leyendo el código del documento. Si no se puede leer, "
                                     "hay un botón para cargarlos a mano."],
        ["Dictado por voz", "El relato y las descripciones se dictan en lugar de escribirse."],
        ["Ubicación por GPS", "El lugar exacto del hecho se toma con un toque."],
        ["Botones en lugar de listas", "Las opciones quedan marcadas al tocarlas; se usan con una mano."],
        ["Modo sol y teclado numérico", "Alto contraste en la vía pública; teclado de números para horas, DNI y teléfonos."],
        ["Fotos del lugar", "Las fotografías tomadas con la cámara quedan adjuntas a la actuación."],
        ["Aplicación instalable", "Se agrega a la pantalla de inicio del celular (Android o iPhone), sin tienda de aplicaciones."]],
        [52 * mm, ANCHO - 52 * mm])]

    # 4. Calidad
    s += h1("4. Controles de calidad antes de generar el acta")
    s += [pj("El sistema verifica la información con una <b>lista de control</b> que distingue requisitos <b>obligatorios</b> (sin ellos no se genera "
             "el acta) y <b>complementarios</b> (se avisan, pero no bloquean). En un siniestro vial con un lesionado, la lista reúne 24 puntos "
             "de control. Además, cruza los datos entre sí para detectar contradicciones."),
          pj("Cada aviso es un botón: al tocarlo, el sistema lleva al paso y a la pregunta exacta para completar o corregir el dato.")]
    s += [tabla(["Lo que el sistema informó en el caso de prueba", "Tipo"], [
        ["Hora de arribo y lugar exacto", "Obligatorio"],
        ["Inspección ocular con posición final de vehículos", "Obligatorio"],
        ["Rastros relevados (o constancia de que no hay)", "Obligatorio"],
        ["Zona probable de impacto (dónde se concentran los restos)", "Obligatorio"],
        ["Calidad en que queda cada vehículo", "Obligatorio"],
        ["Quién intervino primero en el lugar", "Obligatorio"],
        ["La edad del conductor (35) no coincide con su fecha de nacimiento (42 años)", "Contradicción"]],
        [ANCHO - 34 * mm, 34 * mm], ROJO),
          Paragraph("Tabla generada por el sistema a partir de un caso ficticio cargado «de memoria», con las omisiones más habituales.", st["pc"]),
          Spacer(1, 6)]
    s += h2("Contradicciones que detecta")
    s += lista(["Una persona ubicada en la vereda y, a la vez, en un asiento del vehículo.",
                "Edad que no coincide con la fecha de nacimiento, o fecha inválida.",
                "Cantidad de vehículos del croquis distinta de la cargada.",
                "Horas de arribo de los equipos anteriores al aviso (contemplando el cambio de día).",
                "Disposiciones de la Fiscalía sin su cumplimiento registrado (por ejemplo, Criminalística sin hora de arribo)."])

    # 5. Inspección y croquis
    s += h1("5. Inspección ocular, croquis y competencias")
    s += [pj("La inspección ocular es una de las partes que con más frecuencia queda incompleta. La ruta pregunta la ubicación exacta del "
             "siniestro, las condiciones de luz, clima y calzada, la señalización, los rastros, la <b>zona probable de impacto</b> y la "
             "posición final de vehículos y personas."),
          pj("Se respetan las competencias de cada área: el sistema <b>no pide mediciones</b>, longitudes de frenado ni el punto exacto de impacto, "
             "que corresponden a la División Criminalística. El acta deja constancia expresa de ello."),
          caja("Texto que agrega el acta: «Queda a cargo de la División Criminalística la determinación técnica del punto de impacto, de las "
               "huellas y de las mediciones correspondientes.»", "tip"),
          imagen(I("croquis_ui.png"), ancho=ANCHO * 0.78, alto_max=150 * mm,
                 pie="Figura 3. Croquis ilustrativo armado con el editor del sistema (caso ficticio): calles, vehículo con giro, peatón, "
                     "zona probable de impacto, testigo, semáforos, sentido de circulación y leyenda automática.")]

    # 6. Documentos
    s += h1("6. Documentos que produce")
    s += [tabla(["Documento", "Características"], [
        ["Acta de intervención y comunicación", "Redactada con cohesión, en el estilo de las actas de la dependencia. El texto para NOTeWEB se copia "
                                                "desde «lo siguiente:», sin el preámbulo. Incluye el croquis en hoja aparte."],
        ["Notas según el delito", "Exámenes médicos, dosajes, informes, cadena de custodia, entre otras. En A4: original en la mitad superior y "
                                  "duplicado en la inferior, con espacio para el sello (sin bloque de firma, porque se firman con sello de tinta)."],
        ["Actas de diligencia", "Constatación de domicilio, averiguaciones, inspección ocular, notificación, secuestro, entrega y acta libre."],
        ["Parte a la superioridad", "Preliminar (con los datos «a confirmar» marcados) y ampliatorio desde el caso; llega a la bandeja de los jefes, con acuse de lectura."],
        ["Estadística y mapa del delito", "Lugar, fecha, hora, modalidad y medio salen del mismo procedimiento, sin volver a cargar planillas; los DNI se reemplazan por códigos."]],
        [48 * mm, ANCHO - 48 * mm]),
          Spacer(1, 6),
          dos(I("acta-1.png"), "Figura 4. Acta de intervención generada (caso ficticio).",
              I("nota-1.png"), "Figura 5. Nota en A4 con original y duplicado, lista para sellar.")]
    s += h2("Fin de las planillas de Excel")
    s += [pj("Hoy las comisarías, las jefaturas de zona y las Unidades Regionales arman la estadística y el mapa del delito con planillas de "
             "Excel que cada dependencia completa a mano, con criterios distintos y con datos muchas veces erróneos o incompletos, que se "
             "consolidan a mano en cada nivel y llegan con demora. Con la plataforma, el dato estadístico <b>no se carga: se produce</b> al "
             "documentar el procedimiento. La misma actuación que genera el acta alimenta el mapa del delito y la estadística de la comisaría, "
             "la zona, la regional y la provincia, con un solo criterio y sin duplicados."),
          caja("Cada nivel de conducción ve el mismo dato, al instante, con el detalle que necesite, y los nombres y DNI quedan reemplazados por "
               "códigos en todo lo que se exporta.", "ok")]
    s += h2("Partes a la superioridad: fin del informe por WhatsApp")
    s += [pj("Hoy toda la Policía informa los hechos a sus jefes por <b>WhatsApp</b>. Es un informe informal, que el oficial redacta mientras "
             "procede y que muchas veces envía como <b>adelanto</b> con datos que todavía no tiene confirmados. Ese mensaje no queda registrado "
             "en ningún sistema institucional, la información viaja por una aplicación personal sin resguardo, y si el hecho no es de relevancia "
             "el informe queda en la nada: nadie puede contar después cuántos hechos hubo, de qué tipo ni en qué dependencia."),
          tabla(["Parte por WhatsApp (hoy)", "Parte desde la plataforma"], [
              ["Mensaje libre, distinto en cada caso.", "Formato único: hecho, lugar, hora, cifras, síntesis, fiscalía e informante."],
              ["Datos sin confirmar que no se distinguen de los confirmados.", "Cada dato no confirmado se marca «a confirmar» y se amplía después."],
              ["El adelanto y la ampliación son mensajes sueltos.", "Parte preliminar y ampliatorio vinculados; el ampliatorio sale de los datos del caso."],
              ["Aplicación personal, sin resguardo institucional.", "Dentro del sistema, con usuario y clave; solo lo ven los jefes de esa dependencia."],
              ["No se sabe quién lo leyó.", "Acuse de lectura con nombre y hora."],
              ["Si el hecho no es relevante, se pierde.", "Todo parte queda registrado y se cuenta."],
              ["El jefe suma partes de memoria.", "Bandeja con conteos por tipo de hecho y dependencia, urgentes y preliminares sin ampliar."]],
              [ANCHO / 2, ANCHO / 2], ROJO),
          Spacer(1, 4),
          _ejemplo("<b>Ejemplo de parte preliminar generado por el sistema (caso ficticio)</b><br/><font face='Courier' size='8'>"
               "PARTE PRELIMINAR<br/>COMISARÍA SECCIONAL 1RA. · 2026-11-17 19:50<br/>HECHO: Siniestro vial<br/>"
               "FECHA Y HORA: 17/11/2026 · 19:45<br/>LUGAR: Av. Mate de Luna y Laprida<br/>"
               "CIFRAS: 1 víctima(s), 1 lesionado(s), 0 aprehendido(s)/demorado(s)<br/>"
               "SÍNTESIS: Atropello de peatón; una víctima consciente trasladada en ambulancia.<br/>FISCALÍA: A CONFIRMAR<br/>"
               "DATOS A CONFIRMAR: identidad de los involucrados; intervención fiscal. Se ampliará.<br/>"
               "INFORMA: OFICIAL AYUDANTE PÉREZ MARTÍN</font>"),
          pj("Para la conducción, el parte deja de ser un mensaje más en el teléfono y pasa a ser un <b>dato</b>: cuántos hechos hubo hoy, de qué "
             "tipo, en qué dependencias, cuántos con aprehendidos y cuántos adelantos todavía esperan su ampliación. La bandeja se actualiza sola.")]
    s += h2("Denuncias recibidas por NOTeWEB")
    s += [pj("Cuando la denuncia ya fue tomada, el oficial <b>sube el PDF</b> y el sistema muestra las notas que corresponden al delito. Solo pide "
             "un dato cuando una nota lo necesita (por ejemplo, la persona a examinar). Para continuar la investigación, genera las <b>actas de "
             "diligencia</b>."),
          imagen(I("diligencia-1.png"), ancho=ANCHO * 0.42, pie="Figura 6. Acta de constatación de domicilio generada (caso ficticio).")]
    s += h2("Arribo de equipos")
    s += [pj("En el paso de cumplimiento se registra la llegada de Criminalística, Policía Vial, Medicina Legal, Bomberos, SIE 107, grúa u otros: "
             "hora de arribo, móvil, a cargo de quién, tareas realizadas y hora de finalización. Si la Fiscalía dispuso la intervención de un "
             "equipo, el sistema controla que su arribo esté consignado.")]

    # 7. Calidad documental
    s += h1("7. Mejora de la calidad documental")
    s += [pj("El mayor beneficio de la plataforma no es solo el tiempo: es la <b>calidad y completitud</b> de lo que se documenta. Al recorrer la "
             "ruta, el oficial deja constancia de aspectos del procedimiento que, redactando de memoria y con apuro, suelen omitirse."),
          kpis([("200–300 %", "mejora esperada en la<br/>completitud documental"), ("100 %", "de los requisitos<br/>obligatorios antes del acta"),
                ("0", "contradicciones<br/>entre piezas")]),
          Spacer(1, 6),
          pj("<b>Cómo se mide.</b> Se toma la lista de control del sistema (24 puntos en un siniestro vial con lesionado) y se cuenta cuántos de esos "
             "puntos aparecen documentados en una muestra de actas anteriores al piloto y en las actas confeccionadas con la plataforma. "
             "Una mejora del 200 % al 300 % equivale, por ejemplo, a pasar de 6 a 8 puntos documentados por acta a entre 18 y 24."),
          caja("La meta se informará con <b>datos medidos</b> en la prueba piloto, sobre actas reales y con la misma lista de control, para que la "
               "Superioridad evalúe el resultado con evidencia.", "ojo")]
    s += h2("Lo que recibe el Ministerio Público Fiscal")
    s += lista(["Toma de conocimiento con vía, hora e informante.",
                "Hora de salida, móvil y personal; hora de arribo y lugar exacto.",
                "Actuación del primer interventor y del personal presente, identificado.",
                "Involucrados con sus datos completos, vehículos, seguro, licencia y daños.",
                "Inspección ocular completa, zona probable de impacto, posición final y croquis.",
                "Comunicación con la Fiscalía y cada disposición con su cumplimiento.",
                "Secuestros con número de protocolo de cadena de custodia.",
                "Arribo y labor de cada equipo, con sus horarios.",
                "Notas y diligencias con datos idénticos a los del acta."])
    s += [caja("Con todo ello, la causa llega en condiciones de ser <b>judicializada</b>: los elementos que la Fiscalía necesita para investigar y "
               "decidir están consignados desde el inicio, y se reducen los requerimientos por omisiones.", "ok")]

    # 8. Seguridad
    s += h1("8. Seguridad y protección de datos")
    s += [tabla(["Medida", "Detalle"], [
        ["Acceso", "Usuario y contraseña personales; contraseñas guardadas cifradas; bloqueo general con código de instalación."],
        ["Base de datos", "Propia, fuera de servicios de inteligencia artificial y de repositorios públicos."],
        ["Exportación y estadística", "Anónimas por defecto: códigos en lugar de DNI y nombres."],
        ["Piloto", "Hasta la autorización, se trabaja con datos ficticios. Las capturas de este informe corresponden a un caso inventado."],
        ["Escala institucional", "Se recomienda alojar el sistema en servidores de la Policía de Tucumán."]],
        [44 * mm, ANCHO - 44 * mm])]

    s += h2("Firma digital: el paso que completa el circuito")
    s += [pj("Hoy el acta y las notas que genera la plataforma se imprimen, se firman y se sellan con tinta. El paso siguiente es la "
             "<b>firma digital</b> (Ley N.º 25.506): da al documento digital la misma validez que "
             "la firma manuscrita, identifica sin duda al firmante y permite detectar cualquier alteración posterior. Se propone gestionar el "
             "certificado de firma digital de los oficiales y jefes que firman, con su <b>registro en DIMAC</b>, para que las notas, los partes "
             "a la superioridad y, en coordinación con el Ministerio Público Fiscal, las piezas que se elevan, puedan firmarse y enviarse sin papel."),
          caja("Con la firma digital, el procedimiento queda <b>digital de punta a punta</b>: se registra en el lugar, el documento sale solo, "
               "se firma con plena validez jurídica y llega a destino al instante. Mientras se implementa, el papel firmado y sellado sigue "
               "siendo válido.", "ok")]

    # 9. Carácter piloto
    s += h2("Carácter piloto y adaptación continua")
    s += [pj("La plataforma <b>no es un producto cerrado ni un formato estandarizado</b>. Durante la prueba piloto se modificará según las "
             "necesidades que surjan del trabajo diario del auxiliar de turno y de las observaciones de la Fiscalía."),
          P.pasos([(1, "El auxiliar de turno o la jefatura plantea una necesidad o una observación."),
                   (2, "Los Comisarios Abogados revisan su encuadre legal."),
                   (3, "Se implementa el cambio y se prueba con un caso ficticio."),
                   (4, "Se publica y llega a todos los teléfonos sin reinstalar.")])]

    # 10. Pedido
    s += h1("9. Prueba piloto y lo que se solicita")
    s += [tabla(["Indicador", "Cómo se mide"], [
        ["Completitud documental", "Puntos de la lista de control documentados por acta (antes y durante el piloto)."],
        ["Tiempo por procedimiento", "Desde el arribo hasta tener el acta y las notas listas."],
        ["Requerimientos de la Fiscalía", "Cantidad de actuaciones devueltas o ampliadas por omisiones."],
        ["Opinión de los usuarios", "Encuesta breve a los auxiliares de turno."]],
        [52 * mm, ANCHO - 52 * mm]),
          Spacer(1, 6),
          pj("Se solicita respetuosamente:"),
          P.pasos([(1, "<b>Autorizar la prueba piloto</b> en una comisaría, por un período definido y con seguimiento semanal."),
                   (2, "<b>Capacitar</b> a los auxiliares de turno y a los cadetes del I.E.S.P. mediante simulacros guionados."),
                   (3, "<b>Coordinar</b> con el Ministerio Público Fiscal la recepción de las actuaciones del piloto y sus observaciones."),
                   (4, "<b>Gestionar la firma digital</b> de los oficiales y jefes que firman, con el registro de sus certificados en DIMAC."),
                   (5, "<b>Realizar una demostración práctica</b> ante la Superioridad.")])]
    s += h2("Conclusión")
    s += [pj("La Plataforma para Oficiales de Turno es una ayuda concreta para quien está en la calle: reduce la transcripción, ordena el "
             "procedimiento y, sobre todo, <b>eleva la calidad de la documentación</b> que llega a la Justicia. Lo hace sin apartarse de la "
             "normativa vigente, respetando las competencias de cada área y dejando la autoría y la responsabilidad en el funcionario actuante. "
             "La prueba piloto permitirá medir sus resultados y ajustarla a las necesidades reales del personal."),
          firma()]
    return s


if __name__ == "__main__":
    doc = Doc(SALIDA)
    doc.multiBuild(armar())
    print(SALIDA)
