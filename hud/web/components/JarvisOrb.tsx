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
//   createJarvisFullBody,
// } from "@/lib/jarvisFullBody";

// import {
//   createOrbScene,
// } from "@/lib/orbScene";

// import {
//   HandTracker,
//   type TrackerStatus,
// } from "@/lib/handTracker";


// type CameraState =
//   | "off"
//   | "starting"
//   | "on"
//   | "error";


// type AvatarType =
//   | "orb"
//   | "robot"
//   | "full-body";


// type UltronColor = {
//   name: string;
//   value: number;
// };


// // =====================================================
// // SCENE API
// // =====================================================
// //
// // All three avatar scenes support the normal scene
// // controls. Only the ULTRON orb supports setUltronColor.
// //
// // Keeping the color function optional means ROBOT and
// // FULL BODY do not need to implement it.
// // =====================================================

// type SceneApi =
//   OrbSceneApi & {
//     setUltronColor?: (
//       color: number
//     ) => void;
//   };


// // =====================================================
// // TRACKER MODE LABELS
// // =====================================================

// const MODE_LABEL: Record<
//   TrackerStatus["mode"],
//   string
// > = {
//   idle: "STANDBY",
//   spin: "SPIN",
//   zoom: "ZOOM",
// };


// // =====================================================
// // ULTRON COLOR PRESETS
// // =====================================================

// const ULTRON_COLORS: UltronColor[] = [

//   {
//     name: "RED",
//     value: 0xff2020,
//   },

//   {
//     name: "ORANGE",
//     value: 0xff7a20,
//   },

//   {
//     name: "BLUE",
//     value: 0x2080ff,
//   },

//   {
//     name: "CYAN",
//     value: 0x20eaff,
//   },

//   {
//     name: "PURPLE",
//     value: 0x9b30ff,
//   },

//   {
//     name: "GREEN",
//     value: 0x20ff80,
//   },

//   {
//     name: "WHITE",
//     value: 0xffffff,
//   },

// ];


// export default function JarvisOrb() {

//   const containerRef =
//     useRef<HTMLDivElement>(null);

//   const videoRef =
//     useRef<HTMLVideoElement>(null);

//   const overlayRef =
//     useRef<HTMLCanvasElement>(null);

//   const sceneRef =
//     useRef<SceneApi | null>(null);

//   const trackerRef =
//     useRef<HandTracker | null>(null);


//   // ===================================================
//   // STATE
//   // ===================================================

//   const [camera, setCamera] =
//     useState<CameraState>("off");


//   const [status, setStatus] =
//     useState<TrackerStatus>({
//       hands: 0,
//       mode: "idle",
//     });


//   const [error, setError] =
//     useState<string | null>(null);


//   const [avatarType, setAvatarType] =
//     useState<AvatarType>("robot");


//   const [ultronColor, setUltronColor] =
//     useState<number>(
//       ULTRON_COLORS[0].value
//     );


//   // =====================================================
//   // AVATAR INITIALIZATION / SWITCHING
//   // =====================================================

//   useEffect(() => {

//     const container =
//       containerRef.current;

//     if (!container) {
//       return;
//     }


//     let scene: SceneApi;


//     // ---------------------------------------------------
//     // ULTRON ORB
//     // ---------------------------------------------------

//     if (avatarType === "orb") {

//       scene =
//         createOrbScene(
//           container
//         );

//     }

//     // ---------------------------------------------------
//     // FULL BODY
//     // ---------------------------------------------------

//     else if (
//       avatarType === "full-body"
//     ) {

//       scene =
//         createJarvisFullBody(
//           container
//         );

//     }

//     // ---------------------------------------------------
//     // NORMAL ROBOT
//     // ---------------------------------------------------

//     else {

//       scene =
//         createJarvisAvatar(
//           container
//         );

//     }


//     sceneRef.current =
//       scene;


//     // ---------------------------------------------------
//     // Apply current ULTRON color
//     // ---------------------------------------------------

//     if (
//       avatarType === "orb" &&
//       scene.setUltronColor
//     ) {

//       scene.setUltronColor(
//         ultronColor
//       );

//     }


//     // ---------------------------------------------------
//     // Cleanup
//     // ---------------------------------------------------

//     return () => {

//       scene.dispose();

//       if (
//         sceneRef.current === scene
//       ) {

//         sceneRef.current =
//           null;

//       }

//     };

//   }, [avatarType]);


//   // =====================================================
//   // APPLY ULTRON COLOR
//   // =====================================================
//   //
//   // IMPORTANT:
//   // Changing the color does NOT recreate the scene.
//   // It directly updates the existing ULTRON orb.
//   // =====================================================

//   useEffect(() => {

//     if (
//       avatarType !== "orb"
//     ) {

//       return;

//     }


//     sceneRef.current?.setUltronColor?.(
//       ultronColor
//     );

//   }, [
//     avatarType,
//     ultronColor,
//   ]);


//   // =====================================================
//   // CHANGE ULTRON COLOR
//   // =====================================================

//   const changeUltronColor =
//     useCallback(
//       (color: number) => {

//         setUltronColor(
//           color
//         );

//       },
//       []
//     );


//   // =====================================================
//   // STOP GESTURES
//   // =====================================================

//   const stopGestures =
//     useCallback(() => {

//       trackerRef.current?.stop();

//       trackerRef.current =
//         null;


//       setCamera(
//         "off"
//       );


//       setStatus({
//         hands: 0,
//         mode: "idle",
//       });

//     }, []);


//   // =====================================================
//   // START GESTURES
//   // =====================================================

//   const startGestures =
//     useCallback(
//       async () => {

//         const video =
//           videoRef.current;

//         const overlay =
//           overlayRef.current;


//         if (
//           !video ||
//           !overlay ||
//           trackerRef.current
//         ) {

//           return;

//         }


//         setCamera(
//           "starting"
//         );


//         setError(
//           null
//         );


//         const tracker =
//           new HandTracker(
//             video,
//             overlay,
//             {

//               onRotate: (
//                 dt,
//                 dp
//               ) => {

//                 sceneRef.current?.rotateBy(
//                   dt,
//                   dp
//                 );

//               },


//               onZoom: (
//                 factor
//               ) => {

//                 sceneRef.current?.zoomBy(
//                   factor
//                 );

//               },


//               onStatus:
//                 setStatus,

//             }
//           );


//         trackerRef.current =
//           tracker;


//         try {

//           await tracker.start();

//           setCamera(
//             "on"
//           );

//         }

//         catch (err) {

//           trackerRef.current =
//             null;


//           tracker.stop();


//           setCamera(
//             "error"
//           );


//           setError(

//             err instanceof DOMException &&
//             err.name === "NotAllowedError"

//               ? "CAMERA ACCESS DENIED"

//               : "TRACKING INIT FAILED"

//           );

//         }

//       },
//       []
//     );


//   // =====================================================
//   // GESTURE TOGGLE
//   // =====================================================

//   const toggleGestures =
//     useCallback(() => {

//       if (
//         trackerRef.current
//       ) {

//         stopGestures();

//       }

//       else {

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
//       (
//         e: KeyboardEvent
//       ) => {

//         switch (
//           e.key
//         ) {

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

//   }, [
//     toggleGestures,
//   ]);


//   // =====================================================
//   // CAMERA STATE
//   // =====================================================

//   const cameraOn =
//     camera === "on";


//   // =====================================================
//   // RENDER
//   // =====================================================

//   return (

//     <main className="jarvis-hud">


//       {/* ================================================= */}
//       {/* ULTRON / JARVIS AVATAR */}
//       {/* ================================================= */}

//       <div
//         ref={containerRef}
//         className="orb-root"
//       />


//       {/* ================================================= */}
//       {/* VISUAL OVERLAYS */}
//       {/* ================================================= */}

//       <div
//         className="overlay-vignette"
//       />

//       <div
//         className="overlay-grain"
//       />

//       <div
//         className="overlay-scanlines"
//       />


//       {/* ================================================= */}
//       {/* CONTROL HINT */}
//       {/* ================================================= */}

//       {/* <div className="hud hud-hint">

//         <div>

//           <span className="key">
//             DRAG
//           </span>

//           {" "}
//           spin
//           &nbsp;&nbsp;

//           <span className="key">
//             SCROLL
//           </span>

//           {" "}
//           zoom

//         </div>


//         <div>

//           {cameraOn ? (

//             <>

//               <span className="key">
//                 PINCH + MOVE
//               </span>

//               {" "}
//               spin
//               &nbsp;&nbsp;

//               <span className="key">
//                 2 HANDS
//               </span>

//               {" "}
//               zoom

//             </>

//           ) : (

//             <>

//               <span className="key">
//                 G
//               </span>

//               {" "}
//               gestures
//               &nbsp;&nbsp;

//               <span className="key">
//                 R
//               </span>

//               {" "}
//               reset
//               &nbsp;&nbsp;

//               <span className="key">
//                 +/−
//               </span>

//               {" "}
//               zoom

//             </>

//           )}

//         </div>

//       </div> */}


//       {/* ================================================= */}
//       {/* HUD CONTROLS */}
//       {/* ================================================= */}

//       <div className="hud hud-controls">

//         {/* ================================================= */}
//         {/* CAMERA PANEL */}
//         {/* ================================================= */}

//         <div
//           className={
//             `camera-panel${
//               cameraOn
//                 ? " visible"
//                 : ""
//             }`
//           }
//         >

//           {/* View finder corners */}

//           <div className="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-[var(--assistant-colour)] pointer-events-none z-10" />

//           <div className="absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-[var(--assistant-colour)] pointer-events-none z-10" />

//           <div className="absolute bottom-0 left-0 w-2 h-2 border-b-2 border-l-2 border-[var(--assistant-colour)] pointer-events-none z-10" />

//           <div className="absolute bottom-0 right-0 w-2 h-2 border-b-2 border-r-2 border-[var(--assistant-colour)] pointer-events-none z-10" />


//           {/* Camera */}

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


//           {/* Camera status */}

//           <div className="camera-status flex items-center justify-between">

//             <span className="flex items-center gap-1.5">

//               <span
//                 className={
//                   `w-1.5 h-1.5 rounded-full ${
//                     status.hands > 0
//                       ? "bg-[#00ff66] shadow-[0_0_6px_#00ff66]"
//                       : "bg-[var(--assistant-colour)] opacity-60"
//                   }`
//                 }
//               />

//               {status.hands > 0
//                 ? `${status.hands} HAND${
//                     status.hands > 1
//                       ? "S"
//                       : ""
//                   } · ${
//                     MODE_LABEL[status.mode]
//                   }`
//                 : "SCANNING"}

//             </span>

//           </div>

//         </div>


//         {/* ================================================= */}
//         {/* ERROR */}
//         {/* ================================================= */}

//         {error && (

//           <div className="hud-error">
//             {error}
//           </div>

//         )}


//         {/* ================================================= */}
//         {/* GESTURE CONTROL */}
//         {/* ================================================= */}

//         <div
//           className="hud-row"
//           style={{
//             marginBottom: "8px",
//           }}
//         >

//           <button
//             type="button"
//             className="hud-btn"
//             aria-pressed={cameraOn}
//             onClick={toggleGestures}
//             disabled={camera === "starting"}
//           >

//             {camera === "starting"
//               ? "INITIALIZING…"
//               : cameraOn
//                 ? "● GESTURES ON"
//                 : "○ GESTURES OFF"}

//           </button>

//         </div>


//         {/* ================================================= */}
//         {/* ZOOM CONTROLS */}
//         {/* ================================================= */}

//         <div
//           className="hud-row"
//           style={{
//             display: "flex",
//             gap: "8px",
//             marginBottom: "10px",
//           }}
//         >

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


//         {/* ================================================= */}
//         {/* AVATAR SELECTOR */}
//         {/* ================================================= */}

//         <div
//           className="hud-avatar-selector"
//           style={{
//             width: "100%",
//             marginTop: "2px",
//           }}
//         >

//           {/* ORB / ROBOT */}

//           <div
//             className="hud-row"
//             style={{
//               display: "flex",
//               gap: "8px",
//               width: "100%",
//               marginBottom: "6px",
//             }}
//           >

//             <button
//               type="button"
//               className="hud-btn"
//               style={{
//                 flex: 1,
//                 minWidth: 0,
//               }}
//               aria-pressed={
//                 avatarType === "orb"
//               }
//               onClick={() =>
//                 setAvatarType("orb")
//               }
//             >

//               {avatarType === "orb"
//                 ? "● ORB"
//                 : "○ ORB"}

//             </button>


//             <button
//               type="button"
//               className="hud-btn"
//               style={{
//                 flex: 1,
//                 minWidth: 0,
//               }}
//               aria-pressed={
//                 avatarType === "robot"
//               }
//               onClick={() =>
//                 setAvatarType("robot")
//               }
//             >

//               {avatarType === "robot"
//                 ? "● ROBOT"
//                 : "○ ROBOT"}

//             </button>

//           </div>


//           {/* FULL BODY */}

//           <div
//             className="hud-row"
//             style={{
//               width: "100%",
//               marginBottom: "10px",
//             }}
//           >

//             <button
//               type="button"
//               className="hud-btn"
//               style={{
//                 width: "100%",
//               }}
//               aria-pressed={
//                 avatarType === "full-body"
//               }
//               onClick={() =>
//                 setAvatarType("full-body")
//               }
//             >

//               {avatarType === "full-body"
//                 ? "● FULL BODY"
//                 : "○ FULL BODY"}

//             </button>

//           </div>


//           {/* ================================================= */}
//           {/* ULTRON COLOR CONTROLS */}
//           {/* ================================================= */}

//           {avatarType === "orb" && (

//             <div
//               className="ultron-color-panel"
//               aria-label="ULTRON color selection"
//               style={{
//                 position: "fixed",
//                 left: "220px",
//                 top: "583px",
//                 width: "105px",
//                 zIndex: 50,
//               }}
//             >

//               {/* COLOR TITLE */}

//               <div
//                 style={{
//                   paddingBottom: "4px",
//                 }}
//               >

//                 <span
//                   className="ultron-color-label"
//                   style={{
//                     fontSize: "10px",
//                     letterSpacing: "2px",
//                     opacity: 0.9,
//                   }}
//                 >
//                   ULTRON COLOR
//                 </span>

//               </div>


//               {/* ================================================= */}
//               {/* COLORS — 2 PER ROW */}
//               {/* ================================================= */}

//               <div
//                 className="ultron-color-row"
//                 style={{
//                   display: "grid",
//                   gridTemplateColumns: "36px 36px",
//                   gap: "5px",
//                   width: "78px",
//                   justifyContent: "start",
//                 }}
//               >

//                 {ULTRON_COLORS.map(
//                   (color) => {

//                     const active =
//                       ultronColor ===
//                       color.value;


//                     const hex =
//                       `#${color.value
//                         .toString(16)
//                         .padStart(
//                           6,
//                           "0"
//                         )}`;


//                     return (

//                       <button
//                         key={color.name}
//                         type="button"
//                         className={
//                           `hud-btn ultron-color-btn${
//                             active
//                               ? " active"
//                               : ""
//                           }`
//                         }
//                         style={{
//                           width: "36px",
//                           height: "36px",
//                           minWidth: "36px",
//                           padding: "0",
//                           borderRadius: "50%",
//                           display: "flex",
//                           flexDirection: "column",
//                           alignItems: "center",
//                           justifyContent: "center",
//                           gap: "3px",
//                           whiteSpace: "nowrap",
//                         }}
//                         aria-label={
//                           `ULTRON color ${color.name}`
//                         }
//                         aria-pressed={active}
//                         title={color.name}
//                         onClick={() =>
//                           changeUltronColor(
//                             color.value
//                           )
//                         }
//                       >

//                         <span
//                           className="ultron-color-dot"
//                           style={{
//                             width: "5px",
//                             height: "5px",
//                             minWidth: "5px",
//                             borderRadius: "50%",
//                             backgroundColor: hex,
//                             boxShadow:
//                               active
//                                 ? `0 0 6px ${hex}`
//                                 : `0 0 2px ${hex}`,
//                           }}
//                         />

//                         <span
//                           style={{
//                             fontSize: "7px",
//                             lineHeight: "1",
//                           }}
//                         >
//                           {color.name}
//                         </span>

//                       </button>

//                     );

//                   }
//                 )}

//               </div>

//             </div>

//           )}

//         </div>

//       </div>

//     </main>

//   );

// }

// ============================================================================================================================================ //

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
  createExpressiveRobot,
  type ExpressiveRobotSituation,
} from "@/lib/expressiveRobot";

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
  | "full-body"
  | "expressive";


type UltronColor = {
  name: string;
  value: number;
};


// =====================================================
// SCENE API
// =====================================================
//
// All avatar scenes support the normal camera controls.
// Only the ULTRON orb supports setUltronColor.
//
// EXPRESSIVE ROBOT additionally supports
// setSituation(), which will be connected to the
// real JARVIS situation/state.
// =====================================================

type SceneApi =
  OrbSceneApi & {
    setUltronColor?: (
      color: number
    ) => void;

    setSituation?: (
      situation: ExpressiveRobotSituation
    ) => void;
  };


// =====================================================
// TRACKER MODE LABELS
// =====================================================

const MODE_LABEL: Record<
  TrackerStatus["mode"],
  string
> = {
  idle: "STANDBY",
  spin: "SPIN",
  zoom: "ZOOM",
};


// =====================================================
// ULTRON COLOR PRESETS
// =====================================================

const ULTRON_COLORS: UltronColor[] = [

  {
    name: "RED",
    value: 0xff2020,
  },

  {
    name: "ORANGE",
    value: 0xff7a20,
  },

  {
    name: "BLUE",
    value: 0x2080ff,
  },

  {
    name: "CYAN",
    value: 0x20eaff,
  },

  {
    name: "PURPLE",
    value: 0x9b30ff,
  },

  {
    name: "GREEN",
    value: 0x20ff80,
  },

  {
    name: "WHITE",
    value: 0xffffff,
  },

];


export default function JarvisOrb(
  {
    expressiveSituation,
  }: {
    expressiveSituation?: ExpressiveRobotSituation;
  }
) {

  const containerRef =
    useRef<HTMLDivElement>(null);

  const videoRef =
    useRef<HTMLVideoElement>(null);

  const overlayRef =
    useRef<HTMLCanvasElement>(null);

  const sceneRef =
    useRef<SceneApi | null>(null);

  const trackerRef =
    useRef<HandTracker | null>(null);


  // ===================================================
  // STATE
  // ===================================================

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


  const [ultronColor, setUltronColor] =
    useState<number>(
      ULTRON_COLORS[0].value
    );


  // =====================================================
  // AVATAR INITIALIZATION / SWITCHING
  // =====================================================

  useEffect(() => {

    const container =
      containerRef.current;

    if (!container) {
      return;
    }


    let scene: SceneApi;


    // ---------------------------------------------------
    // ULTRON ORB
    // ---------------------------------------------------

    if (avatarType === "orb") {

      scene =
        createOrbScene(
          container
        );

    }

    // ---------------------------------------------------
    // FULL BODY
    // ---------------------------------------------------

    else if (
      avatarType === "full-body"
    ) {

      scene =
        createJarvisFullBody(
          container
        );

    }

    // ---------------------------------------------------
    // EXPRESSIVE ROBOT
    // ---------------------------------------------------

    else if (
      avatarType === "expressive"
    ) {

      scene =
        createExpressiveRobot(
          container
        );

    }

    // ---------------------------------------------------
    // NORMAL ROBOT
    // ---------------------------------------------------

    else {

      scene =
        createJarvisAvatar(
          container
        );

    }


    sceneRef.current =
      scene;


    // ---------------------------------------------------
    // Apply current ULTRON color
    // ---------------------------------------------------

    if (
      avatarType === "orb" &&
      scene.setUltronColor
    ) {

      scene.setUltronColor(
        ultronColor
      );

    }


    // ---------------------------------------------------
    // Apply current EXPRESSIVE situation
    // ---------------------------------------------------

    if (
      avatarType === "expressive" &&
      scene.setSituation &&
      expressiveSituation
    ) {

      scene.setSituation(
        expressiveSituation
      );

    }


    // ---------------------------------------------------
    // Cleanup
    // ---------------------------------------------------

    return () => {

      scene.dispose();

      if (
        sceneRef.current === scene
      ) {

        sceneRef.current =
          null;

      }

    };

  }, [
    avatarType,
    expressiveSituation,
    ultronColor,
  ]);


  // =====================================================
  // APPLY EXPRESSIVE ROBOT SITUATION
  // =====================================================
  //
  // The expressive robot does NOT have manual
  // animation buttons.
  //
  // Its animation is driven by JARVIS situation data.
  // =====================================================

  useEffect(() => {

    if (
      avatarType !== "expressive" ||
      !expressiveSituation
    ) {

      return;

    }


    sceneRef.current?.setSituation?.(
      expressiveSituation
    );

  }, [
    avatarType,
    expressiveSituation,
  ]);


  // =====================================================
  // APPLY ULTRON COLOR
  // =====================================================
  //
  // IMPORTANT:
  // Changing the color does NOT recreate the scene.
  // It directly updates the existing ULTRON orb.
  // =====================================================

  useEffect(() => {

    if (
      avatarType !== "orb"
    ) {

      return;

    }


    sceneRef.current?.setUltronColor?.(
      ultronColor
    );

  }, [
    avatarType,
    ultronColor,
  ]);


  // =====================================================
  // CHANGE ULTRON COLOR
  // =====================================================

  const changeUltronColor =
    useCallback(
      (color: number) => {

        setUltronColor(
          color
        );

      },
      []
    );


  // =====================================================
  // STOP GESTURES
  // =====================================================

  const stopGestures =
    useCallback(() => {

      trackerRef.current?.stop();

      trackerRef.current =
        null;


      setCamera(
        "off"
      );


      setStatus({
        hands: 0,
        mode: "idle",
      });

    }, []);


  // =====================================================
  // START GESTURES
  // =====================================================

  const startGestures =
    useCallback(
      async () => {

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


        setCamera(
          "starting"
        );


        setError(
          null
        );


        const tracker =
          new HandTracker(
            video,
            overlay,
            {

              onRotate: (
                dt,
                dp
              ) => {

                sceneRef.current?.rotateBy(
                  dt,
                  dp
                );

              },


              onZoom: (
                factor
              ) => {

                sceneRef.current?.zoomBy(
                  factor
                );

              },


              onStatus:
                setStatus,

            }
          );


        trackerRef.current =
          tracker;


        try {

          await tracker.start();

          setCamera(
            "on"
          );

        }

        catch (err) {

          trackerRef.current =
            null;


          tracker.stop();


          setCamera(
            "error"
          );


          setError(

            err instanceof DOMException &&
            err.name === "NotAllowedError"

              ? "CAMERA ACCESS DENIED"

              : "TRACKING INIT FAILED"

          );

        }

      },
      []
    );


  // =====================================================
  // GESTURE TOGGLE
  // =====================================================

  const toggleGestures =
    useCallback(() => {

      if (
        trackerRef.current
      ) {

        stopGestures();

      }

      else {

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
      (
        e: KeyboardEvent
      ) => {

        switch (
          e.key
        ) {

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

  }, [
    toggleGestures,
  ]);


  // =====================================================
  // CAMERA STATE
  // =====================================================

  const cameraOn =
    camera === "on";


  // =====================================================
  // RENDER
  // =====================================================

  return (

    <main className="jarvis-hud">


      {/* ================================================= */}
      {/* ULTRON / JARVIS AVATAR */}
      {/* ================================================= */}

      <div
        ref={containerRef}
        className="orb-root"
      />


      {/* ================================================= */}
      {/* VISUAL OVERLAYS */}
      {/* ================================================= */}

      <div
        className="overlay-vignette"
      />

      <div
        className="overlay-grain"
      />

      <div
        className="overlay-scanlines"
      />


      {/* ================================================= */}
      {/* CONTROL HINT */}
      {/* ================================================= */}

      {/* <div className="hud hud-hint">

        <div>

          <span className="key">
            DRAG
          </span>

          {" "}
          spin
          &nbsp;&nbsp;

          <span className="key">
            SCROLL
          </span>

          {" "}
          zoom

        </div>


        <div>

          {cameraOn ? (

            <>

              <span className="key">
                PINCH + MOVE
              </span>

              {" "}
              spin
              &nbsp;&nbsp;

              <span className="key">
                2 HANDS
              </span>

              {" "}
              zoom

            </>

          ) : (

            <>

              <span className="key">
                G
              </span>

              {" "}
              gestures
              &nbsp;&nbsp;

              <span className="key">
                R
              </span>

              {" "}
              reset
              &nbsp;&nbsp;

              <span className="key">
                +/−
              </span>

              {" "}
              zoom

            </>

          )}

        </div>

      </div> */}


      {/* ================================================= */}
      {/* HUD CONTROLS */}
      {/* ================================================= */}

      <div className="hud hud-controls">

        {/* ================================================= */}
        {/* CAMERA PANEL */}
        {/* ================================================= */}

        <div
          className={
            `camera-panel${
              cameraOn
                ? " visible"
                : ""
            }`
          }
        >

          {/* View finder corners */}

          <div className="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-[var(--assistant-colour)] pointer-events-none z-10" />

          <div className="absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-[var(--assistant-colour)] pointer-events-none z-10" />

          <div className="absolute bottom-0 left-0 w-2 h-2 border-b-2 border-l-2 border-[var(--assistant-colour)] pointer-events-none z-10" />

          <div className="absolute bottom-0 right-0 w-2 h-2 border-b-2 border-r-2 border-[var(--assistant-colour)] pointer-events-none z-10" />


          {/* Camera */}

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


          {/* Camera status */}

          <div className="camera-status flex items-center justify-between">

            <span className="flex items-center gap-1.5">

              <span
                className={
                  `w-1.5 h-1.5 rounded-full ${
                    status.hands > 0
                      ? "bg-[#00ff66] shadow-[0_0_6px_#00ff66]"
                      : "bg-[var(--assistant-colour)] opacity-60"
                  }`
                }
              />

              {status.hands > 0
                ? `${status.hands} HAND${
                    status.hands > 1
                      ? "S"
                      : ""
                  } · ${
                    MODE_LABEL[status.mode]
                  }`
                : "SCANNING"}

            </span>

          </div>

        </div>


        {/* ================================================= */}
        {/* ERROR */}
        {/* ================================================= */}

        {error && (

          <div className="hud-error">
            {error}
          </div>

        )}


        {/* ================================================= */}
        {/* GESTURE CONTROL */}
        {/* ================================================= */}

        <div
          className="hud-row"
          style={{
            marginBottom: "8px",
          }}
        >

          <button
            type="button"
            className="hud-btn"
            aria-pressed={cameraOn}
            onClick={toggleGestures}
            disabled={camera === "starting"}
          >

            {camera === "starting"
              ? "INITIALIZING…"
              : cameraOn
                ? "● GESTURES ON"
                : "○ GESTURES OFF"}

          </button>

        </div>


        {/* ================================================= */}
        {/* ZOOM CONTROLS */}
        {/* ================================================= */}

        <div
          className="hud-row"
          style={{
            display: "flex",
            gap: "8px",
            marginBottom: "10px",
          }}
        >

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


        {/* ================================================= */}
        {/* AVATAR SELECTOR */}
        {/* ================================================= */}

        <div
          className="hud-avatar-selector"
          style={{
            width: "100%",
            marginTop: "2px",
          }}
        >

          {/* ORB / ROBOT */}

          <div
            className="hud-row"
            style={{
              display: "flex",
              gap: "8px",
              width: "100%",
              marginBottom: "6px",
            }}
          >

            <button
              type="button"
              className="hud-btn"
              style={{
                flex: 1,
                minWidth: 0,
              }}
              aria-pressed={
                avatarType === "orb"
              }
              onClick={() =>
                setAvatarType("orb")
              }
            >

              {avatarType === "orb"
                ? "● ORB"
                : "○ ORB"}

            </button>


            <button
              type="button"
              className="hud-btn"
              style={{
                flex: 1,
                minWidth: 0,
              }}
              aria-pressed={
                avatarType === "robot"
              }
              onClick={() =>
                setAvatarType("robot")
              }
            >

              {avatarType === "robot"
                ? "● ROBOT"
                : "○ ROBOT"}

            </button>

          </div>


          {/* FULL BODY */}

          <div
            className="hud-row"
            style={{
              width: "100%",
              marginBottom: "6px",
            }}
          >

            <button
              type="button"
              className="hud-btn"
              style={{
                width: "100%",
              }}
              aria-pressed={
                avatarType === "full-body"
              }
              onClick={() =>
                setAvatarType("full-body")
              }
            >

              {avatarType === "full-body"
                ? "● FULL BODY"
                : "○ FULL BODY"}

            </button>

          </div>


          {/* EXPRESSIVE ROBOT */}

          <div
            className="hud-row"
            style={{
              width: "100%",
              marginBottom: "10px",
            }}
          >

            <button
              type="button"
              className="hud-btn"
              style={{
                width: "100%",
              }}
              aria-pressed={
                avatarType === "expressive"
              }
              onClick={() =>
                setAvatarType("expressive")
              }
            >

              {avatarType === "expressive"
                ? "● EXPRESSIVE"
                : "○ EXPRESSIVE"}

            </button>

          </div>


          {/* ================================================= */}
          {/* ULTRON COLOR CONTROLS */}
          {/* ================================================= */}

          {avatarType === "orb" && (

            <div
              className="ultron-color-panel"
              aria-label="ULTRON color selection"
              style={{
                position: "fixed",
                left: "220px",
                top: "583px",
                width: "105px",
                zIndex: 50,
              }}
            >

              {/* COLOR TITLE */}

              <div
                style={{
                  paddingBottom: "4px",
                }}
              >

                <span
                  className="ultron-color-label"
                  style={{
                    fontSize: "10px",
                    letterSpacing: "2px",
                    opacity: 0.9,
                  }}
                >
                  ULTRON COLOR
                </span>

              </div>


              {/* ================================================= */}
              {/* COLORS — 2 PER ROW */}
              {/* ================================================= */}

              <div
                className="ultron-color-row"
                style={{
                  display: "grid",
                  gridTemplateColumns: "36px 36px",
                  gap: "5px",
                  width: "78px",
                  justifyContent: "start",
                }}
              >

                {ULTRON_COLORS.map(
                  (color) => {

                    const active =
                      ultronColor ===
                      color.value;


                    const hex =
                      `#${color.value
                        .toString(16)
                        .padStart(
                          6,
                          "0"
                        )}`;


                    return (

                      <button
                        key={color.name}
                        type="button"
                        className={
                          `hud-btn ultron-color-btn${
                            active
                              ? " active"
                              : ""
                          }`
                        }
                        style={{
                          width: "36px",
                          height: "36px",
                          minWidth: "36px",
                          padding: "0",
                          borderRadius: "50%",
                          display: "flex",
                          flexDirection: "column",
                          alignItems: "center",
                          justifyContent: "center",
                          gap: "3px",
                          whiteSpace: "nowrap",
                        }}
                        aria-label={
                          `ULTRON color ${color.name}`
                        }
                        aria-pressed={active}
                        title={color.name}
                        onClick={() =>
                          changeUltronColor(
                            color.value
                          )
                        }
                      >

                        <span
                          className="ultron-color-dot"
                          style={{
                            width: "5px",
                            height: "5px",
                            minWidth: "5px",
                            borderRadius: "50%",
                            backgroundColor: hex,
                            boxShadow:
                              active
                                ? `0 0 6px ${hex}`
                                : `0 0 2px ${hex}`,
                          }}
                        />

                        <span
                          style={{
                            fontSize: "7px",
                            lineHeight: "1",
                          }}
                        >
                          {color.name}
                        </span>

                      </button>

                    );

                  }
                )}

              </div>

            </div>

          )}

        </div>

      </div>

    </main>

  );

}
