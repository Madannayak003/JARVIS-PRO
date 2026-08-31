"use client";

import {
  useEffect,
  useRef,
  useState,
} from "react";

import JarvisOrb from "@/components/JarvisOrb";
import HudCockpit from "@/components/HudCockpit";
import { QRCodeSVG } from "qrcode.react";

import {
  HUDBridge,
  type HUDConnectionStatus,
  type HUDBridgeEvent,
  type HUDState,
} from "@/lib/hudBridge";


const EMPTY_STATE: HUDState = {
  status: "idle",
  voice_mode: "online",
  ai_model: "",
  current_task: "",
  task_status: "",
  listening: false,
  speaking: false,
  thinking: false,
  executing: false,
  system: {},
  notification: "",
  error: "",
  last_event: "",
  last_update: "",
};


export type HUDActivity = {
  id: string;

  speaker:
    | "user"
    | "jarvis"
    | "system";

  text: string;

  timestamp: string;
};


type SettingsModal =
  | "remote"
  | "customise"
  | null;


  type RemoteInfo = {
  ok: boolean;
    url: string;
    pairing_url: string;
    pairing_pin: string;
    pairing_active: boolean;
    clients: number;
  };

export default function Home() {

  const [
    hudState,
    setHudState,
  ] = useState<HUDState>(
    EMPTY_STATE
  );


  const [
    connection,
    setConnection,
  ] = useState<HUDConnectionStatus>(
    "connecting"
  );


  const [
    activities,
    setActivities,
  ] = useState<HUDActivity[]>(
    []
  );

  const [
    morningBriefHeadlines,
    setMorningBriefHeadlines,
  ] = useState<
    Array<{
      category: string;
      title: string;
      link?: string;
    }>
  >([]);

  const [
    morningBriefActive,
    setMorningBriefActive,
  ] = useState(false);

  const [
    morningBriefStartedSpeaking,
    setMorningBriefStartedSpeaking,
  ] = useState(false);

  const morningBriefActiveRef =
    useRef(false);

  const morningBriefStartedSpeakingRef =
    useRef(false);

  /* =========================================================
     SETTINGS
     ========================================================= */

  const [
    settingsOpen,
    setSettingsOpen,
  ] = useState(false);


  const [
    modal,
    setModal,
  ] = useState<SettingsModal>(
    null
  );


  const [
    autoStart,
    setAutoStart,
  ] = useState(false);


  const [
    morningBrief,
    setMorningBrief,
  ] = useState(true);


  const [
    assistantName,
    setAssistantName,
  ] = useState("JARVIS");


  const [
    userName,
    setUserName,
  ] = useState("");


  const [
    assistantColour,
    setAssistantColour,
  ] = useState("#ffaa30");

  const [
    remoteInfo,
    setRemoteInfo,
  ] = useState<RemoteInfo | null>(null);

  const [
    remoteLoading,
    setRemoteLoading,
  ] = useState(false);

  const [
    shortcutLoading,
    setShortcutLoading,
  ] = useState(false);

  /* =========================================================
     LOAD SETTINGS
     ========================================================= */

  useEffect(() => {

    try {

      const saved =
        window.localStorage.getItem(
          "jarvis-pro-settings"
        );

      if (!saved) {
        return;
      }

      const settings =
        JSON.parse(saved);

      if (
        typeof settings.autoStart ===
        "boolean"
      ) {
        setAutoStart(
          settings.autoStart
        );
      }

      if (
        typeof settings.morningBrief ===
        "boolean"
      ) {
        setMorningBrief(
          settings.morningBrief
        );
      }

      if (
        typeof settings.assistantName ===
        "string"
      ) {
        setAssistantName(
          settings.assistantName
        );
      }

      if (
        typeof settings.userName ===
        "string"
      ) {
        setUserName(
          settings.userName
        );
      }

      if (
        typeof settings.assistantColour ===
        "string"
      ) {
        setAssistantColour(
          settings.assistantColour
        );
      }

    } catch {

      // Ignore invalid saved settings.

    }

  }, []);

  useEffect(() => {

  const loadMorningBrief = async () => {

    try {

      const response = await fetch(
        "http://127.0.0.1:8765/api/local/morning-brief"
      );

      const result = await response.json();

      if (
        response.ok &&
        result.ok &&
        typeof result.enabled === "boolean"
      ) {

        setMorningBrief(
          result.enabled
        );

      }

    } catch (error) {

      console.error(
        "[HUD] Could not load Morning Brief setting:",
        error
      );

    }

  };

  loadMorningBrief();

}, []);


  /* =========================================================
     SAVE SETTINGS
     ========================================================= */

  const saveSettings = () => {

    try {

      window.localStorage.setItem(
        "jarvis-pro-settings",
        JSON.stringify({
          autoStart,
          morningBrief,
          assistantName,
          userName,
          assistantColour,
        })
      );

    } catch {

      // Ignore localStorage failures.

    }

  };


  /* =========================================================
     FULLSCREEN
     ========================================================= */

  const toggleFullscreen = async () => {

    try {

      if (!document.fullscreenElement) {

        await document.documentElement.requestFullscreen();

      } else {

        await document.exitFullscreen();

      }

    } catch {

      // Browser may deny fullscreen.

    }

  };


  /* =========================================================
     DESKTOP SHORTCUT
     ========================================================= */

  const createDesktopShortcut = async () => {

    if (shortcutLoading) {
      return;
    }

    setShortcutLoading(true);

    try {

      const dashboardUrl =
        process.env
          .NEXT_PUBLIC_JARVIS_DASHBOARD_URL
        ||
        (
          typeof window !== "undefined"
            ? `http://${window.location.hostname}:8765`
            : "http://127.0.0.1:8765"
        );

      const response =
        await fetch(
          `${dashboardUrl}/api/local/shortcut`,
          {
            method: "POST",
            cache: "no-store",
          }
        );

      const data =
        await response.json();

      if (!response.ok || !data.ok) {

        throw new Error(
          data?.error ||
          "Unable to create desktop shortcut."
        );

      }

      alert(
        data.message ||
        "JARVIS PRO desktop shortcut created successfully."
      );

    } catch (error) {

      console.error(
        "[DESKTOP SHORTCUT]",
        error
      );

      alert(
        error instanceof Error
          ? error.message
          : "Desktop shortcut creation failed."
      );

    } finally {

      setShortcutLoading(false);

    }

  };


  /* =========================================================
     REMOTE CONTROL
     ========================================================= */

  const openRemoteControl = async () => {

    setModal("remote");
    setRemoteLoading(true);

    try {

      const bridgeUrl =
        process.env
          .NEXT_PUBLIC_JARVIS_DASHBOARD_URL
        || (
          typeof window !== "undefined"
            ? `http://${window.location.hostname}:8765`
            : "http://127.0.0.1:8765"
        );

      const response =
        await fetch(
          `${bridgeUrl}/api/info`,
          {
            cache: "no-store",
          }
        );

      if (!response.ok) {

        throw new Error(
          "Remote information unavailable"
        );

      }

      const data =
        await response.json() as RemoteInfo;

      setRemoteInfo(data);

    } catch {

      setRemoteInfo(null);

    } finally {

      setRemoteLoading(false);

    }

  };


  /* =========================================================
     CUSTOMISE ASSISTANT
     ========================================================= */

  const openCustomise = () => {

    setModal("customise");

  };


  /* =========================================================
     APPLY ASSISTANT SETTINGS
     ========================================================= */

  const applyAssistantSettings = () => {

    saveSettings();

    setModal(null);

  };


  /* =========================================================
     CLOSE SETTINGS
     ========================================================= */

  const closeSettings = () => {

    setSettingsOpen(false);

  };


  /* =========================================================
     HUD SSE CONNECTION
     ========================================================= */

  useEffect(() => {

    const bridge =
      new HUDBridge(

        process.env
          .NEXT_PUBLIC_JARVIS_HUD_BRIDGE_URL
        ||
        "http://127.0.0.1:8766",

        setHudState,

        (
          event: HUDBridgeEvent
        ) => {

          /* =========================================================
            MORNING BRIEF
            ========================================================= */

          if (event.name === "morning_brief") {

            const headlines =
              Array.isArray(
                event.data?.headlines
              )
                ? event.data.headlines
                : [];

            if (headlines.length > 0) {

              setMorningBriefHeadlines(
                headlines
              );

              setMorningBriefActive(true);

              setMorningBriefStartedSpeaking(false);

              morningBriefActiveRef.current = true;

              morningBriefStartedSpeakingRef.current = false;

            }

            return;

          }

          /* =========================================================
            MORNING BRIEF SPEECH LIFECYCLE
            ========================================================= */

          if (event.name === "speaking") {

            if (
              morningBriefActiveRef.current
            ) {

              setMorningBriefStartedSpeaking(true);

              morningBriefStartedSpeakingRef.current = true;

            }

            return;

          }

          /* =========================================================
            ACTIVITY LOG
            ========================================================= */

          if (
            event.name !== "command" &&
            event.name !== "response"
          ) {

            return;

          }


          const speaker =
            event.name === "command"
              ? "user"
              : "jarvis";


          const text =
            String(
              event.data?.text ?? ""
            ).trim();


          if (!text) {

            return;

          }


          const activity: HUDActivity = {

            id:
              `${event.timestamp}-${Math.random()}`,

            speaker,

            text,

            timestamp:
              event.timestamp,

          };


          setActivities(
            (previous) => {

              const next = [
                ...previous,
                activity,
              ];

              /*
               * Keep the latest 30 messages.
               */

              return next.slice(-30);

            }
          );

        },

        setConnection,

      );


    bridge.connect();


    return () =>
      bridge.disconnect();

  }, []);


  return (

    <main className="jarvis-hud">

      {/* =====================================================
          ULTRON ENGINE
          ===================================================== */}

      <div className="ultron-layer">

        <JarvisOrb />

      </div>


      {/* =====================================================
          JARVIS COCKPIT
          ===================================================== */}

      <HudCockpit
        state={hudState}
        activities={activities}
        morningBriefHeadlines={morningBriefHeadlines}
        onMorningBriefClose={() => {
          setMorningBriefActive(false);
          setMorningBriefHeadlines([]);
        }}
      />

      {morningBriefActive &&
        morningBriefHeadlines.length > 0 && (

        <div className="morning-brief-overlay">

          <button
            type="button"
            className="morning-brief-close"
            onClick={() => {
              setMorningBriefActive(false);
              setMorningBriefHeadlines([]);
            }}
            aria-label="Close morning brief"
          >
            ×
          </button>

          <div className="morning-brief-header">

            <span className="morning-brief-marker">
              ◆
            </span>

            <span>
              TODAY'S TOP HEADLINES
            </span>

          </div>


          <div className="morning-brief-list">

            {morningBriefHeadlines.map(
              (headline, index) => (

                <div
                  key={`${headline.title}-${index}`}
                  className="morning-brief-item"
                >

                  <span className="morning-brief-category">
                    {headline.category.toUpperCase()}
                  </span>

                  <span className="morning-brief-title">
                    {headline.title}
                  </span>

                </div>

              )
            )}

          </div>

        </div>

      )}


      {/* =====================================================
          CONNECTION
          ===================================================== */}

      <div className="hud-bridge-status">

        <span
          className={
            `hud-bridge-dot ${connection}`
          }
          aria-hidden="true"
        />

        <span>

          JARVIS LINK ·{" "}

          {connection === "connected"

            ? hudState.status.toUpperCase()

            : connection.toUpperCase()}

        </span>

      </div>


      {/* =====================================================
          SETTINGS BUTTON
          ===================================================== */}

      <button
        type="button"
        className="jarvis-settings-button"
        aria-label="Open JARVIS settings"
        aria-expanded={settingsOpen}
        onClick={() =>
          setSettingsOpen(
            (open) => !open
          )
        }
      >
        ⚙
      </button>


      {/* =====================================================
          SETTINGS PANEL
          ===================================================== */}

      {settingsOpen && (

        <aside
          className="jarvis-settings-panel"
          aria-label="JARVIS settings"
        >

          <div className="settings-panel-brand">

            <span>
              JARVIS PRO
            </span>

          </div>


          <div className="settings-section-title">

            <span>◆</span>

            CONTROLS

          </div>


          {/* -------------------------------------------------
              REMOTE CONTROL
              ------------------------------------------------- */}

          <button
            type="button"
            className="settings-control settings-control-primary"
            onClick={openRemoteControl}
          >

            <span className="settings-control-icon">
              ●
            </span>

            <span>
              REMOTE CONTROL
            </span>

          </button>


          {/* -------------------------------------------------
              FULLSCREEN
              ------------------------------------------------- */}

          <button
            type="button"
            className="settings-control"
            onClick={toggleFullscreen}
          >

            <span className="settings-control-icon">
              ◇
            </span>

            <span>
              FULLSCREEN
            </span>

            <span className="settings-control-key">
              [F11]
            </span>

          </button>


          {/* -------------------------------------------------
              DESKTOP SHORTCUT
              ------------------------------------------------- */}

          <button
            type="button"
            className="settings-control"
            onClick={createDesktopShortcut}
            disabled={shortcutLoading}
          >

            <span className="settings-control-icon">
              ≡
            </span>

            <span>
              {shortcutLoading
                ? "CREATING SHORTCUT..."
                : "CREATE DESKTOP SHORTCUT"}
            </span>

          </button>


          {/* -------------------------------------------------
              AUTO START
              ------------------------------------------------- */}

          <button
            type="button"
            className={
              `settings-control ${
                autoStart
                  ? "settings-control-toggle-on"
                  : ""
              }`
            }
            onClick={() => {

              const next =
                !autoStart;

              setAutoStart(next);

              try {

                window.localStorage.setItem(
                  "jarvis-pro-settings",
                  JSON.stringify({
                    autoStart: next,
                    morningBrief,
                    assistantName,
                    userName,
                    assistantColour,
                  })
                );

              } catch {}

            }}
          >

            <span className="settings-control-icon">
              ≡
            </span>

            <span>
              AUTO-START:
            </span>

            <strong>
              {autoStart
                ? "ON"
                : "OFF"}
            </strong>

          </button>


          {/* -------------------------------------------------
              CUSTOMISE ASSISTANT
              ------------------------------------------------- */}

          <button
            type="button"
            className="settings-control"
            onClick={openCustomise}
          >

            <span className="settings-control-icon">
              ⚙
            </span>

            <span>
              CUSTOMISE ASSISTANT
            </span>

          </button>


          {/* -------------------------------------------------
              MORNING BRIEF
              ------------------------------------------------- */}

          <button
            type="button"
            className={
              `settings-control settings-control-brief ${
                morningBrief
                  ? "settings-control-brief-on"
                  : ""
              }`
            }
            onClick={async () => {

              const next = !morningBrief;

              setMorningBrief(next);

              try {

                const response = await fetch(
                  "http://127.0.0.1:8765/api/local/morning-brief",
                  {
                    method: "POST",
                    headers: {
                      "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                      enabled: next,
                    }),
                  }
                );

                const result = await response.json();

                if (!response.ok || !result.ok) {

                  throw new Error(
                    result.error ||
                    "Failed to update Morning Brief."
                  );

                }

                console.log(
                  "[HUD] Morning Brief:",
                  result.enabled
                    ? "ON"
                    : "OFF"
                );

              } catch (error) {

                console.error(
                  "[HUD] Morning Brief update failed:",
                  error
                );

                setMorningBrief(!next);

              }

            }}
          >

            <span className="settings-control-icon">
              ✳
            </span>

            <span>
              MORNING BRIEF:
            </span>

            <strong>
              {morningBrief
                ? "ON"
                : "OFF"}
            </strong>

          </button>

        </aside>

      )}


      {/* =====================================================
          REMOTE CONTROL MODAL
          ===================================================== */}

      {modal === "remote" && (

        <div
          className="settings-modal-backdrop"
          onClick={() =>
            setModal(null)
          }
        >

          <section
            className="settings-modal remote-modal"
            onClick={(event) =>
              event.stopPropagation()
            }
          >

            <div className="settings-modal-heading">

              <span>
                ◆
              </span>

              REMOTE ACCESS

            </div>


            <div className="remote-modal-content">

              <div className="remote-title">
                JARVIS PRO REMOTE
              </div>


              <p className="remote-description">
                Scan to connect your device
              </p>


              {remoteLoading ? (

                <div className="remote-loading">
                  CONNECTING TO JARVIS...
                </div>

              ) : remoteInfo?.pairing_active &&
                remoteInfo.pairing_url ? (

                <>
                  {/* =========================================
                      QR CODE
                      ========================================= */}

                  <div className="remote-qr-wrapper">

                    <div className="remote-qr">

                      <QRCodeSVG
                        value={
                          remoteInfo.pairing_url
                        }
                        size={220}
                        bgColor="#050505"
                        fgColor="#ffcc66"
                        level="M"
                        includeMargin
                      />

                    </div>

                    <div className="remote-qr-label">
                      SCAN TO CONNECT
                    </div>

                  </div>


                  {/* =========================================
                      PAIRING PIN
                      ========================================= */}

                  <div className="remote-pin-box">

                    <span className="remote-pin-label">
                      PAIRING PIN
                    </span>

                    <strong className="remote-pin">
                      {remoteInfo.pairing_pin}
                    </strong>

                  </div>


                  {/* =========================================
                      DASHBOARD
                      ========================================= */}

                  <div className="remote-status-box">

                    <span>
                      JARVIS DASHBOARD
                    </span>

                    <strong>
                      {remoteInfo.url}
                    </strong>

                  </div>

                </>

              ) : (

                <div className="remote-offline">

                  <strong>
                    PAIRING NOT AVAILABLE
                  </strong>

                  <span>
                    Start the JARVIS dashboard
                    and open Remote Control again.
                  </span>

                </div>

              )}


              <p className="remote-note">

                Scan the QR code with your phone.
                Your device will open the JARVIS
                remote pairing page.

              </p>


              <div className="settings-modal-actions">

                <button
                  type="button"
                  className="settings-modal-button settings-modal-button-primary"
                  onClick={() => {

                    const url =
                      remoteInfo?.pairing_url ||
                      remoteInfo?.url;

                    if (!url) {
                      return;
                    }

                    window.open(
                      url,
                      "_blank",
                      "noopener,noreferrer"
                    );

                  }}
                  disabled={!remoteInfo}
                >
                  OPEN REMOTE
                </button>


                <button
                  type="button"
                  className="settings-modal-button"
                  onClick={() =>
                    setModal(null)
                  }
                >
                  DISMISS
                </button>

              </div>

            </div>

          </section>

        </div>

      )}


      {/* =====================================================
          CUSTOMISE ASSISTANT MODAL
          ===================================================== */}

      {modal === "customise" && (

        <div
          className="settings-modal-backdrop"
          onClick={() =>
            setModal(null)
          }
        >

          <section
            className="settings-modal customise-modal"
            onClick={(event) =>
              event.stopPropagation()
            }
          >

            <div className="settings-modal-heading">

              <span>
                ⚙
              </span>

              CUSTOMISE ASSISTANT

            </div>


            <div className="customise-form">

              <label>

                ASSISTANT NAME

                <input
                  type="text"
                  value={assistantName}
                  onChange={(event) =>
                    setAssistantName(
                      event.target.value
                    )
                  }
                  placeholder="JARVIS"
                />

              </label>


              <label>

                YOUR NAME

                <span className="settings-field-help">
                  leave blank for default sir / efendim
                </span>

                <input
                  type="text"
                  value={userName}
                  onChange={(event) =>
                    setUserName(
                      event.target.value
                    )
                  }
                  placeholder="e.g. Tony"
                />

              </label>


              <label>

                UI COLOUR

                <span className="settings-field-help">
                  choose HUD accent colour
                </span>

                <div className="colour-control">

                  <input
                    type="color"
                    value={assistantColour}
                    onChange={(event) =>
                      setAssistantColour(
                        event.target.value
                      )
                    }
                  />

                  <input
                    type="text"
                    value={assistantColour}
                    onChange={(event) =>
                      setAssistantColour(
                        event.target.value
                      )
                    }
                  />

                </div>

              </label>


              <div className="settings-modal-actions">

                <button
                  type="button"
                  className="settings-modal-button settings-modal-button-primary"
                  onClick={applyAssistantSettings}
                >
                  APPLY CHANGES
                </button>


                <button
                  type="button"
                  className="settings-modal-button"
                  onClick={() =>
                    setModal(null)
                  }
                >
                  CANCEL
                </button>

              </div>

            </div>

          </section>

        </div>

      )}

    </main>

  );

}