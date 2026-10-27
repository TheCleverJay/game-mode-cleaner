#!/usr/bin/env python3
"""Unit + edge tests for game-mode-cleaner (stdlib unittest, mock processes)."""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from game_mode_cleaner import __version__  # noqa: E402
from game_mode_cleaner import catalog  # noqa: E402
from game_mode_cleaner.cli import main  # noqa: E402
from game_mode_cleaner.engine import build_interrupter_set, plan_actions, restore_hint_lines  # noqa: E402
from game_mode_cleaner.exclusions import load_name_file, merge_exclusions, parse_name_list  # noqa: E402
from game_mode_cleaner.process_info import mock_processes, name_key  # noqa: E402


class TestCatalog(unittest.TestCase):
    def test_version(self):
        self.assertEqual(__version__, "0.1.0")

    def test_never_kill_has_criticals(self):
        nk = catalog.never_kill_names()
        for must in ("csrss.exe", "lsass.exe", "services.exe", "msmpeng.exe", "explorer.exe"):
            self.assertIn(must, nk)

    def test_presets(self):
        presets = catalog.list_presets()
        self.assertIn("light", presets)
        self.assertIn("aggressive", presets)
        self.assertIn("custom", presets)
        light = catalog.interrupter_names_for_groups(catalog.preset_group_names("light"))
        aggr = catalog.interrupter_names_for_groups(catalog.preset_group_names("aggressive"))
        self.assertTrue(light)
        self.assertTrue(light.issubset(aggr))
        self.assertEqual(catalog.preset_group_names("custom"), [])

    def test_unknown_preset(self):
        with self.assertRaises(ValueError):
            catalog.preset_group_names("nope")


class TestExclusions(unittest.TestCase):
    def test_parse_comments_and_paths(self):
        got = parse_name_list(
            [
                "# comment",
                "Discord.exe  # keep voice",
                r"C:\Program Files\Google\Chrome\chrome.exe",
                "  ",
            ]
        )
        self.assertEqual(got, {"discord.exe", "chrome.exe"})

    def test_load_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as fh:
            fh.write("# keep\nOneDrive.exe\nsteam\n")
            path = fh.name
        try:
            got = load_name_file(path)
            self.assertEqual(got, {"onedrive.exe", "steam"})
        finally:
            Path(path).unlink(missing_ok=True)

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_name_file("/tmp/game-mode-cleaner-missing-exclusions-xyz.txt")

    def test_merge_includes_never_kill(self):
        merged = merge_exclusions(
            cli_excludes=["notepad.exe"],
            built_in_never_kill={"csrss.exe"},
        )
        self.assertIn("csrss.exe", merged)
        self.assertIn("notepad.exe", merged)


class TestEngine(unittest.TestCase):
    def test_dry_run_targets_mock(self):
        procs = mock_processes()
        plan = plan_actions(procs, preset="light", dry_run=True)
        names = {t.name.lower() for t in plan.targets}
        self.assertTrue(plan.dry_run)
        self.assertIn("chrome.exe", names)
        self.assertIn("onedrive.exe", names)
        self.assertIn("icue.exe", names)
        # never-kill must not appear
        for t in plan.targets:
            self.assertNotIn(name_key(t.name), catalog.never_kill_names())

    def test_exclude_removes_target(self):
        procs = mock_processes()
        plan = plan_actions(
            procs, preset="light", exclude=["chrome.exe", "OneDrive.exe"], dry_run=True
        )
        names = {name_key(t.name) for t in plan.targets}
        self.assertNotIn("chrome.exe", names)
        self.assertNotIn("onedrive.exe", names)
        self.assertTrue(any(name_key(p.name) == "chrome.exe" for p in plan.skipped_protected))

    def test_exclude_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as fh:
            fh.write("Discord.exe\n")
            path = fh.name
        try:
            plan = plan_actions(
                mock_processes(),
                preset="aggressive",
                exclude_file=path,
                dry_run=True,
            )
            names = {name_key(t.name) for t in plan.targets}
            self.assertNotIn("discord.exe", names)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_custom_preset_empty_without_targets(self):
        plan = plan_actions(mock_processes(), preset="custom", dry_run=True)
        self.assertEqual(plan.targets, [])

    def test_custom_with_targets_still_respects_never_kill(self):
        keys = build_interrupter_set(
            "custom", extra_targets=["csrss.exe", "chrome.exe"]
        )
        self.assertNotIn("csrss.exe", keys)
        self.assertIn("chrome.exe", keys)

    def test_aggressive_includes_discord(self):
        plan = plan_actions(mock_processes(), preset="aggressive", dry_run=True)
        names = {name_key(t.name) for t in plan.targets}
        self.assertIn("discord.exe", names)
        self.assertIn("searchindexer.exe", names)

    def test_restore_hints(self):
        lines = restore_hint_lines(["chrome.exe", "no-such-app.exe"])
        self.assertTrue(any("chrome" in x for x in lines))
        self.assertTrue(any("no-such-app" in x for x in lines))

    def test_never_kill_process_not_targeted_even_if_named_like_interrupter(self):
        # explorer is never-kill; ensure skipped
        procs = mock_processes()
        plan = plan_actions(procs, preset="aggressive", dry_run=True)
        for t in plan.targets:
            self.assertNotEqual(name_key(t.name), "explorer.exe")
            self.assertNotEqual(name_key(t.name), "msmpeng.exe")


class TestCLI(unittest.TestCase):
    def test_help(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            with self.assertRaises(SystemExit) as ctx:
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_version(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            with self.assertRaises(SystemExit) as ctx:
                main(["--version"])
        self.assertEqual(ctx.exception.code, 0)
        self.assertIn("0.1.0", buf.getvalue())

    def test_mock_dry_run(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["--source", "mock", "--lang", "zh"])
        self.assertEqual(code, 0)
        self.assertIn("预览", buf.getvalue())

    def test_json_out(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["--source", "mock", "--json", "--preset", "light"])
        self.assertEqual(code, 0)
        data = json.loads(buf.getvalue())
        self.assertEqual(data["version"], "0.1.0")
        self.assertTrue(data["dry_run"])
        self.assertIsInstance(data["targets"], list)
        self.assertGreater(len(data["targets"]), 0)

    def test_list_restore_hint(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["--restore-hint"])
        self.assertEqual(code, 0)
        self.assertIn("chrome", buf.getvalue().lower())

    def test_bad_exclude_file(self):
        err = io.StringIO()
        with redirect_stderr(err):
            code = main(["--source", "mock", "--exclude-file", "/tmp/gmc-nope-12345.txt"])
        self.assertEqual(code, 2)

    def test_export_catalog(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "catalog.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main(["--export-catalog", str(dest)])
            self.assertEqual(code, 0)
            self.assertTrue(dest.is_file())
            data = json.loads(dest.read_text(encoding="utf-8"))
            self.assertIn("never_kill", data)


class TestPackagingSurface(unittest.TestCase):
    def test_maturity_files(self):
        for name in (
            "LICENSE",
            "SECURITY.md",
            "CONTRIBUTING.md",
            "CONTRIBUTING.zh-CN.md",
            "CHANGELOG.md",
            "CODE_OF_CONDUCT.md",
            "README.md",
            "README.zh-CN.md",
            ".gitignore",
            "exclusions.txt",
            "GameMode-Preview.bat",
            "GameMode-Apply.bat",
            "scripts/GameModeCleaner.ps1",
            "docs/zh/exclusions.md",
            "docs/en/exclusions.md",
            "docs/zh/safety.md",
            "docs/en/safety.md",
        ):
            self.assertTrue((ROOT / name).is_file(), msg=f"missing {name}")

    def test_readme_zh_has_three_steps_no_star_bait(self):
        text = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        self.assertIn("三步走", text)
        self.assertIn("exclusions.txt", text)
        self.assertIn("GameMode-Preview.bat", text)
        self.assertNotIn("为什么值得 star", text)
        self.assertNotIn("Why star", text)

    def test_readme_en_no_star_bait(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Three steps", text)
        low = text.lower()
        self.assertNotIn("why star this", low)
        self.assertNotIn("why star", low)


if __name__ == "__main__":
    unittest.main()
