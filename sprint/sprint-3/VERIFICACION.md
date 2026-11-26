# Cómo confirmar el Sprint 3

**Alcance: HU-11–HU-15.** Usar la [guía paso a paso](Guia_Verificacion_Sprint_3.md) y cuentas activas de los roles indicados. Registrar una fila por caso probado con **Aprobada / Falló / No ejecutada**, evidencia, responsable y fecha real.

## 1. Comprobar la publicación

- [ ] El commit de GitHub coincide con el commit Live de Render y `/version`.
- [ ] [CI Sprint 3](https://github.com/braescrus14-cloud/Distribuidora/actions/workflows/sprint-3.yml) está en verde para ese commit.
- [ ] `/health` responde correctamente y se conservan los datos de ensayo esperados.
- [ ] Las cuentas utilizadas tienen los roles correctos; no se publican contraseñas ni secretos.

La aplicación se ejecuta desde `proyecto-completo`. [Ajuste de carpeta en Render](../../proyecto-completo/documentacion/Despliegue_Render.md).

## 2. Verificar las cinco historias

| Historia | Rol | Resultado esperado | Resultado y evidencia | Responsable / fecha |
| --- | --- | --- | --- | --- |
| HU-11 | Auxiliar 04 / Bodega 03 | FEFO y EAN correcto; alistamiento descuenta una vez y produce rótulo QR. | Por registrar | Por registrar |
| HU-12 | Logística 07 | Capacidad y asignación válidas; ruta con pedidos alistados y orden de visitas. | Por registrar | Por registrar |
| HU-13 | Bodega 03 | Rótulo ajeno rechazado; cargue completo permite manifiesto y despacho. | Por registrar | Por registrar |
| HU-14 | Conductor 08 / Bodega 03 | Firma/foto/GPS y novedad; cola offline persiste y sincroniza sin duplicar. | Por registrar | Por registrar |
| HU-15 | Cliente 10 | Seguimiento propio con estados/ETA aproximada; pedido ajeno y evidencias privadas protegidos. | Por registrar | Por registrar |

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

[Registro SDD del sprint](Registro_SDD.md) · [Expediente](README.md) · [Código del cierre histórico](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-3) · [Todos los sprints](../README.md).
