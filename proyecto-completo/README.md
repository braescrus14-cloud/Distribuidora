# Proyecto completo de Distribuidora Villali

Esta carpeta contiene el código integrado de **HU-01–HU-20**, correspondiente a los cuatro sprints. El frontend usa HTML, CSS y JavaScript; Python sirve la aplicación y la API. Render conserva los datos operativos en MongoDB Atlas. DIAN y PSE son simulaciones académicas.

## Archivos principales

| Archivos | Función |
| --- | --- |
| app.py, app.js, index.html, style.css | Acceso, cuentas, catálogo e inventario |
| commerce.py | Proveedores, compras, clientes y pedidos |
| logistics.py, logistics.js | FEFO, rutas, despacho, evidencia y seguimiento |
| finance.py, finance.js, finance.css | Facturas, pagos, cartera, liquidaciones, indicadores y devoluciones |
| mongo_store.py | Persistencia y transacciones en Atlas |
| landing.html, landing.js, landing.css, workspace.js | Portada y espacios por rol |
| tests/ y test_*.py | Pruebas de los cuatro sprints y del portal |
| documentacion/ | Entrega general, versiones, revisión y despliegue |

## Ejecutar en Windows

Abrir PowerShell en esta carpeta:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\iniciar.ps1
```

El primer arranque local permite crear `admin` con una contraseña de 10–128 caracteres, mayúscula, número y símbolo. Después abrir [localhost:8080](http://localhost:8080) y mantener el proceso activo. Si faltan dependencias, instalar `python -m pip install -r requirements.txt`. También se puede iniciar con `python app.py --setup-if-needed`.

Sin variables de conexión externas, la ejecución local conserva datos en `villali.sqlite3`. En Render se mantiene la misma conexión `MONGODB_URI` y base `MONGODB_DATABASE`; no cambiarlas para reorganizar carpetas ni ejecutar semillas sobre datos existentes. No subir credenciales ni archivos de base al repositorio.

## Probar y confirmar los sprints

[Sprint 1](../sprint/sprint-1/VERIFICACION.md) · [Sprint 2](../sprint/sprint-2/VERIFICACION.md) · [Sprint 3](../sprint/sprint-3/VERIFICACION.md) · [Sprint 4](../sprint/sprint-4/VERIFICACION.md).

Las CI usan bases de ensayo. Si se ejecutan pruebas manualmente desde esta carpeta, usar un entorno aislado que no tenga las variables de Atlas operativo. Suites: `tests/smoke.py`, `tests/access.py`, `test_commerce.py`, `test_logistics.py`, `test_finance.py` y `test_public_portal.py`.

## Configuración y entrega

- **[Desplegar con la nueva carpeta en Render](documentacion/Despliegue_Render.md)**.
- [Entrega de los cuatro sprints](documentacion/Entrega_Proyecto.md).
- [Índice de documentación general](documentacion/README.md).
- [Versiones históricas y comparación](documentacion/Versiones.md).

El catálogo se importa con `cargar_catalogo.py`; los lotes se cargan desde la interfaz de inventario o por recepción de compras. No son el mismo archivo. Los precios orientativos requieren validación comercial. Los correos de invitación/recuperación requieren `RESEND_API_KEY`, `VILLALI_MAIL_FROM` y `VILLALI_SECURITY_EMAIL`; sin proveedor, el administrador dispone del enlace manual de invitación. La bandeja de facturas del simulador no envía correo real.
