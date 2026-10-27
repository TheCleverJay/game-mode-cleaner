# Contributing to game-mode-cleaner

Thanks for helping. Keep the happy path **double-click simple** for non-technical Windows users.

## Ground rules

- **No secrets** in commits, issues, or samples.
- Runtime Python dependencies stay at **zero** unless strongly discussed.
- Do not add trading execution, broker adapters, MiniQMT/`xtquant`, or live order paths.
- Do not add disk wipes, Defender disable, or undocumented kernel memory tricks.
- Prefer clear Preview/Apply `.bat` UX and tests over long prose.
- Docs are for **outsiders**: install, usage, exclusions, safety — no star-bait sections.

## Dev setup

```bash
git clone https://github.com/TheCleverJay/game-mode-cleaner.git
cd game-mode-cleaner
PYTHONPATH=src python3 tests/test_smoke.py
./scripts/smoke.sh
```

## Pull requests

1. Fork and branch from `main`.
2. Add/adjust tests (happy path + one edge/error). Keep `--source mock` green on Linux.
3. Smoke must print `SMOKE_OK`.
4. Update `CHANGELOG.md` under `[Unreleased]` when user-visible.
5. Keep EN + zh-CN README/docs in sync for user-facing behavior.
6. If you change interrupter names, update `src/game_mode_cleaner/data/catalog.json` (PS1 reads the same file).

## Code style

- Python ≥ 3.10, stdlib-first, type hints welcome.
- No unexplained TODOs on the public surface.
- Dry-run remains the default.

## License

By contributing you agree your work is released under the MIT License.
