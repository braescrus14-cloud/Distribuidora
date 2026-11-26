# Cómo confirmar el Sprint 2

**Alcance: HU-06–HU-10.** Usar la [guía paso a paso](Guia_Verificacion_Sprint_2.md) y cuentas activas de los roles indicados. Registrar una fila por caso probado con **Aprobada / Falló / No ejecutada**, evidencia, responsable y fecha real.

## 1. Comprobar la publicación

- [ ] El commit de GitHub coincide con el commit Live de Render y `/version`.
- [ ] [CI Sprint 2](https://github.com/braescrus14-cloud/Distribuidora/actions/workflows/sprint-2.yml) está en verde para ese commit.
- [ ] `/health` responde correctamente y se conservan los datos de ensayo esperados.
- [ ] Las cuentas utilizadas tienen los roles correctos; no se publican contraseñas ni secretos.

La aplicación se ejecuta desde `proyecto-completo`. [Ajuste de carpeta en Render](../../proyecto-completo/documentacion/Despliegue_Render.md).

## 2. Verificar las cinco historias

| Historia | Rol | Resultado esperado | Resultado y evidencia | Responsable / fecha |
| --- | --- | --- | --- | --- |
| HU-06 | Compras 05 | Proveedor con NIT válido y productos asociados; inactivo fuera de nuevas compras. | Por registrar | Por registrar |
| HU-07 | Compras 05 / Gerencia 01 / Bodega 03–04 | Compra sobre $10 millones exige aprobación; recepción parcial suma el lote; vencimiento insuficiente rechazado. | Por registrar | Por registrar |
| HU-08 | Asesor 06 / Gerencia 01 | Ficha y cuenta de cliente vinculadas; cupo/cartera restringidos al rol correspondiente. | Por registrar | Por registrar |
| HU-09 | Asesor 06 | Pedido confirmado reserva unidades; faltante, cupo excedido y mora rechazan sin reserva extra. | Por registrar | Por registrar |
| HU-10 | Cliente 10 | Ve su ficha y pedidos; solicitud queda por revisar; otro cliente no accede. | Por registrar | Por registrar |

## 3. Confirmar las cuatro puertas SDD

| Puerta | Comprobación para el equipo | Decisión, responsable y fecha |
| --- | --- | --- |
| 0 · Constitución | Principios, responsabilidades, trazabilidad y alcance acordados | Por registrar |
| 1 · Especificación | Cinco historias y criterios revisados; adaptaciones académicas explícitas | Por registrar |
| 2 · Plan | Arquitectura, permisos, persistencia y contratos revisados | Por registrar |
| 3 · Tareas | Tareas y evidencias revisadas y registradas en Sprint Tools | Por registrar |

## 4. Registrar la aceptación

- [ ] Hay un resultado y evidencia por cada historia, incluidos los errores esperados.
- [ ] Las condiciones o fallos quedaron descritos con responsable de solución.
- [ ] La Product Owner registró Aceptada / Aceptada con condiciones / No aceptada, con fecha y evidencia.
- [ ] Las decisiones SDD están ratificadas por las personas responsables.

Las CI verifican casos técnicos; la aceptación del sprint requiere esa revisión del equipo. No atribuir aprobaciones a compañeros sin su confirmación.

[Expediente](README.md) · [Código del cierre histórico](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-2) · [Todos los sprints](../README.md).
