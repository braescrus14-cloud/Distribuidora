# Villali Sprint 1

Aplicación local para autenticación, administración de usuarios, catálogo,
carga inicial de inventario y consulta de existencias por lote.

## Ejecutar en Windows

Abre PowerShell en esta carpeta y ejecuta:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\iniciar.ps1
```

En el primer arranque define la contraseña del usuario `admin` en la terminal.
Debe tener al menos 10 caracteres, una mayúscula, un número y un símbolo.
Luego abre [Villali en localhost](http://localhost:8080). Mantén la terminal abierta.
Puedes cambiar el puerto agregando `-Puerto 8081` al comando.

El lanzador busca Python con `openpyxl` instalado. Si hace falta instalarlo, usa
Python 3.10 o posterior y ejecuta `python -m pip install -r requirements.txt`.
También puedes ejecutar `python app.py --setup-if-needed`.

## Probar las cinco historias

1. Inicia sesión como `admin`. El menú Auditoría muestra accesos, bloqueos y denegaciones.
2. Crea un Jefe de Bodega y un Auxiliar de Bodega. Copia cada enlace de invitación
   y ábrelo en una ventana privada para definir la contraseña correspondiente.
3. Entra como Jefe de Bodega y agrega un producto en el catálogo. Puedes probar
   con el SKU `CHK-CAC-15` y el EAN `7702001234567`.
4. En Carga inicial, descarga la plantilla. Escribe el SKU, un lote, un vencimiento
   futuro, una cantidad entera y una ubicación. Guarda el archivo como `.xlsx`,
   súbelo, revisa la validación y confirma. La base local representa una bodega.
5. Entra como Auxiliar de Bodega y consulta el EAN. Puedes usar un lector configurado
   para enviar Enter, escribir el código o buscar por nombre. El botón de cámara
   abre una vista de demostración que no decodifica ni guarda imágenes.

El catálogo de Italcol se carga por separado con
`python cargar_catalogo.py "ruta-al-catalogo.xlsx"`. El Excel de catálogo
no contiene los lotes, ubicaciones ni cantidades de la carga inicial de bodega.
El importador conserva los identificadores y lotes cuando se actualiza una referencia.
Los precios orientativos y las bases de comparación requieren validación comercial.

## Alcance de la versión local

Python sirve la interfaz y la API en `localhost`. SQLite guarda los datos en
`villali.sqlite3`. La autenticación usa contraseñas derivadas con PBKDF2 y cookies
de sesión de solo HTTP. Las sesiones vencen tras 15 minutos sin actividad en
dispositivos táctiles y 30 minutos en escritorio. Cinco intentos incorrectos
bloquean una cuenta durante 15 minutos.

Las invitaciones se comparten manualmente y la auditoría muestra los bloqueos.
El frontend usa HTML, CSS y JavaScript. Python sirve la API local y SQLite
persiste los datos. La arquitectura del taller,
el envío por correo y la publicación en staging requieren trabajo adicional.
