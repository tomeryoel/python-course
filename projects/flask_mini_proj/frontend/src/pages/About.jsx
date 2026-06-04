import { Brain } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";
import { Card, CardHeader } from "../components/ui/Card";
import { useLocale } from "../context/LocaleContext";

export default function About() {
  const { uiDisclaimer } = useLocale();

  return (
    <>
      <PageHeader title="אודות הפרויקט" subtitle="פרויקט גמר — PTSD Companion" />

      <div className="grid gap-5 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="מטרה" />
          <p className="text-sm leading-relaxed text-slate-300">
            PTSD Companion הוא עוזר דיגיטלי אישי לזיכרון טיפולי, עומס קוגניטיבי ומצבי
            מצוקה. הוא עוזר לזכור הנחיות מהמטפלים, לבצע משימות יומיות, ולשאול שאלות
            מבוססות מסמכים בלבד.
          </p>
        </Card>
        <Card>
          <Brain className="mb-3 h-8 w-8 text-accent-light" />
          <p className="text-xs text-slate-500">זיכרון חיצוני מתמשך</p>
        </Card>
      </div>

      <Card className="mt-5">
        <CardHeader title="ארכיטקטורה" />
        <pre className="overflow-x-auto rounded-xl border border-glass-border bg-black/30 p-4 text-left text-xs leading-relaxed text-slate-400" dir="ltr">
{`Documents → Bedrock Knowledge Base
         ↓
    Flask + boto3 (RAG + tasks API)
         ↓
    React + Tailwind + tasks.json
         ↓
    Docker → EC2`}
        </pre>
      </Card>

      <Card className="mt-5">
        <CardHeader title="שירותי AWS" />
        <ul className="list-inside list-disc space-y-1 text-sm text-slate-300">
          <li>Amazon Bedrock Knowledge Base</li>
          <li>bedrock-agent-runtime (retrieve)</li>
          <li>bedrock-runtime (converse)</li>
          <li>S3 + EC2 לפריסה</li>
        </ul>
      </Card>

      <Card className="mt-5 border-amber-400/20">
        <CardHeader title="הצהרה רפואית" />
        <p className="text-sm text-slate-300">{uiDisclaimer}</p>
        <p className="mt-3 text-xs text-slate-500">
          דמו סטודנטיאלי עם מסמכים פיקטיביים — לא לשימוש קליני אמיתי.
        </p>
      </Card>
    </>
  );
}
