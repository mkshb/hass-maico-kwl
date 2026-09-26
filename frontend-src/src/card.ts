import { LitElement, css, html, nothing, type PropertyValues } from "lit";
import { property, state } from "lit/decorators.js";

import { KwlDevice, maicoDeviceIds } from "./device";
import { REPORTED, controlStyles, renderControls, type Control, type ControlsContext } from "./controls";
import { browserLocalize, localize } from "./localize";
import { renderSchematic, schematicStyles } from "./schematic";
import { buildTiles, renderTiles, tileStyles } from "./tiles";
import type { HomeAssistant, MaicoKwlCardConfig } from "./types";

const CARD_TYPE = "maico-kwl-card";

// The unit applies a change slowly and the integration reports it with its
// next poll (30 s by default), so a change is shown at once and kept for up
// to this long while the unit has not confirmed it yet.
const PENDING_TIMEOUT_MS = 35_000;

interface Pending {
  value: string;
  timer: number;
}

export class MaicoKwlCard extends LitElement {
  @property({ attribute: false }) public hass?: HomeAssistant;

  @state() private _config?: MaicoKwlCardConfig;

  private readonly _uid = `kwl${Math.random().toString(36).slice(2, 10)}`;

  @state() private _pending = new Map<Control, Pending>();

  public setConfig(config: MaicoKwlCardConfig): void {
    this._config = config;
  }

  public getCardSize(): number {
    return 6;
  }

  public static async getConfigElement(): Promise<HTMLElement> {
    const { EDITOR_TYPE } = await import("./editor");
    return document.createElement(EDITOR_TYPE);
  }

  public static getStubConfig(hass: HomeAssistant): Omit<MaicoKwlCardConfig, "type"> {
    const [deviceId] = maicoDeviceIds(hass);
    return deviceId ? { device_id: deviceId } : {};
  }

  public disconnectedCallback(): void {
    super.disconnectedCallback();
    for (const control of [...this._pending.keys()]) this._clearPending(control);
  }

  protected willUpdate(changed: PropertyValues<this>): void {
    // A pending change is done once the unit reports the value.
    if (!changed.has("hass") || !this._pending.size || !this.hass) return;
    const device = this._device();
    if (!device) return;
    for (const [control, pending] of this._pending) {
      if (REPORTED[control](device) === pending.value) this._clearPending(control);
    }
  }

  private _clearPending(control: Control): void {
    const pending = this._pending.get(control);
    if (!pending) return;
    window.clearTimeout(pending.timer);
    this._pending.delete(control);
    this._pending = new Map(this._pending);
  }

  private _controls(device: KwlDevice): ControlsContext {
    return {
      hass: this.hass!,
      device,
      moreInfo: (key) => this._moreInfo(device.entityId(key)),
      shown: (control) => this._pending.get(control)?.value ?? REPORTED[control](device),
      pending: (control) => this._pending.has(control),
      change: (control, value, send) => {
        this._clearPending(control);
        if (REPORTED[control](device) === value) {
          send();
          return;
        }
        const timer = window.setTimeout(() => this._clearPending(control), PENDING_TIMEOUT_MS);
        this._pending = new Map(this._pending).set(control, { value, timer });
        send().catch(() => this._clearPending(control));
      },
    };
  }

  /** The configured unit, or the only/first one when none is configured. */
  private _device(): KwlDevice | undefined {
    const deviceId = this._config?.device_id ?? maicoDeviceIds(this.hass!)[0];
    if (!deviceId || !this.hass!.devices[deviceId]) return undefined;
    return new KwlDevice(this.hass!, deviceId);
  }

  protected render() {
    if (!this.hass || !this._config) return nothing;
    const device = this._device();
    if (!device) {
      const message = this._config.device_id ? "device_missing" : "no_device";
      return html`<ha-card><p class="empty">${localize(this.hass, message)}</p></ha-card>`;
    }
    return html`
      <ha-card .header=${device.name} class=${this.hass.themes?.darkMode ? "dark" : ""}>
        <div class="content">
          ${renderSchematic({
            hass: this.hass,
            device,
            uid: this._uid,
            moreInfo: (key) => this._moreInfo(device.entityId(key)),
          })}
          ${renderTiles(this.hass, buildTiles(this.hass, device), (entityId) => this._moreInfo(entityId))}
          ${renderControls(this._controls(device))}
        </div>
      </ha-card>
    `;
  }

  private _moreInfo(entityId: string | undefined): void {
    if (!entityId) return;
    this.dispatchEvent(
      new CustomEvent("hass-more-info", { detail: { entityId }, bubbles: true, composed: true }),
    );
  }

  static styles = [
    schematicStyles,
    tileStyles,
    controlStyles,
    css`
    ha-card {
      --kwl-bus-bg: #dcebf6;
      --kwl-bus-fg: #01497c;
      --kwl-warn-bg: #fff1dc;
      --kwl-warn-fg: #7a4a00;
      --kwl-good: #2e7d32;
      --kwl-moderate: #f9a825;
      --kwl-poor: #c62828;
    }
    ha-card.dark {
      --kwl-bus-bg: #123447;
      --kwl-bus-fg: #8fd3f7;
      --kwl-warn-bg: #3b2c12;
      --kwl-warn-fg: #ffcc80;
      --kwl-good: #81c784;
      --kwl-moderate: #ffd54f;
      --kwl-poor: #ef5350;
    }
    .content {
      padding: 0 16px 16px;
    }
    .empty {
      padding: 16px;
      margin: 0;
      color: var(--secondary-text-color);
    }
  `,
  ];
}

declare global {
  interface Window {
    customCards?: { type: string; name: string; description: string; preview?: boolean }[];
  }
}

if (!customElements.get(CARD_TYPE)) {
  customElements.define(CARD_TYPE, MaicoKwlCard);
  window.customCards = window.customCards ?? [];
  window.customCards.push({
    type: CARD_TYPE,
    name: browserLocalize("card_name"),
    description: browserLocalize("card_description"),
    preview: true,
  });
}
