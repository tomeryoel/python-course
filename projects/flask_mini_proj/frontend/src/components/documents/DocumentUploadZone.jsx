import { useCallback, useState } from "react";
import { CloudUpload, FileUp } from "lucide-react";
import { uploadDocument } from "../../api";
import {
  addUploadedDocument,
  fileTypeBadge,
  validateFile,
} from "../../lib/documentsStore";
import { cn } from "../../lib/cn";
import ErrorAlert from "../ui/ErrorAlert";

export default function DocumentUploadZone({ onUploaded }) {
  const [dragging, setDragging] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("idle"); // idle | uploading | success | error
  const [message, setMessage] = useState("");

  const processFile = useCallback(
    async (file) => {
      const validation = validateFile(file);
      if (!validation.valid) {
        setStatus("error");
        setMessage(validation.error);
        return;
      }

      setStatus("uploading");
      setProgress(10);
      setMessage("");

      try {
        const result = await uploadDocument(file, (p) => setProgress(p));
        setProgress(100);
        setStatus("success");
        setMessage(
          result.synced
            ? "המסמך הועלה ויסונכרן לבסיס הידע שלך."
            : "המסמך נשמר — סנכרון לענן יושלם כשהשרת יהיה זמין."
        );
        onUploaded?.(result.document);
      } catch (err) {
        console.error("[upload]", err);
        setStatus("error");
        setMessage("לא הצלחנו להעלות את הקובץ. נסה שוב מאוחר יותר.");
      } finally {
        setTimeout(() => setProgress(0), 2500);
      }
    },
    [onUploaded]
  );

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) processFile(file);
  };

  return (
    <div className="glass-panel p-6">
      <h3 className="text-lg font-semibold text-white">העלה סיכום חדש</h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-400">
        העלה סיכום חדש כדי לעדכן את הזיכרון החיצוני וההנחיות האישיות שלך.
        מסמכים חדשים יתווספו לבסיס הידע הקליני וישמשו יחד עם הסיכומים הקיימים.
      </p>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={cn(
          "mt-5 flex flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-12 transition-all duration-200",
          dragging
            ? "border-accent bg-accent/10 shadow-glow"
            : "border-glass-border bg-black/20 hover:border-accent/40"
        )}
      >
        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-accent/15 text-accent-light">
          <CloudUpload className="h-7 w-7" />
        </div>
        <p className="text-sm text-slate-300">גרור קובץ לכאן או</p>
        <label className="mt-3 inline-flex cursor-pointer items-center gap-2 rounded-xl border border-glass-border bg-glass px-4 py-2 text-sm text-slate-200 transition hover:bg-white/10 focus-ring">
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            className="sr-only"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) processFile(f);
              e.target.value = "";
            }}
          />
          <FileUp className="h-4 w-4" />
          בחר קובץ
        </label>
        <p className="mt-4 text-xs text-slate-500">PDF · DOCX · TXT · עד 15MB</p>
      </div>

      {status === "uploading" && (
        <div className="mt-4">
          <div className="mb-1 flex justify-between text-xs text-slate-400">
            <span>מעלה…</span>
            <span>{progress}%</span>
          </div>
          <div className="h-1.5 overflow-hidden rounded-full bg-white/10">
            <div
              className="h-full rounded-full bg-accent transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {status === "success" && (
        <p className="mt-4 rounded-lg border border-teal-400/30 bg-teal-500/10 px-3 py-2 text-sm text-teal-100">
          {message}
        </p>
      )}

      {status === "error" && (
        <div className="mt-4">
          <ErrorAlert message={message} />
        </div>
      )}
    </div>
  );
}

// Fix Button - doesn't support as="span", use span wrapper in upload zone