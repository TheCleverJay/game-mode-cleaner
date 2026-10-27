"""Process snapshot providers: mock (tests), Linux /proc (secondary), Windows (primary via PS)."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class ProcInfo:
    pid: int
    name: str
    rss_bytes: int = 0
    path: str = ""

    @property
    def name_key(self) -> str:
        return name_key(self.name)


def name_key(name: str) -> str:
    s = (name or "").strip().replace("\\", "/").split("/")[-1]
    return s.lower()


def mock_processes(rows: Sequence[tuple[int, str, int]] | None = None) -> list[ProcInfo]:
    """Build a fake process table for dry-run / unit tests.

    Each row: (pid, name, rss_bytes).
    """
    if rows is None:
        rows = [
            (4, "System", 0),
            (100, "csrss.exe", 8_000_000),
            (200, "explorer.exe", 80_000_000),
            (300, "MsMpEng.exe", 200_000_000),
            (400, "chrome.exe", 1_200_000_000),
            (401, "chrome.exe", 900_000_000),
            (402, "chrome_crashpad_handler.exe", 12_000_000),
            (500, "Discord.exe", 450_000_000),
            (600, "OneDrive.exe", 180_000_000),
            (700, "steam.exe", 320_000_000),
            (800, "iCUE.exe", 210_000_000),
            (900, "SearchIndexer.exe", 150_000_000),
            (1000, "EXCEL.EXE", 400_000_000),
            (1100, "mygame.exe", 2_000_000_000),
            (1200, "python3", 40_000_000),
        ]
    return [ProcInfo(pid=p, name=n, rss_bytes=r) for p, n, r in rows]


def linux_processes() -> list[ProcInfo]:
    """Best-effort /proc snapshot (secondary platform; not the primary gaming target)."""
    out: list[ProcInfo] = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        base = f"/proc/{pid}"
        try:
            with open(f"{base}/comm", encoding="utf-8", errors="replace") as fh:
                name = fh.read().strip()
            rss = 0
            with open(f"{base}/status", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if line.startswith("VmRSS:"):
                        parts = line.split()
                        # value in kB
                        rss = int(parts[1]) * 1024
                        break
            out.append(ProcInfo(pid=pid, name=name, rss_bytes=rss))
        except (OSError, ValueError, IndexError, PermissionError):
            continue
    return out


def snapshot(source: str = "auto", mock_rows: Sequence[tuple[int, str, int]] | None = None) -> list[ProcInfo]:
    """Return process list.

    source: auto | mock | linux | empty
    On this Linux box, auto → linux. Windows live terminate is handled by GameModeCleaner.ps1.
    """
    src = (source or "auto").lower()
    if src == "mock":
        return mock_processes(mock_rows)
    if src == "empty":
        return []
    if src == "linux":
        return linux_processes()
    if src == "auto":
        if sys.platform.startswith("linux"):
            return linux_processes()
        if sys.platform.startswith("win"):
            # Python on Windows: light WMI-free fallback via tasklist is fragile;
            # prefer PowerShell script for apply. For list/dry-run we still try mock unless PS used.
            return mock_processes(mock_rows)
        return mock_processes(mock_rows)
    raise ValueError(f"unknown process source {source!r}")


def format_bytes(n: int) -> str:
    if n < 0:
        n = 0
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    val = float(n)
    for u in units:
        if val < 1024.0 or u == units[-1]:
            if u == "B":
                return f"{int(val)} {u}"
            return f"{val:.1f} {u}"
        val /= 1024.0
    return f"{n} B"


def total_rss(procs: Iterable[ProcInfo]) -> int:
    return sum(max(0, p.rss_bytes) for p in procs)
