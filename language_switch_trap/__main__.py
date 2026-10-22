"""CLI: python -m language_switch_trap transcripts/*.jsonl"""

from __future__ import annotations

import sys
from pathlib import Path

from language_switch_trap.score import format_details, format_table, score_path

_FLAGS = {"--verbose", "--help", "-h"}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    unknown = [arg for arg in args if arg.startswith("-") and arg not in _FLAGS]
    if unknown:
        print(f"unknown flag: {unknown[0]}", file=sys.stderr)
        print(_usage(), file=sys.stderr)
        return 2
    verbose = "--verbose" in args
    paths = [arg for arg in args if arg not in _FLAGS]
    if not paths or "--help" in args or "-h" in args:
        print(_usage(), file=sys.stderr if not paths else sys.stdout)
        return 2 if not paths else 0
    try:
        reports = [score_path(Path(path)) for path in paths]
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(format_table(reports))
    if verbose:
        print()
        print(format_details(reports))
    return 0


def _usage() -> str:
    return "usage: python -m language_switch_trap [--verbose] <journey.jsonl>..."


if __name__ == "__main__":
    raise SystemExit(main())
