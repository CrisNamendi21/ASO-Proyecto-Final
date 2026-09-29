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

    def create_file(self, nombre: str) -> Resultado:
        resultado = self._interfaz.create_file(nombre)
        self._guardar_recorrido()
        return resultado

    def open_file(self, nombre: str, modo: str) -> Resultado:
        resultado = self._interfaz.open_file(nombre, modo)
        self._guardar_recorrido()
        return resultado

    def read_file(self, descriptor: int) -> Resultado:
        resultado = self._interfaz.read_file(descriptor)
        self._guardar_recorrido()
        return resultado

    def write_file(self, descriptor: int, datos: str) -> Resultado:
        resultado = self._interfaz.write_file(descriptor, datos)
        self._guardar_recorrido()
        return resultado

    def close_file(self, descriptor: int) -> Resultado:
        resultado = self._interfaz.close_file(descriptor)
        self._guardar_recorrido()
        return resultado

    def delete_file(self, nombre: str) -> Resultado:
        resultado = self._interfaz.delete_file(nombre)
        self._guardar_recorrido()
        return resultado

    def list_files(self) -> Resultado:
        resultado = self._interfaz.list_files()
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
