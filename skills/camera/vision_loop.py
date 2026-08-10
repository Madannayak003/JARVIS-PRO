import threading
import time

from skills.camera.vision import vision
from skills.camera.scene_analyzer import scene_analyzer


class VisionLoop:

    def __init__(self, interval=0.5):

        self.interval = interval

        self.running = False
        self.thread = None

        self.latest_scene = None

        # Used to signal that the first scene is ready
        self.scene_ready = threading.Event()

    # --------------------------------------------------
    # Start
    # --------------------------------------------------

    def start(self):

        if self.running:

            print("[VISION LOOP] Already running.")

            # If already running, wait briefly for a scene
            self.scene_ready.wait(timeout=5)

            return True

        print("[VISION LOOP] Starting...")

        # Clear previous state
        self.latest_scene = None
        self.scene_ready.clear()

        if not vision.start():

            print(
                "[VISION LOOP] Vision failed to start."
            )

            return False

        self.running = True

        self.thread = threading.Thread(
            target=self._run,
            name="VisionLoop",
            daemon=True
        )

        self.thread.start()

        print(
            "[VISION LOOP] Started. "
            "Waiting for first scene..."
        )

        # Wait until the first YOLO scene is available.
        # This prevents vision_query from seeing None.
        if not self.scene_ready.wait(timeout=10):

            print(
                "[VISION LOOP] WARNING: "
                "First scene was not ready within 10 seconds."
            )

        else:

            print(
                "[VISION LOOP] First scene ready."
            )

        return True

    # --------------------------------------------------
    # Processing Loop
    # --------------------------------------------------

    def _run(self):

        print("[VISION LOOP] Worker started.")

        while self.running:

            try:

                frame = vision.get_frame()

                if frame is None:

                    time.sleep(
                        self.interval
                    )

                    continue

                detections = vision.detect(
                    frame
                )

                scene = scene_analyzer.analyze(
                    detections,
                    frame.shape[1]
                )

                self.latest_scene = scene

                # Signal first successful scene
                if not self.scene_ready.is_set():

                    self.scene_ready.set()

            except Exception as e:

                print(
                    "[VISION LOOP ERROR]",
                    e
                )

            # Don't sleep after stop was requested
            if self.running:

                time.sleep(
                    self.interval
                )

        print(
            "[VISION LOOP] Worker exited."
        )

    # --------------------------------------------------
    # Get Latest Scene
    # --------------------------------------------------

    def get_scene(self):

        return self.latest_scene

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    def status(self):

        return {
            "running": self.running,
            "scene": self.latest_scene
        }

    # --------------------------------------------------
    # Stop
    # --------------------------------------------------

    def stop(self):

        if not self.running:

            print(
                "[VISION LOOP] Already stopped."
            )

            return True

        print(
            "[VISION LOOP] Stopping..."
        )

        # Tell worker to stop
        self.running = False

        # Wait for worker to completely exit.
        # Do NOT release the camera while YOLO is still
        # processing a frame.
        if (
            self.thread
            and self.thread.is_alive()
        ):

            self.thread.join(
                timeout=15
            )

        # Safety check
        if (
            self.thread
            and self.thread.is_alive()
        ):

            print(
                "[VISION LOOP] WARNING: "
                "Worker did not stop within timeout."
            )

        self.thread = None

        # Now it is safe to stop the vision/camera system
        vision.stop()

        self.latest_scene = None
        self.scene_ready.clear()

        print(
            "[VISION LOOP] Stopped."
        )

        return True


vision_loop = VisionLoop()