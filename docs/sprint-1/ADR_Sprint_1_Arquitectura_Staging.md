# Decisión de arquitectura para staging del Sprint 1

**Estado** · Propuesta para aprobación en la Puerta 2.

El frontend de Villali usa HTML, CSS y JavaScript sin compilación. La versión
implementada sirve la API con Python y conserva los datos en SQLite. El taller
propone React y TypeScript, Java 21 con Spring Boot y PostgreSQL. El equipo debe
resolver esa diferencia antes de dar por aprobada la arquitectura.

## Decisión propuesta

Aceptar la implementación actual para la revisión del Sprint 1 en un único
servicio de staging. Usar una base SQLite independiente en disco persistente.
Mantener el navegador y la API bajo el mismo origen HTTPS. Las invitaciones y
las alertas de bloqueo salen mediante la API HTTPS de Resend. Las credenciales
se configuran como secretos del entorno.

La decisión preserva los flujos que se pueden revisar hoy. Si la arquitectura del
taller es un requisito obligatorio, registrar esa condición en la Puerta 2 y
programar la migración antes de declarar conformidad con el taller.

## Evidencia requerida

- CI en verde para el commit que se va a desplegar.
- URL HTTPS de staging y respuesta satisfactoria de `/health`.
- Alta y activación por correo, bloqueo y recepción de la alerta en una cuenta de ensayo.
- Verificación de que un reinicio conserva los datos de staging.
- Decisión, nombre, fecha y observaciones del responsable de la Puerta 2.
