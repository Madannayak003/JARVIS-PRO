"""Focused checks for the separated HUD, speech, and diagnostic outputs."""

from __future__ import annotations

import io
import os
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from core.diagnostics import debug_print
from hud.bus import hud_bus
from hud.manager import HUDManager
from voice.speech_text import clean_for_speech


class PresentationCleanupTests(unittest.TestCase):
    def test_debug_output_is_opt_in(self):
        output = io.StringIO()

        with patch.dict(os.environ, {"JARVIS_DEBUG": "0"}, clear=False):
            with redirect_stdout(output):
                debug_print("hidden diagnostic")

        self.assertEqual(output.getvalue(), "")

        output = io.StringIO()
        with patch.dict(os.environ, {"JARVIS_DEBUG": "1"}, clear=False):
            with redirect_stdout(output):
                debug_print("visible diagnostic")

        self.assertIn("visible diagnostic", output.getvalue())

    def test_speech_keeps_decimals_and_suppresses_structured_output(self):
        spoken = clean_for_speech(
            "The run took 0.068214 seconds.\n"
            '{"result": 333332833333500000, "ok": true}'
        )

        self.assertIn("0.068214", spoken)
        self.assertNotIn("333332833333500000", spoken)
        self.assertNotIn('"result"', spoken)

    def test_hud_response_preserves_one_original_formatted_entry(self):
        manager = HUDManager()
        events = []

        def collect(event):
            events.append(event)

        hud_bus.subscribe(collect)
        try:
            original = "## Code Example\n\n```python\nprint('Hello')\n```"
            manager.response(original)
        finally:
            hud_bus.unsubscribe(collect)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].name, "response")
        self.assertEqual(events[0].data["text"], original)

    def test_streaming_tts_no_longer_emits_sentence_activity_events(self):
        tts_source = (
            Path(__file__).parents[1] / "voice" / "tts_pipeline.py"
        ).read_text(encoding="utf-8")
        worker_source = (
            Path(__file__).parents[1] / "ai" / "ai_worker.py"
        ).read_text(encoding="utf-8")

        self.assertNotIn("notify_speech_output(", tts_source)
        self.assertIn("HUDIntegration.response(answer)", worker_source)


if __name__ == "__main__":
    unittest.main()
