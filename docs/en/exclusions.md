# Exclusions tutorial

Goal: tell the cleaner which processes to **keep**.

## Where is the file?

`exclusions.txt` at the repo root (Notepad is fine).  
You can also copy `examples/exclusions.example.txt`.

## Format

- **One process name per line**  
- `#` starts a comment  
- `Discord.exe` or `Discord` both work  
- Full paths are reduced to the basename  

Example:

```
# keep voice chat
Discord.exe

# keep a browser for guides
chrome.exe

# game binary if it was ever matched by mistake
HollowKnight.exe
```

## How to find the name

1. Open Task Manager (`Ctrl+Shift+Esc`)  
2. Open the **Details** tab  
3. Copy the **Name** column into `exclusions.txt`  
4. Save  
5. Run `GameMode-Preview.bat` again and confirm it is no longer listed  

## Relation to never-kill

A hard-coded never-kill list always applies (system critical, Defender cores, …).  
Your exclusions are **merged** with it: either side protects the process.

## CLI equivalents

```bash
game-mode-cleaner --source mock --exclude-file exclusions.txt --exclude notepad.exe
```

```powershell
.\scripts\GameModeCleaner.ps1 -ExcludeFile .\exclusions.txt -Exclude notepad.exe
```
