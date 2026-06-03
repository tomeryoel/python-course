import { useEffect, useState } from "react";
import {
  createTask,
  extractTasks,
  fetchTasks,
  patchTask,
  removeTask,
} from "../api";
import { CATEGORY_LABELS } from "../data/examples";

const emptyForm = {
  title: "",
  description: "",
  category: "routine",
  time: "",
  source: "הוספה ידנית",
};

export default function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState("");
  const [form, setForm] = useState(emptyForm);
  const [extractText, setExtractText] = useState("");
  const [extractSource, setExtractSource] = useState("סיכום חדש");
  const [loading, setLoading] = useState(false);

  const load = () =>
    fetchTasks()
      .then(setTasks)
      .catch((e) => setError(e.message));

  useEffect(() => {
    load();
  }, []);

  const open = tasks.filter((t) => t.status === "open");
  const done = tasks.filter((t) => t.status === "done");
  const progress = tasks.length
    ? Math.round((done.length / tasks.length) * 100)
    : 0;

  async function toggle(task) {
    const status = task.status === "done" ? "open" : "done";
    await patchTask(task.id, { status });
    load();
  }

  async function handleAdd(e) {
    e.preventDefault();
    try {
      await createTask(form);
      setForm(emptyForm);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(id) {
    if (!confirm("למחוק משימה?")) return;
    await removeTask(id);
    load();
  }

  async function handleExtract(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await extractTasks(extractText, extractSource);
      setExtractText("");
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const grouped = {};
  open.forEach((t) => {
    const c = t.category || "routine";
    if (!grouped[c]) grouped[c] = [];
    grouped[c].push(t);
  });

  return (
    <>
      <h1 className="page-title">לוח משימות</h1>
      <p className="page-sub">משימות תפקותיות מהמסמכים — tasks.json</p>

      <div className="glass-card">
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span>התקדמות</span>
          <span>{done.length}/{tasks.length}</span>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
      </div>

      {error && <div className="error-box">{error}</div>}

      {Object.entries(grouped).map(([cat, list]) => (
        <div key={cat} className="glass-card">
          <h3>{CATEGORY_LABELS[cat] || cat}</h3>
          {list.map((t) => (
            <div key={t.id} className={`task-item ${t.status === "done" ? "done" : ""}`}>
              <input
                type="checkbox"
                checked={t.status === "done"}
                onChange={() => toggle(t)}
              />
              <div style={{ flex: 1 }}>
                <strong>{t.title}</strong>
                <p style={{ fontSize: "0.9rem", color: "var(--gray)" }}>{t.description}</p>
                {t.time && <span className="chip">🕐 {t.time}</span>}
                {t.safety_note && (
                  <p style={{ fontSize: "0.8rem", color: "var(--warning)", marginTop: "0.35rem" }}>
                    {t.safety_note}
                  </p>
                )}
              </div>
              <button className="btn btn-ghost" onClick={() => handleDelete(t.id)} type="button">
                מחק
              </button>
            </div>
          ))}
        </div>
      ))}

      <div className="grid-2">
        <div className="glass-card">
          <h3>הוסף משימה</h3>
          <form onSubmit={handleAdd}>
            <div className="form-row">
              <label>כותרת</label>
              <input
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                required
              />
            </div>
            <div className="form-row">
              <label>תיאור</label>
              <textarea
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
              />
            </div>
            <div className="form-row">
              <label>קטגוריה</label>
              <select
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
              >
                {Object.entries(CATEGORY_LABELS).map(([k, v]) => (
                  <option key={k} value={k}>
                    {v}
                  </option>
                ))}
              </select>
            </div>
            <button className="btn btn-primary" type="submit">
              הוסף
            </button>
          </form>
        </div>

        <div className="glass-card">
          <h3>חילוץ משימות מסיכום</h3>
          <form onSubmit={handleExtract}>
            <div className="form-row">
              <label>שם מקור</label>
              <input
                value={extractSource}
                onChange={(e) => setExtractSource(e.target.value)}
              />
            </div>
            <div className="form-row">
              <label>הדבק טקסט סיכום</label>
              <textarea
                rows={5}
                value={extractText}
                onChange={(e) => setExtractText(e.target.value)}
                required
              />
            </div>
            <button className="btn btn-primary" type="submit" disabled={loading}>
              {loading ? "מחלץ…" : "חלץ משימות (Bedrock)"}
            </button>
          </form>
        </div>
      </div>
    </>
  );
}
