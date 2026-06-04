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

export async function uploadDocument(file, onProgress) {
  const formData = new FormData();
  formData.append("file", file);

  const tick = (n) => onProgress?.(n);
  tick(15);

  const res = await fetch(`${API}/api/documents/upload`, {
    method: "POST",
    body: formData,
    credentials: "include",
  });

  tick(85);
  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.error || "שגיאה בהעלאה");
  }

  tick(100);
  const doc = data.document;
  return {
    synced: doc?.status === "synced",
    document: {
      id: doc.id,
      name: doc.name,
      type: doc.type,
      uploadedAt: doc.uploaded_at,
      status: doc.status === "pending_ingestion" ? "pending_sync" : doc.status,
      size: doc.size_bytes,
    },
  };
}

export async function fetchUploadedDocuments() {
  const res = await fetch(`${API}/api/documents`);
  if (res.ok) {
    const data = await res.json();
    return (data.documents || []).map((d) => ({
      id: d.id,
      name: d.name,
      type: d.type,
      uploadedAt: d.uploaded_at,
      status: d.status === "pending_ingestion" ? "pending_sync" : d.status,
      size: d.size_bytes,
    }));
  }
  const { loadUploadedDocuments } = await import("./lib/documentsStore");
  return loadUploadedDocuments();
}
