"use client";

import type {
  HUDState,
  HUDBridgeEvent,
} from "@/lib/hudBridge";


type Props = {

  state: HUDState;

  events: HUDBridgeEvent[];

};


// =========================================================
// VALUE FORMATTER
// =========================================================

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

  return String(
    value
  );

}


// =========================================================
// SYSTEM BAR
// =========================================================

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

            : formatValue(
                value
              )}

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


// =========================================================
// EVENT MESSAGE
// =========================================================

function getEventMessage(
  event: HUDBridgeEvent
) {

  const data =
    event.data || {};


  // -------------------------------------------------------
  // Notification
  // -------------------------------------------------------

  if (
    typeof data.message === "string" &&
    data.message
  ) {

    return data.message;

  }


  // -------------------------------------------------------
  // Error
  // -------------------------------------------------------

  if (
    typeof data.error === "string" &&
    data.error
  ) {

    return data.error;

  }


  // -------------------------------------------------------
  // Task
  // -------------------------------------------------------

  if (
    typeof data.task === "string" &&
    data.task
  ) {

    return (
      `${event.name} · ${data.task}`
    );

  }


  // -------------------------------------------------------
  // Voice mode
  // -------------------------------------------------------

  if (
    typeof data.mode === "string" &&
    data.mode
  ) {

    return (
      `${event.name} · ${data.mode}`
    );

  }


  // -------------------------------------------------------
  // AI model
  // -------------------------------------------------------

  if (
    typeof data.model === "string" &&
    data.model
  ) {

    return (
      `${event.name} · ${data.model}`
    );

  }


  // -------------------------------------------------------
  // Normal event
  // -------------------------------------------------------

  return event.name
    .replaceAll(
      "_",
      " "
    )
    .toUpperCase();

}


// =========================================================
// TIME
// =========================================================

function formatEventTime(
  timestamp: string
) {

  if (!timestamp) {

    return "--:--:--";

  }


  try {

    return new Date(
      timestamp
    ).toLocaleTimeString(
      [],
      {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false,
      }
    );

  } catch {

    return "--:--:--";

  }

}


// =========================================================
// COCKPIT
// =========================================================

export default function HudCockpit({

  state,

  events,

}: Props) {


  const system =
    state.system || {};


  const activeStatus =
    state.status?.toUpperCase() ||
    "IDLE";


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

            {state.voice_mode
              ?.toUpperCase() ||
              "ONLINE"}

          </span>

        </div>

      </header>


      {/* ================================================= */}
      {/* SYSTEM MONITOR */}
      {/* ================================================= */}

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


      {/* ================================================= */}
      {/* ACTIVITY LOG */}
      {/* ================================================= */}

      <aside className="cockpit-panel cockpit-right">

        <div className="panel-heading">

          <span className="panel-marker">
            ◆
          </span>

          ACTIVITY LOG

        </div>


        <div className="activity-log">

          {events.length === 0 ? (

            <div className="activity-empty">

              SYSTEM READY

            </div>

          ) : (

            events
              .slice()
              .reverse()
              .map(
                (
                  event,
                  index
                ) => (

                  <div
                    className="activity-log-entry"
                    key={`${event.timestamp}-${event.name}-${index}`}
                  >

                    <span className="activity-time">

                      {formatEventTime(
                        event.timestamp
                      )}

                    </span>


                    <span className="activity-event">

                      {getEventMessage(
                        event
                      )}

                    </span>

                  </div>

                )
              )

          )}

        </div>

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