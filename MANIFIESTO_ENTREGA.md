# Manifiesto del paquete de entrega

Desde la raíz del proyecto:

```powershell
python crear_paquete.py
```

Se generan `dist/ASO_Proyecto_Final.zip` y `dist/ASO_Proyecto_Final.sha256`.
La suma SHA-256 permite comprobar la integridad del ZIP. El generador usa una lista
explícita de archivos y termina con error si falta alguno de ellos.

## Contenido

- Arranque, demostración, verificador y generador del paquete.
- Fuentes Python de `simulador/` y `tests/`.
- README, manual, matriz de pruebas, notas técnicas, evidencias, guía de defensa,
  informe final y este manifiesto.
- Los dos documentos académicos originales bajo `docs/`.
- `.gitignore`.
- La carpeta vacía `datos/archivos/`.

## Exclusiones

Se excluyen las instrucciones internas de desarrollo, el historial de Git,
`__pycache__`, archivos `.pyc`, el directorio `dist/` y todos los archivos existentes
en `datos/archivos/`. Los datos locales permanecen en el proyecto original.

Los archivos que se creen al usar la copia extraída persistirán dentro de su propia
carpeta `datos/archivos/`.

## Uso después de extraer

Se necesita Python con Tkinter y permiso de escritura en la carpeta extraída.
El ZIP contiene código fuente, no un ejecutable independiente.

Desde esa carpeta:

```powershell
python verificar_entrega.py
python main.py
```

El primer comando comprueba archivos requeridos, Tkinter, compilación, pruebas y
demostración. El segundo abre la interfaz para seguir el [manual](MANUAL_USO.md).

Para comparar la suma del paquete con el valor del archivo `.sha256`:

```powershell
Get-FileHash -Algorithm SHA256 .\dist\ASO_Proyecto_Final.zip
Get-Content .\dist\ASO_Proyecto_Final.sha256
```
