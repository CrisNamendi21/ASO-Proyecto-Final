"""Punto de composición: conecta componentes sin lógica de recursos."""

from simulador.aplicacion import AplicacionUsuario
from simulador.bitacora import Bitacora
from simulador.dispatcher import Dispatcher
from simulador.interfaz_syscalls import InterfazSystemCalls
from simulador.kernel import Kernel
from simulador.procesos import GestorProcesos


def crear_aplicacion() -> AplicacionUsuario:
    gestor = GestorProcesos()
    kernel = Kernel(Dispatcher(gestor), Bitacora())
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
