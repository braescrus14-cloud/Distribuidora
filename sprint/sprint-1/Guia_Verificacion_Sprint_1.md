# Paso a paso para probar el Sprint 1

Usar registros de ensayo identificables y conservar los saldos existentes. El código de los cuatro sprints se ejecuta desde `proyecto-completo`. No publicar contraseñas, cookies ni la conexión de Atlas como evidencia.

## 1. Comprobar versión y acceso

1. Abrir [CI Sprint 1](https://github.com/braescrus14-cloud/Distribuidora/actions/workflows/sprint-1.yml) y anotar el commit correcto.
2. Confirmar ese commit Live en Render y en [la versión publicada](https://villali-staging.onrender.com/version). Si se está publicando por primera vez la nueva organización, seguir el [ajuste de carpeta raíz](../../proyecto-completo/documentacion/Despliegue_Render.md).
3. Abrir [Ingresar](https://villali-staging.onrender.com/entrar) con una cuenta activa; verificar su nombre y rol. Cerrar sesión y comprobar que ya no se puede consultar información protegida.
4. Los casos de contraseña incorrecta, bloqueo y caducidad están cubiertos por `tests/smoke.py` y `tests/access.py` en bases desechables. Para demostrarlos manualmente, usar una cuenta dedicada al ensayo y no bloquear una cuenta de trabajo.

## 2. Usuarios y permisos · HU-02

1. Con Administrador 02, abrir **Usuarios y roles** y crear una cuenta de Auxiliar de Bodega 04.
2. Abrir su invitación en otro contexto de navegador, configurar una contraseña válida e ingresar sin recargar manualmente la página. El enlace debe ser de un solo uso.
3. Comprobar que el auxiliar accede a inventario y que no puede administrar usuarios.
4. Con una cuenta de ensayo, verificar que desactivarla invalida su sesión. Reactivarla cuando termine el caso. No eliminar registros ajenos al ensayo.

## 3. Catálogo · HU-03

1. Con Jefe de Bodega 03, abrir **Catálogo**. Buscar por nombre, SKU y EAN.
2. Registrar un producto de ensayo con SKU y EAN únicos, presentación, precio y mínimo. Comprobar que se guarda y aparece al consultar de nuevo.
3. Probar un EAN duplicado: debe rechazarse sin crear otra referencia. Otros roles de consulta no deben poder modificar productos.

## 4. Excel de inventario · HU-04

1. Abrir **Importar inventario** y descargar la plantilla.
2. Copiar un **SKU activo que exista en ese catálogo**. Agregar un lote nuevo, vencimiento futuro, cantidad entera positiva y ubicación. El Excel de catálogo no reemplaza este Excel de lotes.
3. Validar el archivo: comprobar filas y unidades antes de confirmar. Una fila con SKU desconocido debe mostrar su error sin cargar el archivo parcialmente.
4. Confirmar el archivo válido y comprobar sus lotes y unidades en inventario. Un reenvío del mismo archivo no debe duplicar el movimiento.
5. Si ya existe carga inicial, usar la modalidad adicional que ofrece la versión integrada, con lotes no duplicados.

## 5. Consulta y cámara · HU-05

1. Con Auxiliar 04, consultar el SKU, nombre o EAN utilizado. Verificar lote, ubicación, disponible y vencimiento contra el Excel.
2. Comprobar el semáforo de vencimiento con registros de ensayo apropiados. Escribir el EAN o usar un lector que lo ingrese como teclado.
3. Abrir la cámara con permiso en un dispositivo compatible. La cámara es una demostración y no decodifica códigos; registrar esta adaptación en la revisión del criterio del taller.

Completar [VERIFICACION](VERIFICACION.md) con capturas y resultados. Registrar la aceptación y las condiciones reales en [SDD](Registro_Aprobaciones_SDD_Sprint_1.md).
