import type { EntityKey } from "./keys";
import type { HassEntityState, HomeAssistant } from "./types";

export const DOMAIN = "maico_kwl";

const MISSING_STATES = new Set(["unavailable", "unknown"]);

/**
 * The units a user can switch these sensors to in HA (temperature, duration,
 * volume flow rate), as factors or functions to the unit the card calculates
 * in. The integration reports °C, days and m³/h.
 */
const TO_BASE: Record<string, Record<string, (value: number) => number>> = {
  "°C": { "°C": (v) => v, "°F": (v) => ((v - 32) * 5) / 9, K: (v) => v - 273.15 },
  d: {
    d: (v) => v,
    w: (v) => v * 7,
    h: (v) => v / 24,
    min: (v) => v / 1440,
    s: (v) => v / 86400,
    ms: (v) => v / 86_400_000,
  },
  "m³/h": {
    "m³/h": (v) => v,
    "m³/min": (v) => v * 60,
    "m³/s": (v) => v * 3600,
    "L/h": (v) => v / 1000,
    "L/min": (v) => (v * 60) / 1000,
    "L/s": (v) => (v * 3600) / 1000,
    "mL/s": (v) => (v * 3600) / 1_000_000,
    "ft³/min": (v) => v * 1.699011,
    "gal/min": (v) => v * 0.227125,
  },
};

/**
 * The integration's entities per device, as translation_key -> entity_id.
 * HA hands out a new entities object only when the registry changes, so this
 * is worked out once per registry state instead of on every update.
 */
const registryCache = new WeakMap<object, Map<string, Map<string, string>>>();

function entitiesByDevice(hass: HomeAssistant): Map<string, Map<string, string>> {
  let devices = registryCache.get(hass.entities);
  if (!devices) {
    devices = new Map();
    for (const entry of Object.values(hass.entities)) {
      if (entry.platform !== DOMAIN || !entry.device_id || !entry.translation_key) continue;
      if (!devices.has(entry.device_id)) devices.set(entry.device_id, new Map());
      devices.get(entry.device_id)!.set(entry.translation_key, entry.entity_id);
    }
    registryCache.set(hass.entities, devices);
  }
  return devices;
}

/** Ids of all devices that have entities of this integration. */
export function maicoDeviceIds(hass: HomeAssistant): string[] {
  return [...entitiesByDevice(hass).keys()];
}

/**
 * One unit as the card sees it: its entities looked up by translation_key.
 *
 * An entity the unit does not have (a missing accessory, a register the
 * probe left out) is simply absent, and every accessor returns undefined, so
 * the card leaves that part out instead of showing a broken value.
 */
export class KwlDevice {
  private readonly _entityIds: Map<string, string>;

  constructor(
    private readonly _hass: HomeAssistant,
    public readonly deviceId: string,
  ) {
    this._entityIds = entitiesByDevice(_hass).get(deviceId) ?? new Map();
  }

  /** Every entity id of the unit, for telling whether a hass update matters. */
  get entityIds(): string[] {
    return [...this._entityIds.values()];
  }

  get name(): string {
    const device = this._hass.devices[this.deviceId];
    return device?.name_by_user || device?.name || "Maico KWL";
  }

  entityId(key: EntityKey): string | undefined {
    return this._entityIds.get(key);
  }

  has(key: EntityKey): boolean {
    return this.stateObj(key) !== undefined;
  }

  /** The state object, or undefined if the entity is absent or has no value. */
  stateObj(key: EntityKey): HassEntityState | undefined {
    const entityId = this._entityIds.get(key);
    const stateObj = entityId ? this._hass.states[entityId] : undefined;
    return stateObj && !MISSING_STATES.has(stateObj.state) ? stateObj : undefined;
  }

  /** The state object even when it has no value yet ("unknown"). */
  rawStateObj(key: EntityKey): HassEntityState | undefined {
    const entityId = this._entityIds.get(key);
    return entityId ? this._hass.states[entityId] : undefined;
  }

  state(key: EntityKey): string | undefined {
    return this.stateObj(key)?.state;
  }

  number(key: EntityKey): number | undefined {
    const value = Number(this.state(key));
    return this.state(key) === undefined || Number.isNaN(value) ? undefined : value;
  }

  /**
   * The value in the card's unit (°C, d or m³/h), whatever unit the user
   * set for the entity. Undefined for a unit the card does not know, rather
   * than a wrong number.
   */
  numberIn(key: EntityKey, unit: "°C" | "d" | "m³/h"): number | undefined {
    const value = this.number(key);
    if (value === undefined) return undefined;
    const from = this.attribute<string>(key, "unit_of_measurement");
    if (from === undefined) return value;
    const convert = TO_BASE[unit][from];
    return convert ? convert(value) : undefined;
  }

  isOn(key: EntityKey): boolean | undefined {
    const state = this.state(key);
    return state === undefined ? undefined : state === "on";
  }

  attribute<T = unknown>(key: EntityKey, name: string): T | undefined {
    return this.stateObj(key)?.attributes[name] as T | undefined;
  }

  /** The value as HA shows it: translated, rounded, with unit. */
  format(key: EntityKey): string | undefined {
    const stateObj = this.stateObj(key);
    return stateObj ? this._hass.formatEntityState(stateObj) : undefined;
  }

  /** Keys of a group that this unit has, in the given order. */
  present(keys: readonly EntityKey[]): EntityKey[] {
    return keys.filter((key) => this.has(key));
  }
}
