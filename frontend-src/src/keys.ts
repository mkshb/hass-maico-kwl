// The entities the card uses, by their translation_key. The integration
// gives every entity a fixed translation_key (the register key), so the card
// finds them on any unit without knowing entity ids. tests/test_frontend.py
// checks every key here against the integration's strings.json.

export const KEY = {
  // Airflow schematic
  tempOutdoor: "temp_air_intake",
  tempSupply: "temp_supply_air",
  tempExtract: "temp_extract_air",
  tempExhaust: "temp_exhaust_air",
  airflowSupply: "airflow_supply",
  airflowExhaust: "airflow_exhaust",
  fanSpeedSupply: "fan_speed_supply",
  fanSpeedExhaust: "fan_speed_exhaust",
  fanSupplyActive: "fan_supply_active",
  fanExhaustActive: "fan_exhaust_active",
  bypassOpen: "summer_bypass_open",
  ptcHeaterActive: "ptc_heater_active",
  heatRecoveryEfficiency: "heat_recovery_efficiency",
  heatRecoveryPower: "heat_recovery_power",
  // Room values
  roomTempSource: "room_temp_source",
  tempRoom: "temp_room",
  tempRoomExternal: "temp_room_external",
  roomTempBusSent: "room_temp_bus_sent",
  humidityExhaust: "humidity_exhaust",
  humidityBusSent: "humidity_bus_sent",
  airQualityBusSent: "air_quality_bus_sent",
  // Controls
  operatingMode: "operating_mode",
  ventilationLevel: "ventilation_level",
  currentVentLevel: "current_vent_level",
  boost: "boost_ventilation",
  season: "season",
  // Filters
  filterRemainingDevice: "filter_remaining_device",
  filterRemainingOutdoor: "filter_remaining_outdoor",
  filterRemainingRoom: "filter_remaining_room",
  filterRuntimeDevice: "filter_runtime_device",
  filterRuntimeOutdoor: "filter_runtime_outdoor",
  filterRuntimeRoom: "filter_runtime_room",
  filterNextChange: "filter_next_change",
  // Faults and notices
  problem: "problem",
  faultCode: "fault_code",
  noticeCode: "notice_code",
} as const;

// Room sensors the unit reads itself (wired 1-4, EnOcean 0-7).
export const HUMIDITY_SENSOR_KEYS = [
  "humidity_sensor_1", "humidity_sensor_2", "humidity_sensor_3", "humidity_sensor_4",
  "enocean_humidity_id0", "enocean_humidity_id1", "enocean_humidity_id2", "enocean_humidity_id3",
  "enocean_humidity_id4", "enocean_humidity_id5", "enocean_humidity_id6", "enocean_humidity_id7",
] as const;

export const CO2_SENSOR_KEYS = [
  "co2_sensor_1", "co2_sensor_2", "co2_sensor_3", "co2_sensor_4",
  "enocean_co2_id0", "enocean_co2_id1", "enocean_co2_id2", "enocean_co2_id3",
  "enocean_co2_id4", "enocean_co2_id5", "enocean_co2_id6", "enocean_co2_id7",
] as const;

export const VOC_SENSOR_KEYS = [
  "voc_sensor_1", "voc_sensor_2", "voc_sensor_3", "voc_sensor_4",
  "enocean_voc_id0", "enocean_voc_id1", "enocean_voc_id2", "enocean_voc_id3",
  "enocean_voc_id4", "enocean_voc_id5", "enocean_voc_id6", "enocean_voc_id7",
] as const;

export type EntityKey =
  | (typeof KEY)[keyof typeof KEY]
  | (typeof HUMIDITY_SENSOR_KEYS)[number]
  | (typeof CO2_SENSOR_KEYS)[number]
  | (typeof VOC_SENSOR_KEYS)[number];
