"""Figuras de la propuesta que cambian con el avance de los sistemas (mapa de informatización).

Uso (desde la raíz del repo):  python3 docs/propuesta/figuras.py
"""
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch  # noqa: E402

SALIDA = os.path.join(os.path.dirname(__file__), "img")
NAVY = "#0F1E45"

ESTADOS = {"func": ("EN FUNCIONAMIENTO", "#15803D"), "piloto": ("PILOTO EN CURSO", "#1D4ED8"),
           "des": ("EN DESARROLLO", "#C2410C"), "rel": ("A RELEVAR", "#64748B")}

AREAS = [  # (título, subtítulo, color, estado) en sentido horario desde arriba
    ("Mesas de Entradas", "todas las Direcciones", "#1D4ED8", "rel"),
    ("Dpto. Personal D-1", "legajos · licencias · sanciones", "#1A9E6E", "rel"),
    ("Dpto. Logística D-4", "inventario · vehículos", "#C98400", "rel"),
    ("Dpto. Judicial D-5", "oficios · sumarios", "#D9581F", "rel"),
    ("Medicina Legal", "exámenes · informes", "#D14D80", "des"),
    ("Asuntos Internos", "actuaciones · sumarios", "#8B84E8", "rel"),
    ("Institutos e Instrucción", "expedientes · actividades", "#1D4ED8", "func"),
    ("I.E.S.P.", "legajos académicos · compañía", "#0E7F2E", "func"),
    ("Gabinete Interdisc.", "certificados · seguimiento", "#0E7F2E", "func"),
    ("Relaciones Policiales", "eventos · ceremonial", "#E06666", "rel"),
    ("Armería y Tiro", "armas · prácticas", "#C98400", "rel"),
    ("Comisarías", "U. Regionales · oficiales de turno", "#2F7FE0", "piloto"),
]


def mapa():
    fig, ax = plt.subplots(figsize=(21, 14), dpi=100)
    ax.set_xlim(-11.2, 11.2)
    ax.set_ylim(-6.6, 7.2)
    ax.axis("off")
    ax.text(0, 6.75, "Mapa de informatización propuesto", ha="center", va="center", fontsize=34, weight="bold", color=NAVY)
    rx, ry = 8.4, 5.0
    for i, (tit, sub, col, est) in enumerate(AREAS):
        a = math.pi / 2 - math.pi / len(AREAS) - i * 2 * math.pi / len(AREAS)
        x, y = rx * math.cos(a), ry * math.sin(a) - 0.2
        ax.plot([0, x * 0.82], [-0.2, y * 0.82 - 0.03], color="#CBD5E1", lw=3, zorder=1)
        w, h = 3.7, 1.0
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.18", fc=col, ec="none", zorder=3))
        ax.text(x, y + 0.17, tit, ha="center", va="center", fontsize=15.5, weight="bold", color="white", zorder=4)
        ax.text(x, y - 0.2, sub, ha="center", va="center", fontsize=11.5, color="white", zorder=4)
        etq, ce = ESTADOS[est]
        ax.add_patch(FancyBboxPatch((x - 1.3, y - h / 2 - 0.47), 2.6, 0.3, boxstyle="round,pad=0.02,rounding_size=0.14",
                                    fc="white", ec=ce, lw=2.2, zorder=3))
        ax.text(x, y - h / 2 - 0.32, etq, ha="center", va="center", fontsize=10, weight="bold", color=ce, zorder=4)
    ax.add_patch(Circle((0, -0.2), 2.3, fc=NAVY, ec="#FACC15", lw=6, zorder=5))
    ax.text(0, 0.65, "PLATAFORMA\nCOMÚN", ha="center", va="center", fontsize=25, weight="bold", color="white", zorder=6, linespacing=1.3)
    ax.text(0, -0.45, "web · app en el celular", ha="center", fontsize=15, color="#CBD5E1", zorder=6)
    ax.text(0, -0.95, "roles · auditoría · respaldo", ha="center", fontsize=15, color="#CBD5E1", zorder=6)
    ax.text(0, -1.5, "mesa de trabajo", ha="center", fontsize=15, color="#FDE68A", zorder=6)
    fig.savefig(os.path.join(SALIDA, "mapa.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    mapa()
    print("ok")
