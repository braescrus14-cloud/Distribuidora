const $ = (id) => document.getElementById(id);
const panel = $("panel");
let user;
let activeModule;
let stopCamera = () => {};
let expiryCheck;
let lastActivity = 0;
let activationToken = new URLSearchParams(location.hash.slice(1)).get("invitar");
if (activationToken) history.replaceState(null, "", "/");

const icons = {
  box: '<path d="m12 3 9 5v8l-9 5-9-5V8zM3 8l9 5 9-5m-9 5v8m-5-15 9 5"/>',
  stock: '<rect x="3" y="7" width="18" height="14" rx="2"/><path d="M3 12h18M8 7V4h8v3m-6 9h4"/>',
  upload: '<path d="M12 16V4m-5 5 5-5 5 5M4 16v4h16v-4"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21v-2a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v2"/>',
  lock: '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
  eye: '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  camera: '<path d="M3 7h4l2-3h6l2 3h4v13H3z"/><circle cx="12" cy="13" r="3"/>',
};

function icon(name) {
  return `<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${icons[name]}</svg>`;
}

for (const [id, name] of [["login-user-icon", "user"], ["login-lock-icon", "lock"],
  ["toggle-password", "eye"], ["toggle-sidebar", "menu"]]) {
  $(id).innerHTML = icon(name);
}

$("toggle-password").onclick = () => {
  const input = $("login-password");
  const reveal = input.type === "password";
  input.type = reveal ? "text" : "password";
  $("toggle-password").setAttribute("aria-pressed", String(reveal));
  $("toggle-password").setAttribute("aria-label", reveal ? "Ocultar contraseña" : "Mostrar contraseña");
};

function sidebarOpen(open) {
  document.body.classList.toggle("sidebar-closed", !open);
  $("toggle-sidebar").setAttribute("aria-expanded", String(open));
}

$("toggle-sidebar").onclick = () => sidebarOpen(document.body.classList.contains("sidebar-closed"));

function notify(message = "", error = false) {
  $("notice").textContent = message;
  $("notice").hidden = !message;
  $("notice").classList.toggle("error", error);
}

async function request(path, data, raw = false) {
  const response = await fetch(path, data === undefined ? {} : {
    method: "POST",
    headers: { "Content-Type": raw ? "application/octet-stream" : "application/json" },
    body: raw ? data : JSON.stringify(data),
  });
  const result = await response.json();
  if (!response.ok) {
    if (response.status === 401 && user) showLogin();
    throw Object.assign(new Error(result.error), { details: result.errors });
  }
  return result;
}

function handle(action) {
  return async (event) => {
    event?.preventDefault();
    notify();
    try {
      await action(event);
    } catch (error) {
      notify(error.message, true);
    }
  };
}

function values(form) {
  return Object.fromEntries(new FormData(form));
}

function table(headers, rows) {
  const container = document.createElement("div");
  container.className = "scroll";
  const table = document.createElement("table");
  const header = table.createTHead().insertRow();
  for (const name of headers) {
    const cell = document.createElement("th");
    cell.scope = "col";
    cell.textContent = name;
    header.append(cell);
  }
  const body = table.createTBody();
  for (const row of rows) {
    const element = body.insertRow();
    for (const [index, value] of row.entries()) {
      const cell = element.insertCell();
      cell.dataset.label = headers[index] || "Acciones";
      if (value instanceof Node) cell.append(value);
      else cell.textContent = value;
    }
  }
  container.append(table);
  return container;
}

function button(title, click) {
  const element = document.createElement("button");
  element.type = "button";
  element.className = "secondary";
  element.textContent = title;
  element.onclick = handle(click);
  return element;
}

function badge(label, tone) {
  const element = document.createElement("span");
  element.className = `badge ${tone}`;
  element.textContent = label;
  return element;
}

function productIdentity(product) {
  const category = (product.species || "").toLowerCase();
  const families = [
    [/postura|pollo|reproductora|pavo|codorniz/, "🐔", "aves"],
    [/porci/, "🐖", "porcinos"],
    [/bovin|ganader/, "🐄", "bovinos"],
    [/equin/, "🐎", "equinos"],
    [/peces|acuic/, "🐟", "peces"],
    [/conejo|cuye/, "🐇", "pequenas"],
    [/ovino/, "🐑", "pequenas"],
    [/canin/, "🐕", "pequenas"],
    [/felin/, "🐈", "pequenas"],
    [/materia/, "🌾", "insumos"],
  ];
  const [, symbol, tone] = families.find(([pattern]) => pattern.test(category)) || [null, "◈", "insumos"];
  const identity = document.createElement("span");
  identity.className = "product-identity";
  const tile = document.createElement("span");
  tile.className = `product-tile ${tone}`;
  tile.setAttribute("aria-hidden", "true");
  tile.textContent = symbol;
  const name = document.createElement("strong");
  name.textContent = product.name;
  identity.append(tile, name);
  return identity;
}

function showLogin() {
  document.body.classList.add("access");
  stopCamera();
  clearInterval(expiryCheck);
  user = null;
  $("sidebar").hidden = true;
  $("topbar").hidden = true;
  $("login-password").type = "password";
  $("toggle-password").setAttribute("aria-pressed", "false");
  $("toggle-password").setAttribute("aria-label", "Mostrar contraseña");
  $("menu").hidden = true;
  $("account").hidden = true;
  panel.hidden = true;
  panel.replaceChildren();
  $("login").hidden = Boolean(activationToken);
  $("activate").hidden = !activationToken;
}

async function startSession() {
  user = await request("/api/session");
  document.body.classList.remove("access");
  $("login").hidden = true;
  $("activate").hidden = true;
  $("account").hidden = false;
  $("sidebar").hidden = false;
  $("topbar").hidden = false;
  sidebarOpen(!matchMedia("(max-width: 760px)").matches);
  $("identity").textContent = user.name;
  $("profile-role").textContent = user.role_name;
  $("avatar").textContent = user.name.trim().split(/\s+/).slice(0, 2).map((word) => word[0]).join("").toUpperCase();
  const modules = [];
  if (user.role === "02") modules.push(["Usuarios y roles", users, "user"]);
  if (user.catalog) modules.push(["Catálogo", products, "box"]);
  if (user.inventory) modules.push(["Inventario", inventory, "stock"]);
  if (user.role === "03") modules.push(["Importar inventario", importer, "upload"]);
  if (user.role === "02") modules.push(["Auditoría de accesos", audit, "clock"]);
  const nav = $("menu");
  nav.hidden = !modules.length;
  nav.replaceChildren();
  for (const [title, render, symbol] of modules) {
    const item = button(title, async () => {
      stopCamera();
      activeModule = render;
      $("section-title").textContent = title;
      if (matchMedia("(max-width: 760px)").matches) sidebarOpen(false);
      for (const other of nav.children) other.setAttribute("aria-current", String(other === item));
      panel.hidden = false;
      await render();
    });
    item.insertAdjacentHTML("afterbegin", icon(symbol));
    nav.append(item);
  }
  if (nav.firstChild) nav.firstChild.click();
  else {
    activeModule = null;
    $("section-title").textContent = "Acceso";
    panel.hidden = false;
    panel.innerHTML = "<h1>Sesión iniciada</h1><p>Este rol no tiene acceso al catálogo, al inventario ni a la administración de usuarios.</p>";
  }
  clearInterval(expiryCheck);
  lastActivity = Date.now();
  expiryCheck = setInterval(() => {
    if (document.visibilityState === "visible") {
      request("/api/session").catch((error) => notify(error.message, true));
    }
  }, 15000);
}

$("login-form").onsubmit = handle(async (event) => {
  const form = event.currentTarget;
  const mobile = matchMedia("(pointer: coarse)").matches || navigator.userAgentData?.mobile === true;
  await request("/api/login", { ...values(form), mobile });
  form.reset();
  await startSession();
});
$("activate-form").onsubmit = handle(async (event) => {
  const form = event.currentTarget;
  await request("/api/activate", { ...values(form), token: activationToken });
  form.reset();
  activationToken = null;
  showLogin();
  notify("Contraseña configurada. Ya puedes iniciar sesión.");
});
$("logout").onclick = handle(async () => {
  await request("/api/logout", {});
  showLogin();
});

for (const event of ["pointerdown", "keydown", "input"]) {
  document.addEventListener(event, () => {
    if (!user || Date.now() - lastActivity < 30000) return;
    lastActivity = Date.now();
    request("/api/activity", {}).catch((error) => notify(error.message, true));
  });
}

async function users() {
  panel.innerHTML = `<div class="page-heading"><div><h1>Usuarios y roles</h1>
    <p>Administra las cuentas y sus permisos de acceso.</p></div><button id="new-user">+ Nuevo usuario</button></div>
    <div class="grid toolbar"><label>Buscar usuario <input type="search" id="user-search" placeholder="Nombre o usuario"></label>
      <label>Rol <select id="role-filter"><option value="">Todos los roles</option></select></label>
      <label>Estado <select id="user-status"><option value="">Todos</option><option value="active">Activo</option><option value="pending">Por activar</option><option value="inactive">Inactivo</option></select></label></div>
    <dialog id="user-dialog" aria-labelledby="user-dialog-title"><h2 id="user-dialog-title">Nuevo usuario</h2><p>La invitación permite definir la contraseña una sola vez.</p>
    <form id="user-form"><div class="grid">
      <label>Usuario <input name="username" required maxlength="80"></label>
      <label>Nombre <input name="name" required maxlength="120"></label>
      <label>Rol <select name="role" required></select></label></div>
      <div id="user-options" hidden><label class="check"><input type="checkbox" name="active" checked> Cuenta activa</label>
      <label class="check"><input type="checkbox" name="invite"> Generar una invitación nueva</label></div>
      <p class="form-error" role="alert" hidden></p>
      <div class="actions"><button type="button" class="secondary" id="cancel-user">Cancelar</button><button id="save-user">Crear usuario</button></div>
    </form></dialog><div id="user-result" aria-live="polite"></div>`;
  const form = $("user-form");
  const result = $("user-result");
  const dialog = $("user-dialog");
  const { users: records, roles } = await request("/api/users");
  if (activeModule !== users || !form.isConnected) return;
  let selected;
  let wasActive;
  for (const [key, label] of Object.entries(roles)) {
    form.elements.role.add(new Option(label, key));
    $("role-filter").add(new Option(label, key));
  }
  const reset = () => {
    selected = undefined;
    form.reset();
    form.elements.username.readOnly = false;
    $("user-options").hidden = true;
    $("save-user").textContent = "Crear usuario";
    $("user-dialog-title").textContent = "Nuevo usuario";
    form.querySelector(".form-error").hidden = true;
  };
  $("cancel-user").onclick = () => dialog.close();
  $("new-user").onclick = () => { reset(); dialog.showModal(); };
  const statusOf = (row) => row.active ? (row.configured ? "active" : "pending") : "inactive";
  const renderRows = () => {
    const query = $("user-search").value.trim().toLocaleLowerCase("es");
    const role = $("role-filter").value;
    const status = $("user-status").value;
    const filtered = records.filter((row) => (!role || row.role === role) && (!status || statusOf(row) === status)
      && `${row.name} ${row.username}`.toLocaleLowerCase("es").includes(query));
    result.replaceChildren(table(["Usuario", "Nombre", "Rol", "Estado", ""], filtered.map((row) => [
    row.username, row.name, roles[row.role], row.active ? (row.configured ? badge("Activo", "verde") : badge("Por activar", "amarillo")) : badge("Inactivo", "neutral"),
    button("Editar", () => {
      reset();
      selected = row.id;
      wasActive = Boolean(row.active);
      form.elements.username.value = row.username;
      form.elements.username.readOnly = true;
      form.elements.name.value = row.name;
      form.elements.role.value = row.role;
      form.elements.active.checked = Boolean(row.active);
      form.elements.invite.checked = false;
      $("user-options").hidden = false;
      $("save-user").textContent = "Guardar cambios";
      $("user-dialog-title").textContent = "Editar usuario";
      dialog.showModal();
      form.elements.name.focus();
    }),
    ])));
    if (!filtered.length) result.append("No hay usuarios para estos filtros.");
  };
  for (const id of ["user-search", "role-filter", "user-status"]) $(id).oninput = renderRows;
  renderRows();
  form.onsubmit = handle(async () => {
    if (selected && wasActive && !form.elements.active.checked && !confirm("¿Desactivar esta cuenta?")) return;
    const result = await saveForm(form, "/api/users", { ...values(form), id: selected,
      active: form.elements.active.checked, invite: form.elements.invite.checked });
    if (!result) return;
    if (!form.isConnected) return;
    await users();
    notify("Usuario guardado.");
    if (result.invitation) {
      const link = document.createElement("a");
      link.href = result.invitation;
      link.textContent = result.invitation;
      $("notice").append(document.createElement("br"), "Enlace de invitación: ", link);
    }
  });
}

async function saveForm(form, path, data) {
  const errorBox = form.querySelector(".form-error");
  errorBox.hidden = true;
  try {
    return await request(path, data);
  } catch (error) {
    errorBox.textContent = error.message;
    errorBox.hidden = false;
  }
}

async function audit() {
  panel.innerHTML = "<h1>Auditoría de accesos</h1><p>Registro de actividad y seguridad. Las fechas se muestran en UTC.</p>";
  const rows = await request("/api/audit");
  if (activeModule !== audit) return;
  panel.append(table(["Fecha UTC", "Usuario", "Evento", "IP", "Detalle"],
    rows.map((row) => [row.at, row.actor, row.event, row.ip, row.detail])));
}

function products() {
  panel.innerHTML = `<div class="page-heading"><div><h1>Catálogo de productos</h1>
    <p>Consulta las referencias por nombre, código, marca o especie.</p></div><button id="new-product" hidden>+ Nuevo producto</button></div>
    <form id="catalog-filter" class="toolbar"><div class="grid">
      <label>Nombre, SKU o código <input type="search" name="q" placeholder="Buscar referencia"></label>
      <label>Marca <input name="brand"></label>
      <label>Especie <input name="species"></label>
    </div><div class="actions"><button>Filtrar</button></div></form>
    <dialog id="product-dialog" aria-labelledby="product-title"><form id="product-form"><h2 id="product-title">Nuevo producto</h2><div class="grid">
      <label>SKU <input name="sku" required></label>
      <label>Código EAN-13 <input name="barcode" inputmode="numeric" pattern="[0-9]{13}" required></label>
      <label>Nombre <input name="name" required></label>
      <label>Marca <input name="brand" required></label>
      <label>Especie <input name="species" required></label>
      <label>Presentación <input name="presentation" required></label>
      <label>Precio base (COP) <input name="price" type="number" min="0" step="0.01" required></label>
      <label>Stock mínimo <input name="minimum" type="number" min="1" step="1" required></label>
      </div><label class="check" id="product-status" hidden><input name="active" type="checkbox" checked> Producto activo</label>
      <p class="form-error" role="alert" hidden></p>
      <div class="actions"><button type="button" class="secondary" id="cancel-product">Cancelar</button><button>Guardar producto</button></div>
    </form></dialog><div id="product-list" aria-live="polite"></div>`;
  const editable = user.role === "03";
  const form = $("product-form");
  const dialog = $("product-dialog");
  $("new-product").hidden = !editable;
  const filter = $("catalog-filter");
  const result = $("product-list");
  let page = 1;
  let selected;
  let generation = 0;
  const money = new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP" });
  const reset = () => {
    selected = undefined;
    form.reset();
    $("product-title").textContent = "Nuevo producto";
    form.elements.price.required = true;
    form.elements.presentation.required = true;
    $("product-status").hidden = true;
    form.querySelector(".form-error").hidden = true;
  };
  $("cancel-product").onclick = () => dialog.close();
  $("new-product").onclick = () => { reset(); dialog.showModal(); };
  const load = async () => {
    const current = ++generation;
    const query = new URLSearchParams({ ...values(filter), page });
    const data = await request("/api/products?" + query);
    if (current !== generation || !result.isConnected) return;
    const headings = ["SKU", "Producto", "EAN-13", "Marca", "Especie", "Presentación", "Precio", "Mínimo", "Estado"];
    if (editable) headings.push("");
    result.replaceChildren(table(headings, data.products.map((row) => {
      const demo = row.sku.startsWith("DEMO-IT-");
      const price = row.price_status === "Pendiente de cotización" ? row.price_status
        : money.format(row.price_cents / 100) + (/estimaci/i.test(row.price_status || "") ? " · estimado"
          : /históric/i.test(row.price_status || "") ? " · histórico" : "");
      const cells = [row.sku, productIdentity(row), row.barcode, row.brand, row.species, row.presentation || "—",
        price, row.minimum,
        row.active ? (demo ? badge("Demostración", "neutral") : badge("Activo", "verde")) : badge("Inactivo", "neutral")];
      if (editable) cells.push(button("Editar", () => {
        reset();
        selected = row.id;
        for (const key of ["sku", "barcode", "name", "brand", "species", "presentation", "minimum"]) {
          form.elements[key].value = row[key];
        }
        form.elements.price.value = row.price_status === "Pendiente de cotización" ? "" : (row.price_cents / 100).toFixed(2);
        form.elements.price.required = row.price_status !== "Pendiente de cotización";
        form.elements.presentation.required = Boolean(row.presentation);
        form.elements.active.checked = Boolean(row.active);
        $("product-title").textContent = "Editar producto";
        $("product-status").hidden = false;
        dialog.showModal();
        form.elements.sku.focus();
      }));
      return cells;
    })));
    if (!data.products.length) result.append("No hay productos para estos filtros.");
    if (data.products.some((row) => row.sku.startsWith("DEMO-IT-") || row.price_status)) {
      const note = document.createElement("p");
      note.className = "data-note";
      note.textContent = "Precios orientativos en COP. Las bases de comparación no verifican el empaque.";
      result.prepend(note);
    }
    const controls = document.createElement("div");
    controls.className = "actions";
    const back = button("Anterior", () => { page--; return load(); });
    back.disabled = page === 1;
    const next = button("Siguiente", () => { page++; return load(); });
    next.disabled = !data.more;
    controls.append(back, `Página ${page}`, next);
    result.append(controls);
  };
  filter.onsubmit = handle(() => { page = 1; return load(); });
  form.onsubmit = handle(async () => {
    const saved = await saveForm(form, "/api/products", { ...values(form), id: selected, active: form.elements.active.checked });
    if (!saved || !form.isConnected) return;
    dialog.close();
    reset();
    await load();
    notify("Producto guardado.");
  });
  return load();
}

function importer() {
  panel.innerHTML = `<div class="page-heading"><div><h1>Importar inventario</h1>
    <p>Valida los lotes del Excel antes de guardarlos en la bodega.</p></div>
    <a class="download" href="/api/template" download>Descargar plantilla Excel</a></div>
    <ol class="steps" id="import-steps"><li>Seleccionar archivo</li><li>Validar información</li><li>Revisar resultados</li><li>Confirmar carga</li></ol>
    <form id="import-form">
      <label class="drop-zone" id="drop-zone">${icon("upload")}<strong>Selecciona o arrastra un archivo Excel</strong>
      <span>Formato .xlsx · Usa la plantilla para registrar los lotes.</span>
      <input id="inventory-file" type="file" accept=".xlsx" required></label>
      <div class="actions"><button>Validar archivo</button><button type="button" id="confirm-import" disabled>Confirmar carga</button></div>
    </form><div id="import-result"></div>`;
  const fileInput = $("inventory-file");
  const confirm = $("confirm-import");
  const result = $("import-result");
  let verified;
  const setStep = (index) => [...$("import-steps").children].forEach((item, position) => {
    item.classList.toggle("complete", position < index);
    if (position === index) item.setAttribute("aria-current", "step");
    else item.removeAttribute("aria-current");
  });
  setStep(0);
  fileInput.onchange = () => {
    verified = undefined;
    confirm.disabled = true;
    result.replaceChildren();
    setStep(fileInput.files.length ? 1 : 0);
  };
  const dropZone = $("drop-zone");
  dropZone.ondragover = (event) => { event.preventDefault(); dropZone.classList.add("drag-over"); };
  dropZone.ondragleave = () => dropZone.classList.remove("drag-over");
  dropZone.ondrop = (event) => {
    event.preventDefault();
    dropZone.classList.remove("drag-over");
    const file = event.dataTransfer.files[0];
    if (!file?.name.toLowerCase().endsWith(".xlsx")) {
      notify("Selecciona un archivo .xlsx.", true);
      return;
    }
    const transfer = new DataTransfer();
    transfer.items.add(file);
    fileInput.files = transfer.files;
    fileInput.onchange();
  };
  const showErrors = (errors) => {
    result.replaceChildren(table(["Fila", "Motivo"], errors.map((item) => [item.fila, item.motivo])));
    result.append(button("Descargar reporte de errores", () => {
      const csv = ["Fila,Motivo", ...errors.map((item) => `${item.fila},"${item.motivo.replaceAll('"', '""')}"`)].join("\r\n");
      const url = URL.createObjectURL(new Blob(["\ufeff", csv], { type: "text/csv;charset=utf-8" }));
      const link = document.createElement("a");
      link.href = url;
      link.download = "errores_inventario.csv";
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }));
  };
  $("import-form").onsubmit = handle(async () => {
    const file = fileInput.files[0];
    confirm.disabled = true;
    verified = undefined;
    result.replaceChildren();
    const data = await request("/api/import/preview", file, true);
    if (fileInput.files[0] !== file || !fileInput.isConnected) return;
    setStep(2);
    if (data.errors.length) {
      showErrors(data.errors);
      notify("Corrige las filas señaladas antes de confirmar.", true);
      return;
    }
    verified = { file, digest: data.digest };
    result.textContent = `Validación correcta. ${data.count} filas y ${data.units} unidades para cargar.`;
    confirm.disabled = false;
  });
  confirm.onclick = handle(async () => {
    if (!verified) return;
    if (!window.confirm("¿Confirmar la carga inicial del archivo validado?")) return;
    confirm.disabled = true;
    try {
      const data = await request("/api/import/confirm?digest=" + verified.digest, verified.file, true);
      verified = undefined;
      if (fileInput.isConnected) setStep(3);
      result.textContent = data.repeat ? "Este archivo ya se cargó." : `Carga guardada. ${data.count} saldos por lote.`;
    } catch (error) {
      if (error.details) showErrors(error.details);
      confirm.disabled = false;
      throw error;
    }
  });
}

function beep() {
  try {
    const audio = new AudioContext();
    const tone = audio.createOscillator();
    const volume = audio.createGain();
    volume.gain.value = 0.05;
    tone.connect(volume).connect(audio.destination);
    tone.onended = () => { audio.close(); };
    tone.start();
    tone.stop(audio.currentTime + 0.09);
  } catch { /* El sonido es opcional si el navegador lo bloquea. */ }
}

function inventory() {
  panel.innerHTML = `<h1>Consulta de inventario</h1>
    <p class="section-intro">Encuentra existencias por producto y revisa el vencimiento de cada lote.</p>
    <form id="lookup"><div class="grid">
      <label>Código EAN-13 <input name="code" inputmode="numeric" autocomplete="off" autofocus></label>
      <label>O busca por nombre <input name="q"></label>
      </div><div class="actions"><button>Consultar</button><button type="button" class="secondary" id="camera">${icon("camera")} Escanear con cámara</button>
      <button type="button" class="secondary" id="all-stock">Ver existencias</button></div>
    </form><section id="camera-demo" class="toolbar" aria-label="Demostración de cámara" hidden>
      <p>Vista en directo de demostración. La cámara no lee ni guarda códigos.</p>
      <video id="scanner" playsinline muted></video>
      <div class="actions"><button type="button" class="secondary" id="close-camera">Cerrar cámara</button></div>
    </section><div id="stock"></div>`;
  const form = $("lookup");
  const video = $("scanner");
  const cameraDemo = $("camera-demo");
  const result = $("stock");
  let generation = 0;
  const lookup = async () => {
    const current = ++generation;
    const data = values(form);
    const query = data.code.trim() ? { code: data.code } : { q: data.q };
    const overview = !data.code.trim() && !data.q.trim();
    result.replaceChildren();
    if (data.code.trim()) beep();
    const products = await request("/api/inventory?" + new URLSearchParams(query));
    if (current !== generation || !result.isConnected) return;
    if (products.some((product) => product.lots.some((lot) => lot.demo))) {
      const note = document.createElement("p");
      note.className = "data-note";
      note.textContent = "Existencias de demostración";
      result.append(note);
    }
    if (overview) {
      if (!products.length) {
        result.append("Todavía no hay existencias registradas.");
        return;
      }
      const cards = document.createElement("div");
      cards.className = "stock-cards";
      for (const product of products) {
        const card = document.createElement("article");
        const stats = document.createElement("div");
        stats.className = "stock-stats";
        const available = document.createElement("strong");
        available.textContent = product.total.toLocaleString("es-CO");
        const lots = document.createElement("span");
        lots.textContent = `Disponibles · ${product.lots.length} lotes`;
        stats.append(available, lots);
        const detail = button("Ver lotes", () => {
          form.elements.code.value = product.barcode;
          form.elements.q.value = "";
          return lookup();
        });
        card.append(productIdentity(product), stats, detail);
        cards.append(card);
      }
      result.append(cards);
      return;
    }
    for (const product of products) {
      const article = document.createElement("article");
      const title = document.createElement("h2");
      title.append(productIdentity(product));
      const total = document.createElement("p");
      total.textContent = `SKU ${product.sku} · Disponible total: ${product.total}`;
      article.append(title, total);
      article.append(table(["Lote", "Ubicación", "Vencimiento", "Disponible", "Estado"], product.lots.map((row) => {
        const badge = document.createElement("span");
        badge.className = row.color;
        badge.textContent = row.days < 0 ? "Vencido" :
          row.color === "rojo" ? "Próximo a vencer" : `${row.days} días`;
        return [row.lot, row.location, row.expiry, row.available, badge];
      })));
      result.append(article);
    }
  };
  form.onsubmit = handle(lookup);
  $("all-stock").onclick = handle(() => {
    form.reset();
    return lookup();
  });
  form.elements.q.oninput = () => { form.elements.code.value = ""; };
  $("camera").onclick = handle(async () => {
    stopCamera();
    if (!navigator.mediaDevices?.getUserMedia) {
      throw new Error("El navegador no ofrece acceso a la cámara. Abre Villali en localhost o con HTTPS.");
    }
    let cancelled = false;
    let stream;
    stopCamera = () => {
      cancelled = true;
      stream?.getTracks().forEach((track) => track.stop());
      video.srcObject = null;
      cameraDemo.hidden = true;
    };
    const release = stopCamera;
    cameraDemo.hidden = false;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: "environment" } }, audio: false });
      if (cancelled || !video.isConnected) { release(); return; }
      video.srcObject = stream;
      await video.play();
    } catch {
      if (cancelled) return;
      release();
      throw new Error("No se pudo abrir la cámara. Revisa los permisos del navegador y vuelve a intentarlo.");
    }
  });
  $("close-camera").onclick = () => stopCamera();
  return lookup();
}

showLogin();
if (!activationToken) startSession().catch(() => showLogin());
