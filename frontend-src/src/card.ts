import { LitElement, css, html, nothing, type PropertyValues } from "lit";
import { property, state } from "lit/decorators.js";

import { KwlDevice, maicoDeviceIds } from "./device";
import { KEY } from "./keys";
import { REPORTED, controlStyles, renderControls, type Control, type ControlsContext } from "./controls";
import { renderHeader, headerStyles } from "./header";
import { browserLocalize, localize } from "./localize";
import { renderSchematic, schematicStyles } from "./schematic";
import { buildTiles, renderTiles, tileStyles } from "./tiles";
import type { HomeAssistant, MaicoKwlCardConfig } from "./types";

const CARD_TYPE = "maico-kwl-card";

// The unit applies a change slowly and the integration reports it with its
// next poll (30 s by default), so a change is shown at once and kept for up
// to this long while the unit has not confirmed it yet.
const PENDING_TIMEOUT_MS = 35_000;

// Below this card width the level bar shows icons instead of words.
const NARROW_PX = 400;
const SCHEMATIC_WIDTH = 420;
// How often today's recovered energy is read from the statistics.
const ENERGY_REFRESH_MS = 5 * 60_000;
const SCHEMATIC_MAX_PX = 460;

interface Pending {
  value: string;
  timer: number;
}

export class MaicoKwlCard extends LitElement {
  @property({ attribute: false }) public hass?: HomeAssistant;

  @state() private _config?: MaicoKwlCardConfig;

  private readonly _uid = `kwl${Math.random().toString(36).slice(2, 10)}`;

  @state() private _pending = new Map<Control, Pending>();

  @state() private _messagesExpanded = false;

  /** Rendered width of the card, for the narrow layout. */
  @state() private _width = 0;

  private _resizeObserver?: ResizeObserver;

  /** Heat recovered today in kWh, from the recorder statistics. */
  @state() private _energyToday?: number;

  private _energyFetchedAt = 0;

  public setConfig(config: MaicoKwlCardConfig): void {
    if (config.device_id !== this._config?.device_id) {
      // Another unit: its energy is read anew, not taken from the last one.
      this._energyToday = undefined;
      this._energyFetchedAt = 0;
    }
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

  public connectedCallback(): void {
    super.connectedCallback();
    this._resizeObserver ??= new ResizeObserver(([entry]) => {
      const width = Math.round(entry.contentRect.width);
      // Render in the next frame: a layout change inside the callback would
      // start the observer again ("ResizeObserver loop", reported by Safari).
      if (width !== this._width) requestAnimationFrame(() => (this._width = width));
    });
    this._resizeObserver.observe(this);
  }

  public disconnectedCallback(): void {
    super.disconnectedCallback();
    this._resizeObserver?.disconnect();
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

  protected firstUpdated(): void {
    // Measure right away: the resize observer reports later (in Safari after
    // the first paint), and a narrow card would flash its wide layout.
    const width = Math.round(this.getBoundingClientRect().width);
    if (width) this._width = width;
  }

  protected updated(changed: PropertyValues<this>): void {
    super.updated(changed);
    const inputs = changed.has("hass") || changed.has("_config" as keyof MaicoKwlCard);
    if (inputs && Date.now() - this._energyFetchedAt > ENERGY_REFRESH_MS) {
      this._fetchEnergyToday();
    }
  }

  /** The energy sensor counts up for ever; today's share is its change since midnight. */
  private async _fetchEnergyToday(): Promise<void> {
    // Also without an energy entity: no new lookup on every update.
    this._energyFetchedAt = Date.now();
    const entityId = this._energyEntityId();
    if (!entityId) {
      this._energyToday = undefined;
      return;
    }
    let energy: number | undefined;
    try {
      const result = await this.hass!.callWS<{ change?: number | null }>({
        type: "recorder/statistic_during_period",
        statistic_id: entityId,
        calendar: { period: "day" },
        types: ["change"],
      });
      energy = typeof result.change === "number" ? Math.max(0, result.change) : undefined;
    } catch {
      // No statistics yet (e.g. a new entity): leave the line out.
      energy = undefined;
    }
    // The unit may have changed while the answer was on its way.
    if (this._energyEntityId() === entityId) this._energyToday = energy;
  }

  private _energyEntityId(): string | undefined {
    return (this.hass && this._device())?.entityId(KEY.heatRecoveryEnergy);
  }

  /** Drop the pending change of a control, or only this one if given. */
  private _clearPending(control: Control, only?: Pending): void {
    const pending = this._pending.get(control);
    if (!pending || (only && pending !== only)) return;
    window.clearTimeout(pending.timer);
    this._pending.delete(control);
    this._pending = new Map(this._pending);
  }

  private _controls(device: KwlDevice): ControlsContext {
    return {
      hass: this.hass!,
      device,
      narrow: this._width > 0 && this._width < NARROW_PX,
      moreInfo: (key) => this._moreInfo(device.entityId(key)),
      shown: (control) => this._pending.get(control)?.value ?? REPORTED[control](device),
      pending: (control) => this._pending.has(control),
      change: (control, value, send) => {
        this._clearPending(control);
        if (REPORTED[control](device) === value) {
          // Nothing to wait for, and nothing to undo if HA refuses it.
          send().catch(() => undefined);
          return;
        }
        const pending: Pending = { value, timer: 0 };
        pending.timer = window.setTimeout(() => this._clearPending(control, pending), PENDING_TIMEOUT_MS);
        this._pending = new Map(this._pending).set(control, pending);
        // A refused call undoes its own change only, not a later one.
        send().catch(() => this._clearPending(control, pending));
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
      <ha-card class=${this.hass.themes?.darkMode ? "dark" : ""}>
        ${renderHeader({
          hass: this.hass,
          device,
          expanded: this._messagesExpanded,
          toggle: () => (this._messagesExpanded = !this._messagesExpanded),
          moreInfo: (key) => this._moreInfo(device.entityId(key)),
        })}
        <div class="content">
          ${renderSchematic({
            hass: this.hass,
            device,
            uid: this._uid,
            // The SVG is 420 units wide, drawn into the card minus its padding.
            scale: this._width ? SCHEMATIC_WIDTH / Math.min(SCHEMATIC_MAX_PX, this._width - 32) : 1,
            moreInfo: (key) => this._moreInfo(device.entityId(key)),
          })}
          ${renderTiles(this.hass, buildTiles(this.hass, device, this._energyToday), (entityId) =>
            this._moreInfo(entityId),
          )}
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
    headerStyles,
    schematicStyles,
    tileStyles,
    controlStyles,
    css`
    /* A block, not the default inline: resize observers skip inline boxes. */
    :host {
      display: block;
    }
    ha-card {
      color: var(--primary-text-color);
      --kwl-bus-bg: #dcebf6;
      --kwl-bus-fg: #01497c;
      --kwl-warn-bg: #fff1dc;
      --kwl-warn-fg: #7a4a00;
      --kwl-good: #2e7d32;
      --kwl-moderate: #f9a825;
      --kwl-poor: #c62828;
      --kwl-fault-bg: #fde7e7;
      --kwl-fault-fg: #9b1c1c;
    }
    ha-card.dark {
      --kwl-bus-bg: #123447;
      --kwl-bus-fg: #8fd3f7;
      --kwl-warn-bg: #3b2c12;
      --kwl-warn-fg: #ffcc80;
      --kwl-good: #81c784;
      --kwl-moderate: #ffd54f;
      --kwl-poor: #ef5350;
      --kwl-fault-bg: #4a1c1c;
      --kwl-fault-fg: #ffb4b4;
    }
    .content {
      padding: 16px;
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
