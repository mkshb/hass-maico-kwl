import { css, html, nothing, type TemplateResult } from "lit";

import type { KwlDevice } from "./device";
import { CO2_SENSOR_KEYS, HUMIDITY_SENSOR_KEYS, KEY, VOC_SENSOR_KEYS, type EntityKey } from "./keys";
import { localize, type StringKey } from "./localize";
import type { HomeAssistant } from "./types";

// The unit expects a bus value at least every 10 minutes.
const BUS_STALE_MINUTES = 10;

// CO2 levels (ppm) for the air quality dot.
const AIR_GOOD_MAX = 800;
const AIR_MODERATE_MAX = 1400;

export interface Tile {
  label: StringKey;
  /** Entity the value comes from. */
  key: EntityKey;
  /** Entity to open on tap: the source entity for bus values. */
  moreInfo: string | undefined;
  value: string;
  sub?: string;
  bus?: { stale: boolean };
  air?: "good" | "moderate" | "poor";
}

type T = (key: StringKey, values?: Record<string, string | number>) => string;

function friendlyName(hass: HomeAssistant, entityId: string): string {
  const name = hass.states[entityId]?.attributes.friendly_name;
  return typeof name === "string" ? name : entityId;
}

/** A value the integration writes to the unit over the bus, from a HA entity. */
function busTile(
  hass: HomeAssistant,
  device: KwlDevice,
  t: T,
  label: StringKey,
  key: EntityKey,
  now: number,
): Tile | undefined {
  const value = device.format(key);
  const source = device.attribute<string>(key, "source_entity");
  if (value === undefined || !source) return undefined;
  const written = device.attribute<string>(key, "last_written");
  const minutes = written ? Math.floor((now - Date.parse(written)) / 60000) : undefined;
  const stale = minutes === undefined || minutes >= BUS_STALE_MINUTES;
  return {
    label,
    key,
    moreInfo: source,
    value,
    sub: minutes === undefined
      ? t("bus_never")
      : stale
        ? t("bus_stale", { minutes })
        : t("from_source", { name: friendlyName(hass, source) }),
    bus: { stale },
  };
}

/** The highest reading of a group of room sensors (the worst room counts). */
function highestSensor(hass: HomeAssistant, device: KwlDevice, label: StringKey, keys: readonly EntityKey[]): Tile | undefined {
  const present = device.present(keys).filter((key) => device.number(key) !== undefined);
  if (!present.length) return undefined;
  const key = present.reduce((a, b) => (device.number(b)! > device.number(a)! ? b : a));
  const entityId = device.entityId(key)!;
  return {
    label,
    key,
    moreInfo: entityId,
    value: device.format(key)!,
    sub: present.length > 1 ? friendlyName(hass, entityId) : undefined,
  };
}

function plainTile(device: KwlDevice, label: StringKey, key: EntityKey, sub?: string): Tile | undefined {
  const value = device.format(key);
  return value === undefined ? undefined : { label, key, moreInfo: device.entityId(key), value, sub };
}

export function roomTile(hass: HomeAssistant, device: KwlDevice, t: T, now: number): Tile | undefined {
  // The unit regulates on the room temperature from the source set on it.
  switch (device.state(KEY.roomTempSource)) {
    case "bus":
      return busTile(hass, device, t, "tile_room", KEY.roomTempBusSent, now) ?? plainTile(device, "tile_room", KEY.tempRoom);
    case "external":
      return plainTile(device, "tile_room", KEY.tempRoomExternal, t("sub_external_sensor"))
        ?? plainTile(device, "tile_room", KEY.tempRoom);
    default:
      return plainTile(device, "tile_room", KEY.tempRoom);
  }
}

export function humidityTile(hass: HomeAssistant, device: KwlDevice, t: T, now: number): Tile | undefined {
  return busTile(hass, device, t, "tile_humidity", KEY.humidityBusSent, now)
    ?? highestSensor(hass, device, "tile_humidity", HUMIDITY_SENSOR_KEYS)
    ?? plainTile(device, "tile_humidity", KEY.humidityExhaust, t("sub_extract_air"));
}

export function airQualityTile(hass: HomeAssistant, device: KwlDevice, t: T, now: number): Tile | undefined {
  const tile = highestSensor(hass, device, "tile_air_quality", CO2_SENSOR_KEYS)
    ?? highestSensor(hass, device, "tile_air_quality", VOC_SENSOR_KEYS)
    ?? busTile(hass, device, t, "tile_air_quality", KEY.airQualityBusSent, now);
  if (!tile) return undefined;
  const ppm = device.number(tile.key);
  if (ppm !== undefined) {
    tile.air = ppm <= AIR_GOOD_MAX ? "good" : ppm <= AIR_MODERATE_MAX ? "moderate" : "poor";
  }
  return tile;
}

export function heatRecoveryTile(device: KwlDevice): Tile | undefined {
  return plainTile(device, "tile_heat_recovery", KEY.heatRecoveryPower);
}

export function buildTiles(hass: HomeAssistant, device: KwlDevice, now = Date.now()): Tile[] {
  const t: T = (key, values) => localize(hass, key, values);
  return [
    roomTile(hass, device, t, now),
    humidityTile(hass, device, t, now),
    airQualityTile(hass, device, t, now),
    heatRecoveryTile(device),
  ].filter((tile): tile is Tile => tile !== undefined);
}

export function renderTiles(
  hass: HomeAssistant,
  tiles: Tile[],
  moreInfo: (entityId: string | undefined) => void,
): TemplateResult | typeof nothing {
  if (!tiles.length) return nothing;
  const t = (key: StringKey) => localize(hass, key);
  return html`
    <div class="tiles">
      ${tiles.map(
        (tile) => html`
          <button class="tile" type="button" @click=${() => moreInfo(tile.moreInfo)}>
            <span class="tile-label">
              ${t(tile.label)}
              ${tile.bus
                ? html`<span class=${tile.bus.stale ? "badge stale" : "badge"}>${t("bus_badge")}</span>`
                : nothing}
            </span>
            <span class="tile-value">
              ${tile.air
                ? html`<span class=${`dot air-${tile.air}`} title=${t(`air_${tile.air}`)}></span>`
                : nothing}
              ${tile.value}
            </span>
            ${tile.sub
              ? html`<span class=${tile.bus?.stale ? "tile-sub stale" : "tile-sub"}>${tile.sub}</span>`
              : nothing}
          </button>
        `,
      )}
    </div>
  `;
}

export const tileStyles = css`
  .tiles {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    margin-top: 16px;
  }
  .tile {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-height: 72px;
    padding: 10px 12px;
    border: 0;
    border-radius: 10px;
    background: var(--secondary-background-color, #f5f5f5);
    color: var(--primary-text-color);
    font: inherit;
    text-align: left;
    cursor: pointer;
  }
  .tile:focus-visible {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
  }
  .tile-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: var(--secondary-text-color);
  }
  .tile-value {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 18px;
    font-weight: 500;
  }
  .tile-sub {
    overflow: hidden;
    max-width: 100%;
    font-size: 11px;
    color: var(--secondary-text-color);
    white-space: nowrap;
    text-overflow: ellipsis;
  }
  .badge {
    padding: 1px 6px;
    border-radius: 6px;
    background: var(--kwl-bus-bg);
    color: var(--kwl-bus-fg);
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.3px;
  }
  .badge.stale {
    background: var(--kwl-warn-bg);
    color: var(--kwl-warn-fg);
  }
  .tile-sub.stale {
    color: var(--kwl-warn-fg);
  }
  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  .air-good {
    background: var(--kwl-good);
  }
  .air-moderate {
    background: var(--kwl-moderate);
  }
  .air-poor {
    background: var(--kwl-poor);
  }
`;
