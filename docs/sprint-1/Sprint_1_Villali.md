# Sprint 1 de la plataforma Villali

**Periodo planificado** · 9 al 15 de noviembre de 2026\
**Estado** · Borrador para revisión del equipo y la Product Owner\
**Alcance** · HU-01 a HU-05, 21 puntos de historia

El incremento permite iniciar sesión con un rol, gestionar usuarios y catálogo, importar
el inventario inicial y consultar el saldo por lote, ubicación y vencimiento desde bodega.
Compras, pedidos, logística, facturación y recaudo corresponden a sprints posteriores.
Los escenarios que mencionan pedidos o facturación se verifican con datos de prueba
o con pruebas de autorización, sin implementar esos módulos en el Sprint 1.

## Constitución para la revisión inicial

- Aprobar los criterios de aceptación antes de desarrollar una funcionalidad.
- Escribir primero las pruebas. Cada cambio de código se vincula con una tarjeta T### y tiene revisión cruzada.
- Usar un monolito modular y documentar las nuevas dependencias mediante decisiones de arquitectura.
- Aplicar mínimo privilegio en el servidor. Configurar secretos fuera del código y usar datos sintéticos en las pruebas.
- Auditar el acceso, las denegaciones de permisos y los movimientos de inventario. Aplicar los requisitos de privacidad del taller.

## Especificación funcional


### HU-01 · Autenticación segura y control de sesión

**Prioridad y estimación** · 3 SP · Must\
**Rol** · ROL-02 · Administrador del Sistema\
**Responsable** · Cesar Johan Casado Calderon

La historia busca que cada usuario ingrese con credenciales personales y que las sesiones inactivas se cierren solas para proteger la información comercial de Villali y cumplir la Ley 1581 de 2012.

**Precondiciones**\
Existe un usuario administrador creado por el script inicial (seed). Los 10 roles base están cargados en la base de datos. El entorno publica la aplicación solo por HTTPS.

**Reglas de negocio**

- RN-01: La contraseña tiene mínimo 10 caracteres con mayúscula, número y símbolo. (Seguridad TI)
- RN-02: Tras 5 intentos fallidos consecutivos la cuenta se bloquea 15 minutos. (Seguridad TI)
- RN-03: La sesión expira tras 15 minutos de inactividad en tablet/móvil y 30 minutos en escritorio.  (Gerencia)

**Requisitos EARS**

- REQ-VIL-001 [Evento]: Cuando un usuario envía credenciales válidas, el sistema deberá emitir un token de acceso con su rol y registrar el ingreso en la bitácora de auditoría.
- REQ-VIL-002 [No deseado]: Si un usuario acumula 5 intentos fallidos consecutivos, entonces el sistema deberá bloquear la cuenta 15 minutos y notificar al Administrador del Sistema.

**Criterios de aceptación**

- AC-001.1: Dado que el usuario “aux.bodega01” está activo y su contraseña es correcta, cuando ingresa usuario y contraseña en la pantalla de inicio, entonces accede a la plataforma, ve solo el menú de su rol y el ingreso queda registrado con fecha, hora e IP.
- AC-001.2: Dado que un usuario ya falló 4 intentos consecutivos, cuando ingresa una contraseña incorrecta por quinta vez, entonces la cuenta queda bloqueada 15 minutos y se muestra “Cuenta bloqueada temporalmente”.
- AC-001.3 (borde): Dado que una sesión en tablet lleva 15 minutos sin actividad, cuando el usuario intenta registrar una operación, entonces el sistema pide autenticarse de nuevo y no registra la operación.

### HU-02 · Gestión de usuarios y asignación de roles (RBAC)

**Prioridad y estimación** · 5 SP · Must\
**Rol** · ROL-02 · Administrador del Sistema\
**Responsable** · Cristian Danilo Pineda Ramirez

La historia busca crear usuarios, asignarles uno de los 10 roles de la plataforma y desactivarlos cuando dejen la empresa para que cada persona acceda solo a las funciones que su cargo requiere (mínimo privilegio).

**Precondiciones**\
HU-01 terminada: la autenticación funciona. La matriz de permisos por rol y módulo está aprobada en la spec (sección 2 de este documento).

**Reglas de negocio**

- RN-04: Cada usuario tiene exactamente un rol activo. (Gerencia)
- RN-05: Un usuario no se elimina: se desactiva, para conservar la trazabilidad de sus operaciones. (Auditoría / Ley 1581)
- RN-06: Solo el Administrador del Sistema asigna los roles Gerente General y Administrador del Sistema.  (Seguridad TI)

**Requisitos EARS**

- REQ-VIL-003 [Estado]: Mientras un usuario esté desactivado, el sistema deberá rechazar su autenticación y conservar su historial de operaciones.
- REQ-VIL-004 [No deseado]: Si un usuario intenta acceder a una pantalla o API no autorizada para su rol, entonces el sistema deberá responder 403 y registrar el intento.

**Criterios de aceptación**

- AC-002.1: Dado que el Administrador está en el módulo “Usuarios”, cuando crea a “Laura Gómez” con el rol Asesor Comercial, entonces el usuario queda activo, recibe un correo para definir su contraseña y solo ve Clientes, Pedidos y Catálogo (consulta).
- AC-002.2: Dado que un Auxiliar de Bodega está autenticado, cuando intenta abrir el módulo de Facturación por URL directa, entonces el sistema responde “Acceso denegado” (403) y registra el intento en auditoría.
- AC-002.3: Dado que el usuario “vend03” fue desactivado, cuando intenta iniciar sesión, entonces el acceso se rechaza y sus pedidos históricos siguen visibles con su nombre.

### HU-03 · Gestión del catálogo de productos

**Prioridad y estimación** · 3 SP · Must\
**Rol** · ROL-03 · Jefe de Bodega\
**Responsable** · Brayan Esteban Cruz Arango

La historia busca registrar y mantener el catálogo de productos (marca, especie, presentación, código de barras, precio base y stock mínimo) para tener una única fuente de verdad que reemplace las hojas de cálculo.

**Precondiciones**\
Roles y permisos operativos (HU-02). Especies, marcas y unidades de medida parametrizadas.

**Reglas de negocio**

- RN-07: El SKU y el código de barras (EAN-13) son únicos. (Jefe de Bodega)
- RN-08: Todo producto tiene un stock mínimo (punto de reorden) mayor que cero. (Compras)
- RN-09: Un producto con movimientos no se elimina; se marca inactivo.  (Auditoría)

**Requisitos EARS**

- REQ-VIL-005 [Evento]: Cuando el Jefe de Bodega guarda un producto con datos completos, el sistema deberá crearlo activo y disponible para compras y ventas.
- REQ-VIL-006 [No deseado]: Si el código de barras ya pertenece a otro producto, entonces el sistema deberá rechazar el registro indicando qué producto lo usa.

**Criterios de aceptación**

- AC-003.1: Dado que no existe el SKU “CHK-CAC-15”, cuando el Jefe de Bodega registra “Chunky Cachorros 15 kg”, especie Caninos, EAN 7702001234567, precio $185.000 y stock mínimo 10, entonces el producto queda activo y aparece en el catálogo.
- AC-003.2: Dado que el EAN 7702001234567 ya está asignado a CHK-CAC-15, cuando se intenta registrar otro producto con ese código, entonces el sistema lo rechaza con “Código de barras ya registrado en CHK-CAC-15”.

### HU-04 · Carga inicial de inventario desde Excel

**Prioridad y estimación** · 5 SP · Must\
**Rol** · ROL-03 · Jefe de Bodega\
**Responsable** · Cesar Johan Casado Calderon

La historia busca importar el inventario inicial (productos, lotes, vencimientos y cantidades) desde las hojas de cálculo actuales para arrancar la operación con saldos reales sin digitarlos uno a uno.

**Precondiciones**\
Catálogo de productos cargado (HU-03). Plantilla Excel oficial publicada en la plataforma. Bodega y ubicaciones base creadas.

**Reglas de negocio**

- RN-10: La importación es todo o nada por archivo: si una fila falla, no se carga ninguna. (Jefe de Bodega)
- RN-11: Cada lote requiere número de lote y una fecha de vencimiento futura. (Calidad)
- RN-12: Hay una sola carga inicial por bodega; después solo se ajusta con movimientos auditados.  (Auditoría)

**Requisitos EARS**

- REQ-VIL-007 [Evento]: Cuando el Jefe de Bodega carga un archivo con la plantilla oficial, el sistema deberá validar todas las filas y mostrar un resumen antes de confirmar.
- REQ-VIL-008 [No deseado]: Si alguna fila tiene SKU inexistente, cantidad negativa o lote vencido, entonces el sistema deberá rechazar el archivo completo y entregar un reporte de errores por fila.

**Criterios de aceptación**

- AC-004.1: Dado que el archivo “inventario_inicial.xlsx” tiene 320 filas válidas, cuando el Jefe de Bodega confirma la importación, entonces se crean los 320 saldos por lote y se registra un movimiento auditado “CARGA_INICIAL”.
- AC-004.2: Dado que el archivo tiene 3 filas con SKU inexistente, cuando se valida el archivo, entonces no se carga ninguna fila y se descarga un reporte con las filas 14, 87 y 203 y su motivo.

### HU-05 · Consulta de inventario por lote y vencimiento con lector de códigos

**Prioridad y estimación** · 5 SP · Must\
**Rol** · ROL-04 · Auxiliar de Bodega\
**Responsable** · Cristian Danilo Pineda Ramirez

La historia busca escanear el código de barras de un producto con la tablet y ver su existencia por lote, ubicación y fecha de vencimiento para encontrar rápido la mercancía y detectar a tiempo los lotes próximos a vencer.

**Precondiciones**\
Inventario inicial cargado (HU-04). Tablet con cámara o lector autorizado. Usuario con rol Auxiliar de Bodega.

**Reglas de negocio**

- RN-13: Semáforo de vencimiento: rojo ≤ 30 días, amarillo 31–60 días, verde > 60 días. (Jefe de Bodega)
- RN-14: Saldo disponible = saldo físico − cantidades reservadas por pedidos.  (Comercial)

**Requisitos EARS**

- REQ-VIL-009 [Evento]: Cuando el auxiliar escanea un código registrado, el sistema deberá mostrar el saldo disponible por lote ordenado por fecha de vencimiento ascendente.
- REQ-VIL-010 [Estado]: Mientras un lote tenga 30 días o menos para vencer, el sistema deberá mostrarlo en rojo con la etiqueta “Próximo a vencer”.

**Criterios de aceptación**

- AC-005.1: Dado que “Chunky Cachorros 15 kg” tiene el lote L-101 (40 und, vence en 20 días) y el L-115 (60 und, vence en 150 días), cuando el auxiliar escanea su código, entonces ve primero L-101 en rojo y luego L-115 en verde, con un total disponible de 100.
- AC-005.2: Dado que el código escaneado no existe en el catálogo, cuando se procesa la lectura, entonces se muestra “Producto no registrado” y se ofrece buscar por nombre.
- AC-005.3: Dado que hay 10 unidades del lote L-101 reservadas por un pedido, cuando se consulta el producto, entonces el disponible de L-101 aparece como 30.

## Roles base

| ID | Rol | Categoría |
| --- | --- | --- |
| ROL-01 | Gerente General | Administrativo |
| ROL-02 | Administrador del Sistema | Sistema |
| ROL-03 | Jefe de Bodega | Operativo (supervisión) |
| ROL-04 | Auxiliar de Bodega | Operativo |
| ROL-05 | Coordinador de Compras | Administrativo |
| ROL-06 | Asesor Comercial | Comercial |
| ROL-07 | Coordinador de Logística y Despachos | Operativo (supervisión) |
| ROL-08 | Conductor / Repartidor | Operativo (campo) |
| ROL-09 | Auxiliar Contable y de Facturación | Administrativo |
| ROL-10 | Cliente (mayorista o minorista) | Externo / comercial |

El administrador gestiona usuarios. El jefe de bodega modifica el catálogo y confirma
la carga inicial. El auxiliar de bodega consulta existencias. El catálogo se expone
en modo de consulta según la matriz de permisos del taller. Las autorizaciones se
prueban por rol en el backend, incluso si la interfaz oculta el módulo.

## Plan técnico

1. Preparar el repositorio con Java 21, Spring Boot 3, PostgreSQL 16 y Flyway.
   Organizar el monolito por módulos de identidad, catálogo e inventario. Usar React 18,
   TypeScript y Vite para la interfaz adaptable y OpenAPI 3 para el contrato HTTP.
2. Crear las migraciones V1–V4, la vista de disponibilidad y el usuario inicial mediante
   configuración de entorno. Incorporar pruebas de autenticación, roles y catálogo.
3. Validar el Excel con Apache POI antes de confirmar. La confirmación revalida el archivo,
   escribe saldos y movimientos en una única transacción y protege contra dos cargas
   simultáneas para la misma bodega. Comparar cantidad y claves por SKU, lote y ubicación.
4. Integrar búsqueda manual, lector y cámara. Probar la consulta por código
   con el orden de vencimiento, el semáforo y los saldos disponibles.
5. Ejecutar las pruebas de backend con JUnit 5 y PostgreSQL mediante Testcontainers,
   y las de interfaz con Vitest. Tras CI en verde, usar Render para el staging
   solicitado, con PostgreSQL, HTTPS, variables de entorno y datos de prueba.

## Tareas para Sprint Tools

Usar los IDs del Excel para crear las tarjetas y conservar el responsable, el revisor
y las dependencias. La marca [P] identifica tareas que pueden prepararse en paralelo.
El estado inicial de este backlog es **To Do**. El Excel etiqueta las tareas como Done,
mientras el plan indica Por empezar. La finalización se verificará con el repositorio,
las pruebas y las revisiones.

| ID | HU | Capa | Trabajo | Referencia | Responsable | Revisor | Dependencias | Horas |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T001 | HU-01 | BD | Migración V1: tablas usuario, rol y bitácora de acceso | REQ-VIL-001 | Cristian Danilo Pineda Ramirez | Cesar Johan Casado Calderon | — | 3 |
| T002 [P] | HU-01 | Testing | Pruebas de autenticación, bloqueo y expiración | AC-001.1 a 001.3 | Brayan Esteban Cruz Arango | Cesar Johan Casado Calderon | — | 3 |
| T003 | HU-01 | Backend | Servicio de autenticación JWT con BCrypt, bloqueo por intentos y expiración | REQ-VIL-001, 002 | Cesar Johan Casado Calderon | Brayan Esteban Cruz Arango | T001, T002 | 5 |
| T004 | HU-01 | Frontend | Pantalla de inicio de sesión responsive y cierre por inactividad | AC-001.1, 001.3 | Cristian Danilo Pineda Ramirez | Cesar Johan Casado Calderon | T003 | 4 |
| T005 | HU-02 | BD | Migración V2: permisos por rol y carga de los 10 roles | REQ-VIL-003 | Cristian Danilo Pineda Ramirez | Cesar Johan Casado Calderon | — | 3 |
| T006 [P] | HU-02 | Testing | Pruebas de la matriz de permisos por rol | AC-002.1 a 002.3 | Brayan Esteban Cruz Arango | Cesar Johan Casado Calderon | — | 4 |
| T007 | HU-02 | Backend | API de usuarios y filtro de autorización por rol | REQ-VIL-003, 004 | Cesar Johan Casado Calderon | Brayan Esteban Cruz Arango | T005, T006 | 6 |
| T008 | HU-02 | Frontend | Módulo de administración de usuarios y menú dinámico por rol | AC-002.1 | Cristian Danilo Pineda Ramirez | Cesar Johan Casado Calderon | T007 | 5 |
| T009 | HU-03 | BD | Migración V3: producto, especie, marca y unidad | REQ-VIL-005 | Cristian Danilo Pineda Ramirez | Cesar Johan Casado Calderon | — | 2.5 |
| T010 [P] | HU-03 | Testing | Pruebas de unicidad y validaciones de producto | AC-003.1, 003.2 | Brayan Esteban Cruz Arango | Cesar Johan Casado Calderon | — | 2.5 |
| T011 | HU-03 | Backend | API CRUD de productos con búsqueda paginada | REQ-VIL-005, 006 | Cesar Johan Casado Calderon | Brayan Esteban Cruz Arango | T009, T010 | 4 |
| T012 | HU-03 | Frontend | Pantalla de catálogo con filtros por especie y marca | AC-003.1 | Cristian Danilo Pineda Ramirez | Cesar Johan Casado Calderon | T011 | 4 |
| T013 | HU-04 | BD | Migración V4: lote, saldo de inventario y movimiento | REQ-VIL-007 | Cristian Danilo Pineda Ramirez | Cesar Johan Casado Calderon | — | 3 |
| T014 [P] | HU-04 | Testing | Pruebas con archivos Excel válidos, incompletos y corruptos | AC-004.1, 004.2 | Brayan Esteban Cruz Arango | Cesar Johan Casado Calderon | — | 3 |
| T015 | HU-04 | Backend | Servicio de importación transaccional con Apache POI | REQ-VIL-007, 008 | Cesar Johan Casado Calderon | Brayan Esteban Cruz Arango | T013, T014 | 6 |
| T016 | HU-04 | Frontend | Asistente de carga con vista previa y reporte de errores | AC-004.2 | Cristian Danilo Pineda Ramirez | Cesar Johan Casado Calderon | T015 | 4 |
| T017 | HU-05 | BD | Vista de saldo disponible por lote e índice por vencimiento | REQ-VIL-009 | Cristian Danilo Pineda Ramirez | Cesar Johan Casado Calderon | — | 2.5 |
| T018 [P] | HU-05 | Testing | Pruebas de semáforo y saldo disponible | AC-005.1 a 005.3 | Brayan Esteban Cruz Arango | Cesar Johan Casado Calderon | — | 3 |
| T019 | HU-05 | Backend | Endpoint GET /inventario/productos/{ean} | REQ-VIL-009, 010 | Cesar Johan Casado Calderon | Brayan Esteban Cruz Arango | T017, T018 | 4 |
| T020 | HU-05 | Frontend | Pantalla de consulta con escaneo por cámara (PWA para tablet) | AC-005.1, 005.2 | Cristian Danilo Pineda Ramirez | Brayan Esteban Cruz Arango | T019 | 5 |

**Total estimado** · 76.5 horas de tareas técnicas.

En el tablero, mover a In Progress cuando se resuelvan las dependencias. Limitar
In Progress a 4 tarjetas y QA/Review a 3. Para entrar en QA/Review, el PR referencia
el ID y CI está en verde. El revisor mueve la tarjeta a Done al comprobar la evidencia.

## Revisiones y evidencia de cierre

| Revisión | Evidencia requerida | Estado |
| --- | --- | --- |
| Puerta 0 | Constitución y reglas de trabajo ratificadas | Pendiente |
| Puerta 1 | Requisitos, reglas y criterios de aceptación aprobados | Pendiente |
| Puerta 2 | Plan, decisiones de arquitectura y contrato OpenAPI revisados | Pendiente |
| Puerta 3 | Dependencias, estimaciones y tarjetas comprobadas en Sprint Tools | Pendiente |
| Sprint Review | Aceptación de HU-01 a HU-05 y resultados de CI | Pendiente |
| Conciliación | Inventario de origen conciliado al 100 % | Pendiente |
| Staging | URL en Render y prueba de humo con datos sintéticos | Pendiente |

Para iniciar la implementación, hacen falta el repositorio o proyecto de Sprint Tools y
la aprobación de los criterios según el flujo SDD. Para verificar la carga real se requiere
el Excel de inventario de origen. La plantilla oficial de carga, el servicio de correo
para invitaciones y el dispositivo de escaneo quedan por confirmar con el equipo.

## Fuentes

- Taller Scrum SDD Tasks a Kanban Villali, secciones 1 a 6.
- Proyecto Scrum Distribuidora Villali, hojas Historias de Usuario, Plan Sprint,
  Plan del Proyecto, Roles del Sistema y Tareas SDD y Kanban.
