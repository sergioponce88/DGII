"""Figura de la ruta guiada (9 pasos) para el informe del sistema para oficiales de turno."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = os.path.join(os.path.dirname(__file__), "img")
NAVY, AMBAR = "#0F1E36", "#C68A12"
PASOS = [
    ("Conocimiento", "vía, hora, quién informa\ny qué se informó"),
    ("Salida", "hora, móvil y\npersonal que acompaña"),
    ("Arribo", "hora, lugar exacto (GPS)\ny constatación"),
    ("En el lugar", "primer interventor,\npersonal presente y acciones"),
    ("Involucrados", "conductores, víctimas,\ntestigos y vehículos"),
    ("Inspección", "ubicación, condiciones,\nrastros y zona probable"),
    ("Fiscalía", "hora, unidad, funcionario\ny disposiciones"),
    ("Cumplimiento", "lo dispuesto, secuestros\ny arribo de equipos"),
    ("Croquis y extras", "croquis, estadística\ny documentos"),
]

fig, ax = plt.subplots(figsize=(12, 6.2), dpi=200)
ax.set_xlim(0, 12); ax.set_ylim(0, 6.2); ax.axis("off")
ax.text(6, 5.9, "Ruta guiada del procedimiento: nueve pasos en el orden en que ocurren", ha="center", fontsize=15, weight="bold", color=NAVY)
for i, (t, d) in enumerate(PASOS):
    col, fila = i % 3, i // 3
    x, y = 0.3 + col * 3.95, 4.0 - fila * 1.85
    ax.add_patch(FancyBboxPatch((x, y), 3.55, 1.5, boxstyle="round,pad=0.02,rounding_size=0.18", fc="#F4F1EA", ec="#D9D2C0", lw=1.2))
    ax.add_patch(plt.Circle((x + 0.48, y + 0.75), 0.33, color=AMBAR))
    ax.text(x + 0.48, y + 0.75, str(i + 1), ha="center", va="center", fontsize=15, weight="bold", color="white")
    ax.text(x + 1.0, y + 1.05, t, fontsize=13, weight="bold", color=NAVY, va="center")
    ax.text(x + 1.0, y + 0.52, d, fontsize=9.6, color="#4A5568", va="center", linespacing=1.3)
    if col < 2:
        ax.annotate("", xy=(x + 3.9, y + 0.75), xytext=(x + 3.6, y + 0.75), arrowprops=dict(arrowstyle="-|>", color="#94A3B8", lw=1.6))
ax.text(6, 0.18, "Cada paso muestra pocas preguntas por pantalla, guarda solo y avisa lo que falta antes de avanzar.",
        ha="center", fontsize=10.5, color="#4A5568", style="italic")
plt.savefig(os.path.join(OUT, "ruta9.png"), bbox_inches="tight", facecolor="white")
print("ok")
