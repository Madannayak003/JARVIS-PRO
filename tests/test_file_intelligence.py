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
        self.assertEqual(calls[0]["capability"], "file_intelligence")
        self.assertEqual(calls[0]["provider"], "gemini")
        self.assertEqual(calls[0]["model"], "gemini-3.5-flash-lite")

    def test_file_question_uses_the_same_dedicated_model(self):
        record = files.save_uploaded_file("notes.txt", b"The phone number is 555-0100.")
        calls = []

        class Response:
            success = True
            text = "555-0100"

        class Service:
            def generate(self, **kwargs):
                calls.append(kwargs)
                return Response()

        service_module = types.ModuleType("ai.core.service")
        service_module.ai_service = Service()
        with patch.dict(sys.modules, {"ai.core.service": service_module}):
            result = files.file_intelligence_action({"action": "file_question_request", "question": "What is the phone number?"})
        self.assertEqual(result, "555-0100")
        self.assertEqual(calls[0]["capability"], "file_intelligence")
        self.assertEqual(calls[0]["provider"], "gemini")
        self.assertEqual(calls[0]["model"], "gemini-3.5-flash-lite")

    def test_question_router_requires_active_ready_file(self):
        from core.routers.file_router import file_route

        self.assertIsNone(file_route("What is the phone number mentioned in this file?"))
        files.save_uploaded_file("resume.txt", b"phone number: 555-0100")
        for question in (
            "What is the phone number mentioned in this file?",
            "What is the person's name?",
            "Where did they do their internship?",
            "What does this PDF say about education?",
            "Can you explain this document?",
        ):
            plan = file_route(question)
            self.assertEqual(plan[0]["action"], "file_question_request", question)

    def test_read_does_not_call_ai(self):
        record = files.save_uploaded_file("read.txt", b"Read-only content")
        with patch.object(files, "speak_file", return_value={"started": True}), \
             patch.dict(sys.modules, {"ai.core.service": types.ModuleType("ai.core.service")}):
            result = files.file_intelligence_action({"action": "file_intelligence_request", "request": "Read this file"})
        self.assertEqual(result["file"]["id"], record["id"])

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
