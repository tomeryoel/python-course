import { createContext, useCallback, useContext, useMemo, useState } from "react";
import {
  LOCALES,
  detectLocaleFromText,
  getUiDisclaimer,
  normalizeAnswerDisclaimers,
  t,
} from "../lib/i18n";

const LocaleContext = createContext(null);

export function LocaleProvider({ children }) {
  const [locale, setLocale] = useState(LOCALES.he);

  const setLocaleFromUserMessage = useCallback((text) => {
    const next = detectLocaleFromText(text);
    setLocale(next);
    return next;
  }, []);

  const processAssistantAnswer = useCallback(
    (answer, userLocale) => {
      const active = userLocale || locale;
      return normalizeAnswerDisclaimers(answer, active);
    },
    [locale]
  );

  const value = useMemo(
    () => ({
      locale,
      setLocale: (loc) => setLocale(loc === LOCALES.en ? LOCALES.en : LOCALES.he),
      setLocaleFromUserMessage,
      processAssistantAnswer,
      uiDisclaimer: getUiDisclaimer(locale),
      t: (key) => t(locale, key),
    }),
    [locale, setLocaleFromUserMessage, processAssistantAnswer]
  );

  return (
    <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>
  );
}

export function useLocale() {
  const ctx = useContext(LocaleContext);
  if (!ctx) throw new Error("useLocale must be used within LocaleProvider");
  return ctx;
}
