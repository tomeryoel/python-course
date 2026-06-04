const STORAGE_KEY = "ptsd_companion_uploaded_docs";

export function loadUploadedDocuments() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveUploadedDocuments(docs) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(docs));
}

export function addUploadedDocument(entry) {
  const docs = loadUploadedDocuments();
  docs.unshift(entry);
  saveUploadedDocuments(docs);
  return docs;
}

export const ACCEPTED_TYPES = {
  "application/pdf": { ext: "PDF", label: "PDF" },
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {
    ext: "DOCX",
    label: "DOCX",
  },
  "text/plain": { ext: "TXT", label: "TXT" },
};

export const ACCEPTED_EXTENSIONS = [".pdf", ".docx", ".txt"];

export function validateFile(file) {
  const name = file.name.toLowerCase();
  const okExt = ACCEPTED_EXTENSIONS.some((e) => name.endsWith(e));
  const okMime = Object.keys(ACCEPTED_TYPES).includes(file.type) || okExt;
  if (!okMime) {
    return { valid: false, error: "סוג קובץ לא נתמך. PDF, DOCX או TXT בלבד." };
  }
  if (file.size > 15 * 1024 * 1024) {
    return { valid: false, error: "הקובץ גדול מדי (מקסימום 15MB)." };
  }
  return { valid: true };
}

export function fileTypeBadge(file) {
  const n = file.name.toLowerCase();
  if (n.endsWith(".pdf")) return "PDF";
  if (n.endsWith(".docx")) return "DOCX";
  if (n.endsWith(".txt")) return "TXT";
  return "FILE";
}
