const CACHE = "villali-sprint3-shell-v1";
const SHELL = ["/entrar", "/app.js?v=15", "/style.css?v=9", "/logistics.js", "/logistics.css?v=1",
  "/driver-store.js", "/villali-logo.png", "/app-icon.svg", "/manifest.webmanifest"];
self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(SHELL)));
});
self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((key) =>
    key.startsWith("villali-sprint3-shell") && key !== CACHE).map((key) => caches.delete(key)))));
});
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin || event.request.method !== "GET" ||
      url.pathname.startsWith("/api/") || url.pathname === "/") return;
  if (!SHELL.some((path) => new URL(path, self.location.origin).pathname === url.pathname)) return;
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request).then((response) =>
    response || caches.match(url.pathname))));
});
