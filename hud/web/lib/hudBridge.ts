/**
 * JARVIS PRO
 * HUD Web Bridge
 *
 * UI-1.6
 *
 * Browser client for the Python HUD SSE bridge.
 *
 * Python JARVIS
 *      ↓
 * HUD Web Bridge
 *      ↓
 * SSE
 *      ↓
 * HUDBridge
 *      ↓
 * Next.js HUD
 */

export type HUDState = {
  status: string;
  voice_mode: string;
  ai_model: string;
  current_task: string;
  task_status: string;

  listening: boolean;
  speaking: boolean;
  thinking: boolean;
  executing: boolean;

  system: Record<string, unknown>;

  notification: string;
  error: string;

  last_event: string;
  last_update: string;
};

export type HUDBridgeEvent = {
  name: string;

  data: Record<string, unknown>;

  timestamp: string;

  source?: string | null;

  state: HUDState;
};

export type HUDConnectionStatus =
  | "connecting"
  | "connected"
  | "offline";


const DEFAULT_URL =
  "http://127.0.0.1:8766";


export class HUDBridge {

  private source: EventSource | null = null;


  constructor(

    private readonly baseUrl =
      DEFAULT_URL,

    private readonly onState?: (
      state: HUDState
    ) => void,

    private readonly onEvent?: (
      event: HUDBridgeEvent
    ) => void,

    private readonly onConnection?: (
      status: HUDConnectionStatus
    ) => void,

  ) {}


  // =========================================================
  // CONNECT
  // =========================================================

  connect(): void {

    this.disconnect();


    this.onConnection?.(
      "connecting"
    );


    const source =
      new EventSource(
        `${this.baseUrl}/events`
      );


    this.source = source;


    // =======================================================
    // CONNECTION OPEN
    // =======================================================

    source.onopen = () => {

      this.onConnection?.(
        "connected"
      );

    };


    // =======================================================
    // INITIAL STATE
    // =======================================================

    source.addEventListener(
      "state",
      (message) => {

        try {

          const state =
            JSON.parse(
              message.data
            ) as HUDState;


          this.onState?.(
            state
          );

        } catch {

          console.warn(
            "[HUD BRIDGE] Invalid state message."
          );

        }

      }
    );


    // =======================================================
    // LIVE HUD EVENT
    // =======================================================

    source.addEventListener(
      "hud",
      (message) => {

        try {

          const event =
            JSON.parse(
              message.data
            ) as HUDBridgeEvent;


          // Update current state.
          this.onState?.(
            event.state
          );


          // Forward complete event.
          this.onEvent?.(
            event
          );

        } catch {

          console.warn(
            "[HUD BRIDGE] Invalid HUD event."
          );

        }

      }
    );


    // =======================================================
    // CONNECTION ERROR
    // =======================================================

    source.onerror = () => {

      this.onConnection?.(
        "offline"
      );

    };

  }


  // =========================================================
  // DISCONNECT
  // =========================================================

  disconnect(): void {

    if (this.source) {

      this.source.close();

      this.source = null;

    }

  }

}