"""Guion de dos páginas para la reunión con el Jefe y Subjefe de Policía (18/11/2026)."""
import importlib.util
import os
import sys

sys.path.insert(0, os.getcwd())
_spec = importlib.util.spec_from_file_location("prop", os.path.join(os.path.dirname(__file__), "build.py"))
PR = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(PR)
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.platypus import BaseDocTemplate, Frame, NextPageTemplate, PageTemplate, Paragraph, Spacer, Table, TableStyle  # noqa: E402

st, ANCHO, NAVY, AMARILLO = PR.st, PR.ANCHO, PR.NAVY, PR.AMARILLO
SALIDA = os.environ.get("PDF", "Guion_Reunion_Jefatura.pdf")
h = ParagraphStyle("gh", parent=st["p"], fontName="SB", fontSize=11.5, leading=14, textColor=NAVY, spaceBefore=7, spaceAfter=3)
t = ParagraphStyle("gt", parent=st["p"], fontSize=9.6, leading=12.6, alignment=4)
li = ParagraphStyle("gl", parent=t, leftIndent=11, bulletIndent=1, spaceAfter=2)
tit = ParagraphStyle("gti", parent=st["p"], fontName="SB", fontSize=16, leading=19, textColor=NAVY)
sub = ParagraphStyle("gsu", parent=st["p"], fontSize=9.5, textColor=PR.GRIS)


def L(items):
    return [Paragraph(x, li, bulletText="•") for x in items]


def caja(texto, color):
    tb = Table([[Paragraph(texto, t)]], colWidths=[ANCHO])
    tb.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), color), ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                            ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return tb


s = [Paragraph("Guion para la reunión con la Jefatura de Policía", tit),
     Paragraph("18 de noviembre de 2026 · Propuesta de informatización y transformación digital · Uso interno de los expositores", sub),
     Spacer(1, 6),
     caja("<b>Objetivo de la reunión:</b> obtener el aval para adoptar la gestión basada en datos como política institucional y la autorización "
          "para iniciar el análisis del flujo de trabajo en comisarías, jefaturas de zona, Unidades Regionales, departamentos, direcciones y oficinas.",
          colors.HexColor("#FEF3C7")),
     Paragraph("1. Apertura (2 minutos): reconocer, no corregir", h)]
s += L(["La Policía de Tucumán tiene hoy un rendimiento reconocido y en crecimiento. La propuesta <b>no viene a cambiar lo que funciona</b>: viene a "
        "registrarlo, medirlo y multiplicarlo.",
        "Frase guía: «Todo lo que la Institución hace bien hoy queda en libros y planillas que nadie puede sumar. Queremos que ese trabajo se vea.»"])
s += [Paragraph("2. La idea central (3 minutos): el dato como recurso de gestión", h)]
s += L(["Estamos en 2026: la Justicia tucumana terminó de digitalizar sus expedientes penales en papel; la Fiscalía recibe denuncias digitales. "
        "La Policía produce la <b>primera pieza</b> de cada causa y gran parte de la información de seguridad de la Provincia, y sigue en papel.",
        "Digitalizar no es «pasar el papel a la pantalla»: es registrar cada hecho <b>una sola vez, de manera uniforme y en el momento</b>, para que "
        "el mismo dato sirva al documento, al parte, a la estadística y a la decisión.",
        "Lo que hoy no se ve: horas del personal operativo en tareas administrativas, demanda por zona y horario, tiempos de respuesta a la "
        "Justicia, carga real de cada dependencia, actuaciones que vuelven con requerimientos. Con datos, <b>todo eso se mide</b>."])
s += [Paragraph("3. La evidencia (3 minutos): ya funciona, sin costo de licencias", h)]
s += L(["Seis sistemas propios: expedientes de la D.G.I.I., legajos académicos y de compañía, gabinete interdisciplinario del I.E.S.P., piloto para "
        "oficiales de turno y Medicina Legal en desarrollo. Hechos con personal propio y herramientas de uso libre.",
        "El piloto para oficiales de turno: carga única en el celular, acta para NOTeWEB, notas en A4, controles que detectan lo que falta. "
        "Meta: documentación de procedimientos entre un 200 % y un 300 % más completa, medida con la misma lista de control.",
        "Si hay tiempo y señal: <b>demostración en vivo</b> desde el celular (caso ficticio). Si no, mostrar las capturas del informe."])
s += [Paragraph("4. El método (3 minutos): análisis profundo, área por área", h)]
s += L(["No se propone un sistema único para todos. Cada área tiene su circuito, sus plazos y su lenguaje: por eso el <b>análisis del flujo de "
        "trabajo</b> es el corazón de la propuesta.",
        "Siete etapas: relevamiento, medición (línea de base), inventario de datos, diagnóstico, diseño validado con el personal y revisado "
        "jurídicamente, priorización y piloto medido.",
        "Invitación concreta: que cada sector —comisarías, zonas, regionales, departamentos, direcciones, oficinas— designe un referente y abra "
        "sus libros, planillas y modelos para el relevamiento. El análisis también muestra <b>lo que funciona bien y hay que preservar</b>."])
s += [Paragraph("5. Garantías (2 minutos): marco legal y seguridad", h)]
s += L(["Dos Comisarios Abogados revisan que cada sistema, documento y paso se encuadre en la normativa vigente y en lo dispuesto por la justicia "
        "ordinaria (CPP Ley 8933, Ley Orgánica 3656, Ley 25.326 de datos personales, firma digital Ley 7.291/25.506).",
        "Usuarios y claves, roles por jerarquía, registro de cada acción, base de datos propia, exportaciones anónimas, sin inteligencia artificial "
        "redactando actas. A escala institucional, servidores de la Policía."])
s += [Paragraph("6. El pedido (2 minutos): qué necesitamos de la Jefatura", h)]
s += L(["<b>Aval</b> para adoptar la gestión basada en datos como política de la Institución.",
        "<b>Referentes</b> por sector y una mesa de trabajo de informatización.",
        "<b>Autorización</b> para entrevistar y relevar el flujo de trabajo en las áreas que la Jefatura priorice.",
        "<b>Pilotos</b> medidos: una comisaría para el sistema de oficiales de turno y las áreas que se definan.",
        "Cuentas institucionales y, a mediano plazo, un servidor propio."])
s += [Paragraph("Preguntas probables y respuestas breves", h),
      PR.tabla(["Pregunta", "Respuesta"], [
          ["¿Cuánto cuesta?", "Sin licencias. Personal propio, equipamiento existente y planes gratuitos en la nube; a escala, un servidor institucional."],
          ["¿Esto reemplaza a NOTeWEB o a los sistemas del MPF?", "No. Los complementa: prepara la información para volcarla en ellos y genera lo que ellos no hacen."],
          ["¿Qué pasa si no hay señal?", "Funciona con datos móviles y bajo consumo; los documentos impresos siguen siendo válidos."],
          ["¿Y la seguridad de los datos?", "Claves cifradas, roles, auditoría, base propia y exportaciones anónimas. Revisión jurídica permanente."],
          ["¿Cómo sabemos si sirve?", "Cada piloto mide una línea de base y el resultado: tiempo por trámite, completitud, vencimientos, opinión del personal."],
          ["¿Qué pasa si se va quien lo hizo?", "Código documentado en repositorios, manuales, referentes por área y mesa de trabajo."],
          ["¿Esto se impone a las áreas?", "No. Nace del relevamiento con cada área y se ajusta con la opinión de sus usuarios."]],
          [52 * mm, ANCHO - 52 * mm]),
      Spacer(1, 6),
      caja("<b>Cierre:</b> «No pedimos que cambien cómo trabajan. Pedimos permiso para ir a cada sector, entender cómo trabaja y volver con datos "
           "que muestren lo que ya se hace y lo que se puede mejorar. La decisión de extenderlo será de la Jefatura, con esa evidencia en la mano.»",
           colors.HexColor("#DCFCE7"))]


class Doc(BaseDocTemplate):
    def __init__(self, ruta):
        super().__init__(ruta, pagesize=PR.B.A4, leftMargin=PR.M, rightMargin=PR.M, topMargin=18 * mm, bottomMargin=16 * mm,
                         title="Guion para la reunión con la Jefatura de Policía", author=PR.AUTOR)
        self.addPageTemplates([PageTemplate("n", [Frame(PR.M, 16 * mm, ANCHO, PR.H - 34 * mm, id="f")], onPage=PR.normal)])


Doc(SALIDA).build(s)
print(SALIDA)
