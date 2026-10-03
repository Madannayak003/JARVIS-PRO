import tempfile
import unittest
import sys
import types
import threading
from unittest.mock import patch
from pathlib import Path

# Keep the unit tests focused on storage/extraction behavior even when the
# optional runtime provider dependencies are not installed in the test shell.
registry_stub = types.ModuleType("core.registry")
registry_stub.register = lambda *args, **kwargs: None
sys.modules.setdefault("core.registry", registry_stub)

from skills.files import file_intelligence as files


class FileIntelligenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old_root = files.ROOT
        self.old_files = files.FILES_DIR
        self.old_index = files.INDEX_PATH
        files.ROOT = Path(self.temp.name)
        files.FILES_DIR = files.ROOT / "files"
        files.INDEX_PATH = files.ROOT / "index.json"

    def tearDown(self):
        files.ROOT = self.old_root
        files.FILES_DIR = self.old_files
        files.INDEX_PATH = self.old_index
        self.temp.cleanup()

    def test_filename_is_sanitized_and_upload_is_contextual(self):
        record = files.save_uploaded_file("..\\notes/../todo.txt", b"Arduino\nuse motors")
        self.assertEqual(record["filename"], "todo.txt")
        self.assertEqual(record["processing_status"], "READY")
        self.assertEqual(files.read_file(record["id"])["text"], "Arduino\nuse motors")

    def test_search_and_edit_create_backup(self):
        record = files.save_uploaded_file("main.py", b"timeout = 10\n")
        self.assertEqual(files.search_files("timeout", [record["id"]])[0]["count"], 1)
        edited = files.edit_file(record["id"], "timeout = 10", "timeout = 30")
        self.assertTrue(Path(edited["backup"]).is_file())
        self.assertIn("30", files.read_file(record["id"])["text"])

    def test_unsupported_format_is_reported_without_crashing(self):
        record = files.save_uploaded_file("program.exe", b"MZ")
        self.assertEqual(record["type"]["supported"], False)
        self.assertEqual(record["processing_status"], "FAILED")

    def test_document_analysis_uses_existing_reasoning_capability(self):
        record = files.save_uploaded_file("notes.txt", b"The internship was at JARVIS Labs.")
        calls = []

        class Response:
            success = True
            text = "A short summary."

        class Service:
            def generate(self, **kwargs):
                calls.append(kwargs)
                return Response()

        service_module = types.ModuleType("ai.core.service")
        service_module.ai_service = Service()
        with patch.dict(sys.modules, {"ai.core.service": service_module}):
            self.assertEqual(files.summarize_file(record["id"], "Summarize it."), "A short summary.")
        self.assertEqual(calls[0]["capability"], "reasoning")

    def test_folder_action_uses_exact_record_path(self):
        record = files.save_uploaded_file("notes.txt", b"content")
        with patch.object(files.subprocess, "Popen") as popen:
            result = files.file_intelligence_action({"action": "file_open_folder", "file_id": record["id"]})
        self.assertTrue(result.endswith(record["id"]))
        self.assertEqual(popen.call_args.args[0][0], "explorer.exe")
        self.assertIn(record["id"], popen.call_args.args[0][1])

    def test_missing_file_context_is_reported(self):
        with self.assertRaises(FileNotFoundError):
            files.read_file("missing-file")

    def test_speak_file_uses_existing_voice_manager_and_chunks(self):
        record = files.save_uploaded_file("speech.txt", ("one " * 400).encode("utf-8"))
        calls = []
        voice_module = types.ModuleType("voice.manager")
        session = types.SimpleNamespace(cancel_event=threading.Event())
        voice_module.start_speech_session = lambda: session
        voice_module.speak = lambda text, **kwargs: calls.append((text, kwargs))
        with patch.dict(sys.modules, {"voice.manager": voice_module}):
            result = files.speak_file(record["id"])
            files._speech_thread.join(timeout=2)
        self.assertTrue(result["started"])
        self.assertGreater(len(calls), 1)
        self.assertTrue(all(call[1]["session"] is session for call in calls))


if __name__ == "__main__":
    unittest.main()
