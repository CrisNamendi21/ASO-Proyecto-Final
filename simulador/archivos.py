"""Gestión física confinada de archivos simulados (diseño, sección 10)."""

from dataclasses import dataclass
import os
from pathlib import Path, PureWindowsPath
import tempfile

from .contratos import Resultado
from .errores import error


@dataclass(frozen=True)
class Archivo:
    nombre: str
    ruta: Path


@dataclass(frozen=True)
class ArchivoAbierto:
    descriptor: int
    archivo: Archivo
    modo: str


class GestorArchivos:
    MODOS = {"r", "w", "rw"}
    PREFIJO_TEMPORAL = ".__simulador_tmp_"
    DISPOSITIVOS_WINDOWS = {
        "CON", "PRN", "AUX", "NUL", "CLOCK$",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }

    def __init__(self, raiz: Path) -> None:
        self._raiz_solicitada = Path(raiz).absolute()
        self._archivos_abiertos: dict[int, ArchivoAbierto] = {}
        self._siguiente_descriptor = 1
        try:
            self._raiz_solicitada.mkdir(parents=True, exist_ok=True)
            self._raiz = self._raiz_solicitada.resolve(strict=True)
        except OSError as exc:
            raise RuntimeError("No fue posible preparar el directorio administrado.") from exc
        if self._es_redireccion(self._raiz_solicitada) or not self._raiz.is_dir():
            raise ValueError("La raíz administrada no puede ser un enlace o redirección.")

    def create_file(self, nombre: str) -> Resultado:
        ruta, fallo = self._preparar_ruta(nombre)
        if fallo is not None:
            return fallo
        assert ruta is not None
        if ruta.exists() or ruta.is_symlink():
            return error("FILE_001" if self._es_redireccion(ruta) else "FILE_002")
        try:
            with ruta.open("x", encoding="utf-8", newline=""):
                pass
        except FileExistsError:
            return error("FILE_002")
        except OSError as exc:
            return self._fallo_fisico("crear", exc)
        return Resultado("EXITO", "FILE-01", "Archivo creado correctamente.",
                         {"nombre": nombre, "estado": "Cerrado"})

    def open_file(self, nombre: str, modo: str) -> Resultado:
        ruta, fallo = self._preparar_ruta(nombre)
        if fallo is not None:
            return fallo
        assert ruta is not None
        # Precedencia del diseño §10.7: existencia, modo y apertura activa.
        if not ruta.exists():
            return error("FILE_003")
        if self._es_redireccion(ruta) or not ruta.is_file():
            return error("FILE_001")
        if not isinstance(modo, str) or modo not in self.MODOS:
            return error("FILE_004")
        if self._apertura_por_ruta(ruta) is not None:
            return error("FILE_005")
        descriptor = self._siguiente_descriptor
        self._archivos_abiertos[descriptor] = ArchivoAbierto(
            descriptor, Archivo(nombre, ruta), modo)
        self._siguiente_descriptor += 1
        return Resultado("EXITO", "FILE-02", "Archivo abierto correctamente.",
                         {"descriptor": descriptor})

    def read_file(self, descriptor: int) -> Resultado:
        apertura = self._obtener_apertura(descriptor)
        if apertura is None:
            return error("FILE_006")
        if "r" not in apertura.modo:
            return error("FILE_007")
        validacion = self._validar_destino_descriptor(apertura)
        if validacion is not None:
            return validacion
        try:
            contenido = apertura.archivo.ruta.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            return self._fallo_fisico("leer", exc)
        return Resultado("EXITO", "FILE-03", "Archivo leído correctamente.",
                         {"contenido": contenido})

    def write_file(self, descriptor: int, datos: str) -> Resultado:
        apertura = self._obtener_apertura(descriptor)
        if apertura is None:
            return error("FILE_006")
        if "w" not in apertura.modo:
            return error("FILE_007")
        # El tipo de datos se valida también en el límite del dispatcher; esta defensa
        # evita que una llamada interna accidental llegue a las operaciones físicas.
        if not isinstance(datos, str):
            return error("SYS_002")
        validacion = self._validar_destino_descriptor(apertura)
        if validacion is not None:
            return validacion

        temporal: Path | None = None
        descriptor_fisico: int | None = None
        try:
            descriptor_fisico, nombre_temporal = tempfile.mkstemp(
                dir=self._raiz, prefix=self.PREFIJO_TEMPORAL, suffix=".tmp", text=True)
            temporal = Path(nombre_temporal)
            if self._es_redireccion(temporal) or temporal.parent.resolve(strict=True) != self._raiz:
                raise OSError("El archivo temporal quedó fuera de la raíz autorizada.")
            with os.fdopen(descriptor_fisico, "w", encoding="utf-8", newline="") as archivo:
                descriptor_fisico = None
                archivo.write(datos)
                archivo.flush()
                os.fsync(archivo.fileno())
            os.replace(temporal, apertura.archivo.ruta)
            temporal = None
        except (OSError, UnicodeError) as exc:
            if descriptor_fisico is not None:
                os.close(descriptor_fisico)
            limpieza = self._limpiar_temporal(temporal)
            return self._fallo_fisico("escribir", exc, limpieza)
        return Resultado("EXITO", "FILE-04", "Archivo escrito correctamente.",
                         {"caracteres_escritos": len(datos)})

    def close_file(self, descriptor: int) -> Resultado:
        apertura = self._obtener_apertura(descriptor)
        if apertura is None:
            return error("FILE_006")
        # Cerrar solo retira la apertura simulada. Debe poder liberar un descriptor
        # aunque otro programa haya borrado el archivo físico durante la sesión.
        del self._archivos_abiertos[descriptor]
        return Resultado("EXITO", "FILE-05", "Archivo cerrado correctamente.",
                         {"descriptor": descriptor, "estado": "Cerrado"})

    def delete_file(self, nombre: str) -> Resultado:
        ruta, fallo = self._preparar_ruta(nombre)
        if fallo is not None:
            return fallo
        assert ruta is not None
        if not ruta.exists():
            return error("FILE_003")
        if self._es_redireccion(ruta) or not ruta.is_file():
            return error("FILE_001")
        if self._apertura_por_ruta(ruta) is not None:
            return error("FILE_008")
        try:
            ruta.unlink()
        except OSError as exc:
            return self._fallo_fisico("eliminar", exc)
        return Resultado("EXITO", "FILE-06", "Archivo eliminado correctamente.",
                         {"nombre": nombre})

    def list_files(self) -> Resultado:
        fallo_raiz = self._validar_raiz()
        if fallo_raiz is not None:
            return fallo_raiz
        archivos: list[dict[str, object]] = []
        try:
            entradas = sorted(self._raiz.iterdir(), key=lambda p: p.name.casefold())
            for ruta in entradas:
                if ruta.name.startswith(self.PREFIJO_TEMPORAL):
                    continue
                if self._es_redireccion(ruta) or not ruta.is_file():
                    continue
                apertura = self._apertura_por_ruta(ruta)
                archivos.append({
                    "nombre": ruta.name,
                    "estado": "Abierto" if apertura else "Cerrado",
                    "descriptor": apertura.descriptor if apertura else None,
                    "modo": apertura.modo if apertura else None,
                })
        except OSError as exc:
            return self._fallo_fisico("listar", exc)
        return Resultado("EXITO", "FILE-07", f"Archivos encontrados: {len(archivos)}.",
                         {"archivos": archivos})

    def _preparar_ruta(self, nombre: object) -> tuple[Path | None, Resultado | None]:
        if not self._nombre_valido(nombre):
            return None, error("FILE_001")
        fallo_raiz = self._validar_raiz()
        if fallo_raiz is not None:
            return None, fallo_raiz
        ruta = self._raiz / nombre
        try:
            if ruta.parent.resolve(strict=True) != self._raiz:
                return None, error("FILE_001")
        except OSError as exc:
            return None, self._fallo_fisico("acceder_raiz", exc)
        return ruta, None

    def _nombre_valido(self, nombre: object) -> bool:
        if not isinstance(nombre, str) or not nombre.strip() or nombre in {".", ".."}:
            return False
        if nombre.startswith(self.PREFIJO_TEMPORAL) or any(ord(c) < 32 for c in nombre):
            return False
        if any(c in nombre for c in '<>:"/\\|?*'):
            return False
        if nombre.endswith((" ", ".")) or Path(nombre).is_absolute():
            return False
        windows = PureWindowsPath(nombre)
        if windows.is_absolute() or windows.drive or windows.root:
            return False
        base = nombre.split(".", 1)[0].upper()
        return base not in self.DISPOSITIVOS_WINDOWS

    def _validar_raiz(self) -> Resultado | None:
        try:
            self._raiz_solicitada.lstat()
            if self._es_redireccion(self._raiz_solicitada):
                return error("FILE_001")
            if not self._raiz_solicitada.is_dir():
                return self._fallo_fisico(
                    "acceder_raiz", NotADirectoryError("La raíz administrada dejó de ser un directorio."))
            if self._raiz_solicitada.resolve(strict=True) != self._raiz:
                return error("FILE_001")
        except OSError as exc:
            return self._fallo_fisico("acceder_raiz", exc)
        return None

    @staticmethod
    def _es_redireccion(ruta: Path) -> bool:
        try:
            if ruta.is_symlink():
                return True
            estado = ruta.lstat()
            atributos = getattr(estado, "st_file_attributes", 0)
            es_reparse = bool(
                atributos & getattr(__import__("stat"), "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))
            # Un hard link dentro de la raíz podría exponer el contenido de un archivo
            # externo aunque no cambie la ruta resuelta.
            es_hardlink = ruta.is_file() and getattr(estado, "st_nlink", 1) > 1
            return es_reparse or es_hardlink
        except (FileNotFoundError, OSError):
            return False

    def _obtener_apertura(self, descriptor: object) -> ArchivoAbierto | None:
        if type(descriptor) is not int:
            return None
        return self._archivos_abiertos.get(descriptor)

    def _apertura_por_ruta(self, ruta: Path) -> ArchivoAbierto | None:
        return next((a for a in self._archivos_abiertos.values() if a.archivo.ruta == ruta), None)

    def _validar_destino_descriptor(self, apertura: ArchivoAbierto) -> Resultado | None:
        ruta = apertura.archivo.ruta
        fallo_raiz = self._validar_raiz()
        if fallo_raiz is not None:
            return fallo_raiz
        if ruta.parent != self._raiz or self._es_redireccion(ruta):
            return error("FILE_001")
        if not ruta.exists() or not ruta.is_file():
            return self._fallo_fisico("acceder", FileNotFoundError("El archivo abierto ya no está disponible."))
        return None

    @staticmethod
    def _limpiar_temporal(temporal: Path | None) -> str | None:
        if temporal is None:
            return None
        try:
            if temporal.exists():
                temporal.unlink()
        except OSError as exc:
            return f"{type(exc).__name__}: {exc}"
        return None

    @staticmethod
    def _fallo_fisico(operacion: str, exc: Exception,
                      limpieza: str | None = None) -> Resultado:
        datos: dict[str, object] = {
            "operacion": operacion,
            "tipo": type(exc).__name__,
            "codigo_host": getattr(exc, "winerror", None) or getattr(exc, "errno", None),
        }
        if limpieza:
            datos["fallo_limpieza_temporal"] = limpieza
        return Resultado("ERROR", "FILE_009",
                         "Fallo técnico al acceder al almacenamiento del simulador.", datos)
