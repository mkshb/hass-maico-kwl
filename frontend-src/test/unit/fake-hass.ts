// A minimal hass object for the pure functions: entities of one unit, keyed
// by translation_key, with states and attributes.

import type { HomeAssistant } from "../../src/types.ts";

export interface Spec {
  state: string;
  attributes?: Record<string, unknown>;
}

export function fakeHass(specs: Record<string, Spec>, language = "en"): HomeAssistant {
  const entities: HomeAssistant["entities"] = {};
  const states: HomeAssistant["states"] = {};
  for (const [key, spec] of Object.entries(specs)) {
    const entityId = `sensor.maico_${key}`;
    entities[entityId] = { entity_id: entityId, platform: "maico_kwl", device_id: "unit", translation_key: key };
    states[entityId] = {
      entity_id: entityId,
      state: spec.state,
      attributes: { friendly_name: key, ...spec.attributes },
      last_changed: "",
      last_updated: "",
    };
  }
  states["sensor.source"] = {
    entity_id: "sensor.source",
    state: "1",
    attributes: { friendly_name: "Living room" },
    last_changed: "",
    last_updated: "",
  };
  return {
    language,
    locale: { language },
    entities,
    states,
    devices: { unit: { id: "unit", name: "Maico KWL", name_by_user: null } },
    formatEntityState: (stateObj, value) => value ?? stateObj.state,
    formatEntityAttributeValue: (_stateObj, _attribute, value) => `label:${String(value)}`,
    callService: async () => undefined,
    callWS: async () => ({}) as never,
  };
}
