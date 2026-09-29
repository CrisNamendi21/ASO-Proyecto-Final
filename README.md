# Simulador de interfaz de llamadas al sistema

Proyecto universitario de Arquitectura de Sistemas Operativos en Python y
Tkinter/ttk. **Incremento 1: creación de procesos de extremo a extremo.**
El proyecto completo aún no está terminado: solo `create_process` está implementada.

La simulación no cambia privilegios del procesador, no ejecuta código dentro del
kernel anfitrión ni crea o termina procesos reales. Este incremento tampoco opera
sobre archivos de datos. Todos los procesos y eventos existen solo durante la sesión.

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

No se modificaron documentos fuente. `docs/` y `AGENTS.md` ya estaban ignorados en
Git al comenzar este incremento; deben acompañar al proyecto por separado.

Las decisiones que concretan vacíos del diseño y las excepciones autorizadas se
mantienen en [DECISIONES.md](DECISIONES.md), con fuente, motivo, aprobación, estado
y evidencia. Ese registro no sustituye las fuentes ni `AGENTS.md`. Se ubica en la
raíz para que no quede excluido por la regla existente que ignora `docs/`.

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

`demo.py` fuerza UTF-8 en su salida para que las flechas del recorrido funcionen
también en una consola Windows con salida redirigida. No requiere archivos de datos.

## Qué incluye este incremento

- Crear un proceso: nombre no vacío, máximo 50 caracteres; prioridad entera 1–5.
- Rechazar nombres de solo espacios y valores de tipos incorrectos. Los booleanos
  no se aceptan como prioridades aunque Python los considere subclases de `int`.
- Admitir nombres repetidos; PID secuenciales desde 101. Un rechazo no consume PID.
- Registrar internamente `Nuevo` y pasar a `Listo` antes del éxito.
- Devolver un `Resultado` con `estado`, `codigo`, `mensaje`, `datos`.
- Registrar exactamente un evento por llamada, incluyendo rechazos.
- Consultar copias de bitácora y recorrido sin crear nuevos eventos.
- GUI con Inicio, creación de Procesos, Bitácora, Salir y Archivos deshabilitado.
- Catálogo central completo de errores, aunque solo se usan `PROC_001`, `SYS_001`
  y `SYS_002` en esta etapa.

La enum declara los cuatro estados del diseño. Solo se implementa la transición de
creación; las demás transiciones y operaciones corresponden al siguiente incremento.

## Recorrido y responsabilidades

```text
GUI → AplicacionUsuario → InterfazSystemCalls → Kernel → Dispatcher
    → GestorProcesos → Dispatcher → Kernel [registra evento]
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
| `simulador/contratos.py` | Dataclasses `Solicitud` y `Resultado`. |
| `simulador/errores.py` | Catálogo del diseño §13.1. |
| `simulador/bitacora.py` | Eventos en memoria y copias de consulta. |
| `simulador/gui/ventana.py` | Entradas y presentación; no importa gestores ni accede al disco. |
| `demo.py` | Programa de prueba a través de la aplicación en modo usuario. |
| `tests/test_integracion.py` | Pruebas de contratos, efectos, eventos y recorrido real. |

Las pruebas inspeccionan el estado privado del gestor para comprobar los efectos
porque las consultas de procesos todavía no están implementadas. El código de
presentación y la aplicación nunca utilizan esa vía.

## Contrato vigente y validaciones

Firma pública: `create_process(nombre: str, prioridad: int) -> Resultado`.

| Resultado | estado | codigo | datos |
| --- | --- | --- | --- |
| Creación válida | `EXITO` | `PROC-01` | `{"pid": 101}` (PID asignado) |
| Nombre o prioridad inválidos | `ERROR` | `PROC_001` | `{}` |
| Llamada desconocida | `ERROR` | `SYS_001` | `{}` |
| Estructura de parámetros inválida/incompleta | `ERROR` | `SYS_002` | `{}` |

La prioridad es informativa. No hay scheduler ni ejecución real.

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

Identificar antes de procesar corresponde al flujo del diseño §11.5. Esto no está
especificado en el documento; lo propongo como decisión de implementación: exigir
exactamente las claves de la firma impide aceptar parámetros adicionales ignorados.
Nombre y prioridad comparten código, por lo que su orden no cambia el resultado.

La bitácora incluye número, fecha/hora con zona local, llamada, parámetros y
`Resultado` completo (estado, código, mensaje y datos). Los parámetros de esta
etapa contienen solo los datos de creación o solicitudes de prueba.

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
7. Cambiar de pantalla y regresar: consultar no debe añadir eventos.
8. Pulsar Salir. Al abrir otra sesión la bitácora está vacía y el primer PID será 101.

El listado `Treeview` de procesos y sus consultas todavía no existen; se añadirán
junto a las otras tres llamadas. La GUI no fabrica una lista a partir de las entradas.

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

Las pruebas sin GUI no sustituyen la comprobación visual. Este incremento no prueba
confinamiento, archivos ni operaciones de procesos todavía no implementadas.

## Pendiente

- Incremento 2: `list_processes`, `get_process`, `terminate_process`, transiciones,
  Treeview de procesos, CP-02–CP-04 y CE-02–CE-03.
- Implementar las transiciones internas de `Ejecutando` sin activación automática,
  según la decisión aprobada [DEC-001](DECISIONES.md#dec-001--ejecutando-sin-activación-automática).
  No se añade botón, scheduler ni llamada pública para ejecutarlo.
- Incremento de archivos: siete llamadas, confinamiento, aperturas, persistencia,
  CA-01–CA-07, CE-04–CE-09 y pruebas adicionales de seguridad.
- Incorporar `FILE_009` para fallos técnicos de almacenamiento y escritura mediante
  temporal controlado y reemplazo posterior, según DEC-002 y DEC-003 de
  [DECISIONES.md](DECISIONES.md). Ambas decisiones están aprobadas, pero todavía
  no implementadas. No forman parte del catálogo ni del mecanismo originales.
- Completar GUI, demostración general, evidencias, manual y defensa.

Las otras diez llamadas no están registradas en este incremento; no son éxitos
simulados ni funcionalidades terminadas. La meta final sigue siendo las once llamadas
del diseño, sin renombrarlas o reemplazarlas.
