"use client";

import {
  useEffect,
  useRef,
  useState,
} from "react";

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
      ? Math.max(0, Math.min(100, value))
      : null;

  const isHigh =
    numeric !== null &&
    numeric > 85;

  return (
    <div
      className={
        `cockpit-system-row${
          isHigh
            ? " cockpit-system-high"
            : ""
        }`
      }
    >

      <div
        className="cockpit-gauge"
        style={{
          "--gauge-value":
            `${numeric ?? 0}%`,
        } as React.CSSProperties}
      >

        <div
          className="cockpit-gauge-fill"
          style={{
            "--gauge-value":
              `${numeric ?? 0}%`,
          } as React.CSSProperties}
        >

          <div className="cockpit-gauge-center">

            <span className="cockpit-gauge-value">
              {numeric !== null
                ? `${numeric}%`
                : "--"}
            </span>

            <span className="cockpit-gauge-unit">
              LOAD
            </span>

          </div>

        </div>

      </div>


      <div className="cockpit-system-info">

        <span className="cockpit-system-name">
          {label}
        </span>

        <span className="cockpit-system-state">
          {isHigh
            ? "HIGH LOAD"
            : "NOMINAL"}
        </span>

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


function ActivityMessage({
  text,
  animate,
}: {
  text: string;
  animate: boolean;
}) {

  const [displayText, setDisplayText] =
    useState(
      animate ? "" : text
    );

  useEffect(() => {

    if (!animate) {

      setDisplayText(text);

      return;

    }

    setDisplayText("");

    let index = 0;

    const interval =
      window.setInterval(() => {

        index += 1;

        setDisplayText(
          text.slice(0, index)
        );

        if (index >= text.length) {

          window.clearInterval(
            interval
          );

        }

      }, 18);

    return () => {

      window.clearInterval(
        interval
      );

    };

  }, [text, animate]);

  return (
    <>
      {displayText}
    </>
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

  // Reference for auto-scrolling to the latest log entry
  const logEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activities]);


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

                    <ActivityMessage
                      text={activity.text}
                      animate={
                        activity.id ===
                        activities[activities.length - 1]?.id
                      }
                    />

                  </div>

                </div>

              )
            )

          )}

          {/* Auto-scroll anchor target */}
          <div ref={logEndRef} />

        </div>

      </aside>

    </div>

  );

}