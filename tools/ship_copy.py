"""
Zip the current project (excluding venv/.git/__pycache__/etc) so you can copy-paste / send it.

LOCAL copy:
  python3 tools/ship_copy.py --dest ~/Desktop

USB example:
  python3 tools/ship_copy.py --dest /media/$USER/USB_NAME

SCP:
  python3 tools/ship_copy.py --dest user@host:/path

Creates: <project>/.artifacts/<project>_YYYYmmdd_HHMMSS.zip
"""
from __future__ import annotations

import argparse
import fnmatch
import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

DEFAULT_EXCLUDES = (
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".DS_Store",
    "Thumbs.db",
    "venv",
    ".venv",
    "node_modules",
    "dist",
    "build",
    ".artifacts",
)


def _is_scp_dest(dest: str) -> bool:
    if ":" not in dest:
        return False
    if os.name == "nt" and len(dest) >= 3 and dest[1] == ":" and dest[2] in ("\\", "/"):
        return False
    return True


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Zip project and copy to local folder or scp to remote.")
    p.add_argument("--src", type=str, default=".", help="Project root (default: .)")
    p.add_argument("--dest", type=str, required=True, help="Local folder OR scp target user@host:/path")
    p.add_argument("--exclude", action="append", default=[], help="Extra exclude pattern (repeatable).")
    p.add_argument("--include-hidden", action="store_true", help="Include dotfiles/dirs.")
    p.add_argument("--keep", type=int, default=10, help="Keep last N zips in .artifacts (default: 10).")
    p.add_argument("--name", type=str, default="", help="Override zip base name (default: folder name).")
    return p.parse_args(argv)


def _norm_patterns(patterns: Iterable[str]) -> Tuple[str, ...]:
    out: List[str] = []
    for pat in patterns:
        pat = pat.strip().strip("/").strip("\\")
        if pat:
            out.append(pat)
    return tuple(out)


def _should_exclude(rel_posix: str, parts: Tuple[str, ...], *, excludes: Tuple[str, ...], include_hidden: bool) -> bool:
    if not include_hidden and any(p.startswith(".") for p in parts):
        return True

    for part in parts:
        if part in excludes:
            return True

    for pat in excludes:
        if any(ch in pat for ch in "*?[]"):
            if fnmatch.fnmatch(rel_posix, pat) or any(fnmatch.fnmatch(p, pat) for p in parts):
                return True

    return False


def _iter_files(src: Path, *, excludes: Tuple[str, ...], include_hidden: bool):
    src = src.resolve()
    for path in src.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(src)
        rel_posix = rel.as_posix()
        parts = tuple(rel.parts)
        if _should_exclude(rel_posix, parts, excludes=excludes, include_hidden=include_hidden):
            continue
        yield path, rel_posix


def _make_zip(src: Path, artifact_dir: Path, base_name: str, *, excludes: Tuple[str, ...], include_hidden: bool) -> Path:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    zip_path = artifact_dir / f"{base_name}_{ts}.zip"

    count = 0
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for abs_path, rel_posix in _iter_files(src, excludes=excludes, include_hidden=include_hidden):
            z.write(abs_path, arcname=rel_posix)
            count += 1

    if count == 0:
        zip_path.unlink(missing_ok=True)
        raise RuntimeError("No files packaged (check excludes / include-hidden).")
    return zip_path


def _prune(artifact_dir: Path, keep: int) -> None:
    if keep <= 0:
        return
    zips = sorted(artifact_dir.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    for p in zips[keep:]:
        try:
            p.unlink()
        except OSError:
            pass


def _copy_local(zip_path: Path, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / zip_path.name
    shutil.copy2(zip_path, target)
    return target


def _copy_scp(zip_path: Path, dest: str) -> None:
    if shutil.which("scp") is None:
        raise RuntimeError("scp not found on PATH.")
    proc = subprocess.run(["scp", str(zip_path), dest], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "scp failed")


def main(argv: Sequence[str]) -> int:
    args = _parse_args(argv)
    src = Path(args.src).resolve()
    if not src.is_dir():
        print(f"ERROR: --src must be a directory: {src}", file=sys.stderr)
        return 2

    excludes = _norm_patterns(DEFAULT_EXCLUDES + tuple(args.exclude))
    artifact_dir = src / ".artifacts"
    base_name = args.name.strip() or src.name

    try:
        zip_path = _make_zip(src, artifact_dir, base_name, excludes=excludes, include_hidden=bool(args.include_hidden))
        _prune(artifact_dir, int(args.keep))

        if _is_scp_dest(args.dest):
            _copy_scp(zip_path, args.dest)
            print(f"OK: {zip_path.name} -> scp:{args.dest}")
        else:
            target = _copy_local(zip_path, Path(args.dest).expanduser())
            print(f"OK: {zip_path.name} -> {target}")

        print(f"Artifact: {zip_path}")
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
