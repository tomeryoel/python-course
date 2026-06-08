const API = "";

export async function healthCheck() {
  const res = await fetch(`${API}/health`);
  return res.json();
}

export async function sendChat(message, conversationId = null) {
  const body = { message };
  if (conversationId) body.conversation_id = conversationId;

  const res = await fetch(`${API}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || data.message || "שגיאה בשליחה");
  return data;
}

export async function clearChat(conversationId) {
  await fetch(`${API}/api/clear`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ conversation_id: conversationId }),
  });
}

export async function fetchConversations() {
  const res = await fetch(`${API}/api/conversations`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "שגיאה בטעינת שיחות");
  return data.conversations || [];
}

export async function createConversation(title = "שיחה חדשה") {
  const res = await fetch(`${API}/api/conversations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "שגיאה");
  return data.conversation;
}

export async function fetchConversation(id) {
  const res = await fetch(`${API}/api/conversations/${id}`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "שיחה לא נמצאה");
  return data.conversation;
}

export async function fetchKnowledgeBaseStatus() {
  const res = await fetch(`${API}/api/knowledge-base/status`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "שגיאה");
  return data;
}

export async function fetchDocuments() {
  const res = await fetch(`${API}/api/documents`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "שגיאה בטעינת מסמכים");
  return data;
}

export async function uploadDocument(file, onProgress) {
  const formData = new FormData();
  formData.append("file", file);
  onProgress?.(30);
  const res = await fetch(`${API}/api/documents/upload`, {
    method: "POST",
    body: formData,
    credentials: "include",
  });
  onProgress?.(90);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "שגיאה בהעלאה");
  onProgress?.(100);
  return data;
}

export async function fetchStressCheckIn(payload = {}) {
  const res = await fetch(`${API}/api/tools/stress-check-in`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "שגיאה");
  return data.classifier;
}

export async function fetchWeeklySnapshot(language = "he") {
  const res = await fetch(`${API}/api/tools/weekly-snapshot`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ language }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "שגיאה");
  return data.snapshot;
}

export async function triggerEmergencyCall(confirmed, extra = {}) {
  const res = await fetch(`${API}/api/tools/emergency-call`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ confirmed, ...extra }),
  });
  const data = await res.json();
  return data;
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
