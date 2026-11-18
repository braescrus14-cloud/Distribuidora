# Registro de Aprobaciones y Ejecución SDD del Sprint 1

**Proyecto:** Plataforma Web de Distribución y Venta Villali  
**Periodo del Sprint 1:** 2 al 8 de noviembre de 2026  
**Fecha de Sustentación Académica:** 9 de noviembre de 2026  
**Alcance:** Historias de Usuario HU-01 a HU-05 (21 Story Points)  
**Estado:** **Completado y Aprobado al 100%**. Incremento desplegado en Staging con CI en verde.

---

## 1. Verificación y Aprobación Formal de Puertas SDD

| Puerta SDD | Fecha de Aprobación | Responsable por Rol | Decisión Formal | Evidencia Registrada |
| :--- | :---: | :--- | :---: | :--- |
| **Puerta 0 · Constitución** | 02/11/2026 | Product Owner y Equipo | **Aprobada** | Principios innegociables, gobernanza y alcance acotado a HU-01 a HU-05. [Ver Constitución](Sprint_1_Villali.md#constitución-para-la-revisión-inicial) |
| **Puerta 1 · Especificación** | 04/11/2026 | Product Owner y Equipo | **Aprobada** | Requisitos EARS (REQ-VIL-001 a 010), reglas de negocio (RN-01 a 14) y escenarios BDD (AC-001.1 a 005.3). [Ver Especificación](Sprint_1_Villali.md#especificación-funcional) |
| **Puerta 2 · Plan Técnico** | 05/11/2026 | Equipo de Desarrollo | **Aprobada** | Monolito modular, decisiones arquitectónicas ADR, endpoints OpenAPI y estrategia de despliegue dual. [Ver ADR Staging](ADR_Sprint_1_Arquitectura_Staging.md) |
| **Puerta 3 · Desglose de Tareas** | 05/11/2026 | Scrum Master y Desarrolladores | **Aprobada** | 20 tareas técnicas (T001 a T020) estimadas en 76.5 horas, con dependencias y estrategia Test-First en Kanban. [Ver Backlog](Sprint_1_Villali.md#tareas-para-sprint-tools) |

---

## 2. Registro Cronológico de Ejecución de Tareas Técnicas (T001 a T020)

Cronograma de realización diaria durante la semana del Sprint (2 al 8 de noviembre de 2026):

| ID | HU | Capa | Descripción del Trabajo Realizado | Responsable | Revisor | Fecha de Ejecución | Horas | Estado |
| :---: | :---: | :---: | :--- | :--- | :--- | :---: | :---: | :---: |
| **T001** | HU-01 | BD | Migración V1: esquemas de usuarios, sesiones y bitácora de auditoría. | Cristian Danilo Pineda | Cesar Johan Casado | **02/11/2026** | 3.0h | `Hecho` |
| **T005** | HU-02 | BD | Migración V2: catálogo y permisos de los 10 roles base (ROL-01 a ROL-10). | Cristian Danilo Pineda | Cesar Johan Casado | **02/11/2026** | 3.0h | `Hecho` |
| **T002** | HU-01 | Test | Pruebas de autenticación, hash de contraseñas, bloqueo temporal y expiración. | Brayan Esteban Cruz | Cesar Johan Casado | **03/11/2026** | 3.0h | `Hecho` |
| **T006** | HU-02 | Test | Pruebas de la matriz RBAC de permisos por rol y denegación HTTP 403. | Brayan Esteban Cruz | Cesar Johan Casado | **03/11/2026** | 4.0h | `Hecho` |
| **T009** | HU-03 | BD | Migración V3: modelo maestro de productos, marcas, especies y stock mínimo. | Cristian Danilo Pineda | Cesar Johan Casado | **03/11/2026** | 2.5h | `Hecho` |
| **T010** | HU-03 | Test | Pruebas de unicidad de código SKU y código de barras EAN-13. | Brayan Esteban Cruz | Cesar Johan Casado | **03/11/2026** | 2.5h | `Hecho` |
| **T003** | HU-01 | Backend | Servicio de autenticación segura, control de 5 intentos fallidos y timeout. | Cesar Johan Casado | Brayan Esteban Cruz | **04/11/2026** | 5.0h | `Hecho` |
| **T007** | HU-02 | Backend | API de gestión de usuarios, asignación de roles y desactivación lógica. | Cesar Johan Casado | Brayan Esteban Cruz | **04/11/2026** | 6.0h | `Hecho` |
| **T011** | HU-03 | Backend | API CRUD de productos con validaciones de catálogo y filtros de búsqueda. | Cesar Johan Casado | Brayan Esteban Cruz | **04/11/2026** | 4.0h | `Hecho` |
| **T004** | HU-01 | Frontend | Pantalla de inicio de sesión responsive y cierre por inactividad según equipo. | Cristian Danilo Pineda | Cesar Johan Casado | **05/11/2026** | 4.0h | `Hecho` |
| **T008** | HU-02 | Frontend | Módulo de administración de usuarios y menú dinámico por rol. | Cristian Danilo Pineda | Cesar Johan Casado | **05/11/2026** | 5.0h | `Hecho` |
| **T012** | HU-03 | Frontend | Pantalla de catálogo maestro con filtros por especie, marca y stock. | Cristian Danilo Pineda | Cesar Johan Casado | **05/11/2026** | 4.0h | `Hecho` |
| **T013** | HU-04 | BD | Migración V4: modelo de lotes, existencias físicas/reservadas y movimientos. | Cristian Danilo Pineda | Cesar Johan Casado | **05/11/2026** | 3.0h | `Hecho` |
| **T014** | HU-04 | Test | Pruebas de carga Excel con archivos válidos y rollback total ante fallos. | Brayan Esteban Cruz | Cesar Johan Casado | **05/11/2026** | 3.0h | `Hecho` |
| **T015** | HU-04 | Backend | Motor de importación atómica desde Excel con validación estricta y rollback. | Cesar Johan Casado | Brayan Esteban Cruz | **06/11/2026** | 6.0h | `Hecho` |
| **T016** | HU-04 | Frontend | Asistente de carga de inventario con vista previa y reporte de errores por fila. | Cristian Danilo Pineda | Cesar Johan Casado | **06/11/2026** | 4.0h | `Hecho` |
| **T017** | HU-05 | BD | Vista de saldo disponible por lote (Físico - Reservado) e índice de vencimiento. | Cristian Danilo Pineda | Cesar Johan Casado | **06/11/2026** | 2.5h | `Hecho` |
| **T018** | HU-05 | Test | Pruebas del semáforo FEFO (Rojo ≤30d, Amarillo 31-60d, Verde >60d) y reservas. | Brayan Esteban Cruz | Cesar Johan Casado | **06/11/2026** | 3.0h | `Hecho` |
| **T019** | HU-05 | Backend | Endpoint GET para consulta por código escaneado con ordenamiento FEFO. | Cesar Johan Casado | Brayan Esteban Cruz | **06/11/2026** | 4.0h | `Hecho` |
| **T020** | HU-05 | Frontend | Pantalla de escáner para tablet (PWA) con detección de barras/QR y semáforo. | Cristian Danilo Pineda | Brayan Esteban Cruz | **06/11/2026** | 5.0h | `Hecho` |

**Total de horas ejecutadas:** 76.5 horas de desarrollo técnico y testing completadas.

---

## 3. Criterios de Aceptación y Salida del Sprint (DoD)

| Criterio de Salida | Estado | Evidencia Comprobada |
| :--- | :---: | :--- |
| **Puertas 0, 1, 2 y 3 aprobadas y en acta** | **Aprobado** | Documentos formales ratificados y versionados en el repositorio (`docs/sprint-1/`). |
| **HU-01 a HU-05 cumplen Definition of Done** | **Aprobado** | Pruebas automatizadas en verde; revisión cruzada entre pares completada. |
| **Inventario migrado cuadra al 100% con Excel** | **Aprobado** | Carga de 104 productos de catálogo y 125 unidades de Ital Huevo en lotes iniciales. |
| **Incremento desplegado en Staging con CI en verde** | **Aprobado** | Build exitoso en GitHub Actions y aplicación operativa en [Render Staging](https://villali-staging.onrender.com/). |

---

## 4. Enlaces de Acceso y Credenciales de Demostración

* **URL Pública de Staging:** [https://villali-staging.onrender.com/](https://villali-staging.onrender.com/)
* **Contraseña General de Demostración:** `Villali!573e5f54d57`
* **Repositorio Oficial de Código:** [https://github.com/braescrus14-cloud/Distribuidora.git](https://github.com/braescrus14-cloud/Distribuidora.git)
* **Verificación de Salud (Healthcheck HTTP 200):** [https://villali-staging.onrender.com/health](https://villali-staging.onrender.com/health)
