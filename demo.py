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
        resultados = []

        def comprobar(resultado, codigo_esperado):
            if resultado.codigo != codigo_esperado:
                raise RuntimeError(
                    f"Se esperaba {codigo_esperado} y se recibió {resultado.codigo}: "
                    f"{resultado.mensaje}")
            resultados.append(resultado)
            return resultado

        # Secuencia de la demostración exigida: proceso, archivo, error controlado,
        # finalización y eliminación, siempre mediante la aplicación pública.
        creacion = comprobar(app.create_process("Editor", 3), "PROC-01")
        pid = creacion.datos["pid"]
        comprobar(app.list_processes(), "PROC-02")
        comprobar(app.get_process(pid), "PROC-03")
        comprobar(app.create_file("demostracion.txt"), "FILE-01")
        apertura = comprobar(app.open_file("demostracion.txt", "rw"), "FILE-02")
        descriptor = apertura.datos["descriptor"]
        comprobar(app.write_file(descriptor, "Contenido de demostración"), "FILE-04")
        comprobar(app.read_file(descriptor), "FILE-03")
        comprobar(app.close_file(descriptor), "FILE-05")
        comprobar(app.list_files(), "FILE-07")
        comprobar(app.read_file(descriptor), "FILE_006")
        comprobar(app.terminate_process(pid), "PROC-04")
        consulta_final = comprobar(app.get_process(pid), "PROC-03")
        if consulta_final.datos["proceso"]["estado"] != "Finalizado":
            raise RuntimeError("La demostración no conservó el proceso Finalizado.")
        comprobar(app.delete_file("demostracion.txt"), "FILE-06")
        comprobar(app.enviar_solicitud("llamada_inexistente", {}), "SYS_001")
        comprobar(app.enviar_solicitud(
            "create_process", {"nombre": "Incompleto"}), "SYS_002")
        comprobar(app.list_files(), "FILE-07")

        eventos = app.consultar_bitacora()
        if len(eventos) != len(resultados):
            raise RuntimeError("La demostración no generó exactamente un evento por solicitud.")
        for resultado in resultados:
            print(json.dumps(asdict(resultado), ensure_ascii=False))
        print("\nBitácora (un evento por solicitud):")
        for evento in eventos:
            print(evento.numero, evento.llamada, evento.resultado.codigo)
        print("\nÚltimo recorrido:")
        print("\n".join(app.consultar_recorrido()))


if __name__ == "__main__":
    main()
