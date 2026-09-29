"""Enrutamiento explícito; nunca resuelve métodos desde texto arbitrario."""

from .contratos import Resultado, Solicitud
from .errores import error
from .archivos import GestorArchivos
from .procesos import GestorProcesos


class Dispatcher:
    def __init__(self, procesos: GestorProcesos, archivos: GestorArchivos | None = None) -> None:
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
        self._gestores = {nombre: "GestorProcesos" for nombre in self._registro}
        if archivos is not None:
            operaciones_archivos = {
                "create_file": (archivos.create_file, {"nombre"}),
                "open_file": (archivos.open_file, {"nombre", "modo"}),
                "read_file": (archivos.read_file, {"descriptor"}),
                "write_file": (archivos.write_file, {"descriptor", "datos"}),
                "close_file": (archivos.close_file, {"descriptor"}),
                "delete_file": (archivos.delete_file, {"nombre"}),
                "list_files": (archivos.list_files, set()),
            }
            for nombre, (metodo, parametros) in operaciones_archivos.items():
                self._registro[nombre] = metodo
                self._parametros[nombre] = parametros
                self._gestores[nombre] = "GestorArchivos"

    def despachar(self, solicitud: Solicitud, recorrido: list[str]) -> Resultado:
        recorrido.append("Dispatcher: identificar llamada")
        if not isinstance(solicitud.llamada, str) or solicitud.llamada not in self._registro:
            return error("SYS_001")
        parametros = solicitud.parametros
        if not isinstance(parametros, dict) or set(parametros) != self._parametros[solicitud.llamada]:
            return error("SYS_002")
        if solicitud.llamada == "write_file" and not isinstance(parametros["datos"], str):
            return error("SYS_002")
        # Los valores de dominio se validan en el gestor, no en esta capa.
        gestor = self._gestores[solicitud.llamada]
        recorrido.append(gestor + ": validar y procesar")
        resultado = self._registro[solicitud.llamada](**parametros)
        recorrido.append(gestor + " → Dispatcher: " + resultado.estado)
        return resultado
