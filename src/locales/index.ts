import { en } from "./en";
import type { LocaleStrings, ResolvedStrings } from "./types";
import { ko } from "./ko";

// To add a language: create src/locales/<code>.ts exporting a `LocaleStrings` (texts left out
// fall back to English), then register it here.
export const locales: Record<string, LocaleStrings> = { en, ko };

// Steam's own setting already holds language codes ("ko"), but its settings API names languages in
// English ("koreana"); this table covers that second form in case a name shows up.
const steamLanguageCodes: Record<string, string> = {
  english: "en",
  koreana: "ko",
  japanese: "ja",
  schinese: "zh-CN",
  tchinese: "zh-TW",
  german: "de",
  french: "fr",
  spanish: "es",
  latam: "es",
  russian: "ru",
  brazilian: "pt-BR",
  portuguese: "pt",
  italian: "it",
  polish: "pl",
  turkish: "tr",
};

// Where the language comes from, in order: Steam's own setting, then the browser's.
// The Steam setting is read from LocalizationManager.m_rgLocalesToUse, which Decky plugin code (it runs
// in Steam's SharedJSContext) can reach. Checked on a Legion Go 2: it held ["ko"] for a Korean Steam.
export function detectLanguages(): string[] {
  const found: string[] = [];
  try {
    const steamLocales: string[] | undefined = (window as any).LocalizationManager?.m_rgLocalesToUse;
    for (const name of steamLocales ?? []) found.push(steamLanguageCodes[name] ?? name);
  } catch {
    // Not running inside Steam: fall through to the browser language.
  }
  if (typeof navigator !== "undefined" && navigator.language) found.push(navigator.language);
  return found;
}

function findLocale(code: string): LocaleStrings | undefined {
  return locales[code] ?? locales[code.split("-")[0]];
}

// The first requested language that has a file wins; anything it lacks comes from English.
export function resolveStrings(requested: string[]): ResolvedStrings {
  for (const code of requested) {
    const locale = findLocale(code);
    if (locale) return { ...en, ...locale, errors: { ...en.errors, ...locale.errors }, info: { ...en.info, ...locale.info } };
  }
  return en;
}

export function fill(template: string, values: Record<string, string | null | undefined>): string {
  return template.replace(/\{(\w+)\}/g, (_, key: string) => values[key] ?? "");
}
