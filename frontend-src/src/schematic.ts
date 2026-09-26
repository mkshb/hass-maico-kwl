import { css, html, nothing, svg, type SVGTemplateResult, type TemplateResult } from "lit";

import { temperatureColor, temperatureSteps } from "./colors";
import type { KwlDevice } from "./device";
import { KEY, type EntityKey } from "./keys";
import { localize } from "./localize";
import type { HomeAssistant } from "./types";

// Layout in SVG units: outdoor air runs left to right on the top lane,
// extract air right to left on the bottom lane, the heat exchanger sits
// between them and the summer bypass arcs over it.
const TOP = 62;
const BOTTOM = 142;
const BOX_LEFT = 160;
const BOX_RIGHT = 260;
const BYPASS_FROM = 96;
const BYPASS_TO = 324;
const BYPASS_PATH = `M${BYPASS_FROM} ${TOP} C 128 ${TOP}, 128 22, 162 22 L 258 22 C 292 22, 292 ${TOP}, ${BYPASS_TO} ${TOP}`;
const SUPPLY_FAN_X = 340;
const EXHAUST_FAN_X = 80;
const PTC_X = 58;

// Air sheen: one soft sweep per this many seconds at this volume flow.
const SHEEN_SECONDS = 4.5;
const SHEEN_REFERENCE_FLOW = 180;

export interface SchematicContext {
  hass: HomeAssistant;
  device: KwlDevice;
  /** Unique per card, for ids inside the SVG. */
  uid: string;
  /**
   * How much the SVG is shrunk on screen (1 at full size, 1.5 at two thirds).
   * Text grows by it, so it stays readable on a narrow card.
   */
  scale: number;
  moreInfo: (key: EntityKey) => void;
}

export function renderSchematic(ctx: SchematicContext): TemplateResult {
  const { hass, device, uid } = ctx;
  // Font sizes in SVG units, at least the given screen size in px.
  const f = Math.max(1, ctx.scale);
  const size = {
    small: Math.max(12, 11 * f),
    value: Math.max(20, 17 * f),
    fan: Math.max(12, 11.5 * f),
    bypass: Math.max(11, 10.5 * f),
    efficiency: Math.max(18, 15 * f),
  };
  const compact = f > 1.15;
  const dotRadius = Math.max(4, 3.2 * f);
  // The names under the lower temperatures move down as the text grows.
  const bottomNameY = 176 + Math.max(18, size.small * 1.25);
  const dark = hass.themes?.darkMode ?? false;
  const t = (key: Parameters<typeof localize>[1]) => localize(hass, key);

  const outdoor = device.number(KEY.tempOutdoor);
  const supply = device.number(KEY.tempSupply);
  const extract = device.number(KEY.tempExtract);
  const exhaust = device.number(KEY.tempExhaust);

  const hasBypass = device.has(KEY.bypassOpen);
  const bypassOpen = device.isOn(KEY.bypassOpen) ?? false;
  const supplyRunning = device.isOn(KEY.fanSupplyActive) ?? (device.number(KEY.airflowSupply) ?? 0) > 0;
  const exhaustRunning = device.isOn(KEY.fanExhaustActive) ?? (device.number(KEY.airflowExhaust) ?? 0) > 0;

  const topSteps = temperatureSteps(outdoor, supply, dark);
  const bottomSteps = temperatureSteps(exhaust, extract, dark);
  const outdoorColor = temperatureColor(outdoor, dark);
  const supplyColor = temperatureColor(supply, dark);
  const exhaustColor = temperatureColor(exhaust, dark);
  const extractColor = temperatureColor(extract, dark);

  const topTube = bypassOpen
    ? `M20 ${TOP} L${BYPASS_FROM} ${TOP} M${BYPASS_TO} ${TOP} L392 ${TOP}`
    : `M20 ${TOP} L392 ${TOP}`;
  const bottomTube = `M400 ${BOTTOM} L28 ${BOTTOM}`;

  const sheen = (flow: number | undefined) =>
    `${Math.min(12, Math.max(2, (SHEEN_SECONDS * SHEEN_REFERENCE_FLOW) / Math.max(flow ?? SHEEN_REFERENCE_FLOW, 1))).toFixed(2)}s`;

  const clickable = (key: EntityKey, content: SVGTemplateResult, label: string) =>
    device.entityId(key)
      ? svg`<g class="clickable" role="button" tabindex="0" aria-label=${label}
          @click=${() => ctx.moreInfo(key)}
          @keydown=${(ev: KeyboardEvent) => {
            if (ev.key === "Enter" || ev.key === " ") {
              ev.preventDefault();
              ctx.moreInfo(key);
            }
          }}>${content}</g>`
      : content;

  const temperature = (
    key: EntityKey,
    name: string,
    value: number | undefined,
    color: string,
    side: "left" | "right",
    nameY: number,
    valueY: number,
  ) => {
    if (value === undefined) return nothing;
    const formatted = device.format(key)!;
    const left = side === "left";
    return clickable(
      key,
      svg`
        <text class="name" x=${left ? 20 : 400} y=${nameY} text-anchor=${left ? "start" : "end"}
          style=${`font-size: ${size.small}px`}>${name}</text>
        <circle cx=${left ? 20 + dotRadius : 400 - dotRadius} cy=${valueY - size.value * 0.35} r=${dotRadius}
          style=${`fill: ${color}`}></circle>
        <text class="value" x=${left ? 26 + 2 * dotRadius : 394 - 2 * dotRadius} y=${valueY}
          text-anchor=${left ? "start" : "end"} style=${`font-size: ${size.value}px`}>${formatted}</text>
      `,
      `${name} ${formatted}`,
    );
  };

  const fan = (
    x: number,
    y: number,
    running: boolean,
    speedKey: EntityKey,
    flowKey: EntityKey,
    /** Baseline of the lower text line. */
    lastLineY: number,
  ) => {
    const lineGap = size.small * 1.2;
    const rpm = device.number(speedKey);
    const turn = rpm && rpm > 0 ? `${(4000 / rpm).toFixed(2)}s` : "2s";
    const speed = running ? device.format(speedKey) : t("fan_off");
    const flow = running ? device.format(flowKey) : undefined;
    return clickable(
      speedKey,
      svg`
        <circle class="fan-housing" cx=${x} cy=${y} r="13"></circle>
        <g class=${running ? "rotor spinning" : "rotor"} style=${`animation-duration: ${turn}`}>
          <circle cx=${x} cy=${y} r="13" fill="none" stroke="none"></circle>
          ${[0, 120, 240].map(
            (angle) =>
              svg`<ellipse cx=${x} cy=${y - 6} rx="3" ry="5.5" transform=${`rotate(${angle} ${x} ${y})`}></ellipse>`,
          )}
        </g>
        ${speed
          ? svg`<text class="fan-speed" x=${x} y=${lastLineY - lineGap} text-anchor="middle"
              style=${`font-size: ${size.fan}px`}>${speed}</text>`
          : nothing}
        ${flow
          ? svg`<text class="small" x=${x} y=${lastLineY} text-anchor="middle"
              style=${`font-size: ${size.small}px`}>${flow}</text>`
          : nothing}
      `,
      `${speed ?? ""} ${flow ?? ""}`,
    );
  };

  const ptc = () => {
    if (!device.has(KEY.ptcHeaterActive)) return nothing;
    const active = device.isOn(KEY.ptcHeaterActive) ?? false;
    return clickable(
      KEY.ptcHeaterActive,
      svg`<g class=${active ? "ptc active" : "ptc"}>
        <rect x=${PTC_X - 11} y=${TOP - 9} width="22" height="18" rx="4"></rect>
        <path d=${`M${PTC_X - 7} ${TOP} l3 -4 l4 8 l4 -8 l3 4`}></path>
      </g>`,
      t("ptc_heater"),
    );
  };

  const efficiency = device.format(KEY.heatRecoveryEfficiency);

  return html`
    <svg class="schematic" viewBox="0 -14 420 214" role="img"
      aria-label=${[t("outdoor_air"), t("supply_air"), t("extract_air"), t("exhaust_air")].join(", ")}>
      <defs>
        <linearGradient id=${`${uid}-top`} gradientUnits="userSpaceOnUse" x1=${BOX_LEFT} y1="0" x2=${BOX_RIGHT} y2="0">
          ${topSteps.map((color, i) => svg`<stop offset=${i / (topSteps.length - 1)} style=${`stop-color: ${color}`}></stop>`)}
        </linearGradient>
        <linearGradient id=${`${uid}-bottom`} gradientUnits="userSpaceOnUse" x1=${BOX_LEFT} y1="0" x2=${BOX_RIGHT} y2="0">
          ${bottomSteps.map((color, i) => svg`<stop offset=${i / (bottomSteps.length - 1)} style=${`stop-color: ${color}`}></stop>`)}
        </linearGradient>
        <linearGradient id=${`${uid}-sheen`}>
          <stop offset="0" stop-color="#000"></stop>
          <stop offset="0.5" stop-color="#fff"></stop>
          <stop offset="1" stop-color="#000"></stop>
        </linearGradient>
        <mask id=${`${uid}-sheen-right`} maskUnits="userSpaceOnUse" x="0" y="-14" width="420" height="214">
          <rect class="sheen" x="-140" y="-14" width="140" height="214" fill=${`url(#${uid}-sheen)`}
            style=${`animation-duration: ${sheen(device.number(KEY.airflowSupply))}`}></rect>
        </mask>
        <mask id=${`${uid}-sheen-left`} maskUnits="userSpaceOnUse" x="0" y="-14" width="420" height="214">
          <rect class="sheen reverse" x="-140" y="-14" width="140" height="214" fill=${`url(#${uid}-sheen)`}
            style=${`animation-duration: ${sheen(device.number(KEY.airflowExhaust))}`}></rect>
        </mask>
      </defs>

      <rect class="exchanger" x=${BOX_LEFT} y="34" width=${BOX_RIGHT - BOX_LEFT} height="136" rx="12"></rect>
      <line class="exchanger-line" x1=${BOX_LEFT} y1="34" x2=${BOX_RIGHT} y2="170"></line>
      <line class="exchanger-line" x1=${BOX_RIGHT} y1="34" x2=${BOX_LEFT} y2="170"></line>

      ${hasBypass
        ? clickable(
            KEY.bypassOpen,
            svg`
              <path class=${bypassOpen ? "tube" : "bypass-closed"} d=${BYPASS_PATH}
                style=${bypassOpen ? `stroke: ${outdoorColor}` : ""}></path>
              <text class=${bypassOpen ? "bypass-label open" : "bypass-label"} x="210" y="6" text-anchor="middle"
                style=${`font-size: ${size.bypass}px`}>
                ${t(bypassOpen ? "bypass_open" : "bypass_closed")}
              </text>`,
            t(bypassOpen ? "bypass_open" : "bypass_closed"),
          )
        : nothing}

      <path class="tube" d=${topTube} stroke=${`url(#${uid}-top)`}></path>
      ${bypassOpen ? svg`<path class="passage" d=${`M${BYPASS_FROM} ${TOP} L${BYPASS_TO} ${TOP}`}></path>` : nothing}
      <path class="tube" d=${bottomTube} stroke=${`url(#${uid}-bottom)`}></path>
      <polygon points="396,57 406,62 396,67" style=${`fill: ${supplyColor}`}></polygon>
      <polygon points="24,137 14,142 24,147" style=${`fill: ${exhaustColor}`}></polygon>

      ${supplyRunning
        ? svg`<g class="sheen-layer" mask=${`url(#${uid}-sheen-right)`}>
            <path class="tube-sheen" d=${topTube} stroke=${`url(#${uid}-top)`}></path>
            ${bypassOpen ? svg`<path class="tube-sheen" d=${BYPASS_PATH} style=${`stroke: ${outdoorColor}`}></path>` : nothing}
          </g>`
        : nothing}
      ${exhaustRunning
        ? svg`<g class="sheen-layer" mask=${`url(#${uid}-sheen-left)`}>
            <path class="tube-sheen" d=${bottomTube} stroke=${`url(#${uid}-bottom)`}></path>
          </g>`
        : nothing}

      ${ptc()}

      ${efficiency
        ? clickable(
            KEY.heatRecoveryEfficiency,
            svg`
              <rect class="exchanger" x="166" y="80" width="88" height="44" rx="8" stroke="none"></rect>
              ${compact
                ? svg`<text class="value" x="210" y=${102 + size.efficiency * 0.35} text-anchor="middle"
                    style=${`font-size: ${size.efficiency}px`}>${efficiency}</text>`
                : svg`<text class="value" x="210" y="102" text-anchor="middle"
                      style=${`font-size: ${size.efficiency}px`}>${efficiency}</text>
                    <text class="small" x="210" y="117" text-anchor="middle"
                      style=${`font-size: ${size.small}px`}>${t("heat_recovery")}</text>`}`,
            `${t("heat_recovery")} ${efficiency}`,
          )
        : nothing}

      ${fan(SUPPLY_FAN_X, TOP, supplyRunning, KEY.fanSpeedSupply, KEY.airflowSupply, TOP + 17 + size.fan + size.small * 1.2)}
      ${fan(EXHAUST_FAN_X, BOTTOM, exhaustRunning, KEY.fanSpeedExhaust, KEY.airflowExhaust, BOTTOM - 22)}

      ${temperature(KEY.tempOutdoor, t("outdoor_air"), outdoor, outdoorColor, "left", 18, 42)}
      ${temperature(KEY.tempSupply, t("supply_air"), supply, supplyColor, "right", 18, 42)}
      ${temperature(KEY.tempExtract, t("extract_air"), extract, extractColor, "right", bottomNameY, 176)}
      ${temperature(KEY.tempExhaust, t("exhaust_air"), exhaust, exhaustColor, "left", bottomNameY, 176)}
    </svg>
  `;
}

export const schematicStyles = css`
  .schematic {
    display: block;
    width: 100%;
    max-width: 460px;
    margin: 0 auto;
    overflow: visible;
    font-family: inherit;
  }
  .schematic text {
    fill: var(--primary-text-color);
  }
  .schematic .name,
  .schematic .small {
    fill: var(--secondary-text-color);
  }
  .schematic .value,
  .schematic .fan-speed {
    font-weight: 500;
  }
  .exchanger {
    fill: var(--secondary-background-color, #f5f5f5);
    fill-opacity: 0.55;
    stroke: var(--divider-color);
  }
  .exchanger-line {
    stroke: var(--divider-color);
    opacity: 0.6;
  }
  .tube,
  .tube-sheen {
    fill: none;
    stroke-width: 10px;
    stroke-linecap: round;
    stroke-linejoin: round;
  }
  .tube {
    opacity: 0.32;
  }
  .tube-sheen {
    opacity: 0.45;
  }
  .passage,
  .bypass-closed {
    fill: none;
    stroke: var(--secondary-text-color);
    stroke-width: 2px;
    stroke-dasharray: 3 5;
    opacity: 0.35;
  }
  .bypass-label {
    font-weight: 500;
    fill: var(--secondary-text-color);
  }
  .bypass-label.open {
    fill: var(--primary-text-color);
  }
  .fan-housing {
    fill: var(--card-background-color, #fff);
    stroke: var(--secondary-text-color);
    stroke-width: 1.5px;
  }
  .rotor {
    fill: var(--secondary-text-color);
    transform-box: fill-box;
    transform-origin: center;
  }
  .rotor.spinning {
    animation: kwl-spin linear infinite;
  }
  .ptc rect {
    fill: var(--card-background-color, #fff);
    stroke: var(--secondary-text-color);
    stroke-width: 1.5px;
  }
  .ptc path {
    fill: none;
    stroke: var(--secondary-text-color);
    stroke-width: 1.5px;
    stroke-linejoin: round;
  }
  .ptc.active rect,
  .ptc.active path {
    stroke: #f57c00;
  }
  .sheen {
    animation: kwl-sheen linear infinite;
  }
  .sheen.reverse {
    animation-direction: reverse;
  }
  .clickable {
    cursor: pointer;
    outline: none;
  }
  .clickable:focus-visible {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
  }
  @keyframes kwl-spin {
    to {
      transform: rotate(360deg);
    }
  }
  @keyframes kwl-sheen {
    from {
      transform: translateX(0);
    }
    to {
      transform: translateX(560px);
    }
  }
  @media (prefers-reduced-motion: reduce) {
    .rotor.spinning {
      animation: none;
    }
    .sheen-layer {
      display: none;
    }
  }
`;
