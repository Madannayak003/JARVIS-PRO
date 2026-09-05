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
  speaker: "user" | "jarvis" | "system";
  text: string;
  timestamp: string;
};

type SettingsModal = "remote" | "customise" | null;

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
  (typeof window !== "undefined"
    ? `http://${window.location.hostname}:8765`
    : "http://127.0.0.1:8765");

export default function Home() {
  const [hudState, setHudState] = useState<HUDState>(EMPTY_STATE);
  const [connection, setConnection] = useState<HUDConnectionStatus>("connecting");
  const [activities, setActivities] = useState<HUDActivity[]>([]);
  const [waveformLevels, setWaveformLevels] =
    useState<number[]>(Array(16).fill(0));

  const [morningBriefHeadlines, setMorningBriefHeadlines] = useState<
    Array<{
      category: string;
      title: string;
      link?: string;
    }>
  >([]);

  const [morningBriefActive, setMorningBriefActive] = useState(false);
  const [morningBriefStartedSpeaking, setMorningBriefStartedSpeaking] = useState(false);

  const morningBriefActiveRef = useRef(false);
  const morningBriefStartedSpeakingRef = useRef(false);
  const pendingHudCommandsRef = useRef<string[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const microphoneStreamRef = useRef<MediaStream | null>(null);
  const waveformFrameRef = useRef<number | null>(null);
  const waveformLevelsRef = useRef<number[]>([]);

  /* =========================================================
     SETTINGS & MODAL STATE
     ========================================================= */
  const [modal, setModal] = useState<SettingsModal>(null);
  const [autoStart, setAutoStart] = useState(false);
  const [morningBrief, setMorningBrief] = useState(true);
  const [microphoneEnabled, setMicrophoneEnabled] = useState(true);
  const [liveConversationEnabled, setLiveConversationEnabled] = useState(false);

  const [assistantName, setAssistantName] = useState("JARVIS");
  const [userName, setUserName] = useState("MADAN.R");
  const [assistantColour, setAssistantColour] = useState("#ffaa30");

  const [remoteInfo, setRemoteInfo] = useState<RemoteInfo | null>(null);
  const [remoteLoading, setRemoteLoading] = useState(false);
  const [shortcutLoading, setShortcutLoading] = useState(false);

  const [commandInput, setCommandInput] = useState("");
  const [commandSending, setCommandSending] = useState(false);

  /* =========================================================
     LOAD SETTINGS
     ========================================================= */
  useEffect(() => {
    let isMounted = true;

    try {
      const saved = window.localStorage.getItem("jarvis-pro-settings");
      if (saved) {
        const settings = JSON.parse(saved);
        if (typeof settings.autoStart === "boolean") setAutoStart(settings.autoStart);
        if (typeof settings.morningBrief === "boolean") setMorningBrief(settings.morningBrief);
        if (typeof settings.assistantName === "string") setAssistantName(settings.assistantName);
        if (typeof settings.userName === "string") setUserName(settings.userName);
        if (typeof settings.assistantColour === "string") {
          setAssistantColour(settings.assistantColour);
          document.documentElement.style.setProperty("--assistant-colour", settings.assistantColour);
        }
      }
    } catch (error) {
      console.error("[HUD] Local settings fallback failed:", error);
    }

    const loadWithRetry = async (fn: () => Promise<void>, retries = 5, delay = 1000) => {
      for (let i = 0; i < retries; i++) {
        if (!isMounted) return;
        try {
          await fn();
          return;
        } catch {
          await new Promise((res) => setTimeout(res, delay));
        }
      }
    };

    loadWithRetry(async () => {
      const res = await fetch(`${JARVIS_DASHBOARD_URL}/api/local/customise`, { cache: "no-store" });
      if (res.ok) {
        const data = await res.json();
        if (data.ok && isMounted) {
          if (data.assistantName) setAssistantName(data.assistantName);
          if (data.userName) setUserName(data.userName);
          if (data.assistantColour) {
            setAssistantColour(data.assistantColour);
            document.documentElement.style.setProperty("--assistant-colour", data.assistantColour);
          }
        }
      }
    });

    loadWithRetry(async () => {
      const res = await fetch(`${JARVIS_DASHBOARD_URL}/api/local/autostart`, { cache: "no-store" });
      if (res.ok) {
        const data = await res.json();
        if (data.ok && isMounted) setAutoStart(data.enabled);
      }
    });

    loadWithRetry(async () => {
      const res = await fetch(`${JARVIS_DASHBOARD_URL}/api/local/microphone`, { cache: "no-store" });
      if (res.ok) {
        const data = await res.json();
        if (data.ok && isMounted) setMicrophoneEnabled(data.enabled);
      }
    });

    return () => {
      isMounted = false;
    };
  }, []);

  /* =========================================================
     MICROPHONE STATUS & SYNC
     ========================================================= */
  useEffect(() => {
    let isMounted = true;

    const syncMicrophone = async () => {
      if (!isMounted) return;
      try {
        const response = await fetch(`${JARVIS_DASHBOARD_URL}/api/local/microphone`, {
          cache: "no-store",
        });
        const result = await response.json();
        if (response.ok && result.ok && typeof result.enabled === "boolean" && isMounted) {
          setMicrophoneEnabled(result.enabled);
        }
      } catch {}
    };

    const initialTimeout = window.setTimeout(syncMicrophone, 1500);
    const syncInterval = window.setInterval(syncMicrophone, 3000);

    return () => {
      isMounted = false;
      window.clearTimeout(initialTimeout);
      window.clearInterval(syncInterval);
    };
  }, []);

  /* =========================================================
   LIVE MICROPHONE WAVEFORM ANALYSER
   ========================================================= */
  useEffect(() => {
    let cancelled = false;

    const startWaveformAnalyser = async () => {
      try {
        if (cancelled) return;

        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
        });

        if (cancelled) {
          stream.getTracks().forEach((track) => track.stop());
          return;
        }

        microphoneStreamRef.current = stream;

        const AudioContextClass =
          window.AudioContext ||
          (window as typeof window & {
            webkitAudioContext?: typeof AudioContext;
          }).webkitAudioContext;

        if (!AudioContextClass) return;

        const audioContext = new AudioContextClass();
        const analyser = audioContext.createAnalyser();

        analyser.fftSize = 256;
        analyser.smoothingTimeConstant = 0.72;

        const source =
          audioContext.createMediaStreamSource(stream);

        source.connect(analyser);

        audioContextRef.current = audioContext;
        analyserRef.current = analyser;

        const data = new Uint8Array(analyser.fftSize);

        const updateWaveform = () => {
          if (cancelled) return;

          const currentAnalyser = analyserRef.current;

          if (!currentAnalyser) return;

          currentAnalyser.getByteTimeDomainData(data);

          let sum = 0;

          for (let i = 0; i < data.length; i++) {
            const normalized =
              (data[i] - 128) / 128;

            sum += normalized * normalized;
          }

          const rms = Math.sqrt(sum / data.length);

          const level = Math.min(
            1,
            Math.max(0, rms * 5.5)
          );

          const levels = Array.from(
            { length: 16 },
            (_, index) => {
              const centerDistance =
                Math.abs(index - 7.5) / 7.5;

              const falloff =
                1 - centerDistance * 0.45;

              const variation =
                0.82 +
                Math.sin(
                  performance.now() * 0.012 +
                  index * 0.9
                ) * 0.18;

              return Math.min(
                1,
                level * falloff * variation
              );
            }
          );

          waveformLevelsRef.current = levels;
          setWaveformLevels(levels);

          waveformFrameRef.current =
            requestAnimationFrame(updateWaveform);
          };

        updateWaveform();
      } catch (error) {
        console.warn(
          "[HUD WAVEFORM] Microphone analyser unavailable:",
          error
        );
      }
    };

    startWaveformAnalyser();

    return () => {
      cancelled = true;

      if (waveformFrameRef.current !== null) {
        cancelAnimationFrame(
          waveformFrameRef.current
        );
        waveformFrameRef.current = null;
      }

      microphoneStreamRef.current
        ?.getTracks()
        .forEach((track) => track.stop());

      microphoneStreamRef.current = null;

      void audioContextRef.current?.close();

      audioContextRef.current = null;
      analyserRef.current = null;
    };
  }, []);

  /* =========================================================
     MORNING BRIEF STATUS SYNC
     ========================================================= */
  useEffect(() => {
    let cancelled = false;

    const loadMorningBrief = async () => {
      if (cancelled) return;
      try {
        const response = await fetch(`${JARVIS_DASHBOARD_URL}/api/local/morning-brief`, {
          cache: "no-store",
        });
        const result = await response.json();
        if (response.ok && result.ok && typeof result.enabled === "boolean" && !cancelled) {
          setMorningBrief(result.enabled);
        }
      } catch {}
    };

    loadMorningBrief();
    const syncTimer = window.setInterval(loadMorningBrief, 1000);

    return () => {
      cancelled = true;
      window.clearInterval(syncTimer);
    };
  }, []);

  /* =========================================================
     LIVE CONVERSATION STATUS SYNC
     ========================================================= */
  useEffect(() => {
    let cancelled = false;

    const loadLiveConversation = async () => {
      if (cancelled) return;
      try {
        const response = await fetch(`${JARVIS_DASHBOARD_URL}/api/live/status`, {
          cache: "no-store",
        });
        const result = await response.json();
        if (response.ok && result.ok && typeof result.running === "boolean" && !cancelled) {
          setLiveConversationEnabled(result.running);
        }
      } catch {}
    };

    loadLiveConversation();
    const syncTimer = window.setInterval(loadLiveConversation, 1000);

    return () => {
      cancelled = true;
      window.clearInterval(syncTimer);
    };
  }, []);

  /* =========================================================
     HUD SSE CONNECTION (STRICT DEDUPLICATION)
     ========================================================= */
  useEffect(() => {
    let speakTimer: number | null = null;

    const stopHudSpeaking = () => {
      // End the temporary morning-brief speaking lock.
      // The brief overlay can remain visible, but speech itself
      // must no longer keep the HUD in SPEAKING state.
      setMorningBriefStartedSpeaking(false);
      morningBriefStartedSpeakingRef.current = false;

      setHudState((prev) => ({
        ...prev,
        speaking: false,
        status: prev.listening ? "listening" : "idle",
      }));
    };

    const scheduleHudSpeakingStop = (delay: number) => {
      if (speakTimer !== null) {
        window.clearTimeout(speakTimer);
      }

      speakTimer = window.setTimeout(() => {
        speakTimer = null;
        stopHudSpeaking();
      }, delay);
  };

    const bridge = new HUDBridge(
      process.env.NEXT_PUBLIC_JARVIS_HUD_BRIDGE_URL || "http://127.0.0.1:8766",
      setHudState,
      (event: HUDBridgeEvent) => {
        if (event.name === "morning_brief") {
          const headlines = Array.isArray(event.data?.headlines) ? event.data.headlines : [];
          if (headlines.length > 0) {
            setMorningBriefHeadlines(headlines);
            setMorningBriefActive(true);
            setMorningBriefStartedSpeaking(false);
            morningBriefActiveRef.current = true;
            morningBriefStartedSpeakingRef.current = false;
          }
          return;
        }

        if (event.name === "speaking") {
          if (morningBriefActiveRef.current) {
          setMorningBriefStartedSpeaking(true);
          morningBriefStartedSpeakingRef.current = true;

          // Morning Brief can contain several headlines and may
          // speak for much longer than the normal response window.
          // Do NOT use the normal fixed speaking timer here.
          setHudState((prev) => ({
            ...prev,
            speaking: true,
            status: "speaking",
          }));

          return;
        }

        setHudState((prev) => ({
          ...prev,
          speaking: true,
          status: "speaking",
        }));

        scheduleHudSpeakingStop(7000);

        return;
        }

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

        const text = String(
          event.name === "system_activity"
            ? event.data?.message ?? ""
            : event.data?.text ?? ""
        ).trim();

        if (!text) return;

        // Consume pending user command marker to prevent duplicate logs
        if (speaker === "user") {
          const pendingIndex = pendingHudCommandsRef.current.indexOf(text);
          if (pendingIndex !== -1) {
            pendingHudCommandsRef.current.splice(pendingIndex, 1);
            return;
          }
        }

        if (speaker === "jarvis") {
          setHudState((prev) => ({
            ...prev,
            speaking: true,
            status: "speaking",
          }));

          // Each new response chunk extends the speaking window.
          // The HUD returns to idle/listening only after speech
          // activity has stopped for the full delay.
          scheduleHudSpeakingStop(4000);
        }

        // Strict global deduplication check
        setActivities((previous) => {
          const isDuplicate = previous.some(
            (item) => item.text === text && item.speaker === speaker
          );

          if (isDuplicate) {
            return previous;
          }

          const activity: HUDActivity = {
            id: `${event.timestamp}-${Math.random()}`,
            speaker,
            text,
            timestamp: event.timestamp,
          };

          return [...previous, activity].slice(-30);
        });
      },
      setConnection
    );

    bridge.connect();

    return () => {
      bridge.disconnect();

      if (speakTimer !== null) {
        window.clearTimeout(speakTimer);
        speakTimer = null;
      }
    };
  }, []);

  /* =========================================================
     3D AVATAR STATE DISPATCHER (CONTINUOUS SPEECH LOCK)
     ========================================================= */
  useEffect(() => {
    let state: "idle" | "listening" | "thinking" | "speaking" | "executing" = "idle";

    const isSpeaking = 
      hudState.speaking || 
      morningBriefStartedSpeaking || 
      hudState.status === "speaking";

    if (isSpeaking) {
      state = "speaking";
    } else if (hudState.thinking || hudState.status === "thinking") {
      state = "thinking";
    } else if (hudState.executing) {
      state = "executing";
    } else if (hudState.listening || hudState.status === "listening") {
      state = "listening";
    }

    window.dispatchEvent(
      new CustomEvent("jarvis-assistant-state", {
        detail: { state, speaking: isSpeaking },
      })
    );
  }, [
    hudState.speaking,
    hudState.status,
    hudState.thinking,
    hudState.executing,
    hudState.listening,
    morningBriefStartedSpeaking,
  ]);

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
    } catch {}
  };

  /* =========================================================
     DESKTOP SHORTCUT
     ========================================================= */
  const createDesktopShortcut = async () => {
    if (shortcutLoading) return;
    setShortcutLoading(true);

    try {
      const dashboardUrl =
        process.env.NEXT_PUBLIC_JARVIS_DASHBOARD_URL ||
        (typeof window !== "undefined"
          ? `http://${window.location.hostname}:8765`
          : "http://127.0.0.1:8765");

      const response = await fetch(`${dashboardUrl}/api/local/shortcut`, {
        method: "POST",
        cache: "no-store",
      });
      const data = await response.json();

      if (!response.ok || !data.ok) {
        throw new Error(data?.error || "Unable to create desktop shortcut.");
      }

      alert(data.message || "JARVIS PRO desktop shortcut created successfully.");
    } catch (error) {
      console.error("[DESKTOP SHORTCUT]", error);
      alert(error instanceof Error ? error.message : "Desktop shortcut creation failed.");
    } finally {
      setShortcutLoading(false);
    }
  };

  /* =========================================================
    HUD COMMAND INPUT — INSTANT LOG UPDATE WITH RETRY
  ========================================================= */
  const sendHudCommand = async (
    directCommand?: string
  ) => {
    const text =
      (directCommand ?? commandInput).trim();

    if (!text || commandSending) {
      return;
    }

    setCommandSending(true);
    setCommandInput("");

    pendingHudCommandsRef.current.push(text);

    const userActivity: HUDActivity = {
      id: `hud-command-${Date.now()}-${Math.random()}`,
      speaker: "user",
      text,
      timestamp: new Date().toISOString(),
    };

    setActivities((previous) => [
      ...previous,
      userActivity,
    ].slice(-30));

    const currentHost =
      typeof window !== "undefined"
        ? window.location.hostname
        : "127.0.0.1";

    const dashboardEndpoint = `http://${currentHost}:8765/api/command`;

    let success = false;
    let lastError = "Command could not be processed by backend.";

    for (let attempt = 0; attempt < 3; attempt++) {
      try {
        const response = await fetch(
          dashboardEndpoint,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            cache: "no-store",
            body: JSON.stringify({
              command: text,
              text: text,
            }),
          }
        );

        const result = await response.json();

        if (response.ok && result.ok) {
          success = true;
          break;
        }

        lastError = result?.error || result?.message || lastError;
      } catch (error) {
        lastError = error instanceof Error ? error.message : "Network error";
        await new Promise((resolve) => setTimeout(resolve, 600));
      }
    }

    if (!success) {
      console.error("[HUD COMMAND ERROR]", lastError);
      const errorActivity: HUDActivity = {
        id: `${Date.now()}-${Math.random()}`,
        speaker: "system",
        text: `COMMAND FAILED: ${lastError}`,
        timestamp: new Date().toISOString(),
      };
      setActivities((previous) => [...previous, errorActivity].slice(-30));
    }

    const pendingIndex = pendingHudCommandsRef.current.indexOf(text);
    if (pendingIndex !== -1) {
      pendingHudCommandsRef.current.splice(pendingIndex, 1);
    }

    setCommandSending(false);
  };

  /* =========================================================
     REMOTE CONTROL
     ========================================================= */
  const openRemoteControl = async () => {
    setModal("remote");
    setRemoteLoading(true);

    try {
      const bridgeUrl =
        process.env.NEXT_PUBLIC_JARVIS_DASHBOARD_URL ||
        (typeof window !== "undefined"
          ? `http://${window.location.hostname}:8765`
          : "http://127.0.0.1:8765");

      const response = await fetch(`${bridgeUrl}/api/info`, {
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error("Remote information unavailable");
      }

      const data = (await response.json()) as RemoteInfo;
      setRemoteInfo(data);
    } catch {
      setRemoteInfo(null);
    } finally {
      setRemoteLoading(false);
    }
  };

  /* =========================================================
     CUSTOMISE ASSISTANT MODAL
     ========================================================= */
  const openCustomise = () => {
    setModal("customise");
  };

  const applyAssistantSettings = async () => {
    const name = assistantName.trim() || "JARVIS";
    const user = userName.trim();
    const colour = /^#[0-9a-fA-F]{6}$/.test(assistantColour)
      ? assistantColour.toLowerCase()
      : "#ffaa30";

    setAssistantName(name);
    setUserName(user);
    setAssistantColour(colour);

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
      console.error("[HUD] Local settings cache failed:", error);
    }

    try {
      const response = await fetch(`${JARVIS_DASHBOARD_URL}/api/local/customise`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
        body: JSON.stringify({
          assistantName: name,
          userName: user,
          assistantColour: colour,
        }),
      });

      const result = await response.json();
      if (!response.ok || !result.ok) {
        throw new Error(result?.error || "Failed to save assistant settings.");
      }

      if (typeof result.settings?.assistantName === "string") {
        setAssistantName(result.settings.assistantName);
      }
      if (typeof result.settings?.userName === "string") {
        setUserName(result.settings.userName);
      }
      if (typeof result.settings?.assistantColour === "string") {
        setAssistantColour(result.settings.assistantColour);
      }

      setModal(null);
    } catch (error) {
      console.error("[HUD] Assistant settings save failed:", error);
      alert(error instanceof Error ? error.message : "Could not save assistant settings.");
    }
  };

  function AssistantColourPicker({
    value,
    onChange,
  }: {
    value: string;
    onChange: (value: string) => void;
  }) {
    const wheelRef = useRef<HTMLDivElement | null>(null);

    function hexToRgb(hex: string) {
      const clean = hex.replace("#", "");
      if (!/^[0-9a-fA-F]{6}$/.test(clean)) return null;
      return {
        r: parseInt(clean.slice(0, 2), 16),
        g: parseInt(clean.slice(2, 4), 16),
        b: parseInt(clean.slice(4, 6), 16),
      };
    }

    function rgbToHsv(r: number, g: number, b: number) {
      r /= 255; g /= 255; b /= 255;
      const max = Math.max(r, g, b), min = Math.min(r, g, b);
      const delta = max - min;
      let h = 0;
      if (delta !== 0) {
        if (max === r) h = ((g - b) / delta) % 6;
        else if (max === g) h = (b - r) / delta + 2;
        else h = (r - g) / delta + 4;
        h *= 60;
        if (h < 0) h += 360;
      }
      const s = max === 0 ? 0 : delta / max;
      return { h, s, v: max };
    }

    function hsvToHex(h: number, s: number, v: number) {
      const c = v * s;
      const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
      const m = v - c;
      let r = 0, g = 0, b = 0;
      if (h < 60) { r = c; g = x; }
      else if (h < 120) { r = x; g = c; }
      else if (h < 180) { g = c; b = x; }
      else if (h < 240) { g = x; b = c; }
      else if (h < 300) { r = x; g = c; }
      else { r = c; b = x; }

      const toHex = (n: number) =>
        Math.round(Math.max(0, Math.min(1, n + m)) * 255).toString(16).padStart(2, "0");
      return "#" + toHex(r) + toHex(g) + toHex(b);
    }

    const rgb = hexToRgb(value);
    const hsv = rgb ? rgbToHsv(rgb.r, rgb.g, rgb.b) : { h: 35, s: 1, v: 1 };
    
    // Top-aligned angle offset (-90 deg) to match CSS conic-gradient orientation
    const angle = ((hsv.h - 90) * Math.PI) / 180;
    const radius = 38;
    const handleX = 50 + Math.cos(angle) * radius * Math.max(0.4, hsv.s);
    const handleY = 50 + Math.sin(angle) * radius * Math.max(0.4, hsv.s);

    function updateFromPointer(clientX: number, clientY: number) {
      const wheel = wheelRef.current;
      if (!wheel) return;
      const rect = wheel.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      
      const x = clientX - centerX;
      const y = clientY - centerY;
      const distance = Math.hypot(x, y);
      const maxRadius = rect.width / 2;
      
      // Compute angle and offset by +90 deg so Red is at 12 o'clock (0 deg)
      let hue = Math.atan2(y, x) * (180 / Math.PI) + 90;
      if (hue < 0) hue += 360;
      if (hue >= 360) hue -= 360;

      const saturation = Math.min(1, Math.max(0.1, distance / maxRadius));
      onChange(hsvToHex(hue, saturation, 1));
    }

    const resetToDefault = (e: React.SyntheticEvent) => {
      e.preventDefault();
      e.stopPropagation();
      const DEFAULT_COLOR = "#ffaa30";
      onChange(DEFAULT_COLOR);
      setAssistantColour(DEFAULT_COLOR);
      document.documentElement.style.setProperty("--assistant-colour", DEFAULT_COLOR);
    };

    return (
      <div className="assistant-colour-picker" style={{ position: "relative", zIndex: 10 }}>
        <div className="assistant-colour-heading" style={{ position: "relative", zIndex: 20 }}>
          <div>
            <span>UI COLOUR</span>
            <small>choose HUD accent colour</small>
          </div>
          <button
            type="button"
            className="assistant-colour-default"
            style={{
              position: "relative",
              zIndex: 30,
              cursor: "pointer",
              pointerEvents: "auto",
            }}
            onPointerDown={resetToDefault}
            onClick={resetToDefault}
          >
            DEFAULT
          </button>
        </div>

        <div className="assistant-colour-wheel-area" style={{ position: "relative", zIndex: 10 }}>
          <div
            ref={wheelRef}
            className="assistant-colour-wheel"
            onPointerDown={(event) => {
              event.currentTarget.setPointerCapture(event.pointerId);
              updateFromPointer(event.clientX, event.clientY);
            }}
            onPointerMove={(event) => {
              if (event.buttons === 1) {
                updateFromPointer(event.clientX, event.clientY);
              }
            }}
            onPointerUp={(event) => {
              try {
                event.currentTarget.releasePointerCapture(event.pointerId);
              } catch {}
            }}
          >
            <div
              className="assistant-colour-wheel-handle"
              style={{ left: `${handleX}%`, top: `${handleY}%`, pointerEvents: "none" }}
            />
            <div
              className="assistant-colour-preview"
              style={{ background: value, pointerEvents: "none" }}
            />
          </div>
        </div>

        <input
          className="assistant-colour-hex"
          type="text"
          value={value}
          onChange={(event) => {
            const next = event.target.value;
            if (/^#[0-9a-fA-F]{6}$/.test(next)) {
              onChange(next.toLowerCase());
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
          setMorningBriefStartedSpeaking(false);
          morningBriefActiveRef.current = false;
          morningBriefStartedSpeakingRef.current = false;
        }}

        onCommand={(command) => {
          void sendHudCommand(command);
        }}

        onFullscreen={toggleFullscreen}

        onSettings={() => {
          setModal("customise");
        }}
      />

      {/* =====================================================
          COMMAND INPUT
          ===================================================== */}
      <div className="hud-command-input">
        <div className="hud-command-label">◆ COMMAND INPUT</div>
        <div className="hud-command-row">
          <input
            type="text"
            value={commandInput}
            onChange={(event) => setCommandInput(event.target.value)}
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
            onClick={() => void sendHudCommand()}
            disabled={commandSending || !commandInput.trim()}
            aria-label="Send command"
          >
            ▶
          </button>
        </div>
      </div>

      {/* =====================================================
          MORNING BRIEF OVERLAY
          ===================================================== */}
      {morningBriefActive && morningBriefHeadlines.length > 0 && (
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
            <span className="morning-brief-marker">◆</span>
            <span>TODAY'S TOP HEADLINES</span>
          </div>
          <div className="morning-brief-list">
            {morningBriefHeadlines.map((headline, index) => (
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
            ))}
          </div>
        </div>
      )}

      {/* =====================================================
          CONNECTION
          ===================================================== */}
      <div className="hud-bridge-status">
        <span
          className={`hud-bridge-dot ${connection}`}
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
          BOTTOM HUD: INDICATORS + WAVEFORM + 8 INLINE BUTTONS
          ===================================================== */}
      <div className="cockpit-bottom-container">
        {/* RUNTIME INDICATORS WITH BRACKETS & GLOW DOTS */}
        <div className="cockpit-bottom-indicators">
          <div
            className={`voice-indicator ${
              hudState.listening &&
              !hudState.speaking &&
              hudState.status !== "speaking" &&
              !morningBriefStartedSpeaking
                ? "active"
                : ""
            }`}
          >
            <span className="indicator-dot" />
            <span className="indicator-label">[ LISTENING ]</span>
          </div>
          <div className={`voice-indicator ${hudState.thinking ? "active" : ""}`}>
            <span className="indicator-dot" />
            <span className="indicator-label">[ THINKING ]</span>
          </div>
          <div
            className={`voice-indicator ${
              hudState.speaking ||
              hudState.status === "speaking" ||
              morningBriefStartedSpeaking
                ? "active"
                : ""
            }`}
          >
            <span className="indicator-dot" />
            <span className="indicator-label">[ SPEAKING ]</span>
          </div>
          <div className={`voice-indicator ${hudState.executing ? "active" : ""}`}>
            <span className="indicator-dot" />
            <span className="indicator-label">[ EXECUTING ]</span>
          </div>
        </div>

        {/* REACTIVE AUDIO WAVEFORM / SPECTRUM VISUALIZER */}
        <div
          className={`hud-waveform ${
            hudState.listening &&
            !hudState.speaking &&
            hudState.status !== "speaking"
              ? "waveform-live"
              : ""
          }`}
          aria-hidden="true"
        >
          {Array.from({ length: 16 }, (_, index) => {
            const level =
              waveformLevels[index] ?? 0;

            const active =
              hudState.listening &&
              !hudState.speaking &&
              hudState.status !== "speaking";

            const height = active
              ? `${Math.max(2, level * 24)}px`
              : "2px";

            return (
              <span
                key={index}
                className="wave-bar"
                style={{
                  height,
                  transition:
                    "height 70ms linear",
                }}
              />
            );
          })}
        </div>

        {/* ALL 8 BUTTONS IN ONE TRANSPARENT INLINE ROW */}
        <nav className="hud-bottom-toolbar" aria-label="HUD Cockpit Controls">
          <button type="button" className="hud-bar-btn" onClick={openRemoteControl}>
            <span className="btn-icon">⚙</span>
            <span>REMOTE</span>
          </button>

          <button type="button" className="hud-bar-btn" onClick={toggleFullscreen}>
            <span className="btn-icon">⛶</span>
            <span>FULLSCREEN</span>
          </button>

          <button
            type="button"
            className={`hud-bar-btn ${microphoneEnabled ? "is-active" : ""}`}
            onClick={async () => {
              const next = !microphoneEnabled;
              setMicrophoneEnabled(next);
              try {
                const res = await fetch(`${JARVIS_DASHBOARD_URL}/api/local/microphone`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ enabled: next }),
                });
                const result = await res.json();
                if (!res.ok || !result.ok) throw new Error(result.error);
                setMicrophoneEnabled(Boolean(result.enabled));
              } catch (err) {
                console.error(err);
                setMicrophoneEnabled(!next);
              }
            }}
          >
            <span className="btn-icon">🎙</span>
            <span>MIC {microphoneEnabled ? "ON" : "OFF"}</span>
          </button>

          <button
            type="button"
            className={`hud-bar-btn ${liveConversationEnabled ? "is-active" : ""}`}
            onClick={async () => {
              const next = !liveConversationEnabled;
              setLiveConversationEnabled(next);
              try {
                const res = await fetch(
                  `${JARVIS_DASHBOARD_URL}/api/live/${next ? "start" : "stop"}`,
                  { method: "POST", cache: "no-store" }
                );
                const result = await res.json();
                if (!res.ok || !result.ok) throw new Error(result.error);
                setLiveConversationEnabled(next);
              } catch (err) {
                console.error(err);
                setLiveConversationEnabled(!next);
              }
            }}
          >
            <span className="btn-icon">◉</span>
            <span>LIVE {liveConversationEnabled ? "ON" : "OFF"}</span>
          </button>

          <button
            type="button"
            className={`hud-bar-btn ${morningBrief ? "is-active" : ""}`}
            onClick={async () => {
              const next = !morningBrief;
              setMorningBrief(next);
              try {
                const res = await fetch(`${JARVIS_DASHBOARD_URL}/api/local/morning-brief`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ enabled: next }),
                });
                const result = await res.json();
                if (!res.ok || !result.ok) throw new Error(result.error);
              } catch (err) {
                console.error(err);
                setMorningBrief(!next);
              }
            }}
          >
            <span className="btn-icon">☀</span>
            <span>BRIEF {morningBrief ? "ON" : "OFF"}</span>
          </button>

          <button
            type="button"
            className={`hud-bar-btn ${autoStart ? "is-active" : ""}`}
            onClick={() => {
              const next = !autoStart;
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
            <span className="btn-icon">⚡</span>
            <span>AUTO-START {autoStart ? "ON" : "OFF"}</span>
          </button>

          <button
            type="button"
            className="hud-bar-btn"
            onClick={createDesktopShortcut}
            disabled={shortcutLoading}
          >
            <span className="btn-icon">🔗</span>
            <span>{shortcutLoading ? "SHORTCUT..." : "SHORTCUT"}</span>
          </button>

          <button type="button" className="hud-bar-btn" onClick={openCustomise}>
            <span className="btn-icon">🛠</span>
            <span>CUSTOMISE</span>
          </button>
        </nav>
      </div>

      {/* =====================================================
          REMOTE CONTROL MODAL
          ===================================================== */}
      {modal === "remote" && (
        <div
          className="settings-modal-backdrop"
          onClick={() => setModal(null)}
        >
          <section
            className="settings-modal remote-modal"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="settings-modal-heading">
              <span>◆</span>
              REMOTE ACCESS
            </div>

            <div className="remote-modal-content">
              <div className="remote-title">JARVIS PRO REMOTE</div>
              <p className="remote-description">Scan to connect your device</p>

              {remoteLoading ? (
                <div className="remote-loading">CONNECTING TO JARVIS...</div>
              ) : remoteInfo?.pairing_active && remoteInfo.pairing_url ? (
                <>
                  <div className="remote-qr-wrapper">
                    <div className="remote-qr">
                      <QRCodeSVG
                        value={remoteInfo.pairing_url}
                        size={220}
                        bgColor="#050505"
                        fgColor="#ffcc66"
                        level="M"
                        includeMargin
                      />
                    </div>
                    <div className="remote-qr-label">SCAN TO CONNECT</div>
                  </div>

                  <div className="remote-pin-box">
                    <span className="remote-pin-label">PAIRING PIN</span>
                    <strong className="remote-pin">{remoteInfo.pairing_pin}</strong>
                  </div>

                  <div className="remote-status-box">
                    <span>JARVIS DASHBOARD</span>
                    <strong>{remoteInfo.url}</strong>
                  </div>
                </>
              ) : (
                <div className="remote-offline">
                  <strong>PAIRING NOT AVAILABLE</strong>
                  <span>Start the JARVIS dashboard and open Remote Control again.</span>
                </div>
              )}

              <p className="remote-note">
                Scan the QR code with your phone. Your device will open the JARVIS remote pairing page.
              </p>

              <div className="settings-modal-actions">
                <button
                  type="button"
                  className="settings-modal-button settings-modal-button-primary"
                  onClick={() => {
                    const url = remoteInfo?.pairing_url || remoteInfo?.url;
                    if (!url) return;
                    window.open(url, "_blank", "noopener,noreferrer");
                  }}
                  disabled={!remoteInfo}
                >
                  OPEN REMOTE
                </button>
                <button
                  type="button"
                  className="settings-modal-button"
                  onClick={() => setModal(null)}
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
          onClick={() => setModal(null)}
        >
          <section
            className="settings-modal customise-modal"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="settings-modal-heading">
              <span>⚙</span>
              CUSTOMISE ASSISTANT
            </div>

            <div className="customise-form">
              <label>
                ASSISTANT NAME
                <input
                  type="text"
                  value={assistantName}
                  onChange={(event) => setAssistantName(event.target.value)}
                  placeholder="JARVIS"
                />
              </label>

              <label>
                YOUR NAME
                <span className="settings-field-help">leave blank for default sir / efendim</span>
                <input
                  type="text"
                  value={userName}
                  onChange={(event) => setUserName(event.target.value)}
                  placeholder="e.g. Tony"
                />
              </label>

              <AssistantColourPicker
                value={assistantColour}
                onChange={(c) => {
                  setAssistantColour(c);
                  document.documentElement.style.setProperty("--assistant-colour", c);
                }}
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
                  onClick={() => setModal(null)}
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