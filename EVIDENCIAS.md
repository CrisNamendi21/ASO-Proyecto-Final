# Registro de evidencias

## Ejecución automatizada

El 29 de septiembre de 2026 se ejecutó:

```powershell
python -m unittest discover -s tests -v
python demo.py
python -m compileall -q main.py demo.py simulador tests
```

Resultado de pruebas: **58 ejecutadas, 56 correctas y 2 omitidas**. Las omisiones
corresponden únicamente a los casos de symlink: Windows devolvió `WinError 1314`
porque el entorno no otorgó privilegio para crearlos. La cobertura de hard links,
traversal, rutas absolutas, separadores, modos, descriptores, fallos físicos,
persistencia y bitácora se ejecutó correctamente.

`demo.py` verificó 16 solicitudes públicas y la existencia de exactamente un evento
de bitácora por solicitud. La demostración usa un directorio temporal, por lo que no
modifica los archivos persistentes de la interfaz.

## Revisión visual manual

La revisión de la ventana “Simulador de System Calls — Incremento 4” se realizó el
29 de septiembre de 2026 con una ventana de 1050×780 píxeles.

| Pantalla | Evidencia observada |
| --- | --- |
| Inicio | Encabezado, navegación, explicación de alcance y paneles inferiores visibles. |
| Procesos | Campos, selector de prioridad, cuatro controles y tabla de cuatro columnas visibles. Se creó y listó `Evidencia` con PID 101 y estado Listo. |
| Resultado y recorrido | La creación mostró `EXITO`, `PROC-01`, PID 101 y las etapas GUI → aplicación → interfaz → kernel → dispatcher → gestor → retorno. |
| Archivos | Campos de nombre, modo y descriptor; controles Crear, Abrir, Leer, Escribir, Cerrar, Eliminar y Listar; área de contenido y tabla visibles sin recortes. |
| Bitácora | Las filas `create_process` y `list_processes` mostraron evento, hora, llamada, estado y código. El panel de detalle permanece de solo lectura. |

La prueba de Tk también comprueba que las vistas solicitadas caben a 850×700. Las
capturas visuales de esta revisión quedaron visibles durante la ejecución de la
verificación; este registro conserva los hechos observados y una ruta reproducible
para repetirlos mediante [MANUAL_USO.md](MANUAL_USO.md).

## Limitación documentada

Los dos casos de symlink deben repetirse en un Windows con privilegio de creación de
enlaces simbólicos. No es un fallo funcional conocido: el código y los casos de
seguridad están implementados, pero esa capacidad del anfitrión no estaba disponible.

## Cierre del incremento 6

`python verificar_entrega.py` comprobó en una sola ejecución los 12 archivos de
entrega requeridos, Tkinter, compilación, 58 pruebas y la demostración de 16
solicitudes. El resultado final fue `ENTREGA VERIFICADA`.
