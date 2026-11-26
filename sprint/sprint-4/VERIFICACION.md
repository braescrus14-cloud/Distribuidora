# Cómo confirmar el Sprint 4

**Alcance: HU-16–HU-20.** Usar la [guía paso a paso](Guia_Verificacion_Sprint_4.md) y cuentas activas de los roles indicados. Registrar una fila por caso probado con **Aprobada / Falló / No ejecutada**, evidencia, responsable y fecha real.

## 1. Comprobar la publicación

- [ ] El commit de GitHub coincide con el commit Live de Render y `/version`.
- [ ] [CI Sprint 4](https://github.com/braescrus14-cloud/Distribuidora/actions/workflows/sprint-4.yml) está en verde para ese commit.
- [ ] `/health` responde correctamente y se conservan los datos de ensayo esperados.
- [ ] Las cuentas utilizadas tienen los roles correctos; no se publican contraseñas ni secretos.

La aplicación se ejecuta desde `proyecto-completo`. [Ajuste de carpeta en Render](../../proyecto-completo/documentacion/Despliegue_Render.md).

## 2. Verificar las cinco historias

| Historia | Rol | Resultado esperado | Resultado y evidencia | Responsable / fecha |
| --- | --- | --- | --- | --- |
| HU-16 | Contabilidad 09 | Factura por lo entregado, PDF/XML académicos, rechazo con motivo y reenvío conservando consecutivo. | Por registrar | Por registrar |
| HU-17 | Contabilidad 09 / Cliente 10 | Abono cambia saldo; sobrepago rechazado; PSE firmado cancela saldo sin cobro real. | Por registrar | Por registrar |
| HU-18 | Logística 07 | Ruta liquidada aplica recaudo una vez; diferencia exige acta y conserva faltante/sobrante. | Por registrar | Por registrar |
| HU-19 | Gerencia 01 | Filtros y comparación correctos; mínimo 20/disponible 8 da faltante 12; Excel/PDF y corte coinciden. | Por registrar | Por registrar |
| HU-20 | Bodega 03 | Íntegro repone lote, avería no aumenta stock, nota crédito concilia y pago final cierra el pedido. | Por registrar | Por registrar |

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

[Registro SDD del sprint](Registro_SDD.md) · [Expediente](README.md) · [Código del cierre histórico](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-4) · [Todos los sprints](../README.md).
