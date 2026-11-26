const $ = (id) => document.getElementById(id);
import { logisticsView, trackingView, syncDeliveries } from "/logistics.js";
import { workspaceHome, publicAdmin } from "/workspace.js";
import { financeView } from "/finance.js";
const panel = $("panel");
let user;
let activeModule;
let stopCamera = () => {};
let expiryCheck;
let lastActivity = 0;
let activationToken;

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
$("recover-access").onclick = () => {
  $("recovery-form").reset();
  $("recovery-form").elements.username.value = $("login-form").elements.username.value;
  $("recovery-status").hidden = true;
  $("recovery-dialog").showModal();
};
$("close-recovery").onclick = () => $("recovery-dialog").close();
$("recovery-form").onsubmit = async (event) => {
  event.preventDefault();
  const form = event.currentTarget, submit = form.querySelector("button:not([type=button])");
  if (submit.disabled) return;
  submit.disabled = true;
  try { $("recovery-status").textContent = (await request("/api/public/recover", values(form))).message; }
  catch (error) { $("recovery-status").textContent = error.message; }
  finally { submit.disabled = false; $("recovery-status").hidden = false; }
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

async function withLoading(host, layout, message, action) {
  const bar = '<span class="skeleton-bar"></span>';
  const layouts = {
    table: () => `<div class="skeleton-table">${Array.from({ length: 5 }, () =>
      `<div class="skeleton-row">${bar.repeat(5)}</div>`).join("")}</div>`,
    stock: () => `<div class="stock-cards">${Array.from({ length: 6 }, () =>
      `<article><div class="skeleton-identity">${bar.repeat(2)}</div>${bar.repeat(2)}</article>`).join("")}</div>`,
    lots: () => `<div class="skeleton-detail"><div class="skeleton-identity">${bar.repeat(2)}</div>
      ${bar}<div class="skeleton-table">${Array.from({ length: 3 }, () =>
      `<div class="skeleton-row">${bar.repeat(5)}</div>`).join("")}</div></div>`,
    summary: () => `<div class="skeleton-summary">${bar.repeat(2)}</div>`,
  };
  const loading = document.createElement("div");
  loading.className = "loading-placeholder";
  loading.innerHTML = `<span class="loading-status" role="status"></span><div aria-hidden="true">${layouts[layout]()}</div>`;
  loading.firstElementChild.textContent = message;
  host.setAttribute("aria-busy", "true");
  host.append(loading);
  try {
    return await action();
  } finally {
    loading.remove();
    if (!host.querySelector(":scope > .loading-placeholder")) host.removeAttribute("aria-busy");
  }
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
  delete document.body.dataset.role;
  activeModule = null;
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

function openInvitation() {
  const token = new URLSearchParams(location.hash.slice(1)).get("invitar");
  if (!token) return false;
  activationToken = token;
  history.replaceState(null, "", location.pathname + location.search);
  $("activate-form").reset();
  notify();
  showLogin();
  $("activate-form").elements.password.focus();
  return true;
}

async function startSession() {
  let session;
  try {
    session = await request("/api/session");
  } catch (error) {
    const saved = localStorage.getItem("villali-driver");
    if (navigator.onLine || !saved) throw error;
    session = JSON.parse(saved);
    notify("Modo sin conexión. Las entregas quedan pendientes de sincronización.");
  }
  if (activationToken) return;
  user = session;
  if (user.role === "08") localStorage.setItem("villali-driver", JSON.stringify(user));
  else localStorage.removeItem("villali-driver");
  document.body.dataset.role = user.role;
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
  if (["09", "01"].includes(user.role)) modules.push(["Facturas", financeView("facturas", user, request, handle, panel), "stock"]);
  if (user.role === "09") modules.push(["Pagos y cartera", financeView("pagos", user, request, handle, panel), "stock"]);
  if (user.role === "07") modules.push(["Liquidación de rutas", financeView("liquidaciones", user, request, handle, panel), "stock"]);
  if (user.role === "03") modules.push(["Devoluciones y mermas", financeView("devoluciones", user, request, handle, panel), "box"]);
  if (user.role === "01") modules.push(["Tablero gerencial", financeView("indicadores", user, request, handle, panel), "stock"]);
  if (user.role === "10") modules.push(["Mis facturas y pagos", financeView("pse", user, request, handle, panel), "stock"]);
  if (["03", "04"].includes(user.role)) modules.push(["Alistamiento FEFO", logisticsView("picking", user, request, handle, panel), "box"]);
  if (user.role === "07") modules.push(["Planificar distribución", logisticsView("routes", user, request, handle, panel), "stock"]);
  if (user.role === "03") modules.push(["Cargue y manifiestos", logisticsView("dispatch", user, request, handle, panel), "upload"]);
  if (user.role === "08") modules.push(["Mis entregas", logisticsView("deliveries", user, request, handle, panel), "stock"]);
  if (user.role === "10") modules.push(["Seguimiento de pedidos", trackingView(user, request, handle, panel), "clock"]);
  if (user.role === "05") modules.push(["Proveedores", commercialView("proveedores"), "user"]);
  if (["01", "03", "04", "05"].includes(user.role)) modules.push(["Compras y recepción", commercialView("compras"), "box"]);
  if (["01", "06"].includes(user.role)) modules.push(["Clientes", commercialView("clientes"), "user"]);
  if (["06", "10"].includes(user.role)) modules.push([user.role === "10" ? "Portal de pedidos" : "Pedidos de venta", commercialView("pedidos"), "stock"]);
  if (user.role === "02") modules.push(["Usuarios y roles", users, "user"]);
  if (user.role === "02") modules.push(["Solicitudes y contacto", publicAdmin(request, handle, panel), "user"]);
  if (user.catalog) modules.push(["Catálogo", products, "box"]);
  if (user.inventory) modules.push(["Inventario", inventory, "stock"]);
  if (user.role === "03") modules.push(["Importar inventario", importer, "upload"]);
  if (user.role === "02") modules.push(["Auditoría de accesos", audit, "clock"]);
  const roleCopy = {
    "01": "Dirección y control", "02": "Administración y seguridad", "03": "Control de bodega",
    "04": "Preparación de pedidos", "05": "Abastecimiento", "06": "Gestión comercial",
    "07": "Centro de distribución", "08": "Mi jornada de reparto", "09": "Control contable", "10": "Mi finca y mis pedidos",
  };
  document.querySelector(".workspace-brand .subtitle").textContent = roleCopy[user.role];
  const nav = $("menu");
  const openWorkspaceModule = (title) => {
    const index = modules.findIndex((entry) => entry[0] === title);
    if (index >= 0) nav.children[index]?.click();
  };
  modules.unshift(["Inicio", workspaceHome(user, request, panel, openWorkspaceModule, handle), "box"]);
  nav.hidden = !modules.length;
  nav.replaceChildren();
  for (const [title, render, symbol] of modules) {
    const item = button(title, async () => {
      stopCamera();
      activeModule = render;
      $("section-title").textContent = title;
      if (matchMedia("(max-width: 760px)").matches) sidebarOpen(false);
      for (const other of nav.children) other.setAttribute("aria-current", String(other === item));
      window.scrollTo({top:0,behavior:"instant"});
      panel.hidden = false;
      panel.classList.remove("workspace-home");
      panel.removeAttribute("data-layout");
      panel.classList.remove("module-enter");
      requestAnimationFrame(() => panel.classList.add("module-enter"));
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
    if (navigator.onLine && document.visibilityState === "visible") {
      request("/api/session").catch((error) => notify(error.message, true));
    }
  }, 15000);
  if (user.role === "08") syncDeliveries(user.id, request).catch((error) => notify(error.message, true));
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
  const token = activationToken;
  await request("/api/activate", { ...values(form), token });
  if (activationToken !== token) return;
  form.reset();
  activationToken = null;
  showLogin();
  notify("Contraseña configurada. Ya puedes iniciar sesión.");
});
$("logout").onclick = handle(async () => {
  await request("/api/logout", {});
  localStorage.removeItem("villali-driver");
  showLogin();
});
window.addEventListener("online", () => {
  if (user?.role === "08") syncDeliveries(user.id, request).then(() => {
    if (user?.role === "08" && activeModule && !panel.querySelector("dialog[open]")) return activeModule();
  }).catch((error) => notify(error.message, true));
});
if ("serviceWorker" in navigator) navigator.serviceWorker.register("/service-worker.js").catch(() => {});

for (const event of ["pointerdown", "keydown", "input"]) {
  document.addEventListener(event, () => {
    if (!user || !navigator.onLine || Date.now() - lastActivity < 30000) return;
    lastActivity = Date.now();
    request("/api/activity", {}).catch((error) => notify(error.message, true));
  });
}

async function users() {
  panel.innerHTML = `<div class="page-heading"><div><h1>Usuarios y roles</h1>
    <p>Administra las cuentas y sus permisos de acceso.</p></div><button id="new-user" disabled>+ Nuevo usuario</button></div>
    <div class="grid toolbar"><label>Buscar usuario <input type="search" id="user-search" placeholder="Nombre o usuario"></label>
      <label>Rol <select id="role-filter"><option value="">Todos los roles</option></select></label>
      <label>Estado <select id="user-status"><option value="">Todos</option><option value="active">Activo</option><option value="pending">Por activar</option><option value="inactive">Inactivo</option></select></label></div>
    <dialog id="user-dialog" aria-labelledby="user-dialog-title"><h2 id="user-dialog-title">Nuevo usuario</h2><p>La invitación permite definir la contraseña una sola vez.</p>
    <form id="user-form"><div class="grid">
      <label>Usuario <input name="username" required maxlength="80"></label>
      <label>Nombre <input name="name" required maxlength="120"></label>
      <label>Correo <input name="email" type="email" maxlength="254" autocomplete="off"></label>
      <label>Rol <select name="role" required></select></label></div>
      <div id="user-options" hidden><label class="check"><input type="checkbox" name="active" checked> Cuenta activa</label>
      <label class="check"><input type="checkbox" name="invite"> Generar una invitación nueva</label></div>
      <p class="form-error" role="alert" hidden></p>
      <div class="actions"><button type="button" class="secondary" id="delete-user" hidden>Eliminar cuenta</button>
      <button type="button" class="secondary" id="cancel-user">Cancelar</button><button id="save-user">Crear usuario</button></div>
    </form></dialog><div id="user-result" aria-live="polite"></div>`;
  const form = $("user-form");
  const result = $("user-result");
  const dialog = $("user-dialog");
  const deleteAccount = $("delete-user");
  const saveAccount = $("save-user");
  const cancel = $("cancel-user");
  const newAccount = $("new-user");
  const { users: records, roles } = await withLoading(result, "table", "Cargando usuarios…", () => request("/api/users"));
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
    deleteAccount.hidden = true;
    saveAccount.textContent = "Crear usuario";
    $("user-dialog-title").textContent = "Nuevo usuario";
    form.querySelector(".form-error").hidden = true;
  };
  const setPending = (pending) => {
    for (const control of [saveAccount, deleteAccount, cancel]) control.disabled = pending;
    dialog.setAttribute("aria-busy", String(pending));
  };
  dialog.oncancel = (event) => { if (saveAccount.disabled) event.preventDefault(); };
  cancel.onclick = () => dialog.close();
  newAccount.disabled = false;
  newAccount.onclick = () => { reset(); dialog.showModal(); };
  deleteAccount.onclick = handle(async () => {
    if (saveAccount.disabled) return;
    const username = form.elements.username.value;
    if (!confirm(`¿Eliminar definitivamente la cuenta «${username}»? Se cerrarán sus sesiones y se invalidarán sus invitaciones.`)) return;
    setPending(true);
    try {
      const deleted = await saveForm(form, "/api/users/delete", { id: selected, username });
      if (!deleted || !form.isConnected) return;
      const index = records.findIndex((row) => row.id === selected);
      if (index !== -1) records.splice(index, 1);
      dialog.close();
      renderRows();
      notify(`Se eliminó la cuenta «${username}».`);
    } finally {
      setPending(false);
    }
  });
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
      form.elements.email.value = row.email || "";
      form.elements.role.value = row.role;
      form.elements.active.checked = Boolean(row.active);
      form.elements.invite.checked = false;
      $("user-options").hidden = false;
      deleteAccount.hidden = row.id === user.id;
      saveAccount.textContent = "Guardar cambios";
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
    if (saveAccount.disabled) return;
    if (selected && wasActive && !form.elements.active.checked && !confirm("¿Desactivar esta cuenta?")) return;
    setPending(true);
    try {
      const saved = await saveForm(form, "/api/users", { ...values(form), id: selected,
        active: form.elements.active.checked, invite: form.elements.invite.checked });
      if (!saved || !form.isConnected) return;
      const index = records.findIndex((row) => row.id === saved.account.id);
      if (index === -1) records.push(saved.account);
      else records[index] = saved.account;
      records.sort((a, b) => (a.username > b.username) - (a.username < b.username));
      dialog.close();
      renderRows();
      notify(saved.mail_status === "aceptado" ? "Usuario guardado. El proveedor aceptó el correo de invitación."
        : saved.mail_status === "error" ? "Usuario guardado. No se pudo enviar el correo. Comparte el enlace manualmente."
        : "Usuario guardado.");
      if (saved.invitation) {
        const link = document.createElement("a");
        link.href = saved.invitation;
        link.target = "_blank";
        link.rel = "noopener";
        link.textContent = "Abrir invitación (nueva pestaña)";
        $("notice").append(document.createElement("br"), link);
      }
    } finally {
      setPending(false);
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

const commerceLabels = {
  proveedores: "Proveedores", compras: "Compras y recepción",
  clientes: "Clientes", pedidos: "Pedidos de venta",
};

function commercialView(kind) {
  return async function render() {
    const title = kind === "pedidos" && user.role === "10" ? "Portal de pedidos" : commerceLabels[kind];
    const path = "/api/comercio/" + kind;
    panel.innerHTML = "<h1></h1><div></div>";
    panel.firstElementChild.textContent = title;
    const heading = panel.firstElementChild;
    const body = panel.lastElementChild;
    const data = await withLoading(body, "table", "Cargando registros…", () => request(path));
    if (!heading.isConnected) return;
    body.remove();
    const portal = kind === "pedidos" && user.role === "10";
    if (portal && !data.portal) {
      panel.append(commercialNote("Tu cuenta todavía no tiene una ficha activa vinculada. Pide a tu asesor que te asigne tu propia cuenta del portal."));
      return;
    }
    if (portal) panel.append(commercialNote(`Cliente: ${data.portal.name} · Lista de precios ${data.portal.price_list}`));

    function openForm(title, fields, fill, payload, submitLabel = "Guardar") {
      const dialog = document.createElement("dialog");
      dialog.innerHTML = '<h2></h2><form><div class="grid"></div><p class="form-error" role="alert" hidden></p>' +
        '<div class="actions"><button type="button" class="secondary">Cancelar</button><button>Guardar</button></div></form>';
      dialog.querySelector("h2").textContent = title;
      const form = dialog.querySelector("form");
      form.firstElementChild.innerHTML = fields;
      fill(form);
      const requestId = crypto.randomUUID();
      const cancel = form.querySelector('button[type="button"].secondary');
      const submit = form.lastElementChild.lastElementChild;
      submit.textContent = submitLabel;
      cancel.onclick = () => dialog.close();
      dialog.onclose = () => dialog.remove();
      dialog.oncancel = (event) => { if (submit.disabled) event.preventDefault(); };
      form.onsubmit = handle(async () => {
        if (submit.disabled) return;
        submit.disabled = cancel.disabled = true;
        try {
          const result = await saveForm(form, path, { ...payload(form), request_id: requestId });
          if (!result || !heading.isConnected) return;
          dialog.close();
          await render();
          notify(result.number ? result.number + " · " + result.status : "Registro guardado.");
        } finally {
          submit.disabled = cancel.disabled = false;
        }
      });
      panel.append(dialog);
      dialog.showModal();
    }

    function options(select, list, key, label) {
      select.replaceChildren(...list.map((row) => new Option(label(row), row[key])));
    }

    function editVendor(row = {}) {
      openForm(row.id ? "Editar proveedor" : "Nuevo proveedor",
        '<label>NIT y dígito de verificación <input name="nit" required><small>Ejemplo: 900123456-8, con guion y sin puntos.</small></label>' +
        '<label>Razón social <input name="name" maxlength="120" required><small>Ejemplo: Distribuciones La Cumbre.</small></label>' +
        '<label>Contacto <input name="contact" maxlength="120" required><small>Ejemplo: Mariana Solano, área comercial.</small></label>' +
        '<label>Condiciones de pago <input name="terms" maxlength="120" required><small>Ejemplo: crédito a 30 días desde la fecha de factura.</small></label>' +
        '<fieldset class="commercial-products"><legend>Productos suministrados</legend>' +
        '<label>Buscar por nombre o SKU <input type="search" name="product_search"></label>' +
        '<small>Marca los productos que puedes comprar a este proveedor.</small><div data-products></div><small data-selected></small></fieldset>' +
        '<label class="check"><input name="active" type="checkbox" checked> Proveedor activo</label>',
        (form) => {
          const list = form.querySelector("[data-products]");
          const current = new Set(row.skus || []);
          const choices = data.products.map((item) => {
            const label = document.createElement("label");
            label.className = "check";
            const input = document.createElement("input");
            input.type = "checkbox";
            input.name = "skus";
            input.value = item.sku;
            input.checked = current.has(item.sku);
            label.append(input, item.sku + " · " + item.name);
            list.append(label);
            return label;
          });
          const count = () => {
            form.querySelector("[data-selected]").textContent = `${list.querySelectorAll(":checked").length} seleccionados`;
          };
          list.onchange = count;
          count();
          form.elements.product_search.oninput = () => {
            const query = form.elements.product_search.value.trim().toLowerCase();
            for (const choice of choices) choice.hidden = !choice.textContent.toLowerCase().includes(query);
          };
          for (const name of ["name", "contact", "terms"]) form.elements[name].value = row[name] || "";
          form.elements.nit.value = row.id || "";
          form.elements.nit.readOnly = Boolean(row.id);
          form.elements.active.checked = row.active ?? true;
        }, (form) => ({ nit: form.elements.nit.value, name: form.elements.name.value,
                        contact: form.elements.contact.value, terms: form.elements.terms.value,
                        id: row.id, active: form.elements.active.checked, skus: new FormData(form).getAll("skus") }));
    }

    function editClient(row = {}) {
      if (user.role === "01") {
        openForm("Cupo y cartera",
          '<label>Cupo (COP) <input name="credit" type="number" min="0" required></label>' +
          '<label>Saldo pendiente (COP) <input name="balance" type="number" min="0" required></label>' +
          '<label>Vencimiento más antiguo <input name="due" type="date"></label>',
          (form) => {
            form.elements.credit.value = row.credit / 100;
            form.elements.balance.value = row.balance / 100;
            form.elements.due.value = row.due;
          }, (form) => ({ id: row.id, credit: Number(form.elements.credit.value) * 100,
                          balance: Number(form.elements.balance.value) * 100, due: form.elements.due.value }));
        return;
      }
      openForm(row.id ? "Editar cliente" : "Nuevo cliente",
        '<label>Nombre <input name="name" maxlength="120" required></label>' +
        '<label>Zona de entrega <input name="zone" maxlength="120" required></label>' +
        '<label>Tipo <select name="type"><option value="mayorista">Mayorista · Lista A</option>' +
        '<option value="minorista">Minorista · Lista B</option></select></label>' +
        '<label>Cuenta del portal <select name="account"></select><small>Vincula una cuenta individual de rol Cliente a esta ficha.</small></label>' +
        '<label class="check"><input name="consent" type="checkbox" required> Autorización de datos registrada</label>' +
        '<label class="check"><input name="active" type="checkbox" checked> Cliente activo</label>',
        (form) => {
          const available = data.accounts.filter((account) => !account.linked || account.linked === row.id);
          options(form.elements.account, [{id: 0, name: "Sin cuenta"}, ...available], "id", (item) => item.name);
          form.elements.account.value = String(row.account || 0);
          form.elements.type.value = row.type || "minorista";
          form.elements.name.value = row.name || "";
          form.elements.zone.value = row.zone || "";
          form.elements.active.checked = row.active ?? true;
          form.elements.consent.checked = Boolean(row.consent);
        }, (form) => ({ ...values(form), id: row.id, active: form.elements.active.checked,
                        consent: form.elements.consent.checked }));
    }

    function orderForm(purchase) {
      const parties = purchase ? data.suppliers : (portal ? [] : data.customers);
      openForm(purchase ? "Nueva orden de compra" : "Nuevo pedido",
        (portal ? "" : '<label>' + (purchase ? "Proveedor" : "Cliente") + ' <select name="party" required></select></label>') +
        '<div data-items></div><div class="actions" data-add></div><p data-total></p>' +
        (purchase ? "" : '<label class="check"><input name="credit" type="checkbox"> Pedido a crédito</label>'),
        (form) => {
          const items = form.querySelector("[data-items]");
          const chosen = () => portal ? null : parties.find((item) => item.id === form.elements.party.value);
          if (!portal) options(form.elements.party, parties, "id", (item) => item.name);
          function optionText(item) {
            if (purchase) return item.sku + " · " + item.name;
            const cents = !portal && chosen()?.price_list === "A" ? Math.round(item.price_cents * .95) : item.price_cents;
            return item.name + " · " + money(cents / 100) + " · Disponible: " + item.available;
          }
          function refresh() {
            const party = chosen();
            const catalog = (data.products || []).filter((item) => !purchase || party?.skus.includes(item.sku));
            for (const select of items.querySelectorAll("select")) {
              const previous = select.value;
              options(select, catalog, "sku", optionText);
              for (const option of select.options) {
                const item = catalog.find((product) => product.sku === option.value);
                option.disabled = !purchase && item.available === 0;
                if (option.disabled) option.textContent += " · Agotado";
              }
              select.value = catalog.some((item) => item.sku === previous) ? previous :
                ([...select.options].find((option) => !option.disabled)?.value || "");
            }
            add.disabled = !catalog.some((item) => purchase || item.available > 0);
            form.querySelector("[data-total]").textContent = "Total: " + money([...items.children].reduce((sum, row) => {
              const product = catalog.find((item) => item.sku === row.querySelector("select").value);
              if (!product) return sum;
              const cents = !portal && party?.price_list === "A" ? Math.round(product.price_cents * .95) : product.price_cents;
              const unit = purchase ? Number(row.querySelector("[name=cost]").value) : cents / 100;
              return sum + unit * Number(row.querySelector("[name=quantity]").value);
            }, 0));
          }
          function addLine() {
            const row = document.createElement("div");
            row.className = "grid";
            row.innerHTML = '<label>Producto <select required></select></label>' +
              '<label>Cantidad <input name="quantity" type="number" min="1" value="1" required><small>Ejemplo: 20 unidades.</small></label>' +
              (purchase ? '<label>Costo unitario (COP) <input name="cost" type="number" min="1" required><small>Ejemplo: 125000 por unidad.</small></label>' : "");
            row.append(button("Quitar producto", () => { row.remove(); refresh(); }));
            items.append(row);
            refresh();
          }
          const add = button("Agregar producto", addLine);
          form.querySelector("[data-add]").append(add);
          form.oninput = refresh;
          addLine();
        }, (form) => ({
          action: "create", ...(!portal ? { [purchase ? "supplier" : "customer"]: form.elements.party.value } : {}),
          credit: Boolean(form.elements.credit?.checked),
          lines: [...form.querySelector("[data-items]").children].map((row) => ({
            sku: row.querySelector("select").value, quantity: row.querySelector("[name=quantity]").value,
            cost: row.querySelector("[name=cost]")?.value,
          })),
        }), purchase ? "Crear orden" : (portal ? "Enviar pedido" : "Confirmar pedido"));
    }

    function details(row, purchase) {
      const block = document.createElement("details");
      const caption = document.createElement("summary");
      caption.textContent = "Ver productos";
      const fields = ["Producto", "Cantidad", "Valor unitario"];
      if (purchase) fields.push("Recibido", "Pendiente");
      else if (!portal) fields.push("Reserva");
      block.append(caption, table(fields, row.lines.map((line) => [
        line.name, line.quantity, money(line.price / 100), ...(purchase ? [line.received, line.quantity - line.received] :
          (portal ? [] : [(line.reservations || []).map((lot) => lot.lot + " · " + lot.quantity).join(", ")])),
      ])));
      if (purchase && row.receipts.length) {
        block.append(table(["Lote", "Ubicación", "Vencimiento", "Cantidad"],
          row.receipts.map((lot) => [lot.lot, lot.location, lot.expiry, lot.quantity])));
      }
      return block;
    }

    function receive(row) {
      const pending = row.lines.filter((line) => line.quantity > line.received);
      openForm("Recibir mercancía · " + row.number,
        '<label>Producto pendiente <select name="sku" required></select><small>Selecciona el producto que llegó en este lote.</small></label>' +
        '<label>Código EAN del empaque <input name="scan" inputmode="numeric" pattern="[0-9]{13}"><small>Opcional. El lector selecciona el producto correspondiente.</small></label>' +
        '<label>Lote <input name="lot" required><small>Ejemplo: LT-2026-014.</small></label>' +
        '<label>Ubicación <input name="location" required><small>Ejemplo: Bodega A, estante 02.</small></label>' +
        '<label>Vencimiento <input name="expiry" type="date" required><small>Debe quedar al menos a seis meses.</small></label>' +
        '<label>Cantidad recibida <input name="quantity" type="number" min="1" required><small data-pending></small></label>',
        (form) => {
          options(form.elements.sku, pending, "sku", (line) => line.name + " · " + line.sku);
          const update = () => {
            const barcode = form.elements.scan.value;
            const match = pending.find((item) => data.barcodes[item.sku] === barcode);
            form.elements.scan.setCustomValidity(barcode && !match ? "El EAN debe coincidir con un producto pendiente de esta orden." : "");
            if (match) form.elements.sku.value = match.sku;
            const line = pending.find((item) => item.sku === form.elements.sku.value);
            const available = line.quantity - line.received;
            form.querySelector("[data-pending]").textContent = `${available} pendientes de este producto. Puedes recibir menos.`;
            form.elements.quantity.max = available;
          };
          form.elements.sku.onchange = () => { form.elements.scan.value = ""; update(); };
          form.elements.scan.onkeydown = (event) => { if (event.key === "Enter") event.preventDefault(); };
          form.elements.scan.oninput = update;
          update();
        },
        (form) => ({ ...values(form), sku: form.elements.scan.value || form.elements.sku.value, id: row.id, action: "receive" }),
        "Registrar recepción");
    }

    function confirmOrder(row, action, label) {
      openForm(label, '<p data-confirm></p>',
        (form) => { form.querySelector("[data-confirm]").textContent = row.number + " · " + money(row.total / 100); },
        () => ({ id: row.id, action }), action === "approve" ? "Aprobar orden" : "Confirmar pedido");
    }

    if (kind === "proveedores") {
      panel.append(button("Nuevo proveedor", () => editVendor()), table(["NIT", "Proveedor", "Contacto", "Pago", "Estado", ""],
        data.rows.map((row) => [row.id, row.name, row.contact, row.terms, row.active ? "Activo" : "Inactivo",
                                button("Editar", () => editVendor(row))])));
      return;
    }
    if (kind === "clientes") {
      if (user.role === "06") panel.append(button("Nuevo cliente", () => editClient()));
      panel.append(table(["Cliente", "Tipo", "Zona", "Lista", "Cupo", "Estado", ""],
        data.rows.map((row) => [row.name, row.type, row.zone, row.price_list, money(row.credit / 100),
                                row.active ? "Activo" : "Inactivo", button("Editar", () => editClient(row))])));
      return;
    }
    const purchase = kind === "compras";
    if (purchase) {
      const help = {
        "05": "Crea la orden con un proveedor activo. Las órdenes superiores a $10 millones requieren aprobación de Gerencia.",
        "01": "Usa Aprobar orden en las compras pendientes para habilitar su recepción en Bodega.",
        "03": "Usa Registrar recepción en las órdenes aprobadas o parciales. Puedes recibir un lote a la vez.",
        "04": "Usa Registrar recepción en las órdenes aprobadas o parciales. Puedes recibir un lote a la vez.",
      };
      panel.append(commercialNote(help[user.role]));
    }
    if ((purchase && user.role === "05") || !purchase) {
      const create = button(purchase ? "Nueva orden de compra" : "Nuevo pedido", () => orderForm(purchase));
      create.disabled = purchase ? !data.suppliers.length : (!portal && !data.customers.length);
      panel.append(create);
      if (create.disabled) panel.append(commercialNote(purchase ?
        "Activa un proveedor y asígnale productos desde Proveedores." : "Crea una ficha de cliente activa desde Clientes."));
    }
    if (!data.rows.length) {
      panel.append(commercialNote(purchase ? "Aún no hay órdenes de compra." : "Aún no hay pedidos."));
      return;
    }
    panel.append(table(["Número", purchase ? "Proveedor" : (portal ? "Fecha" : "Cliente"), "Total", "Estado", "Detalle", "Acción"],
      data.rows.map((row) => {
        let action = purchase ? ({
          "Pendiente de aprobación": "Espera aprobación de Gerencia",
          "Aprobada": "Pendiente de recepción en Bodega",
          "Recibida parcial": "Pendiente de completar en Bodega",
          "Recibida completa": "Recepción finalizada",
        }[row.status] || "") : "";
        if (purchase && user.role === "01" && row.status === "Pendiente de aprobación") {
          action = button("Aprobar orden", () => confirmOrder(row, "approve", "Aprobar compra"));
        } else if (purchase && ["03", "04"].includes(user.role) && ["Aprobada", "Recibida parcial"].includes(row.status)) {
          action = button("Registrar recepción", () => receive(row));
        } else if (!purchase && user.role === "06" && row.status === "PENDIENTE_REVISIÓN") {
          action = button("Confirmar", () => confirmOrder(row, "confirm", "Confirmar y reservar inventario"));
        }
        return [row.number, purchase ? row.supplier_name : (portal ? row.date.slice(0, 10) : row.customer_name),
                money(row.total / 100), row.status === "PENDIENTE_REVISIÓN" ? "Pendiente de revisión" : row.status,
                details(row, purchase), action];
      })));
  };
}

function commercialNote(message) {
  const element = document.createElement("p");
  element.className = "section-intro";
  element.textContent = message;
  return element;
}

function money(pesos) {
  return new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP" }).format(pesos);
}


async function audit() {
  panel.innerHTML = "<h1>Auditoría de accesos</h1><p>Registro de actividad y seguridad. Las fechas se muestran en UTC.</p><div></div>";
  const body = panel.lastElementChild;
  const rows = await withLoading(body, "table", "Cargando auditoría…", () => request("/api/audit"));
  if (!body.isConnected) return;
  body.append(table(["Fecha UTC", "Usuario", "Evento", "IP", "Detalle"],
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
    result.replaceChildren();
    const data = await withLoading(result, "table", "Cargando catálogo…", () => request("/api/products?" + query));
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
      <label>Tipo de carga <select id="import-mode">
        <option value="add" selected>Carga adicional</option><option value="initial">Carga inicial</option>
      </select><small>Carga adicional agrega lotes nuevos al saldo existente. Usa Carga inicial para la primera carga de bodega.</small></label>
      <label class="drop-zone" id="drop-zone">${icon("upload")}<strong>Selecciona o arrastra un archivo Excel</strong>
      <span>Formato .xlsx · Usa la plantilla para registrar los lotes.</span>
      <input id="inventory-file" type="file" accept=".xlsx" required></label>
      <div class="actions"><button>Validar archivo</button><button type="button" id="confirm-import" disabled>Confirmar carga</button></div>
    </form><div id="import-result"></div>`;
  const fileInput = $("inventory-file");
  const importForm = $("import-form");
  const modeInput = $("import-mode");
  const confirm = $("confirm-import");
  const result = $("import-result");
  let verified;
  let busy = false;
  const validate = importForm.querySelector("button");
  function setBusy(progress) {
    busy = progress;
    for (const control of [fileInput, modeInput, validate]) control.disabled = progress;
    confirm.disabled = progress || !verified;
  }
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
  modeInput.onchange = fileInput.onchange;
  const dropZone = $("drop-zone");
  dropZone.ondragover = (event) => { event.preventDefault(); dropZone.classList.add("drag-over"); };
  dropZone.ondragleave = () => dropZone.classList.remove("drag-over");
  dropZone.ondrop = (event) => {
    event.preventDefault();
    dropZone.classList.remove("drag-over");
    if (busy) return;
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
  importForm.onsubmit = handle(async () => {
    if (busy) return;
    const file = fileInput.files[0];
    const mode = modeInput.value;
    verified = undefined;
    setBusy(true);
    result.replaceChildren();
    try {
      const data = await withLoading(result, "summary", "Validando los lotes…",
        () => request("/api/import/preview?mode=" + mode, file, true));
      if (!fileInput.isConnected) return;
      setStep(2);
      if (data.repeat) {
        result.textContent = "Este archivo ya se cargó.";
        return;
      }
      if (data.errors.length) {
        showErrors(data.errors);
        notify("Corrige las filas señaladas antes de confirmar.", true);
        return;
      }
      verified = { file, digest: data.digest, mode };
      result.textContent = `Validación correcta. ${data.count} lotes y ${data.units} unidades para cargar.`;
    } finally {
      setBusy(false);
    }
  });
  confirm.onclick = handle(async () => {
    if (busy || !verified) return;
    if (!window.confirm("¿Confirmar la carga de los lotes del archivo validado?")) return;
    setBusy(true);
    result.replaceChildren();
    try {
      const url = "/api/import/confirm?" + new URLSearchParams({digest: verified.digest, mode: verified.mode});
      const data = await withLoading(result, "summary", "Guardando los lotes…",
        () => request(url, verified.file, true));
      verified = undefined;
      if (fileInput.isConnected) setStep(3);
      result.textContent = data.repeat ? "Este archivo ya se cargó." : `Carga guardada. ${data.count} saldos por lote.`;
    } catch (error) {
      if (error.details) {
        verified = undefined;
        showErrors(error.details);
      }
      throw error;
    } finally {
      setBusy(false);
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
    const products = await withLoading(result, overview ? "stock" : "lots", "Cargando inventario…",
      () => request("/api/inventory?" + new URLSearchParams(query)));
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

window.addEventListener("hashchange", openInvitation);
if (!openInvitation()) {
  showLogin();
  startSession().catch(() => showLogin());
}
