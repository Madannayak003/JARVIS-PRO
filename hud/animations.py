"""
JARVIS PRO HUD
Ultron Animation Engine
"""

import math
import random
import time


class AnimationEngine:

    def __init__(self):

        self.started = time.time()

        self.particles = []

        self._create_particles()

    # =====================================================
    # Time
    # =====================================================

    def elapsed(self):

        return (
            time.time()
            - self.started
        )

    # =====================================================
    # Particles
    # =====================================================

    def _create_particles(self):

        for _ in range(150):

            self.particles.append({

                "x": random.random(),

                "y": random.random(),

                "size": random.uniform(
                    0.5,
                    2.5
                ),

                "speed": random.uniform(
                    0.02,
                    0.10
                ),

                "phase": random.uniform(
                    0,
                    math.pi * 2
                ),

            })

    # =====================================================

    def particle_position(
        self,
        particle,
    ):

        t = self.elapsed()

        x = particle["x"]

        y = (
            particle["y"]
            - (
                t
                * particle["speed"]
            )
        ) % 1.0

        wobble = math.sin(
            t
            + particle["phase"]
        ) * 0.004

        return (
            x + wobble,
            y,
        )

    # =====================================================
    # Rotation
    # =====================================================

    def rotation(
        self,
        speed=1.0,
    ):

        return (
            self.elapsed()
            * speed
            * 360
        ) % 360

    # =====================================================
    # Pulse
    # =====================================================

    def pulse(
        self,
        speed=2.0,
    ):

        return (
            math.sin(
                self.elapsed()
                * speed
            )
            + 1
        ) / 2

    # =====================================================
    # Energy
    # =====================================================

    def energy(
        self,
        index,
        count,
    ):

        t = self.elapsed()

        angle = (
            index
            / max(
                count,
                1
            )
            * math.pi
            * 2
        )

        return (

            math.sin(
                angle * 3
                + t * 4
            )

            * 0.5

            + 0.5

        )

    # =====================================================
    # Scan
    # =====================================================

    def scan_position(self):

        return (
            self.elapsed()
            * 0.20
        ) % 1.0