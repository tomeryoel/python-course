import { DEMO_DOCUMENTS } from "../data/examples";

export default function Documents() {
  return (
    <>
      <h1 className="page-title">מסמכי המקור</h1>
      <p className="page-sub">
        שישה מסמכים קליניים מדומים בעברית — שמות ומספרי רישיון פיקטיביים.
        התוכן הגולמי לא מוצג כאן מטעמי פרטיות.
      </p>

      <div className="glass-card">
        <h3>סוגי מסמכים</h3>
        <p>
          <strong>DOCX</strong> — סיכומי פסיכולוגיה: פרוטוקולים, CBT, EMDR, קרקוע, עומס
          קוגניטיבי.
        </p>
        <p style={{ marginTop: "0.5rem" }}>
          <strong>PDF</strong> — סיכומי פסיכיאטריה: תרופות, שינה, SOS, שינויי מינון.
        </p>
        <p style={{ marginTop: "0.75rem", color: "var(--gray)" }}>
          המערכת תומכת בעתיד גם במסמכים באנגלית — התשובות ימשיכו בעברית כברירת מחדל.
        </p>
      </div>

      <div className="grid-2">
        {DEMO_DOCUMENTS.map((doc) => (
          <div key={doc.name} className="glass-card">
            <span className="chip">{doc.type}</span>
            <span className="chip">{doc.role}</span>
            <h3 style={{ marginTop: "0.5rem" }}>{doc.name}</h3>
            <p style={{ color: "var(--gray)", fontSize: "0.9rem" }}>{doc.note}</p>
          </div>
        ))}
      </div>

      <div className="glass-card">
        <h3>זרימת RAG</h3>
        <p>
          המסמכים הועלו ל-Amazon Bedrock Knowledge Base. בכל שאלה, המערכת שולפת קטעים
          רלוונטיים ומייצרת תשובה מבוססת מסמכים בלבד.
        </p>
      </div>
    </>
  );
}
