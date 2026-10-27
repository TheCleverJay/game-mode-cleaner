"""Parse user exclusions (keep-alive) and optional custom target lists."""

from __future__ import annotations

from pathlib import Path


def _norm(name: str) -> str:
    s = name.strip()
    if not s or s.startswith("#"):
        return ""
    # strip inline comments
    if "#" in s:
        s = s.split("#", 1)[0].strip()
    if not s:
        return ""
    # basename only for paths
    s = s.replace("\\", "/").split("/")[-1]
    return s.lower()


def parse_name_list(items: list[str] | None) -> set[str]:
    out: set[str] = set()
    for item in items or []:
        n = _norm(item)
        if n:
            out.add(n)
    return out


def load_name_file(path: str | Path | None) -> set[str]:
    if not path:
        return set()
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"name list file not found: {p}")
    out: set[str] = set()
    for line in p.read_text(encoding="utf-8").splitlines():
        n = _norm(line)
        if n:
            out.add(n)
    return out


def merge_exclusions(
    *,
    cli_excludes: list[str] | None = None,
    exclude_file: str | Path | None = None,
    built_in_never_kill: set[str] | None = None,
) -> set[str]:
    """Union of hard never-kill + file + CLI excludes. Never empty of never-kill."""
    merged = set(built_in_never_kill or set())
    merged |= load_name_file(exclude_file)
    merged |= parse_name_list(cli_excludes)
    return merged
