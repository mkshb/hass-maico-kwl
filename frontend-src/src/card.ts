import { LitElement, css, html, nothing } from "lit";
import { property, state } from "lit/decorators.js";

import type { HomeAssistant, MaicoKwlCardConfig } from "./types";

export const DOMAIN = "maico_kwl";
const CARD_TYPE = "maico-kwl-card";

export class MaicoKwlCard extends LitElement {
  @property({ attribute: false }) public hass?: HomeAssistant;

  @state() private _config?: MaicoKwlCardConfig;

  public setConfig(config: MaicoKwlCardConfig): void {
    this._config = config;
  }

  public getCardSize(): number {
    return 4;
  }

  public static getStubConfig(): Omit<MaicoKwlCardConfig, "type"> {
    return {};
  }

  private _deviceId(): string | undefined {
    if (this._config?.device_id) return this._config.device_id;
    return Object.values(this.hass!.entities).find(
      (entry) => entry.platform === DOMAIN && entry.device_id,
    )?.device_id;
  }

  protected render() {
    if (!this.hass || !this._config) return nothing;
    const deviceId = this._deviceId();
    const device = deviceId ? this.hass.devices[deviceId] : undefined;
    const entities = Object.values(this.hass.entities).filter(
      (entry) => entry.platform === DOMAIN && entry.device_id === deviceId && !entry.hidden,
    );
    return html`
      <ha-card .header=${device?.name_by_user || device?.name || "Maico KWL"}>
        <div class="content">
          ${entities.length
            ? html`<table>
                ${entities.map((entry) => {
                  const stateObj = this.hass!.states[entry.entity_id];
                  return html`<tr>
                    <td>${stateObj?.attributes.friendly_name ?? entry.entity_id}</td>
                    <td class="state">
                      ${stateObj ? this.hass!.formatEntityState(stateObj) : ""}
                    </td>
                  </tr>`;
                })}
              </table>`
            : html`<p class="empty">No Maico KWL unit found.</p>`}
        </div>
      </ha-card>
    `;
  }

  static styles = css`
    .content {
      padding: 0 16px 16px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
    }
    td {
      padding: 4px 0;
      border-bottom: 1px solid var(--divider-color);
    }
    td.state {
      text-align: right;
      color: var(--secondary-text-color);
    }
    .empty {
      color: var(--secondary-text-color);
    }
  `;
}

declare global {
  interface Window {
    customCards?: { type: string; name: string; description: string }[];
  }
}

if (!customElements.get(CARD_TYPE)) {
  customElements.define(CARD_TYPE, MaicoKwlCard);
  window.customCards = window.customCards ?? [];
  window.customCards.push({
    type: CARD_TYPE,
    name: "Maico KWL",
    description: "Airflow, temperatures and controls of a Maico ventilation unit.",
  });
}
