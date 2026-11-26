# Paso a paso · Verificar Sprint 2 en Render

## Antes de empezar

1. Abre [la aplicación](https://villali-staging.onrender.com/) y pulsa **Ingresar**. Usa correo registrado o usuario y contraseña; no hay selector de tipo de cuenta.
2. Comprueba en Render que el último despliegue esté **Live** y anota su commit. En GitHub abre la rama [main del repositorio vigente](https://github.com/braescrus14-cloud/Distribuidora/tree/main), no una copia antigua ni una rama archivada.
3. Prepara cuentas de Compras 05, Gerencia 01, Bodega 03/04, Asesor 06 y Cliente 10. El administrador 02 gestiona cuentas, pero no recibe automáticamente los módulos de todos los roles.
4. Usa registros académicos identificables y cuentas de cliente diferentes. No borres saldos existentes ni cambies MongoDB para ensayar.

## Recorrido funcional

| Paso | Cuenta | Acción | Resultado esperado |
| --- | --- | --- | --- |
| 1 · HU-06 | Compras 05 | Abre Proveedores, registra un proveedor con NIT y dígito válidos, y selecciona un producto activo. | Proveedor guardado, producto asociado y disponible al crear compras. |
| 2 · HU-06 | Compras 05 | Desactiva ese proveedor y revisa las opciones de nueva compra; después vuelve a activarlo. | No aparece como proveedor elegible mientras esté inactivo. |
| 3 · HU-07 | Compras 05 | Crea una compra de ejemplo superior a COP 10 millones. | Queda pendiente de aprobación gerencial. No recibir antes de aprobar. |
| 4 · HU-07 | Gerencia 01 | Abre la compra y apruébala. | El estado permite la recepción autorizada. |
| 5 · HU-07 | Bodega 03/04 | Recibe parte de la cantidad con lote único, ubicación y vencimiento superior a seis meses desde el día del ensayo. | Aumenta el saldo físico por lo recibido; el resto continúa pendiente. |
| 6 · HU-07 | Bodega 03/04 | Prueba un vencimiento insuficiente y después completa con uno válido. | El inválido se rechaza sin aumentar existencias. |
| 7 · HU-08 | Asesor 06 | Crea o toma una ficha de cliente con zona, lista A/B y consentimiento; vincula su cuenta de Cliente. | El portal accede solo a la ficha vinculada. |
| 8 · HU-08/09 | Gerencia 01 | Configura cupo y cartera de ensayo. | Solo Gerencia modifica esas condiciones. |
| 9 · HU-10 | Cliente 10 | Abre Portal de pedidos y solicita un producto con saldo. | Pedido pendiente de revisión, visible para su asesor. |
| 10 · HU-09 | Asesor 06 | Revisa y confirma el pedido. Anota disponible y reservado antes/después. | Se reserva la cantidad confirmada; el saldo físico no se descuenta todavía. |
| 11 · HU-09 | Asesor 06 | Intenta exceder el saldo disponible o el cupo y usa cartera vencida en un caso separado. | Rechazo claro sin reserva adicional. |
| 12 · HU-10 | Otro Cliente 10 | Revisa su portal y prueba un identificador ajeno. | No ve fichas ni pedidos de otros clientes. |

El pedido confirmado del paso 10 puede usarse como entrada de la [guía del Sprint 3](../sprint-3/Guia_Verificacion_Sprint_3.md).

## Evidencia a entregar

Guardar commit desplegado, fecha, responsables, identificadores de proveedor/compra/cliente/pedido y capturas de los resultados. Anexar [CI Sprint 2](https://github.com/braescrus14-cloud/Distribuidora/actions/workflows/sprint-2.yml) correspondiente a ese commit. Marcar cada prueba **Aprobada**, **Falló** o **No ejecutada** según lo observado. La cuenta y la clave se comparten por un canal privado, no en GitHub.

No crear otro servicio en Render, no apuntar a otra base de Atlas y no ejecutar cargas iniciales para comprobar este incremento.
