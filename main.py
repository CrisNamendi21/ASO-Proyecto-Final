"""Punto de composición: conecta componentes sin lógica de recursos."""

from pathlib import Path

from simulador.aplicacion import AplicacionUsuario
from simulador.bitacora import Bitacora
from simulador.archivos import GestorArchivos
from simulador.dispatcher import Dispatcher
from simulador.interfaz_syscalls import InterfazSystemCalls
from simulador.kernel import Kernel
from simulador.procesos import GestorProcesos


def crear_aplicacion(directorio_archivos: Path | None = None) -> AplicacionUsuario:
    gestor = GestorProcesos()
    raiz = directorio_archivos or Path(__file__).resolve().parent / "datos" / "archivos"
    kernel = Kernel(Dispatcher(gestor, GestorArchivos(raiz)), Bitacora())
    return AplicacionUsuario(InterfazSystemCalls(kernel))


def main() -> None:
    # Importación diferida: el núcleo y la demostración funcionan sin Tkinter.
    import tkinter as tk
    from simulador.gui.ventana import Ventana

    raiz = tk.Tk()
    Ventana(raiz, crear_aplicacion())
    raiz.mainloop()


if __name__ == "__main__":
    main()
