# Evidencias de funcionamiento

## Entorno y resultados

Verificación del 11 de octubre de 2026 en Windows, con Python 3.13.15 y Tk 8.6.

| Comprobación | Resultado |
| --- | --- |
| Compilación de fuentes y pruebas | Sin errores. |
| Suite de unittest | 58 casos: 56 correctos, 2 omitidos, ningún fallo. |
| Demostración | 16 solicitudes, códigos esperados y exactamente 16 eventos. |
| Verificación de entrega | Código de salida 0 y `ENTREGA VERIFICADA`. |

Comandos utilizados desde la raíz:

```powershell
python -m compileall -q main.py demo.py verificar_entrega.py crear_paquete.py simulador tests
python -m unittest discover -s tests -v
python demo.py
python verificar_entrega.py
```

La matriz CP, CA y CE se relaciona con las pruebas en
[MATRIZ_PRUEBAS.md](MATRIZ_PRUEBAS.md). Las pruebas de archivos y la demostración
usan directorios temporales; no modifican los archivos persistentes de la aplicación.

## Casos comprobados

Se verificaron creación, listado, consulta y finalización de procesos; límites de
nombre y prioridad; PID secuenciales; transiciones internas y estado terminal.

Para archivos se comprobaron las siete operaciones, modos de acceso, apertura
única, descriptores secuenciales, reemplazo completo, persistencia, nombres inválidos,
rutas externas, hard links y revalidación del destino por descriptor. Las pruebas
de fallos físicos comprueban errores controlados y conservación del original ante
fallos de escritura o reemplazo.

Las pruebas de integración comprueban el resultado y su evento. También verifican
el recorrido por capas, el registro anterior al retorno, las copias de consulta y
que la bitácora guarde cantidades sin copiar el contenido leído o escrito.

## Comprobación de la interfaz

La prueba `test_secuencia_visible_de_las_siete_operaciones` abrió una ventana Tk real,
recorrió las cuatro vistas y comprobó sus dimensiones solicitadas. Ejecutó las siete
operaciones de archivos desde los controladores de la GUI, verificó resultados,
contenido y tabla, provocó `FILE_008` y comprobó nueve eventos en Bitácora. La ventana
se cerró al terminar la prueba.

Esta comprobación es automatizada y no sustituye una revisión visual manual de
legibilidad, distribución o recortes. Para comprobar esos aspectos, ejecutar
`python main.py` y seguir el [manual de uso](MANUAL_USO.md). No se atribuye una nueva
inspección visual manual a la ejecución de pruebas de esta fecha.

## Limitación de enlaces simbólicos

Se omitieron estos dos casos porque Windows devolvió `WinError 1314` al intentar
crear enlaces simbólicos:

- `test_enlaces_no_se_listan_abren_eliminan_ni_modifican_destino`.
- `test_raiz_no_puede_ser_enlace_o_redireccion`.

Deben repetirse en un entorno con ese privilegio. Las omisiones no prueban el
resultado de esos casos. Las pruebas de hard links sí se ejecutaron correctamente.

## Reproducción desde el paquete

Generar el ZIP con `python crear_paquete.py`, extraerlo en una carpeta vacía y
ejecutar allí `python verificar_entrega.py`. El contenido previsto y la comprobación
de integridad se describen en [MANIFIESTO_ENTREGA.md](MANIFIESTO_ENTREGA.md).
