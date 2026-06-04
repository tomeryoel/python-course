import { useCallback, useEffect, useState } from "react";
import { fetchUploadedDocuments } from "../api";
import DocumentUploadZone from "../components/documents/DocumentUploadZone";
import UploadedDocumentsList from "../components/documents/UploadedDocumentsList";
import PageHeader from "../components/layout/PageHeader";
import { Card, CardHeader } from "../components/ui/Card";
import Badge from "../components/ui/Badge";
import { DEMO_DOCUMENTS } from "../data/examples";

export default function Documents() {
  const [uploaded, setUploaded] = useState([]);

  const refresh = useCallback(() => {
    fetchUploadedDocuments().then(setUploaded);
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <>
      <PageHeader
        title="מסמכים ומקורות"
        subtitle="בסיס הידע הקליני שלך מתעדכן לאחר כל ביקור — מסמכי הדמו + העלאות חדשות."
      />

      <DocumentUploadZone onUploaded={refresh} />

      <Card className="mt-6">
        <CardHeader
          title="מסמכים שהועלו"
          subtitle="היסטוריית העלאות וסטטוס סנכרון"
        />
        <UploadedDocumentsList documents={uploaded} />
      </Card>

      <Card className="mt-6">
        <CardHeader
          title="מאגר הדמו (Knowledge Base)"
          subtitle="שישה מסמכים פיקטיביים — תוכן גולמי לא מוצג מטעמי פרטיות"
        />
        <div className="mb-4 rounded-xl border border-accent/20 bg-accent/5 px-4 py-3 text-sm text-slate-300">
          מסמכים חדשים שתעלה ישולבו יחד עם המסמכים הקיימים — המערכת תשתמש בכל
          ההקשר הרפואי הזמין לתשובות והנחיות עתידיות.
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          {DEMO_DOCUMENTS.map((doc) => (
            <article
              key={doc.name}
              className="rounded-xl border border-glass-border bg-black/20 p-4 transition hover:border-accent/30"
            >
              <div className="mb-2 flex flex-wrap gap-2">
                <Badge>{doc.type}</Badge>
                <Badge category="routine">{doc.role}</Badge>
              </div>
              <h4 className="font-medium text-white">{doc.name}</h4>
              <p className="mt-1 text-sm text-slate-400">{doc.note}</p>
            </article>
          ))}
        </div>
      </Card>

      <Card className="mt-6">
        <CardHeader title="סוגי מסמכים" />
        <div className="grid gap-4 text-sm text-slate-300 md:grid-cols-2">
          <p>
            <strong className="text-accent-light">DOCX</strong> — סיכומי פסיכולוגיה:
            CBT, EMDR, קרקוע, עומס קוגניטיבי.
          </p>
          <p>
            <strong className="text-accent-light">PDF</strong> — סיכומי פסיכיאטריה:
            תרופות, שינה, SOS.
          </p>
        </div>
      </Card>
    </>
  );
}
