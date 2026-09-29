"""Enrutamiento explícito; nunca resuelve métodos desde texto arbitrario."""

from .contratos import Resultado, Solicitud
from .errores import error
from .procesos import GestorProcesos


class Dispatcher:
    def __init__(self, procesos: GestorProcesos) -> None:
        # Registro cerrado: las siete llamadas de archivos siguen pendientes.
        self._registro = {
            "create_process": procesos.create_process,
            "list_processes": procesos.list_processes,
            "get_process": procesos.get_process,
            "terminate_process": procesos.terminate_process,
        }
        self._parametros = {
            "create_process": {"nombre", "prioridad"},
            "list_processes": set(),
            "get_process": {"pid"},
            "terminate_process": {"pid"},
        }

    def despachar(self, solicitud: Solicitud, recorrido: list[str]) -> Resultado:
        recorrido.append("Dispatcher: identificar llamada")
        if not isinstance(solicitud.llamada, str) or solicitud.llamada not in self._registro:
            return error("SYS_001")
        parametros = solicitud.parametros
        if not isinstance(parametros, dict) or set(parametros) != self._parametros[solicitud.llamada]:
            return error("SYS_002")
        # Los valores de dominio se validan en el gestor, no en esta capa.
        recorrido.append("GestorProcesos: validar y procesar")
        resultado = self._registro[solicitud.llamada](**parametros)
        recorrido.append("GestorProcesos → Dispatcher: " + resultado.estado)
        return resultado
