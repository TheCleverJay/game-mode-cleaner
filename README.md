# game-mode-cleaner

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](./pyproject.toml)

Quiet background apps that steal RAM/CPU before you launch a game. **Dry-run / preview by default.** Customizable keep-alive exclusions. Primary OS: **Windows** (double-click `.bat`). Linux helper is secondary.

- English · [中文](./README.zh-CN.md)
- License: MIT · Python ≥ 3.10 (optional CLI) · Proposed GitHub: [`TheCleverJay/game-mode-cleaner`](https://github.com/TheCleverJay/game-mode-cleaner)

---

## Three steps (no coding required)

1. **Download** this repo and unzip it anywhere.  
2. **(Optional) Edit exclusions**: open `exclusions.txt` in Notepad and **add process names you want to keep** (one per line, e.g. `Discord.exe`). Lines starting with `#` are comments.  
3. **Double-click**  
   - `GameMode-Preview.bat` — **list only** (safe; do this first)  
   - `GameMode-Apply.bat` — actually stop matches; asks you to type `Y` once  

Then relaunch any app you still need from the Start Menu.

> Honest limit: this reduces background contention on low-spec PCs. It does **not** promise AAA at 60 FPS.

English double-click twins: `GameMode-Preview-EN.bat` / `GameMode-Apply-EN.bat`.

---

## Exclusions

Root file: `exclusions.txt` (also `examples/exclusions.example.txt`).

```
# one process name per line
Discord.exe
chrome.exe
mygame.exe
```

- Task Manager → **Details** → copy the **Name** column.  
- `Discord` or `Discord.exe` both work.  
- Critical system processes are hard-protected even if you omit them.  

Details: [docs/en/exclusions.md](./docs/en/exclusions.md)

---

## What it may stop vs never touches

| May stop (on interrupter list and not excluded) | Never touches |
|---|---|
| Background browsers, cloud sync, RGB overlays, some updaters, chat clients, etc. (by preset) | Hard-coded never-kill: `csrss`, `lsass`, Defender cores, `explorer` by default, … |

Presets: `light` (default) · `aggressive` · `custom` (only names you supply as targets).

Default is preview. Only Apply / `--apply` stops processes. No undocumented standby-list hacks, no permanent Defender disable, no file wipes.

---

## Optional CLI

```bash
pip install -e .
game-mode-cleaner --help

# Mock process table (works on Linux CI)
PYTHONPATH=src python3 -m game_mode_cleaner.cli --source mock --lang en
PYTHONPATH=src python3 -m game_mode_cleaner.cli --source mock --exclude-file exclusions.txt
```

Windows PowerShell:

```powershell
.\scripts\GameModeCleaner.ps1
.\scripts\GameModeCleaner.ps1 -Apply -Lang en
.\scripts\GameModeCleaner.ps1 -Preset aggressive -ExcludeFile .\exclusions.txt
```

---

## Docs

- [docs/en/exclusions.md](./docs/en/exclusions.md) — customize exclusions  
- [docs/en/safety.md](./docs/en/safety.md) — safety & limits  
- [docs/zh/exclusions.md](./docs/zh/exclusions.md) · [docs/zh/safety.md](./docs/zh/safety.md)

## Contributing / security

[CONTRIBUTING.md](./CONTRIBUTING.md) · [中文](./CONTRIBUTING.zh-CN.md)  
[SECURITY.md](./SECURITY.md) · [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) · [CHANGELOG.md](./CHANGELOG.md)

## Out of scope

No disk wipe, ransomware, malware registry, permanent Defender off, trading/broker/MiniQMT code, or FPS guarantees.
