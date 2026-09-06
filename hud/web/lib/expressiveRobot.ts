import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

export interface ExpressiveRobotSituation {
  status?: string;
  listening?: boolean;
  speaking?: boolean;
  thinking?: boolean;
  executing?: boolean;
  task_status?: string;
  notification?: string;
  error?: string;
  last_event?: string;
}

export interface ExpressiveRobotApi {
  rotateBy(deltaTheta: number, deltaPhi: number): void;
  zoomBy(factor: number): void;
  zoomIn(): void;
  zoomOut(): void;
  resetView(): void;
  setSituation(situation: ExpressiveRobotSituation): void;
  dispose(): void;
}

const MODEL_URL = "/models/RobotExpressive.glb";
const AMBER = new THREE.Color(0xffaa30);

type BaseState =
  | "Idle"
  | "Walking"
  | "Running"
  | "Dance"
  | "Sitting"
  | "Standing";

type Emote =
  | "Jump"
  | "Yes"
  | "No"
  | "Wave"
  | "Punch"
  | "ThumbsUp";

type FaceExpression =
  | "Angry"
  | "Surprised"
  | "Sad";

const BASE_STATES: BaseState[] = [
  "Idle",
  "Walking",
  "Running",
  "Dance",
  "Sitting",
  "Standing",
];

const EMOTES: Emote[] = [
  "Jump",
  "Yes",
  "No",
  "Wave",
  "Punch",
  "ThumbsUp",
];

const EXPRESSIONS: FaceExpression[] = [
  "Angry",
  "Surprised",
  "Sad",
];

export function createExpressiveRobot(
  container: HTMLElement
): ExpressiveRobotApi {

  const width = Math.max(
    container.clientWidth,
    1
  );

  const height = Math.max(
    container.clientHeight,
    1
  );

  const scene =
    new THREE.Scene();

  const camera =
    new THREE.PerspectiveCamera(
      34,
      width / height,
      0.1,
      50
    );

  // ---------------------------------------------------
  // EXPRESSIVE ROBOT FRAMING
  // ---------------------------------------------------
  //
  // The RobotExpressive model is physically large
  // relative to the JARVIS HUD viewport. Keep the
  // model at its original scale and use a wider
  // camera distance so the complete robot stays
  // comfortably visible.
  //
  // This is intentionally separate from the other
  // avatar implementations.
  // ---------------------------------------------------

  // The Expressive Robot must keep the same visual size
  // in normal and fullscreen HUD modes. The final camera
  // distance is calculated from the loaded model bounds
  // instead of relying on a fixed distance.
  camera.position.set(
    0,
    1.35,
    5.2
  );

  camera.lookAt(
    0,
    0.95,
    0
  );

  const renderer =
    new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
    });

  renderer.setPixelRatio(
    Math.min(
      window.devicePixelRatio,
      2
    )
  );

  renderer.setSize(
    width,
    height
  );

  renderer.setClearColor(
    0x000000,
    0
  );

  renderer.outputColorSpace =
    THREE.SRGBColorSpace;

  renderer.toneMapping =
    THREE.ACESFilmicToneMapping;

  renderer.toneMappingExposure =
    1.05;

  renderer.domElement.style.width =
    "100%";

  renderer.domElement.style.height =
    "100%";

  renderer.domElement.style.display =
    "block";

  container.appendChild(
    renderer.domElement
  );

  // ---------------------------------------------------
  // JARVIS HUD LIGHTING
  // ---------------------------------------------------

  const ambient =
    new THREE.AmbientLight(
      0xffffff,
      1.4
    );

  scene.add(ambient);

  const keyLight =
    new THREE.DirectionalLight(
      0xffffff,
      2.0
    );

  keyLight.position.set(
    1.5,
    3.5,
    4
  );

  scene.add(keyLight);

  const fillLight =
    new THREE.DirectionalLight(
      0xa5b8cf,
      1.0
    );

  fillLight.position.set(
    -2.5,
    2.0,
    2.0
  );

  scene.add(fillLight);

  const rimLight =
    new THREE.PointLight(
      AMBER,
      4.0,
      7.0
    );

  rimLight.position.set(
    1.5,
    2.5,
    -2
  );

  scene.add(rimLight);

  // ---------------------------------------------------
  // MODEL / ANIMATION STATE
  // ---------------------------------------------------

  let model:
    | THREE.Object3D
    | null = null;

  let mixer:
    | THREE.AnimationMixer
    | null = null;

  const actions:
    Record<
      string,
      THREE.AnimationAction
    > = {};

  let activeAction:
    | THREE.AnimationAction
    | null = null;

  let face:
    | THREE.Object3D
    | null = null;

  let faceDictionary:
    | Record<string, number>
    | null = null;

  let faceInfluences:
    | number[]
    | null = null;

  let currentBaseState:
    BaseState = "Idle";

  let lastSituationKey = "";

  // Keep the latest JARVIS situation even while the GLB
  // is still loading. It will be applied immediately
  // after the model and AnimationMixer are ready.
  let latestSituation:
    ExpressiveRobotSituation = {};

  let disposed = false;

  // ---------------------------------------------------
  // CAMERA / VIEW
  // ---------------------------------------------------
  //
  // Use the same OrbitControls architecture as the
  // working JARVIS ROBOT avatar. This is important:
  // mouse drag and HandTracker both operate on the same
  // camera state instead of maintaining two competing
  // rotation systems.
  // ---------------------------------------------------

  let zoom = 1;

  // Keep the current, already-correct Expressive Robot
  // size/framing while using OrbitControls for movement.
  const DEFAULT_CAMERA_Z = 5.2;
  const DEFAULT_CAMERA_Y = 1.35;
  const DEFAULT_LOOK_AT_Y = 0.95;

  // Target percentage of the available viewport height.
  const TARGET_SCREEN_HEIGHT = 0.52;

  let adaptiveCameraZ =
    DEFAULT_CAMERA_Z;

  const controls =
    new OrbitControls(
      camera,
      renderer.domElement,
    );

  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.enablePan = false;
  controls.minDistance = 2.35;
  controls.maxDistance = 8.5;
  controls.target.set(
    0,
    DEFAULT_LOOK_AT_Y,
    0,
  );
  controls.update();

  const spherical =
    new THREE.Spherical();

  const offset =
    new THREE.Vector3();

  function updateAdaptiveCamera() {

    if (!model) {
      adaptiveCameraZ =
        DEFAULT_CAMERA_Z;

      return;
    }

    const bounds =
      new THREE.Box3().setFromObject(
        model,
      );

    const modelHeight =
      Math.max(
        bounds.max.y - bounds.min.y,
        0.001,
      );

    const halfFov =
      THREE.MathUtils.degToRad(
        34 / 2,
      );

    const fittedDistance =
      modelHeight /
      (
        2 *
        Math.tan(halfFov) *
        TARGET_SCREEN_HEIGHT
      );

    adaptiveCameraZ =
      THREE.MathUtils.clamp(
        fittedDistance,
        3.5,
        12,
      );
  }

  function applyAdaptiveDistance() {

    offset
      .copy(camera.position)
      .sub(controls.target);

    if (
      offset.lengthSq() <
      0.000001
    ) {
      offset.set(
        0,
        DEFAULT_CAMERA_Y -
          DEFAULT_LOOK_AT_Y,
        adaptiveCameraZ,
      );
    }

    spherical.setFromVector3(
      offset,
    );

    spherical.radius =
      THREE.MathUtils.clamp(
        adaptiveCameraZ / zoom,
        controls.minDistance,
        controls.maxDistance,
      );

    spherical.makeSafe();

    offset.setFromSpherical(
      spherical,
    );

    camera.position
      .copy(controls.target)
      .add(offset);

    controls.update();
  }

  function rotateBy(
    deltaTheta: number,
    deltaPhi: number,
  ) {

    offset
      .copy(camera.position)
      .sub(controls.target);

    spherical.setFromVector3(
      offset,
    );

    spherical.theta -=
      deltaTheta;

    spherical.phi =
      THREE.MathUtils.clamp(
        spherical.phi - deltaPhi,
        0.12,
        Math.PI - 0.12,
      );

    spherical.makeSafe();

    offset.setFromSpherical(
      spherical,
    );

    camera.position
      .copy(controls.target)
      .add(offset);

    controls.update();
  }

  function zoomBy(
    factor: number,
  ) {

    zoom =
      THREE.MathUtils.clamp(
        zoom * factor,
        0.65,
        2.4,
      );

    offset
      .copy(camera.position)
      .sub(controls.target);

    if (
      offset.lengthSq() <
      0.000001
    ) {
      offset.set(
        0,
        DEFAULT_CAMERA_Y -
          DEFAULT_LOOK_AT_Y,
        adaptiveCameraZ,
      );
    }

    offset.setLength(
      THREE.MathUtils.clamp(
        adaptiveCameraZ / zoom,
        controls.minDistance,
        controls.maxDistance,
      ),
    );

    camera.position
      .copy(controls.target)
      .add(offset);

    controls.update();
  }

  function zoomIn() {
    zoomBy(0.68);
  }

  function zoomOut() {
    zoomBy(1.47);
  }

  function resetView() {

    zoom = 1;

    controls.target.set(
      0,
      DEFAULT_LOOK_AT_Y,
      0,
    );

    camera.position.set(
      0,
      DEFAULT_CAMERA_Y,
      adaptiveCameraZ,
    );

    controls.update();
  }

  // ---------------------------------------------------
  // ANIMATION HELPERS
  // ---------------------------------------------------

  function findAction(
    name: string
  ) {

    // Keep the official RobotExpressive animation names
    // as the source of truth.
    if (
      !BASE_STATES.includes(
        name as BaseState
      ) &&
      !EMOTES.includes(
        name as Emote
      )
    ) {
      return null;
    }

    return actions[name] ?? null;
  }

  function fadeToAction(
    name: string,
    duration = 0.35
  ) {

    const next =
      findAction(name);

    if (!next) {
      return;
    }

    const previous =
      activeAction;

    if (
      previous === next
    ) {
      return;
    }

    if (previous) {
      previous.fadeOut(
        duration
      );
    }

    next
      .reset()
      .setEffectiveTimeScale(1)
      .setEffectiveWeight(1)
      .fadeIn(duration)
      .play();

    activeAction =
      next;
  }

  function playBaseState(
    state: BaseState
  ) {

    if (!actions[state]) {
      return;
    }

    currentBaseState =
      state;

    const action =
      actions[state];

    action.loop =
      THREE.LoopRepeat;

    action.clampWhenFinished =
      false;

    fadeToAction(
      state,
      0.3
    );
  }

  function playEmote(
    emote: Emote
  ) {

    const action =
      actions[emote];

    if (!action) {
      return;
    }

    const previousBase =
      currentBaseState;

    action.reset();
    action.setLoop(
      THREE.LoopOnce,
      1
    );
    action.clampWhenFinished =
      true;

    const restore =
      () => {

        mixer?.removeEventListener(
          "finished",
          restore
        );

        playBaseState(
          previousBase
        );
      };

    mixer?.addEventListener(
      "finished",
      restore
    );

    action
      .setEffectiveTimeScale(1)
      .setEffectiveWeight(1)
      .fadeIn(0.18)
      .play();

    activeAction =
      action;
  }

  function findFaceTarget(
    expression: FaceExpression
  ): number | null {

    if (!faceDictionary) {
      return null;
    }

    const exact =
      faceDictionary[
        expression
      ];

    if (
      typeof exact ===
      "number"
    ) {
      return exact;
    }

    const wanted =
      expression.toLowerCase();

    const key =
      Object.keys(
        faceDictionary
      ).find(
        (name) => {
          const normalized =
            name
              .toLowerCase()
              .replace(
                /[ _-]/g,
                ""
              );

          const target =
            wanted.replace(
              /[ _-]/g,
              ""
            );

          return (
            normalized === target ||
            normalized.includes(target) ||
            target.includes(normalized)
          );
        }
      );

    return key
      ? faceDictionary[key]
      : null;
  }

  function setExpression(
    expression: FaceExpression,
    weight: number
  ) {

    if (
      !faceInfluences
    ) {
      return;
    }

    if (
      !EXPRESSIONS.includes(
        expression
      )
    ) {
      return;
    }

    const index =
      findFaceTarget(
        expression
      );

    if (
      index === null
    ) {
      return;
    }

    faceInfluences[index] =
      THREE.MathUtils.clamp(
        weight,
        0,
        1
      );
  }

  function clearExpressions() {

    if (
      !faceInfluences ||
      !faceDictionary
    ) {
      return;
    }

    for (
      const index of Object.values(
        faceDictionary
      )
    ) {
      faceInfluences[index] = 0;
    }
  }

  // ---------------------------------------------------
  // AUTOMATIC JARVIS BEHAVIOUR
  // ---------------------------------------------------

  function setSituation(
    situation: ExpressiveRobotSituation
  ) {

    // Always remember the latest JARVIS state.
    // The model may still be loading.
    latestSituation = {
      ...situation,
    };

    if (!model || !mixer) {
      return;
    }

    const error =
      String(
        situation.error ?? ""
      ).trim();

    const taskStatus =
      String(
        situation.task_status ?? ""
      ).toLowerCase();

    const notification =
      String(
        situation.notification ?? ""
      ).toLowerCase();

    const lastEvent =
      String(
        situation.last_event ?? ""
      ).toLowerCase();

    const status =
      String(
        situation.status ?? ""
      ).toLowerCase();

    const key =
      [
        situation.listening ? "L" : "",
        situation.speaking ? "S" : "",
        situation.thinking ? "T" : "",
        situation.executing ? "E" : "",
        taskStatus,
        notification,
        error,
        lastEvent,
        status,
      ].join("|");

    if (
      key === lastSituationKey
    ) {
      return;
    }

    lastSituationKey =
      key;

    // -------------------------------------------------
    // ERROR / FAILURE
    // -------------------------------------------------

    if (
      error ||
      taskStatus.includes("error") ||
      taskStatus.includes("failed") ||
      taskStatus.includes("failure")
    ) {

      clearExpressions();

      setExpression(
        "Angry",
        0.85
      );

      playEmote(
        "No"
      );

      return;
    }

    // -------------------------------------------------
    // SUCCESS
    // -------------------------------------------------

    if (
      taskStatus.includes("success") ||
      taskStatus.includes("complete") ||
      taskStatus.includes("done") ||
      notification.includes("success") ||
      notification.includes("complete")
    ) {

      clearExpressions();

      playEmote(
        "ThumbsUp"
      );

      return;
    }

    // -------------------------------------------------
    // LISTENING
    // -------------------------------------------------

    if (
      situation.listening
    ) {

      clearExpressions();

      playBaseState(
        "Standing"
      );

      return;
    }

    // -------------------------------------------------
    // THINKING
    // -------------------------------------------------

    if (
      situation.thinking
    ) {

      clearExpressions();

      // Standing is more natural for processing than
      // making the robot walk in place.
      playBaseState(
        "Standing"
      );

      return;
    }

    // -------------------------------------------------
    // EXECUTING
    // -------------------------------------------------

    if (
      situation.executing
    ) {

      clearExpressions();

      // Use Walking for an active task. This is the
      // closest continuous action in RobotExpressive.
      playBaseState(
        "Walking"
      );

      return;
    }

    // -------------------------------------------------
    // SPEAKING
    // -------------------------------------------------

    if (
      situation.speaking
    ) {

      clearExpressions();

      playBaseState(
        "Idle"
      );

      return;
    }

    // -------------------------------------------------
    // EVENT / ACTION MAPPING
    // -------------------------------------------------
    //
    // These allow richer JARVIS events to trigger the
    // RobotExpressive emotes without exposing manual
    // animation buttons in the HUD.
    // -------------------------------------------------

    const actionText =
      [
        lastEvent,
        notification,
        taskStatus,
        status,
      ].join(" ");

    if (
      actionText.includes("wave") ||
      actionText.includes("greeting") ||
      actionText.includes("hello")
    ) {

      clearExpressions();

      playEmote(
        "Wave"
      );

      return;
    }

    if (
      actionText.includes("jump")
    ) {

      clearExpressions();

      playEmote(
        "Jump"
      );

      return;
    }

    if (
      actionText.includes("yes") ||
      actionText.includes("confirm") ||
      actionText.includes("approved")
    ) {

      clearExpressions();

      playEmote(
        "Yes"
      );

      return;
    }

    if (
      actionText.includes("no") ||
      actionText.includes("deny") ||
      actionText.includes("denied")
    ) {

      clearExpressions();

      playEmote(
        "No"
      );

      return;
    }

    if (
      actionText.includes("punch")
    ) {

      clearExpressions();

      playEmote(
        "Punch"
      );

      return;
    }

    // -------------------------------------------------
    // AUTOMATIC FACE EXPRESSIONS
    // -------------------------------------------------

    if (
      actionText.includes("surpris") ||
      actionText.includes("wow") ||
      actionText.includes("unexpected")
    ) {

      clearExpressions();

      setExpression(
        "Surprised",
        0.90
      );

      playBaseState(
        "Standing"
      );

      return;
    }

    if (
      actionText.includes("angry") ||
      actionText.includes("frustrat")
    ) {

      clearExpressions();

      setExpression(
        "Angry",
        0.80
      );

      playBaseState(
        "Standing"
      );

      return;
    }

    if (
      actionText.includes("sad")
    ) {

      clearExpressions();

      setExpression(
        "Sad",
        0.80
      );

      playBaseState(
        "Standing"
      );

      return;
    }

    // -------------------------------------------------
    // DEFAULT
    // -------------------------------------------------

    clearExpressions();

    playBaseState(
      "Idle"
    );
  }

  // ---------------------------------------------------
  // LOAD ROBOT EXPRESSIVE MODEL
  // ---------------------------------------------------

  const loader =
    new GLTFLoader();

  loader.load(
    MODEL_URL,

    (gltf) => {

      if (disposed) {
        return;
      }

      model =
        gltf.scene;

      scene.add(
        model
      );

      // The official Three.js model
      // is authored at a convenient
      // human scale. Adjust it for
      // the JARVIS viewport.

      // The RobotExpressive asset is much larger than
      // the visual scale used by the other JARVIS
      // avatars. Keep its proportions and animations
      // intact, but render it at a compact HUD scale.
      model.scale.setScalar(
        0.55
      );

      model.position.set(
        0,
        0,
        0
      );

      updateAdaptiveCamera();

      // -------------------------------------------------
      // ANIMATION MIXER
      // -------------------------------------------------

      mixer =
        new THREE.AnimationMixer(
          model
        );

      for (
        const clip of
        gltf.animations
      ) {

        const action =
          mixer.clipAction(
            clip
          );

        actions[
          clip.name
        ] = action;

        if (
          EMOTES.includes(
            clip.name as Emote
          )
        ) {

          action.loop =
            THREE.LoopOnce;

          action.clampWhenFinished =
            true;

        }
      }

      // -------------------------------------------------
      // FACE MORPHS
      // -------------------------------------------------

      model.traverse(
        (object) => {

          const mesh =
            object as THREE.Mesh;

          if (
            mesh.morphTargetDictionary &&
            mesh.morphTargetInfluences
          ) {

            if (
              !face
            ) {

              face =
                mesh;

              faceDictionary =
                mesh.morphTargetDictionary;

              faceInfluences =
                mesh.morphTargetInfluences;
            }
          }
        }
      );

      // Recalculate the correct camera distance using
      // the loaded model's actual bounds, then frame it
      // with the same camera architecture as the other
      // JARVIS avatars.
      updateAdaptiveCamera();

      resetView();

      // Start in JARVIS idle mode.
      playBaseState(
        "Idle"
      );

      // Apply the latest JARVIS situation immediately.
      // This is important because the model can finish
      // loading after JARVIS has already entered a state.
      lastSituationKey = "";

      setSituation(
        latestSituation
      );

    },

    undefined,

    (error) => {

      console.error(
        "[EXPRESSIVE ROBOT] Model load failed:",
        error
      );

    }
  );

  // ---------------------------------------------------
  // EXISTING JARVIS STATE BRIDGE
  // ---------------------------------------------------
  //
  // The working JARVIS avatar already publishes
  // "jarvis-assistant-state". Listen to the same event
  // so EXPRESSIVE automatically follows the real JARVIS
  // state without requiring manual animation buttons.
  // ---------------------------------------------------

  const handleJarvisState = (
    event: Event
  ) => {

    const customEvent =
      event as CustomEvent<{
        state?: string;
      }>;

    const next =
      String(
        customEvent.detail?.state ?? ""
      ).toLowerCase();

    if (
      next === "idle" ||
      next === "listening" ||
      next === "thinking" ||
      next === "speaking" ||
      next === "executing"
    ) {

      setSituation({
        status: next,
        listening:
          next === "listening",
        thinking:
          next === "thinking",
        speaking:
          next === "speaking",
        executing:
          next === "executing",
      });

    }
  };

  window.addEventListener(
    "jarvis-assistant-state",
    handleJarvisState
  );

  // ---------------------------------------------------
  // RESIZE
  // ---------------------------------------------------

  const resizeObserver =
    new ResizeObserver(
      () => {

        if (disposed) {
          return;
        }

        const nextWidth =
          Math.max(
            container.clientWidth,
            1
          );

        const nextHeight =
          Math.max(
            container.clientHeight,
            1
          );

        camera.aspect =
          nextWidth /
          nextHeight;

        camera.updateProjectionMatrix();

        updateAdaptiveCamera();

        renderer.setSize(
          nextWidth,
          nextHeight
        );
      }
    );

  resizeObserver.observe(
    container
  );

  // ---------------------------------------------------
  // RENDER LOOP
  // ---------------------------------------------------

  let previousTime =
    performance.now();

  let animationFrame =
    0;

  function animate(
    now: number
  ) {

    if (disposed) {
      return;
    }

    const delta =
      Math.min(
        (now - previousTime) /
          1000,
        0.1
      );

    previousTime =
      now;

    // OrbitControls is the single camera controller for
    // the Expressive Robot. Mouse, wheel, +/− buttons,
    // and HandTracker all update the same camera state.
    mixer?.update(
      delta
    );

    controls.update();

    renderer.render(
      scene,
      camera
    );

    animationFrame =
      requestAnimationFrame(
        animate
      );
  }

  animationFrame =
    requestAnimationFrame(
      animate
    );

  // ---------------------------------------------------
  // DISPOSE
  // ---------------------------------------------------

  function dispose() {

    disposed = true;

    cancelAnimationFrame(
      animationFrame
    );

    resizeObserver.disconnect();

    window.removeEventListener(
      "jarvis-assistant-state",
      handleJarvisState
    );

    mixer?.stopAllAction();

    controls.dispose();

    renderer.dispose();

    if (
      renderer.domElement.parentElement ===
      container
    ) {
      container.removeChild(
        renderer.domElement
      );
    }

    scene.traverse(
      (object) => {

        const mesh =
          object as THREE.Mesh;

        if (
          mesh.geometry
        ) {
          mesh.geometry.dispose();
        }

        const material =
          mesh.material;

        if (
          Array.isArray(material)
        ) {

          material.forEach(
            (item) =>
              item.dispose()
          );

        } else if (
          material
        ) {

          material.dispose();

        }
      }
    );
  }

  return {
    rotateBy,
    zoomBy,
    zoomIn,
    zoomOut,
    resetView,
    setSituation,
    dispose,
  };
}
