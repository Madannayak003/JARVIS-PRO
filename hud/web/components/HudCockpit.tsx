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
  PersonalLinkEntry,
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

  onSchedules: () => void;

  showActivityLog: boolean;
  showSystemMonitor: boolean;
  showQuickTools: boolean;
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


function formatUptime(
  uptime: unknown,
) {

  if (
    typeof uptime !== "number" ||
    !Number.isFinite(uptime)
  ) {

    return "--:--:--";

  }

  const totalSeconds = Math.floor(uptime);

  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor(
    (totalSeconds % 3600) / 60
  );
  const seconds = totalSeconds % 60;

  return [hours, minutes, seconds]
    .map((value) => String(value).padStart(2, "0"))
    .join(":");

}


function SystemInfoCard({
  status,
  uptime,
}: {
  status: unknown;
  uptime: string;
}) {

  const systemStatus = formatValue(
    status,
    "--"
  ).toUpperCase();

  return (
    <div className="cockpit-system-row cockpit-system-info-card">

      <div className="cockpit-system-info-block">

        <span className="cockpit-system-name">
          SYSTEM STATUS
        </span>

        <span className="cockpit-system-state cockpit-system-live-state">
          <span className="cockpit-system-status-dot" />
          {systemStatus}
        </span>

      </div>

      <div className="cockpit-system-info-block">

        <span className="cockpit-system-name">
          UPTIME
        </span>

        <span className="cockpit-system-state cockpit-system-uptime">
          {uptime}
        </span>

      </div>

    </div>
  );

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

    const isBattery =
    label === "BAT";

  const isGreen =
    numeric !== null &&
    (
      isBattery
        ? numeric >= 85
        : numeric < 35
    );

  const isYellow =
    numeric !== null &&
    numeric >= 35 &&
    numeric <= 85;

  const isRed =
    numeric !== null &&
    (
      isBattery
        ? numeric < 35
        : numeric > 85
    );

  return (
    <div
      className={
        `cockpit-system-row${
          isGreen
            ? " cockpit-status-green"
            : ""
        }${
          isYellow
            ? " cockpit-status-yellow"
            : ""
        }${
          isRed
            ? " cockpit-status-red"
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
          {isGreen
            ? "GOOD"
            : isYellow
              ? "MEDIUM"
              : isRed
                ? (isBattery ? "LOW" : "HIGH LOAD")
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


function PersonalLinksActivity({
  entries,
}: {
  entries: PersonalLinkEntry[];
}) {
  return (
    <div>
      {entries.map((entry) => (
        <div key={entry.url}>
          <a
            href={entry.url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(event) => {
              event.preventDefault();
              window.open(entry.url, "_blank", "noopener,noreferrer");
            }}
          >
            {entry.name}: {entry.url}
          </a>
        </div>
      ))}
    </div>
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
  onSchedules,
  showActivityLog,
  showSystemMonitor,
  showQuickTools,
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

  // Reference for the activity log container
  const activityLogRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const log = activityLogRef.current;

    if (!log) {
      return;
    }

    const scrollToLatest = () => {
      log.scrollTop = log.scrollHeight;
    };

    // Scroll when a new activity arrives.
    requestAnimationFrame(scrollToLatest);

    // Keep the log pinned to the newest text while
    // ActivityMessage is typing the response.
    const observer = new MutationObserver(() => {
      requestAnimationFrame(scrollToLatest);
    });

    observer.observe(log, {
      childList: true,
      subtree: true,
      characterData: true,
    });

    return () => {
      observer.disconnect();
    };
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
          aria-label={`${assistantName} navigation`}
        >

          <button
            type="button"
            onClick={() => onCommand("shutdown")}
          >
            SHUTDOWN
          </button>

          <button
            type="button"
            onClick={() => onCommand("running apps")}
          >
            RUNNING
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
          {assistantName || "Assistant"}
        </div>


        {/* ================================================= */}
        {/* HEADER TOOLS */}
        {/* ================================================= */}

        <nav
          className="cockpit-header-nav cockpit-header-nav-right"
          aria-label={`${assistantName} tools`}
        >

          <button
            type="button"
            onClick={() => onCommand("what is on my screen")}
          >
            SCREEN
          </button>

          <button
            type="button"
            onClick={() => onCommand("take photo")}
          >
            CAPTURE
          </button>

          <button
            type="button"
            onClick={() => onCommand("recent files")}
          >
            FILES
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

    {showSystemMonitor && (
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

          <SystemInfoCard
            status={state.voice_mode}
            uptime={formatUptime(system.uptime)}
          />

        </div>

      </aside>
    )}


      {/* ============================================= */}
      {/* RIGHT — REAL ACTIVITY LOG */}
      {/* ============================================= */}

    {showActivityLog && (
      <aside className="cockpit-panel cockpit-right">

        <div className="panel-heading">

          <span className="panel-marker">
            ◆
          </span>

          ACTIVITY LOG

        </div>

        <div
         ref={activityLogRef}
         className="activity-log">

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

                      {activity.speaker === "user"
                        ? "USER"
                        : activity.speaker === "live"
                          ? `${assistantName} • LIVE`
                          : activity.speaker === "jarvis"
                            ? assistantName
                            : "SYS"}

                    </span>

                  </div>


                  <div className="activity-message-text">

                    {activity.personalLinks?.length ? (
                      <PersonalLinksActivity
                        entries={activity.personalLinks}
                      />
                    ) : (
                      <ActivityMessage
                        text={activity.text}
                        animate={
                          activity.id ===
                          activities[activities.length - 1]?.id
                        }
                      />
                    )}

                  </div>

                </div>

              )
            )

          )}
          
        </div>

      </aside>
    )}

      {/* ================================================= */}
      {/* QUICK TOOLS */}
      {/* ================================================= */}

    {showQuickTools && (
      <aside className="cockpit-quick-tools">

        {/* <div className="panel-heading">
          <span className="panel-marker">
            ◆
          </span>
          QUICK TOOLS
        </div> */}

        <div className="quick-tools-grid">
          {/* GOOGLE */}
          <button
            type="button"
            onClick={() => onCommand("open google")}
            aria-label="Open Google"
          >
            <span className="quick-tool-icon">
              <svg viewBox="0 0 24 24" width="22" height="22">
                <path
                  fill="#4285F4"
                  d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z"
                />
                <path
                  fill="#34A853"
                  d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 10.03 0 12s.45 3.82 1.25 5.42l4.03-3.15z"
                />
                <path
                  fill="#EA4335"
                  d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
                />
              </svg>
            </span>
            <span>GOOGLE</span>
          </button>

          {/* YOUTUBE */}
          <button
            type="button"
            onClick={() => onCommand("open youtube")}
            aria-label="Open YouTube"
          >
            <span className="quick-tool-icon">
              <svg viewBox="0 0 24 24" width="22" height="22">
                <path
                  fill="#FF0000"
                  d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814z"
                />
                <polygon fill="#FFFFFF" points="9.545,15.568 15.818,12 9.545,8.432" />
              </svg>
            </span>
            <span>YOUTUBE</span>
          </button>

          {/* EMAIL */}
          <button
            type="button"
            onClick={() => onCommand("open gmail")}
            aria-label="Open Email"
          >
            <span className="quick-tool-icon">
              <svg viewBox="0 0 24 24" width="22" height="22">
                <path
                  fill="#4285F4"
                  d="M22 6.5v11a2.5 2.5 0 0 1-2.5 2.5H19V8.58l-7 5.25-7-5.25V20H4.5A2.5 2.5 0 0 1 2 17.5v-11a2.5 2.5 0 0 1 3.97-2.02L12 8.94l6.03-4.46A2.5 2.5 0 0 1 22 6.5z"
                />
                <path
                  fill="#EA4335"
                  d="M20 4.5h-2.5L12 8.94 6.5 4.5H4a2.5 2.5 0 0 0-2 1v1l10 7.5 10-7.5v-1a2.5 2.5 0 0 0-2-1z"
                />
              </svg>
            </span>
            <span>EMAIL</span>
          </button>

          {/* MAPS */}
          <button
            type="button"
            onClick={() => onCommand("open google maps")}
            aria-label="Open Google Maps"
          >
            <span className="quick-tool-icon">
              <svg viewBox="0 0 24 24" width="22" height="22">
                <path
                  fill="#EA4335"
                  d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"
                />
                <circle fill="#FFFFFF" cx="12" cy="9" r="3" />
              </svg>
            </span>
            <span>MAPS</span>
          </button>

          {/* TRANSLATE */}
          <button
            type="button"
            onClick={() => onCommand("open google translate")}
            aria-label="Open Google Translate"
          >
            <span className="quick-tool-icon">
              <svg viewBox="0 0 24 24" width="22" height="22">
                <path
                  fill="#1A73E8"
                  d="M12.87 15.07l-2.54-2.51.03-.03c1.74-1.94 2.98-4.17 3.71-6.53H17V4h-7V2H8v2H1v2h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.11 5.02L4 19l5-5 3.11 3.11.76-2.04z"
                />
                <path
                  fill="#34A853"
                  d="M18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z"
                />
              </svg>
            </span>
            <span>TRANSLATE</span>
          </button>

          {/* WEBSITES */}
          <button
            type="button"
            onClick={() => onCommand("open website list")}
            aria-label="Open website list"
          >
            <span className="quick-tool-icon">
              <svg
                viewBox="0 0 24 24"
                width="22"
                height="22"
                fill="none"
                stroke="#00d4ff"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <circle cx="12" cy="12" r="10" />
                <line x1="2" y1="12" x2="22" y2="12" />
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
              </svg>
            </span>
            <span>WEBSITES</span>
          </button>

          {/* SCHEDULES */}
          <button
            type="button"
            onClick={onSchedules}
            aria-label="Open Schedules"
          >
            <span className="quick-tool-icon">
              <svg
                viewBox="0 0 24 24"
                width="22"
                height="22"
                fill="none"
                stroke="#00e5ff"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <rect x="3" y="5" width="18" height="16" rx="2" />
                <path d="M16 3v4M8 3v4M3 10h18M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01" />
              </svg>
            </span>
            <span>SCHEDULES</span>
          </button>

          {/* LOCK */}
          <button
            type="button"
            onClick={() => onCommand("lock")}
            aria-label="Lock PC"
          >
            <span className="quick-tool-icon">
              <svg
                viewBox="0 0 24 24"
                width="22"
                height="22"
                fill="none"
                stroke="#00e5ff"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <rect x="5" y="11" width="14" height="10" rx="2" fill="#00e5ff" fillOpacity="0.15" />
                <path d="M8 11V7a4 4 0 0 1 8 0v4" />
                <circle cx="12" cy="16" r="1.5" fill="#00e5ff" />
              </svg>
            </span>
            <span>LOCK</span>
          </button>
        </div>

      </aside>
    )}
      
    </div>

  );

}
