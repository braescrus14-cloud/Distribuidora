# Tabla de verificación · Sprint 3

**Aplicación:** [Villali](https://villali-staging.onrender.com/) · [Acceso](https://villali-staging.onrender.com/entrar). Registrar el commit mostrado en Render antes de iniciar. Completar las pruebas con datos de ensayo identificables y cuentas distintas para Cliente y Conductor.

| ID | Historia / rol | Prueba | Resultado esperado | Resultado y evidencia del equipo |
| --- | --- | --- | --- | --- |
| 11.1 | HU-11 · Auxiliar 04 | Confirmar 15 unidades con 10 en el lote de vencimiento cercano y saldo en el siguiente. | Reserva 10 + 5 en orden FEFO, sin usar saldo reservado o vencido. | Por registrar |
| 11.2 | HU-11 · Auxiliar 04 | Ingresar un EAN diferente y luego el esperado. | Mensaje y alerta sonora para el incorrecto; línea pendiente hasta verificar el correcto. | Por registrar |
| 11.3 | HU-11 · Auxiliar 04 / Jefe 03 | Finalizar con todas las líneas verificadas; reintentar la acción. | ALISTADO; descuento físico y liberación de reserva una sola vez. | Por registrar |
| 12.1 | HU-12 · Logística 07 | Registrar pesos/destinos y agrupar pedidos alistados de la misma zona. | Ruta con conductor, vehículo, visitas y mapa esquemático por proximidad. | Por registrar |
| 12.2 | HU-12 · Logística 07 | Probar exceso de carga, zonas distintas y conductor/vehículo ocupado. | Rechazo con explicación; no crear la ruta inválida. | Por registrar |
| 13.1 | HU-13 · Auxiliar 04 / Jefe 03 | Descargar el rótulo de un pedido ALISTADO. | PDF con QR y número del pedido. | Por registrar |
| 13.2 | HU-13 · Jefe 03 | Verificar un rótulo ajeno, repetir uno válido y dejar otro sin cargar. | Ajeno rechazado; repetido no duplica; despacho pendiente mientras falten pedidos. | Por registrar |
| 13.3 | HU-13 · Jefe 03 | Completar cargue y emitir manifiesto. | PDF MD-… con ruta/vehículo/conductor/visitas; pedidos EN_RUTA. | Por registrar |
| 14.1 | HU-14 · Conductor 08 | Registrar firma, foto y ubicación de una entrega propia. | ENTREGADO; fechas de captura y recepción; evidencia conservada en MongoDB. | Por registrar |
| 14.2 | HU-14 · Conductor 08 / Logística 07 / Jefe 03 | Marcar cliente cerrado; consultar aviso y recibir el retorno físicamente. | NOVEDAD, aviso persistente y retorno; reintegro por lote una sola vez al recibirlo. | Por registrar |
| 14.3 | HU-14 · Conductor 08 | Abrir jornada con red, guardar tres confirmaciones sin red, recargar y reconectar. | Tres pendientes conservados; sincronización con sesión válida sin duplicados. | Por registrar |
| 14.4 | HU-14 · Segundo Conductor 08 | Intentar consultar jornada/evidencia de otro conductor. | Sin acceso a rutas ajenas; evidencia ajena 404. | Por registrar |
| 15.1 | HU-15 · Cliente 10 | Consultar el pedido antes y después de alistar, despachar y entregar. | Línea de tiempo; en ruta, ETA aproximada y paradas pendientes anteriores; actualización periódica. | Por registrar |
| 15.2 | HU-15 · Segundo Cliente 10 | Consultar el identificador de un pedido ajeno. | 404; no exponer datos del otro cliente ni pruebas de entrega. | Por registrar |
| UX.1 | Visitante | Revisar portada en celular y escritorio; explorar los cuatro estados de la demostración. | Sin solapamientos ni desplazamiento horizontal; imágenes, iconos y botones con destinos claros. | Por registrar |
| UX.2 | Visitante / Administrador 02 | Enviar solicitud con consentimiento y consultarla en Solicitudes y contacto. | Mensaje de registro; solicitud persistente y privada; administrador puede marcar Contactado. | Por registrar |
| UX.3 | Todas las cuentas | Iniciar por correo o usuario sin elegir rol y solicitar recuperación con correo registrado. | El rol se reconoce automáticamente; errores claros y recuperación de un solo uso si el proveedor está configurado. | Por registrar |
| UX.4 | Diez roles | Abrir Inicio con cada perfil y sus acciones principales. | Tableros y estructuras diferentes por responsabilidad; acceso limitado a los módulos autorizados. | Por registrar |
| UX.5 | Accesibilidad | Activar movimiento reducido y navegar con teclado. | Animaciones desactivadas, foco visible y controles operables. | Por registrar |
| UX.6 | Visitante / Administrador 02 | Completar un testimonio sin autorizar, comprobar API pública y después autorizarlo. | Borrador privado; publicación solo tras autorización; marcadores para datos faltantes. | Por registrar |
| UX.7 | Visitante móvil | Cambiar los cuatro estados de la demo, abrir fichas y usar WhatsApp mientras desplaza la página. | Sin saltos de altura, diálogo con cierre claro y contacto en barra superior. | Por registrar |
| P.1 | Persistencia / equipo | Guardar registros identificables, reiniciar el servicio y volver a consultar. | Los registros siguen en la misma base de Atlas. No importar ni sembrar datos al reiniciar. | Por registrar |

## Registro de cada sesión de prueba

| Campo | Completar |
| --- | --- |
| Commit de aplicación desplegado | |
| Fecha y responsable | |
| Dispositivo / navegador | |
| IDs de pedidos, rutas y lotes utilizados | |
| Resultado por prueba: Aprobado / Falló / No ejecutado | |
| Enlace de captura, PDF o ejecución de CI | |
| Incidencias y correcciones | |

Las suites automatizadas son evidencia técnica; las celdas anteriores se completan con los resultados reales del equipo. No equivalen a una aceptación firmada por la Product Owner. [Registro de decisiones SDD](Registro_SDD.md).
