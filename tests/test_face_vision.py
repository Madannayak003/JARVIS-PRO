"""Focused local Vision face-registration and speech regressions."""

from pathlib import Path
import tempfile
import time
import unittest

from core.routers.vision_router import vision_route
from skills.camera.face_recognizer import FaceRecognizer
from skills.camera.face_registration import FaceRegistrationFlow
from skills.camera.face_registry import FaceRegistry, sanitize_name
from skills.camera.face_speech import VisionSpeechState, people_message
from skills.camera.scene_analyzer import SceneAnalyzer


class FaceRegistryTests(unittest.TestCase):
    def test_canonical_root_and_directory_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "data" / "faces"
            registry = FaceRegistry(root)
            self.assertEqual(registry.root, root)
            self.assertEqual(registry.ensure_identity("Madan"), root / "Madan")
            self.assertTrue((root / "Madan").is_dir())

    def test_name_sanitization_blocks_path_traversal(self):
        self.assertEqual(sanitize_name(" Rahul "), "Rahul")
        self.assertEqual(sanitize_name("Rahul/../other"), "Rahul_.._other")
        with self.assertRaises(ValueError):
            sanitize_name("../")

    def test_registration_sample_saving(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = FaceRegistry(Path(directory))

            def writer(path, frame):
                Path(path).write_bytes(str(frame).encode())
                return True

            saved = registry.save_samples("Madan", ["one", "two"], writer)
            self.assertEqual([path.name for path in saved], ["face_001.jpg", "face_002.jpg"])
            self.assertEqual(len(registry.samples("Madan")), 2)

    def test_specific_and_all_face_deletion(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = FaceRegistry(Path(directory))

            def writer(path, frame):
                Path(path).write_bytes(str(frame).encode())
                return True

            registry.save_samples("Madan", ["one"], writer)
            registry.save_samples("Rahul", ["two"], writer)
            self.assertTrue(registry.delete_identity("Madan"))
            self.assertEqual(registry.identities(), ["Rahul"])
            self.assertFalse(registry.delete_identity("Madan"))
            self.assertEqual(registry.delete_all(), 1)
            self.assertEqual(registry.identities(), [])
            self.assertTrue(Path(directory).is_dir())

    def test_registered_identity_lookup_and_unknown_result(self):
        with tempfile.TemporaryDirectory() as directory:
            recognizer = FaceRecognizer(FaceRegistry(Path(directory)))
            recognizer._label_to_name = {1: "Madan"}
            self.assertEqual(recognizer.prediction_result(1, 20)["name"], "Madan")
            self.assertTrue(recognizer.prediction_result(1, 20)["recognized"])
            unknown = recognizer.prediction_result(1, 90)
            self.assertIsNone(unknown["name"])
            self.assertFalse(unknown["recognized"])


class FaceSpeechTests(unittest.TestCase):
    def test_wording_for_owner_other_unknown_and_multiple_people(self):
        madan = {"label": "person", "recognized": True, "name": "Madan"}
        rahul = {"label": "person", "recognized": True, "name": "Rahul"}
        unknown = {"label": "person", "recognized": False, "name": None}
        self.assertEqual(people_message([madan]), "I see you, Madan.")
        self.assertEqual(people_message([rahul]), "I see Rahul.")
        self.assertEqual(people_message([unknown]), "I see a person.")
        self.assertEqual(people_message([unknown, unknown]), "I see 2 people.")
        self.assertEqual(people_message([madan, rahul]), "I see you, Madan, and Rahul.")
        self.assertEqual(people_message([madan, unknown]), "I see you, Madan, and another person.")
        self.assertEqual(people_message([rahul, unknown]), "I see Rahul and another person.")

    def test_speech_deduplication_leave_return_and_identity_change(self):
        now = [100.0]
        state = VisionSpeechState(cooldown=10, clock=lambda: now[0])
        madan = [{"label": "person", "recognized": True, "name": "Madan"}]
        rahul = [{"label": "person", "recognized": True, "name": "Rahul"}]
        self.assertTrue(state.should_speak(madan))
        self.assertFalse(state.should_speak(madan))
        self.assertFalse(state.should_speak([]))
        now[0] = 111.0
        self.assertTrue(state.should_speak(madan))
        self.assertTrue(state.should_speak(rahul))

    def test_new_vision_session_can_announce_same_person_again(self):
        state = VisionSpeechState(cooldown=60, clock=lambda: 100.0)
        madan = [{"label": "person", "recognized": True, "name": "Madan"}]
        self.assertTrue(state.should_speak(madan))
        self.assertFalse(state.should_speak(madan))
        state.reset()
        self.assertTrue(state.should_speak(madan))


class VisionIntegrationTests(unittest.TestCase):
    def test_registration_commands_are_deterministic(self):
        self.assertEqual(vision_route("register my face"), [{"action": "register_face"}])
        self.assertEqual(vision_route("register Rahul"), [{"action": "register_face", "name": "Rahul"}])
        self.assertEqual(vision_route("register face as Madan"), [{"action": "register_face", "name": "Madan"}])
        self.assertEqual(vision_route("cancel registration"), [{"action": "cancel_face_registration"}])
        self.assertEqual(vision_route("start vision"), [{"action": "vision_start"}])
        self.assertEqual(vision_route("stop vision"), [{"action": "vision_stop"}])
        self.assertEqual(vision_route("delete face Rahul"), [{"action": "delete_face", "name": "Rahul"}])
        self.assertEqual(vision_route("delete all faces"), [{"action": "delete_face", "all": True}])

    def test_existing_scene_description_for_non_person_objects_is_preserved(self):
        scene = SceneAnalyzer().analyze([
            {"label": "bottle", "confidence": 0.9, "box": [0, 0, 100, 100]}
        ], 640, 480)
        self.assertIn("bottle", scene["description"])

    def test_person_only_scene_is_described(self):
        scene = SceneAnalyzer().analyze([
            {"label": "person", "confidence": 0.9, "box": [0, 0, 100, 200]}
        ], 640, 480)
        self.assertIn("person", scene["description"])

    def test_person_and_bottle_are_both_retained_and_described(self):
        scene = SceneAnalyzer().analyze([
            {"label": "person", "confidence": 0.9, "box": [0, 0, 100, 200]},
            {"label": "bottle", "confidence": 0.9, "box": [120, 0, 180, 160]},
        ], 640, 480)
        self.assertEqual(
            [item["label"] for item in scene["objects"]],
            ["person", "bottle"],
        )
        self.assertIn("person", scene["description"])
        self.assertIn("bottle", scene["description"])

    def test_bottle_without_person_is_preserved(self):
        scene = SceneAnalyzer().analyze([
            {"label": "bottle", "confidence": 0.9, "box": [0, 0, 100, 160]}
        ], 640, 480)
        self.assertEqual(scene["counts"], {"bottle": 1})
        self.assertIn("bottle", scene["description"])

    def test_person_bottle_and_laptop_are_all_retained(self):
        scene = SceneAnalyzer().analyze([
            {"label": "person", "confidence": 0.9, "box": [0, 0, 100, 200]},
            {"label": "bottle", "confidence": 0.9, "box": [120, 0, 180, 160]},
            {"label": "laptop", "confidence": 0.9, "box": [200, 0, 360, 130]},
        ], 640, 480)
        self.assertEqual(
            set(scene["counts"]),
            {"person", "bottle", "laptop"},
        )
        for label in ("person", "bottle", "laptop"):
            self.assertIn(label, scene["description"])

    def test_face_enrichment_keeps_registered_person_and_bottle(self):
        recognizer = FaceRecognizer(FaceRegistry(Path(tempfile.mkdtemp())))
        recognizer.analyze_frame = lambda frame, detections=None: [{
            "type": "face",
            "name": "Madan",
            "recognized": True,
            "confidence": 0.95,
            "box": [10, 0, 90, 80],
        }]
        detections = [
            {"label": "person", "confidence": 0.9, "box": [0, 0, 100, 200]},
            {"label": "bottle", "confidence": 0.9, "box": [120, 0, 180, 160]},
        ]
        enriched = recognizer.enrich_detections(object(), detections)
        self.assertEqual(
            [item["label"] for item in enriched],
            ["person", "bottle"],
        )
        self.assertEqual(enriched[0]["name"], "Madan")
        scene = SceneAnalyzer().analyze(enriched, 640, 480)
        self.assertIn("Madan", scene["description"])
        self.assertIn("bottle", scene["description"])

    def test_unknown_person_and_bottle_are_both_preserved(self):
        recognizer = FaceRecognizer(FaceRegistry(Path(tempfile.mkdtemp())))
        recognizer.analyze_frame = lambda frame, detections=None: [{
            "type": "face",
            "name": None,
            "recognized": False,
            "confidence": 0.0,
            "box": [10, 0, 90, 80],
        }]
        detections = [
            {"label": "person", "confidence": 0.9, "box": [0, 0, 100, 200]},
            {"label": "bottle", "confidence": 0.9, "box": [120, 0, 180, 160]},
        ]
        enriched = recognizer.enrich_detections(object(), detections)
        scene = SceneAnalyzer().analyze(enriched, 640, 480)
        self.assertEqual(set(scene["counts"]), {"person", "bottle"})
        self.assertIn("bottle", scene["description"])

    def test_deleted_face_does_not_remove_bottle_detection(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = FaceRegistry(Path(directory))
            registry.ensure_identity("Madan")
            self.assertTrue(registry.delete_identity("Madan"))

            recognizer = FaceRecognizer(registry)
            recognizer.analyze_frame = lambda frame, detections=None: [{
                "type": "face",
                "name": None,
                "recognized": False,
                "confidence": 0.0,
                "box": [10, 0, 90, 80],
            }]
            detections = [
                {"label": "person", "confidence": 0.9, "box": [0, 0, 100, 200]},
                {"label": "bottle", "confidence": 0.9, "box": [120, 0, 180, 160]},
            ]
            enriched = recognizer.enrich_detections(object(), detections)
            self.assertEqual(
                [item["label"] for item in enriched],
                ["person", "bottle"],
            )

    def test_multiple_objects_without_face_are_preserved(self):
        scene = SceneAnalyzer().analyze([
            {"label": "bottle", "confidence": 0.9, "box": [0, 0, 100, 160]},
            {"label": "cup", "confidence": 0.9, "box": [120, 0, 180, 120]},
        ], 640, 480)
        self.assertEqual(set(scene["counts"]), {"bottle", "cup"})

    def test_registration_cancellation_and_camera_failure_are_safe(self):
        class Camera:
            def opened(self):
                return False
            def start(self):
                return False
            def stop(self):
                return None

        class Recognizer:
            def detect_faces(self, frame):
                return []

        flow = FaceRegistrationFlow(
            registry=FaceRegistry(Path(tempfile.mkdtemp())),
            recognizer=Recognizer(),
            camera_manager=Camera(),
        )
        self.assertTrue(flow.start("Madan"))
        deadline = time.time() + 1
        while flow.active and time.time() < deadline:
            time.sleep(0.01)
        self.assertFalse(flow.active)
        self.assertTrue(flow.cancel() is False)


if __name__ == "__main__":
    unittest.main()
