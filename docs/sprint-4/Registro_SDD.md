# Registro SDD del Sprint 4

**Preparación técnica:** 25/11/2026. **Periodo del Excel:** 30/11–06/12/2026. **Alcance:** HU-16–HU-20, T060–T078. Los simuladores académicos DIAN/PSE fueron elegidos expresamente por el usuario en este chat. Esta autorización no reemplaza la revisión de cada historia por la Product Owner.

## Cuatro puertas

| Puerta | Evidencia | Decisión | Responsable y fecha |
| --- | --- | --- | --- |
| 0 · Constitución | Copia inmutable del Sprint 3, conservación de Atlas, trazabilidad y documentos académicos identificados | Pendiente de ratificación del equipo | Por registrar |
| 1 · Especificación | [Cinco historias y adaptación académica](spec.md) | Simuladores autorizados por el usuario; aprobación completa pendiente | Product Owner / por registrar |
| 2 · Plan | [Arquitectura documental, API, permisos y conciliación](plan.md) | Pendiente de revisión técnica | Por registrar |
| 3 · Tareas | [T060–T078 y pruebas](tasks.md), CI y [guía](Guia_Verificacion_Sprint_4.md) | Pendiente de revisión cruzada y registro en Sprint Tools | Por registrar |

## Evidencias técnicas del 25 de noviembre

- `tests/smoke.py`: HU-01–HU-05 correctas en HTTP local.
- `test_commerce.py`: HU-06–HU-10 correctas, incluida persistencia después de reiniciar.
- `test_logistics.py`: HU-11–HU-15 correctas; FEFO, permisos, capacidad, PDF, entrega, retornos e idempotencia.
- `test_finance.py`: permisos de los diez roles, aislamiento del cliente, rechazo/reenvío, facturación parcial, abonos, sobrepago, firma PSE/caducidad/repetición, concurrencia, liquidaciones, notas, devoluciones, merma por vencimiento, filtros, exportación, corte materializado y reinicio.
- Navegador Edge local: Facturas 1440 px; Pagos 390 px; Tablero 1440/390 px; Liquidación/Devoluciones 1360 px; Cliente 390 px. Sin desbordamiento de página ni errores JavaScript en ese recorrido.
- [CI Sprint 4](https://github.com/braescrus14-cloud/Distribuidora/actions/workflows/sprint-4.yml): consultar la ejecución del commit que se evalúa para SQLite/PostgreSQL/MongoDB. [Todas las CI](https://github.com/braescrus14-cloud/Distribuidora/actions).

La evidencia de publicación debe vincular el commit Live de Render con `/version` y `/health`. Una construcción exitosa no demuestra que el servicio esté ejecutando la misma versión. El resultado final se registra en [Entrega del proyecto](../Entrega_Proyecto.md).

## Aceptación de las cinco historias

| Historia | Evidencia para demostrar | Decisión | Product Owner / fecha |
| --- | --- | --- | --- |
| HU-16 | Factura, PDF/XML, bandeja académica y reenvío | Pendiente de aceptación | Por registrar |
| HU-17 | Abono, cartera, PSE y bloqueo por otras deudas | Pendiente de aceptación | Por registrar |
| HU-18 | Conciliación, pagos y acta | Pendiente de aceptación | Por registrar |
| HU-19 | Tablero, comparación y exportación conciliada | Pendiente de aceptación | Por registrar |
| HU-20 | Lotes, merma, nota y cierre | Pendiente de aceptación | Por registrar |

Registrar fecha real, responsable, versión, resultado y condiciones después de la demostración. No convertir asignaciones del Excel ni casos simulados en aprobaciones firmadas por compañeros.
