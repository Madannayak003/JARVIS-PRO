"use client";

import type { CSSProperties } from "react";

import type {
  HUDState,
} from "@/lib/hudBridge";

import type {
  HUDActivity,
} from "@/app/page";


type Props = {

  state: HUDState;

  activities: HUDActivity[];

  assistantName: string;

  userName: string;

  morningBriefHeadlines: Array<{
    category: string;
    title: string;
    link?: string;
  }>;

  onMorningBriefClose: () => void;

};


function formatValue(
  value: unknown,
  fallback = "--"
) {

  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {

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

      ? Math.max(
          0,
          Math.min(
            100,
            value
          )
        )

      : null;


  return (

    <div className="cockpit-system-row">

      <div className="cockpit-system-label">

        <span>
          {label}
        </span>

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


function formatTime(
  timestamp: string
) {

  if (!timestamp) {

    return "--:--:--";

  }

  const date =
    new Date(timestamp);

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {

    return timestamp;

  }

  return date.toLocaleTimeString(
    [],
    {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    }
  );

}


export default function HudCockpit({
  state,
  activities,
  assistantName,
  userName,
  morningBriefHeadlines,
  onMorningBriefClose,
}: Props) {

  const system =
    state.system || {};


  const activeStatus =
    state.status?.toUpperCase()
    || "IDLE";


  return (

    <div className="hud-cockpit">

      {/* ============================================= */}
      {/* TOP BAR */}
      {/* ============================================= */}

      <header className="cockpit-header">

        <div className="cockpit-brand">

          <span className="brand-main">
            {assistantName}
          </span>

          <span className="brand-pro">
            PRO
          </span>

        </div>


        <div className="cockpit-title">
          {assistantName || "JARVIS"}
        </div>


        <div className="cockpit-system-status">

          <span className="status-label">
            SYSTEM
          </span>

          <span className="status-value">

            {state.voice_mode
              ?.toUpperCase()
              || "ONLINE"}

          </span>

        </div>

      </header>


      {/* ============================================= */}
      {/* LEFT — SYSTEM MONITOR */}
      {/* ============================================= */}

      <aside className="cockpit-panel cockpit-left">

        <div className="panel-heading">

          <span className="panel-marker">
            ◆
          </span>

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

            <span>
              NET
            </span>

            <span>

              {formatValue(
                system.network,
                "ONLINE"
              )}

            </span>

          </div>


          <div className="cockpit-data-row">

            <span>
              GPU
            </span>

            <span>

              {formatValue(
                system.gpu,
                "N/A"
              )}

            </span>

          </div>


          <div className="cockpit-data-row">

            <span>
              MODE
            </span>

            <span>

              {formatValue(
                state.voice_mode,
                "ONLINE"
              ).toUpperCase()}

            </span>

          </div>

        </div>

      </aside>


      {/* ============================================= */}
      {/* RIGHT — REAL ACTIVITY LOG */}
      {/* ============================================= */}

      <aside className="cockpit-panel cockpit-right">

        <div className="panel-heading">

          <span className="panel-marker">
            ◆
          </span>

          ACTIVITY LOG

        </div>


        <div className="activity-log">

          {activities.length === 0 ? (

            <div className="activity-empty">

              Waiting for conversation...

            </div>

          ) : (

            activities.map(
              (activity) => (

                <div
                  key={activity.id}
                  className={
                    `activity-message ` +
                    `activity-${activity.speaker}`
                  }
                >

                  <div className="activity-message-meta">

                    <span>
                      {formatTime(
                        activity.timestamp
                      )}
                    </span>

                    <span>

                      {activity.speaker ===
                        "user"

                        ? "USER"

                        : activity.speaker ===
                          "jarvis"

                          ? assistantName

                          : "SYS"}

                    </span>

                  </div>


                  <div className="activity-message-text">

                    {activity.text}

                  </div>

                </div>

              )
            )

          )}

        </div>

      </aside>

      {/* ============================================= */}
      {/* BOTTOM RUNTIME STATUS */}
      {/* ============================================= */}

      <div className="cockpit-bottom">

        <div
          className={
            `voice-indicator ${
              state.listening
                ? "active"
                : ""
            }`
          }
        >
          LISTENING
        </div>


        <div
          className={
            `voice-indicator ${
              state.thinking
                ? "active"
                : ""
            }`
          }
        >
          THINKING
        </div>


        <div
          className={
            `voice-indicator ${
              state.speaking
                ? "active"
                : ""
            }`
          }
        >
          SPEAKING
        </div>


        <div
          className={
            `voice-indicator ${
              state.executing
                ? "active"
                : ""
            }`
          }
        >
          EXECUTING
        </div>

      </div>

    </div>

  );

}