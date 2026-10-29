"""Copia las tablas del Sistema de Expedientes DGII de la base vieja de Supabase a la base nueva.

- La base vieja NO se modifica (se abre en modo solo lectura).
- En la base nueva crea la estructura (el mismo ESQUEMA de db.py) y copia los datos tabla por tabla.
- Al final compara la cantidad de filas de cada tabla en las dos bases.

Uso (desde la carpeta del repo, en la PC):
    pip install psycopg2-binary
    python herramientas/copiar_base.py

Pide las dos direcciones (connection string «Session pooler», puerto 5432) y después limpia la pantalla.
"""
import ast
import io
import os
import sys
from pathlib import Path

import psycopg2

# Orden: primero las tablas de las que dependen las demás (claves foráneas)
TABLAS = ["config", "dependencias", "tipos_expediente", "autoridades", "usuarios", "expedientes", "movimientos",
          "cursos", "personal_curso", "eventos", "adjuntos", "actuaciones", "documentos", "recepciones", "auditoria"]


def esquema():
    """Lee el texto ESQUEMA de db.py sin importar Streamlit."""
    arbol = ast.parse((Path(__file__).resolve().parent.parent / "db.py").read_text(encoding="utf-8"))
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign) and any(getattr(t, "id", "") == "ESQUEMA" for t in nodo.targets):
            return ast.literal_eval(nodo.value)
    sys.exit("No se encontró ESQUEMA en db.py")


def _limpiar(txt):
    """Quita espacios, comillas y el «SUPABASE_URL =» si se pegó la línea entera de los Secrets."""
    txt = (txt or "").strip()
    if "=" in txt.split("://")[0]:
        txt = txt.split("=", 1)[1]
    return txt.strip().strip('"').strip("'").strip()


def columnas(cur, tabla):
    """Columnas copiables (las calculadas, como «identificador», las genera la base sola)."""
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' "
                "AND table_name = %s AND is_generated = 'NEVER' ORDER BY ordinal_position", (tabla,))
    return [r[0] for r in cur.fetchall()]


def contar(cur, tabla):
    cur.execute(f'SELECT COUNT(*) FROM "{tabla}"')
    return cur.fetchone()[0]


def main():
    print("=== Copia de la base del Sistema de Expedientes DGII ===\n")
    print("Pegue cada dirección con clic derecho (o Ctrl+V) y apriete Enter.\n")
    origen = _limpiar(input("Dirección de la base VIEJA: "))
    destino = _limpiar(input("Dirección de la base NUEVA: "))
    os.system("cls" if os.name == "nt" else "clear")  # no dejar las claves a la vista
    print("=== Copia de la base del Sistema de Expedientes DGII ===\n")
    for nombre, url in (("VIEJA", origen), ("NUEVA", destino)):
        if not url.startswith(("postgresql://", "postgres://")) or "[" in url:
            sys.exit(f"❌ La dirección {nombre} no es válida: debe empezar con postgresql:// y no tener [YOUR-PASSWORD].")
    if origen == destino:
        sys.exit("❌ Las dos direcciones son iguales.")

    co = psycopg2.connect(origen, connect_timeout=15)
    co.set_session(readonly=True)
    cd = psycopg2.connect(destino, connect_timeout=15)
    o, d = co.cursor(), cd.cursor()
    print("✔ Conectado a las dos bases.")

    faltan = [t for t in TABLAS if not columnas(o, t)]
    if faltan:
        sys.exit(f"❌ En la base vieja no están estas tablas: {', '.join(faltan)}. ¿Es la dirección correcta?")

    d.execute(esquema())
    cd.commit()
    print("✔ Estructura creada en la base nueva.")

    con_datos = [t for t in TABLAS if contar(d, t)]
    if con_datos:
        print(f"\n⚠ La base nueva ya tiene datos en: {', '.join(con_datos)}")
        if input("¿Borrarlos y reemplazarlos por los de la base vieja? (escriba SI): ").strip().upper() != "SI":
            sys.exit("Cancelado. No se copió nada.")
        d.execute("TRUNCATE " + ", ".join(f'"{t}"' for t in TABLAS) + " RESTART IDENTITY CASCADE")

    try:
        for t in TABLAS:
            cols_d = set(columnas(d, t))
            cols = [c for c in columnas(o, t) if c in cols_d]
            lista = ", ".join(f'"{c}"' for c in cols)
            buf = io.StringIO()
            o.copy_expert(f'COPY (SELECT {lista} FROM "{t}") TO STDOUT WITH (FORMAT csv, HEADER false)', buf)
            buf.seek(0)
            d.copy_expert(f'COPY "{t}" ({lista}) FROM STDIN WITH (FORMAT csv, HEADER false)', buf)
            if "id" in cols:  # que los próximos registros sigan la numeración
                d.execute(f"SELECT setval(pg_get_serial_sequence('\"{t}\"', 'id'), "
                          f'COALESCE((SELECT MAX(id) FROM "{t}"), 1), (SELECT MAX(id) FROM "{t}") IS NOT NULL)')
            print(f"  · {t}: copiada")
        cd.commit()
    except Exception as e:
        cd.rollback()
        sys.exit(f"❌ Error al copiar ({e}). Se deshizo todo en la base nueva; la vieja no se tocó.")

    print("\nControl de filas (vieja → nueva):")
    ok = True
    for t in TABLAS:
        a, b = contar(o, t), contar(d, t)
        ok &= a == b
        print(f"  {'✔' if a == b else '✖'} {t:<18} {a:>6} → {b:>6}")
    co.close()
    cd.close()
    print("\n✅ Copia completa y verificada." if ok else "\n❌ Hay diferencias: no cambie todavía el Secret de la app.")


if __name__ == "__main__":
    main()
