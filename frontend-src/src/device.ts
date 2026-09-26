import type { EntityKey } from "./keys";
import type { HassEntityState, HomeAssistant } from "./types";

export const DOMAIN = "maico_kwl";

const MISSING_STATES = new Set(["unavailable", "unknown"]);

/** Ids of all devices that have entities of this integration. */
export function maicoDeviceIds(hass: HomeAssistant): string[] {
  const ids = new Set<string>();
  for (const entry of Object.values(hass.entities)) {
    if (entry.platform === DOMAIN && entry.device_id) ids.add(entry.device_id);
  }
  return [...ids];
}

/**
 * One unit as the card sees it: its entities looked up by translation_key.
 *
 * An entity the unit does not have (a missing accessory, a register the
 * probe left out) is simply absent, and every accessor returns undefined, so
 * the card leaves that part out instead of showing a broken value.
 */
export class KwlDevice {
  private readonly _entityIds = new Map<string, string>();

  constructor(
    private readonly _hass: HomeAssistant,
    public readonly deviceId: string,
  ) {
    for (const entry of Object.values(_hass.entities)) {
      if (entry.platform === DOMAIN && entry.device_id === deviceId && entry.translation_key) {
        this._entityIds.set(entry.translation_key, entry.entity_id);
      }
    }
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

  state(key: EntityKey): string | undefined {
    return this.stateObj(key)?.state;
  }

  number(key: EntityKey): number | undefined {
    const value = Number(this.state(key));
    return this.state(key) === undefined || Number.isNaN(value) ? undefined : value;
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
