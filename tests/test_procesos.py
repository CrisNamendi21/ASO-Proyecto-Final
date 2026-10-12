"""CP-02–CP-04, CE-02–CE-03 e invariantes de procesos."""

from contextlib import ExitStack
from dataclasses import replace
import unittest
from unittest.mock import patch

from simulador.aplicacion import AplicacionUsuario
from simulador.bitacora import Bitacora
from simulador.contratos import Resultado
from simulador.dispatcher import Dispatcher
from simulador.interfaz_syscalls import InterfazSystemCalls
from simulador.kernel import Kernel
from simulador.procesos import EstadoProceso, GestorProcesos, Proceso


class IntegracionProcesos(unittest.TestCase):
    def setUp(self):
        self.gestor = GestorProcesos()
        self.bitacora = Bitacora()
        self.dispatcher = Dispatcher(self.gestor)
        self.kernel = Kernel(self.dispatcher, self.bitacora)
        self.interfaz = InterfazSystemCalls(self.kernel)
        self.app = AplicacionUsuario(self.interfaz)

    def llamada(self, nombre, parametros, codigo, datos, transporte=False):
        antes = dict(self.gestor._procesos)
        siguiente = self.gestor._siguiente_pid
        eventos_antes = self.app.consultar_bitacora()
        if transporte:
            resultado = self.app.enviar_solicitud(nombre, parametros)
        else:
            resultado = getattr(self.app, nombre)(**parametros)
        self.assertIsInstance(resultado, Resultado)
        self.assertEqual(resultado.codigo, codigo)
        self.assertEqual(resultado.estado, "ERROR" if "_" in codigo else "EXITO")
        self.assertTrue(resultado.mensaje)
        self.assertEqual(resultado.datos, datos)
        esperado = dict(antes)
        if codigo == "PROC-01":
            esperado[siguiente] = Proceso(siguiente, parametros["nombre"], EstadoProceso.LISTO,
                                          parametros["prioridad"])
            self.assertEqual(self.gestor._siguiente_pid, siguiente + 1)
        else:
            self.assertEqual(self.gestor._siguiente_pid, siguiente)
            if codigo == "PROC-04":
                pid = parametros["pid"]
                esperado[pid] = replace(antes[pid], estado=EstadoProceso.FINALIZADO)
        self.assertEqual(self.gestor._procesos, esperado)
        eventos = self.app.consultar_bitacora()
        self.assertEqual(len(eventos), len(eventos_antes) + 1)
        self.assertEqual(eventos[:-1], eventos_antes)
        self.assertEqual(eventos[-1].numero, len(eventos))
        self.assertEqual(eventos[-1].llamada, nombre)
        self.assertEqual(eventos[-1].parametros, parametros)
        self.assertEqual(eventos[-1].resultado, resultado)
        return resultado

    def crear(self, nombre="Editor", prioridad=3):
        pid = self.gestor._siguiente_pid
        self.llamada("create_process", {"nombre": nombre, "prioridad": prioridad}, "PROC-01", {"pid": pid})
        return {"pid": pid, "nombre": nombre, "estado": "Listo", "prioridad": prioridad}

    def finalizar(self, pid, anterior="Listo"):
        return self.llamada("terminate_process", {"pid": pid}, "PROC-04",
                            {"pid": pid, "estado": "Finalizado", "estado_anterior": anterior})

    def test_CP_02_listado_y_vacio(self):
        self.llamada("list_processes", {}, "PROC-02", {"procesos": []})
        uno = self.crear()
        dos = self.crear("Calculadora", 5)
        self.llamada("list_processes", {}, "PROC-02", {"procesos": [uno, dos]})

    def test_CP_03_consulta_individual(self):
        proceso = self.crear()
        self.llamada("get_process", {"pid": 101}, "PROC-03", {"proceso": proceso})

    def test_CP_04_finalizar_conserva_registro_y_no_reutiliza_pid(self):
        proceso = self.crear()
        self.finalizar(101)
        proceso["estado"] = "Finalizado"
        self.llamada("get_process", {"pid": 101}, "PROC-03", {"proceso": proceso})
        self.llamada("list_processes", {}, "PROC-02", {"procesos": [proceso]})
        otro = self.crear()
        self.assertEqual(otro["pid"], 102)
        self.llamada("list_processes", {}, "PROC-02", {"procesos": [proceso, otro]})

    def test_CE_02_pid_inexistente_en_consulta_y_finalizacion(self):
        self.crear()
        for nombre in ("get_process", "terminate_process"):
            self.llamada(nombre, {"pid": 999}, "PROC_002", {})

    def test_CE_03_doble_finalizacion(self):
        self.crear()
        self.finalizar(101)
        self.llamada("terminate_process", {"pid": 101}, "PROC_003", {})

    def test_pid_invalido_y_tipos_no_convertidos_por_el_nucleo(self):
        self.crear()
        for nombre in ("get_process", "terminate_process"):
            for pid in (None, "101", 101.0, True, False, [], {}, 0, -1):
                with self.subTest(llamada=nombre, pid=pid):
                    self.llamada(nombre, {"pid": pid}, "PROC_002", {})

    def test_parametros_incompletos_y_extra_no_alcanzan_gestor(self):
        for nombre, parametros in (("get_process", {}), ("terminate_process", {}),
                                   ("get_process", {"pid": 999, "extra": 1}),
                                   ("terminate_process", {"pid": 999, "extra": 1}),
                                   ("list_processes", {"pid": 101})):
            with self.subTest(llamada=nombre, parametros=parametros):
                self.llamada(nombre, parametros, "SYS_002", {}, transporte=True)
                self.assertFalse(any("GestorProcesos" in s for s in self.app.consultar_recorrido()))

    def test_consultas_devuelven_copias_independientes(self):
        proceso = self.crear()
        consulta = self.llamada("get_process", {"pid": 101}, "PROC-03", {"proceso": proceso})
        listado = self.llamada("list_processes", {}, "PROC-02", {"procesos": [proceso]})
        consulta.datos["proceso"]["estado"] = "Alterado"
        listado.datos["procesos"][0]["nombre"] = "Alterado"
        listado.datos["procesos"].clear()
        self.llamada("get_process", {"pid": 101}, "PROC-03", {"proceso": proceso})
        self.llamada("list_processes", {}, "PROC-02", {"procesos": [proceso]})
        eventos = self.app.consultar_bitacora()
        self.assertEqual(eventos[1].resultado.datos, {"proceso": proceso})
        self.assertEqual(eventos[2].resultado.datos, {"procesos": [proceso]})

    def test_ejecutando_interno_consultas_no_mutan_y_finalizacion_valida(self):
        proceso = self.crear()
        # La prueba prepara Ejecutando mediante el gestor; la GUI no lo activa.
        self.gestor._cambiar_estado(101, EstadoProceso.EJECUTANDO)
        proceso["estado"] = "Ejecutando"
        self.llamada("get_process", {"pid": 101}, "PROC-03", {"proceso": proceso})
        self.llamada("list_processes", {}, "PROC-02", {"procesos": [proceso]})
        self.finalizar(101, "Ejecutando")
        self.assertEqual(self.app.consultar_bitacora()[-1].resultado.datos["estado_anterior"], "Ejecutando")

    def test_transicion_no_es_llamada_publica(self):
        self.crear()
        for nombre in ("_cambiar_estado", "_admitir", "execute_process"):
            self.llamada(nombre, {"pid": 101}, "SYS_001", {}, transporte=True)

    def test_recorrido_real_de_las_tres_llamadas_y_registro_previo_al_retorno(self):
        for nombre in ("list_processes", "get_process", "terminate_process"):
            with self.subTest(llamada=nombre):
                self.setUp()
                proceso = self.crear()
                orden = []

                def observar(etiqueta, metodo):
                    def ejecutar(*args, **kwargs):
                        orden.append(etiqueta + ":entrada")
                        resultado = metodo(*args, **kwargs)
                        orden.append(etiqueta + ":salida")
                        return resultado
                    return ejecutar

                with patch.object(self.gestor, nombre, side_effect=observar("gestor", getattr(self.gestor, nombre))):
                    self.dispatcher = Dispatcher(self.gestor)
                    self.kernel = Kernel(self.dispatcher, self.bitacora)
                    self.interfaz = InterfazSystemCalls(self.kernel)
                    self.app = AplicacionUsuario(self.interfaz)
                    with ExitStack() as pila:
                        for objeto, metodo, etiqueta in ((self.app, nombre, "app"),
                                                        (self.interfaz, nombre, "interfaz"),
                                                        (self.kernel, "atender", "kernel"),
                                                        (self.dispatcher, "despachar", "dispatcher"),
                                                        (self.bitacora, "registrar", "registro")):
                            pila.enter_context(patch.object(objeto, metodo,
                                side_effect=observar(etiqueta, getattr(objeto, metodo))))
                        if nombre == "list_processes":
                            self.llamada(nombre, {}, "PROC-02", {"procesos": [proceso]})
                        elif nombre == "get_process":
                            self.llamada(nombre, {"pid": 101}, "PROC-03", {"proceso": proceso})
                        else:
                            self.finalizar(101)
                self.assertEqual(orden, [
                    "app:entrada", "interfaz:entrada", "kernel:entrada", "dispatcher:entrada", "gestor:entrada",
                    "gestor:salida", "dispatcher:salida", "registro:entrada", "registro:salida",
                    "kernel:salida", "interfaz:salida", "app:salida",
                ])


class TransicionesInternas(unittest.TestCase):
    def test_matriz_completa_de_transiciones(self):
        permitidas = {
            (EstadoProceso.NUEVO, EstadoProceso.LISTO),
            (EstadoProceso.LISTO, EstadoProceso.EJECUTANDO),
            (EstadoProceso.EJECUTANDO, EstadoProceso.LISTO),
            (EstadoProceso.LISTO, EstadoProceso.FINALIZADO),
            (EstadoProceso.EJECUTANDO, EstadoProceso.FINALIZADO),
        }
        for anterior in EstadoProceso:
            for nuevo in EstadoProceso:
                with self.subTest(anterior=anterior, nuevo=nuevo):
                    gestor = GestorProcesos()
                    original = Proceso(101, "Editor", anterior, 3)
                    gestor._procesos[101] = original
                    if (anterior, nuevo) in permitidas:
                        gestor._cambiar_estado(101, nuevo)
                        self.assertEqual(gestor._procesos[101], replace(original, estado=nuevo))
                    else:
                        with self.assertRaises(ValueError):
                            gestor._cambiar_estado(101, nuevo)
                        self.assertEqual(gestor._procesos[101], original)

    def test_maximo_un_ejecutando_y_liberacion(self):
        gestor = GestorProcesos()
        gestor.create_process("Uno", 1)
        gestor.create_process("Dos", 5)
        gestor._cambiar_estado(101, EstadoProceso.EJECUTANDO)
        antes = dict(gestor._procesos)
        with self.assertRaises(ValueError):
            gestor._cambiar_estado(102, EstadoProceso.EJECUTANDO)
        self.assertEqual(gestor._procesos, antes)
        gestor._cambiar_estado(101, EstadoProceso.LISTO)
        gestor._cambiar_estado(102, EstadoProceso.EJECUTANDO)
        self.assertEqual(sum(p.estado == EstadoProceso.EJECUTANDO for p in gestor._procesos.values()), 1)
        gestor._cambiar_estado(102, EstadoProceso.FINALIZADO)
        gestor._cambiar_estado(101, EstadoProceso.EJECUTANDO)
        self.assertEqual(gestor._procesos[102].estado, EstadoProceso.FINALIZADO)

    def test_transicion_interna_con_pid_o_estado_invalido(self):
        gestor = GestorProcesos()
        gestor.create_process("Editor", 3)
        antes = dict(gestor._procesos)
        for pid, estado in ((999, EstadoProceso.LISTO), (True, EstadoProceso.LISTO),
                            (101, "Ejecutando"), (101, [])):
            with self.subTest(pid=pid, estado=estado):
                with self.assertRaises(ValueError):
                    gestor._cambiar_estado(pid, estado)
                self.assertEqual(gestor._procesos, antes)


if __name__ == "__main__":
    unittest.main()
