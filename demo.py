"""Demostración de procesos y archivos mediante la aplicación en modo usuario."""

from dataclasses import asdict
import json
from pathlib import Path
import sys
import tempfile

from main import crear_aplicacion


def main() -> None:
    # Windows puede usar cp1252 al redirigir stdout; el recorrido contiene flechas.
    sys.stdout.reconfigure(encoding="utf-8")
    # La demostración automatizada usa almacenamiento temporal para no tocar datos
    # personales ni el directorio persistente que utiliza la GUI.
    with tempfile.TemporaryDirectory() as temporal:
        app = crear_aplicacion(Path(temporal) / "archivos")
        creacion = app.create_process("Editor", 3)
        pid = creacion.datos["pid"]
        resultados = [
            creacion,
            app.list_processes(),
            app.get_process(pid),
            app.get_process(999),
            app.terminate_process(pid),
            app.get_process(pid),
            app.list_processes(),
            app.terminate_process(pid),
            app.create_process("", 6),
            app.enviar_solicitud("llamada_inexistente", {}),
            app.enviar_solicitud("create_process", {"nombre": "Incompleto"}),
            app.create_file("demostracion.txt"),
        ]
        apertura = app.open_file("demostracion.txt", "rw")
        resultados.append(apertura)
        descriptor = apertura.datos["descriptor"]
        resultados.extend([
            app.write_file(descriptor, "Contenido de demostración"),
            app.read_file(descriptor),
            app.list_files(),
            app.close_file(descriptor),
            app.delete_file("demostracion.txt"),
            app.list_files(),
        ])
        for resultado in resultados:
            print(json.dumps(asdict(resultado), ensure_ascii=False))
        print("\nBitácora (un evento por solicitud):")
        for evento in app.consultar_bitacora():
            print(evento.numero, evento.llamada, evento.resultado.codigo)
        print("\nÚltimo recorrido:")
        print("\n".join(app.consultar_recorrido()))


if __name__ == "__main__":
    main()
