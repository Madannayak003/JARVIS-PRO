// "use client";

// import {
//   useCallback,
//   useEffect,
//   useRef,
//   useState,
// } from "react";

// import {
//   createJarvisAvatar,
//   type OrbSceneApi,
// } from "@/lib/jarvisAvatar";

// import {
//   HandTracker,
//   type TrackerStatus,
// } from "@/lib/handTracker";


// type CameraState =
//   | "off"
//   | "starting"
//   | "on"
//   | "error";


// const MODE_LABEL: Record<
//   TrackerStatus["mode"],
//   string
// > = {
//   idle: "STANDBY",
//   spin: "SPIN",
//   zoom: "ZOOM",
// };


// export default function JarvisOrb() {

//   const containerRef =
//     useRef<HTMLDivElement>(null);

//   const videoRef =
//     useRef<HTMLVideoElement>(null);

//   const overlayRef =
//     useRef<HTMLCanvasElement>(null);

//   const sceneRef =
//     useRef<OrbSceneApi | null>(null);

//   const trackerRef =
//     useRef<HandTracker | null>(null);


//   const [camera, setCamera] =
//     useState<CameraState>("off");

//   const [status, setStatus] =
//     useState<TrackerStatus>({
//       hands: 0,
//       mode: "idle",
//     });

//   const [error, setError] =
//     useState<string | null>(null);


//   // =====================================================
//   // ORB INITIALIZATION
//   // =====================================================

//   useEffect(() => {

//     const container =
//       containerRef.current;

//     if (!container) {
//       return;
//     }

//     const scene =
//       createJarvisAvatar(container);

//     sceneRef.current =
//       scene;


//     return () => {

//       trackerRef.current?.stop();

//       trackerRef.current =
//         null;

//       scene.dispose();

//       sceneRef.current =
//         null;

//     };

//   }, []);


//   // =====================================================
//   // STOP GESTURES
//   // =====================================================

//   const stopGestures =
//     useCallback(() => {

//       trackerRef.current?.stop();

//       trackerRef.current =
//         null;

//       setCamera("off");

//       setStatus({
//         hands: 0,
//         mode: "idle",
//       });

//     }, []);


//   // =====================================================
//   // START GESTURES
//   // =====================================================

//   const startGestures =
//     useCallback(async () => {

//       const video =
//         videoRef.current;

//       const overlay =
//         overlayRef.current;


//       if (
//         !video ||
//         !overlay ||
//         trackerRef.current
//       ) {
//         return;
//       }


//       setCamera("starting");

//       setError(null);


//       const tracker =
//         new HandTracker(
//           video,
//           overlay,
//           {
//             onRotate: (dt, dp) =>
//               sceneRef.current?.rotateBy(
//                 dt,
//                 dp
//               ),

//             onZoom: (factor) =>
//               sceneRef.current?.zoomBy(
//                 factor
//               ),

//             onStatus: setStatus,
//           }
//         );


//       trackerRef.current =
//         tracker;


//       try {

//         await tracker.start();

//         setCamera("on");

//       } catch (err) {

//         trackerRef.current =
//           null;

//         tracker.stop();

//         setCamera("error");


//         setError(
//           err instanceof DOMException &&
//           err.name === "NotAllowedError"

//             ? "CAMERA ACCESS DENIED"

//             : "TRACKING INIT FAILED"
//         );

//       }

//     }, []);


//   // =====================================================
//   // GESTURE TOGGLE
//   // =====================================================

//   const toggleGestures =
//     useCallback(() => {

//       if (trackerRef.current) {

//         stopGestures();

//       } else {

//         void startGestures();

//       }

//     }, [
//       startGestures,
//       stopGestures,
//     ]);


//   // =====================================================
//   // KEYBOARD CONTROLS
//   // =====================================================

//   useEffect(() => {

//     const onKey =
//       (e: KeyboardEvent) => {

//         switch (e.key) {

//           case "+":
//           case "=":

//             sceneRef.current?.zoomIn();

//             break;


//           case "-":
//           case "_":

//             sceneRef.current?.zoomOut();

//             break;


//           case "r":
//           case "R":

//             sceneRef.current?.resetView();

//             break;


//           case "g":
//           case "G":

//             toggleGestures();

//             break;

//         }

//       };


//     window.addEventListener(
//       "keydown",
//       onKey
//     );


//     return () => {

//       window.removeEventListener(
//         "keydown",
//         onKey
//       );

//     };

//   }, [toggleGestures]);


//   const cameraOn =
//     camera === "on";


//   return (

//     <main className="jarvis-hud">

//       {/* ============================================= */}
//       {/* ULTRON / JARVIS ORB */}
//       {/* ============================================= */}

//       <div
//         ref={containerRef}
//         className="orb-root"
//       />


//       {/* ============================================= */}
//       {/* VISUAL OVERLAYS */}
//       {/* ============================================= */}

//       <div className="overlay-vignette" />

//       <div className="overlay-grain" />

//       <div className="overlay-scanlines" />

//       {/* ============================================= */}
//       {/* CONTROL HINT */}
//       {/* ============================================= */}

//       <div className="hud hud-hint">

//         <div>

//           <span className="key">
//             DRAG
//           </span>

//           {" "}spin&nbsp;&nbsp;

//           <span className="key">
//             SCROLL
//           </span>

//           {" "}zoom

//         </div>


//         <div>

//           {cameraOn ? (

//             <>
//               <span className="key">
//                 PINCH + MOVE
//               </span>

//               {" "}spin&nbsp;&nbsp;

//               <span className="key">
//                 2 HANDS
//               </span>

//               {" "}zoom
//             </>

//           ) : (

//             <>
//               <span className="key">
//                 G
//               </span>

//               {" "}gestures&nbsp;&nbsp;

//               <span className="key">
//                 R
//               </span>

//               {" "}reset&nbsp;&nbsp;

//               <span className="key">
//                 +/−
//               </span>

//               {" "}zoom
//             </>

//           )}

//         </div>

//       </div>


//       {/* ============================================= */}
//       {/* HUD CONTROLS */}
//       {/* ============================================= */}

//       <div className="hud hud-controls">

//         <div
//           className={
//             `camera-panel${
//               cameraOn
//                 ? " visible"
//                 : ""
//             }`
//           }
//         >
//           {/* Cybernetic view finder corners */}
//           <div className="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-[var(--assistant-colour)] pointer-events-none z-10" />
//           <div className="absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-[var(--assistant-colour)] pointer-events-none z-10" />
//           <div className="absolute bottom-0 left-0 w-2 h-2 border-b-2 border-l-2 border-[var(--assistant-colour)] pointer-events-none z-10" />
//           <div className="absolute bottom-0 right-0 w-2 h-2 border-b-2 border-r-2 border-[var(--assistant-colour)] pointer-events-none z-10" />

//           <video
//             ref={videoRef}
//             muted
//             playsInline
//             className="camera-video"
//           />

//           <canvas
//             ref={overlayRef}
//             width={208}
//             height={156}
//             className="camera-overlay"
//           />

//           <div className="camera-status flex items-center justify-between">
//             <span className="flex items-center gap-1.5">
//               <span className={`w-1.5 h-1.5 rounded-full ${status.hands > 0 ? "bg-[#00ff66] shadow-[0_0_6px_#00ff66]" : "bg-[var(--assistant-colour)] opacity-60"}`} />
//               {status.hands > 0

//                 ? `${status.hands} HAND${
//                     status.hands > 1
//                       ? "S"
//                       : ""
//                   } · ${
//                     MODE_LABEL[
//                       status.mode
//                     ]
//                   }`

//                 : "SCANNING"}
//             </span>
//           </div>

//         </div>


//         {error && (

//           <div className="hud-error">
//             {error}
//           </div>

//         )}


//         <div className="hud-row">

//           <button
//             type="button"
//             className="hud-btn"
//             aria-pressed={cameraOn}
//             onClick={toggleGestures}
//             disabled={
//               camera === "starting"
//             }
//           >

//             {camera === "starting"

//               ? "INITIALIZING…"

//               : cameraOn

//                 ? "● GESTURES ON"

//                 : "○ GESTURES OFF"}

//           </button>

//         </div>


//         <div className="hud-row">

//           <button
//             type="button"
//             className="hud-btn"
//             onClick={() =>
//               sceneRef.current?.zoomIn()
//             }
//             aria-label="Zoom in"
//           >
//             +
//           </button>


//           <button
//             type="button"
//             className="hud-btn"
//             onClick={() =>
//               sceneRef.current?.zoomOut()
//             }
//             aria-label="Zoom out"
//           >
//             −
//           </button>


//           <button
//             type="button"
//             className="hud-btn"
//             onClick={() =>
//               sceneRef.current?.resetView()
//             }
//           >
//             RESET
//           </button>

//         </div>

//       </div>

//     </main>

//   );

// }

"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  createJarvisAvatar,
  type OrbSceneApi,
} from "@/lib/jarvisAvatar";

import {
  createJarvisFullBody,
} from "@/lib/jarvisFullBody";

import {
  createOrbScene,
} from "@/lib/orbScene";

import {
  HandTracker,
  type TrackerStatus,
} from "@/lib/handTracker";


type CameraState =
  | "off"
  | "starting"
  | "on"
  | "error";

type AvatarType =
  | "orb"
  | "robot"
  | "full-body";


const MODE_LABEL: Record<
  TrackerStatus["mode"],
  string
> = {
  idle: "STANDBY",
  spin: "SPIN",
  zoom: "ZOOM",
};


export default function JarvisOrb() {

  const containerRef =
    useRef<HTMLDivElement>(null);

  const videoRef =
    useRef<HTMLVideoElement>(null);

  const overlayRef =
    useRef<HTMLCanvasElement>(null);

  const sceneRef =
    useRef<OrbSceneApi | null>(null);

  const trackerRef =
    useRef<HandTracker | null>(null);


  const [camera, setCamera] =
    useState<CameraState>("off");

  const [status, setStatus] =
    useState<TrackerStatus>({
      hands: 0,
      mode: "idle",
    });

  const [error, setError] =
    useState<string | null>(null);

  const [avatarType, setAvatarType] =
    useState<AvatarType>("robot");


  // =====================================================
  // AVATAR INITIALIZATION / SWITCHING
  // =====================================================

  useEffect(() => {

    const container =
      containerRef.current;

    if (!container) {
      return;
    }

    let scene: OrbSceneApi;

    if (avatarType === "orb") {
      scene = createOrbScene(container);
    } else if (avatarType === "full-body") {
      scene = createJarvisFullBody(container);
    } else {
      scene = createJarvisAvatar(container);
    }

    sceneRef.current = scene;

    return () => {
      scene.dispose();
      sceneRef.current = null;
    };

  }, [avatarType]);


  // =====================================================
  // STOP GESTURES
  // =====================================================

  const stopGestures =
    useCallback(() => {

      trackerRef.current?.stop();

      trackerRef.current =
        null;

      setCamera("off");

      setStatus({
        hands: 0,
        mode: "idle",
      });

    }, []);


  // =====================================================
  // START GESTURES
  // =====================================================

  const startGestures =
    useCallback(async () => {

      const video =
        videoRef.current;

      const overlay =
        overlayRef.current;


      if (
        !video ||
        !overlay ||
        trackerRef.current
      ) {
        return;
      }


      setCamera("starting");

      setError(null);


      const tracker =
        new HandTracker(
          video,
          overlay,
          {
            onRotate: (dt, dp) =>
              sceneRef.current?.rotateBy(
                dt,
                dp
              ),

            onZoom: (factor) =>
              sceneRef.current?.zoomBy(
                factor
              ),

            onStatus: setStatus,
          }
        );


      trackerRef.current =
        tracker;


      try {

        await tracker.start();

        setCamera("on");

      } catch (err) {

        trackerRef.current =
          null;

        tracker.stop();

        setCamera("error");


        setError(
          err instanceof DOMException &&
          err.name === "NotAllowedError"

            ? "CAMERA ACCESS DENIED"

            : "TRACKING INIT FAILED"
        );

      }

    }, []);


  // =====================================================
  // GESTURE TOGGLE
  // =====================================================

  const toggleGestures =
    useCallback(() => {

      if (trackerRef.current) {

        stopGestures();

      } else {

        void startGestures();

      }

    }, [
      startGestures,
      stopGestures,
    ]);


  // =====================================================
  // KEYBOARD CONTROLS
  // =====================================================

  useEffect(() => {

    const onKey =
      (e: KeyboardEvent) => {

        switch (e.key) {

          case "+":
          case "=":

            sceneRef.current?.zoomIn();

            break;


          case "-":
          case "_":

            sceneRef.current?.zoomOut();

            break;


          case "r":
          case "R":

            sceneRef.current?.resetView();

            break;


          case "g":
          case "G":

            toggleGestures();

            break;

        }

      };


    window.addEventListener(
      "keydown",
      onKey
    );


    return () => {

      window.removeEventListener(
        "keydown",
        onKey
      );

    };

  }, [toggleGestures]);


  const cameraOn =
    camera === "on";


  return (

    <main className="jarvis-hud">

      {/* ============================================= */}
      {/* ULTRON / JARVIS ORB */}
      {/* ============================================= */}

      <div
        ref={containerRef}
        className="orb-root"
      />


      {/* ============================================= */}
      {/* VISUAL OVERLAYS */}
      {/* ============================================= */}

      <div className="overlay-vignette" />

      <div className="overlay-grain" />

      <div className="overlay-scanlines" />

      {/* ============================================= */}
      {/* CONTROL HINT */}
      {/* ============================================= */}

      <div className="hud hud-hint">

        <div>

          <span className="key">
            DRAG
          </span>

          {" "}spin&nbsp;&nbsp;

          <span className="key">
            SCROLL
          </span>

          {" "}zoom

        </div>


        <div>

          {cameraOn ? (

            <>
              <span className="key">
                PINCH + MOVE
              </span>

              {" "}spin&nbsp;&nbsp;

              <span className="key">
                2 HANDS
              </span>

              {" "}zoom
            </>

          ) : (

            <>
              <span className="key">
                G
              </span>

              {" "}gestures&nbsp;&nbsp;

              <span className="key">
                R
              </span>

              {" "}reset&nbsp;&nbsp;

              <span className="key">
                +/−
              </span>

              {" "}zoom
            </>

          )}

        </div>

      </div>


      {/* ============================================= */}
      {/* HUD CONTROLS */}
      {/* ============================================= */}

      <div className="hud hud-controls">

        <div
          className={
            `camera-panel${
              cameraOn
                ? " visible"
                : ""
            }`
          }
        >
          {/* Cybernetic view finder corners */}
          <div className="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-[var(--assistant-colour)] pointer-events-none z-10" />
          <div className="absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-[var(--assistant-colour)] pointer-events-none z-10" />
          <div className="absolute bottom-0 left-0 w-2 h-2 border-b-2 border-l-2 border-[var(--assistant-colour)] pointer-events-none z-10" />
          <div className="absolute bottom-0 right-0 w-2 h-2 border-b-2 border-r-2 border-[var(--assistant-colour)] pointer-events-none z-10" />

          <video
            ref={videoRef}
            muted
            playsInline
            className="camera-video"
          />

          <canvas
            ref={overlayRef}
            width={208}
            height={156}
            className="camera-overlay"
          />

          <div className="camera-status flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <span className={`w-1.5 h-1.5 rounded-full ${status.hands > 0 ? "bg-[#00ff66] shadow-[0_0_6px_#00ff66]" : "bg-[var(--assistant-colour)] opacity-60"}`} />
              {status.hands > 0

                ? `${status.hands} HAND${
                    status.hands > 1
                      ? "S"
                      : ""
                  } · ${
                    MODE_LABEL[
                      status.mode
                    ]
                  }`

                : "SCANNING"}
            </span>
          </div>

        </div>


        {error && (

          <div className="hud-error">
            {error}
          </div>

        )}

        <div className="hud-row">

          <button
            type="button"
            className="hud-btn"
            aria-pressed={cameraOn}
            onClick={toggleGestures}
            disabled={
              camera === "starting"
            }
          >

            {camera === "starting"

              ? "INITIALIZING…"

              : cameraOn

                ? "● GESTURES ON"

                : "○ GESTURES OFF"}

          </button>

        </div>


        <div className="hud-row">

          <button
            type="button"
            className="hud-btn"
            onClick={() =>
              sceneRef.current?.zoomIn()
            }
            aria-label="Zoom in"
          >
            +
          </button>


          <button
            type="button"
            className="hud-btn"
            onClick={() =>
              sceneRef.current?.zoomOut()
            }
            aria-label="Zoom out"
          >
            −
          </button>


          <button
            type="button"
            className="hud-btn"
            onClick={() =>
              sceneRef.current?.resetView()
            }
          >
            RESET
          </button>

        </div>

        <div className="hud-avatar-selector">

          <div className="hud-row">
            <button
              type="button"
              className="hud-btn"
              aria-pressed={avatarType === "orb"}
              onClick={() => setAvatarType("orb")}
            >
              {avatarType === "orb" ? "● ORB" : "○ ORB"}
            </button>

            <button
              type="button"
              className="hud-btn"
              aria-pressed={avatarType === "robot"}
              onClick={() => setAvatarType("robot")}
            >
              {avatarType === "robot" ? "● ROBOT" : "○ ROBOT"}
            </button>
          </div>

          <div className="hud-row">
            <button
              type="button"
              className="hud-btn"
              aria-pressed={avatarType === "full-body"}
              onClick={() => setAvatarType("full-body")}
            >
              {avatarType === "full-body"
                ? "● FULL BODY"
                : "○ FULL BODY"}
            </button>
          </div>
          
        </div>

      </div>

    </main>

  );

}