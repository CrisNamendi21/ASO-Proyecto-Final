# Manual de uso

## Requisitos y arranque

Se necesita Python 3 con Tkinter. Desde PowerShell, dentro de la carpeta del
proyecto:

```powershell
cd "C:\Users\Cristopher\Desktop\ASO"
python main.py
```

Si `python` no está asociado a Python 3, usar `py main.py`.

Para ejecutar la demostración automatizada y las pruebas:

```powershell
python demo.py
python -m unittest discover -s tests -v
```

No hay dependencias externas que instalar.

## Recorrido manual de demostración

1. Abrir **Procesos**.
2. Escribir `Editor`, elegir prioridad 3 y pulsar **Crear proceso**. El resultado
   debe indicar `PROC-01` y el PID 101 durante una sesión nueva.
3. Pulsar **Listar procesos**. La tabla muestra PID, Nombre, Estado y Prioridad.
4. Seleccionar la fila, pulsar **Consultar proceso** y después **Finalizar proceso**.
   El resultado de finalización contiene el estado anterior y `Finalizado`.
5. Pulsar **Listar procesos** otra vez para comprobar que el proceso se conserva.
6. Abrir **Archivos**, escribir `ejemplo.txt`, elegir modo `rw` y pulsar **Crear**.
7. Pulsar **Abrir**; el descriptor aparece en el campo correspondiente.
8. Escribir contenido, pulsar **Escribir** y después **Leer**. La lectura vuelve a
   mostrar el texto en el área de contenido.
9. Pulsar **Cerrar** y **Listar archivos**. El archivo debe figurar como Cerrado.
10. Abrir el archivo e intentar **Eliminar**: el resultado debe ser `FILE_008`.
    Cerrarlo y eliminarlo demuestra la eliminación permitida.
11. Abrir **Bitácora**. Cada solicitud anterior aparece una sola vez. Seleccionar un
    evento muestra sus parámetros, estado, código, mensaje y datos.
12. Pulsar **Salir** al terminar. Los procesos, descriptores, aperturas y bitácora se
    reinician al iniciar otra sesión; los archivos cerrados que no se eliminen se
    conservan bajo `datos/archivos/`.

## Cómo interpretar la pantalla

El panel **Resultado de la última llamada** presenta `estado`, `codigo`, `mensaje` y
`datos`. El panel **Recorrido conceptual** muestra las etapas reales atravesadas por
la solicitud. La GUI no modifica gestores ni archivos directamente.

Los códigos con guion, por ejemplo `PROC-01` o `FILE-04`, representan éxitos de una
llamada. Los códigos con guion bajo, como `PROC_001` o `FILE_006`, representan
errores controlados. `FILE_009` comunica un fallo físico o de codificación del
almacenamiento; no se presenta como éxito.

## Seguridad de archivos

Solo se aceptan nombres simples. Rutas, separadores, unidades de Windows, enlaces,
dispositivos y flujos alternativos se rechazan. Los archivos físicos se administran
exclusivamente bajo `datos/archivos/`; no usar esa carpeta para pruebas destructivas
automatizadas.

## Comprobación antes de entregar

- Ejecutar las pruebas y confirmar que no haya fallos.
- Ejecutar `python demo.py` y comprobar que imprime los 16 eventos esperados.
- Realizar el recorrido manual anterior.
- Consultar [MATRIZ_PRUEBAS.md](MATRIZ_PRUEBAS.md) y [DECISIONES.md](DECISIONES.md)
  antes de la defensa.
