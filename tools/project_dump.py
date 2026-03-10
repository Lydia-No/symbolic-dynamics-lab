from __future__ import annotations

import argparse
import fnmatch
import os
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
    "*.zip",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.pdf",
    "*.mp4",
    "*.mov",
    "*.avi",
)


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Dump a repo into one text file for copy/paste.")
    p.add_argument("--src", type=str, default=".", help="Project root (default: .)")
    p.add_argument("--out", type=str, default="project_dump.txt", help="Output text file path")
    p.add_argument("--include-hidden", action="store_true", help="Include dotfiles/dirs (default: off)")
    p.add_argument("--max-bytes", type=int, default=400_000, help="Max bytes per file (default: 400000).")
    p.add_argument("--exclude", action="append", default=[], help="Extra exclude glob/pattern (repeatable).")
    p.add_argument("--include", action="append", default=[], help="ONLY include paths matching these globs.")
    return p.parse_args(argv)


def _norm_patterns(patterns: Iterable[str]) -> Tuple[str, ...]:
    out: List[str] = []
    for pat in patterns:
        pat = pat.strip().strip("/").strip("\\")
        if pat:
            out.append(pat)
    return tuple(out)


def _match_any_glob(path_posix: str, parts: Tuple[str, ...], globs: Tuple[str, ...]) -> bool:
    for g in globs:
        if fnmatch.fnmatch(path_posix, g):
            return True
        if any(fnmatch.fnmatch(p, g) for p in parts):
            return True
    return False


def _should_exclude(rel_posix: str, parts: Tuple[str, ...], *, excludes: Tuple[str, ...], include_hidden: bool) -> bool:
    if not include_hidden and any(p.startswith(".") for p in parts):
        return True
    if _match_any_glob(rel_posix, parts, excludes):
        return True
    return False


def _iter_files(src: Path, *, excludes: Tuple[str, ...], includes: Tuple[str, ...], include_hidden: bool):
    src = src.resolve()
    for path in sorted(src.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(src)
        rel_posix = rel.as_posix()
        parts = tuple(rel.parts)

        if includes and not _match_any_glob(rel_posix, parts, includes):
            continue
        if _should_exclude(rel_posix, parts, excludes=excludes, include_hidden=include_hidden):
            continue

        yield path, rel_posix


def _read_text_safely(path: Path) -> str:
    data = path.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1", errors="replace")


def main(argv: Sequence[str]) -> int:
    args = _parse_args(argv)
    src = Path(args.src).resolve()
    out = Path(args.out).resolve()

    if not src.is_dir():
        print(f"ERROR: --src must be a directory: {src}")
        return 2

    excludes = _norm_patterns(DEFAULT_EXCLUDES + tuple(args.exclude))
    includes = _norm_patterns(args.include)

    lines: List[str] = []
    lines.append("# PROJECT DUMP")
    lines.append(f"# src: {src}")
    lines.append("")

    included_count = 0
    skipped_count = 0

    for abs_path, rel_posix in _iter_files(
        src,
        excludes=excludes,
        includes=includes,
        include_hidden=bool(args.include_hidden),
    ):
        size = abs_path.stat().st_size
        if size > int(args.max_bytes):
            skipped_count += 1
            lines.append(f"\n\n===== FILE: {rel_posix} =====")
            lines.append(f"[SKIPPED: size {size} bytes > max_bytes {args.max_bytes}]")
            continue

        try:
            text = _read_text_safely(abs_path)
        except OSError as e:
            skipped_count += 1
            lines.append(f"\n\n===== FILE: {rel_posix} =====")
            lines.append(f"[SKIPPED: read error: {e}]")
            continue

        included_count += 1
        lines.append(f"\n\n===== FILE: {rel_posix} =====")
        lines.append(text.rstrip("\n"))
        lines.append("")

    lines.append("\n# SUMMARY")
    lines.append(f"# included_files: {included_count}")
    lines.append(f"# skipped_files: {skipped_count}")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"OK: wrote {out}")
    print(f"Included: {included_count} | Skipped: {skipped_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(os.sys.argv[1:]))
