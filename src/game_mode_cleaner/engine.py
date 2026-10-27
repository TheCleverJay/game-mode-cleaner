"""Match running processes against interrupter catalog with never-kill + exclusions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

from . import catalog
from .exclusions import load_name_file, merge_exclusions, parse_name_list
from .process_info import ProcInfo, format_bytes, name_key, total_rss


@dataclass
class TargetHit:
    pid: int
    name: str
    rss_bytes: int
    reason: str  # group or "custom-target"


@dataclass
class Plan:
    preset: str
    dry_run: bool
    protected: set[str]
    interrupter_keys: set[str]
    targets: list[TargetHit] = field(default_factory=list)
    skipped_protected: list[ProcInfo] = field(default_factory=list)
    total_rss_before: int = 0
    estimated_freeable_rss: int = 0

    def summary_lines(self) -> list[str]:
        lines = [
            f"preset={self.preset}  dry_run={self.dry_run}  "
            f"candidates={len(self.targets)}  "
            f"protected_names={len(self.protected)}",
            f"process_rss_seen={format_bytes(self.total_rss_before)}  "
            f"est_freeable_if_stopped={format_bytes(self.estimated_freeable_rss)}",
            "note: Estimates are sum of matched working sets; OS may reclaim less/more. "
            "This tool quiets processes — it does not promise higher FPS.",
        ]
        if self.targets:
            lines.append("targets:")
            for t in sorted(self.targets, key=lambda x: (-x.rss_bytes, x.name.lower(), x.pid)):
                lines.append(
                    f"  pid={t.pid:<7} rss={format_bytes(t.rss_bytes):>10}  "
                    f"{t.name}  [{t.reason}]"
                )
        else:
            lines.append("targets: (none)")
        if self.skipped_protected:
            lines.append(f"skipped_as_protected: {len(self.skipped_protected)} process(es)")
        return lines


def build_interrupter_set(
    preset: str,
    *,
    targets_file: str | None = None,
    extra_targets: list[str] | None = None,
) -> set[str]:
    if preset == "custom":
        keys = set()
    else:
        groups = catalog.preset_group_names(preset)
        keys = catalog.interrupter_names_for_groups(groups)
    keys |= load_name_file(targets_file) if targets_file else set()
    keys |= parse_name_list(extra_targets)
    # never allow never-kill into interrupter set even if listed in custom targets
    keys -= catalog.never_kill_names()
    return keys


def plan_actions(
    processes: Sequence[ProcInfo],
    *,
    preset: str = "light",
    exclude: list[str] | None = None,
    exclude_file: str | None = None,
    targets_file: str | None = None,
    extra_targets: list[str] | None = None,
    dry_run: bool = True,
) -> Plan:
    protected = merge_exclusions(
        cli_excludes=exclude,
        exclude_file=exclude_file,
        built_in_never_kill=catalog.never_kill_names(),
    )
    interrupters = build_interrupter_set(
        preset, targets_file=targets_file, extra_targets=extra_targets
    )
    plan = Plan(
        preset=preset,
        dry_run=dry_run,
        protected=protected,
        interrupter_keys=interrupters,
        total_rss_before=total_rss(processes),
    )
    if not interrupters:
        return plan

    # reason lookup: which group owns a name
    reason_map = _group_reason_map()
    seen_skip: set[int] = set()

    for proc in processes:
        key = proc.name_key
        if key in protected:
            if key in interrupters and proc.pid not in seen_skip:
                plan.skipped_protected.append(proc)
                seen_skip.add(proc.pid)
            continue
        if key not in interrupters:
            continue
        reason = reason_map.get(key, "custom-target")
        plan.targets.append(
            TargetHit(pid=proc.pid, name=proc.name, rss_bytes=proc.rss_bytes, reason=reason)
        )
        plan.estimated_freeable_rss += max(0, proc.rss_bytes)
    return plan


def _group_reason_map() -> dict[str, str]:
    cat = catalog.load_catalog()
    out: dict[str, str] = {}
    for gname, gmeta in (cat.get("groups") or {}).items():
        for n in gmeta.get("names") or []:
            out[name_key(n)] = gname
    return out


def apply_plan_posix_sigterm(plan: Plan) -> list[str]:
    """Secondary Linux helper: SIGTERM matching PIDs. Refuses if dry_run.

    Windows apply must use scripts/GameModeCleaner.ps1.
    """
    import os
    import signal

    if plan.dry_run:
        return ["refused: dry_run=True; pass --apply to stop matched processes"]
    messages: list[str] = []
    for t in plan.targets:
        try:
            os.kill(t.pid, signal.SIGTERM)
            messages.append(f"SIGTERM sent to pid={t.pid} ({t.name})")
        except ProcessLookupError:
            messages.append(f"pid={t.pid} already gone")
        except PermissionError:
            messages.append(f"permission denied for pid={t.pid} ({t.name})")
        except OSError as exc:
            messages.append(f"failed pid={t.pid}: {exc}")
    return messages


def restore_hint_lines(names: Iterable[str]) -> list[str]:
    hints = catalog.restore_hints()
    lines: list[str] = []
    for n in sorted({name_key(x) for x in names}):
        tip = hints.get(n)
        if tip:
            lines.append(f"  {n}: {tip}")
        else:
            lines.append(f"  {n}: relaunch from Start Menu / your usual shortcut")
    return lines
