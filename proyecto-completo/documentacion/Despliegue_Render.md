# Desplegar la estructura de carpetas en Render

El programa se trasladó de `sprint-1` a **`proyecto-completo`**. El servicio existente debe usar la nueva carpeta. El cambio conserva el plan gratuito, las variables de entorno y la misma base MongoDB Atlas.

## Ajuste único de carpeta raíz

1. Esperar las cuatro CI en verde para el commit de esta organización.
2. En Render, abrir **villali-staging → Settings → Build & Deploy → Root Directory**.
3. Cambiar `sprint-1` por **`proyecto-completo`** y guardar. El `rootDir` de `render.yaml` ya contiene ese valor. Si el servicio no está gestionado por Blueprint, editar el YAML en GitHub no cambia por sí solo la configuración guardada en el panel.
4. Mantener **Build Command:** `pip install -r requirements.txt`; **Start Command:** `python app.py`; **Health Check:** `/health`.
5. Mantener rama **main**, plan **Free** y los valores actuales de `MONGODB_URI`, `MONGODB_DATABASE` y las demás variables.
6. Usar **Manual Deploy → Deploy latest commit**, si guardar no inició el despliegue.
7. Comprobar **Live** para ese commit, [salud](https://villali-staging.onrender.com/health) y [versión](https://villali-staging.onrender.com/version). Después ingresar con una cuenta de cada rol necesario.

No iniciar un despliegue nuevo con la carpeta raíz antigua: esa ruta ya no contiene el programa en esta estructura. La publicación anterior que siga Live corresponde al código de su propio commit.

Según la [documentación oficial de Render](https://render.com/docs/monorepo-support), los comandos se ejecutan dentro de Root Directory y los archivos externos a esa carpeta no están disponibles al servicio. Por eso no se dejó un lanzador que dependa de una carpeta hermana.

## Datos y comprobación

Reorganizar código no borra los documentos de Atlas. No cambiar de base, borrar colecciones, ejecutar restauraciones o volver a cargar el catálogo/inventario para desplegar. El servicio debe arrancar con los mismos usuarios, lotes, pedidos y evidencias.

Para la aceptación, seguir [las cuatro verificaciones](../../sprint/README.md) y guardar el commit, CI, URL y resultados reales. Un cambio de carpeta no convierte una revisión pendiente en aprobación.
