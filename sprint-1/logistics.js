import { stored, queueDelivery, synchronize } from "/driver-store.js";
export const syncDeliveries = synchronize;

const labels = { picking: "Alistamiento FEFO", routes: "Planificar distribución", dispatch: "Cargue y despacho",
  deliveries: "Mis entregas" };
const stateLabel = (state) => ({ CONFIRMADO: "Confirmado", ALISTADO: "Alistado", EN_RUTA: "En ruta",
  ENTREGADO: "Entregado", NOVEDAD: "Novedad", PLANIFICADA: "Planificada", FINALIZADA: "Finalizada" }[state] || state);

function text(tag, content, className) {
  const node = document.createElement(tag);
  node.textContent = content;
  if (className) node.className = className;
  return node;
}

function link(label, url) {
  const node = text("a", label, "download secondary");
  node.href = url;
  node.target = "_blank";
  node.rel = "noopener";
  return node;
}

function input(label, name, type = "text", hint = "") {
  const node = document.createElement("label");
  node.append(document.createTextNode(label));
  const field = document.createElement("input");
  field.name = name;
  field.type = type;
  field.required = true;
  if (type === "number") field.step = "any";
  node.append(field);
  if (hint) node.append(text("small", hint));
  return node;
}

function select(label, name, rows) {
  const node = document.createElement("label");
  node.append(document.createTextNode(label));
  const field = document.createElement("select");
  field.name = name;
  field.required = true;
  for (const [value, caption] of rows) field.add(new Option(caption, value));
  node.append(field);
  return node;
}

function alertTone() {
  try {
    const audio = new AudioContext();
    const oscillator = audio.createOscillator();
    const gain = audio.createGain();
    oscillator.frequency.value = 220;
    gain.gain.value = .08;
    oscillator.connect(gain).connect(audio.destination);
    oscillator.onended = () => audio.close();
    oscillator.start();
    oscillator.stop(audio.currentTime + .22);
  } catch {}
}

function openDialog(panel, title, submitLabel, fields, submitAction, handle) {
  const dialog = document.createElement("dialog");
  dialog.setAttribute("aria-label", title);
  const form = document.createElement("form");
  const error = text("p", "", "form-error");
  error.hidden = true;
  const controls = document.createElement("div");
  controls.className = "actions";
  const cancel = text("button", "Cancelar", "secondary");
  cancel.type = "button";
  cancel.onclick = () => dialog.close();
  const submit = text("button", submitLabel);
  controls.append(cancel, submit);
  form.append(text("h2", title), ...fields, error, controls);
  dialog.append(form);
  dialog.onclose = () => dialog.remove();
  dialog.oncancel = (event) => { if (submit.disabled) event.preventDefault(); };
  form.onsubmit = handle(async () => {
    if (submit.disabled) return;
    cancel.disabled = submit.disabled = true;
    error.hidden = true;
    try {
      await submitAction(Object.fromEntries(new FormData(form)), form);
      dialog.close();
    } catch (problem) {
      alertTone();
      error.textContent = problem.message;
      error.hidden = false;
    } finally { cancel.disabled = submit.disabled = false; }
  });
  panel.append(dialog);
  dialog.showModal();
  return form;
}

function routeMap(route) {
  const points = [route.origin, ...route.stops.map((stop) => stop.destination)];
  const box = document.createElement("div");
  box.className = "route-map";
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 600 240");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", "Mapa esquemático de visitas en orden sugerido por proximidad");
  const lats = points.map((point) => point.lat);
  const lngs = points.map((point) => point.lng);
  const minLat = Math.min(...lats), minLng = Math.min(...lngs);
  const latRange = Math.max(...lats) - minLat || .01;
  const lngRange = Math.max(...lngs) - minLng || .01;
  const projected = points.map((point) => [40 + (point.lng - minLng) / lngRange * 520,
    200 - (point.lat - minLat) / latRange * 160]);
  const path = document.createElementNS(svg.namespaceURI, "polyline");
  path.setAttribute("points", projected.map((point) => point.join(",")).join(" "));
  path.setAttribute("fill", "none");
  path.setAttribute("stroke", "#41845c");
  path.setAttribute("stroke-width", "3");
  svg.append(path);
  projected.forEach(([x, y], index) => {
    const circle = document.createElementNS(svg.namespaceURI, "circle");
    circle.setAttribute("cx", x);
    circle.setAttribute("cy", y);
    circle.setAttribute("r", "12");
    circle.setAttribute("fill", index ? "#f3cd39" : "#205631");
    const label = document.createElementNS(svg.namespaceURI, "text");
    label.setAttribute("x", x);
    label.setAttribute("y", y + 4);
    label.setAttribute("text-anchor", "middle");
    label.setAttribute("fill", index ? "#142e1d" : "#fff");
    label.textContent = index || "B";
    svg.append(circle, label);
  });
  box.append(svg, text("small", "B · Bodega. Visitas ordenadas por cercanía entre coordenadas; recorrido esquemático."));
  return box;
}

export function logisticsView(kind, user, request, handle, panel) {
  return async function render() {
    const loading = text("div", "", "logistics-loading");
    const loadingStatus = text("p", "Cargando la jornada…", "section-intro");
    loadingStatus.setAttribute("role", "status");
    loading.append(loadingStatus);
    for (let index = 0; index < 3; index++) {
      const skeleton = text("div", "", "logistics-card skeleton");
      skeleton.setAttribute("aria-hidden", "true");
      loading.append(skeleton);
    }
    panel.replaceChildren(loading);
    const marker = panel.firstChild;
    let data;
    const path = "/api/logistica/" + kind;
    try {
      data = await request(path);
      if (kind === "deliveries") await stored("journeys", "readwrite", (store) => store.put({ userId: user.id, data }));
    } catch (error) {
      if (kind !== "deliveries" || navigator.onLine) throw error;
      data = (await stored("journeys", "readonly", (store) => store.get(user.id)))?.data;
      if (!data) throw new Error("Abre tu jornada con conexión antes de salir a repartir.");
    }
    if (!marker.isConnected) return;
    panel.replaceChildren(text("p", user.role_name, "role-eyebrow"), text("h1", labels[kind]));
    const explanation = {
      picking: "Toma los lotes en el orden indicado. Confirma cada referencia con su EAN antes de finalizar.",
      routes: "Registra el peso por unidad y el destino de cada cliente. Después asigna los pedidos alistados.",
      dispatch: "Verifica los rótulos de la ruta y emite el manifiesto al completar el cargue.",
      deliveries: "Abre una entrega para registrar el resultado. Las confirmaciones pendientes se sincronizan al recuperar conexión.",
    };
    panel.append(text("p", explanation[kind], "section-intro"));
    const action = (label, fn, secondary = true) => {
      const button = text("button", label, secondary ? "secondary" : "");
      button.type = "button";
      button.onclick = handle(fn);
      return button;
    };
    const mutation = async (payload) => {
      await request(path, payload);
      if (panel.isConnected) await render();
    };
    const formAction = (title, caption, fields, build, after) => {
      const key = crypto.randomUUID();
      return openDialog(panel, title, caption, fields, async (values, form) => {
        await request(path, { ...build(values, form), request_id: key });
        if (after) after();
        if (panel.isConnected) await render();
      }, handle);
    };
    const viewProof = async (stop) => {
      const evidence = await request("/api/logistica/evidence?id=" + stop.order);
      const dialog = text("dialog", "", "delivery-proof");
      dialog.setAttribute("aria-label", "Evidencia de entrega");
      dialog.append(text("h2", stop.number), text("p", evidence.at ?
        "Registrada el " + new Date(evidence.at).toLocaleString("es-CO") : "Todavía no hay una confirmación de entrega."));
      if (evidence.note) dialog.append(text("p", evidence.note));
      for (const [key, label] of [["signature", "Firma de recepción"], ["photo", "Fotografía de entrega"]]) {
        if (!evidence[key]) continue;
        const image = document.createElement("img");
        image.src = evidence[key];
        image.alt = label;
        dialog.append(text("h3", label), image);
      }
      const close = action("Cerrar", () => dialog.close());
      dialog.append(close);
      dialog.onclose = () => dialog.remove();
      panel.append(dialog);
      dialog.showModal();
    };

    if (kind === "picking") {
      const rows = data.orders || [];
      if (!rows.length) panel.append(text("p", "No hay pedidos confirmados o alistados pendientes de ruta."));
      for (const order of rows) {
        const card = text("article", "", "logistics-card");
        card.append(text("span", stateLabel(order.status), "logistics-state"), text("h2", order.number),
          text("p", order.customer_name));
        for (const line of order.lines) {
          const row = text("div", "", "picking-line");
          row.append(text("strong", line.name), text("p", line.quantity + " unidades · " + line.sku));
          const list = document.createElement("ul");
          for (const allocation of line.reservations || []) list.append(text("li",
            allocation.lot + " · " + allocation.location + " · " + allocation.quantity + " und · Vence " + (allocation.expiry || "Consultar lote")));
          row.append(list);
          if (line.picked) row.append(text("span", "Producto verificado", "badge verde"));
          else row.append(action("Escanear producto", () => {
            const field = input("Código EAN del producto", "barcode", "text", "Usa el lector o escribe los 13 dígitos.");
            formAction("Verificar · " + line.name, "Verificar producto", [field],
              (values) => ({ action: "scan", id: order.id, sku: line.sku, barcode: values.barcode }));
          }));
          card.append(row);
        }
        if (order.status === "CONFIRMADO") {
          const finish = action("Finalizar alistamiento", () => formAction("Finalizar " + order.number,
            "Descontar inventario y alistar", [text("p", "Se descontará el saldo físico de los lotes reservados.")],
            () => ({ action: "finish", id: order.id })), false);
          finish.disabled = !order.lines.every((line) => line.picked);
          card.append(finish);
        } else card.append(link("Descargar rótulo QR", "/api/logistica/rotulo?id=" + order.id));
        panel.append(card);
      }
      return;
    }

    if (kind === "routes") {
      const setup = document.createElement("div");
      setup.className = "logistics-setup";
      setup.append(action("Registrar vehículo", () => formAction("Vehículo de reparto", "Guardar vehículo", [
        input("Placa", "plate", "text", "Ejemplo: STR-456"), input("Capacidad de carga (kg)", "capacity", "number"),
      ], (values) => ({ ...values, action: "vehicle" }))),
      action("Peso por unidad", () => formAction("Peso de los productos", "Guardar peso", [
        select("Producto", "sku", data.products.map((item) => [item.sku, item.name + " · " + item.sku])),
        input("Peso por unidad de venta (kg)", "kg", "number", "Un bulto de 40 kg se registra como 40."),
      ], (values) => ({ ...values, action: "weight" }))),
      action("Dirección de entrega", () => formAction("Destino del cliente", "Guardar destino", [
        select("Cliente", "customer", data.customers.map((item) => [item.id, item.name + " · " + item.zone])),
        input("Dirección y referencia", "address", "text", "Vereda, finca, acceso o punto de encuentro."),
        input("Latitud", "lat", "number", "Ejemplo: 4.7110"), input("Longitud", "lng", "number", "Ejemplo: -74.0721"),
      ], (values) => ({ ...values, action: "destination" }))));
      panel.append(setup);
      const config = text("details", "", "logistics-card");
      config.append(text("summary", "Configuración de carga y destinos"));
      config.append(text("p", data.vehicles.map((row) => row.id + " · " + row.capacity + " kg").join(" | ") || "Registra el primer vehículo."));
      config.append(text("p", data.weights.map((row) => row.id + " · " + row.kg + " kg/unidad").join(" | ") || "Configura el peso de los productos del pedido."));
      config.append(text("p", data.destinations.map((row) => row.address).join(" | ") || "Registra las coordenadas de los clientes."));
      panel.append(config);
      const plan = action("Planificar ruta", () => {
        const orders = text("fieldset", "", "route-order-selector");
        orders.append(text("legend", "Pedidos alistados"));
        for (const order of data.orders) {
          const label = document.createElement("label");
          label.className = "check";
          const checkbox = document.createElement("input");
          checkbox.type = "checkbox";
          checkbox.name = "order";
          checkbox.value = order.id;
          label.append(checkbox, order.number + " · " + order.customer_name);
          orders.append(label);
        }
        const departure = input("Salida prevista", "departure", "datetime-local");
        departure.querySelector("input").value = new Date(Date.now() - new Date().getTimezoneOffset() * 60000 + 3600000).toISOString().slice(0, 16);
        formAction("Planificar distribución", "Crear ruta", [
          select("Vehículo", "vehicle", data.vehicles.filter((row) => row.active).map((row) => [row.id, row.plate + " · " + row.capacity + " kg"])),
          select("Conductor", "driver", data.drivers.map((row) => [row.id, row.name])),
          departure, input("Latitud de bodega", "lat", "number"), input("Longitud de bodega", "lng", "number"), orders,
        ], (values, form) => ({ ...values, action: "plan", orders: new FormData(form).getAll("order") }));
      }, false);
      plan.disabled = !data.orders.length || !data.drivers.length || !data.vehicles.length;
      panel.append(plan);
      if (plan.disabled) panel.append(text("p", "Necesitas pedidos alistados, un vehículo y una cuenta activa de rol Conductor."));
      for (const notice of data.alerts) panel.append(text("p", notice.order + " · " + notice.note, "logistics-warning"));
      for (const route of data.routes) {
        const card = text("article", "", "logistics-card");
        card.append(text("span", stateLabel(route.status), "logistics-state"), text("h2", route.number),
          text("p", route.vehicle + " · " + route.driver_name + " · " + route.kg + " kg"), routeMap(route));
        const stops = document.createElement("ol");
        for (const stop of route.stops) stops.append(text("li", stop.customer + " · " + stop.number + " · " + stop.destination.address));
        card.append(stops);
        if (route.manifest) card.append(link("Manifiesto PDF", "/api/logistica/manifiesto?id=" + route.id));
        if (route.status !== "PLANIFICADA") for (const stop of route.stops) {
          card.append(action("Evidencia · " + stop.number, () => viewProof(stop)));
        }
        panel.append(card);
      }
      for (const row of data.returns.filter((row) => row.status === "PENDIENTE_RECEPCION")) panel.append(text("p", "Retorno pendiente de bodega · " + row.order + " · " + row.note, "logistics-warning"));
      return;
    }

    if (kind === "dispatch") {
      if (!data.routes.length) panel.append(text("p", "No hay rutas planificadas para cargar."));
      for (const route of data.routes) {
        const card = text("article", "", "logistics-card");
        card.append(text("h2", route.number), text("p", route.vehicle + " · " + route.driver_name),
          text("p", route.loaded.length + " de " + route.orders.length + " pedidos cargados"));
        if (route.status === "PLANIFICADA") {
          const form = document.createElement("form");
          form.className = "route-scan";
          form.append(input("Rótulo del pedido", "label", "text", "Escanea el QR con tu lector o escribe el número PV-…"));
          const scan = text("button", "Verificar cargue");
          form.append(scan);
          form.onsubmit = handle(async (event) => {
            scan.disabled = true;
            try { await mutation({ action: "load", id: route.id, label: form.elements.label.value }); }
            catch (error) { alertTone(); throw error; }
            finally { scan.disabled = false; }
          });
          card.append(form);
          const launch = action("Emitir manifiesto y despachar", () => formAction("Despachar " + route.number,
            "Confirmar salida", [text("p", "Todos los pedidos cargados pasarán a En ruta.")],
            () => ({ action: "dispatch", id: route.id })), false);
          launch.disabled = route.loaded.length !== route.orders.length;
          card.append(launch);
        } else card.append(link("Abrir manifiesto PDF", "/api/logistica/manifiesto?id=" + route.id));
        panel.append(card);
      }
      for (const row of data.returns) {
        const block = text("article", "", "logistics-card");
        block.append(text("h2", row.order + " · Retorno"), text("p", row.note));
        if (row.status === "PENDIENTE_RECEPCION") {
          block.append(action("Recibir retorno en bodega", () => formAction("Recepción del retorno",
            "Registrar unidades devueltas", [input("Ubicación de retorno", "location", "text", "Registra únicamente mercancía verificada físicamente.")],
            (values) => ({...values, action:"return", id:row.id}))));
        } else block.append(text("p", "Retorno recibido en " + row.location));
        panel.append(block);
      }
      return;
    }

    const pending = (await stored("pending", "readonly", (store) => store.getAll())).filter((row) => row.userId === user.id);
    panel.append(text("p", navigator.onLine ? "Conexión disponible" : "Sin conexión", "logistics-state"),
      text("p", pending.length + " confirmaciones pendientes de sincronizar"),
      action("Sincronizar y actualizar", async () => { await synchronize(user.id, request); await render(); }));
    const queued = new Set(pending.map((row) => row.payload.id));
    if (!data.orders.length) panel.append(text("p", "Todavía no tienes entregas asignadas."));
    for (const route of data.routes) {
      panel.append(text("h2", route.number + " · " + route.vehicle));
      for (const stop of route.stops) {
        const order = data.orders.find((row) => row.id === stop.order);
        if (!order) continue;
        const card = text("article", "", "logistics-card delivery-card");
        card.append(text("span", queued.has(order.id) ? "Guardado en este dispositivo" : stateLabel(order.status), "logistics-state"),
          text("h2", stop.customer), text("p", stop.destination.address), text("p", order.number));
        if (order.status === "EN_RUTA" && !queued.has(order.id)) {
          card.append(action("Registrar entrega", () => deliveryForm(order, user, panel, request, handle, render), false));
        }
        panel.append(card);
      }
    }
  };
}

function fileImage(file) {
  return new Promise((resolve, reject) => {
    if (!file || !/^image\/(jpeg|png|webp)$/.test(file.type) || file.size > 15_000_000) {
      reject(new Error("Selecciona una foto JPG, PNG o WebP de hasta 15 MB."));
      return;
    }
    const url = URL.createObjectURL(file);
    const image = new Image();
    image.onload = () => {
      const canvas = document.createElement("canvas");
      const scale = Math.min(1, 1000 / Math.max(image.width, image.height));
      canvas.width = image.width * scale;
      canvas.height = image.height * scale;
      canvas.getContext("2d").drawImage(image, 0, 0, canvas.width, canvas.height);
      URL.revokeObjectURL(url);
      resolve(canvas.toDataURL("image/jpeg", .65));
    };
    image.onerror = () => { URL.revokeObjectURL(url); reject(new Error("No se pudo leer la foto.")); };
    image.src = url;
  });
}

function deliveryForm(order, user, panel, request, handle, refresh) {
  let signed = false;
  let coordinates;
  const signature = document.createElement("canvas");
  signature.width = 640;
  signature.height = 200;
  signature.className = "signature";
  signature.setAttribute("aria-label", "Área para dibujar la firma de quien recibe");
  const context = signature.getContext("2d");
  context.fillStyle = "#fff";
  context.fillRect(0, 0, 640, 200);
  context.strokeStyle = "#183624";
  context.lineWidth = 3;
  let drawing = false;
  const point = (event) => {
    const box = signature.getBoundingClientRect();
    return [(event.clientX - box.left) * 640 / box.width, (event.clientY - box.top) * 200 / box.height];
  };
  signature.onpointerdown = (event) => {
    event.preventDefault();
    signature.setPointerCapture(event.pointerId);
    drawing = true;
    context.beginPath();
    context.moveTo(...point(event));
  };
  signature.onpointermove = (event) => {
    if (drawing) { context.lineTo(...point(event)); context.stroke(); signed = true; }
  };
  signature.onpointerup = signature.onpointercancel = () => { drawing = false; };
  const photo = input("Foto de la entrega", "photo", "file");
  photo.querySelector("input").accept = "image/jpeg,image/png,image/webp";
  photo.querySelector("input").setAttribute("capture", "environment");
  const evidence = document.createElement("fieldset");
  evidence.append(text("legend", "Evidencia de recepción"), text("p", "Pide autorización a quien recibe para registrar su firma y foto."),
    text("label", "Firma de quien recibe"), signature);
  const clear = text("button", "Limpiar firma", "secondary");
  clear.type = "button";
  clear.onclick = () => { context.fillStyle = "#fff"; context.fillRect(0, 0, 640, 200); signed = false; };
  const geo = text("button", "Obtener ubicación", "secondary");
  geo.type = "button";
  const status = text("p", "Obtén la ubicación antes de confirmar.");
  geo.onclick = () => {
    if (!navigator.geolocation) { status.textContent = "El navegador no ofrece ubicación."; return; }
    navigator.geolocation.getCurrentPosition((position) => {
      coordinates = { lat: position.coords.latitude, lng: position.coords.longitude };
      status.textContent = "Ubicación registrada.";
    }, () => { status.textContent = "Activa el permiso de ubicación para registrar una entrega completada."; },
    { enableHighAccuracy: true, timeout: 15000, maximumAge: 60000 });
  };
  evidence.append(clear, photo, geo, status);
  const outcome = select("Resultado", "result", [["ENTREGADO", "Entregado"], ["NOVEDAD", "No entregado / novedad"]]);
  const note = input("Observación", "note", "text", "Ejemplo: cliente cerrado o nombre de quien recibe.");
  const requestId = crypto.randomUUID();
  const form = openDialog(panel, "Entrega · " + order.number, "Guardar confirmación", [outcome, evidence, note],
    async (values) => {
      const payload = { id: order.id, result: values.result, note: values.note, request_id: requestId,
        captured_at: new Date().toISOString() };
      if (values.result === "ENTREGADO") {
        if (!signed || !coordinates) throw new Error("Registra la firma y la ubicación antes de confirmar.");
        payload.signature = signature.toDataURL("image/png");
        payload.photo = await fileImage(form.elements.photo.files[0]);
        Object.assign(payload, coordinates);
      }
      // Persist first so a network interruption after acceptance is safely retried with the same identifier.
      await queueDelivery(user.id, payload);
      if (navigator.onLine) {
        try { await synchronize(user.id, request); }
        catch (error) { status.textContent = "Guardada en el dispositivo. " + error.message; }
      }
      await refresh();
    }, handle);
  outcome.querySelector("select").onchange = () => {
    const delivered = form.elements.result.value === "ENTREGADO";
    evidence.hidden = !delivered;
    form.elements.photo.required = delivered;
    form.elements.note.required = !delivered;
  };
  form.elements.note.required = false;
}

export function trackingView(user, request, handle, panel) {
  return async function render() {
    panel.replaceChildren(text("p", "MI FINCA · MIS PEDIDOS", "role-eyebrow"), text("h1", "Seguimiento de pedidos"));
    const container = document.createElement("div");
    panel.append(container);
    const data = await request("/api/comercio/pedidos");
    if (!container.isConnected) return;
    if (!data.portal) { container.append(text("p", "Pide a tu asesor que vincule tu cuenta con tu ficha de cliente.")); return; }
    if (!data.rows.length) container.append(text("p", "Todavía no tienes pedidos registrados."));
    for (const order of data.rows) {
      const card = text("article", "", "logistics-card");
      card.append(text("h2", order.number), text("span", stateLabel(order.status), "logistics-state"));
      const details = document.createElement("div");
      let finished = false;
      const button = text("button", "Actualizar seguimiento", "secondary");
      const update = handle(async () => {
        const status = await request("/api/logistica/tracking?id=" + order.id);
        if (!card.isConnected) return;
        card.querySelector(".logistics-state").textContent = stateLabel(status.status);
        finished = ["ENTREGADO", "NOVEDAD", "CANCELADO"].includes(status.status);
        const timeline = document.createElement("ol");
        timeline.className = "order-timeline";
        for (const event of status.timeline) timeline.append(text("li", event.label + " · " +
          new Date(event.at).toLocaleString("es-CO")));
        details.replaceChildren(timeline);
        if (status.eta) details.append(text("p", "Llegada estimada: " + new Date(status.eta).toLocaleTimeString("es-CO") +
          " · " + status.ahead + " entregas antes de la tuya."));
      });
      button.onclick = update;
      card.append(details, button);
      container.append(card);
      await update();
      const poll = async () => {
        if (!card.isConnected || finished) return;
        if (document.visibilityState === "visible" && navigator.onLine) await update();
        if (card.isConnected && !finished) setTimeout(poll, 20000);
      };
      setTimeout(poll, 20000);
    }
  };
}
