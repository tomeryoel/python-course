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
  tick(20);

  const res = await fetch(`${API}/api/documents/upload`, {
    method: "POST",
    body: formData,
    credentials: "include",
  });

  tick(80);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "שגיאה בהעלאה");

  tick(100);
  return {
    document: data.document,
    indexingStatus: data.indexing_status,
    index: data.index,
    message: data.message,
  };
}

export async function fetchDocuments() {
  const res = await fetch(`${API}/api/documents`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "שגיאה בטעינת מסמכים");
  return { documents: data.documents || [], index: data.index || null };
}

export async function fetchIndexStatus() {
  const res = await fetch(`${API}/api/index/status`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "שגיאה בטעינת סטטוס האינדקס");
  return data.index;
}

export async function rebuildIndex() {
  const res = await fetch(`${API}/api/index/rebuild`, { method: "POST" });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "בניית האינדקס נכשלה");
  return data;
}
