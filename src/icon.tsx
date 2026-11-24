// Plugin list icon: Material Icons "hdr_on" (Apache-2.0), imported as raw SVG text.
import hdrOnSvg from "@material-design-icons/svg/filled/hdr_on.svg";

// Make the icon follow the surrounding text size and color instead of the fixed 24px black default.
const markup = hdrOnSvg.replace(/ (width|height)="\d+"/g, "").replace("<svg", '<svg width="1em" height="1em" fill="currentColor"');

export function StreamIcon() {
  return <span style={{ display: "inline-flex" }} aria-hidden="true" dangerouslySetInnerHTML={{ __html: markup }} />;
}
