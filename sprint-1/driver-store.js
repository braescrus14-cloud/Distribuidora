function database() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open("villali-entregas", 1);
    request.onupgradeneeded = () => {
      request.result.createObjectStore("pending", { keyPath: "key" });
      request.result.createObjectStore("journeys", { keyPath: "userId" });
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(new Error("No se pudo abrir el almacenamiento del dispositivo."));
  });
}

export async function stored(store, mode, operation) {
  const db = await database();
  try {
    return await new Promise((resolve, reject) => {
      const transaction = db.transaction(store, mode);
      const request = operation(transaction.objectStore(store));
      transaction.oncomplete = () => resolve(request.result);
      transaction.onabort = () => reject(transaction.error || new Error("No se guardaron los datos en este dispositivo."));
      transaction.onerror = () => reject(transaction.error);
    });
  } finally { db.close(); }
}

export async function queueDelivery(userId, payload) {
  return stored("pending", "readwrite", (store) => store.put({
    key: userId + "-" + payload.request_id, userId, payload, created: Date.now(),
  }));
}

let syncing = false;
export async function synchronize(userId, request) {
  if (syncing || !navigator.onLine) return;
  syncing = true;
  try {
    const session = await request("/api/session");
    if (session.id !== userId || session.role !== "08") throw new Error("Inicia sesión con la cuenta que guardó las entregas.");
    const pending = await stored("pending", "readonly", (store) => store.getAll());
    for (const item of pending.filter((row) => row.userId === userId).sort((a, b) => a.created - b.created)) {
      await request("/api/logistica/deliveries", item.payload);
      await stored("pending", "readwrite", (store) => store.delete(item.key));
    }
  } finally { syncing = false; }
}
