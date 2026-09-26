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
  },
} as const;

export type StringKey = keyof (typeof STRINGS)["en"];

export function localize(hass: HomeAssistant | undefined, key: StringKey): string {
  const language = (hass?.locale?.language ?? hass?.language ?? "en").split("-")[0];
  const strings: Record<StringKey, string> =
    language in STRINGS ? STRINGS[language as keyof typeof STRINGS] : STRINGS.en;
  return strings[key];
}

/** For the card picker, before any hass object exists. */
export function browserLocalize(key: StringKey): string {
  const language = navigator.language.split("-")[0];
  return (language in STRINGS ? STRINGS[language as keyof typeof STRINGS] : STRINGS.en)[key];
}
