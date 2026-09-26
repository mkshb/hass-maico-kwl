import { css, html, nothing, type TemplateResult } from "lit";

import type { KwlDevice } from "./device";
import { KEY, type EntityKey } from "./keys";
import { localize } from "./localize";
import type { HomeAssistant } from "./types";

// Notices the card already shows elsewhere (the bypass arc in the schematic).
const SHOWN_ELSEWHERE = new Set(["bypass_active"]);

export interface Message {
  kind: "fault" | "notice";
  text: string;
}

function activeBits(device: KwlDevice, key: EntityKey): string[] {
  const active = device.attribute<unknown>(key, "active");
  return Array.isArray(active) ? active.filter((bit): bit is string => typeof bit === "string") : [];
}

/** Active faults first, then notices, as translated text. */
export function activeMessages(hass: HomeAssistant, device: KwlDevice): Message[] {
  const messages: Message[] = [];
  for (const [kind, key] of [["fault", KEY.faultCode], ["notice", KEY.noticeCode]] as const) {
    const stateObj = device.stateObj(key);
    if (!stateObj) continue;
    for (const bit of activeBits(device, key)) {
      if (kind === "notice" && SHOWN_ELSEWHERE.has(bit)) continue;
      messages.push({ kind, text: hass.formatEntityAttributeValue(stateObj, "active", bit) });
    }
  }
  return messages;
}

export interface HeaderContext {
  hass: HomeAssistant;
  device: KwlDevice;
  expanded: boolean;
  toggle: () => void;
  moreInfo: (key: EntityKey) => void;
}

export function renderHeader(ctx: HeaderContext): TemplateResult {
  const { hass, device } = ctx;
  const messages = activeMessages(hass, device);
  const faults = messages.filter((m) => m.kind === "fault").length;
  const notices = messages.length - faults;
  const label = faults
    ? faults === 1 ? localize(hass, "faults_one") : localize(hass, "faults_many", { count: faults })
    : notices === 1 ? localize(hass, "notices_one") : localize(hass, "notices_many", { count: notices });

  return html`
    <div class="header">
      <div class="title">${device.name}</div>
      ${messages.length
        ? html`<button
            type="button"
            class=${faults ? "chip fault" : "chip notice"}
            aria-expanded=${ctx.expanded ? "true" : "false"}
            @click=${ctx.toggle}
          >
            <svg viewBox="0 0 16 16" aria-hidden="true">
              <circle cx="8" cy="8" r="6.5"></circle>
              <line x1="8" y1="4.5" x2="8" y2="9"></line>
              <line x1="8" y1="11.4" x2="8" y2="11.5"></line>
            </svg>
            ${label}
          </button>`
        : nothing}
    </div>
    ${messages.length && ctx.expanded
      ? html`<ul class="messages">
          ${messages.map(
            (message) => html`<li>
              <button
                type="button"
                class=${message.kind}
                @click=${() => ctx.moreInfo(message.kind === "fault" ? KEY.faultCode : KEY.noticeCode)}
              >
                ${message.text}
              </button>
            </li>`,
          )}
        </ul>`
      : nothing}
  `;
}

export const headerStyles = css`
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 16px 16px 0;
  }
  .title {
    min-width: 0;
    overflow: hidden;
    font-size: 20px;
    font-weight: 400;
    line-height: 28px;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .chip {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    gap: 6px;
    height: 32px;
    padding: 0 12px;
    border: 0;
    border-radius: 16px;
    font: inherit;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
  }
  .chip svg {
    width: 16px;
    height: 16px;
    fill: none;
    stroke: currentColor;
    stroke-width: 2px;
    stroke-linecap: round;
  }
  .chip.notice {
    background: var(--kwl-warn-bg);
    color: var(--kwl-warn-fg);
  }
  .chip.fault {
    background: var(--kwl-fault-bg);
    color: var(--kwl-fault-fg);
  }
  .chip:focus-visible,
  .messages button:focus-visible {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
  }
  .messages {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin: 12px 16px 0;
    padding: 0;
    list-style: none;
  }
  .messages button {
    width: 100%;
    padding: 8px 12px;
    border: 0;
    border-radius: 8px;
    font: inherit;
    font-size: 13px;
    text-align: left;
    cursor: pointer;
  }
  .messages .notice {
    background: var(--kwl-warn-bg);
    color: var(--kwl-warn-fg);
  }
  .messages .fault {
    background: var(--kwl-fault-bg);
    color: var(--kwl-fault-fg);
  }
`;
