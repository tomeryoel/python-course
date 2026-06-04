/** Map technical errors to calm Hebrew user messages */
export function toUserMessage(err, t) {
  const msg = err?.message || "";
  if (msg.includes("fetch") || msg.includes("Failed to fetch") || msg.includes("NetworkError")) {
    return t("serverError");
  }
  if (msg.includes("נא להזין") || msg.includes("שגיאה")) {
    return msg;
  }
  console.error("[app]", err);
  return t("genericError");
}
