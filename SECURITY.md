# Security Policy

## Supported versions

Only the latest `0.x` release line on `main` is supported.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security problems.

Email **hanabot@mail.grokbot.com** with:

- Affected repository and version / commit
- Description and impact
- Steps to reproduce (PoC welcome privately)

We aim to acknowledge within a few business days.

## Scope notes for this project

This tool can **stop user processes** when `-Apply` / `--apply` is used.
Reports especially welcome for:

- Any path that can stop never-kill / system-critical processes
- Any path that deletes user files, changes Defender permanently, or writes malware-like registry keys
- Privilege escalation beyond a clear, documented elevation prompt

## What this project will never ask for

- Production secrets, API keys, private keys, or passwords in issues/PRs
- Live Tailscale IPs, account numbers, or broker credentials in sample data
- Payment addresses or wallet seeds

If you accidentally paste a secret into an issue or PR, rotate it immediately
and tell us so we can scrub logs where possible.
