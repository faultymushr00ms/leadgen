"""Launchd template and installer for the nightly scan."""

import os
import plistlib
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLIST = ROOT / "scripts" / "com.forge.nightlyscan.plist"
INSTALL = ROOT / "scripts" / "install_schedule.sh"
NIGHTLY = ROOT / "scripts" / "nightly_scan.sh"
MAC_ROOT = "/Users/sky/leadgen/leadgen"


class PlistTests(unittest.TestCase):
    def test_schedule_path_and_path_env(self):
        data = plistlib.loads(PLIST.read_bytes())
        self.assertEqual(data["Label"], "com.forge.nightlyscan")
        self.assertEqual(data["StartCalendarInterval"], {"Hour": 6, "Minute": 30})
        self.assertEqual(data["ProgramArguments"], [
            "/bin/bash",
            f"{MAC_ROOT}/scripts/nightly_scan.sh",
        ])
        self.assertEqual(data["WorkingDirectory"], MAC_ROOT)
        self.assertEqual(data["StandardOutPath"], f"{MAC_ROOT}/logs/launchd_stdout.log")
        self.assertEqual(data["StandardErrorPath"], f"{MAC_ROOT}/logs/launchd_stderr.log")
        path = data["EnvironmentVariables"]["PATH"]
        self.assertIn("/opt/homebrew/bin", path)
        self.assertIn("/usr/local/bin", path)
        self.assertFalse(data["RunAtLoad"])
        text = PLIST.read_text(encoding="utf-8").lower()
        self.assertIn("asleep", text)
        self.assertIn("wakes", text)


class InstallScriptTests(unittest.TestCase):
    def _fake_launchctl(self, bindir, log, bootstrap_code=0, print_code=0):
        fake = bindir / "launchctl"
        fake.write_text(
            "#!/bin/bash\n"
            f'echo "$@" >> "{log}"\n'
            'if [[ "$1" == "bootstrap" ]]; then exit ' + str(bootstrap_code) + '; fi\n'
            'if [[ "$1" == "print" ]]; then exit ' + str(print_code) + '; fi\n'
            'if [[ "$1" == "list" ]]; then echo "123 0 com.forge.nightlyscan"; fi\n'
            "exit 0\n",
            encoding="utf-8",
        )
        fake.chmod(fake.stat().st_mode | stat.S_IEXEC)

    def _run(self, home, bindir, forge_root):
        env = os.environ.copy()
        env["HOME"] = str(home)
        env["PATH"] = str(bindir) + os.pathsep + env.get("PATH", "")
        env["FORGE_ROOT"] = str(forge_root)
        return subprocess.run(
            ["bash", str(INSTALL)],
            env=env,
            capture_output=True,
            text=True,
        )

    def test_bootstrap_and_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            home.mkdir()
            bindir = Path(tmp) / "bin"
            bindir.mkdir()
            log = home / "launchctl.log"
            self._fake_launchctl(bindir, log)
            forge_root = Path(tmp) / "leadgen"
            forge_root.mkdir()
            proc = self._run(home, bindir, forge_root)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            dest = home / "Library" / "LaunchAgents" / "com.forge.nightlyscan.plist"
            data = plistlib.loads(dest.read_bytes())
            self.assertEqual(data["WorkingDirectory"], str(forge_root))
            self.assertTrue((forge_root / "logs").is_dir())
            recorded = log.read_text(encoding="utf-8")
            self.assertIn("bootstrap", recorded)
            self.assertIn("print", recorded)
            self.assertIn("asleep", proc.stdout.lower())

    def test_load_fallback_when_bootstrap_is_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            home.mkdir()
            bindir = Path(tmp) / "bin"
            bindir.mkdir()
            log = home / "launchctl.log"
            self._fake_launchctl(bindir, log, bootstrap_code=1, print_code=1)
            forge_root = Path(tmp) / "leadgen"
            forge_root.mkdir()
            proc = self._run(home, bindir, forge_root)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            recorded = log.read_text(encoding="utf-8")
            self.assertIn("bootstrap", recorded)
            self.assertIn("load", recorded)
            self.assertIn("list", recorded)


class NightlyScriptTests(unittest.TestCase):
    def test_shell_scripts_parse_and_nightly_always_exits_zero(self):
        for script in (NIGHTLY, INSTALL):
            proc = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
        text = NIGHTLY.read_text(encoding="utf-8")
        self.assertIn("scripts/daily_audit.py", text)
        self.assertIn("scripts/publish_reports.py", text)
        self.assertIn('--as-of "$DATE"', text)
        self.assertIn('--date "$DATE"', text)
        lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
        self.assertEqual(lines[-1], "exit 0")


if __name__ == "__main__":
    unittest.main()
