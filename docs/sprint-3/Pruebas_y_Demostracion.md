# Pruebas y demostración · Sprint 3

## Preparación

Abrir la portada pública y pulsar **Ingresar a Villali**. Usar las cuentas del proyecto con los roles indicados; los cambios de apariencia no conceden permisos nuevos. El administrador debe tener un Conductor activo y un Cliente vinculado a su ficha comercial. No se incluyen contraseñas en este documento.

En el acceso actualizado, seleccionar **Clientes** para el rol 10 y **Equipo** para los demás. Después de ingresar aparece un Inicio específico para cada responsabilidad. Abrir desde allí las acciones principales o los módulos del menú. En celular se puede desplegar el menú con su botón superior. [Tabla completa para registrar la verificación](Tabla_Verificacion_Sprint_3.md).

Se necesitan pedidos confirmados con reservas y lotes vigentes. El catálogo por sí solo no genera existencias. Si falta saldo, registrar una recepción de compra o una carga adicional validada. Usar datos de ensayo separados de los saldos reales.

## Recorrido para el profesor

| Paso | Perfil | Qué mostrar | Resultado esperado |
| --- | --- | --- | --- |
| 1 | Visitante | Portada, líneas de nutrición, proceso de compra, versión móvil | Información del campo y entrada al sistema sin exponer información privada |
| 2 | Asesor 06 | Crear/confirmar un pedido con saldo | Reserva FEFO, estado Confirmado |
| 3 | Auxiliar 04 | Abrir Alistamiento FEFO, probar un EAN distinto y luego el correcto | Rechazo visible y sonoro; solo el EAN correcto confirma la referencia |
| 4 | Auxiliar 04 | Finalizar el pedido y descargar rótulo | Estado Alistado, descuento físico único y PDF con QR |
| 5 | Coordinador 07 | Registrar vehículo, kg por unidad y coordenadas de clientes | Configuración visible; ayudas explican cada campo |
| 6 | Coordinador 07 | Intentar exceso de capacidad y luego planificar una ruta válida | Rechazo del exceso; mapa y orden de visitas para pedidos de igual zona |
| 7 | Jefe 03 | Verificar un rótulo ajeno y después los de la ruta | Pedido ajeno rechazado; solo cargue completo habilita despacho |
| 8 | Jefe 03 | Emitir manifiesto y abrir PDF | Manifiesto MD-… y pedidos En ruta |
| 9 | Cliente 10 | Consultar seguimiento con su cuenta | Línea de tiempo, ETA aproximada y entregas anteriores pendientes |
| 10 | Conductor 08 | Abrir jornada, registrar firma, foto y ubicación con permiso | Pedido Entregado y evidencia guardada |
| 11 | Conductor 08 | Registrar una entrega con cliente cerrado como Novedad | Observación obligatoria, aviso a Coordinación y retorno pendiente |
| 12 | Jefe 03 | Recibir físicamente el retorno y registrar ubicación | Cantidad repuesta por lote una sola vez |
| 13 | Coordinador 07 | Abrir Evidencia del pedido en su ruta | Firma y fotografía protegidas |

Las coordenadas del destino son las de la finca; las de origen son las de la bodega. El peso se registra por **unidad de venta**, por ejemplo 40 para un bulto de 40 kg. La capacidad del vehículo está en kg. El mapa representa proximidad geográfica; no reemplaza la verificación vial del coordinador.

## Prueba sin conexión

1. En un teléfono autorizado, abrir `/entrar` con conexión y entrar como Conductor. Esperar a que aparezca su jornada asignada.
2. Con al menos tres pedidos En ruta, desconectar la red. Registrar tres confirmaciones con sus evidencias o novedades válidas.
3. Comprobar **3 confirmaciones pendientes de sincronizar**, recargar y verificar que siguen pendientes.
4. Recuperar conexión. Esperar la sincronización o pulsar **Sincronizar y actualizar**. Si la sesión venció, volver a ingresar con la misma cuenta.
5. Verificar cero pendientes y una sola confirmación por pedido. Confirmar desde otra cuenta autorizada el estado y sus evidencias.

El navegador conserva la cola en ese dispositivo. No borrar datos del sitio, desinstalar la aplicación ni usar navegación privada antes de sincronizar. Se registra fecha de captura y fecha del servidor por separado. GPS puede requerir permiso, HTTPS y disponibilidad del dispositivo aun sin red.

## Privacidad

Con dos clientes vinculados a fichas distintas, intentar consultar `/api/logistica/tracking?id=IDENTIFICADOR_AJENO` desde la segunda sesión: debe devolver 404. Con un segundo conductor, la jornada y las evidencias del primero no deben ser accesibles. Un rol no autorizado recibe 403. Las pruebas de firma/foto no aparecen en el portal del cliente.

## Comprobaciones ejecutadas el 20 de noviembre de 2026

- `python tests/smoke.py`: regresión HU-01 a HU-05, satisfactoria en SQLite local.
- `python test_commerce.py`: regresión HU-06 a HU-10 y persistencia tras reinicio, satisfactoria en SQLite local.
- `python test_logistics.py`: HU-11 a HU-15 por HTTP, permisos de los diez roles, FEFO 10+5, doble finalización concurrente, capacidad, rótulo/manifiesto PDF, entregas, novedad, retorno, reintentos y persistencia tras reinicio.
- Navegador Edge en entorno local aislado: portada escritorio/móvil, acceso y vista inicial de los diez roles, apertura de evidencia y ausencia de errores JavaScript. Tres confirmaciones en IndexedDB sobrevivieron a una recarga sin red y se enviaron una vez al recuperar conexión; esa comprobación del navegador usó un receptor HTTP simulado. La idempotencia del servidor se verifica aparte en la suite HTTP.

La CI `sprint-3.yml` repite la suite logística con SQLite, PostgreSQL y MongoDB en réplica de ensayo. El resultado de la ejecución se consulta en [GitHub Actions](https://github.com/braescrus14-cloud/Distribuidora/actions/workflows/sprint-3.yml). No usa la base de Atlas de Render.

## Validación pendiente del equipo

Realizar el recorrido en staging, validar los pesos/destinos reales, el lector de bodega y captura de cámara/GPS en el teléfono del conductor. Anexar la ejecución CI del commit desplegado, prueba de persistencia en Atlas tras reinicio y aceptación por historia. Los ensayos automatizados no sustituyen esas aprobaciones.
