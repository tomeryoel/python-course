import { useCallback, useEffect, useState } from "react";
import {
  Bot,
  CheckCircle2,
  Cloud,
  Database,
  FileText,
  XCircle,
} from "lucide-react";
import { fetchDocuments } from "../api";
import DocumentUploadZone from "../components/documents/DocumentUploadZone";
import PageHeader from "../components/layout/PageHeader";
import { Card, CardHeader } from "../components/ui/Card";
import Badge from "../components/ui/Badge";
import EmptyState from "../components/ui/EmptyState";
import ErrorAlert from "../components/ui/ErrorAlert";

function formatBytes(n) {
  if (!n) return "0 KB";
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(0)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

function StatusRow({ ok, label, detail }) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-white/8 bg-black/20 px-4 py-3">
      {ok ? (
        <CheckCircle2 className="h-5 w-5 shrink-0 text-teal-400" />
      ) : (
        <XCircle className="h-5 w-5 shrink-0 text-amber-400" />
      )}
      <div>
        <p className="text-sm font-medium text-white">{label}</p>
        {detail && <p className="text-xs text-slate-500">{detail}</p>}
      </div>
    </div>
  );
}

export default function Documents() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    setError("");
    try {
      setData(await fetchDocuments());
    } catch (e) {
      setError(e?.message || "שגיאה");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const kb = data?.knowledge_base;
  const s3Docs = data?.s3_documents || [];

  return (
    <>
      <PageHeader
        title="מסמכים ו-RAG"
        subtitle="מקור האמת: S3 → Bedrock Knowledge Base → Bedrock Agent"
      />

      {error && <ErrorAlert message={error} className="mb-5" />}

      <Card premium>
        <CardHeader
          title="סטטוס ארכיטקטורה"
          subtitle={kb?.note || "Bedrock Agent + Knowledge Base"}
        />
        {loading ? (
          <p className="text-sm text-slate-400">טוען…</p>
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            <StatusRow
              ok={kb?.agent_configured}
              label="Bedrock Agent"
              detail={
                kb?.agent_configured
                  ? "מוגדר — Flask קורא invoke_agent"
                  : "הגדר BEDROCK_AGENT_ID ו-BEDROCK_AGENT_ALIAS_ID"
              }
            />
            <StatusRow
              ok={kb?.knowledge_base_configured}
              label="Bedrock Knowledge Base"
              detail={kb?.knowledge_base_id || "לא מוגדר"}
            />
            <StatusRow
              ok={kb?.s3_bucket_configured}
              label="S3 Bucket"
              detail={
                kb?.s3_bucket_name
                  ? `${kb.s3_bucket_name}/${kb.s3_prefix}`
                  : "הגדר S3_BUCKET_NAME"
              }
            />
            <StatusRow
              ok={data?.runtime_mode === "bedrock_agent_knowledge_base"}
              label="Runtime mode"
              detail={data?.runtime_mode || "—"}
            />
          </div>
        )}
      </Card>

      <div className="mt-6">
        <DocumentUploadZone onUploaded={refresh} />
        <p className="mt-2 text-xs text-slate-500">
          העלאה מקומית — ל-RAG בפרודקשן: העלה ל-S3 והפעל סנכרון Knowledge Base.
        </p>
      </div>

      <Card className="mt-6">
        <CardHeader
          title="מסמכים ב-S3"
          subtitle="רשימה מה-bucket המוגדר (אם זמין)"
          action={<Cloud className="h-5 w-5 text-accent-light" />}
        />
        {loading ? (
          <p className="text-sm text-slate-400">טוען…</p>
        ) : !kb?.s3_bucket_configured ? (
          <EmptyState
            icon={Cloud}
            title="S3 לא מוגדר"
            description="הגדר S3_BUCKET_NAME ב-.env כדי לראות מסמכים."
          />
        ) : s3Docs.length === 0 ? (
          <EmptyState
            icon={FileText}
            title="לא נמצאו קבצים"
            description={`בדוק prefix: ${kb?.s3_prefix || "data/"}`}
          />
        ) : (
          <ul className="space-y-3">
            {s3Docs.map((doc) => (
              <li
                key={doc.key}
                className="flex items-center gap-4 rounded-xl border border-white/8 bg-black/20 p-4"
              >
                <FileText className="h-5 w-5 text-accent-light" />
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium text-white">{doc.name}</p>
                  <p className="text-xs text-slate-500">
                    {formatBytes(doc.size_bytes)} · {doc.key}
                  </p>
                </div>
                <Badge>{doc.type}</Badge>
              </li>
            ))}
          </ul>
        )}
        {data?.s3_error && (
          <p className="mt-3 text-xs text-amber-300">S3: {data.s3_error}</p>
        )}
      </Card>

      <Card className="mt-6">
        <CardHeader title="איך RAG עובד" />
        <div className="flex items-start gap-3 text-sm leading-relaxed text-slate-300">
          <Database className="mt-0.5 h-5 w-5 shrink-0 text-accent-light" />
          <p>
            המסמכים ב-<strong className="text-accent-light">S3</strong> מאונדקסים ב-{" "}
            <strong className="text-accent-light">Bedrock Knowledge Base</strong>.
            ה-<strong className="text-accent-light">Bedrock Agent</strong> מבצע RAG ומפעיל
            Lambda tools. Flask קורא <code className="text-accent-light">invoke_agent</code>{" "}
            בלבד — לא שאילתות וקטור ישירות ולא FAISS מקומי. אחסון וקטורי: S3 Vectors דרך Knowledge Base.
          </p>
          <Bot className="hidden h-5 w-5 text-accent/50 md:block" />
        </div>
      </Card>
    </>
  );
}
