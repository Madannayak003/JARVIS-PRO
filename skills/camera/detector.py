"""
JARVIS PRO
Vision Object Detector

Stage 2:
YOLO-based object detection.

The detector is independent from CameraManager.
"""

from pathlib import Path

from ultralytics import YOLO


class ObjectDetector:

    def __init__(self, model_path="yolo11n.pt"):

        self.model_path = Path(model_path)
        self.model = None
        self.loaded = False

    # --------------------------------------------------
    # Load Model
    # --------------------------------------------------

    def load(self):

        if self.loaded:
            return True

        try:

            print(
                f"[VISION DETECTOR] Loading model: "
                f"{self.model_path}"
            )

            self.model = YOLO(str(self.model_path))

            self.loaded = True

            print("[VISION DETECTOR] Model loaded.")

            return True

        except Exception as e:

            print(
                f"[VISION DETECTOR ERROR] "
                f"Model load failed: {e}"
            )

            self.model = None
            self.loaded = False

            return False

    # --------------------------------------------------
    # Detect
    # --------------------------------------------------

    def detect(self, frame):

        if frame is None:

            print(
                "[VISION DETECTOR] "
                "No frame supplied."
            )

            return []

        if not self.load():

            return []

        try:

            results = self.model.predict(
                source=frame,
                device="cpu",
                verbose=False
            )

            detections = []

            for result in results:

                boxes = result.boxes

                if boxes is None:
                    continue

                for box in boxes:

                    class_id = int(
                        box.cls[0]
                    )

                    confidence = float(
                        box.conf[0]
                    )

                    label = result.names[
                        class_id
                    ]

                    coordinates = [
                        int(value)
                        for value in box.xyxy[0].tolist()
                    ]

                    detections.append(
                        {
                            "label": label,
                            "confidence": confidence,
                            "box": coordinates,
                        }
                    )

            return detections

        except Exception as e:

            print(
                f"[VISION DETECTOR ERROR] "
                f"Detection failed: {e}"
            )

            return []


detector = ObjectDetector()