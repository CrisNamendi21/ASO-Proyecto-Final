# Estado de la entrega

Verificación automatizada: 11 de octubre de 2026.

El simulador implementa las once llamadas de la especificación técnica. La
compilación, las pruebas disponibles y la demostración terminan correctamente.
Los detalles reproducibles se encuentran en [EVIDENCIAS.md](EVIDENCIAS.md).

| Aspecto | Comprobación |
| --- | --- |
| Python y Tkinter | Python 3.13.15, Tk 8.6 y apertura de ventana durante la prueba de GUI. |
| Once llamadas y arquitectura por capas | Registro del dispatcher y pruebas de integración del recorrido. |
| Procesos, PID y transiciones | CP-01–CP-04, errores de procesos y pruebas de invariantes. |
| Archivos, modos y descriptores | CA-01–CA-07 y pruebas de permisos, cierre y secuencias. |
| Confinamiento y persistencia | Pruebas de rutas, nombres, hard links, destinos y reinicio de aperturas. |
| Manejo de errores | CE-01–CE-10 y fallos de almacenamiento con `FILE_009`. |
| Bitácora | Un evento por solicitud, copias de consulta y cantidades sin contenido de archivos. |
| Interfaz | Prueba funcional con Tk real, navegación y operaciones de archivos. |
| Programa de demostración | 16 solicitudes y 16 eventos con resultados comprobados. |
| Documentación | README, manual, notas técnicas, matriz, evidencias y guía de defensa. |

## Verificación y paquete

```powershell
python verificar_entrega.py
python crear_paquete.py
```

El verificador terminó con código 0 y `ENTREGA VERIFICADA`: 58 casos de prueba,
56 correctos y 2 omitidos. El generador produce `dist/ASO_Proyecto_Final.zip` y
su suma SHA-256. El [manifiesto](MANIFIESTO_ENTREGA.md) describe su contenido y uso.

## Límites de la verificación

Dos pruebas de enlaces simbólicos no pudieron ejecutarse por `WinError 1314`.
Se requiere un entorno con permiso para crearlos antes de afirmar que esos dos
casos están comprobados. Las pruebas de hard links sí finalizaron correctamente.

La prueba automatizada de la GUI no certifica una revisión visual manual. El
[manual](MANUAL_USO.md) permite repetir la navegación, resultados, errores y cierre
antes de la exposición.

## Alcance del simulador

Los procesos, descriptores, aperturas y eventos duran una sesión. Los archivos físicos
persisten dentro de `datos/archivos/`. No se implementan procesos reales, planificación
del procesador, base de datos ni protección frente a modificaciones concurrentes de
otros programas. La separación usuario/kernel representa el flujo de una solicitud,
sin cambiar privilegios del procesador.
