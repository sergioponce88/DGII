"""Figura del circuito del repositorio de protocolos y normativa."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)
NAVY, AZUL, AMBAR, VERDE, VIOLETA = "#0F1E36", "#1D4ED8", "#C68A12", "#15803D", "#7C3AED"


def card(ax, x, y, w, h, t, d, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15", fc=color, ec="none"))
    ax.text(x + w / 2, y + h * 0.66, t, ha="center", va="center", fontsize=11.5, weight="bold", color="white")
    ax.text(x + w / 2, y + h * 0.3, d, ha="center", va="center", fontsize=8.6, color="white", linespacing=1.25)


fig, ax = plt.subplots(figsize=(12, 5.4), dpi=200)
ax.set_xlim(0, 12); ax.set_ylim(0, 5.4); ax.axis("off")
ax.text(6, 5.15, "De la norma al oficial en la calle: circuito del repositorio", ha="center", fontsize=14, weight="bold", color=NAVY)
pasos = [("Fuente", "ley, decreto, acordada,\nresolución, protocolo", AZUL),
         ("Revisión jurídica", "vigencia, alcance\ny versión", AMBAR),
         ("Publicación", "ficha, texto,\nresumen operativo", VERDE),
         ("Aviso", "a quien corresponde:\nnueva o modificada", VERDE),
         ("Consulta", "desde el celular,\nen el lugar del hecho", VIOLETA),
         ("Datos", "qué se consulta,\ndónde y cuándo", NAVY)]
for i, (t, d, c) in enumerate(pasos):
    x = 0.25 + i * 1.97
    card(ax, x, 2.8, 1.75, 1.6, t, d, c)
    if i < 5:
        ax.annotate("", xy=(x + 1.95, 3.6), xytext=(x + 1.77, 3.6), arrowprops=dict(arrowstyle="-|>", color="#94A3B8", lw=1.6))
ax.add_patch(FancyBboxPatch((0.25, 0.6), 11.55, 1.6, boxstyle="round,pad=0.02,rounding_size=0.15", fc="#F4F1EA", ec="#D9D2C0"))
ax.text(6, 1.75, "Cada norma tiene una sola versión vigente, con fecha, fuente oficial y resumen operativo revisado", ha="center",
        fontsize=10.5, weight="bold", color=NAVY)
ax.text(6, 1.05, "Un protocolo derogado o reemplazado no desaparece: queda como histórico, marcado como «sin vigencia», con la fecha y la norma que lo reemplazó.",
        ha="center", fontsize=9, color="#4A5568")
plt.savefig(os.path.join(OUT, "circuito.png"), bbox_inches="tight", facecolor="white")
print("ok")
