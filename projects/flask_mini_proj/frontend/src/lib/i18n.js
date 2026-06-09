/**
 * Lightweight i18n — Hebrew default; English when user explicitly requests.
 * Frontend-only (no backend changes).
 */

export const LOCALES = { he: "he", en: "en" };

export { LOCALES as defaultLocales };

const HEBREW_DISCLAIMER_MED =
  "לפי המסמכים שהועלו בלבד, ולא כהנחיה רפואית חדשה…";
const ENGLISH_DISCLAIMER_MED =
  "Based only on the uploaded documents and not as new medical advice.";

const HEBREW_DISCLAIMER_UI =
  "המערכת אינה מחליפה ייעוץ רפואי, פסיכיאטרי או פסיכולוגי. היא מציגה מידע על בסיס המסמכים שהועלו בלבד.";
const ENGLISH_DISCLAIMER_UI =
  "This system does not replace medical, psychiatric, or psychological advice. It displays information based only on uploaded documents.";

const ENGLISH_REQUEST_PATTERNS = [
  /\banswer\s+in\s+english\b/i,
  /\brespond\s+in\s+english\b/i,
  /\breply\s+in\s+english\b/i,
  /\bin\s+english\s+please\b/i,
  /\bplease\s+answer\s+in\s+english\b/i,
  /\benglish\s+please\b/i,
  /באנגלית\s*(\?|\.|!)?\s*$/i,
  /ענה\s+באנגלית/i,
  /תענה\s+באנגלית/i,
  /בבקשה\s+באנגלית/i,
];

/** Detect if user explicitly wants English */
export function detectLocaleFromText(text = "") {
  const t = text.trim();
  if (!t) return LOCALES.he;
  if (ENGLISH_REQUEST_PATTERNS.some((p) => p.test(t))) return LOCALES.en;
  return LOCALES.he;
}

/** Infer display locale from assistant answer (Hebrew chars vs mostly English) */
export function detectLocaleFromAnswer(answer = "", fallback = LOCALES.he) {
  const hebrewChars = (answer.match(/[\u0590-\u05FF]/g) || []).length;
  const latinChars = (answer.match(/[a-zA-Z]/g) || []).length;
  if (latinChars > hebrewChars * 1.5 && latinChars > 40) return LOCALES.en;
  return fallback;
}

export function getMedicationDisclaimer(locale = LOCALES.he) {
  return locale === LOCALES.en ? ENGLISH_DISCLAIMER_MED : HEBREW_DISCLAIMER_MED;
}

export function getUiDisclaimer(locale = LOCALES.he) {
  return locale === LOCALES.en ? ENGLISH_DISCLAIMER_UI : HEBREW_DISCLAIMER_UI;
}

const DISCLAIMER_VARIANTS = [
  HEBREW_DISCLAIMER_MED,
  "לפי המסמכים בלבד ולא כהנחיה רפואית חדשה.",
  "לפי המסמכים שהועלו בלבד",
  ENGLISH_DISCLAIMER_MED,
  "Based only on the uploaded documents",
];

// Keywords marking a line as a medical safety disclaimer (Hebrew + English).
const DISCLAIMER_KEYWORDS = [
  "לא כהנחיה רפואית",
  "כהנחיה רפואית חדשה",
  "לפי המסמכים שהועלו",
  "לפי המסמכים בלבד",
  "איני רופא",
  "אינני רופא",
  "אני לא רופא",
  "פנה לפסיכיאטר",
  "פני לפסיכיאטר",
  "אל תשנה שום דבר לפני",
  "not as new medical advice",
  "based only on the uploaded documents",
];

function normalizeDisclaimerText(text = "") {
  return text
    .replace(/[*_`]/g, "")
    .replace(/…/g, "")
    .replace(/[.,:;!?\-–—()"'\u05f3\u05f4]/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

function isDisclaimerLine(line) {
  const norm = normalizeDisclaimerText(line);
  return DISCLAIMER_KEYWORDS.some((kw) => norm.includes(normalizeDisclaimerText(kw)));
}

/** Keep at most one medical disclaimer line, catching near-duplicates. */
function dedupeDisclaimerLines(answer) {
  const lines = answer.split("\n");
  let seen = false;
  const kept = [];
  for (const line of lines) {
    if (line.trim() && isDisclaimerLine(line)) {
      if (seen) continue;
      seen = true;
    }
    kept.push(line);
  }
  return kept.join("\n").trim();
}

/** Normalize medication disclaimer in assistant text to match locale */
export function normalizeAnswerDisclaimers(answer, locale = LOCALES.he) {
  if (!answer) return answer;
  let result = answer;
  const target = getMedicationDisclaimer(locale);

  for (const variant of DISCLAIMER_VARIANTS) {
    if (result.includes(variant)) {
      result = result.split(variant).join(target);
    }
  }

  if (
    locale === LOCALES.en &&
    /תרופ|medication|cipralex|clonex|ציפרלקס|קלונקס/i.test(answer) &&
    !result.includes(ENGLISH_DISCLAIMER_MED)
  ) {
    result = `${result.trim()}\n\n${target}`;
  }

  // Final safety net: ensure the disclaimer appears at most once (near-dupe aware).
  return dedupeDisclaimerLines(result);
}

export const strings = {
  he: {
    chatEmpty: "בחר שאלה לדוגמה או כתוב מה אתה מרגיש עכשיו.",
    chatPlaceholder: "כתוב כאן… למשל: אני בסטרס עכשיו",
    send: "שלח",
    clear: "נקה",
    scenarios: "תרחישי בדיקה",
    generalQuestions: "שאלות כלליות",
    sources: "מקורות",
    serverError: "לא ניתן להתחבר לשרת. ודא ש-Flask רץ על פורט 5000.",
    genericError: "משהו לא הצליח. נסה שוב בעוד רגע.",
    loading: "חושב…",
    noTasks: "אין משימות פתוחות כרגע.",
    noUploads: "עדיין לא הועלו מסמכים חדשים.",
    uploadTitle: "העלה סיכום חדש",
    uploadHint:
      "העלה סיכום חדש כדי לעדכן את הזיכרון החיצוני וההנחיות האישיות שלך.",
  },
  en: {
    chatEmpty: "Pick an example or write how you feel right now.",
    chatPlaceholder: "Type here… e.g. I am stressed right now",
    send: "Send",
    clear: "Clear",
    scenarios: "Test scenarios",
    generalQuestions: "General questions",
    sources: "Sources",
    serverError: "Cannot reach server. Ensure Flask runs on port 5000.",
    genericError: "Something went wrong. Please try again shortly.",
    loading: "Thinking…",
    noTasks: "No open tasks right now.",
    noUploads: "No new documents uploaded yet.",
    uploadTitle: "Upload new summary",
    uploadHint:
      "Upload a new summary to update your external memory and personal guidance.",
  },
};

export function t(locale, key) {
  return strings[locale]?.[key] ?? strings.he[key] ?? key;
}
