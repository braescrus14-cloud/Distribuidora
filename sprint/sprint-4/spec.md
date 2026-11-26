# Especificación del Sprint 4

Fuente de alcance: `Proyecto Scrum Distribuidora Villali.xlsx`, hojas Historias de Usuario, Plan Sprint y Tareas SDD y Kanban. Los ejemplos monetarios se muestran en COP. El servidor conserva importes en centavos enteros para evitar errores de redondeo.

| Historia | Rol | Puntos | Comportamiento y criterios implementados |
| --- | --- | --- | --- |
| HU-16 · Facturación | 09 | 5 | AC-016.1: pedido entregado de $3.250.000 genera factura, PDF/XML y CUFE de prueba, con destinatario en bandeja simulada. AC-016.2: dos bultos devueltos en ruta se excluyen de las cantidades facturadas. AC-016.3: NIT inválido deja RECHAZADA con motivo y conserva el consecutivo al corregir. |
| HU-17 · Pagos y cartera | 09 | 5 | AC-017.1: abono de $1.250.000 sobre $3.250.000 deja $2.000.000 y PAGO_PARCIAL. AC-017.2: confirmación firmada de PSE cancela el saldo; deja de bloquear por mora si no existen otras deudas vencidas. AC-017.3: $2.500.000 sobre saldo $2.000.000 se rechaza. |
| HU-18 · Liquidación | 07 | 3 | AC-018.1: recibido igual al esperado de $4.800.000 aplica pagos y deja LIQUIDADA. AC-018.2: faltante de $50.000 exige acta. Un sobrante también exige acta y se conserva sin aplicarlo como sobrepago. |
| HU-19 · Tablero | 01 | 5 | AC-019.1: filtro octubre de 2026 suma $185.000.000 en el ensayo, compara septiembre y muestra top 10 de clientes/productos. AC-019.2: mínimo 20 y disponible 8 muestra faltante 12. AC-019.3: Excel y PDF usan los mismos filtros; los cortes materializados conservan los resultados del momento del guardado. |
| HU-20 · Devoluciones y cierre | 03 | 3 | AC-020.1: dos bultos íntegros aumentan el lote original y generan nota crédito si ya se facturaron. AC-020.2: avería registra merma sin aumentar existencias. AC-020.3: saldo cero cierra el pedido cuando no quedan devoluciones pendientes de inspección. |

## Reglas de conciliación

La factura se emite por cantidades efectivamente entregadas. Una devolución posterior a la entrega se inspecciona antes de facturar; se descuenta de la primera factura. Si ya se había emitido, se genera una nota crédito. Así se evita descontar dos veces la misma devolución. Si la factura ya estaba pagada, la nota produce un **saldo a favor** visible; no simula un reembolso bancario.

Una liquidación exige ruta finalizada, facturas aceptadas e inspección de devoluciones. Se recaudan las facturas de contado pendientes, sin volver a cobrar las ya pagadas ni las ventas a crédito. Un faltante mantiene la deuda y un sobrante queda identificado en el acta.

Los saldos anteriores al Sprint 4 se mantienen separados de las nuevas facturas y se pueden abonar desde Contabilidad. El cupo comercial no suma dos veces un pedido ya facturado. Las solicitudes repetidas de pago, corte, inspección y liquidación no duplican sus efectos.

## Alcance de los indicadores

- Ventas: facturas aceptadas menos notas crédito por la fecha de cada documento, filtradas por periodo, cliente, zona y SKU.
- Comparación: mes calendario anterior para un mes completo; periodo anterior de igual duración para otros intervalos. Sin ventas base, se informa “Sin base comparable”.
- Inventario: existencia actual del SKU, disponible sin vencidos ni reservas, mínimo, faltante y unidades vencidas. No se asigna inventario a clientes o zonas.
- Rotación operativa: unidades netas facturadas del periodo / existencia física actual. La pantalla y los archivos explican esta definición; no equivale a una rotación contable calculada sobre inventario promedio.
- Cartera: saldos actuales por cliente y zona, con edades Al día, 1–30, 31–60, 61–90 y Más de 90. No es un saldo histórico a la fecha final ni una asignación de cartera por SKU.
- Mermas: devoluciones inspeccionadas como merma y retiros de lotes vencidos registrados por Bodega. Las unidades vencidas aún no retiradas se muestran por separado; no se descuentan automáticamente sin inspección.

## Adaptación académica autorizada

La llamada a proveedor DIAN, el CUFE y la distribución de PDF/XML se simulan. El XML se identifica como `AcademicInvoice`, no como documento fiscal validado. La transacción PSE solo se contabiliza al verificar un evento firmado del simulador. No se usan credenciales DIAN/PSE reales ni se solicita un plan de pago.
