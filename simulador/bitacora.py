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
        parametros = deepcopy(solicitud.parametros)
        resultado_registrado = deepcopy(resultado)
        # Diseño §13.4: la bitácora registra cantidades, no el contenido leído/escrito.
        if solicitud.llamada == "write_file" and "datos" in parametros:
            datos = parametros.pop("datos")
            parametros["caracteres_solicitados"] = len(datos) if isinstance(datos, str) else None
        if solicitud.llamada == "read_file" and resultado.estado == "EXITO":
            contenido = resultado.datos.get("contenido")
            resultado_registrado = Resultado(
                resultado.estado,
                resultado.codigo,
                resultado.mensaje,
                {"caracteres_leidos": len(contenido)} if isinstance(contenido, str) else {},
            )
        self._eventos.append(Evento(
            numero=len(self._eventos) + 1,
            fecha_hora=datetime.now().astimezone().isoformat(timespec="seconds"),
            llamada=deepcopy(solicitud.llamada),
            parametros=parametros,
            resultado=resultado_registrado,
        ))

    def consultar(self) -> tuple[Evento, ...]:
        # Ni las colecciones anidadas de una consulta modifican el registro.
        return deepcopy(tuple(self._eventos))
