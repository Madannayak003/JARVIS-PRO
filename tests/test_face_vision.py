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
