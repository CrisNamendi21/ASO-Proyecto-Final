# Manifiesto del paquete de entrega — incremento 7

El paquete portable se genera desde la raíz del proyecto con:

```powershell
python crear_paquete.py
```

El resultado se guarda en `dist/ASO_Incremento_7.zip`, acompañado por
`dist/ASO_Incremento_7.sha256` para comprobar su integridad. El generador utiliza
una lista cerrada de contenidos: si falta un archivo requerido, termina con error
en lugar de producir una entrega incompleta.

## Contenido incluido

- Código de arranque, demostración y verificación.
- Paquete `simulador/` y pruebas de `tests/`, únicamente como fuentes `.py`.
- README, manual, matriz, decisiones, evidencias, guía de defensa e informe final.
- `AGENTS.md` y los dos documentos fuente bajo `docs/`, sin modificarlos.
- Una carpeta vacía `datos/archivos/`, preparada para los archivos que el usuario
  cree al ejecutar la aplicación.

## Exclusiones deliberadas

- Historial y configuración interna de Git.
- `__pycache__`, bytecode `.pyc` y otros archivos generados.
- El propio directorio `dist/`.
- Archivos existentes en `datos/archivos/`, porque pueden pertenecer a una sesión
  personal o a una demostración anterior.

Estas exclusiones no cambian el funcionamiento: los archivos físicos que se creen
después de extraer el ZIP persistirán dentro de la nueva `datos/archivos/`.

## Comprobación después de extraer

Desde la raíz extraída:

```powershell
python verificar_entrega.py
python main.py
```

El primer comando valida archivos requeridos, Tkinter, compilación, pruebas y la
demostración. El segundo abre la interfaz gráfica para repetir el recorrido manual.

Esto no está especificado en los documentos académicos; se incorpora como decisión
de implementación para evitar omisiones y contaminación de la entrega final. No
añade llamadas al sistema, capas, dependencias ni comportamiento funcional.
