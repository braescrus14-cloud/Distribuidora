# Distribuidora Villali

Aplicación académica para gestionar acceso, catálogo, inventario, compras, pedidos, distribución y recaudo. Integra **los cuatro sprints y las veinte historias de usuario** en un solo programa, con diez roles y persistencia en MongoDB Atlas. DIAN y PSE funcionan mediante simuladores académicos, sin validez fiscal ni movimientos de dinero real.

**[Abrir Villali](https://villali-staging.onrender.com/)** · [Ingresar](https://villali-staging.onrender.com/entrar) · **[Documentación completa](docs/README.md)** · [Versiones de los sprints](docs/Versiones.md)

## Revisar y probar cada sprint

| Sprint | Historias | Funciones | Documentación | Paso a paso |
| --- | --- | --- | --- | --- |
| 1 | HU-01–05 | Acceso, roles, catálogo y lotes | [Plan y criterios](docs/sprint-1/Sprint_1_Villali.md) | [Guía base](sprint-1/README.md#probar-las-cinco-historias) |
| 2 | HU-06–10 | Proveedores, compras, clientes y pedidos | [Expediente](docs/sprint-2/README.md) | [Probar Sprint 2](docs/sprint-2/Guia_Verificacion_Sprint_2.md) |
| 3 | HU-11–15 | Alistamiento, rutas, despacho y entrega | [Expediente](docs/sprint-3/README.md) | [Probar Sprint 3](docs/sprint-3/Guia_Verificacion_Sprint_3.md) |
| 4 | HU-16–20 | Facturación, pagos, reportes y cierre | [Expediente](docs/sprint-4/README.md) | **[Probar Sprint 4](docs/sprint-4/Guia_Verificacion_Sprint_4.md)** |

## Estructura del repositorio

```text
.github/workflows/   Pruebas automatizadas de los cuatro sprints
docs/               Documentación, guías, evidencias e historial
sprint-1/           Aplicación integrada de los cuatro sprints
README.md           Entrada y navegación del proyecto
render.yaml         Configuración del servicio existente
```

La carpeta del programa conserva el nombre `sprint-1` porque Render usa esa ruta. Contiene la aplicación vigente completa. El código anterior de cada sprint se consulta desde **Tags**, sin duplicar carpetas del programa en `main`.

## Ejecutar, comprobar y presentar

- [Instalación en Windows](sprint-1/README.md#ejecutar-en-windows).
- [Entrega y recorrido de los cuatro sprints](docs/Entrega_Proyecto.md).
- [GitHub Actions](https://github.com/braescrus14-cloud/Distribuidora/actions): revisar las cuatro CI del commit evaluado.
- [Informe de revisión integral](docs/Revision_Integral_2026-11-25.md): accesos, permisos, pruebas y corrección móvil.
- [Versión publicada en Render](https://villali-staging.onrender.com/version) y [salud del servicio](https://villali-staging.onrender.com/health): comparar el commit con la ejecución de CI y el despliegue Live.

## Versiones y datos

`main` contiene el trabajo vigente. Las etiquetas **sprint-1**, **sprint-2**, **sprint-3** y **sprint-4** conservan sus cierres; las variantes intermedias quedan bajo `historial/`. [Consultar las copias, sus commits y las comparaciones](docs/Versiones.md).

Render conserva el servicio gratuito y la misma base Atlas. No cambiar las variables de MongoDB ni ejecutar semillas al actualizar código. Las copias de Git contienen código y documentación; no son respaldos de los datos privados de la empresa. Las decisiones SDD y la aceptación de historias se registran por sus responsables en cada expediente.
