# Distribuidora Villali

Proyecto académico de gestión agropecuaria con cuatro sprints, veinte historias y diez roles. La aplicación usa HTML, CSS y JavaScript en la interfaz, Python en el servidor y MongoDB Atlas en Render. DIAN y PSE son simuladores académicos, sin validez fiscal ni movimientos de dinero real.

## Las dos carpetas principales

| Carpeta | Qué encontrarás |
| --- | --- |
| **[sprint](sprint/README.md)** | Información de los Sprints 1, 2, 3 y 4, anexos, guías de prueba y cómo confirmar cada uno |
| **[proyecto-completo](proyecto-completo/README.md)** | Código integrado de los cuatro sprints, instalación y documentación de entrega |

```text
sprint/
  sprint-1/          HU-01–05 · Acceso, catálogo e inventario
  sprint-2/          HU-06–10 · Compras, clientes y pedidos
  sprint-3/          HU-11–15 · Distribución y entrega
  sprint-4/          HU-16–20 · Facturación, recaudo y cierre
proyecto-completo/   Programa integrado y documentación general
.github/workflows/  Pruebas automatizadas por sprint
render.yaml         Configuración del servicio
```

## Confirmar cada sprint

| Sprint | Guía de prueba | Cómo verificar y registrar aceptación |
| --- | --- | --- |
| 1 | [Paso a paso](sprint/sprint-1/Guia_Verificacion_Sprint_1.md) | [VERIFICACION](sprint/sprint-1/VERIFICACION.md) |
| 2 | [Paso a paso](sprint/sprint-2/Guia_Verificacion_Sprint_2.md) | [VERIFICACION](sprint/sprint-2/VERIFICACION.md) |
| 3 | [Paso a paso](sprint/sprint-3/Guia_Verificacion_Sprint_3.md) | [VERIFICACION](sprint/sprint-3/VERIFICACION.md) |
| 4 | [Paso a paso](sprint/sprint-4/Guia_Verificacion_Sprint_4.md) | [VERIFICACION](sprint/sprint-4/VERIFICACION.md) |

[Aplicación](https://villali-staging.onrender.com/) · [Ingresar](https://villali-staging.onrender.com/entrar) · [CI de los cuatro sprints](https://github.com/braescrus14-cloud/Distribuidora/actions) · [Versiones históricas](proyecto-completo/documentacion/Versiones.md).

El código histórico de cada cierre sigue conservado en sus etiquetas. La carpeta `proyecto-completo` contiene el programa vigente. **Para desplegar esta estructura, la carpeta raíz del servicio de Render debe ser `proyecto-completo`**; conservar el plan gratuito y las variables actuales de Atlas. [Ajuste de Render paso a paso](proyecto-completo/documentacion/Despliegue_Render.md).
