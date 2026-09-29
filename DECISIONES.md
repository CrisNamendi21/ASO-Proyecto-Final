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
| DEC-001 | Ejecutando sin activación automática | Aprobación explícita de las tres recomendaciones | Aprobada; transiciones completas y pruebas pendientes del incremento 2 |
| DEC-002 | FILE_009 para fallos técnicos de almacenamiento | Aprobación explícita de las tres recomendaciones | Aprobada; implementación pendiente del incremento de archivos |
| DEC-003 | Escritura mediante temporal y reemplazo posterior | Aprobación explícita de las tres recomendaciones | Aprobada; implementación pendiente del incremento de archivos |
| DEC-004 | Rechazar nombres de proceso de solo espacios | Respuesta explícita durante el incremento 1 | Implementada y probada |
| DEC-005 | Representación concreta del resultado | Análisis aprobado antes del incremento 1 | Implementada para create_process; otras llamadas pendientes |
| DEC-006 | Consulta de bitácora y recorrido sin nuevas system calls | AGENTS.md y análisis aprobado | Implementada y probada en el incremento 1 |
| DEC-007 | Estructura exacta de parámetros y transporte de solicitudes | Concreción de implementación documentada en el incremento 1 | Implementada y probada; sin aprobación individual registrada |

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

**Estado real:** el incremento 1 declara los cuatro estados y solo implementa
Nuevo → Listo. No hay ejecución automática. Falta implementar y comprobar el
resto de las transiciones en el incremento 2.

**Código relacionado:** [procesos.py](simulador/procesos.py).

**Verificación pendiente:** transiciones permitidas y rechazadas, estado terminal,
máximo un Ejecutando, consultas sin cambios de estado y finalización desde ambos
estados admitidos. Las pruebas internas podrán preparar Ejecutando; la GUI y el
programa de demostración no accederán directamente al gestor para hacerlo.

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

**Estado real:** pendiente del incremento de archivos. El catálogo actual en
[errores.py](simulador/errores.py) todavía contiene solo los códigos originales.

**Verificación pendiente:** simular fallos de E/S de manera controlada en pruebas
aisladas, comprobar respuesta y un evento final, ausencia de falso éxito y coherencia
del estado de aperturas. No utilizar archivos personales ni alterar permisos globales.

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

**Estado real:** pendiente del incremento de archivos; no existe todavía un
GestorArchivos ni operaciones físicas de archivos de datos.

**Verificación pendiente:** reemplazo completo y cantidad de caracteres; fallo antes
del reemplazo que conserve el contenido original; error al reemplazar; administración
del temporal sin exposición en list_files; bitácora única y ningún falso éxito.
Las pruebas usarán directorios temporales aislados.

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

**Estado:** [contratos.py](simulador/contratos.py) y creación implementados y probados.
Las formas propuestas para las otras diez llamadas siguen pendientes de implementación.
DEC-002 concreta una excepción al diccionario vacío para diagnósticos de fallos técnicos.

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
