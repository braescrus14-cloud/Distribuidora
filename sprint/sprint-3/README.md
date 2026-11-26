# Sprint 3 · Distribución y entrega

**[Cómo confirmar este sprint](VERIFICACION.md)** · [Todos los sprints](../README.md)

**HU-11–HU-15 · 21 puntos · T041–T059.** El incremento conecta pedidos confirmados con alistamiento, rutas, despacho, entrega y seguimiento. También incorpora la portada para productores rurales y las experiencias de los diez roles.

**[Paso a paso para probar el Sprint 3](Guia_Verificacion_Sprint_3.md)** · [Tabla para registrar resultados](Tabla_Verificacion_Sprint_3.md) · [Copia de cierre](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-3)

## Documentos del expediente

| Documento | Contenido |
| --- | --- |
| [Informe consolidado](Informe_Consolidado_Sprint_3.md) | Funciones, mejoras, cronología, pruebas y publicación |
| [Especificación](spec.md) | Cinco historias y criterios de aceptación |
| [Plan técnico](plan.md) | Arquitectura, contratos, permisos, PWA y límites de mapa/ETA |
| [Tareas](tasks.md) | T041–T059 y trazabilidad |
| [Registro SDD](Registro_SDD.md) | Cuatro puertas, evidencias y aceptación pendiente de responsables |
| [Copias y restauración](Copias_y_Restauracion.md) | Copia del Sprint 3 y recuperación sin sustituir Atlas |
| [Manifiesto SHA-256](Manifiesto_Respaldo_Sprint_3.json) | Archivos del cierre y comprobaciones de recursos publicados |
| [Datos académicos](Datos_Demostracion_Academica.md) | Procedencia de los ejemplos de la portada |
| [Validaciones pendientes](Datos_Pendientes_Confirmacion.md) | Datos técnicos de fabricante que requieren confirmación |
| [Historial de diseño](historial/README.md) | Revisiones anteriores de portada, animaciones y acceso |

## Código y pruebas

La versión vigente está integrada con los otros sprints en [main/proyecto-completo](../../proyecto-completo). [CI Sprint 3](https://github.com/braescrus14-cloud/Distribuidora/actions/workflows/sprint-3.yml) cubre SQLite, PostgreSQL y MongoDB de ensayo.

La referencia de cierre es la etiqueta `sprint-3`, commit `d07c5673968e4e9ea883d1564d354ee920e5346d`. Consultar [todas las versiones y comparaciones](../../proyecto-completo/documentacion/Versiones.md). Las pruebas de cámara, GPS, lector y trabajo sin conexión se completan con los dispositivos del equipo; las estimaciones de ruta no equivalen a navegación vial ni GPS en vivo.
