# Tareas SDD y trazabilidad · Sprint 3

Los responsables y revisores siguientes son los previstos en el Excel de origen. Su aparición no constituye firma, revisión realizada ni aceptación. La evidencia indica dónde revisar la implementación integrada; no se copia el estado «Done» de la plantilla como prueba de ejecución.

| Tarea | Historia / trabajo | Responsable previsto | Revisor previsto | Dependencias | Evidencia |
| --- | --- | --- | --- | --- | --- |
| T041 | HU-11 · Migración V9: orden de alistamiento y detalle por lote | Cristian Danilo Pineda Ramirez | Cesar Johan Casado Calderon | Sin dependencia | `commerce_records`: pedidos y reservas; adaptación MongoDB en plan.md |
| T042 [P] | HU-11 · Pruebas del algoritmo FEFO y casos de borde (lotes con igual fecha) | Brayan Esteban Cruz Arango | Cesar Johan Casado Calderon | Sin dependencia | `test_logistics.py`: FEFO y finalización concurrente |
| T043 | HU-11 · Motor de asignación FEFO y orden de alistamiento | Cesar Johan Casado Calderon | Brayan Esteban Cruz Arango | T041, T042 | `commerce.py` reservas + `logistics.py` alistamiento |
| T044 | HU-11 · Pantalla de alistamiento guiado con escaneo y alerta sonora | Cristian Danilo Pineda Ramirez | Brayan Esteban Cruz Arango | T043 | `logistics.js`: tarjetas, EAN y alerta sonora |
| T045 | HU-12 · Migración V10: vehículo, conductor, ruta y ruta-pedido | Cristian Danilo Pineda Ramirez | Cesar Johan Casado Calderon | Sin dependencia | `vehiculos`, `rutas`, `destinos`, `pesos` en MongoDB |
| T046 [P] | HU-12 · Pruebas de capacidad, conductor único y orden de visitas | Brayan Esteban Cruz Arango | Cesar Johan Casado Calderon | Sin dependencia | `test_logistics.py`: capacidad y exclusión de conductor |
| T047 | HU-12 · Servicio de rutas con orden sugerido por distancia | Cesar Johan Casado Calderon | Brayan Esteban Cruz Arango | T045, T046 | `logistics.py`: plan_route, Haversine y proximidad |
| T048 | HU-12 · Tablero de planificación de rutas con mapa | Cristian Danilo Pineda Ramirez | Cesar Johan Casado Calderon | T047 | `logistics.js`: planificación y mapa SVG |
| T049 [P] | HU-13 · Pruebas de cargue, ruta equivocada y manifiesto | Brayan Esteban Cruz Arango | Cesar Johan Casado Calderon | Sin dependencia | `test_logistics.py`: rótulo ajeno y PDF |
| T050 [P] | HU-13 · Generación del rótulo QR del pedido al finalizar el alistamiento | Cristian Danilo Pineda Ramirez | Cesar Johan Casado Calderon | Sin dependencia | `logistics.py`: rótulo QR en PDF |
| T051 | HU-13 · Servicio de cargue y emisión del manifiesto en PDF | Cesar Johan Casado Calderon | Brayan Esteban Cruz Arango | T049, T050 | `logistics.py`: load_order, dispatch_route y manifiesto |
| T052 | HU-13 · Pantalla de cargue con escaneo de rótulos | Cristian Danilo Pineda Ramirez | Cesar Johan Casado Calderon | T051 | `logistics.js`: verificación de cargue |
| T053 | HU-14 · Migración V11: entrega, evidencia y novedad | Cristian Danilo Pineda Ramirez | Cesar Johan Casado Calderon | Sin dependencia | Pedido.delivery, retornos y avisos persistentes |
| T054 [P] | HU-14 · Pruebas de entrega, novedad y sincronización sin conexión | Brayan Esteban Cruz Arango | Cesar Johan Casado Calderon | Sin dependencia | `test_logistics.py` + prueba de IndexedDB en navegador |
| T055 | HU-14 · API de entregas con carga de evidencias | Cesar Johan Casado Calderon | Brayan Esteban Cruz Arango | T053, T054 | `logistics.py`: validación y persistencia de evidencia |
| T056 | HU-14 · App PWA del conductor con modo sin conexión (IndexedDB) | Cristian Danilo Pineda Ramirez | Brayan Esteban Cruz Arango | T055 | `driver-store.js`, service worker y vista móvil |
| T057 [P] | HU-15 · Pruebas de privacidad y línea de tiempo | Brayan Esteban Cruz Arango | Cesar Johan Casado Calderon | Sin dependencia | `test_logistics.py`: 404 ajeno y timeline |
| T058 | HU-15 · Servicio de eventos de estado y cálculo de hora estimada | Cesar Johan Casado Calderon | Brayan Esteban Cruz Arango | T057 | `logistics.py`: tracking y ETA |
| T059 | HU-15 · Vista de seguimiento en el portal | Cristian Danilo Pineda Ramirez | Cesar Johan Casado Calderon | T058 | `logistics.js`: seguimiento propio y actualización periódica |

La portada, la distinción visual de los diez perfiles y la compatibilidad de invitaciones antiguas son requisitos adicionales solicitados el 20 de noviembre. Evidencia: `landing.html`, `landing.css`, `farm.jpg`, `logistics.css` y `landing.js`.

Estado técnico: implementado para revisión. Antes de cerrar, registrar las decisiones de las cuatro puertas en [Registro SDD](Registro_SDD.md), subir evidencias al tablero y completar las pruebas de dispositivo/staging.
