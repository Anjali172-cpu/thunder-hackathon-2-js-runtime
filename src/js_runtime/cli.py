"""Command-line interface for the JavaScript runtime."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .engine import JavaScriptExecutionError, JavaScriptRuntime


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="pyjs",
        description="Execute JavaScript from a file or stdin using Python and QuickJS.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Path to a JavaScript file. If omitted, JavaScript is read from stdin.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Maximum execution time in seconds. Default: 5.",
    )
    parser.add_argument(
        "--memory",
        type=int,
        default=64,
        help="Maximum QuickJS heap memory in megabytes. Default: 64.",
    )
    parser.add_argument(
    "--version",
    action="version",
    version="pyjs 1.0.0",
    )
    return parser


def read_source(file_name: str | None) -> str:
    """Read JavaScript source code from a file or stdin."""
    if file_name is None:
        return sys.stdin.read()

    path = Path(file_name)
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise JavaScriptExecutionError(f"Could not read {path}: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        source = read_source(args.file)
        runtime = JavaScriptRuntime(
            timeout_seconds=args.timeout,
            memory_limit_mb=args.memory,
        )
        output = runtime.execute(source, filename=args.file or "<stdin>")
    except JavaScriptExecutionError as exc:
        print(f"JavaScriptRuntimeError: {exc}", file=sys.stderr)
        return 1

    if runtime.has_output:
        sys.stdout.write(output)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
