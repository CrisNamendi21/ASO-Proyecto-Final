# Registro de decisiones de implementación

Este archivo conserva las decisiones necesarias para concretar aspectos no definidos
en las fuentes y las excepciones aprobadas expresamente por el usuario. Explica qué
se decidió, por qué y qué falta implementar o comprobar. No es una nueva
especificación académica ni sustituye los documentos originales o `AGENTS.md`.

## Referencias y reglas de uso

- Especificación técnica principal: `docs/Proyecto Arquitectura de sistemas operativos.docx`.
- Requisitos académicos, entregables y rúbrica: `docs/Propuesta #7.pdf`.
- Instrucciones de trabajo y restricciones: `AGENTS.md` y decisiones explícitas del usuario.
- Antes de cada incremento, contrastar el cambio con esas fuentes y consultar este
  registro. Una decisión local no autoriza a cambiar otras reglas del proyecto.
- Distinguir siempre requisito documental, instrucción del usuario y decisión de
  implementación. No atribuir estas decisiones al profesor.
- Resolver detalles internos sencillos de forma compatible y documentarlos. Si una
  ambigüedad cambia una firma, código, seguridad, comportamiento observable o alcance,
  consultar al usuario antes de implementar esa parte, como establece `AGENTS.md`.
- Aprobado no significa implementado ni probado. Actualizar los estados y enlazar
  código y evidencias cuando existan; conservar el motivo y la aprobación original.
- Si una decisión cambia, añadir una entrada que sustituya explícitamente a la
  anterior; no borrar el historial ni modificar las fuentes para justificar el código.

## Resumen

| ID | Decisión | Origen de autorización | Estado |
| --- | --- | --- | --- |
| DEC-001 | Ejecutando sin activación automática | Aprobación explícita de las tres recomendaciones | Implementada y probada |
| DEC-002 | FILE_009 para fallos técnicos de almacenamiento | Aprobación explícita de las tres recomendaciones | Implementada y probada |
| DEC-003 | Escritura mediante temporal y reemplazo posterior | Aprobación explícita de las tres recomendaciones | Implementada y probada |
| DEC-004 | Rechazar nombres de proceso de solo espacios | Respuesta explícita durante el incremento 1 | Implementada y probada |
| DEC-005 | Representación concreta del resultado | Análisis aprobado antes del incremento 1 | Implementada para las 11 llamadas |
| DEC-006 | Consulta de bitácora y recorrido sin nuevas system calls | AGENTS.md y análisis aprobado | Implementada y probada en el incremento 1 |
| DEC-007 | Estructura exacta de parámetros y transporte de solicitudes | Concreción de implementación documentada en el incremento 1 | Implementada y probada; sin aprobación individual registrada |
| DEC-008 | Incluir estado anterior en la finalización | Aprobación explícita durante el incremento 2 | Implementada y probada |
| DEC-009 | Reglas concretas para nombres físicos y temporales internos | Decisión rutinaria compatible con el confinamiento | Implementada y probada |
| DEC-010 | Cerrar un descriptor aunque el archivo físico haya desaparecido | Decisión rutinaria compatible con FILE-05 | Implementada y probada |

## DEC-001 — Ejecutando sin activación automática

**Fuente:** diseño §§9.3–9.4 y reglas de procesos de `AGENTS.md`.

**Lo documentado:** existen Nuevo, Listo, Ejecutando y Finalizado; el gestor controla
Ejecutando; como máximo un proceso puede estar en ese estado. No se permite añadir
una llamada pública o un botón de ejecución. Las transiciones admitidas son
Nuevo → Listo, Listo → Ejecutando, Ejecutando → Listo, Listo → Finalizado y
Ejecutando → Finalizado; Finalizado es terminal.

**Vacío:** no se define una actividad concreta que active o termine Ejecutando.

Esto no está especificado en el documento; lo propongo como decisión de implementación:
el funcionamiento normal utilizará Nuevo → Listo → Finalizado, sin activación
automática de Ejecutando. El modelo conservará ese estado y el gestor validará sus
transiciones mediante un mecanismo interno, comprobado con pruebas internas.

**Motivo:** evita inventar un scheduler o vincular arbitrariamente una consulta u
operación de archivo con la ejecución de un proceso. Listar y consultar no deben
cambiar estados. Finalizar podrá aplicarse a Listo o Ejecutando.

**Aprobación:** el usuario aprobó expresamente las tres recomendaciones y pidió dejar
constancia de los aspectos no previstos en el documento (conversación del 29/09/2026).

**Estado real:** implementada. No hay ejecución automática; el gestor conserva y
valida toda la matriz de transiciones mediante su mecanismo interno.

**Código relacionado:** [procesos.py](simulador/procesos.py).

**Verificación:** [test_procesos.py](tests/test_procesos.py) comprueba transiciones
permitidas y rechazadas, estado terminal, máximo un Ejecutando, consultas sin cambios
y finalización desde Listo y Ejecutando. La GUI y la demostración no modifican ese
estado directamente.

## DEC-002 — Código FILE_009 para fallos técnicos de almacenamiento

**Fuente:** diseño §§8.1, 10 y 13.1; apartado de errores de `AGENTS.md`.

**Lo documentado:** las respuestas son uniformes y existe un catálogo de errores de
dominio y solicitud. No hay un código general para fallos físicos del anfitrión;
`AGENTS.md` exige acordar su representación y prohíbe simular éxito o atribuir esos
fallos a parámetros incorrectos.

Esto no está especificado en el documento; lo propongo como decisión de implementación:
añadir `FILE_009`, con significado **Fallo técnico al acceder al almacenamiento del
simulador**, para comunicar problemas como permisos del anfitrión, falta de espacio
u otros fallos de almacenamiento que no correspondan a un código de dominio existente.

**Motivo:** mantiene el resultado estructurado, distingue errores de uso de problemas
externos y evita que una excepción física se presente como éxito o como `SYS_002`.

**Contrato aprobado:** `estado="ERROR"`, `codigo="FILE_009"`, mensaje comprensible
y datos diagnósticos de la operación, tipo de excepción y código del anfitrión cuando
esté disponible. La bitácora registrará el fallo sin copiar el contenido del archivo.
La forma concreta de esos datos se documentará al implementar el contrato de archivos.

**Límites:** no sustituye FILE_001–FILE_008 ni agrega una system call. Un archivo
inexistente sigue correspondiendo a FILE_003; descriptor inválido a FILE_006; modo
sin permiso a FILE_007. No es una captura indiscriminada de cualquier error del código.

**Aprobación:** explícita, dentro de las tres recomendaciones aceptadas por el usuario
el 29/09/2026. Es una ampliación autorizada del catálogo, no un código del documento
original ni una autorización del profesor.

**Estado real:** implementada en [errores.py](simulador/errores.py) y
[archivos.py](simulador/archivos.py). Los datos diagnósticos son `operacion`, `tipo`
y `codigo_host`; si falla la limpieza protegida se añade
`fallo_limpieza_temporal`.

**Verificación:** [test_archivos.py](tests/test_archivos.py) simula permisos denegados
y falta de espacio dentro de directorios temporales; comprueba `FILE_009`, evento
final, ausencia de falso éxito y conservación del archivo original. El incremento 4
añade raíz eliminada y errores de codificación de lectura/escritura, que tampoco
escapan como excepciones sin manejar.

## DEC-003 — Proteger la escritura con un temporal controlado

**Fuente:** diseño §§10.9, 10.14 y 13.5; confinamiento y validación de `AGENTS.md`.

**Lo documentado:** write_file reemplaza todo el contenido, utiliza un descriptor con
permiso, devuelve caracteres escritos y opera exclusivamente en el directorio
controlado. Las solicitudes rechazadas no deben producir cambios inconsistentes.

**Vacío:** no se define cómo evitar que un fallo durante la escritura deje el archivo
original vacío o parcialmente escrito.

Esto no está especificado en el documento; lo propongo como decisión de implementación:
escribir primero en un temporal dentro de la carpeta controlada y reemplazar el
destino únicamente después de completar correctamente esa escritura. El gestor
administrará el temporal y no lo mostrará como archivo del usuario.

**Motivo:** reduce el riesgo de perder el contenido previo ante un fallo durante la
escritura, sin cambiar la firma ni la semántica de reemplazo completo de write_file.

**Límites:** solo GestorArchivos realizará esas operaciones físicas. El temporal y
el destino quedan sujetos al confinamiento. No se promete recuperación frente a
cortes de energía, transacciones generales ni protección frente a modificaciones
concurrentes de otros programas. Los fallos se comunicarán mediante DEC-002 y se
conservará información diagnóstica, también si la limpieza del temporal falla.

**Aprobación:** explícita, dentro de las tres recomendaciones aceptadas por el usuario
el 29/09/2026.

**Estado real:** implementada en [archivos.py](simulador/archivos.py). El prefijo
interno del temporal es `.__simulador_tmp_` y no se expone mediante `list_files`.

**Verificación:** [test_archivos.py](tests/test_archivos.py) comprueba reemplazo
completo, cantidad de caracteres, fallo antes y durante el reemplazo, conservación
del original, limpieza del temporal y un evento sin copiar contenidos. Todas esas
pruebas utilizan directorios temporales aislados.

## DEC-004 — Nombres de proceso compuestos solo por espacios

**Fuente:** diseño §§9.1 y 9.9: nombre no vacío y máximo 50 caracteres.

Esto no está especificado en el documento; lo propongo como decisión de implementación:
rechazar nombres compuestos únicamente por espacios en blanco con PROC_001, conservar
sin recortar los nombres válidos y medir la longitud original.

**Motivo:** evita procesos sin nombre visible y evita cambiar silenciosamente la
entrada del usuario. **Aprobación:** respuesta explícita del usuario durante el
incremento 1: «Sí, rechazar nombres de solo espacios».

**Estado:** implementada en [procesos.py](simulador/procesos.py); comprobada por
`test_espacios_y_nombre_conservado` y pruebas de límites de
[test_integracion.py](tests/test_integracion.py).

## DEC-005 — Representación concreta del resultado

**Fuente:** diseño §8.1 y ejemplo de §12.7; contrato uniforme de `AGENTS.md`.

Esto no está especificado en el documento; lo propongo como decisión de implementación:
usar una dataclass Resultado con los cuatro campos documentados, estados EXITO/ERROR,
ID de operación en éxitos, código de error en rechazos y un diccionario en datos.
create_process devuelve `{"pid": identificador}` y los rechazos actuales devuelven `{}`.

**Motivo:** respuesta única y fácil de presentar y probar. **Aprobación:** incluida
en el análisis aprobado por el usuario antes del incremento 1.

**Estado:** [contratos.py](simulador/contratos.py) y las once llamadas implementadas
y probadas. DEC-002 concreta la excepción al diccionario vacío para diagnósticos de
fallos técnicos.

## DEC-006 — Bitácora en memoria y consultas de solo lectura

**Fuente:** diseño §§6.8, 12.8 y 13.4; `AGENTS.md` ya exige consulta mediante la
aplicación, sin una duodécima system call y sin exponer estado modificable.

Esto no está especificado en el documento; lo propongo como decisión de implementación:
conservar la bitácora solo durante la sesión, devolver copias por la cadena
aplicación → interfaz → kernel y conservar una tupla con el recorrido de la última
solicitud. Consultar esos datos no genera eventos.

**Motivo:** permite la observación educativa sin ciclos de registro, modificaciones
externas o persistencia adicional. **Autorización:** vía de consulta establecida en
`AGENTS.md`; memoria y representación incluidas en el análisis aprobado.

**Estado:** implementado; pruebas de copias, consultas sin eventos y recorrido real
en [test_integracion.py](tests/test_integracion.py). La evidencia del incremento 1
figura en [README.md](README.md#trazabilidad-y-evidencia).

## DEC-007 — Estructura de parámetros y transporte general

**Fuente:** diseño §§6.3, 8, 11.5 y 13.1; separación de validación estructural y de
dominio de `AGENTS.md`.

Esto no está especificado en el documento; lo propongo como decisión de implementación:
representar los parámetros en un diccionario con exactamente las claves de la firma,
rechazar ausencias o extras con SYS_002 y ofrecer enviar_solicitud como transporte
general para ejercitar solicitudes inválidas. No es una nueva system call.

**Motivo:** evita parámetros ignorados y permite demostrar CE-10 sin que una llamada
Python con argumentos omitidos falle antes de llegar al kernel y su bitácora.

**Precedencia registrada:** identificar la llamada (SYS_001), validar estructura
(SYS_002), validar dominio en el gestor (PROC_001 para creación).

**Estado y autorización:** concreción implementada y documentada en el incremento 1;
no se registra una aprobación individual del usuario para estas reglas. Esta entrada
conserva su origen real y no convierte retroactivamente la implementación en requisito
académico ni en aprobación explícita.

**Evidencia:** pruebas CE-10, parámetros extra y precedencia en
[test_integracion.py](tests/test_integracion.py).

## DEC-008 — Estado anterior en el resultado de finalización

**Fuente:** diseño §8.2, que exige registrar en bitácora el PID, estado anterior,
estado final y resultado de `terminate_process`; contrato uniforme del diseño §8.1.

**Vacío:** el diseño no establece cómo transportar el estado anterior desde el
gestor hasta el único punto de registro final del kernel.

Esto no está especificado en el documento; lo propongo como decisión de implementación:
el campo `datos` del resultado exitoso de `terminate_process` contiene `pid`,
`estado_anterior` y `estado`. Como el kernel registra el resultado completo antes de
devolverlo, la bitácora conserva ambos estados sin introducir un canal adicional.

**Motivo:** mantiene un solo resultado y un solo evento por solicitud, respeta las
capas y evita que el kernel consulte directamente el estado interno del gestor.

**Aprobación:** respuesta explícita del usuario durante el incremento 2:
«Sí, incluir estado_anterior en el resultado y la bitácora».

**Estado:** implementada en [procesos.py](simulador/procesos.py) y comprobada desde
Listo y Ejecutando por [test_procesos.py](tests/test_procesos.py). La doble
finalización devuelve `PROC_003` sin modificar el proceso.

## DEC-009 — Reglas concretas para nombres físicos y temporales internos

**Fuente:** diseño §10 y reglas de confinamiento de `AGENTS.md`, que exigen nombres
simples, rechazar rutas, dispositivos y flujos especiales, y validar antes de cambiar
el almacenamiento.

**Vacío:** las fuentes no enumeran todas las variantes de nombre que Windows ajusta
o interpreta especialmente ni reservan un nombre para los temporales de escritura.

Esto no está especificado en el documento; lo propongo como decisión de implementación:
además de las prohibiciones expresas, se rechazan nombres de solo espacios, nombres
terminados en punto o espacio y el prefijo interno `.__simulador_tmp_`. No se recortan,
normalizan ni convierten nombres válidos. El gestor también rechaza `:` para impedir
flujos alternativos, caracteres reservados de Windows, controles ASCII y nombres de
dispositivo de Windows, incluso con extensión.
Las entradas detectadas como enlaces físicos con más de un nombre también se tratan
como redirecciones para no exponer un archivo externo mediante un hard link.

**Motivo y límites:** evita que un nombre aceptado cambie de identidad al llegar al
sistema de archivos y evita colisiones con temporales internos. No añade carpetas,
rutas ni una regla de extensión obligatoria.

**Autorización:** decisión rutinaria compatible con las reglas de seguridad de
`AGENTS.md`; no existe una aprobación individual del usuario ni se presenta como
requisito académico adicional.

**Estado y evidencia:** implementada en [archivos.py](simulador/archivos.py) y
comprobada por `test_nombres_no_son_rutas_y_no_afectan_archivos_externos` en
[test_archivos.py](tests/test_archivos.py).

## DEC-010 — Cerrar un descriptor aunque el archivo físico haya desaparecido

**Fuente:** diseño §§10.10 y 10.13: `close_file` retira la apertura e invalida el
descriptor. `AGENTS.md` no exige protección frente a cambios concurrentes de otros
programas.

**Vacío:** no se define qué ocurre si otro programa elimina el archivo después de
abrirlo en el simulador y antes de solicitar el cierre.

Esto no está especificado en el documento; lo propongo como decisión de implementación:
si el descriptor sigue activo, `close_file` lo retira y devuelve `FILE-05` aunque el
archivo físico ya no exista. Leer o escribir antes del cierre sí devuelve `FILE_009`
porque esas operaciones necesitan el destino físico.

**Motivo y límites:** cerrar es una operación sobre la tabla temporal y debe permitir
liberar una apertura obsoleta. No se intenta recuperar el archivo ni protegerlo de
cambios externos concurrentes.

**Autorización:** decisión rutinaria compatible con el contrato de cierre; no existe
una aprobación individual del usuario ni se presenta como requisito académico nuevo.

**Estado y evidencia:** implementada en [archivos.py](simulador/archivos.py) y
comprobada por `test_cierre_libera_descriptor_si_archivo_desaparece_externamente`.

## Plantilla para decisiones futuras

### DEC-NNN — Título concreto

- **Fuente y sección:** documento e instrucciones aplicables.
- **Requisito existente:** qué está definido y debe conservarse.
- **Vacío o discrepancia:** qué falta concretar.
- **Propuesta:** «Esto no está especificado en el documento; lo propongo como decisión de implementación», seguida de la elección.
- **Motivo y límites:** por qué es necesaria y cómo mantiene el alcance.
- **Autorización:** decisión rutinaria compatible o aprobación explícita, indicando
  mensaje/fecha; si falta una aprobación necesaria, marcar Pendiente.
- **Estado de implementación:** pendiente, parcial, implementada o sustituida.
- **Código y evidencia:** archivos, pruebas realizadas y resultados auténticos;
  distinguir pruebas planeadas de ejecutadas.
- **Sustituye a:** identificador anterior, si corresponde.
