# Copias y restauración del Sprint 3

**Corte documental:** 25 de noviembre de 2026. **Repositorio:** braescrus14-cloud/Distribuidora. El respaldo conserva código y documentación. No contiene la base de Atlas, sesiones del navegador ni secretos de Render.

## Copia de cierre

- [Rama sprint-3-archivo](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-3-archivo): fotografía de los Sprints 1, 2 y 3 integrados, con el informe y la documentación de cierre. La rama queda reservada como referencia antes de continuar el proyecto.
- [Descargar la copia completa como ZIP](https://github.com/braescrus14-cloud/Distribuidora/archive/refs/heads/sprint-3-archivo.zip): archivo generado por GitHub desde esa misma rama. No es una segunda copia de los datos de la empresa.
- [Manifiesto SHA-256](Manifiesto_Respaldo_Sprint_3.json): identifica los 40 archivos de la aplicación y las respuestas públicas comprobadas. En archivos de texto se normaliza CRLF a LF para comparar Windows con Render.
- Copia local del mismo corte: `C:/Distribuidora/Respaldos/Sprint3_Cierre_2026-11-25.zip`. La aplicación de trabajo continúa en `C:/Distribuidora/Sprint3`.

La aplicación de referencia publicada es `7796943c9e73769c766ace322f5180c7c813240d`. La documentación acumulada antes de este informe estaba en `09498e29fcf9448e971aaa8bcf057470ca02f870`. La rama de archivo incorpora además este cierre documental; el hash final se consulta en su encabezado de GitHub, sin confundirlo con un cambio de programa.

## Copias anteriores conservadas en GitHub

| Referencia | Commit | Qué conserva |
| --- | --- | --- |
| [sprint-1-archivo](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-1-archivo) | b7e70f004397e4d171e324fdb25a17452e59fe4f | Versión histórica del Sprint 1. |
| [sprint-2-archivo](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-2-archivo) | bd7e69b83c5ef8bee8c1df1b333d4e7fa7511db4 | Sprints 1 y 2 antes del incremento logístico. |
| [sprint-3-antes-redisenio](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-3-antes-redisenio) | 8cb4624a6f2ac8a5722d51c9dca89c16d6fb04dc | Primera versión publicada de Sprint 3 antes del rediseño. |
| [sprint-3-ux-79-archivo](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-3-ux-79-archivo) | 65a7e332315f475f26afef16b8bba7ece2932618 | Primer rediseño y sus evidencias. |
| [sprint-3-antes-acceso-unico](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-3-antes-acceso-unico) | c4fdaf8a240ec9057512a1b62bce700387a528d3 | Revisión visual anterior al acceso único por correo/usuario. |

Archivos locales anteriores existentes y comprobados: `Sprints_1_y_2_bd7e69b.zip`, `Sprint3_antes_redisenio_8cb462.zip` y `Sprint3_antes_revision_final_65a7e33.zip`. Se conservan como historial, sin sustituir la copia de cierre.

## Comparar versiones para la presentación

1. Abre [Sprint 2 → versión publicada de Sprint 3](https://github.com/braescrus14-cloud/Distribuidora/compare/bd7e69b83c5ef8bee8c1df1b333d4e7fa7511db4...7796943c9e73769c766ace322f5180c7c813240d).
2. Abre [primera versión logística → mejoras finales](https://github.com/braescrus14-cloud/Distribuidora/compare/e65a60c0483eb786dc3eca9c9c06290b4a3a8506...7796943c9e73769c766ace322f5180c7c813240d).
3. Usa el [informe consolidado](Informe_Consolidado_Sprint_3.md) para relacionar cambios con historias, tareas y mejoras solicitadas.

## Recuperar código sin perder datos

1. Descarga el ZIP de la rama de archivo o consulta los archivos desde GitHub. Extrae en un directorio de trabajo separado para comparar, sin sobrescribir datos locales de operación.
2. Para revertir el servicio existente, selecciona un commit de código conocido con **Manual Deploy → Deploy a specific commit**, tras revisar compatibilidad. No cambies la carpeta raíz `sprint-1` ni el plan gratuito.
3. Conserva `MONGODB_URI`, `MONGODB_DATABASE` y las demás variables ya configuradas. No publiques sus valores ni habilites cargas iniciales para hacer rollback.
4. Comprueba `/health`, acceso, inventario, pedidos, rutas y evidencias con las cuentas autorizadas. Revertir código no revierte las operaciones que ya se guardaron en la base.
5. Una recuperación de datos de Atlas requiere una exportación o respaldo de esa base y un procedimiento independiente. No se realizó ni se afirma aquí que exista una copia de Atlas.
6. Antes de borrar datos del sitio en un teléfono de reparto, sincroniza sus confirmaciones pendientes. El ZIP de código no recupera la cola IndexedDB de ese dispositivo.
