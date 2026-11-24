// Runs before the plugin code is loaded. Fakes the Steam setting the plugin reads its language from:
// open the preview with ?lang=koreana (or ?lang=ko) to try another language.
const requested = new URLSearchParams(window.location.search).get("lang");
if (requested) {
  (window as any).LocalizationManager = { m_rgLocalesToUse: [requested] };
}
