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

  const JARVIS_DASHBOARD_URL =
    process.env.NEXT_PUBLIC_JARVIS_DASHBOARD_URL ||
    "http://127.0.0.1:8765";

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
  microphoneEnabled,
    setMicrophoneEnabled,
  ] = useState(true);

  const [
    liveConversationEnabled,
    setLiveConversationEnabled,
  ] = useState(false);


  const [
    assistantName,
    setAssistantName,
  ] = useState("JARVIS");


  const [
    userName,
    setUserName,
  ] = useState("MADAN.R");


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

  const [
    commandInput,
    setCommandInput,
  ] = useState("");

  const [
    commandSending,
    setCommandSending,
  ] = useState(false);

  /* =========================================================
   LOAD SETTINGS
   ========================================================= */

  useEffect(() => {

    const loadSettings = async () => {

      /*
      * -------------------------------------------------------
      * FIRST: load localStorage as a temporary fallback.
      * -------------------------------------------------------
      */

      try {

        const saved =
          window.localStorage.getItem(
            "jarvis-pro-settings"
          );

        if (saved) {

          const settings =
            JSON.parse(saved);

          if (
            typeof settings.autoStart === "boolean"
          ) {
            setAutoStart(settings.autoStart);
          }

          if (
            typeof settings.morningBrief === "boolean"
          ) {
            setMorningBrief(settings.morningBrief);
          }

          if (
            typeof settings.assistantName === "string"
          ) {
            setAssistantName(settings.assistantName);
          }

          if (
            typeof settings.userName === "string"
          ) {
            setUserName(settings.userName);
          }

          if (
            typeof settings.assistantColour === "string"
          ) {
            setAssistantColour(
              settings.assistantColour
            );
          }

        }

      } catch (error) {

        console.error(
          "[HUD] Local settings fallback failed:",
          error
        );

      }


      /*
      * -------------------------------------------------------
      * SECOND: Python backend is the real source of truth.
      * -------------------------------------------------------
      */

      try {

        const response =
          await fetch(
            `${JARVIS_DASHBOARD_URL}/api/local/customise`,
            {
              cache: "no-store",
            }
          );

        const result =
          await response.json();

        if (
          response.ok &&
          result.ok
        ) {

          if (
            typeof result.assistantName === "string"
          ) {
            setAssistantName(
              result.assistantName
            );
          }

          if (
            typeof result.userName === "string"
          ) {
            setUserName(
              result.userName
            );
          }

          if (
            typeof result.assistantColour === "string"
          ) {
            setAssistantColour(
              result.assistantColour
            );
          }

        }

      } catch (error) {

        console.error(
          "[HUD] Could not load persistent assistant settings:",
          error
        );

      }


      /*
      * -------------------------------------------------------
      * AUTO START
      * -------------------------------------------------------
      */

      try {

        const response =
          await fetch(
            `${JARVIS_DASHBOARD_URL}/api/local/autostart`,
            {
              cache: "no-store",
            }
          );

        const result =
          await response.json();

        if (
          response.ok &&
          result.ok &&
          typeof result.enabled === "boolean"
        ) {

          setAutoStart(
            result.enabled
          );

        }

      } catch (error) {

        console.error(
          "[HUD] Could not load Auto-Start status:",
          error
        );

      }

            /*
       * -------------------------------------------------------
       * END SETTINGS LOADING
       * -------------------------------------------------------
       */

    };

    loadSettings();

  }, []);


  /*
   * =========================================================
   * MICROPHONE STARTUP STATUS
   * =========================================================
   *
   * The HUD can load slightly before the background
   * microphone listener starts.
   *
   * Therefore we retry the status check briefly during
   * startup instead of changing the actual microphone state.
   */

  useEffect(() => {

    let cancelled = false;

    let timer: number | null = null;

    let attempts = 0;

    const MAX_ATTEMPTS = 10;


    const loadMicrophone = async () => {

      if (cancelled) {
        return;
      }


      attempts += 1;


      try {

        const response =
          await fetch(
            `${JARVIS_DASHBOARD_URL}/api/local/microphone`,
            {
              cache: "no-store",
            }
          );


        const result =
          await response.json();


        if (
          response.ok &&
          result.ok &&
          typeof result.enabled === "boolean"
        ) {

          /*
           * Update the HUD from the real backend state.
           */
          if (!cancelled) {

            setMicrophoneEnabled(
              result.enabled
            );

          }


          /*
           * If the microphone is still OFF during
           * JARVIS startup, give the background listener
           * a little time to finish initializing.
           *
           * Stop retrying after MAX_ATTEMPTS so we don't
           * continuously poll when the user intentionally
           * keeps the microphone OFF.
           */
          if (
            !result.enabled &&
            attempts < MAX_ATTEMPTS &&
            !cancelled
          ) {

            timer =
              window.setTimeout(
                loadMicrophone,
                1000
              );

          }

          return;

        }


        /*
         * Unexpected response.
         * Retry briefly during startup.
         */
        if (
          attempts < MAX_ATTEMPTS &&
          !cancelled
        ) {

          timer =
            window.setTimeout(
              loadMicrophone,
              1000
            );

        }

      } catch (error) {

        console.error(
          "[HUD] Could not load microphone status:",
          error
        );


        /*
         * Dashboard may still be starting.
         */
        if (
          attempts < MAX_ATTEMPTS &&
          !cancelled
        ) {

          timer =
            window.setTimeout(
              loadMicrophone,
              1000
            );

        }

      }

    };


    loadMicrophone();


    return () => {

      cancelled = true;

      if (timer !== null) {

        window.clearTimeout(timer);

      }

    };

  }, []);

  
  /*
  * -------------------------------------------------------
  * MORNING BRIEF STATUS
  * -------------------------------------------------------
  */

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
  
  
  /*
  * -------------------------------------------------------
  * LIVE CONVERSATION STATUS
  * -------------------------------------------------------
  */

  useEffect(() => {

    const loadLiveConversation = async () => {

      try {

        const response = await fetch(
          "http://127.0.0.1:8765/api/live/status",
          {
            cache: "no-store",
          }
        );

        const result =
          await response.json();

        if (
          response.ok &&
          result.ok &&
          typeof result.running === "boolean"
        ) {

          setLiveConversationEnabled(
            result.running
          );

        }

      } catch (error) {

        console.error(
          "[HUD] Could not load Live Conversation status:",
          error
        );

      }

    };

    loadLiveConversation();

  }, []);


  /* =========================================================
     SAVE SETTINGS
     ========================================================= */

  const saveSettings = (
    nextAssistantName = assistantName,
    nextUserName = userName,
    nextAssistantColour = assistantColour,
  ) => {

    try {

      window.localStorage.setItem(
        "jarvis-pro-settings",
        JSON.stringify({
          autoStart,
          morningBrief,
          assistantName: nextAssistantName,
          userName: nextUserName,
          assistantColour: nextAssistantColour,
        })
      );

    } catch (error) {

      console.error(
        "[HUD] Could not save assistant settings:",
        error
      );

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
    HUD COMMAND INPUT
  ========================================================= */

  const sendHudCommand = async () => {

    const text =
      commandInput.trim();

    if (
      !text ||
      commandSending
    ) {
      return;
    }


    setCommandSending(true);


    try {

      const response =
        await fetch(
          `${JARVIS_DASHBOARD_URL}/api/command`,
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/json",
            },
            cache: "no-store",
            body: JSON.stringify({
              text,
            }),
          }
        );


      const result =
        await response.json();


      if (
        !response.ok ||
        !result.ok
      ) {

        throw new Error(
          result?.error ||
          "Command could not be sent."
        );

      }


      /*
       * Clear only after the backend accepts
       * the command.
       */
      setCommandInput("");

    } catch (error) {

      console.error(
        "[HUD COMMAND]",
        error
      );

    } finally {

      setCommandSending(false);

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

  const applyAssistantSettings = async () => {

    const name =
      assistantName.trim() || "JARVIS";

    const user =
      userName.trim();

    const colour =
      /^#[0-9a-fA-F]{6}$/.test(
        assistantColour
      )
        ? assistantColour.toLowerCase()
        : "#ffaa30";


    /*
    * Update UI immediately.
    */

    setAssistantName(name);
    setUserName(user);
    setAssistantColour(colour);


    /*
    * Keep localStorage as a fallback/cache.
    */

    try {

      window.localStorage.setItem(
        "jarvis-pro-settings",
        JSON.stringify({
          autoStart,
          morningBrief,
          assistantName: name,
          userName: user,
          assistantColour: colour,
        })
      );

    } catch (error) {

      console.error(
        "[HUD] Local settings cache failed:",
        error
      );

    }


    /*
    * Persist to the actual JARVIS backend.
    */

    try {

      const response =
        await fetch(
          `${JARVIS_DASHBOARD_URL}/api/local/customise`,
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/json",
            },
            cache: "no-store",
            body: JSON.stringify({
              assistantName: name,
              userName: user,
              assistantColour: colour,
            }),
          }
        );

      const result =
        await response.json();

      if (
        !response.ok ||
        !result.ok
      ) {

        throw new Error(
          result?.error ||
          "Failed to save assistant settings."
        );

      }

      /*
      * Use the backend-confirmed values.
      */

      if (
        typeof result.settings?.assistantName ===
        "string"
      ) {

        setAssistantName(
          result.settings.assistantName
        );

      }

      if (
        typeof result.settings?.userName ===
        "string"
      ) {

        setUserName(
          result.settings.userName
        );

      }

      if (
        typeof result.settings?.assistantColour ===
        "string"
      ) {

        setAssistantColour(
          result.settings.assistantColour
        );

      }

      console.log(
        "[HUD] Assistant settings saved."
      );

      setModal(null);

    } catch (error) {

      console.error(
        "[HUD] Assistant settings save failed:",
        error
      );

      alert(
        error instanceof Error
          ? error.message
          : "Could not save assistant settings."
      );

    }

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
            event.name !== "response" &&
            event.name !== "system_activity"
          ) {
            return;
          }


          const speaker =
            event.name === "command"
              ? "user"
              : event.name === "response"
                ? "jarvis"
                : "system";


          const text =
            String(
              event.name === "system_activity"
                ? event.data?.message ?? ""
                : event.data?.text ?? ""
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


function AssistantColourPicker({
  value,
  onChange,
}: {
  value: string;
  onChange: (value: string) => void;
}) {
  const wheelRef = useRef<HTMLDivElement | null>(null);
  const [dragging, setDragging] = useState(false);

  function hexToRgb(hex: string) {
    const clean = hex.replace("#", "");

    if (!/^[0-9a-fA-F]{6}$/.test(clean)) {
      return null;
    }

    return {
      r: parseInt(clean.slice(0, 2), 16),
      g: parseInt(clean.slice(2, 4), 16),
      b: parseInt(clean.slice(4, 6), 16),
    };
  }

  function rgbToHsv(
    r: number,
    g: number,
    b: number
  ) {
    r /= 255;
    g /= 255;
    b /= 255;

    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    const delta = max - min;

    let h = 0;

    if (delta !== 0) {
      if (max === r) {
        h = ((g - b) / delta) % 6;
      } else if (max === g) {
        h = (b - r) / delta + 2;
      } else {
        h = (r - g) / delta + 4;
      }

      h *= 60;

      if (h < 0) {
        h += 360;
      }
    }

    const s =
      max === 0
        ? 0
        : delta / max;

    return {
      h,
      s,
      v: max,
    };
  }

  function hsvToHex(
    h: number,
    s: number,
    v: number
  ) {
    const c = v * s;
    const x =
      c *
      (
        1 -
        Math.abs(
          ((h / 60) % 2) - 1
        )
      );

    const m = v - c;

    let r = 0;
    let g = 0;
    let b = 0;

    if (h < 60) {
      r = c;
      g = x;
    } else if (h < 120) {
      r = x;
      g = c;
    } else if (h < 180) {
      g = c;
      b = x;
    } else if (h < 240) {
      g = x;
      b = c;
    } else if (h < 300) {
      r = x;
      b = c;
    } else {
      r = c;
      b = x;
    }

    const toHex = (n: number) =>
      Math.round(
        (n + m) * 255
      )
        .toString(16)
        .padStart(2, "0");

    return (
      "#" +
      toHex(r) +
      toHex(g) +
      toHex(b)
    );
  }

  const rgb = hexToRgb(value);

  const hsv = rgb
    ? rgbToHsv(
        rgb.r,
        rgb.g,
        rgb.b
      )
    : {
        h: 35,
        s: 1,
        v: 1,
      };

  const angle =
    (hsv.h * Math.PI) / 180;

  const radius = 43;

  const handleX =
    50 +
    Math.cos(angle) *
      radius *
      hsv.s;

  const handleY =
    50 +
    Math.sin(angle) *
      radius *
      hsv.s;

  function updateFromPointer(
    event: React.PointerEvent<HTMLDivElement>
  ) {
    const wheel =
      wheelRef.current;

    if (!wheel) {
      return;
    }

    const rect =
      wheel.getBoundingClientRect();

    const x =
      event.clientX -
      (rect.left + rect.width / 2);

    const y =
      event.clientY -
      (rect.top + rect.height / 2);

    const distance =
      Math.sqrt(
        x * x +
        y * y
      );

    const maxRadius =
      Math.min(
        rect.width,
        rect.height
      ) / 2;

    const clampedRadius =
      Math.min(
        distance,
        maxRadius
      );

    let hue =
      Math.atan2(
        y,
        x
      ) *
      (180 / Math.PI);

    if (hue < 0) {
      hue += 360;
    }

    const saturation =
      Math.min(
        1,
        clampedRadius /
          maxRadius
      );

    onChange(
      hsvToHex(
        hue,
        saturation,
        1
      )
    );
  }

  return (
    <div className="assistant-colour-picker">

      <div className="assistant-colour-heading">

        <div>

          <span>
            UI COLOUR
          </span>

          <small>
            choose HUD accent colour
          </small>

        </div>

        <button
          type="button"
          className="assistant-colour-default"
          onClick={() => {
            onChange("#ffaa30");
          }}
        >
          DEFAULT
        </button>

      </div>


      <div className="assistant-colour-wheel-area">

        <div
          ref={wheelRef}
          className="assistant-colour-wheel"
          onPointerDown={(event) => {
            setDragging(true);
            event.currentTarget.setPointerCapture(
              event.pointerId
            );
            updateFromPointer(event);
          }}
          onPointerMove={(event) => {
            if (dragging) {
              updateFromPointer(event);
            }
          }}
          onPointerUp={() => {
            setDragging(false);
          }}
          onPointerCancel={() => {
            setDragging(false);
          }}
        >

          <div
            className="assistant-colour-wheel-handle"
            style={{
              left: `${handleX}%`,
              top: `${handleY}%`,
            }}
          />

          <div
            className="assistant-colour-preview"
            style={{
              background: value,
            }}
          />

        </div>

      </div>


      <input
        className="assistant-colour-hex"
        type="text"
        value={value}
        onChange={(event) => {
          const next =
            event.target.value;

          if (
            /^#[0-9a-fA-F]{6}$/.test(
              next
            )
          ) {
            onChange(
              next.toLowerCase()
            );
          } else {
            onChange(next);
          }
        }}
        spellCheck={false}
      />

    </div>
  );
}


  return (

      <main
        className="jarvis-hud"
        style={{
          "--assistant-colour": assistantColour,
        } as React.CSSProperties}
      >

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
        assistantName={assistantName}
        userName={userName}
        morningBriefHeadlines={morningBriefHeadlines}
        onMorningBriefClose={() => {
          setMorningBriefActive(false);
          setMorningBriefHeadlines([]);
        }}
      />

      {/* =====================================================
          COMMAND INPUT
          ===================================================== */}

      <div className="hud-command-input">

        <div className="hud-command-label">
          ◆ COMMAND INPUT
        </div>

        <div className="hud-command-row">

          <input
            type="text"
            value={commandInput}
            onChange={(event) =>
              setCommandInput(
                event.target.value
              )
            }
            onKeyDown={(event) => {

              if (event.key === "Enter") {

                event.preventDefault();

                void sendHudCommand();

              }

            }}
            placeholder="Type a command or question..."
            autoComplete="off"
            autoCorrect="off"
            spellCheck={false}
            disabled={commandSending}
          />

          <button
            type="button"
            onClick={() =>
              void sendHudCommand()
            }
            disabled={
              commandSending ||
              !commandInput.trim()
            }
            aria-label="Send command"
          >
            ▶
          </button>

        </div>

      </div>

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
              MICROPHONE
              ------------------------------------------------- */}

          <button
            type="button"
            className={
              `settings-control ${
                microphoneEnabled
                  ? "settings-control-toggle-on"
                  : ""
              }`
            }
            onClick={async () => {

              const next =
                !microphoneEnabled;

              setMicrophoneEnabled(next);

              try {

                const response =
                  await fetch(
                    "http://127.0.0.1:8765/api/local/microphone",
                    {
                      method: "POST",
                      headers: {
                        "Content-Type":
                          "application/json",
                      },
                      body: JSON.stringify({
                        enabled: next,
                      }),
                    }
                  );

                const result =
                  await response.json();

                if (
                  !response.ok ||
                  !result.ok
                ) {

                  throw new Error(
                    result.error ||
                    "Failed to update microphone."
                  );

                }

                setMicrophoneEnabled(
                  Boolean(result.enabled)
                );

                console.log(
                  "[HUD] Microphone:",
                  result.enabled
                    ? "ON"
                    : "OFF"
                );

              } catch (error) {

                console.error(
                  "[HUD] Microphone update failed:",
                  error
                );

                setMicrophoneEnabled(
                  !next
                );

              }

            }}
          >

            <span className="settings-control-icon">
              ●
            </span>

            <span>
              MICROPHONE:
            </span>

            <strong>
              {microphoneEnabled
                ? "ON"
                : "OFF"}
            </strong>

          </button>

          {/* -------------------------------------------------
              LIVE CONVERSATION
              ------------------------------------------------- */}

          <button
            type="button"
            className={
              `settings-control ${
                liveConversationEnabled
                  ? "settings-control-toggle-on"
                  : ""
              }`
            }
            onClick={async () => {

              const next =
                !liveConversationEnabled;

              setLiveConversationEnabled(next);

              try {

                const response =
                  await fetch(
                    `http://127.0.0.1:8765/api/live/${
                      next
                        ? "start"
                        : "stop"
                    }`,
                    {
                      method: "POST",
                      cache: "no-store",
                    }
                  );

                const result =
                  await response.json();

                if (
                  !response.ok ||
                  !result.ok
                ) {

                  throw new Error(
                    result.error ||
                    "Failed to update Live Conversation."
                  );

                }

                setLiveConversationEnabled(
                  next
                );

                console.log(
                  "[HUD] Live Conversation:",
                  next
                    ? "ON"
                    : "OFF"
                );

              } catch (error) {

                console.error(
                  "[HUD] Live Conversation update failed:",
                  error
                );

                setLiveConversationEnabled(
                  !next
                );

              }

            }}
          >

            <span className="settings-control-icon">
              ●
            </span>

            <span>
              LIVE CONVERSATION:
            </span>

            <strong>
              {liveConversationEnabled
                ? "ON"
                : "OFF"}
            </strong>

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


              <AssistantColourPicker
                value={assistantColour}
                onChange={setAssistantColour}
              />

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