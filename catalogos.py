"""Catálogos iniciales del sistema. Todo lo que se siembra aquí es editable desde ⚙️ Configuración."""

INSTITUCION = "DIRECCIÓN GENERAL DE INSTITUTOS E INSTRUCCIÓN"
INSTITUCION_CORTA = "D.G.I.I."
SUBTITULO = "Policía de Tucumán · Mesa de Entradas y Registro de Expedientes"

# Paleta categórica validada (CVD-safe) sobre fondo oscuro, en orden fijo.
PALETA = ["#3987E5", "#D95926", "#199E70", "#C98500", "#D55181", "#008300", "#9085E9", "#E66767"]
STATUS = {"ok": "#0CA30C", "warning": "#FAB219", "serious": "#EC835A", "critical": "#D03B3B", "neutral": "#64748B"}

ORIGENES = ["INICIADO EN LA DIRECCIÓN", "RECIBIDO DE OTRA DEPENDENCIA"]

# (nombre, sigla, color)
DEPENDENCIAS_SEED = [
    ("DIRECCIÓN GENERAL DE INSTITUTOS E INSTRUCCIÓN", "DGII", PALETA[0]),
    ("JEFATURA DE POLICÍA", "JEF", PALETA[7]),
    ("SUBJEFATURA DE POLICÍA", "SUBJEF", PALETA[1]),
    ('I.E.S.P. "GRAL. JOSÉ F. DE SAN MARTÍN"', "IESP", PALETA[2]),
    ("ESCUELA DE SUBOFICIALES Y AGENTES", "ESyA", PALETA[3]),
    ("GABINETE INTERDISCIPLINARIO", "GAB", PALETA[4]),
    ("DIRECCIÓN GENERAL DE RECURSOS HUMANOS", "RRHH", PALETA[5]),
    ("DIRECCIÓN GENERAL DE ADMINISTRACIÓN", "ADM", PALETA[6]),
    ("OTRA DEPENDENCIA", "OTRA", "#64748B"),
]
DEP_PROPIA = DEPENDENCIAS_SEED[0][0]

GRUPOS = [
    "Formación y Capacitación",
    "Disciplinario",
    "Administrativo",
    "Institucional",
    "Gabinete",
    "Planificación y Estadística",
    "Otros",
]

# (nombre, grupo, origen habitual DIR/EXT/AMBOS, lleva datos de curso)
TIPOS_SEED = [
    ("AUTORIZACIÓN PARA REALIZAR CURSO", "Formación y Capacitación", "AMBOS", True),
    ("AUTORIZACIÓN PARA DICTAR CURSO", "Formación y Capacitación", "AMBOS", True),
    ("SOLICITUD DE OFERTA ACADÉMICA", "Formación y Capacitación", "DIR", False),
    ("SOLICITUD DE FORMACIÓN", "Formación y Capacitación", "AMBOS", True),
    ("PRÁCTICA DE TIRO", "Formación y Capacitación", "EXT", True),
    ("TALLER", "Formación y Capacitación", "EXT", True),
    ("CONGRESO", "Formación y Capacitación", "EXT", True),
    ("DISERTACIÓN", "Formación y Capacitación", "EXT", True),
    ("DIPLOMATURA", "Formación y Capacitación", "EXT", True),
    ("BECA", "Formación y Capacitación", "EXT", True),
    ("SEMINARIO", "Formación y Capacitación", "EXT", True),
    ("SUMARIO ADMINISTRATIVO", "Disciplinario", "AMBOS", False),
    ("INFORMACIÓN SUMARIA", "Disciplinario", "AMBOS", False),
    ("SANCIÓN DISCIPLINARIA (ESCUELAS)", "Disciplinario", "EXT", False),
    ("ACTUACIONES ADMINISTRATIVAS", "Administrativo", "AMBOS", False),
    ("NOTIFICACIÓN", "Administrativo", "EXT", False),
    ("PROYECTO", "Administrativo", "EXT", False),
    ("AUTORIZACIÓN A EVENTO DEPORTIVO", "Institucional", "EXT", False),
    ("COLABORACIÓN DE EFECTIVOS DE LA DIRECCIÓN", "Institucional", "EXT", False),
    ("EXTENSIÓN DE COLABORACIÓN", "Institucional", "EXT", False),
    ("INVITACIÓN", "Institucional", "EXT", False),
    ("INTERVENCIÓN GABINETE INTERDISCIPLINARIO", "Gabinete", "EXT", False),
    ("ESTADÍSTICA", "Planificación y Estadística", "DIR", False),
    ("PLANIFICACIÓN ANUAL DE CURSOS", "Planificación y Estadística", "DIR", True),
    ("OTRO", "Otros", "AMBOS", False),
]

ESTADOS = ["EN TRÁMITE", "EN DESPACHO", "TRAMITADO", "REMITIDO", "EN ESPERA DE RESPUESTA", "RESUELTO", "ARCHIVADO"]
ESTADOS_CERRADOS = ["RESUELTO", "ARCHIVADO"]
COLOR_ESTADO = {
    "EN TRÁMITE": PALETA[0],
    "EN DESPACHO": PALETA[6],
    "TRAMITADO": PALETA[2],
    "REMITIDO": PALETA[3],
    "EN ESPERA DE RESPUESTA": PALETA[1],
    "RESUELTO": STATUS["ok"],
    "ARCHIVADO": STATUS["neutral"],
}

PRIORIDADES = ["NORMAL", "URGENTE TRÁMITE"]

DESPACHOS = [
    "",
    "VISTO BUENO",
    "A CONSIDERACIÓN DEL COMANDO SUPERIOR",
    "PARA CONOCIMIENTO",
    "PARA DILIGENCIAMIENTO",
    "PARA INFORME",
    "NO AUTORIZADO",
]

TIPOS_MOVIMIENTO = ["SALIDA", "INGRESO", "PASE INTERNO", "TRÁMITE", "DEVOLUCIÓN", "ARCHIVO"]
ESTADO_POR_MOVIMIENTO = {
    "SALIDA": "REMITIDO",
    "INGRESO": "EN TRÁMITE",
    "PASE INTERNO": "EN DESPACHO",
    "TRÁMITE": "TRAMITADO",
    "DEVOLUCIÓN": "REMITIDO",
    "ARCHIVO": "ARCHIVADO",
}

# Qué se hizo al tramitar el expediente
ACCIONES_TRAMITE = [
    "NOTA ELEVADA",
    "PROVIDENCIA / DESPACHO FIRMADO",
    "INFORME PRODUCIDO",
    "AUTORIZACIÓN OTORGADA",
    "NOTIFICACIÓN REALIZADA",
    "RESPUESTA ENVIADA",
    "PASE A DIVISIÓN / ESCUELA",
    "OTRO",
]

CATEGORIAS_CURSO = ["REALIZAR / CURSAR", "DICTAR / DISERTAR", "ORGANIZAR", "ASISTIR / PARTICIPAR"]

# Todo lo que acontece en la Dirección (con o sin expediente)
TIPOS_ACTIVIDAD = [
    "CURSO", "FORMACIÓN", "CAPACITACIÓN", "DISERTACIÓN", "CONGRESO", "SEMINARIO", "TALLER", "JORNADA",
    "DIPLOMATURA", "BECA", "PRÁCTICA DE TIRO", "EVENTO DEPORTIVO", "ACTO / CEREMONIA", "COLABORACIÓN DE EFECTIVOS",
    "INTERVENCIÓN GABINETE", "REUNIÓN", "VISITA / INSPECCIÓN", "OTRA",
]
# Tipo de expediente -> tipo de actividad sugerido
ACTIVIDAD_POR_TIPO = {
    "AUTORIZACIÓN PARA REALIZAR CURSO": "CURSO", "AUTORIZACIÓN PARA DICTAR CURSO": "CURSO", "SOLICITUD DE FORMACIÓN": "FORMACIÓN",
    "PRÁCTICA DE TIRO": "PRÁCTICA DE TIRO", "TALLER": "TALLER", "CONGRESO": "CONGRESO", "DISERTACIÓN": "DISERTACIÓN",
    "DIPLOMATURA": "DIPLOMATURA", "BECA": "BECA", "SEMINARIO": "SEMINARIO", "AUTORIZACIÓN A EVENTO DEPORTIVO": "EVENTO DEPORTIVO",
    "COLABORACIÓN DE EFECTIVOS DE LA DIRECCIÓN": "COLABORACIÓN DE EFECTIVOS", "EXTENSIÓN DE COLABORACIÓN": "COLABORACIÓN DE EFECTIVOS",
    "INTERVENCIÓN GABINETE INTERDISCIPLINARIO": "INTERVENCIÓN GABINETE", "INVITACIÓN": "ACTO / CEREMONIA",
    "PLANIFICACIÓN ANUAL DE CURSOS": "CURSO",
}
MODALIDADES = ["INTERNO", "EXTERNO", "MIXTO"]
AMBITOS = ["EN LA PROVINCIA", "FUERA DE LA PROVINCIA"]
REQUERIMIENTOS = [
    "SIN REQUERIMIENTO (INFORMATIVO)",
    "SOLO AUTORIZACIÓN",
    "AUTORIZACIÓN + VIÁTICO + MOVILIDAD",
    "AUTORIZACIÓN + VIÁTICO",
    "AUTORIZACIÓN + MOVILIDAD",
]
ESTADOS_CURSO = ["PREVISTO", "SOLICITADO", "AUTORIZADO", "NO AUTORIZADO", "SUSPENDIDO"]
ROLES_PERSONAL = ["CURSANTE", "DISERTANTE", "INSTRUCTOR", "COORDINADOR", "PARTICIPANTE", "ORGANIZADOR", "COLABORADOR"]

PROVINCIAS = [
    "TUCUMÁN", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CÓRDOBA", "CORRIENTES",
    "ENTRE RÍOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUÉN",
    "RÍO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO",
    "TIERRA DEL FUEGO", "FUERZA FEDERAL", "EXTRANJERO",
]

# Escala jerárquica de la Policía de Tucumán. Jerarquía -> escalafón (oficiales tramitan / suboficiales cargan)
JERARQUIAS = {
    "COMISARIO GENERAL": "OFICIAL",
    "COMISARIO MAYOR": "OFICIAL",
    "COMISARIO INSPECTOR": "OFICIAL",
    "COMISARIO": "OFICIAL",
    "SUBCOMISARIO": "OFICIAL",
    "OFICIAL PRINCIPAL": "OFICIAL",
    "OFICIAL AUXILIAR": "OFICIAL",
    "OFICIAL AYUDANTE": "OFICIAL",
    "OFICIAL SUBAYUDANTE": "OFICIAL",
    "SUBOFICIAL MAYOR": "SUBOFICIAL",
    "SUBOFICIAL PRINCIPAL": "SUBOFICIAL",
    "SARGENTO AYUDANTE": "SUBOFICIAL",
    "SARGENTO PRIMERO": "SUBOFICIAL",
    "SARGENTO": "SUBOFICIAL",
    "CABO PRIMERO": "SUBOFICIAL",
    "CABO": "SUBOFICIAL",
    "AGENTE": "SUBOFICIAL",
    "PERSONAL TRANSITORIO POLICIAL (PTP)": "PTP",
    # Escuela de Oficiales: cadete (ingreso civil), agente cadete y suboficiales cadetes
    # (cabo, sargento y sargento primero cadete / abanderado, ascensos ad honorem en el IESP)
    "CADETE DE 1° AÑO": "CADETE",
    "CADETE DE 2° AÑO": "CADETE",
    "CADETE DE 3° AÑO": "CADETE",
    "AGENTE CADETE": "CADETE",
    "CABO CADETE": "CADETE",
    "SARGENTO CADETE": "CADETE",
    "SARGENTO PRIMERO CADETE (ABANDERADO)": "CADETE",  # ascendido ad honorem en el IESP
    # Escuela de Suboficiales y Agentes
    "ASPIRANTE (ESCUELA DE SUBOFICIALES)": "ASPIRANTE",
    "PERSONAL CIVIL": "OTRO",
    "OTRO": "OTRO",
}
ESCALAFONES = ["OFICIAL", "SUBOFICIAL", "PTP", "CADETE", "ASPIRANTE", "OTRO"]
# Los usuarios del sistema son solo personal policial en actividad (y civil); PTP, cadetes y aspirantes
# figuran únicamente como personal afectado a expedientes / actividades.
GRADOS_USUARIO = [g for g, e in JERARQUIAS.items() if e in ("OFICIAL", "SUBOFICIAL")] + ["PERSONAL CIVIL"]


def escalafon(grado):
    """Escalafón de un grado; tolera grados escritos de otra forma (p. ej. cargados antes del cambio de escala)."""
    g = str(grado or "").strip().upper()
    if g in JERARQUIAS:
        return JERARQUIAS[g]
    if "PTP" in g or "TRANSITORIO" in g:
        return "PTP"
    if "ASPIRANTE" in g:
        return "ASPIRANTE"
    if "CADETE" in g:
        return "CADETE"
    if g.startswith(("COMISARIO", "SUBCOMISARIO", "OFICIAL", "OF.")):
        return "OFICIAL"
    if g.startswith(("SUBOFICIAL", "SARGENTO", "CABO", "AGENTE", "SGTO")):
        return "SUBOFICIAL"
    return "OTRO"

TIPOS_EVENTO = ["INICIO DE CURSO", "FIN DE CURSO", "VENCIMIENTO", "REUNIÓN", "ACTO / CEREMONIA", "EVENTO DEPORTIVO", "OTRO"]

CONFIG_DEFAULT = {
    "nro_inicial": "1",
    "folio_inicial": "1",
    "libro_actual": "1",
    "renglones_por_folio": "10",
    "paso_folio": "2",
    "reinicio_anual": "NO",
    "dias_aviso_cursos": "7",
    "dias_estancado": "15",
    "wp_por_defecto": "",
    "gdrive_folder_id": "1Qai_8GktJcfYxF2u1jytjj-MR8Zo7Uk0",
}
