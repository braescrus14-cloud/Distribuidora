# Registro de aprobaciones SDD del Sprint 1

**Proyecto** · Plataforma Villali  
**Alcance** · HU-01 a HU-05  
**Estado** · En revisión. Las aprobaciones se registran cuando el responsable confirme su decisión.

## Puertas de revisión

| Puerta | Evidencia para revisión | Decisión | Responsable y fecha |
| --- | --- | --- | --- |
| 0 · Constitución | Principios de trabajo, trazabilidad de cambios, privacidad y revisión cruzada descritos en `Sprint_1_Villali.md`. | Pendiente de ratificación | Por registrar |
| 1 · Especificación | Cinco historias con criterios de aceptación. Revisar la distinción entre cámara de demostración y escaneo de códigos, y el estado de las notificaciones de acceso. | Pendiente de aprobación | Por registrar |
| 2 · Plan técnico | Frontend HTML, CSS y JavaScript. La versión local usa un servicio Python y SQLite. Resolver la diferencia frente a la arquitectura propuesta en el taller y revisar el contrato de la API. | Pendiente de decisión técnica | Por registrar |
| 3 · Tareas | Veinte tareas con responsables, dependencias y referencias a criterios. Falta comprobar su registro y sus evidencias en Sprint Tools. | Pendiente de verificación | Por registrar |

Para cada decisión, anotar la fecha, el responsable, la versión o enlace de la evidencia y las observaciones o condiciones.

## Evidencias del incremento

| Historia | Evidencia disponible | Pendiente para aceptación |
| --- | --- | --- |
| HU-01 · Acceso | Inicio y cierre de sesión, vencimiento, bloqueo por intentos y bitácora de accesos verificados localmente. | Completar la notificación al administrador según el taller y confirmar su entrega. |
| HU-02 · Roles | Administración de cuentas y permisos, con diez perfiles de prueba. | Probar la matriz completa con cada rol y el envío de invitaciones por correo. |
| HU-03 · Catálogo | 91 referencias del Excel actualizado, con 72 precios estimados y 19 referencias de precios publicados anteriormente. El catálogo y el inventario identifican las líneas con distintivos visuales. | Validar códigos internos, empaques no confirmados y precios de operación con Villali. |
| HU-04 · Excel de inventario | Validación previa, rechazo de un archivo con errores y carga atómica probados con datos de ensayo. | Recibir el Excel de bodega con SKU, lotes, ubicaciones, cantidades y vencimientos. Conciliar el 100 % de los saldos. |
| HU-05 · Consulta por lote | Consulta por código o nombre, semáforo de vencimiento y vista de cámara de demostración. | Probar con el dispositivo de bodega y completar el escaneo efectivo según el criterio del taller. |

## Cierre del sprint

- Registrar la aceptación de las cinco historias por la Product Owner durante la revisión.
- Publicar el código, ejecutar CI y anexar el resultado en verde.
- Desplegar el incremento en staging y adjuntar URL y resultado de la prueba de humo. El taller exige staging con CI en verde. Render es el proveedor previsto para Villali.
- Anexar la conciliación del inventario de origen y las decisiones de las cuatro puertas SDD.
