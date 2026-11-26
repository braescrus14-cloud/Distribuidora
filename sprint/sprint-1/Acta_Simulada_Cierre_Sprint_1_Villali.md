# Acta simulada de cierre del Sprint 1 de Villali

**Periodo reprogramado** · 2 al 8 de noviembre de 2026  
**Revisión simulada** · 6 de noviembre de 2026  
**Cierre simulado** · 8 de noviembre de 2026  
**Presentación académica** · 9 de noviembre de 2026

> Ejercicio académico. Las decisiones y fechas de aprobación corresponden a una simulación que adelanta siete días el cronograma del taller. Las evidencias técnicas se adjuntan para la presentación y conservan sus fechas de origen.

El equipo revisó el acceso por roles, el catálogo, la carga inicial desde Excel y la consulta de existencias por lote y vencimiento. En el escenario simulado, el equipo acepta el incremento para demostración académica y registra las validaciones operativas pendientes.

## Decisiones SDD simuladas

| Puerta | Fecha | Responsable por rol | Decisión del escenario |
| --- | --- | --- | --- |
| 0 · Constitución | 02/11/2026 | Product Owner y equipo | Ratificada. El sprint se limita a HU-01 a HU-05 y requiere evidencia para su revisión. |
| 1 · Especificación | 04/11/2026 | Product Owner y equipo | Aprobada la especificación para la revisión académica. Se registra el alcance de la demostración de escaneo y correo. |
| 2 · Plan técnico | 05/11/2026 | Equipo de desarrollo y Product Owner | Aceptada la arquitectura implementada para staging de demostración, con frontend HTML, CSS y JavaScript, API Python y SQLite. Se registra la limitación de persistencia del plan gratuito de Render. |
| 3 · Tareas | 05/11/2026 | Scrum Master y equipo | Revisadas las 20 tareas del plan y su relación con las cinco historias. Las evidencias se consultan en el repositorio y en el registro SDD. |

## Aceptación simulada en la Sprint Review

| Historia | Decisión simulada | Fecha | Evidencia y alcance |
| --- | --- | --- | --- |
| HU-01 · Acceso | Aceptada para demostración | 06/11/2026 | Inicio y cierre de sesión, bloqueo y auditoría. El aviso por correo tiene prueba simulada. |
| HU-02 · Usuarios y roles | Aceptada para demostración | 06/11/2026 | Gestión de cuentas, permisos e invitación por enlace. El envío por correo tiene prueba simulada. |
| HU-03 · Catálogo | Aceptada para demostración | 06/11/2026 | Catálogo con SKU internos y precios de referencia. |
| HU-04 · Carga inicial | Aceptada para demostración | 06/11/2026 | Carga desde Excel con validación previa y registro en auditoría. |
| HU-05 · Consulta de inventario | Aceptada para demostración | 06/11/2026 | Consulta por código o nombre y detalle de lotes con cantidad, ubicación y vencimiento. La cámara funciona en modo demostración. |

## Evidencias y pendientes registrados

- El flujo de integración continua pasó para el commit `17e5f09`. [Ejecución de GitHub Actions](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/42563294259)
- Se verificó el acceso público por HTTPS al entorno de demostración y la respuesta satisfactoria de `/health`. [Villali en Render](https://villali-staging.onrender.com/)
- Para la presentación, el usuario confirmó la carga en Render de 104 productos y dos lotes de Ital Huevo, con 50 y 75 unidades para un total de 125.
- El cierre simulado deja registrados tres pendientes operativos: conciliar las existencias reales de bodega, confirmar la entrega de los correos y validar el escaneo con el dispositivo de trabajo.
- Las decisiones que el equipo confirme durante su revisión se consignan con responsable, fecha y evidencia en el registro oficial. [Registro de aprobaciones SDD](Registro_Aprobaciones_SDD_Sprint_1.md)
