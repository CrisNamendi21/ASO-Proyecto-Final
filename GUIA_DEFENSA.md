# Guía breve para la defensa

## Idea central

El programa es una simulación educativa de llamadas al sistema. No crea procesos de
Windows ni modifica privilegios del procesador. Simula procesos en memoria y maneja
archivos físicos confinados bajo la carpeta controlada del proyecto.

## Explicación de la arquitectura

Para explicar una operación, usar este recorrido:

```text
GUI → Aplicación en modo usuario → System Call Interface → Kernel simulado
→ Dispatcher → GestorProcesos o GestorArchivos → Resultado/error
→ Kernel registra bitácora → retorno hasta la GUI
```

La GUI recoge entradas y presenta resultados. La aplicación en modo usuario solicita
servicios. La interfaz estructura la solicitud. El kernel coordina y registra el
evento final. El dispatcher solo enruta llamadas conocidas mediante un registro
explícito. Los gestores son los únicos dueños del estado de procesos y archivos.

## Demostración sugerida

1. Crear y listar un proceso; señalar PID, estado Listo y prioridad.
2. Consultarlo, finalizarlo y volver a consultarlo para comprobar Finalizado.
3. Crear, abrir, escribir, leer, cerrar y listar un archivo.
4. Intentar eliminar el archivo abierto para provocar `FILE_008`.
5. Cerrar y eliminar el archivo.
6. Abrir Bitácora y mostrar que los éxitos y errores tienen un único evento.
7. Señalar el recorrido conceptual de una llamada exitosa y uno rechazado.

## Preguntas probables

**¿Por qué no hay scheduler?** La prioridad es informativa. El diseño no exige un
scheduler. El estado Ejecutando se controla internamente
y no existe un botón ni una llamada pública que lo active.

**¿Por qué los archivos sí son reales?** La especificación lo exige, pero están
confinados a `datos/archivos/`. El gestor rechaza rutas, enlaces y otros nombres que
podrían salir de esa raíz.

**¿Qué es un descriptor?** Es un entero simulado, secuencial desde 1; no es un
manejador de Windows. Solo es válido mientras el archivo permanece abierto.

**¿Qué ocurre al escribir?** Se reemplaza el contenido completo. Primero se escribe
un temporal dentro de la raíz y luego se reemplaza el destino, para no dejar el
archivo original parcialmente escrito ante un fallo.

**¿Qué es FILE_009?** Es el código que informa errores físicos o de
codificación del almacenamiento que el catálogo original no definía. Conserva datos
diagnósticos y no simula éxito.

**¿Cómo se comprueba la calidad?** La matriz CP, CA y CE está en
[MATRIZ_PRUEBAS.md](MATRIZ_PRUEBAS.md). La ejecución consolidada tiene 58 pruebas,
con dos omisiones documentadas por falta de privilegio del anfitrión para symlinks.

## Límites que conviene declarar

No hay persistencia de procesos, descriptores, aperturas ni bitácora entre sesiones.
No se intenta proteger frente a modificaciones concurrentes de otros programas. La
simulación no es una sandbox del sistema operativo anfitrión.
