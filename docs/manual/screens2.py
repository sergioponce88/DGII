"""Maquetas nuevas del manual v2 (Mi trabajo, Tramitar, IA, Comisión, WhatsApp, hoja de ruta)."""
import os

from PIL import Image, ImageDraw

from mock import AMBAR, AZUL, BORDE, CARD, INK, INK2, INPUT, MUTED, NAR, PAL, ROJO, VERDE, WA, Pantalla, font, telefono

OUT = os.environ.get("OUT", "img")
os.makedirs(OUT, exist_ok=True)
P = lambda n: os.path.join(OUT, n)  # noqa: E731
DGII = "DIRECCIÓN GRAL. DE INSTITUTOS E INSTRUCCIÓN"
NARANJA = (245, 158, 11)


def seg(p, x, y, opciones, sel=0, w=None):
    """Control segmentado (botones unidos)."""
    xx = x
    for i, o in enumerate(opciones):
        ancho = w or int(p.d.textlength(o, font=font(14, "SemiBold"))) + 34
        p.d.rounded_rectangle([xx, y, xx + ancho, y + 42], 10, fill=(37, 99, 235) if i == sel else (30, 41, 59),
                              outline=(96, 165, 250) if i == sel else BORDE, width=2)
        p.text(xx + ancho // 2, y + 21, o, 14, "SemiBold", INK if i == sel else INK2, anchor="mm")
        xx += ancho + 6
    return y + 58


def ruta(p, x, y, pasos):
    xx = x
    for i, s in enumerate(pasos):
        w = int(p.d.textlength(s, font=font(13, "Bold"))) + 26
        p.d.rounded_rectangle([xx, y, xx + w, y + 30], 15, fill=(23, 37, 84), outline=(96, 165, 250))
        p.text(xx + w // 2, y + 15, s, 13, "Bold", INK, anchor="mm")
        xx += w
        if i < len(pasos) - 1:
            p.text(xx + 14, y + 15, "→", 16, "Bold", MUTED, anchor="mm")
            xx += 28
    return y + 46


def tarjeta(p, x, y, w, nro, tipo, chips, asunto, acento=PAL[0], h=150):
    p.card(x, y, w, h, acento)
    p.text(x + 26, y + 16, nro, 24, "ExtraBold")
    p.text(x + 26 + p.d.textlength(nro, font=font(24, "ExtraBold")) + 14, y + 26, "AÑO 2026 · LIBRO 1", 11, "SemiBold", MUTED)
    xx = p.chip(x + 26, y + 56, tipo, (96, 165, 250))
    for s, c in chips:
        xx = p.chip(xx, y + 56, s, c)
    p.text(x + 26, y + 100, asunto, 13, "Regular", INK2)
    return y + h + 12


def mi_trabajo():
    p = Pantalla(1600, 940, activo="Mi trabajo", titulo="Mi trabajo", sub="Bandeja del oficial: tramitar y despachar")
    x = 340
    y = ruta(p, x, p.y - 8, ["Para tramitar", "Nota o trámite", "Despacho", "Comisionista"])
    p.marca(1000, y - 30, 1)
    p.d.rounded_rectangle([x, y, 1560, y + 46], 10, fill=(15, 23, 42), outline=BORDE)
    p.text(x + 18, y + 23, "›  Llegó un expediente (buscar · reingreso · nuevo)", 15, "SemiBold", INK2, anchor="lm")
    p.marca(1540, y + 23, 2)
    y += 64
    y = p.kpis(x, y, [("Para tramitar", 7, "1 vencido · 2 urgentes", AMBAR), ("Para despachar", 2, "tramitados que siguen aquí", PAL[3]),
                      ("Con el comisionista", 3, "esperando entrega", PAL[6])], 1220)
    y = p.tabs(x, y, ["Para tramitar (7)", "Para despachar (2)", "Con el comisionista (3)"], 0)
    p.marca(330, y - 40, 3)
    p.text(x, y - 4, "Ordenados: vencidos, urgentes y más días esperando primero.", 13, "Regular", MUTED)
    y += 22
    y = tarjeta(p, x, y, 1220, "N° 546 / F° 120 / O° 2", "SUMARIO ADMINISTRATIVO",
                [("EN TRÁMITE", PAL[0]), ("VENCIDO hace 2 d", ROJO), ("URGENTE", NAR), ("D.G.I.I.", PAL[6])],
                "INFORMACIÓN SUMARIA – CADETE DE II AÑO · Origen: JEFATURA DE POLICÍA · 27 días sin moverse", ROJO)
    p.boton(x, y, 600, "Nota en Word", "sec")
    p.boton(x + 620, y, 600, "Tramitar y despachar")
    p.marca(x + 30, y + 24, 4)
    p.marca(x + 1200, y + 24, 5)
    y += 70
    y = tarjeta(p, x, y, 1220, "N° 584 / F° 56 / O° 6", "AUTORIZACIÓN A EVENTO DEPORTIVO",
                [("EN TRÁMITE", PAL[0]), ("PENDIENTE DE TRÁMITE", AMBAR), ("D.G.I.I.", PAL[6])],
                "COMPETENCIA DE LA PISTA DE OBSTÁCULOS · Origen: ESCUELA DE SUBOFICIALES Y AGENTES · 0 días", PAL[0])
    p.boton(x, y, 600, "Nota en Word", "sec")
    p.boton(x + 620, y, 600, "Tramitar y despachar")
    return p.guardar(P("20_mi_trabajo.png"))


def mesa():
    p = Pantalla(1600, 1060, activo="Mi trabajo", titulo="Mi trabajo", sub="Mesa de entradas: recibir y registrar")
    x = 340
    y = ruta(p, x, p.y - 8, ["Llega", "Lo busco", "Reingreso o alta", "Queda para el oficial"])
    y = p.seccion(x, y, "Llegó un expediente", 1220)
    y = p.campo(x, y, 1220, "Busque por N° (de la Dirección o de origen) o por asunto", "584")
    p.marca(1580, y - 40, 1)
    y = tarjeta(p, x, y, 1220, "N° 584 / F° 56 / O° 6", "AUTORIZACIÓN A EVENTO DEPORTIVO",
                [("TRAMITADO", PAL[2]), ("D.G.I.I.", PAL[6]), ("JEFATURA DE POLICÍA", PAL[7])],
                "COMPETENCIA DE LA PISTA DE OBSTÁCULOS · Último movimiento: SALIDA a JEFATURA DE POLICÍA", PAL[7])
    p.boton(x, y, 1220, "Volvió: registrar reingreso de 584/56/6", "sec")
    p.marca(1580, y + 24, 2)
    y += 70
    p.card(x, y, 1220, 300)
    p.campo(x + 24, y + 20, 570, "Vuelve desde", "JEFATURA DE POLICÍA", "select")
    p.campo(x + 620, y + 20, 570, "Vuelve con (despacho / resolución)", "RESOLUCIÓN", "select")
    p.marca(1210, y + 66, 3)
    p.campo(x + 24, y + 108, 570, "Quién lo trae", "Escriba para buscar…", "select", placeholder=True)
    p.campo(x + 620, y + 108, 570, "Quién lo recibe", "SARGENTO PÉREZ ANA", "select")
    p.marca(1210, y + 154, 4)
    p.boton(x + 24, y + 210, 360, "Registrar reingreso")
    y += 320
    p.boton(x, y, 420, "No es ninguno: cargar como nuevo", "sec")
    p.marca(x + 440, y + 24, 5)
    return p.guardar(P("21_mesa.png"))


def libro_elegir():
    p = Pantalla(1600, 560, activo="Nuevo Expediente", titulo="Nuevo Expediente", sub="Registro en el libro · N° EXP / FOLIO / ORDEN")
    x = 340
    p.text(x, p.y, "¿A qué libro corresponde este expediente?", 17, "Bold")
    y = p.y + 40
    for i, (s, c, d) in enumerate([("D.G.I.I.", PAL[0], "Dirección General de Institutos e Instrucción"),
                                   ("I.E.S.P.", PAL[2], "Instituto de Enseñanza Superior de Policía")]):
        xx = x + i * 620
        p.card(xx, y, 600, 120, c)
        p.d.ellipse([xx + 30, y + 30, xx + 54, y + 54], outline=c, width=3)
        if i == 0:
            p.d.ellipse([xx + 36, y + 36, xx + 48, y + 48], fill=c)
        p.text(xx + 72, y + 30, s, 22, "ExtraBold")
        p.text(xx + 72, y + 70, d, 14, "Regular", INK2)
    p.marca(x + 590, y + 20, 1)
    p.marca(x + 1210, y + 20, 2)
    p.alerta(x, y + 150, 1220, "Cada libro tiene su propia numeración", "Mismo personal, dos libros: el sistema propone N°, folio y orden del libro elegido.", AZUL, "i")
    return p.guardar(P("22_libro_elegir.png"))


def tramitar_despachar():
    p = Pantalla(1600, 1000, activo="Mi trabajo", titulo="Tramitar y despachar", sub="Todo en un solo paso")
    x = 340
    p.alerta(x, p.y, 1220, "PENDIENTE DE TRÁMITE", "Asiente lo realizado y a dónde va, todo en un solo paso.", AMBAR, "…")
    y = p.y + 90
    p.card(x, y, 1220, 640)
    p.text(x + 24, y + 20, "Tramitar y despachar", 18, "Bold")
    p.campo(x + 24, y + 60, 570, "¿Qué se hizo?", "NOTA ELEVADA", "select")
    p.campo(x + 620, y + 60, 570, "Tramitado por", "OFICIAL AUXILIAR ALVAREZ ÁNGEL ADRIÁN", "select")
    p.marca(1210, y + 106, 1)
    p.campo(x + 24, y + 150, 1166, "Detalle (N° de nota, providencia, a quién se respondió…)", "Elevación solicitando autorización al Sr. Jefe de Policía")
    p.text(x + 24, y + 240, "›  Otra fecha u hora (si no fue ahora)", 14, "SemiBold", MUTED)
    p.text(x + 24, y + 280, "¿Y después?", 14, "SemiBold", INK2)
    seg(p, x + 24, y + 306, ["Lo lleva el comisionista", "Sale ahora (lo entrego yo)", "Queda en la Dirección"], 0)
    p.marca(1210, y + 326, 2)
    p.campo(x + 24, y + 370, 570, "Destino →", "JEFATURA DE POLICÍA", "select")
    p.campo(x + 620, y + 370, 570, "Despacho con el que sale", "A CONSIDERACIÓN DEL COMANDO SUPERIOR", "select")
    p.campo(x + 24, y + 458, 1166, "Indicaciones para el comisionista (opcional)", "Entregar en mano al Secretario", placeholder=True)
    p.marca(1210, y + 504, 3)
    p.boton(x + 24, y + 560, 1166, "Tramitar y despachar")
    p.marca(1210, y + 584, 4)
    return p.guardar(P("23_tramitar_despachar.png"))


def tramitar_word():
    p = Pantalla(1600, 1100, activo="Tramitar", titulo="Tramitar", sub="Notas, pases, elevaciones, oficios y actuaciones en Word")
    x = 340
    p.campo(x, p.y, 1220, "Expediente a tramitar", "[D.G.I.I.] 584/56/6 · 2026 · AUTORIZACIÓN A EVENTO DEPORTIVO", "select")
    y = p.y + 92
    p.marca(1580, y - 40, 1)
    p.text(x, y, "1  ¿Qué va a hacer?", 16, "Bold", (147, 197, 253))
    seg(p, x, y + 30, ["Notas y pases", "Notificación", "Proyecto", "Oficios judiciales", "Actuaciones / Sumario"], 0)
    y += 100
    for i, (t, d) in enumerate([("Elevación", "A Jefatura / Subjefatura con opinión"), ("Pase a División / Escuela", "Remito para informe o cumplimiento"),
                                ("Pase a Relaciones", "Formación, cursos, Compañía"), ("Devolver al origen", "Cumplido, vuelve a quien lo inició")]):
        xx = x + i * 308
        sel = i == 0
        p.d.rounded_rectangle([xx, y, xx + 296, y + 96], 12, fill=(23, 37, 84) if sel else CARD, outline=(96, 165, 250) if sel else BORDE, width=2)
        p.text(xx + 18, y + 22, t, 15, "Bold")
        p.text(xx + 18, y + 56, d, 12, "Regular", INK2)
    p.marca(x + 290, y + 10, 2)
    y += 120
    p.text(x, y, "3  Complete los datos · a la derecha ve cómo queda la nota", 16, "Bold", (147, 197, 253))
    y += 34
    p.d.rounded_rectangle([x, y, x + 600, y + 46], 10, fill=(15, 23, 42), outline=(250, 204, 21))
    p.text(x + 18, y + 23, "›  Completar con IA · fotos del expediente e instrucciones", 14, "SemiBold", INK, anchor="lm")
    p.marca(x + 620, y + 23, 3)
    yy = y + 64
    yy = p.campo(x, yy, 600, "Elevar a", "Al Señor Jefe de Policía de la Provincia", "select")
    yy = p.campo(x, yy, 600, "Opinión de la Dirección", "FAVORABLE", "select")
    p.campo(x, yy, 600, "Cuerpo de la nota", "…solicitando autorización para la competencia…", h=120)
    p.marca(x + 620, yy + 80, 4)
    # vista previa
    px = x + 640
    p.d.rounded_rectangle([px, y, px + 580, y + 470], 10, fill=(255, 255, 255))
    try:
        lg = Image.open("assets/logo_policia.png").convert("RGBA")
        lg.thumbnail((50, 56))
        p.im.paste(lg, (px + 24, y + 18), lg)
        lg2 = Image.open("assets/logo_dgii.png").convert("RGBA")
        lg2.thumbnail((50, 56))
        p.im.paste(lg2, (px + 506, y + 18), lg2)
    except OSError:
        pass
    neg = (17, 24, 39)
    p.text(px + 290, y + 34, "POLICÍA DE TUCUMÁN", 13, "Bold", neg, anchor="mm")
    p.text(px + 290, y + 54, "DIRECCIÓN GENERAL DE INSTITUTOS E INSTRUCCIÓN", 10, "SemiBold", neg, anchor="mm")
    p.text(px + 556, y + 100, "San Miguel de Tucumán, 23 de octubre de 2026.-", 10, "Regular", neg, anchor="ra")
    p.text(px + 30, y + 130, "AL SEÑOR JEFE DE POLICÍA DE LA PROVINCIA", 10, "Bold", neg)
    p.text(px + 30, y + 148, "SU DESPACHO:", 10, "Bold", neg)
    for i in range(9):
        p.d.line([px + 30 + (60 if i == 0 else 0), y + 190 + i * 22, px + 550 - (120 if i == 8 else 0), y + 190 + i * 22], fill=(156, 163, 175), width=6)
    p.text(px + 290, y + 446, "Vista previa", 11, "SemiBold", (100, 116, 139), anchor="mm")
    p.marca(px + 560, y + 20, 5)
    y += 490
    p.text(x, y, "4  Revisar y generar el Word", 16, "Bold", (147, 197, 253))
    p.boton(x, y + 34, 600, "Revisar redacción", "sec")
    p.boton(x + 620, y + 34, 600, "Generar Word")
    p.marca(x + 30, y + 58, 6)
    p.marca(x + 1200, y + 58, 7)
    return p.guardar(P("24_tramitar_word.png"))


def ia():
    p = Pantalla(1600, 800, activo="Tramitar", titulo="Completar con IA", sub="Fotos del expediente e instrucciones")
    x = 340
    p.text(x, p.y, "Saque fotos de las fojas (o suba el PDF) y, si quiere, indíquele cómo redactarlo.", 14, "Regular", INK2)
    y = p.y + 34
    p.d.rounded_rectangle([x, y, x + 1220, y + 110], 12, fill=INPUT, outline=BORDE, width=2)
    p.text(x + 610, y + 38, "Arrastre o elija fotos / PDF  ·  en el celular: Cámara", 15, "SemiBold", INK2, anchor="mm")
    for i in range(3):
        p.d.rounded_rectangle([x + 470 + i * 100, y + 62, x + 550 + i * 100, y + 100], 6, fill=(51, 65, 85))
        p.text(x + 510 + i * 100, y + 81, f"foja {i + 1}", 11, "SemiBold", INK, anchor="mm")
    p.marca(1580, y + 55, 1)
    y += 134
    p.text(x, y, "Instrucciones para la IA (opcional · cómo quiere que lo redacte)", 15, "Bold")
    y += 32
    xx = x
    for i, s in enumerate(["Opinión FAVORABLE", "Opinión DESFAVORABLE", "A consideración del Comando Superior", "Breve (2–3 líneas)",
                           "Detallado", "Mencionar las fojas", "Pedir que se notifique al causante"]):
        w = int(p.d.textlength(s, font=font(13, "SemiBold"))) + 28
        if xx + w > x + 1220:
            xx, y = x, y + 44
        sel = i in (0, 3)
        p.d.rounded_rectangle([xx, y, xx + w, y + 34], 17, fill=(29, 78, 216) if sel else (30, 41, 59), outline=(96, 165, 250) if sel else BORDE, width=2)
        p.text(xx + w // 2, y + 17, s, 13, "SemiBold", INK if sel else INK2, anchor="mm")
        xx += w + 8
    p.marca(1580, y - 10, 2)
    y += 52
    p.d.rounded_rectangle([x, y, x + 1220, y + 96], 10, fill=INPUT, outline=BORDE, width=2)
    p.text(x + 16, y + 18, "Destacar que la Escuela cumple con el cronograma y que no afecta el servicio;", 14, "Medium", INK)
    p.text(x + 16, y + 44, "pedir que se informe el resultado de la competencia.", 14, "Medium", INK)
    p.marca(1580, y + 48, 3)
    y += 116
    p.boton(x, y, 1220, "Leer fojas y proponer el texto")
    p.marca(1580, y + 24, 4)
    y += 70
    p.card(x, y, 1220, 140, VERDE)
    p.text(x + 24, y + 18, "Cuerpo de la nota — propuesta", 14, "Bold")
    p.text(x + 24, y + 48, "…que la Escuela de Suboficiales y Agentes cumple con el cronograma previsto y que la actividad no afecta", 13, "Regular", INK2)
    p.text(x + 24, y + 72, "el normal desarrollo del servicio, por lo que esta Dirección emite opinión FAVORABLE…", 13, "Regular", INK2)
    p.boton(x + 24, y + 96, 400, "Usar estos textos en el formulario", h=36)
    p.marca(1580, y + 112, 5)
    return p.guardar(P("25_ia.png"))


def resultado():
    p = Pantalla(1600, 760, activo="Tramitar", titulo="Tramitar", sub="5 · Imprimir y asentar")
    x = 340
    y = p.y
    p.boton(x, y, 1220, "Descargar Word para imprimir")
    p.marca(1580, y + 24, 1)
    y += 70
    p.d.rounded_rectangle([x, y, x + 1220, y + 90], 12, fill=(6, 46, 30), outline=(34, 197, 94), width=2)
    p.text(x + 20, y + 20, "Quedó TRAMITADO por OFICIAL AUXILIAR ALVAREZ ÁNGEL ADRIÁN y encargado al comisionista → JEFATURA DE POLICÍA.", 14, "Bold")
    p.text(x + 20, y + 52, "Ya le aparece en «Para entregar». No hace falta cargarlo en Trámite ni en Movimiento.", 13, "Regular", INK2)
    p.marca(1580, y + 45, 2)
    y += 110
    p.d.rounded_rectangle([x, y, x + 1220, y + 46], 10, fill=(15, 23, 42), outline=BORDE)
    p.text(x + 18, y + 23, "›  Cambiar: otro destino, lo entrego yo ahora, o queda aquí", 15, "SemiBold", INK2, anchor="lm")
    p.marca(1580, y + 23, 3)
    y += 64
    p.boton(x, y, 600, "Deshacer (no estaba terminado)", "sec")
    p.boton(x + 620, y, 600, "Listo: volver a Mi trabajo (siguiente)", "sec")
    p.marca(x + 30, y + 24, 4)
    p.marca(x + 1200, y + 24, 5)
    return p.guardar(P("26_resultado.png"))


def comision():
    p = Pantalla(520, 1100, movil=True, activo="Comisión (entregas)")
    y = p.y
    p.text(24, y, "Comisión", 26, "ExtraBold")
    p.text(24, y + 40, "ENTREGA DE EXPEDIENTES TRAMITADOS", 10, "SemiBold", MUTED)
    y += 74
    for i, (l, v, c) in enumerate([("PARA ENTREGAR", 3, AMBAR), ("ENTREGADOS HOY", 2, VERDE)]):
        xx = 24 + i * 242
        p.card(xx, y, 230, 92, c)
        p.text(xx + 18, y + 14, l, 11, "Bold", MUTED)
        p.text(xx + 18, y + 34, str(v), 30, "ExtraBold")
    p.marca(470, y + 46, 1)
    y += 112
    p.card(24, y, 472, 168, NARANJA)
    p.text(46, y + 16, "584/56/6", 22, "ExtraBold")
    p.text(170, y + 24, "D.G.I.I. · EVENTO DEPORTIVO", 11, "SemiBold", MUTED)
    p.text(46, y + 56, "→ JEFATURA DE POLICÍA", 15, "Bold")
    p.text(46, y + 84, "A CONSIDERACIÓN DEL COMANDO SUPERIOR", 12, "Regular", INK2)
    p.text(46, y + 108, "Encargó: OF. AUX. ALVAREZ · 6 fojas", 12, "Regular", MUTED)
    p.text(46, y + 132, "Entregar en mano al Secretario", 12, "SemiBold", (253, 230, 138))
    y += 180
    p.boton(24, y, 472, "Entregar 584/56/6")
    p.marca(470, y + 24, 2)
    y += 76
    p.text(24, y, "Formulario de entrega", 15, "Bold", (147, 197, 253))
    y += 30
    y = p.campo(24, y, 472, "Destino →", "JEFATURA DE POLICÍA", "select")
    y = p.campo(24, y, 472, "Quién lo lleva / entrega", "AGENTE ESYA ROMERO", "select")
    y = p.campo(24, y, 472, "Quién lo recibe *", "SGTO. PÉREZ (MESA DE ENTRADAS)", "select")
    p.marca(470, y - 40, 3)
    y = p.boton(24, y, 472, "Registrar entrega")
    p.marca(470, y - 40, 4)
    p.boton(24, y, 472, "Avisar por WhatsApp", "wa")
    p.marca(470, y + 24, 5)
    return telefono(p, P("27_comision.png"))


def whatsapp():
    p = Pantalla(1600, 860, activo="Actividades y Personal", titulo="Actividades y Personal", sub="Qué está pasando")
    x = 340
    p.boton(x, p.y, 460, "Informar qué está pasando por WhatsApp", "wa")
    p.marca(x + 480, p.y + 24, 1)
    y = p.y + 64
    p.d.rounded_rectangle([x, y, x + 760, y + 640], 14, fill=CARD, outline=(96, 165, 250), width=2)
    p.campo(x + 24, y + 20, 712, "Enviar a", "Elegir contacto en WhatsApp", "select")
    p.marca(x + 750, y + 66, 2)
    p.text(x + 24, y + 110, "Mensaje (puede editarlo)", 14, "SemiBold", INK2)
    p.d.rounded_rectangle([x + 24, y + 136, x + 736, y + 540], 10, fill=INPUT, outline=BORDE, width=2)
    lineas = ["*D.G.I.I. – Actividades: qué está pasando*", "23/10/2026 18:01", "", "*En desarrollo hoy (2)*",
              "• *CURSO DE TIRO TÁCTICO* (CURSO) – 15/10 al 25/10 · CITTU · 12", "• *JORNADA DE GÉNERO* (DISERTACIÓN) – 23/10 · 09:30",
              "", "*Próximos 7 días (1)*", "• *ACTO ANIVERSARIO* (ACTO) – 28/10 · Plaza de armas · 60", "",
              "*Terminaron esta semana (1)*", "• *TORNEO DE FÚTBOL* (EVENTO DEPORTIVO) – 20/10"]
    for i, l in enumerate(lineas):
        p.text(x + 42, y + 152 + i * 30, l, 13, "Medium", INK if l.startswith("*") else INK2)
    p.marca(x + 750, y + 330, 3)
    p.boton(x + 24, y + 560, 712, "Abrir WhatsApp", "wa")
    p.marca(x + 750, y + 584, 4)
    # globo de whatsapp
    gx = x + 800
    p.d.rounded_rectangle([gx, y + 120, gx + 420, y + 480], 18, fill=(11, 20, 26), outline=(37, 211, 102), width=3)
    p.d.rounded_rectangle([gx + 20, y + 150, gx + 400, y + 440], 12, fill=(0, 92, 75))
    for i, l in enumerate(["D.G.I.I. – Actividades", "En desarrollo hoy (2)", "• Curso de tiro táctico", "• Jornada de género",
                           "Próximos 7 días (1)", "• Acto aniversario", "…"]):
        p.text(gx + 40, y + 172 + i * 36, l, 14, "Bold" if i in (0, 1, 4) else "Regular", INK)
    p.text(gx + 210, y + 500, "Así le llega al grupo", 13, "SemiBold", MUTED, anchor="mm")
    return p.guardar(P("28_whatsapp.png"))


def hoja_ruta():
    p = Pantalla(1600, 820, activo="Ficha de Expediente", titulo="Ficha de Expediente", sub="Hoja de ruta")
    x = 340
    y = p.tabs(x, p.y, ["Trámite", "PDF", "Hoja de ruta", "Registrar movimiento", "Curso y personal", "Alertas", "Editar"], 2)
    items = [(NARANJA, "PARA ENTREGAR · con el comisionista → JEFATURA DE POLICÍA",
              "23/10/2026 22:56 · pendiente: al entregarlo se asienta la SALIDA con quién lo recibe",
              "Encargó: OFICIAL AUXILIAR ALVAREZ · Despacho: A CONSIDERACIÓN DEL COMANDO SUPERIOR"),
             (PAL[0], "TRAMITADO · en DIRECCIÓN GENERAL DE INSTITUTOS E INSTRUCCIÓN", "23/10/2026 22:56 · registró OFICIAL AUXILIAR ALVAREZ",
              "Se hizo: NOTA ELEVADA · Tramitó: OFICIAL AUXILIAR ALVAREZ · Elevación → Jefe de Policía de la Provincia"),
             (PAL[0], "INGRESO · ESCUELA DE SUBOFICIALES Y AGENTES → DIRECCIÓN GENERAL DE INSTITUTOS E INSTRUCCIÓN",
              "23/10/2026 22:06 · registró SARGENTO PÉREZ ANA", "Lleva/entrega: AGENTE ESYA · Recibe: OF. AUX. MIRANDA · Fojas: 6")]
    for i, (c, t1, t2, t3) in enumerate(items):
        p.d.ellipse([x + 4, y + 26, x + 26, y + 48], outline=c, width=4)
        if i < len(items) - 1:
            p.d.line([x + 15, y + 50, x + 15, y + 150], fill=BORDE, width=3)
        p.card(x + 44, y, 1176, 130, c)
        p.text(x + 70, y + 18, t1, 15, "Bold")
        p.text(x + 70, y + 52, t2, 13, "Regular", MUTED)
        p.text(x + 70, y + 84, t3, 13, "SemiBold", INK2)
        p.marca(1580, y + 64, i + 1)
        y += 150
    p.d.rounded_rectangle([x, y, x + 1220, y + 46], 10, fill=(15, 23, 42), outline=BORDE)
    p.text(x + 18, y + 23, "›  Corregir: eliminar movimientos o trámites cargados por error", 15, "SemiBold", INK2, anchor="lm")
    p.marca(1580, y + 23, 4)
    return p.guardar(P("29_hoja_ruta.png"))


def roles():
    """Diagrama de las tres rutas de trabajo."""
    W, H = 1800, 900
    im = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)
    carriles = [("SUBOFICIAL · Mesa de entradas", (180, 83, 9), ["Llega el\nexpediente", "Lo busca por N°\n(Mi trabajo)", "¿Ya existe?\nReingreso · si no, Nuevo", "Queda en\nPara tramitar"]),
                ("OFICIAL · Trámite", (21, 128, 61), ["Abre\nMi trabajo", "Nota en Word\no Tramitar y despachar", "Elige: comisionista,\nsale ahora o queda", "Siguiente\nexpediente"]),
                ("COMISIONISTA · Entregas", (109, 40, 217), ["Ve\nPara entregar", "Lleva el\nexpediente", "Carga quién\nlo recibe", "Salida asentada\n+ WhatsApp"])]
    d.text((60, 40), "Una ruta de trabajo para cada uno", font=font(40, "ExtraBold"), fill=(15, 30, 70))
    d.text((60, 96), "El expediente pasa de una bandeja a la otra sin volver a cargar datos.", font=font(20, "Medium"), fill=(71, 85, 105))
    y = 160
    for titulo, c, pasos in carriles:
        d.rounded_rectangle([40, y, W - 40, y + 210], 22, fill=tuple(int(v * 0.08 + 255 * 0.92) for v in c), outline=c, width=3)
        d.rounded_rectangle([40, y, 380, y + 210], 22, fill=c)
        d.multiline_text((210, y + 105), titulo.replace(" · ", "\n"), font=font(24, "ExtraBold"), fill=(255, 255, 255), anchor="mm", align="center")
        for i, s in enumerate(pasos):
            x = 420 + i * 340
            d.rounded_rectangle([x, y + 40, x + 290, y + 170], 18, fill=(255, 255, 255), outline=c, width=3)
            d.ellipse([x - 14, y + 26, x + 22, y + 62], fill=c)
            d.text((x + 4, y + 44), str(i + 1), font=font(20, "Black"), fill=(255, 255, 255), anchor="mm")
            d.multiline_text((x + 145, y + 105), s, font=font(19, "Bold"), fill=(30, 41, 59), anchor="mm", align="center", spacing=6)
            if i < 3:
                d.polygon([(x + 300, y + 95), (x + 326, y + 105), (x + 300, y + 115)], fill=c)
        y += 240
    # flechas entre carriles
    d.line([1385, 380, 1385, 400], fill=(21, 128, 61), width=6)
    d.line([1385, 620, 1385, 640], fill=(109, 40, 217), width=6)
    im.save(P("19_roles.png"), optimize=True)
    return P("19_roles.png")


TODAS = [roles, mi_trabajo, mesa, libro_elegir, tramitar_despachar, tramitar_word, ia, resultado, comision, whatsapp, hoja_ruta]

if __name__ == "__main__":
    for f in TODAS:
        print(f())
