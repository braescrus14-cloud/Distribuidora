# Registro de aprobaciones SDD del Sprint 1

**Proyecto** · Plataforma Villali  
**Periodo reprogramado** · 2 al 8 de noviembre de 2026  
**Presentación académica** · 9 de noviembre de 2026  
**Alcance** · HU-01 a HU-05  
**Estado** · Incremento desplegado para la demostración académica. Aprobación formal pendiente de confirmación.

La revisión del **6 de noviembre** y el cierre del **8 de noviembre** se documentaron como ejercicio académico. El acta contiene las decisiones simuladas de las cuatro puertas y las cinco historias. [Acta simulada de cierre](Acta_Simulada_Cierre_Sprint_1_Villali.md)

## Evidencias del incremento

| Historia | Evidencia registrada | Validación pendiente |
| --- | --- | --- |
| HU-01 · Acceso | Inicio y cierre de sesión, vencimiento, bloqueo por intentos y auditoría. La alerta de bloqueo pasó la prueba con correo simulado. | Confirmar la recepción de la alerta en staging. |
| HU-02 · Usuarios y roles | Administración de cuentas y permisos. La invitación y la activación se probaron con correo simulado. | Verificar la matriz completa de permisos y recibir una invitación real. |
| HU-03 · Catálogo | Se confirmó la carga de **104 productos** en Render. El catálogo incorpora **91 referencias** del Excel actualizado y referencias adicionales de la base local. | Validar códigos, empaques y precios con Villali. |
| HU-04 · Carga de inventario | Se confirmó la carga de **dos lotes de Ital Huevo**, con **50 y 75 unidades** para un total de **125**, mediante el Excel de demostración. | Conciliar la carga con el inventario real de bodega. |
| HU-05 · Consulta por lote | Consulta por nombre o código y detalle por lote con cantidad, ubicación y vencimiento. La cámara funciona en modo demostración. | Validar el escaneo con el dispositivo de bodega. |

## CI y despliegue

- **CI en verde.** El flujo `CI Sprint 1 #3` pasó para el commit `17e5f09` de `main`. [Ejecución de GitHub Actions](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/42563294259)
- **Staging desplegado.** Se verificaron el acceso público por HTTPS y la respuesta HTTP 200 de `/health`. El entorno usa el plan gratuito de Render. [Villali en Render](https://villali-staging.onrender.com/)

## Puertas SDD

| Puerta | Fecha del ejercicio | Estado formal | Evidencia para revisión |
| --- | --- | --- | --- |
| 0 · Constitución | 02/11/2026 | Por confirmar | [Principios de trabajo y alcance](Sprint_1_Villali.md) |
| 1 · Especificación | 04/11/2026 | Por confirmar | [Historias y criterios de aceptación](Sprint_1_Villali.md) |
| 2 · Plan técnico | 05/11/2026 | Por confirmar | [Decisión de arquitectura para staging](ADR_Sprint_1_Arquitectura_Staging.md) |
| 3 · Tareas | 05/11/2026 | Por confirmar | [Veinte tareas con responsables, dependencias y trazabilidad](Sprint_1_Villali.md) |

## Aceptación de historias

La revisión simulada del **06/11/2026** registra HU-01 a HU-05 como **aceptadas para demostración académica**. Para el cierre formal, la Product Owner debe registrar su decisión, fecha y evidencia para cada historia. [Detalle de aceptación por historia](Acta_Simulada_Cierre_Sprint_1_Villali.md#aceptación-simulada-en-la-sprint-review)
