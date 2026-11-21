# Sprint 3 · Distribución y entrega

**Proyecto:** Distribuidora Villali · **Historias:** HU-11 a HU-15 · **Estimación del backlog:** 21 puntos.

El incremento conecta los pedidos confirmados del Sprint 2 con bodega, rutas, despacho y entrega. La entrada pública presenta la empresa a productores rurales; el acceso al sistema permanece separado en `/entrar`.

## Anexos

- [Especificación y criterios de aceptación](spec.md): alcance de las cinco historias y de la página pública.
- [Plan técnico y arquitectura](plan.md): almacenamiento en MongoDB, contratos, permisos, PWA y límites de la estimación de rutas.
- [Tareas y trazabilidad](tasks.md): correspondencia T041–T059 del Excel con código y evidencias.
- [Guía de pruebas por rol](pruebas.md): recorrido para compañeros y profesor, incluidos casos negativos y trabajo sin conexión.
- [Revisiones SDD y aceptación](Registro_SDD.md): cuatro puertas y cinco historias para ratificación por los responsables.

## Versiones para comparar

| Versión | Fuente |
| --- | --- |
| Sprint 1 histórico | [Rama sprint-1-archivo](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-1-archivo/sprint-1) |
| Sprints 1 y 2 antes de este incremento | [Rama sprint-2-archivo](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-2-archivo), conservada en `bd7e69b83c5ef8bee8c1df1b333d4e7fa7511db4` |
| Aplicación integrada con Sprint 3 | [Código en main/sprint-1](../../sprint-1) |

La carpeta operativa conserva el nombre `sprint-1` para respetar la configuración del servicio existente de Render. El nombre de la carpeta no restringe las historias integradas. No se duplicó la base de datos ni se reemplazaron sus saldos.

## Entorno

- [Portada de Villali](https://villali-staging.onrender.com/).
- [Acceso a clientes y equipo](https://villali-staging.onrender.com/entrar).
- [CI del Sprint 3](https://github.com/braescrus14-cloud/Distribuidora/actions/workflows/sprint-3.yml).

El despliegue se debe comprobar contra el commit publicado en `main`. Una URL disponible por sí sola no demuestra que tenga la versión nueva.
