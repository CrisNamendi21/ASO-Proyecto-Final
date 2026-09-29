"""Comprobación funcional de la pantalla de archivos con Tk real."""

from pathlib import Path
import tempfile
import tkinter as tk
import unittest

from main import crear_aplicacion
from simulador.gui.ventana import Ventana


class PantallaArchivos(unittest.TestCase):
    def test_secuencia_visible_de_las_siete_operaciones(self):
        try:
            raiz = tk.Tk()
        except tk.TclError as exc:
            self.skipTest(f"Tk no está disponible en este entorno: {exc}")
        try:
            with tempfile.TemporaryDirectory() as temporal:
                app = crear_aplicacion(Path(temporal) / "archivos")
                ventana = Ventana(raiz, app)
                raiz.geometry("850x700")
                raiz.update_idletasks()
                for nombre in ("Procesos", "Archivos", "Bitácora", "Inicio"):
                    ventana.mostrar(nombre)
                    raiz.update_idletasks()
                    vista = ventana.vistas[nombre]
                    self.assertGreaterEqual(vista.winfo_width(), vista.winfo_reqwidth())
                    self.assertGreaterEqual(vista.winfo_height(), vista.winfo_reqheight())
                ventana.mostrar("Archivos")
                ventana.nombre_archivo.set("gui.txt")
                ventana.crear_archivo()
                self.assertIn("FILE-01", ventana.resultado.get("1.0", "end"))
                ventana.modo_archivo.set("rw")
                ventana.abrir_archivo()
                self.assertEqual(ventana.descriptor_archivo.get(), "1")
                ventana.contenido_archivo.insert("1.0", "texto desde GUI")
                ventana.escribir_archivo()
                self.assertIn("FILE-04", ventana.resultado.get("1.0", "end"))
                ventana.contenido_archivo.delete("1.0", "end")
                ventana.leer_archivo()
                self.assertEqual(ventana.contenido_archivo.get("1.0", "end-1c"),
                                 "texto desde GUI")
                ventana.listar_archivos()
                fila = ventana.archivos.item(ventana.archivos.get_children()[0], "values")
                self.assertEqual(tuple(fila), ("gui.txt", "Abierto", "1", "rw"))
                ventana.eliminar_archivo()
                self.assertIn("FILE_008", ventana.resultado.get("1.0", "end"))
                ventana.cerrar_archivo()
                ventana.eliminar_archivo()
                ventana.listar_archivos()
                self.assertEqual(ventana.archivos.get_children(), ())
                ventana.mostrar("Bitácora")
                self.assertEqual(len(ventana.eventos.get_children()), 9)
                self.assertEqual(len(app.consultar_bitacora()), 9)
        finally:
            raiz.destroy()


if __name__ == "__main__":
    unittest.main()
