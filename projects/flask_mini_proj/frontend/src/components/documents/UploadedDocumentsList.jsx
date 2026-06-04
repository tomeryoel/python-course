import { FileText, Upload } from "lucide-react";
import Badge from "../ui/Badge";
import EmptyState from "../ui/EmptyState";

const statusLabels = {
  synced: { text: "מסונכרן", className: "text-teal-300" },
  pending_sync: { text: "ממתין לסנכרון", className: "text-amber-300" },
  error: { text: "שגיאה", className: "text-red-300" },
};

export default function UploadedDocumentsList({ documents }) {
  if (!documents?.length) {
    return (
      <EmptyState
        icon={Upload}
        title="עדיין לא הועלו מסמכים חדשים"
        description="סיכומים שתעלה יופיעו כאן עם תאריך, סוג קובץ וסטטוס סנכרון."
      />
    );
  }

  return (
    <ul className="space-y-3">
      {documents.map((doc) => {
        const st = statusLabels[doc.status] || statusLabels.pending_sync;
        return (
          <li
            key={doc.id}
            className="flex items-center gap-4 rounded-xl border border-glass-border bg-black/20 p-4 transition hover:border-accent/30"
          >
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-accent/10 text-accent-light">
              <FileText className="h-5 w-5" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate font-medium text-white">{doc.name}</p>
              <p className="mt-0.5 text-xs text-slate-500">
                {new Date(doc.uploadedAt).toLocaleString("he-IL")}
              </p>
            </div>
            <Badge>{doc.type}</Badge>
            <span className={`text-xs font-medium ${st.className}`}>{st.text}</span>
          </li>
        );
      })}
    </ul>
  );
}
