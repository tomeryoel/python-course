const API = "";

export async function healthCheck() {
  const res = await fetch(`${API}/health`);
  return res.json();
}

export async function sendChat(question) {
  const res = await fetch(`${API}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ question }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "שגיאה בשליחה");
  return data;
}

export async function clearChat() {
  await fetch(`${API}/api/clear`, { method: "POST", credentials: "include" });
}

export async function fetchTasks() {
  const res = await fetch(`${API}/api/tasks`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "שגיאה בטעינת משימות");
  return data.tasks || [];
}

export async function createTask(task) {
  const res = await fetch(`${API}/api/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(task),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "שגיאה");
  return data.task;
}

export async function patchTask(id, updates) {
  const res = await fetch(`${API}/api/tasks/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "שגיאה");
  return data.task;
}

export async function removeTask(id) {
  const res = await fetch(`${API}/api/tasks/${id}`, { method: "DELETE" });
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.error || "שגיאה");
  }
}

/**
 * Upload clinical document — tries backend; falls back to local queue for UI demo.
 * Prepared for: POST /api/documents/upload
 */
export async function uploadDocument(file, onProgress) {
  const formData = new FormData();
  formData.append("file", file);

  const tick = (n) => onProgress?.(n);

  try {
    tick(20);
    const res = await fetch(`${API}/api/documents/upload`, {
      method: "POST",
      body: formData,
      credentials: "include",
    });
    tick(80);

    if (res.ok) {
      const data = await res.json();
      tick(100);
      const doc = {
        id: data.id || `doc_${Date.now()}`,
        name: file.name,
        type: file.name.split(".").pop()?.toUpperCase(),
        uploadedAt: new Date().toISOString(),
        status: "synced",
      };
      return { synced: true, document: doc };
    }
  } catch (e) {
    console.warn("[upload] backend unavailable, using local queue", e);
  }

  // Local fallback — architecture ready for future sync
  tick(40);
  await delay(400);
  tick(70);
  await delay(300);

  const { addUploadedDocument, fileTypeBadge } = await import("./lib/documentsStore");
  const doc = {
    id: `local_${Date.now()}`,
    name: file.name,
    type: fileTypeBadge(file),
    uploadedAt: new Date().toISOString(),
    status: "pending_sync",
    size: file.size,
  };
  addUploadedDocument(doc);
  tick(100);
  return { synced: false, document: doc };
}

function delay(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

export async function fetchUploadedDocuments() {
  try {
    const res = await fetch(`${API}/api/documents`);
    if (res.ok) {
      const data = await res.json();
      return data.documents || [];
    }
  } catch {
    /* use local */
  }
  const { loadUploadedDocuments } = await import("./lib/documentsStore");
  return loadUploadedDocuments();
}

export async function extractTasks(documentText, sourceName) {
  const res = await fetch(`${API}/api/extract-tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      document_text: documentText,
      source_name: sourceName,
    }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "שגיאה בחילוץ");
  return data;
}
