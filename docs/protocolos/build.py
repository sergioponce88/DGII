"""Propuesta: Repositorio Digital de Protocolos y Normativa Vigente de la Policía de Tucumán. PDF A4.

Uso (desde la raíz del repo):
    PDF=docs/Propuesta_Repositorio_Protocolos_Normativa.pdf python3 docs/protocolos/build.py
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
SALIDA = os.environ.get("PDF", "Propuesta_Repositorio_Protocolos_Normativa.pdf")
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
    c.drawCentredString(W / 2, H - 100 * mm, "POLICÍA DE TUCUMÁN")
    c.setFillColor(colors.white)
    c.setFont("SB", 13)
    c.drawCentredString(W / 2, H - 116 * mm, "PROPUESTA INSTITUCIONAL")
    c.setFont("SB", 24)
    c.drawCentredString(W / 2, H - 131 * mm, "REPOSITORIO DIGITAL DE")
    c.drawCentredString(W / 2, H - 142 * mm, "PROTOCOLOS Y NORMATIVA")
    c.setFont("S", 12.5)
    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.drawCentredString(W / 2, H - 154 * mm, "Un solo lugar, oficial y actualizado, donde todo el personal consulte los protocolos")
    c.drawCentredString(W / 2, H - 161 * mm, "y la normativa vigente que aplica la Policía de Tucumán")
    c.setFillColor(AMARILLO)
    c.roundRect(W / 2 - 62 * mm, H - 182 * mm, 124 * mm, 11 * mm, 5.5 * mm, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("SB", 10.5)
    c.drawCentredString(W / 2, H - 178.3 * mm, "Vigencia revisada jurídicamente · sin costo de licencias")
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
    c.drawString(M, H - 7.6 * mm, "REPOSITORIO DE PROTOCOLOS Y NORMATIVA · PROPUESTA")
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
                         title="Repositorio Digital de Protocolos y Normativa – Propuesta", author=AUTOR)
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

    s += [Paragraph(f"San Miguel de Tucumán, {HOY.day:02d} de {MESES[HOY.month - 1].capitalize()} de {HOY.year}.-",
                    ParagraphStyle("fr", parent=st["p"], alignment=2)), Spacer(1, 8),
          Paragraph("Al Señor<br/>Jefe de Policía de la Provincia<br/><u>Su Despacho:</u>", st["p"]), Spacer(1, 6),
          Paragraph("<b>Ref.:</b> Propuesta de creación de un Repositorio Digital de Protocolos y Normativa Vigente para el personal de la "
                    "Policía de Tucumán.-", st["p"]), Spacer(1, 6),
          Paragraph("De mi mayor consideración:", st["p"]),
          Paragraph("Tenemos el agrado de dirigirnos a Usted, por la vía jerárquica correspondiente, a fin de elevar a su consideración la "
                    "propuesta de creación de un <b>Repositorio Digital de Protocolos y Normativa Vigente</b>: un único lugar, oficial y "
                    "actualizado, donde todo el personal policial pueda consultar desde el celular los protocolos de actuación propios y los que "
                    "la Policía aplica por disposición del Ministerio Público Fiscal, el Poder Judicial, los Ministerios y otros organismos, junto "
                    "con las leyes, decretos y resoluciones que rigen su tarea.", st["carta"]),
          Paragraph("Hoy ese lugar <b>no existe</b> en la Provincia. Los protocolos circulan en copias, cadenas de mensajes y archivos sueltos; "
                    "cuando una ley se sanciona o se modifica, el personal no sabe a dónde recurrir para conocer el texto vigente. Esa ausencia "
                    "es una <b>falla a la hora de proceder</b>: el oficial actúa con la versión que tiene a mano, que puede estar desactualizada, "
                    "y la Institución queda expuesta a observaciones de la Justicia que podrían evitarse.", st["carta"]),
          Paragraph("La propuesta no crea normas ni interpreta la ley: <b>publica lo que ya rige</b>, con su fuente oficial, su fecha y un resumen "
                    "operativo revisado por los Comisarios Abogados que suscriben, quienes controlan la vigencia y el alcance de cada pieza. "
                    "Como en los demás sistemas de la propuesta general de informatización, cada consulta queda registrada como dato: qué se "
                    "busca, desde dónde y cuándo, lo que indica a la Institución qué necesita capacitar y qué protocolos deben revisarse.", st["carta"]),
          Paragraph("Quedamos a disposición para una demostración práctica. Sin otro particular, saludamos a Usted con atenta y distinguida "
                    "consideración y respeto.-", st["carta"]),
          firma()]

    s += [PageBreak(), Paragraph("Índice", st["h1"]), Spacer(1, 4)]
    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle("t0", fontName="SB", fontSize=10, leading=13, textColor=NAVY),
                       ParagraphStyle("t1", fontName="S", fontSize=8.6, leading=10.4, leftIndent=14, textColor=TINTA)]
    s += [toc]

    s += h1("Resumen ejecutivo")
    s += [Paragraph("<b>Qué se propone:</b> un repositorio web propio, de acceso exclusivo para el personal policial, con todos los protocolos y "
                    "la normativa que la Policía de Tucumán aplica, en su versión vigente, con fuente oficial, resumen operativo y aviso de cada "
                    "novedad, consultable desde el celular en el lugar del hecho.", st["lead"]),
          Spacer(1, 4),
          kpis([("1", "fuente oficial única<br/>para toda la fuerza"), ("Vigente", "cada norma con fecha,<br/>fuente y revisión jurídica"),
                ("Aviso", "cuando una norma es<br/>nueva o se modifica"), ("$0", "en licencias<br/>de software")]),
          Spacer(1, 8),
          tabla(["Punto", "Síntesis"], [
              ["<b>Problema</b>", "No existe en la Provincia un lugar donde consultar los protocolos y la normativa vigente. Circulan copias "
                                  "desactualizadas y, ante una ley nueva o modificada, el personal no sabe a dónde recurrir."],
              ["<b>Consecuencia</b>", "Procedimientos que se apartan del protocolo vigente sin saberlo, criterios distintos entre dependencias y "
                                      "observaciones de la Justicia evitables."],
              ["<b>Solución</b>", "Repositorio digital con buscador, fichas por norma, resumen operativo, versión vigente e históricas, avisos "
                                  "de novedades y vínculo con la capacitación."],
              ["<b>Garantía</b>", "Nada se publica sin revisión jurídica de vigencia y alcance. El repositorio informa; no interpreta ni crea normas."],
              ["<b>Datos</b>", "Qué se consulta, desde qué dependencia y cuándo: indica qué capacitar y qué protocolos revisar."],
              ["<b>Se solicita</b>", "Aval para su creación, designación de la autoridad responsable de la publicación y autorización para "
                                     "requerir a cada área los protocolos que aplica."]],
              [30 * mm, ANCHO - 30 * mm])]

    s += h1("1. Fundamentación")
    s += [pj("El personal policial aplica a diario normas de origen diverso: el Código Procesal Penal y sus reformas, la Ley Orgánica y el régimen "
             "de personal, leyes especiales (violencia de género, régimen penal juvenil, tránsito, estupefacientes), protocolos del Ministerio "
             "Público Fiscal, acordadas y resoluciones del Poder Judicial, protocolos de los Ministerios de Seguridad provincial y nacional, "
             "de Salud, de Desarrollo Social, y los propios de la Institución."),
          pj("Toda esa normativa existe y está publicada en boletines oficiales y sitios de distintos organismos. Pero <b>para el oficial que está "
             "en la calle no existe un lugar donde encontrarla</b> reunida, filtrada por lo que le corresponde aplicar y garantizada en su "
             "vigencia. Las consecuencias son conocidas:"),
          tabla(["Situación", "Efecto"], [
              ["El protocolo llega por copia o cadena de mensajes.", "Conviven versiones distintas; nadie sabe cuál es la vigente."],
              ["Una ley nueva o modificada se difunde de manera informal.", "Parte del personal sigue aplicando el texto anterior."],
              ["Cada dependencia conserva sus propios modelos.", "Criterios distintos ante el mismo hecho, según la comisaría."],
              ["No hay a quién consultar de inmediato.", "El oficial decide con lo que recuerda, o demora el procedimiento."],
              ["La Fiscalía o el Juzgado observan la actuación.", "Más requerimientos, más trabajo y exposición institucional."]],
              [ANCHO / 2, ANCHO / 2], ROJO)]
    s += h2("Lo que ya hace la Justicia y lo que falta")
    s += [pj("El Poder Judicial y el Ministerio Público Fiscal publican sus acordadas, resoluciones y protocolos en sus propios sitios, y la "
             "Legislatura y el Boletín Oficial publican las leyes. Esa publicidad cumple su fin jurídico, pero está pensada desde cada organismo, "
             "no desde la necesidad del policía: <b>nadie reúne, en un solo lugar y en lenguaje operativo, lo que la Policía debe aplicar</b>. "
             "El repositorio cubre ese vacío sin reemplazar ninguna publicación oficial: cada ficha remite a su fuente."),
          caja("Conocer la norma vigente es condición de un procedimiento válido. Poner la normativa al alcance del personal no es una mejora "
               "administrativa: es parte de la <b>garantía de legalidad</b> de la actuación policial.", "ojo")]

    s += h1("2. Qué es el repositorio")
    s += [imagen(I("circuito.png"), pie="Figura 1. Circuito de publicación y consulta: nada llega al personal sin revisión de vigencia.", alto_max=80 * mm),
          Spacer(1, 4),
          tabla(["Módulo", "Qué hace"], [
              ["<b>Acceso del personal</b>", "Ingreso con legajo o DNI validado contra la base del personal en actividad; solo personal policial."],
              ["<b>Ficha por norma</b>", "Título, organismo emisor, tipo (ley, decreto, acordada, resolución, protocolo), fecha, estado de vigencia, "
                                         "texto oficial, enlace a la fuente y <b>resumen operativo</b>: qué debe hacer el policía, paso a paso."],
              ["<b>Buscador</b>", "Por palabra, tema, organismo, tipo de hecho o situación («violencia de género», «menor demorado», «siniestro vial»)."],
              ["<b>Versiones</b>", "Una sola versión vigente por norma; las anteriores quedan como históricas, con fecha y norma que las reemplazó."],
              ["<b>Avisos</b>", "Cuando se publica una norma nueva o se modifica una existente, aviso al personal al que le corresponde, con "
                                "constancia de lectura en las que la Superioridad disponga."],
              ["<b>Carpetas por tema y por función</b>", "Lo que necesita el oficial de turno, el personal de calle, el instructor sumarial, el área "
                                                         "técnica; cada uno encuentra primero lo suyo."],
              ["<b>Vínculo con la capacitación</b>", "Cada norma puede enlazar a la disertación o curso de la Plataforma de Capacitación Virtual que la explica."],
              ["<b>Consulta sin conexión</b>", "Las fichas consultadas quedan disponibles en el celular para zonas sin señal."],
              ["<b>Tablero</b>", "Qué se consulta, cuánto, desde dónde y cuándo; normas con más consultas; novedades pendientes de lectura."]],
              [44 * mm, ANCHO - 44 * mm])]
    s += h2("Qué contiene")
    s += lista(["<b>Normativa general:</b> Código Procesal Penal (Ley N.º 8933) y reformas, Ley Orgánica (Ley N.º 3656), régimen de personal, Código Penal "
                "en lo que concierne a la actuación policial, leyes especiales nacionales y provinciales.",
                "<b>Protocolos de otros organismos que la Policía aplica:</b> Ministerio Público Fiscal, Poder Judicial (acordadas y reglamentos), "
                "Ministerios de Seguridad, Salud y Desarrollo Social, organismos de niñez y de género.",
                "<b>Protocolos propios:</b> órdenes del día, disposiciones de la Jefatura, instructivos de las Direcciones y Divisiones.",
                "<b>Modelos operativos:</b> actas, notas y formularios vigentes, integrados con los sistemas que ya los generan."])

    s += h1("3. Garantías: vigencia y encuadre jurídico")
    s += [tabla(["Aspecto", "Cómo se resuelve"], [
        ["Qué se publica", "Solo normas y protocolos oficiales, con enlace a su fuente. El repositorio no crea normas ni las interpreta: informa."],
        ["Quién publica", "La autoridad que la Jefatura designe. Cada ficha registra quién la cargó, quién la revisó y cuándo."],
        ["Revisión jurídica", "Los Comisarios Abogados del proyecto controlan vigencia, alcance y el resumen operativo antes de publicar."],
        ["Resúmenes operativos", "Son una guía de lectura; la ficha aclara que ante cualquier duda rige el texto oficial, que está a un toque."],
        ["Actualización", "Seguimiento del Boletín Oficial, de los sitios del Poder Judicial y del M.P.F., y de las comunicaciones que recibe la Policía."],
        ["Datos personales", "Solo se usan para validar el acceso (legajo o DNI). Las consultas se registran por dependencia para la estadística, "
                             "con resguardo de la Ley N.º 25.326."]],
        [40 * mm, ANCHO - 40 * mm]),
          caja("<b>Encuadre legal permanente:</b> nada se publica sin revisión; cada ficha remite a la fuente oficial; las versiones históricas "
               "se conservan para reconstruir qué norma regía en cada fecha.", "ok")]

    s += h1("4. Del registro al análisis")
    s += [pj("Cada consulta al repositorio es un dato. Con el tiempo, esos datos muestran a la Institución algo que hoy no puede ver:"),
          tabla(["Pregunta de gestión", "Hoy", "Con el repositorio"], [
              ["¿Qué protocolos consulta más el personal, y desde dónde?", "No se sabe.", "Ranking por tema, dependencia y horario."],
              ["¿Llegó la norma nueva a quienes deben aplicarla?", "Se supone.", "Avisos enviados y leídos, por dependencia."],
              ["¿Qué temas generan dudas y conviene capacitar?", "Se intuye.", "Consultas sin resultado y búsquedas repetidas."],
              ["¿Qué protocolos están desactualizados o duplicados?", "Se descubre al fallar.", "Revisión programada y alertas de vencimiento."],
              ["¿Qué normas aplica cada área y cuántas son?", "Nadie lo tiene consolidado.", "Inventario normativo de la Institución."]],
              [ANCHO * 0.44, ANCHO * 0.2, ANCHO * 0.36]),
          caja("El repositorio y la Plataforma de Capacitación Virtual se complementan: el primero muestra qué se consulta y qué genera dudas; "
               "la segunda convoca a la disertación que lo explica. Juntos cierran el circuito entre la norma y la práctica.", "tip")]

    s += h1("5. Tecnología, implementación e indicadores")
    s += [tabla(["Componente", "Solución"], [
        ["Plataforma", "Desarrollo propio con herramientas de uso libre, como los sistemas en funcionamiento; instalable en el celular."],
        ["Base de datos", "Propia, con respaldo; a escala, en servidores de la Policía."],
        ["Documentos", "PDF oficiales y fichas en texto, con buscador de contenido."],
        ["Costo", "Sin licencias; equipamiento existente y personal propio."]],
        [34 * mm, ANCHO - 34 * mm]),
          Spacer(1, 6),
          P.pasos([(1, "<b>Relevamiento (1 mes):</b> inventario de protocolos y normas que aplica cada área; fuentes y responsables."),
                   (2, "<b>Carga inicial revisada (2 meses):</b> normas de mayor uso primero (procedimiento penal, género, niñez, tránsito, personal)."),
                   (3, "<b>Piloto (2 meses):</b> acceso para dos dependencias y una Unidad Regional; avisos de novedades y medición de consultas."),
                   (4, "<b>Extensión:</b> toda la fuerza, carpetas por función, vínculo con la capacitación y tablero para la Superioridad.")]),
          Spacer(1, 6),
          tabla(["Indicador", "Cómo se mide"], [
              ["Cobertura normativa", "Normas y protocolos publicados respecto del inventario relevado."],
              ["Actualización", "Días entre la publicación oficial de una norma y su carga revisada."],
              ["Alcance de los avisos", "Personal que recibió y leyó cada novedad, por dependencia."],
              ["Uso", "Consultas por agente, dependencia y tema; consultas sin resultado."],
              ["Calidad de la actuación", "Observaciones de la Justicia por aplicación de normas no vigentes, antes y después."]],
              [48 * mm, ANCHO - 48 * mm])]

    s += h1("6. Lo que se solicita a la Superioridad")
    s += [P.pasos([(1, "<b>Aval institucional</b> para crear el Repositorio Digital de Protocolos y Normativa Vigente."),
                   (2, "<b>Designación de la autoridad responsable</b> de la publicación y de los referentes de cada área que aportarán sus protocolos."),
                   (3, "<b>Autorización</b> para requerir a Direcciones, Divisiones y Unidades Regionales los protocolos y modelos que aplican."),
                   (4, "<b>Autorización</b> para usar la base del personal en actividad con la finalidad exclusiva de validar el acceso."),
                   (5, "<b>Prueba piloto</b> en dos dependencias y una Unidad Regional, y difusión por la orden del día.")])]
    s += h2("Conclusión")
    s += [pj("Un procedimiento es válido cuando se ajusta a la norma vigente, y nadie puede ajustarse a lo que no conoce. Poner los protocolos "
             "y la normativa al alcance de cada policía, desde el celular, con vigencia garantizada y en lenguaje operativo, es una de las "
             "mejoras de mayor impacto y menor costo que la Institución puede encarar. Y, como en cada sistema de la propuesta general, el uso "
             "del repositorio producirá <b>datos</b> que hoy no existen: qué consulta el personal, qué dudas tiene y qué debe capacitarse, para "
             "seguir optimizando un rendimiento institucional que ya es reconocido."),
          caja("La propuesta queda <b>abierta a las observaciones de la Superioridad</b> y de las áreas que aporten sus protocolos.", "ok"),
          firma()]
    return s


if __name__ == "__main__":
    doc = Doc(SALIDA)
    doc.multiBuild(armar())
    print(SALIDA)
