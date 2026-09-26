// A unit on a cold day with the bypass closed: the airflow colours show the
// heat exchange best. Room values come over the bus from HA entities.
// Keys are the entities' translation_keys, as the card looks them up.

const MINUTE = 60_000;

// The browser clock is frozen here, so ages ("2 min ago") never drift.
// Explicit offset: a naive time would be read in the host's time zone.
export const FIXED_TIME = Date.parse("2026-01-15T10:00:00+01:00");

export function unitStates(now = FIXED_TIME) {
  const written = new Date(now - 2 * MINUTE).toISOString();
  return {
    temp_air_intake: { state: "2.0", unit: "°C", precision: 1 },
    temp_supply_air: { state: "18.6", unit: "°C", precision: 1 },
    temp_extract_air: { state: "22.4", unit: "°C", precision: 1 },
    temp_exhaust_air: { state: "5.9", unit: "°C", precision: 1 },
    airflow_supply: { state: "160", unit: "m³/h", precision: 0 },
    airflow_exhaust: { state: "160", unit: "m³/h", precision: 0 },
    fan_speed_supply: { state: "1690", unit: "rpm", precision: 0 },
    fan_speed_exhaust: { state: "1540", unit: "rpm", precision: 0 },
    fan_supply_active: { state: "on" },
    fan_exhaust_active: { state: "on" },
    summer_bypass_open: { state: "off" },
    heat_recovery_efficiency: { state: "81.3", unit: "%", precision: 0 },
    heat_recovery_power: { state: "903", unit: "W", precision: 0 },
    heat_recovery_energy: { state: "412.6", unit: "kWh", precision: 2 },
    room_temp_source: { state: "bus", options: ["comfort_bde", "external", "internal", "bus"] },
    temp_room: { state: "21.6", unit: "°C", precision: 1 },
    room_temp_bus_sent: {
      state: "21.8", unit: "°C", precision: 1,
      attributes: { source_entity: "sensor.living_room_temperature", last_written: written },
    },
    humidity_exhaust: { state: "41", unit: "%", precision: 0 },
    absolute_humidity_extract: { state: "8.1", unit: "g/m³", precision: 1 },
    season: { state: "winter", options: ["winter", "summer"] },
    humidity_bus_sent: {
      state: "44", unit: "%", precision: 0,
      attributes: { source_entity: "sensor.bathroom_humidity", last_written: written },
    },
    air_quality_bus_sent: {
      state: "640", unit: "ppm", precision: 0,
      attributes: { source_entity: "sensor.living_room_co2", last_written: written },
    },
    operating_mode: {
      state: "auto_sensor",
      options: ["off", "manual", "auto_time", "auto_sensor", "eco_supply_air", "eco_exhaust_air"],
    },
    ventilation_level: {
      state: "nominal",
      options: ["off", "humidity_protection", "reduced", "nominal", "intensive"],
    },
    current_vent_level: { state: "nominal" },
    boost_ventilation: { state: "off" },
    off_lock: { state: "off" },
    filter_remaining_device: { state: "212", unit: "d", precision: 0 },
    filter_runtime_device: { state: "12", unit: "mo", precision: 0 },
    filter_next_change: { state: "2027-04-26", date: true },
    notice_code: { state: "0", attributes: { active: [] } },
    fault_code: { state: "0", attributes: { active: [] } },
  };
}

// Source entities of the bus values, by their friendly names.
export const SOURCES = {
  "sensor.living_room_temperature": "Living room temperature",
  "sensor.bathroom_humidity": "Bathroom humidity",
  "sensor.living_room_co2": "Living room CO2",
};

// Home Assistant's default theme colours.
export const THEMES = {
  light: {
    "--primary-text-color": "#212121",
    "--secondary-text-color": "#727272",
    "--disabled-text-color": "#bdbdbd",
    "--primary-color": "#03a9f4",
    "--text-primary-color": "#ffffff",
    "--card-background-color": "#ffffff",
    "--primary-background-color": "#fafafa",
    "--secondary-background-color": "#e5e5e5",
    "--divider-color": "rgba(0, 0, 0, 0.12)",
  },
  dark: {
    "--primary-text-color": "#e1e1e1",
    "--secondary-text-color": "#9b9b9b",
    "--disabled-text-color": "#6f6f6f",
    "--primary-color": "#03a9f4",
    "--text-primary-color": "#ffffff",
    "--card-background-color": "#1c1c1c",
    "--primary-background-color": "#111111",
    "--secondary-background-color": "#282828",
    "--divider-color": "rgba(225, 225, 225, 0.12)",
  },
};

// Heat recovered today, as the recorder statistics report it.
export const ENERGY_TODAY_KWH = 12.4;
