# Plan técnico · Sprint 3

## Decisión de integración

La aplicación existente continúa en `main/sprint-1`, sin modificar `rootDir`, servicio, plan gratuito o variables de Render. Respaldo previo: `sprint-2-archivo` en `bd7e69b`. Frontend HTML/CSS/JavaScript sin framework ni compilación; backend Python ya existente. No se afirma que el backend sea JavaScript.

La arquitectura del taller menciona migraciones V9–V11 relacionales. La versión integrada conserva el adaptador MongoDB establecido en los sprints previos: los nuevos agregados usan `commerce_records` mediante `kind/record_key/payload`. Se mantiene la compatibilidad SQLite para pruebas locales y PostgreSQL para regresión. No hay migración destructiva ni traslado automático a otra base. Esta equivalencia requiere ratificación técnica, no una aprobación supuesta.

## Datos y consistencia

| Agregado | Contenido |
| --- | --- |
| pedidos | Reservas existentes, confirmación de líneas, alistamiento, despacho y entrega |
| vehiculos / pesos / destinos | Capacidad, kg por unidad y destino del cliente |
| rutas | Vehículo, conductor, pedidos, secuencia, cargue, estado y manifiesto |
| avisos_logistica | Novedades consultables por Coordinación |
| retornos | Mercancía pendiente/recibida, lote y ubicación de retorno |

Los lotes conservan `quantity` física y `reserved`; el disponible es su diferencia. El alistamiento descuenta ambas columnas en una transacción. La devolución verificada recupera la cantidad física sin reactivar la reserva. El adaptador Mongo utiliza las transacciones y el mecanismo de concurrencia existente; Atlas debe permitirlas.

Firma y foto comprimida se guardan en MongoDB dentro de la entrega, no en el disco efímero de Render. Cada imagen se valida y limita a 600 KB; se limita también el cuerpo HTTP. Los identificadores de solicitud hacen idempotentes creación de ruta, entregas y recepción de retornos.

## Contrato HTTP

Todos los endpoints operativos exigen sesión. Los POST conservan comprobación de origen, validación, comprobación de rol activo dentro de la transacción y bitácora.

| Endpoint `/api/logistica/…` | Rol | Acciones |
| --- | --- | --- |
| picking | 03 y 04 | GET órdenes; POST `scan` / `finish` |
| routes | 07 | GET planificación; POST `vehicle` / `weight` / `destination` / `plan` |
| dispatch | 03 | GET cargue y retornos; POST `load` / `dispatch` / `return` |
| deliveries | 08 | GET jornada propia; POST resultado `ENTREGADO` / `NOVEDAD` |
| tracking?id= | 10 | GET seguimiento propio; ajeno 404 |
| rotulo?id= | 03, 04 y 07 | PDF con QR de pedido alistado |
| manifiesto?id= | 03 y 07 | PDF de ruta despachada |
| evidence?id= | 03, 07 y conductor asignado | Prueba de entrega protegida |

## Módulos

`logistics.py` concentra reglas; `logistics.js` construye vistas con DOM y texto seguro. `logistics.css` diferencia perfiles. `driver-store.js` maneja IndexedDB y sincronización por usuario. El service worker guarda únicamente archivos de interfaz; no guarda respuestas de API en caché. La jornada y las confirmaciones del conductor están separadas por identificador de cuenta.

El mapa SVG local usa Haversine y vecino más cercano; evita claves, costes o servicios cartográficos externos. La ETA supone 30 km/h y 15 minutos de servicio por visita, con un mínimo de cinco minutos por tramo. Durante el reparto se ajusta según las paradas aún pendientes; no conoce tráfico ni ubicación en vivo.

## Operación y recursos

Se agregan `reportlab` para PDF y `qrcode[pil]` para QR. La imagen rural `farm.jpg` se optimizó a aproximadamente 147 KB y se sirve desde el mismo origen. No se cargan fuentes o scripts externos. El logo PNG es el aportado por el usuario; `app-icon.svg` es un monograma para instalar la PWA.

Mantener `MONGODB_URI`, `MONGODB_DATABASE` y las credenciales existentes. No copiar secretos al repositorio. La copia de código no sustituye una copia de seguridad de Atlas. Desplegar sobre la misma base conserva registros; cambiar el nombre de base o borrar documentos puede hacer que dejen de verse.

## Despliegue

Con las tres suites de CI en verde, Render → `villali-staging` → Manual Deploy → Deploy latest commit. Verificar el hash, `/health`, la portada en `/`, acceso en `/entrar` y las vistas de cada rol. Probar un registro tras reinicio y comparar el saldo de origen. No habilitar datos semilla ni volver a importar inventario al desplegar.

Para revertir código, desplegar el commit anterior o la referencia del respaldo después de revisar compatibilidad; nunca borrar MongoDB para hacer rollback. Las antiguas invitaciones `/#invitar=…` redirigen al acceso y conservan el token.
