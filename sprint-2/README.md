# Villali · Sprint 2

El módulo comercial agrega proveedores, órdenes de compra, recepción por lote, clientes, pedidos de venta y el portal de pedidos. El código del Sprint 1 se usa como base para el catálogo, los perfiles y el inventario.

## Recorrido por perfiles

1. Crea cuentas para Coordinador de Compras, Gerente General, Jefe o Auxiliar de Bodega, Asesor Comercial y Cliente desde **Usuarios y roles**. Activa las cuentas con sus invitaciones.
2. Como Coordinador de Compras, habilita un proveedor y asóciale productos. Crea una orden por encima de COP 10 millones para mostrar la aprobación por Gerencia.
3. Como personal de Bodega, recibe la orden aprobada. Puedes escribir el SKU o usar un lector que ingrese el EAN como teclado. Registra el lote, la ubicación y un vencimiento de al menos seis meses.
4. Como Asesor Comercial, registra al cliente o toma una ficha sin asesor editándola. Vincula la cuenta de cliente para habilitar el portal. El precio mayorista de la lista A aplica un descuento del 5 % sobre el catálogo. La lista B usa el precio del catálogo.
5. Como Gerente General, registra el cupo y el saldo de cartera. Para un saldo pendiente, registra el vencimiento más antiguo. El sistema usa esos datos para validar los pedidos a crédito.
6. Como Cliente, abre **Portal de pedidos** y envía una solicitud. Como Asesor, ábrela y confírmala. Compara las unidades disponibles antes y después de la reserva.

Los avisos de compra pendiente y pedido por revisar aparecen en las listas de Gerencia y del Asesor. Para habilitar el correo, configura `RESEND_API_KEY` y `VILLALI_MAIL_FROM` y registra el correo del destinatario en su cuenta. Los correos pueden verificarse en **Auditoría de accesos**.

## Ejecución vigente y Render

Este directorio conserva una versión de referencia del Sprint 2. Para probar el servicio actual, usa la aplicación integrada en `main/sprint-1`; no cambies la rama ni la carpeta raíz de Render a `sprint-2` y no crees otra base de datos.

- [Documentación vigente del Sprint 2](../docs/sprint-2/README.md).
- [Paso a paso de verificación](../docs/sprint-2/Guia_Verificacion_Sprint_2.md).
- [Instrucciones locales de la aplicación integrada](../sprint-1/README.md).
- [Versión archivada de los dos primeros sprints](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-2-archivo).

El servicio `villali-staging` conserva su plan gratuito y la base `villali` existente en MongoDB Atlas. No usar cargas iniciales ni cambiar `MONGODB_DATABASE` para comprobar los incrementos..
