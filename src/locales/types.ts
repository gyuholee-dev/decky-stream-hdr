import type { Strings } from "./en";

// The info page sections that only some languages provide yet: they are shown only when a language
// has the text, so a language can gain them without the English reference being changed first.
export type InfoStrings = Strings["info"] & {
  requirementsHeading?: string;
  requirements?: string[];
  clientHeading?: string;
  client?: string[];
};

// All texts of a language once English has filled the gaps.
export type ResolvedStrings = Omit<Strings, "info"> & { info: InfoStrings };

// What a language file provides: anything left out is taken from English.
export type LocaleStrings = Partial<Omit<Strings, "errors" | "info">> & {
  errors?: Record<string, string>;
  info?: Partial<InfoStrings>;
};
