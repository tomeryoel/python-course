import { useState } from "react";
import { AlertTriangle, Phone } from "lucide-react";
import Button from "../ui/Button";
import { cn } from "../../lib/cn";

/** Confirmation modal — emergency call requires explicit user approval. */
export default function EmergencyContactModal({ open, onClose, onConfirm, loading, result }) {
  const [checked, setChecked] = useState(false);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
      <div
        className="w-full max-w-md rounded-2xl border border-amber-400/30 bg-navy-deep p-6 shadow-2xl"
        role="dialog"
        aria-labelledby="emergency-title"
      >
        <div className="mb-4 flex items-center gap-3 text-amber-200">
          <AlertTriangle className="h-6 w-6 shrink-0" />
          <h2 id="emergency-title" className="text-lg font-semibold">
            ליצור קשר עם איש קשר החירום?
          </h2>
        </div>
        <p className="text-sm leading-relaxed text-slate-300">
          פעולה זו תפעיל שיחת תמיכה אוטומטית דרך Amazon Connect לאיש הקשר שהגדרת.
          <strong className="mt-2 block text-amber-200/90">
            זו אינה שירות חירום רפואי (101/100).
          </strong>
        </p>
        <label className="mt-4 flex cursor-pointer items-start gap-2 text-sm text-slate-300">
          <input
            type="checkbox"
            checked={checked}
            onChange={(e) => setChecked(e.target.checked)}
            className="mt-1"
          />
          אני מאשר/ת ליצור קשר עם איש הקשר שלי
        </label>
        {result && (
          <p
            className={cn(
              "mt-3 rounded-lg px-3 py-2 text-sm",
              result.result?.status === "call_started"
                ? "bg-teal-500/10 text-teal-200"
                : "bg-red-500/10 text-red-200"
            )}
          >
            {result.result?.message || result.result?.error || result.message}
          </p>
        )}
        <div className="mt-6 flex gap-3">
          <Button variant="secondary" className="flex-1" onClick={onClose} disabled={loading}>
            ביטול
          </Button>
          <Button
            variant="danger"
            className="flex-1"
            disabled={!checked || loading}
            onClick={() => onConfirm()}
          >
            <Phone className="h-4 w-4" />
            {loading ? "מפעיל…" : "אשר והתקשר"}
          </Button>
        </div>
      </div>
    </div>
  );
}
