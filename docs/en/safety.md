# Safety and limits

## Safe defaults

- Default is **preview**: print targets only; do not stop processes.  
- `GameMode-Apply.bat` asks you to type `Y` once before applying.  
- Never-kill is hard-coded; exclusions cannot force-kill those names.  
- Prefer stopping the current user’s processes; admin is usually not required.  

## Explicitly out of scope

- No file deletion, disk wipe, or ransomware behavior  
- No permanent Windows Defender / Security Center disable  
- No malware-like registry writes or persistence implants  
- No undocumented standby-list flushes (this release is process quieting only)  
- No trading, broker, or MiniQMT code  

## Honest expectations

- Helps low-spec PCs by cutting background RAM/CPU contention.  
- Does **not** guarantee FPS or AAA smoothness.  
- “Freeable” figures sum matched working sets; the OS may reclaim less or more.  

## Privileges

Access-denied on some processes is normal (system / other sessions). Skip them; do not disable antivirus to force kills.

## Reporting

Security issues → **hanabot@mail.grokbot.com** (see [SECURITY.md](../../SECURITY.md)). Do not file public exploit details.
