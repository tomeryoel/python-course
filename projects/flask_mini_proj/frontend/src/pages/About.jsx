import { DISCLAIMER } from "../data/examples";

export default function About() {
  return (
    <>
      <h1 className="page-title">אודות הפרויקט</h1>
      <p className="page-sub">פרויקט גמר — PTSD Companion</p>

      <div className="glass-card">
        <h3>מטרה</h3>
        <p>
          PTSD Companion הוא עוזר דיגיטלי אישי לזיכרון טיפולי, עומס קוגניטיבי ומצבי
          מצוקה. הוא עוזר לזכור הנחיות מהפסיכולוג/פסיכיאטר, לבצע משימות יומיות, ולשאול
          שאלות מבוססות מסמכים בלבד.
        </p>
      </div>

      <div className="glass-card">
        <h3>ארכיטקטורה</h3>
        <pre
          style={{
            background: "rgba(0,0,0,0.25)",
            padding: "1rem",
            borderRadius: "10px",
            overflow: "auto",
            fontSize: "0.85rem",
            direction: "ltr",
            textAlign: "left",
          }}
        >
{`Documents → Bedrock Knowledge Base
         ↓
    Flask + boto3 (RAG + tasks API)
         ↓
    React UI + tasks.json
         ↓
    Docker → EC2 (public demo)`}
        </pre>
      </div>

      <div className="glass-card">
        <h3>שירותי AWS</h3>
        <ul style={{ paddingRight: "1.25rem" }}>
          <li>Amazon Bedrock Knowledge Base</li>
          <li>bedrock-agent-runtime (retrieve)</li>
          <li>bedrock-runtime (converse — Amazon Nova)</li>
          <li>S3 — אחסון מסמכי המקור</li>
          <li>EC2 — פריסה ציבורית לבדיקה</li>
        </ul>
      </div>

      <div className="glass-card">
        <h3>הצהרה רפואית</h3>
        <p>{DISCLAIMER}</p>
        <p style={{ marginTop: "0.5rem", color: "var(--gray)" }}>
          זהו דמו סטודנטיאלי עם מסמכים פיקטיביים — לא לשימוש קליני אמיתי.
        </p>
      </div>
    </>
  );
}
