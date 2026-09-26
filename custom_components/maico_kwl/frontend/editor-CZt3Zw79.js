import{_ as e,n as t,r as i,i as a,D as s,A as o,l as d,b as c}from"./card-CDJrFJJs.js";const r="maico-kwl-card-editor";class MaicoKwlCardEditor extends a{constructor(){super(...arguments),this._schema=[{name:"device_id",selector:{device:{filter:{integration:s}}}}]}setConfig(e){this._config=e}render(){return this.hass&&this._config?c`
      <ha-form
        .hass=${this.hass}
        .data=${this._config}
        .schema=${this._schema}
        .computeLabel=${()=>d(this.hass,"editor_device")}
        @value-changed=${this._valueChanged}
      ></ha-form>
    `:o}_valueChanged(e){const t={...e.detail.value};t.device_id||delete t.device_id,this.dispatchEvent(new CustomEvent("config-changed",{detail:{config:t},bubbles:!0,composed:!0}))}}e([t({attribute:!1})],MaicoKwlCardEditor.prototype,"hass",void 0),e([i()],MaicoKwlCardEditor.prototype,"_config",void 0),customElements.get(r)||customElements.define(r,MaicoKwlCardEditor);export{r as EDITOR_TYPE,MaicoKwlCardEditor};
