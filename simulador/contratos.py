"""Contratos simples de comunicación (diseño, secciones 6.3 y 8.1)."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Solicitud:
    llamada: str
    parametros: dict[str, object]


@dataclass(frozen=True)
class Resultado:
    estado: str
    codigo: str
    mensaje: str
    datos: dict[str, object] = field(default_factory=dict)
