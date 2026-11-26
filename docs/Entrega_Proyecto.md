# Entrega académica de los cuatro sprints

Villali integra las **20 historias HU-01–HU-20** del proyecto en una sola aplicación: acceso e inventario, compras y pedidos, distribución y seguimiento, facturación y recaudo. La portada y las diez experiencias por rol se conservan. Las conexiones DIAN/PSE del Sprint 4 son simuladores académicos autorizados.

## Qué cambió y dónde revisarlo

| Sprint | Incremento | Documentación y demostración | Copia histórica |
| --- | --- | --- | --- |
| 1 · HU-01–05 | Sesión, usuarios/permisos, catálogo, Excel, consulta por lote | [Expediente](sprint-1/Sprint_1_Villali.md) · [Aplicación base](../sprint-1/README.md) | [sprint-1](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-1) |
| 2 · HU-06–10 | Proveedores, compras, clientes, venta y portal propio | [Expediente](sprint-2/README.md) · [Guía](sprint-2/Guia_Verificacion_Sprint_2.md) | [sprint-2](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-2) |
| 3 · HU-11–15 | FEFO, rutas, despacho, evidencia de entrega y seguimiento; portada/UX | [Informe completo](sprint-3/Informe_Consolidado_Sprint_3.md) · [Guía](sprint-3/Guia_Verificacion_Sprint_3.md) | [sprint-3](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-3) |
| 4 · HU-16–20 | Facturas, pagos/cartera, liquidación, indicadores, devoluciones/cierre | [Expediente](sprint-4/README.md) · **[Guía Sprint 4](sprint-4/Guia_Verificacion_Sprint_4.md)** | Código integrado en main; corte final se identifica por commit |

Las ramas históricas conservan su código aunque el servicio de Render avance. No es necesario crear servicios ni bases duplicados para compararlas. La comparación de GitHub [Sprint 3 → versión actual](https://github.com/braescrus14-cloud/Distribuidora/compare/sprint-3...main) muestra el incremento final.

## Tecnología y persistencia

Frontend HTML/CSS/JavaScript, servidor Python, MongoDB Atlas en Render y pruebas compatibles con SQLite/PostgreSQL. Render usa `main/sprint-1`; el nombre es histórico y no limita la aplicación al Sprint 1. Los documentos financieros y las evidencias se conservan en Atlas. PDF/XML se regeneran desde los registros, sin depender del disco de Render.

No se cambian `MONGODB_URI`, `MONGODB_DATABASE` ni las credenciales para publicar este incremento. No ejecutar cargas iniciales o semillas sobre una base con datos existentes. Los respaldos de código no incluyen los datos privados de MongoDB: el equipo debe conservar una copia de datos fuera del repositorio.

## Verificación de la versión

[Aplicación](https://villali-staging.onrender.com/) · [Acceso](https://villali-staging.onrender.com/entrar) · [Versión y commit](https://villali-staging.onrender.com/version) · [Salud](https://villali-staging.onrender.com/health) · [Cuatro workflows de CI](https://github.com/braescrus14-cloud/Distribuidora/actions).

La versión final debe mostrar `sprints-1-a-4` y los dos proveedores en modo `simulador-academico`. Comparar su commit con el Live de Render y las CI. La validación local del 25/11/2026 cubrió las cuatro suites, reinicios y siete recorridos visuales de los nuevos módulos en computador/celular; las pruebas de PostgreSQL/MongoDB corresponden a los workflows publicados.

## Para presentar al profesor

1. Mostrar el README, las cuatro carpetas de documentación y las copias históricas.
2. Mostrar CI del mismo commit publicado, `/version` y `/health`.
3. Recorrer compra → lote → pedido → FEFO → ruta → entrega → factura → pago → cierre usando las guías por sprint.
4. Demostrar dos roles distintos y que el cliente solo accede a sus pedidos/documentos.
5. Descargar manifiesto, factura, XML, nota crédito, acta de ruta y reporte Excel/PDF del filtro mostrado.
6. Explicar la simulación DIAN/PSE y registrar las revisiones/aceptaciones reales en cada expediente SDD.

La entrega académica no convierte los ejemplos de la portada en datos empresariales verificados ni los documentos del simulador en comprobantes legales. La aceptación de las historias y las cuatro puertas corresponde a los responsables del equipo.
