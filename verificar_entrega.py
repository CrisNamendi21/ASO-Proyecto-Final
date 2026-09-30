"""Verificación reproducible de la entrega final con herramientas estándar."""

from pathlib import Path
import os
import subprocess
import sys


RAIZ = Path(__file__).resolve().parent
ARCHIVOS_REQUERIDOS = (
    "main.py",
    "demo.py",
    "verificar_entrega.py",
    "README.md",
    "MANUAL_USO.md",
    "MATRIZ_PRUEBAS.md",
    "DECISIONES.md",
    "EVIDENCIAS.md",
    "GUIA_DEFENSA.md",
    "AGENTS.md",
    "docs/Proyecto Arquitectura de sistemas operativos.docx",
    "docs/Propuesta #7.pdf",
)


def ejecutar(nombre: str, argumentos: list[str]) -> bool:
    print(f"\n=== {nombre} ===", flush=True)
    resultado = subprocess.run(
        [sys.executable, *argumentos], cwd=RAIZ, check=False,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if resultado.returncode == 0:
        print(f"[OK] {nombre}", flush=True)
        return True
    print(f"[FALLO] {nombre}: código {resultado.returncode}", flush=True)
    return False


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    print(f"Python: {sys.version.split()[0]}")
    faltantes = [ruta for ruta in ARCHIVOS_REQUERIDOS if not (RAIZ / ruta).exists()]
    if faltantes:
        print("[FALLO] Faltan archivos requeridos:")
        for ruta in faltantes:
            print(f"- {ruta}")
        return 1
    print(f"[OK] Archivos requeridos: {len(ARCHIVOS_REQUERIDOS)}")

    try:
        import tkinter  # noqa: F401
    except ImportError as exc:
        print(f"[FALLO] Tkinter no está disponible: {exc}")
        return 1
    print("[OK] Tkinter disponible")

    verificaciones = (
        ("Compilación", ["-m", "compileall", "-q", "main.py", "demo.py",
                          "verificar_entrega.py", "simulador", "tests"]),
        ("Pruebas", ["-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("Demostración", ["demo.py"]),
    )
    correcto = all(ejecutar(nombre, argumentos)
                   for nombre, argumentos in verificaciones)
    print("\n=== Resultado final ===")
    print("ENTREGA VERIFICADA" if correcto else "ENTREGA CON FALLOS")
    return 0 if correcto else 1


if __name__ == "__main__":
    raise SystemExit(main())
