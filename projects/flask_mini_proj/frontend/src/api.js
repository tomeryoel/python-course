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
