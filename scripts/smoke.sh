#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src
rm -rf src/game_mode_cleaner/__pycache__ tests/__pycache__

python3 -m game_mode_cleaner.cli --help >/dev/null
python3 -m game_mode_cleaner.cli --version | grep -q 0.1.0

# Dry-run demos on mock process table (works on Linux box)
python3 -m game_mode_cleaner.cli --source mock --lang zh | grep -qiE '预览|preview|targets'
python3 -m game_mode_cleaner.cli --source mock --preset light --exclude chrome.exe >/tmp/gmc-ex.txt
grep -qi 'targets' /tmp/gmc-ex.txt
# excluded chrome should not appear as a target line (pid lines only)
! grep -E '^\s+pid=.*chrome\.exe' /tmp/gmc-ex.txt
python3 -m game_mode_cleaner.cli --source mock --json >/tmp/gmc.json
python3 -c 'import json; d=json.load(open("/tmp/gmc.json")); assert d["dry_run"] is True; assert d["targets"]'

python3 -m game_mode_cleaner.cli --restore-hint | grep -qi chrome
python3 -m game_mode_cleaner.cli --export-catalog /tmp/gmc-catalog.json >/dev/null
test -f /tmp/gmc-catalog.json

python3 tests/test_smoke.py -q

# Maturity surface
test -f SECURITY.md && test -f CONTRIBUTING.md && test -f CONTRIBUTING.zh-CN.md
test -f CHANGELOG.md && test -f CODE_OF_CONDUCT.md && test -f .gitignore
test -f README.md && test -f README.zh-CN.md
test -f exclusions.txt && test -f examples/exclusions.example.txt
test -f GameMode-Preview.bat && test -f GameMode-Apply.bat
test -f GameMode-Preview-EN.bat && test -f GameMode-Apply-EN.bat
test -f scripts/GameModeCleaner.ps1
test -f docs/zh/exclusions.md && test -f docs/en/exclusions.md
test -f docs/zh/safety.md && test -f docs/en/safety.md

# Foolproof CN readme
grep -q '三步走' README.zh-CN.md
grep -q '把不想关的程序名加进这个文件' README.zh-CN.md
# No star-bait
! grep -Eiq 'why star|为什么值得[[:space:]]*star|求star|求 star' README.md README.zh-CN.md

# Red lines: no broker / wipe / defender-kill in product code
if grep -RE '^(from|import)[[:space:]].*(xtquant|miniqmt|qmt_consumer|joinquant)' src; then
  echo 'FAIL: banned import' >&2; exit 1
fi
if grep -REi 'BEGIN OPENSSH PRIVATE KEY|YOUR_APTOS_USDT_ADDRESS' src examples; then
  echo 'FAIL: secret/payment leak' >&2; exit 1
fi
if grep -REi 'Format-Volume|cipher\.exe|DisableAntiSpyware|DisableRealtimeMonitoring' src GameMode-*.bat scripts/GameModeCleaner.ps1; then
  echo 'FAIL: dangerous wipe/defender pattern' >&2; exit 1
fi

# Optional: syntax-check PowerShell when pwsh exists
if command -v pwsh >/dev/null 2>&1; then
  pwsh -NoProfile -Command '& { $null = [System.Management.Automation.Language.Parser]::ParseFile("scripts/GameModeCleaner.ps1", [ref]$null, [ref]$errs); if ($errs) { $errs | ForEach-Object { $_.ToString() }; exit 1 } }'
fi

echo SMOKE_OK
