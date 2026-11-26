# Plan técnico del Sprint 4

La aplicación mantiene el frontend HTML, CSS y JavaScript y el servidor Python existente. En Render usa **MongoDB Atlas**, mediante el adaptador `mongo_store.py`; las pruebas también cubren SQLite y PostgreSQL. Se conserva el origen `main/sprint-1`, el plan gratuito y las variables existentes de Atlas.

## Almacenamiento y transacciones

Las tareas V12–V14 del taller se adaptan al modelo documental vigente. La colección persistente `commerce_records` diferencia registros por tipo y clave: `facturas`, `pagos`, `bandeja_facturas`, `fiscal_customers`, `notas_credito`, `liquidaciones`, `mermas`, `pse_intents`, `finance_counters`, `finance_secrets` e `indicadores_materializados`. Se reutilizan pedidos, clientes, rutas y retornos; los movimientos físicos actualizan los lotes originales. No se introduce H2 ni un archivo local como almacenamiento de Render.

Cada operación de escritura usa la transacción y el control de concurrencia existentes del adaptador. Los consecutivos se guardan en Atlas, los pagos tienen clave de solicitud y las inspecciones/liquidaciones verifican el registro previo. Una petición repetida no vuelve a aplicar dinero, unidades o notas crédito. Los saldos anteriores se conservan en la ficha del cliente al iniciar su conciliación financiera.

Los cortes de indicadores son documentos materializados con filtros, fecha, autor y reporte completo. Se conservan al reiniciar. El tablero normal consulta datos actuales; un Excel de un corte usa su resultado congelado. Las lecturas de productos/lotes y sumas de pagos/notas se agrupan para evitar una consulta por cada referencia.

## API y autorización

Prefijo protegido: `/api/finanzas/`. La sesión del servidor determina el rol y la cuenta de cliente; no se acepta una identidad enviada por el navegador.

| Recurso | Método | Permisos y efecto |
| --- | --- | --- |
| facturas | GET / POST | 01 consulta, 09 consulta/emite/reenvía, 10 consulta solo las propias |
| documento?id=…&format=pdf o xml | GET | 01/09 y cliente propietario; descarga factura |
| bandeja | GET | 09; envíos simulados y nombres de adjuntos |
| pagos | GET / POST | 09 consulta y registra efectivo/transferencia; 10 consulta solo sus pagos |
| cartera | GET | 01/09; facturas y saldos anteriores por edad |
| pse | GET / POST | 09 o cliente propietario; acciones start/simulate |
| pse-webhook | POST | Evento externo sin sesión; exige firma y fecha válidas |
| liquidaciones | GET / POST | 07; cierre transaccional de ruta |
| acta-ruta?id=… | GET | 07; acta PDF |
| devoluciones | GET / POST | 03; report, inspect o expiry |
| nota-credito?id=… | GET | 01/03/09 y cliente propietario; nota PDF |
| indicadores | GET / POST | 01; filtros, format=xlsx/pdf, cut=identificador o action=snapshot |
| cortes | GET | 01; historial de reportes materializados |
| /version | GET público | Sprints, commit de Render y modos académicos; no publica secretos |

Facturas, abonos, cortes y reingresos se auditan con usuario, fecha y referencia. El servidor vuelve a comprobar que la cuenta siga activa y conserve el rol antes de escribir.

## Pasarela académica

Al iniciar PSE se conserva una intención con factura, cliente, valor y estado PENDIENTE. El botón de prueba fabrica un evento y ejecuta el mismo validador del webhook: `HMAC-SHA256(timestamp + '.' + cuerpo_original)`, cabeceras `X-PSE-Timestamp` y `X-PSE-Signature`, tolerancia de cinco minutos. La clave aleatoria se conserva en Atlas y no se devuelve al frontend. Una firma incorrecta, evento vencido o valor diferente se rechaza; una confirmación repetida no repite el pago. Esta convención es propia del simulador, no el contrato de una pasarela comercial.

## Documentos y experiencia

`finance.py` concentra las reglas y exportaciones; `finance.js` muestra formularios por rol y `finance.css` adapta tarjetas, tablas y diálogos a celular. Los formularios explican valores en COP y el carácter académico. Excel escapa celdas que podrían interpretarse como fórmulas. PDF/XML se generan al descargar, con autorización, desde los registros persistentes; no dependen del disco efímero de Render.

El caché PWA se actualiza a `villali-shell-v5`. Se conservan IndexedDB y la cola de entregas del conductor. Las devoluciones parciales en ruta registran cantidades por SKU/lote sin revelar precios al conductor. No se cambian la portada ni el acceso único.

## Comprobación y despliegue

Ejecutar las cuatro suites y CI antes de desplegar el último commit en el servicio existente. Confirmar `/version` y `/health`, además de las pantallas por rol. No volver a ejecutar semillas de catálogo/inventario sobre Atlas. Las ramas archivadas son copias del código; la copia de datos corresponde al respaldo de MongoDB del equipo y no debe subirse al repositorio.
