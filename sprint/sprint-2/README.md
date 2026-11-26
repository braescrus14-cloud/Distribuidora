# Sprint 2 · Compras, proveedores, clientes y pedidos

**[Cómo confirmar este sprint](VERIFICACION.md)** · [Todos los sprints](../README.md)

Este es el índice del segundo incremento de Villali. La aplicación integrada usa `main/proyecto-completo` y la misma base de MongoDB Atlas del servicio existente de [Render](https://villali-staging.onrender.com/). El código histórico se conserva en la etiqueta `sprint-2`; no se necesita otra carpeta de programa ni otro servicio para usar estas funciones. [Versiones conservadas](../../proyecto-completo/documentacion/Versiones.md).

## Documentos y evidencias

- **[Paso a paso para verificar el Sprint 2 en Render](Guia_Verificacion_Sprint_2.md).** Preparación, roles, recorrido y resultados esperados.
- [Alcance, puntos y diferencias respecto al Sprint 1](../../proyecto-completo/documentacion/historial/Comparacion_Sprint_1_y_2_Villali.md).
- [Comparación de los tres sprints](../../proyecto-completo/documentacion/historial/Comparacion_Sprints_1_2_3.md).
- [Código comercial integrado](../../proyecto-completo/commerce.py), [interfaz](../../proyecto-completo/app.js) y [pruebas](../../proyecto-completo/test_commerce.py).
- [CI Sprint 2](https://github.com/braescrus14-cloud/Distribuidora/actions/workflows/sprint-2.yml): SQLite, PostgreSQL y MongoDB de ensayo, permisos, reservas y persistencia.
- [Versión archivada antes del Sprint 3](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-2).

## Historias implementadas

| Historia | Comportamiento a verificar | Perfil principal |
| --- | --- | --- |
| HU-06 | Proveedor con NIT y dígito válidos, productos asociados y estado activo/inactivo. | Coordinador de Compras · 05 |
| HU-07 | Orden de compra, aprobación sobre COP 10 millones y recepción por lote con al menos seis meses de vida útil. | Compras · 05, Gerencia · 01, Bodega · 03/04 |
| HU-08 | Cliente con zona y lista de precios; cupo y cartera administrados por Gerencia. | Asesor · 06 y Gerencia · 01 |
| HU-09 | Venta validada contra stock, precio, cupo/cartera; confirmación reserva unidades por lote. | Asesor · 06 |
| HU-10 | Portal de la ficha vinculada; solicitud pendiente de revisión y aislamiento entre clientes. | Cliente · 10 y Asesor · 06 |

El resultado de una CI no equivale a aceptación de una historia. Registrar las pruebas reales del equipo con fecha, responsable y evidencia; no atribuir aprobaciones a compañeros que no las hayan realizado.
