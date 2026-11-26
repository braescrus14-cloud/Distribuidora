# Paso a paso · Comprobar que el Sprint 3 está publicado y funciona

**Aplicación:** [Villali en Render](https://villali-staging.onrender.com/) · **Ingreso:** [Mi espacio](https://villali-staging.onrender.com/entrar) · **Repositorio vigente:** [braescrus14-cloud/Distribuidora, main](https://github.com/braescrus14-cloud/Distribuidora/tree/main).

**Publicación comprobada el 21 de noviembre de 2026:** [commit de aplicación 7796943](https://github.com/braescrus14-cloud/Distribuidora/commit/7796943c9e73769c766ace322f5180c7c813240d). Las CI del mismo código terminaron correctamente: [Sprint 1](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/44951305192), [Sprint 2](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/44951305297) y [Sprint 3](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/44951305330). Se verificaron por HTTP la portada nueva y el CSS unificado, y en el navegador publicado los testimonios académicos. Los recorridos operativos siguientes se registran cuando el equipo los ejecute.

Hay dos comprobaciones diferentes: **publicación** (qué versión está en Render) y **funcionamiento** (qué hacen HU-11 a HU-15). Ver solo la portada no demuestra que todo el sprint haya sido aceptado.

## 1. Comprueba que estás en el GitHub correcto

1. Abre el enlace de la rama `main` indicado arriba. Comprueba propietario `braescrus14-cloud` y nombre `Distribuidora`.
2. En el README, busca **Las dos carpetas principales** y **Confirmar cada sprint**. Deben aparecer los cuatro expedientes y el proyecto integrado.
3. Abre [sprint/sprint-2](../sprint-2/README.md) y [sprint/sprint-3](README.md). En Sprint 3 debes encontrar especificación, plan, tareas, registro SDD, tabla de pruebas, `VERIFICACION.md` y esta guía.
4. Si ves solo Sprint 1 y el commit `d537a85`, revisa que no sea un fork, una rama de archivo o una URL fijada a un commit antiguo. Entra de nuevo por el enlace directo a `main`.

## 2. Verifica el despliegue en Render

1. Abre Render → **villali-staging → Deploys**.
2. Busca la fila más reciente con estado **Live**. Abre su commit y anota el identificador completo. Un despliegue fallido nuevo no reemplaza necesariamente al anterior que sigue Live.
3. En GitHub → **Actions**, comprueba las cuatro CI correspondientes al mismo commit de aplicación. Deben estar en verde.
4. Comprueba que el servicio sigue en **Free**, rama `main`, carpeta raíz `proyecto-completo`. Esa carpeta contiene los cuatro sprints integrados. [Ajuste de carpeta raíz](../../proyecto-completo/documentacion/Despliegue_Render.md).
5. Conserva las variables de MongoDB existentes. No copies su contenido a capturas ni al repositorio. No crees otra base ni actives cargas iniciales.
6. Abre Villali y usa **Ctrl + F5**. En celular, actualiza con conexión antes de probar la jornada sin red.

**Comprobación pública rápida:** deben aparecer la portada, las cuatro líneas, las fichas técnicas y la demo de seguimiento. El login tiene **Correo o usuario** y **Contraseña**, sin selector Clientes/Equipo. La demo de la portada es ilustrativa: las funciones reales se comprueban dentro del portal con los roles siguientes.

## 3. Prepara cuentas y un pedido de ensayo

| Cuenta / rol | Módulo del Sprint 3 que debe ver |
| --- | --- |
| Auxiliar de Bodega · 04 | Alistamiento FEFO |
| Jefe de Bodega · 03 | Alistamiento FEFO y Cargue y manifiestos |
| Coordinador de Logística · 07 | Planificar distribución |
| Conductor · 08 | Mis entregas |
| Cliente · 10 | Seguimiento de pedidos y Portal de pedidos, solo de su ficha |

El Administrador del Sistema 02 crea o habilita cuentas; no recibe todos los módulos operativos por ser administrador. Inicia con la cuenta que corresponde a cada prueba. No publiques contraseñas.

1. El Asesor 06 necesita un cliente activo con zona, cuenta de Cliente vinculada y un producto activo con saldo vigente. Puedes prepararlo con la [guía del Sprint 2](../sprint-2/Guia_Verificacion_Sprint_2.md).
2. Crea un pedido de ensayo de **5 unidades** de un producto que tenga al menos 5 disponibles. Anota número `PV-…`, SKU, EAN, lotes, existencia física, reservado y disponible. Usa un nombre o referencia que permita reconocer el ensayo.
3. Confirma el pedido con Asesor. Debe quedar **Confirmado**: reservado aumenta en 5, disponible baja en 5 y físico permanece igual.
4. Para demostrar FEFO con dos lotes, elige un producto que realmente tenga reservas repartidas entre dos lotes vigentes. No inventes el EAN: cópialo de Catálogo. No borres ni reemplaces inventario para preparar la prueba.

## 4. HU-11 · Alistar el pedido por vencimiento

1. Ingresa con Auxiliar 04 o Jefe 03 y abre **Alistamiento FEFO**.
2. Localiza el `PV-…` del paso anterior. Revisa lote, ubicación, vencimiento y cantidad asignada a cada línea.
3. Pulsa **Escanear producto** e introduce primero un EAN incorrecto. Debe rechazarse sin marcar la línea; el aviso sonoro depende de que el dispositivo tenga audio habilitado.
4. Ingresa el EAN correcto de Catálogo, manualmente o con lector USB/Bluetooth que escriba como teclado. Debe aparecer **Producto verificado**.
5. Completa todas las líneas. **Finalizar alistamiento** solo se habilita al verificarlas.
6. Confirma **Descontar inventario y alistar**. Debe pasar a **Alistado**. Para el ejemplo de 5 unidades, físico y reservado bajan en 5 respecto a antes de finalizar; no se descuenta dos veces al actualizar.
7. Descarga **rótulo QR**. Guarda el PDF y una captura de los saldos antes y después.

## 5. HU-12 · Planificar una ruta

1. Entra con Logística 07 → **Planificar distribución**.
2. Pulsa **Registrar vehículo**. Para el ensayo puedes usar placa `DEM-321` y capacidad **400 kg**; no representa un vehículo real.
3. En **Peso por unidad**, selecciona el SKU del pedido. Si la unidad de venta es un bulto de 40 kg, escribe **40**, no el peso total del pedido.
4. En **Dirección de entrega**, selecciona el cliente y registra dirección, latitud y longitud de ensayo válidas. Por ejemplo, destino `7.13, -73.11` y origen de bodega `7.12, -73.12`; son coordenadas de demostración, no la ubicación de Villali.
5. Pulsa **Planificar ruta**, elige vehículo, una cuenta activa de Conductor, salida prevista, coordenadas de bodega y pedidos **Alistados** de la misma zona.
6. Comprueba la capacidad: 5 bultos × 40 kg = **200 kg**, que caben en 400 kg. Si pruebas un vehículo con capacidad inferior a la carga, el sistema debe rechazar la ruta; no cambies el peso del producto para evadir la validación.
7. Crea la ruta válida. Debe mostrar número, visitas ordenadas, peso y mapa. Anota el identificador. No debe asignarse el mismo conductor o vehículo a dos rutas pendientes simultáneas.

El mapa organiza por proximidad geográfica y la ETA es aproximada. No es navegación vial ni seguimiento GPS en vivo.

## 6. HU-13 · Cargar y despachar

1. Entra como Jefe 03 → **Cargue y manifiestos**.
2. Abre la ruta de ensayo y revisa sus pedidos.
3. Prueba un rótulo que no pertenezca a esa ruta: debe rechazarse sin sumar cargue.
4. En **Rótulo del pedido**, escanea el QR o escribe el número `PV-…` válido de cada pedido. El cargue repetido no debe duplicarse.
5. **Emitir manifiesto y despachar** solo se habilita al cargar todos los pedidos de la ruta.
6. Confirma salida y abre **manifiesto PDF**. Debe tener `MD-…`, vehículo, conductor, peso y visitas. Ruta y pedidos pasan a **En ruta**.

## 7. HU-15 · Ver seguimiento como cliente

1. Ingresa con la cuenta de Cliente 10 vinculada al pedido, no con una cuenta genérica sin ficha.
2. Abre **Seguimiento de pedidos** y localiza el `PV-…`.
3. Comprueba la línea de tiempo: Confirmado → Alistado → En ruta. Durante la ruta deben mostrarse ETA aproximada y entregas pendientes anteriores cuando correspondan.
4. Una segunda cuenta de Cliente no debe poder consultar ese pedido ni sus evidencias privadas. Verifica este caso con dos clientes de ensayo distintos.

## 8. HU-14 · Registrar entrega

1. Ingresa con el Conductor 08 asignado → **Mis entregas**. Debe ver sus rutas y pedidos.
2. Abre **Registrar entrega**. Para una entrega completada registra firma, foto y ubicación, concediendo los permisos solicitados en el dispositivo.
3. Confirma. Debe cambiar a **Entregado** y conservar fecha de captura y de recepción.
4. Logística consulta la evidencia autorizada; el Cliente ve su estado actualizado sin acceso a la foto/firma operativa privada.
5. Para un ensayo separado, usa otro pedido y registra **Novedad** con observación. Logística recibe el aviso y Bodega ve el retorno pendiente. Solo al recibir físicamente ese retorno debe reintegrarse la cantidad al lote una vez.

No simules una entrega real sobre un pedido ajeno al ensayo. Las imágenes y firmas utilizadas en la demostración deben estar autorizadas.

## 9. Verifica trabajo sin conexión y persistencia

1. Para probar la cola offline prepara **tres pedidos En ruta** del mismo conductor y abre su jornada con conexión.
2. Desconecta la red; registra las tres confirmaciones y comprueba el contador de pendientes. Recarga en ese mismo navegador: los pendientes deben conservarse.
3. No borres datos del sitio ni uses modo privado. Recupera conexión y pulsa **Sincronizar y actualizar** si hace falta. Si la sesión venció, entra con la misma cuenta.
4. Confirma cero pendientes y una sola entrega por pedido desde otra cuenta autorizada.
5. Para Atlas, el responsable del servicio puede reiniciar el mismo servicio en Render y volver a consultar pedidos, rutas y evidencias guardados. No cambies `MONGODB_DATABASE`, no resembres datos y no borres colecciones.

## 10. Registra lo que vas a presentar

Usa la [tabla de verificación del Sprint 3](Tabla_Verificacion_Sprint_3.md). Por cada prueba anota **Aprobada / Falló / No ejecutada**, fecha, responsable y captura o PDF. Adjunta:

- Commit Live de Render y CI verde del mismo código.
- Pedido `PV-…`, ruta y manifiesto `MD-…` utilizados.
- Capturas de estados y saldos antes/después, rótulo y manifiesto PDF.
- Evidencia de entrega, ensayo sin red y comprobación tras reinicio, si se ejecutaron.
- Aceptación por historia y decisiones SDD solo cuando las personas responsables las confirmen, en [Registro SDD](Registro_SDD.md).

## Si no ves un módulo o no hay datos

| Síntoma | Comprobar |
| --- | --- |
| GitHub muestra solo Sprint 1 | Propietario correcto, rama main y URL sin commit antiguo. |
| Render muestra la portada anterior | Commit de la fila Live; después Ctrl + F5. No basta con que un despliegue previo siga Live. |
| Falta el menú de logística | Rol 07, no Administrador 02 ni Asesor 06. |
| Alistamiento vacío | Pedido confirmado con reservas y sin ruta; catálogo sin stock no genera pedidos alistables. |
| Planificar ruta deshabilitado | Pedido alistado, vehículo activo y Conductor activo; pesos y destinos configurados. |
| Cliente sin pedidos | Cuenta vinculada a la ficha del pedido; no usar la de otro cliente. |
| Conductor sin entregas | Asignación a ese conductor y ruta ya despachada. |
| GPS/cámara fallan | HTTPS, permisos y dispositivo; registrar fallo, no dar la prueba por aprobada. |
