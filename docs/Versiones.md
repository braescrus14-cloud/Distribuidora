# Versiones y organización del repositorio

**Organización realizada el 25 de noviembre de 2026.** `main` es la rama de trabajo y contiene una sola aplicación integrada. Las versiones cerradas se conservan como **etiquetas Git (Tags)**; no son programas que deban desplegarse por separado.

## Cierres de los cuatro sprints

| Etiqueta | Alcance acumulado | Commit conservado | Consultar y descargar |
| --- | --- | --- | --- |
| sprint-1 | HU-01–05 | `b7e70f004397e4d171e324fdb25a17452e59fe4f` | [Código](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-1) · [ZIP](https://github.com/braescrus14-cloud/Distribuidora/archive/refs/tags/sprint-1.zip) |
| sprint-2 | HU-01–10 | `bd7e69b83c5ef8bee8c1df1b333d4e7fa7511db4` | [Código](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-2) · [ZIP](https://github.com/braescrus14-cloud/Distribuidora/archive/refs/tags/sprint-2.zip) |
| sprint-3 | HU-01–15 y cierre documental | `d07c5673968e4e9ea883d1564d354ee920e5346d` | [Código](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-3) · [ZIP](https://github.com/braescrus14-cloud/Distribuidora/archive/refs/tags/sprint-3.zip) |
| sprint-4 | HU-01–20 y revisión integral | `dd76142784eb321203f19a17f0adf24885d55ba6` | [Código](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-4) · [ZIP](https://github.com/braescrus14-cloud/Distribuidora/archive/refs/tags/sprint-4.zip) |

Los commits de cierre no se modifican al reorganizar `main`. En GitHub, abrir el selector de rama y elegir la pestaña **Tags** para consultarlos. Los documentos dentro de una etiqueta reflejan la estructura que existía al cerrar esa versión; para navegar la documentación vigente, volver al [índice de main](README.md).

## Comparar incrementos

- [Sprint 1 → Sprint 2](https://github.com/braescrus14-cloud/Distribuidora/compare/sprint-1...sprint-2).
- [Sprint 2 → Sprint 3](https://github.com/braescrus14-cloud/Distribuidora/compare/sprint-2...sprint-3).
- [Sprint 3 → Sprint 4](https://github.com/braescrus14-cloud/Distribuidora/compare/sprint-3...sprint-4).
- [Cierre Sprint 4 → trabajo actual](https://github.com/braescrus14-cloud/Distribuidora/compare/sprint-4...main).

## Referencias intermedias

Estas etiquetas conservan los puntos anteriores de diseño y desarrollo; no son ramas de trabajo adicionales.

| Etiqueta | Commit | Origen anterior |
| --- | --- | --- |
| historial/sprint-2-inicial | [4bab91da27046025983d426aa011591c6c09bea2](https://github.com/braescrus14-cloud/Distribuidora/tree/4bab91da27046025983d426aa011591c6c09bea2) | Rama sprint-2 |
| historial/sprint-3-antes-redisenio | [8cb4624a6f2ac8a5722d51c9dca89c16d6fb04dc](https://github.com/braescrus14-cloud/Distribuidora/tree/8cb4624a6f2ac8a5722d51c9dca89c16d6fb04dc) | Rama sprint-3-antes-redisenio |
| historial/sprint-3-ux-79 | [65a7e332315f475f26afef16b8bba7ece2932618](https://github.com/braescrus14-cloud/Distribuidora/tree/65a7e332315f475f26afef16b8bba7ece2932618) | Rama sprint-3-ux-79-archivo |
| historial/sprint-3-antes-acceso-unico | [c4fdaf8a240ec9057512a1b62bce700387a528d3](https://github.com/braescrus14-cloud/Distribuidora/tree/c4fdaf8a240ec9057512a1b62bce700387a528d3) | Rama sprint-3-antes-acceso-unico |

Las antiguas ramas `sprint-1-archivo`, `sprint-2-archivo`, `sprint-3-archivo` y `sprint-4-archivo` corresponden, respectivamente, a las etiquetas de cierre de la primera tabla. Las otras cuatro ramas se trasladaron a las etiquetas de historial. Cada etiqueta conserva exactamente el SHA de su rama anterior.

## Qué se retiró de main

- Carpeta raíz `sprint-2/`: segunda copia antigua del programa; conservada en las etiquetas y en el historial Git.
- `render-sprint-2.yaml`: configuración antigua de otro servicio/base. La configuración vigente es `render.yaml`.
- `Pruebas_y_Demostracion.md` del Sprint 3: recorrido repetido, unificado en `Guia_Verificacion_Sprint_3.md`. El informe conserva la evidencia de su ensayo sin conexión.
- Comparaciones anteriores y revisiones de diseño: agrupadas en directorios `historial/`, con sus enlaces actualizados.
- Repeticiones de alcance y enlaces en el README raíz: sustituidas por un índice y enlaces a los expedientes correspondientes.

## Respaldos y recuperación

Antes de retirar las ramas se creó y verificó un respaldo completo de sus objetos e historial en `C:/Distribuidora/Respaldos/Antes_Organizacion_GitHub_dd76142.bundle`, con archivo SHA-256 adjunto. También se conservan los ZIP anteriores y la copia integrada en `C:/Distribuidora/Sprint4`.

Para consultar una versión, descargar el ZIP de su etiqueta y extraerlo en otra carpeta. Para restaurar una rama, crearla desde el commit de la tabla; conservar la etiqueta. La operación de retirar ramas no elimina esos commits porque siguen referenciados por las etiquetas.

Render continúa usando **main → sprint-1**, con el mismo `render.yaml`, servicio gratuito y MongoDB Atlas. Esta limpieza no cambia el programa operativo ni su configuración de almacenamiento. Al restaurar código, conservar las variables de Atlas y comprobar compatibilidad antes de desplegar. Un rollback de código no revierte los datos.

Las etiquetas, ZIP y el bundle son respaldos del repositorio, no de Atlas ni de la cola offline del conductor. Sincronizar las entregas pendientes antes de borrar datos del navegador y conservar por separado los respaldos de la base que gestione el equipo.
