# Especificación · Sprint 3

**Fuente:** `Proyecto Scrum Distribuidora Villali.xlsx`, historias HU-11–HU-15 y tareas T041–T059. La portada y la diferenciación visual de los roles son requisitos adicionales solicitados para la presentación. Este documento describe el incremento implementado; su aceptación corresponde al equipo.

## HU-11 · Alistamiento FEFO · 5 puntos

Auxiliar de Bodega prepara pedidos confirmados usando las reservas por lote del Sprint 2.

- **AC-011.1:** si se requieren 15 unidades y el lote de vencimiento más cercano tiene 10, se asignan 10 de este y 5 del siguiente. Los empates se resuelven por lote y ubicación. No se utilizan existencias vencidas o ya reservadas.
- **AC-011.2:** un EAN diferente del producto esperado produce un mensaje y alerta sonora, y mantiene la línea pendiente. El código puede venir de un lector USB/Bluetooth que escribe como teclado o ingresarse manualmente.
- **AC-011.3:** solo al confirmar todas las líneas se termina el alistamiento. El pedido pasa a `ALISTADO`; se descuentan simultáneamente existencia física y reserva. Reintentar no descuenta dos veces. Un lote que venció después de reservar requiere revisión de bodega.

## HU-12 · Planificación de rutas · 5 puntos

Coordinación de Logística registra vehículo/capacidad, conductor, peso por unidad y coordenadas de destinos.

- **AC-012.1:** únicamente se agrupan pedidos `ALISTADO`, sin ruta previa y de la misma zona. Se propone una secuencia por proximidad y un mapa esquemático con visitas numeradas.
- **AC-012.2:** la suma de unidades por peso no supera la capacidad. Se informa el exceso en kg. El vehículo y el conductor no pueden ocupar dos rutas pendientes simultáneas.

La distancia es geográfica entre coordenadas y no una navegación vial. La hora de llegada es aproximada y no constituye una promesa comercial ni seguimiento GPS del vehículo.

## HU-13 · Cargue y manifiesto · 3 puntos

- **AC-013.1:** Bodega genera un rótulo PDF con QR para un pedido alistado. En el cargue se valida su número contra la ruta; un pedido ajeno se rechaza. La verificación repetida no duplica el cargue.
- **AC-013.2:** se exige la totalidad de los pedidos cargados para emitir el manifiesto `MD-…` en PDF. Ruta y pedidos pasan a `EN_RUTA`. El PDF contiene vehículo, conductor, peso y relación de visitas.

## HU-14 · Entrega móvil y novedades · 5 puntos

- **AC-014.1:** un conductor solo consulta sus rutas. Para entregar registra firma, foto, coordenadas y fecha de captura; el servidor conserva además la fecha de recepción. Pedido a `ENTREGADO`.
- **AC-014.2:** una novedad exige observación, crea un aviso persistente para Coordinación y un retorno pendiente para Bodega. La recepción física del retorno reintegra las unidades una vez, con el lote y vencimiento de origen.
- **AC-014.3:** la jornada se abre primero con conexión. Las confirmaciones se guardan en IndexedDB antes de enviarse; sobreviven a la recarga y se sincronizan con su mismo identificador al recuperar la conexión y una sesión válida. No se crean entregas duplicadas.

No se almacena contraseña en el dispositivo. El navegador conserva datos de la jornada y las evidencias pendientes: se debe usar un dispositivo autorizado y sincronizar antes de borrar sus datos. Las capturas deben sincronizarse en un máximo de siete días; una sesión vencida exige volver a ingresar.

## HU-15 · Seguimiento del cliente · 3 puntos

- **AC-015.1:** cada cliente consulta la secuencia confirmado → alistado → en ruta → entregado/novedad. En ruta se muestra llegada estimada y cantidad de entregas pendientes anteriores. Actualización cada 20 segundos con la vista visible y conexión, además del botón manual.
- **AC-015.2:** pedir un identificador que pertenece a otro cliente devuelve 404. No se divulgan el recorrido de otros clientes, pruebas de entrega, cupos ni coordenadas del conductor.

## Portada y experiencia por rol

Portada pública orientada a fincas y nutrición para bovinos, aves, porcinos y otras especies. Incluye la marca oficial, imagen rural generada para el proyecto, líneas, proceso de compra y acceso. No se publican contactos, estadísticas ni testimonios inventados.

Los diez perfiles conservan sus permisos. Cada uno tiene acento, fondo y descripción propios; Bodega trabaja con tarjetas de preparación, Logística con mapa/configuración, Conductor con jornada móvil y Cliente con seguimiento y portal. Se conserva el lenguaje visual de la marca y el acceso existente.
