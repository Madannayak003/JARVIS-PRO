import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

export interface FlyingRobotSceneApi {
  rotateBy(deltaTheta: number, deltaPhi: number): void;
  zoomBy(factor: number): void;
  zoomIn(): void;
  zoomOut(): void;
  resetView(): void;
  dispose(): void;
}

type JarvisState =
  | "idle"
  | "listening"
  | "thinking"
  | "speaking"
  | "executing";

const MODEL_URL = "/models/flying_robot.glb";

/*
 * Visual size of the flying robot.
 *
 * The original 2.50 made the robot too large for
 * the HUD and caused the top of the model to feel
 * clipped.
 */
const MODEL_HEIGHT = 2.10;

const MIN_DISTANCE = 2.35;
const MAX_DISTANCE = 8.5;

/*
 * Default camera position.
 *
 * Slightly farther away gives the complete flying
 * robot comfortable space inside the HUD.
 */
const DEFAULT_CAMERA_POSITION = new THREE.Vector3(
  0,
  0,
  5.8,
);

const DEFAULT_TARGET = new THREE.Vector3(
  0,
  0,
  0,
);

export function createFlyingRobot(
  container: HTMLElement,
): FlyingRobotSceneApi {
  const width = Math.max(
    container.clientWidth,
    1,
  );

  const height = Math.max(
    container.clientHeight,
    1,
  );

  // ----------------------------------------------------------
  // SCENE
  // ----------------------------------------------------------

  const scene = new THREE.Scene();

  // ----------------------------------------------------------
  // CAMERA
  // ----------------------------------------------------------

  const camera =
    new THREE.PerspectiveCamera(
      38,
      width / height,
      0.05,
      100,
    );

  camera.position.copy(
    DEFAULT_CAMERA_POSITION,
  );

  // ----------------------------------------------------------
  // RENDERER
  // ----------------------------------------------------------

  const renderer =
    new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
    });

  renderer.setPixelRatio(
    Math.min(
      window.devicePixelRatio || 1,
      2,
    ),
  );

  renderer.setSize(
    width,
    height,
  );

  renderer.outputColorSpace =
    THREE.SRGBColorSpace;

  renderer.setClearColor(
    0x000000,
    0,
  );

  container.appendChild(
    renderer.domElement,
  );

  // ----------------------------------------------------------
  // LIGHTING
  // ----------------------------------------------------------

  const ambient =
    new THREE.AmbientLight(
      0xffffff,
      1.6,
    );

  scene.add(ambient);

  const keyLight =
    new THREE.DirectionalLight(
      0xffffff,
      2.2,
    );

  keyLight.position.set(
    3,
    4,
    5,
  );

  scene.add(keyLight);

  const rimLight =
    new THREE.PointLight(
      0x20eaff,
      3.0,
      10,
    );

  rimLight.position.set(
    -3,
    2,
    -2,
  );

  scene.add(rimLight);

  // ----------------------------------------------------------
  // ORBIT CONTROLS
  // ----------------------------------------------------------

  const controls =
    new OrbitControls(
      camera,
      renderer.domElement,
    );

  controls.enableDamping = true;
  controls.dampingFactor = 0.07;

  controls.enablePan = false;

  controls.minDistance =
    MIN_DISTANCE;

  controls.maxDistance =
    MAX_DISTANCE;

  controls.target.copy(
    DEFAULT_TARGET,
  );

  // ----------------------------------------------------------
  // MODEL
  // ----------------------------------------------------------

  let model:
    THREE.Object3D | null = null;

  /*
   * IMPORTANT:
   *
   * The GLB is centered after loading.
   * Animation must move relative to this position,
   * not replace it.
   */
  const modelBasePosition =
    new THREE.Vector3();

  let disposed = false;

  const loader =
    new GLTFLoader();

  loader.load(
    MODEL_URL,

    (gltf) => {
      if (disposed) {
        return;
      }

      model = gltf.scene;

      model.name =
        "JARVIS_FLYING_ROBOT";

      // ------------------------------------------------------
      // AUTO-FIT MODEL
      // ------------------------------------------------------

      const rawBox =
        new THREE.Box3()
          .setFromObject(model);

      const rawSize =
        new THREE.Vector3();

      rawBox.getSize(
        rawSize,
      );

      if (rawSize.y > 0) {
        model.scale.setScalar(
          MODEL_HEIGHT /
            rawSize.y,
        );
      }

      // ------------------------------------------------------
      // CENTER MODEL
      // ------------------------------------------------------

      const fittedBox =
        new THREE.Box3()
          .setFromObject(model);

      const center =
        new THREE.Vector3();

      fittedBox.getCenter(
        center,
      );

      /*
       * Center the entire GLB around
       * the camera target.
       */
      model.position.x -=
        center.x;

      model.position.y -=
        center.y;

      model.position.z -=
        center.z;

      /*
       * Save the correctly centered position.
       *
       * The animation loop will always animate
       * relative to this position.
       */
      modelBasePosition.copy(
        model.position,
      );

      scene.add(model);
    },

    undefined,

    (error) => {
      console.error(
        "[JARVIS FLYING ROBOT] Failed to load GLB:",
        error,
      );
    },
  );

  // ----------------------------------------------------------
  // STATE
  // ----------------------------------------------------------

  let state: JarvisState =
    "idle";

  function handleState(
    event: Event,
  ) {
    const customEvent =
      event as CustomEvent<{
        state?: JarvisState;
      }>;

    if (
      customEvent.detail?.state
    ) {
      state =
        customEvent.detail.state;
    }
  }

  window.addEventListener(
    "jarvis-assistant-state",
    handleState,
  );

  // ----------------------------------------------------------
  // ANIMATION
  // ----------------------------------------------------------

  const clock =
    new THREE.Clock();

  let rafId = 0;

  function animate() {
    if (disposed) {
      return;
    }

    rafId =
      requestAnimationFrame(
        animate,
      );

    const t =
      clock.getElapsedTime();

    if (model) {
      // ----------------------------------------------------
      // STATE-BASED FLOATING
      // ----------------------------------------------------

      let floatAmount =
        0.035;

      let floatSpeed =
        1.4;

      if (
        state === "listening"
      ) {
        floatAmount =
          0.055;

        floatSpeed =
          2.2;
      }

      if (
        state === "speaking"
      ) {
        floatAmount =
          0.07;

        floatSpeed =
          2.8;
      }

      /*
       * Always animate from the original centered
       * position.
       *
       * This prevents the model from slowly becoming
       * vertically misplaced.
       */
      model.position.x =
        modelBasePosition.x;

      model.position.y =
        modelBasePosition.y +
        Math.sin(
          t * floatSpeed,
        ) *
          floatAmount;

      model.position.z =
        modelBasePosition.z;

      // ----------------------------------------------------
      // SUBTLE IDLE ROTATION
      // ----------------------------------------------------

      model.rotation.y =
        Math.sin(
          t * 0.45,
        ) *
          0.025;
    }

    controls.update();

    renderer.render(
      scene,
      camera,
    );
  }

  animate();

  // ----------------------------------------------------------
  // CAMERA CONTROLS
  // ----------------------------------------------------------

  function rotateBy(
    deltaTheta: number,
    deltaPhi: number,
  ) {
    const offset =
      camera.position
        .clone()
        .sub(
          controls.target,
        );

    /*
     * Horizontal rotation.
     */
    offset.applyAxisAngle(
      new THREE.Vector3(
        0,
        1,
        0,
      ),
      deltaTheta,
    );

    /*
     * Vertical rotation.
     *
     * Kept intentionally subtle so the flying robot
     * remains visually stable in the HUD.
     */
    const horizontalDistance =
      Math.sqrt(
        offset.x * offset.x +
          offset.z * offset.z,
      );

    if (
      horizontalDistance > 0.0001
    ) {
      const currentPhi =
        Math.atan2(
          offset.y,
          horizontalDistance,
        );

      const nextPhi =
        THREE.MathUtils.clamp(
          currentPhi +
            deltaPhi,
          -1.15,
          1.15,
        );

      offset.y =
        Math.sin(nextPhi) *
        offset.length();

      const horizontalScale =
        Math.cos(nextPhi);

      const horizontalLength =
        Math.sqrt(
          offset.x * offset.x +
            offset.z * offset.z,
        );

      if (
        horizontalLength > 0.0001
      ) {
        const scale =
          (horizontalScale *
            offset.length()) /
          horizontalLength;

        offset.x *= scale;
        offset.z *= scale;
      }
    }

    camera.position.copy(
      controls.target
        .clone()
        .add(offset),
    );

    controls.update();
  }

  function zoomBy(
    factor: number,
  ) {
    const offset =
      camera.position
        .clone()
        .sub(
          controls.target,
        );

    const distance =
      offset.length();

    const nextDistance =
      THREE.MathUtils.clamp(
        distance * factor,
        MIN_DISTANCE,
        MAX_DISTANCE,
      );

    offset.setLength(
      nextDistance,
    );

    camera.position.copy(
      controls.target
        .clone()
        .add(offset),
    );

    controls.update();
  }

  function resetView() {
    camera.position.copy(
      DEFAULT_CAMERA_POSITION,
    );

    controls.target.copy(
      DEFAULT_TARGET,
    );

    controls.update();
  }

  // ----------------------------------------------------------
  // RESIZE
  // ----------------------------------------------------------

  function onResize() {
    const w =
      Math.max(
        container.clientWidth,
        1,
      );

    const h =
      Math.max(
        container.clientHeight,
        1,
      );

    camera.aspect =
      w / h;

    camera.updateProjectionMatrix();

    renderer.setSize(
      w,
      h,
    );
  }

  window.addEventListener(
    "resize",
    onResize,
  );

  // ----------------------------------------------------------
  // CLEANUP
  // ----------------------------------------------------------

  function dispose() {
    disposed = true;

    cancelAnimationFrame(
      rafId,
    );

    window.removeEventListener(
      "resize",
      onResize,
    );

    window.removeEventListener(
      "jarvis-assistant-state",
      handleState,
    );

    controls.dispose();

    scene.traverse(
      (object) => {
        const mesh =
          object as THREE.Mesh;

        if (mesh.geometry) {
          mesh.geometry.dispose();
        }

        const materials =
          Array.isArray(
            mesh.material,
          )
            ? mesh.material
            : mesh.material
              ? [mesh.material]
              : [];

        for (
          const material of materials
        ) {
          material.dispose();
        }
      },
    );

    renderer.dispose();

    if (
      renderer.domElement
        .parentElement
    ) {
      renderer.domElement.remove();
    }
  }

  // ----------------------------------------------------------
  // PUBLIC API
  // ----------------------------------------------------------

  return {
    rotateBy,

    zoomBy,

    zoomIn: () =>
      zoomBy(0.68),

    zoomOut: () =>
      zoomBy(1.47),

    resetView,

    dispose,
  };
}