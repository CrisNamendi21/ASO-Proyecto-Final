"""Crea el paquete portable del proyecto con una lista explícita de archivos."""

from hashlib import sha256
from io import TextIOWrapper
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


RAIZ = Path(__file__).resolve().parent
DIRECTORIO_SALIDA = RAIZ / "dist"
PAQUETE = DIRECTORIO_SALIDA / "ASO_Proyecto_Final.zip"
ARCHIVO_HASH = DIRECTORIO_SALIDA / "ASO_Proyecto_Final.sha256"

ARCHIVOS_REQUERIDOS = (
    ".gitignore",
    "main.py",
    "demo.py",
    "verificar_entrega.py",
    "crear_paquete.py",
    "README.md",
    "MANUAL_USO.md",
    "MATRIZ_PRUEBAS.md",
    "DECISIONES.md",
    "EVIDENCIAS.md",
    "GUIA_DEFENSA.md",
    "ENTREGA_FINAL.md",
    "MANIFIESTO_ENTREGA.md",
    "docs/Proyecto Arquitectura de sistemas operativos.docx",
    "docs/Propuesta #7.pdf",
)


def _archivos_python(carpeta: str) -> list[str]:
    """Devuelve solo fuentes Python, sin cachés ni artefactos generados."""
    return [
        ruta.relative_to(RAIZ).as_posix()
        for ruta in sorted((RAIZ / carpeta).rglob("*.py"))
        if "__pycache__" not in ruta.parts
    ]


def archivos_del_paquete() -> list[str]:
    """Construye y valida el manifiesto cerrado del ZIP."""
    rutas = [*ARCHIVOS_REQUERIDOS, *_archivos_python("simulador"),
             *_archivos_python("tests")]
    faltantes = [ruta for ruta in rutas if not (RAIZ / ruta).is_file()]
    if faltantes:
        detalle = "\n".join(f"- {ruta}" for ruta in faltantes)
        raise FileNotFoundError(f"Faltan archivos requeridos:\n{detalle}")
    return rutas


def crear_paquete() -> tuple[Path, Path, int, str]:
    """Genera el ZIP y su SHA-256; devuelve rutas, cantidad y resumen."""
    rutas = archivos_del_paquete()
    DIRECTORIO_SALIDA.mkdir(exist_ok=True)

    with ZipFile(PAQUETE, "w", compression=ZIP_DEFLATED) as archivo_zip:
        for ruta_relativa in rutas:
            archivo_zip.write(RAIZ / ruta_relativa, ruta_relativa)

        # Los datos personales no se distribuyen; la aplicación recibe su raíz vacía.
        entrada_datos = ZipInfo("datos/archivos/")
        entrada_datos.external_attr = 0o40775 << 16
        archivo_zip.writestr(entrada_datos, b"")

    resumen = sha256(PAQUETE.read_bytes()).hexdigest()
    ARCHIVO_HASH.write_text(
        f"{resumen}  {PAQUETE.name}\n", encoding="ascii")
    return PAQUETE, ARCHIVO_HASH, len(rutas), resumen


def main() -> int:
    if isinstance(sys.stdout, TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    if isinstance(sys.stderr, TextIOWrapper):
        sys.stderr.reconfigure(encoding="utf-8")
    try:
        paquete, archivo_hash, cantidad, resumen = crear_paquete()
    except (FileNotFoundError, OSError) as exc:
        print(f"[FALLO] No se pudo crear el paquete: {exc}")
        return 1

    print(f"[OK] Paquete creado: {paquete}")
    print(f"[OK] Archivos incluidos: {cantidad} y datos/archivos/ vacío")
    print(f"[OK] SHA-256: {resumen}")
    print(f"[OK] Suma guardada en: {archivo_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
