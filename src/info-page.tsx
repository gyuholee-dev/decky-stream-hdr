import { DialogBody, DialogButton, Focusable, Navigation } from "@decky/ui";

import type { ReactNode } from "react";

import { RepositoryIcon } from "./icon";
import { pluginInfo } from "./info";
import { ScrollWindow } from "./scroll-window";
import { strings } from "./strings";

// Route of the info page. It is registered in index.tsx and opened by the "Plugin Info" button.
export const infoRoute = "/streamhdr-info";

// The page is laid out like GitHub renders a README: a heading with a thin line under it, text with a comfortable
// line height, and real lists whose wrapped lines align under the first word.
const LINE_COLOR = "rgba(255, 255, 255, 0.3)";

function SectionHeader({ children, title }: { children: ReactNode; title?: boolean }) {
  return (
    <div
      style={{
        fontSize: title ? "1.75rem" : "1.5rem",
        fontWeight: 600,
        lineHeight: 1.25,
        paddingBottom: "8px",
        marginTop: "24px",
        marginBottom: "16px",
        borderBottom: `1px solid ${LINE_COLOR}`,
      }}
    >
      {children}
    </div>
  );
}

function Section({ heading, title, children }: { heading: string; title?: boolean; children: ReactNode }) {
  return (
    <div>
      <SectionHeader title={title}>{heading}</SectionHeader>
      {children}
    </div>
  );
}

function Paragraph({ children }: { children: ReactNode }) {
  return <div style={{ lineHeight: 1.5, marginBottom: "16px" }}>{children}</div>;
}

// A bulleted or numbered list; `ordered` numbers the items.
function Items({ items, ordered }: { items: string[]; ordered?: boolean }) {
  const List = ordered ? "ol" : "ul";
  return (
    <List style={{ listStyleType: ordered ? "decimal" : "disc", paddingLeft: "2em", margin: "0 0 16px 0", lineHeight: 1.5 }}>
      {items.map((text, index) => (
        <li key={text} style={{ marginTop: index === 0 ? 0 : "4px" }}>
          {text}
        </li>
      ))}
    </List>
  );
}

// A section that only exists in languages which provide its texts.
function OptionalSection({ heading, items }: { heading?: string; items?: string[] }) {
  if (!heading || !items?.length) return null;
  return (
    <Section heading={heading}>
      <Items items={items} />
    </Section>
  );
}

export function InfoPage() {
  const info = strings.info;
  return (
    // The back button returns to the previous screen. The window scrolls with the stick or d-pad.
    <ScrollWindow onCancel={() => Navigation.NavigateBack()}>
      <div
        style={{
          padding: "0 30px 24px",
          // Break between words, not inside them; only text that cannot break otherwise wraps anywhere.
          wordBreak: "keep-all",
          overflowWrap: "anywhere",
        }}
      >
        <DialogBody>
          <Section heading={strings.pluginName} title>
            <Paragraph>{info.about}</Paragraph>
          </Section>
          <Section heading={info.usageHeading}>
            <Items items={info.usage} ordered />
          </Section>
          <OptionalSection heading={info.requirementsHeading} items={info.requirements} />
          <Section heading={info.hostHeading}>
            <Items items={info.host} />
          </Section>
          <OptionalSection heading={info.clientHeading} items={info.client} />
          <Section heading={info.detailsHeading}>
            <Items items={[`${info.version}: ${pluginInfo.version}`, `${info.author}: ${pluginInfo.author}`, `${info.license}: ${pluginInfo.license}`]} />
            {/* A button at the right edge: as tall as Steam's own buttons (like Reset All Settings), but only as wide as its content. */}
            <Focusable style={{ display: "flex", justifyContent: "flex-end" }}>
              <DialogButton
                onClick={() => Navigation.NavigateToExternalWeb(pluginInfo.repositoryUrl)}
                style={{ width: "auto", minWidth: "auto", paddingLeft: "28px", paddingRight: "28px", display: "inline-flex", alignItems: "center" }}
              >
                <span style={{ display: "inline-flex", marginRight: "10px" }}>
                  <RepositoryIcon />
                </span>
                {strings.githubButton}
              </DialogButton>
            </Focusable>
          </Section>
        </DialogBody>
      </div>
    </ScrollWindow>
  );
}
