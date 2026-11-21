# Villali · Comparación de los sprints 1 y 2

| | Sprint 1 · Base operativa | Sprint 2 · Flujo comercial |
| --- | --- | --- |
| Alcance | HU-01 a HU-05 | HU-06 a HU-10 |
| Resultado | Gestionar el acceso y consultar las existencias por producto y lote. | Comprar a proveedores habilitados, recibir por lote y registrar pedidos con reserva de existencias. |
| Estado | Aplicación publicada para demostración. | Integrado con Sprint 3 en `main/sprint-1` y publicado en el servicio existente. |

## Sprint 1 · Versión de referencia

| Historia | Qué se puede mostrar |
| --- | --- |
| HU-01 · Acceso | Inicio y cierre de sesión, control de sesión y auditoría. |
| HU-02 · Usuarios y roles | Administración de cuentas, permisos, invitación para configurar la contraseña y eliminación de cuentas. |
| HU-03 · Catálogo | Consulta y mantenimiento de productos. |
| HU-04 · Inventario inicial | Carga desde Excel con validación previa. |
| HU-05 · Consulta por lote | Disponibilidad, ubicación y vencimiento. Vista de cámara en modo demostración. |

- [Código de la versión de referencia `b7e70f0`](https://github.com/braescrus14-cloud/Distribuidora/tree/b7e70f004397e4d171e324fdb25a17452e59fe4f/sprint-1)
- [Plan del Sprint 1](sprint-1/Sprint_1_Villali.md)
- [Pruebas del Sprint 1](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/42693510836)
- [Demostración del Sprint 1 en Render](https://villali-staging.onrender.com/)

## Sprint 2 · Cambios incorporados

| Historia | Puntos | Qué debe poder mostrarse en la revisión |
| --- | ---: | --- |
| HU-06 · Proveedores | 3 | Registrar un proveedor con NIT válido y asociarle productos. Un proveedor inactivo queda fuera de las opciones de compra. |
| HU-07 · Compras y recepción | 5 | Una orden superior a COP 10 millones pasa a aprobación gerencial. Al recibir un lote de una orden aprobada, aumenta el saldo por la cantidad recibida. Se rechazan lotes con menos de seis meses de vida útil. |
| HU-08 · Clientes | 3 | Registrar mayoristas o minoristas con lista de precios, zona de entrega y autorización de datos. Solo la Gerencia modifica cupos. |
| HU-09 · Pedidos de venta | 5 | Validar precio, stock y cupo. Confirmar un pedido reserva unidades por lote. La cartera vencida bloquea el pedido a crédito. |
| HU-10 · Portal B2B | 5 | Un cliente ve sus precios, envía un pedido pendiente de revisión y el asesor recibe el aviso. Las referencias agotadas quedan sin opción de agregar. |

Fuente del alcance del Sprint 2 · Proyecto Scrum Distribuidora Villali, hojas **Historias de Usuario**, **Plan Sprint** y **Tareas SDD y Kanban**. HU-06 a HU-09 tienen prioridad Must. HU-10 tiene prioridad Should.

## Dependencias entre historias

1. Preparar la base del Sprint 2 a partir de la versión de referencia.
2. Implementar proveedores y clientes. Validar NIT, estados y permisos para modificar cupos.
3. Construir órdenes de compra y recepción. Comprobar que el saldo cambie al recibir y que el lote quede asociado al proveedor.
4. Implementar pedidos y reservas por lote. Definir el origen de la cartera vencida y probar que dos pedidos simultáneos respeten el saldo disponible.
5. Incorporar el portal B2B. Verificar los precios por cliente, el estado del pedido y el aviso al asesor.

[Documentación vigente del Sprint 2](sprint-2/README.md) · [Paso a paso](sprint-2/Guia_Verificacion_Sprint_2.md) · [Pruebas automatizadas](https://github.com/braescrus14-cloud/Distribuidora/actions/workflows/sprint-2.yml)

## Demostración y despliegue

Abrir el Sprint 1 y consultar un saldo por lote. En el Sprint 2, mostrar la recepción de una compra y confirmar un pedido. Comparar el saldo físico con la cantidad disponible después de la reserva.

El servicio `villali-staging` usa la aplicación integrada en `main`, carpeta `sprint-1`. El despliegue se inicia manualmente en el servicio existente y reutiliza la base `villali` de Atlas. La [versión archivada del Sprint 1](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-1-archivo/sprint-1) queda disponible para comparar.
