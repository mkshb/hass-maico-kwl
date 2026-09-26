// The parts of the frontend's hass object the card uses.

export interface HassEntityRegistryEntry {
  entity_id: string;
  device_id?: string;
  platform: string;
  translation_key?: string;
  hidden?: boolean;
}

export interface HassDevice {
  id: string;
  name: string | null;
  name_by_user: string | null;
}

export interface HassEntityState {
  entity_id: string;
  state: string;
  attributes: Record<string, unknown>;
  last_changed: string;
  last_updated: string;
}

export interface HomeAssistant {
  states: Record<string, HassEntityState>;
  entities: Record<string, HassEntityRegistryEntry>;
  devices: Record<string, HassDevice>;
  language: string;
  locale?: { language: string };
  themes?: { darkMode?: boolean };
  formatEntityState(state: HassEntityState, value?: string): string;
  formatEntityAttributeValue(state: HassEntityState, attribute: string, value?: unknown): string;
  callService(domain: string, service: string, data?: Record<string, unknown>): Promise<unknown>;
}

export interface MaicoKwlCardConfig {
  type: string;
  device_id?: string;
}
