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

  onCommand: (command: string) => void;

  onFullscreen: () => void;

  onSettings: () => void;

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
  onCommand,
  onFullscreen,
  onSettings,
}: Props) {

  const system =
    state.system || {};

  // Live Clock State
  const [currentTime, setCurrentTime] = useState("");
  const [todayDate, setTodayDate] = useState("");

  useEffect(() => {
    const updateClock = () => {
      const now = new Date();

      setCurrentTime(
        now.toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
          hour12: false,
        })
      );

      setTodayDate(
        now.toLocaleDateString("en-GB", {
          weekday: "short",
          day: "2-digit",
          month: "short",
        })
      );
    };

    updateClock();

    const timer = setInterval(
      updateClock,
      1000
    );

    return () => clearInterval(timer);
  }, []);

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

        {/* ================================================= */}
        {/* BRAND */}
        {/* ================================================= */}

        <div className="cockpit-brand">

          <span className="brand-main">
            {assistantName}
          </span>

          <span className="brand-pro">
            PRO
          </span>

        </div>


        {/* ================================================= */}
        {/* HEADER QUICK NAV */}
        {/* ================================================= */}

        <nav
          className="cockpit-header-nav cockpit-header-nav-left"
          aria-label="JARVIS navigation"
        >

          <button
            type="button"
            onClick={() => onCommand("go home")}
          >
            HOME
          </button>

          <button
            type="button"
            onClick={() => onCommand("open apps")}
          >
            APPS
          </button>

          <button
            type="button"
            onClick={() => onCommand("weather")}
          >
            WEATHER
          </button>

          <button
            type="button"
            onClick={() => onCommand("news")}
          >
            NEWS
          </button>

          <button
            type="button"
            onClick={() => onCommand("play music")}
          >
            MUSIC
          </button>

        </nav>


        {/* ================================================= */}
        {/* CENTER TITLE */}
        {/* ================================================= */}

        <div className="cockpit-title">
          {assistantName || "JARVIS"}
        </div>


        {/* ================================================= */}
        {/* HEADER TOOLS */}
        {/* ================================================= */}

        <nav
          className="cockpit-header-nav cockpit-header-nav-right"
          aria-label="JARVIS tools"
        >

          <button
            type="button"
            onClick={() => onCommand("what is on my screen")}
          >
            SCREEN
          </button>

          <button
            type="button"
            onClick={() => onCommand("take a screenshot")}
          >
            CAPTURE
          </button>

          <button
            type="button"
            onClick={() => onCommand("create")}
          >
            CREATE
          </button>

          <button
            type="button"
            onClick={() => onCommand("take a note")}
          >
            NOTES
          </button>

          <button
            type="button"
            onClick={onSettings}
          >
            SETTINGS
          </button>

        </nav>


        {/* ================================================= */}
        {/* SYSTEM STATUS */}
        {/* ================================================= */}

        <div className="cockpit-system-status">

          <div
            style={{
              display: "flex",
              gap: "8px",
              alignItems: "center",
            }}
          >

            <span className="status-label">
              TIME
            </span>

            <span className="status-value">
              {currentTime || "--:--:--"}
            </span>

          </div>


          <div
            style={{
              display: "flex",
              gap: "8px",
              alignItems: "center",
            }}
          >

            <span className="status-label">
              SYSTEM
            </span>

            <span className="status-value">
              {state.voice_mode
                ?.toUpperCase()
                || "ONLINE"}
            </span>

          </div>

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

      {/* ================================================= */}
      {/* QUICK TOOLS */}
      {/* ================================================= */}

      <aside className="cockpit-quick-tools">

        <div className="panel-heading">

          <span className="panel-marker">
            ◆
          </span>

          QUICK TOOLS

        </div>


        <div className="quick-tools-grid">

          <button
            type="button"
            onClick={() => onCommand("open app")}
          >
            <span className="quick-tool-icon">▣</span>
            <span>OPEN APP</span>
          </button>

          <button
            type="button"
            onClick={() => onCommand("open website")}
          >
            <span className="quick-tool-icon">◎</span>
            <span>WEBSITE</span>
          </button>

          <button
            type="button"
            onClick={() => onCommand("search")}
          >
            <span className="quick-tool-icon">⌕</span>
            <span>SEARCH</span>
          </button>

          <button
            type="button"
            onClick={() => onCommand("open calculate")}
          >
            <span className="quick-tool-icon">▦</span>
            <span>CALCULATOR</span>
          </button>

          <button
            type="button"
            onClick={() => onCommand("translate")}
          >
            <span className="quick-tool-icon">文</span>
            <span>TRANSLATE</span>
          </button>

          <button
            type="button"
            onClick={() => onCommand("open youtube")}
          >
            <span className="quick-tool-icon">▶</span>
            <span>YOUTUBE</span>
          </button>

          <button
            type="button"
            onClick={() => onCommand("open maps")}
          >
            <span className="quick-tool-icon">⌖</span>
            <span>MAPS</span>
          </button>

          <button
            type="button"
            onClick={() => onCommand("open gmail")}
          >
            <span className="quick-tool-icon">✉</span>
            <span>EMAIL</span>
          </button>

        </div>

      </aside>


      {/* ================================================= */}
      {/* TODAY */}
      {/* ================================================= */}

      {/* <aside className="cockpit-today">

        <div className="panel-heading">

          <span className="panel-marker">
            ◆
          </span>

          TODAY

          <span className="today-date">
            {todayDate}
          </span>

        </div>


        <div className="today-content">

          <div className="today-item">

            <span className="today-icon">
              ◷
            </span>

            <div>

              <div className="today-label">
                UPCOMING
              </div>

              <div className="today-value">
                No upcoming events
              </div>

            </div>

          </div>


          <div className="today-item">

            <span className="today-icon">
              ☑
            </span>

            <div>

              <div className="today-label">
                TASKS
              </div>

              <div className="today-value">
                No pending tasks
              </div>

            </div>

          </div>


          <div className="today-item">

            <span className="today-icon">
              ◆
            </span>

            <div>

              <div className="today-label">
                BRIEF
              </div>

              <div className="today-value">

                {morningBriefHeadlines.length > 0
                  ? `${morningBriefHeadlines.length} headlines available`
                  : "No brief loaded"}

              </div>

            </div>

          </div>

        </div>

      </aside> */}

    </div>

  );

}