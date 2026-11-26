# Revisión de portada, acceso y animaciones · Sprint 3

[Estado consolidado y cierre documental del 25/11](../Informe_Consolidado_Sprint_3.md). Esta revisión se conserva como parte del historial.

> Actualización posterior: [acceso único, lectores públicos y pie académico](Simplificacion_Acceso_y_Portada.md). Sustituye las decisiones de indexación y separación Clientes/Equipo descritas en esta revisión.

Fecha: 21 de noviembre de 2026. Base anterior: `65a7e332315f475f26afef16b8bba7ece2932618`. Se conserva el titular «El campo nos mueve. Tu producción, también.», la propuesta de valor y los nombres de las secciones. No cambia la lógica operativa de las historias de los tres sprints ni se importan o reemplazan saldos de MongoDB.

## Cambios y problema que resuelven

| Cambio | Problema resuelto |
| --- | --- |
| Pie con razón social, NIT, ciudad, dirección, horarios y redes oficiales editables. | El visitante identifica qué información falta confirmar sin recibir datos supuestos. |
| Tiempo de respuesta y horario bajo Enviar solicitud. | Aclara la expectativa de contacto; conserva marcadores mientras falta el compromiso real. |
| Sitio web como campo trampa fuera de pantalla, `tabindex=-1`, `aria-hidden=true`, `autocomplete=off`. | El productor no ve ni completa un campo ajeno a su solicitud; los robots no crean registros. |
| WhatsApp en barra superior fija, mensaje precargado y espacio seguro en móvil. | Mantiene un contacto accesible sin tapar el formulario ni duplicar el acceso a Ingresar. |
| Cerrar aviso, Cerrar ficha técnica y Volver al ingreso. | Los controles explican qué cierran y no aparecen fuera de sus diálogos. |
| Tres indicadores y dos testimonios preparados junto a la solicitud. | La prueba social solo se publica cuando hay cifras reales y autorización; los borradores quedan privados. |
| Doce fichas con fuente original, composición cuando está confirmada, etapa y modo de uso. | El visitante puede profundizar sin inventar equivalencias ni presentaciones. |
| Consultar esta línea selecciona el interés en el formulario. | Evita que el productor repita su selección. |
| Fotografías de avicultura, porcicultura, ganadería y equinos; retirada una tarjeta superpuesta. | La portada representa las cuatro líneas y los pies de foto se leen sin solapamientos. |
| Animaciones de entrada por opacidad, sin mover contenedores; demo con altura reservada. | Evita saltos al desplazarse y cambiar de estado; respeta movimiento reducido. |
| Login con etiquetas visibles, Clientes/Equipo, recuperación y fondo oscuro. | Mantiene la continuidad visual y deja claros el acceso y los errores. |
| Modo de publicación explícito y metadatos revisados. | Staging continúa sin indexación y la transición futura a producción queda controlada. |

## Validación realizada

- Suite HTTP de solicitudes públicas, permisos, consentimiento, anti-spam, recuperación de un solo uso y persistencia tras reiniciar: correcta en SQLite local. Incluye publicación/retiro de testimonio y privacidad del borrador.
- Navegador Edge Chromium local: 1440, 390 y 320 px, sin desbordamiento horizontal; WhatsApp visible al desplazarse, honeypot fuera de pantalla, 12 fichas, selector de interés y movimiento reducido correctos.
- Los cuatro estados de la demo conservan la misma altura en cada ancho (603,52 px escritorio y 586,75 px móvil en la prueba).
- Inicio de sesión de diez roles: tableros accesibles, permisos conservados y contenedor sin transformación durante el scroll. Cambio de módulo vuelve al inicio de la pantalla.
- Los resultados de CI y el despliegue se registran cuando terminen; estas pruebas no sustituyen aceptación por los responsables ni pruebas físicas con el dispositivo de bodega.

## Fuentes y pendientes de productos

Las fuentes oficiales se revisaron el 21 de noviembre de 2026; el catálogo de trabajo conserva las diez referencias originales. SUPER TERNERAS y SUPER NOVILLAS amplían la consulta de crianza con disponibilidad pendiente, sin crear stock. Se descartaron fórmulas de otros países. No se asumió que la variante Naranja 360 fuera equivalente a la referencia antigua ni se corrigió por intuición el valor negativo de fibra publicado para POLLO CRIOLLO.

- [SUPER POLLO ENGORDE](https://italcol.com/producto/super-pollo-engorde-granja/)
- [POLLO CRIOLLO](https://italcol.com/producto/pollo-criollo/)
- [SUPER HUEVO PREPICO](https://italcol.com/producto/super-huevo-prepico/)
- [Cerdo Levante 1 Naranja](https://italcol.com/producto/cerdo-levante-1-naranja-360/)
- [Cerdo Engorde Naranja](https://italcol.com/producto/cerdo-engorde-naranja-360/)
- [Cerda Gestación Naranja](https://italcol.com/producto/cerda-gestacion-naranja/)
- [CREMOSA FIBRA DIGESTIBLE](https://italcol.com/producto/producto-cremosa-fibra-digestible/)
- [ITAL LECHE](https://italcol.com/producto/ital-leche/)
- [BRÍO YEGUAS](https://italcol.com/producto/brio-yeguas/)
- [BRIO SPORT](https://italcol.com/producto/brio-sport/)
- [SUPER TERNERAS](https://italcol.com/producto/super-terneras/)
- [SUPER NOVILLAS](https://italcol.com/producto/super-novillas/)

[Lista completa de datos pendientes](../Datos_Pendientes_Confirmacion.md).

## Imágenes

Nueva imagen ilustrativa `sprint-1/horses.jpg`, generada con ImageGen y comprimida a 900 px, JPEG de aproximadamente 111 KiB. No afirma representar instalaciones de Villali. Prompt: “Two healthy chestnut adult horses grazing in a lush Colombian paddock, warm morning light, deep green and gold palette, realistic anatomy, no people, logos or text”. Se conservan las imágenes ilustrativas de campo, galpón y cerdos.

## Publicación y datos

El servicio actual continúa en plan gratuito y staging. No cambiar `MONGODB_URI` ni `MONGODB_DATABASE`, no reinicializar el almacén ni sembrar catálogo al arrancar. La actualización agrega campos opcionales a la configuración existente y conserva valores que una edición parcial no envíe. No se modifica el esquema de IndexedDB de la jornada sin conexión. Se renueva solo la caché de recursos del service worker.

Para el futuro dominio de producción, configurar `VILLALI_SITE_MODE=production` y el origen público correcto según el arranque existente. La portada y sus recursos públicos dejan de emitir `noindex,nofollow,noarchive`; `/entrar`, la API y las respuestas de error mantienen la restricción. `robots.txt` de producción excluye `/entrar` y `/api/`. El modo predeterminado es staging. Favicon SVG y Open Graph (título, descripción e imagen absoluta de galpón) permanecen presentes. La prueba HTTP verificó ambos modos; no se habilitó indexación en Render staging.
