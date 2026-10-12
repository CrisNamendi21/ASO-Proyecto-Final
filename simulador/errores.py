"""Errores del simulador, incluidos los fallos físicos de almacenamiento."""

from .contratos import Resultado


CATALOGO = {
    "PROC_001": "Datos de proceso inválidos.",
    "PROC_002": "PID inválido o inexistente.",
    "PROC_003": "Proceso previamente finalizado.",
    "FILE_001": "Nombre o ruta de archivo inválida.",
    "FILE_002": "Archivo ya existente.",
    "FILE_003": "Archivo inexistente.",
    "FILE_004": "Modo de apertura inválido.",
    "FILE_005": "Archivo previamente abierto.",
    "FILE_006": "Descriptor inválido o archivo cerrado.",
    "FILE_007": "Operación no permitida por el modo de apertura.",
    "FILE_008": "Intento de eliminar un archivo abierto.",
    "FILE_009": "Fallo técnico al acceder al almacenamiento del simulador.",
    "SYS_001": "Llamada al sistema no reconocida.",
    "SYS_002": "Parámetros requeridos inválidos o incompletos.",
}


def error(codigo: str) -> Resultado:
    return Resultado("ERROR", codigo, CATALOGO[codigo])
