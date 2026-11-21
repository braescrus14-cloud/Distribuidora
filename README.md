# Distribuidora Villali

Villali conecta la gestión de usuarios, catálogo e inventario del Sprint 1 con las compras y pedidos del Sprint 2 y la distribución del Sprint 3. Incluye una portada para productores rurales y espacios de trabajo diferenciados para los diez roles. Los datos operativos y las evidencias se conservan en MongoDB Atlas.

## Empieza aquí: documentación y verificación

**Repositorio vigente:** [braescrus14-cloud/Distribuidora · rama main](https://github.com/braescrus14-cloud/Distribuidora/tree/main). Si ves solo `docs/sprint-1` y el commit `d537a85`, estás viendo una versión anterior. Comprueba el propietario, la rama y que la URL no apunte a un commit archivado.

| Sprint | Historias y documentación | Paso a paso para probar | Evidencias |
| --- | --- | --- | --- |
| 1 · Acceso, catálogo e inventario | [Plan HU-01–HU-05](https://github.com/braescrus14-cloud/Distribuidora/blob/main/docs/sprint-1/Sprint_1_Villali.md) | [Guía de la aplicación base](https://github.com/braescrus14-cloud/Distribuidora/blob/main/sprint-1/README.md) | [Registro Sprint 1](https://github.com/braescrus14-cloud/Distribuidora/blob/main/docs/sprint-1/Registro_Aprobaciones_SDD_Sprint_1.md) |
| 2 · Compras y ventas | [Índice HU-06–HU-10](https://github.com/braescrus14-cloud/Distribuidora/blob/main/docs/sprint-2/README.md) | [Verificar Sprint 2 en Render](https://github.com/braescrus14-cloud/Distribuidora/blob/main/docs/sprint-2/Guia_Verificacion_Sprint_2.md) | [CI Sprint 2](https://github.com/braescrus14-cloud/Distribuidora/actions/workflows/sprint-2.yml) |
| 3 · Distribución y entrega | [Índice HU-11–HU-15](https://github.com/braescrus14-cloud/Distribuidora/blob/main/docs/sprint-3/README.md) | **[Verificar paso a paso el Sprint 3](https://github.com/braescrus14-cloud/Distribuidora/blob/main/docs/sprint-3/Guia_Verificacion_Sprint_3.md)** | [Tabla de pruebas](https://github.com/braescrus14-cloud/Distribuidora/blob/main/docs/sprint-3/Tabla_Verificacion_Sprint_3.md) · [CI](https://github.com/braescrus14-cloud/Distribuidora/actions/workflows/sprint-3.yml) |

**Los tres sprints funcionan en la misma aplicación de Render.** La carpeta de ejecución conserva el nombre `sprint-1` por la configuración del servicio; incluye las funciones de los Sprints 1, 2 y 3. No hay que crear otro servicio ni otra base de datos para probarlos.

## Aplicación y código

- **Villali en Render.** La entrada pública presenta la empresa y sus líneas. El acceso operativo está en `/entrar` y muestra los módulos habilitados para cada rol. [Abrir Villali](https://villali-staging.onrender.com/) · [Ingresar](https://villali-staging.onrender.com/entrar). Verificar la versión del último despliegue.
- **Aplicación integrada para Render.** El servicio existente toma su código de la carpeta `sprint-1` en `main`. Usa MongoDB Atlas para conservar los datos. [Ver aplicación integrada](sprint-1)
- **Versión histórica del Sprint 1.** [Ver código archivado](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-1-archivo/sprint-1)
- **Respaldo de Sprints 1 y 2.** Versión conservada antes de incorporar la distribución. [Ver `sprint-2-archivo`](https://github.com/braescrus14-cloud/Distribuidora/tree/sprint-2-archivo)
- **Cambios de los tres sprints.** [Comparar versiones](docs/Comparacion_Sprints_1_2_3.md)
- **Comparación de los sprints.** [Revisar alcance y cambios](docs/Comparacion_Sprint_1_y_2_Villali.md)
- **Arranque en Windows.** Instrucciones para ejecutar la aplicación en tu equipo, cargar el catálogo y probar el flujo de inventario. [Ver instrucciones para Windows](sprint-1/README.md)

## Sprint 3 · Alistamiento, distribución y entrega

| Historia | Funcionalidad incorporada |
| --- | --- |
| **HU-11 · Alistamiento FEFO** | Lotes reservados por vencimiento, validación de EAN y descuento físico al finalizar. |
| **HU-12 · Rutas** | Agrupación por zona, pesos, capacidad, conductor único y mapa de visitas por proximidad. |
| **HU-13 · Despacho** | Rótulos QR, comprobación del cargue por ruta y manifiesto PDF. |
| **HU-14 · Entregas** | Jornada del conductor, firma/foto/ubicación, cola sin conexión, novedades y retornos. |
| **HU-15 · Seguimiento** | Línea de tiempo del pedido propio, hora estimada y entregas pendientes anteriores. |

- [Documentación y anexos del Sprint 3](docs/sprint-3/README.md): historias, arquitectura, contrato, tareas T041–T059 y estado SDD.
- [Guía para compañeros y demostración](docs/sprint-3/Pruebas_y_Demostracion.md): recorrido por roles y prueba sin conexión.
- [Tabla de verificación del Sprint 3](docs/sprint-3/Tabla_Verificacion_Sprint_3.md): pruebas, resultados esperados y espacio para evidencias del equipo.
- [Portada y espacios por rol](docs/sprint-3/UX_Portada_y_Perfiles.md): contacto, solicitud de cuenta, recuperación de acceso, diseño y animaciones accesibles.
- [CI del Sprint 3](https://github.com/braescrus14-cloud/Distribuidora/actions/workflows/sprint-3.yml): pruebas con SQLite, PostgreSQL y MongoDB de ensayo.
- [Registro de revisiones y aceptación](docs/sprint-3/Registro_SDD.md): decisiones que deben confirmar los responsables.

La ETA y el mapa son estimaciones geográficas; no representan navegación vial ni GPS en vivo. El lector de códigos puede ingresar el valor como teclado. Las pruebas de cámara, ubicación y lector se completan con los dispositivos del equipo.

## Sprint 2 · Compras, proveedores, clientes y pedidos

| Historia | Funcionalidad incorporada |
| --- | --- |
| **HU-06 · Proveedores** | Registro de proveedores, validación del dígito de verificación del NIT y asociación de productos. Las compras se crean con proveedores activos. |
| **HU-07 · Compras y recepción** | Órdenes de compra, aprobación gerencial cuando el total supera **$10 millones COP** y recepción parcial o completa por lote. Se exige una vida útil de al menos seis meses. |
| **HU-08 · Clientes** | Fichas de mayoristas y minoristas con zona y lista de precios. Gerencia administra el cupo y la cartera. |
| **HU-09 · Pedidos de venta** | Validación de disponibilidad, precio, cupo y cartera. Al confirmar el pedido, se reservan unidades por lote y disminuye el disponible. |
| **HU-10 · Portal B2B** | Cada cuenta de cliente accede a su ficha y a sus pedidos. Los pedidos del portal quedan pendientes de revisión para el asesor. |

La versión integrada también admite **cargas adicionales de Excel** para incorporar lotes a existencias ya registradas. La validación detecta duplicados antes de guardar.

- **Guía de pruebas por rol.** Recorrido desde la creación de una compra hasta la confirmación de un pedido. [Ver guía del Sprint 2](docs/sprint-2/Guia_Verificacion_Sprint_2.md)
- **Pruebas automatizadas.** GitHub Actions verificó las historias del Sprint 2 con SQLite, PostgreSQL y MongoDB, incluida la persistencia al reiniciar la aplicación. [Ver ejecución de CI](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/43944883006)
- **Aceptación del Sprint 2.** Registra los resultados de la demostración por historia, con responsable, fecha y evidencia. [Comparar los sprints](docs/Comparacion_Sprint_1_y_2_Villali.md)

## Evidencias y documentación del Sprint 1

- **Plan y especificación.** Cronograma reprogramado, historias HU-01 a HU-05, criterios de aceptación y tareas. [Ver el plan](https://github.com/braescrus14-cloud/Distribuidora/blob/main/docs/sprint-1/Sprint_1_Villali.md)
- **Pruebas automatizadas del Sprint 1.** Evidencia histórica de GitHub Actions para el commit `17e5f09`. [Ver la ejecución de CI](https://github.com/braescrus14-cloud/Distribuidora/actions/runs/42563294259)
- **Registro SDD.** Evidencias de la aplicación, del catálogo y de la carga de inventario, junto con el estado de las aprobaciones formales. [Ver el registro](https://github.com/braescrus14-cloud/Distribuidora/blob/main/docs/sprint-1/Registro_Aprobaciones_SDD_Sprint_1.md)
- **Acta simulada de cierre.** Ejercicio académico con las fechas y decisiones simuladas de las cuatro puertas SDD y las cinco historias. [Ver el acta simulada](https://github.com/braescrus14-cloud/Distribuidora/blob/main/docs/sprint-1/Acta_Simulada_Cierre_Sprint_1_Villali.md)
- **Decisión de arquitectura.** Propuesta técnica para el entorno de demostración y diferencias con la arquitectura del taller. [Ver el ADR](https://github.com/braescrus14-cloud/Distribuidora/blob/main/docs/sprint-1/ADR_Sprint_1_Arquitectura_Staging.md)

- [Revisión final de portada y animaciones](docs/sprint-3/Revision_UX_Final.md): cambios, fuentes y validaciones.
- [Datos pendientes de confirmación](docs/sprint-3/Datos_Pendientes_Confirmacion.md): lista completa para el cliente y configuración por el administrador.

- [Acceso único y portada para evaluación](docs/sprint-3/Simplificacion_Acceso_y_Portada.md): cambios posteriores, enlaces con destinos diferenciados y datos académicos del pie.
