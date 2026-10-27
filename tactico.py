"""Capa visual «Tactical Next-Gen» de Expedientes DGII.

- CAPA: retoque global (vidrio, bordes sub-píxel, brillos y microinteracciones) sobre los estilos de ui.py.
- tarjeta_expediente_pro(): tarjeta de la Ficha de Expediente con anillo de plazo, indicadores y hoja de ruta compacta.
Solo HTML/CSS (Streamlit no ejecuta JS en st.markdown). No importa `app`.
"""
import pandas as pd
import streamlit as st

import catalogos as C
import db
import ui

CIAN, AMBAR, ROJO, VERDE, VIOLETA = "#22D3EE", "#F59E0B", "#F43F5E", "#34D399", "#A78BFA"

CAPA = """<style>
/* ═══ Capa «Tactical Next-Gen» (Expedientes DGII): sobre los estilos de ui.py, sin cambiar la estructura ═══ */
@keyframes tg-entrada { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
.stApp { background:
  repeating-linear-gradient(0deg, rgba(148,163,184,.025) 0 1px, transparent 1px 32px),
  repeating-linear-gradient(90deg, rgba(148,163,184,.025) 0 1px, transparent 1px 32px),
  radial-gradient(1200px 520px at 50% -10%, rgba(34,211,238,.10), transparent 60%),
  radial-gradient(circle at 50% 0%, #111C38 0%, #070A14 100%) !important; }

.hdr { border-bottom: 0 !important; position: relative; padding-bottom: 12px !important; }
.hdr::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 1px;
  background: linear-gradient(90deg, rgba(34,211,238,.75), rgba(167,139,250,.45) 40%, transparent 85%); }
.hdr h1 { text-shadow: 0 0 24px rgba(34,211,238,.25); }
.hdr img { filter: drop-shadow(0 0 12px rgba(34,211,238,.35)); }

.kpi { background: linear-gradient(180deg, rgba(30,41,59,.55), rgba(15,23,42,.65)) !important;
  border: 1px solid rgba(148,163,184,.10) !important; border-radius: 16px !important;
  backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.05), 0 14px 30px -18px rgba(2,6,23,.9);
  transition: transform .25s cubic-bezier(.2,.8,.2,1), box-shadow .25s, border-color .25s;
  animation: tg-entrada .5s cubic-bezier(.2,.8,.2,1) both; }
.kpi:hover { transform: translateY(-3px); border-color: color-mix(in srgb, var(--k, #22D3EE) 55%, transparent) !important;
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--k, #22D3EE) 30%, transparent),
              0 14px 34px -12px color-mix(in srgb, var(--k, #22D3EE) 55%, transparent); }
.kpi::before { width: 3px !important; box-shadow: 0 0 14px var(--k, #22D3EE); }
.kpi .kv { text-shadow: 0 0 18px color-mix(in srgb, var(--k, #22D3EE) 35%, transparent); font-variant-numeric: tabular-nums; }

.card { background: linear-gradient(160deg, rgba(15,23,42,.78), rgba(7,10,20,.86)) !important;
  border: 1px solid rgba(148,163,184,.10) !important; border-radius: 16px !important; backdrop-filter: blur(12px);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.05), 0 24px 48px -28px rgba(2,6,23,.95) !important;
  transition: transform .25s cubic-bezier(.2,.8,.2,1), box-shadow .25s; animation: tg-entrada .45s cubic-bezier(.2,.8,.2,1) both; }
.card.acc { border-left: 0 !important; box-shadow: inset 3px 0 0 var(--c, #3B82F6), inset 0 1px 0 rgba(255,255,255,.05),
  0 24px 48px -28px rgba(2,6,23,.95) !important; }
.card.acc:hover { transform: translateY(-2px); box-shadow: inset 3px 0 0 var(--c, #3B82F6),
  0 0 0 1px color-mix(in srgb, var(--c, #3B82F6) 35%, transparent),
  0 18px 40px -16px color-mix(in srgb, var(--c, #3B82F6) 55%, transparent) !important; }
.ident { text-shadow: 0 0 20px rgba(34,211,238,.18); }
.chip { backdrop-filter: blur(6px); transition: box-shadow .2s; }
.chip:hover { box-shadow: 0 0 12px -2px currentColor; }

.sec { background: linear-gradient(90deg, rgba(34,211,238,.10), transparent 70%) !important;
  border-left: 3px solid #22D3EE !important; box-shadow: -6px 0 18px -8px rgba(34,211,238,.6); }
.sec h4 { color: #A5F3FC !important; }

.tl { border-left: 0 !important; }
.tl::before { content: ""; position: absolute; left: -1px; top: 6px; bottom: 6px; width: 2px; border-radius: 2px;
  background: linear-gradient(180deg, #22D3EE, rgba(167,139,250,.5), transparent); box-shadow: 0 0 10px rgba(34,211,238,.4); }
.tl .it { background: linear-gradient(160deg, rgba(15,23,42,.72), rgba(7,10,20,.8)) !important;
  border: 1px solid rgba(148,163,184,.10) !important; transition: transform .2s, box-shadow .2s, border-color .2s; }
.tl .it:hover { transform: translateX(3px); border-color: color-mix(in srgb, var(--c, #3B82F6) 50%, transparent) !important;
  box-shadow: 0 10px 26px -14px color-mix(in srgb, var(--c, #3B82F6) 60%, transparent); }
.tl .it::before { box-shadow: 0 0 0 2px var(--c, #3B82F6), 0 0 14px var(--c, #3B82F6) !important; }

.alerta { backdrop-filter: blur(8px); }
[data-testid="stForm"], [data-testid="stExpander"] details {
  background: linear-gradient(160deg, rgba(15,23,42,.72), rgba(7,10,20,.80)) !important;
  border: 1px solid rgba(148,163,184,.10) !important; border-radius: 16px !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.04), 0 18px 40px -28px rgba(2,6,23,.95); }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #0891B2, #2563EB) !important;
  box-shadow: 0 0 16px -4px rgba(34,211,238,.7); }
[data-testid="stDataFrame"], [data-testid="stDataEditor"] { border-radius: 14px; overflow: hidden;
  border: 1px solid rgba(148,163,184,.10); box-shadow: 0 16px 36px -26px rgba(2,6,23,.95); }
.stButton > button, .stDownloadButton > button, div.stFormSubmitButton > button { transition: transform .15s, box-shadow .25s !important; }
.stButton > button:hover, .stDownloadButton > button:hover, div.stFormSubmitButton > button:hover {
  transform: translateY(-1px); box-shadow: 0 0 0 1px rgba(34,211,238,.3), 0 8px 22px -10px rgba(34,211,238,.6) !important; }
div.stFormSubmitButton > button, .stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #0891B2, #2563EB) !important; border: 1px solid rgba(103,232,249,.45) !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #05080F, #03050A) !important;
  border-right: 1px solid rgba(34,211,238,.12) !important; box-shadow: 8px 0 30px -20px rgba(34,211,238,.35); }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
  background: linear-gradient(90deg, rgba(34,211,238,.22), rgba(37,99,235,.10)) !important;
  border: 1px solid rgba(34,211,238,.45) !important; box-shadow: inset 3px 0 0 #22D3EE, 0 0 18px -6px rgba(34,211,238,.6); }

@media (prefers-reduced-motion: reduce) { .kpi, .card, .tl .it { animation: none !important; transition: none !important; } }
/* ═══ Centro de comando: cabecera, indicadores y anillos (visibles en todas las pantallas) ═══ */
@keyframes cmd-giro { to { --cmd-ang: 360deg; } }
@keyframes cmd-barrido { 0% { transform: translateX(-120%); } 55%,100% { transform: translateX(260%); } }
@keyframes cmd-latido { 0%,100% { opacity: 1; box-shadow: 0 0 0 0 rgba(52,211,153,.6); } 50% { opacity: .7; box-shadow: 0 0 0 6px rgba(52,211,153,0); } }
@keyframes cmd-anillo { from { --cmd-val: 0; } }
@property --cmd-ang { syntax: '<angle>'; inherits: false; initial-value: 0deg; }
@property --cmd-val { syntax: '<number>'; inherits: false; initial-value: 0; }

.cmd-hdr { position: relative; isolation: isolate; border-radius: 22px; padding: 1px; margin: 0 0 18px;
  background: conic-gradient(from var(--cmd-ang), transparent 0deg, rgba(34,211,238,.9) 70deg, rgba(167,139,250,.6) 140deg, transparent 220deg);
  animation: cmd-giro 10s linear infinite; box-shadow: 0 30px 60px -32px rgba(2,6,23,.95), 0 18px 40px -24px rgba(8,145,178,.45); }
.cmd-hdr .in { position: relative; overflow: hidden; border-radius: 21px; padding: 18px 24px; display: flex; gap: 18px; align-items: center;
  background: radial-gradient(700px 200px at 0% 0%, rgba(34,211,238,.14), transparent 60%),
              radial-gradient(500px 200px at 100% 100%, rgba(167,139,250,.12), transparent 60%),
              repeating-linear-gradient(90deg, rgba(148,163,184,.04) 0 1px, transparent 1px 26px),
              linear-gradient(160deg, rgba(15,23,42,.94), rgba(7,10,20,.97));
  box-shadow: inset 0 1px 0 rgba(255,255,255,.06); }
.cmd-hdr .in::after { content: ""; position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(105deg, transparent 42%, rgba(255,255,255,.07) 50%, transparent 58%); animation: cmd-barrido 8s ease-in-out infinite; }
.cmd-hdr img { filter: drop-shadow(0 0 14px rgba(34,211,238,.45)); }
.cmd-hdr h1 { margin: 0 !important; padding: 0 !important; font-size: 1.85rem !important; font-weight: 800 !important; letter-spacing: -.5px;
  background: linear-gradient(90deg, #F8FAFC, #A5F3FC 60%, #C4B5FD); -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent; }
.cmd-hdr .sub { margin-top: 4px; color: #94A3B8; font-size: .76rem; letter-spacing: 1.4px; text-transform: uppercase; font-weight: 600; }
.cmd-hdr .meta { margin-left: auto; text-align: right; white-space: nowrap; }
.cmd-hdr .meta b { display: block; color: #E2E8F0; font-size: .85rem; font-weight: 700; }
.cmd-hdr .meta i { display: inline-flex; align-items: center; gap: 6px; font-style: normal; color: #34D399; font-size: .68rem;
  letter-spacing: 1.2px; text-transform: uppercase; font-weight: 800; margin-top: 4px; }
.cmd-hdr .meta i::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: #34D399; animation: cmd-latido 2s infinite; }

.tk-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; margin: 6px 0 18px; }
.tk { position: relative; overflow: hidden; border-radius: 16px; padding: 14px 16px 12px;
  background: radial-gradient(240px 90px at 0% 0%, color-mix(in srgb, var(--k) 18%, transparent), transparent 70%),
              linear-gradient(180deg, rgba(30,41,59,.6), rgba(15,23,42,.7));
  border: 1px solid rgba(148,163,184,.10); backdrop-filter: blur(10px);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.05), 0 14px 30px -18px rgba(2,6,23,.9);
  transition: transform .25s cubic-bezier(.2,.8,.2,1), box-shadow .25s, border-color .25s; animation: tg-entrada .5s both; }
.tk::before { content: ""; position: absolute; left: 14px; right: 14px; top: 0; height: 2px; border-radius: 2px;
  background: linear-gradient(90deg, transparent, var(--k), transparent); box-shadow: 0 0 12px var(--k); }
.tk:hover { transform: translateY(-3px); border-color: color-mix(in srgb, var(--k) 55%, transparent);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--k) 30%, transparent), 0 16px 34px -12px color-mix(in srgb, var(--k) 55%, transparent); }
.tk .l { font-size: .64rem; color: #94A3B8; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; }
.tk .v { font-size: 2rem; font-weight: 800; color: #F8FAFC; line-height: 1.05; margin-top: 6px; font-variant-numeric: tabular-nums;
  text-shadow: 0 0 22px color-mix(in srgb, var(--k) 45%, transparent); }
.tk .n { font-size: .72rem; color: color-mix(in srgb, var(--k) 70%, #E2E8F0); margin-top: 4px; font-weight: 600; }

.cmd-hero { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 14px; margin: 4px 0 18px; }
.cmd-ring { display: flex; gap: 14px; align-items: center; padding: 14px 16px; border-radius: 18px;
  background: linear-gradient(160deg, rgba(15,23,42,.78), rgba(7,10,20,.86)); border: 1px solid rgba(148,163,184,.10);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.05), 0 20px 40px -26px rgba(2,6,23,.95); transition: transform .25s, box-shadow .25s; }
.cmd-ring:hover { transform: translateY(-2px); box-shadow: 0 0 0 1px color-mix(in srgb, var(--c) 35%, transparent), 0 18px 36px -16px color-mix(in srgb, var(--c) 55%, transparent); }
.cmd-ring .g { flex: 0 0 84px; height: 84px; border-radius: 50%; position: relative; display: grid; place-items: center;
  --cmd-val: var(--v); animation: cmd-anillo 1.4s cubic-bezier(.34,1.56,.64,1) both;
  background: conic-gradient(var(--c) calc(var(--cmd-val) * 3.6deg), rgba(148,163,184,.10) 0);
  filter: drop-shadow(0 0 10px color-mix(in srgb, var(--c) 55%, transparent)); }
.cmd-ring .g::before { content: ""; position: absolute; inset: 7px; border-radius: 50%; background: radial-gradient(circle at 50% 30%, #13203A, #070A14 70%); }
.cmd-ring .g b { position: relative; font-size: 1.25rem; font-weight: 800; color: #F8FAFC; }
.cmd-ring .t { font-size: .68rem; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; color: var(--c); }
.cmd-ring .d { font-size: .8rem; color: #CBD5E1; margin-top: 4px; line-height: 1.35; }

[data-testid="stPlotlyChart"] { background: linear-gradient(160deg, rgba(15,23,42,.72), rgba(7,10,20,.82)); border-radius: 18px;
  border: 1px solid rgba(148,163,184,.10); padding: 8px 10px; box-shadow: inset 0 1px 0 rgba(255,255,255,.04), 0 20px 40px -28px rgba(2,6,23,.95); }
@media (max-width: 640px) { .cmd-hdr .in { flex-wrap: wrap; padding: 14px; } .cmd-hdr h1 { font-size: 1.25rem !important; }
  .cmd-hdr .meta { margin-left: 0; text-align: left; } .tk .v { font-size: 1.45rem; } .tk-grid { grid-template-columns: repeat(2, 1fr); gap: 8px; } }
@media (prefers-reduced-motion: reduce) { .cmd-hdr, .cmd-hdr .in::after, .tk, .cmd-ring .g { animation: none !important; } }

</style>"""

CSS_TARJETA = """<style>
@keyframes tx-giro { to { --tx-ang: 360deg; } }
@keyframes tx-barrido { 0% { transform: translateX(-120%); } 60%,100% { transform: translateX(220%); } }
@keyframes tx-pulso { 0%,100% { box-shadow: 0 0 0 0 rgba(244,63,94,.55); } 50% { box-shadow: 0 0 0 6px rgba(244,63,94,0); } }
@keyframes tx-entrada { from { opacity: 0; transform: translateY(10px) scale(.985); } to { opacity: 1; transform: none; } }
@keyframes tx-anillo { from { --tx-val: 0; } }
@property --tx-ang { syntax: '<angle>'; inherits: false; initial-value: 0deg; }
@property --tx-val { syntax: '<number>'; inherits: false; initial-value: 0; }

.tx-card { position: relative; isolation: isolate; border-radius: 22px; padding: 1px; margin: 4px 0 18px;
  background: conic-gradient(from var(--tx-ang), rgba(34,211,238,.0) 0deg, rgba(34,211,238,.85) 60deg,
              rgba(167,139,250,.55) 120deg, rgba(34,211,238,0) 200deg, rgba(34,211,238,0) 360deg);
  animation: tx-entrada .6s cubic-bezier(.2,.8,.2,1) both, tx-giro 9s linear infinite;
  box-shadow: 0 1px 0 rgba(255,255,255,.04) inset, 0 30px 60px -30px rgba(2,6,23,.9),
              0 18px 36px -18px rgba(8,145,178,.35), 0 0 0 1px rgba(148,163,184,.06); }
.tx-in { position: relative; overflow: hidden; border-radius: 21px; padding: 22px 24px 18px;
  background:
    radial-gradient(900px 260px at 0% 0%, rgba(34,211,238,.10), transparent 60%),
    radial-gradient(600px 300px at 100% 100%, rgba(167,139,250,.10), transparent 60%),
    repeating-linear-gradient(0deg, rgba(148,163,184,.035) 0 1px, transparent 1px 28px),
    repeating-linear-gradient(90deg, rgba(148,163,184,.035) 0 1px, transparent 1px 28px),
    linear-gradient(160deg, rgba(15,23,42,.92), rgba(7,10,20,.96));
  backdrop-filter: blur(14px) saturate(140%); -webkit-backdrop-filter: blur(14px) saturate(140%);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.06), inset 0 -40px 80px -40px rgba(34,211,238,.08); }
.tx-in::after { content: ""; position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(105deg, transparent 40%, rgba(255,255,255,.06) 50%, transparent 60%);
  animation: tx-barrido 7s ease-in-out infinite; }

.tx-top { display: grid; grid-template-columns: auto 1fr auto; gap: 22px; align-items: center; }
.tx-foto { width: 96px; height: 96px; border-radius: 20px; position: relative; display: grid; place-items: center;
  font-size: 2rem; font-weight: 800; color: #E0F2FE !important; letter-spacing: 1px;
  background: var(--foto, none) center/cover, linear-gradient(140deg, #0E7490, #312E81);
  box-shadow: 0 0 0 1px rgba(34,211,238,.45), 0 0 24px -4px rgba(34,211,238,.55), inset 0 0 20px rgba(0,0,0,.35); }
.tx-foto.con-foto { color: transparent !important; }
.tx-foto i { position: absolute; right: -6px; bottom: -6px; width: 22px; height: 22px; border-radius: 50%;
  border: 3px solid #0B1222; background: var(--estado); }
.tx-id h2 { margin: 0 !important; font-size: 1.55rem !important; font-weight: 800 !important; letter-spacing: -.3px;
  color: #F8FAFC !important; line-height: 1.15 !important; padding: 0 !important; }
.tx-id .tx-sub { margin-top: 6px; font-size: .78rem; color: #94A3B8 !important; letter-spacing: 1.2px;
  text-transform: uppercase; font-weight: 600; }
.tx-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.tx-chip { font-size: .7rem; font-weight: 700; letter-spacing: .6px; text-transform: uppercase; padding: 4px 10px;
  border-radius: 999px; color: var(--c) !important; background: color-mix(in srgb, var(--c) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--c) 40%, transparent); }
.tx-chip.alerta { animation: tx-pulso 1.8s ease-in-out infinite; }

.tx-iag { --v: 0; width: 132px; height: 132px; border-radius: 50%; position: relative; display: grid; place-items: center;
  --tx-val: var(--v); animation: tx-anillo 1.4s cubic-bezier(.34,1.56,.64,1) both;
  background: conic-gradient(var(--c) calc(var(--tx-val) * 3.6deg), rgba(148,163,184,.10) 0);
  filter: drop-shadow(0 0 14px color-mix(in srgb, var(--c) 55%, transparent)); }
.tx-iag::before { content: ""; position: absolute; inset: 9px; border-radius: 50%;
  background: radial-gradient(circle at 50% 30%, #13203A, #070A14 70%);
  box-shadow: inset 0 0 0 1px rgba(148,163,184,.10), inset 0 8px 24px rgba(0,0,0,.6); }
.tx-iag div { position: relative; text-align: center; }
.tx-iag b { display: block; font-size: 2.1rem; font-weight: 800; line-height: 1; color: #F8FAFC !important;
  text-shadow: 0 0 18px color-mix(in srgb, var(--c) 70%, transparent); }
.tx-iag small { display: block; margin-top: 4px; font-size: .58rem; letter-spacing: 1.6px; font-weight: 700;
  text-transform: uppercase; color: var(--c) !important; }
.tx-iag small.e { margin-top: 1px; font-size: .62rem; letter-spacing: .8px; color: #E2E8F0 !important; max-width: 92px; line-height: 1.15; }

.tx-kpis { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 12px; margin-top: 20px; }
.tx-kpi { position: relative; border-radius: 14px; padding: 12px 14px 12px; overflow: hidden;
  background: linear-gradient(180deg, rgba(30,41,59,.55), rgba(15,23,42,.55));
  border: 1px solid rgba(148,163,184,.10); box-shadow: inset 0 1px 0 rgba(255,255,255,.04);
  transition: transform .25s cubic-bezier(.2,.8,.2,1), box-shadow .25s, border-color .25s; }
.tx-kpi:hover { transform: translateY(-3px); border-color: color-mix(in srgb, var(--c) 55%, transparent);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--c) 35%, transparent), 0 10px 30px -10px color-mix(in srgb, var(--c) 60%, transparent); }
.tx-kpi::before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; background: var(--c);
  box-shadow: 0 0 12px var(--c); }
.tx-kpi .l { font-size: .64rem; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; color: #94A3B8 !important; }
.tx-kpi .v { font-size: 1.55rem; font-weight: 800; margin-top: 2px; color: #F8FAFC !important; font-variant-numeric: tabular-nums; }
.tx-kpi .v em { font-style: normal; font-size: .8rem; color: #64748B !important; margin-left: 3px; font-weight: 700; }
.tx-kpi .p { font-size: .72rem; color: var(--c) !important; font-weight: 600; margin-top: 2px; }
.tx-bar { height: 4px; border-radius: 4px; margin-top: 8px; background: rgba(148,163,184,.12); overflow: hidden; }
.tx-bar div { height: 100%; width: calc(var(--w) * 1%); border-radius: 4px;
  background: linear-gradient(90deg, color-mix(in srgb, var(--c) 40%, transparent), var(--c)); box-shadow: 0 0 10px var(--c); }

.tx-tl { margin-top: 18px; display: grid; grid-template-columns: repeat(3, 1fr); position: relative; gap: 10px; }
.tx-tl::before { content: ""; position: absolute; left: 4%; right: 4%; top: 13px; height: 2px; border-radius: 2px;
  background: linear-gradient(90deg, var(--g1), var(--g2), var(--g3)); opacity: .85; }
.tx-et { position: relative; padding-top: 30px; text-align: center; }
.tx-et .n { position: absolute; top: 4px; left: 50%; transform: translateX(-50%); width: 20px; height: 20px;
  border-radius: 50%; background: #070A14; border: 2px solid var(--c); box-shadow: 0 0 0 4px rgba(7,10,20,1), 0 0 14px var(--c); }
.tx-et.actual .n { background: var(--c); }
.tx-et.futuro .n { border-style: dashed; box-shadow: 0 0 0 4px rgba(7,10,20,1); opacity: .6; }
.tx-et .t { font-size: .72rem; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; color: var(--c) !important; }
.tx-et .d { font-size: .74rem; color: #CBD5E1 !important; margin-top: 2px; }
.tx-et.futuro .t, .tx-et.futuro .d { opacity: .45; }

@media (max-width: 900px) {
  .tx-top { grid-template-columns: auto 1fr; } .tx-iag { grid-column: 1 / -1; justify-self: center; }
  .tx-kpis { grid-template-columns: repeat(2, minmax(0,1fr)); }
}
@media (prefers-reduced-motion: reduce) { .tx-card, .tx-in::after, .tx-chip.alerta, .tx-iag { animation: none !important; } }
.tx-icono { width: 96px; height: 96px; border-radius: 20px; display: grid; place-items: center; font-size: 2.6rem;
  background: linear-gradient(140deg, color-mix(in srgb, var(--c) 55%, #0B1222), #111827);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--c) 60%, transparent), 0 0 26px -4px var(--c), inset 0 0 20px rgba(0,0,0,.35); }
.tx-asunto { margin-top: 10px; font-size: .92rem; color: #E2E8F0 !important; line-height: 1.45; }
.tx-asunto b { color: #F8FAFC !important; }
.tx-in .chip { margin-top: 2px; }
.tx-tl.ruta::before { background: var(--grad); }
.tx-iag small { letter-spacing: .5px !important; font-size: .55rem !important; max-width: 96px; line-height: 1.15; margin-left: auto; margin-right: auto; }
</style>"""


def _anillo(r):
    """(valor 0-100 del anillo, número central, etiqueta, color)."""
    hoy = pd.Timestamp(db.hoy())
    cerrado = r.get("estado") in C.ESTADOS_CERRADOS
    if bool(r.get("tramitado")) or cerrado:
        return 100, "✓", ("Cerrado" if cerrado else "Tramitado"), VERDE
    ing = pd.Timestamp(r["fecha_ingreso"]).normalize() if pd.notna(r.get("fecha_ingreso")) else hoy
    if pd.notna(r.get("fecha_termino")):
        fin = pd.Timestamp(r["fecha_termino"]).normalize()
        total = max((fin - ing).days, 1)
        resta = (fin - hoy).days
        consumido = max(0, min(100, 100 * (hoy - ing).days / total))
        color = ROJO if resta < 0 else (AMBAR if resta <= 2 else CIAN)
        return consumido, resta, ("Días vencido" if resta < 0 else "Días para vencer"), color
    ref = r.get("ult_mov") if pd.notna(r.get("ult_mov")) else r.get("fecha_ingreso")
    d = ui.dias_desde(ref) or 0
    color = ROJO if d > 15 else (AMBAR if d > 7 else VERDE)
    return min(100, d * 100 / 30), d, "Días sin moverse", color


def _ruta(movs, mapa, r):
    """Últimas 5 escalas de la hoja de ruta, en orden cronológico."""
    m = movs.sort_values("fecha_hora").tail(5) if not movs.empty else movs
    escalas = [(row.get("destino") or "—", row.get("fecha_hora"), row.get("tipo")) for _, row in m.iterrows()]
    if not escalas:
        escalas = [(r.get("ubicacion_actual") or C.DEP_PROPIA, r.get("fecha_ingreso"), "INGRESO")]
    n = len(escalas)
    cols = [ui.color_dep(dst, mapa) for dst, _f, _t in escalas]
    stops = ", ".join(f"{c} {int(100 * i / max(n - 1, 1))}%" for i, c in enumerate(cols)) if n > 1 else f"{cols[0]}, {cols[0]}"
    etapas = []
    for i, ((dst, f, tipo), c) in enumerate(zip(escalas, cols)):
        clase = "actual" if i == n - 1 else ""
        etapas.append(f'<div class="tx-et {clase}" style="--c:{c}"><div class="n"></div>'
                      f'<div class="t">{ui.esc(ui.sigla_dep(dst))}</div>'
                      f'<div class="d">{ui.esc("✅ " if tipo == "TRÁMITE" else "")}{ui.fmt_fecha(f)}</div></div>')
    return (f'<div class="tx-tl ruta" style="grid-template-columns:repeat({n},1fr);--grad:linear-gradient(90deg,{stops})">'
            f'{"".join(etapas)}</div>')


def tarjeta_html(r, mapa, movs, n_personal=0, n_cursos=0):
    linea1, linea2 = ui.chips_expediente(r, mapa)
    valor, centro, etiqueta, color = _anillo(r)
    ub = r.get("ubicacion_actual") or "—"
    c_ub = ui.color_dep(ub, mapa)
    dias = ui.dias_desde(r.get("fecha_ingreso"))
    ult = movs["fecha_hora"].max() if not movs.empty else r.get("ult_mov")
    kpis = [
        ("Días desde ingreso", dias if dias is not None else "—", "", ui.fmt_fecha(r.get("fecha_ingreso")), CIAN,
         min(100, (dias or 0) * 100 / 60)),
        ("Movimientos", len(movs), "", f"último {ui.fmt_fecha(ult, True)}", VIOLETA, min(100, len(movs) * 10)),
        ("Dependencias", movs["destino"].nunique() if not movs.empty else 0, "", "destinos recorridos", c_ub,
         min(100, (movs["destino"].nunique() if not movs.empty else 0) * 20)),
        ("Personal afectado", n_personal, "", f"{n_cursos} actividad(es)", VERDE, min(100, n_personal * 10)),
    ]
    kpis_html = "".join(
        f'<div class="tx-kpi" style="--c:{c}"><div class="l">{ui.esc(l)}</div><div class="v">{ui.esc(v)}<em>{ui.esc(u)}</em></div>'
        f'<div class="p">{ui.esc(p)}</div><div class="tx-bar"><div style="--w:{w:.0f}"></div></div></div>'
        for l, v, u, p, c, w in kpis)
    org = r.get("dependencia_origen") or "—"
    asunto = (f'<div class="tx-asunto"><b>{ui.esc(r.get("asunto") or "Sin asunto")}</b><br>'
              f'Origen: {ui.esc(org)}{" · Iniciador: " + ui.esc(r.get("iniciador")) if r.get("iniciador") else ""}</div>')
    icono = "✅" if bool(r.get("tramitado")) else ("🗄️" if r.get("estado") in C.ESTADOS_CERRADOS else "📂")
    return (f'<div class="tx-card"><div class="tx-in"><div class="tx-top">'
            f'<div class="tx-icono" style="--c:{c_ub}">{icono}</div>'
            f'<div class="tx-id"><h2>N° {ui.esc(r.get("nro_exp"))} / F° {ui.esc(r.get("folio"))} / O° {ui.esc(r.get("orden"))}</h2>'
            f'<div class="tx-sub">Año {ui.esc(r.get("anio"))} · Libro {ui.esc(r.get("libro"))} · 📍 {ui.esc(ub)}</div>'
            f'<div style="margin-top:8px">{linea1}</div><div style="margin-top:2px">{linea2}</div>{asunto}</div>'
            f'<div class="tx-iag" style="--v:{valor:.0f};--c:{color}" title="Estado del plazo del expediente">'
            f'<div><b>{ui.esc(centro)}</b><small>{ui.esc(etiqueta)}</small></div></div>'
            f'</div><div class="tx-kpis">{kpis_html}</div>{_ruta(movs, mapa, r)}</div></div>')


def tarjeta_expediente_pro(r, mapa, movs, n_personal=0, n_cursos=0):
    st.markdown(CSS_TARJETA, unsafe_allow_html=True)
    st.markdown(tarjeta_html(r, mapa, movs, n_personal, n_cursos), unsafe_allow_html=True)


_DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
_MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def header_html(img, titulo, sub):
    h = db.ahora() if hasattr(db, "ahora") else pd.Timestamp.now()
    fecha = f"{_DIAS[h.weekday()]} {h.day} de {_MESES[h.month - 1]} · {h:%H:%M}"
    return (f'<div class="cmd-hdr"><div class="in">{img}<div><h1>{ui.esc(titulo)}</h1><div class="sub">{ui.esc(sub)}</div></div>'
            f'<div class="meta"><b>{ui.esc(fecha)}</b><i>Sistema operativo</i></div></div></div>')


def kpis_html(items):
    """items: (etiqueta, valor, nota, color) — mismo formato que ui.kpis."""
    return '<div class="tk-grid">' + "".join(
        f'<div class="tk" style="--k:{c}"><div class="l">{ui.esc(l)}</div><div class="v">{ui.esc(v)}</div>'
        f'<div class="n">{ui.esc(n)}</div></div>' for l, v, n, c in items) + "</div>"


def hero_html(anillos):
    """anillos: (título, valor central, porcentaje 0-100, detalle, color)."""
    return '<div class="cmd-hero">' + "".join(
        f'<div class="cmd-ring" style="--c:{c}"><div class="g" style="--v:{max(0, min(100, p)):.0f}"><b>{ui.esc(v)}</b></div>'
        f'<div><div class="t">{ui.esc(t)}</div><div class="d">{ui.esc(d)}</div></div></div>' for t, v, p, d, c in anillos) + "</div>"
