"use client";

import {
  useEffect,
  useState,
} from "react";

import JarvisOrb from "@/components/JarvisOrb";
import HudCockpit from "@/components/HudCockpit";

import {
  HUDBridge,
  type HUDConnectionStatus,
  type HUDState,
  type HUDBridgeEvent,
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

  // =======================================================
  // CURRENT HUD STATE
  // =======================================================

  const [
    hudState,
    setHudState,
  ] = useState<HUDState>(
    EMPTY_STATE
  );


  // =======================================================
  // ACTIVITY HISTORY
  // =======================================================

  const [
    hudEvents,
    setHudEvents,
  ] = useState<HUDBridgeEvent[]>(
    []
  );


  // =======================================================
  // CONNECTION
  // =======================================================

  const [
    connection,
    setConnection,
  ] = useState<HUDConnectionStatus>(
    "connecting"
  );


  // =======================================================
  // HUD CONNECTION
  // =======================================================

  useEffect(() => {

    const bridge = new HUDBridge(

      process.env
        .NEXT_PUBLIC_JARVIS_HUD_BRIDGE_URL ||
        "http://127.0.0.1:8766",


      // ===================================================
      // STATE
      // ===================================================

      (state) => {

        setHudState(
          state
        );

      },


      // ===================================================
      // EVENT
      // ===================================================

      (event) => {

        setHudEvents(
          (previous) => {

            // ---------------------------------------------
            // Never put telemetry updates into activity log.
            // ---------------------------------------------

            if (
              event.name ===
              "system_update"
            ) {

              return previous;

            }


            // ---------------------------------------------
            // Ignore repeated identical events.
            //
            // Example:
            //
            // LISTENING
            // LISTENING
            // LISTENING
            //
            // becomes:
            //
            // LISTENING
            // ---------------------------------------------

            const last =
              previous[
                previous.length - 1
              ];


            if (
              last &&
              last.name === event.name
            ) {

              return previous;

            }


            // ---------------------------------------------
            // Add new event.
            // ---------------------------------------------

            const next = [
              ...previous,
              event,
            ];


            // ---------------------------------------------
            // Keep only latest 25 meaningful events.
            // ---------------------------------------------

            return next.slice(
              -25
            );

          }
        );

      },


      // ===================================================
      // CONNECTION
      // ===================================================

      (status) => {

        setConnection(
          status
        );

      },

    );


    bridge.connect();


    return () => {

      bridge.disconnect();

    };

  }, []);


  // =======================================================
  // UI
  // =======================================================

  return (

    <main className="jarvis-hud">


      {/* ================================================= */}
      {/* ULTRON ENGINE */}
      {/* ================================================= */}

      <div className="ultron-layer">

        <JarvisOrb />

      </div>


      {/* ================================================= */}
      {/* JARVIS COCKPIT */}
      {/* ================================================= */}

      <HudCockpit

        state={hudState}

        events={hudEvents}

      />


      {/* ================================================= */}
      {/* CONNECTION */}
      {/* ================================================= */}

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