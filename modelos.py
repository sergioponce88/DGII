"""Modelos de tramitación del oficial: campos del formulario + armado del Word.

Cada Modelo declara sus campos (el formulario se arma solo en vistas/v_tramitar.py) y una
función render(v, ctx) que devuelve el documento. ctx trae: exp (expediente), act (datos de la
actuación/sumario), cfg (configuración), aut (autoridades por clave), hoy.
"""
from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Callable

import docword as W

# ───────────────────────── Estructuras ─────────────────────────
@dataclass
class Campo:
    key: str
    label: str
    tipo: str = "text"  # text | area | int | date | time | select | check | autoridad
    defecto: object = None  # valor o función(ctx)
    opciones: list = field(default_factory=list)
    ayuda: str = ""
    ia: bool = False  # habilita "Revisar redacción"
    requerido: bool = False


@dataclass
class Modelo:
    id: str
    nombre: str
    icono: str
    grupo: str
    descripcion: str
    campos: list
    render: Callable
    accion: str = "NOTA ELEVADA"
    sensible: bool = False  # datos personales: no se envía a IA externa
    hoja: str = "oficio"
    destino: Callable = None  # v -> clave de autoridad destino (para registrar la salida)
    despacho: Callable = None  # v -> despacho del expediente


GRUPOS = ["Notas y pases", "Notificación", "Proyecto", "Actuaciones / Sumario"]

# ───────────────────────── Textos comunes ─────────────────────────
OPINIONES = ["FAVORABLE", "DESFAVORABLE", "NO REÚNE LAS CONDICIONES", "A CONSIDERACIÓN DEL COMANDO SUPERIOR"]
VERBOS = {"SUPERIOR": "elevo", "PAR": "remito", "INTERNO": "pase"}
CIERRE = "Sin otro particular, saludo a Usted con atenta consideración y respeto.-"
CLASES = ["ACTUACIONES ADMINISTRATIVAS", "INFORMACIÓN SUMARIA", "SUMARIO ADMINISTRATIVO", "SUMARIO ADMINISTRATIVO INTERNO"]


def _s(x):
    return "" if x is None else str(x).strip()


def autoridad(ctx, clave):
    return ctx["aut"].get(clave) or {"clave": clave, "cargo": clave, "tratamiento": "Señor", "saludo": "Despacho", "relacion": "PAR"}


def clave_elevacion(ctx):
    return ctx["cfg"].get("elevar_a") or "SUBJEFE"


def referencia(d, ctx, asunto=None):
    e = ctx["exp"]
    sec = ctx["cfg"].get("sec_ref") or "Sec. D.G.I.I."
    txt = f"**Ref.:** Expte. N° {_s(e.get('identificador'))} {sec} — **Asunto:** {_s(asunto or e.get('asunto')) or '—'}.-"
    ini = _s(e.get("dependencia_origen"))
    d.referencia(txt, f"Iniciado por: {ini}" if ini and ini != ctx["cfg"].get("dep_propia") else None)


def intro(ctx, v, objeto="el presente expediente", fin="para su conocimiento e intervención administrativa de competencia"):
    a = autoridad(ctx, v.get("destino"))
    verbo = v.get("verbo") if v.get("verbo") and v.get("verbo") != "automático" else VERBOS.get(a.get("relacion"), "remito")
    car = _s(ctx["cfg"].get("firmante_caracter")) or "en mi carácter de Director General de Institutos e Instrucción"
    fojas = int(v.get("fojas") or 0)
    pre = f"En un cómputo de (- {fojas:02d} -) fojas útiles, " if fojas else ""
    car = car[0].lower() + car[1:] if pre else car[0].upper() + car[1:]
    return f"{pre}{car}, {verbo} a Usted {objeto} {fin}"


def firma_director(d, ctx, v):
    if v.get("firma", True):
        d.firma(_s(ctx["cfg"].get("firmante_nombre")), _s(ctx["cfg"].get("firmante_cargo")) or "Director General de Institutos e Instrucción")


def nota_base(ctx, v, cuerpo, asunto=None, cierre=CIERRE):
    """Nota estándar: fecha, destinatario, referencia, saludo, cuerpo, cierre y firma."""
    d = W.Doc(ctx["cfg"])
    d.fecha(v.get("fecha") or ctx["hoy"])
    d.destinatario(autoridad(ctx, v.get("destino")))
    referencia(d, ctx, asunto)
    d.parrafo("De mi mayor consideración:", sangria=False, despues=8)
    for t in cuerpo:
        if _s(t):
            d.parrafo(t)
    d.parrafo(cierre)
    firma_director(d, ctx, v)
    return d


def parrafos(texto):
    return [p.strip() for p in _s(texto).split("\n") if p.strip()]


def act_txt(ctx, corto=False):
    """'SUMARIO ADMINISTRATIVO N° 379/202/05 Sec. D.G.I.I.; CAUSA: ...; CAUSANTE: ...'"""
    a, e = ctx["act"], ctx["exp"]
    sec = ctx["cfg"].get("sec_ref") or "Sec. D.G.I.I."
    num = _s(a.get("numero")) or _s(e.get("identificador"))
    partes = [f"{_s(a.get('clase')) or 'ACTUACIONES ADMINISTRATIVAS'} N° {num} {sec}"]
    if corto:
        return partes[0]
    for k, lbl in (("causa", "CAUSA"), ("causante", "CAUSANTE"), ("victima", "VÍCTIMA"), ("ocurrido", "OCURRIDO"), ("interviene", "INTERVIENE")):
        if _s(a.get(k)):
            val = _s(a.get(k))
            if k == "causante" and _s(a.get("causante_lp")):
                val += f", L.P. N° {_s(a.get('causante_lp'))}"
            partes.append(f"{lbl}: {val}")
        elif k == "causa" and _s(e.get("asunto")):
            partes.append(f"CAUSA: {_s(e.get('asunto'))}")
    return "; ".join(partes)


def encabezado_acta(ctx, v, titulo):
    a = ctx["act"]
    f = v.get("fecha") or ctx["hoy"]
    h = v.get("hora") or time(10, 0)
    ins_lp, sec_lp = _s(a.get("instructor_lp")), _s(a.get("secretario_lp"))
    return (f"**{titulo}:** En la Ciudad de San Miguel de Tucumán, Departamento Capital, Provincia de Tucumán, República Argentina, "
            f"{W.fecha_letras(f)}, siendo {W.hora_letras(h)}, el funcionario de policía que suscribe "
            f"**{_s(a.get('instructor')) or '________'}**, Legajo Personal número {W.legajo_letras(ins_lp) if ins_lp else '____'}, "
            f"dependiente del Departamento General de Policía, con prestación de servicio en el Instituto de Enseñanza Superior de Policía "
            f"“General José Francisco de San Martín”, cumpliendo la función de {_s(a.get('instructor_funcion')) or 'Instructor'}, "
            f"secundado en este acto por el **{_s(a.get('secretario')) or '________'}**, Legajo Personal número "
            f"{W.legajo_letras(sec_lp) if sec_lp else '____'}, labra la presente a los fines y efectos legales de dejar debidamente "
            f"documentado lo siguiente: ")


CIERRE_ACTA = ("No siendo para más el presente acto, se da por finalizado el mismo, el cual labro, sello y firmo para constancia "
               "juntamente con el Secretario de Actuaciones, lo que **CERTIFICA**.-")


def firmas_instruccion(d, ctx):
    a = ctx["act"]
    d.firmas_dobles((_s(a.get("secretario")), "Secretario de Actuaciones"), (_s(a.get("instructor")), "Instructor"))


def doc_policial(ctx, titulo):
    """Encabezado de piezas de instrucción: POLICÍA DE TUCUMÁN · I.E.S.P. y título."""
    d = W.Doc(ctx["cfg"])
    d.titulo(titulo, tam=12.5)
    return d


# ───────────────────────── Campos reutilizables ─────────────────────────
def C_fecha():
    return Campo("fecha", "Fecha del documento", "date", lambda c: c["hoy"])


def C_fojas():
    return Campo("fojas", "Fojas útiles", "int", lambda c: int(c["exp"].get("fojas") or 0) if str(c["exp"].get("fojas") or "").replace(".0", "").isdigit() else 0,
                 ayuda="0 = no se menciona el cómputo de fojas")


def C_destino(defecto, label="Destinatario"):
    return Campo("destino", label, "autoridad", defecto)


def C_verbo():
    return Campo("verbo", "Verbo", "select", "automático", ["automático", "elevo", "remito", "pase", "sírvase"],
                 ayuda="Automático: elevo a superiores, remito a pares, pase a dependencias internas")


def C_firma():
    return Campo("firma", "Incluir firma del Director", "check", True)


# ───────────────────────── 1. Elevación solicitando autorización ─────────────────────────
def _txt_opinion(v):
    op, mot = v.get("opinion"), _s(v.get("motivo"))
    mot = (" " + mot) if mot and not mot.startswith((",", ".")) else mot
    if op == "FAVORABLE":
        t = f"Es por ello que esta Dirección General es de opinión **FAVORABLE** –salvo mayor y mejor criterio Superior–{mot or ' a lo solicitado'}."
    elif op == "DESFAVORABLE":
        t = f"Es por ello que esta Dirección General es de opinión **DESFAVORABLE** –salvo mayor y mejor criterio Superior–{mot}."
    elif op == "NO REÚNE LAS CONDICIONES":
        t = f"Analizado lo actuado, esta Dirección General considera que la presente solicitud **NO REÚNE LAS CONDICIONES** necesarias para su tratamiento{mot}."
    else:
        t = f"Por lo expuesto, se eleva el presente **A CONSIDERACIÓN DEL COMANDO SUPERIOR**{mot}."
    return t.replace("..", ".")


def r_elevacion(v, ctx):
    cuerpo = [intro(ctx, v) + "."] + parrafos(v.get("fundamento")) + [_txt_opinion(v)]
    if v.get("mision"):
        cuerpo.append("Asimismo, en caso de resultar viable, se solicita que la presente revista el carácter de "
                      "**MISIÓN OFICIAL Y NECESIDAD INSTITUCIONAL**.")
    return nota_base(ctx, v, cuerpo)


def _despacho_opinion(v):
    return "VISTO BUENO" if v.get("opinion") == "FAVORABLE" else "A CONSIDERACIÓN DEL COMANDO SUPERIOR"


ELEVACION = Modelo(
    "elevacion", "Elevación solicitando autorización", "⬆️", "Notas y pases",
    "A Jefatura o Subjefatura (según configuración) con la opinión de la Dirección.",
    [C_fecha(), C_destino(clave_elevacion, "Elevar a"), C_fojas(),
     Campo("fundamento", "Fundamento (qué se solicita, quién, cuándo, dónde)", "area", "", ia=True,
           ayuda="Ej.: Teniéndose en cuenta la invitación de… para que personal de… participe en… desde el… en…"),
     Campo("opinion", "Opinión de la Dirección", "select", "FAVORABLE", OPINIONES),
     Campo("motivo", "Motivo / complemento de la opinión", "area", "", ia=True,
           ayuda="Ej.: , teniéndose en cuenta que los conocimientos adquiridos serán replicados…"),
     Campo("mision", "Solicitar carácter de Misión Oficial y Necesidad Institucional", "check", False),
     C_verbo(), C_firma()],
    r_elevacion, "NOTA ELEVADA", destino=lambda v: v.get("destino"), despacho=_despacho_opinion)


# ───────────────────────── 2. Pases (Escuela Superior, CITTU, Compañía, Gabinete, origen) ─────────────────────────
FINES = {
    "conocimiento": "para su conocimiento e intervención administrativa de competencia",
    "opinion": "a los fines de que realice el análisis correspondiente y brinde opinión de competencia",
    "cumplimiento": "contando con la AUTORIZACIÓN del Comando Superior, para su conocimiento y cumplimiento",
    "gabinete": "a los fines de su intervención profesional de competencia",
    "devolucion": "a los fines de su conocimiento, toda vez que se ha cumplimentado lo requerido por esa instancia",
}


def r_pase(v, ctx):
    fin = FINES.get(v.get("fin"), FINES["conocimiento"])
    cuerpo = [intro(ctx, v, fin=fin) + "."] + parrafos(v.get("detalle"))
    if v.get("cumplido"):
        cuerpo.append(f"**CUMPLIDO**, {_s(v.get('cumplido_txt')) or 'vuelva para trámites ulteriores'}.")
    return nota_base(ctx, v, cuerpo)


def _pase(id_, nombre, icono, desc, destino, fin, cumplido=False, cumplido_txt="", detalle_ayuda="", accion="PASE A DIVISIÓN / ESCUELA"):
    return Modelo(
        id_, nombre, icono, "Notas y pases", desc,
        [C_fecha(), C_destino(destino), C_fojas(),
         Campo("fin", "Finalidad", "select", fin, list(FINES)),
         Campo("detalle", "Indicaciones / detalle (opcional)", "area", "", ia=True, ayuda=detalle_ayuda),
         Campo("cumplido", "Agregar «CUMPLIDO, …»", "check", cumplido),
         Campo("cumplido_txt", "Texto del cumplido", "text", cumplido_txt or "vuelva para trámites ulteriores"),
         C_verbo(), C_firma()],
        r_pase, accion, destino=lambda v: v.get("destino"))


PASE_SUPERIOR = _pase("pase_superior", "Pase a la Escuela Superior", "🏫", "Becas, diplomaturas, disertaciones, talleres y cursos.",
                      "ESC_SUPERIOR", "conocimiento")
PASE_CITTU = _pase("pase_cittu", "Pase al CITTU (práctica de tiro)", "🎯", "Se pide análisis y opinión de competencia.", "CITTU", "opinion",
                   True, "elévense los actuados a esta Dirección General para la prosecución del trámite",
                   "Ej.: Al respecto y de acuerdo al presente proyecto, deberá realizar un análisis del mismo…")
PASE_COMPANIA = _pase("pase_compania", "Pase a Compañía (cumplimiento)", "🪖", "Formación autorizada que vuelve: pase para su cumplimiento.",
                      "COMPANIA", "cumplimiento")
PASE_GABINETE = _pase("pase_gabinete", "Pase al Gabinete Interdisciplinario", "🧠", "Solicitud de intervención del gabinete.",
                      "GABINETE", "gabinete", True, "vuelva para trámites ulteriores")
PASE_ORIGEN = _pase("pase_origen", "Pase a origen / otra dependencia", "↩️", "Devolución al origen o pase a cualquier dependencia.",
                    None, "devolucion")


# ───────────────────────── 3. Solicitud de formación → Relaciones Policiales ─────────────────────────
MOVILIDAD = {"brinda": "la parte solicitante brindará la movilidad para el traslado del personal",
             "no brinda": "la parte solicitante NO brinda movilidad, por lo que deberá preverse el traslado del personal",
             "sin dato": "no se especifica si la parte solicitante brindará movilidad"}


def r_relaciones(v, ctx):
    pers = _s(v.get("personal")) or "los educandos"
    cuerpo = [intro(ctx, v, fin="para su conocimiento e intervención administrativa de competencia, a los fines de que se ponga "
                    "en conocimiento del Comando Superior") + "."] + parrafos(v.get("detalle"))
    viable = v.get("viable") == "VIABLE"
    cuerpo.append(f"Que, en referencia a esta solicitud, esta Dirección General es de opinión que podría ser "
                  f"**{'VIABLE' if viable else 'NO VIABLE'}** –salvo mayor y mejor criterio Superior– la participación de {pers} "
                  f"en este evento; asimismo, se hace constar que {MOVILIDAD[v.get('movilidad') or 'sin dato']}.")
    return nota_base(ctx, v, cuerpo, cierre="Sin otro particular, saludo a Usted con distinguida consideración y respeto.-")


RELACIONES = Modelo(
    "relaciones", "Solicitud de formación → Relaciones Policiales", "🤝", "Notas y pases",
    "Para que ponga en conocimiento del Comando Superior: viabilidad y movilidad.",
    [C_fecha(), C_destino("RELACIONES"), C_fojas(),
     Campo("personal", "Personal solicitado", "text", "los educandos", ayuda="Ej.: cadetes de III° año y Banda de Música"),
     Campo("detalle", "Detalle del pedido (opcional)", "area", "", ia=True),
     Campo("viable", "Opinión", "select", "VIABLE", ["VIABLE", "NO VIABLE"]),
     Campo("movilidad", "Movilidad", "select", "brinda", list(MOVILIDAD)),
     C_verbo(), C_firma()],
    r_relaciones, "NOTA ELEVADA", destino=lambda v: v.get("destino"),
    despacho=lambda v: "VISTO BUENO" if v.get("viable") == "VIABLE" else "A CONSIDERACIÓN DEL COMANDO SUPERIOR")


# ───────────────────────── 4. Sanción disciplinaria (visto bueno) ─────────────────────────
def r_sancion(v, ctx):
    cuerpo = [f"Con el **VISTO BUENO** de esta Dirección General, {('en un cómputo de (- %02d -) fojas útiles, ' % int(v['fojas'])) if int(v.get('fojas') or 0) else ''}"
              f"elevo a Usted adjunto a la presente la **Planilla de Sanción Disciplinaria** del {_s(v.get('sancionado')) or '________'}"
              + (f", impuesta por {_s(v.get('impuesta_por'))}" if _s(v.get("impuesta_por")) else "")
              + (f", consistente en {_s(v.get('sancion'))}" if _s(v.get("sancion")) else "")
              + (f", por infracción a {_s(v.get('infraccion'))}" if _s(v.get("infraccion")) else "")
              + ", a los fines de que sea agregada a su legajo personal y demás efectos que estime corresponder."]
    return nota_base(ctx, v, cuerpo + parrafos(v.get("detalle")))


SANCION = Modelo(
    "sancion", "Sanción disciplinaria: visto bueno y elevación", "⚖️", "Notas y pases",
    "Llega para la firma del Director: se da el visto bueno y se eleva al D-1 o al origen.",
    [C_fecha(), C_destino("D1", "Elevar a (D-1 u origen)"), C_fojas(),
     Campo("sancionado", "Sancionado (grado, apellido y nombre, L.P.)", "text", "", requerido=True),
     Campo("sancion", "Sanción", "text", "", ayuda="Ej.: cinco (05) días de arresto sin perjuicio del servicio"),
     Campo("impuesta_por", "Impuesta por", "text", ""),
     Campo("infraccion", "Infracción", "text", "", ayuda="Ej.: Cap. II Art. 10 Inc. 1° Ap. “b” del R.R.D.P."),
     Campo("detalle", "Detalle adicional (opcional)", "area", ""),
     C_firma()],
    r_sancion, "AUTORIZACIÓN OTORGADA", sensible=True, destino=lambda v: v.get("destino"), despacho=lambda v: "VISTO BUENO")


# ───────────────────────── 5. Notificación (cédula) ─────────────────────────
MOTIVOS_NOTIF = ["Declarar como imputado / causante", "Declarar como testigo", "Tomar conocimiento", "Presentar documentación", "Otro"]


def _txt_cedula(v, ctx, causa):
    f = v.get("fecha") or ctx["hoy"]
    pers = _s(v.get("persona")) or "________"
    plazo, hor = _s(v.get("plazo")) or "48 horas hábiles", _s(v.get("horario")) or "15:00 a 23:00 horas"
    lugar = _s(v.get("lugar")) or "la Instrucción"
    m = v.get("motivo")
    base = f"“SAN MIGUEL DE TUCUMÁN, {W.fecha_larga(f)}. Atento al estado de las presentes actuaciones y apelando a la subsidiariedad del Art. 17 del R.D.C., notifíquese a {pers}, "
    if m == MOTIVOS_NOTIF[0]:
        t = (f"a efectos de que en un término de {plazo} de notificado y en horario de {hor} (Art. 111 RRDP), comparezca por ante {lugar} "
             f"a prestar declaración como imputado (Art. 114 y cc. RRDP) en {causa}. Asimismo, hágase saber que en caso de incomparecencia "
             f"en el término de emplazamiento sin causa justificada será declarado en rebeldía, sin perjuicio de la prosecución de la causa (Art. 112 RRDP).")
    elif m == MOTIVOS_NOTIF[1]:
        t = (f"a efectos de que en un término de {plazo} de notificado y en horario de {hor}, comparezca por ante {lugar} a prestar "
             f"declaración testimonial en {causa}, munido de su Documento Nacional de Identidad.")
    elif m == MOTIVOS_NOTIF[2]:
        t = f"a efectos de que tome conocimiento de lo dispuesto en {causa}: {_s(v.get('detalle'))}"
    elif m == MOTIVOS_NOTIF[3]:
        t = f"a efectos de que en un término de {plazo} de notificado presente por ante {lugar}: {_s(v.get('detalle'))}, en {causa}."
    else:
        t = _s(v.get("detalle"))
    if m in MOTIVOS_NOTIF[:2] and _s(v.get("detalle")):
        t += " " + _s(v.get("detalle"))
    return base + t.rstrip(".") + ". Cúrsese la pertinente Cédula de Notificación.”"


def _cedula(d, v, ctx):
    causa = act_txt(ctx) if ctx["act"] else f"el Expte. N° {_s(ctx['exp'].get('identificador'))} — Asunto: {_s(ctx['exp'].get('asunto'))}"
    d.caja_titulo("CÉDULA DE NOTIFICACIÓN", 13)
    d.parrafo(f"**SR./SRA.:** {_s(v.get('persona')) or '________'}", sangria=False, despues=2)
    d.parrafo(f"**DLIO. LAB.:** {_s(v.get('domicilio')) or 'I.E.S.P. “G.J.F.S.M.” – Muñecas 1025, S. M. de Tucumán'}", sangria=False, despues=2)
    d.parrafo(f"**CAUSA:** {causa}.-", sangria=False, despues=10)
    d.parrafo("Se notifica a Usted del siguiente proveído dictado en autos: " + _txt_cedula(v, ctx, causa))
    d.parrafo("**QUEDA UD. DEBIDAMENTE NOTIFICADO.**", sangria=True, antes=6)
    d.parrafo(f"S. M. de Tucumán, {W.fecha_larga(v.get('fecha') or ctx['hoy'])}.-", sangria=True)
    d.renglones_firma(["NOTIFICADO (firma)", "ACLARACIÓN Y CARÁCTER DEL RECEPTOR", "DNI N° ·  FECHA ___/___/______  ·  HORA ______",
                       "FIRMA DEL NOTIFICADOR", "ACLARACIÓN, JERARQUÍA Y N° DE CARGO"])


def r_notificacion(v, ctx):
    d = W.Doc(ctx["cfg"])
    _cedula(d, v, ctx)
    if v.get("duplicado"):
        d.salto()
        d.parrafo("— DUPLICADO —", sangria=False, alin="c", negrita=True, color=W.GRIS, tam=9)
        _cedula(d, v, ctx)
    return d


NOTIFICACION = Modelo(
    "notificacion", "Cédula de notificación", "📨", "Notificación",
    "Una notificación según lo que pide el expediente: comparecer, tomar conocimiento, presentar documentación.",
    [C_fecha(),
     Campo("persona", "A quién se notifica (grado, apellido y nombre, L.P.)", "text", "", requerido=True),
     Campo("domicilio", "Domicilio laboral / real", "text", "I.E.S.P. “G.J.F.S.M.” – Muñecas 1025, S. M. de Tucumán"),
     Campo("motivo", "Qué se notifica", "select", MOTIVOS_NOTIF[1], MOTIVOS_NOTIF),
     Campo("plazo", "Plazo", "text", "48 horas hábiles"),
     Campo("horario", "Horario", "text", "15:00 a 23:00 horas"),
     Campo("lugar", "Ante quién / dónde", "text", "la Instrucción"),
     Campo("detalle", "Detalle (qué debe conocer o presentar)", "area", "", ia=True),
     Campo("duplicado", "Imprimir con duplicado", "check", True)],
    r_notificacion, "NOTIFICACIÓN REALIZADA", sensible=True)


# ───────────────────────── 6. Proyecto ─────────────────────────
SECCIONES_PROY = [("fundamentacion", "Fundamentación"), ("objetivo", "Objetivo"), ("caracteristicas", "Características generales"),
                  ("responsabilidad", "Responsabilidad"), ("lugar", "Lugar"), ("fecha_proy", "Fecha"), ("anexos", "Anexos")]


def r_proyecto(v, ctx):
    d = W.Doc(ctx["cfg"])
    for _ in range(5):
        d.parrafo(sangria=False)
    d.titulo("PROYECTO", tam=26, subrayar=False, despues=6)
    d.titulo(_s(v.get("titulo")).upper() or "—", tam=16, subrayar=False, despues=40)
    d.parrafo(f"**PROCEDENCIA:** {_s(v.get('procedencia'))}", sangria=False, alin="c")
    if _s(ctx["exp"].get("identificador")):
        d.parrafo(f"**Expte. N°** {_s(ctx['exp'].get('identificador'))} {ctx['cfg'].get('sec_ref') or 'Sec. D.G.I.I.'}", sangria=False, alin="c")
    d.parrafo(f"San Miguel de Tucumán, {W.fecha_larga(v.get('fecha') or ctx['hoy'])}", sangria=False, alin="c")
    d.salto()
    for i, (k, t) in enumerate(SECCIONES_PROY, 1):
        if _s(v.get(k)):
            d.parrafo(f"{i}. {t.upper()}", sangria=False, negrita=True, color=W.NAVY, antes=8, despues=4)
            for p in parrafos(v.get(k)):
                d.parrafo(p)
    return d


PROYECTO = Modelo(
    "proyecto", "Proyecto", "🗂️", "Proyecto",
    "Carátula, fundamentación, objetivo, características, responsabilidad, lugar, fecha y anexos.",
    [C_fecha(), Campo("titulo", "Título del proyecto", "text", lambda c: _s(c["exp"].get("asunto")), requerido=True),
     Campo("procedencia", "Procedencia", "text", "Dirección General de Institutos e Instrucción")]
    + [Campo(k, t, "area" if k not in ("lugar", "fecha_proy") else "text", "", ia=k not in ("lugar", "fecha_proy")) for k, t in SECCIONES_PROY],
    r_proyecto, "INFORME PRODUCIDO")


# ───────────────────────── 7. Actuaciones administrativas / Sumario ─────────────────────────
def r_caratula(v, ctx):
    a = ctx["act"]
    d = W.Doc(ctx["cfg"])
    t = d.d.add_table(rows=2, cols=2)
    t.style = "Table Grid"
    t.alignment = 2
    W.fijar_anchos(t, (W.Cm(1.6), W.Cm(4)))
    for i, k in enumerate(("N°", "Folio")):
        t.cell(i, 0).text, t.cell(i, 1).text = k, ""
    for _ in range(3):
        d.parrafo(sangria=False)
    d.titulo("POLICÍA DE TUCUMÁN", tam=22, subrayar=False, despues=18)
    d.caja_titulo("PROCEDENCIA")
    d.parrafo("INSTITUTO DE ENSEÑANZA SUPERIOR DE POLICÍA “GRL. JOSÉ FRANCISCO DE SAN MARTÍN” – DIRECCIÓN GENERAL DE INSTITUTOS E INSTRUCCIÓN",
              sangria=False, alin="c", negrita=True, despues=24)
    d.caja_titulo("ASUNTO")
    d.parrafo(f"“{act_txt(ctx).upper()}”.-", sangria=False, alin="c", negrita=True, despues=24)
    if _s(a.get("interviene")):
        d.caja_titulo("INTERVIENE")
        d.parrafo(_s(a.get("interviene")).upper(), sangria=False, alin="c", negrita=True)
    return d


def r_acta_apertura(v, ctx):
    d = doc_policial(ctx, "ACTA DE APERTURA")
    titulo = f"ACTA DE APERTURA DE {_s(ctx['act'].get('clase')) or 'ACTUACIONES ADMINISTRATIVAS'}"
    d.parrafo(encabezado_acta(ctx, v, titulo) + f"Que de acuerdo a {act_txt(ctx)}, iniciadas a raíz de que " + _s(v.get("relato"))
              + " Por tal motivo se labra la presente a los fines de que sirva de Acta de Apertura de las presentes actuaciones a instruirse, "
                "con el fin de establecer la responsabilidad administrativa que en dicha faz le cupiere, en el marco de la reglamentación policial vigente. "
              + CIERRE_ACTA)
    firmas_instruccion(d, ctx)
    return d


PROV_TIPOS = ["Recepción, designación de secretario y recaratulación", "Adjunta documentación", "Cursa notificaciones / cita a declarar", "Libre"]


def r_providencia(v, ctx):
    a = ctx["act"]
    d = W.Doc(ctx["cfg"], hoja="media", membrete=False)
    d.parrafo(f"San Miguel de Tucumán, {W.fecha_larga(v.get('fecha') or ctx['hoy'])}", sangria=False, alin="r", negrita=True, despues=8)
    tipo, det = v.get("tipo"), _s(v.get("detalle"))
    clase = _s(a.get("clase")) or "ACTUACIONES ADMINISTRATIVAS"
    if tipo == PROV_TIPOS[0]:
        t = (f"Por recepcionado el presente **{clase}**, me doy por notificado de mi designación como instructor y en término asignado. "
             f"En consecuencia, designo como secretario de actuaciones al **{_s(a.get('secretario')) or '________'}**, quien juntamente conmigo "
             f"suscribirá esta y demás diligencias a practicarse.")
        if v.get("recaratular"):
            t += f" Asimismo, se procede a **RECARATULAR** estos obrados como **{act_txt(ctx, corto=True).rstrip('.')}**."
    elif tipo == PROV_TIPOS[1]:
        t = f"Atento al estado de las presentes actuaciones y apelando a la subsidiariedad del Art. 160 del R.D.P., se adjunta a estos actuados {det}."
    elif tipo == PROV_TIPOS[2]:
        t = (f"Atento al estado de las presentes actuaciones y apelando a la subsidiariedad del Art. 17 del R.D.C., a los fines de continuar con "
             f"la investigación administrativa se procede a cursar notificaciones {det}.")
    else:
        t = det
    d.parrafo(t.replace("..", ".").replace(".**.", ".**") + " **CONSTE**.-")
    d.firma(_s(a.get("instructor")), "Instructor", lado="r")
    return d


def r_valoracion(v, ctx):
    a = ctx["act"]
    d = doc_policial(ctx, "VALORACIÓN OBJETIVA")
    d.parrafo("ANÁLISIS VALORATIVO DE LO ACTUADO HASTA EL MOMENTO EN LAS PRESENTES DILIGENCIAS ADMINISTRATIVAS", sangria=False, alin="c", tam=10, color=W.GRIS)
    d.parrafo("**VISTO:**", sangria=False, antes=6)
    d.parrafo(f"El contenido de las presentes actuaciones administrativas internas: {act_txt(ctx)}, y…")
    d.parrafo("**CONSIDERANDO:**", sangria=False, antes=6)
    for p in parrafos(v.get("considerando")):
        d.parrafo(p)
    d.parrafo("Por lo expuesto, esta Instancia", sangria=True)
    d.parrafo("**RESUELVE:**", sangria=False, antes=4)
    arts = []
    car = v.get("caracter")
    norma = {"INFORMACIÓN SUMARIA": "el Art. 196, inc. “a”, del R.R.D.P.", "SUMARIO ADMINISTRATIVO": "el Art. 101 del R.R.D.P."}.get(car, "la reglamentación")
    if car == "ARCHIVO":
        arts.append("PROCEDER al **ARCHIVO** de las presentes actuaciones, por no surgir responsabilidad administrativa.")
    else:
        arts.append(f"Que las presentes actuaciones deben tomar el carácter de **“{car}”**, conforme a la valoración objetiva que antecede, "
                    f"en concordancia con lo dispuesto por {norma} en vigencia, con el único objeto de investigar la conducta del causante.")
        if _s(a.get("causante")):
            arts.append(f"Consignar como **CAUSANTE ADMINISTRATIVO** al {_s(a.get('causante'))}"
                        + (f", identificado con el Legajo Personal N° {_s(a.get('causante_lp'))}" if _s(a.get("causante_lp")) else "") + ".")
        if v.get("designar"):
            arts.append(f"Designar al {_s(a.get('instructor'))} como **INSTRUCTOR** de las presentes actuaciones administrativas"
                        + (f", {_s(v.get('fundamento_instructor'))}" if _s(v.get("fundamento_instructor")) else "") + ".")
    dest = autoridad(ctx, v.get("destino"))
    arts.append(f"**ELEVAR** lo actuado al Sr. {dest.get('cargo')}, para su intervención de competencia.")
    for i, t in enumerate(arts, 1):
        d.parrafo(f"**Artículo {i}°.-** {t}", sangria=False)
    d.parrafo(f"SAN MIGUEL DE TUCUMÁN, {W.fecha_larga(v.get('fecha') or ctx['hoy']).upper()}.-", sangria=False, alin="r", negrita=True, antes=8)
    d.firma(_s(a.get("instructor")) or _s(ctx["cfg"].get("firmante_nombre")), "Instructor")
    return d


def _datos_persona(v):
    partes = [f"**{_s(v.get('nombre')).upper() or '________'}**", _s(v.get("nacionalidad")) or "argentino/a", "instruido/a",
              _s(v.get("estado_civil")) or "soltero/a"]
    if _s(v.get("edad")):
        partes.append(f"de {_s(v.get('edad'))} años de edad")
    if _s(v.get("dni")):
        partes.append(f"DNI N° {_s(v.get('dni'))}")
    if _s(v.get("domicilio")):
        partes.append(f"domiciliado/a en {_s(v.get('domicilio'))}")
    if _s(v.get("telefono")):
        partes.append(f"Cel.: {_s(v.get('telefono'))}")
    if _s(v.get("padres")):
        partes.append(f"hijo/a de {_s(v.get('padres'))}")
    return ", ".join(partes)


CAMPOS_PERSONA = [
    Campo("nombre", "Apellido y nombre", "text", "", requerido=True),
    Campo("condicion", "Condición (grado / cadete de … año, L.P.)", "text", ""),
    Campo("nacionalidad", "Nacionalidad", "text", "argentino/a"),
    Campo("estado_civil", "Estado civil", "text", "soltero/a"),
    Campo("edad", "Edad", "text", ""),
    Campo("dni", "DNI", "text", ""),
    Campo("domicilio", "Domicilio", "text", ""),
    Campo("telefono", "Teléfono", "text", ""),
    Campo("padres", "Hijo/a de (padre y madre, (v)/(f))", "text", ""),
]


def r_testigo(v, ctx):
    d = doc_policial(ctx, "DECLARACIÓN TESTIMONIAL")
    d.parrafo(f"{_s(v.get('nombre')).upper()} — {_s(v.get('condicion'))}", sangria=False, alin="c", negrita=True, despues=8)
    cadete = (" y por ser un cadete, también de la falta GRAVE que contempla el Capítulo II, Artículo 12, Inciso “m” del R.R.D.P. que dice: "
              "“AFIRMAR UNA FALSEDAD, NEGAR O CALLAR LA VERDAD EN TODO O EN PARTE EN LAS DECLARACIONES, INFORMES O TRADUCCIONES QUE SE "
              "PRESTEN COMO TESTIGOS, PERITOS O TRADUCTORES ANTE LA INSTRUCCIÓN DEL SUMARIO ADMINISTRATIVO O INFORMACIONES SUMARIAS "
              "ADMINISTRATIVAS”") if v.get("es_cadete") else ""
    f, h = v.get("fecha") or ctx["hoy"], v.get("hora") or time(10, 0)
    d.parrafo(f"En la ciudad de San Miguel de Tucumán, Departamento Capital, Provincia de Tucumán, {W.fecha_letras(f)}, siendo "
              f"{W.hora_letras(h)}, se hace comparecer por ante esta Instrucción a una persona que fuera previamente citada para ello, a los "
              f"fines de que preste **DECLARACIÓN ADMINISTRATIVA DE CARÁCTER INFORMATIVO** en {act_txt(ctx)}. Invitado al acto accedió de "
              f"conformidad e instruido conforme lo normado en el Artículo 17 del Reglamento del Cadete (R.D.C.), como así también del "
              f"Artículo 129 del R.R.D.P. vigente, de las penas de falso testimonio{cadete}, y previo juramento que prestó en legal forma de "
              f"decir verdad de todo cuanto supiere y le fuere preguntado, dijo “SÍ, JURO”. Interrogado por sus datos personales dijo llamarse: "
              f"{_datos_persona(v)}. Conforme el Artículo 131 del R.R.D.P., preguntado si conoce a las partes y si con respecto a ellas le "
              f"comprenden las generales de la ley que en este acto le son explicadas, **RESPONDE:** {_s(v.get('generales')) or 'NO TENGO IMPEDIMENTO ALGUNO EN DECLARAR'}. "
              f"Preguntado por el hecho que se investiga, **DECLARA:** {_s(v.get('relato'))}")
    for p in parrafos(v.get("preguntas")):
        d.parrafo(p)
    d.parrafo("No siendo para más, se da por finalizado el acto, previa lectura y ratificación de su contenido, firmando el declarante "
              "por ante mí y el Secretario de Actuaciones, lo que **CERTIFICA**.-")
    d.firma(_s(v.get("nombre")).upper(), "Declarante", lado="c")
    firmas_instruccion(d, ctx)
    return d


def r_causante(v, ctx):
    a = ctx["act"]
    d = doc_policial(ctx, "DECLARACIÓN ADMINISTRATIVA DEL CAUSANTE")
    d.parrafo(f"{_s(v.get('nombre')).upper()} — {_s(v.get('condicion'))}", sangria=False, alin="c", negrita=True, despues=8)
    f, h = v.get("fecha") or ctx["hoy"], v.get("hora") or time(10, 0)
    t = (f"En la ciudad de San Miguel de Tucumán, Departamento Capital, Provincia de Tucumán, República Argentina, {W.fecha_letras(f)}, "
         f"siendo {W.hora_letras(h)}, se hace comparecer por ante esta Instrucción a una persona que debe prestar declaración administrativa "
         f"como imputado en autos. Preguntado por sus nombres y demás condiciones personales dijo llamarse: {_datos_persona(v)}"
         + (f", quien actualmente es {_s(v.get('condicion'))}" if _s(v.get("condicion")) else "") +
         ". Seguidamente y apelando a la subsidiariedad prevista por el Art. 17 del R.D.C., conforme lo estipulado por el Art. 114 del R.R.D.P. "
         "vigente, se le hacen conocer los derechos que le asisten, consistentes en: a) Exigir que se le haga conocer los hechos y las faltas que "
         "se le atribuyen; b) Ofrecer la prueba de que pretenda valerse, la que se ajustará a las normas del presente Reglamento; c) Dictar por sí "
         "su declaración; y d) Rubricar cada una de las hojas de su declaración, o pedir que lo haga el instructor. Asimismo, se le hace conocer que "
         "podrá ejercer los derechos señalados precedentemente con arreglo a las demás normas que prescribe este Reglamento, hasta el momento en que "
         "se le corra traslado para ejercer el derecho de defensa. También se le hace conocer que, conforme al Art. 118 del R.R.D.P., podrá negarse "
         f"a declarar sin que ello signifique presunción en su contra. Acto seguido se le pone en conocimiento que en este Instituto se instruye "
         f"{act_txt(ctx)}. Seguidamente se le hace conocer que se le atribuye el hecho que {_s(v.get('hecho')) or _s(a.get('hecho'))}")
    d.parrafo(t)
    if v.get("declara") == "Se niega a declarar (Art. 118 R.R.D.P.)":
        d.parrafo("Preguntado si va a declarar, **RESPONDE:** QUE NO ES SU DESEO DECLARAR, haciendo uso del derecho que le confiere el Art. 118 del R.R.D.P.")
    else:
        d.parrafo(f"Preguntado si va a declarar, **RESPONDE:** QUE SÍ. **DECLARA:** {_s(v.get('relato'))}")
        for p in parrafos(v.get("preguntas")):
            d.parrafo(p)
    d.parrafo("No siendo para más, se da por finalizado el acto, previa lectura y ratificación, firmando el compareciente por ante mí "
              "y el Secretario de Actuaciones, lo que **CERTIFICA**.-")
    d.firma(_s(v.get("nombre")).upper(), "Causante", lado="c")
    firmas_instruccion(d, ctx)
    return d


def r_visu(v, ctx):
    d = doc_policial(ctx, "ACTA DE INSPECCIÓN OCULAR")
    d.parrafo(encabezado_acta(ctx, v, "ACTA DE INSPECCIÓN OCULAR") + f"Que de acuerdo a {act_txt(ctx)}, " + _s(v.get("descripcion")) + " " + CIERRE_ACTA)
    firmas_instruccion(d, ctx)
    return d


def r_defensa(v, ctx):
    a = ctx["act"]
    d = doc_policial(ctx, "ACTA PARA NOTIFICAR DERECHO DE DEFENSA")
    ini = v.get("inicio") or ctx["hoy"]
    dias = int(v.get("dias") or 5)
    fin = W.dias_habiles(ini, dias)
    t = (encabezado_acta(ctx, v, "ACTA PARA NOTIFICAR DERECHO DE DEFENSA") +
         f"Que en la fecha y hora indicada, previamente citado, comparece en el término de emplazamiento por ante esta Instrucción el "
         f"{_s(v.get('condicion')) or _s(a.get('causante'))}: {_datos_persona(v)}, a quien se le hace conocer que, atento a las Conclusiones "
         f"Definitivas de fojas {_s(v.get('fojas_concl')) or '___'}, la instrucción considera que el causante termina encuadrando su conducta "
         f"en las normas previstas en {_s(v.get('encuadre')) or '________'}. Seguidamente, conforme lo prevé la citada normativa, se procede a "
         f"correrle traslado para que ejercite su Derecho de Defensa por el término de {dias:02d} ({W.letras(dias)}) días hábiles, los que, ante "
         f"la inexistencia de notificación expresa, comenzarán a computarse a partir de las cero horas del día {W.fecha_corta(ini)} y culminan a "
         f"horas veinticuatro del día {W.fecha_corta(fin)}. Asimismo, se le hace conocer que conforme lo prescripto por el Art. 140 del citado "
         f"cuerpo legal, si no ejercita tal derecho en el término citado se le dará por decaído el mismo. Conforme lo previsto por el Art. 147 del "
         f"R.R.D.P., podrá defenderse por sí o designar un oficial para que lo represente y ejercite su derecho de defensa, debiendo recaer tal "
         f"designación sobre un oficial de la jerarquía de Subayudante a Principal y perteneciente al mismo escalafón que el imputado. El oficial "
         f"defensor no podrá pertenecer al personal de Asesoría Letrada de la Jefatura o Unidad Regional, al Departamento Judicial D-5 ni a la "
         f"dependencia específica que tiene a su cargo la instrucción del sumario administrativo (Art. 148 R.R.D.P.). Habiendo el compareciente "
         f"tomado vista de lo actuado y conocimiento del traslado para ejercitar su Derecho de Defensa, se da por notificado y dice: ")
    resp = {"Ejercerá su derecho de defensa": "“ES MI DESEO EJERCER EL DERECHO DE DEFENSA”.",
            "Renuncia al derecho de defensa": "“NO ES MI DESEO EJERCER EL DERECHO DE DEFENSA, POR LO QUE RENUNCIO AL MISMO”."}
    d.parrafo(t + "**" + resp.get(v.get("respuesta"), resp["Ejercerá su derecho de defensa"]) + "** " +
              "Por lo que, no siendo para más, se da por finalizado el acto, el cual labro, sello y firmo juntamente con el compareciente y el "
              "actuario para constancia, lo que **CERTIFICA**.-")
    d.firma(_s(v.get("nombre")).upper(), "Compareciente", lado="c")
    firmas_instruccion(d, ctx)
    return d


def r_analisis(v, ctx):
    d = doc_policial(ctx, f"EXAMEN N° {int(v.get('numero') or 1):02d}")
    d.parrafo(f"**{_s(v.get('dirigido')).upper()}:**", sangria=False, despues=8)
    d.parrafo(f"Analizando el contenido de {act_txt(ctx)}, de cuyo estudio surge:")
    for p in parrafos(v.get("analisis")):
        d.parrafo(p)
    a = ctx["act"]
    caus = f"{_s(a.get('causante'))}" + (f", Legajo Personal N° {_s(a.get('causante_lp'))}" if _s(a.get("causante_lp")) else "")
    if v.get("resultado") == "Surge responsabilidad administrativa":
        d.parrafo(f"En virtud de ello y de lo obrado en autos, **surge responsabilidad administrativa** por parte del {caus}, considerando esta "
                  f"Instrucción que el mismo con su conducta incurrió en lo establecido en {_s(v.get('encuadre')) or '________'}.")
    else:
        d.parrafo(f"En virtud de ello y de lo obrado en autos, **no surge responsabilidad administrativa** por parte del {caus}, considerando esta "
                  f"Instrucción que el mismo con su conducta no incurrió en ninguna falta normada en el R.I.E.C. y R.R.D.P., quedando exento de toda responsabilidad.")
    d.parrafo(f"SAN MIGUEL DE TUCUMÁN, {W.fecha_larga(v.get('fecha') or ctx['hoy']).upper()}.-", sangria=False, alin="r", negrita=True, antes=6)
    d.firma(_s(a.get("instructor")), "Instructor")
    return d


def r_conclusiones(v, ctx):
    a = ctx["act"]
    d = doc_policial(ctx, "CONCLUSIONES DEFINITIVAS")
    d.parrafo("**VISTO:**", sangria=False)
    d.parrafo(f"El contenido de {act_txt(ctx)}, y…")
    d.parrafo("**CONSIDERANDO:**", sangria=False, antes=6)
    for p in parrafos(v.get("considerando")):
        d.parrafo(p)
    d.parrafo("Por ello…", sangria=True)
    d.parrafo("**RESUELVO:**", sangria=False, antes=4)
    for i, t in enumerate(parrafos(v.get("resuelvo")), 1):
        d.parrafo(f"**ARTÍCULO {i}°:** {t}", sangria=False)
    d.parrafo(f"SAN MIGUEL DE TUCUMÁN, {W.fecha_larga(v.get('fecha') or ctx['hoy']).upper()}.-", sangria=False, alin="r", negrita=True, antes=6)
    d.firma(_s(a.get("instructor")), "Instructor")
    return d


def r_elev_actuacion(v, ctx):
    cuerpo = [intro(ctx, v, objeto=f"las presentes {act_txt(ctx)}", fin="para su conocimiento e intervención de competencia") + "."]
    cuerpo += parrafos(v.get("resumen"))
    return nota_base(ctx, v, cuerpo, asunto=act_txt(ctx))


def _fh():
    return [C_fecha(), Campo("hora", "Hora", "time", time(10, 0))]


ACT = "Actuaciones / Sumario"
CARATULA = Modelo("caratula", "Carátula", "📁", ACT, "Con los datos de la actuación.", [], r_caratula, "INFORME PRODUCIDO", sensible=True)
ACTA_APERTURA = Modelo("acta_apertura", "Acta cabeza (apertura)", "📝", ACT, "Acta de apertura de las actuaciones.",
                       _fh() + [Campo("relato", "Relato del hecho (iniciadas a raíz de que…)", "area", lambda c: _s(c["act"].get("hecho")), ia=True, requerido=True)],
                       r_acta_apertura, "INFORME PRODUCIDO", sensible=True)
PROVIDENCIA = Modelo("providencia", "Providencia (hoja chica)", "📄", ACT, "Recepción y designación, adjunta documentación, notificaciones.",
                     [C_fecha(), Campo("tipo", "Tipo de providencia", "select", PROV_TIPOS[0], PROV_TIPOS),
                      Campo("recaratular", "Recaratular", "check", True),
                      Campo("detalle", "Detalle (qué se adjunta / a quién se notifica / texto libre)", "area", "", ia=True)],
                     r_providencia, "PROVIDENCIA / DESPACHO FIRMADO", sensible=True, hoja="media")
VALORACION = Modelo("valoracion", "Valoración objetiva", "🔍", ACT, "Visto, considerando y resuelve: carácter, causante, instructor y elevación.",
                    [C_fecha(), Campo("considerando", "Considerando (un párrafo por renglón: «Que a foja N°…»)", "area",
                                      lambda c: f"Que las presentes actuaciones de índole administrativa dieron inicio a raíz de que {_s(c['act'].get('hecho'))}", ia=True),
                     Campo("caracter", "Carácter que toman", "select", "SUMARIO ADMINISTRATIVO", ["INFORMACIÓN SUMARIA", "SUMARIO ADMINISTRATIVO", "ARCHIVO"]),
                     Campo("designar", "Designar instructor", "check", True),
                     Campo("fundamento_instructor", "Fundamento de la designación (opcional)", "text", ""),
                     C_destino(clave_elevacion, "Elevar a")],
                    r_valoracion, "INFORME PRODUCIDO", sensible=True)
TESTIGO = Modelo("testigo", "Declaración de testigo", "🗣️", ACT, "Declaración administrativa de carácter informativo.",
                 _fh() + CAMPOS_PERSONA + [Campo("es_cadete", "Es cadete (agrega Art. 12 inc. «m» R.R.D.P.)", "check", True),
                                           Campo("generales", "Generales de la ley", "text", "NO TENGO IMPEDIMENTO ALGUNO EN DECLARAR"),
                                           Campo("relato", "Declaración", "area", "", ia=True, requerido=True),
                                           Campo("preguntas", "Preguntas y respuestas (opcional)", "area", "", ia=True)],
                 r_testigo, "INFORME PRODUCIDO", sensible=True)
CAUSANTE = Modelo("causante", "Declaración del causante", "👤", ACT, "Declaración administrativa como imputado (Art. 114 R.R.D.P.).",
                  _fh() + CAMPOS_PERSONA + [Campo("hecho", "Hecho que se le atribuye", "area", lambda c: _s(c["act"].get("hecho")), ia=True),
                                            Campo("declara", "¿Declara?", "select", "Declara", ["Declara", "Se niega a declarar (Art. 118 R.R.D.P.)"]),
                                            Campo("relato", "Declaración", "area", "", ia=True),
                                            Campo("preguntas", "Preguntas y respuestas (opcional)", "area", "", ia=True)],
                  r_causante, "INFORME PRODUCIDO", sensible=True)
VISU = Modelo("visu", "Inspección de visu (ocular)", "👁️", ACT, "Si corresponde.",
              _fh() + [Campo("descripcion", "Qué se inspecciona y qué se constata", "area", "", ia=True, requerido=True)],
              r_visu, "INFORME PRODUCIDO", sensible=True)
DEFENSA = Modelo("defensa", "Defensa (derecho de defensa)", "🛡️", ACT, "Acta para notificar el derecho de defensa (Art. 140, 147 y 148 R.R.D.P.).",
                 _fh() + CAMPOS_PERSONA[:1] + [Campo("condicion", "Condición (grado / cadete de … año, L.P.)", "text", lambda c: _s(c["act"].get("causante")))] + CAMPOS_PERSONA[2:]
                 + [Campo("fojas_concl", "Fojas de las Conclusiones Definitivas", "text", ""),
                    Campo("encuadre", "Encuadre (artículos e incisos)", "area", "", ia=True),
                    Campo("inicio", "Inicio del plazo", "date", lambda c: c["hoy"]),
                    Campo("dias", "Días hábiles", "int", 5),
                    Campo("respuesta", "Respuesta del causante", "select", "Ejercerá su derecho de defensa",
                          ["Ejercerá su derecho de defensa", "Renuncia al derecho de defensa"])],
                 r_defensa, "NOTIFICACIÓN REALIZADA", sensible=True)
ANALISIS = Modelo("analisis", "Análisis (examen al Asesor Letrado)", "🧾", ACT, "Examen de lo actuado para el Asesor Letrado.",
                  [C_fecha(), Campo("numero", "Examen N°", "int", 1),
                   Campo("dirigido", "Dirigido a", "text", "Sr. Asesor Letrado del I.E.S.P. “G.J.F.S.M.”"),
                   Campo("analisis", "Análisis (un párrafo por renglón)", "area", "", ia=True, requerido=True),
                   Campo("resultado", "Resultado", "select", "Surge responsabilidad administrativa",
                         ["Surge responsabilidad administrativa", "No surge responsabilidad administrativa"]),
                   Campo("encuadre", "Encuadre (si surge responsabilidad)", "area", "", ia=True)],
                  r_analisis, "INFORME PRODUCIDO", sensible=True)
CONCLUSIONES = Modelo("conclusiones", "Conclusiones definitivas", "✅", ACT, "Visto, considerando y resuelvo (un artículo por renglón).",
                      [C_fecha(), Campo("considerando", "Considerando (un párrafo por renglón)", "area", "", ia=True, requerido=True),
                       Campo("resuelvo", "Resuelvo (un artículo por renglón)", "area",
                             lambda c: "PROCEDER al ARCHIVO de estos actuados, por no encontrar responsable administrativo.\n"
                                       "Cumplido, elévese el presente al Señor Director General de Institutos e Instrucción.", ia=True)],
                      r_conclusiones, "INFORME PRODUCIDO", sensible=True)
ELEV_ACT = Modelo("elev_actuacion", "Elevación de las actuaciones", "📤", ACT, "Eleva lo actuado a Jefatura / Subjefatura.",
                  [C_fecha(), C_destino(clave_elevacion, "Elevar a"), C_fojas(),
                   Campo("resumen", "Resumen / pedido (opcional)", "area", "", ia=True), C_verbo(), C_firma()],
                  r_elev_actuacion, "NOTA ELEVADA", sensible=True, destino=lambda v: v.get("destino"))

MODELOS = {m.id: m for m in [ELEVACION, PASE_SUPERIOR, PASE_CITTU, RELACIONES, PASE_COMPANIA, PASE_GABINETE, SANCION, PASE_ORIGEN,
                              NOTIFICACION, PROYECTO, CARATULA, ACTA_APERTURA, PROVIDENCIA, VALORACION, TESTIGO, CAUSANTE, VISU,
                              DEFENSA, ANALISIS, CONCLUSIONES, ELEV_ACT]}

# Pasos de las actuaciones según su origen (lo explicado por el usuario)
PASOS_INTERNA = ["caratula", "acta_apertura", "providencia", "valoracion", "testigo", "notificacion", "visu", "defensa", "analisis", "conclusiones"]
PASOS_EXTERNA = ["notificacion", "causante", "testigo", "analisis", "elev_actuacion"]
PASOS_SUMARIO = ["providencia", "notificacion", "causante", "testigo", "visu", "analisis", "defensa", "conclusiones", "elev_actuacion"]

# Sugerencias por tipo de expediente
SUGERIDOS = [
    (("SUMARIO", "INFORMACIÓN SUMARIA", "ACTUACIONES ADMINISTRATIVAS"), []),  # usan el flujo de actuaciones
    (("DICTAR CURSO",), ["elevacion", "pase_superior"]),
    (("REALIZAR CURSO", "BECA", "DIPLOMATURA", "DISERTACIÓN", "TALLER", "SEMINARIO", "CONGRESO"), ["pase_superior", "elevacion"]),
    (("PRÁCTICA DE TIRO",), ["pase_cittu", "elevacion"]),
    (("SOLICITUD DE FORMACIÓN",), ["relaciones", "pase_compania"]),
    (("GABINETE",), ["pase_gabinete"]),
    (("EVENTO DEPORTIVO",), ["elevacion"]),
    (("COLABORACIÓN",), ["elevacion", "pase_origen"]),
    (("SANCIÓN",), ["sancion"]),
    (("NOTIFICACIÓN",), ["notificacion"]),
    (("PROYECTO",), ["elevacion", "proyecto"]),
    (("INVITACIÓN",), ["elevacion", "relaciones"]),
]


def es_actuacion(tipo):
    t = (tipo or "").upper()
    return any(k in t for k in SUGERIDOS[0][0])


def sugeridos(tipo):
    t = (tipo or "").upper()
    for claves, ids in SUGERIDOS[1:]:
        if any(k in t for k in claves):
            return ids
    return ["elevacion", "pase_origen", "notificacion"]


def valores_por_defecto(m: Modelo, ctx):
    return {c.key: (c.defecto(ctx) if callable(c.defecto) else c.defecto) for c in m.campos}
