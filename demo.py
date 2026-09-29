"""Demostración de procesos a través de la aplicación en modo usuario."""

from dataclasses import asdict
import json
import sys

from main import crear_aplicacion


def main() -> None:
    # Windows puede usar cp1252 al redirigir stdout; el recorrido contiene flechas.
    sys.stdout.reconfigure(encoding="utf-8")
    app = crear_aplicacion()
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
    ]
    for resultado in resultados:
        print(json.dumps(asdict(resultado), ensure_ascii=False))
    print("\nBitácora (un evento por solicitud):")
    for evento in app.consultar_bitacora():
        print(evento.numero, evento.llamada, evento.resultado.codigo)
    print("\nÚltimo recorrido (rechazo antes del gestor):")
    print("\n".join(app.consultar_recorrido()))


if __name__ == "__main__":
    main()
