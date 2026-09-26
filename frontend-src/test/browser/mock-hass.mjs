// Runs in the test page: a stand-in for ha-card and ha-form, a hass object
// built from the fixture, and the card loaded through its own loader.
// Everything the card sends to HA is recorded on window.kwl.

const id = new URLSearchParams(location.search).get("fixture");
const fixture = await (await fetch(`/fixture/${id}.json`)).json();

if (!customElements.get("ha-card")) {
  customElements.define("ha-card", class extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: "open" }).innerHTML =
        "<style>:host { display: block; border-radius: 12px; border: 1px solid var(--divider-color);" +
        " background: var(--card-background-color); color: var(--primary-text-color); }</style><slot></slot>";
    }
  });
}
if (!customElements.get("ha-form")) {
  // Records what the editor hands to HA's form.
  customElements.define("ha-form", class extends HTMLElement {});
}

for (const [name, value] of Object.entries(fixture.theme)) {
  document.documentElement.style.setProperty(name, value);
}

const kwl = {
  serviceCalls: [],
  wsCalls: [],
  moreInfo: [],
  pending: 0,
  failServices: fixture.failServices ?? false,
  energyToday: fixture.energyToday,
  states: structuredClone(fixture.states),
  hass: undefined,
  card: undefined,
};
window.kwl = kwl;

document.addEventListener("hass-more-info", (ev) => kwl.moreInfo.push(ev.detail.entityId));

const number = (value, digits) =>
  new Intl.NumberFormat(fixture.language, { minimumFractionDigits: digits, maximumFractionDigits: digits })
    .format(value);

// A fixture key is a translation_key, or "key@name" for the same kind of
// entity on another unit.
const entityId = (key) => `sensor.maico_${key.replace("@", "_")}`;
const keyOf = (stateObj) =>
  Object.keys(kwl.states).find((key) => entityId(key) === stateObj.entity_id) ?? "";

// Like HA: a new hass object on every change, but the registry, locale and
// theme objects stay the same, and so does the state object of every entity
// that did not change.
const locale = { language: fixture.language };
const themes = { darkMode: fixture.dark };
let previous = { entities: undefined, entityKeys: "", states: {}, specs: {} };

/** A fresh hass object, as HA hands the card a new one on every change. */
function buildHass() {
  const entities = {};
  const states = {};
  const specs = {};
  for (const [key, spec] of Object.entries(kwl.states)) {
    if (spec === null) continue;
    const id = entityId(key);
    entities[id] = {
      entity_id: id,
      platform: "maico_kwl",
      device_id: spec.device ?? "unit",
      translation_key: key.split("@")[0],
    };
    specs[id] = JSON.stringify(spec);
    if (previous.specs[id] === specs[id]) {
      states[id] = previous.states[id];
      continue;
    }
    states[id] = {
      entity_id: id,
      state: spec.state,
      attributes: {
        friendly_name: spec.name ?? key,
        ...(spec.unit ? { unit_of_measurement: spec.unit } : {}),
        ...(spec.options ? { options: spec.options } : {}),
        ...spec.attributes,
      },
      last_changed: new Date().toISOString(),
      last_updated: new Date().toISOString(),
    };
  }
  for (const [id, name] of Object.entries(fixture.sources)) {
    states[id] = previous.states[id] ?? { entity_id: id, state: "1", attributes: { friendly_name: name } };
  }
  const entityKeys = JSON.stringify(entities);
  const sameRegistry = entityKeys === previous.entityKeys;
  previous = { entities: sameRegistry ? previous.entities : entities, entityKeys, states, specs };
  const specOf = (stateObj) => kwl.states[keyOf(stateObj)] ?? {};
  const kindOf = (stateObj) => keyOf(stateObj).split("@")[0];
  const track = async (promise) => {
    kwl.pending++;
    try {
      return await promise;
    } finally {
      kwl.pending--;
    }
  };
  return {
    language: fixture.language,
    locale,
    themes,
    entities: previous.entities,
    states,
    devices: fixture.devices,
    formatEntityState(stateObj, value = stateObj.state) {
      const spec = specOf(stateObj);
      const label = fixture.labels[kindOf(stateObj)]?.[value];
      if (label) return label;
      if (spec.date) {
        return new Intl.DateTimeFormat(fixture.language, { dateStyle: "medium" }).format(new Date(value));
      }
      if (spec.unit) {
        const text = number(Number(value), spec.precision ?? 0);
        return spec.unit === "%" ? `${text} %` : `${text} ${spec.unit}`;
      }
      return value;
    },
    formatEntityAttributeValue(stateObj, attribute, value) {
      return fixture.attributeLabels[kindOf(stateObj)]?.[attribute]?.[value] ?? String(value);
    },
    callService(domain, service, data) {
      kwl.serviceCalls.push({ domain, service, data });
      // failServices: true refuses every call, a number that many first calls,
      // after failDelay ms (so a later call can overtake it).
      const fail = kwl.failServices === true || kwl.failServices-- > 0;
      if (!fail) return track(Promise.resolve());
      return track(
        new Promise((_, reject) => setTimeout(() => reject(new Error("refused")), fixture.failDelay ?? 0)),
      );
    },
    callWS(message) {
      kwl.wsCalls.push(message);
      if (message.type === "recorder/statistic_during_period") {
        return track(
          kwl.energyToday === undefined
            ? Promise.reject(new Error("no statistics"))
            : Promise.resolve({ change: kwl.energyToday }),
        );
      }
      return track(Promise.reject(new Error(`unknown command ${message.type}`)));
    },
  };
}

/** Change entities the way HA reports them: a new hass object. */
kwl.update = (patch) => {
  for (const [key, spec] of Object.entries(patch)) {
    kwl.states[key] = spec === null ? null : { ...kwl.states[key], ...spec };
  }
  kwl.hass = buildHass();
  kwl.card.hass = kwl.hass;
};

customElements.define("home-assistant", class extends HTMLElement {});
await import("/frontend/maico-kwl-card.js");
await customElements.whenDefined("maico-kwl-card");

kwl.hass = buildHass();
const card = document.createElement("maico-kwl-card");
card.style.width = `${fixture.width}px`;
card.setConfig({ type: "custom:maico-kwl-card", ...fixture.config });
card.hass = kwl.hass;
kwl.card = card;
document.getElementById("frame").appendChild(card);
await document.fonts.ready;
kwl.ready = true;
