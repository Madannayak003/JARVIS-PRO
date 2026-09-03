import * as THREE from "three";

import { OrbitControls } from "three/addons/controls/OrbitControls.js";

import {
  EffectComposer,
} from "three/addons/postprocessing/EffectComposer.js";

import {
  RenderPass,
} from "three/addons/postprocessing/RenderPass.js";

import {
  UnrealBloomPass,
} from "three/addons/postprocessing/UnrealBloomPass.js";

import {
  ShaderPass,
} from "three/addons/postprocessing/ShaderPass.js";


/* ============================================================
   PUBLIC API
   ------------------------------------------------------------
   IMPORTANT:
   JarvisOrb.tsx already depends on this API.
   DO NOT CHANGE IT.
   ============================================================ */

export interface OrbSceneApi {

  rotateBy(
    deltaTheta: number,
    deltaPhi: number,
  ): void;

  zoomBy(
    factor: number,
  ): void;

  zoomIn(): void;

  zoomOut(): void;

  resetView(): void;

  dispose(): void;
}


/* ============================================================
   CAMERA
   ============================================================ */

const HOME_POSITION =
  new THREE.Vector3(
    0,
    0.15,
    6.4,
  );

const MIN_DISTANCE = 3.0;

const MAX_DISTANCE = 14.0;


/* ============================================================
   COLORS
   ============================================================ */

const C_AMBER =
  new THREE.Color(
    0xffa51f,
  );

const C_BRIGHT =
  new THREE.Color(
    0xffd27a,
  );

const C_DIM =
  new THREE.Color(
    0x5c3b12,
  );

const C_WHITE =
  new THREE.Color(
    0xfff0c0,
  );


/* ============================================================
   HELPERS
   ============================================================ */

function lineMaterial(
  color: THREE.Color,
  opacity = 1,
) {
  return new THREE.LineBasicMaterial({
    color,
    transparent: true,
    opacity,
    blending:
      THREE.AdditiveBlending,
    depthWrite: false,
  });
}


function makeLine(
  points: THREE.Vector3[],
  material: THREE.LineBasicMaterial,
) {
  const geometry =
    new THREE.BufferGeometry();

  geometry.setFromPoints(
    points,
  );

  return new THREE.Line(
    geometry,
    material,
  );
}


function makeCircle(
  radius: number,
  material: THREE.LineBasicMaterial,
  segments = 96,
) {
  const points:
    THREE.Vector3[] = [];

  for (
    let i = 0;
    i <= segments;
    i++
  ) {
    const a =
      (i / segments) *
      Math.PI *
      2;

    points.push(
      new THREE.Vector3(
        Math.cos(a) * radius,
        Math.sin(a) * radius,
        0,
      ),
    );
  }

  return makeLine(
    points,
    material,
  );
}


/* ============================================================
   CREATE SCENE
   ============================================================ */

export function createOrbScene(
  container: HTMLElement,
): OrbSceneApi {

  const width =
    Math.max(
      container.clientWidth,
      1,
    );

  const height =
    Math.max(
      container.clientHeight,
      1,
    );


  /* ==========================================================
     SCENE
     ========================================================== */

  const scene =
    new THREE.Scene();


  /* ==========================================================
     CAMERA
     ========================================================== */

  const camera =
    new THREE.PerspectiveCamera(
      48,
      width / height,
      0.1,
      100,
    );

  camera.position.copy(
    HOME_POSITION,
  );


  /* ==========================================================
     RENDERER
     ========================================================== */

  const renderer =
    new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
    });

  renderer.setSize(
    width,
    height,
  );

  renderer.setPixelRatio(
    Math.min(
      window.devicePixelRatio,
      2,
    ),
  );

  renderer.toneMapping =
    THREE.ACESFilmicToneMapping;

  renderer.toneMappingExposure =
    1.15;

  renderer.setClearColor(
    0x000000,
    0,
  );

  renderer.domElement.style.width =
    "100%";

  renderer.domElement.style.height =
    "100%";

  renderer.domElement.style.display =
    "block";

  container.appendChild(
    renderer.domElement,
  );


  /* ==========================================================
     POST PROCESSING
     ========================================================== */

  const composer =
    new EffectComposer(
      renderer,
    );

  composer.addPass(
    new RenderPass(
      scene,
      camera,
    ),
  );


  const bloom =
    new UnrealBloomPass(
      new THREE.Vector2(
        width,
        height,
      ),
      1.65,
      0.45,
      0.08,
    );

  composer.addPass(
    bloom,
  );


  /* ==========================================================
     COLOR / FLICKER SHADER
     ========================================================== */

  const chromaticShader = {

    uniforms: {

      tDiffuse: {
        value: null,
      },

      uTime: {
        value: 0,
      },

      uIntensity: {
        value: 0.0018,
      },

    },

    vertexShader: `
      varying vec2 vUv;

      void main() {

        vUv = uv;

        gl_Position =
          projectionMatrix *
          modelViewMatrix *
          vec4(
            position,
            1.0
          );
      }
    `,

    fragmentShader: `
      uniform sampler2D tDiffuse;
      uniform float uTime;
      uniform float uIntensity;

      varying vec2 vUv;

      void main() {

        vec2 direction =
          vUv -
          vec2(
            0.5
          );

        float distanceFromCenter =
          length(
            direction
          );

        float offset =
          uIntensity *
          distanceFromCenter;

        float flicker =
          1.0 +
          0.012 *
          sin(
            uTime * 31.0
          );

        vec4 red =
          texture2D(
            tDiffuse,
            vUv +
            direction *
            offset
          );

        vec4 green =
          texture2D(
            tDiffuse,
            vUv
          );

        vec4 blue =
          texture2D(
            tDiffuse,
            vUv -
            direction *
            offset
          );

        gl_FragColor =
          vec4(
            red.r,
            green.g,
            blue.b,
            green.a
          ) *
          flicker;
      }
    `,
  };


  const chromaticPass =
    new ShaderPass(
      chromaticShader,
    );

  composer.addPass(
    chromaticPass,
  );


  /* ==========================================================
     MAIN JARVIS GROUP
     ========================================================== */

  const jarvis =
    new THREE.Group();

  scene.add(
    jarvis,
  );


  /* ==========================================================
   JARVIS FACE — STEP 4A
   ========================================================== */

  const head =
    new THREE.Group();

  jarvis.add(
    head,
  );


  /* ==========================================================
    FACE MATERIALS
    ========================================================== */

  const faceBright =
    lineMaterial(
      C_BRIGHT,
      0.96,
    );

  const faceNormal =
    lineMaterial(
      C_AMBER,
      0.72,
    );

  const faceDim =
    lineMaterial(
      C_DIM,
      0.42,
    );

  const faceWhite =
    lineMaterial(
      C_WHITE,
      0.98,
    );

  /* ==========================================================
   COMPATIBILITY MATERIAL ALIASES
   ----------------------------------------------------------
   Existing animation code uses these names.
   Keep them mapped to the new face materials.
   ========================================================== */

  const normal =
    faceNormal;

  const dim =
    faceDim;

  const bright =
    faceBright;

  const white =
    faceWhite;


  /* ==========================================================
    HEAD OUTER SILHOUETTE
    ========================================================== */

  const outerHeadPoints: THREE.Vector3[] = [
    new THREE.Vector3(
      -1.02,
      0.70,
      0,
    ),

    new THREE.Vector3(
      -0.96,
      1.02,
      0,
    ),

    new THREE.Vector3(
      -0.78,
      1.30,
      0,
    ),

    new THREE.Vector3(
      -0.48,
      1.48,
      0,
    ),

    new THREE.Vector3(
      -0.18,
      1.56,
      0,
    ),

    new THREE.Vector3(
      0,
      1.58,
      0,
    ),

    new THREE.Vector3(
      0.18,
      1.56,
      0,
    ),

    new THREE.Vector3(
      0.48,
      1.48,
      0,
    ),

    new THREE.Vector3(
      0.78,
      1.30,
      0,
    ),

    new THREE.Vector3(
      0.96,
      1.02,
      0,
    ),

    new THREE.Vector3(
      1.02,
      0.70,
      0,
    ),

    new THREE.Vector3(
      1.00,
      0.28,
      0,
    ),

    new THREE.Vector3(
      0.90,
      -0.12,
      0,
    ),

    new THREE.Vector3(
      0.76,
      -0.48,
      0,
    ),

    new THREE.Vector3(
      0.50,
      -0.70,
      0,
    ),

    new THREE.Vector3(
      0.22,
      -0.82,
      0,
    ),

    new THREE.Vector3(
      0,
      -0.86,
      0,
    ),

    new THREE.Vector3(
      -0.22,
      -0.82,
      0,
    ),

    new THREE.Vector3(
      -0.50,
      -0.70,
      0,
    ),

    new THREE.Vector3(
      -0.76,
      -0.48,
      0,
    ),

    new THREE.Vector3(
      -0.90,
      -0.12,
      0,
    ),

    new THREE.Vector3(
      -1.00,
      0.28,
      0,
    ),

    new THREE.Vector3(
      -1.02,
      0.70,
      0,
    ),
  ];

  head.add(
    makeLine(
      outerHeadPoints,
      faceBright,
    ),
  );


  /* ==========================================================
    INNER HEAD CONTOUR
    ========================================================== */

  const innerHeadPoints: THREE.Vector3[] = [
    new THREE.Vector3(
      -0.82,
      0.72,
      0.018,
    ),

    new THREE.Vector3(
      -0.74,
      1.02,
      0.018,
    ),

    new THREE.Vector3(
      -0.48,
      1.25,
      0.018,
    ),

    new THREE.Vector3(
      -0.18,
      1.37,
      0.018,
    ),

    new THREE.Vector3(
      0,
      1.40,
      0.018,
    ),

    new THREE.Vector3(
      0.18,
      1.37,
      0.018,
    ),

    new THREE.Vector3(
      0.48,
      1.25,
      0.018,
    ),

    new THREE.Vector3(
      0.74,
      1.02,
      0.018,
    ),

    new THREE.Vector3(
      0.82,
      0.72,
      0.018,
    ),

    new THREE.Vector3(
      0.82,
      0.30,
      0.018,
    ),

    new THREE.Vector3(
      0.68,
      -0.08,
      0.018,
    ),

    new THREE.Vector3(
      0.44,
      -0.42,
      0.018,
    ),

    new THREE.Vector3(
      0.20,
      -0.58,
      0.018,
    ),

    new THREE.Vector3(
      0,
      -0.63,
      0.018,
    ),

    new THREE.Vector3(
      -0.20,
      -0.58,
      0.018,
    ),

    new THREE.Vector3(
      -0.44,
      -0.42,
      0.018,
    ),

    new THREE.Vector3(
      -0.68,
      -0.08,
      0.018,
    ),

    new THREE.Vector3(
      -0.82,
      0.30,
      0.018,
    ),

    new THREE.Vector3(
      -0.82,
      0.72,
      0.018,
    ),
  ];

  head.add(
    makeLine(
      innerHeadPoints,
      faceDim,
    ),
  );


  /* ==========================================================
    FOREHEAD ARCHITECTURE
    ========================================================== */

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.55,
          1.12,
          0.035,
        ),

        new THREE.Vector3(
          -0.38,
          1.34,
          0.035,
        ),

        new THREE.Vector3(
          -0.16,
          1.46,
          0.035,
        ),

        new THREE.Vector3(
          0,
          1.50,
          0.035,
        ),

        new THREE.Vector3(
          0.16,
          1.46,
          0.035,
        ),

        new THREE.Vector3(
          0.38,
          1.34,
          0.035,
        ),

        new THREE.Vector3(
          0.55,
          1.12,
          0.035,
        ),
      ],
      faceNormal,
    ),
  );


  /* ==========================================================
    FOREHEAD VERTICAL DATA LINES
    ========================================================== */

  for (
    let i = -4;
    i <= 4;
    i++
  ) {
    const x =
      i * 0.105;

    const top =
      1.04 -
      Math.abs(i) *
        0.015;

    head.add(
      makeLine(
        [
          new THREE.Vector3(
            x,
            top,
            0.028,
          ),

          new THREE.Vector3(
            x * 0.72,
            0.78,
            0.028,
          ),
        ],
        faceDim,
      ),
    );
  }


  /* ==========================================================
    TEMPLE STRUCTURE
    ========================================================== */

  for (
    const side of [-1, 1]
  ) {
    const sx =
      side;

    head.add(
      makeLine(
        [
          new THREE.Vector3(
            sx * 0.78,
            0.98,
            0.035,
          ),

          new THREE.Vector3(
            sx * 0.94,
            0.76,
            0.035,
          ),

          new THREE.Vector3(
            sx * 0.96,
            0.45,
            0.035,
          ),

          new THREE.Vector3(
            sx * 0.84,
            0.25,
            0.035,
          ),
        ],
        faceNormal,
      ),
    );
  }


  /* ==========================================================
    CHEEKBONE STRUCTURE
    ========================================================== */

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.80,
          0.18,
          0.04,
        ),

        new THREE.Vector3(
          -0.58,
          0.02,
          0.04,
        ),

        new THREE.Vector3(
          -0.30,
          -0.06,
          0.04,
        ),
      ],
      faceDim,
    ),
  );

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          0.80,
          0.18,
          0.04,
        ),

        new THREE.Vector3(
          0.58,
          0.02,
          0.04,
        ),

        new THREE.Vector3(
          0.30,
          -0.06,
          0.04,
        ),
      ],
      faceDim,
    ),
  );


  /* ==========================================================
    JAW ARCHITECTURE
    ========================================================== */

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.84,
          -0.05,
          0.035,
        ),

        new THREE.Vector3(
          -0.72,
          -0.34,
          0.035,
        ),

        new THREE.Vector3(
          -0.48,
          -0.58,
          0.035,
        ),

        new THREE.Vector3(
          -0.20,
          -0.72,
          0.035,
        ),

        new THREE.Vector3(
          0,
          -0.76,
          0.035,
        ),

        new THREE.Vector3(
          0.20,
          -0.72,
          0.035,
        ),

        new THREE.Vector3(
          0.48,
          -0.58,
          0.035,
        ),

        new THREE.Vector3(
          0.72,
          -0.34,
          0.035,
        ),

        new THREE.Vector3(
          0.84,
          -0.05,
          0.035,
        ),
      ],
      faceNormal,
    ),
  );


  /* ==========================================================
    CHIN PLATE
    ========================================================== */

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.30,
          -0.56,
          0.055,
        ),

        new THREE.Vector3(
          -0.18,
          -0.68,
          0.055,
        ),

        new THREE.Vector3(
          0,
          -0.72,
          0.055,
        ),

        new THREE.Vector3(
          0.18,
          -0.68,
          0.055,
        ),

        new THREE.Vector3(
          0.30,
          -0.56,
          0.055,
        ),
      ],
      faceBright,
    ),
  );


  /* ==========================================================
    SIDE EAR / TEMPORAL MODULES
    ========================================================== */

  for (
    const side of [-1, 1]
  ) {
    const x =
      side * 1.04;

    const ear =
      new THREE.Group();

    ear.position.x =
      x;

    ear.position.y =
      0.45;

    ear.position.z =
      0.02;

    head.add(
      ear,
    );

    ear.add(
      makeLine(
        [
          new THREE.Vector3(
            0,
            0.22,
            0,
          ),

          new THREE.Vector3(
            side * 0.10,
            0.12,
            0,
          ),

          new THREE.Vector3(
            side * 0.10,
            -0.14,
            0,
          ),

          new THREE.Vector3(
            0,
            -0.24,
            0,
          ),
        ],
        faceNormal,
      ),
    );

    ear.add(
      makeLine(
        [
          new THREE.Vector3(
            0,
            0.08,
            0.02,
          ),

          new THREE.Vector3(
            side * 0.06,
            0,
            0.02,
          ),

          new THREE.Vector3(
            0,
            -0.08,
            0.02,
          ),
        ],
        faceDim,
      ),
    );
  }


  /* ==========================================================
    FACE CENTER AXIS
    ========================================================== */

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          0,
          0.92,
          0.045,
        ),

        new THREE.Vector3(
          0,
          0.52,
          0.045,
        ),

        new THREE.Vector3(
          0,
          0.10,
          0.045,
        ),

        new THREE.Vector3(
          0,
          -0.14,
          0.045,
        ),
      ],
      faceDim,
    ),
  );


  /* ==========================================================
    FOREHEAD JARVIS CORE
    ========================================================== */

  const foreheadCore =
    makeCircle(
      0.205,
      faceBright,
      64,
    );

  foreheadCore.position.set(
    0,
    1.12,
    0.075,
  );

  head.add(
    foreheadCore,
  );


  const foreheadCoreInner =
    makeCircle(
      0.065,
      faceWhite,
      40,
    );

  foreheadCoreInner.position.set(
    0,
    1.12,
    0.09,
  );

  head.add(
    foreheadCoreInner,
  );


  /* ==========================================================
    FOREHEAD CORE RADIAL DATA
    ========================================================== */

  for (
    let i = 0;
    i < 12;
    i++
  ) {
    const angle =
      (i / 12) *
      Math.PI *
      2;

    const inner =
      0.24;

    const outer =
      0.34;

    head.add(
      makeLine(
        [
          new THREE.Vector3(
            Math.cos(angle) *
              inner,
            1.12 +
              Math.sin(angle) *
                inner,
            0.055,
          ),

          new THREE.Vector3(
            Math.cos(angle) *
              outer,
            1.12 +
              Math.sin(angle) *
                outer,
            0.055,
          ),
        ],
        faceNormal,
      ),
    );
  }


  /* ==========================================================
    SUBTLE FACE GRID
    ========================================================== */

  for (
    let i = -4;
    i <= 4;
    i++
  ) {
    const y =
      i * 0.20;

    const halfWidth =
      Math.max(
        0.18,
        0.88 -
          Math.abs(i) *
            0.10,
      );

    head.add(
      makeLine(
        [
          new THREE.Vector3(
            -halfWidth,
            y,
            -0.015,
          ),

          new THREE.Vector3(
            halfWidth,
            y,
            -0.015,
          ),
        ],
        faceDim,
      ),
    );
  }


  /* ==========================================================
    FACIAL DATA NODES
    ========================================================== */

  const faceNodes:
    THREE.Mesh[] = [];

  for (
    let i = 0;
    i < 16;
    i++
  ) {
    const angle =
      (i / 16) *
      Math.PI *
      2;

    const radius =
      0.78;

    const geometry =
      new THREE.OctahedronGeometry(
        0.018,
        0,
      );

    const material =
      new THREE.MeshBasicMaterial({
        color:
          i % 4 === 0
            ? C_BRIGHT
            : C_AMBER,

        transparent:
          true,

        opacity:
          0.70,

        blending:
          THREE.AdditiveBlending,

        depthWrite:
          false,
      });

    const node =
      new THREE.Mesh(
        geometry,
        material,
      );

    node.position.set(
      Math.cos(angle) *
        radius,

      Math.sin(angle) *
        radius *
        0.85,

      0.08,
    );

    head.add(
      node,
    );

    faceNodes.push(
      node,
    );
  }

    /* ==========================================================
     EYES
     ----------------------------------------------------------
     These objects are intentionally kept as named groups
     because the existing blink / eye-look animation uses them.
     ========================================================== */

  const leftEye =
    new THREE.Group();

  const rightEye =
    new THREE.Group();


  leftEye.position.set(
    -0.49,
    0.49,
    0.10,
  );

  rightEye.position.set(
    0.49,
    0.49,
    0.10,
  );


  head.add(
    leftEye,
  );

  head.add(
    rightEye,
  );


  /* ==========================================================
     EYE SHAPES
     ========================================================== */

  const eyeShapeLeft =
    makeLine(
      [
        new THREE.Vector3(
          -0.34,
          0,
          0,
        ),

        new THREE.Vector3(
          -0.20,
          0.095,
          0,
        ),

        new THREE.Vector3(
          0,
          0.115,
          0,
        ),

        new THREE.Vector3(
          0.20,
          0.095,
          0,
        ),

        new THREE.Vector3(
          0.34,
          0,
          0,
        ),

        new THREE.Vector3(
          0.20,
          -0.075,
          0,
        ),

        new THREE.Vector3(
          0,
          -0.09,
          0,
        ),

        new THREE.Vector3(
          -0.20,
          -0.075,
          0,
        ),

        new THREE.Vector3(
          -0.34,
          0,
          0,
        ),
      ],
      faceBright,
    );


  const eyeShapeRight =
    eyeShapeLeft.clone();


  leftEye.add(
    eyeShapeLeft,
  );

  rightEye.add(
    eyeShapeRight,
  );


  /* ==========================================================
     EYE CORES
     ========================================================== */

  const leftEyeCore =
    makeCircle(
      0.070,
      faceWhite,
      40,
    );

  const rightEyeCore =
    makeCircle(
      0.070,
      faceWhite,
      40,
    );


  leftEyeCore.position.set(
    0,
    0,
    0.025,
  );

  rightEyeCore.position.set(
    0,
    0,
    0.025,
  );


  leftEye.add(
    leftEyeCore,
  );

  rightEye.add(
    rightEyeCore,
  );


  /* ==========================================================
     EYE INNER CORES
     ========================================================== */

  const leftEyeDot =
    makeCircle(
      0.022,
      faceBright,
      24,
    );

  const rightEyeDot =
    makeCircle(
      0.022,
      faceBright,
      24,
    );


  leftEyeDot.position.z =
    0.045;

  rightEyeDot.position.z =
    0.045;


  leftEye.add(
    leftEyeDot,
  );

  rightEye.add(
    rightEyeDot,
  );


  /* ==========================================================
     EYEBROW / UPPER FACIAL ARCH
     ========================================================== */

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.82,
          0.67,
          0.075,
        ),

        new THREE.Vector3(
          -0.63,
          0.76,
          0.075,
        ),

        new THREE.Vector3(
          -0.42,
          0.72,
          0.075,
        ),
      ],
      faceNormal,
    ),
  );


  head.add(
    makeLine(
      [
        new THREE.Vector3(
          0.42,
          0.72,
          0.075,
        ),

        new THREE.Vector3(
          0.63,
          0.76,
          0.075,
        ),

        new THREE.Vector3(
          0.82,
          0.67,
          0.075,
        ),
      ],
      faceNormal,
    ),
  );


  /* ==========================================================
     NOSE STRUCTURE
     ========================================================== */

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.10,
          0.40,
          0.07,
        ),

        new THREE.Vector3(
          -0.075,
          0.20,
          0.07,
        ),

        new THREE.Vector3(
          -0.14,
          0.04,
          0.07,
        ),

        new THREE.Vector3(
          0,
          -0.015,
          0.07,
        ),

        new THREE.Vector3(
          0.14,
          0.04,
          0.07,
        ),

        new THREE.Vector3(
          0.075,
          0.20,
          0.07,
        ),

        new THREE.Vector3(
          0.10,
          0.40,
          0.07,
        ),
      ],
      faceDim,
    ),
  );


  /* ==========================================================
     MOUTH
     ========================================================== */

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.36,
          -0.25,
          0.075,
        ),

        new THREE.Vector3(
          -0.18,
          -0.20,
          0.075,
        ),

        new THREE.Vector3(
          0,
          -0.22,
          0.075,
        ),

        new THREE.Vector3(
          0.18,
          -0.20,
          0.075,
        ),

        new THREE.Vector3(
          0.36,
          -0.25,
          0.075,
        ),
      ],
      faceNormal,
    ),
  );


  head.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.30,
          -0.33,
          0.075,
        ),

        new THREE.Vector3(
          -0.16,
          -0.38,
          0.075,
        ),

        new THREE.Vector3(
          0,
          -0.40,
          0.075,
        ),

        new THREE.Vector3(
          0.16,
          -0.38,
          0.075,
        ),

        new THREE.Vector3(
          0.30,
          -0.33,
          0.075,
        ),
      ],
      faceDim,
    ),
  );


  /* ==========================================================
     SPEECH WAVEFORM
     ----------------------------------------------------------
     Existing speaking animation controls these bars.
     ========================================================== */

  const mouthBars:
    THREE.Line[] = [];


  const mouthBarCount =
    13;

  const mouthSpacing =
    0.045;

  const mouthCenter =
    (
      mouthBarCount - 1
    ) / 2;


  for (
    let i = 0;
    i < mouthBarCount;
    i++
  ) {

    const x =
      (
        i -
        mouthCenter
      ) *
      mouthSpacing;


    const bar =
      makeLine(
        [
          new THREE.Vector3(
            x,
            -0.29,
            0.095,
          ),

          new THREE.Vector3(
            x,
            -0.29 +
              0.075,
            0.095,
          ),
        ],
        faceWhite,
      );


    bar.scale.y =
      0.35;


    head.add(
      bar,
    );

    mouthBars.push(
      bar,
    );
  }


  let speechPulse =
    0;

    /* ==========================================================
     JARVIS FACIAL ARCHITECTURE — STEP 4B
     ----------------------------------------------------------
     This fills the interior of the holographic face.
     ========================================================== */


  /* ==========================================================
     FOREHEAD INNER PANELS
     ========================================================== */

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.62,
          0.96,
          0.065,
        ),
        new THREE.Vector3(
          -0.44,
          1.12,
          0.065,
        ),
        new THREE.Vector3(
          -0.22,
          1.20,
          0.065,
        ),
      ],
      faceDim,
    ),
  );

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          0.62,
          0.96,
          0.065,
        ),
        new THREE.Vector3(
          0.44,
          1.12,
          0.065,
        ),
        new THREE.Vector3(
          0.22,
          1.20,
          0.065,
        ),
      ],
      faceDim,
    ),
  );


  /* ==========================================================
     FOREHEAD SIDE CIRCUITS
     ========================================================== */

  for (
    const side of [-1, 1]
  ) {

    const s =
      side;

    for (
      let i = 0;
      i < 3;
      i++
    ) {

      const y =
        0.82 -
        i * 0.15;

      head.add(
        makeLine(
          [
            new THREE.Vector3(
              s * (
                0.56 +
                i * 0.08
              ),
              y,
              0.055,
            ),

            new THREE.Vector3(
              s * (
                0.72 +
                i * 0.045
              ),
              y - 0.035,
              0.055,
            ),

            new THREE.Vector3(
              s * (
                0.78 +
                i * 0.035
              ),
              y - 0.11,
              0.055,
            ),
          ],
          faceDim,
        ),
      );
    }
  }


  /* ==========================================================
     EYEBROW INNER ARCHES
     ========================================================== */

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.82,
          0.63,
          0.085,
        ),
        new THREE.Vector3(
          -0.67,
          0.72,
          0.085,
        ),
        new THREE.Vector3(
          -0.49,
          0.75,
          0.085,
        ),
        new THREE.Vector3(
          -0.34,
          0.68,
          0.085,
        ),
      ],
      faceBright,
    ),
  );

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          0.34,
          0.68,
          0.085,
        ),
        new THREE.Vector3(
          0.49,
          0.75,
          0.085,
        ),
        new THREE.Vector3(
          0.67,
          0.72,
          0.085,
        ),
        new THREE.Vector3(
          0.82,
          0.63,
          0.085,
        ),
      ],
      faceBright,
    ),
  );


  /* ==========================================================
     LOWER EYE SOCKETS
     ========================================================== */

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.80,
          0.46,
          0.075,
        ),
        new THREE.Vector3(
          -0.63,
          0.40,
          0.075,
        ),
        new THREE.Vector3(
          -0.48,
          0.39,
          0.075,
        ),
        new THREE.Vector3(
          -0.34,
          0.45,
          0.075,
        ),
      ],
      faceDim,
    ),
  );

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          0.34,
          0.45,
          0.075,
        ),
        new THREE.Vector3(
          0.48,
          0.39,
          0.075,
        ),
        new THREE.Vector3(
          0.63,
          0.40,
          0.075,
        ),
        new THREE.Vector3(
          0.80,
          0.46,
          0.075,
        ),
      ],
      faceDim,
    ),
  );


  /* ==========================================================
     EYE INNER DATA RINGS
     ========================================================== */

  const leftEyeRing =
    makeCircle(
      0.115,
      faceDim,
      48,
    );

  leftEyeRing.position.set(
    -0.49,
    0.49,
    0.065,
  );

  leftEyeRing.scale.y =
    0.62;

  head.add(
    leftEyeRing,
  );


  const rightEyeRing =
    makeCircle(
      0.115,
      faceDim,
      48,
    );

  rightEyeRing.position.set(
    0.49,
    0.49,
    0.065,
  );

  rightEyeRing.scale.y =
    0.62;

  head.add(
    rightEyeRing,
  );


  /* ==========================================================
     NOSE BRIDGE
     ========================================================== */

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.07,
          0.46,
          0.09,
        ),
        new THREE.Vector3(
          -0.055,
          0.31,
          0.09,
        ),
        new THREE.Vector3(
          -0.08,
          0.17,
          0.09,
        ),
        new THREE.Vector3(
          -0.15,
          0.04,
          0.09,
        ),
      ],
      faceBright,
    ),
  );

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          0.07,
          0.46,
          0.09,
        ),
        new THREE.Vector3(
          0.055,
          0.31,
          0.09,
        ),
        new THREE.Vector3(
          0.08,
          0.17,
          0.09,
        ),
        new THREE.Vector3(
          0.15,
          0.04,
          0.09,
        ),
      ],
      faceBright,
    ),
  );


  /* ==========================================================
     NOSE TIP
     ========================================================== */

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.15,
          0.04,
          0.095,
        ),
        new THREE.Vector3(
          -0.08,
          -0.015,
          0.095,
        ),
        new THREE.Vector3(
          0,
          -0.025,
          0.095,
        ),
        new THREE.Vector3(
          0.08,
          -0.015,
          0.095,
        ),
        new THREE.Vector3(
          0.15,
          0.04,
          0.095,
        ),
      ],
      faceBright,
    ),
  );


  /* ==========================================================
     NOSE DATA LINES
     ========================================================== */

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.20,
          0.14,
          0.065,
        ),
        new THREE.Vector3(
          -0.27,
          0.08,
          0.065,
        ),
        new THREE.Vector3(
          -0.30,
          0.01,
          0.065,
        ),
      ],
      faceDim,
    ),
  );

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          0.20,
          0.14,
          0.065,
        ),
        new THREE.Vector3(
          0.27,
          0.08,
          0.065,
        ),
        new THREE.Vector3(
          0.30,
          0.01,
          0.065,
        ),
      ],
      faceDim,
    ),
  );


  /* ==========================================================
     CHEEK PLANES
     ========================================================== */

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.82,
          0.22,
          0.06,
        ),
        new THREE.Vector3(
          -0.70,
          0.13,
          0.06,
        ),
        new THREE.Vector3(
          -0.55,
          0.08,
          0.06,
        ),
        new THREE.Vector3(
          -0.38,
          0.04,
          0.06,
        ),
      ],
      faceNormal,
    ),
  );

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          0.82,
          0.22,
          0.06,
        ),
        new THREE.Vector3(
          0.70,
          0.13,
          0.06,
        ),
        new THREE.Vector3(
          0.55,
          0.08,
          0.06,
        ),
        new THREE.Vector3(
          0.38,
          0.04,
          0.06,
        ),
      ],
      faceNormal,
    ),
  );


  /* ==========================================================
     LOWER CHEEK DATA
     ========================================================== */

  for (
    const side of [-1, 1]
  ) {

    const s =
      side;

    for (
      let i = 0;
      i < 3;
      i++
    ) {

      const startX =
        s * (
          0.38 +
          i * 0.08
        );

      const startY =
        -0.05 -
        i * 0.08;

      head.add(
        makeLine(
          [
            new THREE.Vector3(
              startX,
              startY,
              0.055,
            ),

            new THREE.Vector3(
              s * (
                0.56 +
                i * 0.07
              ),
              startY - 0.06,
              0.055,
            ),

            new THREE.Vector3(
              s * (
                0.68 +
                i * 0.05
              ),
              startY - 0.16,
              0.055,
            ),
          ],
          faceDim,
        ),
      );
    }
  }


  /* ==========================================================
     MOUTH OUTER ARCHITECTURE
     ========================================================== */

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.42,
          -0.25,
          0.10,
        ),
        new THREE.Vector3(
          -0.30,
          -0.18,
          0.10,
        ),
        new THREE.Vector3(
          -0.14,
          -0.15,
          0.10,
        ),
        new THREE.Vector3(
          0,
          -0.17,
          0.10,
        ),
        new THREE.Vector3(
          0.14,
          -0.15,
          0.10,
        ),
        new THREE.Vector3(
          0.30,
          -0.18,
          0.10,
        ),
        new THREE.Vector3(
          0.42,
          -0.25,
          0.10,
        ),
      ],
      faceBright,
    ),
  );


  /* ==========================================================
     LOWER MOUTH ARCH
     ========================================================== */

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.36,
          -0.36,
          0.10,
        ),
        new THREE.Vector3(
          -0.22,
          -0.43,
          0.10,
        ),
        new THREE.Vector3(
          0,
          -0.46,
          0.10,
        ),
        new THREE.Vector3(
          0.22,
          -0.43,
          0.10,
        ),
        new THREE.Vector3(
          0.36,
          -0.36,
          0.10,
        ),
      ],
      faceNormal,
    ),
  );


  /* ==========================================================
     MOUTH CORNER CIRCUITS
     ========================================================== */

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.42,
          -0.25,
          0.075,
        ),
        new THREE.Vector3(
          -0.52,
          -0.30,
          0.075,
        ),
        new THREE.Vector3(
          -0.58,
          -0.40,
          0.075,
        ),
      ],
      faceDim,
    ),
  );

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          0.42,
          -0.25,
          0.075,
        ),
        new THREE.Vector3(
          0.52,
          -0.30,
          0.075,
        ),
        new THREE.Vector3(
          0.58,
          -0.40,
          0.075,
        ),
      ],
      faceDim,
    ),
  );


  /* ==========================================================
     CHIN DATA ARCHITECTURE
     ========================================================== */

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.46,
          -0.47,
          0.065,
        ),
        new THREE.Vector3(
          -0.32,
          -0.54,
          0.065,
        ),
        new THREE.Vector3(
          -0.16,
          -0.58,
          0.065,
        ),
        new THREE.Vector3(
          0,
          -0.60,
          0.065,
        ),
      ],
      faceDim,
    ),
  );

  head.add(
    makeLine(
      [
        new THREE.Vector3(
          0,
          -0.60,
          0.065,
        ),
        new THREE.Vector3(
          0.16,
          -0.58,
          0.065,
        ),
        new THREE.Vector3(
          0.32,
          -0.54,
          0.065,
        ),
        new THREE.Vector3(
          0.46,
          -0.47,
          0.065,
        ),
      ],
      faceDim,
    ),
  );


  /* ==========================================================
     VERTICAL FACIAL SCAN LINES
     ========================================================== */

  for (
    let i = -3;
    i <= 3;
    i++
  ) {

    const x =
      i * 0.13;

    head.add(
      makeLine(
        [
          new THREE.Vector3(
            x,
            0.28,
            -0.005,
          ),

          new THREE.Vector3(
            x * 0.82,
            -0.48,
            -0.005,
          ),
        ],
        lineMaterial(
          C_DIM,
          0.20,
        ),
      ),
    );
  }


  /* ==========================================================
     FACIAL CIRCUIT NODES
     ========================================================== */

  const circuitPoints = [
    [-0.72, 0.55],
    [-0.76, 0.22],
    [-0.68, -0.08],
    [-0.58, -0.35],
    [-0.38, -0.50],

    [0.72, 0.55],
    [0.76, 0.22],
    [0.68, -0.08],
    [0.58, -0.35],
    [0.38, -0.50],

    [-0.30, 0.88],
    [0.30, 0.88],
  ];


  for (
    let i = 0;
    i < circuitPoints.length;
    i++
  ) {

    const [
      x,
      y,
    ] =
      circuitPoints[i];


    const node =
      new THREE.Mesh(
        new THREE.OctahedronGeometry(
          0.014,
          0,
        ),

        new THREE.MeshBasicMaterial({
          color:
            i % 3 === 0
              ? C_BRIGHT
              : C_AMBER,

          transparent:
            true,

          opacity:
            0.65,

          blending:
            THREE.AdditiveBlending,

          depthWrite:
            false,
        }),
      );


    node.position.set(
      x,
      y,
      0.105,
    );


    head.add(
      node,
    );
  }


  /* ==========================================================
     NECK
     ========================================================== */

  const neck =
    new THREE.Group();

  neck.position.y =
    -1.02;

  jarvis.add(
    neck,
  );


  neck.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.48,
          0,
          0,
        ),

        new THREE.Vector3(
          -0.38,
          -0.55,
          0,
        ),

        new THREE.Vector3(
          -0.18,
          -0.72,
          0,
        ),

        new THREE.Vector3(
          0,
          -0.76,
          0,
        ),

        new THREE.Vector3(
          0.18,
          -0.72,
          0,
        ),

        new THREE.Vector3(
          0.38,
          -0.55,
          0,
        ),

        new THREE.Vector3(
          0.48,
          0,
          0,
        ),
      ],
      normal,
    ),
  );


  /* ==========================================================
     NECK DATA
     ========================================================== */

  for (
    let i = 0;
    i < 7;
    i++
  ) {

    const x =
      -0.30 +
      i * 0.10;

    neck.add(
      makeLine(
        [
          new THREE.Vector3(
            x,
            -0.10,
            0.02,
          ),

          new THREE.Vector3(
            x,
            -0.58,
            0.02,
          ),
        ],
        dim,
      ),
    );
  }


  /* ==========================================================
     CHEST CORE
     ========================================================== */

  const chest =
    new THREE.Group();

  chest.position.y =
    -1.75;

  jarvis.add(
    chest,
  );


  const chestRing =
    makeCircle(
      0.42,
      normal,
      72,
    );

  chest.add(
    chestRing,
  );


  const chestRing2 =
    makeCircle(
      0.24,
      bright,
      72,
    );

  chest.add(
    chestRing2,
  );


  const chestCore =
    makeCircle(
      0.09,
      white,
      32,
    );

  chest.add(
    chestCore,
  );


  /* ==========================================================
     CHEST FRAME
     ========================================================== */

  chest.add(
    makeLine(
      [
        new THREE.Vector3(
          -0.42,
          0,
          0,
        ),

        new THREE.Vector3(
          -0.80,
          -0.42,
          0,
        ),

        new THREE.Vector3(
          -1.0,
          -0.80,
          0,
        ),
      ],
      dim,
    ),
  );

  chest.add(
    makeLine(
      [
        new THREE.Vector3(
          0.42,
          0,
          0,
        ),

        new THREE.Vector3(
          0.80,
          -0.42,
          0,
        ),

        new THREE.Vector3(
          1.0,
          -0.80,
          0,
        ),
      ],
      dim,
    ),
  );


  /* ==========================================================
     HOLOGRAPHIC ORBIT RINGS
     ========================================================== */

 const orbitGroup =
  new THREE.Group();

  /*
  * Keep the large holographic rings
  * behind the JARVIS face.
  */
  orbitGroup.position.z = -0.65;

  jarvis.add(
    orbitGroup,
  );


  const orbit1 =
    makeCircle(
      2.25,
      dim,
      120,
    );

  orbit1.rotation.x =
    Math.PI / 2;

  orbit1.rotation.z =
    0.35;

  orbitGroup.add(
    orbit1,
  );


  const orbit2 =
    makeCircle(
      2.55,
      dim,
      120,
    );

  orbit2.rotation.y =
    Math.PI / 2;

  orbit2.rotation.z =
    -0.30;

  orbitGroup.add(
    orbit2,
  );


  const orbit3 =
    makeCircle(
      2.05,
      normal,
      120,
    );

  orbit3.rotation.x =
    Math.PI / 2;

  orbit3.rotation.z =
    -0.8;

  orbitGroup.add(
    orbit3,
  );


  /* ==========================================================
     ORBIT NODES
     ========================================================== */

  const orbitNodes:
    THREE.Mesh[] = [];

  for (
    let i = 0;
    i < 18;
    i++
  ) {

    const geometry =
      new THREE.OctahedronGeometry(
        0.045,
        0,
      );

    const material =
      new THREE.MeshBasicMaterial({
        color:
          i % 3 === 0
            ? C_BRIGHT
            : C_AMBER,

        transparent: true,

        opacity: 0.75,

        blending:
          THREE.AdditiveBlending,

        depthWrite: false,
      });

    const node =
      new THREE.Mesh(
        geometry,
        material,
      );

    const angle =
      (i / 18) *
      Math.PI *
      2;

    node.position.set(
      Math.cos(angle) *
        2.3,

      Math.sin(angle * 1.7) *
        0.8,

      Math.sin(angle) *
        1.4,
    );

    orbitGroup.add(
      node,
    );

    orbitNodes.push(
      node,
    );
  }


  /* ==========================================================
     PARTICLE FIELD
     ========================================================== */

  const particleCount =
    360;

  const particlePositions =
    new Float32Array(
      particleCount * 3,
    );

  for (
    let i = 0;
    i < particleCount;
    i++
  ) {

    const radius =
      2.2 +
      Math.random() *
      3.2;

    const theta =
      Math.random() *
      Math.PI *
      2;

    const phi =
      Math.acos(
        2 *
          Math.random() -
          1,
      );

    particlePositions[
      i * 3
    ] =
      radius *
      Math.sin(phi) *
      Math.cos(theta);

    particlePositions[
      i * 3 + 1
    ] =
      radius *
      Math.cos(phi);

    particlePositions[
      i * 3 + 2
    ] =
      radius *
      Math.sin(phi) *
      Math.sin(theta);
  }


  const particleGeometry =
    new THREE.BufferGeometry();

  particleGeometry.setAttribute(
    "position",
    new THREE.BufferAttribute(
      particlePositions,
      3,
    ),
  );


  const particleMaterial =
    new THREE.PointsMaterial({
      color:
        C_AMBER,

      size:
        0.025,

      transparent:
        true,

      opacity:
        0.48,

      blending:
        THREE.AdditiveBlending,

      depthWrite:
        false,
    });


  const particles =
    new THREE.Points(
      particleGeometry,
      particleMaterial,
    );

    /*
    * Particle field is atmospheric,
    * not drawn over the face.
    */
    particles.renderOrder = -5;

    scene.add(
      particles,
    );


  /* ==========================================================
     SCAN RINGS
     ========================================================== */

  const scanGroup =
  new THREE.Group();

  /*
  * Scan geometry stays behind
  * the main JARVIS character.
  */
  scanGroup.position.z = -0.55;

  jarvis.add(
    scanGroup,
  );


  const scanRings:
    THREE.Line[] = [];

  for (
    let i = 0;
    i < 5;
    i++
  ) {

    const ring =
      makeCircle(
        1.25 +
          i * 0.32,

        lineMaterial(
          i === 0
            ? C_BRIGHT
            : C_DIM,

          i === 0
            ? 0.35
            : 0.18,
        ),

        120,
      );

    ring.rotation.x =
      Math.PI / 2;

    ring.position.y =
      -1.0 +
      i * 0.20;

    scanGroup.add(
      ring,
    );

    scanRings.push(
      ring,
    );
  }


  /* ==========================================================
     DATA SPIKES
     ========================================================== */

  const dataSpikes:
    THREE.Line[] = [];

  for (
    let i = 0;
    i < 32;
    i++
  ) {

    const angle =
      (i / 32) *
      Math.PI *
      2;

    const radius =
      2.65;

    const length =
      0.05 +
      Math.random() *
      0.25;

    const spike =
      makeLine(
        [
          new THREE.Vector3(
            Math.cos(angle) *
              radius,

            Math.sin(angle) *
              radius,

            0,
          ),

          new THREE.Vector3(
            Math.cos(angle) *
              (radius + length),

            Math.sin(angle) *
              (radius + length),

            0,
          ),
        ],
        dim,
      );

    jarvis.add(
      spike,
    );

    dataSpikes.push(
      spike,
    );
  }


  /* ==========================================================
     CAMERA CONTROLS
     ========================================================== */

  const controls =
    new OrbitControls(
      camera,
      renderer.domElement,
    );

  controls.enableDamping =
    true;

  controls.dampingFactor =
    0.08;

  controls.enablePan =
    false;

  controls.minDistance =
    MIN_DISTANCE;

  controls.maxDistance =
    MAX_DISTANCE;

  controls.target.set(
    0,
    -0.15,
    0,
  );

  controls.update();


  /* ==========================================================
     GESTURE / PROGRAMMATIC CAMERA CONTROL
     ========================================================== */

  const sphericalScratch =
    new THREE.Spherical();

  const offsetScratch =
    new THREE.Vector3();


  function rotateBy(
    deltaTheta: number,
    deltaPhi: number,
  ) {

    offsetScratch
      .copy(camera.position)
      .sub(
        controls.target,
      );

    sphericalScratch
      .setFromVector3(
        offsetScratch,
      );

    sphericalScratch.theta -=
      deltaTheta;

    sphericalScratch.phi =
      THREE.MathUtils.clamp(
        sphericalScratch.phi -
          deltaPhi,

        0.05,

        Math.PI - 0.05,
      );

    sphericalScratch.makeSafe();

    offsetScratch
      .setFromSpherical(
        sphericalScratch,
      );

    camera.position
      .copy(
        controls.target,
      )
      .add(
        offsetScratch,
      );

    camera.lookAt(
      controls.target,
    );
  }


  function zoomBy(
    factor: number,
  ) {

    offsetScratch
      .copy(camera.position)
      .sub(
        controls.target,
      );

    const distance =
      THREE.MathUtils.clamp(
        offsetScratch.length() *
          factor,

        MIN_DISTANCE,

        MAX_DISTANCE,
      );

    offsetScratch
      .setLength(
        distance,
      );

    camera.position
      .copy(
        controls.target,
      )
      .add(
        offsetScratch,
      );
  }


  function resetView() {

    camera.position.copy(
      HOME_POSITION,
    );

    controls.target.set(
      0,
      -0.15,
      0,
    );

    camera.lookAt(
      controls.target,
    );

    controls.update();
  }

    /* ==========================================================
     JARVIS VISUAL STATE
     ========================================================== */

    type JarvisVisualState =
      | "idle"
      | "listening"
      | "thinking"
      | "speaking"
      | "executing";


    let jarvisState:
      JarvisVisualState =
        "idle";


    let targetEyeLookX =
      0;

    let targetEyeLookY =
      0;

    let eyeLookX =
      0;

    let eyeLookY =
      0;


    function handleJarvisState(
      event: Event,
    ) {

      const customEvent =
        event as CustomEvent<{
          state?: string;
        }>;


      const state =
        customEvent.detail?.state;


      if (
        state ===
        "idle" ||
        state ===
        "listening" ||
        state ===
        "thinking" ||
        state ===
        "speaking" ||
        state ===
        "executing"
      ) {
        jarvisState =
          state;
      }
    }


    window.addEventListener(
      "jarvis-assistant-state",
      handleJarvisState,
    );


  /* ==========================================================
     ANIMATION
     ========================================================== */

  const clock =
    new THREE.Clock();

    /* ==========================================================
   JARVIS BLINK SYSTEM
   ========================================================== */

  let nextBlink =
    2.5 +
    Math.random() * 3.5;

  let blinkStart =
    -10;

  let blinkActive =
    false;

  let rafId =
    0;

  let disposed =
    false;


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

      /* --------------------------------------------------------
        NATURAL BLINK
        -------------------------------------------------------- */

      if (
        !blinkActive &&
        t >= nextBlink
      ) {
        blinkActive = true;
        blinkStart = t;
      }

      if (blinkActive) {
        const blinkTime =
          t - blinkStart;

        const blinkDuration =
          0.16;

        const blinkProgress =
          Math.min(
            blinkTime /
              blinkDuration,
            1,
          );

        const blinkAmount =
          Math.sin(
            blinkProgress *
              Math.PI,
          );

        const eyeScale =
          1 -
          blinkAmount *
            0.92;

        leftEye.scale.y =
          eyeScale;

        rightEye.scale.y =
          eyeScale;

        if (
          blinkProgress >= 1
        ) {
          blinkActive = false;

          nextBlink =
            t +
            2.5 +
            Math.random() *
              4.5;

          leftEye.scale.y =
            1;

          rightEye.scale.y =
            1;
        }
      }

    /* --------------------------------------------------------
      JARVIS EYE MOVEMENT
      -------------------------------------------------------- */

    if (
      jarvisState ===
      "listening"
    ) {
      /*
      * Listening:
      * subtle scanning movement.
      */
      targetEyeLookX =
        Math.sin(
          t * 0.85,
        ) *
        0.045;

      targetEyeLookY =
        Math.sin(
          t * 0.55,
        ) *
        0.018;
    } else if (
      jarvisState ===
      "thinking"
    ) {
      /*
      * Thinking:
      * slightly more deliberate
      * eye movement.
      */
      targetEyeLookX =
        Math.sin(
          t * 1.35,
        ) *
        0.075;

      targetEyeLookY =
        Math.sin(
          t * 0.9,
        ) *
        0.035;
    } else {
      /*
      * Idle / speaking:
      * return eyes to center.
      */
      targetEyeLookX = 0;
      targetEyeLookY = 0;
    }


    /*
    * Smooth eye movement.
    */
    eyeLookX +=
      (
        targetEyeLookX -
        eyeLookX
      ) *
      0.08;

    eyeLookY +=
      (
        targetEyeLookY -
        eyeLookY
      ) *
      0.08;


    /*
    * Apply to both eyes.
    */
    leftEyeCore.position.x =
      -0.49 +
      eyeLookX;

    leftEyeCore.position.y =
      0.49 +
      eyeLookY;

    rightEyeCore.position.x =
      0.49 +
      eyeLookX;

    rightEyeCore.position.y =
      0.49 +
      eyeLookY;


    /* --------------------------------------------------------
   MAIN JARVIS MOTION
   -------------------------------------------------------- */

  const speaking =
    jarvisState === "speaking";

  const listening =
    jarvisState === "listening";

  const thinking =
    jarvisState === "thinking";

  const executing =
    jarvisState === "executing";

  /* --------------------------------------------------------
    LISTENING / THINKING ENERGY
    -------------------------------------------------------- */

  const listeningEnergy =
    listening
      ? 0.12 +
        Math.abs(
          Math.sin(
            t * 2.2,
          ),
        ) *
          0.10
      : 0;

  const thinkingEnergy =
    thinking
      ? 0.16 +
        Math.abs(
          Math.sin(
            t * 3.8,
          ),
        ) *
          0.16
      : 0;


  const floatSpeed =
    speaking
      ? 1.8
      : thinking
        ? 1.15
        : 0.8;


  const floatAmount =
    speaking
      ? 0.075
      : thinking
        ? 0.065
        : 0.055;


  jarvis.position.y =
    Math.sin(
      t * floatSpeed,
    ) *
    floatAmount;


  jarvis.rotation.y =
    Math.sin(
      t *
        (
          speaking
            ? 0.42
            : thinking
              ? 0.30
              : 0.22
        ),
    ) *
    (
      speaking
        ? 0.075
        : 0.055
    );


  jarvis.rotation.x =
    Math.sin(
      t * 0.31,
    ) *
    (
      listening
        ? 0.030
        : 0.018
    );


    jarvis.rotation.x =
      Math.sin(
        t * 0.31,
      ) *
      0.018;


    /* --------------------------------------------------------
       HEAD BREATHING
       -------------------------------------------------------- */

    head.scale.x =
      1 +
      Math.sin(
        t * 1.1,
      ) *
      0.008;

    head.scale.y =
      1 +
      Math.sin(
        t * 1.1 +
        0.7,
      ) *
      0.006;


    /* --------------------------------------------------------
       EYE ENERGY
       -------------------------------------------------------- */

    const baseEyePulse =
      0.70 +
      Math.sin(
        t * 3.4,
      ) *
      0.30;

    const speakingEyePulse =
      jarvisState ===
      "speaking"
        ? 0.18 +
          Math.abs(
            Math.sin(
              t * 7.0,
            ),
          ) *
            0.22
        : 0;

    white.opacity =
      Math.min(
        1,
        baseEyePulse +
          speakingEyePulse,
      );


    /* --------------------------------------------------------
      FOREHEAD INTELLIGENCE CORE
      -------------------------------------------------------- */

    const foreheadSpeed =
      speaking
        ? 1.25
        : thinking
          ? 1.65
          : listening
            ? 1.0
            : 0.7;

    foreheadCore.rotation.z =
      t *
      foreheadSpeed;

    const foreheadPulse =
      speaking
        ? 0.24
        : thinking
          ? 0.22
          : listening
            ? 0.18
            : 0.15;

    const foreheadPulseSpeed =
      speaking
        ? 5.5
        : thinking
          ? 4.2
          : listening
            ? 3.2
            : 2.4;

    foreheadCoreInner.scale.setScalar(
      0.8 +
        Math.sin(
          t *
            foreheadPulseSpeed,
        ) *
          foreheadPulse,
    );

    /* --------------------------------------------------------
      JARVIS SPEECH WAVEFORM
      -------------------------------------------------------- */

    if (
      jarvisState ===
      "speaking"
    ) {
      speechPulse +=
        0.16;

      for (
        let i = 0;
        i < mouthBars.length;
        i++
      ) {
        const bar =
          mouthBars[i];

        const center =
          (
            mouthBars.length - 1
          ) / 2;

        const distance =
          Math.abs(
            i - center,
          );

        const centerWeight =
          Math.max(
            0.25,
            1 -
              distance /
                center,
          );

        const primaryWave =
          Math.abs(
            Math.sin(
              t * 8.5 +
                i * 0.72,
            ),
          );

        const secondaryWave =
          Math.abs(
            Math.sin(
              t * 13.5 +
                i * 1.15,
            ),
          );

        const height =
          0.35 +
          primaryWave *
            0.75 *
            centerWeight +
          secondaryWave *
            0.30;

        bar.scale.y =
          height;
      }
    } else {
      speechPulse *=
        0.88;

      for (
        let i = 0;
        i < mouthBars.length;
        i++
      ) {
        const bar =
          mouthBars[i];

        bar.scale.y =
          0.35;
      }
    }


    /* --------------------------------------------------------
       CHEST CORE
       -------------------------------------------------------- */

    chestRing.rotation.z =
      t * 0.9;

    chestRing2.rotation.z =
      -t * 1.6;

    const coreSpeed =
      speaking
        ? 7.0
        : thinking
          ? 4.5
          : executing
            ? 5.5
            : 3.0;


    const coreStrength =
      speaking
        ? 0.28
        : thinking
          ? 0.23
          : executing
            ? 0.26
            : 0.18;


    chestCore.scale.setScalar(
      0.85 +
        Math.sin(
          t * coreSpeed,
        ) *
          coreStrength,
    );


    /* --------------------------------------------------------
       ORBITS
       -------------------------------------------------------- */

    orbitGroup.rotation.y =
      t * 0.18;

    orbitGroup.rotation.x =
      Math.sin(
        t * 0.35,
      ) *
      0.12;

    orbitGroup.rotation.z =
      Math.sin(
        t * 0.22,
      ) *
      0.08;


    /* --------------------------------------------------------
       ORBIT NODES
       -------------------------------------------------------- */

    for (
      let i = 0;
      i < orbitNodes.length;
      i++
    ) {

      const node =
        orbitNodes[i];

      node.rotation.x +=
        0.012;

      node.rotation.y +=
        0.018;

      const scale =
        0.75 +
        Math.sin(
          t * 2 +
          i,
        ) *
        0.25;

      node.scale.setScalar(
        scale,
      );
    }


    /* --------------------------------------------------------
       PARTICLES
       -------------------------------------------------------- */

    const particleSpeed =
      thinking
        ? 0.042
        : listening
          ? 0.026
          : 0.018;

    particles.rotation.y =
      t *
      particleSpeed;

    particles.rotation.x =
      Math.sin(
        t *
          (
            thinking
              ? 0.22
              : 0.12
          ),
      ) *
      (
        thinking
          ? 0.065
          : 0.04
      );


    /* --------------------------------------------------------
       SCAN RINGS
       -------------------------------------------------------- */

    for (
      let i = 0;
      i < scanRings.length;
      i++
    ) {

      const ring =
        scanRings[i];

      const scanSpeed =
        thinking
          ? 0.34
          : listening
            ? 0.20
            : 0.15;

      ring.rotation.z =
        t *
        (
          i % 2 === 0
            ? scanSpeed
            : -scanSpeed *
              0.8
        );

      const scanMovement =
        thinking
          ? 0.065
          : listening
            ? 0.045
            : 0.035;

      ring.position.y =
        -1.0 +
        i * 0.20 +
        Math.sin(
          t * 1.2 +
          i,
        ) *
          scanMovement;
    }


    /* --------------------------------------------------------
       DATA SPIKES
       -------------------------------------------------------- */

    for (
      let i = 0;
      i < dataSpikes.length;
      i++
    ) {
      const material =
        dataSpikes[i].material;

      if (
        Array.isArray(material)
      ) {
        for (
          const item of material
        ) {
          item.opacity =
            0.25 +
            Math.abs(
              Math.sin(
                t * 2 +
                i * 0.4,
              ),
            ) *
            0.40;
        }
      } else {
        material.opacity =
          0.25 +
          Math.abs(
            Math.sin(
              t * 2 +
              i * 0.4,
            ),
          ) *
          0.40;
      }
    }


    /* --------------------------------------------------------
       BLOOM
       -------------------------------------------------------- */

    const bloomBase =
      speaking
        ? 1.72
        : thinking
          ? 1.60
          : listening
            ? 1.54
            : executing
              ? 1.62
              : 1.45;


    const bloomPulse =
      speaking
        ? 0.32
        : thinking
          ? 0.27
          : listening
            ? 0.20
            : 0.22;


    bloom.strength =
      bloomBase +
      Math.sin(
        t *
          (
            speaking
              ? 5.5
              : 0.75
          ),
      ) *
        bloomPulse;


    /* --------------------------------------------------------
       CHROMATIC TIME
       -------------------------------------------------------- */

    chromaticPass
      .uniforms
      .uTime
      .value =
      t;


    controls.update();

    composer.render();
  }


  animate();


  /* ==========================================================
     RESIZE
     ========================================================== */

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


  /* ==========================================================
     CLEANUP
     ========================================================== */

  function dispose() {

    disposed = true;

    window.removeEventListener(
      "jarvis-assistant-state",
      handleJarvisState,
    );

    cancelAnimationFrame(
      rafId,
    );

    window.removeEventListener(
      "resize",
      onResize,
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
            : [
                mesh.material,
              ];

        for (
          const material of
            materials
        ) {

          if (!material) {
            continue;
          }

          const anyMaterial =
            material as
              THREE.Material & {
                map?: THREE.Texture;
              };

          anyMaterial.map?.dispose();

          material.dispose();
        }
      },
    );

    composer.dispose();

    renderer.dispose();

    renderer.domElement.remove();
  }


  /* ==========================================================
     PUBLIC API
     ========================================================== */

  return {

    rotateBy,

    zoomBy,

    zoomIn: () =>
      zoomBy(0.65),

    zoomOut: () =>
      zoomBy(1.55),

    resetView,

    dispose,
  };
}