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

## Ejecución local

Desde `sprint-2`, instala dependencias con `python -m pip install -r requirements.txt`. Ejecuta `python app.py --setup-if-needed` y abre la URL que imprime el servidor. Para cargar los primeros proveedores, clientes y existencias, configura `VILLALI_SEED_COMMERCE=1` antes de iniciar. La carga inicial se ejecuta una vez por base. Puedes verificar el flujo con `python test_commerce.py` sobre una base local temporal, sin variables de conexión a una base compartida.

## Render

Crea un servicio web Python gratuito a partir de la rama `sprint-2` con carpeta raíz `sprint-2`. Configura el build con `pip install -r requirements.txt`, el arranque con `python app.py` y el health check con `/health`. El archivo `render-sprint-2.yaml` contiene la misma configuración para usarla como Blueprint.

Configura `MONGODB_URI` y `VILLALI_ADMIN_PASSWORD` en Render. Usa `MONGODB_DATABASE=villali_sprint2` y `VILLALI_SEED_COMMERCE=1`. Para revisar ambas versiones, abre el servicio del Sprint 1 y la URL del nuevo servicio en dos pestañas.

Para actualizar `villali-staging`, abre **Settings → Build & Deploy**, elige la rama `sprint-2` y cambia **Root Directory** a `sprint-2`. Conserva `MONGODB_URI` y configura explícitamente `MONGODB_DATABASE=villali` si ese es el nombre que usa el servicio actual. Configura `VILLALI_SEED_COMMERCE=0` para trabajar con el catálogo y las existencias existentes. Comprueba el acceso del servicio a Atlas antes de desplegar en **Manual Deploy**.

Render requiere una conexión MongoDB y el nombre explícito de la base. La carga inicial del servicio independiente registra su ejecución en MongoDB para que un reinicio no vuelva a cargar las existencias.
