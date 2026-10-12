# Matriz de pruebas y trazabilidad

Esta matriz relaciona los casos de la especificación técnica §13 y las comprobaciones
adicionales de implementación con sus pruebas. Los casos de integración entran por
`AplicacionUsuario` y recorren interfaz, kernel, dispatcher, gestor y bitácora.

## Procesos — CP-01 a CP-04

| ID | Operación comprobada | Resultado esperado | Prueba automatizada |
| --- | --- | --- | --- |
| CP-01 | Crear proceso válido | `PROC-01`, PID 101 y estado Listo | `test_CP_01_creacion_y_transicion_nuevo_listo` |
| CP-02 | Listar procesos, incluida colección vacía | `PROC-02` y lista de copias | `test_CP_02_listado_y_vacio` |
| CP-03 | Consultar proceso existente | `PROC-03` e información completa | `test_CP_03_consulta_individual` |
| CP-04 | Finalizar sin eliminar el registro | `PROC-04`, estado anterior y Finalizado | `test_CP_04_finalizar_conserva_registro_y_no_reutiliza_pid` |

## Archivos — CA-01 a CA-07

| ID | Operación comprobada | Resultado esperado | Prueba automatizada |
| --- | --- | --- | --- |
| CA-01 | Crear archivo vacío y cerrado | `FILE-01` | `test_CA_01_a_CA_07_flujo_documental_completo` |
| CA-02 | Abrir en modo `rw` | `FILE-02` y descriptor 1 | misma secuencia CA completa |
| CA-03 | Escribir reemplazando contenido | `FILE-04` y cantidad de caracteres | misma secuencia CA completa |
| CA-04 | Leer por descriptor | `FILE-03` y contenido | misma secuencia CA completa |
| CA-05 | Cerrar e invalidar descriptor | `FILE-05` | misma secuencia CA completa |
| CA-06 | Listar nombre y estado | `FILE-07` | misma secuencia CA completa |
| CA-07 | Eliminar archivo cerrado | `FILE-06` | misma secuencia CA completa |

## Errores — CE-01 a CE-10

| ID | Condición comprobada | Código esperado | Prueba automatizada |
| --- | --- | --- | --- |
| CE-01 | Datos de proceso inválidos | `PROC_001` | `test_CE_01_datos_invalidos` |
| CE-02 | PID inexistente | `PROC_002` | `test_CE_02_pid_inexistente_en_consulta_y_finalizacion` |
| CE-03 | Doble finalización | `PROC_003` | `test_CE_03_doble_finalizacion` |
| CE-04 | Crear archivo existente sin truncarlo | `FILE_002` | `test_CE_04_existente_no_trunca` |
| CE-05 | Abrir o eliminar archivo inexistente | `FILE_003` | `test_CE_05_inexistente_y_modo_invalido` |
| CE-06 | Apertura duplicada | `FILE_005` | `test_CE_06_apertura_duplicada_en_cualquier_modo` |
| CE-07 | Lectura con descriptor inválido | `FILE_006` | `test_CE_07_CE_08_descriptor_invalido_doble_cierre_y_uso_posterior` |
| CE-08 | Escritura con descriptor inválido | `FILE_006` | misma prueba CE-07/CE-08 |
| CE-09 | Eliminar archivo abierto | `FILE_008` | `test_CE_09_no_elimina_archivo_abierto` |
| CE-10a | Llamada desconocida | `SYS_001` | `test_CE_10_llamada_desconocida` |
| CE-10b | Parámetros incompletos | `SYS_002` | `test_CE_10_parametros_incompletos` |

## Reglas e invariantes adicionales

| Regla | Evidencia automatizada principal |
| --- | --- |
| Exactamente 11 llamadas registradas | `test_dispatcher_registra_exactamente_las_once_system_calls` |
| Tipos, límites, PID secuencial, repetidos y transiciones | `test_integracion.py`, `test_procesos.py` |
| Modos, apertura única y descriptor secuencial | `test_modos_no_truncan_y_aplican_permisos`, prueba de descriptores |
| Reemplazo completo y persistencia | pruebas de reemplazo y `test_persistencia_fisica_y_reinicio_de_aperturas` |
| Doble cierre y uso después de cerrar | prueba CE-07/CE-08 |
| Confinamiento, traversal y archivos externos intactos | pruebas de nombres, symlink, hard link y revalidación por descriptor |
| Fallos físicos `FILE_009` sin falso éxito | pruebas de raíz, lectura, codificación, temporal y reemplazo |
| Contenido ausente de la bitácora | `test_bitacora_registra_cantidades_sin_contenido` |
| Un evento final por solicitud | ayudantes de todas las pruebas de integración |
| GUI de archivos, navegación y dimensiones de vistas | `test_secuencia_visible_de_las_siete_operaciones` |
| Demostración pública completa | `python demo.py`, que valida códigos y cantidad de eventos |

## Trazabilidad por componente

| Fuente del diseño | Implementación | Pruebas |
| --- | --- | --- |
| §§6, 8.4 y 11.1: recorrido y registro antes del retorno | Aplicación, interfaz, kernel y dispatcher | `test_integracion.py`, `test_procesos.py` |
| §8.1: respuesta uniforme | `contratos.py` y gestores | Ayudantes de integración de CP, CA y CE |
| §§8.2 y 9: procesos y transiciones | `procesos.py` | `test_integracion.py`, `test_procesos.py` |
| §§8.3 y 10: operaciones, modos, descriptores y persistencia | `archivos.py` | `test_archivos.py` |
| §10.14: confinamiento | Validación de nombres, raíz y destinos | Casos de rutas, enlaces y revalidación por descriptor |
| §§6.8, 8.3 y 13.4: bitácora | `kernel.py`, `bitacora.py` | Integración y registro de cantidades sin contenido |
| §12: interfaz | `gui/ventana.py` | `test_gui_archivos.py` y recorrido manual del manual de uso |
| §13.1: errores de dominio y solicitud | `errores.py`, dispatcher y gestores | CE-01–CE-10 |
| Detalles de implementación | [Notas técnicas](DECISIONES.md) | Casos de espacios, copias, parámetros extra y `FILE_009` |

## Evidencia de ejecución

El 11 de octubre de 2026 se ejecutaron:

```powershell
python -m unittest discover -s tests -v
python demo.py
python -m compileall -q main.py demo.py verificar_entrega.py crear_paquete.py simulador tests
python verificar_entrega.py
```

Resultado: **58 casos, 56 correctos y 2 omitidos**, sin fallos. Las omisiones
corresponden a los dos casos de symlink: Windows devolvió `WinError 1314` al
intentar crearlos. La prueba de hard link y las demás pruebas de confinamiento
se ejecutaron correctamente. Los archivos de prueba usan directorios temporales.

La demostración comprobó 16 solicitudes y 16 eventos. El verificador terminó con
`ENTREGA VERIFICADA`. Los límites de estas comprobaciones están en
[EVIDENCIAS.md](EVIDENCIAS.md).
