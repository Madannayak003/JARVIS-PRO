"use client";

import { useEffect, useState } from "react";
import JarvisOrb from "@/components/JarvisOrb";
import HudCockpit from "@/components/HudCockpit";
import {
  HUDBridge,
  type HUDConnectionStatus,
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

export default function Home() {
  const [hudState, setHudState] = useState<HUDState>(EMPTY_STATE);
  const [connection, setConnection] =
    useState<HUDConnectionStatus>("connecting");

  useEffect(() => {
    const bridge = new HUDBridge(
      process.env.NEXT_PUBLIC_JARVIS_HUD_BRIDGE_URL ||
        "http://127.0.0.1:8766",
      setHudState,
      undefined,
      setConnection,
    );

    bridge.connect();

    return () => bridge.disconnect();
  }, []);

  return (
    <main className="jarvis-hud">

      {/* ============================================= */}
      {/* ACTUAL ULTRON ENGINE */}
      {/* ============================================= */}

      <div className="ultron-layer">
        <JarvisOrb />
      </div>

      {/* ============================================= */}
      {/* JARVIS COCKPIT */}
      {/* ============================================= */}

      <HudCockpit
        state={hudState}
      />

      {/* ============================================= */}
      {/* CONNECTION */}
      {/* ============================================= */}

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

    </main>
  );
}
