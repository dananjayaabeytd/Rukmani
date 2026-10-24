"use client";

/**
 * The interface language (English, Sinhala or Tamil), shared with every
 * component through React context. The choice is remembered in the
 * browser, so it stays after a refresh.
 */

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { STRINGS, type Lang, type Strings } from "@/lib/i18n";

const LANG_KEY = "rukmani:lang";

interface LanguageState {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: Strings;
}

const LanguageContext = createContext<LanguageState | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>("en");

  // Restore the saved choice after the first render (browser-only).
  useEffect(() => {
    try {
      const saved = localStorage.getItem(LANG_KEY);
      // eslint-disable-next-line react-hooks/set-state-in-effect -- one-time restore from storage
      if (saved === "en" || saved === "si" || saved === "ta") setLangState(saved);
    } catch {
      // Storage blocked — stay on English.
    }
  }, []);

  // Screen readers and fonts use the page's lang attribute.
  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  function setLang(next: Lang) {
    setLangState(next);
    try {
      localStorage.setItem(LANG_KEY, next);
    } catch {
      // Not saved, but the switch still works for this visit.
    }
  }

  return (
    <LanguageContext.Provider value={{ lang, setLang, t: STRINGS[lang] }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage(): LanguageState {
  const state = useContext(LanguageContext);
  if (!state) throw new Error("useLanguage must be used inside LanguageProvider");
  return state;
}
