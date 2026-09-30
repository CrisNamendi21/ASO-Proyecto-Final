# Simulador de interfaz de llamadas al sistema

Proyecto universitario de Arquitectura de Sistemas Operativos en Python y
Tkinter/ttk. **Incremento 7: paquete portable de entrega.**
Están implementadas las once llamadas: cuatro de procesos y siete de archivos.
La matriz CP/CA/CE, la revisión visual, el manual, las evidencias y el paquete
portable de entrega están consolidados.

La simulación no cambia privilegios del procesador, no ejecuta código dentro del
kernel anfitrión ni crea o termina procesos reales. Los archivos son físicos y se
limitan a `datos/archivos/`; procesos, aperturas, descriptores y eventos existen solo
durante la sesión.

## Fuentes y decisiones del usuario

- `docs/Proyecto Arquitectura de sistemas operativos.docx`: especificación principal;
  arquitectura (§6), contratos (§8), procesos (§9), GUI (§12), pruebas (§13) y
  resultados esperados (§14). Fuente leída, incluidas tablas y siete figuras.
- `docs/Propuesta #7.pdf`: entregables, programa de prueba, demostración y rúbrica.
  Fuente revisada completa (10 páginas).
- `AGENTS.md` y conversación: restricciones adicionales y desarrollo incremental.
- Python prevalece por decisión explícita del usuario; la propuesta contiene
  referencias a C y una introducción que admite Python. No se afirma autorización
  del profesor. Tkinter/ttk y el plazo máximo de 14 días se mantienen.
- Análisis, estructura, contratos propuestos y primer incremento aprobados.
- El usuario confirmó rechazar nombres de solo espacios con `PROC_001`, conservar
  sin recortar los nombres válidos y contar su longitud original.

No se modificaron documentos fuente. `docs/` y `AGENTS.md` están ignorados en Git,
pero `crear_paquete.py` los incorpora expresamente al ZIP local de entrega.

Las decisiones que concretan vacíos del diseño y las excepciones autorizadas se
mantienen en [DECISIONES.md](DECISIONES.md), con fuente, motivo, aprobación, estado
y evidencia. Ese registro no sustituye las fuentes ni `AGENTS.md`. Se ubica en la
raíz para que no quede excluido por la regla existente que ignora `docs/`.
La correspondencia caso por caso está en [MATRIZ_PRUEBAS.md](MATRIZ_PRUEBAS.md).
El uso reproducible de la aplicación está en [MANUAL_USO.md](MANUAL_USO.md), la
evidencia consolidada en [EVIDENCIAS.md](EVIDENCIAS.md) y el guion de exposición en
[GUIA_DEFENSA.md](GUIA_DEFENSA.md).
El resultado contra los criterios de aceptación está en
[ENTREGA_FINAL.md](ENTREGA_FINAL.md).

## Preparación y ejecución

Se necesita Python con Tkinter. No hay dependencias externas ni paquetes que instalar
con pip. Entorno comprobado: **Windows, Python 3.13.15, Tk 8.6**.

Desde PowerShell, dentro de la carpeta del proyecto:

```powershell
python --version
python -c "import tkinter; print('Tk', tkinter.TkVersion)"
python main.py
```

Demostración del núcleo sin abrir Tkinter:

```powershell
python demo.py
```

Pruebas:

```powershell
python -m unittest discover -s tests -v
```

Verificación completa de entrega:

```powershell
python verificar_entrega.py
```

Creación del paquete portable y su suma SHA-256:

```powershell
python crear_paquete.py
```

El contenido y las exclusiones del ZIP se detallan en
[MANIFIESTO_ENTREGA.md](MANIFIESTO_ENTREGA.md). El paquete deja
`datos/archivos/` vacío para no distribuir archivos personales o de demostración.

`demo.py` fuerza UTF-8 en su salida para que las flechas del recorrido funcionen
también en una consola Windows con salida redirigida. Usa un directorio temporal
aislado y no modifica `datos/archivos/`.

## Qué incluyen los incrementos 1 a 4

- Crear un proceso: nombre no vacío, máximo 50 caracteres; prioridad entera 1–5.
- Rechazar nombres de solo espacios y valores de tipos incorrectos. Los booleanos
  no se aceptan como prioridades aunque Python los considere subclases de `int`.
- Admitir nombres repetidos; PID secuenciales desde 101. Un rechazo no consume PID.
- Registrar internamente `Nuevo` y pasar a `Listo` antes del éxito.
- Devolver un `Resultado` con `estado`, `codigo`, `mensaje`, `datos`.
- Registrar exactamente un evento por llamada, incluyendo rechazos.
- Consultar copias de bitácora y recorrido sin crear nuevos eventos.
- GUI con Inicio, Procesos, Archivos, Bitácora y Salir.
- Catálogo central de errores del diseño y `FILE_009`, ampliación aprobada para
  fallos físicos del almacenamiento.
- `list_processes()` con lista vacía válida y copias de PID, nombre, estado y prioridad.
- `get_process(pid)` con consulta individual y `PROC_002` para PID inválido o inexistente.
- `terminate_process(pid)` conserva el registro, cambia a Finalizado y devuelve
  estado anterior y final; una segunda finalización produce `PROC_003`.
- Matriz interna de transiciones, máximo un Ejecutando y estado Finalizado terminal.
- Según DEC-001, Ejecutando no se activa automáticamente ni dispone de botón o llamada pública.
- `ttk.Treeview` con PID, Nombre, Estado y Prioridad, actualizado únicamente mediante
  una llamada real a `list_processes()`; seleccionar una fila completa el PID.
- Crear, abrir, leer, escribir, cerrar, eliminar y listar archivos mediante
  descriptores simulados secuenciales desde 1.
- Modos exactos `r`, `w` y `rw`, una apertura por archivo, reemplazo total al escribir
  y permanencia del contenido entre sesiones.
- Nombres simples y confinamiento bajo `datos/archivos/`; traversal, rutas absolutas,
  dispositivos, flujos alternativos y redirecciones se rechazan.
- Escritura protegida mediante temporal dentro de la raíz y reemplazo posterior;
  un fallo conserva el original y devuelve `FILE_009`.
- La bitácora registra descriptores y cantidades, sin copiar el contenido leído o escrito.

Las once llamadas están completas. La enum y el gestor de procesos aplican todas
las transiciones del diseño; el funcionamiento público normal usa Nuevo → Listo →
Finalizado, conforme a DEC-001.

## Recorrido y responsabilidades

```text
GUI → AplicacionUsuario → InterfazSystemCalls → Kernel → Dispatcher
    → GestorProcesos o GestorArchivos → Dispatcher → Kernel [registra evento]
    → InterfazSystemCalls → AplicacionUsuario → GUI
```

| Archivo | Componente y responsabilidad |
| --- | --- |
| `main.py` | Composición de componentes y arranque; sin lógica de recursos. |
| `simulador/aplicacion.py` | Aplicación en modo usuario; solo solicita servicios. |
| `simulador/interfaz_syscalls.py` | Estructura solicitudes y devuelve respuestas. |
| `simulador/kernel.py` | Coordina y registra el evento antes del retorno. |
| `simulador/dispatcher.py` | Registro explícito de operaciones y validación estructural. |
| `simulador/procesos.py` | `Proceso`, `EstadoProceso`, `GestorProcesos`; dueño del estado. |
| `simulador/archivos.py` | `Archivo`, aperturas y `GestorArchivos`; único acceso físico a los archivos. |
| `simulador/contratos.py` | Dataclasses `Solicitud` y `Resultado`. |
| `simulador/errores.py` | Catálogo del diseño §13.1. |
| `simulador/bitacora.py` | Eventos en memoria y copias de consulta. |
| `simulador/gui/ventana.py` | Entradas y presentación; no importa gestores ni accede al disco. |
| `demo.py` | Programa de prueba a través de la aplicación en modo usuario. |
| `tests/test_integracion.py` | Pruebas de contratos, efectos, eventos y recorrido real. |
| `tests/test_archivos.py` | CA-01–CA-07, CE-04–CE-09, permisos, persistencia, fallos y confinamiento. |

Las pruebas internas inspeccionan invariantes privadas cuando es necesario. Las
pruebas de integración entran por `AplicacionUsuario`; la GUI y la aplicación nunca
importan gestores ni acceden al disco.

## Contrato vigente y validaciones

Las firmas públicas son las once indicadas en el diseño: `create_process`,
`list_processes`, `get_process`, `terminate_process`, `create_file`, `open_file`,
`read_file`, `write_file`, `close_file`, `delete_file` y `list_files`. Todas devuelven
un `Resultado`.

| Resultado | estado | codigo | datos |
| --- | --- | --- | --- |
| Creación válida | `EXITO` | `PROC-01` | `{"pid": 101}` (PID asignado) |
| Listado válido | `EXITO` | `PROC-02` | `{"procesos": [...]}` |
| Consulta válida | `EXITO` | `PROC-03` | `{"proceso": {...}}` |
| Finalización válida | `EXITO` | `PROC-04` | `{"pid": 101, "estado": "Finalizado", "estado_anterior": "Listo"}` |
| Nombre o prioridad inválidos | `ERROR` | `PROC_001` | `{}` |
| PID inválido o inexistente | `ERROR` | `PROC_002` | `{}` |
| Proceso previamente finalizado | `ERROR` | `PROC_003` | `{}` |
| Llamada desconocida | `ERROR` | `SYS_001` | `{}` |
| Estructura de parámetros inválida/incompleta | `ERROR` | `SYS_002` | `{}` |

La prioridad es informativa. No hay scheduler ni ejecución real.

| Operación válida | codigo | forma de `datos` |
| --- | --- | --- |
| `create_file` | `FILE-01` | `{"nombre": str, "estado": "Cerrado"}` |
| `open_file` | `FILE-02` | `{"descriptor": int}` |
| `read_file` | `FILE-03` | `{"contenido": str}` |
| `write_file` | `FILE-04` | `{"caracteres_escritos": int}` |
| `close_file` | `FILE-05` | `{"descriptor": int, "estado": "Cerrado"}` |
| `delete_file` | `FILE-06` | `{"nombre": str}` |
| `list_files` | `FILE-07` | `{"archivos": [{"nombre", "estado", "descriptor", "modo"}, ...]}` |

Los errores `FILE_001`–`FILE_008` devuelven `datos={}`. `FILE_009`, ampliación
aprobada en DEC-002, devuelve diagnóstico con `operacion`, `tipo` y `codigo_host`;
puede incluir `fallo_limpieza_temporal`. No contiene el texto del archivo.

Esto no está especificado en el documento; lo propongo como decisión de implementación:
los valores concretos `EXITO`/`ERROR` y el diccionario `datos` son la representación
uniforme aprobada en el análisis. Las dataclasses no exponen procesos internos.

`enviar_solicitud(llamada, parametros)` es el transporte general hacia el mismo
kernel, no una system call adicional. Permite demostrar solicitudes desconocidas o
incompletas sin provocar un `TypeError` por omitir argumentos de un método Python.
Por ejemplo, la aplicación puede enviar `create_process` con solo `nombre` y recibir
`SYS_002`. La GUI usa el método con firma explícita.

Precedencia:

1. Identificación: llamada no textual o no registrada → `SYS_001`.
2. Estructura: parámetros no representados por un diccionario, ausentes o extra → `SYS_002`.
3. Dominio: nombre inválido o prioridad inválida → `PROC_001` en el gestor.

En archivos, `open_file` valida nombre, existencia, redirección/tipo, modo y apertura
activa en ese orden. Las operaciones por descriptor validan primero el descriptor y
luego su permiso; `delete_file` comprueba nombre, existencia, redirección/tipo y
apertura. Así, cada entrada que infringe varias reglas tiene un resultado reproducible.

Identificar antes de procesar corresponde al flujo del diseño §11.5. Esto no está
especificado en el documento; lo propongo como decisión de implementación: exigir
exactamente las claves de la firma impide aceptar parámetros adicionales ignorados.
Nombre y prioridad comparten código, por lo que su orden no cambia el resultado.

La bitácora incluye número, fecha/hora con zona local, llamada, parámetros y
`Resultado` (estado, código, mensaje y datos). En `write_file` reemplaza el texto por
`caracteres_solicitados`; en `read_file` registra `caracteres_leidos` en vez del
contenido. Las demás llamadas conservan sus parámetros y resultado completos.

Esto no está especificado en el documento; lo propongo como decisión de implementación:
la bitácora permanece en memoria y su consulta devuelve copias mediante aplicación,
interfaz y kernel, sin una nueva system call. El recorrido se conserva como una tupla
de etapas de la última llamada, registradas en los puntos reales de transferencia.
Consultar cualquiera de ambos no altera recursos ni genera eventos.

## Uso y comprobación visual

1. Ejecutar `python main.py`; Inicio describe la simulación y el alcance actual.
2. Ir a Procesos y pulsar Crear proceso con nombre vacío: debe mostrar `PROC_001`.
3. Escribir `Editor`, dejar prioridad 3 y crear: debe mostrar `PROC-01`, PID 101.
4. Crear otro proceso: debe recibir PID 102, incluso si el nombre se repite.
5. Revisar el recorrido conceptual y abrir Bitácora. Cada intento tiene un evento.
6. Seleccionar un evento para ver parámetros, estado, código, mensaje y datos.
7. Ir a Archivos, crear `ejemplo.txt`, elegir `rw`, abrir y observar el descriptor 1.
8. Escribir texto, leerlo, cerrar y listar. La fila debe mostrar estado Cerrado.
9. Abrirlo de nuevo, intentar eliminarlo y observar `FILE_008`; cerrarlo y eliminarlo.
10. Crear `../externo.txt` debe devolver `FILE_001` sin crear nada fuera de la raíz.
11. Cambiar de pantalla y regresar: consultar la bitácora no añade eventos.
12. Pulsar Salir. Al abrir otra sesión la bitácora está vacía, el primer PID es 101
    y el primer descriptor es 1; los archivos no eliminados permanecen.

Las tablas no se actualizan fabricando filas después de una modificación. El usuario
pulsa Listar procesos o Listar archivos; esa llamada atraviesa las capas, genera su
evento y reemplaza la tabla con los datos devueltos.

## Trazabilidad y evidencia

| Regla | Fuente | Implementación | Prueba |
| --- | --- | --- | --- |
| Creación válida y Nuevo → Listo | §§8.2, 9.3, 9.6; CP-01 | `procesos.py` | `test_CP_01_creacion_y_transicion_nuevo_listo` |
| Rechazo sin registrar proceso | §9.9; CE-01 | `procesos.py` | `test_CE_01_datos_invalidos` |
| Límites, tipos y nombres repetidos | §§9.1, 9.5, 9.9 | `procesos.py` | `test_limites_nombre_y_prioridad`, `test_tipos_invalidos`, `test_repetidos_y_pid_secuenciales_sin_consumir_por_rechazo` |
| Espacios y conservación del nombre | Decisión explícita del usuario | `procesos.py` | `test_espacios_y_nombre_conservado` |
| Llamada desconocida | §13.1; CE-10 | `dispatcher.py` | `test_CE_10_llamada_desconocida` |
| Solicitud incompleta | §13.1; CE-10 | `dispatcher.py` | `test_CE_10_parametros_incompletos` |
| Estructura, extras y precedencia | §11.5 y decisión de implementación | `dispatcher.py` | `test_solicitud_mal_formada_y_parametros_extra`, `test_precedencia_identificacion_estructura_dominio` |
| Respuesta, efecto y evento por solicitud | §§8.1, 13.4–13.5 | Contratos, gestor, kernel y bitácora | Ayudante `comprobar_llamada` usado en cada solicitud de integración |
| Recorrido y registro antes del retorno | §§6.9, 8.4, 11.1 | Todas las capas | `test_recorrido_real_y_registro_antes_del_retorno` observa las invocaciones reales |
| Consulta sin alteración ni eventos | §12.8 y `AGENTS.md` | Copias en `bitacora.py` | `test_copias_no_permiten_modificar_registro_ni_estado`, `test_consultas_de_bitacora_y_recorrido_no_generan_eventos` |
| Reinicio de estado temporal | §§9.5, 12.9 | Nuevas instancias | `test_sesiones_independientes` |
| Listar, consultar y finalizar | §§8.2, 9.7–9.8; CP-02–CP-04 | Capas y `procesos.py` | `test_CP_02_listado_y_vacio`, `test_CP_03_consulta_individual`, `test_CP_04_finalizar_conserva_registro_y_no_reutiliza_pid` |
| PID inválido y doble finalización | §9.9; CE-02–CE-03 | `procesos.py` | `test_CE_02_pid_inexistente_en_consulta_y_finalizacion`, `test_CE_03_doble_finalizacion`, pruebas de tipos |
| Transiciones y un solo Ejecutando | §§9.3–9.4; DEC-001 | `_cambiar_estado` interno | `TransicionesInternas` y prueba de finalización desde Ejecutando |
| Estado anterior en finalización | §8.2; DEC-008 aprobada | resultado PROC-04 y evento | pruebas CP-04 y Ejecutando |
| Flujo completo de archivos | §§8.3, 10; CA-01–CA-07 | Capas y `archivos.py` | `test_CA_01_a_CA_07_flujo_documental_completo` |
| Existencia, apertura y descriptores inválidos | §10.7–10.13; CE-04–CE-09 | `archivos.py` | pruebas `test_CE_04` a `test_CE_09` |
| Modos, reemplazo y descriptores secuenciales | §§10.4–10.10 | `archivos.py` | `test_modos_no_truncan_y_aplican_permisos`, pruebas de reemplazo y secuencia |
| Persistencia y reinicio de aperturas | §10.15 | `archivos.py` | `test_persistencia_fisica_y_reinicio_de_aperturas` |
| Confinamiento y archivo externo intacto | §10; `AGENTS.md` | validación de nombres, raíz y destinos | pruebas de traversal, rutas, enlaces y hard links |
| Fallos físicos sin falso éxito | DEC-002 aprobada | `FILE_009` | pruebas de lectura, temporal y reemplazo fallidos |
| Raíz eliminada y codificación inválida | DEC-002 aprobada | `FILE_009` sin excepción sin manejar | pruebas de raíz y codificación |
| Cierre tras desaparición física | §§10.10, 10.13; DEC-010 | invalida el descriptor sin acceder al disco | `test_cierre_libera_descriptor_si_archivo_desaparece_externamente` |
| Bitácora sin copiar contenidos | §13.4 | `bitacora.py` | `test_bitacora_registra_cantidades_sin_contenido` |
| Registro cerrado de 11 llamadas | §8 | `dispatcher.py` | `test_dispatcher_registra_exactamente_las_once_system_calls` |
| Pantalla con las siete operaciones | §12.6 | `gui/ventana.py` | secuencia Tk real y geometría sin recortes a 850×700 |

Verificación realizada el 29 de septiembre de 2026:

- Python 3.13.15 y Tk 8.6 disponibles.
- `python -m unittest discover -s tests -v`: **14 pruebas correctas**, con subcasos
  adicionales de límites y tipos; ninguna omitida.
- `python demo.py`: un éxito y tres rechazos, cuatro eventos y recorrido de
  parámetros incompletos sin entrada al gestor. Se corrigió un fallo de codificación
  de consola detectado en la primera ejecución y la demostración se volvió a ejecutar.
- Revisión visual mediante control de la ventana: Inicio, Procesos, rechazo de nombre
  vacío, creación de Editor con PID 101 y dos eventos de éxito/error en Bitácora.
  Se ajustó el espacio del recorrido y el detalle de eventos tras esa inspección.
- Segunda revisión visual tras el ajuste: recorrido de ida y vuelta completo y
  detalle del evento visibles; nueva sesión con bitácora vacía y creación con PID 101.
  Se comprobó el cierre mediante Salir y la terminación de la sesión anterior.
- Comprobación de independencia: importar `main` y construir la aplicación de
  usuario no incorpora `tkinter` a los módulos cargados.
- Incremento 2: `python -m unittest discover -s tests -v`: **28 pruebas correctas**,
  sin omisiones. `python demo.py` recorrió creación, listado, consulta, PID inexistente,
  finalización, consulta/listado de Finalizado y doble finalización, con un evento por solicitud.
- Revisión visual del incremento 2: Inicio, los cuatro controles, listado vacío,
  creación de PID 101, aviso de tabla desactualizada, listado con sus cuatro columnas,
  selección de fila, consulta individual, finalización con estado anterior y final,
  nuevo listado conservando el proceso Finalizado, error `PROC_003` por doble
  finalización y cinco eventos correspondientes en Bitácora. Se cerró mediante Salir.
- Incremento 3: `python -m unittest discover -s tests -v`: **51 pruebas ejecutadas**,
  **49 correctas y 2 omitidas**. Las omisiones son las pruebas de symlink de archivo
  y directorio: Windows devolvió `WinError 1314` por falta del privilegio para crearlos.
  La prueba de hard link sí se ejecutó. Ninguna prueba utiliza `datos/archivos/`.
- La versión de `demo.py` del incremento 3 recorrió 19 solicitudes de procesos y
  archivos con un evento por solicitud y almacenamiento temporal aislado.
- `python -m compileall -q main.py demo.py simulador tests`: sin errores.
- Prueba funcional de Tk real: crear, abrir, escribir, leer, listar, provocar
  `FILE_008`, cerrar, eliminar, listar vacío y consultar nueve eventos. La ventana
  también abrió con `python main.py`. El controlador de escritorio disponible no
  expuso ventanas nativas, por lo que no se afirma una inspección visual manual de
  distribución, tamaños o recortes para este incremento.
- Incremento 4: revisión consolidada con **58 pruebas ejecutadas, 56 correctas y
  2 omitidas** por el mismo privilegio de symlinks. Se añadieron nombres y tipos
  inválidos, raíz eliminada, codificación no válida, liberación de un descriptor
  obsoleto, datos no textuales y registro exacto de las 11 llamadas.
- La GUI se reorganizó después de detectar que Archivos solicitaba 406 píxeles y
  solo recibía 330. Resultado y Recorrido ahora están en paralelo; las cuatro vistas
  disponen de su tamaño solicitado incluso con una ventana de 850×700.
- `python demo.py`: 16 solicitudes en el orden de la demostración académica, códigos
  verificados y exactamente un evento por solicitud. El archivo se crea y elimina
  dentro de un directorio temporal.
- Incremento 5: revisión visual manual con la ventana nativa a 1050×780. Inicio,
  Procesos, Archivos y Bitácora se observaron sin recortes. Se creó y listó el proceso
  temporal `Evidencia` (PID 101), se comprobó su resultado y recorrido, y la bitácora
  mostró exactamente los eventos `create_process` y `list_processes`. El detalle y
  los pasos reproducibles están en [EVIDENCIAS.md](EVIDENCIAS.md).
- Se añadieron [MANUAL_USO.md](MANUAL_USO.md), [EVIDENCIAS.md](EVIDENCIAS.md) y
  [GUIA_DEFENSA.md](GUIA_DEFENSA.md). No contienen requisitos nuevos: presentan la
  implementación, pruebas y decisiones ya documentadas.
- Incremento 6: [verificar_entrega.py](verificar_entrega.py) reúne comprobación de
  archivos requeridos, Tkinter, compilación, pruebas y demostración. Su ejecución
  final devolvió `ENTREGA VERIFICADA`. [ENTREGA_FINAL.md](ENTREGA_FINAL.md) contrasta
  cada criterio de aceptación con su evidencia.
- Incremento 7: [crear_paquete.py](crear_paquete.py) genera una entrega portable
  mediante una lista explícita de fuentes, pruebas, manuales y documentos originales.
  Excluye Git, cachés, artefactos previos y datos personales; además produce una suma
  SHA-256. El contenido se define en [MANIFIESTO_ENTREGA.md](MANIFIESTO_ENTREGA.md).

La prueba funcional de Tk complementa la revisión visual manual. Los enlaces
simbólicos deben volver a probarse en un entorno con ese privilegio.

## Pendiente

- Ejecutar las pruebas de symlink en un entorno Windows con privilegio para crearlos.
- Antes de entregar, el equipo puede repetir el recorrido de
  [MANUAL_USO.md](MANUAL_USO.md) y ensayar [GUIA_DEFENSA.md](GUIA_DEFENSA.md).
