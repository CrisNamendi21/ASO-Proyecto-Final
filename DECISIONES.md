# Notas técnicas de implementación

Estas notas explican cómo se concretan aspectos que el diseño deja abiertos.
Complementan la especificación técnica; no añaden requisitos académicos.

## Estados de procesos

El diseño (§§9.3–9.4) define Ejecutando, pero no establece una actividad que lo
active. El uso normal sigue Nuevo → Listo → Finalizado, sin planificador ni
activación automática. `GestorProcesos` conserva todas las transiciones del modelo
y permite como máximo un Ejecutando. Sus cambios internos se comprueban en pruebas.
Listar y consultar nunca modifican estados.

Implementación: `simulador/procesos.py`.

## Nombres de procesos

Para evitar nombres sin texto visible, se rechazan entradas compuestas únicamente
por espacios en blanco con `PROC_001`. Los nombres válidos se conservan sin recortar
y el límite de 50 caracteres se aplica a la entrada original. Esta precisión
complementa la regla de nombre no vacío de §9.1.

Implementación: `simulador/procesos.py`.

## Resultados y finalización

El resultado uniforme de §8.1 se representa con una dataclass `Resultado`:
`estado` (`EXITO` o `ERROR`), `codigo`, `mensaje` y un diccionario `datos`.
Los éxitos usan el ID de la operación; los errores usan su código del catálogo.
El README describe los datos de las once llamadas.

Al finalizar, el resultado incluye `pid`, `estado_anterior` y `estado`. Esto permite
que el kernel registre ambos estados, como exige §8.2, sin consultar directamente
la colección del gestor ni añadir otro canal de comunicación.

Implementación: `simulador/contratos.py`, `simulador/procesos.py` y `simulador/kernel.py`.

## Validación de solicitudes

Los parámetros viajan en un diccionario con exactamente las claves de la firma.
Una clave ausente o adicional produce `SYS_002`, evitando ignorar entradas.
`enviar_solicitud(llamada, parametros)` permite enviar solicitudes generales por el
mismo recorrido y comprobar los errores de sistema; no añade una llamada al registro.

La precedencia es:

1. Llamada no textual o desconocida: `SYS_001`.
2. Parámetros que no son un diccionario, claves ausentes o adicionales, o datos de
   escritura que no son texto: `SYS_002`.
3. Validación del recurso en su gestor, con el código de dominio correspondiente.

En archivos se comprueban nombre y raíz antes de acceder al destino. Abrir valida
existencia, redirección o tipo de archivo, modo y apertura activa, en ese orden.
Leer y escribir validan descriptor, permiso y destino; eliminar comprueba existencia,
redirección o tipo y apertura. El cierre solo necesita una apertura activa.

Implementación: `simulador/dispatcher.py`, `simulador/interfaz_syscalls.py`,
`simulador/aplicacion.py` y `simulador/archivos.py`.

## Fallos físicos del almacenamiento

El catálogo de §13.1 no define un código general para permisos del anfitrión,
falta de espacio o errores de codificación. `FILE_009` cubre esos fallos, sin
reemplazar los errores de dominio `FILE_001`–`FILE_008` ni presentarlos como `SYS_002`.

Devuelve `estado="ERROR"` y un diagnóstico con `operacion`, `tipo` y `codigo_host`
(cuando existe). Si también falla la limpieza de un temporal, añade
`fallo_limpieza_temporal`. Los datos no incluyen el contenido del archivo.
Solo se capturan las excepciones de almacenamiento y codificación previstas.

Implementación: `simulador/errores.py` y `simulador/archivos.py`.

## Escritura protegida

Para evitar que un fallo de escritura deje vacío o incompleto el archivo original,
se escribe primero en un temporal dentro de la raíz controlada y después se reemplaza
el destino. Se conserva así la sustitución completa de contenido definida en §10.9.
Los temporales usan el prefijo reservado `.__simulador_tmp_` y no aparecen en el listado.

Si falla la escritura o el reemplazo, se intenta limpiar el temporal y se devuelve
`FILE_009`. Este mecanismo no garantiza recuperación frente a cortes de energía ni
protección frente a cambios concurrentes de otros programas.

Implementación: `simulador/archivos.py`.

## Confinamiento y nombres físicos

La restricción a `datos/archivos/` de §10.14 se aplica mediante nombres simples y
validación de la raíz y los destinos. Se rechazan rutas, separadores, dispositivos,
flujos alternativos, caracteres reservados de Windows y controles ASCII. También
se rechazan nombres de solo espacios, terminados en punto o espacio, y el prefijo
reservado de temporales. Los nombres válidos no se normalizan silenciosamente.

Se excluyen enlaces simbólicos, junctions, redirecciones y archivos con varios
enlaces físicos. La raíz y el destino se vuelven a comprobar al leer o escribir por
descriptor. El listado omite directorios, redirecciones y temporales internos.
Estas medidas limitan el acceso del simulador, pero no constituyen una sandbox del
sistema operativo.

Implementación: `simulador/archivos.py`.

## Cierre de aperturas obsoletas

Si otro programa elimina un archivo después de abrirlo, su descriptor continúa en
la tabla hasta cerrarlo. `close_file` retira esa apertura y devuelve `FILE-05` aunque
el archivo físico haya desaparecido. Leer o escribir antes del cierre produce
`FILE_009` porque necesita el destino físico. Después del cierre, el descriptor es
inválido y produce `FILE_006`.

Esto permite liberar la apertura sin intentar recuperar archivos externos.
Implementación: `simulador/archivos.py`.

## Bitácora y recorrido

La bitácora permanece en memoria durante la sesión. El kernel registra exactamente
un evento final antes de devolver cada respuesta. Su consulta atraviesa aplicación,
interfaz y kernel, devuelve copias y no genera otra system call ni nuevos eventos.

Cada evento incluye número, fecha y hora con zona local, llamada, parámetros y
resultado. La escritura registra `caracteres_solicitados`; la lectura exitosa guarda
`caracteres_leidos`. Ninguna de las dos copia el contenido completo a la bitácora.

El recorrido se conserva como una tupla de las etapas alcanzadas por la última
solicitud. Permite observar el flujo real sin animaciones ni pausas artificiales.

Implementación: `simulador/bitacora.py`, `simulador/kernel.py`,
`simulador/interfaz_syscalls.py` y `simulador/aplicacion.py`.

## Paquete de entrega

El ZIP se construye con una lista explícita de fuentes, pruebas y documentos.
Incluye `datos/archivos/` vacío y excluye archivos de sesiones anteriores, cachés e
historial de Git. Se genera una suma SHA-256 para comprobar su integridad.
La aplicación necesita Python y Tkinter instalados; el ZIP no contiene un ejecutable
ni un intérprete integrado.

Implementación: `crear_paquete.py` y `verificar_entrega.py`.
