# Guía para verificar el Sprint 4

Esta guía sirve para demostrar HU-16 a HU-20 después de los Sprints 1–3. Los ensayos DIAN/PSE son académicos: no emitirán documentos fiscales ni cobrarán dinero. Registrar resultados reales y capturas; no pegar contraseñas ni URI de Atlas en GitHub.

## 1. Comprobar que se publicó la versión correcta

1. Abrir [GitHub en main](https://github.com/braescrus14-cloud/Distribuidora/tree/main) y localizar `docs/sprint-4`, `sprint-1/finance.py`, `finance.js` y `.github/workflows/sprint-4.yml`.
2. Abrir [GitHub Actions](https://github.com/braescrus14-cloud/Distribuidora/actions). Comprobar que las cuatro CI del commit evaluado terminaron en verde.
3. En Render → villali-staging → Deploys, confirmar **Live para ese mismo commit**. Si es otro, usar Manual Deploy → Deploy latest commit. Mantener servicio gratuito y variables de MongoDB.
4. Abrir [versión publicada](https://villali-staging.onrender.com/version). Debe mostrar `release: sprints-1-a-4`, `sprints: [1,2,3,4]`, ambos modos `simulador-academico` y el commit esperado.
5. Abrir [salud del servicio](https://villali-staging.onrender.com/health): debe responder `status: ok`. Esta prueba lee el almacenamiento; no confirma por sí sola las cinco historias.
6. Entrar por [el acceso único](https://villali-staging.onrender.com/entrar). Si una pestaña antigua conserva el menú anterior, recargarla. No borrar los datos del navegador del conductor mientras haya entregas pendientes de sincronizar.

## 2. Preparar un recorrido controlado

Utilizar cuentas activas de los roles **09 Contabilidad, 07 Logística, 03 Bodega, 01 Gerencia y 10 Cliente**. El administrador puede crearlas por invitación y asociar la cuenta cliente a su ficha. Usar las credenciales actuales del equipo; las cuentas `fin1`–`fin10` de la suite automatizada existen exclusivamente en bases desechables y no se crean en Atlas.

Crear pedidos de ensayo identificables desde el Sprint 2 y completar su alistamiento, ruta, despacho y entrega del Sprint 3. Reservar un pedido a crédito y otro de contado, y un cliente sin otras deudas para probar desbloqueo. Tomar nota del SKU, lote, ubicación y cantidades antes de devolver unidades. No reutilizar documentos ya cerrados para buscar el mismo resultado monetario.

Para replicar el ejemplo de $3.250.000, el total entregado del pedido debe ser ese valor. Los ejemplos no se inyectan automáticamente en la base de la empresa.

## 3. Facturación académica · HU-16

1. Con rol 09, abrir **Facturas → Emitir factura de prueba**.
2. Seleccionar un pedido entregado, escribir NIT con dígito de verificación, correo destinatario del ensayo y vencimiento. Un NIT de ejemplo válido para el ensayo es `901763482-9`; verificar el dígito que corresponda a la ficha usada.
3. Para probar rechazo, usar primero un dígito incorrecto. Debe quedar **Rechazada**, con motivo y consecutivo `FE-DEMO`.
4. Pulsar **Corregir y reenviar** con el NIT válido. Se conserva el consecutivo y queda **Emitida**, con CUFE de prueba.
5. Descargar **PDF** y **XML**. Revisar cantidades, precios, total y marca académica. Revisar el destinatario y adjuntos en **Bandeja de envíos simulados**.
6. En otro pedido, el conductor registra dos unidades devueltas al entregar parcialmente. Tras inspección de Bodega, la factura debe incluir solo las unidades recibidas por el cliente.

El correo se registra, no se envía realmente. El CUFE es un identificador del simulador. Las notas y facturas no se presentan ante DIAN.

## 4. Abonos y cartera · HU-17

1. Con rol 09, abrir **Pagos y cartera → Registrar abono**. Seleccionar la factura de $3.250.000, transferencia y $1.250.000. Escribir referencia del ensayo.
2. Comprobar saldo **$2.000.000**, estado **Pago parcial** y un recibo. Verificar el grupo de edad según vencimiento.
3. Intentar abonar $2.500.000: debe rechazarse sin crear recibo ni cambiar el saldo.
4. Como rol 10 asociado al cliente, abrir **Mis facturas y pagos**. Solo deben aparecer sus documentos, nunca los de otra ficha.
5. Pulsar **Iniciar PSE de prueba**, seleccionar factura e indicar $2.000.000. Debe aparecer una intención **Pendiente**, sin descontar todavía el saldo.
6. Pulsar **Confirmar PSE de prueba**. La confirmación firmada deja **Pagada**, saldo cero y recibo PSE. Un reintento no debe duplicarlo.
7. Si el cliente no conserva otras deudas vencidas, el asesor puede confirmar un nuevo pedido a crédito sujeto a disponibilidad y cupo. Si tiene otra deuda vencida, el bloqueo permanece.

Los saldos anteriores se identifican como **Saldo anterior** y se abonan manualmente desde Contabilidad. No se vuelven a sumar como facturas nuevas.

## 5. Liquidar una ruta · HU-18

1. Finalizar una ruta con entregas de contado y devoluciones ya inspeccionadas. Contabilidad emite sus facturas aceptadas.
2. Con rol 07, abrir **Liquidación de rutas**. Revisar ruta, vehículo y recaudo pendiente.
3. Para recaudo esperado de $4.800.000, registrar $4.800.000. Debe quedar **LIQUIDADA** y los pagos deben verse en las facturas, una sola vez.
4. En otra ruta, registrar $50.000 menos que lo esperado sin acta: el cierre debe rechazarse. Añadir motivo y responsable en **Acta de diferencia** y repetir.
5. Descargar **Acta PDF**. La diferencia se conserva; el faltante no borra deuda. Si hay sobrante, se informa como **Sobrante sin aplicar**, sin sobrepagar facturas.

## 6. Tablero gerencial · HU-19

1. Con rol 01, abrir **Tablero gerencial** y elegir periodo; “Todos” es válido en cliente, zona y producto.
2. Con facturación de ensayo de octubre por $185.000.000, elegir 01/10/2026–31/10/2026. Verificar ventas, top 10 y comparación 01/09–30/09. Sin base previa, debe decir **Sin base comparable**.
3. Aplicar un cliente, zona y SKU conocidos; comprobar que el detalle pertenece al filtro. Un filtro sin documentos debe mostrar ventas cero.
4. En **Inventario y reabastecimiento**, comprobar un producto con mínimo 20 y disponible 8: faltante 12. Se muestran también unidades vencidas y relación venta/stock con su fórmula.
5. Descargar **Exportar Excel** y **Exportar PDF**. Conciliar el total del tablero con el detalle y los filtros de ambos archivos. Excel tiene ventas, resumen, inventario, cartera, rankings y mermas; los importes están identificados en centavos.
6. Pulsar **Guardar corte materializado**. Descargar el Excel del corte desde el historial. Ese resultado se conserva aunque se registren operaciones posteriores.

La cartera es actual y se filtra por cliente/zona; no se reconstruye al último día del periodo ni por SKU. El inventario es actual por SKU, independiente de cliente/zona. Leer estas precisiones al interpretar los indicadores.

## 7. Devoluciones y cierre · HU-20

1. Con rol 03, abrir **Devoluciones y mermas**. Las devoluciones de ruta ya aparecen pendientes de inspección. Para una devolución después de la entrega, pulsar **Registrar devolución posterior a entrega** y seleccionar pedido, SKU, lote, ubicación de origen, unidades y motivo.
2. Inspeccionar dos bultos íntegros: seleccionar **Íntegro: volver al inventario**, ubicación de reingreso y motivo. La cantidad del lote original debe aumentar exactamente en dos, conservando vencimiento.
3. Si ya se facturó, revisar la nota `NC-DEMO` y descargar **Nota PDF**; el saldo disminuye. Si ya se pagó, queda saldo a favor visible. No se genera una segunda nota al repetir inspección.
4. Para un bulto averiado, seleccionar **Dañado o vencido: registrar merma** y motivo “Avería en transporte”. No aumenta el disponible.
5. Si hay existencias vencidas en bodega, usar **Registrar merma por vencimiento**: seleccionar lote, cantidad y acta. Se descuentan solo unidades físicas no reservadas; queda historial para el tablero. Un lote vigente o un exceso se rechaza.
6. Pagar el saldo final de un pedido entregado y facturado, con devoluciones inspeccionadas. Debe pasar a **CERRADO** y continuar visible en seguimiento del cliente.

## 8. Conservar evidencias

| Caso | Resultado esperado | Resultado / enlace | Responsable / fecha |
| --- | --- | --- | --- |
| HU-16 | PDF/XML, rechazo y reenvío sin cambiar consecutivo, factura neta | Por registrar | Por registrar |
| HU-17 | Abono, rechazo de sobrepago, PSE, edades y aislamiento | Por registrar | Por registrar |
| HU-18 | Aplicación de recaudo, acta obligatoria y ruta liquidada | Por registrar | Por registrar |
| HU-19 | Filtros, exportación conciliada, faltantes y corte conservado | Por registrar | Por registrar |
| HU-20 | Reingreso/merma, nota crédito y pedido cerrado | Por registrar | Por registrar |
| Persistencia | Volver a iniciar sesión tras un redespliegue: mismos documentos y saldos | Por registrar | Por registrar |

Anexar capturas sin secretos, consecutivos, PDF/XML/Excel, commit y ejecución CI. Las pruebas automatizadas reinician el servidor contra la misma base de ensayo; no reinician ni rellenan Atlas de la empresa. Completar las decisiones reales en el [registro SDD](Registro_SDD.md).
