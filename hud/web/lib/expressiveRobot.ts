import * as THREE from "three";
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

  let disposed = false;

  // ---------------------------------------------------
  // CAMERA / VIEW
  // ---------------------------------------------------

  let rotationY = 0;
  let rotationX = 0;

  let targetRotationY = 0;
  let targetRotationX = 0;

  let zoom = 1;

  // Wider default framing for the Expressive Robot.
  // This keeps the full body visible instead of
  // filling the entire HUD.
  const DEFAULT_CAMERA_Z = 5.2;

  const DEFAULT_CAMERA_Y = 1.35;
  const DEFAULT_LOOK_AT_Y = 0.95;

  function applyCamera() {

    const x =
      Math.sin(rotationY) *
      DEFAULT_CAMERA_Z /
      zoom;

    const z =
      Math.cos(rotationY) *
      DEFAULT_CAMERA_Z /
      zoom;

    camera.position.x =
      x;

    camera.position.z =
      z;

    camera.position.y =
      DEFAULT_CAMERA_Y +
      rotationX;

    camera.lookAt(
      0,
      DEFAULT_LOOK_AT_Y,
      0
    );
  }

  function rotateBy(
    deltaTheta: number,
    deltaPhi: number
  ) {

    targetRotationY +=
      deltaTheta;

    targetRotationX =
      THREE.MathUtils.clamp(
        targetRotationX +
          deltaPhi,
        -0.8,
        0.8
      );
  }

  function zoomBy(
    factor: number
  ) {

    zoom =
      THREE.MathUtils.clamp(
        zoom * factor,
        0.65,
        2.4
      );
  }

  function zoomIn() {
    zoomBy(1.15);
  }

  function zoomOut() {
    zoomBy(0.87);
  }

  function resetView() {

    targetRotationY = 0;
    targetRotationX = 0;
    zoom = 1;
  }

  // ---------------------------------------------------
  // ANIMATION HELPERS
  // ---------------------------------------------------

  function findAction(
    name: string
  ) {

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
        (name) =>
          name.toLowerCase() ===
          wanted
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

    if (!model) {
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

      // Start in JARVIS idle mode.

      playBaseState(
        "Idle"
      );

      // Re-apply any situation
      // received before model load.

      if (
        lastSituationKey
      ) {

        lastSituationKey =
          "";

      }

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

    targetRotationY =
      THREE.MathUtils.clamp(
        targetRotationY,
        -Math.PI,
        Math.PI
      );

    rotationY +=
      (
        targetRotationY -
        rotationY
      ) * 0.12;

    rotationX +=
      (
        targetRotationX -
        rotationX
      ) * 0.12;

    applyCamera();

    mixer?.update(
      delta
    );

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

    mixer?.stopAllAction();

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
