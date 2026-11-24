import {
  DialogBody,
  DialogBodyText,
  DialogButton,
  DialogControlsSection,
  DialogControlsSectionHeader,
  Focusable,
  Navigation,
} from "@decky/ui";

import { RepositoryIcon } from "./icon";
import { pluginInfo } from "./info";
import { ScrollWindow } from "./scroll-window";
import { strings } from "./strings";

// Route of the info page. It is registered in index.tsx and opened by the "Plugin Info" button.
export const infoRoute = "/streamhdr-info";

// A section that only exists in languages which provide its texts.
function OptionalSection({ heading, items }: { heading?: string; items?: string[] }) {
  if (!heading || !items?.length) return null;
  return (
    <DialogControlsSection>
      <DialogControlsSectionHeader>{heading}</DialogControlsSectionHeader>
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
            <DialogControlsSectionHeader>{strings.pluginName}</DialogControlsSectionHeader>
            <DialogBodyText>{info.about}</DialogBodyText>
          </DialogControlsSection>
          <DialogControlsSection>
            <DialogControlsSectionHeader>{info.usageHeading}</DialogControlsSectionHeader>
            <Bullets items={info.usage} />
          </DialogControlsSection>
          <OptionalSection heading={info.requirementsHeading} items={info.requirements} />
          <DialogControlsSection>
            <DialogControlsSectionHeader>{info.hostHeading}</DialogControlsSectionHeader>
            <Bullets items={info.host} />
          </DialogControlsSection>
          <OptionalSection heading={info.clientHeading} items={info.client} />
          <DialogControlsSection>
            <DialogControlsSectionHeader>{info.detailsHeading}</DialogControlsSectionHeader>
            <DialogBodyText>{`${info.version}: ${pluginInfo.version}`}</DialogBodyText>
            <DialogBodyText>{`${info.author}: ${pluginInfo.author}`}</DialogBodyText>
            <DialogBodyText>{`${info.license}: ${pluginInfo.license}`}</DialogBodyText>
            {/* A small button at the right edge, like the repository links of other plugins. */}
            <Focusable style={{ display: "flex", justifyContent: "flex-end" }}>
              <DialogButton
                onClick={() => Navigation.NavigateToExternalWeb(pluginInfo.repositoryUrl)}
                style={{ width: "auto", minWidth: "auto", padding: "0 16px", minHeight: "30px", fontSize: "12px", display: "inline-flex", alignItems: "center", gap: "8px" }}
              >
                <RepositoryIcon />
                {strings.githubButton}
              </DialogButton>
            </Focusable>
          </DialogControlsSection>
        </DialogBody>
      </div>
    </ScrollWindow>
  );
}
