# Simulador de interfaz de llamadas al sistema

Proyecto universitario de Arquitectura de Sistemas Operativos desarrollado en
Python con Tkinter/ttk. Permite crear, consultar y finalizar procesos simulados,
administrar archivos y observar el recorrido de cada solicitud por las capas del
sistema. Incluye once llamadas: cuatro de procesos y siete de archivos.

Los procesos existen en memoria. Los archivos son físicos y se guardan en
`datos/archivos/`. La transición entre usuario y kernel es conceptual: el programa
no cambia privilegios del procesador ni crea o termina procesos de Windows.

## Requisitos e instalación

Se necesita Python 3.10 o posterior con Tkinter. No hay paquetes externos que
instalar con pip. El entorno comprobado es Windows con Python 3.13.15 y Tk 8.6.

Extraer el paquete completo en una carpeta con permiso de escritura. Desde
PowerShell, abrir esa carpeta y comprobar el entorno:

```powershell
python --version
python -c "import tkinter; print('Tk', tkinter.TkVersion)"
```

## Ejecución

```powershell
python main.py
```

La ventana permite navegar entre Inicio, Procesos, Archivos y Bitácora. Después de
crear o modificar un recurso, pulsar **Listar procesos** o **Listar archivos** para
actualizar su tabla. Cada listado es una llamada y queda registrado en la bitácora.
El [manual de uso](MANUAL_USO.md) explica los campos y un recorrido de demostración.

## Arquitectura y estructura

```text
GUI → AplicacionUsuario → InterfazSystemCalls → Kernel → Dispatcher
    → GestorProcesos o GestorArchivos → Dispatcher → Kernel [registra evento]
    → InterfazSystemCalls → AplicacionUsuario → GUI
```

| Archivo o carpeta | Responsabilidad |
| --- | --- |
| `main.py` | Conecta los componentes y abre la ventana. |
| `simulador/gui/ventana.py` | Recoge entradas y presenta resultados. |
| `simulador/aplicacion.py` | Solicita servicios desde el modo usuario. |
| `simulador/interfaz_syscalls.py` | Estructura solicitudes y devuelve respuestas. |
| `simulador/kernel.py` | Coordina y registra cada evento antes del retorno. |
| `simulador/dispatcher.py` | Valida la estructura y enruta las llamadas conocidas. |
| `simulador/procesos.py` | Administra procesos, PID y transiciones. |
| `simulador/archivos.py` | Controla aperturas y acceso físico a los archivos. |
| `simulador/contratos.py` | Define `Solicitud` y `Resultado`. |
| `simulador/errores.py` | Centraliza los códigos y mensajes de error. |
| `simulador/bitacora.py` | Guarda eventos en memoria y devuelve copias de consulta. |
| `tests/` | Pruebas de integración, invariantes y pantalla de archivos. |
| `demo.py` | Demostración mediante la aplicación en modo usuario. |
| `datos/archivos/` | Almacenamiento de los archivos creados por la aplicación. |
| `docs/` | Especificación técnica y propuesta académica originales. |
| `verificar_entrega.py` | Comprueba archivos, Tkinter, compilación, pruebas y demostración. |
| `crear_paquete.py` | Genera el ZIP de entrega y su suma SHA-256. |

La GUI y la aplicación en modo usuario no acceden a los gestores ni al disco.
Las validaciones de recursos pertenecen a los gestores y funcionan sin abrir Tkinter.

## Llamadas y resultados

Todas las llamadas devuelven `Resultado` con `estado`, `codigo`, `mensaje` y `datos`.
El estado es `EXITO` o `ERROR`; `datos` siempre es un diccionario. Un código con
guion identifica la operación exitosa y un código con guion bajo identifica un error.

En la tabla, `P` representa un diccionario con `pid`, `nombre`, `estado` y
`prioridad`; `A` contiene `nombre`, `estado`, `descriptor` y `modo`.

| ID | Firma pública | Datos devueltos en un éxito |
| --- | --- | --- |
| PROC-01 | `create_process(nombre: str, prioridad: int)` | `{"pid": int}` |
| PROC-02 | `list_processes()` | `{"procesos": [P, ...]}` |
| PROC-03 | `get_process(pid: int)` | `{"proceso": P}` |
| PROC-04 | `terminate_process(pid: int)` | `{"pid": int, "estado": "Finalizado", "estado_anterior": str}` |
| FILE-01 | `create_file(nombre: str)` | `{"nombre": str, "estado": "Cerrado"}` |
| FILE-02 | `open_file(nombre: str, modo: str)` | `{"descriptor": int}` |
| FILE-03 | `read_file(descriptor: int)` | `{"contenido": str}` |
| FILE-04 | `write_file(descriptor: int, datos: str)` | `{"caracteres_escritos": int}` |
| FILE-05 | `close_file(descriptor: int)` | `{"descriptor": int, "estado": "Cerrado"}` |
| FILE-06 | `delete_file(nombre: str)` | `{"nombre": str}` |
| FILE-07 | `list_files()` | `{"archivos": [A, ...]}` |

Los listados vacíos son válidos. En un archivo cerrado, descriptor y modo son
`None`. Los errores de dominio y de solicitud devuelven `datos={}`. `FILE_009`
reserva esos datos para el diagnóstico de fallos del almacenamiento, según las
[notas técnicas](DECISIONES.md).

Los procesos aceptan nombres de 1 a 50 caracteres y prioridad entera de 1 a 5.
Se permiten nombres repetidos. Los PID comienzan en 101 y no se reutilizan durante
la sesión. Crear pasa de Nuevo a Listo; finalizar conserva el registro en estado
Finalizado. La prioridad es informativa y las consultas no cambian estados.

Los archivos aceptan nombres simples, una apertura activa por archivo y los modos
`r`, `w` y `rw`. Los descriptores comienzan en 1 y no se reutilizan durante la sesión.
Crear no abre y abrir no borra contenido. Escribir reemplaza todo el texto y devuelve
su cantidad de caracteres. Cerrar invalida el descriptor; eliminar exige un archivo
cerrado. La bitácora registra cantidades, sin copiar el contenido leído o escrito.

## Pruebas y demostración

```powershell
python -m unittest discover -s tests -v
python demo.py
python verificar_entrega.py
```

La demostración comprueba 16 solicitudes y un evento por solicitud, incluidas las
once operaciones, un descriptor cerrado, una llamada desconocida y parámetros
incompletos. Tanto la demostración como las pruebas de archivos usan directorios
temporales para conservar los datos de la aplicación.

La [matriz de pruebas](MATRIZ_PRUEBAS.md) relaciona CP, CA y CE con sus pruebas.
Los resultados y las limitaciones de verificación están en [EVIDENCIAS.md](EVIDENCIAS.md).

## Entrega

```powershell
python crear_paquete.py
```

Genera `dist/ASO_Proyecto_Final.zip` y `dist/ASO_Proyecto_Final.sha256`.
El ZIP incluye las fuentes, las pruebas y los documentos, con `datos/archivos/`
vacío. Su contenido se describe en [MANIFIESTO_ENTREGA.md](MANIFIESTO_ENTREGA.md).
Los documentos originales de `docs/` se distribuyen en el ZIP aunque esa carpeta
está excluida de Git; deben estar presentes para generar y verificar la entrega.

## Referencias y límites

La especificación `docs/Proyecto Arquitectura de sistemas operativos.docx` define
la arquitectura (§6), las llamadas (§8), los procesos (§9), los archivos (§10),
la interfaz (§12) y las pruebas (§13). `docs/Propuesta #7.pdf` contiene los
entregables y la rúbrica. La implementación en Python sigue la especificación técnica.

Las [notas técnicas](DECISIONES.md) explican los detalles que completan el diseño.
[ENTREGA_FINAL.md](ENTREGA_FINAL.md) resume las comprobaciones y
[GUIA_DEFENSA.md](GUIA_DEFENSA.md) sirve como apoyo para la exposición.

No se implementan un planificador real, procesos del anfitrión, base de datos ni
persistencia de procesos, aperturas o bitácora. Ejecutando existe en el modelo y sus
transiciones se validan internamente, pero no se activa automáticamente. Los archivos
no eliminados permanecen al cerrar la aplicación.

El confinamiento no garantiza aislamiento frente a cambios concurrentes de otros
programas. Las pruebas de enlaces simbólicos requieren que Windows permita crearlos;
una omisión por falta de privilegios no equivale a haber comprobado esos casos.
