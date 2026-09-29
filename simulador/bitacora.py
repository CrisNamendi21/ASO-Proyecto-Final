"""Registro en memoria con copias de consulta (secciones 6.8 y 13.4)."""

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime

from .contratos import Resultado, Solicitud


@dataclass(frozen=True)
class Evento:
    numero: int
    fecha_hora: str
    llamada: str
    parametros: dict[str, object]
    resultado: Resultado


class Bitacora:
    def __init__(self) -> None:
        self._eventos: list[Evento] = []

    def registrar(self, solicitud: Solicitud, resultado: Resultado) -> None:
        self._eventos.append(Evento(
            numero=len(self._eventos) + 1,
            fecha_hora=datetime.now().astimezone().isoformat(timespec="seconds"),
            llamada=deepcopy(solicitud.llamada),
            parametros=deepcopy(solicitud.parametros),
            resultado=deepcopy(resultado),
        ))

    def consultar(self) -> tuple[Evento, ...]:
        # Ni las colecciones anidadas de una consulta modifican el registro.
        return deepcopy(tuple(self._eventos))
