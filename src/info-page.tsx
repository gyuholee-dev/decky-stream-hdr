import {
  DialogBody,
  DialogBodyText,
  DialogButton,
  DialogControlsSection,
  DialogControlsSectionHeader as SteamSectionHeader,
  Focusable,
  Navigation,
} from "@decky/ui";

import type { ReactNode } from "react";

import { RepositoryIcon } from "./icon";
import { pluginInfo } from "./info";
import { ScrollWindow } from "./scroll-window";
import { strings } from "./strings";

// Route of the info page. It is registered in index.tsx and opened by the "Plugin Info" button.
export const infoRoute = "/streamhdr-info";

// Steam draws section headings in capital letters; the texts here are written as they should be read.
function SectionHeader({ children }: { children: ReactNode }) {
  return (
    <SteamSectionHeader>
      <span style={{ textTransform: "none" }}>{children}</span>
    </SteamSectionHeader>
  );
}

// A section that only exists in languages which provide its texts.
function OptionalSection({ heading, items }: { heading?: string; items?: string[] }) {
  if (!heading || !items?.length) return null;
  return (
    <DialogControlsSection>
      <SectionHeader>{heading}</SectionHeader>
      <Bullets items={items} />
    </DialogControlsSection>
  );
}

function Bullets({ items }: { items: string[] }) {
  return (
    <>
      {items.map((text) => (
        <DialogBodyText key={text}>{"• " + text}</DialogBodyText>
      ))}
    </>
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
          <DialogControlsSection>
            <SectionHeader>{strings.pluginName}</SectionHeader>
            <DialogBodyText>{info.about}</DialogBodyText>
          </DialogControlsSection>
          <DialogControlsSection>
            <SectionHeader>{info.usageHeading}</SectionHeader>
            <Bullets items={info.usage} />
          </DialogControlsSection>
          <OptionalSection heading={info.requirementsHeading} items={info.requirements} />
          <DialogControlsSection>
            <SectionHeader>{info.hostHeading}</SectionHeader>
            <Bullets items={info.host} />
          </DialogControlsSection>
          <OptionalSection heading={info.clientHeading} items={info.client} />
          <DialogControlsSection>
            <SectionHeader>{info.detailsHeading}</SectionHeader>
            <DialogBodyText>{`${info.version}: ${pluginInfo.version}`}</DialogBodyText>
            <DialogBodyText>{`${info.author}: ${pluginInfo.author}`}</DialogBodyText>
            <DialogBodyText>{`${info.license}: ${pluginInfo.license}`}</DialogBodyText>
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
          </DialogControlsSection>
        </DialogBody>
      </div>
    </ScrollWindow>
  );
}
