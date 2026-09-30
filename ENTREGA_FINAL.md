# Informe de cierre — incremento 7

Fecha de verificación: 29 de septiembre de 2026.

Este informe contrasta el estado final con los criterios de aceptación de
`AGENTS.md`. No sustituye la especificación técnica ni la propuesta académica.

| Criterio de aceptación | Estado | Evidencia principal |
| --- | --- | --- |
| Python y Tkinter/ttk ejecutables | Cumple | `main.py`, prueba Tk real y `verificar_entrega.py` |
| Exactamente 11 llamadas con firmas definidas | Cumple | registro explícito del dispatcher y prueba correspondiente |
| Recorrido completo por todas las capas | Cumple | pruebas de integración, recorrido visible y demostración |
| Reglas de procesos, PID y transiciones | Cumple | CP-01–CP-04 y pruebas de invariantes |
| Reglas de archivos, modos y descriptores | Cumple | CA-01–CA-07 y pruebas adicionales |
| Confinamiento y persistencia física | Cumple | traversal, rutas, hard links, temporales y reinicio de aperturas |
| Errores exactos y ausencia de falsos éxitos | Cumple | CE-01–CE-10 y `FILE_009` aprobado |
| Un evento final por cada solicitud | Cumple | ayudantes de integración y demostración de 16 eventos |
| Matriz documental completa | Cumple | `MATRIZ_PRUEBAS.md` |
| GUI, navegación, resultados y recorrido | Cumple | prueba Tk y revisión visual del incremento 5 |
| Demostración académica reproducible | Cumple | `demo.py` y `MANUAL_USO.md` |
| Manual, evidencias y defensa | Cumple | documentos finales del incremento 5 |
| Sin fallos críticos conocidos | Cumple | 58 pruebas ejecutadas y demostración correcta |

## Resultado verificable

Ejecutar desde la raíz:

```powershell
python verificar_entrega.py
```

El comando comprueba los archivos requeridos, la disponibilidad de Tkinter, la
compilación, la suite completa y la demostración. Devuelve código distinto de cero
si alguna fase falla.

La entrega portable se construye con `python crear_paquete.py`. Su lista cerrada de
archivos y exclusiones está documentada en `MANIFIESTO_ENTREGA.md`; el ZIP se entrega
con una suma SHA-256 para verificar que no cambió después de generarlo.

## Limitación del entorno

Dos pruebas de symlink se omiten porque Windows devuelve `WinError 1314` al intentar
crear esos enlaces sin privilegio. La implementación rechaza symlinks y junctions;
las pruebas deben repetirse en un entorno con ese permiso para obtener evidencia
ejecutada de esos dos casos. La prueba de hard links sí se ejecuta correctamente.

## Fuera de alcance, conforme al diseño

No se implementan procesos reales, scheduler, persistencia de procesos, base de
datos, sandbox del anfitrión ni protección avanzada frente a modificaciones externas
concurrentes. Estas exclusiones no son defectos pendientes.
