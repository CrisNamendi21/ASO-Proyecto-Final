"""Pruebas por AplicacionUsuario: contratos, efectos y un evento por llamada."""

from dataclasses import fields
from datetime import datetime
import unittest
from unittest.mock import patch

from simulador.aplicacion import AplicacionUsuario
from simulador.bitacora import Bitacora
from simulador.contratos import Resultado
from simulador.dispatcher import Dispatcher
from simulador.interfaz_syscalls import InterfazSystemCalls
from simulador.kernel import Kernel
from simulador.procesos import EstadoProceso, GestorProcesos


class IntegracionCreacion(unittest.TestCase):
    def setUp(self):
        self.gestor = GestorProcesos()
        self.bitacora = Bitacora()
        self.dispatcher = Dispatcher(self.gestor)
        self.kernel = Kernel(self.dispatcher, self.bitacora)
        self.interfaz = InterfazSystemCalls(self.kernel)
        self.app = AplicacionUsuario(self.interfaz)

    def comprobar_llamada(self, accion, codigo, nombre=None, prioridad=None):
        """Comprueba respuesta, efecto y evento incluso en cada subcaso negativo."""
        anteriores = dict(self.gestor._procesos)
        siguiente = self.gestor._siguiente_pid
        numero = len(self.app.consultar_bitacora()) + 1
        resultado = accion()
        self.assertIsInstance(resultado, Resultado)
        self.assertEqual([campo.name for campo in fields(resultado)],
                         ["estado", "codigo", "mensaje", "datos"])
        self.assertEqual(resultado.codigo, codigo)
        self.assertTrue(resultado.mensaje)
        self.assertIsInstance(resultado.datos, dict)
        if codigo == "PROC-01":
            self.assertEqual(resultado.estado, "EXITO")
            self.assertEqual(resultado.datos, {"pid": siguiente})
            proceso = self.gestor._procesos[siguiente]
            self.assertEqual((proceso.pid, proceso.nombre, proceso.prioridad, proceso.estado),
                             (siguiente, nombre, prioridad, EstadoProceso.LISTO))
            self.assertEqual(len(self.gestor._procesos), len(anteriores) + 1)
            self.assertEqual(self.gestor._siguiente_pid, siguiente + 1)
            for pid, previo in anteriores.items():
                self.assertEqual(self.gestor._procesos[pid], previo)
        else:
            self.assertEqual(resultado.estado, "ERROR")
            self.assertEqual(resultado.datos, {})
            self.assertEqual(self.gestor._procesos, anteriores)
            self.assertEqual(self.gestor._siguiente_pid, siguiente)
        eventos = self.app.consultar_bitacora()
        self.assertEqual(len(eventos), numero)
        self.assertEqual(eventos[-1].numero, numero)
        self.assertEqual(eventos[-1].resultado, resultado)
        self.assertIsNotNone(datetime.fromisoformat(eventos[-1].fecha_hora).tzinfo)
        return resultado

    def crear(self, nombre, prioridad, codigo="PROC-01"):
        resultado = self.comprobar_llamada(lambda: self.app.create_process(nombre, prioridad),
                                          codigo, nombre, prioridad)
        evento = self.app.consultar_bitacora()[-1]
        self.assertEqual(evento.llamada, "create_process")
        self.assertEqual(evento.parametros, {"nombre": nombre, "prioridad": prioridad})
        return resultado

    def enviar(self, llamada, parametros, codigo):
        resultado = self.comprobar_llamada(lambda: self.app.enviar_solicitud(llamada, parametros), codigo)
        evento = self.app.consultar_bitacora()[-1]
        self.assertEqual(evento.llamada, llamada)
        self.assertEqual(evento.parametros, parametros)
        return resultado

    def test_CP_01_creacion_y_transicion_nuevo_listo(self):
        admitir = self.gestor._admitir
        estados = []

        def observar_admision(pid):
            estados.append(self.gestor._procesos[pid].estado)
            admitir(pid)
            estados.append(self.gestor._procesos[pid].estado)

        with patch.object(self.gestor, "_admitir", side_effect=observar_admision):
            self.crear("Editor", 3)
        self.assertEqual(estados, [EstadoProceso.NUEVO, EstadoProceso.LISTO])

    def test_CE_01_datos_invalidos(self):
        self.crear("", 6, "PROC_001")

    def test_limites_nombre_y_prioridad(self):
        for nombre in ("a", "a" * 50):
            for prioridad in (1, 5):
                with self.subTest(nombre=nombre, prioridad=prioridad):
                    self.crear(nombre, prioridad)
        self.crear("a" * 51, 3, "PROC_001")
        for prioridad in (0, 6, -1):
            with self.subTest(prioridad=prioridad):
                self.crear("Editor", prioridad, "PROC_001")

    def test_tipos_invalidos(self):
        for nombre in (None, 1, True, [], {}):
            with self.subTest(nombre=nombre):
                self.crear(nombre, 3, "PROC_001")
        for prioridad in (None, "3", 3.0, True, False, [], {}):
            with self.subTest(prioridad=prioridad):
                self.crear("Editor", prioridad, "PROC_001")

    def test_espacios_y_nombre_conservado(self):
        for nombre in (" ", "\t\n"):
            self.crear(nombre, 3, "PROC_001")
        self.crear("  Editor  ", 3)

    def test_repetidos_y_pid_secuenciales_sin_consumir_por_rechazo(self):
        self.crear("Editor", 3)
        self.crear("", 3, "PROC_001")
        self.crear("Editor", 3)
        self.assertEqual(list(self.gestor._procesos), [101, 102])
        self.assertTrue(all(p.estado == EstadoProceso.LISTO for p in self.gestor._procesos.values()))

    def test_CE_10_llamada_desconocida(self):
        self.enviar("no_existe", {}, "SYS_001")
        self.assertFalse(any("GestorProcesos" in paso for paso in self.app.consultar_recorrido()))

    def test_CE_10_parametros_incompletos(self):
        for parametros in ({}, {"nombre": "Editor"}, {"prioridad": 3}):
            with self.subTest(parametros=parametros):
                self.enviar("create_process", parametros, "SYS_002")
                self.assertFalse(any("GestorProcesos" in paso for paso in self.app.consultar_recorrido()))

    def test_solicitud_mal_formada_y_parametros_extra(self):
        for parametros in (None, [], "texto", {"nombre": "Editor", "prioridad": 3, "pid": 77}):
            with self.subTest(parametros=parametros):
                self.enviar("create_process", parametros, "SYS_002")
        for llamada in (None, [], 7):
            with self.subTest(llamada=llamada):
                self.enviar(llamada, {}, "SYS_001")

    def test_precedencia_identificacion_estructura_dominio(self):
        self.enviar("no_existe", None, "SYS_001")
        self.enviar("create_process", {"nombre": ""}, "SYS_002")
        self.crear("", 6, "PROC_001")

    def test_copias_no_permiten_modificar_registro_ni_estado(self):
        resultado = self.crear("Editor", 3)
        resultado.datos["pid"] = 999
        eventos = self.app.consultar_bitacora()
        eventos[0].resultado.datos["pid"] = 888
        eventos[0].parametros["nombre"] = "Alterado"
        copia = self.app.consultar_bitacora()
        self.assertEqual(copia[0].resultado.datos, {"pid": 101})
        self.assertEqual(copia[0].parametros["nombre"], "Editor")
        self.assertEqual(self.gestor._procesos[101].nombre, "Editor")
        self.assertEqual(len(copia), 1)

    def test_consultas_de_bitacora_y_recorrido_no_generan_eventos(self):
        self.assertEqual(self.app.consultar_bitacora(), ())
        self.assertEqual(self.app.consultar_recorrido(), ())
        self.crear("Editor", 3)
        for _ in range(3):
            self.assertEqual(len(self.app.consultar_bitacora()), 1)
            self.assertIsInstance(self.app.consultar_recorrido(), tuple)

    def test_sesiones_independientes(self):
        self.crear("Primera", 3)
        self.setUp()
        self.assertEqual(self.app.consultar_bitacora(), ())
        self.crear("Segunda", 3)

    def test_recorrido_real_y_registro_antes_del_retorno(self):
        orden = []

        def observar(etiqueta, metodo):
            def ejecutar(*args, **kwargs):
                orden.append(etiqueta + ":entrada")
                resultado = metodo(*args, **kwargs)
                orden.append(etiqueta + ":salida")
                return resultado
            return ejecutar

        with patch.object(self.gestor, "create_process",
                          side_effect=observar("gestor", self.gestor.create_process)):
            self.dispatcher = Dispatcher(self.gestor)
        self.kernel = Kernel(self.dispatcher, self.bitacora)
        self.interfaz = InterfazSystemCalls(self.kernel)
        self.app = AplicacionUsuario(self.interfaz)
        with (
            patch.object(self.app, "create_process", side_effect=observar("app", self.app.create_process)),
            patch.object(self.interfaz, "create_process", side_effect=observar("interfaz", self.interfaz.create_process)),
            patch.object(self.kernel, "atender", side_effect=observar("kernel", self.kernel.atender)),
            patch.object(self.dispatcher, "despachar", side_effect=observar("dispatcher", self.dispatcher.despachar)),
            patch.object(self.bitacora, "registrar", side_effect=observar("registro", self.bitacora.registrar)),
        ):
            self.crear("Editor", 3)
        self.assertEqual(orden, [
            "app:entrada", "interfaz:entrada", "kernel:entrada", "dispatcher:entrada", "gestor:entrada",
            "gestor:salida", "dispatcher:salida", "registro:entrada", "registro:salida",
            "kernel:salida", "interfaz:salida", "app:salida",
        ])


if __name__ == "__main__":
    unittest.main()
