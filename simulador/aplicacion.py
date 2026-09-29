"""Programa en modo usuario; no conoce gestores ni accede al disco."""

from .bitacora import Evento
from .contratos import Resultado
from .interfaz_syscalls import InterfazSystemCalls


class AplicacionUsuario:
    def __init__(self, interfaz: InterfazSystemCalls) -> None:
        self._interfaz = interfaz
        self._ultimo_recorrido: tuple[str, ...] = ()

    def create_process(self, nombre: str, prioridad: int) -> Resultado:
        resultado = self._interfaz.create_process(nombre, prioridad)
        self._guardar_recorrido()
        return resultado

    def list_processes(self) -> Resultado:
        resultado = self._interfaz.list_processes()
        self._guardar_recorrido()
        return resultado

    def get_process(self, pid: int) -> Resultado:
        resultado = self._interfaz.get_process(pid)
        self._guardar_recorrido()
        return resultado

    def terminate_process(self, pid: int) -> Resultado:
        resultado = self._interfaz.terminate_process(pid)
        self._guardar_recorrido()
        return resultado

    def enviar_solicitud(self, llamada: str, parametros: dict[str, object]) -> Resultado:
        """Transporte de solicitudes; permite comprobar CE-10 sin otra system call."""
        resultado = self._interfaz.enviar_solicitud(llamada, parametros)
        self._guardar_recorrido()
        return resultado

    def _guardar_recorrido(self) -> None:
        self._ultimo_recorrido = (
            "Aplicación en modo usuario: solicitar servicio",
            *self._interfaz.consultar_recorrido(),
            "System Call Interface → Aplicación en modo usuario: resultado recibido",
        )

    def consultar_bitacora(self) -> tuple[Evento, ...]:
        return self._interfaz.consultar_bitacora()

    def consultar_recorrido(self) -> tuple[str, ...]:
        return self._ultimo_recorrido
