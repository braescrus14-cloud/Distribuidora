# Distribuidora Villali

Villali gestiona usuarios y permisos, productos y existencias por lote. La versión integrada incluye acceso, catálogo e inventario del Sprint 1, además de proveedores, compras, clientes y pedidos del Sprint 2.

## Aplicación y código

- **Villali en Render.** Abre la aplicación integrada. El menú muestra los módulos habilitados para el rol de cada cuenta. [Abrir Villali](https://villali-staging.onrender.com/)
- **Aplicación integrada para Render.** El servicio existente toma su código de la carpeta `sprint-1` en `main`. Usa MongoDB Atlas para conservar los datos. [Ver aplicación integrada](sprint-1)
- **Versión histórica del Sprint 1.** [Ver código archivado](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-1-archivo/sprint-1)
- **Comparación de los sprints.** [Revisar alcance y cambios](docs/Comparacion_Sprint_1_y_2_Villali.md)
- **Arranque en Windows.** Instrucciones para ejecutar la aplicación en tu equipo, cargar el catálogo y probar el flujo de inventario. [Ver instrucciones para Windows](sprint-1/README.md)

## Sprint 2 · Compras, proveedores, clientes y pedidos

| Historia | Funcionalidad incorporada |
| --- | --- |
| **HU-06 · Proveedores** | Registro de proveedores, validación del dígito de verificación del NIT y asociación de productos. Las compras se crean con proveedores activos. |
| **HU-07 · Compras y recepción** | Órdenes de compra, aprobación gerencial cuando el total supera **$10 millones COP** y recepción parcial o completa por lote. Se exige una vida útil de al menos seis meses. |
| **HU-08 · Clientes** | Fichas de mayoristas y minoristas con zona y lista de precios. Gerencia administra el cupo y la cartera. |
| **HU-09 · Pedidos de venta** | Validación de disponibilidad, precio, cupo y cartera. Al confirmar el pedido, se reservan unidades por lote y disminuye el disponible. |
| **HU-10 · Portal B2B** | Cada cuenta de cliente accede a su ficha y a sus pedidos. Los pedidos del portal quedan pendientes de revisión para el asesor. |

La versión integrada también admite **cargas adicionales de Excel** para incorporar lotes a existencias ya registradas. La validación detecta duplicados antes de guardar.

- **Guía de pruebas por rol.** Recorrido desde la creación de una compra hasta la confirmación de un pedido. [Ver guía del Sprint 2](sprint-2/README.md#recorrido-por-perfiles)
- **Pruebas automatizadas.** GitHub Actions verificó las historias del Sprint 2 con SQLite, PostgreSQL y MongoDB, incluida la persistencia al reiniciar la aplicación. [Ver ejecución de CI](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/43944883006)
- **Aceptación del Sprint 2.** Registra los resultados de la demostración por historia, con responsable, fecha y evidencia. [Comparar los sprints](docs/Comparacion_Sprint_1_y_2_Villali.md)

## Evidencias y documentación del Sprint 1

- **Plan y especificación.** Cronograma reprogramado, historias HU-01 a HU-05, criterios de aceptación y tareas. [Ver el plan](https://github.com/braescrus14-cloud/Distribuidora/blob/main/docs/sprint-1/Sprint_1_Villali.md)
- **Pruebas automatizadas del Sprint 1.** Evidencia histórica de GitHub Actions para el commit `17e5f09`. [Ver la ejecución de CI](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/42563294259)
- **Registro SDD.** Evidencias de la aplicación, del catálogo y de la carga de inventario, junto con el estado de las aprobaciones formales. [Ver el registro](https://github.com/braescrus14-cloud/Distribuidora/blob/main/docs/sprint-1/Registro_Aprobaciones_SDD_Sprint_1.md)
- **Acta simulada de cierre.** Ejercicio académico con las fechas y decisiones simuladas de las cuatro puertas SDD y las cinco historias. [Ver el acta simulada](https://github.com/braescrus14-cloud/Distribuidora/blob/main/docs/sprint-1/Acta_Simulada_Cierre_Sprint_1_Villali.md)
- **Decisión de arquitectura.** Propuesta técnica para el entorno de demostración y diferencias con la arquitectura del taller. [Ver el ADR](https://github.com/braescrus14-cloud/Distribuidora/blob/main/docs/sprint-1/ADR_Sprint_1_Arquitectura_Staging.md)
