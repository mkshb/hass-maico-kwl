import { LitElement, css, html, nothing } from "lit";
import { property, state } from "lit/decorators.js";

import { KwlDevice, maicoDeviceIds } from "./device";
import { CO2_SENSOR_KEYS, HUMIDITY_SENSOR_KEYS, KEY, VOC_SENSOR_KEYS, type EntityKey } from "./keys";
import { browserLocalize, localize, type StringKey } from "./localize";
import type { HomeAssistant, MaicoKwlCardConfig } from "./types";

const CARD_TYPE = "maico-kwl-card";

// Until the real layout lands, the card lists what it resolved, grouped the
// way the layout will use it. Entities the unit lacks do not show up.
const GROUPS: [StringKey, readonly EntityKey[]][] = [
  [
    "group_airflow",
    [
      KEY.tempOutdoor, KEY.tempSupply, KEY.tempExtract, KEY.tempExhaust,
      KEY.airflowSupply, KEY.airflowExhaust, KEY.fanSpeedSupply, KEY.fanSpeedExhaust,
      KEY.bypassOpen, KEY.ptcHeaterActive, KEY.heatRecoveryEfficiency, KEY.heatRecoveryPower,
    ],
  ],
  [
    "group_room",
    [
      KEY.roomTempSource, KEY.tempRoom, KEY.tempRoomExternal, KEY.roomTempBusSent,
      KEY.humidityExhaust, KEY.humidityBusSent, KEY.airQualityBusSent,
      ...HUMIDITY_SENSOR_KEYS, ...CO2_SENSOR_KEYS, ...VOC_SENSOR_KEYS,
    ],
  ],
  ["group_controls", [KEY.operatingMode, KEY.ventilationLevel, KEY.currentVentLevel, KEY.boost, KEY.season]],
  [
    "group_filters",
    [KEY.filterRemainingDevice, KEY.filterRemainingOutdoor, KEY.filterRemainingRoom, KEY.filterNextChange],
  ],
  ["group_status", [KEY.problem, KEY.faultCode, KEY.noticeCode]],
];

export class MaicoKwlCard extends LitElement {
  @property({ attribute: false }) public hass?: HomeAssistant;

  @state() private _config?: MaicoKwlCardConfig;

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
      <ha-card .header=${device.name}>
        <div class="content">
          ${GROUPS.map(([title, keys]) => {
            const present = device.present(keys);
            if (!present.length) return nothing;
            return html`
              <h3>${localize(this.hass, title)}</h3>
              <table>
                ${present.map(
                  (key) => html`<tr>
                    <td>${device.stateObj(key)!.attributes.friendly_name ?? key}</td>
                    <td class="state">${device.format(key)}</td>
                  </tr>`,
                )}
              </table>
            `;
          })}
        </div>
      </ha-card>
    `;
  }

  static styles = css`
    .content {
      padding: 0 16px 16px;
    }
    h3 {
      margin: 16px 0 4px;
      font-size: 14px;
      font-weight: 500;
      color: var(--secondary-text-color);
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
      padding: 16px;
      margin: 0;
      color: var(--secondary-text-color);
    }
  `;
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
