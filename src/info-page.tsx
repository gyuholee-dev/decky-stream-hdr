import {
  ButtonItem,
  DialogBody,
  DialogBodyText,
  DialogControlsSection,
  DialogControlsSectionHeader,
  Focusable,
  Navigation,
} from "@decky/ui";

import { RepositoryIcon } from "./icon";
import { pluginInfo } from "./info";
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
    // The top margin keeps the content below Steam's status bar; the back button returns to the previous screen.
    <Focusable onCancel={() => Navigation.NavigateBack()} style={{ marginTop: "40px", height: "calc(100% - 40px)", overflowY: "auto" }}>
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
          <ButtonItem layout="below" onClick={() => Navigation.NavigateToExternalWeb(pluginInfo.repositoryUrl)}>
            <span style={{ display: "inline-flex", alignItems: "center", gap: "8px" }}>
              <RepositoryIcon />
              {strings.githubButton}
            </span>
          </ButtonItem>
        </DialogControlsSection>
      </DialogBody>
    </Focusable>
  );
}
