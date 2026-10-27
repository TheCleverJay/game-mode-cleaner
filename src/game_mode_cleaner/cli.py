"""CLI for game-mode-cleaner. Default is dry-run; Windows happy path uses .bat + PS1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__, catalog
from .engine import apply_plan_posix_sigterm, plan_actions, restore_hint_lines
from .process_info import format_bytes, snapshot, total_rss


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="game-mode-cleaner",
        description=(
            "Quiet background interrupters before gaming. "
            "Dry-run by default. Never kills the hard-coded never-kill list. "
            "Primary OS: Windows (see GameMode-Preview.bat / GameMode-Apply.bat). "
            "Linux helper is secondary."
        ),
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    p.add_argument(
        "--preset",
        choices=sorted(catalog.list_presets()),
        default="light",
        help="light=known hogs; aggressive=broader; custom=only --targets/--targets-file",
    )
    p.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="NAME",
        help="Keep this process name (repeatable). Merged with never-kill + --exclude-file.",
    )
    p.add_argument(
        "--exclude-file",
        metavar="PATH",
        help="Text file: one process name per line (# comments OK).",
    )
    p.add_argument(
        "--targets",
        action="append",
        default=[],
        metavar="NAME",
        help="Extra interrupter names to consider (repeatable).",
    )
    p.add_argument(
        "--targets-file",
        metavar="PATH",
        help="Extra interrupter names file (used alone when --preset custom).",
    )
    p.add_argument(
        "--source",
        choices=["auto", "mock", "linux", "empty"],
        default="auto",
        help="Process list source. mock=demo table (good for CI/Linux box).",
    )
    p.add_argument(
        "--list",
        action="store_true",
        help="List what would be targeted (same as dry-run summary).",
    )
    p.add_argument(
        "--apply",
        action="store_true",
        help="Actually stop matched processes (Linux: SIGTERM). Prefer Windows .bat/PS1.",
    )
    p.add_argument(
        "--restore-hint",
        action="store_true",
        help="Print how to relaunch common apps after a clean.",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Machine-readable plan on stdout.",
    )
    p.add_argument(
        "--export-catalog",
        metavar="PATH",
        help="Write shared catalog JSON copy (for PS1 sync / inspection).",
    )
    p.add_argument(
        "--lang",
        choices=["en", "zh"],
        default="en",
        help="Human message language for banners.",
    )
    return p


def _banner(lang: str, dry_run: bool) -> str:
    if lang == "zh":
        mode = "预览（不会关闭任何程序）" if dry_run else "执行清理（将尝试关闭匹配的程序）"
        return (
            "======== 游戏模式清理 ========\n"
            f"模式: {mode}\n"
            "说明: 只处理干扰项名单里的程序；系统关键进程永远不会动。\n"
            "不会提升到「保证 60 帧」——只是尽量腾出内存/CPU。\n"
            "=============================="
        )
    mode = "PREVIEW (no processes will be stopped)" if dry_run else "APPLY (will try to stop matches)"
    return (
        "======== Game Mode Cleaner ========\n"
        f"Mode: {mode}\n"
        "Only curated interrupters are considered; never-kill list is absolute.\n"
        "Does not promise higher FPS — reduces RAM/CPU contention only.\n"
        "==================================="
    )


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.export_catalog:
        src = Path(__file__).resolve().parent / "data" / "catalog.json"
        dest = Path(args.export_catalog)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"wrote catalog → {dest}")
        return 0

    if args.restore_hint and not args.list and not args.apply and not args.json:
        names = sorted(catalog.restore_hints())
        print("Restore hints:")
        for line in restore_hint_lines(names):
            print(line)
        return 0

    dry_run = not args.apply
    try:
        procs = snapshot(args.source)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        plan = plan_actions(
            procs,
            preset=args.preset,
            exclude=args.exclude,
            exclude_file=args.exclude_file,
            targets_file=args.targets_file,
            extra_targets=args.targets,
            dry_run=dry_run,
        )
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        payload = {
            "version": __version__,
            "preset": plan.preset,
            "dry_run": plan.dry_run,
            "protected_count": len(plan.protected),
            "interrupter_count": len(plan.interrupter_keys),
            "total_rss_before": plan.total_rss_before,
            "estimated_freeable_rss": plan.estimated_freeable_rss,
            "targets": [
                {
                    "pid": t.pid,
                    "name": t.name,
                    "rss_bytes": t.rss_bytes,
                    "reason": t.reason,
                }
                for t in plan.targets
            ],
            "skipped_protected": [
                {"pid": p.pid, "name": p.name, "rss_bytes": p.rss_bytes}
                for p in plan.skipped_protected
            ],
        }
        json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
        print()
        return 0

    print(_banner(args.lang, plan.dry_run))
    print()
    for line in plan.summary_lines():
        print(line)

    if args.restore_hint or (args.apply and plan.targets):
        print()
        print("Restore hints for matched names:")
        for line in restore_hint_lines(t.name for t in plan.targets):
            print(line)

    if args.apply:
        if args.source == "mock":
            print(
                "\nrefused: --apply with --source mock does not kill real processes; "
                "re-run without mock on a real host, or use GameMode-Apply.bat on Windows.",
                file=sys.stderr,
            )
            return 3
        if sys.platform.startswith("win"):
            print(
                "\nnote: On Windows prefer double-click GameMode-Apply.bat "
                "or scripts/GameModeCleaner.ps1 -Apply (same exclusion rules).",
                file=sys.stderr,
            )
            return 3
        before = plan.total_rss_before
        messages = apply_plan_posix_sigterm(plan)
        print()
        for m in messages:
            print(m)
        after = snapshot(args.source)
        print(
            f"\nrough RSS sum before={format_bytes(before)}  "
            f"after_snapshot={format_bytes(total_rss(after))}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
