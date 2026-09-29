"""Interfaz que estructura solicitudes y devuelve respuestas, sección 6.3."""

from .bitacora import Evento
from .contratos import Resultado, Solicitud
from .kernel import Kernel


class InterfazSystemCalls:
    def __init__(self, kernel: Kernel) -> None:
        self._kernel = kernel
        self._ultimo_recorrido: tuple[str, ...] = ()

    def create_process(self, nombre: str, prioridad: int) -> Resultado:
        return self.enviar_solicitud("create_process", {"nombre": nombre, "prioridad": prioridad})

    def list_processes(self) -> Resultado:
        return self.enviar_solicitud("list_processes", {})

    def get_process(self, pid: int) -> Resultado:
        return self.enviar_solicitud("get_process", {"pid": pid})

    def terminate_process(self, pid: int) -> Resultado:
        return self.enviar_solicitud("terminate_process", {"pid": pid})

    def create_file(self, nombre: str) -> Resultado:
        return self.enviar_solicitud("create_file", {"nombre": nombre})

    def open_file(self, nombre: str, modo: str) -> Resultado:
        return self.enviar_solicitud("open_file", {"nombre": nombre, "modo": modo})

    def read_file(self, descriptor: int) -> Resultado:
        return self.enviar_solicitud("read_file", {"descriptor": descriptor})

    def write_file(self, descriptor: int, datos: str) -> Resultado:
        return self.enviar_solicitud("write_file", {"descriptor": descriptor, "datos": datos})

    def close_file(self, descriptor: int) -> Resultado:
        return self.enviar_solicitud("close_file", {"descriptor": descriptor})

    def delete_file(self, nombre: str) -> Resultado:
        return self.enviar_solicitud("delete_file", {"nombre": nombre})

    def list_files(self) -> Resultado:
        return self.enviar_solicitud("list_files", {})

    def enviar_solicitud(self, llamada: str, parametros: dict[str, object]) -> Resultado:
        recorrido = ["System Call Interface: estructurar solicitud"]
        resultado = self._kernel.atender(Solicitud(llamada, parametros), recorrido)
        recorrido.append("Kernel → System Call Interface: devolver resultado")
        self._ultimo_recorrido = tuple(recorrido)
        return resultado

    def consultar_bitacora(self) -> tuple[Evento, ...]:
        return self._kernel.consultar_bitacora()

    def consultar_recorrido(self) -> tuple[str, ...]:
        return self._ultimo_recorrido
