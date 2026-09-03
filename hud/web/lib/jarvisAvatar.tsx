import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";

export interface OrbSceneApi {
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

const AMBER = new THREE.Color(0xffa51f);
const BRIGHT = new THREE.Color(0xffd27a);
const DIM = new THREE.Color(0x6a4314);

const MODEL_URL = "/models/jarvis.glb";

// The uploaded robot is ~0.40 scene-units tall.
// Scale it to a useful HUD size without changing its geometry.
const MODEL_HEIGHT = 2.50;

const MIN_DISTANCE = 2.35;
const MAX_DISTANCE = 8.5;

function makeRing(
  radius: number,
  color: THREE.Color,
  opacity: number,
): THREE.LineLoop {
  const points: THREE.Vector3[] = [];
  const segments = 128;

  for (let i = 0; i < segments; i += 1) {
    const a = (i / segments) * Math.PI * 2;
    points.push(
      new THREE.Vector3(
        Math.cos(a) * radius,
        0,
        Math.sin(a) * radius,
      ),
    );
  }

  const geometry =
    new THREE.BufferGeometry().setFromPoints(points);

  const material = new THREE.LineBasicMaterial({
    color,
    transparent: true,
    opacity,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });

  return new THREE.LineLoop(geometry, material);
}

function isMesh(
  object: THREE.Object3D,
): object is THREE.Mesh {
  return object instanceof THREE.Mesh;
}

export function createJarvisAvatar(
  container: HTMLElement,
): OrbSceneApi {
  const width = Math.max(container.clientWidth, 1);
  const height = Math.max(container.clientHeight, 1);

  const scene = new THREE.Scene();

  const camera = new THREE.PerspectiveCamera(
    38,
    width / height,
    0.05,
    100,
  );

  // Framed for the real robot bust.
  camera.position.set(0, 1.58, 6.05);

  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
  });

  renderer.setPixelRatio(
    Math.min(window.devicePixelRatio, 2),
  );
  renderer.setSize(width, height);
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping =
    THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.68;

  renderer.domElement.style.width = "100%";
  renderer.domElement.style.height = "100%";
  renderer.domElement.style.display = "block";

  container.appendChild(renderer.domElement);

  // ----------------------------------------------------------
  // Lighting
  // Keep the original model opaque and realistic.
  // The previous renderer made everything transparent/additive,
  // which caused this robot's dark materials to disappear.
  // ----------------------------------------------------------

  const ambient = new THREE.AmbientLight(
    0xffffff,
    0.62,
  );
  scene.add(ambient);

  // Neutral front light keeps the white face readable.
  // JARVIS colour is intentionally NOT projected into the face.
  const keyLight = new THREE.DirectionalLight(
    0xffffff,
    1.05,
  );
  keyLight.position.set(0.8, 3.4, 5.5);
  scene.add(keyLight);

  const fillLight = new THREE.DirectionalLight(
    0xb8c0ca,
    0.58,
  );
  fillLight.position.set(-3.2, 1.2, 2.8);
  scene.add(fillLight);

  // Amber is now a side/back rim, giving the model a JARVIS edge
  // without turning the entire face orange.
  const rimLight = new THREE.PointLight(
    AMBER,
    2.0,
    7.0,
  );
  rimLight.position.set(2.8, 2.5, -1.8);
  scene.add(rimLight);

  // A cool neutral rim reveals the black torso against the HUD.
  const bodyRimLight = new THREE.PointLight(
    0x8797aa,
    1.7,
    7.0,
  );
  bodyRimLight.position.set(-2.8, 1.3, -1.6);
  scene.add(bodyRimLight);

  // Focused soft spotlights keep the face and black suit readable
  // without washing the white face in amber.
  const faceSpot = new THREE.SpotLight(
    0xffffff,
    1.55,
    9.0,
    Math.PI / 7,
    0.72,
    1.0,
  );
  faceSpot.position.set(0.6, 3.7, 4.2);
  faceSpot.target.position.set(0, 1.75, 0);
  scene.add(faceSpot);
  scene.add(faceSpot.target);

  const shoulderSpot = new THREE.SpotLight(
    0xd9e2ee,
    2.0,
    7.5,
    Math.PI / 5,
    0.82,
    1.0,
  );
  shoulderSpot.position.set(-3.0, 1.4, 3.0);
  shoulderSpot.target.position.set(0, 0.72, 0);
  scene.add(shoulderSpot);
  scene.add(shoulderSpot.target);

  const composer = new EffectComposer(renderer);

  composer.addPass(
    new RenderPass(scene, camera),
  );

  const bloom = new UnrealBloomPass(
    new THREE.Vector2(width, height),
    0.10,
    0.24,
    0.96,
  );

  composer.addPass(bloom);

  const controls = new OrbitControls(
    camera,
    renderer.domElement,
  );

  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.enablePan = false;
  controls.minDistance = MIN_DISTANCE;
  controls.maxDistance = MAX_DISTANCE;
  controls.target.set(0, 1.50, 0);
  controls.update();

  // ----------------------------------------------------------
  // Avatar container
  // ----------------------------------------------------------

  const avatar = new THREE.Group();
  scene.add(avatar);

  // Simple half-sleeve silhouette behind the source bust.
  // This stays inside the avatar renderer so orbScene.ts remains untouched.
  const sleeves = new THREE.Group();
  sleeves.name = "JARVIS_HALF_SLEEVES";
  avatar.add(sleeves);

  const sleeveMaterial =
    new THREE.MeshStandardMaterial({
      color: 0x10141a,
      metalness: 0.78,
      roughness: 0.30,
    });

  const sleeveAccentMaterial =
    new THREE.MeshStandardMaterial({
      color: 0x202831,
      metalness: 0.72,
      roughness: 0.34,
      emissive: 0x221400,
      emissiveIntensity: 0.12,
    });

  function createHalfSleeve(side: number) {
    const group = new THREE.Group();

    const upper = new THREE.Mesh(
      new THREE.SphereGeometry(0.62, 32, 20),
      sleeveMaterial,
    );
    upper.scale.set(1.05, 0.72, 0.88);
    upper.position.set(
      side * 1.02,
      0.76,
      -0.02,
    );
    group.add(upper);

    const lower = new THREE.Mesh(
      new THREE.CylinderGeometry(
        0.43,
        0.50,
        0.72,
        32,
      ),
      sleeveAccentMaterial,
    );
    lower.rotation.z =
      side * (Math.PI * 0.18);
    lower.position.set(
      side * 1.22,
      0.40,
      -0.02,
    );
    group.add(lower);

    return group;
  }

  sleeves.add(createHalfSleeve(-1));
  sleeves.add(createHalfSleeve(1));

  // ----------------------------------------------------------
  // Ambient HUD rings
  // They stay behind the actual face.
  // ----------------------------------------------------------

  const aura = new THREE.Group();
  aura.position.set(0, -0.95, -0.35);
  avatar.add(aura);

  const ring1 = makeRing(
    1.85,
    AMBER,
    0.16,
  );
  ring1.rotation.x = Math.PI / 2;
  aura.add(ring1);

  const ring2 = makeRing(
    2.35,
    DIM,
    0.09,
  );
  ring2.rotation.x = Math.PI / 2;
  aura.add(ring2);

  const ring3 = makeRing(
    1.25,
    BRIGHT,
    0.10,
  );
  ring3.rotation.x = Math.PI / 2;
  ring3.position.y = 0.62;
  aura.add(ring3);

  // ----------------------------------------------------------
  // Subtle particles
  // ----------------------------------------------------------

  const particleCount = 180;
  const positions =
    new Float32Array(particleCount * 3);

  for (let i = 0; i < particleCount; i += 1) {
    const radius =
      2.0 + Math.random() * 2.3;

    const theta =
      Math.random() * Math.PI * 2;

    const phi =
      Math.acos(2 * Math.random() - 1);

    positions[i * 3] =
      radius *
      Math.sin(phi) *
      Math.cos(theta);

    positions[i * 3 + 1] =
      radius *
      Math.cos(phi) *
      0.68;

    positions[i * 3 + 2] =
      radius *
      Math.sin(phi) *
      Math.sin(theta);
  }

  const particleGeometry =
    new THREE.BufferGeometry();

  particleGeometry.setAttribute(
    "position",
    new THREE.BufferAttribute(
      positions,
      3,
    ),
  );

  const particleMaterial =
    new THREE.PointsMaterial({
      color: AMBER,
      size: 0.015,
      transparent: true,
      opacity: 0.24,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });

  const particles = new THREE.Points(
    particleGeometry,
    particleMaterial,
  );

  scene.add(particles);

  // ----------------------------------------------------------
  // Real model references.
  // These names come from the uploaded GLB.
  // ----------------------------------------------------------

  let model: THREE.Object3D | null = null;

  let faceRoot: THREE.Object3D | null = null;
  let jaw: THREE.Object3D | null = null;
  let leftEye: THREE.Object3D | null = null;
  let rightEye: THREE.Object3D | null = null;
  let forehead: THREE.Object3D | null = null;
  let jawBaseRotationX = 0;

  const eyeBase = new Map<
    THREE.Object3D,
    {
      position: THREE.Vector3;
      scale: THREE.Vector3;
      rotation: THREE.Euler;
    }
  >();

  // Small eye offsets make the real eyeball meshes look around
  // without moving the surrounding face.
  const eyeLookX = 0.0;
  const eyeLookY = 0.0;

  let state: JarvisState = "idle";
  let disposed = false;

  const loader = new GLTFLoader();

  loader.load(
    MODEL_URL,
    (gltf) => {
      if (disposed) return;

      model = gltf.scene;
      model.name = "JARVIS_REAL_ROBOT_FACE";

      // --------------------------------------------------------
      // Auto-fit the actual GLB instead of guessing its size.
      // --------------------------------------------------------

      const rawBox = new THREE.Box3()
        .setFromObject(model);

      const rawSize =
        new THREE.Vector3();

      rawBox.getSize(rawSize);

      if (rawSize.y > 0) {
        model.scale.setScalar(
          MODEL_HEIGHT / rawSize.y,
        );
      }

      // Recalculate after scaling and center the model
      // horizontally and vertically around the avatar target.
      const fittedBox = new THREE.Box3()
        .setFromObject(model);

      const center =
        new THREE.Vector3();

      fittedBox.getCenter(center);

      model.position.x -= center.x;
      model.position.y -= center.y;
      model.position.z -= center.z;

      // Place the bust slightly behind the HUD center.
      model.position.y += 1.55;
      model.position.z = -0.05;

      avatar.add(model);

      model.traverse((object) => {
        if (
          object.name ===
          "RoboFace_23"
        ) {
          faceRoot = object;
        }

        if (
          object.name ===
          "Jaw.R_19"
        ) {
          jaw = object;
        }

        if (
          object.name ===
          "Kito6_FaceMesh_Eye.L_20"
        ) {
          leftEye = object;
        }

        if (
          object.name ===
          "Kito6_FaceMesh_Eye.R_21"
        ) {
          rightEye = object;
        }

        if (
          object.name ===
          "Forehead_6"
        ) {
          forehead = object;
        }

        if (!isMesh(object)) return;

        // IMPORTANT:
        // Preserve the model's original opaque materials.
        // Only add subtle JARVIS emissive treatment.
        const materials =
          Array.isArray(object.material)
            ? object.material
            : [object.material];

        for (const material of materials) {
          const standard =
            material as THREE.MeshStandardMaterial;

          // Preserve the white face and eyes.
          // Only lift very dark source materials slightly so the
          // black neck/chest remains visible on the black HUD.
          if (standard.color) {
            const r = standard.color.r;
            const g = standard.color.g;
            const b = standard.color.b;
            const luminance =
              0.2126 * r +
              0.7152 * g +
              0.0722 * b;

            if (luminance < 0.10) {
              standard.color.lerp(
                new THREE.Color(0x171b21),
                0.72,
              );
              standard.metalness = Math.max(
                standard.metalness ?? 0,
                0.65,
              );
              standard.roughness = Math.max(
                standard.roughness ?? 0.5,
                0.28,
              );
            }
          }

          if (
            "emissive" in standard
          ) {
            // No orange wash over the face.
            standard.emissiveIntensity = 0;
          }

          standard.needsUpdate = true;
        }

        // No wireframe overlay. The source model already has clean
        // mechanical surface detail and should remain recognizable.
      });

      if (jaw) {
        jawBaseRotationX = jaw.rotation.x;
      }

      // Store the exact original transforms.
      for (
        const eye of [leftEye, rightEye]
      ) {
        if (!eye) continue;

        eyeBase.set(eye, {
          position:
            eye.position.clone(),
          scale:
            eye.scale.clone(),
          rotation:
            eye.rotation.clone(),
        });
      }

      console.info(
        "[JARVIS AVATAR] Real robot face loaded:",
        {
          modelUrl: MODEL_URL,
          height: rawSize.y,
          faceRoot: Boolean(faceRoot),
          jaw: Boolean(jaw),
          leftEye: Boolean(leftEye),
          rightEye: Boolean(rightEye),
          forehead: Boolean(forehead),
        },
      );
    },
    (progress) => {
      if (progress.total > 0) {
        console.debug(
          "[JARVIS AVATAR] Loading:",
          Math.round(
            (progress.loaded /
              progress.total) *
              100,
          ) + "%",
        );
      }
    },
    (error) => {
      console.error(
        "[JARVIS AVATAR] Failed to load",
        MODEL_URL,
        error,
      );
    },
  );

  // ----------------------------------------------------------
  // JARVIS state bridge
  // ----------------------------------------------------------

  const handleState = (event: Event) => {
    const customEvent =
      event as CustomEvent<{
        state?: string;
      }>;

    const next =
      customEvent.detail?.state;

    if (
      next === "idle" ||
      next === "listening" ||
      next === "thinking" ||
      next === "speaking" ||
      next === "executing"
    ) {
      state = next;
    }
  };

  window.addEventListener(
    "jarvis-assistant-state",
    handleState,
  );

  // ----------------------------------------------------------
  // Gesture-compatible camera API
  // ----------------------------------------------------------

  const spherical =
    new THREE.Spherical();

  const offset =
    new THREE.Vector3();

  function rotateBy(
    deltaTheta: number,
    deltaPhi: number,
  ) {
    offset
      .copy(camera.position)
      .sub(controls.target);

    spherical.setFromVector3(offset);

    spherical.theta -= deltaTheta;

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

    camera.lookAt(controls.target);
  }

  function zoomBy(
    factor: number,
  ) {
    offset
      .copy(camera.position)
      .sub(controls.target);

    const distance =
      THREE.MathUtils.clamp(
        offset.length() * factor,
        MIN_DISTANCE,
        MAX_DISTANCE,
      );

    offset.setLength(distance);

    camera.position
      .copy(controls.target)
      .add(offset);
  }

  function resetView() {
    camera.position.set(
      0,
      1.58,
      6.05,
    );

    controls.target.set(
      0,
      1.50,
      0,
    );

    camera.lookAt(
      controls.target,
    );

    controls.update();
  }

  // ----------------------------------------------------------
  // Animation
  // ----------------------------------------------------------

  const clock =
    new THREE.Clock();

  let nextBlink =
    2.0 + Math.random() * 3.0;

  let blinkStart = -10;
  let blinkActive = false;
  let blinkDuration = 0.18;

  // Natural gaze target. The eyes are real GLB objects, so we move
  // the actual eyeball assemblies rather than drawing fake eyes.
  let gazeX = 0;
  let gazeY = 0;
  let targetGazeX = 0;
  let targetGazeY = 0;
  let nextGazeChange = 1.4;

  function animate() {
    if (disposed) return;

    rafId = requestAnimationFrame(
      animate,
    );

    const t =
      clock.getElapsedTime();

    const speaking =
      state === "speaking";

    const thinking =
      state === "thinking";

    const listening =
      state === "listening";

    const executing =
      state === "executing";

    // Very subtle floating motion.
    avatar.position.y =
      Math.sin(
        t *
          (speaking
            ? 1.55
            : 0.65),
      ) *
      (speaking
        ? 0.018
        : 0.010);

    // Subtle hologram movement.
    aura.rotation.y =
      t *
      (thinking
        ? 0.20
        : 0.10);

    ring1.rotation.z =
      t * 0.13;

    ring2.rotation.z =
      -t * 0.08;

    ring3.rotation.z =
      t * 0.18;

    particles.rotation.y =
      t *
      (thinking
        ? 0.035
        : 0.018);

    // --------------------------------------------------------
    // Face idle movement
    // --------------------------------------------------------

    if (faceRoot) {
      faceRoot.rotation.y =
        Math.sin(t * 0.42) *
        (listening
          ? 0.026
          : 0.012);

      faceRoot.rotation.x =
        Math.sin(t * 0.31) *
        0.008;
    }

    // --------------------------------------------------------
    // Forehead indicator
    // --------------------------------------------------------

    if (forehead) {
      const pulse =
        speaking
          ? 0.18
          : thinking
            ? 0.13
            : listening
              ? 0.10
              : 0.06;

      const scale =
        1 +
        Math.sin(
          t *
            (speaking
              ? 6.0
              : 2.8),
        ) *
          pulse;

      forehead.scale.setScalar(
        scale,
      );
    }

    // --------------------------------------------------------
    // Real eye assemblies
    //
    // The GLB has no facial morph targets, so we don't fake
    // morph animations. We use the actual eye assemblies for
    // subtle blink/look behavior.
    // --------------------------------------------------------

    for (
      const eye of [leftEye, rightEye]
    ) {
      if (!eye) continue;

      const base =
        eyeBase.get(eye);

      if (!base) continue;

      eye.position.copy(
        base.position,
      );

      eye.rotation.copy(
        base.rotation,
      );

      eye.scale.copy(
        base.scale,
      );
    }

    if (
      leftEye &&
      rightEye
    ) {
      const leftBase =
        eyeBase.get(leftEye);
      const rightBase =
        eyeBase.get(rightEye);

      if (leftBase && rightBase) {
        // Occasionally choose a new natural gaze direction.
        // Thinking looks around more; idle stays restrained.
        if (t >= nextGazeChange) {
          const horizontal =
            thinking
              ? 0.028
              : listening
                ? 0.018
                : 0.010;

          const vertical =
            thinking
              ? 0.014
              : listening
                ? 0.008
                : 0.005;

          targetGazeX =
            (Math.random() * 2 - 1) *
            horizontal;
          targetGazeY =
            (Math.random() * 2 - 1) *
            vertical;

          nextGazeChange =
            t +
            (thinking
              ? 0.9 + Math.random() * 1.4
              : 1.8 + Math.random() * 2.5);
        }

        gazeX = THREE.MathUtils.lerp(
          gazeX,
          targetGazeX,
          0.055,
        );

        gazeY = THREE.MathUtils.lerp(
          gazeY,
          targetGazeY,
          0.055,
        );

        leftEye.position.copy(
          leftBase.position,
        );
        rightEye.position.copy(
          rightBase.position,
        );

        leftEye.position.x += gazeX;
        rightEye.position.x += gazeX;
        leftEye.position.y += gazeY;
        rightEye.position.y += gazeY;

        if (
          !blinkActive &&
          t >= nextBlink
        ) {
          blinkActive = true;
          blinkStart = t;
          blinkDuration = 0.18;
        }

        const blinkFactor =
          blinkActive
            ? 1 -
              Math.sin(
                THREE.MathUtils.clamp(
                  (t - blinkStart) / blinkDuration,
                  0,
                  1,
                ) *
                  Math.PI,
              ) *
                0.96
            : 1;

        leftEye.scale.copy(
          leftBase.scale,
        );
        rightEye.scale.copy(
          rightBase.scale,
        );
        leftEye.scale.y *= blinkFactor;
        rightEye.scale.y *= blinkFactor;

        if (
          blinkActive &&
          t - blinkStart >= blinkDuration
        ) {
          blinkActive = false;
          nextBlink =
            t +
            2.0 +
            Math.random() * 4.5;
        }
      }
    }

    // --------------------------------------------------------
    // Speaking
    //
    // The GLB has no mouth morph target. The jaw is therefore
    // moved only by a tiny amount so the real face remains
    // clean instead of producing a fake waveform over it.
    // --------------------------------------------------------

    if (jaw) {
      const baseX =
        jawBaseRotationX;

      if (speaking) {
        // Speech envelope: several low-frequency components create
        // changing mouth openings instead of a constant flap.
        const envelope =
          0.50 +
          0.30 * Math.sin(t * 7.1) +
          0.20 * Math.sin(t * 12.8 + 0.7);

        const openAmount =
          THREE.MathUtils.clamp(
            envelope,
            0.04,
            1.0,
          ) * 0.135;

        jaw.rotation.x =
          THREE.MathUtils.lerp(
            jaw.rotation.x,
            baseX + openAmount,
            0.24,
          );
      } else {
        jaw.rotation.x =
          THREE.MathUtils.lerp(
            jaw.rotation.x,
            baseX,
            0.18,
          );
      }
    }

    // --------------------------------------------------------
    // Controlled JARVIS lighting intensity
    // --------------------------------------------------------

    rimLight.intensity =
      speaking
        ? 2.55
        : thinking
          ? 2.25
          : executing
            ? 2.35
            : listening
              ? 2.05
              : 1.75;

    bodyRimLight.intensity =
      speaking
        ? 2.05
        : thinking
          ? 1.90
          : executing
            ? 1.95
            : 1.70;

    faceSpot.intensity =
      speaking
        ? 1.75
        : thinking
          ? 1.62
          : listening
            ? 1.58
            : 1.45;

    shoulderSpot.intensity =
      speaking
        ? 2.25
        : executing
          ? 2.15
          : 1.90;

    bloom.strength =
      speaking
        ? 0.24
        : thinking
          ? 0.20
          : listening
            ? 0.18
            : 0.14;

    controls.update();
    composer.render();
  }

  let rafId = 0;
  animate();

  // ----------------------------------------------------------
  // Resize
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

    composer.setSize(
      w,
      h,
    );
  }

  window.addEventListener(
    "resize",
    onResize,
  );

  // ----------------------------------------------------------
  // Cleanup
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

        if (
          mesh.geometry
        ) {
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

    composer.dispose();
    renderer.dispose();

    if (
      renderer.domElement
        .parentElement
    ) {
      renderer.domElement.remove();
    }
  }

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
    