"""Genera las imágenes del manual (maquetas fieles a la app, con llamadas numeradas)."""
import os

from PIL import Image, ImageDraw

from mock import AMBAR, AZUL, BORDE, INK, INK2, MUTED, NAR, PAL, ROJO, VERDE, Pantalla, font, telefono

OUT = os.environ.get("OUT", "img")
os.makedirs(OUT, exist_ok=True)
P = lambda n: os.path.join(OUT, n)  # noqa: E731
DGII = "DIRECCIÓN GRAL. DE INSTITUTOS E INSTRUCCIÓN"


def login():
    p = Pantalla(1400, 860, sidebar=False)
    try:
        logo = Image.open("assets/logo_policia.png").convert("RGBA")
        logo.thumbnail((90, 100))
        p.im.paste(logo, (60, 40), logo)
    except OSError:
        pass
    p.text(170, 52, "Registro de Expedientes", 36, "ExtraBold")
    p.text(170, 104, "POLICÍA DE TUCUMÁN · MESA DE ENTRADAS Y REGISTRO DE EXPEDIENTES", 13, "SemiBold", MUTED)
    p.d.line([60, 150, 1340, 150], fill=AZUL, width=2)
    p.card(400, 220, 600, 470)
    p.text(440, 252, "Ingreso", 24, "Bold")
    y = p.campo(440, 310, 520, "Legajo", "15670")
    p.marca(985, 358, 1)
    y = p.campo(440, y, 520, "Clave", "••••••••")
    p.marca(985, 446, 2)
    p.boton(440, y + 10, 520, "Ingresar")
    p.marca(985, 524, 3)
    p.text(700, 640, "Primer ingreso: el sistema le pedirá crear su clave personal", 14, "Medium", MUTED, anchor="mm")
    return p.guardar(P("01_login.png"))


def panel():
    p = Pantalla(activo="Panel de Control", titulo="Panel de Control", sub="Policía de Tucumán · Mesa de Entradas y Registro de Expedientes")
    p.marca(300, 250, 1)
    p.marca(250, 700, 2)
    y = p.kpis(340, p.y, [("Expedientes 2026", 148, "96 iniciados · 52 recibidos", AZUL), ("Pendientes de trámite", 23, "125 tramitados", AMBAR),
                          ("Urgentes activos", 5, "Urgente trámite", NAR), ("Vencidos", 2, "Término superado", ROJO),
                          ("Fuera de la Dirección", 31, "En otras dependencias", PAL[3])])
    p.marca(1540, 210, 3)
    y = p.alerta(340, y, 1220, "VENCIDO hace 1 d · Exp. 546/120/2", "SUMARIO ADMINISTRATIVO · JEFATURA DE POLICÍA", ROJO)
    p.marca(1540, y - 50, 4)
    # gráfico de barras
    p.card(340, y, 720, 360)
    p.text(366, y + 20, "Ingresos por mes · 2026", 17, "Bold")
    meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct"]
    vals = [(8, 4), (10, 5), (12, 6), (9, 5), (11, 7), (8, 4), (10, 6), (9, 5), (11, 6), (6, 3)]
    for i, (a, b) in enumerate(vals):
        x = 380 + i * 66
        base = y + 320
        p.d.rounded_rectangle([x, base - a * 14, x + 40, base], 4, fill=PAL[0])
        p.d.rounded_rectangle([x, base - a * 14 - b * 14 - 3, x + 40, base - a * 14 - 3], 4, fill=PAL[1])
        p.text(x + 20, base + 12, meses[i], 11, "Medium", MUTED, anchor="mm")
    p.card(1080, y, 480, 360)
    p.text(1106, y + 20, "¿Dónde están los abiertos?", 17, "Bold")
    for i, (n, v, c) in enumerate([("DGII", 18, PAL[0]), ("JEF", 12, PAL[7]), ("IESP", 7, PAL[2]), ("ESyA", 5, PAL[3]), ("SUBJEF", 4, PAL[1])]):
        yy = y + 70 + i * 52
        p.text(1106, yy + 14, n, 13, "Bold", INK2, anchor="lm")
        p.d.rounded_rectangle([1190, yy, 1190 + v * 17, yy + 28], 5, fill=c)
        p.text(1200 + v * 17, yy + 14, str(v), 13, "Bold", INK2, anchor="lm")
    return p.guardar(P("02_panel.png"))


def movil():
    p = Pantalla(520, 1040, movil=True, activo="Movimiento Rápido")
    p.marca(470, 104, 1)
    p.marca(82, 33, 2)
    p.x0, p.y = 24, 156
    p.text(24, p.y, "Movimiento Rápido", 26, "ExtraBold")
    p.text(24, p.y + 40, "TRÁMITE, SALIDAS, INGRESOS Y PASES", 11, "SemiBold", MUTED)
    p.d.line([24, p.y + 64, 496, p.y + 64], fill=AZUL, width=2)
    y = p.campo(24, p.y + 84, 472, "Buscar expediente", "545/120/3 · 2026 · ACTUACIONES…", "select")
    p.card(24, y, 472, 170, PAL[0])
    p.text(46, y + 20, "N° 545 / F° 120 / O° 3", 22, "ExtraBold")
    p.chip(46, y + 60, "ACTUACIONES ADMINISTRATIVAS", (96, 165, 250))
    p.chip(46, y + 96, "EN TRÁMITE", PAL[0])
    p.chip(46, y + 130, "PENDIENTE DE TRÁMITE", AMBAR)
    y += 190
    p.d.rounded_rectangle([24, y, 496, y + 48], 10, fill=(15, 23, 42), outline=BORDE)
    p.d.rounded_rectangle([28, y + 4, 258, y + 44], 8, fill=(37, 99, 235))
    p.text(143, y + 24, "Trámite", 15, "Bold", anchor="mm")
    p.text(377, y + 24, "Movimiento", 15, "Bold", MUTED, anchor="mm")
    p.marca(470, y + 24, 3)
    y += 66
    y = p.campo(24, y, 472, "¿Qué se hizo?", "NOTA ELEVADA", "select")
    y = p.campo(24, y, 472, "Tramitado por", "OF. PPAL. GÓMEZ JUAN")
    p.boton(24, y + 4, 472, "Marcar como TRAMITADO")
    return telefono(p, P("03_movil.png"))


def nuevo_1():
    p = Pantalla(activo="Nuevo Expediente", titulo="Nuevo Expediente", sub="Registro en el libro · N° EXP / FOLIO / ORDEN")
    x = 340
    p.text(x, p.y, "Origen del expediente", 14, "SemiBold", INK2)
    p.radio(x, p.y + 28, ["INICIADO EN LA DIRECCIÓN", "RECIBIDO DE OTRA DEPENDENCIA"], 1)
    p.marca(320, p.y + 38, 1)
    p.campo(960, p.y, 600, "Tipo de expediente", "ACTUACIONES ADMINISTRATIVAS", "select")
    p.marca(1580, p.y + 48, 2)
    y = p.y + 100
    p.campo(x, y, 520, "Dependencia de origen (de dónde viene)", "JEFATURA DE POLICÍA", "select")
    p.boton(870, y + 24, 70, "+", "sec", 46)
    p.marca(320, y + 48, 3)
    p.campo(960, y, 520, "Instancia a la que va", "¿A qué instancia se eleva o remite?", "select", placeholder=True)
    p.boton(1490, y + 24, 70, "+", "sec", 46)
    p.marca(1580, y + 48, 4)
    p.marca(905, y + 2, 5)
    y += 110
    p.card(x, y, 1220, 210)
    p.text(x + 24, y + 18, "Asiento en el libro", 16, "Bold")
    for i, (lab, val) in enumerate([("N° Expediente", "545"), ("Folio (foja izq.)", "120"), ("N° Orden", "3"), ("Libro", "1")]):
        p.campo(x + 24 + i * 250, y + 52, 230, lab, val, "numero")
    p.d.rectangle([x + 1030, y + 82, x + 1050, y + 102], outline=MUTED, width=2)
    p.text(x + 1060, y + 92, "Iniciar nuevo folio", 14, "SemiBold", INK2, anchor="lm")
    p.text(x + 24, y + 150, "545/120/3", 34, "ExtraBold")
    p.text(x + 220, y + 168, "IDENTIFICACIÓN · 10 RENGLONES POR FOLIO", 12, "SemiBold", MUTED)
    p.resaltar(x + 14, y + 140, x + 600, y + 196)
    p.marca(x + 620, y + 168, 6)
    p.marca(x + 1235, y + 92, 7)
    return p.guardar(P("04_nuevo_1.png"))


def nuevo_2():
    p = Pantalla(activo="Nuevo Expediente", titulo="Nuevo Expediente", sub="Datos del expediente")
    x = 340
    p.card(x, p.y, 1220, 760)
    y = p.seccion(x + 20, p.y + 20, "Datos del expediente", 1180)
    p.campo(x + 30, y, 360, "Fecha de ingreso / inicio", "16/10/2026", "fecha")
    p.campo(x + 420, y, 360, "Hora", "09:15")
    p.campo(x + 810, y, 380, "Sale con", "VISTO BUENO", "select")
    p.marca(x + 1205, y + 48, 1)
    y += 90
    p.campo(x + 30, y, 560, "N° de expediente / nota de origen", "9319/269/26D1")
    p.campo(x + 620, y, 570, "Iniciador / causante", "PTP MIRK GUIDO ELIO LEGAJO 15670")
    p.marca(x + 1205, y + 48, 2)
    y += 90
    p.campo(x + 30, y, 1160, "Asunto / carátula", "SU SITUACIÓN ADMINISTRATIVA LABORAL", h=60)
    y += 104
    p.text(x + 30, y, "Prioridad", 14, "SemiBold", INK2)
    p.radio(x + 30, y + 32, ["NORMAL", "URGENTE TRÁMITE"], 0)
    p.campo(x + 380, y, 260, "Fecha de término", "dd/mm/aaaa", "fecha", placeholder=True)
    p.campo(x + 670, y, 180, "Fojas", "4", "numero")
    p.campo(x + 880, y, 310, "Ubicación actual", "DIRECCIÓN GRAL. DE INST…", "select")
    p.marca(x + 1205, y + 48, 3)
    y += 90
    p.campo(x + 30, y, 360, "Entregado por (quien lo trae)", "DORADO JUAN")
    p.campo(x + 420, y, 360, "Recibido por", "OF. PPAL. GÓMEZ JUAN")
    p.campo(x + 810, y, 380, "Estado", "EN TRÁMITE", "select")
    p.marca(x + 1205, y + 48, 4)
    y += 100
    p.boton(x + 30, y, 300, "Registrar expediente")
    p.marca(x + 350, y + 24, 5)
    return p.guardar(P("05_nuevo_2.png"))


def libro_fisico():
    """Diagrama del libro: doble página, folio izquierdo y orden."""
    im = Image.new("RGB", (1600, 760), (255, 255, 255))
    d = ImageDraw.Draw(im)
    papel, linea = (252, 248, 236), (205, 196, 170)
    d.rounded_rectangle([60, 70, 790, 690], 14, fill=papel, outline=(160, 150, 120), width=3)
    d.rounded_rectangle([810, 70, 1540, 690], 14, fill=papel, outline=(160, 150, 120), width=3)
    d.line([800, 60, 800, 700], fill=(120, 110, 90), width=6)
    d.text((80, 84), "FOLIO 120", font=font(26, "ExtraBold"), fill=(30, 58, 138))
    d.text((1520, 84), "FOLIO 121", font=font(26, "ExtraBold"), fill=(120, 110, 90), anchor="ra")
    cols_i = [("ORDEN", 80), ("N° EXP.", 190), ("FECHA", 330), ("TIPO / ASUNTO", 470)]
    cols_d = [("ORIGEN", 830), ("DESTINO", 1050), ("OBSERVACIONES", 1280)]
    for t, x in cols_i + cols_d:
        d.text((x, 140), t, font=font(15, "Bold"), fill=(90, 80, 60))
    datos = [("1", "543", "14/10", "SUMARIO ADM.", "JEFATURA", "JEFATURA"), ("2", "544", "14/10", "BECA", "IESP", "DGII"),
             ("3", "545", "15/10", "ACTUACIONES ADM.", "JEFATURA", "SUBJEFATURA"), ("4", "546", "15/10", "INVITACIÓN", "OTRA DEP.", "DGII")]
    for i in range(10):
        y = 175 + i * 50
        d.line([70, y, 780, y], fill=linea, width=2)
        d.line([820, y, 1530, y], fill=linea, width=2)
        if i < len(datos):
            o, n, f, t, org, des = datos[i]
            color = (17, 24, 39)
            if i == 2:
                d.rectangle([72, y + 3, 778, y + 47], fill=(254, 240, 138))
                d.rectangle([822, y + 3, 1528, y + 47], fill=(254, 240, 138))
            for txt, x in zip([o, n, f, t], [100, 190, 330, 470]):
                d.text((x, y + 13), txt, font=font(18, "SemiBold"), fill=color)
            d.text((830, y + 13), org, font=font(18, "SemiBold"), fill=color)
            d.text((1050, y + 13), des, font=font(18, "SemiBold"), fill=color)
    d.text((800, 30), "LOS DATOS DE CADA EXPEDIENTE OCUPAN LAS DOS PÁGINAS — SE NUMERA LA FOJA IZQUIERDA", font=font(17, "Bold"), fill=(30, 41, 59), anchor="mm")
    d.rounded_rectangle([520, 712, 1080, 756], 22, fill=(30, 58, 138))
    d.text((800, 734), "N° EXP 545  /  FOLIO 120  /  ORDEN 3   =   545/120/3", font=font(20, "ExtraBold"), fill=(255, 255, 255), anchor="mm")
    im.save(P("06_libro_fisico.png"), optimize=True)
    return P("06_libro_fisico.png")


def tarjeta(p, x, y, w, ub="DIRECCIÓN GRAL. DE INSTITUTOS E INSTRUCCIÓN", tram=False):
    p.card(x, y, w, 190, PAL[0])
    p.text(x + 28, y + 18, "N° 545 / F° 120 / O° 3", 28, "ExtraBold")
    p.text(x + 400, y + 30, "AÑO 2026 · LIBRO 1", 12, "SemiBold", MUTED)
    xx = p.chip(x + 28, y + 64, "ACTUACIONES ADMINISTRATIVAS", (96, 165, 250))
    xx = p.chip(xx, y + 64, "TRAMITADO" if tram else "EN TRÁMITE", PAL[2] if tram else PAL[0])
    p.chip(xx, y + 64, "✓ TRAMITADO 16/10/2026" if tram else "PENDIENTE DE TRÁMITE", VERDE if tram else AMBAR)
    xx = p.chip(x + 28, y + 100, "" + ub, PAL[0])
    p.chip(xx, y + 100, "→ SUBJEFATURA DE POLICÍA", PAL[1])
    p.text(x + 28, y + 146, "SU SITUACIÓN ADMINISTRATIVA LABORAL · Origen: JEFATURA DE POLICÍA · Último movimiento: 16/10/2026 09:15", 13, "Regular", INK2)
    return y + 206


def tramite():
    p = Pantalla(activo="Ficha de Expediente", titulo="Ficha de Expediente", sub="Hoja de ruta, movimientos, curso y personal")
    y = tarjeta(p, 340, p.y, 1220)
    y = p.tabs(340, y, ["Trámite", "PDF", "Hoja de ruta", "Registrar movimiento", "Curso y personal", "Alertas", "Editar"], 0)
    p.marca(330, y - 40, 1)
    y = p.alerta(340, y, 1220, "PENDIENTE DE TRÁMITE", "Registre lo realizado para dejarlo asentado en la hoja de ruta.", AMBAR, "…")
    p.card(340, y, 1220, 330)
    p.campo(370, y + 24, 560, "¿Qué se hizo?", "NOTA ELEVADA", "select")
    p.marca(950, y + 72, 2)
    p.campo(980, y + 24, 550, "Tramitado por", "OF. PPAL. GÓMEZ JUAN")
    p.campo(370, y + 114, 560, "Fecha", "16/10/2026", "fecha")
    p.campo(980, y + 114, 550, "Hora", "10:30")
    p.campo(370, y + 204, 1160, "Detalle (N° de nota, providencia, a quién se respondió…)", "Nota N° 123/26 elevada a Subjefatura")
    p.marca(1545, y + 252, 3)
    p.boton(370, y + 340, 320, "Marcar como TRAMITADO")
    p.marca(710, y + 364, 4)
    return p.guardar(P("07_tramite.png"))


def movimiento():
    p = Pantalla(activo="Movimiento Rápido", titulo="Movimiento Rápido", sub="Salidas, ingresos y pases")
    y = tarjeta(p, 340, p.y, 1220)
    p.card(340, y, 1220, 450)
    x1, x2 = 370, 980
    p.campo(x1, y + 20, 560, "Tipo de movimiento", "SALIDA", "select")
    p.marca(950, y + 68, 1)
    p.campo(x2, y + 20, 550, "Destino", "SUBJEFATURA DE POLICÍA", "select")
    p.marca(1545, y + 68, 2)
    p.campo(x1, y + 108, 560, "Desde", "DIRECCIÓN GRAL. DE INSTITUTOS E INSTRUCCIÓN", "select")
    p.campo(x2, y + 108, 550, "Despacho / Resolución", "VISTO BUENO", "select")
    p.marca(1545, y + 156, 3)
    p.campo(x1, y + 196, 270, "Fecha", "16/10/2026", "fecha")
    p.campo(x1 + 290, y + 196, 270, "Hora", "11:05")
    p.campo(x2, y + 196, 550, "Quién lo lleva / entrega", "CABO PÉREZ LUIS")
    p.marca(1545, y + 244, 4)
    p.campo(x1, y + 284, 560, "Quién lo recibe", "SGTO. ROMERO ANA")
    p.d.rectangle([x2, y + 318, x2 + 22, y + 340], outline=MUTED, width=2)
    p.text(x2 + 34, y + 329, "Urgente trámite", 14, "SemiBold", INK2, anchor="lm")
    p.boton(x1, y + 380, 330, "Registrar movimiento")
    y2 = y + 470
    p.alerta(340, y2, 760, "Último movimiento: SALIDA → SUBJEFATURA DE POLICÍA", "16/10/2026 11:05 · lo lleva CABO PÉREZ LUIS", VERDE, "✓")
    p.boton(1120, y2 + 10, 440, "Informar por WhatsApp", "wa", 52)
    p.marca(1580, y2 + 36, 5)
    return p.guardar(P("08_movimiento.png"))


def pdf():
    p = Pantalla(activo="Ficha de Expediente", titulo="Ficha de Expediente", sub="PDF del expediente en Google Drive")
    y = tarjeta(p, 340, p.y, 1220)
    y = p.tabs(340, y, ["Trámite", "PDF", "Hoja de ruta", "Registrar movimiento", "Curso y personal", "Alertas", "Editar"], 1)
    p.boton(340, y, 520, "Ver PDF del expediente (v2)", "sec")
    p.marca(880, y + 24, 1)
    y += 70
    y = p.seccion(340, y, "Subir expediente digitalizado")
    p.d.rounded_rectangle([340, y, 840, y + 48], 10, fill=(15, 23, 42), outline=BORDE)
    p.d.rounded_rectangle([344, y + 4, 580, y + 44], 8, fill=(37, 99, 235))
    p.text(462, y + 24, "Archivo PDF", 15, "Bold", anchor="mm")
    p.text(710, y + 24, "Fotos de las fojas", 15, "Bold", MUTED, anchor="mm")
    p.marca(860, y + 24, 2)
    y += 70
    p.d.rounded_rectangle([340, y, 1560, y + 120], 14, fill=(15, 23, 42), outline=(96, 165, 250), width=2)
    p.text(950, y + 44, "Arrastre el PDF aquí o toque para elegirlo", 18, "SemiBold", INK, anchor="mm")
    p.text(950, y + 78, "Si elige varios PDF se unen en uno · en el celular puede usar la cámara", 13, "Regular", MUTED, anchor="mm")
    p.marca(1580, y + 60, 3)
    y += 140
    y = p.campo(340, y, 1220, "Descripción (opcional)", "Con informe de la División y providencia")
    p.boton(340, y, 420, "Subir a Google Drive (1 archivo)")
    p.marca(780, y + 24, 4)
    return p.guardar(P("09_pdf.png"))


def libro():
    p = Pantalla(activo="Libro de Registro", titulo="Libro de Registro", sub="Control integral de expedientes")
    p.card(340, p.y, 1220, 112)
    p.campo(364, p.y + 16, 560, "Buscar (N°, asunto, iniciador, N° origen)", "situación administrativa")
    p.campo(950, p.y + 16, 280, "Trámite", "Pendientes de trámite", "select")
    p.campo(1250, p.y + 16, 290, "Instancia de destino", "SUBJEFATURA", "select")
    p.marca(330, p.y + 64, 1)
    y = p.y + 132
    y = p.kpis(340, y, [("Resultado", 23, "expedientes filtrados", AZUL), ("Abiertos", 23, "en trámite", PAL[2]),
                        ("Urgentes", 3, "abiertos", NAR), ("Pendientes de trámite", 23, "0 tramitados", AMBAR)])
    cols = ["", "N° Exp/F/O", "Ingreso", "Tipo", "Estado", "Tramitado", "Ubicación", "Destino", "PDF"]
    anch = [36, 130, 110, 230, 140, 120, 170, 170, 114]
    sel = (37, 99, 235)
    filas = [["■", "545/120/3", "15/10/2026", "ACTUACIONES ADM.", "EN TRÁMITE", "NO", "DGII", "SUBJEFATURA", "Ver"],
             ["■", "546/120/4", "15/10/2026", "INVITACIÓN", "EN TRÁMITE", "NO", "DGII", "SUBJEFATURA", "—"],
             ["□", "548/122/1", "16/10/2026", "SUMARIO ADM.", "REMITIDO", "NO", "JEFATURA", "SUBJEFATURA", "Ver"]]
    col = {}
    for r in range(3):
        col[(r, 6)] = ("bg", (30, 58, 100) if filas[r][6] == "DGII" else (110, 35, 35))
        col[(r, 7)] = ("bg", (110, 50, 25))
        col[(r, 4)] = ("tx", PAL[0] if filas[r][4] == "EN TRÁMITE" else PAL[3])
        col[(r, 5)] = ("tx", AMBAR)
        col[(r, 8)] = ("tx", (96, 165, 250))
        if r < 2:
            col[(r, 0)] = ("tx", sel)
    y = p.tabla(340, y, cols, filas, anch, col)
    p.marca(330, y - 120, 2)
    p.card(340, y, 1220, 150)
    p.text(364, y + 18, "Marcar 2 expediente(s) como TRAMITADO: 545/120/3, 546/120/4", 15, "Bold")
    p.campo(364, y + 46, 560, "¿Qué se hizo?", "NOTA ELEVADA", "select")
    p.boton(950, y + 70, 360, "Marcar como tramitados")
    p.marca(1330, y + 94, 3)
    p.boton(1350, y + 70, 190, "Exportar Excel", "sec")
    return p.guardar(P("10_libro.png"))


def hoja_ruta():
    p = Pantalla(activo="Ficha de Expediente", titulo="Ficha de Expediente", sub="Hoja de ruta")
    y = tarjeta(p, 340, p.y, 1220, ub="SUBJEFATURA DE POLICÍA", tram=True)
    y = p.tabs(340, y, ["Trámite", "PDF", "Hoja de ruta", "Registrar movimiento", "Curso y personal", "Alertas", "Editar"], 2)
    p.d.line([370, y, 370, y + 470], fill=(30, 41, 59), width=3)
    items = [("SALIDA · DGII → SUBJEFATURA DE POLICÍA", "16/10/2026 11:05 · registró OF. PPAL. GÓMEZ JUAN", "Despacho: VISTO BUENO · Lleva: CABO PÉREZ LUIS · Recibe: SGTO. ROMERO ANA", PAL[1]),
             ("DIGITALIZACIÓN", "16/10/2026 10:40 · registró SGTO. DÍAZ MARÍA", "PDF v1 subido a Drive (4 fojas)", (96, 165, 250)),
             ("TRÁMITE · DGII", "16/10/2026 10:30 · registró OF. PPAL. GÓMEZ JUAN", "Despacho: NOTA ELEVADA · Nota N° 123/26 elevada a Subjefatura", PAL[2]),
             ("INGRESO · JEFATURA DE POLICÍA → DGII", "15/10/2026 09:15 · registró SGTO. DÍAZ MARÍA", "Lleva: DORADO JUAN · Recibe: SGTO. DÍAZ MARÍA · Fojas: 4", PAL[0])]
    for t1, t2, t3, c in items:
        p.d.ellipse([360, y + 18, 380, y + 38], fill=c, outline=(7, 10, 20), width=3)
        p.card(400, y, 1160, 104)
        p.text(424, y + 16, t1, 16, "Bold")
        p.text(424, y + 44, t2, 13, "Regular", MUTED)
        p.text(424, y + 70, t3, 14, "Regular", INK2)
        y += 118
    p.marca(1580, p.y + 260 + 40, 1)
    p.boton(340, y + 6, 360, "Hoja de ruta (PDF)", "sec")
    p.marca(720, y + 30, 2)
    return p.guardar(P("11_hoja_ruta.png"))


def alertas():
    p = Pantalla(activo="Alertas y Agenda", titulo="Alertas y Agenda", sub="Inicios de curso, vencimientos, expedientes detenidos y eventos")
    y = p.kpis(340, p.y, [("Críticas", 3, "hoy / vencidas", ROJO), ("Importantes", 4, "requieren acción", NAR),
                          ("Próximas", 6, "en los próximos días", AMBAR), ("Informativas", 9, "seguimiento", AZUL)])
    p.marca(330, y - 70, 1)
    y = p.tabs(340, y, ["Alertas", "Agenda 60 días", "Nuevo evento"], 0)
    for t, dsc, c, ic in [("HOY inicia: CURSO DE TIRADOR ESPECIAL", "Exp. 547/120/3 · EFT · EXTERNO · 12 efectivos", ROJO, "!"),
                          ("VENCIDO hace 1 d · Exp. 546/120/2", "SUMARIO ADMINISTRATIVO · JEFATURA DE POLICÍA", ROJO, "!"),
                          ("En 3 días inicia: SEMINARIO DDHH · SIN AUTORIZACIÓN", "Exp. 549/122/2 · 19/10/2026 · IESP", NAR, "!"),
                          ("19 días sin movimiento · Exp. 548/122/1", "INVITACIÓN · SUBJEFATURA DE POLICÍA", AZUL, "i")]:
        p.alerta(340, y, 900, t, dsc, c, ic)
        p.boton(1260, y + 11, 140, "Ficha", "sec", 46)
        p.boton(1414, y + 11, 146, "Avisar", "wa", 46)
        y += 86
    p.marca(330, y - 300, 2)
    p.marca(1580, y - 300, 3)
    return p.guardar(P("12_alertas.png"))


def carga():
    p = Pantalla(activo="Carga Masiva", titulo="Carga Masiva", sub="Importación del libro · Excel o transcripción directa")
    y = p.tabs(340, p.y, ["Desde Excel / CSV", "Transcripción rápida del libro"], 1)
    p.marca(330, y - 40, 1)
    p.campo(340, y, 300, "Renglones a transcribir", "10", "numero")
    p.campo(670, y, 300, "Fecha por defecto", "15/10/2026", "fecha")
    p.boton(1000, y + 24, 260, "Regenerar grilla", "sec", 46)
    y += 100
    cols = ["N° Exp", "Folio", "Orden", "Fecha", "Tipo", "Origen", "Asunto", "Destino"]
    an = [100, 90, 90, 130, 230, 200, 230, 150]
    filas = [["700", "200", "1", "01/10/2026", "BECA", "IESP", "Beca de posgrado", "DGII"],
             ["701", "200", "2", "02/10/2026", "TALLER", "JEFATURA", "Taller de oratoria", "IESP"],
             ["702", "200", "3", "02/10/2026", "⌄", "⌄", "", "⌄"],
             ["703", "200", "4", "02/10/2026", "", "", "", ""]]
    y = p.tabla(340, y, cols, filas, an, {(2, 4): ("tx", MUTED), (2, 5): ("tx", MUTED), (2, 7): ("tx", MUTED)})
    p.marca(330, y - 140, 2)
    y = p.kpis(340, y, [("Filas leídas", 2, "", AZUL), ("Listas para cargar", 2, "nuevas", VERDE), ("Ya existen", 0, "", AMBAR), ("Con error", 0, "", ROJO)])
    p.marca(1580, y - 70, 3)
    p.boton(340, y, 340, "Importar 2 asientos")
    p.marca(700, y + 24, 4)
    return p.guardar(P("13_carga.png"))


def usuarios():
    p = Pantalla(activo="Configuración", titulo="Configuración", sub="Usuarios, libro, dependencias, Drive y respaldo")
    y = p.tabs(340, p.y, ["Usuarios", "Libro y alertas", "Dependencias y colores", "Tipos", "Google Drive", "Respaldo"], 0)
    y = p.kpis(340, y, [("Usuarios habilitados", 8, "1 deshabilitado", AZUL), ("Oficiales", 3, "cargan y tramitan", PAL[2]),
                        ("Suboficiales", 4, "cargan expedientes", PAL[3]), ("Administradores", 1, "configuración", PAL[0])])
    y = p.tabla(340, y, ["Legajo", "Grado", "Apellido", "Nombre", "Función", "Rol", "Habilitado"],
                [["15670", "COMISARIO", "PONCE", "Sergio", "JEFE MESA DE ENTRADAS", "ADMINISTRADOR", "SÍ"],
                 ["16210", "OF. PRINCIPAL", "GÓMEZ", "Juan", "AUXILIAR", "OFICIAL", "SÍ"],
                 ["20001", "SARGENTO", "DÍAZ", "María", "MESA DE ENTRADAS", "SUBOFICIAL", "SÍ"]],
                [110, 160, 150, 130, 300, 210, 160], {(0, 5): ("tx", PAL[0]), (1, 5): ("tx", PAL[2]), (2, 5): ("tx", PAL[3])})
    p.marca(1580, y - 90, 1)
    y = p.seccion(340, y, "Nuevo usuario", 600)
    p.campo(340, y, 290, "Grado", "SARGENTO", "select")
    p.campo(650, y, 290, "Legajo (usuario)", "20015")
    p.campo(340, y + 90, 290, "Apellido", "ROMERO")
    p.campo(650, y + 90, 290, "Nombre", "Ana")
    p.campo(340, y + 180, 600, "Rol", "(según grado) → SUBOFICIAL", "select")
    p.marca(960, y + 228, 2)
    p.boton(340, y + 274, 260, "Crear usuario")
    p.marca(620, y + 298, 3)
    return p.guardar(P("14_usuarios.png"))


def flujo():
    im = Image.new("RGB", (1600, 560), (255, 255, 255))
    d = ImageDraw.Draw(im)
    pasos = [("1", "LLEGA O SE INICIA", "Se registra en el libro\nN° / Folio / Orden", (57, 135, 229), "SUBOFICIAL / OFICIAL"),
             ("2", "PDF", "Se digitaliza y se sube\na Google Drive", (96, 165, 250), "SUBOFICIAL / OFICIAL"),
             ("3", "TRÁMITE", "Se marca TRAMITADO:\nqué se hizo, quién, cuándo", (25, 158, 112), "SOLO OFICIAL"),
             ("4", "SALIDA", "Movimiento a la instancia\ncon quien lo lleva y recibe", (217, 89, 38), "SUBOFICIAL / OFICIAL"),
             ("5", "SEGUIMIENTO", "Alertas, vencimientos\ny devolución / archivo", (144, 133, 233), "TODOS")]
    w, g, x = 270, 45, 40
    for i, (n, t, dsc, c, rol) in enumerate(pasos):
        xx = x + i * (w + g)
        d.rounded_rectangle([xx, 120, xx + w, 420], 22, fill=(248, 250, 252), outline=c, width=4)
        d.ellipse([xx + w // 2 - 34, 86, xx + w // 2 + 34, 154], fill=c)
        d.text((xx + w // 2, 120), n, font=font(34, "Black"), fill=(255, 255, 255), anchor="mm")
        d.text((xx + w // 2, 190), t, font=font(22, "ExtraBold"), fill=(15, 23, 42), anchor="mm")
        d.multiline_text((xx + w // 2, 270), dsc, font=font(18, "Medium"), fill=(51, 65, 85), anchor="mm", align="center", spacing=8)
        d.rounded_rectangle([xx + 20, 356, xx + w - 20, 398], 21, fill=c)
        d.text((xx + w // 2, 377), rol, font=font(14, "Bold"), fill=(255, 255, 255), anchor="mm")
        if i < len(pasos) - 1:
            ax = xx + w + 6
            d.polygon([(ax, 260), (ax + g - 12, 270), (ax, 280)], fill=(148, 163, 184))
    d.text((800, 40), "CICLO DE VIDA DE UN EXPEDIENTE EN EL SISTEMA", font=font(26, "ExtraBold"), fill=(15, 23, 42), anchor="mm")
    d.text((800, 480), "Cada paso queda en la HOJA DE RUTA con fecha, hora y el grado, apellido y nombre de quien lo hizo.",
           font=font(19, "SemiBold"), fill=(30, 58, 138), anchor="mm")
    im.save(P("00_flujo.png"), optimize=True)
    return P("00_flujo.png")


TODAS = [flujo, login, panel, movil, nuevo_1, nuevo_2, libro_fisico, tramite, movimiento, pdf, libro, hoja_ruta, alertas, carga, usuarios]

if __name__ == "__main__":
    for f in TODAS:
        print(f())
