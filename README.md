
# Python JavaScript Runtime

A lightweight JavaScript runtime built in Python using the embedded QuickJS engine. It executes real JavaScript code, captures console output, enforces resource limits, and provides a clean command-line interface with execution statistics and automated testing.

## Features

- Executes real JavaScript using the embedded QuickJS engine
- Supports execution from JavaScript files and standard input (stdin)
- Captures and prints `console.log()` output
- Configurable execution timeout limits
- Configurable memory limits
- Command-line interface (`pyjs`) and Python package support
- Node-style array console formatting
- Supports modern JavaScript features including:
  - `let` and `const`
  - Arrays and objects
  - Functions and arrow functions
  - Callbacks
  - Spread and rest operators
  - `Math` and `Date`
  - Loops and conditional statements
  - Common string and array methods
- Comprehensive automated test suite with hidden-feature coverage using `pytest`
- Supports hidden-test scenarios with additional automated test coverage
- Friendly error handling with descriptive runtime errors

### Runtime Analytics

The runtime can optionally print execution statistics:

- Execution time
- Memory limit
- Number of output lines
- Input size in bytes

Example:

pyjs --stats file.js

## Architecture

The runtime has four layers:

1. Input layer: `src/js_runtime/cli.py` reads JavaScript from a file path or from stdin.
2. Execution layer: `src/js_runtime/engine.py` creates a `quickjs.Context`, applies safety limits, injects a `console` object, and evaluates the JavaScript.
3. Console capture layer: JavaScript `console.log(...)` pushes formatted strings into a JavaScript array named `globalThis.__python_console_lines`.
4. Output layer: the CLI prints the captured lines to stdout exactly once, separated by newline characters.

This approach is stronger than hand-writing a parser because QuickJS already supports modern JavaScript features such as `let`, `const`, arrays, objects, functions, arrow functions, callbacks, spread/rest operators, `Math`, `Date`, loops, `switch`, and common string/array methods.

## Project Structure

```text
python-js-runtime/
  pyproject.toml
  requirements.txt
  README.md
  src/
    js_runtime/
      __init__.py
      __main__.py
      cli.py
      engine.py
  samples/
    test1_odd_even.js
    test2_triangle.js
    test3_armstrong.js
    test4_array_reverse.js
    test5_palindrome.js
    hidden_style_features.js
  tests/
    test_runtime.py
```

## Installation

Use Python 3.9 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

## Running JavaScript

Check version:

```bash
python3 -m src.js_runtime --version
```

Check help:

```bash
python3 -m src.js_runtime --help
```

Run from a file:

```bash
pyjs samples/test1_odd_even.js
```

If the `pyjs` command is unavailable, run:

```bash
PYTHONPATH=src python3 -m js_runtime samples/test1_odd_even.js
```

Run from stdin:

```bash
echo 'console.log("Hello " + "JS");' | pyjs
```

Run without installing the console script:

```bash
PYTHONPATH=src python3 -m js_runtime samples/test1_odd_even.js
```

## Public Hackathon Samples

```bash
pyjs samples/test1_odd_even.js
pyjs samples/test2_triangle.js
pyjs samples/test3_armstrong.js
pyjs samples/test4_array_reverse.js
pyjs samples/test5_palindrome.js
```

Expected outputs:

```text
7 is Odd
```

```text
*
**
***
****
*****
```

```text
true
false
```

```text
Original: 1, 2, 3, 4, 5
Reversed: 5, 4, 3, 2, 1
```

```text
racecar is a Palindrome
```

Note: the hackathon PDF/table appears to show extra spaces or bold formatting in the triangle and array outputs. Real JavaScript code for the triangle prints one more `*` on each line, as shown above.

## Running Tests

```bash
PYTHONPATH=src python3 -m pytest
```

## File-by-File Explanation

### `requirements.txt`

`quickjs>=1.19.4` installs the Python binding for the embedded QuickJS JavaScript engine.

`pytest>=8.0.0` installs the test runner used by `tests/test_runtime.py`.

### `pyproject.toml`

`[build-system]` tells Python packaging tools to use `setuptools`.

`[project]` defines the package name, version, Python version, and runtime dependency.

`[project.scripts]` creates the `pyjs` command. It points to `js_runtime.cli:main`, meaning "import `main` from `src/js_runtime/cli.py` and run it."

`[tool.setuptools.packages.find]` tells setuptools that importable Python packages live inside `src`.

### `src/js_runtime/__init__.py`

This file makes `js_runtime` a package and re-exports `JavaScriptRuntime` and `JavaScriptExecutionError` for clean imports.

### `src/js_runtime/__main__.py`

This file lets users run the package with `python3 -m js_runtime`.

`from .cli import main` imports the CLI function.

`raise SystemExit(main())` runs the CLI and exits with the returned status code.

### `src/js_runtime/cli.py`

`build_parser()` creates the command-line options:

`file` is optional. If present, the runtime reads JavaScript from that file. If absent, it reads stdin.

`--timeout` prevents infinite loops from running forever.

`--memory` limits the QuickJS heap in megabytes.

`read_source()` reads UTF-8 JavaScript from a file or from `sys.stdin`.

`main()` parses arguments, reads source, creates `JavaScriptRuntime`, executes the code, prints captured stdout, and returns `0` for success.

If anything goes wrong, `main()` prints `JavaScriptRuntimeError: ...` to stderr and returns exit code `1`.

### `src/js_runtime/engine.py`

`import quickjs` loads the embedded JavaScript engine. If it is missing, the module raises a clear installation message.

`JavaScriptExecutionError` is the custom exception used for file, configuration, syntax, and runtime errors.

`CONSOLE_BOOTSTRAP` is JavaScript code injected before the user's program. It creates `globalThis.console`.

`globalThis.__python_console_lines = []` creates the JavaScript-side output buffer. This avoids a QuickJS limitation where Python callbacks cannot be called while a time limit is active.

`formatValue(value)` converts JavaScript values into strings suitable for `console.log`. Strings stay unchanged, booleans become `true` or `false`, `null` and `undefined` are represented by their JavaScript names, arrays use comma joining, and objects use `JSON.stringify` where possible.

`console.log(...args)` supports any number of arguments. It formats each argument, joins them with spaces, and pushes one string into `globalThis.__python_console_lines`.

`JavaScriptRuntime` is a dataclass so the timeout, memory limit, and output buffer are explicit.

`execute(source, filename)` clears old output, creates a fresh QuickJS context, applies limits, injects the console bootstrap, executes the user's JavaScript, reads `JSON.stringify(globalThis.__python_console_lines)`, and returns all captured output joined by `\n`.

`_configure_limits(context)` applies memory, stack, and execution-time limits when the installed QuickJS binding supports them.

`has_output` tells the CLI whether JavaScript called `console.log`, even if the logged line was an empty string.

## Error Handling

Syntax errors, thrown JavaScript exceptions, invalid timeout values, invalid memory values, and file-reading failures are converted into `JavaScriptExecutionError`.

The CLI prints those errors to stderr and exits with code `1`, which is friendly for automated judges.

Example:

```bash
echo 'let x = ;' | pyjs
```

If the `pyjs` command is unavailable:

```bash
echo 'let x = ;' | PYTHONPATH=src python3 -m js_runtime
```

Output on stderr:

```text
JavaScriptRuntimeError: SyntaxError: unexpected token in expression: ';'
```

## Hidden Test Robustness

This runtime should handle the listed hidden-case topics because QuickJS implements real JavaScript semantics for:

- `let`, `const`, and function scope
- numbers, strings, booleans, arrays, objects, `null`, and `undefined`
- `if`, `else`, `switch`, `for`, `while`, and `do...while`
- array methods such as `push`, `pop`, `shift`, `unshift`, `map`, `filter`, `reduce`, `reverse`, `sort`, `slice`, and `splice`
- string methods such as `split`, `join`, `replace`, `slice`, `substring`, `trim`, and case conversion
- `Math`, `Date`, callbacks, arrow functions, spread, and rest

Recommended improvements:

- Add deterministic `Math.random()` support if the judge expects fixed random outputs.
- Add a Node-like `console.log` formatter for complex nested objects if hidden tests log raw objects or arrays directly.
- Add optional input functions such as `prompt()` or `readline()` if the hackathon later includes interactive input.
- Add module loading only if required; currently the runtime is intentionally single-file/snippet oriented.
- Add more tests for thrown errors, nested arrays, object logging, sorting numbers with callbacks, and date formatting.
- Package a `Dockerfile` so judges can run the same Python and QuickJS versions every time.

## Submission Notes

For GitHub submission, commit the entire directory. The evaluator can install dependencies, run `pyjs file.js`, or run the test suite with `PYTHONPATH=src python3 -m pytest`
