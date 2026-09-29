"""Modelo y gestión de procesos simulados (diseño, sección 9)."""

from dataclasses import dataclass, replace
from enum import Enum

from .contratos import Resultado
from .errores import error


class EstadoProceso(Enum):
    NUEVO = "Nuevo"
    LISTO = "Listo"
    EJECUTANDO = "Ejecutando"
    FINALIZADO = "Finalizado"


@dataclass(frozen=True)
class Proceso:
    pid: int
    nombre: str
    estado: EstadoProceso
    prioridad: int


class GestorProcesos:
    _TRANSICIONES = {
        EstadoProceso.NUEVO: {EstadoProceso.LISTO},
        EstadoProceso.LISTO: {EstadoProceso.EJECUTANDO, EstadoProceso.FINALIZADO},
        EstadoProceso.EJECUTANDO: {EstadoProceso.LISTO, EstadoProceso.FINALIZADO},
        EstadoProceso.FINALIZADO: set(),
    }

    def __init__(self) -> None:
        self._procesos: dict[int, Proceso] = {}
        self._siguiente_pid = 101

    def create_process(self, nombre: str, prioridad: int) -> Resultado:
        if not isinstance(nombre, str) or not nombre.strip() or len(nombre) > 50:
            return error("PROC_001")
        # bool es una subclase de int en Python, pero no una prioridad numérica.
        if type(prioridad) is not int or not 1 <= prioridad <= 5:
            return error("PROC_001")

        pid = self._siguiente_pid
        self._procesos[pid] = Proceso(pid, nombre, EstadoProceso.NUEVO, prioridad)
        self._admitir(pid)
        self._siguiente_pid += 1
        return Resultado("EXITO", "PROC-01", "Proceso creado correctamente.", {"pid": pid})

    def _admitir(self, pid: int) -> None:
        """Etapa interna de creación; no es una operación pública de ejecución."""
        self._cambiar_estado(pid, EstadoProceso.LISTO)

    def list_processes(self) -> Resultado:
        procesos = [self._informacion(proceso) for proceso in self._procesos.values()]
        return Resultado("EXITO", "PROC-02", f"Procesos encontrados: {len(procesos)}.",
                         {"procesos": procesos})

    def get_process(self, pid: int) -> Resultado:
        if not self._pid_existente(pid):
            return error("PROC_002")
        return Resultado("EXITO", "PROC-03", "Proceso consultado correctamente.",
                         {"proceso": self._informacion(self._procesos[pid])})

    def terminate_process(self, pid: int) -> Resultado:
        if not self._pid_existente(pid):
            return error("PROC_002")
        anterior = self._procesos[pid].estado
        if anterior == EstadoProceso.FINALIZADO:
            return error("PROC_003")
        self._cambiar_estado(pid, EstadoProceso.FINALIZADO)
        # DEC-008: conservar ambos estados en resultado y evento final (§8.2).
        return Resultado("EXITO", "PROC-04", "Proceso finalizado correctamente.",
                         {"pid": pid, "estado": EstadoProceso.FINALIZADO.value,
                          "estado_anterior": anterior.value})

    def _pid_existente(self, pid: int) -> bool:
        return type(pid) is int and pid in self._procesos

    @staticmethod
    def _informacion(proceso: Proceso) -> dict[str, object]:
        # Copia de valores: una consulta no entrega objetos internos del gestor.
        return {"pid": proceso.pid, "nombre": proceso.nombre,
                "estado": proceso.estado.value, "prioridad": proceso.prioridad}

    def _cambiar_estado(self, pid: int, nuevo: EstadoProceso) -> None:
        """Control interno (§9.4, DEC-001); nunca es una system call pública."""
        if not self._pid_existente(pid):
            raise ValueError("PID inválido para una transición interna.")
        proceso = self._procesos[pid]
        if not isinstance(nuevo, EstadoProceso) or nuevo not in self._TRANSICIONES[proceso.estado]:
            raise ValueError("Transición de estado no permitida.")
        if nuevo == EstadoProceso.EJECUTANDO and any(
            p.estado == EstadoProceso.EJECUTANDO for p in self._procesos.values()
        ):
            raise ValueError("Ya existe un proceso en estado Ejecutando.")
        # Validar todo antes de reemplazar. Finalizado no tiene transiciones de salida.
        self._procesos[pid] = replace(proceso, estado=nuevo)
