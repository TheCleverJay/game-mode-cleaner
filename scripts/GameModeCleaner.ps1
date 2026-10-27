<#
.SYNOPSIS
  Game Mode Cleaner — quiet background interrupters before gaming (Windows primary).

.DESCRIPTION
  Dry-run by default. Loads the same catalog.json + exclusions.txt rules as the Python CLI.
  Never stops names on the hard-coded never-kill list.
  Does NOT flush standby lists via undocumented APIs (process quieting only).
  Does NOT promise higher FPS.

.PARAMETER Apply
  Actually stop matched user processes (Stop-Process). Default is preview only.

.PARAMETER Preset
  light | aggressive | custom

.PARAMETER ExcludeFile
  Path to exclusions.txt (one process name per line).

.PARAMETER Lang
  en | zh — console banner language.

.EXAMPLE
  .\GameModeCleaner.ps1
  .\GameModeCleaner.ps1 -Apply -Lang zh
  .\GameModeCleaner.ps1 -Preset aggressive -ExcludeFile ..\exclusions.txt
#>
[CmdletBinding()]
param(
  [switch]$Apply,
  [ValidateSet('light','aggressive','custom')]
  [string]$Preset = 'light',
  [string]$ExcludeFile = '',
  [string]$TargetsFile = '',
  [string[]]$Exclude = @(),
  [ValidateSet('en','zh')]
  [string]$Lang = 'zh',
  [switch]$List,
  [switch]$RestoreHint,
  [switch]$Help
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
if (-not $Root) { $Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path }

function Show-Help {
  @"
Game Mode Cleaner (Windows)

Preview (safe, default):
  .\GameModeCleaner.ps1
  .\GameModeCleaner.ps1 -Lang en

Apply (stop matched interrupters):
  .\GameModeCleaner.ps1 -Apply

Presets: light | aggressive | custom
Exclusions file (keep these running):
  default: $Root\exclusions.txt
  one process name per line, # for comments

Never kills: System, csrss, lsass, services, explorer (default), Defender cores, etc.
"@ | Write-Host
}

if ($Help) { Show-Help; exit 0 }

function Get-NormName([string]$name) {
  if ([string]::IsNullOrWhiteSpace($name)) { return '' }
  $s = $name.Trim()
  if ($s.StartsWith('#')) { return '' }
  $hash = $s.IndexOf('#')
  if ($hash -ge 0) { $s = $s.Substring(0, $hash).Trim() }
  if ([string]::IsNullOrWhiteSpace($s)) { return '' }
  $s = ($s -replace '\\','/').Split('/')[-1]
  return $s.ToLowerInvariant()
}

function Read-NameFile([string]$path) {
  $set = New-Object 'System.Collections.Generic.HashSet[string]'
  if ([string]::IsNullOrWhiteSpace($path)) { return $set }
  if (-not (Test-Path -LiteralPath $path)) {
    throw "name list file not found: $path"
  }
  Get-Content -LiteralPath $path -Encoding UTF8 | ForEach-Object {
    $n = Get-NormName $_
    if ($n) { [void]$set.Add($n) }
  }
  return $set
}

$CatalogPath = Join-Path $Root 'src\game_mode_cleaner\data\catalog.json'
if (-not (Test-Path -LiteralPath $CatalogPath)) {
  Write-Error "catalog.json missing at $CatalogPath"
  exit 2
}
$Catalog = Get-Content -LiteralPath $CatalogPath -Raw -Encoding UTF8 | ConvertFrom-Json

$NeverKill = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($n in $Catalog.never_kill) {
  $k = Get-NormName $n
  if ($k) { [void]$NeverKill.Add($k) }
}

$Protected = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($n in $NeverKill) { [void]$Protected.Add($n) }

if ([string]::IsNullOrWhiteSpace($ExcludeFile)) {
  $defaultEx = Join-Path $Root 'exclusions.txt'
  if (Test-Path -LiteralPath $defaultEx) { $ExcludeFile = $defaultEx }
}
if ($ExcludeFile) {
  foreach ($n in (Read-NameFile $ExcludeFile)) { [void]$Protected.Add($n) }
}
foreach ($e in $Exclude) {
  $k = Get-NormName $e
  if ($k) { [void]$Protected.Add($k) }
}

$Interrupters = New-Object 'System.Collections.Generic.HashSet[string]'
$Reason = @{}
if ($Preset -ne 'custom') {
  $groups = @($Catalog.presets.$Preset.groups)
  foreach ($g in $groups) {
    $names = @($Catalog.groups.$g.names)
    foreach ($n in $names) {
      $k = Get-NormName $n
      if ($k -and -not $NeverKill.Contains($k)) {
        [void]$Interrupters.Add($k)
        if (-not $Reason.ContainsKey($k)) { $Reason[$k] = $g }
      }
    }
  }
}
if ($TargetsFile) {
  foreach ($n in (Read-NameFile $TargetsFile)) {
    if (-not $NeverKill.Contains($n)) {
      [void]$Interrupters.Add($n)
      if (-not $Reason.ContainsKey($n)) { $Reason[$n] = 'custom-target' }
    }
  }
}

if ($RestoreHint -and -not $Apply -and -not $List) {
  Write-Host "Restore hints:"
  $Catalog.restore_hints.PSObject.Properties | ForEach-Object {
    Write-Host ("  {0}: {1}" -f $_.Name, $_.Value)
  }
  exit 0
}

function Format-Bytes([long]$n) {
  if ($n -lt 0) { $n = 0 }
  if ($n -lt 1024) { return "$n B" }
  $v = [double]$n
  foreach ($u in @('KiB','MiB','GiB','TiB')) {
    $v = $v / 1024.0
    if ($v -lt 1024 -or $u -eq 'TiB') {
      return ("{0:N1} {1}" -f $v, $u)
    }
  }
  return "$n B"
}

$dry = -not $Apply
if ($Lang -eq 'zh') {
  $mode = if ($dry) { '预览（不会关闭任何程序）' } else { '执行清理（将尝试关闭匹配的程序）' }
  Write-Host '======== 游戏模式清理 ========'
  Write-Host "模式: $mode"
  Write-Host "预设: $Preset"
  Write-Host '说明: 只处理干扰项名单；系统关键进程永远不会动。'
  Write-Host '不会保证更高帧数——只是尽量腾出内存/CPU。'
  Write-Host '=============================='
} else {
  $mode = if ($dry) { 'PREVIEW (nothing will be stopped)' } else { 'APPLY (will try to stop matches)' }
  Write-Host '======== Game Mode Cleaner ========'
  Write-Host "Mode: $mode"
  Write-Host "Preset: $Preset"
  Write-Host 'Only curated interrupters; never-kill list is absolute.'
  Write-Host 'Does not promise higher FPS — RAM/CPU contention only.'
  Write-Host '==================================='
}
Write-Host ''

$procs = Get-Process -ErrorAction SilentlyContinue
$targets = @()
$skipped = 0
$sumRss = 0L
$freeable = 0L
foreach ($p in $procs) {
  try {
    $ws = [long]$p.WorkingSet64
  } catch { $ws = 0L }
  $sumRss += $ws
  $key = Get-NormName $p.ProcessName
  # Get-Process ProcessName usually has no .exe — accept both
  $keyExe = $key
  if (-not $keyExe.EndsWith('.exe')) { $keyExe = "$key.exe" }
  $matchKey = $null
  if ($Interrupters.Contains($key)) { $matchKey = $key }
  elseif ($Interrupters.Contains($keyExe)) { $matchKey = $keyExe }
  if (-not $matchKey) { continue }
  if ($Protected.Contains($key) -or $Protected.Contains($keyExe) -or $Protected.Contains((Get-NormName $p.ProcessName))) {
    $skipped++
    continue
  }
  # also protect if never-kill basename matches
  if ($NeverKill.Contains($key) -or $NeverKill.Contains($keyExe)) {
    $skipped++
    continue
  }
  $reason = 'custom-target'
  if ($Reason.ContainsKey($matchKey)) { $reason = $Reason[$matchKey] }
  $targets += [pscustomobject]@{
    Pid = $p.Id
    Name = $p.ProcessName
    Rss = $ws
    Reason = $reason
    MatchKey = $matchKey
  }
  $freeable += $ws
}

Write-Host ("candidates={0}  protected_names={1}  skipped_as_protected≈{2}" -f $targets.Count, $Protected.Count, $skipped)
Write-Host ("process_rss_seen={0}  est_freeable_if_stopped={1}" -f (Format-Bytes $sumRss), (Format-Bytes $freeable))
Write-Host 'note: Estimates are sum of matched working sets; OS may reclaim less/more.'
Write-Host ''
if ($targets.Count -eq 0) {
  Write-Host 'targets: (none)'
} else {
  Write-Host 'targets:'
  $targets | Sort-Object Rss -Descending | ForEach-Object {
    Write-Host ("  pid={0,-7} rss={1,10}  {2}  [{3}]" -f $_.Pid, (Format-Bytes $_.Rss), $_.Name, $_.Reason)
  }
}

if ($Apply) {
  Write-Host ''
  foreach ($t in $targets) {
    try {
      Stop-Process -Id $t.Pid -Force -ErrorAction Stop
      Write-Host ("stopped pid={0} ({1})" -f $t.Pid, $t.Name)
    } catch {
      Write-Host ("failed pid={0} ({1}): {2}" -f $t.Pid, $t.Name, $_.Exception.Message)
    }
  }
  if ($targets.Count -gt 0) {
    Write-Host ''
    Write-Host 'Restore hints:'
    $hints = $Catalog.restore_hints
    $targets.MatchKey | Select-Object -Unique | ForEach-Object {
      $k = $_
      $prop = $hints.PSObject.Properties | Where-Object { (Get-NormName $_.Name) -eq $k } | Select-Object -First 1
      if ($prop) { Write-Host ("  {0}: {1}" -f $prop.Name, $prop.Value) }
      else { Write-Host ("  {0}: relaunch from Start Menu" -f $k) }
    }
  }
}

exit 0
