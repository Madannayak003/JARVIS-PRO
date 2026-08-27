"use client";

import type { HUDState } from "@/lib/hudBridge";

type Props = {
  state: HUDState;
};

function formatValue(value: unknown, fallback = "--") {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }

  return String(value);
}

function SystemBar({
  label,
  value,
}: {
  label: string;
  value: unknown;
}) {
  const numeric =
    typeof value === "number"
      ? Math.max(0, Math.min(100, value))
      : null;

  return (
    <div className="cockpit-system-row">
      <div className="cockpit-system-label">
        <span>{label}</span>
        <span>
          {numeric !== null
            ? `${numeric}%`
            : formatValue(value)}
        </span>
      </div>

      <div className="cockpit-bar">
        <div
          className="cockpit-bar-fill"
          style={{
            width:
              numeric !== null
                ? `${numeric}%`
                : "0%",
          }}
        />
      </div>
    </div>
  );
}

export default function HudCockpit({
  state,
}: Props) {
  const system = state.system || {};

  const activeStatus =
    state.status?.toUpperCase() || "IDLE";

  const activity =
    state.current_task ||
    state.notification ||
    "No active task";

  return (
    <div className="hud-cockpit">

      {/* ================================================= */}
      {/* TOP BAR */}
      {/* ================================================= */}

      <header className="cockpit-header">

        <div className="cockpit-brand">
          <span className="brand-main">
            JARVIS
          </span>

          <span className="brand-pro">
            PRO
          </span>
        </div>

        <div className="cockpit-title">
          JARVIS
        </div>

        <div className="cockpit-system-status">
          <span className="status-label">
            SYSTEM
          </span>

          <span className="status-value">
            {state.voice_mode?.toUpperCase() || "ONLINE"}
          </span>
        </div>

      </header>

      {/* ================================================= */}
      {/* LEFT PANEL */}
      {/* ================================================= */}

      <aside className="cockpit-panel cockpit-left">

        <div className="panel-heading">
          <span className="panel-marker">◆</span>
          SYSTEM MONITOR
        </div>

        <div className="panel-body">

          <SystemBar
            label="CPU"
            value={system.cpu}
          />

          <SystemBar
            label="RAM"
            value={system.ram}
          />

          <SystemBar
            label="BAT"
            value={system.battery}
          />

          <div className="cockpit-data-row">
            <span>NET</span>
            <span>
              {formatValue(
                system.network,
                "ONLINE"
              )}
            </span>
          </div>

          <div className="cockpit-data-row">
            <span>GPU</span>
            <span>
              {formatValue(
                system.gpu,
                "N/A"
              )}
            </span>
          </div>

          <div className="cockpit-data-row">
            <span>MODE</span>
            <span>
              {formatValue(
                state.voice_mode,
                "ONLINE"
              ).toUpperCase()}
            </span>
          </div>

        </div>

      </aside>

      {/* ================================================= */}
      {/* RIGHT PANEL */}
      {/* ================================================= */}

      <aside className="cockpit-panel cockpit-right">

        <div className="panel-heading">
          <span className="panel-marker">◆</span>
          ACTIVITY LOG
        </div>

        <div className="activity-section">

          <span className="activity-label">
            STATUS
          </span>

          <span className="activity-value">
            {activeStatus}
          </span>

        </div>

        <div className="activity-section">

          <span className="activity-label">
            TASK
          </span>

          <span className="activity-value">
            {activity}
          </span>

        </div>

        <div className="activity-section">

          <span className="activity-label">
            AI MODEL
          </span>

          <span className="activity-value">
            {state.ai_model || "JARVIS CORE"}
          </span>

        </div>

        {state.error && (
          <div className="activity-error">
            {state.error}
          </div>
        )}

      </aside>

      {/* ================================================= */}
      {/* CENTER LABEL */}
      {/* ================================================= */}

      <div className="cockpit-core-label">

        <div className="core-name">
          JARVIS
        </div>

        <div className="core-status">
          {activeStatus}
        </div>

        <div className="core-subtitle">
          ULTRON CORE // JARVIS PRO
        </div>

      </div>

      {/* ================================================= */}
      {/* BOTTOM STATUS */}
      {/* ================================================= */}

      <div className="cockpit-bottom">

        <div
          className={`voice-indicator ${
            state.listening
              ? "active"
              : ""
          }`}
        >
          LISTENING
        </div>

        <div
          className={`voice-indicator ${
            state.thinking
              ? "active"
              : ""
          }`}
        >
          THINKING
        </div>

        <div
          className={`voice-indicator ${
            state.speaking
              ? "active"
              : ""
          }`}
        >
          SPEAKING
        </div>

        <div
          className={`voice-indicator ${
            state.executing
              ? "active"
              : ""
          }`}
        >
          EXECUTING
        </div>

      </div>

    </div>
  );
}