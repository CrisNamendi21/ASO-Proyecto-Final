"""Coordinación y único registro final de cada solicitud."""

from .bitacora import Bitacora, Evento
from .contratos import Resultado, Solicitud
from .dispatcher import Dispatcher


class Kernel:
    def __init__(self, dispatcher: Dispatcher, bitacora: Bitacora) -> None:
        self._dispatcher = dispatcher
        self._bitacora = bitacora

    def atender(self, solicitud: Solicitud, recorrido: list[str]) -> Resultado:
        recorrido.append("Kernel simulado: recibir solicitud")
        resultado = self._dispatcher.despachar(solicitud, recorrido)
        recorrido.append("Dispatcher → Kernel: " + resultado.estado)
        self._bitacora.registrar(solicitud, resultado)
        recorrido.append("Kernel: registrar evento final")
        return resultado

    def consultar_bitacora(self) -> tuple[Evento, ...]:
        return self._bitacora.consultar()
