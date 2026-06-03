import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { fetchTasks } from "../api";
import { CATEGORY_LABELS } from "../data/examples";

export default function Home() {
  const [tasks, setTasks] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchTasks().then(setTasks).catch(() => setTasks([]));
  }, []);

  const open = tasks.filter((t) => t.status === "open");
  const anchors = open.filter((t) => t.id === "task_008" || t.category === "cognitive_load").slice(0, 3);
  const anchorDisplay = open.slice(0, 3);
  const meds = open.filter((t) => t.category === "medication");
  const sleep = open.filter((t) => t.category === "sleep");

  const today = new Date().toLocaleDateString("he-IL", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });

  return (
    <>
      <h1 className="page-title">שלום, ברוך שובך</h1>
      <p className="page-sub">{today} — היום נתמקד רק במה שחשוב באמת.</p>

      <div className="grid-2">
        <div className="glass-card">
          <h3>שלושת העוגנים להיום</h3>
          <p style={{ color: "var(--gray)", fontSize: "0.9rem", marginBottom: "0.75rem" }}>
            מקסימום 3 משימות עיקריות — השאר מוקפא.
          </p>
          <ul style={{ listStyle: "none" }}>
            {anchorDisplay.map((t) => (
              <li key={t.id} style={{ marginBottom: "0.5rem" }}>
                • {t.title}
              </li>
            ))}
          </ul>
          {anchors.length > 0 && (
            <span className="chip">{CATEGORY_LABELS.cognitive_load}</span>
          )}
        </div>

        <div className="glass-card">
          <h3>תזכורות</h3>
          {meds.map((t) => (
            <p key={t.id}>
              💊 {t.title} — {t.time || "לפי מסמך"}
            </p>
          ))}
          {sleep.map((t) => (
            <p key={t.id}>🌙 {t.title}</p>
          ))}
        </div>
      </div>

      <div className="glass-card" style={{ textAlign: "center" }}>
        <p style={{ marginBottom: "1rem" }}>מרגיש לחץ או פלאשבק? התחל מקרקוע קצר.</p>
        <button
          className="btn btn-grounding"
          onClick={() =>
            navigate("/chat", {
              state: {
                question:
                  "אני בסטרס עכשיו, מה לעשות לפי ההנחיות שלי?",
              },
            })
          }
        >
          התחל קרקוע 5-4-3-2-1
        </button>
        <p style={{ marginTop: "1rem" }}>
          <Link to="/chat">מעבר לשיחה מלאה →</Link>
        </p>
      </div>
    </>
  );
}
