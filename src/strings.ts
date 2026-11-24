import { fill, detectLanguages, resolveStrings } from "./locales";

// Texts in the language Steam is set to (English when that language has no file). The language is
// read once when the plugin loads, so a language change applies after the plugin reloads.
export const strings = resolveStrings(detectLanguages());

export interface ErrorInfo {
  code: string;
  detail: string | null;
}

// Turns an error sent by the backend into text for the current language.
export function errorText(error: ErrorInfo): string {
  const template = strings.errors[error.code];
  if (!template) return fill(strings.unknownError, { code: error.code });
  return fill(template, { detail: error.detail });
}
