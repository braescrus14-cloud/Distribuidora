# Revisión integral de Villali del 25 de noviembre de 2026

Se revisaron las veinte historias integradas, el acceso y los permisos de los diez roles, la portada y las pantallas de operación. Las pruebas destructivas, contraseñas incorrectas y movimientos de inventario/dinero se ejecutaron en bases desechables. En Render solo se iniciaron y cerraron sesiones y se consultaron pantallas: no se crearon pedidos, pagos, usuarios ni cargas de inventario.

## Resultado por entorno

| Comprobación | Resultado observado |
| --- | --- |
| GitHub, integración a9dda80 | Cuatro CI satisfactorias: SQLite, PostgreSQL y MongoDB de ensayo |
| Programa integrado local | Cinco suites satisfactorias: Sprint 1, Sprint 2, Sprint 3, Sprint 4 y portal público |
| Autenticación adicional | Diez contraseñas distintas de ensayo, permisos, sesión caducada, cuenta desactivada, cambio de rol, invitación caducada/reutilizada, revocación y cierre de sesión correctos |
| Cuentas actuales de Render | Diez cuentas activas/configuradas, incluidos admin y los otros nueve roles: ingreso satisfactorio con las credenciales de demostración suministradas por el usuario |
| Navegación publicada | 44 pantallas recorridas; sin excepciones JavaScript, avisos de fallo ni desbordamiento horizontal de página en el recorrido de escritorio |
| Cookies publicadas | Secure y HttpOnly presentes en los diez ingresos; el código usa SameSite=Strict |
| API de usuarios | Devuelve rol, estado y configuración; no devuelve hashes, contraseñas ni tokens de sesión |
| Render, salud | `/health` respondió HTTP 200 y `status: ok` |
| Render, Sprint 4 | `/version` respondió 401 y Contabilidad aún mostró el menú previo; el Sprint 4 no estaba publicado al comprobarlo |

[CI Sprint 1](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/45730943749) · [CI Sprint 2](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/45730943740) · [CI Sprint 3](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/45730943739) · [CI Sprint 4](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/45730943718).

## Acceso y contraseñas

Las contraseñas se guardan mediante PBKDF2-HMAC-SHA256 con 600.000 iteraciones y sal aleatoria por contraseña. Las sesiones e invitaciones se guardan por digest del token. La contraseña nunca se devuelve al administrador: la revisión del ingreso se hizo con la contraseña de demostración proporcionada, no recuperando claves de la base.

Se comprobaron los límites de 10–128 caracteres, mayúscula, número y símbolo; cinco intentos erróneos bloquean temporalmente la cuenta en la prueba del Sprint 1. Las sesiones de escritorio caducan tras 30 minutos de inactividad y las móviles tras 15. Cambiar contraseña, desactivar una cuenta o cambiar su rol invalida las sesiones correspondientes. El cierre de sesión impide reutilizar la cookie. La activación es de un solo uso y respeta su vencimiento.

Las credenciales reales de demostración, cookies, enlaces de activación y URI de MongoDB quedan fuera de este informe y del repositorio. Las claves que aparecen en las suites son exclusivamente de bases desechables. La búsqueda de patrones de credenciales en los archivos revisados no encontró URI de Atlas con contraseña, claves Resend/GitHub ni claves privadas coincidentes con los patrones examinados; no constituye una auditoría de todo el historial Git.

## Revisión funcional y visual

- Sprint 1: invitación, usuarios, permisos, catálogo, Excel validado/atómico, bloqueo y bitácora.
- Sprint 2: proveedores, aprobación de compra, recepción parcial, cupo/cartera, reserva y aislamiento B2B.
- Sprint 3: FEFO, capacidad/rutas, manifiesto, evidencia y retornos, idempotencia, seguimiento y persistencia.
- Sprint 4: factura neta, rechazo/reenvío, PDF/XML, abonos, PSE firmado, cartera, liquidaciones, notas, mermas, filtros, Excel/PDF, cortes y persistencia tras reinicio.
- Portal: consentimiento, solicitudes persistentes, recuperación de un solo uso y permisos de administración.

Los siete recorridos locales de nuevos módulos se verificaron en 390, 1360 y 1440 px. Se comprobó el inicio de los diez roles al cambiar entre 1360, 390 y 320 px.

Se corrigió la adaptación del menú al cruzar el límite de 760 px: al pasar de escritorio a celular se cierra y al regresar se restablece. Antes podía conservar el estado abierto del escritorio y desplazar demasiado el contenido. El archivo principal pasa a `app.js?v=20` y el caché de la aplicación a `villali-sprint3-shell-v6`; se conservan IndexedDB y las entregas pendientes del conductor.

La prueba adicional `sprint-1/tests/access.py` se incorpora a CI Sprint 1 para repetir la revisión de acceso con SQLite, PostgreSQL y MongoDB. Las comprobaciones funcionales de pagos DIAN/PSE siguen siendo académicas, según el alcance autorizado.

## Para cerrar la comprobación publicada

1. Revisar las cuatro CI del commit que contiene este informe y la corrección móvil.
2. Publicar ese commit en el servicio existente de Render mediante Manual Deploy → Deploy latest commit, manteniendo el plan gratuito y las variables actuales de Atlas.
3. Confirmar que [la versión publicada](https://villali-staging.onrender.com/version) informa `sprints-1-a-4` y el mismo commit, y que [salud](https://villali-staging.onrender.com/health) responde correctamente.
4. Repetir [la guía Sprint 4](sprint-4/Guia_Verificacion_Sprint_4.md) con cuentas del equipo y adjuntar evidencias a [SDD](sprint-4/Registro_SDD.md).

La revisión describe los casos y entornos comprobados; no garantiza ausencia absoluta de errores. La recepción real de correo exige proveedor configurado. La cámara, GPS y trabajo sin conexión del conductor se completan con los dispositivos del equipo. Las aceptaciones de las historias corresponden a sus responsables, no a los resultados automáticos.
