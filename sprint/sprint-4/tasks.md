# Tareas y trazabilidad del Sprint 4

Las asignaciones y la numeración proceden de la hoja Tareas SDD y Kanban del Excel. La columna de evidencia vincula implementación y pruebas; no constituye una firma de revisión del responsable indicado. Ventana planificada: 30/11–06/12/2026. Preparación técnica: 25/11/2026.

| Tarea | Trabajo | Responsable / revisor del Excel | Evidencia |
| --- | --- | --- | --- |
| T060 | Esquema de facturas V12 | Cristian / César | Registros facturas, bandeja y contadores en finance.py; adaptación Mongo en plan.md |
| T061 | Pruebas del proveedor | Brayan / César | test_finance.py: NIT rechazado, corrección, consecutivo y PDF/XML |
| T062 | Servicio de facturación | César / Brayan | emit_invoice, document y bandeja simulada |
| T063 | Interfaz de facturas | Cristian / César | finance.js: facturas, emisión, rechazo y reenvío |
| T064 | Esquema de pagos V13 | Cristian / César | pagos, saldos iniciales e intenciones PSE persistentes |
| T065 | Pruebas de webhook | Brayan / César | HMAC válido/incorrecto, caducidad y repetición en test_finance.py |
| T066 | Servicio de pagos | César / Brayan | payment, confirm_pse, account_aging y actualización de cupo |
| T067 | Pagos y cartera | Cristian / César | Módulos Contabilidad/Cliente, edades, recibos y saldos a favor |
| T068 | Pruebas de liquidación | Brayan / César | Recaudo completo, faltante, acta obligatoria y repetición |
| T069 | Servicio de liquidación | César / Brayan | settle_route y pagos contra entrega |
| T070 | Interfaz de liquidación | Cristian / César | Rol 07, recibido/esperado y acta PDF |
| T071 | Indicadores materializados | Cristian / César | dashboard y documentos indicadores_materializados con fecha/filtros |
| T072 | Exactitud y consultas | Brayan / César | Octubre/septiembre, $185 millones, faltante 12, filtros y cortes estables; lecturas agrupadas |
| T073 | API y exportaciones | César / Brayan | export_dashboard, Excel de seis hojas y PDF con filtros idénticos |
| T074 | Tablero gerencial | Cristian / Brayan | Métricas, top 10, filtros, inventario y cortes; navegación móvil verificada |
| T075 | Esquema de devoluciones V14 | Cristian / César | Retornos existentes, notas_credito y mermas persistentes |
| T076 | Pruebas de devolución | Brayan / César | Reingreso +2, avería sin aumento, inspección repetida y cierre tras pago |
| T077 | Servicio de cierre | César / Brayan | report_return, inspect_return, expire_stock y refresh |
| T078 | Interfaz de devoluciones | Cristian / César | Rol 03, inspección, decisión física, merma y nota PDF |

## Cómo registrar una tarea revisada

Abrir su evidencia en el commit evaluado, ejecutar el caso de la [guía](Guia_Verificacion_Sprint_4.md) y registrar resultado, fecha real, responsable y enlace en Sprint Tools. Completar la revisión cruzada antes de marcar aceptación formal en el [registro SDD](Registro_SDD.md). El estado “Completado” del Excel original es planificación de origen, no prueba de una ejecución real.
