"""Mini-motor de maquetas (PIL) que reproduce el aspecto de la app para el manual de usuario."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont

F = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
_cache = {}


def font(size, peso="Regular"):
    k = (size, peso)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(F.format(peso), size)
    return _cache[k]


BG1, BG2 = (7, 10, 20), (17, 28, 56)
SIDEBAR = (4, 6, 11)
CARD = (19, 27, 46)
BORDE = (51, 65, 85)
INPUT = (15, 23, 42)
INK, INK2, MUTED = (248, 250, 252), (203, 213, 225), (148, 163, 184)
AZUL, AZUL2 = (59, 130, 246), (29, 78, 216)
VERDE, AMBAR, ROJO, NAR = (12, 163, 12), (250, 178, 25), (208, 59, 59), (236, 131, 90)
PAL = [(57, 135, 229), (217, 89, 38), (25, 158, 112), (201, 133, 0), (213, 81, 129), (0, 131, 0), (144, 133, 233), (230, 103, 103)]
WA = (22, 163, 74)
CALLOUT = (250, 204, 21)


def hexc(c):
    return c


class Pantalla:
    def __init__(self, w=1600, h=1000, sidebar=True, activo=None, titulo="", sub="", movil=False):
        self.w, self.h = w, h
        self.im = Image.new("RGB", (w, h), BG1)
        self.d = ImageDraw.Draw(self.im)
        # degradado radial simplificado
        for y in range(h):
            t = max(0.0, 1 - y / (h * 0.9))
            c = tuple(int(BG1[i] + (BG2[i] - BG1[i]) * t) for i in range(3))
            self.d.line([(0, y), (w, y)], fill=c)
        self.x0 = 0
        self.marks = []
        if movil:
            self._barra_movil(activo)
            self.x0, self.y = 24, 150
        elif sidebar:
            self._sidebar(activo)
            self.x0, self.y = 340, 40
        else:
            self.x0, self.y = 60, 40
        if titulo:
            self.header(titulo, sub)

    # ── estructura ──
    def _sidebar(self, activo):
        d = self.d
        d.rectangle([0, 0, 300, self.h], fill=SIDEBAR)
        d.line([300, 0, 300, self.h], fill=(30, 41, 59), width=2)
        try:
            logo = Image.open("assets/logo_policia.png").convert("RGBA")
            logo.thumbnail((80, 90))
            self.im.paste(logo, (110, 24), logo)
        except OSError:
            pass
        self.text(150, 128, "MESA DE ENTRADAS", 15, "ExtraBold", anchor="mm")
        self.text(150, 150, "DIRECCIÓN GRAL. DE INSTITUTOS E INSTRUCCIÓN", 10, "SemiBold", (96, 165, 250), anchor="mm")
        items = ["Panel de Control", "Nuevo Expediente", "Movimiento Rápido", "Libro de Registro", "Ficha de Expediente",
                 "Cursos y Personal", "Alertas y Agenda", "Carga Masiva", "Informes", "Configuración"]
        y = 185
        for it in items:
            if it == activo:
                d.rounded_rectangle([14, y - 4, 286, y + 30], 9, fill=(30, 58, 138), outline=(96, 165, 250))
            self.text(34, y + 13, it, 15, "SemiBold" if it == activo else "Medium", INK if it == activo else INK2, anchor="lm")
            y += 40
        d.line([20, y + 6, 280, y + 6], fill=(30, 41, 59))
        self.text(24, y + 30, "OF. PPAL. GÓMEZ JUAN", 13, "Bold")
        self.text(24, y + 50, "Legajo 15670 · JEFE MESA DE ENTRADAS", 11, "Regular", MUTED)
        self.chip(24, y + 66, "OFICIAL", PAL[2])

    def _barra_movil(self, activo):
        d = self.d
        d.rectangle([0, 0, self.w, 64], fill=(7, 10, 20))
        d.rounded_rectangle([14, 16, 50, 50], 8, fill=(30, 58, 138), outline=(96, 165, 250))
        self.text(32, 33, "›", 26, "Bold", anchor="mm")
        d.rounded_rectangle([16, 76, self.w - 16, 132], 12, fill=(29, 78, 216), outline=(96, 165, 250), width=2)
        self.text(36, 104, activo or "Panel de Control", 18, "Bold", anchor="lm")
        self.text(self.w - 40, 104, "⌄", 20, "Bold", anchor="mm")

    def header(self, titulo, sub):
        self.text(self.x0, self.y, titulo, 34 if self.w > 900 else 24, "ExtraBold")
        self.y += 50 if self.w > 900 else 36
        self.text(self.x0, self.y, sub.upper(), 13 if self.w > 900 else 10, "SemiBold", MUTED)
        self.y += 30
        self.d.line([self.x0, self.y, self.w - 40, self.y], fill=(59, 130, 246), width=2)
        self.y += 24

    # ── primitivas ──
    def text(self, x, y, s, size=16, peso="Regular", color=INK, anchor="la"):
        self.d.text((x, y), s, font=font(size, peso), fill=color, anchor=anchor)

    def chip(self, x, y, s, color, size=12):
        f = font(size, "Bold")
        w = int(self.d.textlength(s, font=f)) + 24
        fondo = tuple(int(c * 0.25 + BG1[i] * 0.75) for i, c in enumerate(color))
        self.d.rounded_rectangle([x, y, x + w, y + size + 14], 20, fill=fondo, outline=color)
        self.d.text((x + 12, y + 7), s, font=f, fill=INK)
        return x + w + 8

    def card(self, x, y, w, h, acento=None):
        self.d.rounded_rectangle([x, y, x + w, y + h], 16, fill=CARD, outline=BORDE, width=2)
        if acento:
            self.d.rounded_rectangle([x, y, x + 7, y + h], 4, fill=acento)

    def campo(self, x, y, w, etiqueta, valor="", tipo="texto", placeholder=False, h=46):
        self.text(x, y, etiqueta, 14, "SemiBold", INK2)
        y += 24
        self.d.rounded_rectangle([x, y, x + w, y + h], 9, fill=INPUT, outline=BORDE, width=2)
        self.text(x + 14, y + h // 2, valor, 15, "Medium", MUTED if placeholder else INK, anchor="lm")
        if tipo == "select":
            self.text(x + w - 22, y + h // 2, "⌄", 18, "Bold", MUTED, anchor="mm")
        elif tipo == "fecha":
            self.text(x + w - 26, y + h // 2, "□", 16, "Bold", MUTED, anchor="mm")
        elif tipo == "numero":
            self.text(x + w - 56, y + h // 2, "–   +", 16, "Bold", MUTED, anchor="mm")
        return y + h + 18

    def boton(self, x, y, w, s, tipo="primario", h=48):
        col = {"primario": ((37, 99, 235), (96, 165, 250)), "wa": (WA, (74, 222, 128)), "sec": ((30, 41, 59), BORDE),
               "rojo": ((127, 29, 29), (239, 68, 68))}[tipo]
        self.d.rounded_rectangle([x, y, x + w, y + h], 10, fill=col[0], outline=col[1], width=2)
        self.text(x + w // 2, y + h // 2, s, 15, "Bold", anchor="mm")
        return y + h + 16

    def radio(self, x, y, opciones, sel=0):
        for i, o in enumerate(opciones):
            cx = x + 10
            self.d.ellipse([cx - 9, y + 2, cx + 9, y + 20], outline=AZUL if i == sel else MUTED, width=2)
            if i == sel:
                self.d.ellipse([cx - 4, y + 7, cx + 4, y + 15], fill=AZUL)
            self.text(x + 28, y + 11, o, 14, "SemiBold", INK, anchor="lm")
            x += int(self.d.textlength(o, font=font(14, "SemiBold"))) + 60

    def kpis(self, x, y, items, w_total=None):
        w_total = w_total or (self.w - x - 40)
        n = len(items)
        g = 14
        w = (w_total - g * (n - 1)) // n
        for i, (lab, val, nota, col) in enumerate(items):
            xx = x + i * (w + g)
            self.card(xx, y, w, 104, col)
            self.text(xx + 22, y + 16, lab.upper(), 11, "Bold", MUTED)
            self.text(xx + 22, y + 36, str(val), 32, "ExtraBold")
            self.text(xx + 22, y + 80, nota, 12, "Regular", INK2)
        return y + 124

    def tabs(self, x, y, nombres, sel=0):
        self.d.rounded_rectangle([x, y, self.w - 40, y + 50], 12, fill=(15, 23, 42), outline=(30, 41, 59))
        xx = x + 6
        for i, n in enumerate(nombres):
            w = int(self.d.textlength(n, font=font(14, "SemiBold"))) + 30
            self.d.rounded_rectangle([xx, y + 6, xx + w, y + 44], 9, fill=(37, 99, 235) if i == sel else (30, 41, 59))
            self.text(xx + w // 2, y + 25, n, 14, "SemiBold", INK if i == sel else MUTED, anchor="mm")
            xx += w + 6
        return y + 66

    def tabla(self, x, y, cols, filas, anchos, colores=None):
        w = sum(anchos)
        self.d.rounded_rectangle([x, y, x + w, y + 40 + 38 * len(filas)], 10, fill=(15, 23, 42), outline=BORDE)
        xx = x
        for c, a in zip(cols, anchos):
            self.text(xx + 12, y + 20, c, 13, "Bold", MUTED, anchor="lm")
            xx += a
        for r, fila in enumerate(filas):
            yy = y + 40 + 38 * r
            self.d.line([x, yy, x + w, yy], fill=(30, 41, 59))
            xx = x
            for j, (v, a) in enumerate(zip(fila, anchos)):
                col = (colores or {}).get((r, j))
                if col and col[0] == "bg":
                    self.d.rectangle([xx + 2, yy + 3, xx + a - 2, yy + 35], fill=col[1])
                    self.text(xx + 12, yy + 19, v, 13, "SemiBold", INK, anchor="lm")
                else:
                    self.text(xx + 12, yy + 19, v, 13, "SemiBold" if col else "Regular", col[1] if col else INK2, anchor="lm")
                xx += a
        return y + 40 + 38 * len(filas) + 20

    def alerta(self, x, y, w, titulo, detalle, color, icono="!"):
        fondo = tuple(int(c * 0.18 + BG1[i] * 0.82) for i, c in enumerate(color))
        self.d.rounded_rectangle([x, y, x + w, y + 70], 12, fill=fondo, outline=color, width=2)
        self.d.ellipse([x + 16, y + 20, x + 46, y + 50], fill=color)
        self.text(x + 31, y + 35, icono, 16, "ExtraBold", anchor="mm")
        self.text(x + 62, y + 14, titulo, 16, "Bold")
        self.text(x + 62, y + 40, detalle, 13, "Regular", INK2)
        return y + 86

    def seccion(self, x, y, s, w=None):
        w = w or (self.w - x - 40)
        self.d.rounded_rectangle([x, y, x + w, y + 42], 10, fill=(30, 41, 59))
        self.d.rectangle([x, y, x + 5, y + 42], fill=AZUL)
        self.text(x + 20, y + 21, s, 16, "Bold", (147, 197, 253), anchor="lm")
        return y + 58

    # ── llamadas numeradas para el manual ──
    def marca(self, x, y, n):
        self.marks.append((x, y, n))

    def _pintar_marcas(self):
        for x, y, n in self.marks:
            r = 22
            sombra = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
            sd = ImageDraw.Draw(sombra)
            sd.ellipse([x - r + 3, y - r + 4, x + r + 3, y + r + 4], fill=(0, 0, 0, 160))
            sombra = sombra.filter(ImageFilter.GaussianBlur(4))
            self.im.paste(sombra, (0, 0), sombra)
            self.d = ImageDraw.Draw(self.im)
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=CALLOUT, outline=(17, 24, 39), width=3)
            self.d.text((x, y), str(n), font=font(22, "Black"), fill=(17, 24, 39), anchor="mm")

    def resaltar(self, x1, y1, x2, y2):
        self.d.rounded_rectangle([x1, y1, x2, y2], 12, outline=CALLOUT, width=4)

    def guardar(self, ruta):
        self._pintar_marcas()
        self.im.save(ruta, optimize=True)
        return ruta


def telefono(pantalla: "Pantalla", ruta):
    """Enmarca una pantalla angosta como celular."""
    p = pantalla
    p._pintar_marcas()
    marco = Image.new("RGB", (p.w + 60, p.h + 120), (226, 232, 240))
    d = ImageDraw.Draw(marco)
    d.rounded_rectangle([0, 0, p.w + 59, p.h + 119], 60, fill=(17, 24, 39))
    marco.paste(p.im, (30, 60))
    d.rounded_rectangle([p.w // 2 - 30, 22, p.w // 2 + 90, 38], 8, fill=(0, 0, 0))
    # fondo transparente-ish a blanco
    lienzo = Image.new("RGB", marco.size, (255, 255, 255))
    mask = Image.new("L", marco.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, p.w + 59, p.h + 119], 60, fill=255)
    lienzo.paste(marco, (0, 0), mask)
    lienzo.save(ruta, optimize=True)
    return ruta
