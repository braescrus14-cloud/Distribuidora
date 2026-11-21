if (new URLSearchParams(location.hash.slice(1)).has("invitar")) location.replace("/entrar" + location.hash);
const reduced = matchMedia("(prefers-reduced-motion: reduce)");
// Reveal before entry without translating containers or changing layout height.
const reveals = [...document.querySelectorAll(".reveal")];
let observer;
if (!reduced.matches && "IntersectionObserver" in window) {
 observer = new IntersectionObserver((entries) => {
  for (const entry of entries) if (entry.isIntersecting) {
   entry.target.classList.remove("reveal-pending");
   entry.target.classList.add("reveal-enter");
   observer.unobserve(entry.target);
  }
 }, {rootMargin:"0px 0px 80px 0px", threshold:.01});
 for (const node of reveals) {
  if (node.getBoundingClientRect().top >= innerHeight) { node.classList.add("reveal-pending"); observer.observe(node); }
  node.addEventListener("animationend", () => node.classList.remove("reveal-enter"));
 }
}
reduced.addEventListener("change", () => {
 if (reduced.matches) { observer?.disconnect(); for (const node of reveals) node.classList.remove("reveal-pending", "reveal-enter"); }
});
const states = [
  ["Solicitud enviada", "El asesor recibe tus referencias y cantidades para revisar el pedido."],
  ["Pedido confirmado", "El asesor valida las condiciones y bodega prepara los lotes reservados."],
  ["Tu pedido está en ruta", "Consulta la llegada estimada y las entregas pendientes antes de la tuya."],
  ["Entrega registrada", "La recepción queda respaldada con firma, fotografía y fecha de entrega."],
];
let step = 0, timer;
const play = document.getElementById("play-demo");
function stop() { clearInterval(timer); timer = null; play.textContent = "Reproducir"; play.setAttribute("aria-pressed", "false"); }
function showStep(next) {
  step = next;
  document.getElementById("demo-state").textContent = states[step][0];
  document.getElementById("demo-description").textContent = states[step][1];
  document.querySelector(".demo-step-label").textContent = "PASO " + (step + 1) + " DE 4";
  document.querySelector(".demo-evidence").hidden = step !== 3;
  for (const button of document.querySelectorAll("[data-step]")) {
    const index = Number(button.dataset.step);
    button.setAttribute("aria-pressed", String(index === step));
    button.classList.toggle("done", index < step);
  }
  const stage = document.querySelector(".demo-stage");
  stage.classList.remove("changing");
  requestAnimationFrame(() => stage.classList.add("changing"));
}
for (const button of document.querySelectorAll("[data-step]")) button.onclick = () => { stop(); showStep(Number(button.dataset.step)); };
play.onclick = () => {
  if (timer) { stop(); return; }
  showStep((step + 1) % 4);
  if (reduced.matches) return;
  play.textContent = "Pausar";
  play.setAttribute("aria-pressed", "true");
  timer = setInterval(() => { if (document.visibilityState === "visible") showStep((step + 1) % 4); }, 4000);
};
reduced.addEventListener("change", () => { if (reduced.matches) stop(); });
document.addEventListener("visibilitychange", () => { if (document.hidden) stop(); });
const policy = document.getElementById("policy-dialog");
const policies = {
 privacy: ["Cómo usamos tus datos", "Al enviar la solicitud, autorizas a Distribuidora Villali a guardar tu nombre, correo, teléfono, finca e interés comercial para atenderla y ayudarte con el acceso al portal. El formulario no crea una cuenta ni una compra. La solicitud se conserva en el sistema de Villali y solo es consultable por el administrador autorizado. No publicamos tus datos en la página. Para consultar, corregir o solicitar la eliminación de una solicitud, comunícate por el WhatsApp de contacto."],
 terms: ["Términos de uso", "Esta página presenta las líneas de nutrición animal de Villali y permite solicitar una cuenta. La solicitud está sujeta a revisión del equipo. Las referencias y presentaciones se muestran según el catálogo de trabajo; confirma existencias, empaque, precio y condiciones con tu asesor antes de comprar. La demostración de seguimiento es un ejemplo interactivo, no un pedido real. Las horas de llegada del portal son estimaciones y no navegación en tiempo real. El acceso al portal es personal y depende del rol asignado."],
};
for (const button of document.querySelectorAll("[data-policy]")) button.onclick = () => {
  const [title,copy] = policies[button.dataset.policy];
  document.getElementById("policy-title").textContent = title;
  const paragraph = document.createElement("p"); paragraph.textContent = copy;
  document.getElementById("policy-text").replaceChildren(paragraph);
  policy.showModal();
};
document.getElementById("close-policy").onclick = () => policy.close();
for (const link of document.querySelectorAll("[data-interest]")) link.addEventListener("click", () => {
 document.querySelector("#request-form select").value = link.dataset.interest;
});
fetch("/api/public/contact").then((response) => response.ok ? response.json() : Promise.reject()).then((contact) => {
 const digits = (contact.phone || "").replace(/[^0-9]/g, "");
 for (const link of document.querySelectorAll("[data-whatsapp]")) {
  link.hidden = !digits; if (digits) link.href = "https://wa.me/" + digits + "?text=" + encodeURIComponent("Hola, quiero solicitar una cuenta en Villali");
 }
 for (const link of document.querySelectorAll("[data-phone]")) {
  link.hidden = !digits; if (digits) { link.href = "tel:+" + digits; link.textContent = digits.startsWith("57") && digits.length === 12 ? "+57 " + digits.slice(2,5) + " " + digits.slice(5,8) + " " + digits.slice(8) : contact.phone; }
 }
 const fields = [["[data-company]",contact.legal_name], ["[data-nit]", contact.nit ? "NIT " + contact.nit : ""], ["[data-city]",contact.city], ["[data-address]", contact.address], ["[data-hours]", contact.hours], ["[data-response-time]",contact.response_time]];
 for (const [selector,value] of fields) if (value) for (const node of document.querySelectorAll(selector)) { node.textContent = value; node.hidden = false; }
 if (contact.email && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(contact.email)) for (const link of document.querySelectorAll("[data-email]")) {
  link.href = "mailto:" + contact.email; link.textContent = contact.email; link.hidden = false;
 }
 for (const node of document.querySelectorAll("[data-stat]")) if (contact[node.dataset.stat]) node.textContent = contact[node.dataset.stat];
 for (const node of document.querySelectorAll("[data-social]")) {
  const value = contact[node.dataset.social];
  if (!value || !value.startsWith("https://")) continue;
  const link = document.createElement("a"); link.href = value; link.target="_blank"; link.rel="noopener";
  link.textContent = node.dataset.social === "facebook_url" ? "Facebook" : "Instagram"; node.replaceWith(link);
 }
 for (const node of document.querySelectorAll("[data-testimonial]")) {
  const prefix = "testimonial_" + node.dataset.testimonial + "_";
  if (contact[prefix + "approved"] !== "yes" || !["quote","name","farm","municipality"].every(key => contact[prefix+key])) continue;
  for (const key of ["quote","name","farm","municipality"]) node.querySelector("[data-testimonial-"+key+"]").textContent=contact[prefix+key];
  node.querySelector(".testimonial-label").textContent="EXPERIENCIA AUTORIZADA DEL PRODUCTOR";
 }
 if (contact.email) document.querySelector("[data-email-pending]").hidden=true;
}).catch(() => {});
const form = document.getElementById("request-form"), send = document.getElementById("send-request"), status = document.getElementById("request-status");
let requestId = crypto.randomUUID();
send.disabled = false;
form.onsubmit = async (event) => {
 event.preventDefault(); if (send.disabled) return;
 send.disabled = true; const caption = send.textContent; send.textContent = "Enviando solicitud…"; status.hidden = true;
 try {
  const data = Object.fromEntries(new FormData(form)); data.consent = form.elements.consent.checked; data.request_id = requestId;
  const response = await fetch("/api/public/account-requests", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(data)});
  const result = await response.json(); if (!response.ok) throw new Error(result.error);
  status.textContent = result.message; form.reset(); requestId = crypto.randomUUID();
 } catch (error) { status.textContent = error.message || "No pudimos enviar la solicitud. Inténtalo otra vez o comunícate por WhatsApp."; }
 finally { send.disabled = false; send.textContent = caption; status.hidden = false; }
};

// Each reference keeps its own source; unresolved data remain explicitly marked.
const sheetDialog=document.getElementById("product-dialog");
let productSheets;
const sheetsReady=fetch("/public-products.json").then(response=>{if(!response.ok)throw new Error();return response.json();}).then(rows=>{productSheets=rows;}).catch(()=>{});
for(const link of document.querySelectorAll("[data-product]")) link.addEventListener("click",event=>{
 const product=productSheets?.[link.dataset.product];
 if(!product)return; // The official link remains usable before data load or without JavaScript.
 event.preventDefault();
 document.getElementById("product-title").textContent=product.name;
 const content=document.getElementById("product-content"),description=document.createElement("dl");
 for(const [label,value]of [["Etapa y especie",product.stage],["Presentación",product.presentation],["Modo de uso",product.use]]) {
  const dt=document.createElement("dt"),dd=document.createElement("dd");dt.textContent=label;dd.textContent=value;description.append(dt,dd);
 }
 content.replaceChildren(description);
 const heading=document.createElement("h3");heading.textContent="Composición garantizada";content.append(heading);
 if(product.composition.length){const table=document.createElement("table"),head=table.createTHead().insertRow();for(const value of ["Componente","Garantía"]){const th=document.createElement("th");th.scope="col";th.textContent=value;head.append(th);}const body=table.createTBody();for(const values of product.composition){const row=body.insertRow();for(const value of values){const td=row.insertCell();td.textContent=value;}}content.append(table);}
 if(product.note){const note=document.createElement("p");note.textContent=product.note;content.append(note);}
 if(product.availability){const note=document.createElement("p");note.textContent=product.availability;content.append(note);}
 const source=document.createElement("a");source.href=product.source;source.target="_blank";source.rel="noopener";source.textContent="Consultar ficha original de Italcol";
 const stamp=document.createElement("p");stamp.textContent="Fuente revisada el 21 de noviembre de 2026. Sigue el rótulo del fabricante y confirma la pauta con tu asesor.";
 content.append(stamp,source);sheetDialog.showModal();
});
document.getElementById("close-product").onclick=()=>sheetDialog.close();
