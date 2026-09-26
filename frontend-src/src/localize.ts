import type { HomeAssistant } from "./types";

const STRINGS = {
  en: {
    card_name: "Maico KWL",
    card_description: "Airflow, temperatures and controls of a Maico ventilation unit.",
    no_device: "No Maico KWL unit found.",
    device_missing: "The selected unit no longer exists.",
    editor_device: "Unit",
    group_airflow: "Airflow",
    group_room: "Room",
    group_controls: "Controls",
    group_filters: "Filters",
    group_status: "Status",
    outdoor_air: "Outdoor air",
    supply_air: "Supply air",
    extract_air: "Extract air",
    exhaust_air: "Exhaust air",
    bypass_open: "Bypass open",
    bypass_closed: "Bypass closed",
    heat_recovery: "Heat recovery",
    fan_off: "off",
    ptc_heater: "PTC heater",
    tile_room: "Room",
    tile_humidity: "Humidity",
    tile_air_quality: "Air quality",
    tile_heat_recovery: "Heat recovery",
    bus_badge: "BUS",
    from_source: "from {name}",
    bus_stale: "no new value for {minutes} min",
    bus_never: "no value sent yet",
    sub_extract_air: "extract air",
    sub_external_sensor: "external sensor",
    air_good: "good",
    air_moderate: "moderate",
    air_poor: "poor",
  },
  de: {
    card_name: "Maico KWL",
    card_description: "Luftströme, Temperaturen und Bedienung eines Maico-Lüftungsgeräts.",
    no_device: "Kein Maico-KWL-Gerät gefunden.",
    device_missing: "Das gewählte Gerät gibt es nicht mehr.",
    editor_device: "Gerät",
    group_airflow: "Luftstrom",
    group_room: "Raum",
    group_controls: "Bedienung",
    group_filters: "Filter",
    group_status: "Status",
    outdoor_air: "Außenluft",
    supply_air: "Zuluft",
    extract_air: "Abluft",
    exhaust_air: "Fortluft",
    bypass_open: "Bypass offen",
    bypass_closed: "Bypass zu",
    heat_recovery: "Rückgewinnung",
    fan_off: "aus",
    ptc_heater: "PTC-Heizregister",
    tile_room: "Raum",
    tile_humidity: "Feuchte",
    tile_air_quality: "Luftgüte",
    tile_heat_recovery: "Rückgewinnung",
    bus_badge: "BUS",
    from_source: "von {name}",
    bus_stale: "seit {minutes} min kein neuer Wert",
    bus_never: "noch kein Wert gesendet",
    sub_extract_air: "Abluft",
    sub_external_sensor: "externer Fühler",
    air_good: "gut",
    air_moderate: "mäßig",
    air_poor: "schlecht",
  },
} as const;

export type StringKey = keyof (typeof STRINGS)["en"];

export function localize(
  hass: HomeAssistant | undefined,
  key: StringKey,
  values: Record<string, string | number> = {},
): string {
  const language = (hass?.locale?.language ?? hass?.language ?? "en").split("-")[0];
  const strings: Record<StringKey, string> =
    language in STRINGS ? STRINGS[language as keyof typeof STRINGS] : STRINGS.en;
  return strings[key].replace(/\{(\w+)\}/g, (match, name: string) =>
    name in values ? String(values[name]) : match,
  );
}

/** For the card picker, before any hass object exists. */
export function browserLocalize(key: StringKey): string {
  const language = navigator.language.split("-")[0];
  return (language in STRINGS ? STRINGS[language as keyof typeof STRINGS] : STRINGS.en)[key];
}
