"""Core JavaScript execution engine.

The primary language is Python. JavaScript parsing and execution are delegated
to the embedded QuickJS engine through the Python `quickjs` package.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

try:
    import quickjs
except ImportError as exc:  # pragma: no cover - exercised before tests can run.
    raise RuntimeError(
        "The quickjs package is required. Install dependencies with: "
        "python -m pip install -r requirements.txt"
    ) from exc


class JavaScriptExecutionError(Exception):
    """Raised when reading or executing JavaScript fails."""


CONSOLE_BOOTSTRAP = r"""
(function () {
  globalThis.__python_console_lines = [];

  function formatValue(value) {
    if (value === undefined) return "undefined";
    if (value === null) return "null";

  const type = typeof value;

  function formatArrayItem(item) {
    if (item === undefined) return "undefined";
    if (item === null) return "null";
    if (typeof item === "string") return "'" + item + "'";
    return formatValue(item);
  }
    if (type === "string") return value;
    if (type === "number" || type === "bigint") return String(value);
    if (type === "boolean") return value ? "true" : "false";
    if (type === "function") return value.toString();

  if (Array.isArray(value)) {
    return "[ " + value.map(formatArrayItem).join(", ") + " ]";
  }

    try {
      return JSON.stringify(value);
    } catch (error) {
      return String(value);
    }
  }

  globalThis.console = {
    log: function (...args) {
      globalThis.__python_console_lines.push(args.map(formatValue).join(" "));
    },
    error: function (...args) {
      globalThis.__python_console_lines.push(args.map(formatValue).join(" "));
    },
    warn: function (...args) {
      globalThis.__python_console_lines.push(args.map(formatValue).join(" "));
    }
  };
})();
"""


@dataclass
class JavaScriptRuntime:
    """A small, reusable QuickJS-backed runtime."""

    timeout_seconds: float = 5.0
    memory_limit_mb: int = 64
    _output_lines: list[str] = field(default_factory=list, init=False)

    def execute(self, source: str, filename: str = "<input>") -> str:
        """Execute JavaScript source and return captured console output."""
        self._output_lines.clear()
        context = quickjs.Context()
        self._configure_limits(context)

        try:
            context.eval(CONSOLE_BOOTSTRAP)
            context.eval(f"{source}\n//# sourceURL={filename}")
            output_json = context.eval("JSON.stringify(globalThis.__python_console_lines)")
        except quickjs.JSException as exc:
            raise JavaScriptExecutionError(str(exc)) from exc
        except Exception as exc:
            raise JavaScriptExecutionError(f"Unexpected runtime failure: {exc}") from exc

        self._output_lines.extend(json.loads(output_json))
        return "\n".join(self._output_lines)

    @property
    def has_output(self) -> bool:
        """Return True when JavaScript called console at least once."""
        return len(self._output_lines) > 0

    def _configure_limits(self, context: quickjs.Context) -> None:
        """Apply memory, stack, and time limits when supported by quickjs."""
        if self.memory_limit_mb <= 0:
            raise JavaScriptExecutionError("--memory must be greater than 0")
        if self.timeout_seconds <= 0:
            raise JavaScriptExecutionError("--timeout must be greater than 0")

        memory_bytes = self.memory_limit_mb * 1024 * 1024

        if hasattr(context, "set_memory_limit"):
            context.set_memory_limit(memory_bytes)
        if hasattr(context, "set_max_stack_size"):
            context.set_max_stack_size(1024 * 1024)
        if hasattr(context, "set_time_limit"):
            context.set_time_limit(self.timeout_seconds)
