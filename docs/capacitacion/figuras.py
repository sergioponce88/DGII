"""Figuras de la propuesta de plataforma de capacitación virtual."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)
NAVY, AZUL, AMBAR, VERDE, VIOLETA = "#0F1E36", "#1D4ED8", "#C68A12", "#15803D", "#7C3AED"


def card(ax, x, y, w, h, t, d, color, tc="white"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15", fc=color, ec="none"))
    ax.text(x + w / 2, y + h * 0.66, t, ha="center", va="center", fontsize=11.5, weight="bold", color=tc)
    ax.text(x + w / 2, y + h * 0.3, d, ha="center", va="center", fontsize=8.6, color=tc, linespacing=1.25)


# Figura 1: circuito de la plataforma
fig, ax = plt.subplots(figsize=(12, 5.2), dpi=200)
ax.set_xlim(0, 12); ax.set_ylim(0, 5.2); ax.axis("off")
ax.text(6, 4.95, "Circuito de la capacitación: de la convocatoria al legajo de formación", ha="center", fontsize=14, weight="bold", color=NAVY)
pasos = [("Plan anual", "cursos, disertaciones,\nfechas y cupos", AZUL),
         ("Convocatoria", "a todo el personal,\npor igual y a tiempo", AZUL),
         ("Inscripción", "con legajo o DNI,\nvalidado en la base", AMBAR),
         ("Cursado", "en vivo, grabado\no presencial", VERDE),
         ("Asistencia\ny evaluación", "registro automático\ny certificado", VERDE),
         ("Legajo de\nformación", "historial de cada\nagente, consultable", VIOLETA)]
for i, (t, d, c) in enumerate(pasos):
    x = 0.25 + i * 1.97
    card(ax, x, 2.6, 1.75, 1.6, t, d, c)
    if i < 5:
        ax.annotate("", xy=(x + 1.95, 3.4), xytext=(x + 1.77, 3.4), arrowprops=dict(arrowstyle="-|>", color="#94A3B8", lw=1.6))
ax.add_patch(FancyBboxPatch((0.25, 0.5), 11.55, 1.5, boxstyle="round,pad=0.02,rounding_size=0.15", fc="#F4F1EA", ec="#D9D2C0"))
ax.text(6, 1.6, "Datos que se generan en cada paso", ha="center", fontsize=11, weight="bold", color=NAVY)
ax.text(6, 1.0, "oferta por tema y región · alcance de la convocatoria · inscriptos y cupos · asistencia real · aprobados · "
        "horas de formación por agente, dependencia y Unidad Regional", ha="center", fontsize=9.2, color="#4A5568", wrap=True)
plt.savefig(os.path.join(OUT, "circuito.png"), bbox_inches="tight", facecolor="white")

# Figura 2: cobertura hoy vs plataforma
fig, ax = plt.subplots(figsize=(12, 4.6), dpi=200)
ax.set_xlim(0, 12); ax.set_ylim(0, 4.6); ax.axis("off")
ax.text(6, 4.35, "Publicidad despareja hoy · convocatoria pareja con la plataforma", ha="center", fontsize=14, weight="bold", color=NAVY)
regs = ["Capital", "U.R. Norte", "U.R. Sur", "U.R. Este", "U.R. Oeste"]
hoy = [1.0, 0.45, 0.35, 0.25, 0.3]
for i, (r, v) in enumerate(zip(regs, hoy)):
    x = 0.6 + i * 1.1
    ax.add_patch(FancyBboxPatch((x, 0.9), 0.75, 2.4 * v, boxstyle="round,pad=0.01,rounding_size=0.06", fc="#CBD5E1", ec="none"))
    ax.text(x + 0.375, 0.6, r, ha="center", fontsize=8.2, color="#4A5568")
ax.text(3.0, 3.75, "HOY: la información llega según la dependencia y el contacto", ha="center", fontsize=10, weight="bold", color="#C2410C")
for i, r in enumerate(regs):
    x = 6.7 + i * 1.1
    ax.add_patch(FancyBboxPatch((x, 0.9), 0.75, 2.4, boxstyle="round,pad=0.01,rounding_size=0.06", fc=AZUL, ec="none"))
    ax.text(x + 0.375, 0.6, r, ha="center", fontsize=8.2, color="#4A5568")
ax.text(9.1, 3.75, "CON LA PLATAFORMA: la misma convocatoria, al mismo tiempo, para todos", ha="center", fontsize=10, weight="bold", color=VERDE)
ax.plot([6.15, 6.15], [0.5, 4.0], color="#D9D2C0", lw=1.2, ls="--")
ax.text(6, 0.15, "Esquema ilustrativo: las alturas no representan datos medidos.", ha="center", fontsize=8.2, color="#4A5568", style="italic")
plt.savefig(os.path.join(OUT, "cobertura.png"), bbox_inches="tight", facecolor="white")
print("ok")
