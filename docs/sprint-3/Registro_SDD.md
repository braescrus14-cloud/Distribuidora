# Registro SDD · Sprint 3

**Fecha de preparación:** 20 de noviembre de 2026. **Alcance:** HU-11 a HU-15 y portada/experiencia por rol solicitadas para la revisión. **Ventana de referencia del Excel:** 23–29 de noviembre de 2026; cualquier reprogramación debe confirmarla el equipo.

La implementación y las pruebas son evidencias técnicas. Las decisiones siguientes se completan cuando sus responsables revisen y confirmen; no se registran firmas ni aceptaciones por terceros.

| Puerta | Evidencia disponible | Decisión | Responsable / fecha |
| --- | --- | --- | --- |
| 0 · Constitución | Respaldo de Sprints 1–2, conservación de MongoDB, privacidad y trazabilidad de commits | Pendiente de ratificación | Por registrar |
| 1 · Especificación | [Historias, criterios y límites](spec.md) | Pendiente de aprobación | Product Owner / por registrar |
| 2 · Plan | [Arquitectura y contrato](plan.md); adaptación de migraciones relacionales a MongoDB y límites del mapa/ETA | Pendiente de decisión técnica | Responsable técnico / por registrar |
| 3 · Tareas | [T041–T059](tasks.md), código y [guía de pruebas](Pruebas_y_Demostracion.md) | Pendiente de revisión cruzada y registro en Sprint Tools | Equipo / por registrar |

## Aceptación del incremento

| Historia | Evidencia implementada | Decisión de aceptación | Fecha / responsable |
| --- | --- | --- | --- |
| HU-11 | Alistamiento FEFO, comprobación EAN, descuento físico atómico | Pendiente de demostración y aceptación | Por registrar |
| HU-12 | Capacidad, conductor único, zonas, secuencia y mapa | Pendiente de validar destinos y pesos | Por registrar |
| HU-13 | Rótulo QR, cargue y manifiesto PDF | Pendiente de probar lector y despacho en staging | Por registrar |
| HU-14 | Firma/foto/GPS, novedad, retorno y cola offline | Pendiente de prueba en teléfono y staging | Por registrar |
| HU-15 | Línea de tiempo, ETA estimada y aislamiento del cliente | Pendiente de revisión funcional | Por registrar |

## Evidencias de entrega

Las tres suites de integración finalizaron correctamente para el commit `e65a60c` el 20 de noviembre de 2026, con SQLite, PostgreSQL y MongoDB de ensayo: [Sprint 1](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/44851442645), [Sprint 2](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/44851442667) y [Sprint 3](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/44851442701). Para revisiones posteriores consultar también la CI del commit final.

- [Respaldo de la versión anterior](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-2-archivo): commit `bd7e69b83c5ef8bee8c1df1b333d4e7fa7511db4`.
- [Código integrado](https://github.com/braescrus14-cloud/Distribuidora/tree/main/sprint-1) y [CI del Sprint 3](https://github.com/braescrus14-cloud/Distribuidora/actions/workflows/sprint-3.yml).
- [Aplicación en Render](https://villali-staging.onrender.com/): despliegue del incremento verificado mediante la comprobación pública indicada a continuación. La aceptación funcional corresponde a los responsables.

### Verificación del despliegue · 20 de noviembre de 2026

El usuario confirmó el estado **Live** después de desplegar la última versión. Versión de aplicación: [`a23453847a09d8f7cadb8c62761e79b1e29a0abc`](https://github.com/braescrus14-cloud/Distribuidora/commit/a23453847a09d8f7cadb8c62761e79b1e29a0abc).

- Las CI del commit final terminaron satisfactoriamente: [Sprint 1](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/44851733856), [Sprint 2](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/44851733861) y [Sprint 3](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/44851733858).
- `/health` devolvió HTTP 200 y `{"status":"ok"}`; la comprobación incluye una lectura del almacenamiento configurado.
- `/` mostró la portada «El campo nos mueve»; `/entrar` mostró el acceso «Villali | Mi espacio» con los recursos del Sprint 3.
- `/logistics.js`, `/farm.jpg` y `/manifest.webmanifest` respondieron HTTP 200. La portada, el acceso, el módulo JavaScript logístico y la fotografía coincidieron por SHA-256 con los archivos de la versión publicada.

Esta comprobación pública no inició sesión ni creó pedidos o entregas en Atlas. Queda completar el recorrido autenticado por roles y las pruebas de lector, cámara y GPS en los dispositivos del equipo, además de las decisiones de aceptación de las historias.

Para cerrar: anexar commit, ejecución de CI, fecha del despliegue, resultados reales, responsables de revisión y decisión de Product Owner. El tablero Sprint Tools se actualiza con esas evidencias; estos documentos no prueban que el tablero haya sido actualizado.
