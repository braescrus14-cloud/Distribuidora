# Sprint 4 · Facturación, recaudo y cierre

**[Cómo confirmar este sprint](VERIFICACION.md)** · [Todos los sprints](../README.md)

El Sprint 4 completa el ciclo de compras, venta, distribución y cobro de Villali. Integra **HU-16 a HU-20, 21 puntos y T060–T078** del archivo `Proyecto Scrum Distribuidora Villali.xlsx`. La ventana del Excel es **30 de noviembre a 6 de diciembre de 2026**; la implementación y las pruebas aquí descritas se prepararon el **25 de noviembre de 2026**.

**DIAN y PSE funcionan mediante simuladores académicos**, elegidos por el usuario. Los documentos tienen consecutivos `FE-DEMO`, `NC-DEMO`, `RC-DEMO` y `LQ-DEMO`. No tienen validez fiscal ni mueven dinero. El envío de factura se registra en una bandeja simulada, sin afirmar que llegó un correo real.

## Documentación y pruebas

- **[Paso a paso para verificar Sprint 4](Guia_Verificacion_Sprint_4.md)**: acceso, roles, casos normales, errores y evidencias.
- [Historias y criterios](spec.md): correspondencia con AC-016.1 a AC-020.3.
- [Arquitectura y contrato](plan.md): MongoDB, transacciones, permisos, firma PSE y reportes.
- [Tareas T060–T078](tasks.md): responsables del Excel y evidencias de implementación.
- [Registro SDD y aceptación](Registro_SDD.md): resultados técnicos y decisiones que revisa el equipo.
- [CI Sprint 4](https://github.com/braescrus14-cloud/Distribuidora/actions/workflows/sprint-4.yml): SQLite, PostgreSQL y MongoDB de ensayo.

## Módulos por rol

| Rol | Módulos del Sprint 4 |
| --- | --- |
| 01 · Gerente General | Facturas en consulta y tablero gerencial con filtros, Excel, PDF y cortes conservados |
| 03 · Jefe de Bodega | Devoluciones, inspección, reingreso, merma y notas crédito |
| 07 · Coordinador de Logística | Liquidación de rutas, diferencias y acta PDF |
| 09 · Auxiliar Contable | Emisión y reenvío de facturas, bandeja simulada, pagos y cartera por edades |
| 10 · Cliente | Solo sus facturas, documentos y pagos PSE de prueba |

Los demás roles conservan sus funciones de los Sprints 1–3. El administrador de cuentas no obtiene permisos contables por ser administrador.

## Aplicación y versiones

[Abrir Villali](https://villali-staging.onrender.com/) · [Ingresar](https://villali-staging.onrender.com/entrar) · [Comprobar versión publicada](https://villali-staging.onrender.com/version).

`main/proyecto-completo` sigue siendo la carpeta integrada usada por Render. Se conserva el servicio gratuito y la misma base MongoDB Atlas. El incremento incorpora registros financieros a la estructura existente; no vacía ni vuelve a sembrar la base.

La versión previa está preservada en **[sprint-3](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-3)**, commit `d07c5673968e4e9ea883d1564d354ee920e5346d`. [Informe de Sprint 3](../sprint-3/Informe_Consolidado_Sprint_3.md) · [Copias y restauración](../sprint-3/Copias_y_Restauracion.md) · [Entrega de los cuatro sprints](../../proyecto-completo/documentacion/Entrega_Proyecto.md).
