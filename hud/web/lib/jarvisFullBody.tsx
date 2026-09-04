// ========================================================================================================================================== //
// FULL BODY + EYES + JAW + BLINK + BROW + SMILE + VISIMES jarvis1.glb
// ========================================================================================================================================== //

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

const AMBER = new THREE.Color(0xffaa30);

const MODEL_URL = "/models/jarvis1.glb";
const HEAD_TARGET_Y = 1.62;

export function createJarvisFullBody(container: HTMLElement): OrbSceneApi {
  const width = Math.max(container.clientWidth, 1);
  const height = Math.max(container.clientHeight, 1);

  const scene = new THREE.Scene();

  const camera = new THREE.PerspectiveCamera(34, width / height, 0.1, 50);
  camera.position.set(0, 1.65, 1.45);

  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
  });

  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(width, height);
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;

  renderer.domElement.style.width = "100%";
  renderer.domElement.style.height = "100%";
  renderer.domElement.style.display = "block";

  container.appendChild(renderer.domElement);

  // Lighting
  const ambient = new THREE.AmbientLight(0xffffff, 0.95);
  scene.add(ambient);

  const keyLight = new THREE.DirectionalLight(0xffffff, 1.8);
  keyLight.position.set(0.6, 2.5, 2.5);
  scene.add(keyLight);

  const fillLight = new THREE.DirectionalLight(0xa5b8cf, 0.9);
  fillLight.position.set(-2.0, 1.8, 1.8);
  scene.add(fillLight);

  const rimLight = new THREE.PointLight(AMBER, 3.5, 5.0);
  rimLight.position.set(1.5, 2.0, -1.2);
  scene.add(rimLight);

  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));

  const bloom = new UnrealBloomPass(
    new THREE.Vector2(width, height),
    0.08,
    0.20,
    0.95
  );
  composer.addPass(bloom);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.enablePan = false;
  controls.minDistance = 0.8;
  controls.maxDistance = 4.0;
  controls.target.set(0, HEAD_TARGET_Y, 0);
  controls.update();

  const avatar = new THREE.Group();
  scene.add(avatar);

  // Categorized morph target registry
  interface MorphBinding {
    mesh: THREE.Mesh;
    index: number;
    category: "jaw" | "mouth_wide" | "mouth_round" | "blink_l" | "blink_r" | "brow" | "smile";
  }

  const morphBindings: MorphBinding[] = [];
  let leftEyeBone: THREE.Object3D | null = null;
  let rightEyeBone: THREE.Object3D | null = null;
  let headBone: THREE.Object3D | null = null;
  let neckBone: THREE.Object3D | null = null;

  let state: JarvisState = "idle";
  let isSpeaking = false;
  let disposed = false;

  const loader = new GLTFLoader();

  loader.load(
    MODEL_URL,
    (gltf) => {
      if (disposed) return;

      const model = gltf.scene;
      avatar.add(model);

      model.traverse((node) => {
        if ((node as THREE.Mesh).isMesh) {
          const mesh = node as THREE.Mesh;
          if (mesh.morphTargetDictionary && mesh.morphTargetInfluences) {
            for (const [name, index] of Object.entries(mesh.morphTargetDictionary)) {
              const lower = name.toLowerCase();

              if (
                lower === "jawopen" ||
                lower === "viseme_aa" ||
                lower === "mouthopen" ||
                lower.includes("jaw_open")
              ) {
                morphBindings.push({ mesh, index, category: "jaw" });
              } else if (
                lower.includes("stretch") ||
                lower.includes("viseme_i") ||
                lower.includes("viseme_e") ||
                lower.includes("smile")
              ) {
                morphBindings.push({ mesh, index, category: "mouth_wide" });
              } else if (
                lower.includes("funnel") ||
                lower.includes("viseme_o") ||
                lower.includes("viseme_u") ||
                lower.includes("pucker")
              ) {
                morphBindings.push({ mesh, index, category: "mouth_round" });
              } else if (lower.includes("blink") && (lower.includes("left") || lower.includes("_l") || lower.endsWith("l"))) {
                morphBindings.push({ mesh, index, category: "blink_l" });
              } else if (lower.includes("blink") && (lower.includes("right") || lower.includes("_r") || lower.endsWith("r"))) {
                morphBindings.push({ mesh, index, category: "blink_r" });
              } else if (lower.includes("brow") && lower.includes("up")) {
                morphBindings.push({ mesh, index, category: "brow" });
              }
            }
          }
        }

        const nameLower = node.name.toLowerCase();
        if (nameLower === "lefteye" || nameLower.includes("eyeball_l")) leftEyeBone = node;
        if (nameLower === "righteye" || nameLower.includes("eyeball_r")) rightEyeBone = node;
        if (nameLower === "head") headBone = node;
        if (nameLower === "neck") neckBone = node;
      });
    },
    undefined,
    (err) => console.error("[RPM AVATAR LOAD ERROR]", err)
  );

  const handleState = (event: Event) => {
    const customEvent = event as CustomEvent<{ state?: JarvisState; speaking?: boolean }>;
    if (customEvent.detail?.state) {
      state = customEvent.detail.state;
    }
    if (typeof customEvent.detail?.speaking === "boolean") {
      isSpeaking = customEvent.detail.speaking;
    } else {
      isSpeaking = state === "speaking";
    }
  };

  window.addEventListener("jarvis-assistant-state", handleState);

  function applyCategoryWeight(category: MorphBinding["category"], value: number) {
    const clamped = THREE.MathUtils.clamp(value, 0, 1);
    const updatedMeshes = new Set<THREE.Mesh>();
    for (let i = 0; i < morphBindings.length; i++) {
      if (morphBindings[i].category === category) {
        morphBindings[i].mesh.morphTargetInfluences![morphBindings[i].index] = clamped;
        updatedMeshes.add(morphBindings[i].mesh);
      }
    }
    for (const mesh of updatedMeshes) {
      if (mesh.geometry.attributes.position) {
        mesh.geometry.attributes.position.needsUpdate = true;
      }
    }
  }

  const spherical = new THREE.Spherical();
  const offset = new THREE.Vector3();

  function rotateBy(deltaTheta: number, deltaPhi: number) {
    offset.copy(camera.position).sub(controls.target);
    spherical.setFromVector3(offset);
    spherical.theta -= deltaTheta;
    spherical.phi = THREE.MathUtils.clamp(
      spherical.phi - deltaPhi,
      0.15,
      Math.PI - 0.15
    );
    spherical.makeSafe();
    offset.setFromSpherical(spherical);
    camera.position.copy(controls.target).add(offset);
    camera.lookAt(controls.target);
  }

  function zoomBy(factor: number) {
    offset.copy(camera.position).sub(controls.target);
    const dist = THREE.MathUtils.clamp(offset.length() * factor, 0.8, 4.0);
    offset.setLength(dist);
    camera.position.copy(controls.target).add(offset);
  }

  function resetView() {
    camera.position.set(0, 1.65, 1.45);
    controls.target.set(0, HEAD_TARGET_Y, 0);
    camera.lookAt(controls.target);
    controls.update();
  }

  const clock = new THREE.Clock();

  let nextBlink = 2.0;
  let blinkStart = -10;
  let blinkActive = false;
  const blinkDuration = 0.14;

  let targetGazeX = 0;
  let targetGazeY = 0;
  let currentGazeX = 0;
  let currentGazeY = 0;
  let nextGazeTime = 1.0;

  let currentJaw = 0;
  let currentWide = 0;
  let currentRound = 0;

  function animate() {
    if (disposed) return;
    rafId = requestAnimationFrame(animate);

    const t = clock.getElapsedTime();
    const activeSpeech = isSpeaking || state === "speaking";
    const thinking = state === "thinking";
    const listening = state === "listening";

    if (neckBone) {
      neckBone.rotation.x = Math.sin(t * 1.2) * 0.015;
    }

    // 1. Blinking
    if (!blinkActive && t >= nextBlink) {
      blinkActive = true;
      blinkStart = t;
    }

    let blinkWeight = 0;
    if (blinkActive) {
      const progress = (t - blinkStart) / blinkDuration;
      if (progress >= 1.0) {
        blinkActive = false;
        nextBlink = t + (Math.random() < 0.2 ? 0.22 : 2.5 + Math.random() * 3.5);
      } else {
        blinkWeight = Math.sin(progress * Math.PI);
      }
    }

    applyCategoryWeight("blink_l", blinkWeight);
    applyCategoryWeight("blink_r", blinkWeight);

    // 2. Controlled Lip-Sync
    if (activeSpeech) {
      const wave1 = Math.sin(t * 12.0);
      const wave2 = Math.sin(t * 17.5 + 0.4);
      const wave3 = Math.cos(t * 8.0);

      const rawJaw = Math.max(0, 0.16 * wave1 + 0.10 * wave2 + 0.08 * wave3 + 0.10);
      const targetJaw = THREE.MathUtils.clamp(rawJaw, 0, 0.45);

      const targetWide = Math.max(0, 0.14 * Math.sin(t * 14.0 + 0.2));
      const targetRound = Math.max(0, 0.12 * Math.cos(t * 10.0));

      currentJaw = THREE.MathUtils.lerp(currentJaw, targetJaw, 0.35);
      currentWide = THREE.MathUtils.lerp(currentWide, targetWide, 0.35);
      currentRound = THREE.MathUtils.lerp(currentRound, targetRound, 0.35);

      applyCategoryWeight("jaw", currentJaw);
      applyCategoryWeight("mouth_wide", currentWide);
      applyCategoryWeight("mouth_round", currentRound);
    } else {
      currentJaw = THREE.MathUtils.lerp(currentJaw, 0, 0.25);
      currentWide = THREE.MathUtils.lerp(currentWide, 0, 0.25);
      currentRound = THREE.MathUtils.lerp(currentRound, 0, 0.25);

      applyCategoryWeight("jaw", currentJaw);
      applyCategoryWeight("mouth_wide", currentWide);
      applyCategoryWeight("mouth_round", currentRound);
    }

    // 3. Eyebrows
    if (thinking) {
      applyCategoryWeight("brow", 0.65);
    } else if (listening) {
      applyCategoryWeight("brow", 0.25);
    } else {
      applyCategoryWeight("brow", 0.04);
    }

    // 4. Eye Gaze Tracking
    if (t >= nextGazeTime) {
      if (thinking) {
        targetGazeX = THREE.MathUtils.degToRad(-12);
        targetGazeY = THREE.MathUtils.degToRad(15);
        nextGazeTime = t + 1.1 + Math.random() * 0.8;
      } else if (listening) {
        targetGazeX = (Math.random() * 2 - 1) * 0.02;
        targetGazeY = (Math.random() * 2 - 1) * 0.02;
        nextGazeTime = t + 1.5 + Math.random() * 1.5;
      } else {
        targetGazeX = (Math.random() * 2 - 1) * 0.06;
        targetGazeY = (Math.random() * 2 - 1) * 0.12;
        nextGazeTime = t + 2.0 + Math.random() * 2.0;
      }
    }

    currentGazeX = THREE.MathUtils.lerp(currentGazeX, targetGazeX, 0.08);
    currentGazeY = THREE.MathUtils.lerp(currentGazeY, targetGazeY, 0.08);

    if (leftEyeBone && rightEyeBone) {
      leftEyeBone.rotation.x = currentGazeX;
      leftEyeBone.rotation.y = currentGazeY;
      rightEyeBone.rotation.x = currentGazeX;
      rightEyeBone.rotation.y = currentGazeY;
    }

    // 5. Head Motion
    if (headBone) {
      if (activeSpeech) {
        headBone.rotation.x = THREE.MathUtils.lerp(headBone.rotation.x, Math.sin(t * 3.2) * 0.045, 0.08);
        headBone.rotation.y = THREE.MathUtils.lerp(headBone.rotation.y, Math.sin(t * 1.6) * 0.035, 0.08);
        headBone.rotation.z = THREE.MathUtils.lerp(headBone.rotation.z, Math.sin(t * 1.2) * 0.015, 0.08);
      } else if (thinking) {
        headBone.rotation.x = THREE.MathUtils.lerp(headBone.rotation.x, -0.07, 0.05);
        headBone.rotation.y = THREE.MathUtils.lerp(headBone.rotation.y, 0.12, 0.05);
        headBone.rotation.z = THREE.MathUtils.lerp(headBone.rotation.z, -0.04, 0.05);
      } else if (listening) {
        headBone.rotation.x = THREE.MathUtils.lerp(headBone.rotation.x, 0.06, 0.05);
        headBone.rotation.y = THREE.MathUtils.lerp(headBone.rotation.y, 0.015, 0.05);
        headBone.rotation.z = THREE.MathUtils.lerp(headBone.rotation.z, 0.015, 0.05);
      } else {
        headBone.rotation.x = THREE.MathUtils.lerp(headBone.rotation.x, Math.sin(t * 0.8) * 0.02, 0.05);
        headBone.rotation.y = THREE.MathUtils.lerp(headBone.rotation.y, Math.sin(t * 0.5) * 0.025, 0.05);
        headBone.rotation.z = 0;
      }
    }

    rimLight.intensity = activeSpeech ? 3.5 : thinking ? 2.8 : listening ? 2.4 : 2.0;

    controls.update();
    composer.render();
  }

  let rafId = 0;
  animate();

  function onResize() {
    const w = Math.max(container.clientWidth, 1);
    const h = Math.max(container.clientHeight, 1);

    camera.aspect = w / h;
    camera.updateProjectionMatrix();

    renderer.setSize(w, h);
    composer.setSize(w, h);
  }

  window.addEventListener("resize", onResize);

  function dispose() {
    disposed = true;
    cancelAnimationFrame(rafId);
    window.removeEventListener("resize", onResize);
    window.removeEventListener("jarvis-assistant-state", handleState);

    controls.dispose();

    scene.traverse((object) => {
      const mesh = object as THREE.Mesh;
      if (mesh.geometry) mesh.geometry.dispose();

      const materials = Array.isArray(mesh.material)
        ? mesh.material
        : mesh.material
        ? [mesh.material]
        : [];

      for (const material of materials) {
        material.dispose();
      }
    });

    composer.dispose();
    renderer.dispose();

    if (renderer.domElement.parentElement) {
      renderer.domElement.remove();
    }
  }

  return {
    rotateBy,
    zoomBy,
    zoomIn: () => zoomBy(0.7),
    zoomOut: () => zoomBy(1.4),
    resetView,
    dispose,
  };
}


// // ========================================================================================================================================== //
// // FULL BODY ( STANDING ) + EYES + JAW + BLINK + BROW + SMILE + VISIMES jarvis1.glb
// // ========================================================================================================================================== //

// import * as THREE from "three";
// import { OrbitControls } from "three/addons/controls/OrbitControls.js";
// import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
// import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
// import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
// import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";

// export interface OrbSceneApi {
//   rotateBy(deltaTheta: number, deltaPhi: number): void;
//   zoomBy(factor: number): void;
//   zoomIn(): void;
//   zoomOut(): void;
//   resetView(): void;
//   dispose(): void;
// }

// type JarvisState =
//   | "idle"
//   | "listening"
//   | "thinking"
//   | "speaking"
//   | "executing";

// const AMBER = new THREE.Color(0xffaa30);

// const MODEL_URL = "/models/jarvis1.glb";
// const HEAD_TARGET_Y = 1.55;
// const MODEL_HEIGHT = 3.10;

// export function createJarvisFullBody(container: HTMLElement): OrbSceneApi {
//   const width = Math.max(container.clientWidth, 1);
//   const height = Math.max(container.clientHeight, 1);

//   const scene = new THREE.Scene();

//   const camera = new THREE.PerspectiveCamera(34, width / height, 0.1, 50);
//   camera.position.set(0, 1.55, 5.80);

//   const renderer = new THREE.WebGLRenderer({
//     antialias: true,
//     alpha: true,
//   });

//   renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
//   renderer.setSize(width, height);
//   renderer.setClearColor(0x000000, 0);
//   renderer.outputColorSpace = THREE.SRGBColorSpace;
//   renderer.toneMapping = THREE.ACESFilmicToneMapping;
//   renderer.toneMappingExposure = 1.05;

//   renderer.domElement.style.width = "100%";
//   renderer.domElement.style.height = "100%";
//   renderer.domElement.style.display = "block";

//   container.appendChild(renderer.domElement);

//   // Lighting
//   const ambient = new THREE.AmbientLight(0xffffff, 0.95);
//   scene.add(ambient);

//   const keyLight = new THREE.DirectionalLight(0xffffff, 1.8);
//   keyLight.position.set(0.6, 2.5, 2.5);
//   scene.add(keyLight);

//   const fillLight = new THREE.DirectionalLight(0xa5b8cf, 0.9);
//   fillLight.position.set(-2.0, 1.8, 1.8);
//   scene.add(fillLight);

//   const rimLight = new THREE.PointLight(AMBER, 3.5, 5.0);
//   rimLight.position.set(1.5, 2.0, -1.2);
//   scene.add(rimLight);

//   const composer = new EffectComposer(renderer);
//   composer.addPass(new RenderPass(scene, camera));

//   const bloom = new UnrealBloomPass(
//     new THREE.Vector2(width, height),
//     0.08,
//     0.20,
//     0.95
//   );
//   composer.addPass(bloom);

//   const controls = new OrbitControls(camera, renderer.domElement);
//   controls.enableDamping = true;
//   controls.dampingFactor = 0.08;
//   controls.enablePan = false;
//   controls.minDistance = 2.20;
//   controls.maxDistance = 8.0;
//   controls.target.set(0, HEAD_TARGET_Y, 0);
//   controls.update();

//   const avatar = new THREE.Group();
//   scene.add(avatar);

//   // Categorized morph target registry
//   interface MorphBinding {
//     mesh: THREE.Mesh;
//     index: number;
//     category: "jaw" | "mouth_wide" | "mouth_round" | "blink_l" | "blink_r" | "brow" | "smile";
//   }

//   const morphBindings: MorphBinding[] = [];
//   let leftEyeBone: THREE.Object3D | null = null;
//   let rightEyeBone: THREE.Object3D | null = null;
//   let headBone: THREE.Object3D | null = null;
//   let neckBone: THREE.Object3D | null = null;

//   let state: JarvisState = "idle";
//   let isSpeaking = false;
//   let disposed = false;

//   const loader = new GLTFLoader();

//   loader.load(
//     MODEL_URL,
//     (gltf) => {
//       if (disposed) return;

//       const model = gltf.scene;
//       model.name = "JARVIS_FULL_BODY";

//       // The full-body GLB is authored at a very small scene scale.
//       // Fit it automatically so the whole body is visible in the HUD.
//       const rawBox = new THREE.Box3().setFromObject(model);
//       const rawSize = new THREE.Vector3();
//       rawBox.getSize(rawSize);

//       if (rawSize.y > 0) {
//         model.scale.setScalar(MODEL_HEIGHT / rawSize.y);
//       }

//       const fittedBox = new THREE.Box3().setFromObject(model);
//       const center = new THREE.Vector3();
//       fittedBox.getCenter(center);

//       model.position.x -= center.x;
//       model.position.y -= center.y;
//       model.position.z -= center.z;
//       model.position.y += HEAD_TARGET_Y;

//       avatar.add(model);

//       model.traverse((node) => {
//         if ((node as THREE.Mesh).isMesh) {
//           const mesh = node as THREE.Mesh;
//           if (mesh.morphTargetDictionary && mesh.morphTargetInfluences) {
//             for (const [name, index] of Object.entries(mesh.morphTargetDictionary)) {
//               const lower = name.toLowerCase();

//               if (
//                 lower === "jawopen" ||
//                 lower === "viseme_aa" ||
//                 lower === "mouthopen" ||
//                 lower.includes("jaw_open")
//               ) {
//                 morphBindings.push({ mesh, index, category: "jaw" });
//               } else if (
//                 lower.includes("stretch") ||
//                 lower.includes("viseme_i") ||
//                 lower.includes("viseme_e") ||
//                 lower.includes("smile")
//               ) {
//                 morphBindings.push({ mesh, index, category: "mouth_wide" });
//               } else if (
//                 lower.includes("funnel") ||
//                 lower.includes("viseme_o") ||
//                 lower.includes("viseme_u") ||
//                 lower.includes("pucker")
//               ) {
//                 morphBindings.push({ mesh, index, category: "mouth_round" });
//               } else if (lower.includes("blink") && (lower.includes("left") || lower.includes("_l") || lower.endsWith("l"))) {
//                 morphBindings.push({ mesh, index, category: "blink_l" });
//               } else if (lower.includes("blink") && (lower.includes("right") || lower.includes("_r") || lower.endsWith("r"))) {
//                 morphBindings.push({ mesh, index, category: "blink_r" });
//               } else if (lower.includes("brow") && lower.includes("up")) {
//                 morphBindings.push({ mesh, index, category: "brow" });
//               }
//             }
//           }
//         }

//         const nameLower = node.name.toLowerCase();
//         if (nameLower === "lefteye" || nameLower.includes("eyeball_l")) leftEyeBone = node;
//         if (nameLower === "righteye" || nameLower.includes("eyeball_r")) rightEyeBone = node;
//         if (nameLower === "head") headBone = node;
//         if (nameLower === "neck") neckBone = node;
//       });
//     },
//     undefined,
//     (err) => console.error("[RPM AVATAR LOAD ERROR]", err)
//   );

//   const handleState = (event: Event) => {
//     const customEvent = event as CustomEvent<{ state?: JarvisState; speaking?: boolean }>;
//     if (customEvent.detail?.state) {
//       state = customEvent.detail.state;
//     }
//     if (typeof customEvent.detail?.speaking === "boolean") {
//       isSpeaking = customEvent.detail.speaking;
//     } else {
//       isSpeaking = state === "speaking";
//     }
//   };

//   window.addEventListener("jarvis-assistant-state", handleState);

//   function applyCategoryWeight(category: MorphBinding["category"], value: number) {
//     const clamped = THREE.MathUtils.clamp(value, 0, 1);
//     const updatedMeshes = new Set<THREE.Mesh>();
//     for (let i = 0; i < morphBindings.length; i++) {
//       if (morphBindings[i].category === category) {
//         morphBindings[i].mesh.morphTargetInfluences![morphBindings[i].index] = clamped;
//         updatedMeshes.add(morphBindings[i].mesh);
//       }
//     }
//     for (const mesh of updatedMeshes) {
//       if (mesh.geometry.attributes.position) {
//         mesh.geometry.attributes.position.needsUpdate = true;
//       }
//     }
//   }

//   const spherical = new THREE.Spherical();
//   const offset = new THREE.Vector3();

//   function rotateBy(deltaTheta: number, deltaPhi: number) {
//     offset.copy(camera.position).sub(controls.target);
//     spherical.setFromVector3(offset);
//     spherical.theta -= deltaTheta;
//     spherical.phi = THREE.MathUtils.clamp(
//       spherical.phi - deltaPhi,
//       0.15,
//       Math.PI - 0.15
//     );
//     spherical.makeSafe();
//     offset.setFromSpherical(spherical);
//     camera.position.copy(controls.target).add(offset);
//     camera.lookAt(controls.target);
//   }

//   function zoomBy(factor: number) {
//     offset.copy(camera.position).sub(controls.target);
//     const dist = THREE.MathUtils.clamp(offset.length() * factor, 2.20, 8.0);
//     offset.setLength(dist);
//     camera.position.copy(controls.target).add(offset);
//   }

//   function resetView() {
//     camera.position.set(0, 1.55, 5.80);
//     controls.target.set(0, HEAD_TARGET_Y, 0);
//     camera.lookAt(controls.target);
//     controls.update();
//   }

//   const clock = new THREE.Clock();

//   let nextBlink = 2.0;
//   let blinkStart = -10;
//   let blinkActive = false;
//   const blinkDuration = 0.14;

//   let targetGazeX = 0;
//   let targetGazeY = 0;
//   let currentGazeX = 0;
//   let currentGazeY = 0;
//   let nextGazeTime = 1.0;

//   let currentJaw = 0;
//   let currentWide = 0;
//   let currentRound = 0;

//   function animate() {
//     if (disposed) return;
//     rafId = requestAnimationFrame(animate);

//     const t = clock.getElapsedTime();
//     const activeSpeech = isSpeaking || state === "speaking";
//     const thinking = state === "thinking";
//     const listening = state === "listening";

//     if (neckBone) {
//       neckBone.rotation.x = Math.sin(t * 1.2) * 0.015;
//     }

//     // 1. Blinking
//     if (!blinkActive && t >= nextBlink) {
//       blinkActive = true;
//       blinkStart = t;
//     }

//     let blinkWeight = 0;
//     if (blinkActive) {
//       const progress = (t - blinkStart) / blinkDuration;
//       if (progress >= 1.0) {
//         blinkActive = false;
//         nextBlink = t + (Math.random() < 0.2 ? 0.22 : 2.5 + Math.random() * 3.5);
//       } else {
//         blinkWeight = Math.sin(progress * Math.PI);
//       }
//     }

//     applyCategoryWeight("blink_l", blinkWeight);
//     applyCategoryWeight("blink_r", blinkWeight);

//     // 2. Controlled Lip-Sync
//     if (activeSpeech) {
//       const wave1 = Math.sin(t * 12.0);
//       const wave2 = Math.sin(t * 17.5 + 0.4);
//       const wave3 = Math.cos(t * 8.0);

//       const rawJaw = Math.max(0, 0.16 * wave1 + 0.10 * wave2 + 0.08 * wave3 + 0.10);
//       const targetJaw = THREE.MathUtils.clamp(rawJaw, 0, 0.45);

//       const targetWide = Math.max(0, 0.14 * Math.sin(t * 14.0 + 0.2));
//       const targetRound = Math.max(0, 0.12 * Math.cos(t * 10.0));

//       currentJaw = THREE.MathUtils.lerp(currentJaw, targetJaw, 0.35);
//       currentWide = THREE.MathUtils.lerp(currentWide, targetWide, 0.35);
//       currentRound = THREE.MathUtils.lerp(currentRound, targetRound, 0.35);

//       applyCategoryWeight("jaw", currentJaw);
//       applyCategoryWeight("mouth_wide", currentWide);
//       applyCategoryWeight("mouth_round", currentRound);
//     } else {
//       currentJaw = THREE.MathUtils.lerp(currentJaw, 0, 0.25);
//       currentWide = THREE.MathUtils.lerp(currentWide, 0, 0.25);
//       currentRound = THREE.MathUtils.lerp(currentRound, 0, 0.25);

//       applyCategoryWeight("jaw", currentJaw);
//       applyCategoryWeight("mouth_wide", currentWide);
//       applyCategoryWeight("mouth_round", currentRound);
//     }

//     // 3. Eyebrows
//     if (thinking) {
//       applyCategoryWeight("brow", 0.65);
//     } else if (listening) {
//       applyCategoryWeight("brow", 0.25);
//     } else {
//       applyCategoryWeight("brow", 0.04);
//     }

//     // 4. Eye Gaze Tracking
//     if (t >= nextGazeTime) {
//       if (thinking) {
//         targetGazeX = THREE.MathUtils.degToRad(-12);
//         targetGazeY = THREE.MathUtils.degToRad(15);
//         nextGazeTime = t + 1.1 + Math.random() * 0.8;
//       } else if (listening) {
//         targetGazeX = (Math.random() * 2 - 1) * 0.02;
//         targetGazeY = (Math.random() * 2 - 1) * 0.02;
//         nextGazeTime = t + 1.5 + Math.random() * 1.5;
//       } else {
//         targetGazeX = (Math.random() * 2 - 1) * 0.06;
//         targetGazeY = (Math.random() * 2 - 1) * 0.12;
//         nextGazeTime = t + 2.0 + Math.random() * 2.0;
//       }
//     }

//     currentGazeX = THREE.MathUtils.lerp(currentGazeX, targetGazeX, 0.08);
//     currentGazeY = THREE.MathUtils.lerp(currentGazeY, targetGazeY, 0.08);

//     if (leftEyeBone && rightEyeBone) {
//       leftEyeBone.rotation.x = currentGazeX;
//       leftEyeBone.rotation.y = currentGazeY;
//       rightEyeBone.rotation.x = currentGazeX;
//       rightEyeBone.rotation.y = currentGazeY;
//     }

//     // 5. Head Motion
//     if (headBone) {
//       if (activeSpeech) {
//         headBone.rotation.x = THREE.MathUtils.lerp(headBone.rotation.x, Math.sin(t * 3.2) * 0.045, 0.08);
//         headBone.rotation.y = THREE.MathUtils.lerp(headBone.rotation.y, Math.sin(t * 1.6) * 0.035, 0.08);
//         headBone.rotation.z = THREE.MathUtils.lerp(headBone.rotation.z, Math.sin(t * 1.2) * 0.015, 0.08);
//       } else if (thinking) {
//         headBone.rotation.x = THREE.MathUtils.lerp(headBone.rotation.x, -0.07, 0.05);
//         headBone.rotation.y = THREE.MathUtils.lerp(headBone.rotation.y, 0.12, 0.05);
//         headBone.rotation.z = THREE.MathUtils.lerp(headBone.rotation.z, -0.04, 0.05);
//       } else if (listening) {
//         headBone.rotation.x = THREE.MathUtils.lerp(headBone.rotation.x, 0.06, 0.05);
//         headBone.rotation.y = THREE.MathUtils.lerp(headBone.rotation.y, 0.015, 0.05);
//         headBone.rotation.z = THREE.MathUtils.lerp(headBone.rotation.z, 0.015, 0.05);
//       } else {
//         headBone.rotation.x = THREE.MathUtils.lerp(headBone.rotation.x, Math.sin(t * 0.8) * 0.02, 0.05);
//         headBone.rotation.y = THREE.MathUtils.lerp(headBone.rotation.y, Math.sin(t * 0.5) * 0.025, 0.05);
//         headBone.rotation.z = 0;
//       }
//     }

//     rimLight.intensity = activeSpeech ? 3.5 : thinking ? 2.8 : listening ? 2.4 : 2.0;

//     controls.update();
//     composer.render();
//   }

//   let rafId = 0;
//   animate();

//   function onResize() {
//     const w = Math.max(container.clientWidth, 1);
//     const h = Math.max(container.clientHeight, 1);

//     camera.aspect = w / h;
//     camera.updateProjectionMatrix();

//     renderer.setSize(w, h);
//     composer.setSize(w, h);
//   }

//   window.addEventListener("resize", onResize);

//   function dispose() {
//     disposed = true;
//     cancelAnimationFrame(rafId);
//     window.removeEventListener("resize", onResize);
//     window.removeEventListener("jarvis-assistant-state", handleState);

//     controls.dispose();

//     scene.traverse((object) => {
//       const mesh = object as THREE.Mesh;
//       if (mesh.geometry) mesh.geometry.dispose();

//       const materials = Array.isArray(mesh.material)
//         ? mesh.material
//         : mesh.material
//         ? [mesh.material]
//         : [];

//       for (const material of materials) {
//         material.dispose();
//       }
//     });

//     composer.dispose();
//     renderer.dispose();

//     if (renderer.domElement.parentElement) {
//       renderer.domElement.remove();
//     }
//   }

//   return {
//     rotateBy,
//     zoomBy,
//     zoomIn: () => zoomBy(0.7),
//     zoomOut: () => zoomBy(1.4),
//     resetView,
//     dispose,
//   };
// }