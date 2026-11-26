# Simplificación de acceso y portada

21 de noviembre de 2026. Ajuste posterior a la revisión UX final, según la nueva indicación del usuario. Estas decisiones sustituyen las referencias anteriores a Clientes/Equipo y al bloqueo completo de staging.

- Acceso único por correo registrado o usuario y contraseña. El servidor identifica el rol y conserva sus permisos. Los usuarios existentes siguen funcionando. Si dos cuentas tienen el mismo correo, el inicio por correo se rechaza con el error genérico y se debe usar el usuario o corregir el correo; nunca se selecciona una cuenta arbitraria.
- La portada no emite `noindex` en HTML ni en cabecera, incluso en staging. `robots.txt` permite la portada y el formulario público `/entrar`, y excluye `/api/`. El formulario de ingreso conserva `noindex` para evitar que se indexe, pero los lectores pueden abrirlo; la autenticación continúa obligatoria para las funciones privadas. Se permite evaluar la portada con lectores automáticos sin cambiar variables de Render.
- Un único llamado principal a solicitar cuenta. Se retiraron enlaces repetidos del menú, del pie, de Cómo comprar y del hero. Las fotografías llevan a las tarjetas individuales de cada línea. Las cuatro consultas abren WhatsApp con la línea de interés en el mensaje; las fichas abren el detalle de cada producto.
- Pie completo con datos de ejemplo académicos: Distribuidora Villali S.A.S.; NIT 000.000.000-0; Bucaramanga, Santander; Calle del Campo 12-34; horario lunes a viernes de 8 a. m. a 5 p. m.; correo reservado villali@example.com y perfiles ilustrativos. El pie identifica el carácter académico; no se atribuyen estos datos a la empresa real ni se enlazan cuentas sociales ajenas. El teléfono sí es el autorizado por el usuario. Los valores confirmados que configure el administrador sustituyen los ejemplos.
- No se inventaron testimonios, cifras de ventas ni aprobaciones de las historias. Esos marcadores y los pendientes técnicos del fabricante continúan diferenciados de los datos ilustrativos del pie.

Pruebas: inicio por usuario y correo sin selector, mayúsculas en correo y rechazo de correo compartido; restricciones por rol conservadas. Respuestas públicas, recuperación de acceso y persistencia se prueban en CI. Revisión responsive y de destinos en navegador local. El resultado de publicación se registra al verificar el servicio.

## Publicación verificada

Commit de aplicación `e92ed9740b01e29795db81aa80a242ee65e64200`, confirmado Live por el usuario el 21 de noviembre de 2026 en el servicio existente y gratuito.

- [CI Sprint 1 correcta](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/44949991719).
- [CI Sprint 2 correcta](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/44949991716).
- [CI Sprint 3 correcta](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/44949991689).
- Verificación HTTP en Render: portada 200 sin cabecera ni meta noindex; robots con Allow raíz y exclusión de API; login con app.js v18, sin selector de acceso; un enlace Ingresar y cuatro consultas con línea específica.
- Pie completo sin marcadores de confirmación y con identificación académica. La API de sesión sin autenticación responde 401. No se ingresaron datos de prueba en la base desplegada.
- Copia de código y documentación actualizada en C:/Distribuidora/Sprint3. Respaldo anterior en la etiqueta historial/sprint-3-antes-acceso-unico.
