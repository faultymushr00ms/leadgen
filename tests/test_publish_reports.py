"""Publish data/reports to a reports branch without touching the project repo."""

import importlib.util
import os
import subprocess
import tempfile
import unittest
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_publish():
    path = os.path.join(ROOT, "scripts", "publish_reports.py")
    spec = importlib.util.spec_from_file_location("publish_reports", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


publish = load_publish()


def git(cwd, *args, check=True):
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=check,
        capture_output=True,
        text=True,
    )


class SanitizeTests(unittest.TestCase):
    def test_origin_userinfo_is_removed(self):
        cleaned = publish.sanitize_origin(
            "https://x-access-token:SECRET@github.com/faultymushr00ms/leadgen.git"
        )
        self.assertEqual(cleaned, "https://github.com/faultymushr00ms/leadgen.git")
        self.assertNotIn("SECRET", cleaned)

    def test_log_text_drops_secrets(self):
        cleaned = publish.sanitize_text(
            "fatal: https://x-access-token:SECRET@github.com/faultymushr00ms/leadgen.git"
        )
        self.assertNotIn("SECRET", cleaned)
        self.assertIn("github.com/faultymushr00ms/leadgen.git", cleaned)

    def test_local_paths_are_unchanged(self):
        self.assertEqual(publish.sanitize_origin("/tmp/origin.git"), "/tmp/origin.git")

    def test_resolve_origin_strips_userinfo_from_the_project_remote(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()
            git(project, "init", "-b", "main")
            git(project, "remote", "add", "origin",
                "https://x-access-token:SECRET@github.com/faultymushr00ms/leadgen.git")
            resolved = publish.resolve_origin(str(project))
            self.assertEqual(resolved, "https://github.com/faultymushr00ms/leadgen.git")
            self.assertNotIn("SECRET", resolved)


class PublishFlowTests(unittest.TestCase):
    def _project(self, tmp):
        project = Path(tmp) / "project"
        project.mkdir()
        git(project, "init", "-b", "main")
        (project / "README.md").write_text("source\n", encoding="utf-8")
        git(project, "add", "README.md")
        git(project, "config", "user.email", "test@example.com")
        git(project, "config", "user.name", "Test")
        git(project, "commit", "-m", "init")
        return project

    def test_push_to_reports_branch_leaves_the_project_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self._project(tmp)
            before = git(project, "rev-parse", "HEAD").stdout.strip()
            bare = Path(tmp) / "origin.git"
            subprocess.check_call(["git", "init", "--bare", "-b", "main", str(bare)])
            reports = Path(tmp) / "reports"
            reports.mkdir()
            (reports / "audit_2026-10-23.md").write_text("# audit\n", encoding="utf-8")
            (reports / "audit_2026-10-23.json").write_text("{}\n", encoding="utf-8")
            (reports / "scan_2026-10-23.md").write_text("# scan\n", encoding="utf-8")
            (reports / "notes.txt").write_text("do not publish\n", encoding="utf-8")
            dest = Path(tmp) / "home" / ".forge-reports"
            code = publish.publish(
                str(project), str(reports), str(dest), str(bare), "2026-10-23",
            )
            self.assertEqual(code, 0, "publish failed")
            self.assertEqual(git(project, "rev-parse", "HEAD").stdout.strip(), before)
            self.assertEqual(git(project, "status", "--porcelain").stdout, "")
            self.assertNotIn("reports", git(project, "branch", "--list").stdout)
            check = Path(tmp) / "check"
            subprocess.check_call([
                "git", "clone", "--branch", "reports", str(bare), str(check),
            ])
            published = check / "data" / "reports"
            self.assertTrue((published / "audit_2026-10-23.md").is_file())
            self.assertTrue((published / "audit_2026-10-23.json").is_file())
            self.assertTrue((published / "scan_2026-10-23.md").is_file())
            self.assertFalse((published / "notes.txt").exists())
            latest = (published / "latest.md").read_text(encoding="utf-8")
            self.assertIn("audit_2026-10-23.md", latest)
            self.assertIn("scan_2026-10-23.md", latest)
            self.assertIn("data/reports/latest.md", (check / "README.md").read_text(encoding="utf-8"))
            stored_remote = git(dest, "remote", "get-url", "origin").stdout
            self.assertNotIn("SECRET", stored_remote)

            (reports / "audit_2026-10-23.md").unlink()
            (reports / "audit_2026-10-23.json").unlink()
            (reports / "scan_2026-10-23.md").unlink()
            (reports / "audit_2026-10-24.md").write_text("# next\n", encoding="utf-8")
            code = publish.publish(
                str(project), str(reports), str(dest), str(bare), "2026-10-24",
            )
            self.assertEqual(code, 0, "second publish failed")
            check2 = Path(tmp) / "check2"
            subprocess.check_call([
                "git", "clone", "--branch", "reports", str(bare), str(check2),
            ])
            published2 = check2 / "data" / "reports"
            self.assertTrue((published2 / "audit_2026-10-23.md").is_file())
            self.assertTrue((published2 / "audit_2026-10-24.md").is_file())
            self.assertEqual(git(project, "rev-parse", "HEAD").stdout.strip(), before)

    def test_push_failure_is_logged_and_does_not_raise(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self._project(tmp)
            reports = Path(tmp) / "reports"
            reports.mkdir()
            (reports / "scan_2026-10-23.md").write_text("# scan\n", encoding="utf-8")
            dest = Path(tmp) / "home" / ".forge-reports"
            missing = Path(tmp) / "missing.git"
            buf = StringIO()
            with redirect_stdout(buf):
                code = publish.publish(
                    str(project), str(reports), str(dest), str(missing), "2026-10-23",
                )
            self.assertEqual(code, 1)
            self.assertIn("FAILED", buf.getvalue())
            self.assertEqual(git(project, "status", "--porcelain").stdout, "")

    def test_refuses_to_publish_inside_the_project_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self._project(tmp)
            before = git(project, "rev-parse", "HEAD").stdout.strip()
            reports = Path(tmp) / "reports"
            reports.mkdir()
            (reports / "scan_2026-10-23.md").write_text("# scan\n", encoding="utf-8")
            code = publish.publish(
                str(project),
                str(reports),
                str(project / "data" / "reports"),
                str(Path(tmp) / "origin.git"),
                "2026-10-23",
            )
            self.assertEqual(code, 1)
            self.assertEqual(git(project, "rev-parse", "HEAD").stdout.strip(), before)
            self.assertFalse((project / "data").exists())


if __name__ == "__main__":
    unittest.main()
