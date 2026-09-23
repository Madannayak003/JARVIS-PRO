"""Regression coverage for contextual follow-ups versus vision matching."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location(
    "jarvis_test_vision_router",
    ROOT / "core" / "routers" / "vision_router.py",
)
VISION_ROUTER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VISION_ROUTER)


class VisionFollowUpPrecedenceTests(unittest.TestCase):
    def test_generic_another_one_is_not_a_vision_target(self):
        plan = VISION_ROUTER.vision_route("Show me another one.")

        self.assertIsNone(plan)

    def test_explicit_person_target_remains_available(self):
        plan = VISION_ROUTER.vision_route("Show me another person.")

        self.assertEqual(plan[0]["action"], "vision_target")
        self.assertIn("person", plan[0]["object"])

    def test_find_object_target_remains_available(self):
        plan = VISION_ROUTER.vision_route("Find the red object.")

        self.assertEqual(plan[0]["action"], "vision_target")
        self.assertIn("red object", plan[0]["object"])


if __name__ == "__main__":
    unittest.main()
