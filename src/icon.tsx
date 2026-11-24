// Icons are Material Icons (Apache-2.0), imported as raw SVG text.
import codeSvg from "@material-design-icons/svg/filled/code.svg";
import hdrOnSvg from "@material-design-icons/svg/filled/hdr_on.svg";
import infoSvg from "@material-design-icons/svg/filled/info.svg";

// Make an icon follow the surrounding text size and color instead of the fixed 24px black default.
function inline(svg: string): string {
  return svg.replace(/ (width|height)="\d+"/g, "").replace("<svg", '<svg width="1em" height="1em" fill="currentColor"');
}

function MaterialIcon({ svg }: { svg: string }) {
  return <span style={{ display: "inline-flex" }} aria-hidden="true" dangerouslySetInnerHTML={{ __html: inline(svg) }} />;
}

// Plugin list icon.
export const StreamIcon = () => <MaterialIcon svg={hdrOnSvg} />;
export const InfoIcon = () => <MaterialIcon svg={infoSvg} />;
// Material Icons has no brand logos, so the repository link uses the "code" icon.
export const RepositoryIcon = () => <MaterialIcon svg={codeSvg} />;
