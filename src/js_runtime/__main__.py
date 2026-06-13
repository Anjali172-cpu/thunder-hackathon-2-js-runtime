"""Allows the package to be run with: python -m js_runtime."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
