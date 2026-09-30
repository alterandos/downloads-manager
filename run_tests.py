#!/usr/bin/env python
"""
Downloads Manager test runner.

Usage
-----
  python run_tests.py                  run all logic/unit tests (default)
  python run_tests.py logic            logic tests only
  python run_tests.py ui               visual UI tests (interactive, requires display)
  python run_tests.py all              run everything

Name filter (can be combined with any mode):
  python run_tests.py logic invoice    only invoice-related logic tests
  python run_tests.py logic zip        only ZIP logic tests
  python run_tests.py ui selector      only the selector visual tests

Flags:
  -q / --quiet     minimal output
  -v / --verbose   already the default; kept for explicitness

Examples:
  python run_tests.py
  python run_tests.py logic location_manager
  python run_tests.py ui
"""
import sys


def main():
    try:
        import pytest
    except ImportError:
        print("pytest is not installed.  Run:  .venv\\Scripts\\pip install pytest")
        sys.exit(1)

    raw    = sys.argv[1:]
    flags  = [a for a in raw if a.startswith("-")]
    posargs = [a for a in raw if not a.startswith("-")]

    mode        = "logic"
    name_filter = None

    for arg in posargs:
        if arg in ("logic", "ui", "all"):
            mode = arg
        else:
            name_filter = arg

    args = ["tests/"]

    if mode == "logic":
        args += ["-m", "not ui"]
    elif mode == "ui":
        args += ["-m", "ui", "-s"]   # -s: don't capture stdout (UI tests print instructions)

    if name_filter:
        args += ["-k", name_filter]

    quiet = "-q" in flags or "--quiet" in flags
    if not quiet:
        args.append("-v")

    if mode == "ui" and "-s" not in args:
        args.append("-s")

    print(f"Mode   : {mode}" + (f"   filter: {name_filter!r}" if name_filter else ""))
    print(f"Command: pytest {' '.join(args)}\n")
    sys.exit(pytest.main(args))


if __name__ == "__main__":
    main()
