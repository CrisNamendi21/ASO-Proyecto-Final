"""CA-01–CA-07, CE-04–CE-09 y reglas de archivos del incremento 3."""

import errno
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from simulador.aplicacion import AplicacionUsuario
from simulador.archivos import GestorArchivos
from simulador.bitacora import Bitacora
from simulador.contratos import Resultado
from simulador.dispatcher import Dispatcher
from simulador.interfaz_syscalls import InterfazSystemCalls
from simulador.kernel import Kernel
from simulador.procesos import GestorProcesos


class IntegracionArchivos(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.raiz = Path(self.temporal.name) / "archivos"
        self.gestor = GestorArchivos(self.raiz)
        self.bitacora = Bitacora()
        self.dispatcher = Dispatcher(GestorProcesos(), self.gestor)
        self.app = AplicacionUsuario(InterfazSystemCalls(Kernel(self.dispatcher, self.bitacora)))

    def tearDown(self):
        self.temporal.cleanup()

    def llamar(self, metodo, *args, codigo):
        numero = len(self.app.consultar_bitacora()) + 1
        resultado = getattr(self.app, metodo)(*args)
        self.assertIsInstance(resultado, Resultado)
        self.assertEqual(resultado.codigo, codigo)
        self.assertEqual(resultado.estado, "ERROR" if "_" in codigo else "EXITO")
        self.assertTrue(resultado.mensaje)
        self.assertIsInstance(resultado.datos, dict)
        eventos = self.app.consultar_bitacora()
        self.assertEqual(len(eventos), numero)
        self.assertEqual(eventos[-1].numero, numero)
        self.assertEqual(eventos[-1].llamada, metodo)
        self.assertEqual(eventos[-1].resultado.codigo, codigo)
        return resultado

    def crear(self, nombre="nota.txt", codigo="FILE-01"):
        return self.llamar("create_file", nombre, codigo=codigo)

    def abrir(self, nombre="nota.txt", modo="rw", codigo="FILE-02"):
        return self.llamar("open_file", nombre, modo, codigo=codigo)

    def test_CA_01_a_CA_07_flujo_documental_completo(self):
        creado = self.crear()
        self.assertEqual(creado.datos, {"nombre": "nota.txt", "estado": "Cerrado"})
        self.assertEqual((self.raiz / "nota.txt").read_text(encoding="utf-8"), "")

        abierto = self.abrir()
        descriptor = abierto.datos["descriptor"]
        self.assertEqual(descriptor, 1)
        escrito = self.llamar("write_file", descriptor, "área\nDOS", codigo="FILE-04")
        self.assertEqual(escrito.datos, {"caracteres_escritos": 8})
        leido = self.llamar("read_file", descriptor, codigo="FILE-03")
        self.assertEqual(leido.datos, {"contenido": "área\nDOS"})
        cerrado = self.llamar("close_file", descriptor, codigo="FILE-05")
        self.assertEqual(cerrado.datos, {"descriptor": 1, "estado": "Cerrado"})

        listado = self.llamar("list_files", codigo="FILE-07")
        self.assertEqual(listado.datos, {"archivos": [{
            "nombre": "nota.txt", "estado": "Cerrado", "descriptor": None, "modo": None,
        }]})
        eliminado = self.llamar("delete_file", "nota.txt", codigo="FILE-06")
        self.assertEqual(eliminado.datos, {"nombre": "nota.txt"})
        self.assertFalse((self.raiz / "nota.txt").exists())

    def test_listado_vacio_y_estado_de_archivo_abierto(self):
        self.assertEqual(self.llamar("list_files", codigo="FILE-07").datos, {"archivos": []})
        self.crear("b.txt")
        self.crear("A.txt")
        descriptor = self.abrir("b.txt", "r").datos["descriptor"]
        archivos = self.llamar("list_files", codigo="FILE-07").datos["archivos"]
        self.assertEqual([a["nombre"] for a in archivos], ["A.txt", "b.txt"])
        self.assertEqual(archivos[1], {
            "nombre": "b.txt", "estado": "Abierto", "descriptor": descriptor, "modo": "r",
        })

    def test_modos_no_truncan_y_aplican_permisos(self):
        self.crear()
        (self.raiz / "nota.txt").write_text("original", encoding="utf-8")
        descriptor = self.abrir(modo="w").datos["descriptor"]
        self.assertEqual((self.raiz / "nota.txt").read_text(encoding="utf-8"), "original")
        self.llamar("read_file", descriptor, codigo="FILE_007")
        self.llamar("write_file", descriptor, "nuevo", codigo="FILE-04")
        self.llamar("close_file", descriptor, codigo="FILE-05")
        descriptor = self.abrir(modo="r").datos["descriptor"]
        self.llamar("write_file", descriptor, "prohibido", codigo="FILE_007")
        self.assertEqual(self.llamar("read_file", descriptor, codigo="FILE-03").datos["contenido"],
                         "nuevo")

    def test_escritura_reemplaza_todo_y_cuenta_caracteres(self):
        self.crear()
        descriptor = self.abrir().datos["descriptor"]
        self.llamar("write_file", descriptor, "contenido largo", codigo="FILE-04")
        resultado = self.llamar("write_file", descriptor, "ñ😊", codigo="FILE-04")
        self.assertEqual(resultado.datos, {"caracteres_escritos": 2})
        self.assertEqual((self.raiz / "nota.txt").read_text(encoding="utf-8"), "ñ😊")

    def test_descriptores_secuenciales_no_reutilizados_y_tipos_invalidos(self):
        for nombre in ("a.txt", "b.txt", "c.txt"):
            self.crear(nombre)
        primero = self.abrir("a.txt").datos["descriptor"]
        self.llamar("close_file", primero, codigo="FILE-05")
        segundo = self.abrir("b.txt").datos["descriptor"]
        self.llamar("close_file", segundo, codigo="FILE-05")
        tercero = self.abrir("c.txt").datos["descriptor"]
        self.assertEqual((primero, segundo, tercero), (1, 2, 3))
        for descriptor in (None, "1", 1.0, True, False, [], 99):
            with self.subTest(descriptor=descriptor):
                self.llamar("read_file", descriptor, codigo="FILE_006")

    def test_CE_04_existente_no_trunca(self):
        self.crear()
        ruta = self.raiz / "nota.txt"
        ruta.write_text("conservar", encoding="utf-8")
        self.crear(codigo="FILE_002")
        self.assertEqual(ruta.read_text(encoding="utf-8"), "conservar")

    def test_CE_05_inexistente_y_modo_invalido(self):
        self.abrir("ausente.txt", "r", "FILE_003")
        self.llamar("delete_file", "ausente.txt", codigo="FILE_003")
        self.crear()
        for modo in ("", "R", "a", None, 3):
            with self.subTest(modo=modo):
                self.abrir(modo=modo, codigo="FILE_004")

    def test_CE_06_apertura_duplicada_en_cualquier_modo(self):
        self.crear()
        self.abrir(modo="r")
        for modo in ("r", "w", "rw"):
            self.abrir(modo=modo, codigo="FILE_005")
        self.assertEqual(self.gestor._siguiente_descriptor, 2)

    def test_CE_07_CE_08_descriptor_invalido_doble_cierre_y_uso_posterior(self):
        self.crear()
        descriptor = self.abrir().datos["descriptor"]
        self.llamar("close_file", descriptor, codigo="FILE-05")
        self.llamar("read_file", descriptor, codigo="FILE_006")
        self.llamar("write_file", descriptor, "x", codigo="FILE_006")
        self.llamar("close_file", descriptor, codigo="FILE_006")

    def test_CE_09_no_elimina_archivo_abierto(self):
        self.crear()
        self.abrir()
        self.llamar("delete_file", "nota.txt", codigo="FILE_008")
        self.assertTrue((self.raiz / "nota.txt").is_file())

    def test_validacion_estructural_de_llamadas_de_archivo(self):
        casos = [
            ("create_file", {}, "SYS_002"),
            ("open_file", {"nombre": "a.txt"}, "SYS_002"),
            ("read_file", {"descriptor": 1, "extra": 2}, "SYS_002"),
            ("write_file", {"descriptor": 1, "datos": 7}, "SYS_002"),
            ("list_files", {"extra": True}, "SYS_002"),
        ]
        for llamada, parametros, codigo in casos:
            with self.subTest(llamada=llamada, parametros=parametros):
                resultado = self.app.enviar_solicitud(llamada, parametros)
                self.assertEqual(resultado.codigo, codigo)
                self.assertEqual(self.app.consultar_bitacora()[-1].resultado.codigo, codigo)
                self.assertFalse(any("GestorArchivos" in p for p in self.app.consultar_recorrido()))

    def test_nombres_no_son_rutas_y_no_afectan_archivos_externos(self):
        externo = Path(self.temporal.name) / "externo.txt"
        externo.write_text("intacto", encoding="utf-8")
        invalidos = (
            "", "   ", ".", "..", "../externo.txt", "..\\externo.txt",
            "/tmp/externo.txt", r"C:\\Windows\\win.ini", r"\\servidor\\recurso",
            "sub/cosa.txt", "sub\\cosa.txt", "archivo:flujo", "NUL", "con.txt",
            "final.", "final ", ".__simulador_tmp_usuario", "interrogante?.txt",
            "asterisco*.txt", "menor<.txt", "barra|.txt", "control\n.txt",
        )
        for nombre in invalidos:
            with self.subTest(nombre=nombre):
                self.crear(nombre, "FILE_001")
        self.assertEqual(externo.read_text(encoding="utf-8"), "intacto")
        self.assertEqual(list(self.raiz.iterdir()), [])

    def test_tipos_de_nombre_invalidos(self):
        for nombre in (None, 7, True, False, [], {}, b"archivo.txt"):
            with self.subTest(nombre=nombre):
                self.crear(nombre, "FILE_001")

    def test_enlaces_no_se_listan_abren_eliminan_ni_modifican_destino(self):
        externo = Path(self.temporal.name) / "externo.txt"
        externo.write_text("intacto", encoding="utf-8")
        enlace = self.raiz / "enlace.txt"
        try:
            enlace.symlink_to(externo)
        except OSError as exc:
            self.skipTest(f"El entorno no permite crear enlaces simbólicos: {exc}")
        self.crear("enlace.txt", "FILE_001")
        self.abrir("enlace.txt", "rw", "FILE_001")
        self.llamar("delete_file", "enlace.txt", codigo="FILE_001")
        self.assertEqual(self.llamar("list_files", codigo="FILE-07").datos, {"archivos": []})
        self.assertEqual(externo.read_text(encoding="utf-8"), "intacto")
        self.assertTrue(enlace.is_symlink())

    def test_raiz_no_puede_ser_enlace_o_redireccion(self):
        destino = Path(self.temporal.name) / "destino"
        destino.mkdir()
        enlace = Path(self.temporal.name) / "raiz_enlace"
        try:
            enlace.symlink_to(destino, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"El entorno no permite crear enlaces de directorio: {exc}")
        with self.assertRaises(ValueError):
            GestorArchivos(enlace)

    def test_hardlink_externo_no_se_expone_y_conserva_destino(self):
        externo = Path(self.temporal.name) / "externo_hardlink.txt"
        externo.write_text("intacto", encoding="utf-8")
        enlace = self.raiz / "hardlink.txt"
        try:
            os.link(externo, enlace)
        except OSError as exc:
            self.skipTest(f"El entorno no permite crear hard links: {exc}")
        self.crear("hardlink.txt", "FILE_001")
        self.abrir("hardlink.txt", "r", "FILE_001")
        self.llamar("delete_file", "hardlink.txt", codigo="FILE_001")
        self.assertEqual(self.llamar("list_files", codigo="FILE-07").datos, {"archivos": []})
        self.assertEqual(externo.read_text(encoding="utf-8"), "intacto")

    def test_destino_por_descriptor_se_revalida_antes_de_leer_o_escribir(self):
        self.crear()
        descriptor = self.abrir().datos["descriptor"]
        ruta = self.raiz / "nota.txt"
        ruta.unlink()
        externo = Path(self.temporal.name) / "externo_descriptor.txt"
        externo.write_text("intacto", encoding="utf-8")
        try:
            os.link(externo, ruta)
        except OSError as exc:
            self.skipTest(f"El entorno no permite crear hard links: {exc}")
        self.llamar("read_file", descriptor, codigo="FILE_001")
        self.llamar("write_file", descriptor, "alterado", codigo="FILE_001")
        self.assertEqual(externo.read_text(encoding="utf-8"), "intacto")

    def test_persistencia_fisica_y_reinicio_de_aperturas(self):
        self.crear()
        descriptor = self.abrir().datos["descriptor"]
        self.llamar("write_file", descriptor, "persistente", codigo="FILE-04")
        nuevo = GestorArchivos(self.raiz)
        app_nueva = AplicacionUsuario(InterfazSystemCalls(
            Kernel(Dispatcher(GestorProcesos(), nuevo), Bitacora())))
        listado = app_nueva.list_files().datos["archivos"]
        self.assertEqual(listado, [{
            "nombre": "nota.txt", "estado": "Cerrado", "descriptor": None, "modo": None,
        }])
        descriptor_nuevo = app_nueva.open_file("nota.txt", "r").datos["descriptor"]
        self.assertEqual(descriptor_nuevo, 1)
        self.assertEqual(app_nueva.read_file(descriptor_nuevo).datos["contenido"], "persistente")

    def test_cierre_libera_descriptor_si_archivo_desaparece_externamente(self):
        self.crear()
        descriptor = self.abrir().datos["descriptor"]
        (self.raiz / "nota.txt").unlink()
        self.llamar("close_file", descriptor, codigo="FILE-05")
        self.llamar("read_file", descriptor, codigo="FILE_006")

    def test_raiz_eliminada_durante_sesion_es_fallo_fisico(self):
        self.raiz.rmdir()
        listado = self.llamar("list_files", codigo="FILE_009")
        self.assertEqual(listado.datos["operacion"], "acceder_raiz")
        creacion = self.crear("nuevo.txt", "FILE_009")
        self.assertEqual(creacion.datos["operacion"], "acceder_raiz")

    def test_codificacion_invalida_no_escapa_como_excepcion(self):
        self.crear()
        ruta = self.raiz / "nota.txt"
        ruta.write_bytes(b"\xff")
        descriptor = self.abrir(modo="r").datos["descriptor"]
        lectura = self.llamar("read_file", descriptor, codigo="FILE_009")
        self.assertEqual(lectura.datos["tipo"], "UnicodeDecodeError")

    def test_escritura_no_codificable_conserva_original_y_limpia_temporal(self):
        self.crear()
        ruta = self.raiz / "nota.txt"
        ruta.write_text("original", encoding="utf-8")
        descriptor = self.abrir().datos["descriptor"]
        resultado = self.llamar("write_file", descriptor, "\ud800", codigo="FILE_009")
        self.assertEqual(resultado.datos["tipo"], "UnicodeEncodeError")
        self.assertEqual(ruta.read_text(encoding="utf-8"), "original")
        self.assertEqual([p.name for p in self.raiz.iterdir()], ["nota.txt"])

    def test_datos_de_escritura_no_textuales_se_rechazan_antes_del_gestor(self):
        self.crear()
        descriptor = self.abrir().datos["descriptor"]
        ruta = self.raiz / "nota.txt"
        ruta.write_text("original", encoding="utf-8")
        for datos in (None, 3, True, [], {}, b"bytes"):
            with self.subTest(datos=datos):
                resultado = self.app.enviar_solicitud(
                    "write_file", {"descriptor": descriptor, "datos": datos})
                self.assertEqual(resultado.codigo, "SYS_002")
                self.assertEqual(self.app.consultar_bitacora()[-1].resultado.codigo, "SYS_002")
                self.assertFalse(any("GestorArchivos" in p for p in self.app.consultar_recorrido()))
                self.assertEqual(ruta.read_text(encoding="utf-8"), "original")

    def test_fallo_fisico_de_lectura_se_reporta_sin_falso_exito(self):
        self.crear()
        descriptor = self.abrir(modo="r").datos["descriptor"]
        with patch.object(Path, "read_text", side_effect=PermissionError(errno.EACCES, "denegado")):
            resultado = self.llamar("read_file", descriptor, codigo="FILE_009")
        self.assertEqual(resultado.datos["operacion"], "leer")
        self.assertEqual(resultado.datos["tipo"], "PermissionError")

    def test_escritura_protegida_conserva_original_y_limpia_temporal_si_falla(self):
        self.crear()
        ruta = self.raiz / "nota.txt"
        ruta.write_text("original", encoding="utf-8")
        descriptor = self.abrir().datos["descriptor"]
        with patch("simulador.archivos.os.replace",
                   side_effect=PermissionError(errno.EACCES, "denegado")):
            resultado = self.llamar("write_file", descriptor, "nuevo", codigo="FILE_009")
        self.assertEqual(resultado.datos["operacion"], "escribir")
        self.assertEqual(ruta.read_text(encoding="utf-8"), "original")
        self.assertEqual([p.name for p in self.raiz.iterdir()], ["nota.txt"])

    def test_fallo_al_crear_temporal_no_modifica_original(self):
        self.crear()
        ruta = self.raiz / "nota.txt"
        ruta.write_text("original", encoding="utf-8")
        descriptor = self.abrir().datos["descriptor"]
        with patch("simulador.archivos.tempfile.mkstemp",
                   side_effect=OSError(errno.ENOSPC, "sin espacio")):
            self.llamar("write_file", descriptor, "nuevo", codigo="FILE_009")
        self.assertEqual(ruta.read_text(encoding="utf-8"), "original")

    def test_bitacora_registra_cantidades_sin_contenido(self):
        secreto = "contenido que no debe copiarse"
        self.crear()
        descriptor = self.abrir().datos["descriptor"]
        self.llamar("write_file", descriptor, secreto, codigo="FILE-04")
        evento_escritura = self.app.consultar_bitacora()[-1]
        self.assertEqual(evento_escritura.parametros, {
            "descriptor": descriptor, "caracteres_solicitados": len(secreto),
        })
        self.assertNotIn(secreto, repr(evento_escritura))
        self.llamar("read_file", descriptor, codigo="FILE-03")
        evento_lectura = self.app.consultar_bitacora()[-1]
        self.assertEqual(evento_lectura.resultado.datos, {"caracteres_leidos": len(secreto)})
        self.assertNotIn(secreto, repr(evento_lectura))

    def test_recorrido_identifica_gestor_de_archivos(self):
        self.crear()
        recorrido = self.app.consultar_recorrido()
        self.assertIn("GestorArchivos: validar y procesar", recorrido)
        self.assertLess(recorrido.index("GestorArchivos: validar y procesar"),
                        recorrido.index("Kernel: registrar evento final"))

    def test_dispatcher_registra_exactamente_las_once_system_calls(self):
        esperadas = {
            "create_process", "list_processes", "get_process", "terminate_process",
            "create_file", "open_file", "read_file", "write_file", "close_file",
            "delete_file", "list_files",
        }
        self.assertEqual(set(self.dispatcher._registro), esperadas)
        self.assertEqual(set(self.dispatcher._parametros), esperadas)
        self.assertNotIn("enviar_solicitud", self.dispatcher._registro)
        self.assertNotIn("consultar_bitacora", self.dispatcher._registro)


if __name__ == "__main__":
    unittest.main()
