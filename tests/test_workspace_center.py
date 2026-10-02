import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from hud.workspace_center import WorkspaceCenter


class WorkspaceCenterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name) / "workspace"
        (root / "Html" / "Portfolio").mkdir(parents=True)
        (root / "Html" / "Portfolio" / "index.html").write_text("<h1>test</h1>", encoding="utf-8")
        (root / "Python" / "Worker").mkdir(parents=True)
        (root / "Python" / "Worker" / "main.py").write_text("print('ok')", encoding="utf-8")
        self.center = WorkspaceCenter(root)
        self.center._open = lambda _url: None

    def tearDown(self):
        for project in list(self.center._previews):
            self.center.stop_preview(project)
        self.temp.cleanup()

    def test_discovers_actual_paths_and_types(self):
        projects = self.center.list_projects()["projects"]
        by_name = {project["name"]: project for project in projects}
        self.assertEqual(by_name["Portfolio"]["type"], "HTML")
        self.assertEqual(by_name["Portfolio"]["entry_file"], "index.html")
        self.assertTrue(by_name["Portfolio"]["preview_available"])
        self.assertEqual(by_name["Worker"]["type"], "Python")
        self.assertFalse(by_name["Worker"]["preview_available"])
        self.assertTrue(by_name["Portfolio"]["location"].endswith("Portfolio"))

    def test_preview_uses_localhost_and_can_stop(self):
        project = self.center.list_projects()["projects"][0]
        self.center._open = Mock()
        started = self.center.start_preview(project["id"])
        self.assertTrue(started["ok"])
        self.center._open.assert_not_called()
        self.assertTrue(started["project"]["preview_url"].startswith("http://127.0.0.1:"))
        self.assertTrue(started["project"]["preview_running"])
        external = self.center.open_externally(project["id"])
        self.assertTrue(external["ok"])
        self.center._open.assert_called_once_with(started["project"]["preview_url"])
        stopped = self.center.stop_preview(project["id"])
        self.assertTrue(stopped["ok"])
        self.assertFalse(stopped["project"]["preview_running"])

    def test_non_html_cannot_start_preview(self):
        project = next(item for item in self.center.list_projects()["projects"] if item["name"] == "Worker")
        result = self.center.start_preview(project["id"])
        self.assertFalse(result["ok"])

    def test_outside_project_id_is_rejected(self):
        self.assertIsNone(self.center.detail(str(Path(self.temp.name).parent)))


if __name__ == "__main__":
    unittest.main()
