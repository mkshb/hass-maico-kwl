import { LitElement, html, nothing } from "lit";
import { property, state } from "lit/decorators.js";

import { DOMAIN } from "./device";
import { localize } from "./localize";
import type { HomeAssistant, MaicoKwlCardConfig } from "./types";

export const EDITOR_TYPE = "maico-kwl-card-editor";

export class MaicoKwlCardEditor extends LitElement {
  @property({ attribute: false }) public hass?: HomeAssistant;

  @state() private _config?: MaicoKwlCardConfig;

  public setConfig(config: MaicoKwlCardConfig): void {
    this._config = config;
  }

  private _schema = [
    { name: "device_id", selector: { device: { filter: { integration: DOMAIN } } } },
  ];

  protected render() {
    if (!this.hass || !this._config) return nothing;
    return html`
      <ha-form
        .hass=${this.hass}
        .data=${this._config}
        .schema=${this._schema}
        .computeLabel=${() => localize(this.hass, "editor_device")}
        @value-changed=${this._valueChanged}
      ></ha-form>
    `;
  }

  private _valueChanged(ev: CustomEvent<{ value: MaicoKwlCardConfig }>): void {
    const config = { ...ev.detail.value };
    if (!config.device_id) delete config.device_id;
    this.dispatchEvent(
      new CustomEvent("config-changed", { detail: { config }, bubbles: true, composed: true }),
    );
  }
}

if (!customElements.get(EDITOR_TYPE)) {
  customElements.define(EDITOR_TYPE, MaicoKwlCardEditor);
}
