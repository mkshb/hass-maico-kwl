import {
  mdiFanOff,
  mdiFanSpeed1,
  mdiFanSpeed2,
  mdiFanSpeed3,
  mdiSnowflake,
  mdiWaterPercent,
  mdiWhiteBalanceSunny,
} from "@mdi/js";
import { css, html, nothing, svg, type TemplateResult } from "lit";

import type { KwlDevice } from "./device";
import { KEY, type EntityKey } from "./keys";
import { localize, type StringKey } from "./localize";
import type { HomeAssistant } from "./types";

const LEVELS = ["off", "humidity_protection", "reduced", "nominal", "intensive"] as const;

// On a narrow card the level bar shows these instead of words.
const LEVEL_ICONS: Record<(typeof LEVELS)[number], string> = {
  off: mdiFanOff,
  humidity_protection: mdiWaterPercent,
  reduced: mdiFanSpeed1,
  nominal: mdiFanSpeed2,
  intensive: mdiFanSpeed3,
};

// In these modes the unit picks the level itself, so the level bar is locked.
const AUTO_MODES = new Set(["auto_time", "auto_sensor"]);

// Days per month for the filter interval, which the unit keeps in months.
const DAYS_PER_MONTH = 30.44;
const FILTER_SOON_DAYS = 14;

const FILTERS: [label: StringKey, remaining: EntityKey, runtime: EntityKey][] = [
  ["filter_device", KEY.filterRemainingDevice, KEY.filterRuntimeDevice],
  ["filter_outdoor", KEY.filterRemainingOutdoor, KEY.filterRuntimeOutdoor],
  ["filter_room", KEY.filterRemainingRoom, KEY.filterRuntimeRoom],
];

/** Controls whose change the card shows at once, before the unit confirms it. */
export type Control = "level" | "mode" | "boost";

/** The value of a control as the unit reports it. */
export const REPORTED: Record<Control, (device: KwlDevice) => string | undefined> = {
  // The running level: in the auto modes the unit's own choice.
  level: (device) => device.state(KEY.currentVentLevel) ?? device.state(KEY.ventilationLevel),
  mode: (device) => device.state(KEY.operatingMode),
  boost: (device) => device.state(KEY.boost),
};

export interface ControlsContext {
  hass: HomeAssistant;
  device: KwlDevice;
  /** The card is too narrow for words in the level bar. */
  narrow: boolean;
  moreInfo: (key: EntityKey) => void;
  /** The value to show: a pending change, else the reported one. */
  shown: (control: Control) => string | undefined;
  pending: (control: Control) => boolean;
  /** Show the value at once and send it; the unit confirms it later. */
  change: (control: Control, value: string, send: () => Promise<unknown>) => void;
}

function selectOption(ctx: ControlsContext, control: Control, key: EntityKey, option: string): void {
  const entityId = ctx.device.entityId(key);
  if (!entityId) return;
  ctx.change(control, option, () =>
    ctx.hass.callService("select", "select_option", { entity_id: entityId, option }),
  );
}

function renderLevels(ctx: ControlsContext): TemplateResult | typeof nothing {
  const { hass, device } = ctx;
  const t = (key: StringKey, values?: Record<string, string>) => localize(hass, key, values);
  const levelState = device.stateObj(KEY.ventilationLevel);
  if (!levelState) return nothing;
  const modeState = device.stateObj(KEY.operatingMode);

  const mode = ctx.shown("mode");
  const auto = mode !== undefined && AUTO_MODES.has(mode);
  // The bar shows the running level, and a tap stores the setpoint. Where the
  // two differ (auto modes, unit off, boost) a tap would store a level the
  // unit does not run, so the bar is locked there.
  const lock = auto && modeState
    ? t("level_auto_hint", { mode: hass.formatEntityState(modeState, mode) })
    : mode === "off"
      ? t("level_off_hint")
      : ctx.shown("boost") === "on"
        ? t("level_boost_hint")
        : undefined;
  const current = ctx.shown("level");
  const pending = ctx.pending("level");
  const offLocked = device.isOn(KEY.offLock) ?? false;

  return html`
    <div class="control">
      <div class="control-label" id="kwl-level-label">${t("ventilation_level")}</div>
      <div class=${lock ? "segments locked" : "segments"} role="group" aria-labelledby="kwl-level-label">
        ${LEVELS.map((level) => {
          const active = level === current;
          const disabled = lock !== undefined || (level === "off" && offLocked);
          return html`<button
            type="button"
            class=${active ? (pending ? "segment active pending" : "segment active") : "segment"}
            aria-pressed=${active ? "true" : "false"}
            aria-label=${t(`level_${level}`)}
            title=${t(`level_${level}`)}
            ?disabled=${disabled}
            @click=${() => selectOption(ctx, "level", KEY.ventilationLevel, level)}
          >
            ${ctx.narrow
              ? html`<svg class="level-icon" viewBox="0 0 24 24" aria-hidden="true">
                  ${svg`<path d=${LEVEL_ICONS[level]}></path>`}
                </svg>`
              : t(`level_${level}`)}
          </button>`;
        })}
      </div>
      ${renderLevelHint(ctx, current, lock)}
    </div>
  `;
}

function renderLevelHint(
  ctx: ControlsContext,
  current: string | undefined,
  lock: string | undefined,
): TemplateResult | typeof nothing {
  const t = (key: StringKey) => localize(ctx.hass, key);
  // With icons only, name the running level in words below the bar.
  const parts = [
    ctx.narrow && current && (LEVELS as readonly string[]).includes(current)
      ? t(`level_${current as (typeof LEVELS)[number]}`)
      : undefined,
    lock,
  ].filter(Boolean);
  return parts.length ? html`<div class="hint">${parts.join(" · ")}</div>` : nothing;
}

function renderModeAndBoost(ctx: ControlsContext): TemplateResult | typeof nothing {
  const { hass, device } = ctx;
  const t = (key: StringKey) => localize(hass, key);
  const modeState = device.stateObj(KEY.operatingMode);
  const boostEntity = device.has(KEY.boost) ? device.entityId(KEY.boost) : undefined;
  const seasonState = device.stateObj(KEY.season);
  if (!modeState && !boostEntity && !seasonState) return nothing;

  const options = (modeState?.attributes.options as string[] | undefined) ?? [];
  const mode = ctx.shown("mode");
  const boostOn = ctx.shown("boost") === "on";
  const boostClass = ["button", boostOn ? "active" : "", ctx.pending("boost") ? "pending" : ""].join(" ");
  // On a narrow card the buttons keep only their icons.
  const label = (text: string) => (ctx.narrow ? nothing : html`<span>${text}</span>`);

  return html`
    <div class="mode-row">
      ${modeState
        ? html`<label class="control mode">
            <span class="control-label">${t("operating_mode")}</span>
            <span class="select">
              <select
                class=${ctx.pending("mode") ? "pending" : ""}
                .value=${mode ?? ""}
                @change=${(ev: Event) =>
                  selectOption(ctx, "mode", KEY.operatingMode, (ev.target as HTMLSelectElement).value)}
              >
                ${options.map(
                  (option) => html`<option value=${option} ?selected=${option === mode}>
                    ${hass.formatEntityState(modeState, option)}
                  </option>`,
                )}
              </select>
              <svg class="chevron" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M7 10l5 5 5-5"></path>
              </svg>
            </span>
          </label>`
        : nothing}
      ${boostEntity
        ? html`<button
            type="button"
            class=${boostClass}
            aria-pressed=${boostOn ? "true" : "false"}
            aria-label=${t("boost")}
            title=${t("boost")}
            @click=${() =>
              ctx.change("boost", boostOn ? "off" : "on", () =>
                hass.callService("switch", boostOn ? "turn_off" : "turn_on", { entity_id: boostEntity }),
              )}
          >
            <svg viewBox="0 0 18 18" aria-hidden="true" class="stroke-icon">
              <path d="M2 6 H11 A2.5 2.5 0 1 0 8.5 3.5"></path>
              <path d="M2 10 H14 A2.5 2.5 0 1 1 11.5 12.5"></path>
              <path d="M2 14 H7"></path>
            </svg>
            ${label(t("boost"))}
          </button>`
        : nothing}
      ${seasonState && (seasonState.state === "summer" || seasonState.state === "winter")
        ? html`<button
            type="button"
            class="button"
            aria-label=${hass.formatEntityState(seasonState)}
            title=${hass.formatEntityState(seasonState)}
            @click=${() => ctx.moreInfo(KEY.season)}
          >
            <svg viewBox="0 0 24 24" aria-hidden="true" class="fill-icon">
              ${svg`<path d=${seasonState.state === "summer" ? mdiWhiteBalanceSunny : mdiSnowflake}></path>`}
            </svg>
            ${label(hass.formatEntityState(seasonState))}
          </button>`
        : nothing}
    </div>
  `;
}

function renderFilters(ctx: ControlsContext): TemplateResult | typeof nothing {
  const { hass, device } = ctx;
  const t = (key: StringKey, values?: Record<string, string | number>) => localize(hass, key, values);
  const filters = FILTERS.filter(([, remaining]) => device.numberIn(remaining, "d") !== undefined);
  if (!filters.length) return nothing;
  const nextChange = formatDay(hass, device.state(KEY.filterNextChange)) ?? device.format(KEY.filterNextChange);

  return html`
    <div class="filters">
      ${filters.map(([label, remainingKey, runtimeKey]) => {
        const days = Math.max(0, Math.round(device.numberIn(remainingKey, "d")!));
        const months = device.number(runtimeKey);
        const share = months ? Math.min(1, days / (months * DAYS_PER_MONTH)) : 1;
        const level = days === 0 ? "due" : days <= FILTER_SOON_DAYS ? "soon" : "ok";
        return html`
          <button type="button" class="filter" @click=${() => ctx.moreInfo(remainingKey)}>
            <span class="filter-head">
              <span class="control-label">${t(label)}</span>
              <span class=${`filter-days ${level}`}>
                ${level === "due" ? t("filter_due") : t("filter_days", { days })}
              </span>
            </span>
            <span class="bar"><span class=${`bar-fill ${level}`} style=${`width: ${share * 100}%`}></span></span>
          </button>
        `;
      })}
      ${nextChange ? html`<div class="hint">${t("filter_next_change", { date: nextChange })}</div>` : nothing}
    </div>
  `;
}

/** A date sensor's day in numbers, in the HA language: "27.09.2027". */
export function formatDay(hass: HomeAssistant, isoDay: string | undefined): string | undefined {
  const match = isoDay?.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) return undefined;
  const [year, month, day] = match.slice(1).map(Number);
  const language = hass.locale?.language ?? hass.language ?? "en";
  return new Intl.DateTimeFormat(language, { day: "2-digit", month: "2-digit", year: "numeric" }).format(
    new Date(year, month - 1, day),
  );
}

export function renderControls(ctx: ControlsContext): TemplateResult {
  return html`${renderLevels(ctx)}${renderModeAndBoost(ctx)}${renderFilters(ctx)}`;
}

export const controlStyles = css`
  .pending {
    animation: kwl-pending 1.2s ease-in-out infinite alternate;
  }
  @keyframes kwl-pending {
    from {
      opacity: 1;
    }
    to {
      opacity: 0.55;
    }
  }
  @media (prefers-reduced-motion: reduce) {
    .pending {
      animation: none;
      opacity: 0.7;
    }
  }
  .control {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-top: 16px;
  }
  .control-label {
    font-size: 13px;
    font-weight: 500;
    color: var(--secondary-text-color);
  }
  .hint {
    font-size: 12px;
    color: var(--secondary-text-color);
  }
  .segments {
    display: flex;
    gap: 4px;
    padding: 4px;
    border-radius: 12px;
    background: var(--secondary-background-color, #f5f5f5);
  }
  .segment {
    flex: 1 1 0;
    min-width: 0;
    height: 44px;
    padding: 0 4px;
    border: 0;
    border-radius: 8px;
    background: transparent;
    color: var(--primary-text-color);
    font: inherit;
    font-size: 13px;
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    cursor: pointer;
  }
  .level-icon {
    width: 22px;
    height: 22px;
    fill: currentColor;
    vertical-align: middle;
  }
  .segment.active {
    background: var(--primary-color);
    color: var(--text-primary-color, #fff);
  }
  .segment:disabled {
    cursor: default;
  }
  .segments.locked .segment:not(.active),
  .segment:disabled:not(.active) {
    color: var(--secondary-text-color);
    opacity: 0.75;
  }
  .segments.locked .segment.active {
    opacity: 0.7;
  }
  .segment:focus-visible,
  .button:focus-visible,
  .filter:focus-visible,
  select:focus-visible {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
  }
  .mode-row {
    display: flex;
    align-items: flex-end;
    gap: 8px;
  }
  .mode {
    flex: 1 1 auto;
    min-width: 0;
  }
  /* Without appearance: none Safari draws its own control and ignores the
     border and background; the arrow is drawn by the card instead. */
  .select {
    position: relative;
    display: flex;
  }
  select {
    flex: 1 1 auto;
    min-width: 0;
    height: 44px;
    padding: 0 36px 0 12px;
    border: 0;
    border-radius: 10px;
    background: var(--secondary-background-color, #f5f5f5);
    color: var(--primary-text-color);
    font: inherit;
    font-size: 14px;
    -webkit-appearance: none;
    appearance: none;
    cursor: pointer;
  }
  .chevron {
    position: absolute;
    top: 50%;
    right: 10px;
    width: 20px;
    height: 20px;
    transform: translateY(-50%);
    fill: none;
    stroke: var(--primary-text-color);
    stroke-width: 2px;
    stroke-linecap: round;
    stroke-linejoin: round;
    pointer-events: none;
  }
  .button {
    display: flex;
    flex-shrink: 0;
    justify-content: center;
    min-width: 44px;
    align-items: center;
    gap: 8px;
    height: 44px;
    padding: 0 16px;
    border: 0;
    border-radius: 10px;
    background: var(--secondary-background-color, #f5f5f5);
    color: var(--primary-text-color);
    font: inherit;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
  }
  .button.active {
    background: var(--primary-color);
    color: var(--text-primary-color, #fff);
  }
  .button svg {
    width: 18px;
    height: 18px;
  }
  .stroke-icon {
    fill: none;
    stroke: currentColor;
    stroke-width: 2px;
    stroke-linecap: round;
  }
  .fill-icon {
    fill: currentColor;
  }
  .filters {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 16px;
  }
  .filter {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 0;
    border: 0;
    background: none;
    color: var(--primary-text-color);
    font: inherit;
    text-align: left;
    cursor: pointer;
  }
  .filter-head {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
  }
  .filter-days.soon,
  .filter-days.due {
    color: var(--kwl-warn-fg);
    font-weight: 500;
  }
  .bar {
    display: block;
    height: 6px;
    border-radius: 3px;
    background: var(--secondary-background-color, #f5f5f5);
    overflow: hidden;
  }
  .bar-fill {
    display: block;
    height: 100%;
    border-radius: 3px;
    background: var(--primary-color);
  }
  .bar-fill.soon,
  .bar-fill.due {
    background: var(--kwl-warn-fg);
  }
`;
