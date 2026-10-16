# Sistema de Registro de Expedientes · D.G.I.I. – Policía de Tucumán

Mesa de entradas digital para la **Dirección General de Institutos e Instrucción**: libro de registro (N° EXP / FOLIO / ORDEN), hoja de ruta con movimientos, cursos y personal, alertas, avisos por WhatsApp e informes. Funciona en PC y celular.

## Puesta en marcha (Streamlit Cloud + Supabase)
1. Crear un repo nuevo en GitHub (p. ej. `EXPEDIENTES_DGII`) y subir **todo** el contenido de esta carpeta (incluidas `vistas/`, `assets/` y `.streamlit/config.toml`).
2. En Supabase: *Project Settings → Database → Connection string → Session pooler* (puerto 5432). Puede ser el mismo proyecto de Legajos: las tablas no se pisan.
3. En Streamlit Cloud: *New app* → `app.py` → *Advanced settings → Secrets*:
   ```toml
   SUPABASE_URL = "postgresql://postgres.xxxx:CLAVE@aws-0-sa-east-1.pooler.supabase.com:5432/postgres"
   APP_PASSWORD = "clave-mesa"   # opcional
   ```
4. Al primer ingreso se crean las tablas y se cargan dependencias y tipos de expediente.
5. Ir a **⚙️ Configuración → Libro y alertas** y fijar: N° inicial, folio inicial, renglones por folio y avance de folio (2 = doble página, se numera la foja izquierda).

## Numeración
`N°EXP/FOLIO/ORDEN` — el N° es correlativo; el folio es la foja izquierda del libro; el orden arranca en 1 en cada folio. Cuando el orden alcanza los *renglones por folio*, el siguiente pasa al folio + avance con orden 1. Todo es editable antes de guardar y se valida contra duplicados.

## Módulos
| Página | Uso |
|---|---|
| 📊 Panel de Control | KPIs, ingresos por mes, estado, ubicación actual, tipos, flujo entre dependencias (Sankey) |
| ➕ Nuevo Expediente | Alta con numeración automática; si el tipo es de curso pide datos del curso y del personal |
| 🔁 Movimiento Rápido | Salida / ingreso / pase / archivo con fecha, hora, quién lleva y quién recibe + aviso WhatsApp |
| 📚 Libro de Registro | Filtros, vista tabla, tarjetas (celular) y por folio; exportación Excel |
| 🔎 Ficha | Hoja de ruta (timeline), movimientos, curso/personal, alertas, edición, PDF |
| 🎓 Cursos y Personal | Estadística pedida (autorizados realizados, fuera de la provincia, oficiales/suboficiales, otras provincias, viáticos), planificación anual (Gantt) |
| 🔔 Alertas y Agenda | Inicio de cursos, vencimientos de término, expedientes detenidos, eventos |
| 📥 Carga Masiva | Excel/CSV con encabezados flexibles o transcripción directa del libro en grilla |
| 📈 Informes | Gestión, control de pendientes, libro de movimientos y cursos en PDF/Excel |
| ⚙️ Configuración | Libro, alertas, dependencias (color + WhatsApp), tipos, respaldo y auditoría |

## Estructura
```
app.py            navegación, login, alertas globales
db.py             esquema, lecturas cacheadas, escrituras, numeración
catalogos.py      tipos, dependencias, jerarquías, estados (semillas editables)
comun.py          selector de expediente, formulario de movimiento, motor de alertas
ui.py             CSS responsive, componentes, tema Plotly
reportes.py       PDF (hoja de ruta, informes), Excel, plantilla, WhatsApp
vistas/           una vista por página
```

## Próxima etapa (preparada)
Generación automática de notas/actas por tipo de expediente: cada tipo ya tiene su grupo y datos estructurados (curso, personal, despacho) para alimentar plantillas `.docx` con formato oficial.
