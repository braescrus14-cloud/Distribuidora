# Informe consolidado del Sprint 3

**Proyecto:** Distribuidora Villali. **Corte de documentación:** 25 de noviembre de 2026. **Alcance:** HU-11 a HU-15, tareas T041–T059 y mejoras de portada, acceso y espacios por rol. **Estado técnico:** código integrado y publicado, pruebas automatizadas correctas en la versión indicada. Las decisiones SDD y las aceptaciones del equipo siguen sus registros propios.

## 1. Resultado del incremento

El pedido confirmado del Sprint 2 puede prepararse por lote/vencimiento, asignarse a una ruta, cargarse, despacharse con manifiesto y entregarse con evidencia. El cliente vinculado consulta el estado de su pedido. El conductor puede conservar confirmaciones en el dispositivo cuando no hay conexión y sincronizarlas después.

En el cierre histórico, los tres primeros sprints se ejecutaban juntos en la carpeta `sprint-1`. La organización vigente de main reúne el código en `proyecto-completo` y los expedientes en `sprint/`. La [etiqueta de cierre y sus copias](Copias_y_Restauracion.md) conservan la referencia original.

## 2. Historias y trazabilidad

| Historia | Función implementada | Tareas | Código principal | Evidencia y límite |
| --- | --- | --- | --- | --- |
| HU-11 | Alistamiento FEFO, EAN correcto por línea, descuento físico y de reserva al finalizar, rótulo QR. | T041–T044 y T050 | logistics.py, logistics.js | test_logistics.py: casos de FEFO, EAN incorrecto, finalización concurrente e idempotencia. El lector físico se valida en bodega. |
| HU-12 | Vehículos, conductor activo, peso por unidad, destinos, capacidad y ruta por zona con mapa. | T045–T048 | logistics.py, logistics.js | Capacidad, conductor/vehículo únicos y orden de visitas. El mapa usa distancia geográfica, no navegación vial. |
| HU-13 | Verificación de rótulos de la ruta, cargue completo y manifiesto PDF antes de despachar. | T049–T052 | logistics.py, logistics.js | Rechazo de pedido ajeno y doble cargue; PDF y estado En ruta. |
| HU-14 | Jornada propia, firma, fotografía, ubicación, novedades, retorno y sincronización sin conexión. | T053–T056 | logistics.py, logistics.js, driver-store.js, service-worker.js | Permisos, evidencia y reintentos; cola por usuario en IndexedDB. Cámara/GPS y recepción física se prueban en el dispositivo. |
| HU-15 | Línea de tiempo, hora estimada y visitas pendientes anteriores, con aislamiento por cliente. | T057–T059 | logistics.py, logistics.js | Privacidad entre clientes y estados. La ETA es estimada y no GPS en tiempo real. |

[Especificación y criterios](spec.md) · [Tareas con responsables del plan](tasks.md) · [Arquitectura y contrato de API](plan.md). Los responsables son asignaciones del documento fuente, no constancia de una aprobación firmada.

## 3. Mejoras adicionales solicitadas

| Área | Resultado final |
| --- | --- |
| Portada pública | Mensaje rural conservado, líneas de nutrición, referencias y fichas con fuentes, proceso de compra y demo de seguimiento. |
| Identidad visual | Logo aportado por el usuario; verde profundo y acentos de marca compartidos con el acceso; fotos ilustrativas de galpón, cerdos, ganadería y equinos. |
| Contacto | WhatsApp autorizado, teléfono, formulario persistente con consentimiento y protección anti-spam. Solicitar cuenta no crea una cuenta automáticamente. |
| Administración | Bandeja privada de solicitudes, estado de atención y configuración de datos públicos, cifras y testimonios autorizados. |
| Acceso | Una sola pantalla con correo registrado o usuario y contraseña, identificación automática del rol, recuperación de acceso y errores claros. Se retiró el selector Clientes/Equipo. |
| Roles | Diez inicios con estructuras y acciones por responsabilidad, además de sus colores. Los permisos siguen controlados por el servidor. |
| Navegación | Un solo Ingresar y llamado principal a solicitar cuenta; fotos enlazadas con su línea; consultas por WhatsApp con interés específico; cierres con etiquetas claras. |
| Animaciones | Entradas por opacidad, demo con altura reservada, respeto de movimiento reducido y retirada de tarjetas superpuestas. |
| Tarjetas de productos | Mismo icono de 44 × 44 px, texto legible, columnas según ancho y enlaces de ficha con área táctil. Disponibilidad pendiente consultable al asesor. |
| Evaluación automática | robots permite portada y formulario de acceso; noindex se conserva en acceso/API, pero no en la portada. La autenticación no se retira. |
| Uso académico | Pie con datos de ejemplo y sección de confianza con 8 años, 12 municipios, 240 entregas y dos experiencias simuladas, identificadas como académicas. No son registros reales de ventas ni aceptaciones SDD. |
| Documentación | Índice visible de los tres sprints, índice de Sprint 2, guías vigentes de verificación y corrección de instrucciones antiguas de despliegue. |

[Diseño por rol](historial/UX_Portada_y_Perfiles.md) · [Revisión de animaciones](historial/Revision_UX_Final.md) · [Acceso único](historial/Simplificacion_Acceso_y_Portada.md) · [Ejemplos académicos](Datos_Demostracion_Academica.md).

## 4. Tecnología y conservación de datos

- Interfaz: HTML, CSS y JavaScript, sin un framework de frontend añadido.
- Servidor: Python, lógica comercial/logística y API HTTP. La interfaz no equivale a que el backend sea JavaScript.
- Persistencia desplegada: MongoDB Atlas, con el nombre de base explícito y el servicio existente de Render gratuito. SQLite y PostgreSQL también se ejercitan en CI como almacenes de prueba.
- PDF y QR: reportlab y qrcode; Excel: openpyxl para las funciones de importación existentes.
- Dispositivo: IndexedDB para jornada y confirmaciones por conductor; service worker para recursos de interfaz. No guarda respuestas de API en caché.
- La actualización del programa no borra ni vuelve a sembrar Atlas. Las copias de GitHub son de código/documentos y no incluyen la base ni las variables secretas.

## 5. Cronología del trabajo registrado

| Fecha del commit | Referencia | Cambio |
| --- | --- | --- |
| 20/11/2026 | [e65a60c](https://github.com/braescrus14-cloud/Distribuidora/commit/e65a60c0483eb786dc3eca9c9c06290b4a3a8506) | Primera integración logística del Sprint 3 y portada. |
| 20/11/2026 | [1162f43](https://github.com/braescrus14-cloud/Distribuidora/commit/1162f43bce5bdcba06b8de601de9bb452e3bd0d1) | Rediseño, espacios por rol y solicitudes persistentes. |
| 21/11/2026 | [c4fdaf8](https://github.com/braescrus14-cloud/Distribuidora/commit/c4fdaf8a240ec9057512a1b62bce700387a528d3) | Correcciones de scroll, contacto verificable y fichas técnicas. |
| 21/11/2026 | [aaa1ce9](https://github.com/braescrus14-cloud/Distribuidora/commit/aaa1ce9a281ff5de9ea9b5f396b3402619a2b4ad) y [e92ed97](https://github.com/braescrus14-cloud/Distribuidora/commit/e92ed9740b01e29795db81aa80a242ee65e64200) | Acceso único, enlaces diferenciados, pie académico y lectura pública. |
| 21/11/2026 | [7796943](https://github.com/braescrus14-cloud/Distribuidora/commit/7796943c9e73769c766ace322f5180c7c813240d) | Documentación organizada, guías, ejemplos académicos y corrección del icono equino. |
| 21/11/2026 | [09498e2](https://github.com/braescrus14-cloud/Distribuidora/commit/09498e29fcf9448e971aaa8bcf057470ca02f870) | Registro de publicación y CI en la guía. |
| 25/11/2026 | Este informe | Consolidación, inventario de copias, manifiesto y nueva comprobación pública. |

El Excel conserva una ventana de referencia del 23 al 29 de noviembre para Sprint 3. El historial registra implementación anterior a esa ventana. Este informe no cambia fechas del documento fuente ni transforma esos commits en aprobaciones retrospectivas.

## 6. Evidencias de pruebas y publicación

Versión de aplicación comprobada: `7796943c9e73769c766ace322f5180c7c813240d`. CI del mismo código:

- [Sprint 1, ejecución 44951305192](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/44951305192): correcta.
- [Sprint 2, ejecución 44951305297](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/44951305297): correcta.
- [Sprint 3, ejecución 44951305330](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/44951305330): correcta.

La CI del Sprint 3 incluye test_logistics.py y test_public_portal.py con SQLite, PostgreSQL y MongoDB de ensayo. Las verificaciones del navegador registradas el 20–21/11 cubren diez roles, errores JavaScript/CSP, formulario y movimiento reducido. La última revisión de productos se comprobó a 1710, 1360, 390 y 320 px.

En el ensayo de navegador del 20/11, tres confirmaciones en IndexedDB sobrevivieron a una recarga sin red y se enviaron una vez al recuperar conexión, usando un receptor HTTP simulado. La idempotencia del servidor se comprobó aparte en la suite HTTP. La guía de pruebas se unificó después en `Guia_Verificacion_Sprint_3.md`.

El 25/11 se volvió a consultar Render sin iniciar sesión ni crear registros: `/health` respondió 200 con status ok y nueve recursos públicos respondieron 200 y coincidieron con el código de referencia al normalizar finales de línea. La primera lectura agotó el tiempo mientras la instancia gratuita se reactivaba; el reintento terminó correctamente. Detalle y SHA-256 en el [manifiesto](Manifiesto_Respaldo_Sprint_3.json).

Esto demuestra disponibilidad y correspondencia de recursos públicos. No sustituye un recorrido operativo autenticado ni una prueba física de escáner, cámara, GPS o reinicio de Atlas realizada hoy.

## 7. Cómo revisar y qué queda para aceptación

1. Seguir la [guía completa de verificación](Guia_Verificacion_Sprint_3.md).
2. Guardar pedido, ruta, manifiesto, saldos antes/después y pruebas de entrega utilizados.
3. Completar la [tabla de resultados](Tabla_Verificacion_Sprint_3.md) con resultado, fecha, responsable y evidencia reales.
4. Ratificar las cuatro puertas SDD, la revisión cruzada, el estado del tablero Sprint Tools y la aceptación por HU en [Registro SDD](Registro_SDD.md).
5. Confirmar empaques, variantes y fichas pendientes con el fabricante o asesor. Las dudas técnicas se conservan en [datos pendientes](Datos_Pendientes_Confirmacion.md).

El código y sus copias pueden quedar preparados para continuar el proyecto mientras las aceptaciones humanas permanecen pendientes. No se crean firmas ni resultados de pruebas no ejecutadas.
