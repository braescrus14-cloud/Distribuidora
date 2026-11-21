if (new URLSearchParams(location.hash.slice(1)).has("invitar")) location.replace("/entrar" + location.hash);
const reduced = matchMedia("(prefers-reduced-motion: reduce)");
const observer = new IntersectionObserver((entries) => {
  for (const entry of entries) if (entry.isIntersecting) { entry.target.classList.add("is-visible"); observer.unobserve(entry.target); }
}, { threshold: .12 });
for (const node of document.querySelectorAll(".reveal")) observer.observe(node);
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
  link.hidden = !digits; if (digits) link.href = "https://wa.me/" + digits;
 }
 for (const link of document.querySelectorAll("[data-phone]")) {
  link.hidden = !digits; if (digits) { link.href = "tel:+" + digits; link.textContent = digits.startsWith("57") && digits.length === 12 ? "+57 " + digits.slice(2,5) + " " + digits.slice(5,8) + " " + digits.slice(8) : contact.phone; }
 }
 const fields = [["[data-company]",contact.legal_name], ["[data-nit]", contact.nit ? "NIT " + contact.nit : ""], ["[data-address]", contact.address], ["[data-hours]", contact.hours]];
 for (const [selector,value] of fields) if (value) for (const node of document.querySelectorAll(selector)) { node.textContent = value; node.hidden = false; }
 if (contact.email && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(contact.email)) for (const link of document.querySelectorAll("[data-email]")) {
  link.href = "mailto:" + contact.email; link.textContent = contact.email; link.hidden = false;
 }
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
