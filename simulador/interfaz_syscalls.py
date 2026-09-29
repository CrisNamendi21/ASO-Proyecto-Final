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
