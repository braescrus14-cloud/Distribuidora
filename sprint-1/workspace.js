import { stored } from "/driver-store.js";
const titles = {"01":["Dirección","Tu operación, de un vistazo","executive"],"02":["Administración","Centro de control","control"],"03":["Bodega","El flujo de tu bodega","warehouse"],"04":["Preparación","Tu mesa de alistamiento","picking"],"05":["Abastecimiento","Todo empieza con una buena compra","supply"],"06":["Comercial","Tu mesa comercial","sales"],"07":["Distribución","Centro de distribución","dispatch"],"08":["Reparto","Tu jornada, en movimiento","driver"],"09":["Consulta contable","Información para conciliar","ledger"],"10":["Mi finca","Tu producción, acompañada","farm"]};
function el(tag, content = "", className = "") { const node=document.createElement(tag); node.textContent=content; if(className)node.className=className; return node; }
const status = value => ({CONFIRMADO:"Confirmado",ALISTADO:"Alistado",EN_RUTA:"En ruta",ENTREGADO:"Entregado",NOVEDAD:"Novedad",PLANIFICADA:"Planificada",FINALIZADA:"Finalizada",PENDIENTE_REVISIÓN:"Por revisar"}[value] || value);
function metric(label,value,detail="") { const box=el("article","","home-metric"); box.append(el("span",label),el("strong",String(value)),el("small",detail));return box; }
function card(title,copy="") { const box=el("article","","home-card");box.append(el("h2",title));if(copy)box.append(el("p",copy));return box; }
function row(title,detail,badge="") { const node=el("div","","home-row");const text=el("div");text.append(el("strong",title),el("span",detail));node.append(text);if(badge)node.append(el("span",badge,"home-pill"));return node; }
function action(label,title,open,handle) {const button=el("button",label,"secondary home-action");button.type="button";button.onclick=handle(()=>open(title));return button;}
function rowsCard(title,rows,empty) {const box=card(title);if(!rows.length)box.append(el("p",empty,"home-empty"));for(const item of rows)box.append(item);return box;}
function steps(names,active) {const line=el("ol","","home-stage-steps");for(const [index,name]of names.entries()){const item=el("li",name,index<=active?"done":"");if(index===active)item.setAttribute("aria-current","step");line.append(item);}return line;}
export function workspaceHome(user,request,panel,open,handle) {
 return async function render() {
  const [category,title,layout]=titles[user.role];
  const root=el("div","","home-root");
  const header=el("header","","home-heading");
  const copy=el("div");copy.append(el("p",category.toUpperCase(),"home-eyebrow"),el("h1",title),el("p","Hola, "+user.name+". Este es tu espacio de trabajo."));
  header.append(copy,el("span",new Date().toLocaleDateString("es-CO",{day:"numeric",month:"long"}),"home-date"));
  root.append(header);panel.replaceChildren(root);panel.classList.add("workspace-home");panel.dataset.layout=layout;
  const loading=el("p","Preparando tu espacio…","home-loading");loading.setAttribute("role","status");root.append(loading);
  const get=path=>request(path);
  const go=(label,title)=>action(label,title,open,handle);
  const content=el("div","","home-content");
  try {
   if(user.role==="01") {
    const [purchases,clients]=await Promise.all([get("/api/comercio/compras"),get("/api/comercio/clientes")]);if(!root.isConnected)return;
    const pending=purchases.rows.filter(r=>r.status==="Pendiente de aprobación");
    const banner=card("Las decisiones de hoy","Revisa las órdenes que necesitan tu aprobación y las condiciones comerciales de tus clientes.");banner.classList.add("executive-hero");banner.append(go("Revisar aprobaciones","Compras y recepción"));content.append(banner);
    const metrics=el("div","","home-metrics");metrics.append(metric("Por aprobar",pending.length,"Órdenes de compra"),metric("Clientes activos",clients.rows.filter(r=>r.active).length,"Fichas comerciales"),metric("Compras registradas",purchases.rows.length,"Historial de abastecimiento"));content.append(metrics);
    content.append(rowsCard("Requieren tu decisión",pending.slice(0,5).map(r=>row(r.number,r.supplier_name||"Orden de compra",new Intl.NumberFormat("es-CO",{style:"currency",currency:"COP",maximumFractionDigits:0}).format(r.total/100))),"No hay compras pendientes de aprobación."));
   } else if(user.role==="02") {
    const [accounts,requests]=await Promise.all([get("/api/users"),get("/api/public-admin/requests")]);if(!root.isConnected)return;
    const active=accounts.users.filter(r=>r.active),pending=requests.filter(r=>r.status==="PENDIENTE");
    const console=card("Accesos bajo control","Administra identidades, permisos y solicitudes del sitio público.");console.classList.add("control-console");console.append(el("span","SISTEMA · ACCESO POR ROLES","console-label"),metric("Cuentas activas",active.length,"Usuarios habilitados"),go("Administrar usuarios","Usuarios y roles"),go("Atender solicitudes ("+pending.length+")","Solicitudes y contacto"),go("Revisar auditoría","Auditoría de accesos"));
    const roles=card("Distribución de cuentas");for(const [code,name]of Object.entries(accounts.roles||{})){const count=accounts.users.filter(r=>r.role===code).length;roles.append(row(name,"Perfil "+code,String(count)));}
    content.append(console,roles);
   } else if(user.role==="03") {
    const [pick,dispatch]=await Promise.all([get("/api/logistica/picking"),get("/api/logistica/dispatch")]);if(!root.isConnected)return;
    const board=el("div","","warehouse-board");
    for(const [caption,items,target]of [["Por preparar",pick.orders.filter(r=>r.status==="CONFIRMADO"),"Alistamiento FEFO"],["Alistados",pick.orders.filter(r=>r.status==="ALISTADO"),"Alistamiento FEFO"],["Cargue y despacho",dispatch.routes,"Cargue y manifiestos"]]) {
     const column=card(caption);column.append(el("span",String(items.length),"column-count"));for(const item of items.slice(0,4))column.append(row(item.number,item.customer_name||item.driver_name,status(item.status)));if(!items.length)column.append(el("p","Sin pendientes en esta etapa.","home-empty"));column.append(go("Abrir etapa",target));board.append(column);
    }
    content.append(board);const returns=dispatch.returns.filter(r=>r.status==="PENDIENTE_RECEPCION");content.append(metric("Retornos por recibir",returns.length,"Comprueba físicamente la mercancía"),go("Consultar inventario","Inventario"),go("Importar lotes desde Excel","Importar inventario"));
   } else if(user.role==="04") {
    const data=await get("/api/logistica/picking");if(!root.isConnected)return;
    const next=data.orders.find(r=>r.status==="CONFIRMADO");
    const focus=card(next?next.number:"Tu mesa está al día",next?next.customer_name:"Cuando se confirme un pedido, podrás prepararlo desde aquí.");focus.classList.add("picking-focus");focus.prepend(el("span","01","focus-number"));
    if(next){focus.append(steps(["Ubicar lotes","Verificar EAN","Finalizar"],next.lines.every(r=>r.picked)?2:0));for(const item of next.lines)focus.append(row(item.name,item.quantity+" unidades · "+item.sku,item.picked?"Verificado":"Por verificar"));}
    focus.append(go("Ir a preparar pedidos","Alistamiento FEFO"));content.append(focus,metric("Confirmados",data.orders.filter(r=>r.status==="CONFIRMADO").length,"Pedidos que necesitan preparación"),metric("Alistados",data.orders.filter(r=>r.status==="ALISTADO").length,"Listos para asignación de ruta"));
   } else if(user.role==="05") {
    const [suppliers,purchases]=await Promise.all([get("/api/comercio/proveedores"),get("/api/comercio/compras")]);if(!root.isConnected)return;
    const supply=card("Tu cadena de abastecimiento","De proveedores habilitados a órdenes y recepciones.");supply.classList.add("supply-flow");supply.append(steps(["Proveedor","Orden de compra","Recepción"],0),go("Crear una compra","Compras y recepción"));
    content.append(supply,rowsCard("Proveedores activos",suppliers.rows.filter(r=>r.active).slice(0,5).map(r=>row(r.name,r.contact,r.terms)),"Registra tu primer proveedor."));
    content.append(rowsCard("Órdenes recientes",purchases.rows.slice(-5).reverse().map(r=>row(r.number,r.supplier_name||"Abastecimiento",r.status)),"Todavía no hay compras."),go("Gestionar proveedores","Proveedores"));
   } else if(user.role==="06") {
    const [clients,orders]=await Promise.all([get("/api/comercio/clientes"),get("/api/comercio/pedidos")]);if(!root.isConnected)return;
    const pending=orders.rows.filter(r=>r.status==="PENDIENTE_REVISIÓN");
    const desk=card("Conversaciones que se convierten en pedidos","Confirma las solicitudes del portal y acompaña a tus clientes.");desk.classList.add("sales-desk");desk.append(metric("Solicitudes por revisar",pending.length,"Pedidos del portal B2B"),go("Revisar pedidos","Pedidos de venta"));
    content.append(desk,rowsCard("Tu cartera de clientes",clients.rows.slice(0,6).map(r=>row(r.name,r.zone,"Lista "+r.price_list)),"No hay clientes vinculados a tu asesoría."),rowsCard("Necesitan seguimiento",pending.slice(0,5).map(r=>row(r.number,r.customer_name,"Por revisar")),"No hay solicitudes pendientes."),go("Gestionar clientes","Clientes"));
   } else if(user.role==="07") {
    const data=await get("/api/logistica/routes");if(!root.isConnected)return;
    const active=data.routes.filter(r=>r.status!=="FINALIZADA"),route=active[0];
    const command=card("La distribución, en tus manos","Asigna capacidad, agrupa por zona y coordina las visitas.");command.classList.add("dispatch-command");command.append(go("Abrir planificación","Planificar distribución"));
    if(route){command.append(el("h3",route.number+" · "+route.vehicle));const visits=el("ol","","route-visits");for(const stop of route.stops)visits.append(el("li",stop.customer+" · "+stop.destination.address));command.append(visits);}else command.append(el("p","La próxima ruta comienza con pedidos alistados."));
    content.append(command,metric("Listos para ruta",data.orders.length,"Pedidos alistados sin asignación"),metric("Rutas activas",active.length,"Planificadas o en reparto"),metric("Novedades",data.alerts.length,"Avisos registrados de entregas"));
   } else if(user.role==="08") {
    let data;try{data=await get("/api/logistica/deliveries");await stored("journeys","readwrite",s=>s.put({userId:user.id,data}));}catch(error){if(navigator.onLine)throw error;data=(await stored("journeys","readonly",s=>s.get(user.id)))?.data;if(!data)throw new Error("Abre tu jornada con conexión antes de salir.");}if(!root.isConnected)return;
    const pending=(await stored("pending","readonly",s=>s.getAll())).filter(r=>r.userId===user.id);
    const today=card("Listo para salir","Abre tu jornada para consultar tus paradas y registrar cada entrega.");today.classList.add("driver-launch");today.append(el("span",navigator.onLine?"CON CONEXIÓN":"MODO SIN CONEXIÓN","driver-signal"),metric("Entregas en ruta",data.orders.filter(r=>r.status==="EN_RUTA").length,"Asignadas a tu cuenta"),go("Abrir mi jornada","Mis entregas"));content.append(today);
    const stop=data.routes.flatMap(r=>r.stops).find(s=>data.orders.some(o=>o.id===s.order&&o.status==="EN_RUTA"));if(stop)content.append(rowsCard("Tu próxima parada",[row(stop.customer,stop.destination.address,stop.number)],""));
    content.append(metric("Pendientes en el dispositivo",pending.length,"Se sincronizan al recuperar conexión"));
   } else if(user.role==="09") {
    const data=await get("/api/inventory");if(!root.isConnected)return;
    const ledger=card("Consulta de existencias","Referencias disponibles en esta consulta. Abre el detalle por lote para apoyar tu conciliación de saldos.");ledger.classList.add("ledger-sheet");
    const table=document.createElement("table");const head=table.createTHead().insertRow();for(const value of ["Referencia","Producto","Disponible"])head.append(el("th",value));const body=table.createTBody();for(const item of data){const tr=body.insertRow();for(const value of [item.sku,item.name,String(item.total)])tr.append(el("td",value));}const scroll=el("div","","scroll");scroll.append(table);ledger.append(scroll,go("Abrir consulta por lote","Inventario"));content.append(ledger);
   } else {
    const data=await get("/api/comercio/pedidos");if(!root.isConnected)return;
    const finca=card(data.portal?.name||"Tu finca en Villali","Tus referencias, tus condiciones y el avance de tus pedidos.");finca.classList.add("farm-welcome");finca.append(go("Preparar mi pedido","Portal de pedidos"),go("Ver mis entregas","Seguimiento de pedidos"));content.append(finca);
    const recent=[...data.rows].sort((a,b)=>b.date.localeCompare(a.date)).slice(0,1);
    for(const order of recent){const tracking=card("Tu pedido más reciente",order.number);tracking.append(steps(["Revisión","Confirmado","En ruta","Entregado"],({PENDIENTE_REVISIÓN:0,CONFIRMADO:1,ALISTADO:1,EN_RUTA:2,ENTREGADO:3,NOVEDAD:2}[order.status] ?? 0)),el("p",status(order.status)),go("Consultar seguimiento","Seguimiento de pedidos"));content.append(tracking);}
    if(!data.portal)content.append(el("p","Pide a tu asesor que vincule esta cuenta con tu finca para comenzar.","home-empty"));
   }
   if(root.isConnected)root.append(content);
  } finally {loading.remove();}
 };
}

export function publicAdmin(request,handle,panel) {
 return async function render() {
  const root=el("div");root.append(el("h1","Solicitudes y contacto"),el("p","Atiende las solicitudes de cuenta y configura los datos que se muestran en la portada."));panel.replaceChildren(root);
  const [requests,contact]=await Promise.all([request("/api/public-admin/requests"),request("/api/public-admin/contact")]);if(!root.isConnected)return;
  const inbox=card("Solicitudes de cuenta");if(!requests.length)inbox.append(el("p","No hay solicitudes registradas."));
  for(const item of requests){const block=card(item.name,item.farm||"Solicitud desde la portada");block.append(row(item.email,item.phone,item.interest),el("p",new Date(item.at).toLocaleString("es-CO")+" · "+status(item.status)));
   const mark=el("button",item.status==="CONTACTADO"?"Marcar pendiente":"Marcar contactado","secondary");mark.type="button";mark.onclick=handle(async()=>{mark.disabled=true;try{await request("/api/public-admin/requests",{id:item.id,status:item.status==="CONTACTADO"?"PENDIENTE":"CONTACTADO"});await render();}finally{mark.disabled=false;}});block.append(mark);inbox.append(block);}
  root.append(inbox);
  const form=document.createElement("form");form.className="home-contact-form";form.append(el("h2","Datos públicos de Villali"),el("p","Publica únicamente datos de contacto y de empresa que hayas autorizado. Los campos vacíos se muestran como [CONFIRMAR] en la portada. Los testimonios requieren autorización expresa."));
  function contactField(host,key,label,hint="",multiline=false){const field=el("label",label);const input=document.createElement(multiline?"textarea":"input");input.name=key;if(!multiline)input.type=key==="email"?"email":key.endsWith("_url")?"url":"text";input.value=contact[key]||"";input.maxLength=multiline?500:200;field.append(input,el("small",hint));host.append(field);}
  for(const [key,label,hint]of [["phone","WhatsApp y teléfono","Incluye el código de país."],["email","Correo público","Correo real autorizado para publicar."],["legal_name","Razón social completa","Dato registrado de la empresa."],["nit","NIT","Solo cuando esté confirmado."],["city","Ciudad","Ciudad de atención confirmada."],["address","Dirección","Dirección real de atención."],["hours","Horario de atención","Horario real del equipo."],["response_time","Tiempo de respuesta","Tiempo que el equipo puede comprometer."],["facebook_url","Perfil de Facebook","Enlace HTTPS del perfil oficial."],["instagram_url","Perfil de Instagram","Enlace HTTPS del perfil oficial."]])contactField(form,key,label,hint);
  const statistics=document.createElement("fieldset");statistics.append(el("legend","Cifras verificadas"));
  for(const [key,label]of [["stat_years","Años de operación"],["stat_municipalities","Municipios atendidos"],["stat_deliveries","Entregas al mes"]])contactField(statistics,key,label,"Dejar vacío si falta la confirmación o el soporte.");form.append(statistics);
  for(const index of [1,2]){const box=document.createElement("fieldset"),prefix="testimonial_"+index+"_";box.append(el("legend","Testimonio "+index));
   for(const [key,label]of [["quote","Texto aprobado"],["name","Nombre del productor"],["farm","Finca"],["municipality","Municipio"]])contactField(box,prefix+key,label,"Solo datos reales autorizados.",key==="quote");
   const check=el("label","","check"),input=document.createElement("input");input.type="checkbox";input.name=prefix+"approved";input.value="yes";input.checked=contact[prefix+"approved"]==="yes";check.append(input,document.createTextNode("Confirmo los datos y la autorización del productor para publicar este testimonio."));box.append(check);form.append(box);
  }
  const save=el("button","Guardar datos públicos");form.append(save);form.onsubmit=handle(async()=>{if(save.disabled)return;save.disabled=true;try{const payload=Object.fromEntries(new FormData(form));for(const i of [1,2])payload["testimonial_"+i+"_approved"]=form.elements["testimonial_"+i+"_approved"].checked?"yes":"";await request("/api/public-admin/contact",payload);save.textContent="Datos guardados";}finally{save.disabled=false;}});root.append(form);
 };
}
