# Portada y experiencia por rol · Revisión de diseño

Se conservan la propuesta «El campo nos mueve. Tu producción, también.» y las secciones Líneas de nutrición y Cómo comprar. La revisión corrige la continuidad con el acceso y añade orientación por responsabilidad sin ampliar los permisos de los Sprints 1–3.

| Cambio | Problema que resuelve |
| --- | --- |
| WhatsApp +57 320 742 4661 y teléfono visibles | Ofrece un canal real autorizado por el usuario para quien todavía no tiene cuenta. |
| Solicitar mi cuenta como CTA principal; un solo Ingresar en la navegación | Separa la captación de productores nuevos del acceso a cuentas existentes. |
| Formulario persistente y bandeja del administrador | La solicitud produce un registro atendible, sin simular un correo enviado ni crear una cuenta automáticamente. |
| CSS público aislado y alturas determinadas por el contenido | Evita que las reglas del panel interno recorten o superpongan el texto de portada. |
| Verde profundo, vidrio y ondas compartidos con el acceso | Mantiene continuidad visual al pasar de la portada al login. |
| Fotografías avícola y porcina, con referencias por línea | Muestra las actividades principales y productos concretos del catálogo. |
| Iconos SVG con un mismo trazo | Sustituye emojis de apariencia variable entre dispositivos. |
| Demostración controlable de cuatro estados | Explica el seguimiento antes de que el visitante tenga un pedido o una cuenta. |
| Ondas animadas, aparición por sección y microinteracciones | Aporta movimiento sin añadir librerías pesadas ni alterar los datos operativos. |
| Acceso único por correo o usuario y recuperación de contraseña | Reconoce el rol desde la cuenta y permite solicitar un enlace seguro al correo registrado. |
| Inicio propio para cada rol | Diferencia la estructura, la prioridad y el recorrido, además de la paleta. |
| Favicon y Open Graph; portada y formulario legibles por lectores automáticos | Mejora la presentación al compartir. La portada permite indexación; el acceso conserva noindex y la API permanece protegida. |

> Estado final consolidado: [informe del Sprint 3](Informe_Consolidado_Sprint_3.md). Las evidencias históricas del 20/11 al final de este documento se conservan como historial, no como configuración actual.

## Espacios de trabajo

| Rol | Estructura de Inicio |
| --- | --- |
| Gerencia | Resumen ejecutivo, indicadores reales y órdenes pendientes de aprobación. |
| Administración | Consola de acceso, distribución de cuentas, solicitudes y auditoría. |
| Jefe de Bodega | Tablero de tres etapas: preparar, alistados y cargue; retornos y acceso a lotes. |
| Auxiliar de Bodega | Mesa centrada en el siguiente pedido y sus pasos de preparación. |
| Compras | Flujo proveedor–orden–recepción con proveedores y órdenes recientes. |
| Asesor Comercial | Mesa de solicitudes por revisar y clientes vinculados. |
| Logística | Centro de distribución con ruta activa, visitas y capacidad operativa. |
| Conductor | Inicio móvil, conexión, entregas propias y pendientes del dispositivo. |
| Contabilidad | Hoja de consulta de existencias; no incorpora facturación de un futuro sprint. |
| Cliente | Espacio de su finca y progreso de su último pedido, sin datos de otros clientes. |

Los indicadores proceden de endpoints ya autorizados. La consulta de inventario devuelve hasta 25 referencias; el inicio contable presenta esa consulta y no afirma que sea el total global de la bodega. No se añadieron cifras comerciales ni testimonios sin respaldo.

## Contacto y datos públicos

El teléfono fue proporcionado y autorizado para publicación en el chat. No se dirige correo a un Gmail inventado. El formulario entrega solicitudes a la bandeja **Solicitudes y contacto** del Administrador, donde también se configuran correo real, razón social, NIT, dirección y horarios. Los campos vacíos se omiten de la portada. El correo `contacto@villali.example` aparece únicamente como ejemplo de formato dentro de esa configuración.

Las referencias y presentaciones de las tarjetas proceden del Excel `Catalogo_Italcol_91_Productos_Sin_Imagenes.xlsx`. Se eligieron filas con presentación explícita de 40 kg y se omitieron precios orientativos. Los precios y condiciones se consultan en la cuenta y se confirman con el asesor.

## Formularios y recuperación

Las solicitudes exigen consentimiento, validación y límite de envíos. Se guardan en `commerce_records`, tipo `account_requests`, con identificador para evitar duplicados por reintento. Solo Administrador 02 las consulta y cambia su estado. Los datos de contacto usan `settings/public-contact`; no se reinician datos existentes de Atlas.

La recuperación verifica usuario y correo registrado, responde de forma genérica y usa un enlace de un solo uso válido por 30 minutos. La contraseña no cambia al solicitarlo. Al canjearlo se invalidan las sesiones anteriores. La entrega real del mensaje depende de `RESEND_API_KEY`, `VILLALI_MAIL_FROM` y del correo registrado; las pruebas usan un remitente simulado.

## Accesibilidad y rendimiento

Animaciones CSS, SVG e IntersectionObserver, sin bibliotecas adicionales. Se respeta `prefers-reduced-motion`; la demostración solo se reproduce al solicitarlo y se pausa al ocultar la pestaña. Controles de teclado, foco visible, textos de estado y etiquetas. Las imágenes se optimizaron en JPEG; las secundarias usan carga diferida.

El service worker actualiza únicamente la caché de interfaz y conserva IndexedDB. El inicio y la jornada del conductor continúan disponibles sin red cuando se abrieron previamente con conexión. Las API no se almacenan en la caché HTTP del service worker.

## Procedencia de imágenes

Generadas con la herramienta integrada de imagen, no con CLI. Archivos de aplicación: `sprint-1/poultry.jpg` y `sprint-1/pigs.jpg`, copiados al proyecto y optimizados; los originales permanecen en la carpeta de imágenes generadas de Codex. Son imágenes ilustrativas, no fotografías de instalaciones propias de Villali.

**Prompt avícola:** Photorealistic premium editorial agricultural website photograph, landscape 3:2. Clean open-sided Colombian commercial broiler house, healthy white chickens on dry wood-shaving litter, red circular feeders and nipple drinker lines, airy metal roof, filtered warm morning sunlight and green tropical foliage outside. Humane well-maintained production environment, realistic anatomy and perspective, forest greens and straw tones, chicken foreground lower right, darker roof upper left. No people, text, logos or collage.

**Prompt porcino:** Photorealistic editorial agricultural photograph, landscape 3:2. Healthy pink growing pigs in a clean spacious airy shaded farm nursery pen with dry bedding, natural daylight and green tropical hills through open fencing. Foreground pig to the right, credible professional rural production, deep greens and warm earth palette. Realistic anatomy, humane husbandry, no people, text, labels, equipment brands or graphics.

[Tabla de verificación del incremento](Tabla_Verificacion_Sprint_3.md).

## Evidencia técnica de esta revisión · 20 de noviembre de 2026

Versión de aplicación: [`1162f43bce5bdcba06b8de601de9bb452e3bd0d1`](https://github.com/braescrus14-cloud/Distribuidora/commit/1162f43bce5bdcba06b8de601de9bb452e3bd0d1).

- CI satisfactoria con SQLite, PostgreSQL y MongoDB: [regresión Sprint 1](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/44856494558), [regresión Sprint 2](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/44856494510) y [Sprint 3 y portal público](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/44856494519).
- Navegador Edge en un entorno local aislado: portada a 1440 px y 390 px sin desbordamiento horizontal, solicitud recibida por el administrador, demostración de estados y movimiento reducido verificados.
- Acceso de las diez cuentas de ensayo: Inicio con la estructura correspondiente, acciones autorizadas y ausencia de errores de JavaScript/CSP. Jornada del conductor disponible después de recargar sin red.
- Recuperación probada con remitente simulado: respuesta genérica, enlace de un solo uso, contraseña anterior conservada hasta canje e invalidación de sesiones al configurar la nueva.

El despliegue y la revisión funcional en staging se registran por separado en el registro SDD. Estas pruebas no sustituyen la recepción real del correo ni las aceptaciones del equipo.
