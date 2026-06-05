import { useCallback, useEffect, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Database,
  FileText,
  RefreshCw,
  XCircle,
} from "lucide-react";
import { fetchDocuments, rebuildIndex } from "../api";
import DocumentUploadZone from "../components/documents/DocumentUploadZone";
import PageHeader from "../components/layout/PageHeader";
import { Card, CardHeader } from "../components/ui/Card";
import Badge from "../components/ui/Badge";
import Button from "../components/ui/Button";
import EmptyState from "../components/ui/EmptyState";
import ErrorAlert from "../components/ui/ErrorAlert";

function formatBytes(n) {
  if (!n) return "0 KB";
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(0)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString("he-IL", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return iso;
  }
}

function Stat({ label, value, accent }) {
  return (
    <div className="rounded-xl border border-white/8 bg-white/[0.03] px-4 py-3">
      <p className="text-2xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className={`mt-1 text-lg font-semibold ${accent || "text-white"}`}>{value}</p>
    </div>
  );
}

export default function Documents() {
  const [documents, setDocuments] = useState([]);
  const [index, setIndex] = useState(null);
  const [loading, setLoading] = useState(true);
  const [rebuilding, setRebuilding] = useState(false);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    setError("");
    try {
      const { documents: docs, index: idx } = await fetchDocuments();
      setDocuments(docs);
      setIndex(idx);
    } catch (e) {
      setError(e?.message || "שגיאה בטעינת המסמכים");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function handleRebuild() {
    setRebuilding(true);
    setError("");
    try {
      await rebuildIndex();
      await refresh();
    } catch (e) {
      setError(e?.message || "בניית האינדקס נכשלה");
    } finally {
      setRebuilding(false);
    }
  }

  const rebuildNeeded = index?.rebuild_needed;

  return (
    <>
      <PageHeader
        title="מסמכים ואינדקס"
        subtitle="הנתונים כאן משקפים את המצב האמיתי של תיקיית data/ ושל אינדקס ה-FAISS המקומי."
      />

      {error && <ErrorAlert message={error} className="mb-5" />}

      {/* --- Real index status --- */}
      <Card premium>
        <CardHeader
          title="סטטוס אינדקס FAISS"
          subtitle="אחזור מקומי — ללא OpenSearch וללא Knowledge Base בזמן ריצה"
          action={
            <Button
              variant="secondary"
              size="sm"
              onClick={handleRebuild}
              disabled={rebuilding}
            >
              <RefreshCw className={`h-4 w-4 ${rebuilding ? "animate-spin" : ""}`} />
              {rebuilding ? "בונה…" : "בנה אינדקס מחדש"}
            </Button>
          }
        />

        {loading ? (
          <p className="text-sm text-slate-400">טוען סטטוס…</p>
        ) : (
          <>
            <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-6">
              <Stat
                label="אינדקס קיים"
                value={index?.index_exists ? "כן" : "לא"}
                accent={index?.index_exists ? "text-teal-300" : "text-red-300"}
              />
              <Stat label="מסמכים" value={index?.document_count ?? 0} />
              <Stat label="קטעים (chunks)" value={index?.chunk_count ?? 0} />
              <Stat label="מימד וקטור" value={index?.dimension ?? 0} />
              <Stat label="Backend" value={index?.embedding_backend || "—"} />
              <Stat
                label="בנייה אחרונה"
                value={formatDate(index?.last_built_at)}
                accent="text-slate-200 text-sm"
              />
            </div>

            <div className="mt-4 flex items-center gap-2 text-sm">
              {rebuildNeeded ? (
                <span className="inline-flex items-center gap-2 rounded-lg border border-amber-400/30 bg-amber-500/10 px-3 py-2 text-amber-200">
                  <AlertTriangle className="h-4 w-4" />
                  נדרשת בנייה מחדש — הנתונים השתנו מאז האינדקס האחרון.
                </span>
              ) : (
                <span className="inline-flex items-center gap-2 rounded-lg border border-teal-400/30 bg-teal-500/10 px-3 py-2 text-teal-200">
                  <CheckCircle2 className="h-4 w-4" />
                  האינדקס מעודכן ומוכן לשימוש.
                </span>
              )}
            </div>

            {index?.errors?.length > 0 && (
              <div className="mt-4 rounded-xl border border-red-400/30 bg-red-500/10 p-4">
                <p className="mb-2 text-sm font-medium text-red-200">
                  קבצים שלא נטענו:
                </p>
                <ul className="space-y-1 text-xs text-red-200/90">
                  {index.errors.map((e, i) => (
                    <li key={i}>
                      {e.file}: {e.error}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}
      </Card>

      {/* --- Upload --- */}
      <div className="mt-6">
        <DocumentUploadZone onUploaded={refresh} />
      </div>

      {/* --- Real files in data/ --- */}
      <Card className="mt-6">
        <CardHeader
          title="קבצים בתיקיית data/"
          subtitle="רשימה אמיתית — סוג, גודל, סטטוס אינדוקס ומספר קטעים"
        />
        {loading ? (
          <p className="text-sm text-slate-400">טוען קבצים…</p>
        ) : documents.length === 0 ? (
          <EmptyState
            icon={FileText}
            title="אין מסמכים בתיקיית data/"
            description="העלה קובץ PDF/DOCX/TXT, או הוסף קבצים לתיקיית data/ ובצע בנייה מחדש."
          />
        ) : (
          <ul className="space-y-3">
            {documents.map((doc) => (
              <li
                key={doc.stored_name}
                className="flex items-center gap-4 rounded-xl border border-white/8 bg-black/20 p-4 transition hover:border-accent/30"
              >
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-accent/10 text-accent-light">
                  <FileText className="h-5 w-5" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium text-white">{doc.name}</p>
                  <p className="mt-0.5 text-xs text-slate-500">
                    {formatBytes(doc.size_bytes)} · {formatDate(doc.modified)}
                    {doc.uploaded && " · הועלה דרך הממשק"}
                  </p>
                </div>
                <Badge>{doc.type}</Badge>
                {doc.location === "uploads" && (
                  <Badge category="routine">uploads</Badge>
                )}
                {doc.indexed ? (
                  <span className="inline-flex items-center gap-1 text-xs font-medium text-teal-300">
                    <CheckCircle2 className="h-4 w-4" />
                    {doc.chunk_count} קטעים
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 text-xs font-medium text-amber-300">
                    <XCircle className="h-4 w-4" />
                    לא מאונדקס
                  </span>
                )}
              </li>
            ))}
          </ul>
        )}
      </Card>

      {/* --- Architecture note --- */}
      <Card className="mt-6">
        <CardHeader title="איך זה עובד" />
        <div className="flex items-start gap-3 text-sm leading-relaxed text-slate-300">
          <Database className="mt-0.5 h-5 w-5 shrink-0 text-accent-light" />
          <p>
            השאלות מנותבות דרך <strong className="text-accent-light">אחזור FAISS מקומי</strong>{" "}
            על הקבצים שב-data/, והתשובה מנוסחת ב-<strong className="text-accent-light">Amazon
            Bedrock Runtime</strong>. אין שימוש ב-OpenSearch או ב-Knowledge Base בזמן ריצה —
            ה-Knowledge Base נשמר ב-AWS לצורכי הדגמה וצילומי מסך בלבד.
          </p>
        </div>
      </Card>
    </>
  );
}
