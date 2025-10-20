#!/usr/bin/env python3
r"""
Force PuTTY to use a specific mouse button scheme across ALL saved sessions
by setting the registry value:
  HKCU\Software\SimonTatham\PuTTY\Sessions\<Session>\MouseIsXterm

Values (per PuTTY docs/community references):
  0 = Compromise (Right pastes; Middle extends)
  1 = Xterm      (Right extends; Middle pastes)
  2 = Windows    (Right-click context menu; Paste is a menu item)

Usage:
  python set_putty_mouse_scheme.py --mode xterm --backup --verbose
Options:
  --mode {xterm,compromise,windows}  Which scheme to enforce (default: xterm)
  --dry-run                          Show intended changes without writing
  --backup                           Export PuTTY branch to putty_backup.reg before writing
  --verbose                          Print details
"""

import argparse
import subprocess
import sys
from pathlib import Path

try:
    import winreg  # type: ignore
except ImportError:
    print("This script must be run on Windows (needs 'winreg').", file=sys.stderr)
    sys.exit(1)

SESSIONS_BASE = r"Software\SimonTatham\PuTTY\Sessions"
DEFAULT_KEY   = "Default%20Settings"

MODE_MAP = {
    "compromise": 0,
    "xterm": 1,
    "windows": 2,
}

def open_key(root, path, access=winreg.KEY_READ):
    return winreg.OpenKey(root, path, 0, access)

def enum_subkeys(key):
    i = 0
    while True:
        try:
            name = winreg.EnumKey(key, i)
            yield name
            i += 1
        except OSError:
            break

def export_backup(outfile: Path, verbose: bool):
    cmd = ["reg", "export", r"HKCU\Software\SimonTatham\PuTTY", str(outfile), "/y"]
    if verbose:
        print("Backing up registry with:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True, capture_output=not verbose)
        if verbose:
            print(f"Backup written to: {outfile}")
    except Exception as e:
        print(f"WARNING: backup failed: {e}", file=sys.stderr)

def set_mouse_mode_on_key(sessions_key_path: str, subkey: str, dword_value: int, verbose: bool, dry: bool):
    path = f"{sessions_key_path}\\{subkey}"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE) as k:
            if verbose:
                print(f"[{subkey}] MouseIsXterm = {dword_value}")
            if not dry:
                winreg.SetValueEx(k, "MouseIsXterm", 0, winreg.REG_DWORD, dword_value)
            return True
    except FileNotFoundError:
        return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=list(MODE_MAP.keys()), default="xterm",
                    help="Mouse scheme to enforce (default: xterm)")
    ap.add_argument("--dry-run", action="store_true", help="Show what would change; don't write")
    ap.add_argument("--backup", action="store_true", help="Export PuTTY registry to putty_backup.reg before writing")
    ap.add_argument("--verbose", action="store_true", help="Verbose output")
    args = ap.parse_args()

    val = MODE_MAP[args.mode]

    # Ensure sessions base exists
    try:
        with open_key(winreg.HKEY_CURRENT_USER, SESSIONS_BASE) as base_key:
            pass
    except FileNotFoundError:
        print(f"ERROR: HKCU\\{SESSIONS_BASE} not found. Run PuTTY and save a session first.", file=sys.stderr)
        sys.exit(2)

    if args.backup and not args.dry_run:
        export_backup(Path("putty_backup.reg").resolve(), verbose=args.verbose)

    updated = 0
    with open_key(winreg.HKEY_CURRENT_USER, SESSIONS_BASE) as base_key:
        for sub in enum_subkeys(base_key):
            if not sub:
                continue
            if set_mouse_mode_on_key(SESSIONS_BASE, sub, val, args.verbose, args.dry_run):
                updated += 1

    print(f"Done. Updated MouseIsXterm={val} on {updated} session(s). {'(dry-run)' if args.dry_run else ''}")
    print("Tip: You can also set your preferred mode in 'Default Settings' via PuTTY GUI for new sessions.")

if __name__ == "__main__":
    main()
