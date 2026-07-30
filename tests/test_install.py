from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class FreshEyeInstallTests(unittest.TestCase):
    def test_project_install_copies_skill_and_agents(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "install.py"),
                    "--scope",
                    "project",
                    "--project-dir",
                    str(project),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            skill = project / ".agents" / "skills" / "fresheye"
            agents = project / ".codex" / "agents"
            self.assertTrue((skill / "SKILL.md").is_file())
            self.assertTrue((skill / "personas" / "core.yaml").is_file())
            self.assertTrue((agents / "fresheye-runner.toml").is_file())
            self.assertTrue((agents / "fresheye-judge.toml").is_file())

    def test_existing_install_requires_force(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            command = [
                sys.executable,
                str(ROOT / "scripts" / "install.py"),
                "--scope",
                "project",
                "--project-dir",
                str(project),
            ]
            first = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
            second = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("--force", second.stderr)

    def test_doctor_accepts_project_install(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            install = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "install.py"),
                    "--scope",
                    "project",
                    "--project-dir",
                    str(project),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)

            doctor = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "doctor.py"),
                    "--project-dir",
                    str(project),
                    "--json",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(doctor.returncode, 0, doctor.stderr)
            self.assertIn('"runner_found": true', doctor.stdout)
            self.assertIn('"judge_found": true', doctor.stdout)


if __name__ == "__main__":
    unittest.main()
